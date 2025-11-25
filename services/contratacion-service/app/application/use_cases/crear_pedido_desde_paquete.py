"""
Use Case: Crear Pedido desde Paquete
Crea un pedido basado en un paquete del catálogo
"""
from typing import Any, Optional
from datetime import datetime
from decimal import Decimal

from ...domain.models import Pedido
from ...domain.ports import CatalogoQueryPort, PedidoRepository, ItemPedidoRepository
from ...domain.exceptions import PaqueteNoEncontrado, ErrorCotizacion


class CrearPedidoDesdePaqueteUseCase:
    """
    Crea un pedido desde un paquete predefinido del catálogo.
    Estado inicial: DRAFT (0)
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
        cliente_id: str,
        paquete_id: str,
        tipo_evento_id: str,
        fecha_evento: datetime,
        hora_inicio: str,
        hora_fin: Optional[str],
        num_personas: int,
        ubicacion: str,
        notas: Optional[str] = None,
        proveedores_seleccionados: Optional[list] = None
    ) -> Pedido:
        """
        Ejecuta el caso de uso: crear pedido desde paquete.
        
        Args:
            session: Sesión de base de datos
            cliente_id: ID del cliente
            paquete_id: ID del paquete seleccionado
            tipo_evento_id: Tipo de evento
            fecha_evento: Fecha del evento
            hora_inicio: Hora de inicio (HH:MM)
            hora_fin: Hora de fin opcional
            num_personas: Cantidad de personas
            ubicacion: Ubicación del evento
            notas: Notas adicionales
        
        Returns:
            Pedido creado con sus items en estado DRAFT
        
        Raises:
            PaqueteNoEncontrado: Si el paquete no existe
            ErrorCotizacion: Si no se puede obtener el precio del paquete
        """
        # 1. Consultar paquete en Catálogo
        paquete = self.catalogo_client.get_paquete_detalle(paquete_id)
        
        if not paquete:
            raise PaqueteNoEncontrado(paquete_id)
        
        # 2. Calcular monto total del paquete
        try:
            monto_total = float(paquete.get("monto_total", 0))
        except (ValueError, TypeError):
            raise ErrorCotizacion(
                paquete_id,
                "No se pudo obtener precio total del paquete"
            )
        
        # 3. Crear pedido en estado DRAFT
        pedido = self.pedido_repo.crear(
            session,
            cliente_id=cliente_id,
            tipo_evento_id=tipo_evento_id,
            paquete_id=paquete_id,
            fecha_evento=fecha_evento,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            num_personas=num_personas,
            ubicacion=ubicacion,
            monto_total=monto_total,
            notas=notas
        )
        
        # 4. Crear items del pedido basados en el paquete
        items = paquete.get("items", [])
        for item in items:
            # Calcular subtotal = cantidad * precio_unitario
            cantidad = item.get("cantidad", 1)
            precio_unitario = float(item.get("precio_unit_vigente", 0))
            subtotal = cantidad * precio_unitario
            
            self.item_repo.crear(
                session,
                pedido_id=pedido.id,
                opcion_servicio_id=item["opcion_servicio_id"],
                nombre_servicio=item.get("servicio_nombre", item.get("opcion_nombre", "Servicio")),
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal
            )
        
        return pedido
