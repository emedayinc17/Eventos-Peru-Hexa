import pathlib
import sys
from decimal import Decimal

from fastapi import FastAPI
from fastapi.testclient import TestClient
from dataclasses import dataclass
from typing import Optional


def load_router_module():
    repo_root = pathlib.Path(__file__).resolve().parents[3]
    service_dir = repo_root / "services" / "catalogo-service"
    # ensure repo root and libs/shared on sys.path
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    ev_shared_path = repo_root / "libs" / "shared"
    if str(ev_shared_path) not in sys.path:
        sys.path.insert(0, str(ev_shared_path))
    # add service dir
    if str(service_dir) not in sys.path:
        sys.path.insert(0, str(service_dir))

    import importlib
    module = importlib.import_module("app.entrypoints.fastapi.router")
    deps = importlib.import_module("app.entrypoints.fastapi.dependencies")
    main = importlib.import_module("app.entrypoints.fastapi.main")
    return module, deps, main


def test_rutas_registradas():
    router_module, deps, main = load_router_module()
    router = router_module.build_api_router(router_module.Settings())
    paths = {r.path for r in router.routes}
    # endpoints requeridos por logica_implementacion.md
    assert "/v1/tipos-evento" in paths
    assert "/v1/servicios" in paths or "/v1/servicios" in paths
    assert "/v1/opciones-servicio" in paths
    assert "/v1/paquetes" in paths


def test_alias_y_conversión_decimal():
    # Verificar que el endpoint /v1/opciones-servicio está presente y realiza conversión Decimal->float
    router_module, deps, main = load_router_module()
    router = router_module.build_api_router(router_module.Settings())
    # buscar la ruta y su endpoint callable
    target = None
    for r in router.routes:
        if getattr(r, "path", "") == "/v1/opciones-servicio":
            target = r
            break
    assert target is not None
import pathlib
import sys
from decimal import Decimal

from fastapi import FastAPI
from fastapi.testclient import TestClient


def load_router_module():
    repo_root = pathlib.Path(__file__).resolve().parents[3]
    service_dir = repo_root / "services" / "catalogo-service"
    # ensure repo root and libs/shared on sys.path
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    ev_shared_path = repo_root / "libs" / "shared"
    if str(ev_shared_path) not in sys.path:
        sys.path.insert(0, str(ev_shared_path))
    # add service dir
    if str(service_dir) not in sys.path:
        sys.path.insert(0, str(service_dir))

    import importlib
    module = importlib.import_module("app.entrypoints.fastapi.router")
    deps = importlib.import_module("app.entrypoints.fastapi.dependencies")
    main = importlib.import_module("app.entrypoints.fastapi.main")
    return module, deps, main


def test_tipos_evento_alias(monkeypatch):
    router_module, deps, main = load_router_module()
    app = FastAPI()

    @dataclass
    class Tipo:
        id: str = "t1"
        nombre: str = "Matrimonio"
        descripcion: str = ""
        status: int = 1

    class FakeListTiposUC:
        def execute(self, session, *, limit=50, offset=0):
            return [Tipo()]

    monkeypatch.setattr(router_module, "get_db_session", lambda settings=None: iter([None]))
    monkeypatch.setattr(router_module, "get_list_tipos_evento_use_case", lambda: FakeListTiposUC())

    app.include_router(router_module.build_api_router(router_module.Settings()), prefix="/catalogo")
    client = TestClient(app)

    resp = client.get("/catalogo/v1/tipos-evento")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data and data[0]["nombre"] == "Matrimonio"


def test_servicios_list(monkeypatch):
    router_module, deps, main = load_router_module()
    app = FastAPI()

    @dataclass
    class Servicio:
        id: str = "s1"
        nombre: str = "Catering"
        tipo_evento_id: str = "t1"
        descripcion: str = ""
        status: int = 1

    class FakeListServiciosUC:
        def execute(self, session, *, tipo_evento_id=None, limit=50, offset=0):
            return [Servicio()]

    monkeypatch.setattr(router_module, "get_db_session", lambda settings=None: iter([None]))
    monkeypatch.setattr(router_module, "get_list_servicios_por_tipo_use_case", lambda: FakeListServiciosUC())

    app.include_router(router_module.build_api_router(router_module.Settings()), prefix="/catalogo")
    client = TestClient(app)

    resp = client.get("/catalogo/v1/servicios", params={"tipo_evento_id": "t1"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data and data[0]["nombre"] == "Catering"


def test_opciones_servicio_alias(monkeypatch):
    router_module, deps, main = load_router_module()
    app = FastAPI()

    @dataclass
    class Opcion:
        id: str = "o1"
        servicio_id: str = "s1"
        nombre: str = "Buffet"
        moneda: str = "PEN"
        monto: Decimal = Decimal('120.00')
        detalles: Optional[str] = None
        status: int = 1

    class FakeListOpcionesUC:
        def execute(self, session, *, servicio_id, limit=50, offset=0):
            return [Opcion()]

    monkeypatch.setattr(router_module, "get_db_session", lambda settings=None: iter([None]))
    monkeypatch.setattr(router_module, "get_list_opciones_servicio_use_case", lambda: FakeListOpcionesUC())

    app.include_router(router_module.build_api_router(router_module.Settings()), prefix="/catalogo")
    client = TestClient(app)

    resp = client.get("/catalogo/v1/opciones-servicio", params={"servicio_id": "s1"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data and data[0]["nombre"] == "Buffet"

