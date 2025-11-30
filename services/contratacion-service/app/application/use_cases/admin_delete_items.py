"""
Use Case: Admin Eliminar Items de Pedido
Permite al admin eliminar items de un pedido existente
"""
from typing import Any, List, Dict
from decimal import Decimal

from ...domain.ports import (
    PedidoRepository,
    ItemPedidoRepository,
    ReservaRepository
)
from ...domain.exceptions import (
    PedidoNoEncontrado,
    ItemPedidoNoEncontrado,
    ErrorAsignacionProveedor
)


class AdminDeleteItemsUseCase:
    """
    Elimina items de un pedido existente.
    Solo permitido en estados DRAFT (0) o COTIZADO (1).
    No se puede eliminar items con reserva confirmada.
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
        pedido_id: str,
        item_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Elimina items del pedido.
        
        Args:
            session: Sesión de base de datos
            pedido_id: ID del pedido
            item_ids: Lista de IDs de items a eliminar
        
        Returns:
            Dict con pedido_id, items eliminados y nuevo monto_total
        
        Raises:
            PedidoNoEncontrado: Si el pedido no existe
            ItemPedidoNoEncontrado: Si algún item no existe
            ErrorAsignacionProveedor: Si el pedido no está en estado válido o items tienen reserva
        """
        # 1. Validar pedido existe y está en estado correcto
        pedido = self.pedido_repo.obtener_por_id(session, pedido_id)
        if not pedido:
            raise PedidoNoEncontrado(pedido_id)
        
        # Solo permitir en DRAFT(0) o COTIZADO(1)
        if pedido.status not in (0, 1):
            raise ErrorAsignacionProveedor(
                None,
                None,
                f"Solo se pueden eliminar items en estado DRAFT(0) o COTIZADO(1), estado actual: {pedido.status}"
            )
        
        # 2. Validar items existen y no tienen reserva confirmada
        items_eliminados = []
        monto_reducido = Decimal("0")
        
        for item_id in item_ids:
            # Obtener item
            item = self.item_repo.obtener_por_id(session, item_id)
            if not item:
                raise ItemPedidoNoEncontrado(item_id)
            
            # Validar que el item pertenezca al pedido
            if str(item.pedido_id) != str(pedido_id):
                # Si el item no es del pedido, lo ignoramos o lanzamos error.
                # Lanzar error es más seguro.
                raise ItemPedidoNoEncontrado(f"Item {item_id} no pertenece al pedido {pedido_id}")
            
            # Verificar reservas
            reserva = self.reserva_repo.obtener_por_item(session, item_id)
            if reserva:
                if reserva.status == 1:  # Confirmada
                    raise ErrorAsignacionProveedor(
                        item_id,
                        None,
                        "No se puede eliminar item con reserva confirmada"
                    )
                else:
                    # Si tiene reserva pendiente (0) o cancelada (2), la eliminamos primero
                    # para evitar error de FK
                    self.reserva_repo.eliminar(session, reserva.id)
            
            # Acumular monto a descontar
            monto_reducido += Decimal(str(item.subtotal))
            
            # 3. Eliminar item
            self.item_repo.eliminar(session, item_id)
            
            items_eliminados.append({
                "id": item_id,
                "precio_total": float(item.subtotal)
            })
        
        # 4. Actualizar monto_total del pedido
        # Asegurar que no sea negativo
        monto_actual = Decimal(str(pedido.monto_total)) if pedido.monto_total is not None else Decimal("0")
        nuevo_monto = max(Decimal("0"), monto_actual - monto_reducido)
        
        self.pedido_repo.actualizar_monto(session, pedido_id, float(nuevo_monto))
        
        return {
            "pedido_id": pedido_id,
            "items_eliminados": items_eliminados,
            "monto_total": float(nuevo_monto)
        }
