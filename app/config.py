from dotenv import load_dotenv
import os
from google import genai
from langchain.chat_models import init_chat_model
from loguru import logger
import sys

load_dotenv()

google_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
if not google_client:
    raise RuntimeError("GEMINI_API_KEY environment variable not set/ No se configuro la API KEY de GEMINI")

langchain_model = init_chat_model("google_genai:gemini-2.5-pro", api_key=os.getenv("GEMINI_API_KEY"))
if not langchain_model:
    raise RuntimeError("GEMINI_API_KEY environment variable not set/ No se configuro la API KEY de GEMINI")


logger.remove()
logger.add(sys.stderr, format="<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | <level>{level: <8}</level> | <cyan>{message}</cyan>", level="INFO")
logger.add("logs/app.log", rotation="10 MB", serialize=True)

logger.info("Configuración de Google Gemini y Langchain cargada exitosamente.")