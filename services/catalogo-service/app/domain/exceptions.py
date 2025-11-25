"""
Excepciones de dominio del Catálogo
Errores de negocio específicos del bounded context
"""


class CatalogoException(Exception):
    """Excepción base del dominio Catálogo"""
    pass


class TipoEventoNoEncontrado(CatalogoException):
    """El tipo de evento solicitado no existe"""
    def __init__(self, tipo_evento_id: str):
        self.tipo_evento_id = tipo_evento_id
        super().__init__(f"Tipo de evento no encontrado: {tipo_evento_id}")


class ServicioNoEncontrado(CatalogoException):
    """El servicio solicitado no existe"""
    def __init__(self, servicio_id: str):
        self.servicio_id = servicio_id
        super().__init__(f"Servicio no encontrado: {servicio_id}")


class PaqueteNoEncontrado(CatalogoException):
    """El paquete solicitado no existe"""
    def __init__(self, paquete_id: str):
        self.paquete_id = paquete_id
        super().__init__(f"Paquete no encontrado: {paquete_id}")
