# ENDPOINTS_VALIDATED

Este documento consolida los contratos OpenAPI detectados en los servicios y valida (resumen) los payloads esperados frente al esquema SQL aplicado (`db/bosstrap_remaste.sql`). Incluye notas de incompatibilidades y recomendaciones.

---

## Resumen rápido

- Servicios con contratos OpenAPI localizados:
  - `catalogo-service` — `services/catalogo-service/app/entrypoints/fastapi/contracts/openapi.yaml`
  - `proveedores-service` — `services/proveedores-service/app/entrypoints/fastapi/contracts/openapi.yaml`
  - `contratacion-service` — `services/contratacion-service/app/entrypoints/fastapi/contracts/openapi.yaml`

Los contratos contienen los esquemas de request/response; abajo se documentan las estructuras importantes extraídas y las notas de validación con el modelo de datos actual.

---

## Catalogo Service (base `/v1/catalogo`)

- POST `/admin/tipos`
  - Body (application/json):
    {
      "nombre": string (required),
      "descripcion": string,
      "status": integer (0|1)
    }

- POST `/admin/servicios`
  - Body:
    {
      "nombre": string (required),
      "tipo_evento_id": uuid (required),
      "descripcion": string,
      "status": integer (0|1)
    }

- POST `/admin/opciones` (opcion_servicio)
  - Body:
    {
      "servicio_id": uuid (required),
      "nombre": string (required),
      "detalles": object (opcional),
      "status": integer (0|1)
    }

- POST `/admin/paquetes` (crear paquete con items)
  - Body: `CrearPaqueteRequest`
    {
      "codigo": string (required),
      "nombre": string (required),
      "descripcion": string,
      "items": [ { "opcion_servicio_id": uuid, "cantidad": integer } ] (required)
    }

- GET `/opciones?servicio_id={uuid}` — query param `servicio_id` (uuid, required)
- GET `/paquetes` and `/paquetes/{id}` — listado y detalle

Notas DB:
- Tablas principales: `ev_catalogo.servicio`, `ev_catalogo.opcion_servicio`, `ev_paquetes.paquete`, `ev_paquetes.item_paquete`, `ev_paquetes.precio_paquete`.
- Campos esperados (ids uuid, nombres, monto/vigente para precios) coinciden con los contratos.

---

## Proveedores Service (base `/v1/proveedores`)

- POST `/admin` (crear proveedor)
  - Body:
    {
      "nombre": string (required),
      "email": string,
      "telefono": string,
      "rating_prom": number (0..5),
      "status": integer (0|1)
    }

- POST `/admin/{id}/skills` (agregar skill)
  - Body:
    { "servicio_id": uuid (required), "nivel": integer (1..5) }

- GET `/` (buscar proveedores disponibles)
  - Query: `servicio_id` (uuid, required), `fecha` (date, required)
  - Response item: { "proveedor_id": uuid, "nombre": string, "slots_disponibles": [ { inicio: date-time, fin: date-time } ] }

- POST `/reservas` (crear reserva temporal)
  - Body:
    {
      "proveedor_id": uuid (required),
      "opcion_servicio_id": uuid (required),
      "inicio": date-time (required),
      "fin": date-time (required),
      "correlation_id": string (opcional)
    }

Notas DB:
- Tablas: `ev_proveedores.proveedor`, `ev_proveedores.habilidad_proveedor`, `ev_proveedores.reserva_temporal`.
- `reserva_temporal` contiene `expira_en`, `status` y `proveedor_id` — el contrato está alineado.

Importante: muchas llamadas públicas requieren `servicio_id` — si falta, el servicio devuelve 422. El frontend debe validar y enviar siempre ese parámetro.

---

## Contratacion Service (base `/v1/contratacion`)

- POST `/pedidos` (crear pedido)
  - Body: oneOf `CrearPedidoDesdePaquete` o `CrearPedidoCustom`.
    - CrearPedidoDesdePaquete:
      {
        "paquete_id": uuid (required),
        "fecha_evento": date (required),
        "hora_inicio": time (required),
        "hora_fin": time (nullable),
        "ubicacion": string (required),
        "request_id": string (opcional)
      }
    - CrearPedidoCustom:
      {
        "tipo_evento_id": uuid (required),
        "items": [ { "opcion_servicio_id": uuid, "cantidad": int } ] (required),
        "fecha_evento": date, "hora_inicio": time, "ubicacion": string, "request_id": string
      }

- GET `/pedidos/mios` — lista pedidos del usuario autenticado
- GET `/pedidos/{id}` — detalle pedido
- POST `/pedidos/{id}/enviar-resumen` — body { "to_email": string }

ADMIN
- GET `/admin/pedidos` — query `status` opcional
- PATCH `/admin/pedidos/{id}` — body { "status": integer } (valida transiciones)
- POST `/admin/pedidos/{id}/items` — body `AgregarItemRequest`:
  {
    "tipo_item": integer (1=OPCION_SERVICIO,2=PAQUETE) (required),
    "referencia_id": uuid (required),
    "cantidad": integer (required),
    "precio_unit": number (required)
  }
- POST `/admin/pedidos/{id}/asignar-proveedor` — body `AsignarProveedorRequest`:
  {
    "item_pedido_id": uuid (required),
    "proveedor_id": uuid (required),
    "inicio": date-time (required),
    "fin": date-time (required),
    "hold_id": uuid (opcional)
  }

Notas y ajuste crítico con el esquema actual:
- En `db/bosstrap_remaste.sql` la tabla `ev_contratacion.pedido_evento` NO tiene columna `paquete_id`.
- El modelo correcto en este esquema es representar paquetes como items en `ev_contratacion.item_pedido_evento` con `tipo_item = 2` y `referencia_id = paquete_id`.
- Recomendación de implementación para `CrearPedidoDesdePaquete`:
  1. Crear `pedido_evento` (sin campo `paquete_id`).
  2. Crear `item_pedido_evento` con `tipo_item=2`, `referencia_id=paquete_id`, `cantidad=1`, `precio_unit` calculado desde `ev_paquetes.precio_paquete` vigente.
  3. Calcular `monto_total` en `pedido_evento` sumando items.

Esto evita cambios en la BD y respeta el esquema aplicado.

**Actualización 2025-11-24:**
- Se detectó y corrigió un error 500 en `GET /contratacion/pedidos/mios` y `POST /contratacion/pedidos`.
- Causa: El código intentaba leer la columna `notas` de la tabla `pedido_evento`, la cual no existe en el esquema actual (`db/bosstrap_remaste.sql`).
- Solución: Se eliminó la referencia a `notas` en las consultas SQL del repositorio `MySQLPedidoRepository`.
- Estado actual: Endpoints de contratación validados y funcionando correctamente (200 OK).

---

## Recomendaciones generales

- Normalizar inputs en la capa HTTP: validar UUIDs y campos obligatorios (`servicio_id`, `paquete_id`, `opcion_servicio_id`, etc.).
- Asegurar que los endpoints idempotentes usen `request_id` cuando aplique (creación de pedidos/reservas).
- Documentar claramente en los contratos que `CrearPedidoDesdePaquete` acepta `paquete_id` pero que la persistencia se mapea mediante un item (nota incluida arriba).
- Uniformar la forma de devolver listas: preferir `{ items: [...] }` o arrays pero ser consistente; el frontend ya contiene lógica defensiva (`Array.isArray(x) ? x : x.items`).

---

Si quieres que guarde este archivo y borre `ENDPOINTS.md`, lo hago ahora (ya tengo permiso implícito). ¿Procedo?
