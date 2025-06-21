# 🛠️ Guía de Configuración - D&D 5E RAG Assistant

Esta guía te llevará paso a paso desde la instalación hasta tener el sistema funcionando completamente.

## 📋 Requisitos Previos

### Software Necesario

- **Python 3.8+** (recomendado 3.10+)
- **Ollama** instalado y ejecutándose
- **Git** (para clonar el repositorio)

### Modelos Requeridos

El sistema necesita estos modelos de Ollama:

```
# Modelo de embeddings
ollama pull bge-m3:latest

# Modelo de lenguaje 
ollama pull gemma3:4b        
```

### Verificar Ollama

```
# Verificar que Ollama está ejecutándose
ollama list

# Debería mostrar los modelos instalados
```

## 🚀 Instalación

### 1. Clonar el Repositorio

```
git clone https://github.com/tu-usuario/dnd5e-rag-assistant.git
cd dnd5e-rag-assistant
```

### 2. Crear Entorno Virtual

```
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (macOS/Linux)
source venv/bin/activate
```

### 3. Instalar Dependencias

```
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```
# Copiar archivo de configuración
cp .env.example .env

# Editar configuraciones (opcional)
notepad .env  # Windows
nano .env     # macOS/Linux
```

#### Variables Principales

```
# Modelos (ajustar según tu hardware)
EMBEDDINGS_MODEL=bge-m3:latest
LLM_MODEL=gemma2:9b

# Configuración RAG
CHUNK_SIZE=800
CHUNK_OVERLAP=100
RETRIEVAL_K=4

# LangSmith (opcional - para debugging)
LANGSMITH_TRACING=false
LANGCHAIN_API_KEY=tu_api_key_aqui
LANGCHAIN_PROJECT=dungeons-manual
```

## 📁 Preparar Documentos

### Estructura de Datos

```
data/
└── markdown/
    ├── manual-del-jugador.md
    ├── guia-del-dungeon-master.md
    └── manual-de-monstruos.md
```

### Formato de Documentos

Los archivos Markdown deben usar **separadores de página**:

```
# Capítulo 1: Creación de Personajes

Contenido del capítulo...

---

# Capítulo 2: Razas

Contenido del siguiente capítulo...

---
```

### Obtener Documentos

1. **Convierte tus PDFs** a Markdown usando herramientas como:
   - [Pandoc](https://pandoc.org/)
   - [pdf2md](https://github.com/jzillmann/pdf-to-markdown)
   - Conversión manual
   - [LlamaParse](https://www.llamaindex.ai/llamaparse)

2. **Coloca los archivos** en `data/markdown/`

3. **Verifica el formato** con separadores `---`

## 🗄️ Inicializar Base de Datos

### Verificar Prerrequisitos

```
python scripts/setup_db.py check
```

**Salida esperada:**
```
🔍 Verificando prerrequisitos...
✅ Encontrados X archivos Markdown
✅ Dependencias Python disponibles
✅ Todos los prerrequisitos están OK
```

### Crear Base de Datos

```
# Inicialización completa
python scripts/setup_db.py init
```

**Proceso esperado:**
```
🐉 Inicializando base de datos de D&D 5E...
📁 Directorio de datos: data/markdown
🗄️ Directorio de BD: storage/db_dungeons
🆕 Creando nueva base de datos...
🔄 Procesando X archivos Markdown...
📖 Parseando archivos: 100%
✅ Base de datos inicializada correctamente!
```

### Verificar Instalación

```
# Ver estadísticas
python scripts/setup_db.py stats
```

**Salida esperada:**
```
📊 Estadísticas de la Base de Datos
📄 Documentos indexados: 1,247
📁 Archivos procesados: 3
🕐 Última actualización: 2025-01-15 10:30:45
💾 Ubicación: storage/db_dungeons
📦 Tamaño en disco: 45.2 MB
```

## ▶️ Ejecutar la Aplicación

### Lanzar Streamlit

```
python scripts/run_app.py
```

### Acceder a la Interfaz

1. Abre tu navegador
2. Ve a `http://localhost:8501`
3. ¡Deberías ver la interfaz de D&D RAG Assistant!

### Primera Consulta

Prueba con una pregunta simple:
```
¿Cuáles son las características de un Elfo?
```

## 🔧 Solución de Problemas

### Error: "No module named 'src'"

**Causa:** Estructura de archivos incorrecta o paths mal configurados.

**Solución:**
```
# Verificar estructura
ls -la src/
# Debe mostrar: config.py, vector_pipeline.py, rag_interface.py, etc.

# Ejecutar desde el directorio raíz
cd dnd5e-rag-assistant
python scripts/setup_db.py check
```

### Error: "No se encontraron archivos Markdown"

**Causa:** No hay documentos en `data/markdown/`

**Solución:**
```
# Verificar archivos
ls -la data/markdown/
# Debe mostrar archivos .md

# Añadir archivos de prueba
echo "# Documento de Prueba\n\nContenido..." > data/markdown/test.md
```

### Error de Conexión con Ollama

**Causa:** Ollama no está ejecutándose o modelos no instalados.

**Solución:**
```
# Verificar Ollama
ollama list

# Instalar modelos faltantes
ollama pull bge-m3:latest
ollama pull gemma2:9b

# Reiniciar Ollama si es necesario
```

### Rendimiento Lento

**Optimizaciones:**

1. **Usar modelo más ligero:**
   ```
   LLM_MODEL=gemma3:4b
   ```

2. **Reducir chunks recuperados:**
   ```
   RETRIEVAL_K=3
   ```

3. **Verificar hardware:** El sistema necesita al menos 8GB RAM para modelos grandes.

### Base de Datos Corrupta

**Resetear completamente:**
```
python scripts/setup_db.py reset
# Escribir "RESET" para confirmar

python scripts/setup_db.py init
```

## 📈 Siguientes Pasos

### Añadir Más Documentos

```
# Añadir archivo específico
python scripts/setup_db.py add nuevo-manual.md

# Actualizar base de datos completa
python scripts/setup_db.py init
```

### Configuración Avanzada

- Revisa `src/config.py` para ajustes finos
- Modifica prompts en `src/prompts.py`
- Consulta `docs/usage.md` para funcionalidades avanzadas

### Desarrollo

- Ve `docs/api.md` para documentación del código
- Contribuye siguiendo `CONTRIBUTING.md`

## 📞 Obtener Ayuda

- **Issues:** [GitHub Issues](https://github.com/tu-usuario/dnd5e-rag-assistant/issues)
- **Documentación:** Ver otros archivos en `docs/`
- **Ejemplos:** Revisar `examples/` (si existe)

---

**🎲 ¡Listo para jugar! Tu asistente de D&D está configurado y funcionando.**
```

**Instrucciones para guardarlo:**

1. Copia todo el texto anterior
2. Abre un editor de texto (Notepad, VS Code, etc.)
3. Pega el contenido
4. Guarda como `setup.md` en tu carpeta `docs/`
5. Asegúrate de que la codificación sea UTF-8 para que los emojis se vean correctamente

El archivo está listo para usar en tu repositorio GitHub[1][2].

[1] programming.project_organization
[2] programming.markdown