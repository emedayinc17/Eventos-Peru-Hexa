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

---

## 🔒 Seguridad

### JWT Compartido
Todos los servicios usan el mismo `JWT_SECRET` definido en sus `.env`:
```
JWT_SECRET=dev-secret
```

**⚠️ IMPORTANTE:** En producción, usar un secret fuerte y gestionado por Vault.

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

---

## 🐛 Troubleshooting

### Frontend no conecta al backend
1. Verificar que Gateway esté corriendo: `http://localhost:8000/health`
2. Verificar proxy en `vite.config.ts`: target debe ser `http://localhost:8000`
3. Revisar CORS en Gateway

---

## 📚 Referencias

- [FastAPI Proxy](https://fastapi.tiangolo.com/)
- [HTTPX](https://www.python-httpx.org/)
- [Vite Proxy](https://vitejs.dev/config/server-options.html#server-proxy)
- [Microservices Patterns](https://microservices.io/patterns/apigateway.html)
