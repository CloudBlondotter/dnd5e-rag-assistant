# 🐉 Dungeons & Dragons RAG Assistant

Sistema de Retrieval Augmented Generation (RAG) para consultas sobre las reglas de Dungeons & Dragons 5ª edición.

## 🚀 Características

- Procesamiento inteligente de documentos Markdown
- Búsqueda vectorial con embeddings
- Dos modos de consulta: normal y descomposición secuencial
- Interfaz web intuitiva con Streamlit
- Seguimiento de fuentes y citas precisas

## 📋 Requisitos

- Python 3.8+
- Ollama instalado y ejecutándose
- Modelos: `bge-m3:latest` y `gemma3:4b`

## ⚡ Instalación Rápida

1. **Clonar el repositorio**
git clone https://github.com/CloudBlondotter/dnd5e-rag-assistant.git
cd dungeons-rag


2. **Instalar dependencias**
pip install -r requirements.txt


3. **Configurar entorno**
cp .env.example .env


4. **Añadir documentos**
- Coloca tus archivos .md en `data/markdown/`


5. **Inicializar base de datos**
python scripts/setup_db.py


6. **Lanzar aplicación**
python scripts/run_app.py


## 📁 Estructura del Proyecto

- `src/` - Código fuente principal
- `data/markdown/` - Documentos fuente en Markdown
- `storage/` - Base de datos vectorial y logs
- `scripts/` - Scripts de utilidad
- `docs/` - Documentación adicional

## 🎯 Uso

### Consulta Normal
Ideal para preguntas simples y directas.

### Descomposición Secuencial
Para consultas complejas que involucran múltiples conceptos.


## 📄 Licencia

MIT License
