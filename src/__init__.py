"""
Sistema RAG para Dungeons & Dragons 5ª edición
"""

# Importar las clases/funciones principales
from .vector_pipeline import get_retriever, init_or_update
from .rag_interface import *
from .config import *

# Definir qué se exporta con "from src import *"
__all__ = [
    'get_retriever',
    'init_or_update',
    'EMBEDDINGS_MODEL',
    'LLM_MODEL',
    'CHUNK_SIZE'
]

# Código de inicialización opcional
print("🐉 Dungeons RAG package loaded")
