from fastapi import APIRouter, Depends, HTTPException, status, Body
from ev_shared.config import Settings
from ev_shared.db import session_scope

# Use relative import so module resolves when package is imported as `app...`
from .dependencies_admin import (
    get_create_proveedor_use_case,
    get_update_proveedor_use_case,
    get_delete_proveedor_use_case,
    get_add_habilidad_use_case,
    get_remove_habilidad_use_case,
    get_add_calendario_use_case,
    get_delete_calendario_use_case,
)
from .security import require_user
from typing import Dict, Any
import traceback
from ev_shared.db import session_scope
from sqlalchemy import text

def require_admin(user: Dict[str, Any] = Depends(require_user)):
    with open("e:\\eventos-peru-hexagonal\\debug_proveedores.txt", "a") as f:
        f.write(f"DEBUG: require_admin user payload: {user}\n")
        role = user.get("role", "").upper()
        f.write(f"DEBUG: require_admin extracted role: {role}\n")
    
    role = user.get("role", "").upper()
    if role != "ADMIN":
        raise HTTPException(status_code=403, detail="Requiere rol ADMIN")
    return user

router = APIRouter(
    prefix="/v1/admin/proveedores", 
    tags=["proveedores-admin"],
    dependencies=[Depends(require_admin)]
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_proveedor(payload: dict = Body(...)):
    """Crea un proveedor (admin)."""
    settings = Settings()
    try:
        with session_scope(settings) as session:
            use_case = get_create_proveedor_use_case()
            return use_case.execute(
                session,
                nombre=payload.get("nombre"),
                email=payload.get("email"),
                telefono=payload.get("telefono"),
                categoria=payload.get("categoria"),
                ruc=payload.get("ruc"),
                contacto=payload.get("contacto"),
                direccion=payload.get("direccion"),
                activo=payload.get("activo"),
            )
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))


@router.put("/{proveedor_id}")
def update_proveedor(proveedor_id: str, payload: dict = Body(...)):
    settings = Settings()
    try:
        with session_scope(settings) as session:
            use_case = get_update_proveedor_use_case()
            return use_case.execute(
                session,
                proveedor_id=proveedor_id,
                nombre=payload.get("nombre"),
                email=payload.get("email"),
                telefono=payload.get("telefono"),
                categoria=payload.get("categoria"),
                ruc=payload.get("ruc"),
                contacto=payload.get("contacto"),
                direccion=payload.get("direccion"),
                activo=payload.get("activo"),
            )
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/{proveedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proveedor(proveedor_id: str):
    settings = Settings()
    try:
        with session_scope(settings) as session:
            use_case = get_delete_proveedor_use_case()
            use_case.execute(session, proveedor_id=proveedor_id)
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
    return None


@router.post("/{proveedor_id}/habilidades", status_code=status.HTTP_201_CREATED)
def add_habilidad(proveedor_id: str, payload: dict = Body(...)):
    settings = Settings()
    try:
        with session_scope(settings) as session:
            use_case = get_add_habilidad_use_case()
            return use_case.execute(session, proveedor_id=proveedor_id, servicio_id=payload.get("servicio_id"), nivel=payload.get("nivel", 1))
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/{proveedor_id}/habilidades/{habilidad_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_habilidad(proveedor_id: str, habilidad_id: str):
    settings = Settings()
    try:
        with session_scope(settings) as session:
            use_case = get_remove_habilidad_use_case()
            use_case.execute(session, proveedor_id=proveedor_id, servicio_id=habilidad_id)
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
    return None


@router.post("/{proveedor_id}/calendario", status_code=status.HTTP_201_CREATED)
def add_calendario(proveedor_id: str, payload: dict = Body(...)):
    settings = Settings()
    try:
        with session_scope(settings) as session:
            use_case = get_add_calendario_use_case()
            return use_case.execute(session, proveedor_id=proveedor_id, tipo=payload.get("tipo"), inicio=payload.get("inicio"), fin=payload.get("fin"), motivo=payload.get("motivo"))
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/{proveedor_id}/calendario/{calendario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendario(proveedor_id: str, calendario_id: str):
    settings = Settings()
    try:
        with session_scope(settings) as session:
            use_case = get_delete_calendario_use_case()
            use_case.execute(session, proveedor_id=proveedor_id, calendario_id=calendario_id)
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
    return None


@router.get("")
def list_proveedores():
    """Lista todos los proveedores (admin)."""
    from sqlalchemy import text
    settings = Settings()
    try:
        with session_scope(settings) as session:
            # Simple query to list all providers
            rows = session.execute(text("SELECT * FROM proveedor WHERE is_deleted = 0 ORDER BY created_at DESC")).mappings().all()
            return [dict(row) for row in rows]
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/metrics")
def admin_metrics():
    """Simple admin metrics for Proveedores: return total providers count."""
    settings = Settings()
    try:
        with session_scope(settings) as session:
            row = session.execute(text("SELECT COUNT(1) AS total FROM proveedor WHERE is_deleted = 0")).mappings().first()
            total = int(row["total"]) if row and row.get("total") is not None else 0
            return {"total": total}
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
