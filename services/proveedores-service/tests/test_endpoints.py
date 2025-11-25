"""Consolidated integration-like tests for proveedores-service.

These tests run the FastAPI app in-process via TestClient and patch
the factory functions to use in-memory fakes so tests do not require
an external database. The script covers:
 - Health endpoint
 - Public search for available providers
 - Internal hold lifecycle: create (idempotent via correlation_id), get, confirm, release

This single file is intended to be the canonical test script for the service.
"""

from fastapi.testclient import TestClient
from datetime import datetime, timedelta, date

from app.entrypoints.fastapi.main import app

from app.entrypoints.fastapi import dependencies as deps
from app.domain.models import Proveedor, Hold


class FakeBuscar:
    def execute(self, session, *, servicio_id, fecha, limit=50, offset=0):
        # Return a deterministic provider matching the fixtures in db/script2.sql
        return [
            Proveedor(id="cccccccc-3333-4444-5555-cccccccccccc", nombre="Proveedor Prueba Verificacion", rating_prom=4.5, email="prueba@proveedor.local", telefono="+51 900000000", status=1),
        ]


class FakeCrearHold:
    def __init__(self):
        # store by id and by correlation_id to simulate idempotency
        self.store = {}
        self.by_corr = {}

    def execute(self, session, *, proveedor_id, opcion_servicio_id, inicio, fin, ttl_min=30, correlation_id=None, created_by=None):
        # idempotent by correlation_id
        if correlation_id and correlation_id in self.by_corr:
            return self.by_corr[correlation_id]

        hid = f"hold-{len(self.store)+1}"
        expira = datetime.now() + timedelta(minutes=ttl_min)
        h = Hold(id=hid, proveedor_id=proveedor_id, opcion_servicio_id=opcion_servicio_id,
                 inicio=inicio, fin=fin, expira_en=expira, status=0, correlation_id=correlation_id, created_by=created_by)
        self.store[hid] = h
        if correlation_id:
            """Minimal placeholder to avoid duplicated/malformed tests.

            All canonical tests are now in `test_full_flow.py`.
            This file exists only to keep pytest collection stable during iterative edits.
            """

            def test_placeholder_noop():
                assert True
        if correlation_id and correlation_id in self.by_corr:
            return self.by_corr[correlation_id]

        hid = f"hold-{len(self.store)+1}"
        expira = datetime.now() + timedelta(minutes=ttl_min)
        h = Hold(id=hid, proveedor_id=proveedor_id, opcion_servicio_id=opcion_servicio_id,
                 inicio=inicio, fin=fin, expira_en=expira, status=0, correlation_id=correlation_id, created_by=created_by)
        self.store[hid] = h
        if correlation_id:
            self.by_corr[correlation_id] = h
        return h


class FakeConfirmarHold:
    def __init__(self, creator: FakeCrearHold):
        self.creator = creator

    def execute(self, session, hold_id: str):
        h = self.creator.store.get(hold_id)
        if not h:
            raise Exception("HoldNoEncontrado")
        h.status = 1
        return h


class FakeLiberarHold:
    def __init__(self, creator: FakeCrearHold):
        self.creator = creator

    def execute(self, session, hold_id: str):
        h = self.creator.store.get(hold_id)
        if not h:
            raise Exception("HoldNoEncontrado")
        h.status = 3
        # simulate deletion by removing from store
        del self.creator.store[hold_id]
        return None


class FakeObtenerHold:
    def __init__(self, creator: FakeCrearHold):
        self.creator = creator

    def execute(self, session, hold_id: str):
        return self.creator.store.get(hold_id)


def setup_overrides():
    fake_buscar = FakeBuscar()
    fake_crear = FakeCrearHold()
    fake_confirm = FakeConfirmarHold(fake_crear)
    fake_liberar = FakeLiberarHold(fake_crear)
    fake_obtener = FakeObtenerHold(fake_crear)

    # Patch dependencies used by routers (module-level factories)
    deps.get_buscar_disponibles_use_case = lambda proveedor_query=None: fake_buscar
    deps.get_crear_hold_use_case = lambda holds_repo=None: fake_crear
    deps.get_confirmar_hold_use_case = lambda holds_repo=None: fake_confirm
    deps.get_liberar_hold_use_case = lambda holds_repo=None: fake_liberar
    deps.get_obtener_hold_use_case = lambda holds_repo=None: fake_obtener

    def _fake_db_session(settings=None):
        class DummySession:
            def execute(self, *args, **kwargs):
                class DummyResult:
                    def mappings(self):
                        return []
                return DummyResult()
        yield DummySession()

    deps.get_db_session = _fake_db_session

    # Also patch the router modules which import factories at module import time
    from app.entrypoints.fastapi import router_public, router_internal
    router_public.get_buscar_disponibles_use_case = lambda proveedor_query=None: fake_buscar
    router_public.get_db_session = _fake_db_session

    router_internal.get_crear_hold_use_case = lambda holds_repo=None: fake_crear
    router_internal.get_confirmar_hold_use_case = lambda holds_repo=None: fake_confirm
    router_internal.get_liberar_hold_use_case = lambda holds_repo=None: fake_liberar
    router_internal.get_obtener_hold_use_case = lambda holds_repo=None: fake_obtener
    router_internal.get_db_session = _fake_db_session


def test_health_and_public_search():
    setup_overrides()
    client = TestClient(app)

    r = client.get("/proveedores/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

    params = {"servicio_id": "aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa", "fecha": date.today().isoformat(), "limit": 5}
    r = client.get("/proveedores/v1/proveedores/disponibles", params=params)
    """Archivo eliminado: las pruebas canónicas están en `test_full_flow.py`.

    Este archivo se reemplaza por un marcador vacío para evitar colecciones accidentales.
    """

    def test_placeholder_removed():
        assert True
        "correlation_id": correlation,
        "created_by": "test-suite"
    }
    headers = {"X-Service-Token": "dev-internal-token-change-in-production"}

    # Create hold (first time)
    r1 = client.post("/proveedores/internal/holds", json=payload, headers=headers)
    assert r1.status_code == 201
    h1 = r1.json()
    hid = h1["id"]

    # Create hold again with same correlation_id -> must return same hold (idempotent)
    r2 = client.post("/proveedores/internal/holds", json=payload, headers=headers)
    assert r2.status_code in (200, 201)
    h2 = r2.json()
    assert h2["id"] == hid

    # Get hold
    rg = client.get(f"/proveedores/internal/holds/{hid}", headers=headers)
    assert rg.status_code == 200
    assert rg.json()["id"] == hid

    # Confirm hold
    rc = client.patch(f"/proveedores/internal/holds/{hid}/confirm", headers=headers)
    assert rc.status_code == 200
    assert rc.json()["status"] == 1

    # Release hold
    rd = client.delete(f"/proveedores/internal/holds/{hid}", headers=headers)
    assert rd.status_code == 204
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, date

from app.entrypoints.fastapi.main import app

from app.entrypoints.fastapi import dependencies as deps
from app.domain.models import Proveedor, Hold


class FakeBuscar:
    def execute(self, session, *, servicio_id, fecha, limit=50, offset=0):
        # return two fake providers
        return [
            Proveedor(id="p1", nombre="Prov Uno", rating_prom=4.5, email="a@b", telefono="111", status=1),
            Proveedor(id="p2", nombre="Prov Dos", rating_prom=4.0, email="c@d", telefono="222", status=1),
        ]


class FakeCrearHold:
    def __init__(self):
        self.store = {}

    def execute(self, session, *, proveedor_id, opcion_servicio_id, inicio, fin, ttl_min=30, correlation_id=None, created_by=None):
        hid = f"hold-{len(self.store)+1}"
        expira = datetime.now() + timedelta(minutes=ttl_min)
        h = Hold(id=hid, proveedor_id=proveedor_id, opcion_servicio_id=opcion_servicio_id,
                 inicio=inicio, fin=fin, expira_en=expira, status=0, correlation_id=correlation_id, created_by=created_by)
        self.store[hid] = h
        return h


class FakeConfirmarHold:
    def __init__(self, creator: FakeCrearHold):
        self.creator = creator

    def execute(self, session, hold_id: str):
        h = self.creator.store.get(hold_id)
        if not h:
            raise Exception("HoldNoEncontrado")
        h.status = 1
        return h


class FakeLiberarHold:
    def __init__(self, creator: FakeCrearHold):
        self.creator = creator

    def execute(self, session, hold_id: str):
        h = self.creator.store.get(hold_id)
        if not h:
            raise Exception("HoldNoEncontrado")
        h.status = 3
        return None


class FakeObtenerHold:
    def __init__(self, creator: FakeCrearHold):
        self.creator = creator

    def execute(self, session, hold_id: str):
        return self.creator.store.get(hold_id)


def setup_overrides():
    fake_buscar = FakeBuscar()
    fake_crear = FakeCrearHold()
    fake_confirm = FakeConfirmarHold(fake_crear)
    fake_liberar = FakeLiberarHold(fake_crear)
    fake_obtener = FakeObtenerHold(fake_crear)
    # The routers call the factory functions directly (not via FastAPI Depends),
    # so patch the module-level factories in `deps` to return our fakes.
    # This avoids creating real repositories or DB sessions during tests.
    deps.get_buscar_disponibles_use_case = lambda proveedor_query=None: fake_buscar
    deps.get_crear_hold_use_case = lambda holds_repo=None: fake_crear
    deps.get_confirmar_hold_use_case = lambda holds_repo=None: fake_confirm
    deps.get_liberar_hold_use_case = lambda holds_repo=None: fake_liberar
    deps.get_obtener_hold_use_case = lambda holds_repo=None: fake_obtener

    # Replace get_db_session with a simple generator that yields a dummy session
    def _fake_db_session(settings=None):
        class DummySession:
            def execute(self, *args, **kwargs):
                class DummyResult:
                    def mappings(self):
                        return []
                return DummyResult()
        yield DummySession()

    deps.get_db_session = _fake_db_session
    # Also patch the router modules which import these factories at module import time
    from app.entrypoints.fastapi import router_public, router_internal
    router_public.get_buscar_disponibles_use_case = lambda proveedor_query=None: fake_buscar
    router_public.get_db_session = _fake_db_session

    router_internal.get_crear_hold_use_case = lambda holds_repo=None: fake_crear
    router_internal.get_confirmar_hold_use_case = lambda holds_repo=None: fake_confirm
    router_internal.get_liberar_hold_use_case = lambda holds_repo=None: fake_liberar
    router_internal.get_obtener_hold_use_case = lambda holds_repo=None: fake_obtener
    router_internal.get_db_session = _fake_db_session


def test_public_health_and_buscar_disponibles():
    setup_overrides()
    client = TestClient(app)

    # Health
    r = client.get("/proveedores/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

    # Buscar disponibles
    params = {"servicio_id": "svc1", "fecha": date.today().isoformat(), "limit": 5}
    r = client.get("/proveedores/v1/proveedores/disponibles", params=params)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["id"] == "p1"


def test_internal_hold_flow():
    setup_overrides()
    client = TestClient(app)

    # Create hold (internal)
    start = (datetime.now() + timedelta(hours=1)).isoformat()
    end = (datetime.now() + timedelta(hours=5)).isoformat()
    payload = {
        "proveedor_id": "p1",
        "opcion_servicio_id": "o1",
        "inicio": start,
        "fin": end,
        "ttl_min": 30,
        "correlation_id": "test-123",
        "created_by": "test"
    }
    headers = {"X-Service-Token": "dev-internal-token-change-in-production"}
    r = client.post("/proveedores/internal/holds", json=payload, headers=headers)
    assert r.status_code == 201
    hold = r.json()
    hid = hold["id"]

    # Get hold
    r = client.get(f"/proveedores/internal/holds/{hid}", headers=headers)
    assert r.status_code == 200
    got = r.json()
    assert got["id"] == hid

    # Confirm hold
    r = client.patch(f"/proveedores/internal/holds/{hid}/confirm", headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == 1

    # Liberar hold
    r = client.delete(f"/proveedores/internal/holds/{hid}", headers=headers)
    assert r.status_code == 204
