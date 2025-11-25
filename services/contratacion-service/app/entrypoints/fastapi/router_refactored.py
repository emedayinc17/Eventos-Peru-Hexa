"""
Router de Contratación - Hexagonal Architecture REFACTORIZADO
Capa de orquestación HTTP - SIN lógica de negocio, SIN SQL
"""
from typing import Dict, Any
from dataclasses import asdict
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends

from ev_shared.config import Settings

# DTOs (Pydantic schemas)
from .schemas import (
    Health,
    CrearPedidoDesdePaquete,
    CrearPedidoCustom,
    PedidoEventoOut,
    EnviarResumenRequest,
    EnviarResumenResponse,
    AdminPatchEstadoRequest,
    AdminAddItemsRequest,
    AdminDeleteItemsRequest,
    AdminAsignarProveedorRequest,
    AdminListaPedidosResponse,
)

# Seguridad
from .security import get_current_user, require_role

# Dependencies (Use Cases Factories)
from .dependencies import (
    get_settings,
    get_db_session,
    get_crear_pedido_desde_paquete_use_case,
    get_crear_pedido_custom_use_case,
    get_listar_pedidos_cliente_use_case,
    get_listar_pedidos_admin_use_case,
    get_obtener_pedido_detalle_use_case,
    get_admin_cambiar_estado_use_case,
    get_admin_asignar_proveedor_use_case,
)

# Domain Exceptions
from ...domain.exceptions import (
    PedidoNoEncontrado,
    ItemPedidoNoEncontrado,
    TransicionEstadoInvalida,
    PaqueteNoEncontrado,
    OpcionServicioNoEncontrada,
    ErrorCotizacion,
    ErrorAsignacionProveedor,
    ErrorServicioExterno,
)

router = APIRouter(tags=["contratacion"])


# ============================================================================
# UTILIDADES
# ============================================================================

def _serialize_decimal(obj: Any) -> Any:
    """Convierte Decimal a float recursivamente para JSON serialization"""
    from decimal import Decimal
    
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: _serialize_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_decimal(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj


# ============================================================================
# ENDPOINTS PÚBLICOS
# ============================================================================

@router.get(
    "/health",
    response_model=Health,
    operation_id="contratacion_health",
    openapi_extra={"security": []},
)
def health():
    """Health check sin tocar BD"""
    return {"status": "ok"}


# ============================================================================
# ENDPOINTS CLIENTE (Autenticados)
# ============================================================================

@router.post(
    "/v1/contratacion/pedidos",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    operation_id="contratacion_crear_pedido",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def crear_pedido(
    body: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """
    Crear pedido - Hexagonal pattern
    - OneOf: paquete_id (desde paquete) o items (custom)
    - Llama a CatalogoClient para validar precios
    - Estado inicial: DRAFT (0)
    """
    cliente_id = current_user["sub"]
    
    # Determinar use case según tipo de body
    if "paquete_id" in body:
        # Crear desde paquete
        try:
            payload = CrearPedidoDesdePaquete(**body)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "VALIDACION_ERROR", "message": str(e)}
            )
        
        use_case = get_crear_pedido_desde_paquete_use_case()
        params = {
            "cliente_id": cliente_id,
            "paquete_id": payload.paquete_id,
            "tipo_evento_id": payload.tipo_evento_id,
            "num_personas": payload.num_personas,
            "fecha": payload.fecha,
            "observaciones": payload.observaciones,
        }
    else:
        # Crear custom
        try:
            payload = CrearPedidoCustom(**body)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "VALIDACION_ERROR", "message": str(e)}
            )
        
        use_case = get_crear_pedido_custom_use_case()
        params = {
            "cliente_id": cliente_id,
            "items": [item.dict() for item in payload.items],
            "tipo_evento_id": payload.tipo_evento_id,
            "num_personas": payload.num_personas,
            "fecha": payload.fecha,
            "observaciones": payload.observaciones,
        }
    
    try:
        for session in get_db_session(settings):
            pedido = use_case.execute(session, **params)
            
            # Serializar a dict
            pedido_dict = asdict(pedido)
            return _serialize_decimal(pedido_dict)
            
    except PaqueteNoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PAQUETE_NO_ENCONTRADO"}
        )
    except OpcionServicioNoEncontrada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "OPCION_SERVICIO_NO_ENCONTRADA"}
        )
    except ErrorCotizacion as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ERROR_COTIZACION", "message": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ERROR_INTERNO", "message": str(e)}
        )


@router.get(
    "/v1/contratacion/pedidos/mios",
    response_model=Dict[str, Any],
    operation_id="contratacion_listar_mis_pedidos",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def mis_pedidos(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """Listar pedidos del cliente actual - Hexagonal pattern"""
    cliente_id = current_user["sub"]
    use_case = get_listar_pedidos_cliente_use_case()
    
    try:
        for session in get_db_session(settings):
            pedidos = use_case.execute(session, cliente_id, limit, offset)
            
            # Serializar lista
            pedidos_list = [_serialize_decimal(asdict(p)) for p in pedidos]
            return {"items": pedidos_list}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ERROR_INTERNO", "message": str(e)}
        )


@router.get(
    "/v1/contratacion/pedidos/{pedido_id}",
    response_model=Dict[str, Any],
    operation_id="contratacion_detalle_pedido",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def detalle_pedido(
    pedido_id: str,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """
    Detalle del pedido con items y reservas - Hexagonal pattern
    Retorna: {pedido, items[], reservas[], estado_nombre, total_items, total_reservas}
    """
    cliente_id = current_user["sub"]
    use_case = get_obtener_pedido_detalle_use_case()
    
    try:
        for session in get_db_session(settings):
            detalle = use_case.execute(session, pedido_id)
            
            # Verificar ownership
            if detalle["pedido"]["cliente_id"] != cliente_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"code": "ACCESO_DENEGADO"}
                )
            
            return _serialize_decimal(detalle)
            
    except PedidoNoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PEDIDO_NO_ENCONTRADO"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ERROR_INTERNO", "message": str(e)}
        )


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
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """
    TODO: Enviar resumen por email - DEFERRED (Mensajería feature)
    Esta funcionalidad requiere integración con ev_mensajeria
    Por ahora retorna 202 Accepted sin acción
    """
    return {
        "message": f"Resumen pendiente de envío a {body.to_email}",
        "pedido_id": pedido_id,
    }


# ============================================================================
# ENDPOINTS ADMIN (Autenticados + Role)
# ============================================================================

@router.get(
    "/v1/contratacion/admin/pedidos",
    response_model=AdminListaPedidosResponse,
    operation_id="contratacion_admin_listar_pedidos",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_listar_pedidos(
    estado: int | None = None,
    limit: int = 100,
    offset: int = 0,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
):
    """
    Lista TODOS los pedidos del sistema - SOLO ADMIN
    Hexagonal pattern con filtro opcional por estado
    """
    use_case = get_listar_pedidos_admin_use_case()
    
    try:
        for session in get_db_session(settings):
            pedidos = use_case.execute(session, estado, limit, offset)
            
            # Serializar lista
            pedidos_list = [_serialize_decimal(asdict(p)) for p in pedidos]
            return {
                "items": pedidos_list,
                "total": len(pedidos_list),
                "limit": limit,
                "offset": offset,
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ERROR_INTERNO", "message": str(e)}
        )


@router.patch(
    "/v1/contratacion/admin/pedidos/{pedido_id}",
    response_model=Dict[str, Any],
    operation_id="contratacion_admin_patch_estado",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_patch_estado(
    pedido_id: str,
    body: AdminPatchEstadoRequest,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
):
    """
    Cambiar estado del pedido - SOLO ADMIN
    Hexagonal pattern con validación de transiciones
    Estado 5 (CANCELADO) libera todos los holds automáticamente
    """
    use_case = get_admin_cambiar_estado_use_case()
    
    try:
        for session in get_db_session(settings):
            pedido = use_case.execute(session, pedido_id, body.nuevo_estado)
            
            # Serializar
            pedido_dict = asdict(pedido)
            return _serialize_decimal(pedido_dict)
            
    except PedidoNoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PEDIDO_NO_ENCONTRADO"}
        )
    except TransicionEstadoInvalida as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "TRANSICION_INVALIDA", "message": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ERROR_INTERNO", "message": str(e)}
        )


@router.post(
    "/v1/contratacion/admin/pedidos/{pedido_id}/items",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    operation_id="contratacion_admin_add_items",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_add_items(
    pedido_id: str,
    body: AdminAddItemsRequest,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
):
    """
    TODO: Agregar items a pedido - DEFERRED (Additional feature)
    Solo permitido en estados DRAFT (0) o COTIZADO (1)
    Por ahora retorna 201 sin acción
    """
    return {
        "message": "Funcionalidad pendiente de implementación",
        "pedido_id": pedido_id,
    }


@router.delete(
    "/v1/contratacion/admin/pedidos/{pedido_id}/items",
    response_model=Dict[str, Any],
    operation_id="contratacion_admin_delete_items",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_delete_items(
    pedido_id: str,
    body: AdminDeleteItemsRequest,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
):
    """
    TODO: Eliminar items de pedido - DEFERRED (Additional feature)
    Solo permitido en estados DRAFT (0) o COTIZADO (1)
    Por ahora retorna 200 sin acción
    """
    return {
        "message": "Funcionalidad pendiente de implementación",
        "pedido_id": pedido_id,
    }


@router.post(
    "/v1/contratacion/admin/pedidos/{pedido_id}/asignar-proveedor",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    operation_id="contratacion_admin_asignar_proveedor",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_asignar_proveedor(
    pedido_id: str,
    body: AdminAsignarProveedorRequest,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
):
    """
    Asignar proveedor a item de pedido - SOLO ADMIN
    Hexagonal pattern - ORCHESTRATOR CRÍTICO
    
    Workflow:
    1. Valida pedido en estado APROBADO (2)
    2. Valida item existe y no tiene reserva
    3. Si hold_id → confirma hold existente
       Si no hold_id → crea hold + confirma
    4. Crea reserva permanente
    5. Si todos los items tienen reserva → actualiza pedido a ASIGNADO (3)
    
    Integra con Proveedores Service vía HTTP internal
    """
    use_case = get_admin_asignar_proveedor_use_case()
    
    try:
        for session in get_db_session(settings):
            result = use_case.execute(
                session,
                pedido_id=pedido_id,
                item_pedido_id=body.item_pedido_id,
                proveedor_id=body.proveedor_id,
                opcion_servicio_id=body.opcion_servicio_id,
                fecha_inicio=body.fecha_inicio,
                fecha_fin=body.fecha_fin,
                monto=body.monto,
                hold_id=body.hold_id,
            )
            
            return _serialize_decimal(result)
            
    except PedidoNoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PEDIDO_NO_ENCONTRADO"}
        )
    except ItemPedidoNoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ITEM_PEDIDO_NO_ENCONTRADO"}
        )
    except ErrorAsignacionProveedor as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ERROR_ASIGNACION", "message": str(e)}
        )
    except ErrorServicioExterno as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "ERROR_SERVICIO_EXTERNO", "message": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ERROR_INTERNO", "message": str(e)}
        )


@router.get(
    "/v1/contratacion/admin/pedidos/{pedido_id}",
    response_model=Dict[str, Any],
    operation_id="contratacion_admin_detalle_pedido",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_detalle_pedido(
    pedido_id: str,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
):
    """
    Detalle del pedido para ADMIN - Hexagonal pattern
    Mismo use case que detalle_pedido pero sin validación de ownership
    """
    use_case = get_obtener_pedido_detalle_use_case()
    
    try:
        for session in get_db_session(settings):
            detalle = use_case.execute(session, pedido_id)
            return _serialize_decimal(detalle)
            
    except PedidoNoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PEDIDO_NO_ENCONTRADO"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ERROR_INTERNO", "message": str(e)}
        )


# ============================================================================
# EXPORT FUNCTION (Compatibility con main.py)
# ============================================================================

def build_api_router(settings: Settings | None = None) -> APIRouter:
    """
    Factory function para compatibilidad con main.py
    Retorna el router configurado
    """
    return router
