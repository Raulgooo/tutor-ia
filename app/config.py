from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from openai import OpenAI
from loguru import logger
import sys

load_dotenv()


langchain_model = ChatOpenAI(model="gpt-5.2", api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1")


graph_config = {"recursion_limit": 10}

allowed_extensions = ['.pdf', '.docx', '.txt']

logger.remove()
logger.add(sys.stderr, format="<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | <level>{level: <8}</level> | <cyan>{message}</cyan>", level="INFO")
logger.add("logs/app.log", rotation="10 MB", serialize=True)

logger.info("Configuración de OpenAI cargada exitosamente.")