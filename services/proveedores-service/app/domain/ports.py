"""
Ports (interfaces) del dominio Proveedores - Hexagonal Architecture
Protocol en lugar de ABC para mayor flexibilidad (duck typing)
"""
from typing import Protocol, Optional
from datetime import datetime, date
from .models import Proveedor, Hold


class ProveedorQueryPort(Protocol):
    """
    Puerto de lectura de proveedores (query).
    Implementado por: MySQLProveedorQueryRepository en infrastructure/db/
    """

    def buscar_disponibles(
        self,
        s,  # SQLAlchemy session
        *,
        servicio_id: str,
        fecha: date,
        limit: int = 50,
        offset: int = 0
    ) -> list[Proveedor]:
        """
        Busca proveedores disponibles para un servicio en una fecha.
        Excluye proveedores con holds activos, reservas confirmadas o descansos.
        """
        ...


class HoldsCommandPort(Protocol):
    """
    Puerto de comandos para gestión de holds (reservas temporales).
    Implementado por: MySQLHoldsRepository en infrastructure/db/
    """

    def crear_hold(
        self,
        s,
        *,
        proveedor_id: str,
        opcion_servicio_id: str,
        inicio: datetime,
        fin: datetime,
        ttl_min: int = 30,
        correlation_id: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Hold:
        """
        Crea un hold temporal (idempotente por correlation_id).
        Valida conflictos con otros holds, reservas y descansos.
        Raises: ConflictoDisponibilidadError si no está disponible
        """
        ...

    def confirmar_hold(
        self,
        s,
        *,
        hold_id: str
    ) -> Hold:
        """
        Confirma un hold activo (status 0 → 1).
        Raises: HoldNoEncontrado, HoldExpirado, HoldInvalidoError
        """
        ...

    def liberar_hold(
        self,
        s,
        *,
        hold_id: str
    ) -> None:
        """
        Libera un hold (status → 3).
        Idempotente: no falla si ya está liberado.
        """
        ...

    def obtener_hold(
        self,
        s,
        *,
        hold_id: str
    ) -> Optional[Hold]:
        """
        Obtiene un hold por ID.
        Returns None si no existe.
        """
        ...
