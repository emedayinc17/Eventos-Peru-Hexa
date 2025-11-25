"""
Use Case: Crear Hold Temporal
Caso de uso de comando - Hexagonal Architecture
"""
from typing import Any, Optional
from datetime import datetime

from ...domain.models import Hold
from ...domain.ports import HoldsCommandPort


class CrearHoldUseCase:
    """
    Crea un hold temporal (reserva temporal) para un proveedor.
    Dependencia: HoldsCommandPort (puerto, inyectado)
    """

    def __init__(self, holds_command: HoldsCommandPort):
        self.holds_command = holds_command

    def execute(
        self,
        session: Any,
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
        Ejecuta el caso de uso: crear hold temporal.

        Args:
            session: Sesión de base de datos (SQLAlchemy)
            proveedor_id: ID del proveedor a reservar
            opcion_servicio_id: Opción de servicio
            inicio: Fecha/hora inicio de la reserva
            fin: Fecha/hora fin de la reserva
            ttl_min: Minutos hasta expiración (default 30)
            correlation_id: ID para idempotencia
            created_by: Identificador del servicio que crea el hold

        Returns:
            Hold creado o existente (idempotente)

        Raises:
            ConflictoDisponibilidadError: Si hay conflicto con otro hold/reserva
            RangoTiempoInvalido: Si el rango de tiempo es inválido
        """
        return self.holds_command.crear_hold(
            session,
            proveedor_id=proveedor_id,
            opcion_servicio_id=opcion_servicio_id,
            inicio=inicio,
            fin=fin,
            ttl_min=ttl_min,
            correlation_id=correlation_id,
            created_by=created_by
        )
