"""
Use Case: Admin Asignar Proveedor a Item de Pedido
Crea/confirma hold y genera reserva permanente
"""
from typing import Any, Optional
from datetime import datetime

from ...domain.models import Reserva
from ...domain.ports import (
    PedidoRepository,
    ItemPedidoRepository,
    ReservaRepository,
    ProveedoresHoldPort
)
from ...domain.exceptions import (
    PedidoNoEncontrado,
    ItemPedidoNoEncontrado,
    ErrorAsignacionProveedor,
    ErrorServicioExterno
)


class AdminAsignarProveedorUseCase:
    """
    Admin asigna un proveedor específico a un item del pedido.
    Pasos:
    1. Crear hold en Proveedores (o confirmar si ya existe)
    2. Crear reserva permanente en Contratación
    3. Si es el último item → actualizar pedido a ASIGNADO
    """
    
    def __init__(
        self,
        pedido_repo: PedidoRepository,
        item_repo: ItemPedidoRepository,
        reserva_repo: ReservaRepository,
        proveedores_client: ProveedoresHoldPort
    ):
        self.pedido_repo = pedido_repo
        self.item_repo = item_repo
        self.reserva_repo = reserva_repo
        self.proveedores_client = proveedores_client
    
    def execute(
        self,
        session: Any,
        *,
        pedido_id: str,
        item_pedido_id: str,
        proveedor_id: str,
        inicio: datetime,
        fin: datetime,
        hold_id: Optional[str] = None,
        notas: Optional[str] = None
    ) -> Reserva:
        """
        Ejecuta el caso de uso: asignar proveedor a item.
        
        Args:
            session: Sesión de base de datos
            pedido_id: ID del pedido
            item_pedido_id: ID del item a asignar
            proveedor_id: ID del proveedor seleccionado
            inicio: Fecha/hora inicio del servicio
            fin: Fecha/hora fin del servicio
            hold_id: ID de hold existente (opcional, si ya se creó)
            notas: Notas adicionales
        
        Returns:
            Reserva creada
        
        Raises:
            PedidoNoEncontrado: Si el pedido no existe
            ItemPedidoNoEncontrado: Si el item no existe
            ErrorAsignacionProveedor: Si falla la asignación
        """
        # 1. Validar pedido existe y está en estado correcto
        pedido = self.pedido_repo.obtener_por_id(session, pedido_id)
        if not pedido:
            raise PedidoNoEncontrado(pedido_id)
        
        if not pedido.requiere_asignacion:
            raise ErrorAsignacionProveedor(
                item_pedido_id,
                proveedor_id,
                f"Pedido debe estar en estado APROBADO (2), actual: {pedido.status}"
            )
        
        # 2. Validar item existe
        item = self.item_repo.obtener_por_id(session, item_pedido_id)
        if not item:
            raise ItemPedidoNoEncontrado(item_pedido_id)
        
        # 3. Verificar si ya existe reserva para este item
        reserva_existente = self.reserva_repo.obtener_por_item(session, item_pedido_id)
        if reserva_existente:
            raise ErrorAsignacionProveedor(
                item_pedido_id,
                proveedor_id,
                "Ya existe una reserva para este item"
            )
        
        # 4. Crear o confirmar hold en Proveedores
        print(f"🔍 [DEBUG] Paso 4: Crear/confirmar hold")
        if hold_id:
            # Ya existe hold, solo confirmarlo
            try:
                print(f"🔍 [DEBUG] Confirmando hold existente: {hold_id}")
                hold_response = self.proveedores_client.confirmar_hold(hold_id)
                print(f"✅ [DEBUG] Hold confirmado: {hold_response}")
            except Exception as e:
                print(f"❌ [DEBUG] Error confirmando hold: {type(e).__name__}: {str(e)}")
                raise ErrorServicioExterno(
                    "proveedores",
                    f"Error al confirmar hold {hold_id}: {str(e)}"
                )
        else:
            # Crear nuevo hold y confirmarlo
            try:
                # Crear hold temporal
                hold_payload = {
                    "proveedor_id": proveedor_id,
                    "opcion_servicio_id": item.opcion_servicio_id,
                    "inicio": inicio.isoformat(),
                    "fin": fin.isoformat(),
                    "ttl_min": 30,
                    "correlation_id": f"pedido-{pedido_id}-item-{item_pedido_id}",
                    "created_by": "contratacion-admin"
                }
                print(f"🔍 [DEBUG] Creando hold: {hold_payload}")
                hold_response = self.proveedores_client.crear_hold(hold_payload)
                hold_id = hold_response["id"]
                print(f"✅ [DEBUG] Hold creado: {hold_id}")
                
                # Confirmar hold inmediatamente
                print(f"🔍 [DEBUG] Confirmando hold: {hold_id}")
                self.proveedores_client.confirmar_hold(hold_id)
                print(f"✅ [DEBUG] Hold confirmado")
                
            except Exception as e:
                print(f"❌ [DEBUG] Error en crear/confirmar hold: {type(e).__name__}: {str(e)}")
                raise ErrorServicioExterno(
                    "proveedores",
                    f"Error al crear/confirmar hold: {str(e)}"
                )
        
        # 5. Crear reserva permanente en Contratación
        print(f"🔍 [DEBUG] Paso 5: Crear reserva permanente")
        print(f"🔍 [DEBUG] Parámetros: pedido_id={pedido_id}, item={item_pedido_id}, proveedor={proveedor_id}, hold={hold_id}")
        try:
            reserva = self.reserva_repo.crear(
                session,
                pedido_id=pedido_id,
                item_pedido_id=item_pedido_id,
                proveedor_id=proveedor_id,
                opcion_servicio_id=item.opcion_servicio_id,
                inicio=inicio,
                fin=fin,
                status=1,  # Confirmada
                monto=float(item.subtotal),
                hold_id=hold_id,
                notas=notas
            )
            print(f"✅ [DEBUG] Reserva creada: {reserva}")
        except Exception as e:
            print(f"❌ [DEBUG] Error creando reserva: {type(e).__name__}: {str(e)}")
            raise
        
        # 6. Verificar si todos los items tienen reserva → actualizar pedido a ASIGNADO
        items = self.item_repo.listar_por_pedido(session, pedido_id)
        reservas = self.reserva_repo.listar_por_pedido(session, pedido_id)
        
        if len(items) == len(reservas):
            # Todos los items tienen proveedor asignado
            self.pedido_repo.actualizar_estado(session, pedido_id, 3)  # ASIGNADO
        
        return reserva
