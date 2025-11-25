"""
Excepciones del dominio de Contratación (Hexagonal Architecture)
Excepciones de negocio - independientes de la infraestructura
"""


class ContratacionException(Exception):
    """Excepción base para el dominio de Contratación"""
    pass


class PedidoNoEncontrado(ContratacionException):
    """El pedido solicitado no existe"""
    def __init__(self, pedido_id: str):
        self.pedido_id = pedido_id
        super().__init__(f"Pedido no encontrado: {pedido_id}")


class ItemPedidoNoEncontrado(ContratacionException):
    """El item de pedido solicitado no existe"""
    def __init__(self, item_id: str):
        self.item_id = item_id
        super().__init__(f"Item de pedido no encontrado: {item_id}")


class ReservaNoEncontrada(ContratacionException):
    """La reserva solicitada no existe"""
    def __init__(self, reserva_id: str):
        self.reserva_id = reserva_id
        super().__init__(f"Reserva no encontrada: {reserva_id}")


class TransicionEstadoInvalida(ContratacionException):
    """Transición de estado no permitida"""
    def __init__(self, estado_actual: int, estado_nuevo: int):
        self.estado_actual = estado_actual
        self.estado_nuevo = estado_nuevo
        super().__init__(
            f"Transición inválida: estado {estado_actual} no puede cambiar a {estado_nuevo}"
        )


class PedidoNoEditable(ContratacionException):
    """El pedido no puede ser editado en su estado actual"""
    def __init__(self, pedido_id: str, status: int):
        self.pedido_id = pedido_id
        self.status = status
        super().__init__(
            f"Pedido {pedido_id} no editable en estado {status}"
        )


class ErrorCotizacion(ContratacionException):
    """Error al cotizar pedido (no se pudo obtener precios o crear holds)"""
    def __init__(self, pedido_id: str, detalle: str):
        self.pedido_id = pedido_id
        self.detalle = detalle
        super().__init__(f"Error al cotizar pedido {pedido_id}: {detalle}")


class ErrorAsignacionProveedor(ContratacionException):
    """Error al asignar proveedor a un item"""
    def __init__(self, item_id: str, proveedor_id: str, detalle: str):
        self.item_id = item_id
        self.proveedor_id = proveedor_id
        self.detalle = detalle
        super().__init__(
            f"Error al asignar proveedor {proveedor_id} a item {item_id}: {detalle}"
        )


class PaqueteNoEncontrado(ContratacionException):
    """El paquete solicitado no existe en Catálogo"""
    def __init__(self, paquete_id: str):
        self.paquete_id = paquete_id
        super().__init__(f"Paquete no encontrado en catálogo: {paquete_id}")


class OpcionServicioNoEncontrada(ContratacionException):
    """La opción de servicio no existe o no tiene precio vigente"""
    def __init__(self, opcion_id: str):
        self.opcion_id = opcion_id
        super().__init__(f"Opción de servicio no encontrada: {opcion_id}")


class ErrorServicioExterno(ContratacionException):
    """Error al comunicarse con un servicio externo (Catálogo, Proveedores)"""
    def __init__(self, servicio: str, detalle: str):
        self.servicio = servicio
        self.detalle = detalle
        super().__init__(f"Error en servicio {servicio}: {detalle}")
