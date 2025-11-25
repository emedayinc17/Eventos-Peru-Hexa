"""
Use Case: Liberar Hold
Caso de uso de comando - Hexagonal Architecture
"""
from typing import Any

from ...domain.ports import HoldsCommandPort


class LiberarHoldUseCase:
    """
    Libera un hold temporal (status → 3).
    Útil para rollback o cancelación de pedidos.
    Dependencia: HoldsCommandPort (puerto, inyectado)
    """

    def __init__(self, holds_command: HoldsCommandPort):
        self.holds_command = holds_command

    def execute(
        self,
        session: Any,
        *,
        hold_id: str
    ) -> None:
        """
        Ejecuta el caso de uso: liberar hold.

        Args:
            session: Sesión de base de datos (SQLAlchemy)
            hold_id: ID del hold a liberar

        Returns:
            None (idempotente, no falla si ya está liberado)

        Raises:
            HoldNoEncontrado: Si el hold no existe
            HoldInvalidoError: Si el hold no puede ser liberado
        """
        self.holds_command.liberar_hold(
            session,
            hold_id=hold_id
        )
