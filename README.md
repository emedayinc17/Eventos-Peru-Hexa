
## 📦 Estructura Kustomize Final (Frontend y Backend)

La carpeta `k8s/` en la raíz contiene la estructura real y recomendada para despliegues multi-entorno con Kustomize:

```plaintext
k8s/
	frontend/
		base/
			deployment.yaml
			service.yaml
			ingress.yaml
			kustomization.yaml
		overlays/
			dev/
				kustomization.yaml
			prod/
				kustomization.yaml
	backend/
		base/
			ingress/
				ingress.yaml
			namespace.yaml
			serviceaccount.yaml
			services/
				iam/
					deploy-svc.yaml
				catalogo/
					deploy-svc.yaml
				contratacion/
					deploy-svc.yaml
				proveedores/
					deploy-svc.yaml
				mysql/
					statefulset.yaml
					svc.yaml
					svc-headless.yaml
					configmap.yaml
					secret-root.yaml
					nodeport.yaml
			kustomization.yaml
		overlays/
			dev/
				kustomization.yaml
			prod/
				kustomization.yaml
```


**Ventajas:**
- Personalización de imágenes, dominios, réplicas y variables por entorno sin duplicar YAML.
- ArgoCD puede apuntar a `k8s/frontend/overlays/prod` o `k8s/backend/overlays/prod` según el entorno.
- Estructura clara: cada microservicio backend tiene su subcarpeta bajo `services/`.

**Ejemplo de kustomization.yaml para backend/base:**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: eventos-peru

resources:
	- namespace.yaml
	- serviceaccount.yaml
	- ingress/ingress.yaml
	- services/iam/deploy-svc.yaml
	- services/catalogo/deploy-svc.yaml
	- services/contratacion/deploy-svc.yaml
	- services/proveedores/deploy-svc.yaml
	- services/mysql/statefulset.yaml
	- services/mysql/svc.yaml
	- services/mysql/svc-headless.yaml
	- services/mysql/configmap.yaml
	- services/mysql/secret-root.yaml
	- services/mysql/nodeport.yaml
```

**Ejemplo de Ingress (API Gateway):**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
	name: eventos-api
	namespace: eventos-peru
spec:
	ingressClassName: public
	rules:
		- host: eventos.emeday.inc
			http:
				paths:
					- path: /api/iam
						pathType: Prefix
						backend:
							service:
								name: iam-service
								port:
									number: 8010
					- path: /api/catalogo
						pathType: Prefix
						backend:
							service:
								name: catalogo-service
								port:
									number: 8020
					- path: /api/proveedores
						pathType: Prefix
						backend:
							service:
								name: proveedores-service
								port:
									number: 8030
					- path: /api/contratacion
						pathType: Prefix
						backend:
							service:
								name: contratacion-service
								port:
									number: 8040
```

**Frontend:**
- Se expone en la raíz del dominio (`/`).
- Backend accesible bajo `/api/{servicio}`.

---


# Eventos Perú Hexagonal

Plataforma moderna y componible para la gestión integral de eventos y contrataciones, basada en **microservicios** (FastAPI, Python 3.12+) y un **frontend SPA** profesional (Vue 3 + Vite + TypeScript + TailwindCSS). Arquitectura hexagonal, despliegue en Docker/Kubernetes, APIs seguras y test automáticos.

---

## 🚀 Propuesta de Valor

- **Microservicios desacoplados**: IAM, Catálogo, Proveedores, Contratación.
- **Frontend SPA**: Vue 3, TypeScript, Vite, Pinia, TailwindCSS.
- **API Gateway**: FastAPI, httpx, CORS, proxy seguro.
- **Pruebas y seguridad**: Unitarias, funcionales, integración, rendimiento, pentesting, RBAC, DoS, CORS, inyección.
- **Despliegue**: Docker, docker-compose, Kubernetes (manifests incluidos).
- **Documentación y scripts**: Todo centralizado en `docs/` y `tools/`.

---

## 🏗️ Arquitectura General (Diagrama)

```
┌──────────────────────────────────────────────────────────────┐
│                    CLIENTE (Navegador)                      │
│                                                             │
│  Accede a: http://localhost:5174                            │
└───────────────┬──────────────────────────────────────────────┘
								│
								│ HTTP Requests
								▼
┌──────────────────────────────────────────────────────────────┐
│              🖥️  FRONTEND (Vue 3 + Vite)                    │
│                  Puerto: 5174                               │
│  - Vue 3.4 + TypeScript, Pinia, Vue Router, TailwindCSS     │
│  - Axios, JWT, Guards, Vite Proxy                           │
└───────────────┬──────────────────────────────────────────────┘
								│
								│ Proxy: /api/*
								▼
┌──────────────────────────────────────────────────────────────┐
│           🛡️ API GATEWAY (FastAPI, httpx, CORS)             │
│                  Puerto: 8000                               │
│  - /api/iam            → IAM Service (8010)                 │
│  - /api/catalogo       → Catálogo Service (8020)            │
│  - /api/proveedores    → Proveedores Service (8030)         │
│  - /api/contratacion   → Contratación Service (8040)        │
└─────┬─────┬─────┬─────┬─────────────────────────────────────┘
			│     │     │     │
			▼     ▼     ▼     ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌────────────────────┐
│ IAM   │ │Catálogo│ │Proveedor│ │  Contratación    │
│Service│ │Service │ │Service  │ │    Service       │
│:8010  │ │:8020   │ │:8030    │ │     :8040        │
└───────┘ └───────┘ └───────┘ └────────────────────┘
			│     │     │     │
			▼     ▼     ▼     ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌────────────────────┐
│ ev_iam│ │ev_catalog│ │ev_proveed│ │ ev_contratacion  │
│ MySQL │ │ MySQL   │ │ MySQL   │ │     MySQL        │
│ :3306 │ │ :3306   │ │ :3306   │ │     :3306        │
└───────┘ └───────┘ └───────┘ └────────────────────┘
```

---

## 📂 Estructura del Repositorio

```plaintext
eventos-peru-hexagonal/
├── db/                 # Scripts SQL de inicialización y migración
├── deploy/             # Dockerfile, docker-compose, K8s manifests
├── docs/               # Documentación técnica y funcional
├── frontend/           # SPA Vue 3 + Vite (src/, views/, router/, stores/)
├── gateway/            # API Gateway (FastAPI)
├── libs/               # Librerías compartidas (Python)
├── services/           # Microservicios backend (IAM, Catálogo, etc.)
├── tests/              # Pruebas: software y seguridad
├── tools/              # Scripts utilitarios y E2E
└── start-services.ps1  # Orquestador local (PowerShell)
```

---

## 🧩 Microservicios y Componentes

### 1. IAM Service (Identidad y Acceso)
- **Puerto:** 8010
- **Responsabilidad:** Autenticación, JWT, usuarios, roles (RBAC), auditoría.
- **Endpoints:**
	- `POST /iam/auth/login` — Login (JWT)
	- `POST /iam/auth/register` — Registro
	- `GET /iam/me` — Perfil usuario
	- `GET /iam/admin/users` — Listar usuarios (ADMIN)
	- `PATCH /iam/admin/users/{id}` — Actualizar usuario
	- `DELETE /iam/admin/users/{id}` — Eliminar usuario
- **Seguridad:** JWT HS256, bcrypt, auditoría en tabla `audit_log`.

### 2. Catálogo Service
- **Puerto:** 8020
- **Responsabilidad:** Tipos de evento, servicios, opciones, paquetes.
- **Endpoints:**
	- `GET /catalogo/v1/tipos-evento` — Listar tipos de evento
	- `GET /catalogo/v1/servicios?tipo_evento_id=...` — Servicios por tipo
	- `GET /catalogo/v1/opciones-servicio?servicio_id=...` — Opciones + precio
	- `GET /catalogo/v1/paquetes` — Listar paquetes
	- `GET /catalogo/v1/paquetes/{id}` — Detalle paquete

### 3. Proveedores Service
- **Puerto:** 8030
- **Responsabilidad:** Proveedores, habilidades, disponibilidad, holds.
- **Endpoints:**
	- `GET /proveedores/v1/proveedores/disponibles?servicio_id=...&fecha=...` — Buscar proveedores disponibles
	- `POST /proveedores/internal/holds` — Crear hold (interno)
	- `PATCH /proveedores/internal/holds/{hold_id}/confirm` — Confirmar hold
	- `DELETE /proveedores/internal/holds/{hold_id}` — Liberar hold

### 4. Contratación Service
- **Puerto:** 8040
- **Responsabilidad:** Pedidos, reservas, asignación de proveedores.
- **Endpoints:**
	- `POST /contratacion/pedidos` — Crear pedido (paquete/custom)
	- `GET /contratacion/pedidos/mios` — Pedidos del cliente
	- `GET /contratacion/pedidos/{id}` — Detalle pedido
	- `GET /contratacion/admin/pedidos` — Listar todos (ADMIN)
	- `PATCH /contratacion/admin/pedidos/{id}` — Cambiar estado
	- `POST /contratacion/admin/pedidos/{id}/asignar-proveedor` — Asignar proveedor

### 5. API Gateway
- **Puerto:** 8000
- **Responsabilidad:** Proxy seguro, CORS, health, logging.
- **Rutas:** `/api/iam/*`, `/api/catalogo/*`, `/api/proveedores/*`, `/api/contratacion/*`

### 6. Frontend SPA (Vue 3 + Vite)
- **Puerto dev:** 5174
- **Stack:** Vue 3, TypeScript, Vite, Pinia, Vue Router, TailwindCSS, Axios
- **Vistas:**
	- **Público:** Home, Login, Paquetes, Proveedores
	- **Cliente:** Dashboard, Paquetes, Crear Pedido (Wizard), Mis Pedidos, Perfil
	- **Admin:** Dashboard, Tipos Evento, Servicios, Paquetes, Proveedores, Pedidos, Usuarios
- **Guards:** Autenticación y roles (CLIENTE, ADMIN)

---

## 🔄 Flujo de Usuario (Texto + Diagrama)

### Camino A: Pedido desde Paquete
```
1. Cliente inicia sesión (POST /iam/auth/login)
2. Ve catálogo de paquetes (GET /catalogo/v1/paquetes)
3. Elige paquete y crea pedido (POST /contratacion/pedidos { paquete_id })
4. Consulta estado de su pedido (GET /contratacion/pedidos/mios)
5. Admin puede ver todos los pedidos y asignar proveedor
```

### Camino B: Pedido Custom (por servicios)
```
1. Cliente inicia sesión (POST /iam/auth/login)
2. Ve tipos de evento y servicios (GET /catalogo/v1/tipos-evento, /servicios)
3. Elige servicios y opciones, arma pedido custom
4. Crea pedido (POST /contratacion/pedidos { items: [...] })
5. Consulta estado de su pedido (GET /contratacion/pedidos/mios)
```

---

## 🛡️ Seguridad y Pruebas

- **JWT**: Autenticación y autorización en todos los servicios
- **RBAC**: Roles ADMIN y CLIENTE
- **Contraseñas**: bcrypt, rounds=12
- **CORS**: Configurado en gateway y servicios
- **Pruebas**: Unitarias, funcionales, integración, rendimiento (k6), seguridad (Bandit, Trivy, pentesting, DoS, inyección)
- **Precaución**: No ejecutar pruebas intrusivas en producción

---

## 🛠️ Quickstart (Desarrollo Local)

1. Clonar el repositorio:
	 ```bash
	 git clone <repo-url>
	 cd eventos-peru-hexagonal
	 ```
2. Levantar servicios con Docker Compose:
	 ```bash
	 docker-compose -f deploy/docker-compose.yml up --build -d
	 ```
3. Iniciar frontend en modo desarrollo:
	 ```bash
	 cd frontend
	 npm install
	 npm run dev
	 # Accede a http://localhost:5174
	 ```
4. Ejecutar pruebas:
	 ```bash
	 python -m venv .venv
	 .\.venv\Scripts\Activate.ps1
	 pip install -r tests/requirements.txt
	 pytest tests/PRUEBAS_DE_SOFTWARE/funcionales -q
	 ```

---

## 📚 Documentación y Recursos

- Documentación técnica y funcional: [`docs/`](docs/)
- Diagramas y arquitectura: [`docs/ARQUITECTURA_MICROSERVICIOS.md`](docs/ARQUITECTURA_MICROSERVICIOS.md)
- Lógica de implementación: [`docs/LOGICA_IMPLEMENTACION.md`](docs/LOGICA_IMPLEMENTACION.md)
- Propuesta frontend: [`docs/propuesta_frontend.md`](docs/propuesta_frontend.md)
- Roadmap y fixes: [`docs/ROADMAP.md`](docs/ROADMAP.md), [`docs/FIXES_LOG.md`](docs/FIXES_LOG.md)

---

## 🤝 Contribuir

- Abre un issue para cambios grandes
- Haz PRs pequeños y atómicos, con tests
- Mantén backwards-compatibility y documenta breaking changes

---

© 2025 Emeday Inc. Todos los derechos reservados.


