"""
Use Case: Crear Pedido desde Paquete
Crea un pedido basado en un paquete del catálogo
"""
from typing import Any, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy import text

from ...domain.models import Pedido
from ...domain.ports import CatalogoQueryPort, PedidoRepository, ItemPedidoRepository, ReservaRepository
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
        reserva_repo: ReservaRepository,
        catalogo_client: CatalogoQueryPort
    ):
        self.pedido_repo = pedido_repo
        self.item_repo = item_repo
        self.reserva_repo = reserva_repo
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
        servicios_adicionales: Optional[list] = None,
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
        
        # Mapa de proveedores seleccionados {opcion_id: proveedor_id}
        prov_map = {}
        if proveedores_seleccionados:
            for p in proveedores_seleccionados:
                # p puede ser dict o objeto pydantic convertido a dict
                oid = p.get("opcion_servicio_id")
                pid = p.get("proveedor_id")
                if oid and pid:
                    prov_map[str(oid)] = str(pid)

        # 4. Crear items del pedido basados en el paquete
        items = paquete.get("items", [])
        for item in items:
            # Calcular subtotal = cantidad * precio_unitario
            cantidad = item.get("cantidad", 1)
            precio_unitario = float(item.get("precio_unit_vigente", 0))
            subtotal = cantidad * precio_unitario
            opcion_id = item["opcion_servicio_id"]
            
            item_creado = self.item_repo.crear(
                session,
                pedido_id=pedido.id,
                opcion_servicio_id=opcion_id,
                nombre_servicio=item.get("servicio_nombre", item.get("opcion_nombre", "Servicio")),
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal
            )

            # Crear reserva si hay proveedor seleccionado para esta opción
            if str(opcion_id) in prov_map:
                # Calcular horas para fin (simple logic, should be robust)
                # Asumimos fecha_evento + hora_inicio/fin
                # Por ahora usamos fecha_evento 00:00 si no hay horas precisas
                # TODO: Mejorar manejo de fechas/horas para reservas
                dt_inicio = datetime.combine(fecha_evento, datetime.min.time())
                dt_fin = dt_inicio # Placeholder
                
                self.reserva_repo.crear(
                    session,
                    pedido_id=pedido.id,
                    item_pedido_id=item_creado.id,
                    proveedor_id=prov_map[str(opcion_id)],
                    opcion_servicio_id=opcion_id,
                    inicio=dt_inicio,
                    fin=dt_fin,
                    status=0, # PENDIENTE
                    monto=Decimal(0) # Por definir
                )
        
        # 5. Agregar servicios adicionales si existen
        if servicios_adicionales:
            for servicio_adicional in servicios_adicionales:
                # Obtener precio del servicio desde catálogo
                opcion_id = servicio_adicional.get("opcion_servicio_id")
                cantidad_adicional = servicio_adicional.get("cantidad", 1)
                
                # Consultar precio vigente
                try:
                    precio_vigente = self.catalogo_client.obtener_precio_opcion(opcion_id)
                    precio_unitario_adicional = float(precio_vigente)
                except Exception:
                    # Si no se puede obtener precio, usar 0 (debería manejarse mejor)
                    precio_unitario_adicional = 0.0
                
                subtotal_adicional = cantidad_adicional * precio_unitario_adicional
                
                # Crear item adicional
                self.item_repo.crear(
                    session,
                    pedido_id=pedido.id,
                    opcion_servicio_id=opcion_id,
                    nombre_servicio="Servicio Adicional",  # Podría obtenerse del catálogo
                    cantidad=cantidad_adicional,
                    precio_unitario=precio_unitario_adicional,
                    subtotal=subtotal_adicional,
                    tipo_item='SERVICIO',
                    referencia_id=opcion_id
                )
                
                # Actualizar monto total del pedido
                monto_total += subtotal_adicional
            
            # Actualizar el monto total del pedido si hubo servicios adicionales
            if servicios_adicionales:
                pedido = self.pedido_repo.actualizar_monto(
                    session,
                    pedido_id=pedido.id,
                    nuevo_monto=monto_total
                )

        # Intentar leer la vista enriquecida para devolver datos relacionados (cliente_nombre, tipo_evento_nombre)
        try:
            vp = session.execute(
                text("SELECT * FROM ev_contratacion.v_pedido_con_cliente WHERE id = :pid LIMIT 1"),
                {"pid": pedido.id}
            ).mappings().first()
            if vp:
                r = dict(vp)
                # construir objeto Pedido con campos enriquecidos
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
            # No queremos romper el flujo principal por errores de lectura secundaria
            pass

        return pedido
