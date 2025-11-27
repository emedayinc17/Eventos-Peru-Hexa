"""
Router de Catálogo - Hexagonal Architecture
Capa de orquestación HTTP - SIN lógica de negocio, SIN SQL
"""
from typing import List, Dict, Any, Optional
from dataclasses import asdict
from fastapi import APIRouter, Depends, HTTPException, Query

from ev_shared.config import Settings

# DTOs (Pydantic schemas)
# from .schemas import ...

# Dependencies (Use Cases Factories)
from .dependencies import (
    get_settings,
    get_db_session,
    get_list_paquetes_use_case,
    get_get_paquete_detalle_use_case,
)

# Domain Exceptions
from ...domain.exceptions import PaqueteNoEncontrado


def create_router() -> APIRouter:
    r = APIRouter(tags=["catalogo"])
    settings = get_settings()

    # === GET /v1/paquetes ===
    @r.get("/v1/paquetes", openapi_extra={"security": []})
    def list_paquetes(
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        tipo_evento_id: Optional[str] = Query(None),
    ) -> List[Dict[str, Any]]:
        """Lista paquetes con monto total calculado"""
        session = next(get_db_session(settings))
        use_case = get_list_paquetes_use_case()
        paquetes = use_case.execute(session, limit=limit, offset=offset, tipo_evento_id=tipo_evento_id)
        # Convertir Decimal a float
        result = []
        for p in paquetes:
            d = asdict(p)
            d["monto_total"] = float(d["monto_total"])
            result.append(d)
        return result

    # === GET /v1/paquetes/{id} ===
    @r.get("/v1/paquetes/{id}", openapi_extra={"security": []})
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

def build_api_router(settings: Settings) -> APIRouter:
    """
    Wrapper para mantener compatibilidad con main.py.
    Por ahora simplemente delega a create_router(), que ya usa get_settings() internamente.
    """
    return create_router()
