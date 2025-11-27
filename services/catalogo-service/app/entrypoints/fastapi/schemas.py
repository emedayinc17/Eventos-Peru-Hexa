from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class TipoEvento(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str] = None
    status: int = 1


class Servicio(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str] = None
    tipo_evento_id: Optional[str] = None
    status: int = 1


class OpcionServicio(BaseModel):
    id: str
    servicio_id: str
    nombre: str
    detalles: Optional[Dict[str, Any]] = None
    status: int = 1


class OpcionConPrecio(OpcionServicio):
    moneda: Optional[str]
    monto: float


class Paquete(BaseModel):
    id: Optional[str]
    codigo: Optional[str]
    nombre: Optional[str]
    descripcion: Optional[str] = None
    status: Optional[int] = 1


class PaqueteConPrecioTotal(Paquete):
    moneda: Optional[str]
    monto_total_vigente: float


class ItemPaquete(BaseModel):
    opcion_servicio_id: str
    cantidad: int
    moneda: Optional[str]
    monto: float


class PaqueteDetalle(Paquete):
    items: List[ItemPaquete]


class ErrorResponse(BaseModel):
    detail: str
