"""
Inyección de Dependencias - Hexagonal Architecture (Contratación)
Factory functions para crear use cases con sus dependencias
"""
from typing import Generator
from sqlalchemy.orm import Session

from ev_shared.config import Settings, load_settings
from ev_shared.db import session_scope
from fastapi import HTTPException

# Infrastructure
from ...infrastructure.db.repositories import (
    MySQLPedidoRepository,
    MySQLItemPedidoRepository,
    MySQLReservaRepository,
)
from ...infrastructure.http.catalogo_client import CatalogoClient
from ...infrastructure.http.proveedores_client import ProveedoresClient
from ...infrastructure.http.iam_client import IamClient

# Use Cases
from ...application.use_cases import (
    CrearPedidoDesdePaqueteUseCase,
    CrearPedidoCustomUseCase,
    ListarPedidosClienteUseCase,
    ListarPedidosAdminUseCase,
    ObtenerPedidoDetalleUseCase,
    AdminCambiarEstadoPedidoUseCase,
    AdminAsignarProveedorUseCase,
)
from ...application.use_cases.admin_add_items import AdminAddItemsUseCase
from ...application.use_cases.admin_delete_items import AdminDeleteItemsUseCase


# === Dependencias de Infraestructura ===

def get_settings() -> Settings:
    """Obtiene la configuración global de la aplicación"""
    return load_settings(service_name="contratacion-service")


def get_db_session(settings: Settings = None) -> Generator[Session, None, None]:
    """
    Proporciona una sesión de base de datos (SQLAlchemy).
    Se cierra automáticamente al finalizar la request.
    """
    if settings is None:
        settings = get_settings()
    try:
        with session_scope(settings) as session:
            yield session
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")


# === Repositorios (Implementación de Ports) ===

def get_pedido_repository() -> MySQLPedidoRepository:
    """Factory para el repositorio de pedidos"""
    return MySQLPedidoRepository()


def get_item_pedido_repository() -> MySQLItemPedidoRepository:
    """Factory para el repositorio de items de pedido"""
    return MySQLItemPedidoRepository()


def get_reserva_repository() -> MySQLReservaRepository:
    """Factory para el repositorio de reservas"""
    return MySQLReservaRepository()


# === HTTP Clients (Servicios Externos) ===

def get_catalogo_client(settings: Settings = None) -> CatalogoClient:
    """Factory para cliente HTTP de Catálogo"""
    if settings is None:
        settings = get_settings()
    return CatalogoClient(settings)


def get_proveedores_client(settings: Settings = None) -> ProveedoresClient:
    """Factory para cliente HTTP de Proveedores"""
    if settings is None:
        settings = get_settings()
    return ProveedoresClient(settings)


def get_iam_client(settings: Settings = None) -> IamClient:
    """Factory para cliente HTTP de IAM"""
    if settings is None:
        settings = get_settings()
    return IamClient(settings)


# === Use Cases ===

def get_crear_pedido_desde_paquete_use_case(
    pedido_repo: MySQLPedidoRepository = None,
    item_repo: MySQLItemPedidoRepository = None,
    reserva_repo: MySQLReservaRepository = None,
    catalogo_client: CatalogoClient = None
) -> CrearPedidoDesdePaqueteUseCase:
    """Factory para CrearPedidoDesdePaqueteUseCase"""
    if pedido_repo is None:
        pedido_repo = get_pedido_repository()
    if item_repo is None:
        item_repo = get_item_pedido_repository()
    if reserva_repo is None:
        reserva_repo = get_reserva_repository()
    if catalogo_client is None:
        catalogo_client = get_catalogo_client()
    
    return CrearPedidoDesdePaqueteUseCase(pedido_repo, item_repo, reserva_repo, catalogo_client)


def get_crear_pedido_custom_use_case(
    pedido_repo: MySQLPedidoRepository = None,
    item_repo: MySQLItemPedidoRepository = None,
    catalogo_client: CatalogoClient = None
) -> CrearPedidoCustomUseCase:
    """Factory para CrearPedidoCustomUseCase"""
    if pedido_repo is None:
        pedido_repo = get_pedido_repository()
    if item_repo is None:
        item_repo = get_item_pedido_repository()
    if catalogo_client is None:
        catalogo_client = get_catalogo_client()
    
    return CrearPedidoCustomUseCase(pedido_repo, item_repo, catalogo_client)


def get_listar_pedidos_cliente_use_case(
    pedido_repo: MySQLPedidoRepository = None
) -> ListarPedidosClienteUseCase:
    """Factory para ListarPedidosClienteUseCase"""
    if pedido_repo is None:
        pedido_repo = get_pedido_repository()
    return ListarPedidosClienteUseCase(pedido_repo)


def get_listar_pedidos_admin_use_case(
    pedido_repo: MySQLPedidoRepository = None,
    iam_client: IamClient = None,
    catalogo_client: CatalogoClient = None
) -> ListarPedidosAdminUseCase:
    """Factory para ListarPedidosAdminUseCase"""
    if pedido_repo is None:
        pedido_repo = get_pedido_repository()
    if iam_client is None:
        iam_client = get_iam_client()
    if catalogo_client is None:
        catalogo_client = get_catalogo_client()
    
    return ListarPedidosAdminUseCase(pedido_repo, iam_client, catalogo_client)


def get_obtener_pedido_detalle_use_case(
    pedido_repo: MySQLPedidoRepository = None,
    item_repo: MySQLItemPedidoRepository = None,
    reserva_repo: MySQLReservaRepository = None,
    iam_client: IamClient = None,
    catalogo_client: CatalogoClient = None
) -> ObtenerPedidoDetalleUseCase:
    """Factory para ObtenerPedidoDetalleUseCase"""
    if pedido_repo is None:
        pedido_repo = get_pedido_repository()
    if item_repo is None:
        item_repo = get_item_pedido_repository()
    if reserva_repo is None:
        reserva_repo = get_reserva_repository()
    if iam_client is None:
        iam_client = get_iam_client()
    if catalogo_client is None:
        catalogo_client = get_catalogo_client()
    
    return ObtenerPedidoDetalleUseCase(pedido_repo, item_repo, reserva_repo, iam_client, catalogo_client)


def get_admin_cambiar_estado_use_case(
    pedido_repo: MySQLPedidoRepository = None,
    reserva_repo: MySQLReservaRepository = None,
    proveedores_client: ProveedoresClient = None
) -> AdminCambiarEstadoPedidoUseCase:
    """Factory para AdminCambiarEstadoPedidoUseCase"""
    if pedido_repo is None:
        pedido_repo = get_pedido_repository()
    if reserva_repo is None:
        reserva_repo = get_reserva_repository()
    if proveedores_client is None:
        proveedores_client = get_proveedores_client()
    
    return AdminCambiarEstadoPedidoUseCase(pedido_repo, reserva_repo, proveedores_client)


def get_admin_asignar_proveedor_use_case(
    pedido_repo: MySQLPedidoRepository = None,
    item_repo: MySQLItemPedidoRepository = None,
    reserva_repo: MySQLReservaRepository = None,
    proveedores_client: ProveedoresClient = None
) -> AdminAsignarProveedorUseCase:
    """Factory para AdminAsignarProveedorUseCase"""
    if pedido_repo is None:
        pedido_repo = get_pedido_repository()
    if item_repo is None:
        item_repo = get_item_pedido_repository()
    if reserva_repo is None:
        reserva_repo = get_reserva_repository()
    if proveedores_client is None:
        proveedores_client = get_proveedores_client()
    
    return AdminAsignarProveedorUseCase(
        pedido_repo,
        item_repo,
        reserva_repo,
        proveedores_client
    )


def get_admin_add_items_use_case(
    pedido_repo: MySQLPedidoRepository = None,
    item_repo: MySQLItemPedidoRepository = None,
    catalogo_client: CatalogoClient = None
) -> AdminAddItemsUseCase:
    """Factory para AdminAddItemsUseCase"""
    if pedido_repo is None:
        pedido_repo = get_pedido_repository()
    if item_repo is None:
        item_repo = get_item_pedido_repository()
    if catalogo_client is None:
        catalogo_client = get_catalogo_client()
    
    return AdminAddItemsUseCase(pedido_repo, item_repo, catalogo_client)


def get_admin_delete_items_use_case(
    pedido_repo: MySQLPedidoRepository = None,
    item_repo: MySQLItemPedidoRepository = None,
    reserva_repo: MySQLReservaRepository = None
) -> AdminDeleteItemsUseCase:
    """Factory para AdminDeleteItemsUseCase"""
    if pedido_repo is None:
        pedido_repo = get_pedido_repository()
    if item_repo is None:
        item_repo = get_item_pedido_repository()
    if reserva_repo is None:
        reserva_repo = get_reserva_repository()
    
    return AdminDeleteItemsUseCase(pedido_repo, item_repo, reserva_repo)
