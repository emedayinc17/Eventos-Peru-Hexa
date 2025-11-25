import pytest
from fastapi.testclient import TestClient
import uuid
import sys
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================================
CURRENT = Path(__file__).resolve()
IAM_ROOT = CURRENT.parents[1]
PROJECT_ROOT = CURRENT.parents[3]

for p in (IAM_ROOT, PROJECT_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Importaciones de la aplicación
from app.entrypoints.fastapi.main import app
from app.infrastructure.security.password_adapter import hash_password, verify_password
from app.infrastructure.security.jwt_adapter import create_token, decode_token

client = TestClient(app)

# ============================================================================
# CONTEXTO COMPARTIDO
# ============================================================================
class Context:
    user_email = None
    user_password = "TestPassword123!"
    user_token = None
    user_id = None
    admin_token = None
    admin_email = "admin@eventos.pe"
    admin_password = "Admin_2025!"

ctx = Context()

# ============================================================================
# PRUEBAS UNITARIAS (Caja Blanca - Seguridad)
# ============================================================================

def test_unit_password_hashing():
    """Valida hash y verificación de contraseñas"""
    plain = "Admin123*"
    hashed = hash_password(plain)
    assert verify_password("Admin123*", hashed) is True
    assert verify_password("WrongPass", hashed) is False

def test_unit_jwt_tokens():
    """Valida generación y decodificación de tokens JWT"""
    secret = "TEST_SECRET_KEY_123456"
    subject = "admin@test.com"
    claims = {"role": "ADMIN"}

    token = create_token(
        subject=subject,
        claims=claims,
        secret=secret,
        expires_minutes=15,
    )

    decoded = decode_token(token, secret=secret, algorithms=["HS256"])
    assert decoded["sub"] == subject
    assert decoded["role"] == "ADMIN"

# ============================================================================
# PRUEBAS DE INTEGRACIÓN (Flujo de Endpoints)
# ============================================================================

def test_api_01_health():
    """Validar que el servicio responde (Health Check)"""
    response = client.get("/iam/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_api_02_register_user():
    """Validar registro de nuevo usuario"""
    random_id = str(uuid.uuid4())[:8]
    ctx.user_email = f"pytest_{random_id}@eventos.pe"
    
    payload = {
        "email": ctx.user_email,
        "password": ctx.user_password,
        "nombre": f"Pytest User {random_id}",
        "telefono": "+51 900 000 000"
    }
    
    response = client.post("/iam/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == ctx.user_email
    assert "id" in data
    ctx.user_id = data["id"]

def test_api_03_login_user():
    """Validar login con el usuario creado"""
    payload = {
        "email": ctx.user_email,
        "password": ctx.user_password
    }
    response = client.post("/iam/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "CLIENTE"
    ctx.user_token = data["access_token"]

def test_api_04_get_me():
    """Validar endpoint /me con token de usuario"""
    headers = {"Authorization": f"Bearer {ctx.user_token}"}
    response = client.get("/iam/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == ctx.user_email
    assert data["role"] == "CLIENTE"

def test_api_05_login_admin():
    """Validar login de administrador"""
    payload = {
        "email": ctx.admin_email,
        "password": ctx.admin_password
    }
    response = client.post("/iam/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "ADMIN"
    ctx.admin_token = data["access_token"]

def test_api_06_admin_list_users():
    """Validar listado de usuarios (Solo Admin)"""
    headers = {"Authorization": f"Bearer {ctx.admin_token}"}
    response = client.get("/iam/admin/users?limit=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Verificar que el usuario creado está en la lista
    found = any(u["email"] == ctx.user_email for u in data)
    assert found

def test_api_07_admin_get_user_detail():
    """Validar detalle de usuario (Solo Admin)"""
    headers = {"Authorization": f"Bearer {ctx.admin_token}"}
    response = client.get(f"/iam/admin/users/{ctx.user_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ctx.user_id
    assert data["email"] == ctx.user_email

def test_api_08_admin_patch_user():
    """Validar actualización parcial de usuario (Solo Admin)"""
    headers = {"Authorization": f"Bearer {ctx.admin_token}"}
    new_name = "Pytest User Updated"
    payload = {"nombre": new_name}
    
    response = client.patch(f"/iam/admin/users/{ctx.user_id}", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == new_name

def test_api_09_client_access_denied_to_admin():
    """Validar que un cliente NO puede acceder a rutas de admin"""
    headers = {"Authorization": f"Bearer {ctx.user_token}"}
    response = client.get("/iam/admin/users", headers=headers)
    assert response.status_code == 403

def test_api_10_admin_delete_user():
    """Validar eliminación lógica de usuario (Solo Admin)"""
    headers = {"Authorization": f"Bearer {ctx.admin_token}"}
    response = client.delete(f"/iam/admin/users/{ctx.user_id}", headers=headers)
    assert response.status_code == 204
    
    # Intentar login debería fallar
    payload = {
        "email": ctx.user_email,
        "password": ctx.user_password
    }
    response = client.post("/iam/auth/login", json=payload)
    assert response.status_code == 401
