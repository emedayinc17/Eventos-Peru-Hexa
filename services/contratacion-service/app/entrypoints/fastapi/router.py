"""
Router de Contratación - Hexagonal Architecture REFACTORIZADO
Capa de orquestación HTTP - SIN lógica de negocio, SIN SQL
"""
from typing import Dict, Any
from dataclasses import asdict
from datetime import datetime
import os
from fastapi import APIRouter, HTTPException, status, Depends, Header

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
    get_pedido_repository,
    get_item_pedido_repository,
    get_reserva_repository,
    get_catalogo_client,
    get_crear_pedido_desde_paquete_use_case,
    get_crear_pedido_custom_use_case,
    get_listar_pedidos_cliente_use_case,
    get_listar_pedidos_admin_use_case,
    get_obtener_pedido_detalle_use_case,
    get_admin_cambiar_estado_use_case,
    get_admin_asignar_proveedor_use_case,
    get_admin_add_items_use_case,
    get_admin_delete_items_use_case,
    get_admin_metrics_use_case,

    get_client_metrics_use_case,
)

# Use Cases (for Type Hinting)
from ...application.use_cases import (
    CrearPedidoDesdePaqueteUseCase,
    CrearPedidoCustomUseCase,
    ListarPedidosClienteUseCase,
    ListarPedidosAdminUseCase,
    ObtenerPedidoDetalleUseCase,
    AdminCambiarEstadoPedidoUseCase,
    AdminAsignarProveedorUseCase,
)
from ...application.use_cases.admin_metrics import AdminMetricsUseCase
from ...application.use_cases.client_metrics import ClientMetricsUseCase
from ...application.use_cases.admin_add_items import AdminAddItemsUseCase
from ...application.use_cases.admin_delete_items import AdminDeleteItemsUseCase

# Infrastructure Types for Injection
from ...infrastructure.db.repositories import (
    MySQLPedidoRepository,
    MySQLItemPedidoRepository,
    MySQLReservaRepository,
)
from ...infrastructure.http.catalogo_client import CatalogoClient

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
    "/pedidos",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    operation_id="contratacion_crear_pedido",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def crear_pedido(
    body: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
    # Inject dependencies for manual factory call
    pedido_repo: MySQLPedidoRepository = Depends(get_pedido_repository),
    item_repo: MySQLItemPedidoRepository = Depends(get_item_pedido_repository),
    reserva_repo: MySQLReservaRepository = Depends(get_reserva_repository),
    catalogo_client: CatalogoClient = Depends(get_catalogo_client),
):
    """
    Crear pedido - Hexagonal pattern
    - OneOf: paquete_id (desde paquete) o items (custom)
    - Llama a CatalogoClient para validar precios
    - Estado inicial: DRAFT (0)
    """
    cliente_id = current_user["id"]
    
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
        
        use_case = get_crear_pedido_desde_paquete_use_case(
            pedido_repo=pedido_repo,
            item_repo=item_repo,
            reserva_repo=reserva_repo,
            catalogo_client=catalogo_client
        )
        
        # Convertir date + time strings a datetime y strings
        from datetime import datetime
        fecha_dt = datetime.combine(payload.fecha_evento, datetime.min.time())
        
        # Convertir proveedores_seleccionados a dict si existe
        proveedores = None
        if payload.proveedores_seleccionados:
            proveedores = [p.dict() for p in payload.proveedores_seleccionados]
        
        # Convertir servicios_adicionales a dict si existe
        servicios_adicionales = None
        if payload.servicios_adicionales:
            servicios_adicionales = [s.dict() for s in payload.servicios_adicionales]
        
        params = {
            "cliente_id": cliente_id,
            "paquete_id": payload.paquete_id,
            "tipo_evento_id": payload.tipo_evento_id,
            "num_personas": payload.num_personas,
            "fecha_evento": fecha_dt,
            "hora_inicio": payload.hora_inicio,
            "hora_fin": payload.hora_fin,
            "ubicacion": payload.ubicacion,
            "notas": payload.notas,
            "servicios_adicionales": servicios_adicionales,
            "proveedores_seleccionados": proveedores,
            # Note: use case doesn't accept request_id/correlation_id
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
        
        use_case = get_crear_pedido_custom_use_case(
            pedido_repo=pedido_repo,
            item_repo=item_repo,
            catalogo_client=catalogo_client
        )
        params = {
            "cliente_id": cliente_id,
            "items": [item.dict() for item in payload.items],
            "tipo_evento_id": payload.tipo_evento_id,
            "num_personas": payload.num_personas,
            "fecha_evento": payload.fecha_evento,
            "hora_inicio": payload.hora_inicio,
            "hora_fin": payload.hora_fin,
            "ubicacion": payload.ubicacion,
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
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ERROR_INTERNO", "message": str(e)}
        )


@router.get(
    "/pedidos/mios",
    response_model=Dict[str, Any],
    operation_id="contratacion_listar_mis_pedidos",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def mis_pedidos(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
    use_case: ListarPedidosClienteUseCase = Depends(get_listar_pedidos_cliente_use_case),
):
    """Listar pedidos del cliente actual - Hexagonal pattern"""
    cliente_id = current_user["id"]
    
    try:
        for session in get_db_session(settings):
            pedidos = use_case.execute(
                session,
                cliente_id=cliente_id,
                limit=limit,
                offset=offset
            )
            
            # Serializar lista
            pedidos_list = [_serialize_decimal(asdict(p)) for p in pedidos]
            return {"items": pedidos_list}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ERROR_INTERNO", "message": str(e)}
        )


@router.get(
    "/pedidos/{pedido_id}",
    response_model=Dict[str, Any],
    operation_id="contratacion_detalle_pedido",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def detalle_pedido(
    pedido_id: str,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
    use_case: ObtenerPedidoDetalleUseCase = Depends(get_obtener_pedido_detalle_use_case),
):
    """
    Detalle del pedido con items y reservas - Hexagonal pattern
    Retorna: {pedido, items[], reservas[], estado_nombre, total_items, total_reservas}
    """
    cliente_id = current_user["id"]
    
    try:
        for session in get_db_session(settings):
            detalle = use_case.execute(session, pedido_id=pedido_id)
            
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
    "/admin/pedidos",
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
    authorization: str | None = Header(None),
    use_case: ListarPedidosAdminUseCase = Depends(get_listar_pedidos_admin_use_case),
):
    """
    Lista TODOS los pedidos del sistema - SOLO ADMIN
    Hexagonal pattern con filtro opcional por estado
    """
    
    # Extract token for enrichment
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    
    try:
        for session in get_db_session(settings):
            pedidos = use_case.execute(
                session,
                status=estado,
                limit=limit,
                offset=offset,
                auth_token=token
            )

            # Serializar lista con tolerancia a filas problemáticas
            pedidos_list = []
            errors = []

            # Controlar comportamiento mediante variables de entorno (solo para debugging local)
            debug_mode = os.environ.get('CONTRATACION_DEBUG', '0') == '1'
            skip_bad_rows = os.environ.get('CONTRATACION_DEBUG_SKIP_BAD_ROWS', '1') == '1'

            for p in pedidos:
                try:
                    pedidos_list.append(_serialize_decimal(asdict(p)))
                except Exception as item_exc:
                    # Capturamos información mínima para debugging
                    import traceback
                    tb = traceback.format_exc()
                    err = {
                        "pedido_id": getattr(p, 'id', None),
                        "error": str(item_exc)
                    }
                    if debug_mode:
                        # En modo debug incluimos traza completa (only local use!)
                        err["trace"] = tb
                    errors.append(err)
                    if not skip_bad_rows:
                        # Mantener comportamiento original: propagar la excepción
                        raise

            response = {
                "items": pedidos_list,
                "total": len(pedidos_list),
                "limit": limit,
                "offset": offset,
            }
            if errors:
                # Añadimos una sección debug con información limitada
                response["_debug_errors_skipped"] = errors

            return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ERROR_INTERNO", "message": str(e)}
        )


@router.get(
    "/admin/metrics",
    response_model=Dict[str, Any],
    operation_id="contratacion_admin_metrics",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_metrics(
    from_date: str | None = None,
    to_date: str | None = None,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
    use_case: object = Depends(get_admin_metrics_use_case),
):
    """Return simple aggregated metrics for admin dashboards."""
    try:
        for session in get_db_session(settings):
            result = use_case.execute(session, from_date=from_date, to_date=to_date)
            return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"code": "ERROR_INTERNO", "message": str(e)})


@router.get(
    "/metrics",
    response_model=Dict[str, Any],
    operation_id="contratacion_client_metrics",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def client_metrics(
    from_date: str | None = None,
    to_date: str | None = None,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
    use_case: object = Depends(get_client_metrics_use_case),
):
    """Return client-scoped metrics (counts of own orders)."""
    cliente_id = current_user.get("id") or current_user.get("sub")
    try:
        for session in get_db_session(settings):
            result = use_case.execute(session, cliente_id, from_date=from_date, to_date=to_date)
            return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"code": "ERROR_INTERNO", "message": str(e)})


@router.patch(
    "/admin/pedidos/{pedido_id}",
    response_model=Dict[str, Any],
    operation_id="admin_contratacion_cambiar_estado",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_patch_estado(
    pedido_id: str,
    body: AdminPatchEstadoRequest,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
    use_case: AdminCambiarEstadoPedidoUseCase = Depends(get_admin_cambiar_estado_use_case),
):
    """
    Cambiar estado del pedido - SOLO ADMIN
    Hexagonal pattern con validación de transiciones
    Estado 5 (CANCELADO) libera todos los holds automáticamente
    """
    
    try:
        for session in get_db_session(settings):
            pedido = use_case.execute(session, pedido_id=pedido_id, nuevo_estado=body.estado)
            
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
    "/admin/pedidos/{pedido_id}/items",
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
    use_case: AdminAddItemsUseCase = Depends(get_admin_add_items_use_case),
):
    """
    Agregar items a pedido - SOLO ADMIN
    Solo permitido en estados DRAFT (0) o COTIZADO (1)
    Recalcula monto_total del pedido
    """
    
    try:
        for session in get_db_session(settings):
            result = use_case.execute(
                session,
                pedido_id=pedido_id,
                items=[item.dict() for item in body.items]
            )
            return _serialize_decimal(result)
            
    except PedidoNoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PEDIDO_NO_ENCONTRADO"}
        )
    except OpcionServicioNoEncontrada as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "OPCION_SERVICIO_NO_ENCONTRADA", "message": str(e)}
        )
    except ErrorAsignacionProveedor as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ERROR_VALIDACION", "message": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ERROR_INTERNO", "message": str(e)}
        )


@router.delete(
    "/admin/pedidos/{pedido_id}/items",
    response_model=Dict[str, Any],
    operation_id="contratacion_admin_delete_items",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_delete_items(
    pedido_id: str,
    body: AdminDeleteItemsRequest,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
    use_case: AdminDeleteItemsUseCase = Depends(get_admin_delete_items_use_case),
):
    """
    Eliminar items de pedido - SOLO ADMIN
    Solo permitido en estados DRAFT (0) o COTIZADO (1)
    No se puede eliminar items con reserva confirmada
    Recalcula monto_total del pedido
    """
    
    try:
        for session in get_db_session(settings):
            result = use_case.execute(
                session,
                pedido_id=pedido_id,
                item_ids=body.item_ids
            )
            return _serialize_decimal(result)
            
    except PedidoNoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PEDIDO_NO_ENCONTRADO"}
        )
    except ItemPedidoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ITEM_NO_ENCONTRADO", "message": str(e)}
        )
    except ErrorAsignacionProveedor as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ERROR_VALIDACION", "message": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ERROR_INTERNO", "message": str(e)}
        )


@router.post(
    "/admin/pedidos/{pedido_id}/asignar-proveedor",
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
    use_case: AdminAsignarProveedorUseCase = Depends(get_admin_asignar_proveedor_use_case),
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
    
    try:
        for session in get_db_session(settings):
            reserva = use_case.execute(
                session,
                pedido_id=pedido_id,
                item_pedido_id=body.item_pedido_id,
                proveedor_id=body.proveedor_id,
                inicio=body.fecha_inicio,
                fin=body.fecha_fin,
                hold_id=body.hold_id,
                notas=getattr(body, 'notas', None),
            )
            
            # Convertir objeto Reserva a dict
            result = {
                "reserva_id": reserva.id,
                "pedido_id": reserva.pedido_id,
                "item_pedido_id": reserva.item_pedido_id,
                "proveedor_id": reserva.proveedor_id,
                "opcion_servicio_id": reserva.opcion_servicio_id,
                "inicio": reserva.inicio.isoformat() if hasattr(reserva.inicio, 'isoformat') else str(reserva.inicio),
                "fin": reserva.fin.isoformat() if hasattr(reserva.fin, 'isoformat') else str(reserva.fin),
                "status": reserva.status,
                "monto": float(reserva.monto),
                "hold_id": reserva.hold_id,
                "notas": reserva.notas
            }
            
            return result
            
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
    "/admin/pedidos/{pedido_id}",
    response_model=Dict[str, Any],
    operation_id="contratacion_admin_detalle_pedido",
    openapi_extra={"security": [{"HTTPBearer": []}]},
)
def admin_detalle_pedido(
    pedido_id: str,
    settings: Settings = Depends(get_settings),
    admin=Depends(require_role("admin")),
    authorization: str | None = Header(None),
    use_case: ObtenerPedidoDetalleUseCase = Depends(get_obtener_pedido_detalle_use_case),
):
    """
    Detalle del pedido para ADMIN - Hexagonal pattern
    Mismo use case que detalle_pedido pero sin validación de ownership
    """
    
    # Extract token
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    
    try:
        for session in get_db_session(settings):
            detalle = use_case.execute(session, pedido_id=pedido_id, auth_token=token)
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
