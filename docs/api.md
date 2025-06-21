Basándome en los resultados de búsqueda sobre documentación de APIs[1][2][3][4] y tu proyecto RAG de D&D, aquí está el contenido para `docs/api.md`:

```markdown
# 🔧 Documentación Técnica - D&D 5E RAG Assistant

Esta documentación está dirigida a desarrolladores que quieren entender, modificar o contribuir al sistema.

## 📋 Arquitectura del Sistema

### Componentes Principales

```
src/
├── config.py           # Configuraciones centralizadas
├── vector_pipeline.py  # Pipeline de procesamiento de documentos
├── rag_interface.py    # Interfaz de usuario y motor de consultas
└── prompts.py         # Templates de prompts (si existe)
```

### Flujo de Datos

```
Documentos MD → vector_pipeline → ChromaDB → rag_interface → Usuario
     ↓              ↓              ↓           ↓
  Parsing      Embeddings    Almacenamiento  Consultas
```

## ⚙️ Módulo: config.py

### Variables de Configuración

| Variable | Tipo | Descripción | Por Defecto |
|----------|------|-------------|-------------|
| `PROJECT_ROOT` | Path | Directorio raíz del proyecto | Auto-detectado |
| `DATA_DIR` | Path | Directorio de archivos Markdown | `data/markdown` |
| `DB_DIR` | Path | Directorio de base de datos vectorial | `storage/db_dungeons` |
| `EMBEDDINGS_MODEL` | str | Modelo de embeddings de Ollama | `bge-m3:latest` |
| `LLM_MODEL` | str | Modelo de lenguaje de Ollama | `gemma2:9b` |
| `CHUNK_SIZE` | int | Tamaño máximo de chunks | 800 |
| `CHUNK_OVERLAP` | int | Solapamiento entre chunks | 100 |
| `RETRIEVAL_K` | int | Documentos a recuperar por consulta | 5 |

### Ejemplo de Uso

```
from config import DATA_DIR, EMBEDDINGS_MODEL

# Verificar directorio de datos
if DATA_DIR.exists():
    print(f"Datos encontrados en: {DATA_DIR}")

# Usar configuración en tu código
model = OllamaEmbeddings(model=EMBEDDINGS_MODEL)
```

## 📄 Módulo: vector_pipeline.py

### Funciones Principales

#### `init_or_update()`

**Descripción**: Inicializa o actualiza la base de datos vectorial.

**Parámetros**: Ninguno

**Retorna**: `Chroma` - Instancia de la base de datos vectorial

**Ejemplo**:
```
from vector_pipeline import init_or_update

vector_store = init_or_update()
if vector_store:
    print("Base de datos lista")
```

#### `get_retriever(k: int = 4)`

**Descripción**: Obtiene un retriever configurado (patrón singleton).

**Parámetros**:
- `k` (int): Número de documentos a recuperar por consulta

**Retorna**: Retriever de LangChain configurado

**Ejemplo**:
```
from vector_pipeline import get_retriever

retriever = get_retriever(k=5)
docs = retriever.invoke("¿Qué es un Elfo?")
```

#### `split_markdown_document(md_text: str, doc_name: str)`

**Descripción**: Divide un documento Markdown en chunks procesables.

**Parámetros**:
- `md_text` (str): Contenido completo del archivo Markdown
- `doc_name` (str): Nombre del documento para metadatos

**Retorna**: `List[Document]` - Lista de documentos procesados

**Proceso**:
1. Divide por páginas lógicas (separadas por `---`)
2. Dentro de cada página, divide por headers
3. Si los chunks son muy grandes, divide por tamaño
4. Añade metadatos completos

**Ejemplo**:
```
from vector_pipeline import split_markdown_document

with open("manual.md", "r") as f:
    content = f.read()

chunks = split_markdown_document(content, "Manual del Jugador")
print(f"Generados {len(chunks)} chunks")
```

#### `get_database_stats()`

**Descripción**: Obtiene estadísticas de la base de datos vectorial.

**Retorna**: `Dict[str, Any]` - Estadísticas de la base de datos

**Estructura de Respuesta**:
```
{
    "status": "active",           # active | no_database | error
    "document_count": 1247,       # Número de documentos indexados
    "processed_files": 3,         # Archivos procesados
    "last_update": "2025-01-15 10:30:45"  # Última actualización
}
```

### Utilidades Internas

#### `normalize_filename(path: str | bytes)`
- Normaliza nombres de archivo para usar como clave única

#### `calculate_file_hash(file_path: str)`
- Calcula hash MD5 para detectar cambios en archivos

#### `build_context_and_sources(docs)`
- Construye contexto y extrae fuentes de documentos recuperados

## 🤖 Módulo: rag_interface.py

### Cadenas de Procesamiento

#### `initialize_chains(model, retriever)`

**Descripción**: Inicializa las cadenas de procesamiento con el modelo y retriever dados.

**Parámetros**:
- `model`: Instancia del modelo LLM
- `retriever`: Retriever configurado

**Retorna**: Diccionario con cadenas configuradas

**Estructura de Retorno**:
```
{
    "answer_chain": ChatPromptTemplate | LLM | StrOutputParser,
    "decomposition_chain": ChatPromptTemplate | LLM | StrOutputParser,
    "synthesis_chain": ChatPromptTemplate | LLM | StrOutputParser,
    "retriever": retriever
}
```

### Procesamiento de Consultas

#### `process_normal_query(chains, prompt)`

**Descripción**: Procesa una consulta normal sin descomposición.

**Parámetros**:
- `chains` (dict): Cadenas de procesamiento inicializadas
- `prompt` (str): Consulta del usuario

**Retorna**: Tupla `(answer, sources)`

#### `process_decomposition_query(chains, prompt)`

**Descripción**: Procesa una consulta con descomposición secuencial.

**Parámetros**:
- `chains` (dict): Cadenas de procesamiento inicializadas  
- `prompt` (str): Consulta del usuario

**Retorna**: Tupla `(final_answer, final_sources)`

**Proceso**:
1. Genera sub-preguntas usando `decomposition_chain`
2. Responde cada sub-pregunta individualmente
3. Sintetiza respuesta final usando `synthesis_chain`

### Templates de Prompts

#### ANSWER_PROMPT
- **Propósito**: Respuestas normales y síntesis
- **Variables**: `{context}`, `{question}`

#### DECOMPOSITION_PROMPT  
- **Propósito**: Descomposición de consultas complejas
- **Variables**: `{question}`
- **Salida esperada**: Lista numerada de sub-preguntas

#### SYNTHESIS_PROMPT
- **Propósito**: Síntesis final de sub-respuestas
- **Variables**: `{original_question}`, `{subquestions}`, `{context}`

## 🛠️ Scripts de Utilidad

### setup_db.py

**Comandos disponibles**:

```
python scripts/setup_db.py init [--force]    # Inicializar BD
python scripts/setup_db.py stats             # Ver estadísticas
python scripts/setup_db.py reset             # Resetear BD
python scripts/setup_db.py check             # Verificar prerrequisitos
python scripts/setup_db.py add file1.md ...  # Añadir archivos
```

### run_app.py

**Función**: Lanza la aplicación Streamlit

```
python scripts/run_app.py
```

## 🔧 Personalización Avanzada

### Modificar Prompts

Los prompts están definidos en `rag_interface.py`. Para modificarlos:

```
# Ejemplo: Modificar prompt de respuesta
CUSTOM_ANSWER_PROMPT = ChatPromptTemplate.from_template("""
Eres un experto Dungeon Master especializado en D&D 5E.

CONTEXTO: {context}
PREGUNTA: {question}

Responde con:
1. Respuesta directa
2. Explicación detallada  
3. Ejemplos prácticos
4. Referencias específicas

RESPUESTA:
""")
```

### Añadir Nuevos Modelos

Para soportar otros modelos LLM:

```
# En config.py
LLM_PROVIDERS = {
    "ollama": OllamaLLM,
    "openai": ChatOpenAI,
    "anthropic": ChatAnthropic
}

# Uso dinámico
provider = LLM_PROVIDERS[config.LLM_PROVIDER]
model = provider(model=config.LLM_MODEL)
```

### Métricas Personalizadas

Para añadir métricas de rendimiento:

```
import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} ejecutado en {duration:.2f}s")
        return result
    return wrapper

@measure_time
def enhanced_retrieval(query):
    # Tu lógica de retrieval
    pass
```


## 🔄 Contribución

### Estructura de Commits

```
feat: añadir soporte para nuevos formatos de documento
fix: corregir error en división de chunks grandes
docs: actualizar documentación de API
refactor: optimizar consultas a base de datos
```

### Pull Requests

1. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
2. Implementar cambios con tests
3. Actualizar documentación
4. Crear PR con descripción detallada

### Estándares de Código

- **Formato**: Black (`black src/`)
- **Linting**: Flake8 (`flake8 src/`) 
- **Type hints**: mypy (`mypy src/`)
- **Docstrings**: Formato Google

## 📚 Recursos Adicionales

### Dependencies

Ver `requirements.txt` para lista completa:

```
streamlit>=1.20.0
langchain>=0.1.0
langchain-community>=0.0.20
langchain-ollama>=0.1.0
chromadb>=0.4.0
pandas>=1.5.0
tqdm>=4.64.0
```

### Configuración IDE

**VS Code** (`.vscode/settings.json`):
```
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

---

**🔧 Esta documentación está diseñada para desarrolladores que quieren contribuir o modificar el sistema RAG de D&D 5E.**
```
