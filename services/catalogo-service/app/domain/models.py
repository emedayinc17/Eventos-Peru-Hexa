"""
Modelos de dominio del Catálogo (Hexagonal Architecture)
Clases Python puras - SIN dependencias de SQLAlchemy, FastAPI, etc.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class TipoEvento:
    """Tipo de evento del catálogo (ej: Matrimonio, Cumpleaños)"""
    id: str
    nombre: str
    descripcion: Optional[str] = None
    status: int = 1


@dataclass(frozen=True)
class Servicio:
    """Servicio ofrecido para un tipo de evento (ej: Catering, Música)"""
    id: str
    nombre: str
    tipo_evento_id: str
    descripcion: Optional[str] = None
    status: int = 1


@dataclass(frozen=True)
class OpcionServicio:
    """Opción específica de un servicio con su precio vigente"""
    id: str
    servicio_id: str
    nombre: str
    moneda: str
    monto: Decimal
    detalles: Optional[Dict[str, Any]] = None
    status: int = 1


@dataclass(frozen=True)
class ItemPaquete:
    """Item individual dentro de un paquete"""
    opcion_servicio_id: str
    cantidad: int
    precio_unit_vigente: Decimal
    moneda: str
    opcion_nombre: str
    opcion_detalles: Optional[Dict[str, Any]] = None
    servicio_id: Optional[str] = None
    servicio_nombre: Optional[str] = None
    servicio_descripcion: Optional[str] = None
    proveedores: list = None  # Lista de proveedores disponibles para este servicio

    def __post_init__(self):
        """Asegurar que proveedores siempre sea una lista"""
        if self.proveedores is None:
            object.__setattr__(self, 'proveedores', [])


@dataclass(frozen=True)
class PaqueteResumen:
    """Resumen de paquete para listados (sin items)"""
    id: str
    codigo: str
    nombre: str
    moneda: str
    monto_total: Decimal
    descripcion: Optional[str] = None
    tipo_evento_id: Optional[str] = None
    tipo_evento_nombre: Optional[str] = None
    status: int = 1


@dataclass(frozen=True)
class PaqueteDetalle:
    """Paquete completo con todos sus items"""
    id: str
    codigo: str
    nombre: str
    moneda: str
    monto_total: Decimal
    items: list[ItemPaquete]
    descripcion: Optional[str] = None
    status: int = 1
