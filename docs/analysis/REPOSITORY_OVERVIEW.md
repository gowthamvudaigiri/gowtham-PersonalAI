# Repository Overview

## What the Application Does

**Gowtham AI Executive Assistant** is a single-page, AI-powered profile chatbot. It lets visitors or interviewers ask natural-language questions about Gowtham Vudaigiri's professional history — career, projects, certifications, leadership, technical skills, and vision — and receive grounded, LLM-generated answers drawn exclusively from a curated knowledge base.

**Target users:** Recruiters, hiring managers, potential clients, or professional contacts who want a quick, interactive way to learn about Gowtham's background.

---

## Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Frontend / App server | Streamlit | 1.58.0 |
| Markdown renderer | markdown-it-py | 4.2.0 |
| LLM orchestration | LangGraph | 1.2.2 |
| LLM | OpenAI `gpt-4o-mini` | openai 2.38.0 |
| Embeddings | OpenAI `text-embedding-3-small` | — |
| Vector store | ChromaDB | 1.5.9 |
| LangChain integration | langchain-chroma, langchain-openai | 1.1.0 / 1.2.2 |
| Environment config | python-dotenv | 1.2.2 |

---

## Architecture Map

```
User (browser)
    │
    ▼
Streamlit UI  (app.py)
    │  submits question via st.chat_input or sidebar button
    ▼
ProfileAssistantGraph.run(question)  (graph.py)
    │
    ├─ Node 1: detect_intent
    │     └─ LLM call: classify question into 1 of 8 categories
    │
    ├─ Node 2: retrieve
    │     └─ ChromaDB similarity_search(k=1, filter=category)
    │          └─ chroma_db/  (persisted vector store)
    │
    └─ Node 3: generate
          └─ LLM call: answer question using retrieved context
               └─ returns plain string

                    ▲
ingest.py ──────────┘
    reads knowledge_base/*.md
    embeds each file as a single Document
    upserts into ChromaDB (deterministic MD5 IDs)
```

**Knowledge base documents:**

| File | ChromaDB category |
|---|---|
| `about_me.md` | profile |
| `career_timeline.md` | career |
| `certifications.md` | education_and_certifications |
| `leadership.md` | leadership |
| `presentations.md` | presentations |
| `projects.md` | projects |
| `technical_expertise.md` | technology |
| `vision_and_interests.md` | vision |

---

## Directory Structure

```
gowtham-PersonalAI/
├── app.py                  # Streamlit UI entry point
├── graph.py                # LangGraph RAG pipeline
├── ingest.py               # Knowledge base ingestion script
├── requirements.txt        # Pinned Python dependencies
├── runtime.txt             # Python version for deployment (Streamlit Cloud)
├── Instructions.MD         # Product enhancement instructions
├── README.MD               # Short project description
├── knowledge_base/         # Source Markdown documents (8 files + Backup/)
└── chroma_db/              # Persisted ChromaDB vector store (auto-generated)
```

Ignored: `chroma_db/` contents, `__pycache__/`, `knowledge_base/Backup/`.

---

## How to Run Locally

**Prerequisites:** Python 3.10+, an OpenAI API key.

```bash
# 1. Clone and install dependencies
pip install -r requirements.txt

# 2. Create .env file (not currently provided — see confirmed bug below)
echo "OPENAI_API_KEY=sk-..." > .env

# 3. Ingest knowledge base (only needed on first run or after KB changes)
python ingest.py

# 4. Start the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Confirmed Bugs

### Bug 1 — `ingest.py`: `test_query()` call outside `if __name__ == "__main__"` block

**File:** `ingest.py`, line 332  
**Severity:** High  

```python
if __name__ == "__main__":
    ingestion_service = ChromaKnowledgeIngestion(...)
    # ingest_documents() commented out

# ← This line is at module scope (wrong indentation)
ingestion_service.test_query(
    query="list all the projects gowtham was involved in",
    category="projects"
)
```

The `test_query()` call is dedented out of the `if __name__` block. Any import of `ingest.py` would crash with `NameError: name 'ingestion_service' is not defined`. In practice, `ingest.py` is not imported by `app.py` or `graph.py`, so this has not caused a runtime error yet — but it will if `ingest` is ever imported, and it is also confusing to run `python ingest.py` directly (the test query always runs even when commented ingestion is the intent).

**Fix:** Move the `test_query()` call inside the `if __name__ == "__main__"` block.

---

### Bug 2 — `graph.py`: `k=1` retrieval limits answer completeness

**File:** `graph.py`, line 202  
**Severity:** Medium  

Only one document chunk is retrieved per question. Since each knowledge-base file is stored as a single whole-file document, `k=1` means only one entire Markdown file is ever passed to the LLM. Questions that span multiple categories (e.g., "What makes Gowtham a strong engineering leader?" touching both `leadership.md` and `career_timeline.md`) will be answered from only one source.

**Fix:** Increase `k` to 3–4 to allow multi-document context.

---

## What Is Missing

| Gap | Notes |
|---|---|
| `.env.example` | No documented env var template; developers must guess `OPENAI_API_KEY` is required |
| Tests | Zero unit, integration, or e2e tests |
| CI/CD | No GitHub Actions, no automated test or lint pipeline |
| Dockerfile / docker-compose | No containerisation |
| Error handling in UI | `graph.run()` exceptions propagate unhandled; a bad API key or network failure crashes the Streamlit process |
| Rate limiting | No protection against spamming the OpenAI API |
| Streaming | LLM response is fully buffered before display; no token-by-token streaming |
| Developer README | Existing README is 10 lines; no setup, env var, or deployment instructions |
