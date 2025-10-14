from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class Health(BaseModel):
    status: str = "ok"

# -------------------------------------------------
# NOTA Pydantic v2:
# - No definas campos que empiecen con "_".
# - Si algún cliente te enviara JSON con "_campo",
#   usa alias: campo: str = Field(alias="_campo")
#   y agrega model_config = ConfigDict(populate_by_name=True)
# -------------------------------------------------

class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    email: str
    password: str  # Si algún cliente enviara "_password", harías: password: str = Field(alias="_password")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    role: str

class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    email: str
    password: str
    nombre: Optional[str] = None
    telefono: Optional[str] = None

class UsuarioOut(BaseModel):
    id: str
    email: str
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    role: str
    status: int

class CrearUsuarioAdminRequest(RegisterRequest):
    # Si algún cliente te enviara "_password", usar:
    # password: str = Field(alias="_password")
    role: str  # "admin" | "cliente"

class UpdateUsuarioRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    status: Optional[int] = None  # 0/1
    role: Optional[str] = None    # "admin" | "cliente"
