# Funcionales

Descripción
-----------
Estos tests verifican los endpoints HTTP y requieren que los servicios estén
disponibles (por ejemplo con `docker-compose up -d`). Ejecutar con

`pytest tests/PRUEBAS_DE_SOFTWARE/funcionales`.

Prerequisitos
------------
- Servicios del proyecto levantados (ej. `docker-compose up -d`)
- Python 3.8+, `pip` y entorno virtual opcional
- Dependencias Python: ver `tests/requirements.txt`

Variables de entorno
--------------------
- `API_BASE` (por defecto `http://localhost:8000`)
- `TEST_IAM_EMAIL` (email de prueba, por defecto `cliente@test.com`)
- `TEST_IAM_PASSWORD` (password de prueba)

Instalación de dependencias
---------------------------
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r tests/requirements.txt
```

Ejecución
---------
Ejecutar todos los tests funcionales:

```bash
API_BASE="http://localhost:8000" pytest tests/PRUEBAS_DE_SOFTWARE/funcionales -q
```

Notas de seguridad
-----------------
- Estos tests realizan llamadas autenticadas y pueden crear recursos en la
	base de datos. Ejecutar en un entorno de staging o con datos de prueba.
- Revisar los endpoints llamados en cada test antes de ejecutar en entornos
	compartidos.
Funcionales

Descripción:
Pruebas funcionales que validan endpoints principales y roles (CLIENTE / ADMIN).

Cobertura recomendada:
- IAM: `/auth/register`, `/auth/login`, `/me`, `/admin/users`.
- Catálogo: listar tipos, paquetes, servicios.
- Proveedores: disponibilidad, búsqueda, detalles.
- Contratación: creación de pedido, cambio de estado, flujo completo.

Ejecutar (servicios levantados):
```bash
pytest tests/PRUEBAS_DE_SOFTWARE/funcionales/
```

Notas:
- Estas pruebas usan `requests` y esperan servicios locales corriendo.
- Para CI, levantar dependencias en contenedores y ejecutar pruebas con `pytest -k funcional`.
