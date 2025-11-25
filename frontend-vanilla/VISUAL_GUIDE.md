# 🎨 Frontend - Guía Visual de Mejoras

## 📸 Antes vs Después

### Vista de Contratación (Admin)

#### ❌ ANTES (Phase 2)
```
┌─────────────────────────────────────────┐
│  Mis Pedidos                            │
├─────────────────────────────────────────┤
│  📋 Lista simple de pedidos             │
│  - Solo del usuario actual              │
│  - Sin filtros                          │
│  - Sin estadísticas                     │
│  - Solo lectura                         │
└─────────────────────────────────────────┘
```

#### ✅ DESPUÉS (Phase 3)
```
┌─────────────────────────────────────────────────────────────┐
│  Gestión de Pedidos - ADMIN                                 │
├─────────────────────────────────────────────────────────────┤
│  📊 ESTADÍSTICAS GLOBALES                                   │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │ 45   │ │  8   │ │ 12   │ │ 15   │ │  7   │ │  3   │  │
│  │Total │ │Cotiz.│ │Aprob.│ │Asig. │ │Cerr. │ │Canc. │  │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘  │
├─────────────────────────────────────────────────────────────┤
│  🔍 FILTROS                                                 │
│  Estado: [Todos ▼] | ID: [_______] | Cliente: [________]  │
│  [Limpiar] [Aplicar]                                       │
├─────────────────────────────────────────────────────────────┤
│  📋 TODOS LOS PEDIDOS DEL SISTEMA                          │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ [💰 Cotizado] pedido-abc123                         │  │
│  │ Cliente: cliente@eventos.pe                         │  │
│  │ Evento: 2025-12-25 | Monto: S/ 8,300.00            │  │
│  │ Estado: [Cotizado ▼] [👁️ Detalle] [👥 Asignar] [➕ Items] │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ [✅ Aprobado] pedido-def456                         │  │
│  │ ...                                                  │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

### Modal de Detalle de Pedido

#### ❌ ANTES
```
┌──────────────────────────────────────┐
│  Detalle del Pedido                  │
├──────────────────────────────────────┤
│  ID: pedido-abc123                   │
│  Estado: Aprobado                    │
│  Cliente: cliente@eventos.pe         │
│  Total: S/ 8,300.00                  │
│                                      │
│  [Cerrar]                            │
└──────────────────────────────────────┘
```

#### ✅ DESPUÉS
```
┌────────────────────────────────────────────────────────────┐
│  Detalle del Pedido - ADMIN                                │
├────────────────────────────────────────────────────────────┤
│  📋 INFORMACIÓN PRINCIPAL                                  │
│  ID: pedido-abc123                                         │
│  Cliente: cliente@eventos.pe                               │
│  Estado: [✅ Aprobado]                                     │
│  Fecha: 2025-12-25 | Hora: 18:00 | Ubicación: Lima        │
├────────────────────────────────────────────────────────────┤
│  💰 INFORMACIÓN ECONÓMICA                                  │
│  Total: S/ 8,300.00                                        │
│  Creado: 2025-11-20 | Actualizado: 2025-11-21             │
├────────────────────────────────────────────────────────────┤
│  📦 ITEMS DEL PEDIDO                                       │
│  ┌───────┬────────────────────┬──────┬───────────┬────────┐│
│  │ ID    │ Servicio/Opción    │ Cant │ P.Unit    │ Subtot ││
│  ├───────┼────────────────────┼──────┼───────────┼────────┤│
│  │abc123 │ Fotografía Básica  │  2   │ S/ 150.00 │S/ 300.│││
│  │       │ Opción: opt_foto...│      │           │        ││
│  ├───────┼────────────────────┼──────┼───────────┼────────┤│
│  │def456 │ Catering Premium   │  50  │ S/ 80.00  │S/4,000││
│  │       │ Opción: opt_cater..│      │           │        ││
│  ├───────┴────────────────────┴──────┴───────────┼────────┤│
│  │                               TOTAL:           │S/8,300 ││
│  └─────────────────────────────────────────────────────────┘│
├────────────────────────────────────────────────────────────┤
│  ⚡ ACCIONES RÁPIDAS                                       │
│  Estado: [Aprobado ▼] [Aplicar Estado]                    │
│  [👥 Asignar Proveedor] [➕ Gestionar Items]              │
├────────────────────────────────────────────────────────────┤
│  [Cerrar]                                                  │
└────────────────────────────────────────────────────────────┘
```

---

### Modal de Asignación de Proveedores 🆕

```
┌───────────────────────────────────────────────────────────┐
│  👥 Asignar Proveedor a Items                             │
├───────────────────────────────────────────────────────────┤
│  ℹ️  Pedido: pedido-abc123 | Estado: [✅ Aprobado]       │
├───────────────────────────────────────────────────────────┤
│  📦 ITEMS A ASIGNAR                                       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ ☑️ Fotografía Básica (2 x S/ 150.00)               │ │
│  │ ☑️ Catering Premium (50 x S/ 80.00)                │ │
│  │ ☐ Decoración Floral (1 x S/ 500.00)                │ │
│  └─────────────────────────────────────────────────────┘ │
├───────────────────────────────────────────────────────────┤
│  👤 PROVEEDOR                                             │
│  Proveedor ID: [______________________________]           │
│  💡 Ingresa el UUID del proveedor                         │
├───────────────────────────────────────────────────────────┤
│  ⚠️  Solo pedidos APROBADO (2) pueden asignar proveedores│
├───────────────────────────────────────────────────────────┤
│  [❌ Cancelar] [✅ Confirmar Asignación]                 │
└───────────────────────────────────────────────────────────┘
```

---

### Modal de Gestión de Items 🆕

```
┌───────────────────────────────────────────────────────────┐
│  📝 Gestión de Items del Pedido                           │
├───────────────────────────────────────────────────────────┤
│  ℹ️  Pedido: pedido-abc123                               │
├───────────────────────────────────────────────────────────┤
│  [➕ Agregar Items] [🗑️ Eliminar Items]                  │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  ━━━ TAB: AGREGAR ITEMS ━━━                              │
│                                                           │
│  Opción Servicio ID:                                      │
│  [_________________________________]                      │
│                                                           │
│  Cantidad: [___2___]  Precio Unitario: [___150.00____]   │
│                                                           │
│  Nombre del Servicio:                                     │
│  [Fotografía Básica - 4 horas_______]                    │
│                                                           │
│  [➕ Agregar Item]                                        │
│                                                           │
│  ━━━ TAB: ELIMINAR ITEMS ━━━                             │
│                                                           │
│  Items actuales:                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Fotografía Básica                                   │ │
│  │ ID: item-abc123-456-789                             │ │
│  │ Cant: 2 | Precio: S/ 150.00                         │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │ Catering Premium                                    │ │
│  │ ID: item-def456-789-012                             │ │
│  │ ...                                                  │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  IDs a eliminar (separados por coma):                    │
│  [item-abc123-456-789, item-def456-789-012___]           │
│                                                           │
│  [🗑️ Eliminar Items Seleccionados]                      │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

---

### Sistema de Notificaciones Toast 🆕

```
                                           ┌────────────────────┐
                                           │ ✅ Operación       │
                                           │    exitosa         │
                                           │    [X]             │
                                           └────────────────────┘
                                           
                                           ┌────────────────────┐
                                           │ ❌ Error al        │
                                           │    procesar        │
                                           │    [X]             │
                                           └────────────────────┘
                                           
                                           ┌────────────────────┐
                                           │ ⚠️  Transición no  │
                                           │    permitida       │
                                           │    [X]             │
                                           └────────────────────┘
```

---

## 🎨 Paleta de Colores por Estado

```
┌────────────────────────────────────────────────┐
│  Estados de Pedido                             │
├────────────────────────────────────────────────┤
│  [📝 Borrador]    ← Gris    (bg-secondary)   │
│  [💰 Cotizado]    ← Azul    (bg-info)        │
│  [✅ Aprobado]    ← Verde   (bg-success)     │
│  [👥 Asignado]    ← Primario (bg-primary)    │
│  [🏁 Cerrado]     ← Negro   (bg-dark)        │
│  [❌ Cancelado]   ← Rojo    (bg-danger)      │
└────────────────────────────────────────────────┘
```

---

## 🔄 Flujo Visual: Cambiar Estado

```
                    INICIO
                      ↓
        ┌─────────────────────────┐
        │ Admin selecciona estado │
        │ en dropdown             │
        └─────────────────────────┘
                      ↓
        ┌─────────────────────────┐
        │ Validación client-side  │
        │ esTransicionValida()?   │
        └─────────────────────────┘
                ↓           ↓
            ✅ SÍ         ❌ NO
                ↓           ↓
    ┌──────────────┐   ┌──────────────┐
    │ Envía PATCH  │   │ Toast ERROR  │
    │ al backend   │   │ + Revertir   │
    └──────────────┘   │ selector     │
          ↓            └──────────────┘
    ┌──────────────┐          ↓
    │ Backend OK?  │        FIN
    └──────────────┘
        ↓       ↓
      ✅ SÍ   ❌ NO
        ↓       ↓
    ┌────────┐ ┌────────┐
    │ Toast  │ │ Toast  │
    │SUCCESS │ │ ERROR  │
    └────────┘ └────────┘
        ↓
    ┌────────────┐
    │ Recargar   │
    │ pedidos    │
    └────────────┘
        ↓
      FIN
```

---

## 🔄 Flujo Visual: Asignar Proveedor

```
                    INICIO
                      ↓
        ┌─────────────────────────┐
        │ Admin click "Asignar"   │
        └─────────────────────────┘
                      ↓
        ┌─────────────────────────┐
        │ Cargar pedido completo  │
        │ (adminDetallePedido)    │
        └─────────────────────────┘
                      ↓
        ┌─────────────────────────┐
        │ ¿Estado = APROBADO (2)? │
        └─────────────────────────┘
            ↓              ↓
          ✅ SÍ          ❌ NO
            ↓              ↓
    ┌──────────────┐  ┌────────────┐
    │ Abrir modal  │  │ Toast ERROR│
    │ con items    │  │ Solo APROB.│
    └──────────────┘  └────────────┘
            ↓              ↓
    ┌──────────────┐      FIN
    │ Seleccionar  │
    │ items +      │
    │ proveedor_id │
    └──────────────┘
            ↓
    ┌──────────────┐
    │ Confirmar    │
    └──────────────┘
            ↓
    ┌──────────────┐
    │ POST asignar │
    │ proveedor    │
    └──────────────┘
            ↓
    ┌──────────────┐
    │ Backend crea │
    │ holds +      │
    │ cambia estado│
    │ a ASIGNADO   │
    └──────────────┘
            ↓
    ┌──────────────┐
    │ Toast SUCCESS│
    │ + Recargar   │
    └──────────────┘
            ↓
          FIN
```

---

## 📊 Estadísticas Visuales

### ANTES
```
┌────────────────┐
│ Mis Pedidos: 5 │
└────────────────┘
```

### DESPUÉS (Cliente)
```
┌──────────┬──────────────┬─────────────┬─────────────┐
│ Total: 5 │ Confirmados: │ Pendientes: │ Cancelados: │
│          │      2       │      2      │      1      │
└──────────┴──────────────┴─────────────┴─────────────┘
```

### DESPUÉS (Admin)
```
┌────────┬──────────┬──────────┬──────────┬─────────┬────────────┐
│Total:45│Cotizado:8│Aprobado:│Asignado:│Cerrado:7│Cancelado: 3│
│        │          │   12    │   15    │         │            │
└────────┴──────────┴──────────┴──────────┴─────────┴────────────┘
```

---

## 🎯 Interacciones de Usuario

### ADMIN: Gestionar Pedido Completo

```
1. Login como ADMIN
   ↓
2. Ir a /contratacion → Ver todos los pedidos
   ↓
3. Filtrar por estado BORRADOR
   ↓
4. Seleccionar pedido → Cambiar a COTIZADO
   ↓
5. Cambiar a APROBADO
   ↓
6. Click "Asignar" → Seleccionar items + proveedor_id
   ↓
7. Confirmar → Estado cambia a ASIGNADO
   ↓
8. Click "Items" → Agregar item adicional
   ↓
9. Ver detalle → Verificar monto_total actualizado
   ↓
10. Cambiar a CERRADO
```

**Total de clicks:** 10-12 (experiencia fluida)

---

## 💡 Tips de Navegación

### Atajos Visuales

```
🔵 Azul    = Información / Cotizado
🟢 Verde   = Éxito / Aprobado
🔴 Rojo    = Error / Cancelado
⚫ Negro   = Cerrado (final)
🟡 Amarillo = Advertencia
⚪ Gris    = Borrador / Neutral
```

### Iconos de Acción

```
👁️  = Ver detalle
👥 = Asignar proveedor
➕ = Agregar items
🗑️ = Eliminar items
🔄 = Recargar / Actualizar
🔍 = Buscar / Filtrar
✅ = Confirmar
❌ = Cancelar
```

---

## 📱 Responsive Design

### Desktop (>992px)
```
┌────────────────────────────────────────────────┐
│  [Estadísticas en fila horizontal - 6 cards]  │
│  [Filtros en una sola fila]                   │
│  [Tarjetas de pedidos en 2 columnas]          │
└────────────────────────────────────────────────┘
```

### Tablet (768px - 992px)
```
┌────────────────────────────┐
│  [Estadísticas 3x2 grid]  │
│  [Filtros apilados]       │
│  [Pedidos en 1 columna]   │
└────────────────────────────┘
```

### Mobile (<768px)
```
┌──────────────────┐
│  [Stats stack]  │
│  [Filtros tabs] │
│  [Pedidos list] │
└──────────────────┘
```

---

**🎨 Diseño:** Bootstrap 5.3.3  
**🎯 Enfoque:** Mobile-First + Progressive Enhancement  
**♿ Accesibilidad:** WCAG 2.1 Level AA (badges, labels, ARIA)
