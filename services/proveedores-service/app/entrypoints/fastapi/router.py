from fastapi import APIRouter, Depends, Security, HTTPException, status, Body, Query, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from jose import jwt, JWTError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from ev_shared.config import Settings
from ev_shared.db import session_scope

# 👉 HTTP Bearer para endpoints protegidos (muestra Authorize en Swagger)
bearer_scheme = HTTPBearer(auto_error=True)

# === MIDDLEWARE DE VALIDACIÓN INTERNA ===
def validate_internal_request(
    x_service_token: str = Header(None, alias="X-Service-Token"),
    settings: Settings = Depends(lambda: Settings()),
):
    """
    Valida requests internas de otros servicios.
    Usa API Key compartida (env: INTERNAL_SERVICE_TOKEN).
    """
    if x_service_token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=403, detail="Token de servicio inválido")
    return True

def validate_token(
    creds: HTTPAuthorizationCredentials = Security(bearer_scheme),
    settings: Settings = Depends(lambda: Settings()),
):
    token = creds.credentials
    algorithm = getattr(settings, "JWT_ALG", getattr(settings, "JWT_ALGORITHM", "HS256"))
    secret = getattr(settings, "JWT_SECRET", None)
    if not secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT_SECRET no configurado")
    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        if "sub" not in payload or "role" not in payload:
            raise HTTPException(status_code=401, detail="Token inválido (claims)")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")


# ------- Schemas -------
class Health(BaseModel):
    status: str = "ok"

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
    status: int = 0  # 0=hold


def _parse_fecha(f: str) -> datetime.date:
    """
    Acepta YYYY-MM-DD, DD/MM/YYYY y DD-MM-YYYY. Si no, 400.
    """
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(f, fmt).date()
        except ValueError:
            continue
    raise HTTPException(status_code=400, detail="Fecha inválida. Usa YYYY-MM-DD, DD/MM/YYYY o DD-MM-YYYY.")


def build_api_router(settings: Settings) -> APIRouter:
    r = APIRouter(tags=["proveedores"])

    # HEALTH (público)
    @r.get("/health", response_model=Health, operation_id="proveedores_health", openapi_extra={"security": []})
    def health():
        return {"status": "ok"}

    # GET /v1/proveedores/disponibles?servicio_id=...&fecha=... (público)
    # Consulta proveedores disponibles (renombrado para claridad semántica)
    # Intenta chequear reservas confirmadas (ev_contratacion.reserva).
    # Si MySQL devuelve 1142 (permiso denegado), cae a un fallback sin ese chequeo.
    @r.get("/v1/proveedores/disponibles", openapi_extra={"security": []})
    def buscar_disponibles(
        servicio_id: str,
        fecha: str,
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
    ):
        iso_date = _parse_fecha(fecha)
        start = f"{iso_date} 00:00:00"
        end   = f"{iso_date} 23:59:59"

        # Consulta "completa" (con ev_contratacion.reserva)
        sql_full = text("""
            SELECT
              p.id, p.nombre, p.email, p.telefono, p.rating_prom, p.status
            FROM ev_proveedores.proveedor p
            JOIN ev_proveedores.habilidad_proveedor h
              ON h.proveedor_id = p.id AND h.servicio_id = :sid
            WHERE p.is_deleted = 0 AND p.status = 1
              AND NOT EXISTS (  -- holds activos/confirmados que chocan
                SELECT 1
                FROM ev_proveedores.reserva_temporal rt
                WHERE rt.proveedor_id = p.id
                  AND rt.status IN (0,1)
                  AND rt.expira_en > NOW()
                  AND rt.inicio < :end_dt AND rt.fin > :start_dt
              )
              AND NOT EXISTS (  -- reservas confirmadas en contratación
                SELECT 1
                FROM ev_contratacion.reserva r
                WHERE r.proveedor_id = p.id
                  AND r.status = 1
                  AND r.inicio < :end_dt AND r.fin > :start_dt
              )
              AND NOT EXISTS (  -- descansos
                SELECT 1
                FROM ev_proveedores.calendario_proveedor c
                WHERE c.proveedor_id = p.id
                  AND c.tipo = 2
                  AND c.inicio < :end_dt AND c.fin > :start_dt
              )
            ORDER BY p.rating_prom DESC, p.nombre ASC
            LIMIT :lim OFFSET :off
        """)

        # Fallback (sin ev_contratacion.reserva) si 1142
        sql_fallback = text("""
            SELECT
              p.id, p.nombre, p.email, p.telefono, p.rating_prom, p.status
            FROM ev_proveedores.proveedor p
            JOIN ev_proveedores.habilidad_proveedor h
              ON h.proveedor_id = p.id AND h.servicio_id = :sid
            WHERE p.is_deleted = 0 AND p.status = 1
              AND NOT EXISTS (  -- holds activos/confirmados que chocan
                SELECT 1
                FROM ev_proveedores.reserva_temporal rt
                WHERE rt.proveedor_id = p.id
                  AND rt.status IN (0,1)
                  AND rt.expira_en > NOW()
                  AND rt.inicio < :end_dt AND rt.fin > :start_dt
              )
              AND NOT EXISTS (  -- descansos
                SELECT 1
                FROM ev_proveedores.calendario_proveedor c
                WHERE c.proveedor_id = p.id
                  AND c.tipo = 2
                  AND c.inicio < :end_dt AND c.fin > :start_dt
              )
            ORDER BY p.rating_prom DESC, p.nombre ASC
            LIMIT :lim OFFSET :off
        """)

        params = {"sid": servicio_id, "start_dt": start, "end_dt": end, "lim": limit, "off": offset}

        with session_scope(settings) as s:
            try:
                rows = s.execute(sql_full, params).mappings().all()
            except SQLAlchemyError as e:
                # Detecta permiso denegado a ev_contratacion.reserva (1142)
                orig = getattr(e, "orig", None)
                if orig and getattr(orig, "args", None) and len(orig.args) >= 1:
                    errcode = orig.args[0]
                    if errcode == 1142:
                        # Reintenta sin chequear ev_contratacion.reserva
                        rows = s.execute(sql_fallback, params).mappings().all()
                    else:
                        raise
                else:
                    raise

        return [dict(r) for r in rows]

    # POST /internal/holds (INTERNO - solo service-to-service)
    @r.post("/internal/holds", status_code=status.HTTP_201_CREATED, response_model=HoldOut)
    def crear_hold_interno(
        body: CrearHoldIn = Body(...),
        _valid=Depends(validate_internal_request),
    ):
        if body.inicio >= body.fin:
            raise HTTPException(status_code=400, detail="Rango de tiempo inválido (fin > inicio)")

        with session_scope(settings) as s:
            # IDEMPOTENCIA: si ya existe hold con mismo correlation_id + proveedor, retornar existente
            existing = s.execute(
                text("""
                    SELECT id, proveedor_id, opcion_servicio_id, inicio, fin, expira_en, status
                    FROM ev_proveedores.reserva_temporal
                    WHERE proveedor_id = :pid
                      AND correlation_id = :corr
                      AND status IN (0, 1)
                    ORDER BY created_at DESC
                    LIMIT 1
                """),
                {"pid": body.proveedor_id, "corr": body.correlation_id},
            ).mappings().first()

            if existing:
                return HoldOut(
                    id=existing["id"],
                    proveedor_id=existing["proveedor_id"],
                    opcion_servicio_id=existing["opcion_servicio_id"],
                    inicio=str(existing["inicio"]),
                    fin=str(existing["fin"]),
                    expira_en=str(existing["expira_en"]),
                    status=existing["status"],
                )

            # Continuar con validaciones de conflictos
            # Conflictos con holds
            conflict_hold = s.execute(
                text("""
                    SELECT id FROM ev_proveedores.reserva_temporal
                    WHERE proveedor_id = :pid
                      AND status IN (0,1)
                      AND expira_en > NOW()
                      AND inicio < :fin AND fin > :ini
                    LIMIT 1
                """),
                {"pid": body.proveedor_id, "ini": body.inicio, "fin": body.fin},
            ).first()
            if conflict_hold:
                raise HTTPException(status_code=409, detail="Proveedor no disponible (hold activo)")

            # Conflictos con reservas confirmadas (si hay permisos; si no, no romper)
            try:
                conflict_res = s.execute(
                    text("""
                        SELECT id FROM ev_contratacion.reserva
                        WHERE proveedor_id = :pid
                          AND status = 1
                          AND inicio < :fin AND fin > :ini
                        LIMIT 1
                    """),
                    {"pid": body.proveedor_id, "ini": body.inicio, "fin": body.fin},
                ).first()
                if conflict_res:
                    raise HTTPException(status_code=409, detail="Proveedor no disponible (reserva confirmada)")
            except SQLAlchemyError as e:
                orig = getattr(e, "orig", None)
                if not (orig and getattr(orig, "args", None) and len(orig.args) >= 1 and orig.args[0] == 1142):
                    # Si NO es 1142, relanzar el error
                    raise
                # Si es 1142, lo ignoramos para no romper el flujo (quedará menos estricto)

            # Descanso
            conflict_desc = s.execute(
                text("""
                    SELECT id FROM ev_proveedores.calendario_proveedor
                    WHERE proveedor_id = :pid
                      AND tipo = 2
                      AND inicio < :fin AND fin > :ini
                    LIMIT 1
                """),
                {"pid": body.proveedor_id, "ini": body.inicio, "fin": body.fin},
            ).first()
            if conflict_desc:
                raise HTTPException(status_code=409, detail="Proveedor en descanso")

            # Crear hold
            s.execute(
                text("""
                    INSERT INTO ev_proveedores.reserva_temporal
                      (id, proveedor_id, opcion_servicio_id, inicio, fin, status, expira_en, correlation_id, created_by)
                    VALUES
                      (UUID(), :pid, :oid, :ini, :fin, 0, DATE_ADD(NOW(), INTERVAL :ttl MINUTE), :corr, :creator)
                """),
                {
                    "pid": body.proveedor_id,
                    "oid": body.opcion_servicio_id,
                    "ini": body.inicio,
                    "fin": body.fin,
                    "ttl": body.ttl_min,
                    "corr": body.correlation_id,
                    "creator": body.created_by or "contratacion-service",
                },
            )

            row = s.execute(
                text("""
                    SELECT id, proveedor_id, opcion_servicio_id, inicio, fin, expira_en, status
                    FROM ev_proveedores.reserva_temporal
                    WHERE proveedor_id = :pid
                      AND correlation_id = :corr
                    ORDER BY created_at DESC
                    LIMIT 1
                """),
                {"pid": body.proveedor_id, "corr": body.correlation_id},
            ).mappings().first()

        return HoldOut(
            id=row["id"],
            proveedor_id=row["proveedor_id"],
            opcion_servicio_id=row["opcion_servicio_id"],
            inicio=str(row["inicio"]),
            fin=str(row["fin"]),
            expira_en=str(row["expira_en"]),
            status=row["status"],
        )

    # DELETE /internal/holds/{id} (INTERNO)
    @r.delete("/internal/holds/{hold_id}", status_code=status.HTTP_204_NO_CONTENT)
    def liberar_hold_interno(
        hold_id: str = Path(...),
        _valid=Depends(validate_internal_request),
    ):
        """Liberar hold temporal (cancelación o compensación)"""
        with session_scope(settings) as s:
            hold = s.execute(
                text("""SELECT id, status FROM ev_proveedores.reserva_temporal WHERE id = :hid LIMIT 1"""),
                {"hid": hold_id},
            ).mappings().first()

            if not hold:
                raise HTTPException(status_code=404, detail="Hold no encontrado")

            # Idempotencia: si ya está liberado (status=3), no hacer nada
            if hold["status"] == 3:
                return

            if hold["status"] not in (0, 1):
                raise HTTPException(status_code=409, detail="Hold no puede ser liberado (estado inválido)")

            s.execute(
                text("UPDATE ev_proveedores.reserva_temporal SET status = 3 WHERE id = :hid"),
                {"hid": hold_id},
            )
        return

    # PATCH /internal/holds/{hold_id}/confirm (INTERNO)
    @r.patch("/internal/holds/{hold_id}/confirm", status_code=status.HTTP_200_OK)
    def confirmar_hold_interno(
        hold_id: str = Path(...),
        _valid=Depends(validate_internal_request),
    ):
        """Confirmar hold temporal (marca como confirmado antes de crear reserva definitiva)"""
        with session_scope(settings) as s:
            hold = s.execute(
                text("SELECT id, status, expira_en FROM ev_proveedores.reserva_temporal WHERE id = :hid LIMIT 1"),
                {"hid": hold_id},
            ).mappings().first()

            if not hold:
                raise HTTPException(status_code=404, detail="Hold no encontrado")
            
            if hold["status"] != 0:
                raise HTTPException(status_code=409, detail="Hold no está en estado activo (status=0)")

            from datetime import datetime
            if hold["expira_en"] < datetime.now():
                raise HTTPException(status_code=410, detail="Hold expirado")

            s.execute(
                text("UPDATE ev_proveedores.reserva_temporal SET status = 1 WHERE id = :hid AND status = 0"),
                {"hid": hold_id},
            )

        return {"id": hold_id, "status": 1, "message": "Hold confirmado"}

    # GET /internal/holds/{hold_id} (INTERNO)
    @r.get("/internal/holds/{hold_id}")
    def obtener_hold_interno(
        hold_id: str = Path(...),
        _valid=Depends(validate_internal_request),
    ):
        """Consultar estado de un hold (verificación antes de confirmar)"""
        with session_scope(settings) as s:
            hold = s.execute(
                text("""
                    SELECT id, proveedor_id, opcion_servicio_id, inicio, fin, status, expira_en, created_at, correlation_id
                    FROM ev_proveedores.reserva_temporal
                    WHERE id = :hid
                    LIMIT 1
                """),
                {"hid": hold_id},
            ).mappings().first()

            if not hold:
                raise HTTPException(status_code=404, detail="Hold no encontrado")

        return dict(hold)

    return r
