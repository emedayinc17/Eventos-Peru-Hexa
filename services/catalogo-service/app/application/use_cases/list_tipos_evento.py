"""
Use Case: Listar Tipos de Evento
Caso de uso simple de lectura - Hexagonal Architecture
"""
from typing import Any

from ...domain.models import TipoEvento
from ...domain.ports import CatalogoQueryService


class ListTiposEventoUseCase:
    """
    Lista todos los tipos de evento activos del catálogo.
    Dependencia: CatalogoQueryService (puerto, inyectado)
    """

    def __init__(self, catalogo_service: CatalogoQueryService):
        self.catalogo_service = catalogo_service

    def execute(
        self,
        session: Any,  # SQLAlchemy session (inyectado desde infrastructure)
        *,
        limit: int = 50,
        offset: int = 0
    ) -> list[TipoEvento]:
        """
        Ejecuta el caso de uso: listar tipos de evento.

        Args:
            session: Sesión de base de datos (SQLAlchemy)
            limit: Cantidad máxima de resultados
            offset: Número de registros a saltar (paginación)

        Returns:
            Lista de TipoEvento del dominio
        """
        return self.catalogo_service.list_tipos_evento(
            session,
            limit=limit,
            offset=offset
        )
