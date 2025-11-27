import importlib.util
import pathlib
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


def load_router_module() -> object:
    repo_root = pathlib.Path(__file__).resolve().parents[3]
    service_dir = repo_root / "services" / "proveedores-service"
    # Ensure repo root and libs/shared are on sys.path so imports like `ev_shared` resolve
    import sys
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    ev_shared_path = repo_root / "libs" / "shared"
    if str(ev_shared_path) not in sys.path:
        sys.path.insert(0, str(ev_shared_path))
    # Add service dir so relative package imports (from .dependencies) work
    if str(service_dir) not in sys.path:
        sys.path.insert(0, str(service_dir))

    # Import as package module so relative imports inside module work
    import importlib
    module = importlib.import_module("app.entrypoints.fastapi.router_public")
    return module


@pytest.fixture
def router_module():
    return load_router_module()


def test_crear_reserva_success(router_module, monkeypatch):
    app = FastAPI()

    # mock get_db_session to yield a dummy session
    monkeypatch.setattr(router_module, "get_db_session", lambda settings: iter([object()]))

    # mock use case
    class MockCrear:
        def execute(self, session, **kwargs):
            return SimpleNamespace(
                id="hold-1",
                proveedor_id=kwargs.get("proveedor_id"),
                opcion_servicio_id=kwargs.get("opcion_servicio_id"),
                inicio=kwargs.get("inicio"),
                fin=kwargs.get("fin"),
                status=1,
                expira_en=kwargs.get("inicio"),
            )

    monkeypatch.setattr(router_module, "get_crear_hold_use_case", lambda: MockCrear())

    app.include_router(router_module.build_public_router(router_module.Settings()))
    client = TestClient(app)

    payload = {
        "proveedor_id": "prov-1",
        "opcion_servicio_id": "op-1",
        "inicio": "2025-11-26T10:00:00",
        "fin": "2025-11-26T11:00:00",
        "ttl_min": 20,
    }

    resp = client.post("/v1/reservas", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["id"] == "hold-1"
    assert data["proveedor_id"] == "prov-1"


def test_crear_reserva_invalid_date(router_module, monkeypatch):
    app = FastAPI()
    monkeypatch.setattr(router_module, "get_db_session", lambda settings: iter([object()]))
    monkeypatch.setattr(router_module, "get_crear_hold_use_case", lambda: None)
    app.include_router(router_module.build_public_router(router_module.Settings()))
    client = TestClient(app)

    payload = {
        "proveedor_id": "prov-1",
        "opcion_servicio_id": "op-1",
        "inicio": "26-11-2025 10:00",  # invalid ISO
        "fin": "26-11-2025 11:00",
    }

    resp = client.post("/v1/reservas", json=payload)
    assert resp.status_code == 400


def test_liberar_reserva_success(router_module, monkeypatch):
    app = FastAPI()
    monkeypatch.setattr(router_module, "get_db_session", lambda settings: iter([object()]))

    class MockLiberar:
        def __init__(self):
            self.called_with = None

        def execute(self, session, **kwargs):
            self.called_with = kwargs.get("hold_id")

    mock = MockLiberar()
    monkeypatch.setattr(router_module, "get_liberar_hold_use_case", lambda: mock)

    app.include_router(router_module.build_public_router(router_module.Settings()))
    client = TestClient(app)

    resp = client.delete("/v1/reservas/hold-1")
    assert resp.status_code == 204
    assert mock.called_with == "hold-1"
