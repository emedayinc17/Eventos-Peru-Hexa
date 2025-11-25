# Resumen Técnico - Integración Frontend Phase 3

## 📦 Archivos Modificados

### Archivos JavaScript

#### `js/services.js`
**Cambios:**
- ❌ Eliminado endpoint duplicado `adminCambiarEstado`
- ✅ Corregidas todas las rutas ADMIN para usar `/v1/contratacion/admin/...`
- ✅ Agregado endpoint `adminTodosPedidos()` para listar todos los pedidos del sistema

**Nuevos Métodos:**
```javascript
CONTRATACION.adminTodosPedidos()           // GET /v1/contratacion/admin/pedidos
CONTRATACION.adminDetallePedido(id)        // GET /v1/contratacion/admin/pedidos/{id}
CONTRATACION.adminCambiarEstado(id, body)  // PATCH /v1/contratacion/admin/pedidos/{id}
CONTRATACION.adminAgregarItems(id, body)   // POST /v1/contratacion/admin/pedidos/{id}/items
CONTRATACION.adminEliminarItems(id, body)  // DELETE /v1/contratacion/admin/pedidos/{id}/items
CONTRATACION.adminAsignarProveedor(id, body) // POST /v1/contratacion/admin/pedidos/{id}/asignar-proveedor
```

#### `js/app.js`
**Funciones Agregadas:**

1. **Gestión de Modales ADMIN:**
```javascript
setupAdminModals()                    // Inicializa y vincula eventos de modales
abrirModalAsignarProveedor(pedidoId)  // Abre modal de asignación con validación
abrirModalGestionItems(pedidoId)      // Abre modal de gestión de items
cargarItemsParaEliminar(pedidoId)     // Carga items actuales para eliminar
```

2. **Validación de Estados:**
```javascript
esTransicionValida(estadoActual, estadoNuevo) // Valida según TRANSICIONES_VALIDAS
getNombreEstado(estado)                        // Mapea código a nombre legible

const TRANSICIONES_VALIDAS = {
  0: [1, 5],  // DRAFT -> COTIZADO, CANCELADO
  1: [2, 5],  // COTIZADO -> APROBADO, CANCELADO
  2: [3, 5],  // APROBADO -> ASIGNADO, CANCELADO
  3: [4, 5],  // ASIGNADO -> CERRADO, CANCELADO
  4: [],      // CERRADO (final)
  5: []       // CANCELADO (final)
};
```

3. **Sistema de Notificaciones:**
```javascript
showNotification(message, type)  // type: 'success', 'error', 'info', 'warning'
createToastContainer()           // Crea contenedor de toasts si no existe
```

4. **Actualización de Pedidos:**
```javascript
refreshAdminPedidos()          // Recarga lista de pedidos ADMIN con filtros
cambiarEstadoPedidoAdmin(id, estado)  // Cambia estado con validación
updateAdminPedidosStats(pedidos)      // Actualiza tarjetas de estadísticas
verDetallePedidoAdmin(id)             // Muestra modal de detalle avanzado
createAdminPedidoItem(pedido)         // Renderiza tarjeta de pedido para ADMIN
```

**Funciones Modificadas:**

1. **`loadContratacion()`:**
   - Detecta rol (ADMIN vs CLIENTE)
   - Muestra panel correspondiente (admin panel vs client list)
   - Inicializa eventos de filtros y botones

2. **`createPedidoItem(pedido, esAdmin)`:**
   - Renderiza tarjetas diferentes según rol
   - ADMIN: Con dropdown de estado y botones de acción
   - CLIENTE: Solo lectura con botón "Ver detalle"

3. **`verDetallePedidoAdmin(id)`:**
   - Tabla de items mejorada con columnas: ID, Servicio/Opción, Cant, Precio Unit, Subtotal
   - Pie de tabla con monto_total
   - Botones de acción rápida (Cambiar Estado, Asignar Proveedor, Gestionar Items)
   - Validación de transiciones en selector de estado

### Archivos HTML

#### `index.html`
**Nuevos Modales:**

1. **`asignarProveedorModal`:**
```html
<div class="modal fade" id="asignarProveedorModal">
  <!-- Modal con checkboxes para seleccionar items -->
  <!-- Input para proveedor_id -->
  <!-- Validación: solo pedidos APROBADO (2) -->
</div>
```

2. **`gestionItemsModal`:**
```html
<div class="modal fade" id="gestionItemsModal">
  <!-- Tabs: Agregar | Eliminar -->
  <!-- Tab Agregar: Form con opcion_servicio_id, cantidad, precio, nombre -->
  <!-- Tab Eliminar: Lista de items + input para IDs separados por coma -->
</div>
```

3. **Toast Container:**
```html
<div class="toast-container position-fixed bottom-0 end-0 p-3" id="toast-container"></div>
```

**Modificaciones en `#view-contratacion`:**
- Panel admin con filtros (estado, ID, cliente)
- Estadísticas admin (6 tarjetas: total, cotizados, aprobados, asignados, cerrados, cancelados)
- Lista de pedidos con selector de estado inline
- Botones de acción: Ver detalle, Asignar, Items

---

## 🔄 Flujo de Datos

### Crear Pedido (Cliente)
```mermaid
Usuario → Catálogo → "Reservar/Contratar" 
  → Modal (fecha, hora, ubicación) 
  → CONTRATACION.crearPedido(payload)
  → POST /v1/contratacion/pedidos
  → Respuesta: pedido {id, status: 0, monto_total, items: [...]}
  → Redirect a /contratacion
```

**Payload:**
```javascript
{
  "paquete_id": "paq_boda_clasica",
  "fecha_evento": "2025-12-25",
  "hora_inicio": "18:00:00",
  "hora_fin": "23:00:00",
  "ubicacion": "Salón Los Jardines, Lima",
  "request_id": "uuid-autogenerado",
  "correlation_id": "uuid-autogenerado"
}
```

### Cambiar Estado (Admin)
```mermaid
Admin → Selector Estado → onChange
  → esTransicionValida(actual, nuevo)
  → SI válido: CONTRATACION.adminCambiarEstado(id, {estado: nuevo})
  → PATCH /v1/contratacion/admin/pedidos/{id}
  → NO válido: showNotification("Transición no permitida", "error")
```

**Payload:**
```javascript
{
  "estado": 1  // Nuevo estado (int 0-5)
}
```

### Asignar Proveedor (Admin)
```mermaid
Admin → Click "Asignar" 
  → abrirModalAsignarProveedor(id)
  → Cargar pedido: adminDetallePedido(id)
  → SI status !== 2: showNotification("Solo APROBADO", "error")
  → SI status === 2: Mostrar modal con checkboxes de items
  → Seleccionar items + ingresar proveedor_id
  → Submit → adminAsignarProveedor(id, {item_pedido_ids, proveedor_id})
  → POST /v1/contratacion/admin/pedidos/{id}/asignar-proveedor
  → Respuesta: {message, reservas_creadas: [...]}
  → showNotification("Proveedor asignado", "success")
  → refreshAdminPedidos()
```

**Payload:**
```javascript
{
  "item_pedido_ids": ["item-uuid-1", "item-uuid-2"],
  "proveedor_id": "proveedor-uuid"
}
```

### Agregar Items (Admin)
```mermaid
Admin → Click "Items" → Tab "Agregar"
  → Form (opcion_servicio_id, cantidad, precio, nombre)
  → Submit → adminAgregarItems(id, {items: [...]})
  → POST /v1/contratacion/admin/pedidos/{id}/items
  → Backend: Crea item, calcula subtotal, actualiza monto_total
  → Respuesta: {message, items_agregados: [...], nuevo_monto_total}
  → showNotification("Items agregados", "success")
  → refreshAdminPedidos()
```

**Payload:**
```javascript
{
  "items": [{
    "opcion_servicio_id": "opt_foto_basica",
    "cantidad": 2,
    "precio_unit_vigente": 150.00,
    "nombre_servicio": "Fotografía Básica - 4 horas"
  }]
}
```

### Eliminar Items (Admin)
```mermaid
Admin → Click "Items" → Tab "Eliminar"
  → Cargar items actuales: adminDetallePedido(id)
  → Mostrar lista con IDs
  → Copiar IDs → Input (separados por coma)
  → Submit → adminEliminarItems(id, {item_ids: [...]})
  → DELETE /v1/contratacion/admin/pedidos/{id}/items
  → Backend: Elimina items, recalcula monto_total
  → Respuesta: {message, items_eliminados: [...], nuevo_monto_total}
  → showNotification("Items eliminados", "success")
  → refreshAdminPedidos()
```

**Payload:**
```javascript
{
  "item_ids": ["item-uuid-1", "item-uuid-2", "item-uuid-3"]
}
```

---

## 🎨 Componentes de UI

### Badges de Estado
```javascript
function getStatusInfo(status) {
  return {
    0: { text: '📝 Borrador', class: 'bg-secondary' },
    1: { text: '💰 Cotizado', class: 'bg-info' },
    2: { text: '✅ Aprobado', class: 'bg-success' },
    3: { text: '👥 Asignado', class: 'bg-primary' },
    4: { text: '🏁 Cerrado', class: 'bg-dark' },
    5: { text: '❌ Cancelado', class: 'bg-danger' }
  }[status];
}
```

### Toasts Bootstrap
```javascript
// Ejemplo de uso
showNotification('Operación exitosa', 'success');
showNotification('Error al procesar', 'error');
showNotification('Advertencia importante', 'warning');
```

Renderizado:
```html
<div class="toast align-items-center text-bg-success border-0" role="alert">
  <div class="d-flex">
    <div class="toast-body">Operación exitosa</div>
    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
  </div>
</div>
```

### Tabla de Items (Modal Detalle)
```html
<table class="table table-sm table-striped">
  <thead>
    <tr>
      <th>ID</th>
      <th>Servicio / Opción</th>
      <th>Cant.</th>
      <th>Precio Unit.</th>
      <th>Subtotal</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code class="small">abc123...</code></td>
      <td>
        <strong>Fotografía Básica</strong><br>
        <small class="text-muted">Opción: opt_foto_ba...</small>
      </td>
      <td>2</td>
      <td>S/ 150.00</td>
      <td class="fw-semibold">S/ 300.00</td>
    </tr>
  </tbody>
  <tfoot>
    <tr class="table-primary">
      <td colspan="4" class="text-end"><strong>Total:</strong></td>
      <td class="fw-bold">S/ 300.00</td>
    </tr>
  </tfoot>
</table>
```

---

## 🧪 Testing Manual

### Caso 1: Crear Pedido y Cambiar Estados
1. Login como CLIENTE
2. Ir a `/catalogo` → Click "Reservar / Contratar" en un paquete
3. Completar formulario → Confirmar
4. Verificar: Pedido creado con estado 0 (BORRADOR)
5. Logout → Login como ADMIN
6. Ir a `/contratacion` → Buscar pedido creado
7. Cambiar estado: 0 → 1 (COTIZADO) ✅
8. Cambiar estado: 1 → 2 (APROBADO) ✅
9. Intentar: 2 → 4 (CERRADO) ❌ (debe fallar, transición no permitida)
10. Verificar: Notificación de error mostrada

### Caso 2: Asignar Proveedor
**Pre-requisitos:** Tener un pedido en estado APROBADO (2) con items

1. Login como ADMIN
2. Ir a `/contratacion` → Buscar pedido APROBADO
3. Click "Asignar" → Modal abre
4. Verificar: Lista de items con checkboxes
5. Seleccionar 1+ items
6. Ingresar proveedor_id válido (obtener de DB o crear primero)
7. Click "Confirmar Asignación"
8. Verificar: 
   - Toast success mostrado
   - Estado cambia a 3 (ASIGNADO)
   - Lista se recarga

### Caso 3: Agregar Items
1. Login como ADMIN
2. Ir a `/contratacion` → Click "Items" en cualquier pedido
3. Tab "Agregar Items"
4. Completar:
   - opcion_servicio_id: `opt_foto_basica`
   - cantidad: 2
   - precio_unit_vigente: 150.00
   - nombre_servicio: "Fotografía Básica"
5. Click "Agregar Item"
6. Verificar:
   - Toast success
   - Tab "Eliminar" muestra nuevo item
   - Detalle de pedido muestra item agregado
   - monto_total actualizado

### Caso 4: Eliminar Items
1. Login como ADMIN
2. Ir a `/contratacion` → Click "Items" → Tab "Eliminar"
3. Ver lista de items con IDs
4. Copiar 1+ IDs
5. Pegar en input separados por coma
6. Click "Eliminar Items Seleccionados"
7. Verificar:
   - Toast success
   - Items desaparecen de la lista
   - monto_total recalculado

### Caso 5: Validación de Transiciones
1. Login como ADMIN
2. Crear pedido en estado BORRADOR (0)
3. Intentar cambiar directamente a CERRADO (4)
4. Verificar:
   - Error mostrado: "Transición no permitida: BORRADOR → CERRADO"
   - Selector vuelve al estado anterior
5. Cambiar a COTIZADO (1) → ✅ OK
6. Cambiar a APROBADO (2) → ✅ OK
7. Cambiar a CANCELADO (5) → ✅ OK (permitido desde cualquier estado)

---

## 🔒 Seguridad

### Validación Client-Side
- ✅ Transiciones de estado validadas antes de enviar request
- ✅ Estado APROBADO requerido para asignación de proveedores
- ⚠️ **Nota:** La validación definitiva es server-side, el frontend solo previene errores comunes

### Tokens JWT
- ✅ Token incluido en header `Authorization: Bearer <token>`
- ✅ Endpoints ADMIN verifican rol en backend
- ✅ Frontend oculta opciones según rol, pero backend valida permisos

### Sanitización
- ✅ Función `escapeHtml()` usada para prevenir XSS en renders dinámicos
- ✅ IDs de items/proveedores validados como UUIDs en backend

---

## 📊 Métricas de Rendimiento

### Carga Inicial de Pedidos ADMIN
- **Endpoint:** `GET /v1/contratacion/admin/pedidos`
- **Sin filtros:** Devuelve TODOS los pedidos (puede ser lento con >1000 pedidos)
- **Con filtros:** Filtrado server-side recomendado (actualmente client-side)
- **Mejora futura:** Implementar paginación real con limit/offset

### Actualización de Estadísticas
- **Método:** `updateAdminPedidosStats(pedidos)`
- **Complejidad:** O(n) - itera todos los pedidos
- **Optimización:** Usar reduce() si n > 100

### Renders de Modales
- **Items:** Renderizado dinámico con template literals
- **Complejidad:** O(n) donde n = número de items
- **Nota:** Para pedidos con >50 items, considerar virtualización

---

## 🐛 Debugging

### Habilitar Logs Detallados
```javascript
// En fetchJson (services.js), ya hay:
console.log(`🔄 ${method} ${url}`);

// Para ver payloads completos:
console.log("📤 Enviando payload:", payload);
console.log("✅ Respuesta recibida:", response);
```

### Inspeccionar Estado de Pedidos
```javascript
// En consola del navegador:
const pedidos = await CONTRATACION.adminTodosPedidos();
console.table(pedidos.map(p => ({
  id: p.id.substring(0, 8),
  estado: p.status,
  monto: p.monto_total,
  items: p.items?.length || 0
})));
```

### Verificar Transiciones
```javascript
// Testear validación:
esTransicionValida(0, 1); // true (DRAFT → COTIZADO)
esTransicionValida(0, 4); // false (DRAFT → CERRADO)
esTransicionValida(2, 5); // true (APROBADO → CANCELADO)
```

---

## 🚀 Próximos Pasos Técnicos

### Mejoras Pendientes
1. **Paginación Real:** Implementar limit/offset en adminTodosPedidos
2. **Autocompletado:** Usar tom-select para proveedor_id
3. **Validación de UUIDs:** Regex client-side antes de enviar
4. **Caché de Catálogo:** Evitar recargar paquetes/servicios cada vez
5. **Optimistic Updates:** Actualizar UI antes de confirmar request
6. **Undo/Redo:** Permitir revertir cambios de estado
7. **Drag & Drop:** Para agregar items desde catálogo

### Refactoring Sugerido
```javascript
// Separar lógica de negocio en módulos
// js/pedidos.js
export class PedidoManager {
  constructor(contratacionAPI) {
    this.api = contratacionAPI;
  }
  
  async cambiarEstado(id, nuevoEstado) {
    // Validación + request + notificación
  }
  
  async asignarProveedor(id, itemIds, proveedorId) {
    // Validación + request + notificación
  }
}

// js/app.js
import { PedidoManager } from './pedidos.js';
const pedidoManager = new PedidoManager(CONTRATACION);
```

---

## 📚 Referencias

- **Bootstrap 5.3 Docs:** https://getbootstrap.com/docs/5.3/
- **Fetch API:** https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
- **ES6 Modules:** https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules
- **JWT Handling:** https://jwt.io/

---

**Última Actualización:** 2025-11-22  
**Versión Frontend:** Phase 3 Complete  
**Autor:** GitHub Copilot (Claude Sonnet 4.5)
