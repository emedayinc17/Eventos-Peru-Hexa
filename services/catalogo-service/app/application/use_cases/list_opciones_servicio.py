"""
Use Case: Listar Opciones de Servicio con Precios
Caso de uso de lectura - Hexagonal Architecture
"""
from typing import Any

from ...domain.models import OpcionServicio
from ...domain.ports import CatalogoQueryService


class ListOpcionesServicioUseCase:
    """
    Lista opciones de un servicio específico con sus precios vigentes.
    Dependencia: CatalogoQueryService (puerto, inyectado)
    """

    def __init__(self, catalogo_service: CatalogoQueryService):
        self.catalogo_service = catalogo_service

    def execute(
        self,
        session: Any,
        *,
        servicio_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list[OpcionServicio]:
        """
        Ejecuta el caso de uso: listar opciones de servicio.

        Args:
            session: Sesión de base de datos (SQLAlchemy)
            servicio_id: ID del servicio del cual listar opciones
            limit: Cantidad máxima de resultados
            offset: Número de registros a saltar (paginación)

        Returns:
            Lista de OpcionServicio del dominio con precios vigentes
        """
        return self.catalogo_service.list_opciones_por_servicio(
            session,
            servicio_id=servicio_id,
            limit=limit,
            offset=offset
        )
