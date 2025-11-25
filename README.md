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
*   **Puerto:** `8010`
*   **Responsabilidad:** Gestión de usuarios, roles, autenticación (JWT) y auditoría.
*   **Endpoints Clave:**
    *   `POST /iam/auth/login`: Inicio de sesión y generación de tokens.
    *   `POST /iam/auth/register`: Registro de nuevos usuarios.
    *   `GET /iam/users/me`: Perfil del usuario actual.

### 2. Catálogo Service
*   **Puerto:** `8020`
*   **Responsabilidad:** Gestión de servicios ofrecidos, paquetes y precios.
*   **Endpoints Clave:**
    *   `GET /catalogo/servicios`: Listado de servicios disponibles.
    *   `GET /catalogo/paquetes`: Paquetes predefinidos para eventos.
    *   `GET /catalogo/paquetes/{id}`: Detalle de un paquete específico.

### 3. Proveedores Service
*   **Puerto:** `8030`
*   **Responsabilidad:** Gestión de proveedores externos, sus habilidades y disponibilidad.
*   **Endpoints Clave:**
    *   `GET /proveedores`: Búsqueda de proveedores.
    *   `GET /proveedores/{id}/disponibilidad`: Verificar calendario.
    *   `POST /proveedores/reservas-temporales`: Bloqueo temporal de agenda (Holds).

### 4. Contratación Service
*   **Puerto:** `8040`
*   **Responsabilidad:** Core del negocio. Gestión de pedidos, cotizaciones y reservas finales.
*   **Endpoints Clave:**
    *   `POST /contratacion/pedidos`: Crear un nuevo pedido de evento.
    *   `GET /contratacion/pedidos/mis-pedidos`: Historial del cliente.
    *   `PUT /contratacion/pedidos/{id}/estado`: Transiciones de estado (Draft -> Cotizado -> Aprobado -> Asignado).

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
