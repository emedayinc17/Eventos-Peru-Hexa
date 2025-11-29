# Rendimiento

Descripción
-----------
Contiene scripts para pruebas de carga. El script incluido está diseñado
para `k6` (https://k6.io).

Prerequisitos
------------
- `k6` instalado localmente. En Windows se puede instalar con Chocolatey:

```powershell
choco install k6
```

O usar Docker:

```bash
docker run --rm -i -v $(pwd):/scripts -w /scripts loadimpact/k6 run rendimiento/load_test_k6.js
```

Variables útiles
----------------
- `API_BASE`: URL base de la API (por defecto `http://localhost:8000`)

Ejecutar con k6
--------------
```bash
API_BASE="http://localhost:8000" k6 run tests/PRUEBAS_DE_SOFTWARE/rendimiento/load_test_k6.js
```

Consejos
-------
- Ajustar `vus` y `duration` en `load_test_k6.js` según capacidad del entorno.
- No ejecutar pruebas de carga contra entornos de producción sin autorización.
Rendimiento

Descripción:
Scripts y guías para pruebas de carga y estrés (k6, Locust, ab).

Escenarios sugeridos:
- IAM: 50–200 solicitudes simultáneas a `/auth/login`.
- Catálogo: 100 solicitudes concurrentes para listar paquetes.
- Flujo completo de contratación bajo carga moderada.

Ejecutar ejemplo con k6:
```bash
# crear archivo k6 script en esta carpeta y ejecutar:
k6 run tests/PRUEBAS_DE_SOFTWARE/rendimiento/script_k6_login.js
```
