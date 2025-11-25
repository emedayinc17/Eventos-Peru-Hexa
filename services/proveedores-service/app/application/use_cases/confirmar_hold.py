"""
Use Case: Confirmar Hold
Caso de uso de comando - Hexagonal Architecture
"""
from typing import Any

from ...domain.models import Hold
from ...domain.ports import HoldsCommandPort


class ConfirmarHoldUseCase:
    """
    Confirma un hold temporal (status 0 → 1).
    Dependencia: HoldsCommandPort (puerto, inyectado)
    """

    def __init__(self, holds_command: HoldsCommandPort):
        self.holds_command = holds_command

    def execute(
        self,
        session: Any,
        *,
        hold_id: str
    ) -> Hold:
        """
        Ejecuta el caso de uso: confirmar hold.

        Args:
            session: Sesión de base de datos (SQLAlchemy)
            hold_id: ID del hold a confirmar

        Returns:
            Hold confirmado

        Raises:
            HoldNoEncontrado: Si el hold no existe
            HoldExpirado: Si el hold expiró
            HoldInvalidoError: Si el hold no está en estado activo (0)
        """
        return self.holds_command.confirmar_hold(
            session,
            hold_id=hold_id
        )
