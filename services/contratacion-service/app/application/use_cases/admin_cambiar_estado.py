"""
Use Case: Cambiar Estado de Pedido (Admin)
Permite transiciones de estado con validaciones
"""
from typing import Any

from ...domain.models import Pedido
from ...domain.ports import PedidoRepository, ProveedoresHoldPort, ReservaRepository
from ...domain.exceptions import PedidoNoEncontrado, TransicionEstadoInvalida


class AdminCambiarEstadoPedidoUseCase:
    """
    Cambia el estado de un pedido (solo Admin).
    Valida transiciones permitidas y ejecuta acciones asociadas.
    """
    
    def __init__(
        self,
        pedido_repo: PedidoRepository,
        reserva_repo: ReservaRepository,
        proveedores_client: ProveedoresHoldPort
    ):
        self.pedido_repo = pedido_repo
        self.reserva_repo = reserva_repo
        self.proveedores_client = proveedores_client
    
    def execute(
        self,
        session: Any,
        *,
        pedido_id: str,
        nuevo_estado: int
    ) -> Pedido:
        """
        Ejecuta el caso de uso: cambiar estado del pedido.
        
        Args:
            session: Sesión de base de datos
            pedido_id: ID del pedido
            nuevo_estado: Estado destino (0-5)
        
        Returns:
            Pedido actualizado
        
        Raises:
            PedidoNoEncontrado: Si el pedido no existe
            TransicionEstadoInvalida: Si la transición no está permitida
        """
        # 1. Obtener pedido actual
        pedido = self.pedido_repo.obtener_por_id(session, pedido_id)
        if not pedido:
            raise PedidoNoEncontrado(pedido_id)
        
        # 2. Validar transición (delegado al modelo de dominio)
        if not pedido.puede_transicionar_a(nuevo_estado):
            raise TransicionEstadoInvalida(pedido.status, nuevo_estado)
        
        # 3. Ejecutar acciones asociadas según el nuevo estado
        if nuevo_estado == 5:  # CANCELADO
            # Liberar todos los holds asociados
            reservas = self.reserva_repo.listar_por_pedido(session, pedido_id)
            for reserva in reservas:
                if reserva.hold_id:
                    try:
                        self.proveedores_client.liberar_hold(reserva.hold_id)
                    except Exception:
                        # Log error pero continuar (idempotente)
                        pass
        
        # 4. Actualizar estado en BD
        pedido_actualizado = self.pedido_repo.actualizar_estado(
            session,
            pedido_id,
            nuevo_estado
        )
        
        return pedido_actualizado
