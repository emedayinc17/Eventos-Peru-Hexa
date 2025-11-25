"""
Use Cases de Contratación (Hexagonal Architecture)
Casos de uso que orquestan la lógica de negocio
"""

# Use Cases Básicos
from .crear_pedido_desde_paquete import CrearPedidoDesdePaqueteUseCase
from .crear_pedido_custom import CrearPedidoCustomUseCase
from .listar_pedidos_cliente import ListarPedidosClienteUseCase
from .listar_pedidos_admin import ListarPedidosAdminUseCase
from .obtener_pedido_detalle import ObtenerPedidoDetalleUseCase

# Use Cases Complejos
from .admin_cambiar_estado import AdminCambiarEstadoPedidoUseCase
from .admin_asignar_proveedor import AdminAsignarProveedorUseCase

__all__ = [
    # Básicos
    "CrearPedidoDesdePaqueteUseCase",
    "CrearPedidoCustomUseCase",
    "ListarPedidosClienteUseCase",
    "ListarPedidosAdminUseCase",
    "ObtenerPedidoDetalleUseCase",
    # Complejos
    "AdminCambiarEstadoPedidoUseCase",
    "AdminAsignarProveedorUseCase",
]
