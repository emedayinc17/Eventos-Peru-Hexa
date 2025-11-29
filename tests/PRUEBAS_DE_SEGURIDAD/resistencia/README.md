# Resistencia

Descripción
-----------
Pruebas de stress y DoS controlados para evaluar la estabilidad de IAM,
Catálogo y otros servicios críticos. Los scripts están pensados para uso en
staging con monitoreo.

Script incluido
---------------
- `load_test_k6_resilience.js` — script k6 que golpea endpoints de salud
  (`/api/iam/health`, `/api/catalogo/health`) para medir latencia y errores.

Prerequisitos
------------
- `k6` instalado localmente o usar la imagen Docker `loadimpact/k6`.

Ejemplo de ejecución (k6 local):

```bash
API_BASE="http://localhost:8000" k6 run tests/PRUEBAS_DE_SEGURIDAD/resistencia/load_test_k6_resilience.js
```

Ejemplo usando Docker:

```bash
docker run --rm -i -v $(pwd):/scripts -w /scripts loadimpact/k6 run resistencia/load_test_k6_resilience.js
```

Precauciones
-----------
- Estas pruebas generan carga real; coordinar con el equipo de infraestructura.
- Empezar con `vus` y `duration` bajos y aumentarlos progresivamente.
