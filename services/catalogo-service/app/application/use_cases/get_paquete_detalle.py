"""
Use Case: Obtener Detalle de Paquete
Caso de uso de lectura con detalle completo - Hexagonal Architecture
"""
from typing import Any, Optional

from ...domain.models import PaqueteDetalle
from ...domain.ports import CatalogoQueryService
from ...domain.exceptions import PaqueteNoEncontrado


class GetPaqueteDetalleUseCase:
    """
    Obtiene el detalle completo de un paquete incluyendo items y proveedores.
    Dependencia: CatalogoQueryService (puerto, inyectado)
    """

    def __init__(self, catalogo_service: CatalogoQueryService):
        self.catalogo_service = catalogo_service

    def execute(
        self,
        session: Any,
        *,
        paquete_id: str
    ) -> PaqueteDetalle:
        """
        Ejecuta el caso de uso: obtener detalle de paquete.

        Args:
            session: Sesión de base de datos (SQLAlchemy)
            paquete_id: ID del paquete a consultar

        Returns:
            PaqueteDetalle del dominio con items completos

        Raises:
            PaqueteNoEncontrado: Si el paquete no existe
        """
        paquete = self.catalogo_service.get_paquete_detalle(
            session,
            paquete_id=paquete_id
        )

        if paquete is None:
            raise PaqueteNoEncontrado(paquete_id)

        return paquete
