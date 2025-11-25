"""
Use Case: Buscar Proveedores Disponibles
Caso de uso de consulta - Hexagonal Architecture
"""
from typing import Any
from datetime import date

from ...domain.models import Proveedor
from ...domain.ports import ProveedorQueryPort


class BuscarProveedoresDisponiblesUseCase:
    """
    Busca proveedores disponibles para un servicio en una fecha específica.
    Dependencia: ProveedorQueryPort (puerto, inyectado)
    """

    def __init__(self, proveedor_query: ProveedorQueryPort):
        self.proveedor_query = proveedor_query

    def execute(
        self,
        session: Any,
        *,
        servicio_id: str,
        fecha: date,
        limit: int = 50,
        offset: int = 0
    ) -> list[Proveedor]:
        """
        Ejecuta el caso de uso: buscar proveedores disponibles.

        Args:
            session: Sesión de base de datos (SQLAlchemy)
            servicio_id: ID del servicio requerido
            fecha: Fecha para verificar disponibilidad
            limit: Cantidad máxima de resultados
            offset: Número de registros a saltar (paginación)

        Returns:
            Lista de Proveedor disponibles ordenados por rating
        """
        return self.proveedor_query.buscar_disponibles(
            session,
            servicio_id=servicio_id,
            fecha=fecha,
            limit=limit,
            offset=offset
        )
