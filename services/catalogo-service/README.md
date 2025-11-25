# Catálogo Service (Gestión de Productos y Servicios)

Este microservicio es responsable de la gestión y consulta del catálogo de eventos, incluyendo tipos de eventos, servicios, opciones y paquetes predefinidos. Implementa un diseño de **Arquitectura Hexagonal**.

## 🏗 Arquitectura

El servicio sigue los principios de Arquitectura Hexagonal (Ports & Adapters):

- **Domain**: Entidades (`TipoEvento`, `Servicio`, `Paquete`) y lógica de negocio.
- **Application**: Casos de uso (`ListarTiposEvento`, `ListarPaquetes`, `ObtenerDetallePaquete`).
- **Infrastructure**: Adaptadores para base de datos (MySQL) y comunicación HTTP.
- **Entrypoints**: Controladores API (FastAPI Router).

## 🛠 Tech Stack

- **Lenguaje**: Python 3.12
- **Framework Web**: FastAPI + Uvicorn
- **Base de Datos**: MySQL 8.0
- **ORM**: SQLAlchemy (Core/ORM)
- **Seguridad**: Endpoints públicos (MVP).
- **Validación**: Pydantic v2
- **Testing**: Pytest

## 📂 Estructura del Proyecto

```
catalogo-service/
├── app/
│   ├── application/       # Casos de uso
│   ├── domain/            # Entidades y Reglas de Negocio
│   ├── entrypoints/       # API REST
│   └── infrastructure/    # Adaptadores (MySQL, etc.)
├── test/                  # Pruebas automatizadas
├── Dockerfile             # Definición de contenedor
├── requirements.txt       # Dependencias Python
└── run.bat                # Script de ejecución local
```

## 🚀 Ejecución Local

### Prerrequisitos
- Python 3.12+
- MySQL corriendo (con el esquema `ev_catalogo` creado y poblado).

### Pasos
1. **Configurar variables de entorno**:
   Crea un archivo `.env` en la raíz del servicio (o usa las variables por defecto).

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Iniciar el servicio**:
   ```bash
   .\run.bat
   ```
   El servicio estará disponible en `http://localhost:8020`.

## 🐳 Docker

### Construir Imagen
Desde la raíz del repositorio (para incluir librerías compartidas):

```bash
docker build -t catalogo-service:1.0.0 -f services/catalogo-service/Dockerfile .
```

### Ejecutar Contenedor
```bash
docker run -d -p 8020:8020 --name catalogo-service catalogo-service:1.0.0
```

## ✅ Testing

### Ejecutar Pruebas
```bash
cd services/catalogo-service
pytest test/test_catalogo_service.py
```

### Generar Reporte HTML
```bash
pytest test/test_catalogo_service.py --html=test/report_catalogo.html --self-contained-html
```

## 🔌 Endpoints Principales

| Método | Ruta | Descripción | Rol Requerido |
|--------|------|-------------|---------------|
| GET | `/health` | Health check | Público |
| GET | `/v1/catalogo/tipos` | Listar tipos de evento | Público |
| GET | `/v1/catalogo/servicios` | Listar servicios | Público |
| GET | `/v1/catalogo/opciones` | Listar opciones de un servicio | Público |
| GET | `/v1/catalogo/paquetes` | Listar paquetes disponibles | Público |
| GET | `/v1/catalogo/paquetes/{id}` | Ver detalle de un paquete | Público |
