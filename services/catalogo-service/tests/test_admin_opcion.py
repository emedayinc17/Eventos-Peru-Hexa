import importlib
import pathlib
import sys
from fastapi import FastAPI
from fastapi.testclient import TestClient

repo_root = pathlib.Path(__file__).resolve().parents[3]
service_dir = repo_root / "services" / "catalogo-service"
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
if str(service_dir) not in sys.path:
    sys.path.insert(0, str(service_dir))
ev_shared_path = repo_root / "libs" / "shared"
if str(ev_shared_path) not in sys.path:
    sys.path.insert(0, str(ev_shared_path))

router_module = importlib.import_module("app.entrypoints.fastapi.router")
from app.entrypoints.fastapi import dependencies as deps


def test_create_opcion_admin(monkeypatch):
    app = FastAPI()
    monkeypatch.setattr(router_module, "get_db_session", lambda settings: iter([object()]))

    class MockRepo:
        def create_opcion(self, s, *, servicio_id, nombre, moneda, monto, detalles=None):
            return {"id": "op-1", "nombre": nombre}

    monkeypatch.setattr(router_module, "get_create_opcion_use_case", lambda: type("X", (), {"execute": lambda self, session, **kw: MockRepo().create_opcion(None, **kw)})())

    app.include_router(router_module.create_router())
    client = TestClient(app)

    resp = client.post("/v1/admin/opciones", json={"servicio_id": "s-1", "nombre": "Opcion A", "moneda": "PEN", "monto": 150.0})
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == "op-1"
    assert body["nombre"] == "Opcion A"
