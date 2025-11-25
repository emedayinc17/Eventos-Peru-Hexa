"""
Modelos de dominio de Proveedores (Hexagonal Architecture)
Clases Python puras - SIN dependencias de SQLAlchemy, FastAPI, etc.
"""
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Proveedor:
    """Proveedor de servicios para eventos"""
    id: str
    nombre: str
    rating_prom: Decimal
    email: Optional[str] = None
    telefono: Optional[str] = None
    status: int = 1


@dataclass(frozen=True)
class HabilidadProveedor:
    """Habilidad de un proveedor para un servicio específico"""
    id: str
    proveedor_id: str
    servicio_id: str
    nivel: int  # 1-5


@dataclass
class Hold:
    """
    Reserva temporal (hold) de un proveedor.
    Reglas de negocio:
    - status: 0=activo, 1=confirmado, 2=expirado, 3=liberado
    - Debe tener correlation_id para idempotencia
    - Expira después de ttl_min minutos
    """
    id: str
    proveedor_id: str
    opcion_servicio_id: str
    inicio: datetime
    fin: datetime
    expira_en: datetime
    status: int = 0  # 0=hold activo
    correlation_id: Optional[str] = None
    created_by: Optional[str] = None

    def __post_init__(self):
        """Validaciones de reglas de negocio"""
        if self.fin <= self.inicio:
            raise ValueError("La fecha fin debe ser posterior a la fecha inicio")

    @property
    def is_active(self) -> bool:
        """Verifica si el hold está activo (no expirado ni liberado)"""
        return self.status == 0 and self.expira_en > datetime.now()

    @property
    def is_confirmed(self) -> bool:
        """Verifica si el hold fue confirmado"""
        return self.status == 1

    @property
    def is_expired(self) -> bool:
        """Verifica si el hold expiró"""
        return self.status == 2 or self.expira_en <= datetime.now()

    @property
    def is_released(self) -> bool:
        """Verifica si el hold fue liberado manualmente"""
        return self.status == 3
