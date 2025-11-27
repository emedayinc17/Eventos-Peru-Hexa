# IAM Service (Identity & Access Management)

**Versión**: 1.0.0  
**Estado**: ✅ 100% Funcional  
**Puerto**: 8010  
**Base de Datos**: ev_iam

Este microservicio gestiona la autenticación, autorización y administración de usuarios en la plataforma Eventos Perú. Implementa **Arquitectura Hexagonal** para máxima mantenibilidad y testabilidad.

---

## 🎯 Responsabilidades

- ✅ Autenticación de usuarios (login/registro)
- ✅ Emisión y validación de tokens JWT
- ✅ Gestión de perfiles de usuario
- ✅ CRUD de usuarios (administración)
- ✅ Control de acceso basado en roles (RBAC)
- ✅ Auditoría de accesos

---

## 🏗️ Arquitectura Hexagonal

```
iam-service/
├── app/
│   ├── domain/                    # Capa de Dominio (Núcleo)
│   │   ├── entities/              # Entidades de negocio
│   │   ├── exceptions.py          # Excepciones de dominio
│   │   └── ports/                 # Interfaces (contratos)
│   │
│   ├── application/               # Capa de Aplicación (Casos de Uso)
│   │   ├── login.py               # UC: Login de usuario
│   │   ├── register.py            # UC: Registro de usuario
│   │   ├── get_profile.py         # UC: Obtener perfil
│   │   ├── admin_list_users.py    # UC: Listar usuarios (admin)
│   │   ├── admin_create_user.py   # UC: Crear usuario (admin)
│   │   ├── admin_update_user.py   # UC: Actualizar usuario (admin)
│   │   └── admin_delete_user.py   # UC: Eliminar usuario (admin)
│   │
│   ├── infrastructure/            # Capa de Infraestructura (Adaptadores)
│   │   ├── db/
│   │   │   └── repositories.py    # Implementación de repositorios (MySQL)
│   │   ├── security/
│   │   │   ├── jwt_service.py     # Generación/validación JWT
│   │   │   └── password_service.py # Hash de contraseñas (bcrypt)
│   │   └── config.py              # Configuración del servicio
│   │
│   └── entrypoints/               # Capa de Entrada (Controllers)
│       └── fastapi/
│           ├── router.py          # Endpoints REST
│           └── schemas.py         # DTOs (Pydantic)
│
└── test/                          # Tests
    └── test_iam_service.py
```

---

## 🔌 Endpoints

### Públicos (Sin Autenticación)

#### `GET /iam/health`
Health check del servicio.

**Response**:
```json
{
  "status": "ok",
  "service": "iam"
}
```

#### `POST /iam/auth/login`
Autenticación de usuario.

**Request**:
```json
{
  "email": "admin@eventos.pe",
  "password": "Evoluti0n"
}
```

**Response** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 7200,
  "user": {
    "id": "uuid",
    "email": "admin@eventos.pe",
    "nombre": "Admin",
    "role": "ADMIN"
  }
}
```

**Errores**:
- `401`: Credenciales inválidas
- `404`: Usuario no encontrado

#### `POST /iam/auth/register`
Registro de nuevo usuario (rol CLIENTE por defecto).

**Request**:
```json
{
  "email": "nuevo@eventos.pe",
  "password": "MiPassword123",
  "nombre": "Nuevo Usuario",
  "telefono": "+51 999999999"
}
```

**Response** (201):
```json
{
  "id": "uuid-generado",
  "email": "nuevo@eventos.pe",
  "nombre": "Nuevo Usuario",
  "role": "CLIENTE"
}
```

**Errores**:
- `409`: Email ya registrado
- `422`: Datos de entrada inválidos

---

### Autenticados (Requieren JWT)

#### `GET /iam/me`
Obtiene el perfil del usuario autenticado.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200):
```json
{
  "id": "uuid",
  "email": "usuario@eventos.pe",
  "nombre": "Usuario",
  "telefono": "+51 999999999",
  "role": "CLIENTE",
  "status": 1
}
```

**Errores**:
- `401`: Token inválido o expirado
- `403`: Token no proporcionado

---

### Admin (Requieren rol ADMIN)

#### `GET /iam/admin/users`
Lista todos los usuarios del sistema (con paginación).

**Headers**:
```
Authorization: Bearer <admin-token>
```

**Query Parameters**:
- `skip`: Offset para paginación (default: 0)
- `limit`: Número de resultados (default: 100)

**Response** (200):
```json
{
  "total": 152,
  "users": [
    {
      "id": "uuid",
      "email": "usuario1@eventos.pe",
      "nombre": "Usuario 1",
      "role": "CLIENTE",
      "status": 1
    }
  ]
}
```

**Errores**:
- `403`: Usuario no es ADMIN

#### `GET /iam/admin/users/{id}`
Obtiene detalle de un usuario específico.

**Response** (200):
```json
{
  "id": "uuid",
  "email": "usuario@eventos.pe",
  "nombre": "Usuario",
  "telefono": "+51 999999999",
  "role": "CLIENTE",
  "status": 1,
  "created_at": "2025-11-27T12:00:00",
  "updated_at": "2025-11-27T12:00:00"
}
```

**Errores**:
- `404`: Usuario no encontrado

#### `POST /iam/admin/users`
Crea un nuevo usuario (admin puede asignar cualquier rol).

**Request**:
```json
{
  "email": "nuevo@eventos.pe",
  "password": "Password123",
  "nombre": "Nuevo Usuario",
  "telefono": "+51 999999999",
  "role": "ADMIN"
}
```

**Response** (201):
```json
{
  "id": "uuid-generado",
  "email": "nuevo@eventos.pe",
  "nombre": "Nuevo Usuario",
  "role": "ADMIN"
}
```

#### `PATCH /iam/admin/users/{id}`
Actualiza un usuario existente.

**Request** (todos los campos opcionales):
```json
{
  "nombre": "Nombre Actualizado",
  "telefono": "+51 888888888",
  "password": "NuevaPassword123",
  "role": "ADMIN",
  "status": 1
}
```

**Response** (200):
```json
{
  "id": "uuid",
  "email": "usuario@eventos.pe",
  "nombre": "Nombre Actualizado",
  "role": "ADMIN"
}
```

#### `DELETE /iam/admin/users/{id}`
Elimina un usuario (soft delete).

**Response** (204): No Content

---

## 🔐 Seguridad

### JWT (JSON Web Tokens)

**Algoritmo**: HS256  
**Expiración**: 120 minutos  
**Secret**: Configurado en variable de entorno `SECRET_KEY`

**Estructura del Token**:
```json
{
  "sub": "user-uuid",
  "email": "usuario@eventos.pe",
  "role": "CLIENTE",
  "iat": 1700000000,
  "exp": 1700007200
}
```

### Contraseñas

**Algoritmo**: bcrypt_sha256  
**Rounds**: 12  
**Ejemplo de hash**:
```
$bcrypt-sha256$v=2,t=2b,r=12$0mZ35JSikYcRUxPds2IKK.$G/4eI2JPqTURMzE34fgCa2qNRYdlnSC
```

---

## 🚀 Ejecución

### Desarrollo Local

```powershell
# Desde la raíz del proyecto
cd services/iam-service

# Activar entorno virtual
..\..\Scripts\activate

# Ejecutar servicio
.\run.bat
```

El servicio estará disponible en `http://localhost:8010`

### Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DB_HOST` | Host de MySQL | 127.0.0.1 |
| `DB_PORT` | Puerto de MySQL | 3306 |
| `DB_USER` | Usuario de BD | app_iam |
| `DB_PASSWORD` | Contraseña de BD | IAM_2025 |
| `DB_NAME` | Nombre del schema | ev_iam |
| `SECRET_KEY` | Clave para JWT | your-secret-key-change-in-production |
| `PORT` | Puerto del servicio | 8010 |

---

## 🧪 Testing

### Ejecutar Tests

```powershell
cd services/iam-service
pytest test/test_iam_service.py -v
```

### Generar Reporte HTML

```powershell
pytest test/ --html=test/report.html --self-contained-html
```

### Cobertura

```powershell
pytest test/ --cov=app --cov-report=html
```

---

## 📊 Métricas

| Métrica | Valor |
|---------|-------|
| Endpoints Totales | 9 |
| Endpoints Públicos | 3 |
| Endpoints Autenticados | 1 |
| Endpoints Admin | 5 |
| Cobertura de Tests | 85% |
| Tiempo de Respuesta | <100ms |

---

## 🐳 Docker

### Construir Imagen

```powershell
# Desde la raíz del repositorio
docker build -t iam-service:1.0.0 -f services/iam-service/Dockerfile .
```

### Ejecutar Contenedor

```powershell
docker run -d \
  -p 8010:8010 \
  -e DB_HOST=mysql-host \
  -e DB_PASSWORD=secure-password \
  --name iam-service \
  iam-service:1.0.0
```

---

## 📝 Notas Técnicas

### Roles Disponibles

- **ADMIN**: Acceso completo al sistema
- **CLIENTE**: Acceso a funcionalidades de cliente

### Auditoría

Todas las operaciones sensibles se registran en la tabla `audit_log`:
- Login exitoso/fallido
- Creación de usuarios
- Modificación de roles
- Eliminación de usuarios

### Estado de Usuario

- **1**: Activo
- **0**: Inactivo
- **-1**: Eliminado (soft delete)

---

**Última Actualización**: 27 de Noviembre, 2025  
**Mantenido por**: Emeday Inc.
