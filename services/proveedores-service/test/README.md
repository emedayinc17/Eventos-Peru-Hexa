# Pruebas del Servicio de Proveedores

Este directorio contiene las pruebas automatizadas para el servicio de Proveedores (Disponibilidad y Reservas).

## Estructura
- `test_proveedores_service.py`: Script consolidado que incluye pruebas de endpoints públicos y ciclo de vida interno.
- `report_proveedores.html`: Reporte de resultados (generado automáticamente).

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
cd services/proveedores-service
pytest test/test_proveedores_service.py
```

### Opción 2: Generando Reporte HTML (Recomendado)
Para generar un reporte visual detallado de los resultados:

```powershell
cd services/proveedores-service
pytest test/test_proveedores_service.py --html=test/report_proveedores.html --self-contained-html
```

El reporte se guardará en este mismo directorio como `report_proveedores.html`.

## Cobertura de las Pruebas
El script `test_proveedores_service.py` valida los siguientes aspectos:

1. **Pruebas de Integración (API Flow)**:
   - **Health Check**: Disponibilidad del servicio.
   - **Búsqueda Pública**: Consulta de proveedores disponibles por fecha y servicio.
   - **Ciclo de Vida de Reservas (Internal)**:
     - **Crear Hold**: Generación de una reserva temporal.
     - **Obtener Hold**: Verificación de la persistencia de la reserva.
     - **Confirmar Hold**: Cambio de estado a confirmado.
     - **Liberar Hold**: Eliminación/Liberación de la reserva.
