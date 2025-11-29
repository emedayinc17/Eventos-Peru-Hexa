# Inyección

Descripción
-----------
Pruebas de inyección (SQLi, path traversal, command injection). Estas pruebas
deben ejecutarse con extremo cuidado y están deshabilitadas por defecto.

Activación
----------
Para ejecutar las pruebas automatizadas activar la variable de entorno:

```bash
export ALLOW_INJECTION_TESTS=true   # Linux/Mac
setx ALLOW_INJECTION_TESTS true     # Windows (persistente)
```

Checks incluidos
--------------
- `test_sql_injection.py` — envía payloads típicos de SQLi y valida que
  la API no responda con errores 500 ni datos sensibles.
- `test_sql_injection.py` también contiene un test de `path traversal` que
  valida códigos 400/403/404 para rutas maliciosas.

Precauciones
-----------
- Estas pruebas pueden afectar datos; ejecutar sólo en staging y con backups.
- No habilitar `ALLOW_INJECTION_TESTS` en entornos compartidos.
