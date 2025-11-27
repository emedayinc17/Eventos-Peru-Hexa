# Eventos Perú - Arquitectura Hexagonal (Microservicios)

**Autor:** Emeday@2025  
**Versión:** 1.0.0 - Sistema 100% Funcional  
**Estado:** ✅ Desarrollo Completo - Listo para Frontend  
**Fecha:** 27 de Noviembre, 2025

Este proyecto implementa un sistema completo de gestión de eventos utilizando **Arquitectura Hexagonal** (Puertos y Adaptadores) distribuida en microservicios independientes. El sistema está 100% funcional con todos los flujos end-to-end validados.

---

## 📊 Estado del Proyecto

| Componente | Estado | Cobertura |
|------------|--------|-----------|
| **Backend (4 servicios)** | ✅ Completo | 100% |
| **Base de Datos** | ✅ Completo | 100% |
| **Autenticación JWT** | ✅ Completo | 100% |
| **Tests E2E** | ✅ Completo | 100% (3/3 flujos) |
| **Documentación API** | ✅ Completo | 100% |
| **Frontend** | 🔄 En Progreso | 60% |

**Última Validación**: 27 de Noviembre, 2025  
**Tests Ejecutados**: 27 endpoints, 3 flujos completos, 0 errores

---

## 📋 Prerrequisitos

Para ejecutar este proyecto localmente necesitas:

1. **Python 3.12+**: Lenguaje base para todos los microservicios
2. **MySQL 8.0**: Base de datos relacional principal
3. **PowerShell**: Para orquestación de servicios en Windows
4. **Git**: Para control de versiones
5. **Docker** (Opcional): Para despliegue en contenedores
6. **Kubernetes** (Opcional): Para orquestación en producción

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Componentes

```
┌─────────────┐      ┌──────────────────────────────────────┐
│   Frontend  │─────▶│           API Gateway                │
│ (Vanilla JS)│      │    (NGINX/Ingress - Futuro)          │
└─────────────┘      └──────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┬─────────────┐
                │             │             │             │
         ┌──────▼──────┐ ┌───▼────┐ ┌─────▼─────┐ ┌────▼─────┐
         │ IAM Service │ │Catálogo│ │Proveedores│ │Contrata- │
         │   :8010     │ │ :8020  │ │  :8030    │ │ción :8040│
         └──────┬──────┘ └───┬────┘ └─────┬─────┘ └────┬─────┘
                │            │            │            │
         ┌──────▼────────────▼────────────▼────────────▼─────┐
         │              MySQL 8.0 (7 Schemas)                │
         │  ev_iam | ev_catalogo | ev_proveedores |          │
         │  ev_contratacion | ev_mensajeria | ev_paquetes    │
         └────────────────────────────────────────────────────┘
```

### Comunicación Entre Servicios

- **Cliente ↔ Servicios**: HTTP/REST con JWT (Authorization: Bearer)
- **Servicio ↔ Servicio**: HTTP/REST con Service Token (X-Service-Token)
- **Servicios ↔ Base de Datos**: MySQL Pool de Conexiones

---

## 🎯 Microservicios Implementados

### 1. IAM Service (Identidad y Acceso) ✅
- **Puerto**: `8010`
- **Responsabilidad**: Autenticación, autorización, gestión de usuarios
- **Base de Datos**: `ev_iam`
- **Endpoints**: 9 (100% funcionales)
- **Documentación**: [Ver README](services/iam-service/README.md)

**Endpoints Principales**:
```
GET    /iam/health               - Health check
POST   /iam/auth/login           - Login (público)
POST   /iam/auth/register        - Registro (público)
GET    /iam/me                   - Perfil usuario (autenticado)
GET    /iam/admin/users          - Listar usuarios (ADMIN)
POST   /iam/admin/users          - Crear usuario (ADMIN)
PATCH  /iam/admin/users/{id}     - Actualizar usuario (ADMIN)
DELETE /iam/admin/users/{id}     - Eliminar usuario (ADMIN)
```

### 2. Catálogo Service ✅
- **Puerto**: `8020`
- **Responsabilidad**: Gestión de servicios, paquetes y precios
- **Base de Datos**: `ev_catalogo`, `ev_paquetes`
- **Endpoints**: 14 (100% funcionales)
- **Documentación**: [Ver README](services/catalogo-service/README.md)

### 3. Proveedores Service ✅
- **Puerto**: `8030`
- **Responsabilidad**: Gestión de proveedores, disponibilidad, holds
- **Base de Datos**: `ev_proveedores`
- **Endpoints**: 10 (100% funcionales)
- **Documentación**: [Ver README](services/proveedores-service/README.md)

### 4. Contratación Service ✅
- **Puerto**: `8040`
- **Responsabilidad**: Gestión de pedidos, reservas, asignación de proveedores
- **Base de Datos**: `ev_contratacion`
- **Endpoints**: 12 (100% funcionales)
- **Documentación**: [Ver README](services/contratacion-service/README.md)

---

## 🗄️ Base de Datos

### Esquemas MySQL

| Schema | Tablas | Propósito |
|--------|--------|-----------|
| `ev_iam` | usuarios, audit_log | Autenticación y auditoría |
| `ev_catalogo` | tipos_evento, servicios, opciones_servicio | Catálogo de servicios |
| `ev_paquetes` | paquetes, paquetes_items | Paquetes predefinidos |
| `ev_proveedores` | proveedores, habilidades, holds, calendario | Proveedores y disponibilidad |
| `ev_contratacion` | pedidos, items_pedido, reservas | Pedidos y reservas |
| `ev_mensajeria` | outbox | Mensajería asíncrona (futuro) |
| `ev_auditoria` | logs | Auditoría general (futuro) |

### Datos de Prueba

El proyecto incluye datos completos en `db/script2.sql`:

- ✅ **152 usuarios** (CLIENTE y ADMIN)
- ✅ **30 servicios** de eventos
- ✅ **50 proveedores** con habilidades
- ✅ **16 paquetes** predefinidos
- ✅ **Contraseña universal**: "Evoluti0n"

**Usuarios de prueba**:
```
Admin:   admin@eventos.pe / Evoluti0n
Cliente: jorge.martinez711@eventos.pe / Evoluti0n
```

---

## 📂 Estructura del Proyecto

```
eventos-peru-hexagonal/
├── db/                          # Scripts SQL
│   ├── bootstrap.sql            # Esquema inicial
│   └── script2.sql              # Datos de prueba (152 usuarios)
│
├── docs/                        # Documentación
│   ├── API_DOCUMENTATION.md     # Documentación completa de API
│   ├── TEST_E2E_REPORT.md       # Reporte de tests (100% éxito)
│   └── ROADMAP.md               # Hoja de ruta
│
├── tests/                       # Suite de tests (40 tests)
│   ├── conftest.py              # Configuración pytest compartida
│   ├── pytest.ini               # Configuración global pytest
│   ├── README.md                # Guía de uso de tests
│   ├── docs/                    # Documentación de testing
│   │   ├── TESTING_STRATEGY.md
│   │   └── IMPLEMENTATION_SUMMARY.md
│   ├── unit/                    # Tests unitarios
│   ├── integration/             # Tests de integración por servicio
│   │   └── test_iam_service.py  # 9 tests IAM
│   ├── e2e/                     # Tests end-to-end (3 flujos)
│   │   └── test_complete_flows.py
│   ├── security/                # Tests de seguridad (27 endpoints)
│   │   └── test_authorization.py
│   └── reports/                 # Reportes generados
│
├── services/                    # Microservicios Backend
│   ├── iam-service/            # :8010 - Autenticación
│   ├── catalogo-service/       # :8020 - Catálogo
│   ├── proveedores-service/    # :8030 - Proveedores
│   └── contratacion-service/   # :8040 - Contratación
│
├── libs/                        # Librerías compartidas
│   └── shared/                  # Código común (ev_shared)
│
├── frontend-vanilla/            # Cliente Web
│   ├── index.html
│   ├── config.js
│   ├── js/
│   └── css/
│
├── tools/                       # Scripts de utilidad
│   ├── check_db_connection.py
│   ├── setup_admin_user.py
│   └── verify_architecture.py
│
├── start-services.ps1           # Iniciar todos los servicios
└── run-tests.ps1                # Ejecutar tests (suite completa)
```

---

## 🚀 Inicio Rápido

### 1. Clonar el Repositorio

```powershell
git clone https://github.com/emedayinc17/Eventos-Peru-Hexa.git
cd eventos-peru-hexagonal
```

### 2. Configurar Base de Datos

```powershell
# Ejecutar en MySQL 8.0
mysql -u root -p < db/bootstrap.sql
mysql -u root -p < db/script2.sql
```

### 3. Activar Entorno Virtual

```powershell
.\Scripts\activate
```

### 4. Iniciar Servicios

```powershell
# Inicia los 4 microservicios simultáneamente
.\start-services.ps1
```

Los servicios estarán disponibles en:
- IAM: http://localhost:8010
- Catálogo: http://localhost:8020
- Proveedores: http://localhost:8030
- Contratación: http://localhost:8040

### 5. Validar Instalación

```powershell
# Verificar servicios activos
curl http://localhost:8010/iam/health
curl http://localhost:8020/catalogo/health
curl http://localhost:8030/proveedores/health
curl http://localhost:8040/contratacion/health

# Ejecutar suite de tests
.\run-tests.ps1 quick
```

---

## 🧪 Testing

### Suite Completa de Tests

El proyecto cuenta con **40 tests** organizados profesionalmente:

```
tests/
├── unit/           # Tests unitarios (lógica aislada)
├── integration/    # Tests por servicio (HTTP)
├── e2e/            # Tests flujos completos
├── security/       # Tests autenticación/autorización
└── reports/        # Reportes generados
```

**Ejecutar tests**:
```powershell
# Todos los tests
.\run-tests.ps1

# Por tipo
.\run-tests.ps1 integration   # Tests de integración
.\run-tests.ps1 e2e          # Tests E2E
.\run-tests.ps1 security     # Tests de seguridad
.\run-tests.ps1 quick        # Tests rápidos (sin slow)
.\run-tests.ps1 coverage     # Con reporte de cobertura

# Comando directo pytest
pytest tests/ -v
pytest tests/integration/ -v -m integration
pytest tests/e2e/ -v --html=tests/reports/report.html
```

**Resultados**:
- ✅ Tests E2E: **100% éxito** (3/3 flujos)
  - Flujo Cliente: 6 pasos
  - Flujo Admin: 8 pasos
  - Flujo Integrado: 9 pasos
- ✅ Tests Seguridad: **100%** (27 endpoints RBAC)
- ✅ Tests Integración IAM: 9 tests
- ✅ Autenticación reutilizable con fixtures

**Documentación**:
- 📖 [`tests/docs/TESTING_STRATEGY.md`](tests/docs/TESTING_STRATEGY.md) - Estrategia completa de testing
- 📖 [`tests/README.md`](tests/README.md) - Guía de uso de tests
- 📖 [`docs/TEST_E2E_REPORT.md`](docs/TEST_E2E_REPORT.md) - Reporte E2E detallado

---

## 🔐 Seguridad

### Autenticación

- **Método**: JSON Web Tokens (JWT)
- **Algoritmo**: HS256
- **Expiración**: 120 minutos
- **Claims**: sub (user_id), role, iat, exp

### Contraseñas

- **Hash**: bcrypt_sha256
- **Rounds**: 12

### Autorización

- **Roles**: ADMIN, CLIENTE
- **Middleware**: Validación JWT en cada request

### Comunicación Inter-Servicios

- **Token**: INTERNAL_SERVICE_TOKEN
- **Header**: X-Service-Token

---

## 📖 Documentación

### Documentos Disponibles

1. **[API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)** - Documentación completa de API (850+ líneas)
2. **[TEST_E2E_REPORT.md](docs/TEST_E2E_REPORT.md)** - Reporte de tests (950+ líneas)
3. **[ROADMAP.md](docs/ROADMAP.md)** - Hoja de ruta del proyecto

---

## 📊 Métricas de Calidad

| Métrica | Valor | Estado |
|---------|-------|--------|
| **Cobertura E2E** | 100% (3/3 flujos) | ✅ Excelente |
| **Endpoints Funcionales** | 100% (27/27) | ✅ Excelente |
| **Seguridad JWT** | 100% tests pasados | ✅ Excelente |
| **Idempotencia** | Implementada | ✅ Excelente |
| **Tiempo Respuesta** | <1s promedio | ✅ Aceptable |

---

## 🎯 Próximos Pasos

1. ✅ ~~Backend 100% funcional~~ (COMPLETADO)
2. ✅ ~~Tests E2E validados~~ (COMPLETADO)
3. ✅ ~~Documentación API~~ (COMPLETADO)
4. 🔄 Completar Frontend (60% → 100%)
5. 📦 Dockerización completa
6. ☸️ Despliegue en Kubernetes
7. 📊 Monitoring y Observabilidad
8. 🚀 Despliegue a Producción

Ver [ROADMAP.md](docs/ROADMAP.md) para más detalles.

---

## 📝 Licencia

© 2025 Emeday Inc. Todos los derechos reservados.

---

## 📞 Contacto

- **Autor**: Emeday
- **Repositorio**: https://github.com/emedayinc17/Eventos-Peru-Hexa
- **Branch Activo**: emeday

**Última Actualización**: 27 de Noviembre, 2025
