"""
Use Case: Listar Pedidos por Cliente
Lista los pedidos de un cliente específico
"""
from typing import Any, List

from ...domain.models import Pedido
from ...domain.ports import PedidoRepository


class ListarPedidosClienteUseCase:
    """
    Lista pedidos de un cliente específico.
    Caso de uso de consulta - solo lectura.
    """
    
    def __init__(self, pedido_repo: PedidoRepository):
        self.pedido_repo = pedido_repo
    
    def execute(
        self,
        session: Any,
        *,
        cliente_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Pedido]:
        """
        Ejecuta el caso de uso: listar pedidos de un cliente.
        
        Args:
            session: Sesión de base de datos
            cliente_id: ID del cliente
            limit: Cantidad máxima de resultados
            offset: Cantidad de registros a saltar (paginación)
        
        Returns:
            Lista de pedidos del cliente ordenados por fecha de creación
        """
        return self.pedido_repo.listar_por_cliente(
            session,
            cliente_id=cliente_id,
            limit=limit,
            offset=offset
        )
