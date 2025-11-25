"""
Router Interno de Proveedores (Hexagonal Architecture)
Endpoints internos - validación X-Service-Token
CAPA DE ORQUESTACIÓN - SIN lógica de negocio
"""
from dataclasses import asdict
from fastapi import APIRouter, HTTPException, Header, status, Body, Path
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from ev_shared.config import Settings

from ...domain.exceptions import (
    HoldNoEncontrado,
    HoldExpirado,
    HoldInvalidoError,
    ConflictoDisponibilidadError,
    RangoTiempoInvalido,
)
from .dependencies import (
    get_db_session,
    get_crear_hold_use_case,
    get_confirmar_hold_use_case,
    get_liberar_hold_use_case,
    get_obtener_hold_use_case,
)


# === Validation Middleware ===
def validate_internal_token(
    x_service_token: str = Header(None, alias="X-Service-Token"),
    settings: Settings = None
):
    """
    Valida que el request venga de un servicio interno autorizado.
    Requiere X-Service-Token header con el token compartido.
    """
    if settings is None:
        settings = Settings()
    if x_service_token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=403, detail="Token de servicio inválido")
    return True


# === Schemas ===
class CrearHoldIn(BaseModel):
    proveedor_id: str = Field(..., description="ID del proveedor")
    opcion_servicio_id: str = Field(..., description="Opción de servicio a reservar")
    inicio: str = Field(..., description="Datetime ISO, ej: 2025-10-14T14:00:00")
    fin: str = Field(..., description="Datetime ISO, ej: 2025-10-14T18:00:00")
    ttl_min: int = Field(default=30, ge=5, le=1440, description="Minutos hasta expiración (default 30)")
    correlation_id: Optional[str] = Field(default=None)
    created_by: Optional[str] = Field(default="contratacion-service", description="Identificador del servicio que crea el hold")


class HoldOut(BaseModel):
    id: str
    proveedor_id: str
    opcion_servicio_id: str
    inicio: str
    fin: str
    expira_en: str
    status: int = 0


def build_internal_router(settings: Settings) -> APIRouter:
    """
    Construye el router interno de Proveedores.
    Todos los endpoints requieren X-Service-Token header.
    """
    r = APIRouter(tags=["proveedores-internal"])

    # === POST /internal/holds ===
    @r.post("/internal/holds", status_code=status.HTTP_201_CREATED, response_model=HoldOut)
    def crear_hold_interno(
        body: CrearHoldIn = Body(...),
        x_service_token: str = Header(None, alias="X-Service-Token"),
    ):
        """
        Crea un hold temporal (reserva) para un proveedor.
        INTERNO: Requiere X-Service-Token header.
        """
        # Validar X-Service-Token
        if x_service_token != settings.INTERNAL_SERVICE_TOKEN:
            raise HTTPException(status_code=403, detail="Token de servicio inválido")

        use_case = get_crear_hold_use_case()
        
        for session in get_db_session(settings):
            try:
                hold = use_case.execute(
                    session,
                    proveedor_id=body.proveedor_id,
                    opcion_servicio_id=body.opcion_servicio_id,
                    inicio=datetime.fromisoformat(body.inicio),
                    fin=datetime.fromisoformat(body.fin),
                    ttl_min=body.ttl_min,
                    correlation_id=body.correlation_id,
                    created_by=body.created_by
                )
            except RangoTiempoInvalido as e:
                raise HTTPException(status_code=400, detail=str(e))
            except ConflictoDisponibilidadError as e:
                raise HTTPException(status_code=409, detail=str(e))

        return HoldOut(
            id=hold.id,
            proveedor_id=hold.proveedor_id,
            opcion_servicio_id=hold.opcion_servicio_id,
            inicio=str(hold.inicio),
            fin=str(hold.fin),
            expira_en=str(hold.expira_en),
            status=hold.status,
        )

    # === PATCH /internal/holds/{hold_id}/confirm ===
    @r.patch("/internal/holds/{hold_id}/confirm", status_code=status.HTTP_200_OK)
    def confirmar_hold_interno(
        hold_id: str = Path(...),
        x_service_token: str = Header(None, alias="X-Service-Token"),
    ) -> Dict[str, Any]:
        """
        Confirma un hold temporal (status 0 → 1).
        INTERNO: Requiere X-Service-Token header.
        """
        if x_service_token != settings.INTERNAL_SERVICE_TOKEN:
            raise HTTPException(status_code=403, detail="Token de servicio inválido")

        use_case = get_confirmar_hold_use_case()
        
        for session in get_db_session(settings):
            try:
                hold = use_case.execute(session, hold_id=hold_id)
            except HoldNoEncontrado:
                raise HTTPException(status_code=404, detail="Hold no encontrado")
            except HoldExpirado:
                raise HTTPException(status_code=410, detail="Hold expirado")
            except HoldInvalidoError as e:
                raise HTTPException(status_code=409, detail=str(e))

        return {"id": hold.id, "status": hold.status, "message": "Hold confirmado"}

    # === DELETE /internal/holds/{hold_id} ===
    @r.delete("/internal/holds/{hold_id}", status_code=status.HTTP_204_NO_CONTENT)
    def liberar_hold_interno(
        hold_id: str = Path(...),
        x_service_token: str = Header(None, alias="X-Service-Token"),
    ):
        """
        Libera un hold temporal (cancelación/rollback).
        INTERNO: Requiere X-Service-Token header.
        """
        if x_service_token != settings.INTERNAL_SERVICE_TOKEN:
            raise HTTPException(status_code=403, detail="Token de servicio inválido")

        use_case = get_liberar_hold_use_case()
        
        for session in get_db_session(settings):
            try:
                use_case.execute(session, hold_id=hold_id)
            except HoldNoEncontrado:
                raise HTTPException(status_code=404, detail="Hold no encontrado")
            except HoldInvalidoError as e:
                raise HTTPException(status_code=409, detail=str(e))

        return

    # === GET /internal/holds/{hold_id} ===
    @r.get("/internal/holds/{hold_id}")
    def obtener_hold_interno(
        hold_id: str = Path(...),
        x_service_token: str = Header(None, alias="X-Service-Token"),
    ) -> Dict[str, Any]:
        """
        Consulta el estado de un hold temporal.
        INTERNO: Requiere X-Service-Token header.
        """
        if x_service_token != settings.INTERNAL_SERVICE_TOKEN:
            raise HTTPException(status_code=403, detail="Token de servicio inválido")

        use_case = get_obtener_hold_use_case()
        
        for session in get_db_session(settings):
            hold = use_case.execute(session, hold_id=hold_id)

        if not hold:
            raise HTTPException(status_code=404, detail="Hold no encontrado")

        # Convertir a dict y serializar datetimes
        d = asdict(hold)
        d["inicio"] = str(d["inicio"])
        d["fin"] = str(d["fin"])
        d["expira_en"] = str(d["expira_en"])

        return d

    return r
