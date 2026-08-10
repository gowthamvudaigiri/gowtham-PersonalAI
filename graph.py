import os
import uuid
from typing import TypedDict, Optional, List

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from langgraph.graph import StateGraph, END


# =========================================================
# LOAD ENV VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# QUERY CATEGORY MAP
# =========================================================


# =========================================================
# GRAPH STATE
# =========================================================

class GraphState(TypedDict):
    question: str
    category: Optional[str]
    context:  Optional[str]
    answer:   Optional[str]
    history:  Optional[List[dict]]  # [{"role": "user"|"assistant", "content": str}]
    summary:  Optional[str]         # compressed summary of older turns


# =========================================================
# PROFILE ASSISTANT GRAPH
# =========================================================

class ProfileAssistantGraph:
    """
    LangGraph-based RAG pipeline for the
    AI Executive Profile Assistant.

    Nodes:
        1. detect_intent  — maps question to a category
        2. retrieve       — fetches context from Chroma
        3. generate       — LLM generates the final answer
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        persist_directory: str,
        collection_name: str,
        embedding_model: str = "text-embedding-3-small",
        llm_model: str = "gpt-4o-mini"
    ):

        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables"
            )

        # ---------------------------------------------
        # VECTOR STORE
        # ---------------------------------------------

        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=OpenAIEmbeddings(
                model=embedding_model,
                api_key=self.openai_api_key
            ),
            persist_directory=persist_directory
        )

        # ---------------------------------------------
        # LLM
        # ---------------------------------------------

        self.llm = ChatOpenAI(
            model=llm_model,
            api_key=self.openai_api_key,
            temperature=0.3
        )

        # ---------------------------------------------
        # PROMPT
        # ---------------------------------------------

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a professional AI assistant representing Gowtham Vudaigiri,
a senior Data Engineering and BI leader with 19+ years of experience.

Your job is to answer questions about Gowtham Vudaigiri accurately and professionally.
Speak in third person about Gowtham.

You must ONLY answer questions that are directly related to Gowtham Vudaigiri —
his career history, projects, technical skills, leadership experience,
certifications, or professional vision.

Use the context provided below as your primary source. For follow-up questions,
you may also draw on information from the conversation history above.

If a question is about anyone or anything unrelated to Gowtham Vudaigiri,
politely decline and redirect: explain that you are only able to answer
questions about Gowtham's professional profile.

Do NOT generate code samples, tutorials, how-to guides, or any technical
demonstrations — even if asked whether Gowtham is capable of something.
If asked about his technical abilities, describe them from his profile;
do not write or demonstrate code on his behalf.

If the question is about Gowtham but neither the context nor the conversation
history contains enough information, say so honestly rather than making things up.

Context:
{context}"""
            ),
            MessagesPlaceholder(variable_name="history", optional=True),
            (
                "human",
                "{question}"
            )
        ])

        self.intent_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an intent classifier. Given a question about a person's professional profile,
        classify it into exactly ONE of these categories:

        - profile                        → general info, contact, location, who is he
        - career                         → current job, employer, work history, timeline, roles, where working
        - projects                       → projects built, worked on, delivered
        - technology                     → technical skills, tools, stack, programming languages
        - leadership                     → leadership style, team management, mentoring
        - education_and_certifications   → degrees, certifications, courses
        - vision                         → future goals, interests, aspirations
        - presentations                  → talks, public speaking, evangelism

        Respond with ONLY the category name, nothing else."""
            ),
            (
                "human",
                "{question}"
            )
        ])

        # ---------------------------------------------
        # OUTPUT PARSER
        # ---------------------------------------------

        self.output_parser = StrOutputParser()

        # ---------------------------------------------
        # BUILD GRAPH
        # ---------------------------------------------

        self.graph = self._build_graph()

        # Last run_id from stream() — used by app.py to link feedback to traces
        self.last_run_id = None

    # =====================================================
    # NODE 1 — DETECT INTENT
    # =====================================================

    def detect_intent(self, state: GraphState) -> GraphState:

        chain = self.intent_prompt | self.llm | self.output_parser

        detected_category = chain.invoke({
            "question": state["question"]
        }).strip().lower()

        valid_categories = {
            "profile", "career", "projects", "technology",
            "leadership", "education_and_certifications",
            "vision", "presentations"
        }

        if detected_category not in valid_categories:
            detected_category = None

        print(f"\n[Intent Detection]")
        print(f"Question : {state['question']}")
        print(f"Category : {detected_category or 'none — broad search'}")

        return {
            **state,
            "category": detected_category
        }

    # =====================================================
    # NODE 2 — RETRIEVE
    # =====================================================

    def retrieve(self, state: GraphState) -> GraphState:
        """
        Fetch the most relevant document from Chroma.
        Applies a category filter when intent is detected.
        """

        category = state.get("category")

        where_filter = (
            {"category": {"$eq": category}}
            if category else None
        )

        results = self.vector_store.similarity_search(
            query=state["question"],
            k=4,
            filter=where_filter
        )

        context = (
            "\n\n---\n\n".join(r.page_content for r in results)
            if results else "No relevant information found."
        )

        print(f"\n[Retrieval]")
        print(f"Filter   : {f'category = {category}' if category else 'none'}")
        print(f"Context  : {len(context)} characters retrieved")

        return {
            **state,
            "context": context
        }

    # =====================================================
    # NODE 3 — GENERATE
    # =====================================================

    def generate(self, state: GraphState) -> GraphState:
        """
        Pass retrieved context and user question to the LLM.
        Returns the final answer as a plain string via StrOutputParser.
        """

        chain = self.prompt | self.llm | self.output_parser

        answer = chain.invoke({
            "context": state["context"],
            "question": state["question"]
        })

        return {
            **state,
            "answer": answer
        }

    # =====================================================
    # BUILD GRAPH
    # =====================================================

    def _build_graph(self) -> StateGraph:
        """
        Wire the three nodes into a sequential graph.
        """

        workflow = StateGraph(GraphState)

        # Add nodes
        workflow.add_node("detect_intent", self.detect_intent)
        workflow.add_node("retrieve",      self.retrieve)
        workflow.add_node("generate",      self.generate)

        # Define edges
        workflow.set_entry_point("detect_intent")
        workflow.add_edge("detect_intent", "retrieve")
        workflow.add_edge("retrieve",      "generate")
        workflow.add_edge("generate",       END)

        return workflow.compile()

    # =====================================================
    # RUN
    # =====================================================

    def run(self, question: str) -> str:
        """
        Execute the full RAG pipeline for a given question.
        Returns the final answer string.
        """

        print("\n========================================")
        print("PROFILE ASSISTANT — RAG PIPELINE")
        print("========================================")

        result = self.graph.invoke({"question": question})

        print(f"\n[Answer]")
        print("----------------------------------------")
        print(result["answer"])
        print("----------------------------------------")

        return result["answer"]

    # =====================================================
    # HISTORY HELPERS
    # =====================================================

    def _build_history_context(
        self,
        history: Optional[List[dict]],
        summary: Optional[str]
    ) -> List:
        """
        Convert raw message dicts + optional summary into LangChain message objects.
        Summary (if present) is injected as a SystemMessage before recent turns.
        """
        messages = []

        if summary:
            messages.append(SystemMessage(
                content=f"Earlier in this conversation: {summary}"
            ))

        for msg in (history or []):
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        return messages

    def _should_summarize(self, history: List[dict]) -> bool:
        """
        Returns True when the total character count of the history
        exceeds ~12000 chars (≈3000 tokens at 4 chars/token).
        """
        total_chars = sum(len(m["content"]) for m in history)
        return total_chars > 12000

    def _summarize(self, history: List[dict]) -> str:
        """
        Compress the full conversation history into a short summary.
        Reuses self.llm — synchronous, not streamed.
        """
        conversation_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in history
        )
        summarize_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a conversation summarizer. Summarize the following "
                "conversation in 3-5 concise sentences, preserving all key facts, "
                "names, projects, and decisions mentioned."
            ),
            ("human", "{conversation}")
        ])
        chain = summarize_prompt | self.llm | self.output_parser
        return chain.invoke({"conversation": conversation_text})

    # =====================================================
    # STREAM
    # =====================================================

    def stream(
        self,
        question: str,
        history: Optional[List[dict]] = None,
        summary: Optional[str] = None
    ):
        """
        Run intent detection and retrieval synchronously,
        then stream the generation step token by token.
        Passes conversation history for multi-turn context.
        Yields string chunks as they arrive from the LLM.
        """

        state: GraphState = {
            "question": question,
            "category": None,
            "context": None,
            "answer": None,
            "history": history,
            "summary": summary,
        }
        state = self.detect_intent(state)
        state = self.retrieve(state)

        formatted_history = self._build_history_context(history, summary)

        self.last_run_id = uuid.uuid4()
        config = RunnableConfig(run_id=self.last_run_id)

        chain = self.prompt | self.llm | self.output_parser
        for chunk in chain.stream(
            {
                "context": state["context"],
                "question": question,
                "history": formatted_history,
            },
            config=config,
        ):
            yield chunk


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    assistant = ProfileAssistantGraph(
        persist_directory="./chroma_db",
        collection_name="gowtham_profile",
        embedding_model="text-embedding-3-small",
        llm_model="gpt-4o-mini"
    )

    questions = [
        "List all the projects gowtham was involved in",
        "What certifications does gowtham have?",
        "Describe gowtham's leadership experience",
        "What is gowtham's technical skills?",
        "Tell me about gowtham's career history",
        "What are gowtham's future goals and vision?"
    ]

    for question in questions:
        assistant.run(question)