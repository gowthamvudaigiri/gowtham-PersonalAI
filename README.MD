# Gowtham AI Executive Assistant

An AI-powered conversational assistant that answers questions about Gowtham Vudaigiri's professional profile — career history, projects, technical expertise, leadership, certifications, and vision.

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| LLM Orchestration | LangGraph |
| LLM | OpenAI `gpt-4o-mini` |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector Store | ChromaDB |
| LangChain | langchain, langchain-openai, langchain-chroma |

## Features

- Streaming token-by-token responses
- Intent detection routes questions to the most relevant knowledge-base document
- Grounded answers — the assistant only uses information from the profile documents
- 7 suggested questions in the sidebar
- Clickable starter prompts on the welcome screen
- Conversation history persisted per session
- Graceful error handling for API failures

## Project Structure

```
gowtham-PersonalAI/
├── app.py              # Streamlit UI
├── graph.py            # LangGraph RAG pipeline
├── ingest.py           # Knowledge base ingestion script
├── knowledge_base/     # Markdown profile documents
├── chroma_db/          # Persisted ChromaDB vector store
├── requirements.txt    # Python dependencies
└── .env.example        # Environment variable template
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/gowthamvudaigiri/gowtham-PersonalAI.git
cd gowtham-PersonalAI
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 5. Run the app

```bash
python3 -m streamlit run app.py
```

The app will open at **http://localhost:8501**.

## Updating the Knowledge Base

If you edit any files in `knowledge_base/`, re-run the ingestion script to rebuild the vector store:

```bash
python3 ingest.py
```

## Topics You Can Ask About

- Leadership style and team management
- Projects and deliverables
- Technical skills and tools
- Certifications and education
- Career timeline and roles
- Vision and future goals
- Conference talks and presentations
