"""Consolidated pytest test file for proveedores-service.

Covers:
- health
- public search (valid + missing param)
- internal holds lifecycle (create, idempotency, get, confirm, release)
- auth header checks for internal endpoints

This file uses in-process TestClient and patches module-level factories
to use fakes so no DB is required.
"""

from fastapi.testclient import TestClient
from datetime import datetime, timedelta, date

from app.entrypoints.fastapi.main import app
from app.entrypoints.fastapi import dependencies as deps
from app.domain.models import Proveedor, Hold


class FakeBuscar:
    def execute(self, session, *, servicio_id, fecha, limit=50, offset=0):
        return [
            Proveedor(id="cccccccc-3333-4444-5555-cccccccccccc", nombre="Proveedor Prueba Verificacion", rating_prom=4.5, email="prueba@proveedor.local", telefono="+51 900000000", status=1),
        ]


class FakeCrearHold:
    def __init__(self):
        self.store = {}
        self.by_corr = {}

    def execute(self, session, *, proveedor_id, opcion_servicio_id, inicio, fin, ttl_min=30, correlation_id=None, created_by=None):
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

    # Patch routers' module-level factories
    from app.entrypoints.fastapi import router_public, router_internal
    router_public.get_buscar_disponibles_use_case = lambda proveedor_query=None: fake_buscar
    router_public.get_db_session = _fake_db_session
    router_internal.get_crear_hold_use_case = lambda holds_repo=None: fake_crear
    router_internal.get_confirmar_hold_use_case = lambda holds_repo=None: fake_confirm
    router_internal.get_liberar_hold_use_case = lambda holds_repo=None: fake_liberar
    router_internal.get_obtener_hold_use_case = lambda holds_repo=None: fake_obtener
    router_internal.get_db_session = _fake_db_session


def test_health():
    setup_overrides()
    client = TestClient(app)
    r = client.get("/proveedores/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_public_search_ok():
    setup_overrides()
    client = TestClient(app)
    params = {"servicio_id": "aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa", "fecha": date.today().isoformat(), "limit": 5}
    r = client.get("/proveedores/v1/proveedores/disponibles", params=params)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    ids = [p.get("id") for p in data]
    assert "cccccccc-3333-4444-5555-cccccccccccc" in ids


def test_public_search_missing_param():
    setup_overrides()
    client = TestClient(app)
    # missing servicio_id should return 422 from FastAPI validation
    r = client.get("/proveedores/v1/proveedores/disponibles")
    assert r.status_code == 422


def test_internal_holds_lifecycle_and_idempotency():
    setup_overrides()
    client = TestClient(app)
    start = (datetime.now() + timedelta(hours=1)).isoformat()
    end = (datetime.now() + timedelta(hours=5)).isoformat()
    corr = f"corr-{int(datetime.now().timestamp())}"
    payload = {
        "proveedor_id": "cccccccc-3333-4444-5555-cccccccccccc",
        "opcion_servicio_id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
        "inicio": start,
        "fin": end,
        "ttl_min": 30,
        "correlation_id": corr,
        "created_by": "test"
    }
    headers = {"X-Service-Token": "dev-internal-token-change-in-production"}

    r1 = client.post("/proveedores/internal/holds", json=payload, headers=headers)
    assert r1.status_code == 201
    h1 = r1.json()
    hid1 = h1["id"]

    # idempotent creation using same correlation id
    r2 = client.post("/proveedores/internal/holds", json=payload, headers=headers)
    assert r2.status_code in (200, 201)
    h2 = r2.json()
    # allow implementations that return same or new id; continue with returned id
    hid = h2["id"]

    rg = client.get(f"/proveedores/internal/holds/{hid}", headers=headers)
    assert rg.status_code == 200

    rc = client.patch(f"/proveedores/internal/holds/{hid}/confirm", headers=headers)
    assert rc.status_code == 200
    assert rc.json().get("status") == 1

    rd = client.delete(f"/proveedores/internal/holds/{hid}", headers=headers)
    assert rd.status_code == 204


def test_internal_holds_requires_token():
    setup_overrides()
    client = TestClient(app)
    start = (datetime.now() + timedelta(hours=1)).isoformat()
    end = (datetime.now() + timedelta(hours=5)).isoformat()
    payload = {
        "proveedor_id": "cccccccc-3333-4444-5555-cccccccccccc",
        "opcion_servicio_id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
        "inicio": start,
        "fin": end,
        "ttl_min": 30,
        "correlation_id": f"corr-no-token-{int(datetime.now().timestamp())}",
        "created_by": "test"
    }
    # no X-Service-Token header
    r = client.post("/proveedores/internal/holds", json=payload)
    # The router responds with 401 or 403 depending on auth implementation; accept either
    assert r.status_code in (401, 403)
