"""
Use Case: Crear Pedido Custom
Crea un pedido basado en opciones individuales seleccionadas
"""
from typing import Any, List, Dict, Optional
from datetime import datetime
from sqlalchemy import text
from decimal import Decimal

from ...domain.models import Pedido
from ...domain.ports import CatalogoQueryPort, PedidoRepository, ItemPedidoRepository
from ...domain.exceptions import OpcionServicioNoEncontrada, ErrorCotizacion


class CrearPedidoCustomUseCase:
    """
    Crea un pedido custom con opciones individuales.
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
        tipo_evento_id: str,
        fecha_evento: datetime,
        hora_inicio: str,
        hora_fin: Optional[str],
        num_personas: int,
        ubicacion: str,
        items: List[Dict[str, Any]],  # [{"opcion_servicio_id": "...", "cantidad": 1}, ...]
        notas: Optional[str] = None
    ) -> Pedido:
        """
        Ejecuta el caso de uso: crear pedido custom.
        
        Args:
            session: Sesión de base de datos
            cliente_id: ID del cliente
            tipo_evento_id: Tipo de evento
            fecha_evento: Fecha del evento
            hora_inicio: Hora de inicio
            hora_fin: Hora de fin opcional
            num_personas: Cantidad de personas
            ubicacion: Ubicación del evento
            items: Lista de items [{opcion_servicio_id, cantidad}]
            notas: Notas adicionales
        
        Returns:
            Pedido creado con sus items en estado DRAFT
        
        Raises:
            OpcionServicioNoEncontrada: Si alguna opción no existe
            ErrorCotizacion: Si no se puede calcular el precio
        """
        # 1. Validar y obtener precios de cada opción
        monto_total = 0.0
        items_with_prices = []
        
        for item_data in items:
            opcion_id = item_data["opcion_servicio_id"]
            cantidad = item_data.get("cantidad", 1)
            
            # Consultar precio en catálogo
            opcion = self.catalogo_client.get_opcion_servicio_precio(opcion_id)
            
            if not opcion:
                raise OpcionServicioNoEncontrada(opcion_id)
            
            try:
                precio_unitario = float(opcion["precio"])
                subtotal = precio_unitario * cantidad
                monto_total += subtotal
                
                items_with_prices.append({
                    "opcion_servicio_id": opcion_id,
                    "nombre_servicio": opcion["servicio_nombre"],
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "subtotal": subtotal
                })
            except (KeyError, ValueError, TypeError) as e:
                raise ErrorCotizacion(
                    opcion_id,
                    f"Error al procesar precio de opción: {str(e)}"
                )
        
        # 2. Crear pedido en estado DRAFT (sin paquete_id)
        pedido = self.pedido_repo.crear(
            session,
            cliente_id=cliente_id,
            tipo_evento_id=tipo_evento_id,
            paquete_id=None,  # Pedido custom, no basado en paquete
            fecha_evento=fecha_evento,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            num_personas=num_personas,
            ubicacion=ubicacion,
            monto_total=monto_total,
            notas=notas
        )
        
        # 3. Crear items del pedido
        for item_data in items_with_prices:
            self.item_repo.crear(
                session,
                pedido_id=pedido.id,
                opcion_servicio_id=item_data["opcion_servicio_id"],
                nombre_servicio=item_data["nombre_servicio"],
                cantidad=item_data["cantidad"],
                precio_unitario=item_data["precio_unitario"],
                subtotal=item_data["subtotal"]
            )
        
        # Intentar devolver objeto Pedido enriquecido desde la vista de lectura
        try:
            vp = session.execute(
                text("SELECT * FROM ev_contratacion.v_pedido_con_cliente WHERE id = :pid LIMIT 1"),
                {"pid": pedido.id}
            ).mappings().first()
            if vp:
                r = dict(vp)
                enriched = Pedido(
                    id=r.get('id'),
                    cliente_id=r.get('cliente_id'),
                    tipo_evento_id=r.get('tipo_evento_id'),
                    paquete_id=r.get('paquete_id'),
                    fecha_evento=r.get('fecha_evento'),
                    hora_inicio=str(r.get('hora_inicio')),
                    hora_fin=str(r.get('hora_fin')) if r.get('hora_fin') else None,
                    num_personas=r.get('num_personas') or 1,
                    ubicacion=r.get('ubicacion'),
                    status=int(r.get('status') or 0),
                    monto_total=Decimal(str(r.get('monto_total') or 0)),
                    created_at=r.get('created_at'),
                    updated_at=r.get('updated_at') or r.get('created_at'),
                    moneda=r.get('moneda') or 'PEN',
                    notas=r.get('notas'),
                    cliente_nombre=r.get('cliente_nombre'),
                    cliente_email=r.get('cliente_email'),
                    tipo_evento_nombre=r.get('tipo_evento_nombre')
                )
                return enriched
        except Exception:
            pass

        return pedido
