# Proveedores Service

**Versión**: 1.0.0  
**Estado**: ✅ 100% Funcional  
**Puerto**: 8030  
**Base de Datos**: ev_proveedores

Este microservicio gestiona proveedores, su disponibilidad y las reservas temporales (holds) de recursos.

---

## 🎯 Responsabilidades

- ✅ Gestión de proveedores y sus habilidades
- ✅ Búsqueda de proveedores disponibles
- ✅ Creación de holds temporales (reservas preliminares)
- ✅ Confirmación y liberación de holds
- ✅ Validación de conflictos de agenda
- ✅ Idempotencia con correlation_id
- ✅ Calendario de descansos

---

## 🏗️ Arquitectura Hexagonal

```
proveedores-service/
├── app/
│   ├── domain/                 # Entidades (Proveedor, Hold)
│   ├── application/            # Casos de uso
│   ├── infrastructure/         # Adaptadores (MySQL)
│   └── entrypoints/            # API REST (FastAPI)
│
└── test/                       # Tests
```

---

## 🔌 Endpoints

### Públicos

#### `GET /proveedores/health`
Health check.

#### `GET /proveedores/proveedores`
Lista todos los proveedores.

**Response**:
```json
{
  "total": 50,
  "proveedores": [
    {
      "id": "cccccccc-3333-4444-5555-cccccccccccc",
      "nombre": "Proveedor Demo",
      "email": "proveedor@eventos.pe",
      "telefono": "+51 999999999"
    }
  ]
}
```

#### `GET /proveedores/proveedores/disponibles`
Busca proveedores disponibles.

**Query Parameters**:
- `servicio_id`: ID del servicio
- `opcion_servicio_id`: ID de la opción (opcional)
- `fecha_evento`: Fecha del evento (YYYY-MM-DD)
- `hora_inicio`: Hora de inicio (HH:MM:SS)
- `hora_fin`: Hora de fin (HH:MM:SS)

**Response**:
```json
{
  "proveedores": [
    {
      "id": "uuid",
      "nombre": "Proveedor 1",
      "habilidad_nivel": 5,
      "disponible": true
    }
  ]
}
```

---

### Internos (Requieren X-Service-Token)

Estos endpoints solo pueden ser llamados por otros servicios del sistema.

#### `POST /proveedores/internal/holds`
Crea un hold temporal.

**Headers**:
```
X-Service-Token: <internal-token>
```

**Request**:
```json
{
  "proveedor_id": "cccccccc-3333-4444-5555-cccccccccccc",
  "opcion_servicio_id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
  "fecha_inicio": "2026-01-26T18:00:00",
  "fecha_fin": "2026-01-26T23:00:00",
  "ttl_min": 15,
  "correlation_id": "unique-correlation-id"
}
```

**Response** (201):
```json
{
  "hold_id": "uuid",
  "proveedor_id": "uuid",
  "estado": "ACTIVO",
  "expira_en": "2026-01-26T18:15:00"
}
```

**Características**:
- ✅ **Idempotencia**: Si se envía el mismo `correlation_id`, devuelve el hold existente
- ✅ **TTL**: Hold expira automáticamente después de `ttl_min` minutos
- ✅ **Validación**: Detecta conflictos con otros holds y reservas confirmadas
- ✅ **Exclusión Propia**: No considera conflicto si es el mismo `correlation_id`

**Errores**:
- `409 Conflict`: Proveedor no disponible en ese horario
- `403 Forbidden`: Token de servicio inválido
- `422 Unprocessable Entity`: Datos inválidos

#### `PATCH /proveedores/internal/holds/{id}/confirm`
Confirma un hold (lo convierte en reserva permanente).

**Response** (200):
```json
{
  "hold_id": "uuid",
  "estado": "CONFIRMADO"
}
```

#### `DELETE /proveedores/internal/holds/{id}`
Libera/cancela un hold.

**Response** (204): No Content

#### `GET /proveedores/internal/holds/{id}`
Obtiene el estado de un hold.

**Response** (200):
```json
{
  "id": "uuid",
  "proveedor_id": "uuid",
  "estado": "ACTIVO",
  "expira_en": "2026-01-26T18:15:00",
  "created_at": "2026-01-26T18:00:00"
}
```

---

## 🔐 Seguridad

### Endpoints Internos

Los endpoints `/internal/*` están protegidos con un token de servicio:

```python
INTERNAL_SERVICE_TOKEN = "dev-internal-token-change-in-production"
```

**Middleware de validación**:
- Requiere header `X-Service-Token`
- Compara con token configurado
- Retorna `403 Forbidden` si no coincide

---

## 🎯 Validación de Disponibilidad

### Lógica de Conflictos

Un proveedor NO está disponible si:
1. Tiene un **hold activo** en el rango de fechas (excepto mismo `correlation_id`)
2. Tiene una **reserva confirmada** en el rango de fechas
3. Tiene un **período de descanso** programado

### Idempotencia

Cuando se crea un hold con un `correlation_id` ya existente:
- ✅ Devuelve el hold original (no crea duplicado)
- ✅ Actualiza el TTL del hold existente
- ✅ Evita conflictos con el mismo request

---

## 📊 Datos Disponibles

- **Proveedores**: 50
- **Habilidades**: 150+ (relación proveedor-servicio)
- **Holds Activos**: Variable (se limpian automáticamente)

---

## 🚀 Ejecución

```powershell
cd services/proveedores-service
.\run.bat
```

Servicio disponible en `http://localhost:8030`

---

## 🧪 Scripts de Utilidad

```powershell
# Limpiar holds de prueba
python tools/clean_all_holds.py

# Verificar holds activos
python tools/check_holds.py

# Validar proveedor específico
python tools/check_proveedor_completo.py
```

---

**Última Actualización**: 27 de Noviembre, 2025