"""
Puertos (interfaces) del dominio de Contratación (Hexagonal Architecture)
Define contratos sin implementación - Protocols para duck typing
"""
from typing import Protocol, Any, List, Optional, Dict
from datetime import datetime, date
from .models import Pedido, ItemPedido, Reserva


# ============================================================================
# PORTS PARA SERVICIOS EXTERNOS (HTTP)
# ============================================================================

class CatalogoQueryPort(Protocol):
    """Puerto para consultas al servicio de Catálogo"""
    
    def get_paquete_detalle(self, paquete_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene detalle completo de un paquete con sus items y precios"""
        ...
    
    def get_opcion_servicio_precio(self, opcion_servicio_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene precio vigente de una opción de servicio"""
        ...


class ProveedoresHoldPort(Protocol):
    """Puerto para gestión de holds en el servicio de Proveedores"""
    
    def crear_hold(
        self,
        proveedor_id: str,
        opcion_servicio_id: str,
        inicio: datetime,
        fin: datetime,
        ttl_min: int,
        correlation_id: str
    ) -> Dict[str, Any]:
        """Crea un hold temporal. Retorna hold con id, expira_en, status"""
        ...
    
    def confirmar_hold(self, hold_id: str) -> Dict[str, Any]:
        """Confirma un hold (status 0 → 1)"""
        ...
    
    def liberar_hold(self, hold_id: str) -> None:
        """Libera/cancela un hold"""
        ...
    
    def obtener_hold(self, hold_id: str) -> Optional[Dict[str, Any]]:
        """Consulta estado de un hold"""
        ...


# ============================================================================
# PORTS PARA REPOSITORIOS (BASE DE DATOS)
# ============================================================================

class PedidoRepository(Protocol):
    """Puerto para operaciones CRUD de Pedidos"""
    
    def crear(
        self,
        session: Any,
        *,
        cliente_id: str,
        tipo_evento_id: str,
        paquete_id: Optional[str],
        fecha_evento: datetime,
        hora_inicio: str,
        hora_fin: Optional[str],
        num_personas: int,
        ubicacion: str,
        monto_total: float,
        notas: Optional[str] = None
    ) -> Pedido:
        """Crea un nuevo pedido en estado DRAFT (status=0)"""
        ...
    
    def obtener_por_id(self, session: Any, pedido_id: str) -> Optional[Pedido]:
        """Obtiene un pedido por su ID"""
        ...
    
    def listar_por_cliente(
        self,
        session: Any,
        cliente_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Pedido]:
        """Lista pedidos de un cliente específico"""
        ...
    
    def listar_todos(
        self,
        session: Any,
        *,
        status: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Pedido]:
        """Lista todos los pedidos (admin) con filtros opcionales"""
        ...
    
    def actualizar_estado(
        self,
        session: Any,
        pedido_id: str,
        nuevo_estado: int
    ) -> Pedido:
        """Actualiza el estado de un pedido"""
        ...
    
    def actualizar_monto(
        self,
        session: Any,
        pedido_id: str,
        nuevo_monto: float
    ) -> Pedido:
        """Actualiza el monto total del pedido"""
        ...


class ItemPedidoRepository(Protocol):
    """Puerto para operaciones CRUD de Items de Pedido"""
    
    def crear(
        self,
        session: Any,
        *,
        pedido_id: str,
        opcion_servicio_id: str,
        nombre_servicio: str,
        cantidad: int,
        precio_unitario: float,
        subtotal: float
    ) -> ItemPedido:
        """Crea un nuevo item de pedido"""
        ...
    
    def listar_por_pedido(
        self,
        session: Any,
        pedido_id: str
    ) -> List[ItemPedido]:
        """Lista todos los items de un pedido"""
        ...
    
    def obtener_por_id(
        self,
        session: Any,
        item_id: str
    ) -> Optional[ItemPedido]:
        """Obtiene un item por su ID"""
        ...


class ReservaRepository(Protocol):
    """Puerto para operaciones CRUD de Reservas"""
    
    def crear(
        self,
        session: Any,
        *,
        pedido_id: str,
        item_pedido_id: str,
        proveedor_id: str,
        opcion_servicio_id: str,
        inicio: datetime,
        fin: datetime,
        monto: float,
        hold_id: Optional[str] = None,
        notas: Optional[str] = None
    ) -> Reserva:
        """Crea una nueva reserva confirmada (status=1)"""
        ...
    
    def listar_por_pedido(
        self,
        session: Any,
        pedido_id: str
    ) -> List[Reserva]:
        """Lista todas las reservas de un pedido"""
        ...
    
    def obtener_por_item(
        self,
        session: Any,
        item_pedido_id: str
    ) -> Optional[Reserva]:
        """Obtiene la reserva asociada a un item de pedido"""
        ...
    
    def actualizar_estado(
        self,
        session: Any,
        reserva_id: str,
        nuevo_estado: int
    ) -> Reserva:
        """Actualiza el estado de una reserva"""
        ...