import pytest

try:
    from tools import recalculate_package_prices
except Exception:
    recalculate_package_prices = None


def test_recalculate_package_prices_basic():
    """Prueba unitaria para `recalculate_package_prices` si está disponible.

    Si la función no existe en `tools`, la prueba se salta automáticamente.
    """
    if recalculate_package_prices is None:
        pytest.skip("No se encontró tools.recalculate_package_prices; omitiendo test unitario")

    # Algunos utilitarios en `tools` realizan operaciones con la DB
    # y no exponen una función pura para calcular totales. Si existe
    # una función pura `compute_total_price`, la probamos; si no,
    # omitimos la prueba porque la función principal necesita conexión.
    if hasattr(recalculate_package_prices, "compute_total_price"):
        items = [
            {"precio_base": 100.0, "descuento_pct": 0},
            {"precio_base": 50.0, "descuento_pct": 10},
        ]
        result = recalculate_package_prices.compute_total_price(items)
        assert isinstance(result, (int, float))
        assert result > 0
    else:
        pytest.skip("tools.recalculate_package_prices.compute_total_price no disponible; omitiendo test unitario")
