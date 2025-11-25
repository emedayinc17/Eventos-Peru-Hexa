# Contratación Service (Gestión de Pedidos)

Este microservicio es responsable de la gestión del ciclo de vida de los pedidos (contrataciones) de eventos. Permite a los clientes crear y consultar sus pedidos, y a los administradores gestionarlos. Implementa un diseño de **Arquitectura Hexagonal**.

## 🏗 Arquitectura

El servicio sigue los principios de Arquitectura Hexagonal (Ports & Adapters):

- **Domain**: Entidades (`Pedido`, `ItemPedido`) y lógica de negocio.
- **Application**: Casos de uso (`CrearPedido`, `ListarPedidos`, `ActualizarEstado`).
- **Infrastructure**: Adaptadores para base de datos (MySQL) y comunicación HTTP.
- **Entrypoints**: Controladores API (FastAPI Router).

## 🛠 Tech Stack

- **Lenguaje**: Python 3.12
- **Framework Web**: FastAPI + Uvicorn
- **Base de Datos**: MySQL 8.0
- **ORM**: SQLAlchemy (Core/ORM)
- **Seguridad**: Validación de Tokens JWT (emitidos por IAM).
- **Validación**: Pydantic v2
- **Testing**: Pytest

## 📂 Estructura del Proyecto

```
contratacion-service/
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
- MySQL corriendo (con el esquema `ev_contratacion` creado).
- Servicio IAM corriendo en puerto 8010 (para validación de tokens).

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
   El servicio estará disponible en `http://localhost:8040`.

## 🐳 Docker

### Construir Imagen
Desde la raíz del repositorio (para incluir librerías compartidas):

```bash
docker build -t contratacion-service:1.0.0 -f services/contratacion-service/Dockerfile .
```

### Ejecutar Contenedor
```bash
docker run -d -p 8040:8040 --name contratacion-service contratacion-service:1.0.0
```

## ✅ Testing

### Ejecutar Pruebas
```bash
cd services/contratacion-service
pytest test/test_contratacion_service.py
```

### Generar Reporte HTML
```bash
pytest test/test_contratacion_service.py --html=test/report_contratacion.html --self-contained-html
```

## 🔌 Endpoints Principales

| Método | Ruta | Descripción | Rol Requerido |
|--------|------|-------------|---------------|
| POST | `/pedidos` | Crear un nuevo pedido | CLIENT |
| GET | `/pedidos/{id}` | Ver detalle de un pedido | CLIENT (Dueño) / ADMIN |
| GET | `/pedidos/mios` | Listar mis pedidos | CLIENT |
| GET | `/admin/pedidos` | Listar todos los pedidos | ADMIN |
| PATCH | `/admin/pedidos/{id}` | Actualizar estado del pedido | ADMIN |

