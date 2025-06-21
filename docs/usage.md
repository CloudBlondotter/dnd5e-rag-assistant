Aquí tienes el contenido completo para `docs/usage.md`:

```markdown
# 📖 Guía de Uso - D&D 5E RAG Assistant

Esta guía explica cómo utilizar efectivamente el sistema RAG para consultas sobre las reglas de Dungeons & Dragons 5ª edición.

## 🚀 Inicio Rápido

### Lanzar la Aplicación

1. **Verificar que la base de datos está inicializada** (ver `setup.md`):
   ```
   python scripts/setup_db.py stats
   ```

2. **Ejecutar la aplicación**:
   ```
   python scripts/run_app.py
   ```

3. **Abrir en el navegador**: Ve a `http://localhost:8501`

4. **Primera consulta**: Escribe tu pregunta y presiona Enter

### Ejemplo de Primera Consulta

```
¿Cuáles son las características raciales de un Elfo del Bosque?
```

## 🧙‍♂️ Modos de Consulta

El sistema ofrece dos modos optimizados para diferentes tipos de preguntas:

### Consulta Normal

**Cuándo usar:**
- Preguntas directas y específicas
- Consultas sobre una sola regla o concepto
- Cuando necesitas respuestas rápidas

**Ejemplos ideales:**
```
¿Cuánto daño hace un Hacha de Batalla?
¿Qué es una Prueba de Salvación?
¿Cómo funciona el conjuro Bola de Fuego?
```

**Ventajas:**
- Respuesta inmediata (2-5 segundos)
- Directo al grano
- Ideal para consultas durante el juego

### Descomposición Secuencial

**Cuándo usar:**
- Preguntas complejas que involucran múltiples conceptos
- Consultas sobre interacciones entre reglas
- Situaciones de juego complicadas

**Ejemplos ideales:**
```
¿Cómo funciona el Ataque de Oportunidad de un Pícaro con dos armas?
¿Qué sucede cuando un Hechicero hace Metamagia con un conjuro de toque mientras está Agarrado?
¿Cómo se resuelve un combate aéreo entre un Dragón y un Paladín montado?
```

**Ventajas:**
- Análisis exhaustivo (15-30 segundos)
- Considera múltiples aspectos de las reglas
- Respuestas más precisas para situaciones complejas

**Proceso visible:**
1. 🧠 Analiza y descompone la pregunta
2. 🔍 Responde cada sub-pregunta individualmente
3. ✍️ Sintetiza una respuesta completa

## 📚 Cómo Formular Preguntas Efectivas

### Usar Terminología Oficial

**✅ Recomendado:**
```
¿Cuál es la CA de un Esqueleto?
¿Cómo funciona la Acción de Esquivar?
¿Qué es una Prueba de Característica de Fuerza?
```

**❌ Evitar:**
```
¿Cuánta defensa tiene un hueso andante?
¿Cómo esquivo ataques?
¿Cómo tiro dados de fuerza?
```

### Tipos de Preguntas por Categoría

#### **Creación de Personajes**
```
¿Cuáles son los trasfondos disponibles para un Clérigo?
¿Qué competencias obtiene un Guerrero de nivel 1?
¿Cómo se calculan los puntos de golpe iniciales?
```

#### **Combate**
```
¿Cuándo puedo usar mi Reacción?
¿Qué es un Ataque Crítico y cómo se resuelve?
¿Cómo funciona el combate con dos armas?
```

#### **Magia**
```
¿Cuáles son los componentes del conjuro Curar Heridas?
¿Qué pasa si pierdo concentración en un hechizo?
¿Cómo funciona la preparación de conjuros de Clérigo?
```

#### **Exploración**
```
¿Cómo se realizan las pruebas de Percepción?
¿Qué es una Prueba de Grupo?
¿Cómo funciona la visión en la oscuridad?
```

## 🔍 Interpretando las Respuestas

### Estructura de Respuesta Típica

Cada respuesta incluye:

1. **Respuesta directa** al inicio
2. **Explicación detallada** de las reglas
3. **Citas específicas** cuando es relevante
4. **Panel de fuentes** desplegable

### Panel de Fuentes

El panel "📚 Fuentes Consultadas" muestra:

| Columna | Descripción |
|---------|-------------|
| **Archivo** | Nombre del manual consultado |
| **Página** | Página lógica dentro del documento |
| **Sección** | Jerarquía de headers (H1 > H2 > H3) |
| **Extracto** | Fragmento del texto usado |

### Evaluando la Calidad de Respuestas

**✅ Buena respuesta:**
- Cita reglas específicas
- Incluye números de página o sección
- Explica el "por qué" además del "qué"
- Menciona excepciones relevantes

**⚠️ Respuesta limitada:**
- Dice "información no encontrada"
- Respuesta muy vaga o general
- Falta contexto específico

## 🎯 Casos de Uso Específicos

### Durante una Sesión de Juego

**Como DM:**
```
¿Cuál es la CD para trepar una pared de castillo?
¿Cómo determino la iniciativa de múltiples criaturas?
¿Qué pasa cuando un jugador quiere improvisar una acción?
```

**Como Jugador:**
```
¿Puedo lanzar un conjuro y usar mi Acción Adicional?
¿Qué modificadores aplican a mi tirada de ataque?
¿Cuándo recupero mis espacios de conjuro?
```

### Preparación de Sesión

```
¿Cuáles son todas las habilidades especiales de un Owlbear?
¿Cómo funcionan las trampas mecánicas?
¿Qué tesoros puede tener un dragón joven?
```

### Creación de Personajes

```
¿Qué razas tienen bonificación a Carisma?
¿Cuáles son todas las opciones de Trasfondo que dan competencia en Engaño?
¿Cómo multiclaseo entre Pícaro y Hechicero?
```

## ⚙️ Personalización y Configuración

### Ajustar Rendimiento

**Para hardware limitado** (editar `.env`):
```
LLM_MODEL=gemma3:4b
RETRIEVAL_K=3
CHUNK_SIZE=600
```

**Para máximo rendimiento** (hardware potente):
```
LLM_MODEL=gemma2:9b
RETRIEVAL_K=7
CHUNK_SIZE=1000
```

### Modificar Prompts

Los prompts están en `src/rag_interface.py`:

- **ANSWER_PROMPT**: Controla respuestas normales
- **DECOMPOSITION_PROMPT**: Controla descomposición de preguntas
- **SYNTHESIS_PROMPT**: Controla síntesis final

### Añadir Más Documentos

```
# Añadir un manual específico
python scripts/setup_db.py add "nuevo-manual.md"

# Actualizar toda la base de datos
python scripts/setup_db.py init
```

## 🔧 Solución de Problemas de Uso

### "No se encontró información relevante"

**Posibles causas:**
- Pregunta demasiado específica o técnica
- Información no está en los documentos cargados
- Terminología no estándar

**Soluciones:**
```
# Verificar qué documentos están cargados
python scripts/setup_db.py stats

# Reformular la pregunta
# En lugar de: "¿Cómo funciona el hechizo de fuego mágico?"
# Usar: "¿Cómo funciona el conjuro Bola de Fuego?"
```

### Respuestas Inconsistentes

**Para mejorar consistencia:**

1. **Usar modo Descomposición Secuencial** para preguntas complejas
2. **Ser más específico** en las preguntas
3. **Verificar las fuentes** en el panel desplegable

### Rendimiento Lento

**Optimizaciones:**

```
# Verificar estado de Ollama
ollama list

# Usar modelo más ligero temporalmente
LLM_MODEL=gemma3:4b

# Reducir documentos recuperados
RETRIEVAL_K=3
```

## 🎲 Mejores Prácticas

### Para DMs

1. **Preparar preguntas frecuentes** antes de la sesión
2. **Usar marcadores** para reglas que consultas repetidamente
3. **Verificar interpretaciones** con fuentes originales para decisiones importantes

### Para Jugadores

1. **Consultar durante descansos** para no interrumpir el flujo
2. **Entender las reglas** en lugar de memorizarlas
3. **Compartir hallazgos** útiles con otros jugadores

### Para Grupos

1. **Designar un "consultor de reglas"** que use el sistema
2. **Establecer límites de tiempo** para consultas durante combate
3. **Usar el sistema para resolver disputas** de reglas

## 📈 Funcionalidades Avanzadas

### Historial de Conversación

- El sistema mantiene historial dentro de la sesión
- Puedes hacer preguntas de seguimiento
- El contexto se preserva durante la conversación

### Exportar Información

Para guardar respuestas importantes:
1. Copia el texto de la respuesta
2. Usa las fuentes del panel para referencias
3. Crea tu propio documento de "reglas de la casa"

### Validación Cruzada

Cuando tengas dudas:
1. Consulta las fuentes originales mostradas
2. Compara con otras interpretaciones
3. Haz preguntas de seguimiento para clarificar

## 🤝 Contribuir y Mejorar

### Reportar Problemas

Si encuentras respuestas incorrectas:
1. Anota la pregunta exacta
2. Copia la respuesta problemática
3. Verifica las fuentes consultadas
4. Reporta en GitHub Issues

### Sugerir Mejoras

- Nuevos tipos de preguntas frecuentes
- Mejoras en los prompts
- Documentos adicionales a incluir

---

**🎲 ¡Domina las reglas de D&D 5E con tu asistente RAG!**

*Recuerda: Este sistema es una herramienta de apoyo. Para decisiones oficiales en torneos o juego competitivo, siempre consulta los manuales originales.*
```