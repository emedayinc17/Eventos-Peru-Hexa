"""
Use Case: Admin Agregar Items a Pedido
Permite al admin agregar nuevos items a un pedido existente
"""
from typing import Any, List, Dict
from decimal import Decimal

from ...domain.ports import (
    PedidoRepository,
    ItemPedidoRepository,
    CatalogoQueryPort
)
from ...domain.exceptions import (
    PedidoNoEncontrado,
    OpcionServicioNoEncontrada,
    ErrorAsignacionProveedor
)


class AdminAddItemsUseCase:
    """
    Agrega items a un pedido existente.
    Solo permitido en estados DRAFT (0) o COTIZADO (1).
    """
    
    def __init__(
        self,
        pedido_repo: PedidoRepository,
        item_repo: ItemPedidoRepository,
        catalogo_client: CatalogoQueryPort
    ):
        self.pedido_repo = pedido_repo
        self.item_repo = item_repo
        self.catalogo_client = catalogo_client
    
    def execute(
        self,
        session: Any,
        *,
        pedido_id: str,
        items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Agrega items al pedido.
        
        Args:
            session: Sesión de base de datos
            pedido_id: ID del pedido
            items: Lista de items a agregar [{"opcion_servicio_id": "...", "cantidad": 1}]
        
        Returns:
            Dict con pedido_id, items agregados y nuevo monto_total
        
        Raises:
            PedidoNoEncontrado: Si el pedido no existe
            OpcionServicioNoEncontrada: Si alguna opción no existe
            ErrorAsignacionProveedor: Si el pedido no está en estado válido
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
                f"Solo se pueden agregar items en estado DRAFT(0) o COTIZADO(1), estado actual: {pedido.status}"
            )
        
        # 2. Validar y obtener precios de opciones desde Catálogo
        items_creados = []
        monto_adicional = Decimal("0")
        
        for item_data in items:
            opcion_id = item_data["opcion_servicio_id"]
            cantidad = item_data.get("cantidad", 1)
            
            # Consultar precio vigente
            opcion_info = self.catalogo_client.get_opcion_servicio_precio(opcion_id)
            if opcion_info is None:
                raise OpcionServicioNoEncontrada(opcion_id)
            
            precio_unit = Decimal(str(opcion_info["precio"]))
            nombre_servicio = opcion_info.get("servicio_nombre", f"Servicio {opcion_id[:8]}")
            subtotal = precio_unit * cantidad
            
            # 3. Crear item en BD
            item_creado = self.item_repo.crear(
                session,
                pedido_id=pedido_id,
                opcion_servicio_id=opcion_id,
                nombre_servicio=nombre_servicio,
                cantidad=cantidad,
                precio_unitario=float(precio_unit),
                subtotal=float(subtotal),
                tipo_item="SERVICIO",
                referencia_id=opcion_id
            )
            
            items_creados.append({
                "id": item_creado.id,
                "opcion_servicio_id": opcion_id,
                "cantidad": cantidad,
                "precio_unit": float(precio_unit),
                "precio_total": float(subtotal),
                "tipo_item": "SERVICIO",
                "referencia_id": opcion_id
            })
            
            monto_adicional += subtotal
        
        # 4. Actualizar monto_total del pedido
        nuevo_monto = Decimal(str(pedido.monto_total)) + monto_adicional
        self.pedido_repo.actualizar_monto(session, pedido_id, float(nuevo_monto))
        
        return {
            "pedido_id": pedido_id,
            "items_agregados": items_creados,
            "monto_total": float(nuevo_monto)
        }
