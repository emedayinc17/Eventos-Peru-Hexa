"""
Configuración compartida de pytest para todos los tests

Este archivo contiene fixtures globales que pueden ser utilizadas
en cualquier test del proyecto.
"""
import pytest
import requests
from typing import Dict, Optional
import os

# ============================================================================
# CONFIGURACIÓN DE SERVICIOS
# ============================================================================

IAM_URL = os.getenv("IAM_URL", "http://127.0.0.1:8010")
CATALOGO_URL = os.getenv("CATALOGO_URL", "http://127.0.0.1:8020")
PROVEEDORES_URL = os.getenv("PROVEEDORES_URL", "http://127.0.0.1:8030")
CONTRATACION_URL = os.getenv("CONTRATACION_URL", "http://127.0.0.1:8040")

# ============================================================================
# CREDENCIALES DE PRUEBA
# ============================================================================

ADMIN_EMAIL = "admin@eventos.pe"
ADMIN_PASSWORD = "Evoluti0n"
CLIENT_EMAIL = "jorge.martinez711@eventos.pe"
CLIENT_PASSWORD = "Evoluti0n"

# ============================================================================
# IDs DE PRUEBA (desde db/script2.sql)
# ============================================================================

TEST_TIPO_EVENTO_ID = "11111111-1111-1111-1111-111111111111"  # Matrimonio
TEST_SERVICE_ID = "aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa"     # Servicio Prueba
TEST_OPTION_ID = "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb"      # Opción Prueba
TEST_PROVIDER_ID = "cccccccc-3333-4444-5555-cccccccccccc"    # Proveedor Prueba

# ============================================================================
# FIXTURES DE AUTENTICACIÓN
# ============================================================================

@pytest.fixture(scope="session")
def admin_token() -> str:
    """
    Token de administrador válido para toda la sesión de tests.
    
    Se autentica una vez al inicio y reutiliza el token.
    Útil para tests que requieren permisos de admin.
    """
    response = requests.post(
        f"{IAM_URL}/iam/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=10
    )
    assert response.status_code == 200, f"Login admin falló: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def client_token() -> str:
    """
    Token de cliente válido para toda la sesión de tests.
    
    Se autentica una vez al inicio y reutiliza el token.
    Útil para tests que requieren permisos de cliente.
    """
    response = requests.post(
        f"{IAM_URL}/iam/auth/login",
        json={"email": CLIENT_EMAIL, "password": CLIENT_PASSWORD},
        timeout=10
    )
    assert response.status_code == 200, f"Login cliente falló: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token: str) -> Dict[str, str]:
    """Headers HTTP con token de administrador"""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def client_headers(client_token: str) -> Dict[str, str]:
    """Headers HTTP con token de cliente"""
    return {
        "Authorization": f"Bearer {client_token}",
        "Content-Type": "application/json"
    }


# ============================================================================
# FIXTURES DE URLs
# ============================================================================

@pytest.fixture
def iam_url() -> str:
    """URL base del servicio IAM"""
    return IAM_URL


@pytest.fixture
def catalogo_url() -> str:
    """URL base del servicio Catálogo"""
    return CATALOGO_URL


@pytest.fixture
def proveedores_url() -> str:
    """URL base del servicio Proveedores"""
    return PROVEEDORES_URL


@pytest.fixture
def contratacion_url() -> str:
    """URL base del servicio Contratación"""
    return CONTRATACION_URL


# ============================================================================
# FIXTURES DE IDs DE PRUEBA
# ============================================================================

@pytest.fixture
def test_tipo_evento_id() -> str:
    """ID de tipo de evento de prueba (Matrimonio)"""
    return TEST_TIPO_EVENTO_ID


@pytest.fixture
def test_service_id() -> str:
    """ID de servicio de prueba"""
    return TEST_SERVICE_ID


@pytest.fixture
def test_option_id() -> str:
    """ID de opción de servicio de prueba"""
    return TEST_OPTION_ID


@pytest.fixture
def test_provider_id() -> str:
    """ID de proveedor de prueba"""
    return TEST_PROVIDER_ID


# ============================================================================
# FIXTURES DE HELPERS
# ============================================================================

@pytest.fixture
def api_client():
    """
    Cliente HTTP configurado con timeouts razonables.
    
    Útil para hacer requests HTTP en tests.
    """
    class APIClient:
        @staticmethod
        def get(url: str, headers: Optional[Dict] = None, **kwargs):
            return requests.get(url, headers=headers, timeout=10, **kwargs)
        
        @staticmethod
        def post(url: str, headers: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs):
            return requests.post(url, headers=headers, json=json, timeout=10, **kwargs)
        
        @staticmethod
        def patch(url: str, headers: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs):
            return requests.patch(url, headers=headers, json=json, timeout=10, **kwargs)
        
        @staticmethod
        def delete(url: str, headers: Optional[Dict] = None, **kwargs):
            return requests.delete(url, headers=headers, timeout=10, **kwargs)
    
    return APIClient()


# ============================================================================
# HOOKS DE PYTEST
# ============================================================================

def pytest_configure(config):
    """Configuración antes de ejecutar tests"""
    print("\n🚀 Iniciando suite de tests - Eventos Perú")
    print(f"   IAM: {IAM_URL}")
    print(f"   Catálogo: {CATALOGO_URL}")
    print(f"   Proveedores: {PROVEEDORES_URL}")
    print(f"   Contratación: {CONTRATACION_URL}\n")


def pytest_collection_modifyitems(config, items):
    """Modifica items de tests antes de ejecución"""
    # Agregar marker 'slow' a tests que tarden más de 1 segundo
    for item in items:
        if "e2e" in item.nodeid:
            item.add_marker(pytest.mark.slow)


def pytest_sessionfinish(session, exitstatus):
    """Hook ejecutado al finalizar sesión de tests"""
    if exitstatus == 0:
        print("\n✅ Todos los tests pasaron exitosamente")
    else:
        print(f"\n❌ Tests finalizados con errores (exit code: {exitstatus})")
