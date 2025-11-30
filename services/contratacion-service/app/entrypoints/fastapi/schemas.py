from typing import List, Optional, Literal, Union
from datetime import date, time, datetime
from pydantic import BaseModel, Field, EmailStr

# ---------- Infra ----------
class Health(BaseModel):
    status: str = "ok"

# ---------- Cliente: crear pedido ----------
class ProveedorSeleccionado(BaseModel):
    opcion_servicio_id: Union[str, int]
    proveedor_id: Union[str, int]

class ItemCustom(BaseModel):
    opcion_servicio_id: Union[str, int]
    cantidad: int = Field(ge=1, default=1)

class CrearPedidoDesdePaquete(BaseModel):
    paquete_id: Union[str, int]
    tipo_evento_id: Union[str, int]
    fecha_evento: date
    hora_inicio: str  # HH:MM format
    hora_fin: Optional[str] = None  # HH:MM format
    num_personas: int = Field(ge=1)
    ubicacion: str
    notas: Optional[str] = None
    servicios_adicionales: Optional[List[ItemCustom]] = None  # Servicios extras además del paquete
    proveedores_seleccionados: Optional[List[ProveedorSeleccionado]] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None

class CrearPedidoCustom(BaseModel):
    tipo_evento_id: Union[str, int]
    items: List[ItemCustom]
    fecha_evento: date
    hora_inicio: str  # HH:MM format
    hora_fin: Optional[str] = None  # HH:MM format
    num_personas: int = Field(ge=1, default=1)
    ubicacion: str
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None

# Puedes usar esta unión en el router si quieres un oneOf bonito en OpenAPI:
CrearPedidoBody = Union[CrearPedidoDesdePaquete, CrearPedidoCustom]

# ---------- Salidas ----------
class ItemPedidoOut(BaseModel):
    id: str
    pedido_id: str
    tipo_item: Union[str, int]     # 'SERVICIO'/'PAQUETE' or 1/2
    referencia_id: str
    cantidad: int
    precio_unit: float
    precio_total: float
    created_at: datetime

class PedidoEventoOut(BaseModel):
    # columnas de ev_contratacion.v_pedido_con_cliente
    id: str
    cliente_id: str
    cliente_email: Optional[str] = None
    cliente_nombre: Optional[str] = None
    tipo_evento_id: str
    tipo_evento_nombre: Optional[str] = None
    fecha_evento: date
    hora_inicio: time
    hora_fin: Optional[time] = None
    ubicacion: str
    monto_total: float
    moneda: str
    status: int                    # 0..5
    created_at: datetime
    updated_at: Optional[datetime] = None

    # extendido con items al armar la respuesta en commands.obtener_pedido
    items: List[ItemPedidoOut] = []

class EnviarResumenRequest(BaseModel):
    to_email: EmailStr

class EnviarResumenResponse(BaseModel):
    outbox_id: str
    status: Literal["PEND", "ENVIADO", "ERROR", "REINTENTO"] = "PEND"

# ---------- ADMIN DTOs ----------
class AdminPatchEstadoRequest(BaseModel):
    estado: int  # 0=DRAFT,1=COTIZADO,2=APROBADO,3=ASIGNADO,4=CERRADO,5=CANCELADO

class AdminItemAdd(BaseModel):
    opcion_servicio_id: Union[str, int]
    cantidad: int = Field(ge=1, default=1)

class AdminAddItemsRequest(BaseModel):
    items: List[AdminItemAdd]

class AdminDeleteItemsRequest(BaseModel):
    item_ids: List[str]
    
class AdminAsignarProveedorRequest(BaseModel):
    proveedor_id: str
    item_pedido_id: str  # AGREGADO: necesario para asignar proveedor a un item específico
    opcion_servicio_id: str  # AGREGADO: necesario para crear la reserva
    fecha_inicio: datetime   # mapea a ev_contratacion.reserva.inicio
    fecha_fin: datetime      # mapea a ev_contratacion.reserva.fin
    monto: float  # AGREGADO: monto de la reserva
    hold_id: Optional[str] = None


# ---------- ADMIN: Listar todos los pedidos ----------
class AdminListaPedidosResponse(BaseModel):
    items: List[PedidoEventoOut]
    total: Optional[int] = None
    limit: int
    offset: int