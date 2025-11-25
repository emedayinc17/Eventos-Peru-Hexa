# IAM Service (Identity & Access Management)

Este microservicio es responsable de la gestión de identidades, autenticación y autorización dentro de la arquitectura de Eventos Perú. Implementa un diseño de **Arquitectura Hexagonal** para desacoplar la lógica de negocio de los detalles de infraestructura.

## 🏗 Arquitectura

El servicio sigue estrictamente los principios de Arquitectura Hexagonal (Ports & Adapters):

- **Domain**: Entidades y reglas de negocio puras (sin dependencias externas).
- **Application**: Casos de uso que orquestan la lógica de negocio.
- **Infrastructure**: Adaptadores para base de datos (MySQL), seguridad (JWT, Bcrypt) y frameworks web (FastAPI).
- **Entrypoints**: Controladores API (FastAPI Router).

## 🛠 Tech Stack

- **Lenguaje**: Python 3.12
- **Framework Web**: FastAPI + Uvicorn
- **Base de Datos**: MySQL 8.0
- **ORM**: SQLAlchemy (Core/ORM)
- **Seguridad**:
  - JWT (JSON Web Tokens) para autenticación stateless.
  - Bcrypt para hashing de contraseñas.
- **Validación**: Pydantic v2
- **Testing**: Pytest

## 📂 Estructura del Proyecto

```
iam-service/
├── app/
│   ├── application/       # Casos de uso (Login, Register, AdminUser...)
│   ├── domain/            # Puertos (Interfaces) y Excepciones
│   ├── entrypoints/       # API REST (FastAPI Routers & Schemas)
│   └── infrastructure/    # Adaptadores (MySQL Repo, JWT, Password)
├── test/                  # Pruebas automatizadas
├── Dockerfile             # Definición de contenedor
├── requirements.txt       # Dependencias Python
└── run.bat                # Script de ejecución local
```

## 🚀 Ejecución Local

### Prerrequisitos
- Python 3.12+
- MySQL corriendo (con el esquema `ev_iam` creado).
- Entorno virtual activado.

### Pasos
1. **Configurar variables de entorno**:
   Crea un archivo `.env` en la raíz del servicio (o usa las variables por defecto en `run.bat`).

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Iniciar el servicio**:
   ```bash
   .\run.bat
   ```
   El servicio estará disponible en `http://localhost:8010`.

## 🐳 Docker

El servicio está listo para ser contenerizado. El `Dockerfile` está optimizado para producción (usuario no-root, caché de capas).

### Construir Imagen
Desde la raíz del repositorio (para incluir librerías compartidas):

```bash
docker build -t iam-service:1.0.0 -f services/iam-service/Dockerfile .
```

### Ejecutar Contenedor
```bash
docker run -d -p 8010:8010 --name iam-service iam-service:1.0.0
```

## ✅ Testing

El proyecto incluye una suite completa de pruebas unitarias y de integración.

### Ejecutar Pruebas
```bash
cd services/iam-service
pytest test/test_iam_service.py
```

### Generar Reporte HTML
```bash
pytest test/test_iam_service.py --html=test/report_iam.html --self-contained-html
```

## 🔌 Endpoints Principales

| Método | Ruta | Descripción | Rol Requerido |
|--------|------|-------------|---------------|
| GET | `/health` | Health check | Público |
| POST | `/auth/login` | Iniciar sesión (retorna JWT) | Público |
| POST | `/auth/register` | Registrar nuevo usuario | Público |
| GET | `/me` | Perfil del usuario actual | Autenticado |
| GET | `/admin/users` | Listar usuarios | ADMIN |
| POST | `/admin/users` | Crear usuario (Admin) | ADMIN |
| PATCH | `/admin/users/{id}` | Actualizar usuario | ADMIN |
| DELETE | `/admin/users/{id}` | Eliminar usuario (Soft delete) | ADMIN |

---
**Nota**: Para detalles de despliegue en Kubernetes, consultar la carpeta `k8s/` (no documentada aquí por solicitud).
