from fastapi.testclient import TestClient

from app.entrypoints.fastapi.main import app
from app.domain.models import TipoEvento, PaqueteResumen, PaqueteDetalle, ItemPaquete


def mock_list_tipos(*args, **kwargs):
    return [TipoEvento(id="t1", nombre="Matrimonio", descripcion="", status=1)]


def mock_list_paquetes(*args, **kwargs):
    return [
        PaqueteResumen(id="p1", codigo="P-001", nombre="Paquete A", moneda="PEN", monto_total=0, descripcion="", tipo_evento_id=None, tipo_evento_nombre=None, status=1)
    ]


def mock_get_paquete_detalle(*args, **kwargs):
    item = ItemPaquete(opcion_servicio_id="o1", cantidad=1, precio_unit_vigente=0, moneda="PEN", opcion_nombre="Opcion 1", opcion_detalles={}, servicio_id="s1", servicio_nombre="S1", servicio_descripcion="", proveedores=[])
    return PaqueteDetalle(id="p1", codigo="P-001", nombre="Paquete A", moneda="PEN", monto_total=0, items=[item], descripcion="", status=1)


# Override dependencies
app.dependency_overrides.clear()
from app.entrypoints.fastapi import router as catalogo_router_module
from app.entrypoints.fastapi.dependencies import (
    get_list_tipos_evento_use_case,
    get_list_paquetes_use_case,
    get_get_paquete_detalle_use_case,
)


def fake_get_list_tipos_evento_use_case():
    class UC:
        def execute(self, *args, **kwargs):
            return mock_list_tipos()

    return UC()


def fake_get_list_paquetes_use_case():
    class UC:
        def execute(self, *args, **kwargs):
            return mock_list_paquetes()

    return UC()


def fake_get_paquete_detalle_use_case():
    class UC:
        def execute(self, *args, **kwargs):
            return mock_get_paquete_detalle()

    return UC()


app.dependency_overrides[get_list_tipos_evento_use_case] = lambda: fake_get_list_tipos_evento_use_case()
app.dependency_overrides[get_list_paquetes_use_case] = lambda: fake_get_list_paquetes_use_case()
app.dependency_overrides[get_get_paquete_detalle_use_case] = lambda: fake_get_paquete_detalle_use_case()


client = TestClient(app)


def test_list_tipos():
    resp = client.get("/catalogo/v1/tipos")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["nombre"] == "Matrimonio"


def test_list_paquetes():
    resp = client.get("/catalogo/v1/paquetes")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["codigo"] == "P-001"


def test_get_paquete_detalle():
    resp = client.get("/catalogo/v1/paquetes/p1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "p1"
    assert "items" in data
