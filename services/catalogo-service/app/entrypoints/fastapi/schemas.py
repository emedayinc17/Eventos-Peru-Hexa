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
    # Convenience fields provided by the list endpoint to avoid extra requests from the UI
    categoria: Optional[str] = None
    precio_unitario: Optional[float] = None
    opcion_id: Optional[str] = None


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
    # Exponer tipo evento y servicios incluidos para el frontend
    tipo_evento_id: Optional[str] = None
    tipo_evento_nombre: Optional[str] = None
    servicios: Optional[List[Dict[str, Any]]] = []


class ItemPaquete(BaseModel):
    opcion_servicio_id: str
    cantidad: int
    moneda: Optional[str]
    monto: float
    # Información del servicio al que pertenece la opción (opcional)
    servicio_id: Optional[str] = None
    servicio_nombre: Optional[str] = None


class PaqueteDetalle(Paquete):
    moneda: Optional[str]
    monto_total: float
    items: List[ItemPaquete]


class ErrorResponse(BaseModel):
    detail: str
