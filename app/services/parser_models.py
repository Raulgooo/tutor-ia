from pydantic import BaseModel

class ParserError(Exception):
    pass

class FileObj(BaseModel):
    path: str
    suffix: str