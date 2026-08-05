# Implementation Roadmap

Items are organised into four stages based on dependency order, risk, and value. Each stage can be worked on independently after its predecessors are complete. Feature IDs reference `FEATURE_RECOMMENDATIONS.md`.

---

## Stage 1 — Quick Wins
*Zero-dependency fixes and trivial improvements. Safe to implement in any order. No new packages required.*

| ID | Item | Reason | Files Affected | Priority | Effort | Risk | Dependencies |
|---|---|---|---|---|---|---|---|
| S1-01 | Fix `ingest.py` scope bug (move `test_query` inside `__main__`) | Prevents future `NameError` if `ingest` is ever imported; clarifies intent | `ingest.py:332–334` | High | Trivial | None | None |
| S1-02 | Add `.env.example` | Documents required env vars; standard onboarding practice | `.env.example` (new file) | High | Trivial | None | None |
| S1-03 | Increase retrieval depth `k=1` → `k=4` (F-21) | Richer multi-document answers for cross-cutting questions | `graph.py:202–208` | High | Trivial | Low — slightly more tokens per response | None |
| S1-04 | Add API error handling in `app.py` (F-09) | Prevents app crashes from bad API key or network failure | `app.py:775` | Critical | Small | None | None |
| S1-05 | Input strip + length validation (F-12) | Prevents whitespace submissions and oversized inputs | `app.py:751` | Medium | Small | None | None |
| S1-06 | Make starter grid items clickable (F-02) | Removes most prominent UX confusion for new users | `app.py:715–734` | High | Small | None | None |
| S1-07 | Add typography fallback stack | Inter fails gracefully on corporate networks or offline | `app.py:28` | Low | Trivial | None | None |
| S1-08 | Add `requirements-dev.txt` | Separates runtime from dev/test dependencies | `requirements-dev.txt` (new file) | Medium | Trivial | None | None |

---

## Stage 2 — UI Foundation
*Foundational improvements to perceived performance and design maintainability. Implement after Stage 1.*

| ID | Item | Reason | Files Affected | Priority | Effort | Risk | Dependencies |
|---|---|---|---|---|---|---|---|
| S2-01 | Streaming LLM responses (F-01) | Eliminates 3–7s blank wait; single highest-impact UX improvement | `graph.py` (add `stream()`), `app.py:775` | Critical | Medium | Low | S1-04 (error handling must wrap streaming too) |
| S2-02 | Extract CSS to `styles.py` or `.streamlit/style.css` | Decouples design tokens from rendering logic; prevents accidental overwrite | `app.py`, new `styles.py` | Medium | Small | Low | None |
| S2-03 | Extract profile metadata to `PROFILE_META` dict | Allows role/location/title updates without editing HTML strings | `app.py:666–709` | Low | Small | None | None |
| S2-04 | Add `role="log"` + `aria-live` to chat container (accessibility) | Screen-reader users receive answer announcements | `app.py:740–783` | High | Small | None | None |
| S2-05 | Add copy-to-clipboard on assistant answers (F-03) | Primary user workflow is extracting text to share | `app.py:602–612` | Medium | Small | Low | S2-01 (streaming changes how answer text is stored) |
| S2-06 | Add confirmation dialog before "Clear conversation" | Destructive action needs a guard | `app.py:646` | Medium | Small | None | None |
| S2-07 | WCAG contrast fix for small text (`--ink-500` → `--ink-700`) | Passes AA contrast for 11px sidebar labels | `app.py:100–107` | High | Trivial | None | S2-02 (easier after CSS extraction) |

---

## Stage 3 — Core Product Features
*Meaningful new functionality that expands what users can do with the assistant.*

| ID | Item | Reason | Files Affected | Priority | Effort | Risk | Dependencies |
|---|---|---|---|---|---|---|---|
| S3-01 | Multi-turn conversational context (F-05) | Enables follow-up questions; transforms FAQ into conversation | `graph.py` (update `GraphState`, `generate` node), `app.py` | High | Medium | Medium — increased token cost per turn | S2-01 (streaming) |
| S3-02 | Conversation export to Markdown (F-04) | Lets users save and share session transcripts | `app.py` (sidebar `st.download_button`) | Medium | Small | None | None |
| S3-03 | Session-level rate limiting (F-15) | Protects API quota on public deployment | `app.py` (session state counter) | Medium | Small | None | None |
| S3-04 | Follow-up question suggestions (F-08) | Increases session depth; helps users discover profile topics | `graph.py` (new suggestion chain), `app.py` | Low | Medium | Low | S3-01 (context helps) |
| S3-05 | Dark mode toggle (F-06) | Modern comfort feature; prefers-color-scheme compliance | `app.py` (CSS variables + toggle) | Low | Medium | Low | S2-02 (CSS extraction makes this tractable) |
| S3-06 | Suggested question used-state indicator (F-07) | Reduces duplicate sidebar submissions | `app.py:636–642` | Low | Small | None | None |

---

## Stage 4 — Production Readiness
*Engineering infrastructure to make the app deployable, maintainable, and observable.*

| ID | Item | Reason | Files Affected | Priority | Effort | Risk | Dependencies |
|---|---|---|---|---|---|---|---|
| S4-01 | Unit tests for `graph.py` nodes (F-17) | Regression safety for pipeline changes | `tests/test_graph.py` (new) | High | Medium | None | `requirements-dev.txt` from S1-08 |
| S4-02 | Integration test: ingest → retrieve (F-18) | Verifies the full KB pipeline end-to-end | `tests/test_ingest.py` (new) | Medium | Medium | None | S4-01 |
| S4-03 | Docker + docker-compose (F-19) | Reproducible deployment; no manual Python setup | `Dockerfile`, `docker-compose.yml` (new) | Medium | Small | None | None |
| S4-04 | GitHub Actions CI (F-20) | Automated lint + test on every push | `.github/workflows/ci.yml` (new) | Medium | Small | None | S4-01 |
| S4-05 | Dependency security audit (`pip-audit`) | Detects known CVEs in pinned packages | `requirements-dev.txt`, CI step | Medium | Small | None | S4-04 |
| S4-06 | Retry logic for transient OpenAI errors (F-10) | Silent recovery from 429/500 errors | `graph.py` (tenacity decorators) | Medium | Small | None | S1-04 |
| S4-07 | Input sanitisation / prompt injection hardening (F-14) | Defence-in-depth against adversarial prompts | `app.py:751`, `graph.py:generate` | Medium | Small | None | S1-05 |
| S4-08 | Health-check endpoint (F-13) | Enables uptime monitoring | `health.py` (new), `Procfile` | Low | Medium | None | S4-03 |
| S4-09 | Expanded README with setup + deployment docs | Reduces onboarding time for new contributors | `README.MD` | Medium | Small | None | S1-02, S4-03 |

---

## Sequencing Overview

```
Stage 1 (Quick Wins)         ──► Stage 2 (UI Foundation)
     │                                     │
     │                                     ▼
     └──────────────────────────► Stage 3 (Core Features)
                                           │
                                           ▼
                                  Stage 4 (Production)
```

Stage 1 and Stage 4 engineering items (S4-01, S4-03) can be worked in parallel after Stage 1 Quick Wins.

---

## Effort Summary

| Stage | Items | Total Effort |
|---|---|---|
| Stage 1 | 8 | ~1–2 days |
| Stage 2 | 7 | ~2–3 days |
| Stage 3 | 6 | ~3–5 days |
| Stage 4 | 9 | ~3–5 days |
| **Total** | **30** | **~10–15 days** |
