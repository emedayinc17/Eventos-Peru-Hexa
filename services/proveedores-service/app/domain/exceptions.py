"""
Excepciones de dominio de Proveedores
Errores de negocio específicos del bounded context
"""


class ProveedoresException(Exception):
    """Excepción base del dominio Proveedores"""
    pass


class ProveedorNoEncontrado(ProveedoresException):
    """El proveedor solicitado no existe"""
    def __init__(self, proveedor_id: str):
        self.proveedor_id = proveedor_id
        super().__init__(f"Proveedor no encontrado: {proveedor_id}")


class HoldNoEncontrado(ProveedoresException):
    """El hold solicitado no existe"""
    def __init__(self, hold_id: str):
        self.hold_id = hold_id
        super().__init__(f"Hold no encontrado: {hold_id}")


class HoldExpirado(ProveedoresException):
    """El hold ha expirado"""
    def __init__(self, hold_id: str):
        self.hold_id = hold_id
        super().__init__(f"Hold expirado: {hold_id}")


class HoldInvalidoError(ProveedoresException):
    """El hold no está en el estado correcto para la operación"""
    def __init__(self, hold_id: str, estado_actual: int, mensaje: str):
        self.hold_id = hold_id
        self.estado_actual = estado_actual
        super().__init__(f"Hold {hold_id} en estado inválido ({estado_actual}): {mensaje}")


class ConflictoDisponibilidadError(ProveedoresException):
    """Conflicto con otro hold, reserva o descanso"""
    def __init__(self, proveedor_id: str, mensaje: str):
        self.proveedor_id = proveedor_id
        super().__init__(f"Proveedor {proveedor_id} no disponible: {mensaje}")


class RangoTiempoInvalido(ProveedoresException):
    """El rango de tiempo proporcionado es inválido"""
    def __init__(self, mensaje: str):
        super().__init__(f"Rango de tiempo inválido: {mensaje}")
