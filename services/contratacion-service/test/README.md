# Pruebas del Servicio de Contratación

Este directorio contiene las pruebas automatizadas para el servicio de Contratación (Gestión de Pedidos).

## Estructura
- `test_contratacion_service.py`: Script consolidado que incluye pruebas de integración de flujos completos.
- `report_contratacion.html`: Reporte de resultados (generado automáticamente).

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
cd services/contratacion-service
pytest test/test_contratacion_service.py
```

### Opción 2: Generando Reporte HTML (Recomendado)
Para generar un reporte visual detallado de los resultados:

```powershell
cd services/contratacion-service
pytest test/test_contratacion_service.py --html=test/report_contratacion.html --self-contained-html
```

El reporte se guardará en este mismo directorio como `report_contratacion.html`.

## Cobertura de las Pruebas
El script `test_contratacion_service.py` valida los siguientes aspectos:

1. **Pruebas de Integración (API Flow)**:
   - **Health Check**: Disponibilidad del servicio.
   - **Creación de Pedido**: Flujo de cliente para registrar un nuevo pedido.
   - **Detalle de Pedido**: Consulta de información de un pedido específico.
   - **Mis Pedidos**: Listado de pedidos pertenecientes al usuario autenticado.
   - **Gestión Admin**: Listado global de pedidos para administradores.
   - **Actualización de Estado**: Cambio de estado de pedido por parte de un administrador y verificación por el cliente.
