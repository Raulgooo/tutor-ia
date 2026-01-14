import genai
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
from pathlib import Path

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client()

# Función para validar extensiones de archivo
def validate_extension(filename: Path, allowed_extensions: list[str]) -> bool:
    return filename.suffix.lower() in allowed_extensions

# Subir el archivo del entregable a gemini
async def upload_file(file_path: str):
    try:
        ##FUZZY MATCHING en el futuro para evitar duplicados
        allowed_extensions = ['.pdf', '.docx', '.txt']
        if validate_extension(file_path, allowed_extensions) == False:
            raise ValueError("Invalid file extension. Only PDF, DOCX, and TXT are allowed.")
        task = client.files.upload(file=file_path)
        
        return task.name
    except Exception as e:
        return str(e)
## Implementar redis para sesiones individuales.
## CREAR FUNCION DE REDIS PARA CARRUSEL DE ARCHIVOS YA SUBIDOS.