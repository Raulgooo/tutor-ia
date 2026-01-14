SOCRAT-AI 🎓
Socrat-AI es un tutor académico diseñado para guiar a los estudiantes sin entregar respuestas directas. Utiliza el método socrático para fomentar el pensamiento crítico, validando la entrada del usuario contra rúbricas de evaluación y detectando intentos de fraude académico mediante una arquitectura de agentes multi-nodo.

🏗️ Arquitectura y Decisiones Técnicas
El Modelo
Se seleccionó la familia Gemini de Google por su baja latencia y alta precisión en razonamiento lógico.

Modelo Principal: gemini-1.5-flash (seleccionado por su excelente trade-off entre velocidad y rendimiento para tareas de tutoría en tiempo real).

Razonamiento: La capacidad del modelo para seguir instrucciones complejas y manejar salidas estructuradas fue determinante para la lógica de los nodos de control.

El Stack
FastAPI: Elegido por su manejo nativo de asincronía, vital para mitigar la latencia de APIs externas.

Pydantic: Motor central para la validación de contratos de datos y la estructuración de las salidas de los LLMs.

LangGraph: Implementado para orquestar un flujo de agente cíclico y controlado, permitiendo validaciones granulares que un simple System Prompt no podría garantizar.

Gemini Files API: Utilizado para el procesamiento eficiente y económico de documentos (PDF/Docx) adjuntos por el alumno.

Loguru: Gestión de logs para trazabilidad y debugging en desarrollo.

🛡️ Estrategia Anti-Fraude (Guardrails)
En lugar de confiar en un único prompt masivo propenso a prompt injection, el sistema utiliza una estructura de nodos especializados:

Nodo Guardián (Pre-Análisis): Evalúa la intención del usuario. Si detecta un intento de obtener la respuesta directa o plagio, detiene el flujo.

Nodo Tutor: Genera la guía pedagógica basada en la rúbrica y la metodología socrática.

Nodo de Post-Análisis: Un revisor independiente verifica que la respuesta del tutor no haya filtrado accidentalmente la solución y que cumpla con los estándares de calidad.

Flujo de Trabajo
Fragmento de código

graph TD
    %% Nodos principales
    Start((Inicio)) --> PreAnalysis[Pre-Análisis]
    
    %% Decisiones del Nodo de Pre-Análisis
    PreAnalysis -- "Fraude / Riesgo Alto" --> NegativeFeedback[Feedback Negativo]
    PreAnalysis -- "Seguro" --> Tutor[Tutor IA]
    
    %% Proceso de Tutoría
    Tutor --> PostAnalysis[Post-Análisis]
    
    %% Decisiones del Nodo de Post-Análisis
    PostAnalysis -- "Válido" --> End((Fin))
    PostAnalysis -- "No Válido" --> NegativeFeedback
    
    %% Salida final de error
    NegativeFeedback --> End

    %% Estilizado
    style Start fill:#f9f9f9,stroke:#333,stroke-width:2px
    style End fill:#bfb6fc,stroke:#333,stroke-width:4px
    style PreAnalysis fill:#e1f5fe,stroke:#01579b
    style Tutor fill:#e8f5e9,stroke:#2e7d32
    style PostAnalysis fill:#fff3e0,stroke:#ef6c00
    style NegativeFeedback fill:#ffebee,stroke:#c62828
📋 Contratos de Datos (Pydantic Models)
El sistema se comunica mediante estructuras estrictas para asegurar la integridad de los datos entre nodos.

PreAnalysisJudge: Determina el nivel de riesgo (1-5) y la detección de trampas.

AnalysisResult: Contiene el Chain of Thought, el output final y los Anchor References (citas directas de la rúbrica).

TutorState: El objeto de estado global que persiste la información a través del grafo de LangGraph.

Python

class AnalysisResult(BaseModel):
    chain_of_thought: str = Field(..., description="Razonamiento lógico del tutor")
    anchor_references: list[str] = Field(..., description="Fragmentos de la rúbrica utilizados")
    output: str = Field(..., description="Respuesta socrática final")
🧠 Metodología de Prompting
Se implementaron técnicas de ingeniería de prompts de última generación para maximizar la fiabilidad:

Grounding Anchors: Se obliga al modelo a citar textualmente la rúbrica o las instrucciones para reducir alucinaciones.

Chain of Thought (CoT): Cada nodo debe "pensar en voz alta" antes de entregar un resultado, mejorando la coherencia en tareas complejas.

Decisiones Booleanas: Forzamos al modelo a tomar posturas binarias (¿Es trampa? Sí/No) para evitar ambigüedades en la lógica de control.

Separación de Responsabilidades: Cada prompt se enfoca exclusivamente en una tarea (validar, enseñar o revisar), reduciendo la carga cognitiva del modelo.

🚀 Instalación y Uso
Local
Clona el repositorio: git clone ...

Instala dependencias: pip install -r requirements.txt

Configura tus variables de entorno en un archivo .env:

Fragmento de código

GOOGLE_API_KEY=tu_api_key
Ejecuta la aplicación: uvicorn main:app --reload

Docker
Bash

docker build -t socrat-ai .
docker run -p 8000:8000 --env-file .env socrat-ai
🛠️ API Endpoints
POST /tutor/analyze: Recibe el prompt, la rúbrica y archivos adjuntos (multipart).

200 OK: Retorna la respuesta del tutor.

429 Too Many Requests: Límite de cuota de Gemini alcanzado.

500 Internal Error: Error inesperado en el procesamiento.
