from app.schemas import (
    TutorState,
    PreAnalysisJudge,
    AnalysisResult,
    NegativeFeedback,
    PostAnalysisJudge,
    UserPrompt,
)
from app.config import langchain_model as model, logger
from app.utils import md_to_string

async def pre_analysis_node(state: TutorState):
    sys = md_to_string("app/prompts/preanalysis.md")
    logger.info("Iniciando nodo de análisis preliminar.")
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
    logger.info("Determinando ruta después del análisis preliminar.")
    judgement = state["first_judgement"]
    if judgement.cheat_detected or judgement.risk_level > 3.0:
        logger.info("Ruta seleccionada: feedback negativo debido a detección de trampa o alto nivel de riesgo.")
        return "is_cheat"
    logger.info("Ruta seleccionada: proceder con tutoría.")
    return "is_safe"

async def tutor_node(state: TutorState):
    logger.info("Iniciando nodo de tutoría.")
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
    logger.info("Nodo de tutoría completado exitosamente. Pasando a post-análisis.")
    return {"tutor_response": response}

async def negative_node(state: TutorState):
    logger.info("Iniciando nodo de feedback negativo.")
    sys = md_to_string("app/prompts/Negative.md")
    judge = state["first_judgement"]
    is_valid = state.get("is_valid")
    if is_valid is not None and is_valid.valid_output is False:
        logger.info("Generando feedback negativo debido a prompt invalido.")
        response = NegativeFeedback(valid_output="Lo siento, pero no puedo ayudarte con esa solicitud.", chain_of_thought="El prompt proporcionado es inválido o inapropiado.")
        return {"negative_feedback": response}
    else:
        AI_content = (
            f"--- RESULTADO DEL TUTOR ---\n"
            f"CHAIN OF THOUGHT: {judge.chain_of_thought}\n\n"
            f"RISK LEVEL: {judge.risk_level}\n\n"
            f"CHEAT DETECTION: {judge.cheat_detected}"
        )
        structured_llm = model.with_structured_output(NegativeFeedback)
        response = await structured_llm.ainvoke([{"role": "system", "content": sys},
            {"role": "user", "content": AI_content}])
        return {"negative_feedback": response}

async def post_analysis_node(state: TutorState):
    sys = md_to_string("app/prompts/PostAnalysis.md")
    logger.info("Iniciando nodo de post-análisis.")
    tutor_res = state["tutor_response"]
    prompt = state["actual_prompt"]
    AI_content = (
        f"--- RESULTADO DEL TUTOR ---\n"
        f"OUTPUT: {tutor_res.output}\n\n"
        f"CHAIN OF THOUGHT: {tutor_res.chain_of_thought}\n\n"
        f"ANCHOR REFERENCES: {', '.join(tutor_res.anchor_references or [])}"
        f"ORIGINAL INPUT: {prompt}"
    )
    structured_llm = model.with_structured_output(PostAnalysisJudge)
    response = await structured_llm.ainvoke([{"role": "system", "content": sys},
        {"role": "user", "content": AI_content}])
    logger.info("Nodo de post-análisis completado exitosamente.")
    return {"is_valid": response}

def route_after_post_analysis(state: TutorState):
    judgement = state["is_valid"]
    if judgement.valid_output:
        logger.info("Ruta seleccionada: salida válida, finalizando proceso.")
        return "end_valid"
    logger.info("Ruta seleccionada: salida inválida, dirigiendo a feedback negativo.")
    return "end_invalid"

