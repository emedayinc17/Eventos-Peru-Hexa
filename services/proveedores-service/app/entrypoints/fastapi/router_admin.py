from fastapi import APIRouter, Depends, HTTPException, status, Body

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

router = APIRouter(prefix="/v1/admin/proveedores", tags=["proveedores-admin"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_proveedor(payload: dict = Body(...), ):
    """Crea un proveedor (admin).

    Payload es un JSON genérico con los campos necesarios según el dominio.
    """
    try:
        use_case = get_create_proveedor_use_case()
        created_id = use_case.execute(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"id": created_id}


@router.put("/{proveedor_id}")
def update_proveedor(proveedor_id: str, payload: dict = Body(...)):
    try:
        use_case = get_update_proveedor_use_case()
        use_case.execute(proveedor_id, payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"id": proveedor_id}


@router.delete("/{proveedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proveedor(proveedor_id: str):
    try:
        use_case = get_delete_proveedor_use_case()
        use_case.execute(proveedor_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return None


@router.post("/{proveedor_id}/habilidades", status_code=status.HTTP_201_CREATED)
def add_habilidad(proveedor_id: str, payload: dict = Body(...)):
    try:
        use_case = get_add_habilidad_use_case()
        hid = use_case.execute(proveedor_id, payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"habilidad_id": hid}


@router.delete("/{proveedor_id}/habilidades/{habilidad_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_habilidad(proveedor_id: str, habilidad_id: str):
    try:
        use_case = get_remove_habilidad_use_case()
        use_case.execute(proveedor_id, habilidad_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return None


@router.post("/{proveedor_id}/calendario", status_code=status.HTTP_201_CREATED)
def add_calendario(proveedor_id: str, payload: dict = Body(...)):
    try:
        use_case = get_add_calendario_use_case()
        cid = use_case.execute(proveedor_id, payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"calendario_id": cid}


@router.delete("/{proveedor_id}/calendario/{calendario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendario(proveedor_id: str, calendario_id: str):
    try:
        use_case = get_delete_calendario_use_case()
        use_case.execute(proveedor_id, calendario_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return None
