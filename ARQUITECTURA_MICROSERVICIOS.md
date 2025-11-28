# 🏗️ Arquitectura de Microservicios - Eventos Peru

## 📊 Diagrama de Arquitectura Completa

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE (Navegador)                      │
│                                                             │
│  Accede a: http://localhost:5174                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTP Requests
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              🖥️  FRONTEND (Vue.js + Vite)                   │
│                  Puerto: 5174                               │
│                                                             │
│  - Vue 3.4 + TypeScript                                     │
│  - Pinia State Management                                   │
│  - Vue Router                                               │
│  - Axios Client                                             │
│                                                             │
│  Config: VITE_API_BASE_URL=/api                             │
│  Vite Proxy: /api -> http://localhost:8000/api             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Proxy Requests: /api/*
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           🚪 API GATEWAY (FastAPI)                          │
│                  Puerto: 8000                               │
│                                                             │
│  Rutas:                                                     │
│  ├─ /api/iam/*          → http://localhost:8010            │
│  ├─ /api/catalogo/*     → http://localhost:8020            │
│  ├─ /api/proveedores/*  → http://localhost:8030            │
│  └─ /api/contratacion/* → http://localhost:8040            │
│                                                             │
│  Features:                                                  │
│  - Request Proxying (httpx)                                 │
│  - CORS Middleware                                          │
│  - Health Checks                                            │
│  - Load Balancing (futuro)                                  │
└─────┬────────┬─────────┬─────────┬─────────────────────────┘
      │        │         │         │
      │        │         │         │
      ▼        ▼         ▼         ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐
│   IAM    │ │ Catálogo │ │Proveedor │ │  Contratación    │
│ Service  │ │ Service  │ │ Service  │ │    Service       │
│  :8010   │ │  :8020   │ │  :8030   │ │     :8040        │
│          │ │          │ │          │ │                  │
│ Domain:  │ │ Domain:  │ │ Domain:  │ │ Domain:          │
│ - Login  │ │ - Tipos  │ │ - Proveed│ │ - Pedidos        │
│ - Regist │ │ - Servic.│ │ - Contac.│ │ - Facturación    │
│ - JWT    │ │ - Paquete│ │ - Calif. │ │ - Disponibilidad │
│ - Users  │ │ - Catálog│ │          │ │                  │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────────────┘
     │            │            │            │
     │ SQLAlchemy │            │            │
     │            │            │            │
     ▼            ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐
│ ev_iam   │ │ev_catalog│ │ev_proveed│ │ ev_contratacion  │
│  MySQL   │ │  MySQL   │ │  MySQL   │ │     MySQL        │
│  :3306   │ │  :3306   │ │  :3306   │ │     :3306        │
└──────────┘ └──────────┘ └──────────┘ └──────────────────┘
```

---

## 🔄 Flujo de una Petición

### Ejemplo: Login de Usuario

```
1. Usuario ingresa credenciales en frontend (localhost:5174)
   ↓
2. Vue hace POST /api/iam/auth/login
   ↓
3. Vite proxy intercepta y redirige a http://localhost:8000/api/iam/auth/login
   ↓
4. API Gateway recibe en puerto 8000
   ↓
5. Gateway identifica ruta /api/iam/* y proxy a http://localhost:8010/auth/login
   ↓
6. IAM Service (8010) valida credenciales en BD ev_iam
   ↓
7. IAM genera JWT token y responde
   ↓
8. Gateway reenvía response al frontend
   ↓
9. Frontend guarda token en localStorage
   ↓
10. Usuario autenticado ✅
```

### Ejemplo: Listar Paquetes

```
1. Cliente hace GET /api/catalogo/paquetes
   ↓
2. Vite proxy → http://localhost:8000/api/catalogo/paquetes
   ↓
3. Gateway → http://localhost:8010/paquetes (Catálogo Service)
   ↓
4. Catálogo consulta BD ev_catalogo
   ↓
5. Response: Lista de paquetes en JSON
```

### Ejemplo: Crear Pedido (Con autenticación)

```
1. Cliente hace POST /api/contratacion/pedidos
   Headers: { Authorization: "Bearer <JWT>" }
   ↓
2. Vite proxy → http://localhost:8000/api/contratacion/pedidos
   ↓
3. Gateway → http://localhost:8040/pedidos (Contratación Service)
   ↓
4. Contratación valida JWT (usando JWT_SECRET compartido)
   ↓
5. Contratación llama a Catálogo Service para validar paquete
   ↓
6. Contratación crea pedido en BD ev_contratacion
   ↓
7. Response: Pedido creado con ID
```

---

## 🛠️ Configuración de Puertos

| Componente | Puerto | Descripción |
|------------|--------|-------------|
| Frontend (Vite) | **5174** | Interfaz Vue.js |
| API Gateway | **8000** | Punto de entrada único |
| IAM Service | **8010** | Autenticación y usuarios |
| Catálogo Service | **8020** | Tipos, servicios, paquetes |
| Proveedores Service | **8030** | Gestión de proveedores |
| Contratación Service | **8040** | Pedidos y facturación |
| MySQL Database | **3306** | 4 bases de datos separadas |

---

## 🚀 Iniciar Todo el Sistema

### Opción 1: Script Automatizado (Recomendado)

```powershell
# Desde la raíz del proyecto
.\start-services.ps1
```

Este script inicia en orden:
1. IAM Service (8010)
2. Catálogo Service (8020)
3. Proveedores Service (8030)
4. Contratación Service (8040)
5. **API Gateway (8000)** ← NUEVO

### Opción 2: Manual

```powershell
# Terminal 1: IAM
cd services\iam-service
.\run.bat

# Terminal 2: Catálogo
cd services\catalogo-service
.\run.bat

# Terminal 3: Proveedores
cd services\proveedores-service
.\run.bat

# Terminal 4: Contratación
cd services\contratacion-service
.\run.bat

# Terminal 5: Gateway
cd gateway
.\run.bat

# Terminal 6: Frontend
cd frontend
npm run dev
```

---

## ✅ Verificación de Servicios

### 1. Gateway Health Check
```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "services": {
    "iam": "http://127.0.0.1:8010",
    "catalogo": "http://127.0.0.1:8020",
    "proveedores": "http://127.0.0.1:8030",
    "contratacion": "http://127.0.0.1:8040"
  }
}
```

### 2. Verificar Servicios Individuales

```bash
# IAM
curl http://localhost:8010/docs

# Catálogo
curl http://localhost:8020/docs

# Proveedores
curl http://localhost:8030/docs

# Contratación
curl http://localhost:8040/docs
```

### 3. Probar Routing del Gateway

```bash
# Login (IAM)
curl -X POST http://localhost:8000/api/iam/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@eventos.com", "password": "admin123"}'

# Listar paquetes (Catálogo)
curl http://localhost:8000/api/catalogo/paquetes
```

---

## 🔒 Seguridad

### JWT Compartido
Todos los servicios usan el mismo `JWT_SECRET` definido en sus `.env`:
```
JWT_SECRET=dev-secret
```

**⚠️ IMPORTANTE:** En producción, usar un secret fuerte y gestionado por Vault.

### CORS
Gateway permite requests desde:
- `http://localhost:5173`
- `http://localhost:5174`
- `http://localhost:3000`

---

## 📈 Escalabilidad Futura

### Load Balancing
Puedes correr múltiples instancias de cada servicio:

```
Gateway (8000)
    ↓
IAM Service (8010, 8011, 8012) ← Round Robin
Catálogo (8020, 8021, 8022)
...
```

### Service Discovery
Integrar con **Consul** o **Eureka** para descubrimiento dinámico.

### API Gateway Avanzado
Migrar a **Kong**, **Traefik**, o **AWS API Gateway** para features como:
- Rate Limiting
- Authentication centralizada
- Monitoring y Analytics
- Caching

---

## 🐛 Troubleshooting

### Frontend no conecta al backend
1. Verificar que Gateway esté corriendo: `http://localhost:8000/health`
2. Verificar proxy en `vite.config.ts`: target debe ser `http://localhost:8000`
3. Revisar CORS en Gateway

### Gateway no conecta a servicios
1. Verificar que los 4 servicios estén corriendo en puertos correctos
2. Revisar logs del Gateway
3. Verificar `SERVICES` en `gateway/main.py`

### Error 401 Unauthorized
1. Verificar que JWT_SECRET sea el mismo en todos los servicios
2. Verificar que el token se esté enviando en headers
3. Revisar expiración del token

### Servicio no responde
1. Verificar logs del servicio específico
2. Verificar conexión a base de datos
3. Revisar `.env` del servicio

---

## 📚 Referencias

- [FastAPI Proxy](https://fastapi.tiangolo.com/)
- [HTTPX](https://www.python-httpx.org/)
- [Vite Proxy](https://vitejs.dev/config/server-options.html#server-proxy)
- [Microservices Patterns](https://microservices.io/patterns/apigateway.html)
