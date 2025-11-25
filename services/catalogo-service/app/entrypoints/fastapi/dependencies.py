"""
Inyección de Dependencias - Hexagonal Architecture
Factory functions para crear use cases con sus dependencias
"""
from typing import Generator
from sqlalchemy.orm import Session

from ev_shared.config import Settings
from ev_shared.db import session_scope

from ...infrastructure.db.repositories import MySQLCatalogoQueryService
from ...application.use_cases import (
    ListTiposEventoUseCase,
    ListServiciosPorTipoUseCase,
    ListOpcionesServicioUseCase,
    ListPaquetesUseCase,
    GetPaqueteDetalleUseCase,
)


# === Dependencias de Infraestructura ===

def get_settings() -> Settings:
    """Obtiene la configuración global de la aplicación"""
    return Settings()


def get_db_session(settings: Settings = None) -> Generator[Session, None, None]:
    """
    Proporciona una sesión de base de datos (SQLAlchemy).
    Se cierra automáticamente al finalizar la request.
    """
    if settings is None:
        settings = get_settings()
    with session_scope(settings) as session:
        yield session


# === Repositorios (Implementación de Ports) ===

def get_catalogo_query_service() -> MySQLCatalogoQueryService:
    """
    Factory para el servicio de queries de catálogo.
    Implementa el puerto CatalogoQueryService.
    """
    return MySQLCatalogoQueryService()


# === Use Cases (Inyección completa) ===

def get_list_tipos_evento_use_case(
    catalogo_service: MySQLCatalogoQueryService = None
) -> ListTiposEventoUseCase:
    """Factory para ListTiposEventoUseCase"""
    if catalogo_service is None:
        catalogo_service = get_catalogo_query_service()
    return ListTiposEventoUseCase(catalogo_service)


def get_list_servicios_por_tipo_use_case(
    catalogo_service: MySQLCatalogoQueryService = None
) -> ListServiciosPorTipoUseCase:
    """Factory para ListServiciosPorTipoUseCase"""
    if catalogo_service is None:
        catalogo_service = get_catalogo_query_service()
    return ListServiciosPorTipoUseCase(catalogo_service)


def get_list_opciones_servicio_use_case(
    catalogo_service: MySQLCatalogoQueryService = None
) -> ListOpcionesServicioUseCase:
    """Factory para ListOpcionesServicioUseCase"""
    if catalogo_service is None:
        catalogo_service = get_catalogo_query_service()
    return ListOpcionesServicioUseCase(catalogo_service)


def get_list_paquetes_use_case(
    catalogo_service: MySQLCatalogoQueryService = None
) -> ListPaquetesUseCase:
    """Factory para ListPaquetesUseCase"""
    if catalogo_service is None:
        catalogo_service = get_catalogo_query_service()
    return ListPaquetesUseCase(catalogo_service)


def get_get_paquete_detalle_use_case(
    catalogo_service: MySQLCatalogoQueryService = None
) -> GetPaqueteDetalleUseCase:
    """Factory para GetPaqueteDetalleUseCase"""
    if catalogo_service is None:
        catalogo_service = get_catalogo_query_service()
    return GetPaqueteDetalleUseCase(catalogo_service)
