import os
import hashlib
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


# =========================================================
# LOAD ENV VARIABLES
# =========================================================

load_dotenv()


class ChromaKnowledgeIngestion:
    """
    Ingestion framework for AI Executive Profile Assistant.
    Each markdown file is stored as a single document,
    preserving full context for LLM retrieval.
    """

    # =====================================================
    # FILE CONFIG
    # =====================================================

    FILE_CONFIG = {
        "about_me": {
            "category": "profile",
            "topic": "executive_profile"
        },
        "leadership": {
            "category": "leadership",
            "topic": "leadership_experience"
        },
        "projects": {
            "category": "projects",
            "topic": "enterprise_projects"
        },
        "technical_expertise": {
            "category": "technology",
            "topic": "technical_skills"
        },
        "certifications": {
            "category": "education_and_certifications",
            "topic": "education_and_certifications"
        },
        "career_timeline": {
            "category": "career",
            "topic": "career_growth"
        },
        "vision_and_interests": {
            "category": "vision",
            "topic": "future_vision"
        },
        "presentations": {
            "category": "presentations",
            "topic": "public_speaking"
        }
    }

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        knowledge_base_dir: str,
        persist_directory: str,
        collection_name: str,
        embedding_model: str = "text-embedding-3-small",
        profile_type: str = "executive_profile",
        seniority: str = "executive"
    ):

        self.knowledge_base_dir = knowledge_base_dir
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.profile_type = profile_type
        self.seniority = seniority

        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables"
            )

        # ---------------------------------------------
        # OPENAI EMBEDDINGS
        # ---------------------------------------------

        self.embeddings = OpenAIEmbeddings(
            model=self.embedding_model,
            api_key=self.openai_api_key
        )

        # ---------------------------------------------
        # CHROMA VECTOR STORE
        # ---------------------------------------------

        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    # =====================================================
    # MARKDOWN LOADER
    # =====================================================

    def load_markdown_files(self) -> List[Path]:
        """
        Load all markdown files from knowledge base directory.
        """

        knowledge_path = Path(self.knowledge_base_dir)

        markdown_files = list(knowledge_path.glob("*.md"))

        if not markdown_files:
            raise ValueError(
                "No markdown files found in knowledge_base directory"
            )

        print(f"\nFound {len(markdown_files)} markdown files")

        return markdown_files

    # =====================================================
    # BUILD METADATA
    # =====================================================

    def build_metadata(
        self,
        filename: str
    ) -> Dict:
        """
        Build metadata for a single file document.
        """

        config = self.FILE_CONFIG.get(filename, {})

        return {
            "source": f"{filename}.md",
            "filename": filename,
            "category": config.get("category", "general"),
            "topic": config.get("topic", "general"),
            "heading": filename.replace("_", " ").title(),
            "type": self.profile_type,
            "seniority": self.seniority
        }

    # =====================================================
    # GENERATE STABLE ID
    # =====================================================

    def generate_document_id(
        self,
        filename: str
    ) -> str:
        """
        Generate a deterministic ID from filename.
        Ensures re-ingestion upserts rather than duplicates.
        """

        return hashlib.md5(f"full_file::{filename}.md".encode()).hexdigest()

    # =====================================================
    # PROCESS SINGLE FILE
    # =====================================================

    def process_file(
        self,
        file_path: Path
    ) -> Document:
        """
        Read a markdown file and return a single
        Document with its full content and metadata.
        """

        filename = file_path.stem

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        metadata = self.build_metadata(filename)

        return Document(
            page_content=content,
            metadata=metadata
        )

    # =====================================================
    # INGEST DOCUMENTS
    # =====================================================

    def ingest_documents(self):
        """
        Main ingestion pipeline.
        Each markdown file is stored as one document.
        """
        self.vector_store._collection.delete(ids=self.vector_store._collection.get()["ids"])
        all_documents = []
        all_ids = []

        markdown_files = self.load_markdown_files()

        # ---------------------------------------------
        # LOG EXISTING COLLECTION SIZE
        # ---------------------------------------------

        existing_count = self.vector_store._collection.count()
        print(f"Existing docs in collection : {existing_count}")

        # ---------------------------------------------
        # PROCESS ALL FILES
        # ---------------------------------------------

        for file_path in markdown_files:

            try:
                print(f"\nProcessing : {file_path.name}")

                document = self.process_file(file_path)
                doc_id = self.generate_document_id(file_path.stem)

                all_documents.append(document)
                all_ids.append(doc_id)

                print(f"Characters : {len(document.page_content)}")
                print(f"Category   : {document.metadata['category']}")
                print(f"ID         : {doc_id}")

            except Exception as e:
                print(f"[WARNING] Failed to process {file_path.name}: {e}")
                continue

        print(f"\nTotal documents prepared : {len(all_documents)}")

        # ---------------------------------------------
        # UPSERT INTO CHROMADB
        # ---------------------------------------------

        self.vector_store.add_documents(
            documents=all_documents,
            ids=all_ids
        )

        print("\n========================================")
        print("INGESTION COMPLETED SUCCESSFULLY")
        print("========================================")
        print(f"Collection : {self.collection_name}")
        print(f"Documents  : {len(all_documents)}")
        print(f"Database   : {self.persist_directory}")

    # =====================================================
    # TEST RETRIEVAL
    # =====================================================

    def test_query(
        self,
        query: str,
        k: int = 1,
        category: str = None
    ):
        """
        Test similarity search with optional category filter.

        Example categories: 'projects', 'career',
        'technology', 'leadership', 'vision'
        """

        print(f"\nQuery    : '{query}'")
        print(f"Filter   : {f'category = {category}' if category else 'none'}")
        print("\n========================================")
        print("TESTING VECTOR SEARCH")
        print("========================================")

        where_filter = (
            {"category": {"$eq": category}}
            if category else None
        )

        results = self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=where_filter
        )

        for idx, result in enumerate(results, start=1):

            print("\n------------------------------------")
            print(f"RESULT #{idx}")
            print("------------------------------------")
            print("\nMetadata:")
            print(result.metadata)
            print("\nContent:")
            print(result.page_content)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    ingestion_service = ChromaKnowledgeIngestion(
        knowledge_base_dir="./knowledge_base",
        persist_directory="./chroma_db",
        collection_name="gowtham_profile",
        embedding_model="text-embedding-3-small",
        profile_type="executive_profile",
        seniority="executive"
    )

    # -----------------------------------------------------
    # INGEST DOCUMENTS
    # -----------------------------------------------------

    #ingestion_service.ingest_documents()

    # -----------------------------------------------------
    # TEST QUERIES
    # -----------------------------------------------------

ingestion_service.test_query(
    query="list all the projects gowtham was involved in",
    category="projects"
)