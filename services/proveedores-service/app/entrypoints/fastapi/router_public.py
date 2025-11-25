"""
Router Público de Proveedores (Hexagonal Architecture)
Endpoints públicos - sin autenticación
CAPA DE ORQUESTACIÓN - SIN lógica de negocio
"""
from dataclasses import asdict
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Any, Dict, List
from datetime import datetime

from ev_shared.config import Settings

from .dependencies import (
    get_db_session,
    get_buscar_disponibles_use_case,
)


class Health(BaseModel):
    status: str = "ok"


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


def build_public_router(settings: Settings) -> APIRouter:
    """
    Construye el router público de Proveedores.
    Todos los endpoints son de solo lectura (queries).
    """
    r = APIRouter(tags=["proveedores-public"])

    # === HEALTH CHECK ===
    @r.get(
        "/health",
        response_model=Health,
        operation_id="proveedores_health",
        openapi_extra={"security": []}
    )
    def health():
        """Health check del servicio de proveedores"""
        return {"status": "ok"}

    # === GET /v1/proveedores/disponibles ===
    @r.get("/v1/proveedores/disponibles", openapi_extra={"security": []})
    def buscar_disponibles(
        servicio_id: str,
        fecha: str,
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
    ) -> List[Dict[str, Any]]:
        """
        Busca proveedores disponibles para un servicio en una fecha.
        Consulta pública (sin autenticación).
        """
        iso_date = _parse_fecha(fecha)
        use_case = get_buscar_disponibles_use_case()
        
        for session in get_db_session(settings):
            proveedores = use_case.execute(
                session,
                servicio_id=servicio_id,
                fecha=iso_date,
                limit=limit,
                offset=offset
            )

        # Convertir Decimal a float para JSON serialization
        result = []
        for prov in proveedores:
            d = asdict(prov)
            d["rating_prom"] = float(d["rating_prom"])
            result.append(d)
        
        return result

    return r
