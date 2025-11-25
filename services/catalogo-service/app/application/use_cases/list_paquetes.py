"""
Use Case: Listar Paquetes (resumen)
Caso de uso de lectura - Hexagonal Architecture
"""
from typing import Any

from ...domain.models import PaqueteResumen
from ...domain.ports import CatalogoQueryService


class ListPaquetesUseCase:
    """
    Lista paquetes del catálogo con sus montos totales calculados.
    Dependencia: CatalogoQueryService (puerto, inyectado)
    """

    def __init__(self, catalogo_service: CatalogoQueryService):
        self.catalogo_service = catalogo_service

    def execute(
        self,
        session: Any,
        *,
        limit: int = 50,
        offset: int = 0
    ) -> list[PaqueteResumen]:
        """
        Ejecuta el caso de uso: listar paquetes.

        Args:
            session: Sesión de base de datos (SQLAlchemy)
            limit: Cantidad máxima de resultados
            offset: Número de registros a saltar (paginación)

        Returns:
            Lista de PaqueteResumen del dominio
        """
        return self.catalogo_service.list_paquetes(
            session,
            limit=limit,
            offset=offset
        )
