"""
Inyección de Dependencias - Hexagonal Architecture (Contratación)
Factory functions para crear use cases con sus dependencias
"""
from typing import Generator
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends

from ev_shared.config import Settings, load_settings
from ev_shared.db import session_scope

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
from ...application.use_cases.admin_metrics import AdminMetricsUseCase
from ...application.use_cases.client_metrics import ClientMetricsUseCase
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

def get_catalogo_client(settings: Settings = Depends(get_settings)) -> CatalogoClient:
    """Factory para cliente HTTP de Catálogo"""
    return CatalogoClient(settings)


def get_proveedores_client(settings: Settings = Depends(get_settings)) -> ProveedoresClient:
    """Factory para cliente HTTP de Proveedores"""
    return ProveedoresClient(settings)


def get_iam_client(settings: Settings = Depends(get_settings)) -> IamClient:
    """Factory para cliente HTTP de IAM"""
    return IamClient(settings)


# === Use Cases ===

def get_crear_pedido_desde_paquete_use_case(
    pedido_repo: MySQLPedidoRepository = Depends(get_pedido_repository),
    item_repo: MySQLItemPedidoRepository = Depends(get_item_pedido_repository),
    reserva_repo: MySQLReservaRepository = Depends(get_reserva_repository),
    catalogo_client: CatalogoClient = Depends(get_catalogo_client)
) -> CrearPedidoDesdePaqueteUseCase:
    """Factory para CrearPedidoDesdePaqueteUseCase"""
    return CrearPedidoDesdePaqueteUseCase(pedido_repo, item_repo, reserva_repo, catalogo_client)


def get_crear_pedido_custom_use_case(
    pedido_repo: MySQLPedidoRepository = Depends(get_pedido_repository),
    item_repo: MySQLItemPedidoRepository = Depends(get_item_pedido_repository),
    catalogo_client: CatalogoClient = Depends(get_catalogo_client)
) -> CrearPedidoCustomUseCase:
    """Factory para CrearPedidoCustomUseCase"""
    return CrearPedidoCustomUseCase(pedido_repo, item_repo, catalogo_client)


def get_listar_pedidos_cliente_use_case(
    pedido_repo: MySQLPedidoRepository = Depends(get_pedido_repository)
) -> ListarPedidosClienteUseCase:
    """Factory para ListarPedidosClienteUseCase"""
    return ListarPedidosClienteUseCase(pedido_repo)


def get_listar_pedidos_admin_use_case(
    pedido_repo: MySQLPedidoRepository = Depends(get_pedido_repository),
    iam_client: IamClient = Depends(get_iam_client),
    catalogo_client: CatalogoClient = Depends(get_catalogo_client)
) -> ListarPedidosAdminUseCase:
    """Factory para ListarPedidosAdminUseCase"""
    return ListarPedidosAdminUseCase(pedido_repo, iam_client, catalogo_client)


def get_obtener_pedido_detalle_use_case(
    pedido_repo: MySQLPedidoRepository = Depends(get_pedido_repository),
    item_repo: MySQLItemPedidoRepository = Depends(get_item_pedido_repository),
    reserva_repo: MySQLReservaRepository = Depends(get_reserva_repository),
    iam_client: IamClient = Depends(get_iam_client),
    catalogo_client: CatalogoClient = Depends(get_catalogo_client)
) -> ObtenerPedidoDetalleUseCase:
    """Factory para ObtenerPedidoDetalleUseCase"""
    return ObtenerPedidoDetalleUseCase(pedido_repo, item_repo, reserva_repo, iam_client, catalogo_client)


def get_admin_cambiar_estado_use_case(
    pedido_repo: MySQLPedidoRepository = Depends(get_pedido_repository),
    reserva_repo: MySQLReservaRepository = Depends(get_reserva_repository),
    proveedores_client: ProveedoresClient = Depends(get_proveedores_client)
) -> AdminCambiarEstadoPedidoUseCase:
    """Factory para AdminCambiarEstadoPedidoUseCase"""
    return AdminCambiarEstadoPedidoUseCase(pedido_repo, reserva_repo, proveedores_client)


def get_admin_asignar_proveedor_use_case(
    pedido_repo: MySQLPedidoRepository = Depends(get_pedido_repository),
    item_repo: MySQLItemPedidoRepository = Depends(get_item_pedido_repository),
    reserva_repo: MySQLReservaRepository = Depends(get_reserva_repository),
    proveedores_client: ProveedoresClient = Depends(get_proveedores_client)
) -> AdminAsignarProveedorUseCase:
    """Factory para AdminAsignarProveedorUseCase"""
    return AdminAsignarProveedorUseCase(
        pedido_repo,
        item_repo,
        reserva_repo,
        proveedores_client
    )


def get_admin_metrics_use_case(
    pedido_repo: MySQLPedidoRepository = Depends(get_pedido_repository)
) -> AdminMetricsUseCase:
    return AdminMetricsUseCase(pedido_repo)


def get_client_metrics_use_case(
    pedido_repo: MySQLPedidoRepository = Depends(get_pedido_repository)
) -> ClientMetricsUseCase:
    return ClientMetricsUseCase(pedido_repo)


def get_admin_add_items_use_case(
    pedido_repo: MySQLPedidoRepository = Depends(get_pedido_repository),
    item_repo: MySQLItemPedidoRepository = Depends(get_item_pedido_repository),
    catalogo_client: CatalogoClient = Depends(get_catalogo_client)
) -> AdminAddItemsUseCase:
    """Factory para AdminAddItemsUseCase"""
    return AdminAddItemsUseCase(pedido_repo, item_repo, catalogo_client)


def get_admin_delete_items_use_case(
    pedido_repo: MySQLPedidoRepository = Depends(get_pedido_repository),
    item_repo: MySQLItemPedidoRepository = Depends(get_item_pedido_repository),
    reserva_repo: MySQLReservaRepository = Depends(get_reserva_repository)
) -> AdminDeleteItemsUseCase:
    """Factory para AdminDeleteItemsUseCase"""
    return AdminDeleteItemsUseCase(pedido_repo, item_repo, reserva_repo)
