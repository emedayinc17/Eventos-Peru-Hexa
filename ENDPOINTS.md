# ENDPOINTS (inventario rápido)

Este archivo lista los endpoints detectados en el frontend y validados por `tools/validate_frontend_endpoints.py`.

**Formato:** `SERVICIO: [METHOD] /ruta` — *Propósito / Estado (resultado de validación)*

- **IAM (base)**: `http://127.0.0.1:8010/iam`
  - [POST] `/auth/login` — Login público (OK, 200, devuelve `access_token`).
  - [POST] `/auth/register` — Registro público (cliente).
  - [GET] `/me` — Información del usuario autenticado (OK, 200).
  - [GET] `/health` — Salud (OK, 200).
  - [GET] `/admin/users` — Lista de usuarios (ADMIN).
  - [POST] `/admin/users` — Crear usuario (ADMIN).
  - [GET] `/admin/users/{id}` — Obtener usuario (ADMIN).
  - [PATCH] `/admin/users/{id}` — Actualizar usuario (ADMIN).
  - [DELETE] `/admin/users/{id}` — Eliminar usuario (ADMIN).

- **Catálogo (base)**: `http://127.0.0.1:8020/catalogo`
  - [GET] `/health` — Salud (OK, 200).
  - [GET] `/v1/catalogo/tipos` — Tipos de evento.
  - [GET] `/v1/catalogo/servicios` — Servicios del catálogo.
  - [GET] `/v1/catalogo/opciones` — Opciones de servicio.
  - [GET] `/v1/catalogo/paquetes` — Paquetes (OK, 200; contiene seed `bbbbbbb0-...`).
  - [GET] `/v1/catalogo/paquetes/{id}` — Paquete por id (OK, 200 para seed `bbbbbbb0-...`).

- **Proveedores (base)**: `http://127.0.0.1:8030/proveedores`
  - [GET] `/health` — Salud (OK, 200).
  - [GET] `/v1/proveedores/disponibles?servicio_id={id}&fecha={YYYY-MM-DD}&limit=&offset=` — Buscar proveedores disponibles.
    - Nota: la llamada desde el validador sin `servicio_id` devolvió 422 (campo requerido). Frontend usa `PROVEEDORES.buscarDisponibles(servicio_id, fecha, ...)` y debe siempre enviar `servicio_id` para evitar 422.

- **Contratación (base)**: `http://127.0.0.1:8040/contratacion`
  - [GET] `/health` — Salud (OK, 200).
  - [POST] `/v1/contratacion/pedidos` — Crear pedido (cliente).
  - [GET] `/v1/contratacion/pedidos/mios` — Mis pedidos (requiere auth). *Nota: la ruta consultada por el frontend resultó en 404 - posible duplicación de prefijo `/v1/contratacion` en `services.js`.*
  - [GET] `/v1/contratacion/pedidos/{id}` — Detalle pedido.
  - [POST] `/v1/contratacion/pedidos/{id}/enviar-resumen` — Enviar resumen por correo.
  - Admin: rutas bajo `/v1/contratacion/admin/...` para gestión de pedidos.

**Problemas detectados / recomendaciones rápidas**

- `proveedores.disponibles` requiere `servicio_id`. Asegurarse que el flujo que llama a `PROVEEDORES.buscarDisponibles` pase siempre `servicio_id` (por ejemplo, extraer `servicio_id` desde el paquete o la opción seleccionada antes de consultar disponibilidad).

- `contratacion` tiene rutas con prefijo duplicado: en `services.js` las funciones usan `/v1/contratacion/...` y el `CONTRATACION_BASE` ya incluye `/contratacion`, resultando en `.../contratacion/v1/contratacion/...` (producto: 404). Recomiendo eliminar el prefijo duplicado en `services.js` (usar `/v1/...` en las funciones) o ajustar el `CONTRATACION_BASE` para no incluir `/contratacion`.

- Normalizar respuesta de listado: algunos endpoints devuelven arrays (p. ej. `/v1/catalogo/paquetes`) y otros devuelven `{ items: [...] }`. En el frontend usar una normalización defensiva: `const list = Array.isArray(x) ? x : (x?.items || []);`.

- CORS: ya ajusté `CORS_ORIGINS` en `libs/shared/ev_shared/config.py` — recuerda reiniciar los servicios para aplicar cambios.

---

Si quieres, aplico automáticamente las correcciones en `services.js` para arreglar el prefijo duplicado de `contratacion` y actualizo las llamadas a `buscarDisponibles` para validar `servicio_id` antes de la petición.
