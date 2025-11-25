# Frontend Vanilla - Changelog

## [Phase 3.1 - UX Enhancement] - 2025-11-22

### 🎯 Integración de Proveedores en Flujo de Reserva

**Objetivo:** Eliminar vista separada de Proveedores para CLIENTES y permitir selección de proveedores directamente durante la reserva del paquete.

#### ✨ Cambios Principales

##### 1. **Modal de Contratación Mejorado**
- ✅ **Diseño ampliado:** Cambio de `modal-dialog` a `modal-lg` para más espacio
- ✅ **Sección de servicios:** Al seleccionar fecha, se cargan dinámicamente los servicios del paquete
- ✅ **Selección de proveedores por servicio:**
  - Dropdowns individuales para cada servicio
  - Carga automática de proveedores disponibles por fecha
  - Muestra rating (estrellas ⭐) y precio referencial
  - Opción "Sin asignar" permite que Admin asigne después
- ✅ **UI/UX mejorada:**
  - Header con color primary y nombre del paquete
  - Layout en dos columnas para datos del evento
  - Spinner de carga mientras se obtienen proveedores
  - Mensajes de error si no hay proveedores disponibles

##### 2. **Función `cargarProveedoresParaServicios()`** 🆕
```javascript
async function cargarProveedoresParaServicios(servicios, fecha, paquete)
```
- ✅ Itera sobre cada servicio del paquete
- ✅ Llama a `PROVEEDORES.buscarDisponibles(servicioId, fecha, 20, 0)`
- ✅ Ordena proveedores por rating (mayor a menor)
- ✅ Renderiza SELECT con opciones:
  - "Sin asignar (Admin asignará después)" - valor vacío
  - Proveedor: "Nombre ⭐⭐⭐⭐⭐ - S/ 500"
- ✅ Manejo de errores por servicio (no bloquea otros dropdowns)

##### 3. **Payload Extendido de Contratación**
El frontend ahora envía:
```json
{
  "paquete_id": "uuid",
  "tipo_evento_id": "uuid",
  "fecha_evento": "2025-12-25",
  "hora_inicio": "18:00",
  "ubicacion": "...",
  "proveedores_seleccionados": [  // NUEVO ✨
    {
      "opcion_servicio_id": "uuid-servicio-1",
      "proveedor_id": "uuid-proveedor-1"
    },
    {
      "opcion_servicio_id": "uuid-servicio-2",
      "proveedor_id": "uuid-proveedor-2"
    }
  ]
}
```

##### 4. **Vista de Proveedores Restringida a ADMIN**
- ✅ Modificado `configureNavbar()` en `app.js`
- ✅ Enlace "Proveedores" solo visible para rol ADMIN
- ✅ CLIENTES no ven la vista separada de proveedores
- ✅ ADMIN mantiene acceso completo para gestión interna

#### 🔧 Cambios Backend

##### 1. **Schema Actualizado** (`schemas.py`)
```python
class ProveedorSeleccionado(BaseModel):
    opcion_servicio_id: str
    proveedor_id: str

class CrearPedidoDesdePaquete(BaseModel):
    # ... campos existentes ...
    proveedores_seleccionados: Optional[List[ProveedorSeleccionado]] = None  # NUEVO
```

##### 2. **Command Modificado** (`commands.py`)
- ✅ Detecta si `proveedores_seleccionados` existe en payload
- ✅ **Estado inicial automático:**
  - Con proveedores → `COTIZADO (1)`
  - Sin proveedores → `DRAFT (0)`
- ✅ Crea holds individuales para cada proveedor seleccionado
- ✅ Rollback de holds si falla alguna asignación

##### 3. **Use Case Actualizado** (`crear_pedido_desde_paquete.py`)
```python
def execute(
    self,
    session: Any,
    *,
    # ... parámetros existentes ...
    proveedores_seleccionados: Optional[list] = None  # NUEVO
) -> Pedido:
```

##### 4. **Router Modificado** (`router.py`)
- ✅ Convierte `proveedores_seleccionados` a dict para pasar al use case
- ✅ Maneja None/empty list correctamente

#### 📋 Flujo Completo Actualizado

**Flujo CLIENTE (Nueva UX):**
1. Ver catálogo de paquetes
2. Click en "Contratar"
3. **Modal ampliado se abre:**
   - Ingresar fecha, hora, ubicación
   - **Al seleccionar fecha:** Servicios del paquete aparecen
   - **Para cada servicio:** Dropdown con proveedores disponibles
   - **Seleccionar proveedores** (o dejar "Sin asignar")
4. Click en "Confirmar Reserva"
5. **Backend procesa:**
   - Si hay proveedores → Estado COTIZADO, crea holds
   - Si no hay proveedores → Estado DRAFT, Admin asignará después

**Flujo ADMIN (Sin cambios):**
1. Vista de todos los pedidos
2. Cambiar estado según transiciones válidas
3. Asignar/reasignar proveedores en estado APROBADO
4. Gestionar items (agregar/eliminar)

#### 🎨 Mejoras UX/UI

- ✅ **Experiencia unificada:** Un solo modal para toda la reserva
- ✅ **Progresividad:** Servicios aparecen solo después de elegir fecha
- ✅ **Feedback visual:** Spinner mientras carga proveedores
- ✅ **Flexibilidad:** Cliente puede dejar sin asignar si no decide
- ✅ **Transparencia:** Muestra rating y precio de cada proveedor
- ✅ **Separación de roles:**
  - CLIENTE: Flujo simplificado de reserva
  - ADMIN: Control total sobre pedidos y proveedores

#### 🔍 Validaciones y Manejo de Errores

- ✅ **Frontend:**
  - Validación de campos requeridos (fecha, hora, ubicación)
  - Notificación toast si faltan datos
  - Manejo de error si servicio no tiene proveedores

- ✅ **Backend:**
  - Rollback de holds si falla alguna asignación
  - Estado inicial basado en presencia de proveedores
  - Validación de schema con Pydantic

#### 📊 Estado de los Pedidos

| Proveedores Seleccionados | Estado Inicial | Siguiente Paso |
|---------------------------|----------------|----------------|
| ✅ Sí (1 o más)          | COTIZADO (1)   | Admin aprueba → APROBADO |
| ❌ No (lista vacía)      | DRAFT (0)      | Admin asigna y cotiza → COTIZADO |

#### 🚀 Beneficios de la Integración

1. **UX más fluida:** No más navegación entre vistas separadas
2. **Menos pasos:** Reserva + selección de proveedores en un solo flujo
3. **Mejor conversión:** Cliente completa todo de una vez
4. **Claridad de rol:** ADMIN ve proveedores para gestión, CLIENTE para reserva
5. **Flexibilidad:** Cliente puede elegir o dejar que Admin decida

#### 🐛 Issues Conocidos

- ⚠️ Si un servicio no tiene proveedores disponibles, muestra dropdown deshabilitado
- ⚠️ No hay límite de proveedores cargados por servicio (actualmente 20)
- ℹ️ El precio mostrado es referencial (`precio_referencia` del proveedor)

#### 📝 Archivos Modificados

**Frontend:**
- `frontend-vanilla/js/app.js`:
  - Función `showContratacionModal()` ampliada
  - Función `cargarProveedoresParaServicios()` agregada
  - Función `configureNavbar()` modificada

**Backend:**
- `services/contratacion-service/app/entrypoints/fastapi/schemas.py` - Schema extendido
- `services/contratacion-service/app/entrypoints/fastapi/router.py` - Router actualizado
- `services/contratacion-service/app/application/commands.py` - Lógica de holds modificada
- `services/contratacion-service/app/application/use_cases/crear_pedido_desde_paquete.py` - Signature actualizada

---

## [Phase 3 Integration] - 2025-11-22

### ✨ Nuevas Funcionalidades ADMIN

#### 1. **Gestión Completa de Pedidos**
- ✅ Vista de todos los pedidos del sistema (`GET /v1/contratacion/admin/pedidos`)
- ✅ Filtros avanzados:
  - Por estado (Borrador, Cotizado, Aprobado, Asignado, Cerrado, Cancelado)
  - Por ID de pedido
  - Por cliente (email o nombre)
- ✅ Estadísticas globales en tiempo real por estado

#### 2. **Cambio de Estado con Validación**
- ✅ Selector de estado en cada tarjeta de pedido
- ✅ Validación client-side de transiciones permitidas:
  - `DRAFT (0)` → `COTIZADO (1)` o `CANCELADO (5)`
  - `COTIZADO (1)` → `APROBADO (2)` o `CANCELADO (5)`
  - `APROBADO (2)` → `ASIGNADO (3)` o `CANCELADO (5)`
  - `ASIGNADO (3)` → `CERRADO (4)` o `CANCELADO (5)`
- ✅ Notificaciones toast de éxito/error
- ✅ Endpoint: `PATCH /v1/contratacion/admin/pedidos/{id}` con `{estado: int}`

#### 3. **Modal de Asignación de Proveedores** 🆕
- ✅ Asignar proveedores a items específicos de un pedido
- ✅ Validación: Solo pedidos en estado **APROBADO (2)**
- ✅ Selección múltiple de items mediante checkboxes
- ✅ Endpoint: `POST /v1/contratacion/admin/pedidos/{id}/asignar-proveedor`
- ✅ Payload: `{item_pedido_ids: [id1, id2], proveedor_id: "uuid"}`

#### 4. **Modal de Gestión de Items** 🆕
- ✅ **Tab "Agregar Items":**
  - Campos: `opcion_servicio_id`, `cantidad`, `precio_unit_vigente`, `nombre_servicio`
  - Endpoint: `POST /v1/contratacion/admin/pedidos/{id}/items`
  - Payload: `{items: [{opcion_servicio_id, cantidad, precio_unit_vigente?, nombre_servicio?}]}`
- ✅ **Tab "Eliminar Items":**
  - Lista visual de items actuales con IDs
  - Input para IDs separados por coma
  - Endpoint: `DELETE /v1/contratacion/admin/pedidos/{id}/items`
  - Payload: `{item_ids: ["id1", "id2"]}`

#### 5. **Vista de Detalle de Pedido Mejorada** 🔄
- ✅ Tabla de items con columnas:
  - ID (8 primeros caracteres)
  - Servicio/Opción (nombre + opcion_servicio_id)
  - Cantidad
  - Precio Unitario
  - **Subtotal** (nuevo)
- ✅ Pie de tabla con **monto_total** destacado
- ✅ Botones de acción rápida en el modal:
  - Cambiar Estado
  - Asignar Proveedor
  - Gestionar Items

### 🎨 Mejoras UX/UI

#### Sistema de Notificaciones Toast
- ✅ Notificaciones Bootstrap en esquina superior derecha
- ✅ Tipos: `success`, `error`, `info`, `warning`
- ✅ Auto-dismiss después de 5 segundos
- ✅ Función global: `showNotification(message, type)`

#### Validación de Transiciones
- ✅ Feedback inmediato si transición no permitida
- ✅ Mensajes descriptivos: "Transición no permitida: BORRADOR → CERRADO"
- ✅ Reversion automática del selector si transición inválida

#### Filtros y Búsqueda
- ✅ Botón "Limpiar filtros" para resetear todos los filtros
- ✅ Búsqueda en tiempo real (sin necesidad de botón "Aplicar")
- ✅ Contador de filtros activos

### 🔧 Correcciones Técnicas

#### services.js
- ❌ Eliminado endpoint `adminCambiarEstado` duplicado
- ✅ Todas las rutas ADMIN ahora usan `/v1/contratacion/admin/...`
- ✅ Payload de cambio de estado usa `{estado: int}` (no `{status: int}`)

#### app.js
- ✅ Función `cambiarEstadoPedidoAdmin` actualizada con validación
- ✅ Funciones globales agregadas:
  - `abrirModalAsignarProveedor(pedidoId)`
  - `abrirModalGestionItems(pedidoId)`
  - `cargarItemsParaEliminar(pedidoId)`
  - `esTransicionValida(estadoActual, estadoNuevo)`
  - `getNombreEstado(estado)`
  - `showNotification(message, type)`

### 📊 Integración con Backend (Phase 3)

#### Nuevos Campos en item_pedido_evento
El frontend ahora muestra y gestiona todos los campos agregados en Phase 3:
- `opcion_servicio_id` (CHAR 36 NULL)
- `nombre_servicio` (VARCHAR 200 NULL)
- `precio_unitario` (DECIMAL 12,2 NULL)
- `subtotal` (DECIMAL 12,2 NULL)
- `tipo_item` (VARCHAR 50, default 'SERVICIO')

#### Endpoints Utilizados

**CLIENTE:**
- `POST /v1/contratacion/pedidos` - Crear pedido desde paquete
- `GET /v1/contratacion/pedidos/mios` - Listar mis pedidos
- `GET /v1/contratacion/pedidos/{id}` - Detalle de mi pedido

**ADMIN:**
- `GET /v1/contratacion/admin/pedidos` - Listar TODOS los pedidos
- `GET /v1/contratacion/admin/pedidos/{id}` - Detalle de cualquier pedido
- `PATCH /v1/contratacion/admin/pedidos/{id}` - Cambiar estado (body: `{estado: int}`)
- `POST /v1/contratacion/admin/pedidos/{id}/items` - Agregar items
- `DELETE /v1/contratacion/admin/pedidos/{id}/items` - Eliminar items (body: `{item_ids: []}`)
- `POST /v1/contratacion/admin/pedidos/{id}/asignar-proveedor` - Asignar proveedor

### 🎯 Flujo Completo de Trabajo ADMIN

1. **Ver todos los pedidos** en `/contratacion` (rol ADMIN)
2. **Aplicar filtros** por estado/cliente/ID
3. **Cambiar estado** usando dropdown (con validación)
4. **Ver detalle** del pedido (modal completo)
5. **Gestionar items:**
   - Agregar nuevos items con precio/cantidad
   - Eliminar items por ID
6. **Asignar proveedores:**
   - Solo en estado APROBADO
   - Seleccionar items específicos
   - Ingresar proveedor_id
7. **Transiciones válidas:**
   - DRAFT → COTIZADO → APROBADO → ASIGNADO → CERRADO
   - Cualquier estado → CANCELADO (excepto CERRADO)

### 📝 Notas de Implementación

- **Arquitectura Hexagonal:** El frontend sigue el patrón de separación entre cliente (API calls) y lógica de presentación
- **Bootstrap 5.3.3:** Usado para modales, toasts, badges, y componentes responsivos
- **Vanilla JS + ES6 Modules:** Sin frameworks adicionales, máxima compatibilidad
- **Manejo de Errores:** Try-catch en todas las operaciones async con feedback visual

### 🐛 Issues Conocidos y Limitaciones

- ⚠️ Los proveedores disponibles para asignación deben buscarse manualmente (UUID)
- ⚠️ No hay validación de que el proveedor_id exista antes de asignar
- ⚠️ Los filtros de ADMIN no persisten en localStorage (se resetean al recargar)
- ℹ️ El endpoint de reservas directas de proveedores ha sido deshabilitado (solo vía contratación)

### 🚀 Próximas Mejoras Sugeridas

1. **Autocompletar de proveedores** en modal de asignación
2. **Validación server-side de transiciones** (el backend ya la tiene)
3. **Historial de cambios** en el pedido (auditoría)
4. **Exportar pedidos** a CSV/PDF
5. **Notificaciones push** para cambios de estado
6. **Paginación** en lista de pedidos ADMIN (actualmente carga todos)

---

## [Versiones Anteriores]

### [Phase 2] - 2025-11-20
- Implementación de vista de Proveedores
- Búsqueda de disponibilidad por servicio/fecha
- Modal de creación de reservas (deshabilitado en Phase 3)

### [Phase 1] - 2025-11-18
- Implementación de IAM (Login/Register/Admin Users)
- Vista de Catálogo con paquetes y servicios
- Sistema de autenticación JWT
