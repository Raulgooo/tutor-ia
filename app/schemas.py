from pydantic import BaseModel
from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages

class UserPrompt(BaseModel):
    enunciado: str
    rubrica: str
    pregunta: str
    entregable: str

class PreAnalysisJudge(BaseModel):
    cheat_detected: bool
    issues: list[str]

class NegativeFeedback(BaseModel):
    issue: str
    suggestion: str
    output: str

class AnalysisResult(BaseModel):
    output: str
    chain_of_thought: str
    anchor_references: list[str]

class PostAnalysisJudge(BaseModel):
    valid_output: bool
    chain_of_thought: str

class TutorState(TypedDict):
    actual_prompt: UserPrompt
    system_instructions: str
    user_id: str
    first_judgement: Optional[PreAnalysisJudge]
    messages: Annotated[List[dict], add_messages]
    negative_feedback: Optional[NegativeFeedback]
    tutor_response: Optional[AnalysisResult]
    is_valid: Optional[PostAnalysisJudge]
    