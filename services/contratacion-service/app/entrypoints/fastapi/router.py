# services/contratacion-service/app/entrypoints/fastapi/router.py

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from ev_shared.config import Settings

# === DTOs (entrypoint) ===
from .schemas import (
    Health,
    CrearPedidoDesdePaquete,
    CrearPedidoCustom,
    PedidoEventoOut,
    EnviarResumenRequest,
    EnviarResumenResponse,
    # Admin
    AdminPatchEstadoRequest,
    AdminAddItemsRequest,
    AdminDeleteItemsRequest,
    AdminAsignarProveedorRequest,
)

# === Seguridad (entrypoint) ===
from .security import get_current_user, require_role

# === Casos de uso (application/commands) — aquí está tu SQL real ===
from ...application import commands

router = APIRouter(tags=["contratacion"])

# Callable para evitar que FastAPI intente documentar Settings en OpenAPI
def get_settings() -> Settings:
    return Settings()

# --- Infra ---
@router.get(
    "/health",
    response_model=Health,
    operation_id="contratacion_health",
    openapi_extra={"security": []},
)
def health():
    """Ping rápido sin tocar DB."""
    return {"status": "ok"}


# ===========================
#     CLIENTE (protegido)
# ===========================

@router.post(
    "/v1/contratacion/pedidos",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    operation_id="contratacion_crear_pedido",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def crear_pedido(
    body: Dict[str, Any],
    settings: Settings = Depends(get_settings),
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Acepta oneOf:
      - CrearPedidoDesdePaquete
      - CrearPedidoCustom
    """
    try:
        if "paquete_id" in body:
            payload = CrearPedidoDesdePaquete(**body).model_dump()
            return commands.crear_pedido_desde_paquete(settings, user["id"], payload)
        else:
            payload = CrearPedidoCustom(**body).model_dump()
            return commands.crear_pedido_custom(settings, user["id"], payload)
    except ValueError as e:
        # errores de validación de negocio
        raise HTTPException(status_code=400, detail={"code": str(e)})
    except Exception:
        raise HTTPException(status_code=500, detail={"code": "ERR_CREAR_PEDIDO"})


@router.get(
    "/v1/contratacion/pedidos/mios",
    response_model=Dict[str, Any],
    operation_id="contratacion_listar_mis_pedidos",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def mis_pedidos(
    settings: Settings = Depends(get_settings),
    user: Dict[str, Any] = Depends(get_current_user),
):
    data = commands.listar_mis_pedidos(settings, user["id"])
    return {"items": data}


@router.get(
    "/v1/contratacion/pedidos/{pedido_id}",
    response_model=PedidoEventoOut,
    operation_id="contratacion_detalle_pedido",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def detalle_pedido(
    pedido_id: str,
    settings: Settings = Depends(get_settings),
    user: Dict[str, Any] = Depends(get_current_user),
):
    try:
        return commands.obtener_pedido(settings, user["id"], pedido_id)
    except ValueError:
        raise HTTPException(status_code=404, detail={"code": "PEDIDO_NO_ENCONTRADO"})


@router.post(
    "/v1/contratacion/pedidos/{pedido_id}/enviar-resumen",
    response_model=EnviarResumenResponse,
    status_code=status.HTTP_202_ACCEPTED,
    operation_id="contratacion_enviar_resumen",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def enviar_resumen(
    pedido_id: str,
    body: EnviarResumenRequest,
    settings: Settings = Depends(get_settings),
    user: Dict[str, Any] = Depends(get_current_user),
):
    try:
        return commands.enviar_resumen_pedido(settings, user["id"], pedido_id, body.to_email)
    except ValueError:
        raise HTTPException(status_code=404, detail={"code": "PEDIDO_NO_ENCONTRADO"})
    except Exception:
        raise HTTPException(status_code=500, detail={"code": "ERR_OUTBOX"})


# ===========================
#       ADMIN (protegido)
# ===========================

@router.patch(
    "/v1/contratacion/admin/pedidos/{pedido_id}",
    operation_id="contratacion_admin_patch_estado",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_patch_estado(
    pedido_id: str,
    body: AdminPatchEstadoRequest,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
):
    try:
        return commands.admin_cambiar_estado(settings, pedido_id, body.estado)
    except ValueError as e:
        msg = str(e)
        if msg.startswith("TRANSICION_INVALIDA") or msg in ("TOTAL_INVALIDO",):
            raise HTTPException(status_code=400, detail={"code": msg})
        if msg == "PEDIDO_NO_ENCONTRADO":
            raise HTTPException(status_code=404, detail={"code": msg})
        raise HTTPException(status_code=500, detail={"code": "ERR_PATCH_ESTADO"})


@router.post(
    "/v1/contratacion/admin/pedidos/{pedido_id}/items",
    status_code=status.HTTP_200_OK,
    operation_id="contratacion_admin_add_items",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_add_items(
    pedido_id: str,
    body: AdminAddItemsRequest,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
):
    try:
        payload = [i.model_dump() for i in body.items]
        return commands.admin_agregar_items(settings, pedido_id, payload)
    except ValueError as e:
        msg = str(e)
        if msg in ("ITEMS_VACIOS", "OPCION_SIN_PRECIO_VIGENTE"):
            raise HTTPException(status_code=400, detail={"code": msg})
        if msg == "PEDIDO_NO_ENCONTRADO":
            raise HTTPException(status_code=404, detail={"code": msg})
        raise HTTPException(status_code=500, detail={"code": "ERR_ADD_ITEMS"})


@router.delete(
    "/v1/contratacion/admin/pedidos/{pedido_id}/items",
    status_code=status.HTTP_200_OK,
    operation_id="contratacion_admin_delete_items",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_delete_items(
    pedido_id: str,
    body: AdminDeleteItemsRequest,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
):
    try:
        return commands.admin_eliminar_items(settings, pedido_id, body.item_ids)
    except ValueError as e:
        msg = str(e)
        if msg in ("ITEM_IDS_VACIOS",):
            raise HTTPException(status_code=400, detail={"code": msg})
        if msg == "PEDIDO_NO_ENCONTRADO":
            raise HTTPException(status_code=404, detail={"code": msg})
        raise HTTPException(status_code=500, detail={"code": "ERR_DELETE_ITEMS"})


@router.post(
    "/v1/contratacion/admin/pedidos/{pedido_id}/asignar-proveedor",
    status_code=status.HTTP_200_OK,
    operation_id="contratacion_admin_asignar_proveedor",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_asignar_proveedor(
    pedido_id: str,
    body: AdminAsignarProveedorRequest,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
):
    try:
        return commands.admin_asignar_proveedor(
            settings,
            pedido_id=pedido_id,
            proveedor_id=body.proveedor_id,
            fecha_inicio=body.fecha_inicio,
            fecha_fin=body.fecha_fin,
            hold_id=body.hold_id,
        )
    except ValueError as e:
        msg = str(e)
        if msg in ("PEDIDO_NO_ENCONTRADO",):
            raise HTTPException(status_code=404, detail={"code": msg})
        if msg in ("ESTADO_NO_PERMITE_ASIGNACION", "HOLD_INVALIDO", "CONFLICTO_PROVEEDOR"):
            raise HTTPException(status_code=400, detail={"code": msg})
        raise HTTPException(status_code=500, detail={"code": "ERR_ASIGNAR_PROVEEDOR"})


def build_api_router(settings: Settings) -> APIRouter:
    # Mantén la firma por consistencia; si más adelante quieres usar settings,
    # podrás extender esta función sin tocar main.py.
    return router
