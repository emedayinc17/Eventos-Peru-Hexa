import pytest

try:
    from tools import check_prices
except Exception:
    check_prices = None


def test_validate_price_basic():
    """Comprueba la existencia de una función de validación de precios.

    Si `tools.check_prices.validate_price` no existe, la prueba se salta.
    """
    if check_prices is None or not hasattr(check_prices, "validate_price"):
        pytest.skip("tools.check_prices.validate_price no disponible; omitiendo")

    validate = getattr(check_prices, "validate_price")
    assert validate(10.0) is True
    assert validate(0) is False
