## 📐 Modelos y Contratos de Datos

### Arquitectura de Comunicación

Los contratos de datos implementados con **Pydantic** son el núcleo de la comunicación entre agentes del sistema. Cada nodo de LangGraph recibe un objeto `State` (diccionario tipado) que circula entre todos los nodos, permitiendo que tanto la lógica determinista como la lógica impulsada por IA operen sobre estructuras bien definidas.

Esta arquitectura garantiza:
- ✅ **Type Safety**: Validación automática de tipos en tiempo de ejecución
- ✅ **Structured Outputs**: El LLM genera objetos directamente utilizables (vía `llm_with_structured_output`)
- ✅ **Trazabilidad**: Cada nodo documenta su razonamiento mediante `chain_of_thought`
- ✅ **Modularidad**: Contratos especializados para cada fase del flujo

---

### 📥 Entrada del Usuario

```python
class UserPrompt(BaseModel):
    enunciado: str = Field(
        ..., 
        description="El enunciado o instrucción de la actividad academica."
    )
    rubrica: str = Field(
        ..., 
        description="La rúbrica para evaluar la actividad."
    )
    pregunta: str = Field(
        ..., 
        description="La pregunta específica sobre la actividad."
    )
    entregable: Optional[str] = Field(
        None, 
        description="El entregable proporcionado por el estudiante, puede ser texto o un name relacionado a un archivo de GEMINI FILES API."
    )
```

**Propósito**: Modela la entrada del usuario al sistema, incluyendo el contexto de la actividad académica y el entregable del estudiante.

**Decisiones de diseño**:
- `entregable` es opcional y puede ser texto plano o una referencia a un archivo procesado por Gemini Files API
- Todos los campos son requeridos excepto `entregable`. Decidi hacer entregable multi-input(pdf,docx y txt) para permitir pruebas mas interesantes con el modelo.

---

### 🔍 Nodo de Pre-Análisis

```python
class PreAnalysisJudge(BaseModel):
    chain_of_thought: str = Field(
        ..., 
        description="El razonamiento del modelo sobre el análisis preliminar."
    )
    risk_level: float = Field(
        ..., 
        description="Nivel de riesgo asignado a la petición del usuario, en una escala del 1 al 5."
    )
    cheat_detected: bool = Field(
        ..., 
        description="Indica si se detectó alguna forma de trampa o plagio en la petición del usuario."
    )
```

**Propósito**: Actúa como guardián inicial del sistema, evaluando la intención del usuario antes de proceder con la tutoría.

**Decisiones de diseño**:
- `risk_level` es un `float` que permite decisiones graduales (no todo es blanco/negro)
- `cheat_detected` fuerza una decisión binaria clara para el flujo condicional
- `chain_of_thought` expone el razonamiento para debugging y auditoría

---

### 🎓 Nodo del Tutor

```python
class AnalysisResult(BaseModel):
    chain_of_thought: str = Field(
        ..., 
        description="Razonamiento para generar la respuesta socrática"
    )
    anchor_references: list[str] = Field(
        ..., 
        description="Fragmentos textuales de la rúbrica/instrucciones utilizados"
    )
    output: str = Field(
        ..., 
        description="Respuesta socrática generada para el estudiante"
    )
```

**Propósito**: Genera la guía pedagógica basada en el método socrático y la rúbrica proporcionada.

**Decisiones de diseño**:
- `anchor_references` implementa **Grounding**: obliga al modelo a citar textualmente la rúbrica, reduciendo alucinaciones
- La lista de referencias permite trazabilidad de qué criterios académicos se aplicaron
- Separación clara entre el razonamiento interno (`chain_of_thought`) y la salida al usuario (`output`)

---

### ❌ Nodo de Feedback Negativo

```python
class NegativeFeedback(BaseModel):
    output: str = Field(
        ..., 
        description="Mensaje al usuario rechazando la petición sin revelar internos del sistema. Incluye sugerencias cuando sea apropiado"
    )
```

**Propósito**: Maneja casos donde se detecta fraude o la petición no puede ser procesada.

**Decisiones de diseño**:
- Diseño minimalista: un solo campo para mantener el mensaje simple
- Instrucción explícita de **no revelar detalles internos** (evita que usuarios aprendan a evadir el sistema)
- Fomenta respuestas constructivas con alternativas válidas

---

### ✅ Nodo de Post-Análisis

```python
class PostAnalysisJudge(BaseModel):
    valid_output: bool = Field(
        ..., 
        description="Indica si la respuesta del tutor cumple estándares de calidad y no filtra soluciones"
    )
    chain_of_thought: str = Field(
        ..., 
        description="Razonamiento para determinar la validez de la respuesta"
    )
```

**Propósito**: Revisor independiente que verifica la calidad de la respuesta del tutor.

**Decisiones de diseño**:
- Actúa como **segunda línea de defensa**: previene que respuestas inadecuadas lleguen al usuario
- `valid_output` determina si el flujo continúa o se detiene
- Implementa el principio de **separación de responsabilidades**: el tutor crea, el post-análisis valida

---

### 🔄 Estado Global del Sistema

```python
class TutorState(TypedDict):
    actual_prompt: UserPrompt
    first_judgement: Optional[PreAnalysisJudge]
    negative_feedback: Optional[NegativeFeedback]
    tutor_response: Optional[AnalysisResult]
    is_valid: Optional[PostAnalysisJudge]
```

**Propósito**: Contenedor de estado que persiste información a través de todo el grafo de LangGraph.

**Estructura de datos**:
- **Entrada del usuario**: `actual_prompt` contiene toda la información de la solicitud del estudiante
- **Salidas de nodos**: Todos los campos `Optional` se populan conforme avanza el flujo
- **Flujo no lineal**: No todos los campos se llenan en cada ejecución (ej. si se detecta fraude, `tutor_response` permanece `None`)

**Ventajas de TypedDict**:
- Compatible con la API de LangGraph
- Permite tipado estático sin la sobrecarga de una clase completa
- Los campos `Optional` modelan explícitamente los diferentes caminos del flujo
- Diseño minimalista: solo contiene lo esencial para el flujo del grafo

---

### 🔧 Integración con LLM

Todos estos modelos se utilizan con `llm_with_structured_output`, lo que garantiza que el modelo de lenguaje siempre retorne objetos JSON válidos que Pydantic puede deserializar automáticamente:

```python
# Ejemplo de uso en un nodo
structured_llm = llm.with_structured_output(PreAnalysisJudge)
result: PreAnalysisJudge = structured_llm.invoke(prompt)

# El objeto 'result' es directamente utilizable
if result.cheat_detected or result.risk_level >= 4:
    # Detener flujo
    pass
```

Esta arquitectura elimina la necesidad de parsing manual de respuestas del LLM, reduciendo errores y mejorando la mantenibilidad del código.