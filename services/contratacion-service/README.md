# Contratación Service

**Versión**: 1.0.0  
**Estado**: ✅ 100% Funcional  
**Puerto**: 8040  
**Base de Datos**: ev_contratacion

Este microservicio gestiona el ciclo completo de pedidos (contrataciones) de eventos, desde la creación hasta la asignación de proveedores.

---

## 🎯 Responsabilidades

- ✅ Creación de pedidos (desde paquetes o custom)
- ✅ Consulta de pedidos por cliente
- ✅ Gestión de estados de pedido
- ✅ Asignación de proveedores a items
- ✅ Creación de reservas permanentes
- ✅ Integración con Proveedores Service
- ✅ Validación de permisos por rol

---

## 🏗️ Arquitectura Hexagonal

```
contratacion-service/
├── app/
│   ├── domain/                 # Entidades (Pedido, Item, Reserva)
│   ├── application/            # Casos de uso
│   │   ├── crear_pedido.py
│   │   ├── listar_pedidos.py
│   │   ├── cambiar_estado.py
│   │   └── admin_asignar_proveedor.py
│   ├── infrastructure/         # Adaptadores (MySQL, HTTP)
│   └── entrypoints/            # API REST (FastAPI)
│
└── test/                       # Tests
```

---

## 🔌 Endpoints

### Cliente (Autenticado)

#### `POST /contratacion/pedidos`
Crea un nuevo pedido.

**Opción 1 - Desde Paquete**:
```json
{
  "paquete_id": "uuid",
  "tipo_evento_id": "uuid",
  "fecha_evento": "2026-01-26",
  "hora_inicio": "18:00:00",
  "hora_fin": "23:00:00",
  "num_personas": 100,
  "ubicacion": "Lima Centro"
}
```

**Opción 2 - Personalizado**:
```json
{
  "tipo_evento_id": "uuid",
  "fecha_evento": "2026-01-26",
  "hora_inicio": "18:00:00",
  "hora_fin": "23:00:00",
  "num_personas": 100,
  "ubicacion": "Lima Centro",
  "items": [
    {
      "opcion_servicio_id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
      "cantidad": 1,
      "precio_unitario": 1500.00
    }
  ]
}
```

**Response** (201):
```json
{
  "id": "bddf0b63-4e55-4db6-9a16-cb7c2fabebc5",
  "estado": null,
  "monto_total": 1500.0,
  "fecha_evento": "2026-01-26"
}
```

#### `GET /contratacion/pedidos/mios`
Lista pedidos del cliente autenticado.

**Query Parameters**:
- `skip`: Paginación (default: 0)
- `limit`: Límite (default: 50)

**Response**:
```json
{
  "total": 5,
  "pedidos": [
    {
      "id": "uuid",
      "fecha_evento": "2026-01-26",
      "monto_total": 1500.0,
      "estado": "DRAFT"
    }
  ]
}
```

#### `GET /contratacion/pedidos/{id}`
Detalle de un pedido (solo si es del cliente).

**Response**:
```json
{
  "pedido": "uuid",
  "items": 1,
  "reservas": 0,
  "estado_nombre": "DRAFT",
  "monto_total": 1500.0
}
```

---

### Admin (Requiere rol ADMIN)

#### `GET /contratacion/admin/pedidos`
Lista todos los pedidos del sistema.

**Query Parameters**:
- `status`: Filtrar por estado (0=DRAFT, 1=COTIZADO, 2=APROBADO, 3=ASIGNADO)
- `skip`: Paginación
- `limit`: Límite

**Response**:
```json
{
  "total": 100,
  "pedidos": [
    {
      "id": "uuid",
      "cliente_id": "uuid",
      "estado": "APROBADO",
      "monto_total": 8500.0
    }
  ]
}
```

#### `GET /contratacion/admin/pedidos/{id}`
Detalle completo de un pedido (sin validación de ownership).

**Response**:
```json
{
  "id": "uuid",
  "cliente_id": "uuid",
  "estado": "APROBADO",
  "items": [
    {
      "id": "uuid",
      "opcion_servicio_id": "uuid",
      "cantidad": 1,
      "precio_unitario": 1500.0
    }
  ],
  "reservas": []
}
```

#### `PATCH /contratacion/admin/pedidos/{id}`
Cambia el estado de un pedido.

**Request**:
```json
{
  "estado": 1
}
```

**Estados Válidos**:
- `0`: DRAFT
- `1`: COTIZADO
- `2`: APROBADO
- `3`: ASIGNADO (automático al asignar todos los proveedores)
- `4`: CONFIRMADO
- `5`: CANCELADO

**Response** (200):
```json
{
  "nuevo_estado": 1
}
```

#### `POST /contratacion/admin/pedidos/{id}/asignar-proveedor`
Asigna un proveedor a un item del pedido.

**Request**:
```json
{
  "proveedor_id": "cccccccc-3333-4444-5555-cccccccccccc",
  "item_pedido_id": "uuid",
  "opcion_servicio_id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
  "fecha_inicio": "2026-01-26T18:00:00",
  "fecha_fin": "2026-01-26T23:00:00",
  "monto": 1500.00
}
```

**Response** (201):
```json
{
  "pedido_id": "uuid",
  "reserva_id": "981ed60d-8ecb-43c2-91aa-a21f0e1fdc2f",
  "estado": null
}
```

**Workflow Interno**:
1. Valida que pedido esté en estado APROBADO (2)
2. Valida que item exista y no tenga reserva previa
3. Llama a Proveedores Service para crear hold temporal
4. Si hold exitoso, confirma el hold
5. Crea reserva permanente en base de datos local
6. Si todos los items tienen proveedor, cambia estado a ASIGNADO (3)

**Validaciones**:
- ✅ Pedido debe estar APROBADO
- ✅ Item no debe tener reserva previa
- ✅ Proveedor debe estar disponible
- ✅ Hold debe crearse exitosamente
- ✅ Hold debe confirmarse exitosamente

**Errores**:
- `400`: Pedido no está en estado APROBADO
- `404`: Item no encontrado
- `409`: Item ya tiene proveedor asignado
- `503`: Error al comunicarse con Proveedores Service

---

## 🔄 Integración con Proveedores Service

### Flujo de Asignación

```
1. Admin llama POST /admin/pedidos/{id}/asignar-proveedor
   ↓
2. Contratación → Proveedores: POST /internal/holds
   ← Response: {hold_id, estado: ACTIVO}
   ↓
3. Contratación → Proveedores: PATCH /internal/holds/{id}/confirm
   ← Response: {estado: CONFIRMADO}
   ↓
4. Contratación crea Reserva permanente
   ↓
5. Contratación retorna reserva_id al Admin
```

### Configuración de Comunicación

```python
# URL del servicio de proveedores
PROVEEDORES_SERVICE_URL = "http://127.0.0.1:8030/proveedores"

# Token de autenticación inter-servicios
INTERNAL_SERVICE_TOKEN = "dev-internal-token-change-in-production"
```

---

## 📊 Estados de Pedido

| Estado | Código | Descripción | Puede Cambiar A |
|--------|--------|-------------|----------------|
| DRAFT | 0 | Pedido creado | COTIZADO (1) |
| COTIZADO | 1 | Precio calculado | APROBADO (2), CANCELADO (5) |
| APROBADO | 2 | Aprobado por admin | ASIGNADO (3), CANCELADO (5) |
| ASIGNADO | 3 | Proveedores asignados | CONFIRMADO (4), CANCELADO (5) |
| CONFIRMADO | 4 | Pedido confirmado | - |
| CANCELADO | 5 | Pedido cancelado | - |

---

## 🚀 Ejecución

```powershell
cd services/contratacion-service
.\run.bat
```

Servicio disponible en `http://localhost:8040`

---

## 🧪 Scripts de Utilidad

```powershell
# Limpiar reservas de prueba
python tools/clean_all_reservas.py

# Verificar reservas activas
python tools/check_reservas.py

# Test de asignación de proveedor
python tools/test_asignar_proveedor_debug.py
```

---

## 📝 Notas Técnicas

### Cálculo de Monto Total

El monto total se calcula automáticamente:
```python
monto_total = sum(item.cantidad * item.precio_unitario for item in items)
```

### Validación de Ownership

Clientes solo pueden ver sus propios pedidos:
```python
if user.role == "CLIENTE" and pedido.cliente_id != user.id:
    raise HTTPException(403, "No tienes permisos")
```

### Transacciones

Las operaciones críticas usan transacciones de BD para mantener consistencia.

---

**Última Actualización**: 27 de Noviembre, 2025