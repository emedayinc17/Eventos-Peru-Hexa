"""
Use Case: Obtener Detalle Completo de un Pedido
Obtiene un pedido con sus items y reservas
"""
from typing import Any, Dict, Optional
from dataclasses import asdict

from ...domain.models import Pedido
from ...domain.ports import PedidoRepository, ItemPedidoRepository, ReservaRepository
from ...domain.exceptions import PedidoNoEncontrado


class ObtenerPedidoDetalleUseCase:
    """
    Obtiene el detalle completo de un pedido incluyendo items y reservas.
    Caso de uso de consulta - solo lectura.
    """
    
    def __init__(
        self,
        pedido_repo: PedidoRepository,
        item_repo: ItemPedidoRepository,
        reserva_repo: ReservaRepository
    ):
        self.pedido_repo = pedido_repo
        self.item_repo = item_repo
        self.reserva_repo = reserva_repo
    
    def execute(
        self,
        session: Any,
        *,
        pedido_id: str
    ) -> Dict[str, Any]:
        """
        Ejecuta el caso de uso: obtener pedido con detalles.
        
        Args:
            session: Sesión de base de datos
            pedido_id: ID del pedido
        
        Returns:
            Diccionario con pedido, items y reservas
        
        Raises:
            PedidoNoEncontrado: Si el pedido no existe
        """
        # 1. Obtener pedido
        pedido = self.pedido_repo.obtener_por_id(session, pedido_id)
        
        if not pedido:
            raise PedidoNoEncontrado(pedido_id)
        
        # 2. Obtener items del pedido
        items = self.item_repo.listar_por_pedido(session, pedido_id)
        
        # 3. Obtener reservas del pedido
        reservas = self.reserva_repo.listar_por_pedido(session, pedido_id)
        
        # 4. Retornar estructura completa
        return {
            "pedido": asdict(pedido),
            "items": [
                {**asdict(item), "proveedor": getattr(item, "proveedor", None)} 
                for item in items
            ],
            "reservas": [asdict(reserva) for reserva in reservas],
            "estado_nombre": pedido.estado_nombre,
            "total_items": len(items),
            "total_reservas": len(reservas)
        }
