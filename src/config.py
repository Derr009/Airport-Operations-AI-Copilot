import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "airport_policies"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"

# RAG Configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 3

# Gemini Embedding Model
EMBEDDING_MODEL_NAME = "models/gemini-embedding-001"