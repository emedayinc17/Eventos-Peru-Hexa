"""
Ports (interfaces) del dominio Catálogo - Hexagonal Architecture
Protocol en lugar de ABC para mayor flexibilidad (duck typing)
"""
from typing import Protocol, Optional
from .models import TipoEvento, Servicio, OpcionServicio, PaqueteResumen, PaqueteDetalle


class CatalogoQueryService(Protocol):
    """
    Puerto de lectura del catálogo (query).
    Implementado por: MySQLCatalogoQueryService en infrastructure/db/
    """

    def list_tipos_evento(
        self,
        s,  # SQLAlchemy session
        *,
        limit: int = 50,
        offset: int = 0
    ) -> list[TipoEvento]:
        """Lista todos los tipos de evento activos"""
        ...

    def list_servicios_por_tipo(
        self,
        s,
        *,
        tipo_evento_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Servicio]:
        """Lista servicios, opcionalmente filtrados por tipo de evento"""
        ...

    def list_opciones_por_servicio(
        self,
        s,
        *,
        servicio_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list[OpcionServicio]:
        """Lista opciones de un servicio con precios vigentes"""
        ...

    def list_paquetes(
        self,
        s,
        *,
        limit: int = 50,
        offset: int = 0
    ) -> list[PaqueteResumen]:
        """Lista paquetes con monto total calculado"""
        ...

    def get_paquete_detalle(
        self,
        s,
        *,
        paquete_id: str
    ) -> Optional[PaqueteDetalle]:
        """Obtiene detalle completo de un paquete con sus items"""
        ...

