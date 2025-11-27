"""
Inyección de Dependencias - Hexagonal Architecture
Factory functions para crear use cases con sus dependencias
"""
from typing import Generator
from sqlalchemy.orm import Session

from ev_shared.config import Settings
from ev_shared.db import session_scope
from fastapi import HTTPException

from ...infrastructure.db.repositories import MySQLCatalogoQueryService
from ...infrastructure.db.repositories import MySQLCatalogoQueryService, MySQLCatalogoCommandRepository
from ...application.use_cases import (
    ListTiposEventoUseCase,
    ListServiciosPorTipoUseCase,
    ListOpcionesServicioUseCase,
    ListPaquetesUseCase,
    GetPaqueteDetalleUseCase,
    CreateTipoEventoUseCase,
    UpdateTipoEventoUseCase,
    DeleteTipoEventoUseCase,
    CreateServicioUseCase,
    UpdateServicioUseCase,
    DeleteServicioUseCase,
    CreateOpcionUseCase,
    UpdateOpcionUseCase,
    DeleteOpcionUseCase,
    CreatePaqueteUseCase,
    UpdatePaqueteUseCase,
    DeletePaqueteUseCase,
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
    try:
        with session_scope(settings) as session:
            yield session
    except Exception as e:
        # Conectar a la DB falló — devolver 503 para indicar dependencia no disponible
        raise HTTPException(status_code=503, detail="Database unavailable")


# === Repositorios (Implementación de Ports) ===

def get_catalogo_query_service() -> MySQLCatalogoQueryService:
    """
    Factory para el servicio de queries de catálogo.
    Implementa el puerto CatalogoQueryService.
    """
    return MySQLCatalogoQueryService()


def get_catalogo_command_repository() -> MySQLCatalogoCommandRepository:
    """Factory para el repositorio de comandos del catálogo."""
    return MySQLCatalogoCommandRepository()


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


def get_create_tipo_evento_use_case(
    repo: MySQLCatalogoCommandRepository = None
) -> CreateTipoEventoUseCase:
    if repo is None:
        repo = get_catalogo_command_repository()
    return CreateTipoEventoUseCase(repo)


def get_create_servicio_use_case(
    repo: MySQLCatalogoCommandRepository = None
) -> CreateServicioUseCase:
    if repo is None:
        repo = get_catalogo_command_repository()
    return CreateServicioUseCase(repo)


def get_update_servicio_use_case(
    repo: MySQLCatalogoCommandRepository = None
) -> UpdateServicioUseCase:
    if repo is None:
        repo = get_catalogo_command_repository()
    return UpdateServicioUseCase(repo)


def get_delete_servicio_use_case(
    repo: MySQLCatalogoCommandRepository = None
) -> DeleteServicioUseCase:
    if repo is None:
        repo = get_catalogo_command_repository()
    return DeleteServicioUseCase(repo)


def get_create_opcion_use_case(
    repo: MySQLCatalogoCommandRepository = None
) -> CreateOpcionUseCase:
    if repo is None:
        repo = get_catalogo_command_repository()
    return CreateOpcionUseCase(repo)


def get_update_opcion_use_case(
    repo: MySQLCatalogoCommandRepository = None
) -> UpdateOpcionUseCase:
    if repo is None:
        repo = get_catalogo_command_repository()
    return UpdateOpcionUseCase(repo)


def get_delete_opcion_use_case(
    repo: MySQLCatalogoCommandRepository = None
) -> DeleteOpcionUseCase:
    if repo is None:
        repo = get_catalogo_command_repository()
    return DeleteOpcionUseCase(repo)


def get_create_paquete_use_case(
    repo: MySQLCatalogoCommandRepository = None
) -> CreatePaqueteUseCase:
    if repo is None:
        repo = get_catalogo_command_repository()
    return CreatePaqueteUseCase(repo)


def get_update_paquete_use_case(
    repo: MySQLCatalogoCommandRepository = None
) -> UpdatePaqueteUseCase:
    if repo is None:
        repo = get_catalogo_command_repository()
    return UpdatePaqueteUseCase(repo)


def get_delete_paquete_use_case(
    repo: MySQLCatalogoCommandRepository = None
) -> DeletePaqueteUseCase:
    if repo is None:
        repo = get_catalogo_command_repository()
    return DeletePaqueteUseCase(repo)


def get_update_tipo_evento_use_case(
    repo: MySQLCatalogoCommandRepository = None
) -> UpdateTipoEventoUseCase:
    if repo is None:
        repo = get_catalogo_command_repository()
    return UpdateTipoEventoUseCase(repo)


def get_delete_tipo_evento_use_case(
    repo: MySQLCatalogoCommandRepository = None
) -> DeleteTipoEventoUseCase:
    if repo is None:
        repo = get_catalogo_command_repository()
    return DeleteTipoEventoUseCase(repo)
