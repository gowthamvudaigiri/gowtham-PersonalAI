# First Implementation Plan

## Recommended First Slice: Streaming Responses + API Error Handling

### Why This Is the Best Starting Point

This slice delivers the **single largest user-visible improvement** (no more 3–7s frozen wait) while making **zero structural changes** to the existing app. It:

- Requires no new dependencies
- Touches exactly two files (`graph.py` and `app.py`)
- Does not change the knowledge base, prompts, ChromaDB schema, or session state structure
- Demonstrates the app's production readiness without a full redesign
- Is easy to test: visual before/after comparison with a running app
- Pairs naturally with the Critical-priority bug fix (error handling) that should be done anyway

The alternative candidates (making starter grid clickable, WCAG contrast fix) are smaller in visible impact. The multi-turn context feature is higher complexity and should come after streaming is stable.

---

## Scope

### What Changes

#### `graph.py`

Add a `stream(question: str)` generator method to `ProfileAssistantGraph` alongside the existing `run()` method. The `run()` method is preserved unchanged so nothing breaks if `stream()` is not yet called.

The new method:
1. Invokes the full pipeline up through `retrieve` (intent detection + retrieval) synchronously — these are fast operations.
2. Streams only the `generate` node's LLM output token by token.
3. Yields string chunks as they arrive from OpenAI.
4. Accumulates the full answer and returns it (or stores it for session state).

**Approach:** Use LangChain's `.stream()` on the final `prompt | llm | output_parser` chain in the `generate` step. The intent detection and retrieval steps are not streamed (they are short, categorical operations that do not benefit from streaming).

Concretely, add a second public method:

```python
def stream(self, question: str):
    """
    Run intent detection and retrieval synchronously,
    then stream the generation step token by token.
    Yields string chunks.
    """
    # Step 1: detect intent (fast, ~300ms)
    state: GraphState = {"question": question, "category": None, "context": None, "answer": None}
    state = self.detect_intent(state)

    # Step 2: retrieve context (fast, local ChromaDB query)
    state = self.retrieve(state)

    # Step 3: stream generation
    chain = self.prompt | self.llm | self.output_parser
    for chunk in chain.stream({"context": state["context"], "question": question}):
        yield chunk
```

No changes to `detect_intent`, `retrieve`, `generate`, `_build_graph`, or `run`.

---

#### `app.py`

Two changes:

**Change 1 — Use `st.write_stream` for the response (replaces lines 775–778):**

```python
# Before
answer = st.session_state.graph.run(question)
thinking_placeholder.empty()
render_message("assistant", answer)

# After
thinking_placeholder.empty()
answer_chunks = []
with st.chat_message("assistant"):   # native Streamlit container
    answer = st.write_stream(
        st.session_state.graph.stream(question)
    )
```

`st.write_stream` handles the streaming container natively — it renders tokens incrementally and returns the full accumulated string when done. We store the returned string in `answer` for session state.

**Note on rendering style:** The existing `render_message()` function uses custom HTML bubbles for visual consistency. After streaming completes, the streamed content can be re-rendered using `render_message()` via a `st.rerun()`, or the streaming container can be styled to match. The exact approach (stream-then-rerender vs. accept Streamlit's native chat container styling) should be decided during implementation. The simplest path is to accept Streamlit's `st.chat_message` styling for the streaming answer and reserve the custom HTML renderer for history replay.

**Change 2 — Wrap the entire question-handling block in try/except:**

```python
try:
    thinking_placeholder.empty()
    answer = st.write_stream(st.session_state.graph.stream(question))
except Exception as e:
    thinking_placeholder.empty()
    st.error("Something went wrong. Please try again in a moment.")
    # Remove the user message we optimistically appended
    st.session_state.messages.pop()
    answer = None

if answer:
    st.session_state.messages.append({"role": "assistant", "content": answer})
```

This ensures:
- A failed OpenAI call (bad key, rate limit, network timeout) shows a friendly error
- The user's question is removed from history if no answer was produced (avoids orphaned user messages)
- The full traceback is never shown to the user

---

## What Must Not Change

| Element | Location | Why |
|---|---|---|
| `render_message()` for history replay | `app.py:588–613` | Chat history must still render with custom HTML bubbles |
| Sidebar suggested questions + `queue_sidebar_question` | `app.py:619–659` | Same callback mechanism; works with the new question-handling flow |
| Hero section, insight strip, welcome state | `app.py:666–734` | No changes to static UI |
| `st.session_state.messages` structure | `app.py:569–570` | `[{"role": str, "content": str}]` — unchanged |
| `ProfileAssistantGraph.__init__`, `run()`, all nodes | `graph.py` | `run()` stays for backward compatibility |
| ChromaDB collection, embedding model, LLM model | `graph.py` | No configuration changes |

---

## Files Modified

| File | Lines Changed | Nature of Change |
|---|---|---|
| `graph.py` | ~25 lines added | New `stream()` method at the bottom of `ProfileAssistantGraph` |
| `app.py` | ~10 lines modified | Replace `graph.run()` call block with `st.write_stream()` + try/except |

No new files. No new dependencies. No configuration changes.

---

## Testing Plan

### Manual Testing (required before marking done)

1. **Start the app:** `streamlit run app.py`
2. **Streaming happy path:** Ask "What certifications does Gowtham hold?" — verify text appears token by token rather than all at once after a wait.
3. **Sidebar button:** Click a suggested question — verify streaming works the same way as typed input.
4. **History replay:** After receiving a streamed answer, scroll up to verify prior messages still render with custom HTML bubbles (not Streamlit's native chat style).
5. **Error handling:** Temporarily set `OPENAI_API_KEY=invalid` in `.env`, restart, ask a question — verify a friendly error message appears and the app does not crash.
6. **Clear conversation:** Verify clearing still works and the welcome state reappears.
7. **Multi-question session:** Ask 3 questions in sequence. Verify all answers accumulate in session state correctly.

### Automated Tests (if time permits / Stage 4)

- `tests/test_graph.py`: Test that `stream()` yields non-empty string chunks for a mocked LLM response.
- `tests/test_graph.py`: Test that `stream()` raises (or passes through) an `OpenAIError` when the LLM fails.

---

## Acceptance Criteria

| # | Criterion | How to Verify |
|---|---|---|
| AC-1 | Response text appears token by token; no full-page wait | Visual observation |
| AC-2 | A failed API call shows `st.error(...)` and does not crash the app | Set invalid API key, submit question |
| AC-3 | All 7 sidebar suggested questions still trigger a response | Click each button |
| AC-4 | Session history accumulates correctly across multiple questions | Ask 3 questions, inspect `st.session_state.messages` via st.write (debug) or visual |
| AC-5 | "Clear conversation" still resets the session | Click clear, verify welcome state |
| AC-6 | `graph.run()` still works (not removed) | `python graph.py` — runs test questions from `__main__` |

---

## Risks and Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| `st.write_stream` styling conflicts with custom HTML bubble CSS | Medium | Stream into a native `st.chat_message` container; replay from history still uses custom `render_message()`. Accept minor visual inconsistency for the streamed message; resolve in Stage 2. |
| `chain.stream()` raises on first token (not at call site) | Low | The try/except wraps the entire `st.write_stream` call, so any mid-stream error is caught. |
| `run()` removal accidentally breaks `__main__` test block in `graph.py` | None | `run()` is explicitly kept. |
| Streaming adds latency to the intent detection step (currently synchronous) | None | Intent detection and retrieval remain synchronous; only the generation step streams. |

---

## What Comes Next (Stage 1 continuation)

After this slice is merged and tested:
1. `S1-01`: Fix `ingest.py` scope bug (5-minute fix)
2. `S1-02`: Add `.env.example`
3. `S1-03`: Increase `k=1` to `k=4`
4. `S1-06`: Make starter grid items clickable
