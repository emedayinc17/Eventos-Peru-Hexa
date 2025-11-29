Tests structure and guidelines

Overview
- `tests/unit/`: Unit tests (pytest) — mock repositories, isolated business logic. Target services: IAM, catalogo, proveedores, contratacion.
- `tests/functional/`: Functional tests (pytest/httpx/requests) — endpoint-level tests that exercise services with HTTP.
- `tests/integration/`: Integration tests — backend↔backend flows (currently empty, add integration tests here).
- `tests/e2e/`: End-to-end tests (frontend↔backend flows, existing E2E scripts).
- `tests/manual/`: Manual test instructions and interactive checks.
- `tests/performance/`: Performance test scripts (k6/locust) — create as needed.

Guidelines
- Prefer adding new unit tests under `tests/unit/` using pytest and mocking DB/repositories.
- Place endpoint-level tests that require running services in `tests/functional/`.
- Move automated end-to-end flows into `tests/e2e/` and integration tests into `tests/integration/`.
- Keep manual instructions in `tests/manual/` (they are not executed by CI).

How to run
- Unit tests: `pytest tests/unit/`
- Functional tests (services up): `pytest tests/functional/`
- E2E: follow `tests/e2e/README` if present.
