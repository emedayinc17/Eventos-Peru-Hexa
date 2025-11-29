# Control de Accesos

Descripción
-----------
Comprobaciones automatizadas y ejemplos para validar RBAC (roles) y la
gestión correcta de tokens JWT.

Archivo principal
-----------------
- `test_rbac.py` — pruebas pytest que verifican:
  - Rutas `/admin/**` devuelven `403`/`401` para usuarios no autorizados.
  - Tokens manipulados o expirados devuelven `401`.
  - Test positivo para ADMIN cuando se proporcionan `ADMIN_EMAIL` y `ADMIN_PASSWORD`.

Prerequisitos y variables de entorno
-----------------------------------
- `API_BASE` (por defecto `http://localhost:8000`)
- `TEST_IAM_EMAIL` / `TEST_IAM_PASSWORD` — credenciales de usuario de
  prueba (cliente)
- Opcional: `ADMIN_EMAIL` / `ADMIN_PASSWORD` — para ejecutar tests que
  requieren un usuario ADMIN real (test positivo)

Instalación y ejecución
----------------------
```bash
pip install -r tests/requirements.txt
API_BASE="http://localhost:8000" pytest tests/PRUEBAS_DE_SEGURIDAD/control_accesos -q
```

Precauciones
-----------
- Estos tests pueden requerir la creación de usuarios de prueba; ejecutar
  en entorno controlado y con datos aislados.
