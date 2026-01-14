from pydantic import BaseModel

class UserPrompt(BaseModel):
    enunciado: str
    rubrica: str
    pregunta: str
    entregable: str