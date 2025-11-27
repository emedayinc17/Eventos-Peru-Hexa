E2E authenticated tests (IAM)
================================

Overview
--------
This repository includes a small pytest-based E2E test suite under `tests/e2e/` that performs an authenticated flow using the `iam-service` and exercises `catalogo`, `proveedores` and `contratacion` endpoints.

Important safety note
---------------------
- Tests perform real HTTP requests. They are disabled by default — to enable them set the environment variable `E2E_RUN=1`.

How to run (PowerShell)
------------------------
1. Ensure the services are running locally and reachable at the URLs expected. Default URLs:
   - IAM: `http://127.0.0.1:8010/iam`
   - Catalogo: `http://127.0.0.1:8020/catalogo`
   - Proveedores: `http://127.0.0.1:8030/proveedores`
   - Contratacion: `http://127.0.0.1:8040/contratacion`

2. Optionally set environment variables to override defaults (example):
   ```powershell
   $env:IAM_URL = 'http://127.0.0.1:8010/iam'
   $env:CONTRATACION_URL = 'http://127.0.0.1:8040/contratacion'
   $env:TEST_CLIENT_EMAIL = 'demo@eventos.pe'
   $env:TEST_CLIENT_PASSWORD = 'Admin_2025!'
   $env:E2E_RUN = '1'
   .\tools\run_e2e.ps1
   ```

3. The tests will skip automatically if `E2E_RUN` is not `1`.

What the tests do
------------------
- `test_catalogo_package_available` — checks that a seed package endpoint is reachable (200 or 404).
- `test_proveedores_disponibles` — queries providers availability for a service/date.
- `test_create_pedido_flow` — logs in via IAM and attempts to create a `pedido` in Contratacion using a seeded package id; accepts success or common failure responses depending on DB seeds.

Notes and next steps
--------------------
- The suite is intentionally lightweight and defensive so it can run against partially seeded local environments.
- If you want a stricter test (fail when package missing), adjust assertions in `tests/e2e/test_e2e_authenticated_flow.py`.
- For CI, ensure the test runner sets the required environment variables and that the stack (DB + services) is up.
