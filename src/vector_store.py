import os
from typing import List
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

from src.config import CHROMA_DB_DIR, TOP_K_RESULTS, EMBEDDING_MODEL_NAME
from src.document_loader import load_and_chunk_policies

load_dotenv()


def get_embedding_function():
    """
    Returns Google Gemini Embeddings using an active model string.
    Checks for GEMINI_API_KEY or GOOGLE_API_KEY.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Neither GEMINI_API_KEY nor GOOGLE_API_KEY is found in .env!")
    
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        google_api_key=api_key
    )


def initialize_vector_store(force_rebuild: bool = False) -> Chroma:
    """
    Creates or loads a persistent ChromaDB vector store.
    """
    embeddings = get_embedding_function()
    db_path = str(CHROMA_DB_DIR)

    if force_rebuild and os.path.exists(db_path):
        import shutil
        shutil.rmtree(db_path)
        print("Cleared existing ChromaDB vector store.")

    if not os.path.exists(db_path) or force_rebuild:
        print("Building new vector database index...")
        chunks = load_and_chunk_policies()
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=db_path
        )
        print(f"Vector database initialized and saved to '{db_path}'.")
    else:
        print(f"Loading existing vector database from '{db_path}'...")
        vector_db = Chroma(
            persist_directory=db_path,
            embedding_function=embeddings
        )

    return vector_db


def query_vector_store(query_text: str, top_k: int = TOP_K_RESULTS) -> List[Document]:
    """
    Queries ChromaDB and returns top-k matching document chunks.
    """
    vector_db = initialize_vector_store(force_rebuild=False)
    results = vector_db.similarity_search(query_text, k=top_k)
    return results


if __name__ == "__main__":
    # Test vector store indexing and retrieval
    print("\n--- Initializing Vector Store ---")
    results = query_vector_store("What is the maximum surge multiplier allowed at SFO?")
    
    print(f"\n--- Search Query Results (Top {len(results)}) ---")
    for i, doc in enumerate(results, 1):
        print(f"\n[Result {i}]")
        print(f"Source Document: {doc.metadata.get('source')}")
        print(f"Content:\n{doc.page_content}")