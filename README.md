# Eventos Per� - Arquitectura Hexagonal (Microservicios)

**Autor:** Emeday@2025  
**Versi�n:** Phase 3 Complete  
**Estado:** En Desarrollo Activo

Este proyecto implementa un sistema de gesti�n de eventos utilizando una **Arquitectura Hexagonal** (Puertos y Adaptadores) distribuida en microservicios. El objetivo es desacoplar la l�gica de negocio de los detalles de infraestructura, permitiendo escalabilidad y mantenibilidad.

---

##  Prerrequisitos

Para ejecutar este proyecto localmente, necesitas tener instalado:

1.  **Python 3.12+**: Lenguaje base para todos los microservicios.
2.  **MySQL 8.0**: Base de datos relacional principal.
3.  **PowerShell**: Para la orquestaci�n de servicios en entorno Windows.
4.  **Docker & Kubernetes (Opcional)**: Para despliegue en contenedores.

---

##  Arquitectura del Sistema

El sistema est� dividido en 4 microservicios principales, cada uno con su propia responsabilidad y esquema de base de datos (aunque comparten instancia f�sica en desarrollo):

### 1. IAM Service (Identidad y Acceso)
*   **Puerto:** `8010`
*   **Responsabilidad:** Gesti�n de usuarios, roles, autenticaci�n (JWT) y auditor�a.
*   **Endpoints Clave:**
    *   `POST /iam/auth/login`: Inicio de sesi�n y generaci�n de tokens.
    *   `POST /iam/auth/register`: Registro de nuevos usuarios.
    *   `GET /iam/users/me`: Perfil del usuario actual.

### 2. Cat�logo Service
*   **Puerto:** `8020`
*   **Responsabilidad:** Gesti�n de servicios ofrecidos, paquetes y precios.
*   **Endpoints Clave:**
    *   `GET /catalogo/servicios`: Listado de servicios disponibles.
    *   `GET /catalogo/paquetes`: Paquetes predefinidos para eventos.
    *   `GET /catalogo/paquetes/{id}`: Detalle de un paquete espec�fico.

### 3. Proveedores Service
*   **Puerto:** `8030`
*   **Responsabilidad:** Gesti�n de proveedores externos, sus habilidades y disponibilidad.
*   **Endpoints Clave:**
    *   `GET /proveedores`: B�squeda de proveedores.
    *   `GET /proveedores/{id}/disponibilidad`: Verificar calendario.
    *   `POST /proveedores/reservas-temporales`: Bloqueo temporal de agenda (Holds).

### 4. Contrataci�n Service
*   **Puerto:** `8040`
*   **Responsabilidad:** Core del negocio. Gesti�n de pedidos, cotizaciones y reservas finales.
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
##  Despliegue y Ejecuci�n

### 1. Configuraci�n de Base de Datos
El proyecto incluye scripts SQL para inicializar la estructura y datos de prueba.
*   **Script Principal:** `db/bootstrap.sql` (Ejecutar en MySQL 8).
*   **Credenciales por defecto:** Ver `docs/TEST_DATA.md`.

### 2. Ejecuci�n Local (Windows)
Utilizamos un script de PowerShell para orquestar el inicio de todos los servicios simult�neamente.

```powershell
.\start-services.ps1
```
Este script:
1.  Activa el entorno virtual de Python.
2.  Inicia cada microservicio en su puerto correspondiente.
3.  Muestra logs en ventanas separadas.

### 3. Docker y Contenedores
La estrategia de contenedorizaci�n se encuentra en la carpeta `deploy/`.
*   **Dockerfile.api**: Definici�n base para las im�genes de los servicios Python.
*   **docker-compose.yml**: Orquestaci�n local de contenedores (Base de datos + Servicios).

### 4. Kubernetes (K8s)
El despliegue en Kubernetes est� dise�ado para alta disponibilidad.
*   Los manifiestos se encuentran en `frontend-vanilla/k8s/` y `deploy/k8s/` (en desarrollo).
*   Se utiliza **Ingress** para enrutar el tr�fico a los diferentes servicios bas�ndose en el path (`/iam`, `/catalogo`, etc.).

---

##  Frontend
El proyecto incluye un frontend en Vanilla JS (`frontend-vanilla/`) que consume estos microservicios.
*   **Tecnolog�a:** HTML5, CSS3, JS (ES6+).
*   **Configuraci�n:** `config.js` define las URLs base de los microservicios.
*   **Ejecuci�n:** Puede servirse con cualquier servidor est�tico (ej. Live Server, Nginx).

---

##  Seguridad
*   **Autenticaci�n:** Basada en Tokens JWT (JSON Web Tokens).
*   **Contrase�as:** Almacenamiento seguro utilizando hashing (Bcrypt).
*   **CORS:** Configurado para permitir peticiones desde el frontend autorizado.
*   **Nota:** No se exponen credenciales reales en este repositorio. Consulte `docs/TEST_DATA.md` para cuentas de prueba en entorno local.

---

 2025 Emeday Inc. Todos los derechos reservados.
