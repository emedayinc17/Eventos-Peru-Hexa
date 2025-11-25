"""
Use Case: Listar Todos los Pedidos (Admin)
Lista todos los pedidos del sistema con filtros opcionales
"""
from typing import Any, List, Optional

from ...domain.models import Pedido
from ...domain.ports import PedidoRepository


class ListarPedidosAdminUseCase:
    """
    Lista todos los pedidos del sistema (admin).
    Caso de uso de consulta - solo lectura.
    """
    
    def __init__(self, pedido_repo: PedidoRepository):
        self.pedido_repo = pedido_repo
    
    def execute(
        self,
        session: Any,
        *,
        status: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Pedido]:
        """
        Ejecuta el caso de uso: listar todos los pedidos.
        
        Args:
            session: Sesión de base de datos
            status: Filtro opcional por estado (0-5)
            limit: Cantidad máxima de resultados
            offset: Cantidad de registros a saltar (paginación)
        
        Returns:
            Lista de todos los pedidos ordenados por fecha de creación
        """
        return self.pedido_repo.listar_todos(
            session,
            status=status,
            limit=limit,
            offset=offset
        )
