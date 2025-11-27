import pathlib
import sys
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient


def load_admin_module() -> object:
    repo_root = pathlib.Path(__file__).resolve().parents[3]
    service_dir = repo_root / "services" / "proveedores-service"
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    ev_shared_path = repo_root / "libs" / "shared"
    if str(ev_shared_path) not in sys.path:
        sys.path.insert(0, str(ev_shared_path))
    if str(service_dir) not in sys.path:
        sys.path.insert(0, str(service_dir))

    import importlib
    module = importlib.import_module("app.entrypoints.fastapi.router_admin")
    return module


def test_create_proveedor_success():
    module = load_admin_module()
    app = FastAPI()

    # mock session provider
    module.get_session = lambda: iter([object()])

    class MockCreate:
        def execute(self, payload):
            return "prov-123"

    module.get_create_proveedor_use_case = lambda: MockCreate()

    app.include_router(module.router)
    client = TestClient(app)

    payload = {"nombre": "Proveedor X", "email": "p@example.com"}
    resp = client.post("/v1/admin/proveedores/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["id"] == "prov-123"


def test_update_proveedor_success():
    module = load_admin_module()
    app = FastAPI()
    module.get_session = lambda: iter([object()])

    class MockUpdate:
        def execute(self, proveedor_id, payload):
            return None

    module.get_update_proveedor_use_case = lambda: MockUpdate()
    app.include_router(module.router)
    client = TestClient(app)

    resp = client.put("/v1/admin/proveedores/prov-123", json={"nombre": "Nuevo"})
    assert resp.status_code == 200
    assert resp.json()["id"] == "prov-123"


def test_delete_proveedor_success():
    module = load_admin_module()
    app = FastAPI()
    module.get_session = lambda: iter([object()])

    class MockDelete:
        def execute(self, proveedor_id):
            return None

    module.get_delete_proveedor_use_case = lambda: MockDelete()
    app.include_router(module.router)
    client = TestClient(app)

    resp = client.delete("/v1/admin/proveedores/prov-123")
    assert resp.status_code == 204


def test_add_remove_habilidad():
    module = load_admin_module()
    app = FastAPI()
    module.get_session = lambda: iter([object()])

    class MockAdd:
        def execute(self, proveedor_id, payload):
            return "hab-1"

    class MockRemove:
        def execute(self, proveedor_id, habilidad_id):
            return None

    module.get_add_habilidad_use_case = lambda: MockAdd()
    module.get_remove_habilidad_use_case = lambda: MockRemove()

    app.include_router(module.router)
    client = TestClient(app)

    resp = client.post("/v1/admin/proveedores/prov-1/habilidades", json={"nombre": "Limpieza"})
    assert resp.status_code == 201
    assert resp.json()["habilidad_id"] == "hab-1"

    resp2 = client.delete("/v1/admin/proveedores/prov-1/habilidades/hab-1")
    assert resp2.status_code == 204


def test_add_delete_calendario():
    module = load_admin_module()
    app = FastAPI()
    module.get_session = lambda: iter([object()])

    class MockAddCal:
        def execute(self, proveedor_id, payload):
            return "cal-1"

    class MockDelCal:
        def execute(self, proveedor_id, calendario_id):
            return None

    module.get_add_calendario_use_case = lambda: MockAddCal()
    module.get_delete_calendario_use_case = lambda: MockDelCal()

    app.include_router(module.router)
    client = TestClient(app)

    resp = client.post("/v1/admin/proveedores/prov-1/calendario", json={"dias": []})
    assert resp.status_code == 201
    assert resp.json()["calendario_id"] == "cal-1"

    resp2 = client.delete("/v1/admin/proveedores/prov-1/calendario/cal-1")
    assert resp2.status_code == 204
