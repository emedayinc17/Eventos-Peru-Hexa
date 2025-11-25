# Guía Rápida - Frontend Actualizado (Phase 3)

## 🎯 Resumen de Cambios

El frontend ha sido actualizado para integrarse completamente con los servicios de **Contratación Phase 3**, implementando todas las funcionalidades de gestión de pedidos, asignación de proveedores, y administración de items.

---

## 🔐 Acceso y Permisos

### Usuario CLIENTE
- **Puede:**
  - Ver catálogo de paquetes
  - Crear pedidos desde paquetes
  - Ver sus propios pedidos (`/contratacion`)
  - Ver detalle de sus pedidos
- **No puede:**
  - Cambiar estados de pedidos
  - Asignar proveedores
  - Agregar/eliminar items

### Usuario ADMIN
- **Puede hacer TODO lo de CLIENTE +:**
  - Ver TODOS los pedidos del sistema
  - Filtrar por estado/cliente/ID
  - Cambiar estado de cualquier pedido (con validación)
  - Asignar proveedores a items (solo en estado APROBADO)
  - Agregar items a pedidos
  - Eliminar items de pedidos
  - Ver estadísticas globales del sistema

---

## 📋 Guía de Uso - CLIENTE

### 1. Crear un Pedido desde el Catálogo

1. Ir a **Catálogo** (`#/catalogo`)
2. Hacer clic en **"Reservar / Contratar"** en cualquier paquete
3. Completar formulario:
   - Fecha del evento (obligatorio)
   - Hora de inicio (obligatorio)
   - Hora de fin (opcional)
   - Ubicación (obligatorio)
4. Confirmar contratación
5. **Resultado:** Pedido creado en estado **BORRADOR (0)**

### 2. Ver Mis Pedidos

1. Ir a **Contratación** (`#/contratacion`)
2. Ver tarjetas con:
   - Estado del pedido (badge de color)
   - Fecha y hora del evento
   - Ubicación
   - Monto total
3. **Filtrar** por estado usando selector superior
4. **Ver detalle** haciendo clic en botón "Detalle"

### 3. Estadísticas Personales

En la parte superior de `/contratacion` verás 4 tarjetas:
- **Total Pedidos:** Todos tus pedidos
- **Confirmados:** Aprobados + Asignados + Cerrados
- **Pendientes:** Borradores + Cotizados
- **Cancelados:** Pedidos cancelados

---

## 🛠️ Guía de Uso - ADMIN

### 1. Vista General de Pedidos

1. Ir a **Contratación** (`#/contratacion`) como ADMIN
2. Verás **6 tarjetas de estadísticas:**
   - Total, Cotizados, Aprobados, Asignados, Cerrados, Cancelados
3. Panel de filtros con:
   - **Estado:** Dropdown con todos los estados
   - **Buscar por ID:** Input para ID de pedido
   - **Buscar por Cliente:** Input para email/nombre
   - **Botones:** Limpiar filtros | Aplicar

### 2. Cambiar Estado de un Pedido

**Opción A: Desde la lista**
1. Ubicar el pedido en la lista
2. Usar el **dropdown de estado** directamente en la tarjeta
3. Seleccionar nuevo estado
4. ✅ **Validación automática:** Si la transición no es válida, se muestra error

**Opción B: Desde el modal de detalle**
1. Hacer clic en **"Ver detalle"**
2. En el modal, seleccionar estado en dropdown
3. Hacer clic en **"Aplicar Estado"**

**Transiciones Válidas:**
```
BORRADOR (0) → COTIZADO (1) o CANCELADO (5)
COTIZADO (1) → APROBADO (2) o CANCELADO (5)
APROBADO (2) → ASIGNADO (3) o CANCELADO (5)
ASIGNADO (3) → CERRADO (4) o CANCELADO (5)
CERRADO (4) → [ninguna transición]
CANCELADO (5) → [ninguna transición]
```

### 3. Asignar Proveedor a Items 🆕

**Pre-requisito:** El pedido debe estar en estado **APROBADO (2)**

1. Hacer clic en **"Asignar"** en la tarjeta del pedido
2. En el modal:
   - Ver items disponibles con checkboxes
   - **Seleccionar** uno o más items
   - Ingresar **Proveedor ID** (UUID completo)
3. Hacer clic en **"Confirmar Asignación"**
4. ✅ **Resultado:** Items asignados, estado cambia a **ASIGNADO (3)**

**Ejemplo de Proveedor ID:**
```
a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### 4. Agregar Items a un Pedido 🆕

1. Hacer clic en **"Items"** en la tarjeta del pedido
2. Ir al **Tab "Agregar Items"**
3. Completar formulario:
   - **Opción Servicio ID:** UUID de la opción del catálogo (obligatorio)
   - **Cantidad:** Número de unidades (default 1)
   - **Precio Unitario:** Monto en decimales (opcional)
   - **Nombre del Servicio:** Descripción legible (opcional)
4. Hacer clic en **"Agregar Item"**
5. ✅ **Resultado:** Item agregado al pedido, monto_total recalculado

**Ejemplo de payload enviado:**
```json
{
  "items": [{
    "opcion_servicio_id": "opt_foto_basica",
    "cantidad": 2,
    "precio_unit_vigente": 150.00,
    "nombre_servicio": "Fotografía Básica - 4 horas"
  }]
}
```

### 5. Eliminar Items de un Pedido 🆕

1. Hacer clic en **"Items"** en la tarjeta del pedido
2. Ir al **Tab "Eliminar Items"**
3. Ver lista de items con sus IDs (copia el ID completo)
4. Ingresar IDs separados por coma en el input:
   ```
   item-uuid-1, item-uuid-2, item-uuid-3
   ```
5. Hacer clic en **"Eliminar Items Seleccionados"**
6. ✅ **Resultado:** Items eliminados, monto_total recalculado

### 6. Ver Detalle Completo de un Pedido

Al hacer clic en **"Detalle"**, el modal muestra:

**Información Principal:**
- ID del pedido
- Cliente (email)
- Estado (badge de color)
- Fecha evento, Hora inicio, Ubicación

**Información Económica:**
- Monto Total
- Fecha creación
- Última actualización

**Tabla de Items:** (nueva estructura mejorada)
| ID | Servicio/Opción | Cant. | Precio Unit. | Subtotal |
|----|-----------------|-------|--------------|----------|
| `abc123...` | Fotografía Básica<br><small>Opción: opt_foto...</small> | 2 | S/ 150.00 | S/ 300.00 |
| **Total** | | | | **S/ 300.00** |

**Proveedores Involucrados:**
- Lista de proveedores asignados (si aplica)

**Acciones Rápidas:**
- Dropdown + Botón "Aplicar Estado"
- Botón "Asignar Proveedor"
- Botón "Gestionar Items"

---

## 🎨 Sistema de Notificaciones

Todas las operaciones muestran **notificaciones toast** en la esquina superior derecha:

- ✅ **Verde (Success):** Operación exitosa
- ❌ **Rojo (Error):** Error en la operación
- ℹ️ **Azul (Info):** Información general
- ⚠️ **Amarillo (Warning):** Advertencia

Ejemplos:
- ✅ "Estado del pedido actualizado correctamente"
- ✅ "Proveedor asignado exitosamente a 3 item(s)"
- ❌ "Transición no permitida: BORRADOR → CERRADO"
- ❌ "Solo se pueden asignar proveedores a pedidos APROBADOS"

---

## 🔍 Tips y Mejores Prácticas

### Para ADMINS

1. **Flujo recomendado de estados:**
   ```
   DRAFT → cotizar → COTIZADO → aprobar → APROBADO → 
   asignar proveedores → ASIGNADO → cerrar → CERRADO
   ```

2. **Antes de asignar proveedores:**
   - Asegurarse de que el pedido esté APROBADO
   - Verificar que los items tengan opcion_servicio_id válido
   - Tener el UUID del proveedor disponible

3. **Al agregar items:**
   - Siempre incluir `precio_unit_vigente` para cálculo correcto del subtotal
   - Usar `nombre_servicio` para mejor legibilidad

4. **Uso de filtros:**
   - Combinar filtros de estado + cliente para búsquedas rápidas
   - Usar "Limpiar filtros" para resetear todo de una vez

### Para CLIENTES

1. **Al crear pedidos:**
   - Revisar bien la fecha/hora/ubicación antes de confirmar
   - El pedido inicia en BORRADOR, esperar a que ADMIN lo cotice

2. **Seguimiento:**
   - Revisar regularmente la sección "Mis Pedidos"
   - Estados Confirmados = 2 (APROBADO) + 3 (ASIGNADO) + 4 (CERRADO)

---

## 🚨 Solución de Problemas Comunes

### Error: "Transición no permitida"
**Causa:** Intentas cambiar a un estado que no sigue el flujo válido.
**Solución:** Revisar la tabla de transiciones válidas arriba.

### Error: "Solo se pueden asignar proveedores a pedidos APROBADOS"
**Causa:** El pedido no está en estado 2 (APROBADO).
**Solución:** Cambiar primero el estado a APROBADO.

### Error: "Error al asignar proveedor"
**Causa:** Proveedor ID inválido o items no seleccionados.
**Solución:**
- Verificar que el UUID del proveedor sea correcto
- Asegurarse de marcar al menos un checkbox de item

### No se ven los items al abrir modal de asignación
**Causa:** El pedido no tiene items cargados.
**Solución:**
- Usar primero "Gestionar Items" → "Agregar Items"
- O crear el pedido desde un paquete que incluya items

### Monto total no se actualiza
**Causa:** Los items no tienen `precio_unitario` o `subtotal`.
**Solución:**
- Al agregar items, siempre incluir `precio_unit_vigente`
- El backend calcula `subtotal = cantidad * precio_unitario`

---

## 📡 Endpoints Utilizados (Referencia Técnica)

### Cliente
- `POST /v1/contratacion/pedidos` - Crear pedido
- `GET /v1/contratacion/pedidos/mios` - Mis pedidos
- `GET /v1/contratacion/pedidos/{id}` - Detalle

### Admin
- `GET /v1/contratacion/admin/pedidos` - Todos los pedidos
- `GET /v1/contratacion/admin/pedidos/{id}` - Detalle admin
- `PATCH /v1/contratacion/admin/pedidos/{id}` - Cambiar estado
  - Body: `{"estado": 1}` (int)
- `POST /v1/contratacion/admin/pedidos/{id}/items` - Agregar items
  - Body: `{"items": [{"opcion_servicio_id": "...", "cantidad": 1, ...}]}`
- `DELETE /v1/contratacion/admin/pedidos/{id}/items` - Eliminar items
  - Body: `{"item_ids": ["id1", "id2"]}`
- `POST /v1/contratacion/admin/pedidos/{id}/asignar-proveedor` - Asignar proveedor
  - Body: `{"item_pedido_ids": ["id1"], "proveedor_id": "uuid"}`

---

## 🎓 Conceptos Clave

### Estados de Pedido
| Código | Nombre | Descripción |
|--------|--------|-------------|
| 0 | BORRADOR | Pedido recién creado, sin cotización |
| 1 | COTIZADO | Admin asignó precios, pendiente aprobación |
| 2 | APROBADO | Cliente/Admin aprobó la cotización |
| 3 | ASIGNADO | Proveedores asignados a todos los items |
| 4 | CERRADO | Pedido finalizado, evento completado |
| 5 | CANCELADO | Pedido cancelado (desde cualquier estado) |

### Items de Pedido
Cada pedido contiene N items, donde cada item representa:
- Un servicio/opción específica del catálogo
- Cantidad de unidades
- Precio unitario vigente al momento de creación
- Subtotal calculado (cantidad × precio_unitario)

Los items pueden ser de tipo:
- `SERVICIO`: Servicios individuales
- `PAQUETE`: Items provenientes de un paquete predefinido

---

## 📞 Soporte

Para issues o mejoras, revisar:
- `CHANGELOG.md` - Historial completo de cambios
- `README.md` - Documentación del proyecto
- Logs del navegador (F12) para errores técnicos
