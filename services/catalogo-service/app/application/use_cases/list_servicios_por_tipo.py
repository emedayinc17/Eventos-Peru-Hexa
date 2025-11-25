"""
Use Case: Listar Servicios por Tipo de Evento
Caso de uso de lectura con filtro opcional - Hexagonal Architecture
"""
from typing import Any, Optional

from ...domain.models import Servicio
from ...domain.ports import CatalogoQueryService


class ListServiciosPorTipoUseCase:
    """
    Lista servicios del catálogo, opcionalmente filtrados por tipo de evento.
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
    ) -> list[Servicio]:
        """
        Ejecuta el caso de uso: listar servicios.

        Args:
            session: Sesión de base de datos (SQLAlchemy)
            tipo_evento_id: ID del tipo de evento para filtrar (opcional)
            limit: Cantidad máxima de resultados
            offset: Número de registros a saltar (paginación)

        Returns:
            Lista de Servicio del dominio
        """
        return self.catalogo_service.list_servicios_por_tipo(
            session,
            tipo_evento_id=tipo_evento_id,
            limit=limit,
            offset=offset
        )
