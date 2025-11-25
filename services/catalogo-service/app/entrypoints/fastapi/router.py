"""
Router del Catálogo (Hexagonal Architecture)
CAPA DE ORQUESTACIÓN - SIN lógica de negocio
Responsabilidad: transformar HTTP ↔ Domain Models
"""
from dataclasses import asdict
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from ev_shared.config import Settings

from ...domain.exceptions import PaqueteNoEncontrado
from .dependencies import (
    get_db_session,
    get_list_tipos_evento_use_case,
    get_list_servicios_por_tipo_use_case,
    get_list_opciones_servicio_use_case,
    get_list_paquetes_use_case,
    get_get_paquete_detalle_use_case,
)


class Health(BaseModel):
    status: str = "ok"


def build_api_router(settings: Settings) -> APIRouter:
    """
    Construye el router de Catálogo con inyección de dependencias.
    Todos los endpoints son públicos en el MVP.
    """
    r = APIRouter(tags=["catalogo"])

    # === HEALTH CHECK ===
    @r.get(
        "/health",
        response_model=Health,
        operation_id="catalogo_health",
        openapi_extra={"security": []}
    )
    def health():
        """Health check del servicio de catálogo"""
        return {"status": "ok"}

    # === GET /v1/catalogo/tipos ===
    @r.get("/v1/catalogo/tipos", openapi_extra={"security": []})
    def list_tipos_evento(
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ) -> List[Dict[str, Any]]:
        """Lista todos los tipos de evento activos"""
        session = next(get_db_session(settings))
        use_case = get_list_tipos_evento_use_case()
        tipos = use_case.execute(session, limit=limit, offset=offset)
        return [asdict(t) for t in tipos]

    # === GET /v1/catalogo/servicios ===
    @r.get("/v1/catalogo/servicios", openapi_extra={"security": []})
    def list_servicios(
        tipo_evento_id: Optional[str] = None,
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ) -> List[Dict[str, Any]]:
        """Lista servicios, opcionalmente filtrados por tipo de evento"""
        session = next(get_db_session(settings))
        use_case = get_list_servicios_por_tipo_use_case()
        servicios = use_case.execute(
            session,
            tipo_evento_id=tipo_evento_id,
            limit=limit,
            offset=offset
        )
        return [asdict(s) for s in servicios]

    # === GET /v1/catalogo/opciones ===
    @r.get("/v1/catalogo/opciones", openapi_extra={"security": []})
    def list_opciones(
        servicio_id: str,
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ) -> List[Dict[str, Any]]:
        """Lista opciones de un servicio con precios vigentes"""
        session = next(get_db_session(settings))
        use_case = get_list_opciones_servicio_use_case()
        opciones = use_case.execute(
            session,
            servicio_id=servicio_id,
            limit=limit,
            offset=offset
        )
        # Convertir Decimal a float para JSON serialization
        result = []
        for op in opciones:
            d = asdict(op)
            d["monto"] = float(d["monto"])
            result.append(d)
        return result

    # === GET /v1/catalogo/paquetes ===
    @r.get("/v1/catalogo/paquetes", openapi_extra={"security": []})
    def list_paquetes(
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ) -> List[Dict[str, Any]]:
        """Lista paquetes con monto total calculado"""
        session = next(get_db_session(settings))
        use_case = get_list_paquetes_use_case()
        paquetes = use_case.execute(session, limit=limit, offset=offset)
        # Convertir Decimal a float
        result = []
        for p in paquetes:
            d = asdict(p)
            d["monto_total"] = float(d["monto_total"])
            result.append(d)
        return result

    # === GET /v1/catalogo/paquetes/{id} ===
    @r.get("/v1/catalogo/paquetes/{id}", openapi_extra={"security": []})
    def get_paquete_detalle(
        id: str,
    ) -> Dict[str, Any]:
        """Obtiene detalle completo de un paquete con items y proveedores"""
        session = next(get_db_session(settings))
        use_case = get_get_paquete_detalle_use_case()
        try:
            paquete = use_case.execute(session, paquete_id=id)
        except PaqueteNoEncontrado:
            raise HTTPException(status_code=404, detail="Paquete no encontrado")

        # Convertir a dict y serializar Decimals
        result = asdict(paquete)
        result["monto_total"] = float(result["monto_total"])
        
        # Convertir items
        for item in result["items"]:
            item["precio_unit_vigente"] = float(item["precio_unit_vigente"])
        
        return result

    return r
