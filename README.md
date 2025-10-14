# SOA Eventos Perú — Arquitectura Hexagonal (MVP)

> **Estado:** Entorno local funcional (Windows). Servicios: **IAM**, **Catálogo**, **Proveedores**, **Contratación**.  
> Seguridad: **JWT** con `IAM` como emisor. Documentación interactiva: **Swagger UI** por servicio.

---

## 1) Visión General

Este repositorio implementa un **MVP** de un sistema de gestión de **eventos** basado en **microservicios** con **Arquitectura Hexagonal (Ports & Adapters)**.  
Cada servicio expone una API HTTP (FastAPI), usa su propio esquema de base de datos (MySQL) y se integra mediante **JWT** emitidos por el servicio **IAM**.

**Servicios incluidos**:
- **IAM**: autenticación e identidad (emite y refresca **JWT**).
- **Catálogo**: lectura de tipos/servicios/opciones y precios vigentes.
- **Proveedores**: gestión y lectura de proveedores, habilidades y disponibilidad.
- **Contratación**: pedidos de eventos, ítems y reservas.

**Librería compartida (`libs/shared/ev_shared`)**:
- `config`: carga de configuración/entorno.
- `db`: `session_scope` para acceso a BD con SQLAlchemy.
- `security`: helpers de contraseñas (`verify_password`, `hash_password`) y utilidades de seguridad.

---

## 2) Arquitectura Hexagonal (Ports & Adapters)

La **hexagonal** se logra al separar de forma explícita **dominio**, **aplicación**, **infraestructura** y **entradas** (*entrypoints*), más **puertos/ports** definidos desde el dominio y **adaptadores/adapters** en infraestructura:

```
services/<svc>/app/
├── domain/                     # Núcleo del dominio (entidades, puertos)
│   ├── models.py
│   └── ports.py                # Interfaces (p.ej., CatalogoRepository, ProveedorRepository)
├── application/                # Casos de uso / orquestación
│   ├── queries.py              # ServiceContainer, get_container, casos de lectura
│   └── commands.py             # (si aplica) casos de escritura
├── infrastructure/             # Adaptadores (DB, HTTP externos, cache, etc.)
│   └── db/sqlalchemy/
│       ├── repositories.py     # Implementaciones de los puertos contra SQLAlchemy
│       └── mappers.py          # (opcional) mapeos ORM/DTO
└── entrypoints/fastapi/        # Borde del sistema — API HTTP
    ├── main.py                 # app FastAPI, wireado y middlewares
    └── router.py               # endpoints → delegan a application (ports)
```

**Qué lo hace hexagonal aquí:**
- Los **endpoints** (adaptadores de entrada) **no** contienen lógica de dominio: delegan a **application**.
- El **dominio** define **puertos (interfaces)** y la **infraestructura** provee **adaptadores** concretos (repos SQLAlchemy).
- El **acoplamiento** se dirige **hacia interfaces**, no hacia implementaciones (p. ej. `CatalogoRepository`).
- `ServiceContainer` en **application** arma las dependencias (inyecta puertos/adaptadores) sin filtrar a los entrypoints el detalle de infraestructura.
- **Librería compartida** (`ev_shared`) centraliza cross-cutting (config, db, seguridad).

---

## 3) Interconexión y Seguridad

- **JWT** emitido por **IAM** (`/iam/auth/login`) con claims: `sub` (id de usuario), `username` (email).  
- **Servicios de negocio** (**Catálogo**, **Proveedores**, **Contratación**) **exigen JWT** en sus routers mediante `HTTPBearer(auto_error=True)` y un `validate_token()` que decodifica con `JWT_SECRET` y `JWT_ALG` (mismos valores que IAM).  
- **Esquemas de BD separados por bounded context**: `ev_iam`, `ev_catalogo`, `ev_proveedores`, `ev_contratacion`, `ev_paquetes`.  
- **Lectura optimizada** con **vistas** (p. ej. `ev_catalogo.v_opcion_con_precio_vigente`).

**Flujo de autenticación**:
1. `POST /iam/auth/login` (email + password) ⇒ **JWT**.
2. En Swagger del resto de servicios: botón **Authorize** ⇒ `Bearer <JWT>`.
3. Llamadas a endpoints protegidos retornan **401** si no hay token válido.

---

## 4) Estructura del repositorio (resumen)

```
.
├── services/
│   ├── iam-service/
│   │   └── app/entrypoints/fastapi/ (main.py, router.py)
│   ├── catalogo-service/
│   │   └── app/entrypoints/fastapi/ (main.py, router.py)
│   ├── proveedores-service/
│   │   └── app/entrypoints/fastapi/ (main.py, router.py)
│   └── contratacion-service/
│       └── app/entrypoints/fastapi/ (main.py, router.py)
├── libs/
│   └── shared/ev_shared/
│       ├── config/               # Settings
│       ├── db/                   # session_scope
│       └── security/             # passwords.py (verify_password, etc.)
├── tools/                        # utilitarios opcionales
└── start-all.ps1 / stop-all.ps1  # orquestación local
```

> Asegúrate de que cada paquete Python contenga `__init__.py` (especialmente en `app/`, `domain/`, `application/`, `infrastructure/`, `entrypoints/`).

---

## 5) Endpoints principales

- **IAM**
  - `GET  /iam/health`
  - `POST /iam/auth/login`   → `{ email, password }` → `access_token`
  - `POST /iam/auth/refresh` → `token` → `access_token`

- **Catálogo**
  - `GET /catalogo/health`
  - `GET /catalogo/tipos-evento?limit=100`
  - `GET /catalogo/opciones/precios?limit=50` (vista `v_opcion_con_precio_vigente`)

- **Proveedores**
  - `GET /proveedores/health`
  - `GET /proveedores/list?limit=100`
  - `GET /proveedores/list/activos?limit=100` (read-model directo alineado a DDL)

- **Contratación**
  - `GET /contratacion/health`
  - `GET /contratacion/pedidos?limit=50`

**Swagger UI**:  
- IAM: `http://localhost:8010/docs`  
- Catálogo: `http://localhost:8020/docs`  
- Proveedores: `http://localhost:8030/docs`  
- Contratación: `http://localhost:8040/docs`

---

## 6) Requisitos y configuración

**Requisitos**:
- Windows 10/11, PowerShell 5+
- Python 3.11+ (virtualenv recomendado)
- MySQL 8+
- Variables de entorno por servicio (`.env`)

**Variables típicas en `.env`**:
```
# Comunes
DB_HOST=localhost
DB_PORT=3306
DB_USER=app_api       # o el usuario por bounded context (ej. app_catalogo)
DB_PASS=Api_2025!
DB_NAME=ev_catalogo   # (cambia por servicio; p.ej. ev_iam, ev_proveedores, ev_contratacion)

# Seguridad
JWT_SECRET=supersecreto_mvp
JWT_ALG=HS256
JWT_EXPIRES_MIN=60

# App
APP_HOST=0.0.0.0
APP_PORT=8020         # (varía por servicio: IAM 8010, Catálogo 8020, Proveedores 8030, Contratación 8040)
```

> Cada servicio trae `.env.example`. Al primer arranque `run.bat` copia `.env.example` → `.env` si no existe.

---

## 7) Ejecución en local

### a) Por servicio
```bat
services\iam-service\run.bat
services\catalogo-service\run.bat
services\proveedores-service\run.bat
services\contratacion-service\run.bat
```

### b) Todos a la vez (recomendado)
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\start-all.ps1
```
- Guarda PIDs y logs en `.run\` de cada servicio.
- **Detener todo**:
```powershell
.\stop-all.ps1
```

**Logs** (tail en tiempo real):
```powershell
Get-Content -Tail 100 -Wait services\<svc>\.run\out.log
```

---

## 8) Resultados esperados

- **/docs** en cada servicio con botón **Authorize** activo.
- Llamadas protegidas → **401** si no se envía `Authorization: Bearer <token>`.
- **IAM** valida `email + password_hash` y emite **JWT** usable en el resto.
- **Catálogo** responde listas y vistas vigentes de precios.
- **Proveedores** lista activos (si usas el read-model) o según tu `repo` hexagonal.
- **Contratación** lista pedidos (read-model inicial).

---

## 9) Buenas prácticas ya presentes

- Separación hexagonal clara (domain / application / infrastructure / entrypoints).
- Centralización de **config**, **db** y **security** en `ev_shared`.
- Routers con **dependencias JWT** a nivel de router (simple y explícito).
- Vistas de lectura para **consultas eficientes**.
- Scripts de **orquestación local** con control de PIDs y logs.

---

## 10) Sugerencias de mejora (futuras)

- **Auth/Z**: incluir `iss/aud` en JWT, scopes/roles por endpoint, validación de `jti` contra `ev_iam.sesion` (revocación).
- **Observabilidad**: `request_id`, logs estructurados, métricas, tracing (OpenTelemetry).
- **Resiliencia**: timeouts, reintentos, circuit breaker, rate limiting.
- **Validaciones**: DTOs para entrada/salida en `entrypoints`, paginación y sorting consistentes.
- **Migrations**: Alembic + seeds por servicio (en vez de SQL “monolítico”).
- **Testing**: unitarios del dominio, contract tests por puerto, smoke tests post-deploy.
- **CI**: pre-commit (ruff/black/isort), pipeline de linters y tests.
- **Empaquetado**: Docker para entorno local y luego K8s (Helm/ArgoCD), secretos en Vault.
- **Mensajería** (si evoluciona a coreografía): eventos de dominio (pedido creado, reserva confirmada, etc.).

---

## 11) Troubleshooting rápido

- **WinError 10048 (puerto en uso)**: hay procesos previos en 8010/8020/8030/8040. Ejecuta `.\stop-all.ps1`. Si persiste:
  ```powershell
  foreach ($p in 8010,8020,8030,8040) {
    netstat -ano | findstr ":$p" | findstr LISTENING
  }
  ```
  y mata PIDs colgantes con `Stop-Process -Id <PID> -Force`.

- **ImportError/ModuleNotFoundError**: falta `__init__.py` o `PYTHONPATH`. Verifica que `run.bat` exporte:
  ```bat
  set PYTHONPATH=%HERE%\..\..\libs\shared;%HERE%
  ```

- **No aparece “Authorize” en Swagger**: asegúrate de tener `HTTPBearer(auto_error=True)` + dependencia en el `APIRouter`.

---

## 12) Licencia y Contribución

- Licencia: MIT (puedes cambiarla según tu necesidad).
- PRs y mejoras son bienvenidas. Por favor, describe cambios, añade pruebas y ejecuta linters antes de abrir el PR.

---

**¡Listo!** Con este README y los scripts de orquestación puedes levantar todo localmente, probar las APIs con Swagger y validar el flujo de autenticación de extremo a extremo.
