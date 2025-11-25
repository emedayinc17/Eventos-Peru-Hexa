"""
Inyección de Dependencias - Hexagonal Architecture
Factory functions para crear use cases con sus dependencias
"""
from typing import Generator
from sqlalchemy.orm import Session

from ev_shared.config import Settings
from ev_shared.db import session_scope

from ...infrastructure.db.repositories import (
    MySQLProveedorQueryRepository,
    MySQLHoldsRepository,
)
from ...application.use_cases import (
    BuscarProveedoresDisponiblesUseCase,
    CrearHoldUseCase,
    ConfirmarHoldUseCase,
    LiberarHoldUseCase,
    ObtenerHoldUseCase,
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

def get_proveedor_query_repository() -> MySQLProveedorQueryRepository:
    """
    Factory para el repositorio de queries de proveedores.
    Implementa el puerto ProveedorQueryPort.
    """
    return MySQLProveedorQueryRepository()


def get_holds_repository() -> MySQLHoldsRepository:
    """
    Factory para el repositorio de holds.
    Implementa el puerto HoldsCommandPort.
    """
    return MySQLHoldsRepository()


# === Use Cases (Inyección completa) ===

def get_buscar_disponibles_use_case(
    proveedor_query: MySQLProveedorQueryRepository = None
) -> BuscarProveedoresDisponiblesUseCase:
    """Factory para BuscarProveedoresDisponiblesUseCase"""
    if proveedor_query is None:
        proveedor_query = get_proveedor_query_repository()
    return BuscarProveedoresDisponiblesUseCase(proveedor_query)


def get_crear_hold_use_case(
    holds_repo: MySQLHoldsRepository = None
) -> CrearHoldUseCase:
    """Factory para CrearHoldUseCase"""
    if holds_repo is None:
        holds_repo = get_holds_repository()
    return CrearHoldUseCase(holds_repo)


def get_confirmar_hold_use_case(
    holds_repo: MySQLHoldsRepository = None
) -> ConfirmarHoldUseCase:
    """Factory para ConfirmarHoldUseCase"""
    if holds_repo is None:
        holds_repo = get_holds_repository()
    return ConfirmarHoldUseCase(holds_repo)


def get_liberar_hold_use_case(
    holds_repo: MySQLHoldsRepository = None
) -> LiberarHoldUseCase:
    """Factory para LiberarHoldUseCase"""
    if holds_repo is None:
        holds_repo = get_holds_repository()
    return LiberarHoldUseCase(holds_repo)


def get_obtener_hold_use_case(
    holds_repo: MySQLHoldsRepository = None
) -> ObtenerHoldUseCase:
    """Factory para ObtenerHoldUseCase"""
    if holds_repo is None:
        holds_repo = get_holds_repository()
    return ObtenerHoldUseCase(holds_repo)
