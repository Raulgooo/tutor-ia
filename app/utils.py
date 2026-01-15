import os
from pathlib import Path
import tempfile
import shutil

from fastapi import UploadFile, HTTPException

from app.config import logger
from app.services.parser_models import FileObj


def md_to_string(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as md:
            stringmd = md.read()
        return stringmd
    except FileNotFoundError:
        return f"Error: The file {filename} was not found."
    except Exception as e:
        return f"An error occurred: {e}"

def validate_extension(filename: Path, allowed_extensions: list[str]) -> bool:
    return filename.suffix.lower() in allowed_extensions

def store_file(file: UploadFile) -> FileObj:
    try:
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_path = Path(file.filename)
        if not validate_extension(file_path, allowed_extensions):
            logger.error(f"Extension no permitida: {file_path.suffix}")
            raise HTTPException(
            status_code=403, detail="Extension no permitida (Solo PDF, DOCX, TXT")
        # Creamos el archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_path.suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_route = tmp.name
        return FileObj(path=temp_route, suffix=file_path.suffix)
    except Exception as e:
        if 'temp_route' in locals() and os.path.exists(temp_route):
            os.remove(temp_route)
        raise e

def clean_temp_file(temp_route: str):
    if os.path.exists(temp_route):
        os.remove(temp_route)