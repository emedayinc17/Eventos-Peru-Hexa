# Proveedores Service (Gestión de Disponibilidad y Reservas)

Este microservicio es responsable de gestionar la disponibilidad de los proveedores y manejar las reservas temporales ("holds") de recursos. Implementa un diseño de **Arquitectura Hexagonal**.

## 🏗 Arquitectura

El servicio sigue los principios de Arquitectura Hexagonal (Ports & Adapters):

- **Domain**: Entidades (`Proveedor`, `Hold`) y lógica de negocio.
- **Application**: Casos de uso (`BuscarDisponibles`, `CrearHold`, `ConfirmarHold`).
- **Infrastructure**: Adaptadores para base de datos (MySQL) y comunicación HTTP.
- **Entrypoints**: Controladores API (FastAPI Router).

## 🛠 Tech Stack

- **Lenguaje**: Python 3.12
- **Framework Web**: FastAPI + Uvicorn
- **Base de Datos**: MySQL 8.0
- **ORM**: SQLAlchemy (Core/ORM)
- **Seguridad**: 
  - Endpoints públicos para búsqueda.
  - Endpoints internos protegidos por `X-Service-Token`.
- **Validación**: Pydantic v2
- **Testing**: Pytest

## 📂 Estructura del Proyecto

```
proveedores-service/
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
- MySQL corriendo (con el esquema `ev_proveedores` creado).

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
   El servicio estará disponible en `http://localhost:8030`.

## 🐳 Docker

### Construir Imagen
Desde la raíz del repositorio (para incluir librerías compartidas):

```bash
docker build -t proveedores-service:1.0.0 -f services/proveedores-service/Dockerfile .
```

### Ejecutar Contenedor
```bash
docker run -d -p 8030:8030 --name proveedores-service proveedores-service:1.0.0
```

## ✅ Testing

### Ejecutar Pruebas
```bash
cd services/proveedores-service
pytest test/test_proveedores_service.py
```

### Generar Reporte HTML
```bash
pytest test/test_proveedores_service.py --html=test/report_proveedores.html --self-contained-html
```

## 🔌 Endpoints Principales

| Método | Ruta | Descripción | Acceso |
|--------|------|-------------|--------|
| GET | `/health` | Health check | Público |
| GET | `/v1/proveedores/disponibles` | Buscar proveedores disponibles | Público |
| POST | `/internal/holds` | Crear reserva temporal (Hold) | Interno |
| GET | `/internal/holds/{id}` | Obtener detalle de Hold | Interno |
| PATCH | `/internal/holds/{id}/confirm` | Confirmar Hold | Interno |
| DELETE | `/internal/holds/{id}` | Liberar/Cancelar Hold | Interno |
