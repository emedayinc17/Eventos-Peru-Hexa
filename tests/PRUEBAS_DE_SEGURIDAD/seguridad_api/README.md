
# Seguridad API

Descripción
-----------
Comprobaciones automáticas y manuales para verificar políticas CORS,
headers de seguridad y protección relacionada con API.

Checks incluidos
--------------
- Validación de `Access-Control-Allow-Origin` en respuestas (OPTIONS).
- Verificación de headers importantes (`X-Frame-Options`,
  `Content-Security-Policy`, `Referrer-Policy`, `Strict-Transport-Security`).
- Nota sobre CSRF: la aplicación usa JWT sin cookies, por lo que el riesgo
  clásico de CSRF es reducido.

Automatización
-------------
- `test_api_security_headers.py` — pruebas pytest que realizan:
  - OPTIONS a endpoints protegidos para validar CORS.
  - GET a `/` para verificar presencia de headers de seguridad.

Prerequisitos y ejecución
------------------------
```bash
pip install -r tests/requirements.txt
API_BASE="http://localhost:8000" pytest tests/PRUEBAS_DE_SEGURIDAD/seguridad_api -q
```

Notas
-----
- Dependiendo del servidor y configuración de Ingress, algunos headers
  pueden generarse por el reverse-proxy (nginx/ingress). Ajustar
  expectativas del test según la arquitectura.
