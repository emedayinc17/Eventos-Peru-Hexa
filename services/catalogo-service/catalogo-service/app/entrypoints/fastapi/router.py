# router.py — Catalogo Service (MVP: endpoints públicos)
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from typing import Any, Dict, List, Optional

from ev_shared.config import Settings
from ev_shared.db import session_scope


class Health(BaseModel):
    status: str = "ok"


def build_api_router(settings: Settings) -> APIRouter:
    # Todos los endpoints del catálogo son públicos en el MVP
    r = APIRouter(tags=["catalogo"])

    # HEALTH (público)
    @r.get("/health", response_model=Health, operation_id="catalogo_health", openapi_extra={"security": []})
    def health():
        return {"status": "ok"}

    # GET /v1/catalogo/tipos  (público)
    @r.get("/v1/catalogo/tipos", openapi_extra={"security": []})
    def tipos(
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ) -> List[Dict[str, Any]]:
        with session_scope(settings) as s:
            rows = s.execute(
                text("""
                    SELECT id, nombre, descripcion, status
                    FROM ev_catalogo.tipo_evento
                    WHERE is_deleted = 0 AND status = 1
                    ORDER BY created_at DESC
                    LIMIT :lim OFFSET :off
                """),
                {"lim": limit, "off": offset},
            ).mappings().all()
        return [dict(r) for r in rows]

    # GET /v1/catalogo/servicios  (público)
    @r.get("/v1/catalogo/servicios", openapi_extra={"security": []})
    def servicios(
        tipo_evento_id: Optional[str] = None,
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ) -> List[Dict[str, Any]]:
        sql = """
            SELECT id, nombre, descripcion, tipo_evento_id, status
            FROM ev_catalogo.servicio
            WHERE is_deleted = 0 AND status = 1
        """
        params: Dict[str, Any] = {}
        if tipo_evento_id:
            sql += " AND tipo_evento_id = :teid"
            params["teid"] = tipo_evento_id
        sql += " ORDER BY created_at DESC LIMIT :lim OFFSET :off"
        params.update({"lim": limit, "off": offset})

        with session_scope(settings) as s:
            rows = s.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]

    # GET /v1/catalogo/opciones  (público) — precios vigentes por vista
    @r.get("/v1/catalogo/opciones", openapi_extra={"security": []})
    def opciones(
        servicio_id: str,
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ) -> List[Dict[str, Any]]:
        with session_scope(settings) as s:
            rows = s.execute(
                text("""
                    SELECT o.id,
                           o.servicio_id,
                           o.nombre,
                           o.detalles,
                           v.moneda,
                           v.monto
                    FROM ev_catalogo.opcion_servicio o
                    JOIN ev_catalogo.v_opcion_con_precio_vigente v
                      ON v.opcion_id = o.id
                    WHERE o.is_deleted = 0
                      AND o.status = 1
                      AND o.servicio_id = :sid
                    ORDER BY o.created_at DESC
                    LIMIT :lim OFFSET :off
                """),
                {"sid": servicio_id, "lim": limit, "off": offset},
            ).mappings().all()
        return [dict(r) for r in rows]

    # GET /v1/catalogo/paquetes  (público)
    # 🔁 Robusto: calculamos el total vigente agregando sobre v_paquete_detalle
    @r.get("/v1/catalogo/paquetes", openapi_extra={"security": []})
    def paquetes(
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ) -> List[Dict[str, Any]]:
        with session_scope(settings) as s:
            rows = s.execute(
                text("""
                    SELECT
                      d.paquete_id      AS id,
                      MIN(d.codigo)     AS codigo,
                      MIN(d.nombre)     AS nombre,
                      MIN(d.descripcion) AS descripcion,
                      MIN(d.status)     AS status,
                      MIN(d.moneda)     AS moneda,
                      SUM(d.cantidad * d.monto) AS monto_total
                    FROM ev_paquetes.v_paquete_detalle d
                    GROUP BY d.paquete_id
                    ORDER BY codigo ASC
                    LIMIT :lim OFFSET :off
                """),
                {"lim": limit, "off": offset},
            ).mappings().all()
        return [dict(r) for r in rows]

    # GET /v1/catalogo/paquetes/{id}  (público)
    # 🔁 Robusto: cabecera agregada + ítems desde v_paquete_detalle
    @r.get("/v1/catalogo/paquetes/{id}", openapi_extra={"security": []})
    def paquete_detalle(id: str) -> Dict[str, Any]:
        with session_scope(settings) as s:
            head = s.execute(
                text("""
                    SELECT
                      d.paquete_id      AS id,
                      MIN(d.codigo)     AS codigo,
                      MIN(d.nombre)     AS nombre,
                      MIN(d.descripcion) AS descripcion,
                      MIN(d.status)     AS status,
                      MIN(d.moneda)     AS moneda,
                      SUM(d.cantidad * d.monto) AS monto_total
                    FROM ev_paquetes.v_paquete_detalle d
                    WHERE d.paquete_id = :pid
                    GROUP BY d.paquete_id
                    LIMIT 1
                """),
                {"pid": id},
            ).mappings().first()
            if not head:
                raise HTTPException(status_code=404, detail="Paquete no encontrado")

            items = s.execute(
                text("""
                    SELECT
                      d.opcion_servicio_id,
                      d.cantidad,
                      d.moneda,
                      d.monto AS precio_unit_vigente
                    FROM ev_paquetes.v_paquete_detalle d
                    WHERE d.paquete_id = :pid
                """),
                {"pid": id},
            ).mappings().all()

        return {
            **dict(head),
            "items": [dict(i) for i in items],
        }

    return r
