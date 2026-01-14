from schemas import (TutorState, 
    PreAnalysisJudge, 
    AnalysisResult, 
    NegativeFeedback, 
    PostAnalysisJudge, UserPrompt)
from config import langchain_model as model
from utils import md_to_string


async def pre_analysis_node(state: TutorState):
    sys = md_to_string("app/prompts/preanalysis.md")
    prompt = state["actual_prompt"]
    user_content = (
        f"--- CONTEXTO DE LA ACTIVIDAD ---\n"
        f"ENUNCIADO: {prompt.enunciado}\n\n"
        f"--- CRITERIOS DE EVALUACIÓN ---\n"
        f"RÚBRICA: {prompt.rubrica}\n\n"
        f"--- PETICIÓN DEL ESTUDIANTE ---\n"
        f"PREGUNTA: {prompt.pregunta}\n\n"
        f"ENTREGABLE (FRAGMENTO/TEXTO): {prompt.entregable}"
    )
    structured_llm = model.with_structured_output(PreAnalysisJudge)
    response = await structured_llm.ainvoke([{"role": "system", "content": sys}, {"role": "user", "content": user_content}])
    return {"first_judgement": response}

def route_after_pre_analysis(state: TutorState):
    judgement = state["first_judgement"]
    if judgement.cheat_detected or judgement.risk_level > 3.0:
        return "is_cheat"
    return "is_safe"

async def tutor_node(state: TutorState):
    sys = md_to_string("app/prompts/Tutor.md")
    prompt = state["actual_prompt"]
    user_content = (
        f"--- CONTEXTO DE LA ACTIVIDAD ---\n"
        f"ENUNCIADO: {prompt.enunciado}\n\n"
        f"--- CRITERIOS DE EVALUACIÓN ---\n"
        f"RÚBRICA: {prompt.rubrica}\n\n"
        f"--- PETICIÓN DEL ESTUDIANTE ---\n"
        f"PREGUNTA: {prompt.pregunta}\n\n"
        f"ENTREGABLE (FRAGMENTO/TEXTO): {prompt.entregable}"
    )
    structured_llm = model.with_structured_output(AnalysisResult)
    response = await structured_llm.ainvoke([
            {"role": "system", "content": sys},
            *state.get("messages", []),
            {"role": "user", "content": user_content}])
    return {"tutor_response": response,
        "messages": [("assistant", response.output)]}

async def negative_node(state: TutorState):
    sys = md_to_string("app/prompts/Negative.md")
    judge = state["first_judgement"]
    AI_content = (
        f"--- RESULTADO DEL TUTOR ---\n"
        f"CHAIN OF THOUGHT: {judge.chain_of_thought}\n\n"
        f"RISK LEVEL: {judge.risk_level}\n\n"
        f"CHEAT DETECTION: {judge.cheat_detected}"
    )
    structured_llm = model.with_structured_output(NegativeFeedback)
    response = await structured_llm.ainvoke([{"role": "system", "content": sys},
        {"role": "user", "content": AI_content}])
    return {"negative_feedback": response, "messages": [("assistant", response.output)]}

async def post_analysis_node(state: TutorState):
    sys = md_to_string("app/prompts/PostAnalysis.md")
    tutor_res = state["tutor_response"]
    AI_content = (
        f"--- RESULTADO DEL TUTOR ---\n"
        f"OUTPUT: {tutor_res.output}\n\n"
        f"CHAIN OF THOUGHT: {tutor_res.chain_of_thought}\n\n"
        f"ANCHOR REFERENCES: {', '.join(tutor_res.anchor_references or [])}"
    )
    structured_llm = model.with_structured_output(PostAnalysisJudge)
    response = await structured_llm.ainvoke([{"role": "system", "content": sys},
        {"role": "user", "content": AI_content}])
    return {"is_valid": response}

def route_after_post_analysis(state: TutorState):
    judgement = state["is_valid"]
    if judgement.valid_output:
        return "end_valid"
    return "end_invalid"
