Lógica de implementación – Plataforma Eventos Perú

(IAM, Catálogo, Proveedores, Contratación – Arquitectura Hexagonal)

0. Contexto y objetivo

El sistema está compuesto por 4 microservicios backend:

iam-service

catalogo-service

proveedores-service

contratacion-service

Todos usan arquitectura hexagonal:

domain/ → modelos y puertos (interfaces)

application/use_cases/ → casos de uso puros

infrastructure/ → adaptadores (DB, HTTP, etc.)

entrypoints/fastapi/ → router, schemas, security, dependencies

Objetivo funcional

Flujo deseado (corregido):

El cliente elige un tipo_evento.

Puede:

A) Elegir un paquete predefinido para ese tipo de evento

B) Armar un paquete personalizado:

Elige servicios disponibles para ese tipo de evento.

Para cada servicio, ve opciones de servicio (opción + precio vigente).

Para cada opción/servicio, ve proveedores que lo ofrecen y sus ratings.

Finalmente genera un pedido/reserva:

Caso A: basado en un paquete predefinido.

Caso B: basado en la selección de opciones (y más adelante, proveedores).

Los roles:

CLIENTE

Ve catálogo (tipos evento, servicios, paquetes)

Crea pedidos propios (desde paquete o custom)

Lista y consulta sus pedidos

ADMIN

Todo lo anterior

Puede listar pedidos de todos

Cambiar estado de pedidos

Asignar proveedores y confirmar reservas (vía holds en Proveedores)

Meta: extender funcionalidad sin romper:

JWT y autenticación

contratos ya usados por el frontend

casos de uso existentes que ya funcionan

1. Cosas que NO se deben romper
1.1. Infra compartida (ev_shared)

No modificar:

ev_shared.config.Settings / load_settings

ev_shared.security (helpers de JWT)

ev_shared.db.session_scope y helpers de sesión

Los servicios asumen que Settings ya tiene:

cadenas de conexión

JWT_SECRET, JWT_ALGORITHM, etc.

1.2. Paths base de los servicios

Mantener:

IAM: router montado bajo /iam

Catálogo: /catalogo

Proveedores: /proveedores

Contratación: /contratacion

En Kubernetes, el Ingress reescribe:

https://eventos.emeday.inc/iam/...

https://eventos.emeday.inc/catalogo/...

https://eventos.emeday.inc/proveedores/...

https://eventos.emeday.inc/contratacion/...

No cambiar estos prefijos ni el rewrite-target esperado (/$2 en Ingress).

1.3. Seguridad en servicios

iam-service:

Mantener estructura actual de payload JWT:

sub → id del usuario

username/email → correo

role → ADMIN / CLIENTE

contratacion-service:

Archivo entrypoints/fastapi/security.py:

Mantener get_current_user y require_role.

Mantener uso del esquema HTTPBearer para que Swagger muestre Authorize.

proveedores-service:

Mantener HTTPBearer y lógica de decodificación actual para endpoints internos /internal/... (holds).

2. Modelo de datos – visión de dominio

No cambiar estructura de tablas salvo que sea estrictamente necesario.

Relaciones clave (simplificadas):

2.1. Catálogo (ev_catalogo, ev_paquetes)

tipo_evento

servicio (tipo_evento_id → tipo_evento.id)

opcion_servicio (servicio_id → servicio.id)

precio_servicio (historial de precios por opción, con vigencias)

paquete

item_paquete (paquete_id, opcion_servicio_id)

paquete_item_proveedor (proveedor sugerido por item)

precio_paquete + vistas:

v_paquete_detalle

v_paquete_item_full

v_paquete_precio_vigente_total

v_opcion_con_precio_vigente → opción + precio vigente

2.2. Proveedores (ev_proveedores)

proveedor (básico + rating_prom)

habilidad_proveedor (qué servicio ofrece cada proveedor)

calendario_proveedor (bloqueos / agenda)

reserva_temporal (holds)

Vista v_servicio_proveedor_habilidad:

servicio, tipo_evento, proveedor, rating, nivel

2.3. Contratación (ev_contratacion)

pedido_evento (cabecera del pedido)

item_pedido_evento:

opcion_servicio_id, nombre_servicio, cantidad, precio_unitario, subtotal

tipo_item, referencia_id (se puede usar como enlace flexible)

reserva:

item_pedido_id, proveedor_id, inicio, fin, status, hold_id

Vistas:

v_pedido_con_cliente

v_reserva_detalle (join de pedido + items + reserva + proveedor + paquete)

Conclusión:
El modelo actual soporta:

Pedidos a partir de paquetes.

Pedidos custom por opción de servicio.

Asignación de proveedores vía reserva (admin o automatizable).

Consultas completas de detalle por vistas.

3. IAM Service – Lógica y endpoints
3.1. Estado actual

services/iam-service/app/entrypoints/fastapi/router.py

Endpoints (mantener):

GET /iam/health

POST /iam/auth/login

POST /iam/auth/register

GET /iam/me

GET /iam/admin/users

GET /iam/admin/users/{id}

POST /iam/admin/users

PATCH /iam/admin/users/{id}

DELETE /iam/admin/users/{id}

Casos de uso ya implementados:

AuthLoginUseCase

RegisterUserUseCase

GetProfileUseCase

AdminListUsersUseCase

AdminGetUserUseCase

AdminCreateUserUseCase

AdminPatchUserUseCase

AdminDeleteUserUseCase

3.2. Indicaciones para el Agente IA

No agregar lógica de negocio en el router.
Si se requieren ajustes, hacerlos en application/use_cases/ o adaptadores infrastructure/.

No cambiar estructura de JWT.

Cualquier cambio de claims rompería contratacion-service y proveedores-service.

Único posible cambio (opcional):

Añadir campos de perfil adicionales en GET /me si más adelante el frontend los requiere, siempre pasando por el caso de uso y modelos de dominio.

4. Catálogo Service – Lógica y cambios necesarios
4.1. Estado actual

services/catalogo-service/app/entrypoints/fastapi/router.py

Hoy expone:

GET /catalogo/health

GET /catalogo/v1/paquetes

Filtra opcionalmente por tipo_evento_id

GET /catalogo/v1/paquetes/{id}

Casos de uso ya creados (pero no todos expuestos):

ListTiposEventoUseCase

ListServiciosPorTipoUseCase

ListOpcionesServicioUseCase

ListPaquetesUseCase

GetPaqueteDetalleUseCase

Adaptador DB:

infrastructure/db/repositories.py → MySQLCatalogoQueryService
Ya implementa métodos para todos los casos de uso.

4.2. Cambios requeridos (router)

Objetivo: exponer todos los casos de uso y cubrir:

Tipos de evento disponibles.

Servicios por tipo de evento.

Opciones de servicio con precio vigente.

Paquetes filtrables por tipo de evento.

4.2.1. Nuevo endpoint: listar tipos de evento

Agregar en build_api_router:

    @r.get(
        "/v1/tipos-evento",
        summary="Listar tipos de evento",
        operation_id="catalogo_list_tipos_evento",
        openapi_extra={"security": []},
    )
    def list_tipos_evento(
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        settings: Settings = Depends(get_settings),
    ):
        uc = get_list_tipos_evento_use_case()
        with get_catalogo_db_session(settings) as session:
            tipos = uc.execute(session, limit=limit, offset=offset)

        return [asdict(t) for t in tipos]


Usar get_list_tipos_evento_use_case desde dependencies.py.

Usar asdict para convertir dataclasses a dict.

4.2.2. Nuevo endpoint: listar servicios por tipo
    @r.get(
        "/v1/servicios",
        summary="Listar servicios por tipo de evento",
        operation_id="catalogo_list_servicios_por_tipo",
        openapi_extra={"security": []},
    )
    def list_servicios(
        tipo_evento_id: str,
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        settings: Settings = Depends(get_settings),
    ):
        uc = get_list_servicios_por_tipo_use_case()
        with get_catalogo_db_session(settings) as session:
            servicios = uc.execute(
                session,
                tipo_evento_id=tipo_evento_id,
                limit=limit,
                offset=offset,
            )
        return [asdict(s) for s in servicios]

4.2.3. Nuevo endpoint: opciones de servicio + precio vigente
    @r.get(
        "/v1/opciones-servicio",
        summary="Listar opciones de servicio con precio vigente",
        operation_id="catalogo_list_opciones_servicio",
        openapi_extra={"security": []},
    )
    def list_opciones_servicio(
        servicio_id: str,
        fecha_evento: Optional[str] = Query(None),
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        settings: Settings = Depends(get_settings),
    ):
        uc = get_list_opciones_servicio_use_case()

        with get_catalogo_db_session(settings) as session:
            opciones = uc.execute(
                session,
                servicio_id=servicio_id,
                fecha_evento=fecha_evento,
                limit=limit,
                offset=offset,
            )

        result = []
        for o in opciones:
            d = asdict(o)
            # campos Decimal → float
            if "precio_vigente" in d and d["precio_vigente"] is not None:
                d["precio_vigente"] = float(d["precio_vigente"])
            result.append(d)

        return result


Nota:
El campo fecha_evento se puede usar para validar la vigencia de los precios (delegado al use case / repositorio).

4.2.4. Mantener endpoints actuales de paquetes

No modificar la firma de:

GET /catalogo/v1/paquetes

GET /catalogo/v1/paquetes/{id}

Solo, si es necesario, ajustar conversión Decimal → float como ya se hace en el código actual.

5. Proveedores Service – Lógica y ajustes
5.1. Estado actual

services/proveedores-service/app/entrypoints/fastapi/router.py

Endpoints:

Públicos:

GET /proveedores/health

GET /proveedores/v1/proveedores/disponibles

Parámetros:

servicio_id (obligatorio)

fecha (YYYY-MM-DD)

limit, offset

Internos (protegidos, usan JWT):

POST /proveedores/internal/holds

DELETE /proveedores/internal/holds/{hold_id}

PATCH /proveedores/internal/holds/{hold_id}/confirm

GET /proveedores/internal/holds/{hold_id}

El endpoint de búsqueda usa SQL directo (no hex completo aquí, pero está ya así).

5.2. Cambios requeridos

Mantener contrato de GET /v1/proveedores/disponibles.
El frontend y Contratación lo usarán para sugerir proveedores:

No cambiar nombre ni parámetros.

Asegurarse de filtrar por:

p.is_deleted = 0

p.status = 1

Opcional – mejorar respuesta
Estandarizar salida con campos:

{
  "items": [
    {
      "id": "...",
      "nombre": "...",
      "email": "...",
      "telefono": "...",
      "rating_prom": 4.5,
      "status": 1
    }
  ],
  "limit": 50,
  "offset": 0,
  "total": 5
}


Esto implica envolver el list[dict] actual en un objeto, pero solo hacerlo si todavía no hay frontend dependiendo del formato plano.

No modificar lógica de holds internos

Contratación los usa mediante un adaptador que implementa ProveedoresHoldPort.

Mantener firma JSON de entrada/salida.

6. Contratación Service – Lógica y cambios necesarios
6.1. Estado actual

Use cases principales (ya creados):

crear_pedido_desde_paquete.py

crear_pedido_custom.py

listar_pedidos_cliente.py

listar_pedidos_admin.py

obtener_pedido_detalle.py

admin_cambiar_estado.py

admin_asignar_proveedor.py

Router actual (entrypoints/fastapi/router.py) expone:

GET /contratacion/health

POST /contratacion/pedidos

Body dinámico (Dict[str, Any]):

Si trae paquete_id → usa CrearPedidoDesdePaqueteUseCase

Si trae items → usa CrearPedidoCustomUseCase

GET /contratacion/pedidos/mios

GET /contratacion/pedidos/{pedido_id}

POST /contratacion/v1/contratacion/pedidos/{pedido_id}/enviar-resumen

Admin:

GET /contratacion/admin/pedidos

PATCH /contratacion/admin/pedidos/{pedido_id}

GET /contratacion/admin/pedidos/{pedido_id}

POST /contratacion/admin/pedidos/{pedido_id}/items

DELETE /contratacion/admin/pedidos/{pedido_id}/items

POST /contratacion/admin/pedidos/{pedido_id}/asignar-proveedor

6.2. Reglas de negocio que hay que respetar

Estados de pedido:
Mantener la máquina de estados ya implementada (0 = DRAFT, etc.).
No permitir transiciones inválidas (se maneja con TransicionEstadoInvalida).

Integridad de precios:

Siempre que se cree un pedido (desde paquete o custom), el caso de uso debe consultar el catálogo para:

Validar existencia de opciones/paquete

Traer precios vigentes

Calcular subtotal de cada item y monto_total

Reglas de rol:

Endpoints de cliente → get_current_user sin require_role.

Endpoints de admin → Depends(require_role("ADMIN")).

Resiliencia vs Proveedores:

El uso de ProveedoresHoldPort y reservas confirmadas está concentrado en admin_asignar_proveedor.

No mover lógica de reserva confirmada al router; mantener en casos de uso.

6.3. Cambios para soportar flujo funcional nuevo
6.3.1. Crear pedido desde paquete (Camino A)

Ya existe y no hay que romperlo.

Acciones para el Agente IA:

Revisar CrearPedidoDesdePaqueteUseCase:

Validar que:

Usa CatalogoQueryPort para:

validar paquete

traer v_paquete_item_full o similar

Crea pedido_evento y item_pedido_evento correctos

Calcula monto_total a partir de los items

Ajustar sólo si hay bugs evidentes (p. ej., no usa num_personas si es requerido por la BD, etc.), siempre:

Sin cambiar la firma del endpoint /contratacion/pedidos para este caso (debe seguir aceptando {"paquete_id": "...", ...}).

6.3.2. Crear pedido custom (Camino B – sin proveedores aún)

Lo que hay ahora:

Schema:

class ItemCustom(BaseModel):
    opcion_servicio_id: str
    cantidad: int = Field(ge=1, default=1)

class CrearPedidoCustom(BaseModel):
    tipo_evento_id: str
    items: List[ItemCustom]
    fecha_evento: date
    hora_inicio: time
    hora_fin: Optional[time] = None
    num_personas: int = Field(ge=1, default=1)
    ubicacion: str
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None


Use case CrearPedidoCustomUseCase:

Valida opciones de servicio con CatalogoQueryPort.

Crea pedido_evento y item_pedido_evento con PedidoRepository y ItemPedidoRepository.

Calcula precios.

Esto ya implementa “custom por opción de servicio” sin proveedor.

6.3.3. Extensión futura: cliente elige proveedor

Para no romper nada, esta parte se debe diseñar como extensión compatible:

Extender schema (compatible hacia atrás)

En ItemCustom:

class ItemCustom(BaseModel):
    opcion_servicio_id: str
    cantidad: int = Field(ge=1, default=1)
    proveedor_id: Optional[str] = None  # NUEVO, opcional


El frontend actual seguirá funcionando (no envía proveedor_id).

Nuevas versiones podrán enviar proveedor sugerido.

Mantener contrato de /contratacion/pedidos

Seguir recibiendo Dict[str, Any] y detectando:

if "paquete_id" in body: ...

elif "items" in body: ... (custom)

En la rama custom:

Parsear a CrearPedidoCustom como se hace ahora.

Los proveedor_id (si vienen) se usarán en una siguiente fase (por ejemplo, para sugerir a admin).

No crear reservas automáticas en esta fase

Para no tocar demasiado:

Dejar que la confirmación de proveedor + creación de reserva siga en:

AdminAsignarProveedorUseCase + endpoint /admin/pedidos/{pedido_id}/asignar-proveedor

El “cliente elige proveedor” se puede modelar inicialmente a nivel de UI y como metadatos en otra tabla en el futuro.
(Agregar columnas nuevas sí implicaría migración de BD ↔ fuera de alcance inmediato.)

Resumen:
En esta iteración, el backend soporta custom por opción de servicio; la selección de proveedor sigue siendo responsabilidad del admin / back-office usando los endpoints admin ya existentes.

7. Resumen por servicio para el Agente IA
7.1. IAM Service

Mantener todos los endpoints y casos de uso.

No modificar JWT ni esquema de seguridad.

Cambios sólo cosméticos/documentación.

7.2. Catálogo Service

Agregar endpoints en router:

GET /catalogo/v1/tipos-evento

GET /catalogo/v1/servicios?tipo_evento_id=...

GET /catalogo/v1/opciones-servicio?servicio_id=...&fecha_evento=...

Reusar casos de uso y adaptadores ya existentes.

Convertir dataclasses a dict usando asdict y castear Decimal → float donde aplique.

Mantener endpoints existentes de paquetes sin cambios de contrato.

7.3. Proveedores Service

Mantener endpoints:

GET /proveedores/health

GET /proveedores/v1/proveedores/disponibles

/proveedores/internal/holds... (POST, PATCH, DELETE, GET)

Opcional: normalizar respuesta de /disponibles con {items, limit, offset, total}, siempre que no rompa el frontend actual.

No tocar la lógica de holds ni la validación JWT de endpoints internos.

7.4. Contratación Service

Mantener endpoint único:

POST /contratacion/pedidos (oneOf: paquete o custom)

Revisar y corregir, si hace falta, los use cases:

CrearPedidoDesdePaqueteUseCase

CrearPedidoCustomUseCase

ListarPedidosClienteUseCase

ListarPedidosAdminUseCase

ObtenerPedidoDetalleUseCase

AdminCambiarEstadoUseCase

AdminAsignarProveedorUseCase

Extender ItemCustom para aceptar opcionalmente proveedor_id (sin usarlo aún para reservas automáticas).

Mantener endpoints admin de gestión de pedidos y reservas (no romper sus schemas).

8. Recomendación de orden de trabajo para la IA

Catálogo:

Implementar y probar nuevos endpoints de tipos-evento, servicios y opciones-servicio.

Probar con Swagger en https://eventos.emeday.inc/catalogo/docs.

Proveedores:

Revisar /v1/proveedores/disponibles y asegurarse que filtra correctamente por disponibilidad y estado.

Confirmar que los endpoints /internal/holds siguen funcionando con Contratación.

Contratación:

Verificar que POST /contratacion/pedidos funciona para:

crear desde paquete

crear custom

Validar que GET /contratacion/pedidos/mios y GET /contratacion/pedidos/{id} devuelven vistas consolidadas.

Confirmar flujo admin de asignación de proveedor y cambio de estado.

Seguridad / roles:

Asegurarse de que:

Endpoints de cliente usan sólo get_current_user.

Endpoints admin usan Depends(require_role("ADMIN")).