"""
Use Case: Listar Paquetes (resumen)
Caso de uso de lectura - Hexagonal Architecture
"""
from typing import Any, Optional

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
        tipo_evento_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[PaqueteResumen]:
        """
        Ejecuta el caso de uso: listar paquetes.

        Args:
            session: Sesión de base de datos (SQLAlchemy)
            tipo_evento_id: Filtro opcional por tipo de evento
            limit: Cantidad máxima de resultados
            offset: Número de registros a saltar (paginación)

        Returns:
            Lista de PaqueteResumen del dominio
        """
        return self.catalogo_service.list_paquetes(
            session,
            tipo_evento_id=tipo_evento_id,
            limit=limit,
            offset=offset
        )
