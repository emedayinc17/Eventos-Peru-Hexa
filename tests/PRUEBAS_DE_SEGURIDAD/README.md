
# PRUEBAS_DE_SEGURIDAD

Descripción
-----------
Carpeta que centraliza pruebas de seguridad para la plataforma: pentesting,
análisis de vulnerabilidades, control de accesos, resistencia, seguridad
API e inyección. Cada subcarpeta incluye scripts de ejemplo, tests pytest
cuando procede y recomendaciones para su ejecución.

Resumen de contenido
--------------------
- `pentesting/` — `nmap_scan.ps1`, `gobuster_commands.sh` (escaneo y
	enumeración de rutas; scripts en modo seguro por defecto).
- `analisis_vulnerabilidades/` — `bandit_run.sh`, `trivy_scan.sh` (análisis
	estático e imágenes Docker).
- `control_accesos/` — `test_rbac.py` (pytest): validación RBAC y tokens.
- `resistencia/` — `load_test_k6_resilience.js` (k6 load test de salud).
- `seguridad_api/` — `test_api_security_headers.py` (pytest): CORS y headers.
- `inyeccion/` — `test_sql_injection.py` (pytest, deshabilitado por defecto;
	activar con `ALLOW_INJECTION_TESTS=true`).

Precauciones
-----------
- No ejecutar estas pruebas en producción sin autorización explícita.
- Muchas pruebas son intrusivas; usarlas sólo en entornos de staging y con
	backups disponibles.

Ejecución rápida
---------------
- Para tests pytest (control_accesos, seguridad_api, inyeccion):

```bash
python -m venv .venv
. .venv/bin/activate  # o .\.venv\Scripts\Activate.ps1 en Windows
pip install -r tests/requirements.txt
API_BASE="http://localhost:8000" pytest tests/PRUEBAS_DE_SEGURIDAD/control_accesos -q
```

- Para k6:

```bash
API_BASE="http://localhost:8000" k6 run tests/PRUEBAS_DE_SEGURIDAD/resistencia/load_test_k6_resilience.js
```

Consulta el README de cada subcarpeta para instrucciones detalladas.
