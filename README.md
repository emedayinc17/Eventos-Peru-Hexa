
# Eventos Perú — MVP (Arquitectura Hexagonal)

Microservicios en Python + FastAPI + MySQL siguiendo un enfoque **hexagonal**. Incluye IAM, Catálogo, Contratación, Proveedores, Paquetes y un módulo compartido (`ev_shared`). Se priorizan **buenas prácticas**: JWT, soft-delete, auditoría, consultas parametrizadas, y outbox para mensajería.

---

## 🧭 TL;DR (arranque rápido)

1) **Requisitos**  
- Python 3.12+  
- MySQL 8.x  
- PowerShell / Bash

2) **Base de datos**  
- Importa el script consolidado (estructura + seeds + grants):  
  `db/sql/soa_eventos_peru_mvp.sql` (o el archivo .sql consolidado que tengas).

3) **Variables de entorno (.env por servicio)**  
Crea/ajusta los `.env` en cada carpeta `services/<service>/.env` (ver ejemplos abajo).

4) **Levantar servicios (PowerShell)**  
```powershell
# IAM
.\services\iam-service
un.bat

# Catálogo
.\services\catalogo-service
un.bat

# Contratación
.\services\contratacion-service
un.bat
```
(Usa los demás `run.bat` si aplica: proveedores, paquetes, mensajería).

5) **Swagger (por servicio)**  
- `http://localhost:<PUERTO>/docs`  
- OpenAPI JSON: `/openapi.json`

---

## 🧱 Estructura del proyecto (resumen)

```
eventos-peru-hexagonal/
├─ services/
│  ├─ iam-service/
│  │  ├─ app/
│  │  │  └─ entrypoints/fastapi/
│  │  │     ├─ main.py          # crea FastAPI app y registra router; seguridad HTTPBearer en OpenAPI
│  │  │     ├─ router.py        # rutas IAM (auth, me, admin users) + auditoría + soft-delete
│  │  │     └─ schemas.py       # DTOs Pydantic v2
│  │  ├─ .env
│  │  └─ run.bat
│  ├─ catalogo-service/
│  │  ├─ app/entrypoints/fastapi/ (main.py, router.py, schemas.py)
│  │  ├─ .env
│  │  └─ run.bat
│  ├─ contratacion-service/
│  │  ├─ app/
│  │  │  ├─ entrypoints/fastapi/ (main.py, router.py, security.py, schemas.py)
│  │  │  └─ application/commands.py   # casos de uso con SQL parametrizado
│  │  ├─ .env
│  │  └─ run.bat
│  ├─ proveedores-service/ (opcional en este MVP)
│  ├─ paquetes-service/ (opcional en este MVP)
│  └─ mensajeria-service/ (opcional en este MVP)
├─ ev_shared/
│  ├─ __init__.py
│  ├─ config.py               # Settings (dotenv) — DB URL, JWT, etc.
│  ├─ db.py                   # session_scope()
│  └─ security/passwords.py   # hash_password(), verify_password() (bcrypt)
├─ db/
│  └─ sql/
│     └─ soa_eventos_peru_mvp.sql   # **Script consolidado**: esquemas, vistas, seeds, grants
└─ README.md  (este archivo)
```

> **Nota:** la estructura exacta puede variar ligeramente según tu repo, pero lo importante es que cada servicio expone `main.py`, `router.py`, `schemas.py` y un `run.bat` con su `.env` correspondiente.

---

## 🔐 Seguridad y JWT

- **Login** (`/auth/login`) emite JWT **HS256** con claims:
  - `sub` (user id), `username` (email), `role` (`ADMIN`/`CLIENTE`), `iat`, `exp`, `scope`.
- **Protección**: rutas con `openapi_extra={"security": [{"HTTPBearer": []}]}` y dependencia `get_current_user` (valida Bearer).
- **Roles**: helper `require_role("ADMIN")` en rutas admin.
- **Auditoría** (IAM):
  - Tabla `ev_iam.evento_audit`: acciones `LOGIN`, `USUARIO_CREAR`, `USUARIO_ACTUALIZAR`, `USUARIO_ELIMINAR` (con `metadata` JSON).
  - Tabla `ev_iam.login_intento`: registra éxitos/fallos de login.
- **Soft-delete**: `is_deleted=1` y `status=0`. Búsquedas filtran `is_deleted=0`.

---

## 🗃️ Base de datos (resumen)

### Esquemas
- `ev_iam`: `usuario`, `rol`, `usuario_rol`, `sesion`, `evento_audit`, `login_intento`, (reset tokens opcional).
- `ev_catalogo`: `tipo_evento`, `servicio`, `opcion_servicio`, `precio_servicio`, vistas: `v_opcion_con_precio_vigente`.
- `ev_paquetes`: `paquete`, `item_paquete`, `precio_paquete`, vistas: `v_paquete_detalle`, `v_paquete_precio_vigente_total`.
- `ev_contratacion`: `pedido_evento`, `item_pedido_evento`, `reserva`, vista `v_pedido_con_cliente`.
- `ev_proveedores`: `proveedor`, `habilidad_proveedor`, `calendario_proveedor`, `reserva_temporal`.
- `ev_mensajeria`: `email_outbox` (Outbox pattern).

### Usuarios DB / Grants (por bounded context)
- `app_iam`, `app_catalogo`, `app_paquetes`, `app_proveedores`, `app_contratacion`, `app_mensajeria`, `app_api`.
- Cada servicio usa un **usuario y privilegios mínimos** sobre su esquema.

> Aplica el **script SQL consolidado** para crear todo y sembrar datos mínimos (roles, usuario demo, catálogo base).

---

## ⚙️ Configuración (.env por servicio)

### Ejemplo: `services/iam-service/.env`
```
APP_NAME=iam-service
APP_VERSION=0.1.0
APP_HOST=0.0.0.0
APP_PORT=8010

# MySQL (usuario con permisos solo sobre ev_iam)
DB_URL=mysql+pymysql://app_iam:IAM_2025@127.0.0.1:3306/ev_iam

# JWT
JWT_SECRET=super_secreto_largo_y_unico
JWT_ALG=HS256
JWT_EXPIRES_MIN=60
```

### Ejemplo: `services/catalogo-service/.env`
```
APP_NAME=catalogo-service
APP_VERSION=0.1.0
APP_HOST=0.0.0.0
APP_PORT=8020

DB_URL=mysql+pymysql://app_catalogo:Catalogo_2025@127.0.0.1:3306/ev_catalogo
```

### Ejemplo: `services/contratacion-service/.env`
```
APP_NAME=contratacion-service
APP_VERSION=0.1.0
APP_HOST=0.0.0.0
APP_PORT=8040

DB_URL=mysql+pymysql://app_contratacion:Contrata_2025@127.0.0.1:3306/ev_contratacion

# Para consumir IAM (si aplica) o verificar JWT en entrypoint
JWT_SECRET=super_secreto_largo_y_unico
JWT_ALG=HS256
```

> Ajusta host/puerto/secret según tu entorno. Si usas Docker, reemplaza `127.0.0.1` por el nombre del servicio MySQL.

---

## 🧩 Servicios (resumen funcional)

### IAM
- **Público**: `/health`, `/auth/login`, `/auth/register`
- **Protegido**: `/me`
- **Admin (Bearer + rol ADMIN)**: `/admin/users` (CRUD parcial)
- **Prácticas**: soft-delete, auditoría, login_intento, SQL con parámetros, hash de contraseña.

### Catálogo
- Exposición de `tipo_evento`, `servicio`, `opcion_servicio` y `precio` vigente (solo lectura para público).
- Usa vistas (`v_opcion_con_precio_vigente`) para aislar reglas de vigencia.

### Contratación
- **Cliente**: crear pedido desde paquete o custom items; listar/obtener; enviar resumen (outbox).
- **Admin**: cambiar estado, agregar/eliminar ítems, asignar proveedor (reglas simples y conflictos).
- SQL **parametrizado** con `sqlalchemy.text()` y `session_scope()` (evita inyecciones).

---

## 🔎 Buenas prácticas aplicadas

- **Nada hardcodeado** en queries: parámetros `:named` siempre.
- **Separation of concerns**: `entrypoints` (API) vs `application` (casos de uso).
- **Evitar SELECT ***: solo columnas necesarias.
- **Índices** para filtros frecuentes (`status`, `is_deleted`, fechas).
- **Vistas** para modelos de lectura (precio vigente, totales de paquete).
- **Auditoría** y **outbox** para trazabilidad e integración.

---

## 🧪 Ejemplos rápidos (curl)

### Login
```bash
curl -X POST http://localhost:8010/auth/login   -H "Content-Type: application/json"   -d '{"email":"demo@eventos.pe","password":"<TU_PASSWORD_DEMO>"}'
```

### Usar token en una ruta protegida
```bash
TOKEN="<access_token>"
curl http://localhost:8010/me -H "Authorization: Bearer $TOKEN"
```

### Crear usuario (ADMIN)
```bash
curl -X POST http://localhost:8010/admin/users   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{"email":"admin2@eventos.pe","password":"Admin_2025!","nombre":"Admin 2","telefono":"+51 999 111 222","role":"ADMIN"}'
```

### Soft-delete usuario (ADMIN)
```bash
curl -X DELETE http://localhost:8010/admin/users/<user_id>   -H "Authorization: Bearer $TOKEN"
```

---

## 🛠️ Troubleshooting

- **Swagger /openapi.json 500 (Pydantic v2: “class-not-fully-defined”)**  
  Revisa que no se inyecten tipos especiales en dependencias (`Annotated`/`Query`) sin `rebuild()`. En este repo ya se normalizó el uso de `Header`/`Depends` simples.

- **Error Pydantic: “Fields must not use names with leading underscores”**  
  Asegúrate de no definir campos de modelo que comiencen con `_`. Ya está corregido en `schemas.py`.

- **Cambios no reflejados**  
  Limpia caché Python:
  ```powershell
  Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
  Get-ChildItem -Path . -Recurse -Include *.pyc | Remove-Item -Force
  ```

- **401 en rutas admin**  
  Verifica que el `role` del token sea `ADMIN`. Usa `/auth/login` con un usuario admin o asigna el rol vía `/admin/users`.

---

## 📌 Roadmap (siguiente avance)

- Rotación de **JWT_SECRET** y revocación por `sesion`/`jti`.
- Idempotencia en endpoints críticos via `request_id` (Contratación ya lo usa en `pedido_evento`).
- Workers para **email_outbox**.
- Observabilidad: logs estructurados, trazas y métricas.
- Tests automatizados (pytest + httpx).

---

## 🤝 Contribuir

1. Crea rama a partir de `main`.
2. Asegúrate de pasar linters/formatters (black/isort) si los tienes configurados.
3. Abre PR con descripción y pasos de prueba.

---

## 📄 Author

Emeday © 2025
