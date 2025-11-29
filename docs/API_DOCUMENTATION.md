# Documentación API - Sistema Eventos Perú

**Versión**: 1.0.0  
**Fecha**: 27 de Noviembre, 2025  
**Arquitectura**: Hexagonal (Puertos y Adaptadores)  
**Autenticación**: JWT (HS256)

---

## Tabla de Contenidos

1. [Información General](#información-general)
2. [Servicio IAM](#servicio-iam-puerto-8010)
3. [Servicio Catálogo](#servicio-catálogo-puerto-8020)
4. [Servicio Proveedores](#servicio-proveedores-puerto-8030)
5. [Servicio Contratación](#servicio-contratación-puerto-8040)
6. [Códigos de Error](#códigos-de-error)
7. [Flujos de Negocio](#flujos-de-negocio)

---

## Información General

### Base URLs

```
IAM:           http://127.0.0.1:8010
Catálogo:      http://127.0.0.1:8020
Proveedores:   http://127.0.0.1:8030
Contratación:  http://127.0.0.1:8040
```

### Autenticación

Todos los endpoints protegidos requieren header:

```
Authorization: Bearer <JWT_TOKEN>
```

**Obtención de token**: `POST /iam/login`

### Roles de Usuario

- `ADMIN`: Acceso completo a endpoints administrativos
- `CLIENTE`: Acceso a endpoints de cliente (crear pedidos, consultar propios)

### Formato de Respuestas

**Éxito (200/201)**:
```json
{
  "campo1": "valor",
  "campo2": 123
}
```

**Error (4xx/5xx)**:
```json
{
  "detail": {
    "code": "ERROR_CODE",
    "message": "Descripción del error"
  }
}
```

---

## Servicio IAM (Puerto 8010)

### 1. Health Check

**Endpoint**: `GET /iam/health`  
**Autenticación**: No requiere  
**Descripción**: Verifica que el servicio está operativo

**Response 200**:
```json
{
  "status": "ok"
}
```

---

### 2. Login de Usuario

**Endpoint**: `POST /iam/login`  
**Autenticación**: No requiere  
**Descripción**: Autentica usuario y devuelve token JWT

**Request Body**:
```json
{
  "email": "admin@eventos.pe",
  "password": "Evoluti0n"
}
```

**Parámetros**:
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| email | string | Sí | Email del usuario |
| password | string | Sí | Contraseña en texto plano |

**Response 200**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 7200,
  "user": {
    "id": "ee111111-1111-4111-8111-aaaaaaaaaaa1",
    "email": "admin@eventos.pe",
    "nombre": "Administrador Sistema",
    "role": "ADMIN"
  }
}
```

**Errores**:
- `401`: Credenciales inválidas
- `403`: Usuario inactivo (status != 1)

**Casuísticas**:
- ✅ Login exitoso con credenciales válidas
- ❌ Email no existe
- ❌ Contraseña incorrecta
- ❌ Usuario deshabilitado (status = 0)
- ✅ Token expira después de 120 minutos (configurable)

---

### 3. Obtener Perfil del Usuario Actual

**Endpoint**: `GET /iam/me`  
**Autenticación**: Requerida (Bearer Token)  
**Descripción**: Devuelve información del usuario autenticado

**Headers**:
```
Authorization: Bearer <token>
```

**Response 200**:
```json
{
  "id": "ee000027-f34c-a703-8635-4305dedcb4c0",
  "email": "jorge.martinez711@eventos.pe",
  "nombre": "Juan Ortiz",
  "telefono": "+51 986001098",
  "role": "CLIENTE",
  "status": 1
}
```

**Errores**:
- `401`: Token inválido o expirado
- `404`: Usuario no encontrado (token válido pero usuario eliminado)

**Casuísticas**:
- ✅ Usuario autenticado obtiene su perfil
- ❌ Token expirado
- ❌ Token inválido (firma incorrecta)
- ❌ Token sin header Authorization

---

### 4. Listar Todos los Usuarios (Admin)

**Endpoint**: `GET /iam/admin/usuarios`  
**Autenticación**: Requerida (ADMIN)  
**Descripción**: Lista todos los usuarios del sistema

**Headers**:
```
Authorization: Bearer <admin_token>
```

**Query Parameters**:
| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| skip | integer | No | 0 | Número de registros a saltar |
| limit | integer | No | 100 | Máximo de registros a devolver |

**Response 200**:
```json
{
  "total": 152,
  "usuarios": [
    {
      "id": "ee111111-1111-4111-8111-aaaaaaaaaaa1",
      "email": "admin@eventos.pe",
      "nombre": "Administrador Sistema",
      "role": "ADMIN",
      "status": 1,
      "created_at": "2025-11-27T10:00:00"
    }
  ]
}
```

**Errores**:
- `403`: Usuario no es ADMIN

**Casuísticas**:
- ✅ Admin lista usuarios con paginación
- ❌ Cliente intenta acceder (403 Forbidden)
- ✅ Paginación correcta con skip/limit

---

## Servicio Catálogo (Puerto 8020)

### 1. Health Check

**Endpoint**: `GET /catalogo/health`  
**Autenticación**: No requiere  
**Descripción**: Verifica que el servicio está operativo

**Response 200**:
```json
{
  "status": "ok"
}
```

---

### 2. Listar Tipos de Eventos

**Endpoint**: `GET /catalogo/v1/tipos-evento`  
**Autenticación**: No requiere  
**Descripción**: Lista todos los tipos de eventos disponibles

**Query Parameters**:
| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| skip | integer | No | 0 | Offset para paginación |
| limit | integer | No | 100 | Límite de resultados |

**Response 200**:
```json
{
  "total": 10,
  "tipos_evento": [
    {
      "id": "11111111-1111-1111-1111-111111111111",
      "nombre": "Boda",
      "descripcion": "Ceremonias de matrimonio y recepciones",
      "icono": "💍",
      "activo": true
    }
  ]
}
```

**Casuísticas**:
- ✅ Lista todos los tipos activos
- ✅ Paginación funcional
- ✅ No requiere autenticación (catálogo público)

---

### 3. Listar Servicios

**Endpoint**: `GET /catalogo/v1/servicios`  
**Autenticación**: No requiere  
**Descripción**: Lista servicios con sus categorías

**Query Parameters**:
| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| categoria_id | string | No | - | Filtrar por categoría |
| skip | integer | No | 0 | Offset |
| limit | integer | No | 50 | Límite |

**Response 200**:
```json
{
  "total": 30,
  "servicios": [
    {
      "id": "aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa",
      "nombre": "Servicio Prueba Verificacion",
      "descripcion": "Servicio para verificar flujos E2E",
      "categoria_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "categoria_nombre": "Decoración",
      "activo": true,
      "opciones_count": 3
    }
  ]
}
```

**Casuísticas**:
- ✅ Lista todos los servicios
- ✅ Filtrado por categoría
- ✅ Incluye conteo de opciones por servicio

---

### 4. Obtener Detalle de Servicio

**Endpoint**: `GET /catalogo/v1/servicios/{servicio_id}`  
**Autenticación**: No requiere  
**Descripción**: Detalle completo de un servicio con sus opciones

**Path Parameters**:
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| servicio_id | string (UUID) | ID del servicio |

**Response 200**:
```json
{
  "servicio": {
    "id": "aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa",
    "nombre": "Servicio Prueba Verificacion",
    "descripcion": "Descripción detallada",
    "categoria_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "activo": true
  },
  "opciones": [
    {
      "id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
      "nombre": "Opción Premium",
      "descripcion": "Incluye XYZ",
      "precio_base": 1500.00,
      "moneda": "PEN",
      "unidad": "EVENTO",
      "disponible": true
    }
  ]
}
```

**Errores**:
- `404`: Servicio no encontrado

**Casuísticas**:
- ✅ Obtiene servicio con todas sus opciones
- ❌ ID inválido (404)
- ✅ Opciones incluyen precios y disponibilidad

---

### 5. Listar Paquetes

**Endpoint**: `GET /catalogo/v1/paquetes`  
**Autenticación**: No requiere  
**Descripción**: Lista paquetes predefinidos con servicios incluidos

**Query Parameters**:
| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| tipo_evento_id | string | No | - | Filtrar por tipo de evento |
| skip | integer | No | 0 | Offset |
| limit | integer | No | 20 | Límite |

**Response 200**:
```json
{
  "total": 16,
  "paquetes": [
    {
      "id": "3e9089dd-cba2-11f0-938d-10ffe062188c",
      "codigo": "PKG-038D07-152",
      "nombre": "Set Personalizado Único",
      "descripcion": "Paquete integral que incluye todos los servicios necesarios",
      "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
      "tipo_evento_nombre": "Boda",
      "precio_total": 8500.00,
      "moneda": "PEN",
      "activo": true,
      "items_count": 5
    }
  ]
}
```

**Casuísticas**:
- ✅ Lista paquetes con precios totales
- ✅ Filtrado por tipo de evento
- ✅ Incluye conteo de items por paquete

---

### 6. Obtener Detalle de Paquete

**Endpoint**: `GET /catalogo/v1/paquetes/{paquete_id}`  
**Autenticación**: No requiere  
**Descripción**: Detalle completo de paquete con items incluidos

**Path Parameters**:
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| paquete_id | string (UUID) | ID del paquete |

**Response 200**:
```json
{
  "paquete": {
    "id": "3e9089dd-cba2-11f0-938d-10ffe062188c",
    "codigo": "PKG-038D07-152",
    "nombre": "Set Personalizado Único",
    "descripcion": "Descripción completa",
    "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
    "precio_total": 8500.00,
    "activo": true
  },
  "items": [
    {
      "id": "item-uuid",
      "servicio_id": "servicio-uuid",
      "servicio_nombre": "Decoración Floral",
      "opcion_servicio_id": "opcion-uuid",
      "opcion_nombre": "Premium",
      "cantidad": 1,
      "precio_unitario": 2500.00,
      "proveedores_disponibles": 3
    }
  ]
}
```

**Errores**:
- `404`: Paquete no encontrado

**Casuísticas**:
- ✅ Obtiene paquete con todos sus items
- ✅ Muestra proveedores disponibles por item
- ❌ Paquete inactivo (404 o campo activo=false)

---

## Servicio Proveedores (Puerto 8030)

### 1. Health Check

**Endpoint**: `GET /proveedores/health`  
**Autenticación**: No requiere  
**Descripción**: Verifica que el servicio está operativo

**Response 200**:
```json
{
  "status": "ok"
}
```

---

### 2. Listar Proveedores

**Endpoint**: `GET /proveedores/proveedores`  
**Autenticación**: Requerida  
**Descripción**: Lista proveedores con filtros

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| servicio_id | string | No | - | Filtrar por servicio habilitado |
| skip | integer | No | 0 | Offset |
| limit | integer | No | 50 | Límite |

**Response 200**:
```json
{
  "total": 50,
  "proveedores": [
    {
      "id": "cccccccc-3333-4444-5555-cccccccccccc",
      "nombre": "Proveedor Prueba Verificacion",
      "email": "prueba@proveedor.local",
      "telefono": "+51 999000001",
      "rating_prom": 4.80,
      "status": 1,
      "servicios_habilitados": [
        {
          "servicio_id": "aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa",
          "nivel": 5
        }
      ]
    }
  ]
}
```

**Casuísticas**:
- ✅ Lista proveedores activos
- ✅ Filtrado por servicio específico
- ✅ Incluye nivel de habilidad por servicio (1-5)

---

### 2.5 Administración de Proveedores (Admin)

**Endpoint Base**: `/proveedores/v1/admin/proveedores`  
**Autenticación**: Requerida (Role: ADMIN)  
**Nota**: Los endpoints base no deben llevar slash final (`/`).

#### Listar Proveedores (Admin)
**Endpoint**: `GET /proveedores/v1/admin/proveedores`  
**Descripción**: Lista todos los proveedores para gestión administrativa.

#### Crear Proveedor
**Endpoint**: `POST /proveedores/v1/admin/proveedores`  
**Body**:
```json
{
  "nombre": "Nombre Proveedor",
  "email": "email@proveedor.com",
  "telefono": "999888777"
}
```

#### Actualizar Proveedor
**Endpoint**: `PUT /proveedores/v1/admin/proveedores/{id}`  
**Body**:
```json
{
  "nombre": "Nuevo Nombre",
  "email": "nuevo@email.com",
  "telefono": "999888777"
}
```

#### Eliminar Proveedor
**Endpoint**: `DELETE /proveedores/v1/admin/proveedores/{id}`  
**Response**: 204 No Content

---


### 3. Crear Hold Temporal (Interno)

**Endpoint**: `POST /proveedores/internal/holds`  
**Autenticación**: Service Token  
**Descripción**: Crea reserva temporal (hold) de proveedor

**Headers**:
```
X-Service-Token: dev-internal-token-change-in-production
```

**Request Body**:
```json
{
  "proveedor_id": "cccccccc-3333-4444-5555-cccccccccccc",
  "opcion_servicio_id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
  "inicio": "2026-01-11T19:00:00",
  "fin": "2026-01-11T23:00:00",
  "ttl_min": 30,
  "correlation_id": "pedido-xxx-item-yyy",
  "created_by": "contratacion-service"
}
```

**Parámetros**:
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| proveedor_id | string (UUID) | Sí | ID del proveedor |
| opcion_servicio_id | string (UUID) | Sí | Opción de servicio |
| inicio | datetime (ISO) | Sí | Fecha/hora inicio |
| fin | datetime (ISO) | Sí | Fecha/hora fin |
| ttl_min | integer | No (default: 30) | Minutos hasta expiración |
| correlation_id | string | No | ID para idempotencia |
| created_by | string | No | Servicio que crea el hold |

**Response 201**:
```json
{
  "id": "hold-uuid",
  "proveedor_id": "cccccccc-3333-4444-5555-cccccccccccc",
  "opcion_servicio_id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
  "inicio": "2026-01-11 19:00:00",
  "fin": "2026-01-11 23:00:00",
  "expira_en": "2025-11-27 13:30:00",
  "status": 0
}
```

**Errores**:
- `400`: Rango de tiempo inválido (fin <= inicio)
- `403`: Token de servicio inválido
- `409`: Proveedor no disponible (conflicto con otro hold/reserva/descanso)

**Casuísticas**:
- ✅ Hold creado correctamente
- ✅ **Idempotencia**: Múltiples llamadas con mismo correlation_id devuelven mismo hold
- ❌ Conflicto con hold activo existente
- ❌ Conflicto con reserva confirmada
- ❌ Conflicto con período de descanso del proveedor
- ✅ Hold expira automáticamente después de ttl_min

---

### 4. Confirmar Hold (Interno)

**Endpoint**: `PATCH /proveedores/internal/holds/{hold_id}/confirm`  
**Autenticación**: Service Token  
**Descripción**: Confirma hold temporal (status 0 → 1)

**Headers**:
```
X-Service-Token: dev-internal-token-change-in-production
```

**Path Parameters**:
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| hold_id | string (UUID) | ID del hold |

**Response 200**:
```json
{
  "id": "hold-uuid",
  "status": 1,
  "message": "Hold confirmado"
}
```

**Errores**:
- `403`: Token de servicio inválido
- `404`: Hold no encontrado
- `409`: Hold no está en estado activo (status != 0)
- `410`: Hold expirado

**Casuísticas**:
- ✅ Hold confirmado exitosamente
- ❌ Hold ya confirmado (409)
- ❌ Hold expirado (410)
- ❌ Hold liberado previamente (409)

---

### 5. Liberar Hold (Interno)

**Endpoint**: `DELETE /proveedores/internal/holds/{hold_id}`  
**Autenticación**: Service Token  
**Descripción**: Libera hold temporal (rollback/cancelación)

**Headers**:
```
X-Service-Token: dev-internal-token-change-in-production
```

**Path Parameters**:
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| hold_id | string (UUID) | ID del hold |

**Response 204**: No Content

**Errores**:
- `403`: Token de servicio inválido
- `404`: Hold no encontrado
- `409`: Hold en estado inválido

**Casuísticas**:
- ✅ Hold liberado correctamente
- ✅ **Idempotente**: Múltiples llamadas no generan error
- ✅ Libera disponibilidad del proveedor

---

## Servicio Contratación (Puerto 8040)

### 1. Health Check

**Endpoint**: `GET /contratacion/health`  
**Autenticación**: No requiere  
**Descripción**: Verifica que el servicio está operativo

**Response 200**:
```json
{
  "status": "ok"
}
```

---

### 2. Crear Pedido (Cliente)

**Endpoint**: `POST /contratacion/pedidos`  
**Autenticación**: Requerida (CLIENTE o ADMIN)  
**Descripción**: Cliente crea pedido personalizado con items

**Headers**:
```
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
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
  ],
  "notas": "Evento formal"
}
```

**Parámetros**:
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| tipo_evento_id | string (UUID) | Sí | Tipo de evento (Boda, XV años, etc) |
| fecha_evento | date (YYYY-MM-DD) | Sí | Fecha del evento |
| hora_inicio | time (HH:MM:SS) | Sí | Hora de inicio |
| hora_fin | time (HH:MM:SS) | Sí | Hora de fin |
| num_personas | integer | Sí | Número de asistentes |
| ubicacion | string | Sí | Lugar del evento |
| items | array | Sí | Items del pedido (min: 1) |
| items[].opcion_servicio_id | string (UUID) | Sí | Opción de servicio |
| items[].cantidad | integer | Sí | Cantidad (default: 1) |
| items[].precio_unitario | decimal | Sí | Precio unitario |
| notas | string | No | Observaciones adicionales |

**Response 201**:
```json
{
  "id": "pedido-uuid",
  "cliente_id": "cliente-uuid",
  "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
  "fecha_evento": "2026-01-26",
  "status": 0,
  "monto_total": 1500.00,
  "moneda": "PEN",
  "created_at": "2025-11-27T12:00:00"
}
```

**Errores**:
- `400`: Datos inválidos (items vacío, fechas inválidas)
- `401`: No autenticado
- `404`: tipo_evento_id o opcion_servicio_id no existen

**Casuísticas**:
- ✅ Pedido creado en estado DRAFT (status=0)
- ✅ Monto total calculado automáticamente
- ✅ Cliente ID extraído del token JWT
- ❌ Items vacío (400)
- ❌ Fecha evento en el pasado (400)
- ✅ Múltiples items en un pedido

---

### 3. Listar Mis Pedidos (Cliente)

**Endpoint**: `GET /contratacion/pedidos/mios`  
**Autenticación**: Requerida (CLIENTE)  
**Descripción**: Cliente consulta sus propios pedidos

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| skip | integer | No | 0 | Offset |
| limit | integer | No | 50 | Límite |

**Response 200**:
```json
{
  "total": 5,
  "pedidos": [
    {
      "id": "pedido-uuid",
      "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
      "fecha_evento": "2026-01-26",
      "status": 0,
      "estado_nombre": "DRAFT",
      "monto_total": 1500.00,
      "created_at": "2025-11-27T12:00:00",
      "items_count": 1,
      "reservas_count": 0
    }
  ]
}
```

**Errores**:
- `401`: No autenticado

**Casuísticas**:
- ✅ Solo ve pedidos propios (filtrado por cliente_id del token)
- ✅ Paginación funcional
- ✅ Incluye contadores de items y reservas

---

### 4. Obtener Detalle de Pedido (Cliente)

**Endpoint**: `GET /contratacion/pedidos/{pedido_id}`  
**Autenticación**: Requerida (CLIENTE)  
**Descripción**: Cliente consulta detalle de su pedido

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| pedido_id | string (UUID) | ID del pedido |

**Response 200**:
```json
{
  "pedido": {
    "id": "pedido-uuid",
    "cliente_id": "cliente-uuid",
    "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
    "fecha_evento": "2026-01-26",
    "hora_inicio": "18:00:00",
    "hora_fin": "23:00:00",
    "num_personas": 100,
    "ubicacion": "Lima Centro",
    "status": 0,
    "monto_total": 1500.00,
    "moneda": "PEN",
    "created_at": "2025-11-27T12:00:00"
  },
  "items": [
    {
      "id": "item-uuid",
      "pedido_id": "pedido-uuid",
      "opcion_servicio_id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
      "nombre_servicio": "Servicio Prueba",
      "cantidad": 1,
      "precio_unitario": 1500.00,
      "subtotal": 1500.00
    }
  ],
  "reservas": [],
  "estado_nombre": "DRAFT",
  "total_items": 1,
  "total_reservas": 0
}
```

**Errores**:
- `403`: Pedido no pertenece al cliente autenticado
- `404`: Pedido no encontrado

**Casuísticas**:
- ✅ Obtiene pedido con items y reservas
- ❌ Cliente intenta ver pedido de otro (403)
- ✅ Incluye nombres de servicios (join con catálogo)

---

### 5. Listar Todos los Pedidos (Admin)

**Endpoint**: `GET /contratacion/admin/pedidos`  
**Autenticación**: Requerida (ADMIN)  
**Descripción**: Admin lista todos los pedidos del sistema

**Headers**:
```
Authorization: Bearer <admin_token>
```

**Query Parameters**:
| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| status | integer | No | - | Filtrar por estado (0,1,2,3,4) |
| cliente_id | string | No | - | Filtrar por cliente |
| fecha_desde | date | No | - | Filtrar desde fecha |
| fecha_hasta | date | No | - | Filtrar hasta fecha |
| skip | integer | No | 0 | Offset |
| limit | integer | No | 100 | Límite |

**Response 200**:
```json
{
  "total": 250,
  "pedidos": [
    {
      "id": "pedido-uuid",
      "cliente_id": "cliente-uuid",
      "cliente_nombre": "Juan Pérez",
      "cliente_email": "juan@email.com",
      "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
      "tipo_evento_nombre": "Boda",
      "fecha_evento": "2026-01-26",
      "status": 2,
      "estado_nombre": "APROBADO",
      "monto_total": 8500.00,
      "created_at": "2025-11-27T10:00:00",
      "items_count": 5,
      "reservas_count": 3
    }
  ]
}
```

**Errores**:
- `403`: Usuario no es ADMIN

**Casuísticas**:
- ✅ Admin ve todos los pedidos
- ✅ Filtrado por múltiples criterios
- ✅ Incluye información de cliente (join con IAM)
- ✅ Ordenado por fecha de creación descendente

---

### 6. Obtener Detalle de Pedido (Admin)

**Endpoint**: `GET /contratacion/admin/pedidos/{pedido_id}`  
**Autenticación**: Requerida (ADMIN)  
**Descripción**: Admin consulta detalle completo de cualquier pedido

**Headers**:
```
Authorization: Bearer <admin_token>
```

**Path Parameters**:
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| pedido_id | string (UUID) | ID del pedido |

**Response 200**:
```json
{
  "pedido": {
    "id": "pedido-uuid",
    "cliente_id": "cliente-uuid",
    "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
    "fecha_evento": "2026-01-26",
    "hora_inicio": "18:00:00",
    "hora_fin": "23:00:00",
    "num_personas": 100,
    "ubicacion": "Lima Centro",
    "status": 2,
    "monto_total": 1500.00,
    "created_at": "2025-11-27T12:00:00",
    "updated_at": "2025-11-27T12:30:00"
  },
  "items": [
    {
      "id": "item-uuid",
      "pedido_id": "pedido-uuid",
      "opcion_servicio_id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
      "nombre_servicio": "Servicio Prueba",
      "cantidad": 1,
      "precio_unitario": 1500.00,
      "subtotal": 1500.00
    }
  ],
  "reservas": [
    {
      "id": "reserva-uuid",
      "item_pedido_id": "item-uuid",
      "proveedor_id": "proveedor-uuid",
      "proveedor_nombre": "Proveedor XYZ",
      "inicio": "2026-01-26T18:00:00",
      "fin": "2026-01-26T23:00:00",
      "status": 1,
      "hold_id": "hold-uuid"
    }
  ],
  "estado_nombre": "APROBADO",
  "total_items": 1,
  "total_reservas": 1
}
```

**Errores**:
- `403`: Usuario no es ADMIN
- `404`: Pedido no encontrado

**Casuísticas**:
- ✅ Detalle completo con items, reservas y proveedores
- ✅ Incluye nombres de proveedores (join con servicio Proveedores)

---

### 7. Cambiar Estado de Pedido (Admin)

**Endpoint**: `PATCH /contratacion/admin/pedidos/{pedido_id}`  
**Autenticación**: Requerida (ADMIN)  
**Descripción**: Admin actualiza estado del pedido

**Headers**:
```
Authorization: Bearer <admin_token>
```

**Path Parameters**:
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| pedido_id | string (UUID) | ID del pedido |

**Request Body**:
```json
{
  "estado": 1
}
```

**Parámetros**:
| Campo | Tipo | Requerido | Valores | Descripción |
|-------|------|-----------|---------|-------------|
| estado | integer | Sí | 0,1,2,3,4 | Nuevo estado |

**Estados válidos**:
- `0`: DRAFT (Borrador)
- `1`: COTIZADO (Cotizado por admin)
- `2`: APROBADO (Aprobado por cliente)
- `3`: ASIGNADO (Proveedores asignados)
- `4`: CONFIRMADO (Confirmado final)

**Response 200**:
```json
{
  "id": "pedido-uuid",
  "estado": 1,
  "estado_nombre": "COTIZADO",
  "updated_at": "2025-11-27T12:30:00"
}
```

**Errores**:
- `400`: Estado inválido o transición no permitida
- `403`: Usuario no es ADMIN
- `404`: Pedido no encontrado

**Casuísticas**:
- ✅ Cambio de DRAFT (0) → COTIZADO (1)
- ✅ Cambio de COTIZADO (1) → APROBADO (2)
- ✅ Cambio de APROBADO (2) → ASIGNADO (3) (automático al asignar proveedores)
- ❌ Transiciones inválidas (ej: DRAFT → CONFIRMADO directamente)
- ✅ Actualiza timestamp updated_at

---

### 8. Asignar Proveedor a Item de Pedido (Admin)

**Endpoint**: `POST /contratacion/admin/pedidos/{pedido_id}/asignar-proveedor`  
**Autenticación**: Requerida (ADMIN)  
**Descripción**: Admin asigna proveedor específico a item del pedido

**Headers**:
```
Authorization: Bearer <admin_token>
```

**Path Parameters**:
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| pedido_id | string (UUID) | ID del pedido |

**Request Body**:
```json
{
  "proveedor_id": "cccccccc-3333-4444-5555-cccccccccccc",
  "item_pedido_id": "item-uuid",
  "opcion_servicio_id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
  "fecha_inicio": "2026-01-26T18:00:00",
  "fecha_fin": "2026-01-26T23:00:00",
  "monto": 1500.00,
  "hold_id": null,
  "notas": "Proveedor premium seleccionado"
}
```

**Parámetros**:
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| proveedor_id | string (UUID) | Sí | ID del proveedor |
| item_pedido_id | string (UUID) | Sí | ID del item del pedido |
| opcion_servicio_id | string (UUID) | Sí | Opción de servicio |
| fecha_inicio | datetime (ISO) | Sí | Inicio del servicio |
| fecha_fin | datetime (ISO) | Sí | Fin del servicio |
| monto | decimal | Sí | Monto de la reserva |
| hold_id | string (UUID) | No | Hold existente (si ya se creó) |
| notas | string | No | Observaciones |

**Response 201**:
```json
{
  "reserva_id": "reserva-uuid",
  "pedido_id": "pedido-uuid",
  "item_pedido_id": "item-uuid",
  "proveedor_id": "cccccccc-3333-4444-5555-cccccccccccc",
  "opcion_servicio_id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
  "inicio": "2026-01-26T18:00:00",
  "fin": "2026-01-26T23:00:00",
  "status": 1,
  "monto": 1500.00,
  "hold_id": "hold-uuid",
  "notas": "Proveedor premium seleccionado"
}
```

**Errores**:
- `400`: Pedido no está en estado APROBADO (2)
- `403`: Usuario no es ADMIN
- `404`: Pedido o item no encontrado
- `409`: Item ya tiene reserva asignada
- `502`: Error comunicación con servicio Proveedores (proveedor no disponible)

**Workflow interno**:
1. Valida pedido en estado APROBADO (2)
2. Valida item existe y no tiene reserva
3. Si `hold_id` es null:
   - Crea hold en servicio Proveedores
   - Confirma hold inmediatamente
4. Si `hold_id` existe:
   - Solo confirma hold existente
5. Crea reserva permanente en BD local
6. Si todos los items tienen reserva → actualiza pedido a ASIGNADO (3)

**Casuísticas**:
- ✅ Asignación exitosa con creación de hold
- ✅ Asignación exitosa con hold existente
- ❌ Pedido en estado DRAFT (400)
- ❌ Proveedor no disponible (502)
- ❌ Item ya tiene proveedor asignado (409)
- ✅ Actualización automática a ASIGNADO cuando todos items tienen proveedor
- ✅ **Idempotencia**: Múltiples llamadas con mismo correlation_id no duplican reservas

---

## Códigos de Error

### Códigos HTTP

| Código | Descripción | Uso |
|--------|-------------|-----|
| 200 | OK | Operación exitosa |
| 201 | Created | Recurso creado exitosamente |
| 204 | No Content | Operación exitosa sin contenido de respuesta |
| 400 | Bad Request | Datos inválidos o falta parámetro requerido |
| 401 | Unauthorized | Token ausente, inválido o expirado |
| 403 | Forbidden | Usuario sin permisos (ej: CLIENTE accede endpoint ADMIN) |
| 404 | Not Found | Recurso no existe |
| 409 | Conflict | Conflicto de estado (ej: proveedor no disponible) |
| 410 | Gone | Recurso expirado (ej: hold expirado) |
| 422 | Unprocessable Entity | Datos válidos pero lógica de negocio no permite procesarlos |
| 500 | Internal Server Error | Error interno del servidor |
| 502 | Bad Gateway | Error comunicación con servicio externo |

### Códigos de Error de Negocio

| Código | Servicio | Descripción |
|--------|----------|-------------|
| `CREDENCIALES_INVALIDAS` | IAM | Email o contraseña incorrectos |
| `USUARIO_INACTIVO` | IAM | Usuario con status != 1 |
| `TOKEN_EXPIRADO` | IAM | JWT expirado |
| `PEDIDO_NO_ENCONTRADO` | Contratación | Pedido no existe |
| `ITEM_PEDIDO_NO_ENCONTRADO` | Contratación | Item de pedido no existe |
| `ERROR_ASIGNACION` | Contratación | Error al asignar proveedor |
| `ERROR_SERVICIO_EXTERNO` | Contratación | Error en comunicación con Proveedores |
| `PROVEEDOR_NO_DISPONIBLE` | Proveedores | Proveedor tiene conflicto de agenda |
| `HOLD_NO_ENCONTRADO` | Proveedores | Hold no existe |
| `HOLD_EXPIRADO` | Proveedores | Hold superó su TTL |
| `HOLD_INVALIDO` | Proveedores | Hold en estado inválido para operación |

---

## Flujos de Negocio

### Flujo 1: Cliente Crea Pedido Personalizado

1. **Cliente hace login**
   - `POST /iam/login`
   - Obtiene `access_token`

2. **Cliente consulta catálogo**
   - `GET /catalogo/v1/servicios` (opcional: explorar servicios)
   - `GET /catalogo/v1/servicios/{servicio_id}` (ver opciones de servicio)

3. **Cliente crea pedido**
   - `POST /contratacion/pedidos`
   - Incluye items con opciones de servicio seleccionadas
   - Pedido queda en estado DRAFT (0)

4. **Cliente consulta sus pedidos**
   - `GET /contratacion/pedidos/mios`
   - Ve su pedido creado

5. **Cliente consulta detalle**
   - `GET /contratacion/pedidos/{pedido_id}`
   - Ve items incluidos

---

### Flujo 2: Admin Gestiona y Asigna Proveedores

1. **Admin hace login**
   - `POST /iam/login` (con usuario ADMIN)
   - Obtiene `access_token` con role=ADMIN

2. **Admin lista pedidos pendientes**
   - `GET /contratacion/admin/pedidos?status=0`
   - Ve pedidos en DRAFT

3. **Admin revisa detalle del pedido**
   - `GET /contratacion/admin/pedidos/{pedido_id}`
   - Ve items y datos del cliente

4. **Admin cotiza el pedido**
   - `PATCH /contratacion/admin/pedidos/{pedido_id}`
   - Body: `{"estado": 1}`
   - Pedido pasa a COTIZADO

5. **Cliente aprueba (simulado aquí como admin)**
   - `PATCH /contratacion/admin/pedidos/{pedido_id}`
   - Body: `{"estado": 2}`
   - Pedido pasa a APROBADO

6. **Admin consulta proveedores disponibles**
   - `GET /proveedores/proveedores?servicio_id={servicio_id}` (opcional)

7. **Admin asigna proveedor a cada item**
   - `POST /contratacion/admin/pedidos/{pedido_id}/asignar-proveedor`
   - Se crea hold en Proveedores
   - Se confirma hold
   - Se crea reserva permanente

8. **Sistema actualiza estado automáticamente**
   - Cuando todos los items tienen proveedor
   - Pedido pasa a ASIGNADO (3)

9. **Admin verifica asignación**
   - `GET /contratacion/admin/pedidos/{pedido_id}`
   - Ve reservas confirmadas con proveedores

---

### Flujo 3: Ciclo Completo Cliente-Admin

1. **Cliente**: Login + Consulta catálogo de paquetes
   - `POST /iam/login`
   - `GET /catalogo/v1/paquetes`

2. **Cliente**: Crea pedido con múltiples items
   - `POST /contratacion/pedidos`
   - Items basados en paquete seleccionado

3. **Admin**: Login y lista pedidos nuevos
   - `POST /iam/login`
   - `GET /contratacion/admin/pedidos?status=0`

4. **Admin**: Cotiza pedido
   - `PATCH /contratacion/admin/pedidos/{pedido_id}` → estado 1

5. **Admin**: Aprueba pedido
   - `PATCH /contratacion/admin/pedidos/{pedido_id}` → estado 2

6. **Admin**: Asigna proveedores a items
   - `POST /contratacion/admin/pedidos/{pedido_id}/asignar-proveedor` (por cada item)

7. **Cliente**: Consulta estado de su pedido
   - `GET /contratacion/pedidos/{pedido_id}`
   - Ve estado ASIGNADO con reservas confirmadas

---

## Notas Importantes

### Seguridad

1. **JWT Tokens**:
   - Expiran en 120 minutos (configurable en `JWT_EXPIRES_MIN`)
   - Algoritmo HS256
   - Secret compartido: `a040a67e53c324bb01e72d86e732e5db25cdc99a8c6bc29e20355e5c44bfcbfc`

2. **Roles**:
   - Endpoints `/admin/*` requieren role=ADMIN
   - Endpoints cliente validan que acceda solo a sus propios recursos

3. **Service-to-Service**:
   - Endpoints `/internal/*` requieren header `X-Service-Token`
   - Token: `dev-internal-token-change-in-production`

### Idempotencia

1. **Holds**:
   - Usar `correlation_id` para garantizar idempotencia
   - Múltiples llamadas con mismo `correlation_id` devuelven mismo hold

2. **Pedidos**:
   - Usar `request_id` (opcional) para evitar duplicados

### Validaciones de Negocio

1. **Estados de Pedido**:
   - DRAFT (0) → COTIZADO (1) → APROBADO (2) → ASIGNADO (3) → CONFIRMADO (4)
   - No se puede saltar estados

2. **Asignación de Proveedores**:
   - Solo pedidos en estado APROBADO (2)
   - Item no debe tener reserva previa
   - Proveedor debe estar disponible en rango de fechas

3. **Disponibilidad de Proveedores**:
   - Valida conflictos con holds activos
   - Valida conflictos con reservas confirmadas
   - Valida conflictos con períodos de descanso

### Performance

1. **Paginación**:
   - Usar `skip` y `limit` en listados grandes
   - Default limit: varía por endpoint (20-100)

2. **Joins**:
   - Algunos endpoints hacen joins con otros servicios
   - Puede haber latencia en listados con muchos datos

### Moneda

- Todas las operaciones usan **PEN (Soles Peruanos)** por defecto
- Precios con 2 decimales

---

## Changelog

### v1.0.0 (2025-11-27)
- Implementación inicial de 4 servicios
- Autenticación JWT
- Flujos E2E completos validados
- Arquitectura hexagonal implementada
