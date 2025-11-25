"""
Dependencias FastAPI para Catálogo Service - Hexagonal Architecture
Inyección de dependencias: repositorios y use cases
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


# ============================================================================
# DEPENDENCIAS DE INFRAESTRUCTURA
# ============================================================================

def get_catalogo_query_service() -> MySQLCatalogoQueryService:
    """
    Dependencia: instancia del repositorio de lectura.
    Se crea una vez por request (singleton en scope request).
    """
    return MySQLCatalogoQueryService()


# ============================================================================
# DEPENDENCIAS DE USE CASES
# ============================================================================

def get_list_tipos_evento_use_case(
    catalogo_service: MySQLCatalogoQueryService = None
) -> ListTiposEventoUseCase:
    """Dependencia: Use Case para listar tipos de evento"""
    if catalogo_service is None:
        catalogo_service = get_catalogo_query_service()
    return ListTiposEventoUseCase(catalogo_service)


def get_list_servicios_use_case(
    catalogo_service: MySQLCatalogoQueryService = None
) -> ListServiciosPorTipoUseCase:
    """Dependencia: Use Case para listar servicios"""
    if catalogo_service is None:
        catalogo_service = get_catalogo_query_service()
    return ListServiciosPorTipoUseCase(catalogo_service)


def get_list_opciones_use_case(
    catalogo_service: MySQLCatalogoQueryService = None
) -> ListOpcionesServicioUseCase:
    """Dependencia: Use Case para listar opciones de servicio"""
    if catalogo_service is None:
        catalogo_service = get_catalogo_query_service()
    return ListOpcionesServicioUseCase(catalogo_service)


def get_list_paquetes_use_case(
    catalogo_service: MySQLCatalogoQueryService = None
) -> ListPaquetesUseCase:
    """Dependencia: Use Case para listar paquetes"""
    if catalogo_service is None:
        catalogo_service = get_catalogo_query_service()
    return ListPaquetesUseCase(catalogo_service)


def get_paquete_detalle_use_case(
    catalogo_service: MySQLCatalogoQueryService = None
) -> GetPaqueteDetalleUseCase:
    """Dependencia: Use Case para obtener detalle de paquete"""
    if catalogo_service is None:
        catalogo_service = get_catalogo_query_service()
    return GetPaqueteDetalleUseCase(catalogo_service)


# ============================================================================
# DEPENDENCIA DE SESIÓN DB (context manager)
# ============================================================================

def get_db_session(settings: Settings):
    """
    Generador de sesión de base de datos.
    NO usar con Depends() - se llama manualmente en cada endpoint.
    """
    with session_scope(settings) as session:
        yield session
