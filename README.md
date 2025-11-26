# Eventos Perú - Arquitectura Hexagonal (Microservicios)

**Autor:** Emeday@2025  
**Versión:** Phase 3 Complete  
**Estado:** En Desarrollo Activo

Este proyecto implementa un sistema de gestión de eventos utilizando una **Arquitectura Hexagonal** (Puertos y Adaptadores) distribuida en microservicios. El objetivo es desacoplar la lógica de negocio de los detalles de infraestructura, permitiendo escalabilidad y mantenibilidad.

---

## 📋 Prerrequisitos

Para ejecutar este proyecto localmente, necesitas tener instalado:

1.  **Python 3.12+**: Lenguaje base para todos los microservicios.
2.  **MySQL 8.0**: Base de datos relacional principal.
3.  **PowerShell**: Para la orquestación de servicios en entorno Windows.
4.  **Docker & Kubernetes (Opcional)**: Para despliegue en contenedores.

---

## 🏗️ Arquitectura del Sistema

El sistema está dividido en 4 microservicios principales, cada uno con su propia responsabilidad y esquema de base de datos (aunque comparten instancia física en desarrollo):

### 1. IAM Service (Identidad y Acceso)
*   **Puerto (dev):** `8010`
*   **Responsabilidad:** Gestión de usuarios, roles, autenticación (JWT) y auditoría.
*   **Endpoints (ejecutables en el servicio):**
    - `GET  /health` — Health check (público)
    - `POST /auth/login` — Login: recibe { email, password } y devuelve token (access_token)
    - `POST /auth/register` — Registro público: crea usuario
    - `GET  /me` — Perfil del usuario autenticado (Authorization: Bearer <token>)
    - `GET  /admin/users` — Listar usuarios (ADMIN)
    - `GET  /admin/users/{id}` — Obtener usuario por id (ADMIN)
    - `POST /admin/users` — Crear usuario (ADMIN)
    - `PATCH /admin/users/{id}` — Actualizar usuario (ADMIN). Acepta password para cambio.
    - `DELETE /admin/users/{id}` — Eliminar usuario (ADMIN)
    
    Nota: las rutas internas del servicio son las mostradas arriba; cuando se expone públicamente vía Ingress puede añadirse un prefijo por servicio (ej. `/iam`).

### 2. Catálogo Service
*   **Puerto (dev):** `8020`
*   **Responsabilidad:** Gestión de servicios ofrecidos, paquetes y precios.
*   **Endpoints (servicio):**
    - `GET  /health` — Health check (público)
    - `GET  /v1/catalogo/tipos` — Listado de tipos de evento
    - `GET  /v1/catalogo/servicios` — Listado de servicios (filtros: `tipo_evento_id`, pagination)
    - `GET  /v1/catalogo/opciones` — Opciones de un servicio (`servicio_id` requerido)
    - `GET  /v1/catalogo/paquetes` — Listado de paquetes
    - `GET  /v1/catalogo/paquetes/{id}` — Detalle de paquete (items, precios, proveedores)

    Nota: los paths incluyen el prefijo `/v1` en el contrato actual del servicio.

### 3. Proveedores Service
*   **Puerto (dev):** `8030`
*   **Responsabilidad:** Gestión de proveedores, habilidades y disponibilidad.
*   **Endpoints públicos:**
    - `GET /health` — Health check (público)
    - `GET /v1/proveedores/disponibles?servicio_id={id}&fecha={YYYY-MM-DD}` — Buscar proveedores disponibles (público)

*   **Endpoints internos (requieren `X-Service-Token`):**
    - `POST   /internal/holds` — Crear hold (reserva temporal). Req body: proveedor_id, opcion_servicio_id, inicio, fin, ttl_min, correlation_id
    - `PATCH  /internal/holds/{hold_id}/confirm` — Confirmar hold
    - `DELETE /internal/holds/{hold_id}` — Liberar hold (204 No Content)
    - `GET    /internal/holds/{hold_id}` — Consultar estado del hold

    Importante: los endpoints de `internal` requieren el header `X-Service-Token` con el token compartido entre servicios (no son públicos ni accesibles desde navegador).

### 4. Contratación Service
*   **Puerto (dev):** `8040`
*   **Responsabilidad:** Gestión de pedidos (cotizaciones, reservas, asignación de proveedores).
*   **Endpoints (servicio):**
        - `GET  /health` — Health check (público)
        - `POST /pedidos` — Crear pedido (autenticado). El body admite `paquete_id` (crear desde paquete) o `items` (custom). Retorna 201 con el pedido creado.
        - `GET  /pedidos/mios` — Listar pedidos del cliente autenticado (autenticado)
        - `GET  /pedidos/{pedido_id}` — Detalle del pedido (autenticado, ownership check)
        - `POST /v1/contratacion/pedidos/{pedido_id}/enviar-resumen` — Endpoint deferred para envío de resumen (202 Accepted)

*   **Endpoints ADMIN (requieren rol ADMIN):**
        - `GET  /admin/pedidos` — Listar todos los pedidos (ADMIN)
        - `PATCH /admin/pedidos/{pedido_id}` — Cambiar estado del pedido (ADMIN)
        - `POST  /admin/pedidos/{pedido_id}/items` — Agregar items (pendiente/DEFERRED)
        - `DELETE /admin/pedidos/{pedido_id}/items` — Eliminar items (pendiente/DEFERRED)
        - `POST  /admin/pedidos/{pedido_id}/asignar-proveedor` — Asignar proveedor a item (integra con Proveedores, crea/valida holds)
        - `GET /admin/pedidos/{pedido_id}` — Detalle para ADMIN (sin ownership check)

        Nota: el método para cambiar estado en el código es `PATCH` (no `PUT`).

---

## 📌 Observaciones sobre rutas y despliegue
- Los routers de los servicios exponen rutas internas (ej. `/v1/catalogo/...`, `/auth/...`, `/internal/holds`). Cuando se despliegan en Kubernetes normalmente se usa un Ingress que puede mapear un path público (ej. `/catalogo`) hacia el servicio correspondiente. Documentamos aquí las rutas internas tal como están implementadas en el código; el Ingress puede reescribirlas.
- Los endpoints internos (prefijo `/internal`) requieren `X-Service-Token` y no deben ser consumidos por el navegador directamente.
- Autenticación para endpoints protegidos: usar `Authorization: Bearer <JWT>`; el JWT lo emite `POST /auth/login` del IAM.

## 🛠️ Recomendaciones rápidas para despliegue del frontend (ConfigMap)
El `frontend-vanilla/config.js` es la única pieza que el frontend lee en tiempo de ejecución para conocer las URLs de los microservicios. En Kubernetes conviene montar un `ConfigMap` con ese archivo para apuntar a los servicios internos:

Ejemplo `config.prod.js` (crear localmente y añadir a ConfigMap):
```javascript
window.IAM_API_BASE = window.IAM_API_BASE || "http://iam-service:8010/iam";
window.API_BASE = window.API_BASE || window.IAM_API_BASE;
window.CATALOGO_API_BASE = window.CATALOGO_API_BASE || "http://catalogo-service:8020/catalogo";
window.PROVEEDORES_API_BASE = window.PROVEEDORES_API_BASE || "http://proveedores-service:8030/proveedores";
window.CONTRATACION_API_BASE = window.CONTRATACION_API_BASE || "http://contratacion-service:8040/contratacion";
// Quicklogin: solo para dev
window.QUICKLOGIN_CLIENT_EMAIL = window.QUICKLOGIN_CLIENT_EMAIL || "demo@eventos.pe";
window.QUICKLOGIN_CLIENT_PASSWORD = window.QUICKLOGIN_CLIENT_PASSWORD || "Admin_2025!";
```

Crear ConfigMap y montarlo en el Pod (ejemplo PowerShell):
```powershell
kubectl create configmap frontend-config --from-file=config.js=./config.prod.js -n my-namespace
```

Ejemplo de `Deployment` (fragmento) para montar el archivo en nginx:
```yaml
volumes:
    - name: frontend-config
        configMap:
            name: frontend-config
            items:
                - key: config.js
                    path: config.js

containers:
    - name: frontend
        image: my-nginx-frontend:latest
        volumeMounts:
            - name: frontend-config
                mountPath: /usr/share/nginx/html/config.js
                subPath: config.js
```

En nginx conviene desactivar caching para `config.js` para que cambios de configuración sean visibles inmediatamente:
```
location = /config.js {
    add_header Cache-Control "no-store, must-revalidate";
}
```

## 🔐 CORS y seguridad (resumen)
- Los servicios deben aceptar preflight OPTIONS y permitir el header `Authorization` para que el frontend pueda enviar JWT.
- Para endpoints internos usar `X-Service-Token` y validar en middleware (ya implementado en Proveedores internal).
- En producción usar HTTPS y no exponer `QUICKLOGIN` ni credenciales en `config.js`.

## 📎 Contratos y OpenAPI
- Algunos servicios incluyen contratos OpenAPI en `services/*/app/entrypoints/fastapi/contracts/openapi.yaml` — úsalos para generar documentación automática o clientes.

---

Si quieres, puedo añadir ahora una tabla completa (método / path / auth / descripción) en el README para cada endpoint y pegar ejemplos curl para los endpoints críticos (login, crear pedido, buscar proveedores, crear hold interno). ¿Lo genero ahora? 

---

## 📂 Estructura del Proyecto

El repositorio está organizado para separar claramente el backend, frontend, infraestructura y documentación.

```plaintext
eventos-peru-hexagonal/
├── db/                 # Scripts SQL de inicialización y migración
├── deploy/             # Configuraciones de Docker y Kubernetes
├── docs/               # Documentación del proyecto (Roadmap, Test Data)
├── frontend-vanilla/   # Cliente Web (HTML/JS/CSS)
│   ├── css/            # Estilos (Bootstrap + Custom)
│   ├── js/             # Lógica de cliente (API, Auth, App)
│   └── config.js       # Configuración de endpoints
├── libs/               # Librerías compartidas (Python)
│   └── shared/         # Código común entre microservicios
├── services/           # Microservicios Backend
│   ├── catalogo-service/
│   ├── contratacion-service/
│   ├── iam-service/
│   └── proveedores-service/
├── tools/              # Scripts de utilidad y validación
└── start-services.ps1  # Script de orquestación local
```

---

## 🚀 Despliegue y Ejecución

### 1. Configuración de Base de Datos
El proyecto incluye scripts SQL para inicializar la estructura y datos de prueba.
*   **Script Principal:** `db/bootstrap.sql` (Ejecutar en MySQL 8).
*   **Credenciales por defecto:** Ver `docs/TEST_DATA.md`.

### 2. Ejecución Local (Windows)
Utilizamos un script de PowerShell para orquestar el inicio de todos los servicios simultáneamente.

```powershell
.\start-services.ps1
```
Este script:
1.  Activa el entorno virtual de Python.
2.  Inicia cada microservicio en su puerto correspondiente.
3.  Muestra logs en ventanas separadas.

### 3. Docker y Contenedores
La estrategia de contenedorización se encuentra en la carpeta `deploy/`.
*   **Dockerfile.api**: Definición base para las imágenes de los servicios Python.
*   **docker-compose.yml**: Orquestación local de contenedores (Base de datos + Servicios).

### 4. Kubernetes (K8s)
El despliegue en Kubernetes está diseñado para alta disponibilidad.
*   Los manifiestos se encuentran en `frontend-vanilla/k8s/` y `deploy/k8s/` (en desarrollo).
*   Se utiliza **Ingress** para enrutar el tráfico a los diferentes servicios basándose en el path (`/iam`, `/catalogo`, etc.).

---

## 🌐 Frontend
El proyecto incluye un frontend en Vanilla JS (`frontend-vanilla/`) que consume estos microservicios.
*   **Tecnología:** HTML5, CSS3, JS (ES6+).
*   **Configuración:** `config.js` define las URLs base de los microservicios.
*   **Ejecución:** Puede servirse con cualquier servidor estático (ej. Live Server, Nginx).

---

## 🔒 Seguridad
*   **Autenticación:** Basada en Tokens JWT (JSON Web Tokens).
*   **Contraseñas:** Almacenamiento seguro utilizando hashing (Bcrypt).
*   **CORS:** Configurado para permitir peticiones desde el frontend autorizado.
*   **Nota:** No se exponen credenciales reales en este repositorio. Consulte `docs/TEST_DATA.md` para cuentas de prueba en entorno local.

---

© 2025 Emeday Inc. Todos los derechos reservados.
