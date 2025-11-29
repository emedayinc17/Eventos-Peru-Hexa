"""
Use Case: Obtener Detalle Completo de un Pedido
Obtiene un pedido con sus items y reservas
"""
from typing import Any, Dict, Optional
from dataclasses import asdict

from ...domain.models import Pedido
from ...domain.ports import PedidoRepository, ItemPedidoRepository, ReservaRepository
from ...domain.exceptions import PedidoNoEncontrado
from ...infrastructure.http.iam_client import IamClient
from ...infrastructure.http.catalogo_client import CatalogoClient


class ObtenerPedidoDetalleUseCase:
    """
    Obtiene el detalle completo de un pedido incluyendo items y reservas.
    Caso de uso de consulta - solo lectura.
    Enriquece los datos con información de IAM y Catálogo.
    """
    
    def __init__(
        self,
        pedido_repo: PedidoRepository,
        item_repo: ItemPedidoRepository,
        reserva_repo: ReservaRepository,
        iam_client: IamClient,
        catalogo_client: CatalogoClient
    ):
        self.pedido_repo = pedido_repo
        self.item_repo = item_repo
        self.reserva_repo = reserva_repo
        self.iam_client = iam_client
        self.catalogo_client = catalogo_client
    
    def execute(
        self,
        session: Any,
        *,
        pedido_id: str,
        auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta el caso de uso: obtener pedido con detalles.
        
        Args:
            session: Sesión de base de datos
            pedido_id: ID del pedido
            auth_token: Token JWT para autenticación con otros servicios
        
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
        
        # 4. Enriquecimiento de datos (Cliente y Evento)
        # Cliente
        if auth_token and pedido.cliente_id:
            try:
                user_data = self.iam_client.get_user_details(pedido.cliente_id, auth_token)
                if user_data:
                    pedido.cliente_nombre = user_data.get("nombre")
                    pedido.cliente_email = user_data.get("email")
            except Exception:
                pass # Fail silently
        
        # Evento
        if pedido.tipo_evento_id:
            try:
                tipo_data = self.catalogo_client.get_tipo_evento(pedido.tipo_evento_id)
                if tipo_data:
                    pedido.tipo_evento_nombre = tipo_data.get("nombre")
            except Exception:
                pass

        # 5. Retornar estructura completa
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
