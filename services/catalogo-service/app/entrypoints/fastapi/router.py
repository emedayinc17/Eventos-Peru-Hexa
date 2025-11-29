"""
Router de Catálogo - Hexagonal Architecture
Capa de orquestación HTTP - SIN lógica de negocio, SIN SQL
"""
from typing import List, Dict, Any, Optional
from dataclasses import asdict
from fastapi import APIRouter, Depends, HTTPException, Query
import logging
import sqlalchemy
import uuid

from ev_shared.config import Settings
from ev_shared.db import session_scope

# DTOs (Pydantic schemas)
from .schemas import (
    TipoEvento,
    Servicio,
    OpcionConPrecio,
    PaqueteConPrecioTotal,
    PaqueteDetalle,
)

# Security
from .security import require_role

# Dependencies (Use Cases Factories)
from .dependencies import (
    get_settings,
    get_db_session,
    get_list_paquetes_use_case,
    get_get_paquete_detalle_use_case,
    get_list_tipos_evento_use_case,
    get_list_servicios_por_tipo_use_case,
    get_list_opciones_servicio_use_case,
    get_create_tipo_evento_use_case,
    get_update_tipo_evento_use_case,
    get_delete_tipo_evento_use_case,
    get_create_servicio_use_case,
    get_update_servicio_use_case,
    get_delete_servicio_use_case,
    get_create_opcion_use_case,
    get_update_opcion_use_case,
    get_delete_opcion_use_case,
    get_create_paquete_use_case,
    get_update_paquete_use_case,
    get_delete_paquete_use_case,
)

# Domain Exceptions
from ...domain.exceptions import PaqueteNoEncontrado


def create_router() -> APIRouter:
    r = APIRouter(tags=["catalogo"])
    settings = get_settings()

    # === GET /v1/tipos ===
    @r.get("/v1/tipos", response_model=List[TipoEvento], openapi_extra={"security": []})
    def list_tipos(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
        session = next(get_db_session(settings))
        use_case = get_list_tipos_evento_use_case()
        tipos = use_case.execute(session, limit=limit, offset=offset)
        return [asdict(t) for t in tipos]

    # === Alias required by logica_implementacion.md: /v1/tipos-evento ===
    @r.get("/v1/tipos-evento", response_model=List[TipoEvento], openapi_extra={"security": []})
    def list_tipos_evento(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
        session = next(get_db_session(settings))
        use_case = get_list_tipos_evento_use_case()
        tipos = use_case.execute(session, limit=limit, offset=offset)
        return [asdict(t) for t in tipos]

    # === GET /v1/servicios ===
    @r.get("/v1/servicios", response_model=List[Servicio], openapi_extra={"security": []})
    def list_servicios(tipo_evento_id: Optional[str] = Query(None), limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
        session = next(get_db_session(settings))
        use_case = get_list_servicios_por_tipo_use_case()
        servicios = use_case.execute(session, tipo_evento_id=tipo_evento_id, limit=limit, offset=offset)
        # The query implementation may return either domain dataclass instances or
        # lightweight dicts that already include `categoria` and `precio_unitario`.
        out = []
        for s in servicios:
            if isinstance(s, dict):
                # Ensure numeric fields are primitive types
                item = dict(s)
                # precio_unitario may be None - convert to float or leave as None
                if item.get("precio_unitario") is not None:
                    try:
                        item["precio_unitario"] = float(item["precio_unitario"])
                    except Exception:
                        item["precio_unitario"] = None
                out.append(item)
            else:
                out.append(asdict(s))
        return out

    # === GET /v1/opciones ===
    @r.get("/v1/opciones", response_model=List[OpcionConPrecio], openapi_extra={"security": []})
    def list_opciones(servicio_id: str = Query(...), limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
        session = next(get_db_session(settings))
        use_case = get_list_opciones_servicio_use_case()
        opciones = use_case.execute(session, servicio_id=servicio_id, limit=limit, offset=offset)
        # convert Decimal to float
        out = []
        for o in opciones:
            d = asdict(o)
            d["monto"] = float(d.get("monto", 0))
            out.append(d)
        return out

    # === Alias required by logica_implementacion.md: /v1/opciones-servicio ===
    @r.get("/v1/opciones-servicio", response_model=List[OpcionConPrecio], openapi_extra={"security": []})
    def list_opciones_servicio(servicio_id: str = Query(...), fecha_evento: Optional[str] = Query(None), limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
        """Alias compatible: acepta `fecha_evento` but currently delegates to the same use case (fecha ignored by UC)."""
        session = next(get_db_session(settings))
        use_case = get_list_opciones_servicio_use_case()
        opciones = use_case.execute(session, servicio_id=servicio_id, limit=limit, offset=offset)
        out = []
        for o in opciones:
            d = asdict(o)
            d["monto"] = float(d.get("monto", 0))
            out.append(d)
        return out

    # === GET /v1/paquetes ===
    @r.get("/v1/paquetes", response_model=List[PaqueteConPrecioTotal], openapi_extra={"security": []})
    def list_paquetes(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), tipo_evento_id: Optional[str] = Query(None)):
        session = next(get_db_session(settings))
        use_case = get_list_paquetes_use_case()
        paquetes = use_case.execute(session, limit=limit, offset=offset, tipo_evento_id=tipo_evento_id)
        # The repository may return either domain dataclasses or dicts containing
        # quick-summary fields (including `servicios`). Normalize both shapes.
        result = []
        for p in paquetes:
            if isinstance(p, dict):
                item = dict(p)
                # Convert monto_total (Decimal) to monto_total_vigente float for API
                if item.get("monto_total") is not None:
                    try:
                        item["monto_total_vigente"] = float(item["monto_total"])
                    except Exception:
                        item["monto_total_vigente"] = 0.0
                else:
                    item["monto_total_vigente"] = 0.0
                # Ensure servicios is an array
                item["servicios"] = item.get("servicios", [])
                result.append(item)
            else:
                d = asdict(p)
                d["monto_total_vigente"] = float(d.get("monto_total", 0))
                d["precio_base"] = d["monto_total_vigente"]  # Frontend expects precio_base
                d["servicios"] = []
                result.append(d)
        return result

    # === GET /v1/paquetes/{id} ===
    @r.get("/v1/paquetes/{id}", response_model=PaqueteDetalle, openapi_extra={"security": []})
    def get_paquete_detalle(id: str):
        session = next(get_db_session(settings))
        use_case = get_get_paquete_detalle_use_case()
        try:
            paquete = use_case.execute(session, paquete_id=id)
        except PaqueteNoEncontrado:
            raise HTTPException(status_code=404, detail="Paquete no encontrado")

        result = asdict(paquete)
        result["monto_total"] = float(result.get("monto_total", 0))
        # Convertir items
        for item in result["items"]:
            item["precio_unit_vigente"] = float(item.get("precio_unit_vigente", 0))

        # Adapt to PaqueteDetalle schema (monto names)
        items_out = []
        for it in result["items"]:
            # Include servicio_id and servicio_nombre so frontend can map paquete items back to servicios
            items_out.append({
                "opcion_servicio_id": it.get("opcion_servicio_id"),
                "cantidad": it.get("cantidad"),
                "moneda": it.get("moneda"),
                "monto": float(it.get("precio_unit_vigente", 0)),
                "servicio_id": it.get("servicio_id"),
                "servicio_nombre": it.get("servicio_nombre"),
            })
        respuesta = {
            "id": result.get("id"),
            "codigo": result.get("codigo"),
            "nombre": result.get("nombre"),
            "descripcion": result.get("descripcion"),
            "status": result.get("status"),
            "moneda": result.get("moneda"),
            "monto_total": float(result.get("monto_total", 0)),
            "items": items_out,
        }
        return respuesta
    # === ADMIN: CRUD TipoEvento ===
    @r.post("/v1/admin/tipos", status_code=201)
    def create_tipo(payload: dict, admin=Depends(require_role("ADMIN"))):
        """Crear Tipo de Evento (admin). Expects JSON with 'nombre' and optional 'descripcion'."""
        settings = get_settings()
        with session_scope(settings) as session:
            use_case = get_create_tipo_evento_use_case()
            result = use_case.execute(session, nombre=payload.get("nombre"), descripcion=payload.get("descripcion"))
            return result

    @r.put("/v1/admin/tipos/{id}")
    def update_tipo(id: str, payload: dict, admin=Depends(require_role("ADMIN"))):
        settings = get_settings()
        with session_scope(settings) as session:
            use_case = get_update_tipo_evento_use_case()
            result = use_case.execute(session, tipo_id=id, nombre=payload.get("nombre"), descripcion=payload.get("descripcion"))
            return result

    @r.delete("/v1/admin/tipos/{id}", status_code=204)
    def delete_tipo(id: str, admin=Depends(require_role("ADMIN"))):
        settings = get_settings()
        with session_scope(settings) as session:
            use_case = get_delete_tipo_evento_use_case()
            use_case.execute(session, tipo_id=id)
            return

    # === ADMIN: Servicios ===
    @r.post("/v1/admin/servicios", status_code=201)
    def create_servicio(payload: dict, admin=Depends(require_role("ADMIN"))):
        settings = get_settings()
        with session_scope(settings) as session:
            use_case = get_create_servicio_use_case()
            return use_case.execute(session, nombre=payload.get("nombre"), tipo_evento_id=payload.get("tipo_evento_id"), descripcion=payload.get("descripcion"))

    @r.put("/v1/admin/servicios/{id}")
    def update_servicio(id: str, payload: dict, admin=Depends(require_role("ADMIN"))):
        # TEMP LOG: registrar payload recibido para depuración de `status` (usar INFO para que sea visible)
        logging.getLogger("catalogo.router").info(f"[admin.update_servicio] recibido payload for {id}: {payload}")
        settings = get_settings()
        with session_scope(settings) as session:
            use_case = get_update_servicio_use_case()
            # Accept optional `status` in payload to allow toggling availability (0/1)
            return use_case.execute(
                session,
                servicio_id=id,
                nombre=payload.get("nombre"),
                descripcion=payload.get("descripcion"),
                tipo_evento_id=payload.get("tipo_evento_id"),
                status=payload.get("status"),
            )

    @r.delete("/v1/admin/servicios/{id}", status_code=204)
    def delete_servicio(id: str, admin=Depends(require_role("ADMIN"))):
        settings = get_settings()
        with session_scope(settings) as session:
            use_case = get_delete_servicio_use_case()
            use_case.execute(session, servicio_id=id)
            return

    # === ADMIN: Opciones ===
    @r.post("/v1/admin/opciones", status_code=201)
    def create_opcion(payload: dict, admin=Depends(require_role("ADMIN"))):
        settings = get_settings()
        with session_scope(settings) as session:
            use_case = get_create_opcion_use_case()
            return use_case.execute(session, servicio_id=payload.get("servicio_id"), nombre=payload.get("nombre"), moneda=payload.get("moneda"), monto=payload.get("monto"), detalles=payload.get("detalles"))

    @r.put("/v1/admin/opciones/{id}")
    def update_opcion(id: str, payload: dict, admin=Depends(require_role("ADMIN"))):
        settings = get_settings()
        with session_scope(settings) as session:
            use_case = get_update_opcion_use_case()
            return use_case.execute(session, opcion_id=id, nombre=payload.get("nombre"), moneda=payload.get("moneda"), monto=payload.get("monto"), detalles=payload.get("detalles"))

    @r.delete("/v1/admin/opciones/{id}", status_code=204)
    def delete_opcion(id: str, admin=Depends(require_role("ADMIN"))):
        settings = get_settings()
        with session_scope(settings) as session:
            use_case = get_delete_opcion_use_case()
            use_case.execute(session, opcion_id=id)
            return

    # === ADMIN: Paquetes (create básico) ===
    @r.post("/v1/admin/paquetes", status_code=201)
    def create_paquete(payload: dict, admin=Depends(require_role("ADMIN"))):
        # Basic payload validation to prevent server-side 500s caused by malformed requests
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Payload must be a JSON object")
        items = payload.get("items", [])
        if not isinstance(items, list):
            raise HTTPException(status_code=400, detail="'items' must be an array of {opcion_servicio_id,cantidad}")
        for it in items:
            if not isinstance(it, dict) or "opcion_servicio_id" not in it:
                raise HTTPException(status_code=400, detail="Each item must include 'opcion_servicio_id'")

        # Generate code if not provided
        codigo = payload.get("codigo")
        if not codigo:
            import uuid
            codigo = f"PKG-{str(uuid.uuid4())[:8].upper()}"

        settings = get_settings()
        with session_scope(settings) as session:
            use_case = get_create_paquete_use_case()
            try:
                return use_case.execute(
                    session,
                    codigo=codigo,
                    nombre=payload.get("nombre"),
                    descripcion=payload.get("descripcion"),
                    items=items,
                    moneda=payload.get("moneda", "PEN"),
                    monto=payload.get("precio_base"),
                )
            except sqlalchemy.exc.IntegrityError as ie:
                # Duplicate code or FK-like integrity issues -> conflict
                logging.getLogger("catalogo.router").warning(f"[admin.create_paquete] integrity error: {ie}")
                raise HTTPException(status_code=409, detail="Paquete con el mismo código ya existe o datos inválidos")
            except Exception as e:
                # Unexpected error: log and return generic 500
                print(f"CRITICAL ERROR in create_paquete: {e}")
                import traceback
                traceback.print_exc()
                logging.getLogger("catalogo.router").exception(f"[admin.create_paquete] unexpected error: {e}")
                raise HTTPException(status_code=500, detail=f"Error interno al crear paquete: {str(e)}")

    @r.put("/v1/admin/paquetes/{id}")
    def update_paquete(id: str, payload: dict, admin=Depends(require_role("ADMIN"))):
        settings = get_settings()
        try:
            with session_scope(settings) as session:
                use_case = get_update_paquete_use_case()
                return use_case.execute(session, paquete_id=id, nombre=payload.get("nombre"), descripcion=payload.get("descripcion"), items=payload.get("items"), moneda=payload.get("moneda"), monto=payload.get("precio_base"))
        except Exception as e:
            import traceback
            traceback.print_exc()
            logging.getLogger("catalogo.router").exception(f"[admin.update_paquete] unexpected error: {e}")
            raise HTTPException(status_code=500, detail=f"Error interno al actualizar paquete: {str(e)}")

    @r.delete("/v1/admin/paquetes/{id}", status_code=204)
    def delete_paquete(id: str, admin=Depends(require_role("ADMIN"))):
        settings = get_settings()
        try:
            with session_scope(settings) as session:
                use_case = get_delete_paquete_use_case()
                print(f"DEBUG: Repository methods: {dir(use_case.repository)}")
                use_case.execute(session, paquete_id=id)
                return
        except Exception as e:
            import traceback
            traceback.print_exc()
            logging.getLogger("catalogo.router").exception(f"[admin.delete_paquete] unexpected error: {e}")
            raise HTTPException(status_code=500, detail=f"Error interno al eliminar paquete: {str(e)}")

    return r


def build_api_router(settings: Settings) -> APIRouter:
    """
    Wrapper para mantener compatibilidad con main.py.
    Por ahora simplemente delega a create_router(), que ya usa get_settings() internamente.
    """
    return create_router()
