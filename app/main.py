from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional, Annotated
from schemas import UserPrompt
app = FastAPI()

@app.post("/tutor/analizar")
async def analyze_content(enunciado: Annotated[str, Form(..., description = "El enunciado de la actividad academica.")],
                          rubrica: Annotated[str, Form(..., description = "La rúbrica para evaluar la actividad.")],
                          pregunta: Annotated[str, Form(..., description = "La pregunta específica sobre la actividad.")],
                          entregable: Annotated[Optional[UploadFile], File(..., description = "Si desea subir un archivo entregable PDF o DOCX coloque su archivo aqui.")] = None,
                          entregable_texto: Annotated[Optional[str], Form(..., description = "Si desea subir su entregable como texto por favor coloquelo aqui.")] = None):
    return {"message": "Hello World"}