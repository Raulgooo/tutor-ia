from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Optional, Annotated
from schemas import UserPrompt
from graph import graph
import asyncio
from utils import store_file
from config import logger, graph_config
from pydantic import ValidationError
from utils import validate_extension
from services.parser import parse_file

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Handler global para errores de validación de FastAPI."""
    logger.error(f"Error de validación de request: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Error de validación en los datos de entrada.",
            "errors": exc.errors()
        }
    )


@app.post("/tutor/analizar")
async def analyze_content(
    enunciado: Annotated[str, Form(..., description="El enunciado de la actividad academica.")],
    rubrica: Annotated[str, Form(..., description="La rúbrica para evaluar la actividad.")],
    pregunta: Annotated[str, Form(..., description="La pregunta específica sobre la actividad.")],
    entregable: Annotated[Optional[UploadFile], File(description="Archivo entregable PDF,DOCX y TXT.")] = None,
    entregable_texto: Annotated[Optional[str], Form(description="Entregable como texto.")] = None
):
    logger.info("Se recibio una nueva solicitud de análisis de tutoría.")
    try:
        # Validar que si entregable está presente, sea un archivo válido y no texto
        if entregable is not None:
            if not entregable.filename or entregable.filename.strip() == "":
                raise HTTPException(
                    status_code=400,
                    detail="El parámetro 'entregable' debe ser un archivo válido, no texto. Use 'entregable_texto' para enviar contenido como texto."
                )
            temp = store_file(entregable)
            ob = await parse_file(temp)
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
            }, config=graph_config)
        logger.info("Análisis de tutoría completado exitosamente.")
        if result.get("negative_feedback"):
            return [result["negative_feedback"], result["first_judgement"]]
        return result.get("tutor_response")
    except ValidationError as e:
        error_msg = str(e)
        logger.error(f"Error de validación de datos: {e}")
        if "Extension no permitida" in error_msg or "extension" in error_msg.lower():
            raise HTTPException(
                status_code=403,
                detail="Extension no permitida (Solo PDF, DOCX, TXT)"
            )
        raise HTTPException(
            status_code=400,
            detail=f"Datos de entrada inválidos: {error_msg}"
        )
    except RuntimeError as e:
        error_msg = str(e)
        logger.error(f"Error de configuración: {e}")
        if "API_KEY" in error_msg or "API key" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="Error de autenticación: API key no configurada o inválida."
            )
        raise HTTPException(
            status_code=500,
            detail="Error de configuración del servidor."
        )
    except asyncio.TimeoutError as e:
        logger.error(f"Timeout durante el análisis: {e}")
        raise HTTPException(
            status_code=504,
            detail="Tiempo de espera agotado al procesar la solicitud."
        )
    except TimeoutError as e:
        logger.error(f"Timeout durante el análisis: {e}")
        raise HTTPException(
            status_code=504,
            detail="Tiempo de espera agotado al procesar la solicitud."
        )
    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {e}")
        raise HTTPException(
            status_code=404,
            detail="El archivo solicitado no fue encontrado."
        )
        error_msg = str(e)
        logger.error(f"Error del sistema operativo: {e}")
        if "No space left" in error_msg or "disk" in error_msg.lower():
            raise HTTPException(
                status_code=507,
                detail="Espacio en disco insuficiente."
            )
        raise HTTPException(
            status_code=500,
            detail="Error del sistema al procesar el archivo."
        )
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        logger.error(f"Error durante el análisis de tutoría ({error_type}): {e}")
        
        if "429" in error_msg or "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="Límite de tasa excedido al comunicarse con la API."
            )
        if "403" in error_msg or "extension" in error_msg.lower():
            raise HTTPException(
            status_code=403, detail="Extension no permitida (Solo PDF, DOCX, TXT)")
        else:
            raise HTTPException(
                status_code=500,
                detail="Error interno del servidor al procesar la solicitud."
            )
        