PRUEBAS_DE_SOFTWARE

Estructura principal de pruebas del proyecto.

- `unitarias/`: Pruebas unitarias (pytest) — lógica de negocio aislada, repositorios mockeados.
- `funcionales/`: Pruebas funcionales (pytest/requests) — verifican endpoints y comportamiento desde la perspectiva del usuario.
- `integracion/`: Pruebas de integración / E2E — flujos backend↔backend y frontend↔backend.
- `rendimiento/`: Scripts y guías para pruebas de carga (k6, locust).

Cada carpeta contiene sus scripts y un `README.md` con instrucciones para ejecutar.
