import os
from pathlib import Path

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "markdown"
STORAGE_DIR = PROJECT_ROOT / "storage"
DB_DIR = STORAGE_DIR / "db_dungeons"

# Configuración de modelos
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "bge-m3:latest")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:4b")

# Configuración RAG
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "4"))

# LangSmith (opcional)
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "dungeons-manual")
