from pypdf import PdfReader
from docx import Document

from app.services.parser_models import FileObj, ParserError
from app.config import logger


async def parse_file(file: FileObj) -> str:
    suffix = file.suffix
    try:
        if suffix == '.pdf':
            return _parse_pdf(file.path)
        elif suffix == '.docx':
            return _parse_docx(file.path)
        elif suffix == '.txt':
            return _parse_txt(file.path)
    except Exception as e:
        logger.error(f"Error al parsear el archivo {file.path}: {e}")
        raise ParserError(f"Error al parsear archivo: {str(e)}")

def _parse_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text.strip():
                text_parts.append(text)
        if not text_parts:
            logger.error("No se pudo extraer texto del PDF")
            raise ParserError("No se pudo extraer texto del PDF")
        return "\n".join(text_parts)
    except Exception as e:
        raise ParserError(f"Error al parsear PDF: {str(e)}")

def _parse_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        text_parts = []  
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text) 
        if not text_parts:
            raise ParserError("El documento DOCX está vacío")
        return "\n".join(text_parts)
    except Exception as e:
        raise ParserError(f"Error al parsear DOCX: {str(e)}")


def _parse_txt(file_path: str) -> str:
    try:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            with open(file_path, 'rb') as f:
                return f.read().decode('utf-8', errors='ignore')
    except Exception as e:
        raise ParserError(f"Error al leer archivo de texto: {str(e)}")
