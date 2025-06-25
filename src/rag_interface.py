# -------------------------------------------------------------------------#
# RAG INTERFACE - Interfaz de usuario y motor de consultas para D&D 5E
# -------------------------------------------------------------------------#

import streamlit as st
import pandas as pd
from typing import List, Dict, Any

# Importaciones desde módulos internos del proyecto
from config import (
    LANGSMITH_TRACING,
    LANGCHAIN_API_KEY,
    LANGCHAIN_PROJECT,
    LLM_MODEL,
    RETRIEVAL_K
)
from vector_pipeline import get_retriever

# Configuración de LangSmith para trazabilidad (opcional)
if LANGSMITH_TRACING:
    import os
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT

# Importaciones de LangChain
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts import ANSWER_PROMPT, DECOMPOSITION_PROMPT, SYNTHESIS_PROMPT
import re

# -------------------------------------------------------------------------#
# 1. CARGA DE MODELOS (CON CACHÉ)
# -------------------------------------------------------------------------#

@st.cache_resource
def load_model():
    """Carga el modelo LLM con caché de Streamlit para evitar recargas."""
    return OllamaLLM(model=LLM_MODEL, temperature=0)

# -------------------------------------------------------------------------#
# 2. CONFIGURACIÓN DE CADENAS DE PROCESAMIENTO
# -------------------------------------------------------------------------#

def initialize_chains(model, retriever):
    """Inicializa las cadenas de procesamiento con el modelo y retriever dados."""
    answer_chain = ANSWER_PROMPT | model | StrOutputParser()
    decomposition_chain = DECOMPOSITION_PROMPT | model | StrOutputParser()
    synthesis_chain = SYNTHESIS_PROMPT | model | StrOutputParser()
    
    return {
        "answer_chain": answer_chain,
        "decomposition_chain": decomposition_chain,
        "synthesis_chain": synthesis_chain,
        "retriever": retriever
    }

# -------------------------------------------------------------------------#
# 3. UTILIDADES
# -------------------------------------------------------------------------#

def build_context_and_sources(docs):
    """Construye el contexto con metadata y extrae las fuentes de los documentos recuperados."""
    context_parts = []
    sources = []
    seen_sources = set()
    
    for i, doc in enumerate(docs, 1):
        fn = doc.metadata.get("document_name", "desconocido")
        page = doc.metadata.get("page_number", "N/A")
        source_key = (fn, page)
        
        # Incluir metadata en el contexto para el modelo
        metadata_header = f"[FUENTE: {fn}, Página: {page}]"
        content_with_metadata = f"{metadata_header}\n{doc.page_content}"
        context_parts.append(content_with_metadata)
        
        if source_key not in seen_sources:
            path = doc.metadata.get("section_path", "")
            path_str = path if path else "Sin sección"
            snippet = (doc.page_content[:120] + "…") if len(doc.page_content) > 120 else doc.page_content
            
            sources.append({
                "Archivo": fn,
                "Página": page,
                "Sección": path_str,
                "Extracto": snippet,
            })
            seen_sources.add(source_key)
    
    return "\n\n---\n\n".join(context_parts), sources



def parse_sub_questions(text: str) -> List[str]:
    """Parsea la salida del LLM para extraer las sub-preguntas."""
    questions = re.findall(r"^\d+\.\s*(.*)", text, re.MULTILINE)
    
    if not questions:
        # Si no hay lista numerada, podría ser una única pregunta devuelta
        return [text.strip()]
        
    return [q.strip() for q in questions]

# -------------------------------------------------------------------------#
# 4. INTERFAZ DE STREAMLIT
# -------------------------------------------------------------------------#

def create_ui():
    """Configura la interfaz de usuario de Streamlit."""
    st.set_page_config(
        page_title="🐉 Chatbot D&D Avanzado",
        page_icon="🐉",
        layout="wide",
    )
    
    st.title("🐉 Asistente D&D 5ª Edición con Descomposición de Consultas")
    
    # --- UI en el Sidebar ---
    st.sidebar.header("⚙️ Opciones de Consulta")
    query_mode = st.sidebar.radio(
        "Elige el tipo de consulta:",
        ("Consulta Normal", "Descomposición Secuencial"),
        help="**Consulta Normal**: Rápida y directa. Ideal para preguntas simples.\n\n"
             "**Descomposición Secuencial**: Descompone preguntas complejas en sub-preguntas. Más lento pero mucho más preciso para consultas que involucran múltiples conceptos."
    )
    
    return query_mode

# -------------------------------------------------------------------------#
# 5. LÓGICA PRINCIPAL DE PROCESAMIENTO
# -------------------------------------------------------------------------#

def process_normal_query(chains, prompt):
    """Procesa una consulta normal sin descomposición."""
    with st.spinner("🔍 Recuperando información y generando respuesta..."):
        docs = chains["retriever"].invoke(prompt)
        context, sources = build_context_and_sources(docs)
        answer = chains["answer_chain"].invoke({"context": context, "query": prompt})
        
    return answer, sources

def process_decomposition_query(chains, prompt):
    """Procesa una consulta con descomposición secuencial."""
    all_sources = []
    sub_questions_and_answers = []
    
    with st.status("🧠 Analizando y descomponiendo la pregunta...", expanded=True) as status:
        # 1. Generar TODAS las sub-preguntas primero
        st.write("Generando plan de consulta completo...")
        sub_questions_text = chains["decomposition_chain"].invoke({"query": prompt})
        sub_questions = parse_sub_questions(sub_questions_text)
        
        # Si solo hay una pregunta, no hubo descomposición
        if len(sub_questions) == 1 and sub_questions[0] == prompt:
            status.update(label="La pregunta es simple. Procediendo con consulta normal.", state="complete", expanded=False)
            return process_normal_query(chains, prompt)
        else:
            status.update(label=f"Plan generado: {len(sub_questions)} sub-preguntas.", state="running", expanded=True)
        
        # 2. Procesar cada sub-pregunta secuencialmente con contexto acumulado
        for i, sub_q in enumerate(sub_questions):
            st.write(f"**Paso {i+1}/{len(sub_questions)}: Respondiendo a _'{sub_q}'_**")
            
            # Recuperar documentos para la sub-pregunta
            docs = chains["retriever"].invoke(sub_q)
            context, sources = build_context_and_sources(docs)
            
            # Construir contexto histórico de sub-preguntas anteriores
            historical_context = ""
            if sub_questions_and_answers:
                historical_context = "\n\nINFORMACIÓN DE SUB-PREGUNTAS ANTERIORES:\n"
                for prev_q, prev_a in sub_questions_and_answers:
                    historical_context += f"Pregunta: {prev_q}\nRespuesta: {prev_a}\n\n"
            
            # Generar respuesta usando el contexto ampliado
            extended_context = context + historical_context
            sub_answer = chains["answer_chain"].invoke({
                "context": extended_context, 
                "query": sub_q
            })
            
            # Guardar la sub-pregunta y su respuesta
            sub_questions_and_answers.append((sub_q, sub_answer))
            all_sources.extend(sources)
        
        # 3. Recuperar contexto para la pregunta original
        status.update(label="Recuperando contexto para la pregunta original...", state="running")
        original_docs = chains["retriever"].invoke(prompt)
        original_context, original_sources = build_context_and_sources(original_docs)
        all_sources.extend(original_sources)
        
        # 4. Sintetizar respuesta final con TODA la información
        status.update(label="Sintetizando la respuesta final...", state="running")
        st.write("✍️ Creando la respuesta final integrando todo el conocimiento...")
        
        # Construir el contexto completo de sub-preguntas
        accumulated_context = ""
        for sub_q, sub_a in sub_questions_and_answers:
            accumulated_context += f"Sub-pregunta: {sub_q}\nRespuesta: {sub_a}\n\n"
        
        final_answer = chains["synthesis_chain"].invoke({
            "original_query": prompt,
            "subquerys": accumulated_context,
            "context": original_context
        })
        
        status.update(label="¡Respuesta completada!", state="complete", expanded=False)
    
    return final_answer, all_sources
# -------------------------------------------------------------------------#
# 6. PUNTO DE ENTRADA PRINCIPAL
# -------------------------------------------------------------------------#

def main():
    """Función principal que ejecuta la aplicación."""
    # Configurar la interfaz de usuario
    query_mode = create_ui()
    
    # Configurar el historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Mostrar historial de mensajes
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if "sources" in m and m["sources"]:
                with st.expander("📚 Fuentes Consultadas"):
                    df = pd.DataFrame(m["sources"])
                    st.dataframe(df, hide_index=True, use_container_width=True)
    
    # Cargar modelo y retriever
    model = load_model()
    retriever = get_retriever(k=RETRIEVAL_K)
    
    # Inicializar cadenas de procesamiento
    chains = initialize_chains(model, retriever)
    
    # Procesar entrada del usuario
    if prompt := st.chat_input("Escribe tu pregunta sobre D&D…"):
        # Añadir mensaje de usuario al historial y a la UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Mostrar mensaje del asistente
        with st.chat_message("assistant"):
            # Elegir flujo de procesamiento según modo seleccionado
            if query_mode == "Descomposición Secuencial":
                final_answer, final_sources = process_decomposition_query(chains, prompt)
            else:
                final_answer, final_sources = process_normal_query(chains, prompt)
                
            # Mostrar respuesta
            st.markdown(final_answer)
            
            # Mostrar fuentes consolidadas
            if final_sources:
                # Eliminar duplicados para la visualización final
                unique_sources = list({(d['Archivo'], d['Página']): d for d in final_sources}.values())
                df = pd.DataFrame(unique_sources)
                if not df.empty:
                    with st.expander("📚 Fuentes Consultadas"):
                        st.dataframe(df[["Archivo", "Página", "Extracto"]], hide_index=True, use_container_width=True)
            
            # Guardar en historial
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_answer,
                "sources": final_sources
            })

# Ejecutar la aplicación solo si se ejecuta directamente (no al importar)
if __name__ == "__main__":
    main()
