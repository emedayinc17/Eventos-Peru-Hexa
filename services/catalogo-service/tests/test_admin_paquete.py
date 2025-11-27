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


def test_create_update_delete_paquete(monkeypatch):
    app = FastAPI()
    monkeypatch.setattr(router_module, "get_db_session", lambda settings: iter([object()]))

    class MockRepo:
        def create_paquete(self, s, *, codigo, nombre, items, moneda="PEN"):
            return {"id": "p-1", "codigo": codigo}

        def update_paquete(self, s, *, paquete_id, nombre=None, items=None, moneda=None):
            return {"id": paquete_id}

        def delete_paquete(self, s, *, paquete_id):
            return None

    # patch factories
    monkeypatch.setattr(router_module, "get_create_paquete_use_case", lambda: type("X", (), {"execute": lambda self, session, **kw: MockRepo().create_paquete(None, **kw)})())
    monkeypatch.setattr(router_module, "get_update_paquete_use_case", lambda: type("X", (), {"execute": lambda self, session, **kw: MockRepo().update_paquete(None, **kw)})())
    monkeypatch.setattr(router_module, "get_delete_paquete_use_case", lambda: type("X", (), {"execute": lambda self, session, **kw: MockRepo().delete_paquete(None, **kw)})())

    app.include_router(router_module.create_router())
    client = TestClient(app)

    # Create
    resp = client.post("/v1/admin/paquetes", json={"codigo": "PKG1", "nombre": "Pack 1", "items": [{"opcion_servicio_id": "op-1", "cantidad": 1}]})
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == "p-1"

    # Update
    resp2 = client.put("/v1/admin/paquetes/p-1", json={"nombre": "Pack 1 mod", "items": []})
    assert resp2.status_code == 200
    assert resp2.json()["id"] == "p-1"

    # Delete
    resp3 = client.delete("/v1/admin/paquetes/p-1")
    assert resp3.status_code == 204
