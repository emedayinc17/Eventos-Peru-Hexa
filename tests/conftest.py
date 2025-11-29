import os
import pytest
import requests

# Configuración central para tests
API_BASE = os.getenv("API_BASE", "http://localhost:8000")
IAM_EMAIL = os.getenv("TEST_IAM_EMAIL", "cliente@test.com")
IAM_PASSWORD = os.getenv("TEST_IAM_PASSWORD", "Cliente123!")


@pytest.fixture(scope="session")
def api_base():
    return API_BASE


@pytest.fixture(scope="session")
def token(api_base):
    """Obtiene token de IAM. Si no está disponible, marca las pruebas como skip."""
    try:
        resp = requests.post(f"{api_base}/api/iam/login", json={"email": IAM_EMAIL, "password": IAM_PASSWORD}, timeout=5)
    except Exception:
        pytest.skip("IAM no disponible en {api_base}; omitiendo tests que requieren token")
    if resp.status_code != 200:
        pytest.skip(f"Login falló ({resp.status_code}); revisar credenciales o servicio IAM")
    return resp.json().get("access_token")
