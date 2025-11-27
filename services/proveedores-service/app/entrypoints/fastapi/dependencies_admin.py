from fastapi import Depends

# Use the service's dependency helpers (get_db_session) and local repositories
from .dependencies import get_db_session
from ...infrastructure.db.repositories import MySQLProveedorCommandRepository

from ...application.use_cases import (
    CreateProveedorUseCase,
    UpdateProveedorUseCase,
    DeleteProveedorUseCase,
    AddHabilidadUseCase,
    RemoveHabilidadUseCase,
    AddCalendarioUseCase,
    DeleteCalendarioUseCase,
)


def get_create_proveedor_use_case(session=Depends(get_db_session)) -> CreateProveedorUseCase:
    repo = MySQLProveedorCommandRepository()
    return CreateProveedorUseCase(repo)


def get_update_proveedor_use_case(session=Depends(get_db_session)) -> UpdateProveedorUseCase:
    repo = MySQLProveedorCommandRepository()
    return UpdateProveedorUseCase(repo)


def get_delete_proveedor_use_case(session=Depends(get_db_session)) -> DeleteProveedorUseCase:
    repo = MySQLProveedorCommandRepository()
    return DeleteProveedorUseCase(repo)


def get_add_habilidad_use_case(session=Depends(get_db_session)) -> AddHabilidadUseCase:
    repo = MySQLProveedorCommandRepository()
    return AddHabilidadUseCase(repo)


def get_remove_habilidad_use_case(session=Depends(get_db_session)) -> RemoveHabilidadUseCase:
    repo = MySQLProveedorCommandRepository()
    return RemoveHabilidadUseCase(repo)


def get_add_calendario_use_case(session=Depends(get_db_session)) -> AddCalendarioUseCase:
    repo = MySQLProveedorCommandRepository()
    return AddCalendarioUseCase(repo)


def get_delete_calendario_use_case(session=Depends(get_db_session)) -> DeleteCalendarioUseCase:
    repo = MySQLProveedorCommandRepository()
    return DeleteCalendarioUseCase(repo)
