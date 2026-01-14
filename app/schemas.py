from pydantic import BaseModel, Field
from typing import TypedDict, List, Optional, Annotated
import operator

class UserPrompt(BaseModel):
    enunciado: str = Field(..., description="El enunciado o instrucción de la actividad academica.")
    rubrica: str = Field(..., description="La rúbrica para evaluar la actividad.")
    pregunta: str = Field(..., description="La pregunta específica sobre la actividad.")
    entregable: Optional[str] = Field(None, description="El entregable proporcionado por el estudiante, puede ser texto o un name relacionado a un archivo de GEMINI FILES API.")

class PreAnalysisJudge(BaseModel):
    chain_of_thought: str = Field(..., description="El razonamiento del modelo sobre el análisis preliminar.")
    risk_level: int = Field(..., description="Nivel de riesgo asignado a la petición del usuario, en una escala del 1 al 5.")
    cheat_detected: bool = Field(..., description="Indica si se detectó alguna forma de trampa o plagio en la petición del usuario.")

class NegativeFeedback(BaseModel):
    output: str = Field(..., description="Respuesta negativa al usuario. Solo se le niega su peticion sin dar detalles sobre internos del sistema. Otorgar sugerencias o alternativas cuando aplique.")

class AnalysisResult(BaseModel):
    chain_of_thought: str = Field(..., description="El razonamiento del modelo para generar la respuesta del tutor.")
    anchor_references: list[str] = Field(..., description="Lista de referencias ancla utilizadas para fundamentar la respuesta del tutor.(Fragmentos de la rubrica, instrucciones de la actividad.)")
    output: str = Field(..., description="Respuesta generada por el tutor basada en la petición del usuario y la rúbrica proporcionada.")

class PostAnalysisJudge(BaseModel):
    valid_output: bool = Field(..., description="Indica si la respuesta generada por el tutor es válida y adecuada según la rúbrica y el contexto.")
    chain_of_thought: str = Field(..., description="El razonamiento del modelo para determinar si la respuesta fue valida")

class TutorState(TypedDict):
    actual_prompt: UserPrompt
    first_judgement: Optional[PreAnalysisJudge] 
    negative_feedback: Optional[NegativeFeedback]
    tutor_response: Optional[AnalysisResult]
    is_valid: Optional[PostAnalysisJudge]
    