# -------------------------------------------------------------------------#
# VECTOR PIPELINE - Pipeline de procesamiento de documentos Markdown para RAG
# -------------------------------------------------------------------------#

"""
Pipeline de procesamiento de documentos Markdown para D&D 5E

Funcionalidades principales:
• Divide cada fichero por páginas marcadas con '---'
• Dentro de cada página aplica (Headers ➜ Tokens) para producir chunks ≤ 800 tokens
• Almacena metadatos: document_name, page_number, section_path
• Gestiona actualizaciones incrementales basadas en hash MD5
"""

import os
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from tqdm import tqdm

# Importaciones de LangChain
from langchain.schema import Document
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# Importación de configuración interna
from config import (
    PROJECT_ROOT,
    DATA_DIR,
    DB_DIR,
    STORAGE_DIR,
    EMBEDDINGS_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

# -------------------------------------------------------------------------#
# 1. CONFIGURACIÓN Y CONSTANTES
# -------------------------------------------------------------------------#

# Archivos y directorios
PROCESSED_LOG = DB_DIR / "processed_files.json"

# Expresión regular para separar páginas lógicas
PAGE_RE = re.compile(r"(?<=\n)---+\n")

# Instancia global de embeddings (inicializada bajo demanda)
_embeddings: Optional[OllamaEmbeddings] = None
_retriever: Optional[Any] = None

# -------------------------------------------------------------------------#
# 2. UTILIDADES DE ARCHIVOS Y HASH
# -------------------------------------------------------------------------#

def normalize_filename(path: str | bytes) -> str:
    """
    Normaliza el nombre de archivo para usar como clave única.
    
    Args:
        path: Ruta del archivo (str o bytes)
        
    Returns:
        Nombre base del archivo normalizado
    """
    if isinstance(path, bytes):
        path = path.decode("utf-8", "ignore")
    return os.path.basename(path).replace("\\", "/").split("/")[-1].strip()

def calculate_file_hash(file_path: str) -> Optional[str]:
    """
    Calcula el hash MD5 de un archivo.
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        Hash MD5 del archivo o None si hay error
    """
    try:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"Error calculando hash para {file_path}: {e}")
        return None

def list_markdown_files(root_dir: str) -> List[str]:
    """
    Lista recursivamente todos los archivos Markdown en un directorio.
    
    Args:
        root_dir: Directorio raíz para buscar
        
    Returns:
        Lista de rutas de archivos Markdown encontrados
    """
    markdown_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith((".md", ".markdown")):
                markdown_files.append(os.path.normpath(os.path.join(root, file)))
    return markdown_files

# -------------------------------------------------------------------------#
# 3. GESTIÓN DE LOG DE PROCESAMIENTO
# -------------------------------------------------------------------------#

def load_processing_log() -> Dict[str, Any]:
    """
    Carga el log de archivos procesados desde disco.
    
    Returns:
        Diccionario con información de archivos procesados
    """
    if PROCESSED_LOG.exists():
        try:
            with open(PROCESSED_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error cargando log de procesamiento: {e}")
            return {}
    return {}

def save_processing_log(log_data: Dict[str, Any]) -> None:
    """
    Guarda el log de archivos procesados a disco.
    
    Args:
        log_data: Datos del log a guardar
    """
    try:
        # Crear directorio si no existe
        DB_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(PROCESSED_LOG, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error guardando log de procesamiento: {e}")

def update_processing_log(processed_log: Dict[str, Any], file_paths: List[str]) -> None:
    """
    Actualiza el log con los archivos recién procesados.
    
    Args:
        processed_log: Log actual de archivos procesados
        file_paths: Lista de rutas de archivos procesados
    """
    for file_path in file_paths:
        file_hash = calculate_file_hash(file_path)
        if file_hash:
            key = normalize_filename(file_path)
            processed_log[key] = {
                "hash": file_hash,
                "processed": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    save_processing_log(processed_log)

def identify_new_files(all_files: List[str], processed_log: Dict[str, Any]) -> List[str]:
    """
    Identifica archivos nuevos o modificados comparando con el log.
    
    Args:
        all_files: Lista de todos los archivos encontrados
        processed_log: Log de archivos ya procesados
        
    Returns:
        Lista de archivos que necesitan procesamiento
    """
    new_files = []
    
    for file_path in all_files:
        current_hash = calculate_file_hash(file_path)
        if not current_hash:
            continue
            
        file_key = normalize_filename(file_path)
        
        # Archivo es nuevo o ha cambiado
        if (file_key not in processed_log or 
            processed_log[file_key]["hash"] != current_hash):
            new_files.append(file_path)
    
    return new_files

# -------------------------------------------------------------------------#
# 4. PROCESAMIENTO DE DOCUMENTOS MARKDOWN
# -------------------------------------------------------------------------#

def split_markdown_document(md_text: str, doc_name: str) -> List[Document]:
    """
    Divide un documento Markdown en chunks procesables.
    
    Proceso:
    1. Divide por páginas lógicas (separadas por '---')
    2. Dentro de cada página, divide por headers
    3. Si los chunks son muy grandes, divide por tamaño
    4. Añade metadatos completos incluyendo jerarquía de secciones
    
    Args:
        md_text: Contenido completo del archivo Markdown
        doc_name: Nombre del documento para metadatos
        
    Returns:
        Lista de documentos procesados con metadatos
    """
    # Dividir por páginas lógicas
    pages = PAGE_RE.split(md_text)
    print(f"📄 Documento: {doc_name} - Páginas lógicas: {len(pages)}")
    
    # Configurar splitters
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("# ", "H1"),
            ("## ", "H2"), 
            ("### ", "H3"),
            ("#### ", "H4")
        ]
    )
    
    token_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " "],
        length_function=len
    )
    
    chunks = []
    
    for page_idx, page_content in enumerate(pages):
        if not page_content.strip():
            continue
            
        # Paso 1: Dividir por encabezados
        header_docs = header_splitter.split_text(page_content)
        
        # Paso 2: Procesar cada sección
        for doc in header_docs:
            # Si el documento es muy grande, dividir por tamaño
            if len(doc.page_content) > (CHUNK_SIZE * 2):
                subdocs = token_splitter.split_documents([doc])
            else:
                subdocs = [doc]
                
            # Procesar cada chunk final
            for chunk_doc in subdocs:
                # Construir jerarquía de encabezados para contexto
                section_path = " > ".join([
                    chunk_doc.metadata.get(header, "") 
                    for header in ["H1", "H2", "H3", "H4"] 
                    if chunk_doc.metadata.get(header)
                ])
                
                # Actualizar metadatos
                chunk_doc.metadata.update({
                    "document_name": doc_name,
                    "page_number": page_idx + 1,
                    "section_path": section_path,
                    "chunk_size": len(chunk_doc.page_content)
                })
                
                chunks.append(chunk_doc)
    
    print(f"📑 Generados {len(chunks)} chunks para {doc_name}")
    return chunks

def process_markdown_files(file_paths: List[str]) -> List[Document]:
    """
    Procesa múltiples archivos Markdown y devuelve todos los chunks.
    
    Args:
        file_paths: Lista de rutas de archivos a procesar
        
    Returns:
        Lista de todos los documentos procesados
    """
    all_documents = []
    
    print(f"🔄 Procesando {len(file_paths)} archivos Markdown...")
    
    for file_path in tqdm(file_paths, desc="📖 Parseando archivos"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            doc_name = normalize_filename(file_path)
            chunks = split_markdown_document(content, doc_name)
            all_documents.extend(chunks)
            
        except Exception as e:
            print(f"❌ Error procesando {normalize_filename(file_path)}: {e}")
    
    print(f"✅ Total de chunks generados: {len(all_documents)}")
    return all_documents

# -------------------------------------------------------------------------#
# 5. GESTIÓN DE EMBEDDINGS Y BASE DE DATOS VECTORIAL
# -------------------------------------------------------------------------#

def get_embeddings() -> OllamaEmbeddings:
    """
    Obtiene la instancia de embeddings (singleton pattern).
    
    Returns:
        Instancia de OllamaEmbeddings configurada
    """
    global _embeddings
    if _embeddings is None:
        print(f"🤖 Inicializando modelo de embeddings: {EMBEDDINGS_MODEL}")
        _embeddings = OllamaEmbeddings(model=EMBEDDINGS_MODEL)
    return _embeddings

def create_vector_database(documents: List[Document]) -> Chroma:
    """
    Crea una nueva base de datos vectorial a partir de documentos.
    
    Args:
        documents: Lista de documentos a indexar
        
    Returns:
        Instancia de Chroma configurada
    """
    print(f"🗄️ Creando base de datos vectorial en: {DB_DIR}")
    
    embeddings = get_embeddings()
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(DB_DIR)
    )
    
    print(f"✅ Base de datos creada con {len(documents)} documentos")
    return vector_store

def load_existing_database() -> Chroma:
    """
    Carga una base de datos vectorial existente.
    
    Returns:
        Instancia de Chroma cargada desde disco
    """
    print(f"📂 Cargando base de datos existente desde: {DB_DIR}")
    
    embeddings = get_embeddings()
    vector_store = Chroma(
        persist_directory=str(DB_DIR),
        embedding_function=embeddings
    )
    
    return vector_store

# -------------------------------------------------------------------------#
# 6. PIPELINE PRINCIPAL
# -------------------------------------------------------------------------#

def init_or_update() -> Chroma:
    """
    Inicializa o actualiza la base de datos vectorial.
    
    Flujo:
    1. Verifica si existe el directorio de datos
    2. Lista todos los archivos Markdown
    3. Identifica archivos nuevos/modificados
    4. Crea o actualiza la base de datos según sea necesario
    
    Returns:
        Instancia de Chroma lista para usar
        
    Raises:
        FileNotFoundError: Si no existe el directorio de datos
    """
    # Verificar que existe el directorio de datos
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Directorio de datos no encontrado: {DATA_DIR}")
    
    print(f"🔍 Buscando archivos Markdown en: {DATA_DIR}")
    all_files = list_markdown_files(str(DATA_DIR))
    
    if not all_files:
        print("⚠️  No se encontraron archivos Markdown")
        return load_existing_database() if DB_DIR.exists() else None
    
    print(f"📁 Encontrados {len(all_files)} archivos Markdown")
    
    # Cargar log de procesamiento
    processed_log = load_processing_log()
    new_files = identify_new_files(all_files, processed_log)
    
    # Decidir si crear nueva BD o actualizar existente
    db_exists = DB_DIR.exists() and any(DB_DIR.iterdir())
    
    if not db_exists:
        print("🆕 Creando nueva base de datos...")
        documents = process_markdown_files(all_files)
        
        if not documents:
            raise ValueError("No se pudieron procesar documentos")
            
        vector_store = create_vector_database(documents)
        update_processing_log({}, all_files)
        
    else:
        print("🔄 Cargando base de datos existente...")
        vector_store = load_existing_database()
        
        if new_files:
            print(f"📥 Archivos nuevos/actualizados: {len(new_files)}")
            new_documents = process_markdown_files(new_files)
            
            if new_documents:
                print("➕ Añadiendo documentos a la base de datos...")
                vector_store.add_documents(new_documents)
                update_processing_log(processed_log, new_files)
                print("✅ Base de datos actualizada")
            else:
                print("⚠️  No se generaron documentos nuevos")
        else:
            print("✅ Base de datos actualizada - sin cambios")
    
    return vector_store

def get_retriever(k: int = 4):
    """
    Obtiene un retriever configurado (singleton pattern).
    
    Args:
        k: Número de documentos a recuperar por consulta
        
    Returns:
        Retriever configurado y listo para usar
    """
    global _retriever
    
    if _retriever is None:
        print(f"🔧 Inicializando retriever (k={k})...")
        vector_store = init_or_update()
        
        if vector_store is None:
            raise RuntimeError("No se pudo inicializar la base de datos vectorial")
            
        _retriever = vector_store.as_retriever(
            search_kwargs={"k": k}
        )
        print("✅ Retriever inicializado")
    
    return _retriever

# -------------------------------------------------------------------------#
# 7. FUNCIONES DE UTILIDAD PÚBLICA
# -------------------------------------------------------------------------#

def get_database_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas de la base de datos vectorial.
    
    Returns:
        Diccionario con estadísticas de la base de datos
    """
    if not DB_DIR.exists():
        return {"status": "no_database", "document_count": 0}
    
    try:
        vector_store = load_existing_database()
        # Intentar obtener el conteo (esto puede variar según la versión de Chroma)
        collection = vector_store._collection
        count = collection.count()
        
        processed_log = load_processing_log()
        
        return {
            "status": "active",
            "document_count": count,
            "processed_files": len(processed_log),
            "last_update": max(
                [info.get("processed", "") for info in processed_log.values()],
                default="never"
            )
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def reset_database() -> bool:
    """
    Resetea completamente la base de datos vectorial.
    
    Returns:
        True si se reseteo correctamente, False en caso contrario
    """
    try:
        if DB_DIR.exists():
            import shutil
            shutil.rmtree(DB_DIR)
            print("🗑️  Base de datos eliminada")
        
        # Resetear singleton
        global _retriever
        _retriever = None
        
        return True
    except Exception as e:
        print(f"❌ Error reseteando base de datos: {e}")
        return False
