# Pruebas del Servicio de Catálogo

Este directorio contiene las pruebas automatizadas para el servicio de Catálogo (Gestión de Productos y Servicios).

## Estructura
- `test_catalogo_service.py`: Script consolidado que incluye pruebas de integración de endpoints públicos.
- `report_catalogo.html`: Reporte de resultados (generado automáticamente).

## Requisitos Previos
Asegúrate de tener el entorno virtual activado y las dependencias instaladas:

```powershell
# Desde la raíz del proyecto
.\Scripts\activate

# Instalar dependencias de prueba si no las tienes
pip install pytest pytest-html httpx
```

## Ejecución de Pruebas

### Opción 1: Ejecución Estándar (Consola)
Para ver los resultados directamente en la terminal:

```powershell
cd services/catalogo-service
pytest test/test_catalogo_service.py
```

### Opción 2: Generando Reporte HTML (Recomendado)
Para generar un reporte visual detallado de los resultados:

```powershell
cd services/catalogo-service
pytest test/test_catalogo_service.py --html=test/report_catalogo.html --self-contained-html
```

El reporte se guardará en este mismo directorio como `report_catalogo.html`.

## Cobertura de las Pruebas
El script `test_catalogo_service.py` valida los siguientes aspectos:

1. **Pruebas de Integración (API Flow)**:
   - **Health Check**: Disponibilidad del servicio.
   - **Tipos de Evento**: Listado de tipos de eventos disponibles.
   - **Servicios**: Listado de servicios generales.
   - **Paquetes**: Listado de paquetes predefinidos.
   - **Detalle de Paquete**: Consulta de información detallada de un paquete específico (incluyendo items).
   - **Opciones**: Validación de listado de opciones por servicio.
