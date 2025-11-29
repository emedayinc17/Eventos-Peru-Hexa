"""
Modelos de dominio de Contratación (Hexagonal Architecture)
Clases Python puras - SIN dependencias de SQLAlchemy, FastAPI, etc.
"""
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


@dataclass(frozen=True)
class ItemPedido:
    """
    Item individual de un pedido (línea del pedido).
    Representa un servicio/opción contratada.
    """
    id: str
    pedido_id: str
    opcion_servicio_id: str
    nombre_servicio: str  # Desnormalizado para histórico
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal
    
    def __post_init__(self):
        """Validaciones de negocio"""
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        if self.precio_unitario < 0:
            raise ValueError("El precio unitario no puede ser negativo")
        # Validar que subtotal = cantidad * precio_unitario
        expected_subtotal = Decimal(self.cantidad) * self.precio_unitario
        if abs(self.subtotal - expected_subtotal) > Decimal('0.01'):
            raise ValueError(f"Subtotal inconsistente: esperado {expected_subtotal}, recibido {self.subtotal}")


@dataclass
class Pedido:
    """
    Pedido de evento (agregado raíz).
    
    Estados (state machine):
    - 0 = DRAFT: Pedido creado, sin cotización
    - 1 = COTIZADO: Precios calculados, holds creados
    - 2 = APROBADO: Cliente aprobó, holds confirmados
    - 3 = ASIGNADO: Admin asignó proveedores, reservas creadas
    - 4 = CERRADO: Evento completado
    - 5 = CANCELADO: Pedido cancelado, holds liberados
    
    Transiciones válidas:
    - DRAFT → COTIZADO → APROBADO → ASIGNADO → CERRADO
    - cualquier estado → CANCELADO
    """
    id: str
    cliente_id: str
    tipo_evento_id: str
    paquete_id: Optional[str]
    fecha_evento: datetime
    hora_inicio: str
    hora_fin: Optional[str]
    num_personas: int
    ubicacion: str
    status: int  # 0-5 según state machine
    monto_total: Decimal
    created_at: datetime
    updated_at: datetime
    moneda: str = "PEN"  # Default value
    notas: Optional[str] = None
    cliente_nombre: Optional[str] = None
    cliente_email: Optional[str] = None
    tipo_evento_nombre: Optional[str] = None
    
    # Transiciones de estado válidas
    VALID_TRANSITIONS = {
        0: [1, 5],  # DRAFT → COTIZADO o CANCELADO
        1: [2, 5],  # COTIZADO → APROBADO o CANCELADO
        2: [3, 5],  # APROBADO → ASIGNADO o CANCELADO
        3: [4, 5],  # ASIGNADO → CERRADO o CANCELADO
        4: [],      # CERRADO → (terminal)
        5: [],      # CANCELADO → (terminal)
    }
    
    ESTADO_NOMBRES = {
        0: "DRAFT",
        1: "COTIZADO",
        2: "APROBADO",
        3: "ASIGNADO",
        4: "CERRADO",
        5: "CANCELADO"
    }
    
    def __post_init__(self):
        """Validaciones de reglas de negocio"""
        if self.status not in range(6):
            raise ValueError(f"Status inválido: {self.status}. Debe estar entre 0-5")
        if self.num_personas <= 0:
            raise ValueError("El número de personas debe ser mayor a 0")
        if self.monto_total < 0:
            raise ValueError("El monto total no puede ser negativo")
    
    @property
    def estado_nombre(self) -> str:
        """Retorna el nombre del estado actual"""
        return self.ESTADO_NOMBRES.get(self.status, "DESCONOCIDO")
    
    def puede_transicionar_a(self, nuevo_estado: int) -> bool:
        """Verifica si la transición de estado es válida"""
        return nuevo_estado in self.VALID_TRANSITIONS.get(self.status, [])
    
    @property
    def es_editable(self) -> bool:
        """Verifica si el pedido puede ser editado (DRAFT o COTIZADO)"""
        return self.status in (0, 1)
    
    @property
    def esta_activo(self) -> bool:
        """Verifica si el pedido está activo (no cerrado ni cancelado)"""
        return self.status not in (4, 5)
    
    @property
    def requiere_asignacion(self) -> bool:
        """Verifica si el pedido está listo para asignación de proveedores"""
        return self.status == 2  # APROBADO


@dataclass
class Reserva:
    """
    Reserva confirmada de un proveedor para un servicio.
    Se crea cuando Admin asigna proveedor a un item del pedido.
    Es PERMANENTE (no expira como los holds).
    """
    id: str
    pedido_id: str
    item_pedido_id: str
    proveedor_id: str
    opcion_servicio_id: str
    inicio: datetime
    fin: datetime
    status: int  # 0=pendiente, 1=confirmada, 2=cancelada
    monto: Decimal
    hold_id: Optional[str] = None  # Referencia al hold que originó esta reserva
    notas: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones de negocio"""
        if self.fin <= self.inicio:
            raise ValueError("La fecha fin debe ser posterior a la fecha inicio")
        if self.monto < 0:
            raise ValueError("El monto no puede ser negativo")
        if self.status not in (0, 1, 2):
            raise ValueError(f"Status inválido: {self.status}. Debe ser 0, 1 o 2")
    
    @property
    def esta_confirmada(self) -> bool:
        """Verifica si la reserva está confirmada"""
        return self.status == 1
    
    @property
    def duracion_horas(self) -> float:
        """Calcula la duración en horas"""
        delta = self.fin - self.inicio
        return delta.total_seconds() / 3600
