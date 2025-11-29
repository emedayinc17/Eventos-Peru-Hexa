# Integración

Descripción
-----------
Pruebas de integración / end-to-end que cruzan varios servicios (catalogo,
proveedores, contratacion). Estas pruebas requieren un entorno integrado
con todos los servicios en ejecución.

Prerequisitos
------------
- Entorno integrado con servicios levantados (recomendado `docker-compose up -d`)
- Python 3.8+ y dependencias (`tests/requirements.txt`)

Ejecución
---------
```bash
API_BASE="http://localhost:8000" pytest tests/PRUEBAS_DE_SOFTWARE/integracion -q
```

Precauciones
-----------
- Estas pruebas pueden crear recursos en la base de datos. Ejecutar en un
  entorno de staging o usando datos de prueba.
- Limpiar manualmente los recursos si los endpoints no eliminan automáticamente.
- No ejecutar en producción sin autorización.
Integración / E2E

Descripción:
Pruebas de integración y E2E que validan la interacción entre microservicios y (opcionalmente) el frontend.

Ejecutar (recomendado en entorno de staging con servicios desplegados):
```bash
python tests/PRUEBAS_DE_SOFTWARE/integracion/test_complete_flows.py
```

Para pytest-style E2E setear `E2E_RUN=1` y ejecutar `pytest tests/PRUEBAS_DE_SOFTWARE/integracion/`.
