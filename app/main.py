from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional, Annotated
from schemas import UserPrompt
from graph import graph
import asyncio
from services.google import store_file, upload_file
from config import logger

app = FastAPI()


@app.post("/tutor/analizar")
async def analyze_content(
    enunciado: Annotated[str, Form(..., description="El enunciado de la actividad academica.")],
    rubrica: Annotated[str, Form(..., description="La rúbrica para evaluar la actividad.")],
    pregunta: Annotated[str, Form(..., description="La pregunta específica sobre la actividad.")],
    entregable: Annotated[Optional[UploadFile], File(description="Archivo entregable PDF o DOCX.")] = None,
    entregable_texto: Annotated[Optional[str], Form(description="Entregable como texto.")] = None
):
    logger.info("Se recibio una nueva solicitud de análisis de tutoría.")
    try:
        if entregable is not None:
            temp = store_file(entregable)
            obj = await upload_file(temp)
            ob = obj.uri
        else:                            
            ob = entregable_texto
            prompt_data = UserPrompt(
             enunciado=enunciado,
            rubrica=rubrica,
             pregunta=pregunta,
            entregable=ob,
            )
        result = await graph.ainvoke({
            "actual_prompt": prompt_data, 
            "messages": []
            })
        logger.info("Análisis de tutoría completado exitosamente.")
        if result.get("negative_feedback"):
            return result["negative_feedback"]
        return result.get("tutor_response")
    except Exception as e:
        logger.error(f"Error durante el análisis de tutoría: {e}")
        if "429" in str(e):
            raise HTTPException(status_code=429, detail="Límite de tasa excedido al comunicarse con la API de Google Gemini.")
        raise HTTPException(status_code=500, detail=f"Error General")
        