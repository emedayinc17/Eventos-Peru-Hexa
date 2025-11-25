"""
Use Case: Obtener Hold
Caso de uso de consulta - Hexagonal Architecture
"""
from typing import Any, Optional

from ...domain.models import Hold
from ...domain.ports import HoldsCommandPort


class ObtenerHoldUseCase:
    """
    Obtiene el detalle de un hold temporal.
    Dependencia: HoldsCommandPort (puerto, inyectado)
    """

    def __init__(self, holds_command: HoldsCommandPort):
        self.holds_command = holds_command

    def execute(
        self,
        session: Any,
        *,
        hold_id: str
    ) -> Optional[Hold]:
        """
        Ejecuta el caso de uso: obtener hold.

        Args:
            session: Sesión de base de datos (SQLAlchemy)
            hold_id: ID del hold a consultar

        Returns:
            Hold si existe, None si no

        """
        return self.holds_command.obtener_hold(
            session,
            hold_id=hold_id
        )
