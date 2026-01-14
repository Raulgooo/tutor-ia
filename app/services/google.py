from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
from pathlib import Path
from fastapi import UploadFile
import shutil
import tempfile
from config import google_client as client

# Función para validar extensiones de archivo
def validate_extension(filename: Path, allowed_extensions: list[str]) -> bool:
    return filename.suffix.lower() in allowed_extensions

def store_file(file: UploadFile) -> str:
    try:
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_path = Path(file.filename)
        if not validate_extension(file_path, allowed_extensions):
            raise ValueError("Extension no permitida (Solo PDF, DOCX, TXT)")
        # Creamos el archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_path.suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_route = tmp.name
        return temp_route
    except Exception as e:
        if 'temp_route' in locals() and os.path.exists(temp_route):
            os.remove(temp_route)
        raise e
# Subir el archivo del entregable a gemini
async def upload_file(file_path: str):
    try:
        # Usamos el path que hizo store_file
        task = client.files.upload(file=file_path)
        # Borrar Temp del Server
        if os.path.exists(file_path):
            os.remove(file_path)    
        return task
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return str(e)