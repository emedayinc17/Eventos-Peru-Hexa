% Resumen Final: Proyecto Eventos-Perú (Hexagonal)

Fecha: 27-11-2025

Resumen: este documento recoge la planificación, arquitectura, diseño, pruebas, despliegue y mantenimiento del proyecto "Eventos-Perú" (arquitectura hexagonal con microservicios y frontend en Vue3). Incluye diagramas, cuadros de decisión y propuestas para pruebas y operaciones.

--

**Contenido**

- Planificación del proyecto
- Definición de objetivos y alcance
- Análisis de requerimientos
- Diseño de la arquitectura
- Tecnologías usadas
- Diagrama de clases
- Modelamiento de base de datos
- Implementación de patrones
- Arquitectura por capas
- Pruebas de software
  - Pruebas unitarias
  - Pruebas funcionales
  - Pruebas de integración
  - Pruebas de rendimiento
  - Pruebas de seguridad (penetración, vulnerabilidades, control de accesos)
- Plan de despliegue
- Plan de monitoreo
- Plan de mantenimiento
- Repositorio de código y control de versiones
- Reportes estadísticos

--

**1. Planificación del proyecto**

- Duración estimada: 4–6 semanas para primer release estable (features core + UX polish + tests automatizados). Despliegue + CI/CD: 1–2 semanas adicionales.
- Fases:
  1. Descubrimiento y levantamiento de requisitos (2–3 días).
  2. Implementación core frontend (Usuarios, Perfil, Catálogo) (3–5 días).
  3. UX & pruebas (1 semana).
  4. E2E y Playwright/CI (3–4 días).
  5. Docker/Despliegue y monitoreo (1–2 semanas).
  6. Buffer / Contingencias (1 semana).

**Métricas de éxito**
- 100% de endpoints críticos integrados con frontend.
- 90% de cobertura de flujos E2E automatizados.
- Tiempos de respuesta del frontend < 300ms en navegación estándar.

--

**2. Definición de objetivos y alcance**

Objetivo principal: Entregar un frontend unificado conectado al API Gateway que soporte flujos administrativos y de cliente (consulta catálogo, crear pedidos, gestionar pedidos y usuarios) sin tocar la lógica de backend.

Alcance (MVP):
- Frontend funcional para login (IAM), catálogo, CRUD TiposEvento/Servicios/Paquetes, Pedidos (cliente y admin), Usuarios (admin).
- Dev tooling: scripts de integración, E2E automatizados con Playwright.
- UX básico consistente: confirmaciones, toasts, modales y loading states.

Exclusiones en MVP: sistema de pagos, analytics avanzados, PWA completo, exportación avanzada de reportes.

--

**3. Análisis de requerimientos**

- Requerimientos funcionales (ejemplos):
  - Autenticación con IAM vía API Gateway.
  - Listar/filtrar TiposEvento, Servicios, Paquetes.
  - Crear/editar/cancelar Pedidos (cliente y admin) respetando las reglas del backend (PATCH para cambios de estado, cancelación por estado).
  - CRUD de Usuarios (admin) y edición de Perfil (cliente).

- Requerimientos no funcionales:
  - Respuesta <500ms para endpoints cacheables.
  - 99% uptime del API Gateway en entorno de staging.
  - Mecanismos de logging centralizado y métricas tiempo real.

--

**4. Diseño de la arquitectura**

Descripción: Arquitectura de microservicios con API Gateway (FastAPI) que enruta a servicios (IAM, Catálogo, Contratación, Proveedores). Frontend SPA (Vue3 + Vite + TypeScript) consume el Gateway bajo prefijo `/api`.

Merits: separación de responsabilidades, despliegues independientes, escalabilidad por servicio.

Diagrama de alto nivel (Mermaid):

```mermaid
flowchart LR
  subgraph Frontend
    F[Vue3 App (Vite, Pinia, TS)]
  end
  subgraph Gateway[API Gateway (FastAPI)]
    GW[/api/*]
  end
  subgraph Services
    IAM[IAM Service]
    CAT[Catálogo Service]
    CONTR[Contratación Service]
    PROV[Proveedores Service]
  end
  F -->|HTTP /api/*| GW --> IAM
  GW --> CAT
  GW --> CONTR
  GW --> PROV
  note right of CONTR: Versionado /v1 en endpoints
```

Detalles operativos:
- Vite dev proxy debe preservar prefijo `/api` para evitar reescrituras que generan `/api/api/...` y 404.
- Normalización de contratos en cliente: mapear `monto_total_vigente`/`monto_total` a `precio_base` para la UI.

--

**5. Tecnologías usadas**

- Frontend: Vue 3, Vite, TypeScript, Pinia, Vue Router, Tailwind CSS, Axios.
- Testing: Playwright (@playwright/test), pytest para scripts E2E / integración, herramientas internas (scripts Python).
- Backend (existente): FastAPI microservices (IAM, Catálogo, Contratación, Proveedores), PostgreSQL (asumido), gateway reverso.
- DevOps: Docker, docker-compose (propuesta), Kubernetes manifests (propuesta), Prometheus + Grafana para monitoreo.
- CI: GitHub Actions / Azure DevOps / GitLab CI (ejemplo) — pipelines para lint, build, test y deploy.

--

... (rest of migrated summary content preserved)
