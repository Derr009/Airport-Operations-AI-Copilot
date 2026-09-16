import os
from typing import List
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP


def load_and_chunk_policies(data_dir: str = str(DATA_DIR)) -> List[Document]:
    """
    Loads all policy text files from the data directory and splits them into manageable chunks.
    Preserves document source metadata for traceability.
    """
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory not found at {data_dir}")

    # Load all .txt files from the directory
    loader = DirectoryLoader(
        data_dir,
        glob="**/*.txt",
        loader_cls=TextLoader
    )
    raw_documents = loader.load()

    # Normalize source file names in metadata (e.g., 'data/airport_policies/sfo_pricing.txt' -> 'sfo_pricing.txt')
    for doc in raw_documents:
        source_path = doc.metadata.get("source", "")
        doc.metadata["source"] = os.path.basename(source_path)

    # Initialize character splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )

    chunked_docs = text_splitter.split_documents(raw_documents)
    print(f"Loaded {len(raw_documents)} raw policy document(s).")
    print(f"Split into {len(chunked_docs)} semantic chunk(s).")
    
    return chunked_docs


if __name__ == "__main__":
    # Test loading script
    chunks = load_and_chunk_policies()
    if chunks:
        print("\n--- Sample Chunk Preview ---")
        print(f"Source: {chunks[0].metadata['source']}")
        print(f"Content:\n{chunks[0].page_content}")