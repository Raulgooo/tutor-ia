from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable not set/ No se configuro la API KEY de GEMINI")
