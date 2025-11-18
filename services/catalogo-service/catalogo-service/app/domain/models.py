# created by emeday 2025 - corrected hex alignment
from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str] = None
