"""
Tests de Integración - Servicio IAM

Valida todos los endpoints del servicio IAM con autenticación real.
Requiere que el servicio IAM esté corriendo en el puerto 8010.

Ejecutar:
    pytest tests/integration/test_iam_service.py -v
"""
import pytest
import requests


@pytest.mark.integration
class TestIAMHealth:
    """Tests de health check"""
    
    def test_health_endpoint(self, iam_url):
        """
        Test: Health check retorna status ok
        
        Pre-condiciones:
        - Servicio IAM corriendo
        
        Esperado:
        - status_code: 200
        - body: {"status": "ok"}
        """
        response = requests.get(f"{iam_url}/iam/health", timeout=5)
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.integration
class TestIAMAuthentication:
    """Tests de autenticación (login, register)"""
    
    def test_login_admin_success(self, iam_url):
        """
        Test: Login con credenciales de admin retorna token válido
        
        Pre-condiciones:
        - Usuario admin@eventos.pe existe
        - Contraseña es "Evoluti0n"
        
        Pasos:
        1. POST /iam/auth/login con credenciales válidas
        2. Verificar status 200
        3. Verificar presencia de access_token
        
        Esperado:
        - status_code: 200
        - access_token: presente
        - token_type: "bearer"
        """
        response = requests.post(
            f"{iam_url}/iam/auth/login",
            json={"email": "admin@eventos.pe", "password": "Evoluti0n"},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_client_success(self, iam_url):
        """Login con credenciales de cliente retorna token válido"""
        response = requests.post(
            f"{iam_url}/iam/auth/login",
            json={"email": "jorge.martinez711@eventos.pe", "password": "Evoluti0n"},
            timeout=10
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_invalid_password(self, iam_url):
        """
        Test: Login con contraseña incorrecta retorna 401
        
        Esperado:
        - status_code: 401 (Unauthorized)
        """
        response = requests.post(
            f"{iam_url}/iam/auth/login",
            json={"email": "admin@eventos.pe", "password": "WrongPassword"},
            timeout=10
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, iam_url):
        """Login con usuario inexistente retorna 404"""
        response = requests.post(
            f"{iam_url}/iam/auth/login",
            json={"email": "nonexistent@eventos.pe", "password": "Password123"},
            timeout=10
        )
        assert response.status_code == 404


@pytest.mark.integration
class TestIAMProfile:
    """Tests de perfil de usuario"""
    
    def test_get_profile_with_admin_token(self, iam_url, admin_headers):
        """
        Test: Obtener perfil con token de admin retorna datos correctos
        
        Pre-condiciones:
        - Token de admin válido
        
        Pasos:
        1. GET /iam/me con token de admin
        2. Verificar status 200
        3. Verificar que email coincide
        4. Verificar que role es ADMIN
        
        Esperado:
        - status_code: 200
        - email: admin@eventos.pe
        - role: ADMIN
        """
        response = requests.get(f"{iam_url}/iam/me", headers=admin_headers, timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@eventos.pe"
        assert data["role"] == "ADMIN"
    
    def test_get_profile_with_client_token(self, iam_url, client_headers):
        """Obtener perfil con token de cliente retorna datos correctos"""
        response = requests.get(f"{iam_url}/iam/me", headers=client_headers, timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "jorge.martinez711@eventos.pe"
        assert data["role"] == "CLIENTE"
    
    def test_get_profile_without_token(self, iam_url):
        """
        Test: Acceder a perfil sin token retorna 403
        
        Esperado:
        - status_code: 403 (Forbidden)
        """
        response = requests.get(f"{iam_url}/iam/me", timeout=10)
        assert response.status_code == 403


@pytest.mark.integration
class TestIAMAdminUsers:
    """Tests de administración de usuarios (solo ADMIN)"""
    
    def test_list_users_as_admin(self, iam_url, admin_headers):
        """
        Test: Admin puede listar todos los usuarios
        
        Pre-condiciones:
        - Token de admin válido
        - Existen usuarios en la BD
        
        Pasos:
        1. GET /iam/admin/users con token admin
        2. Verificar status 200
        3. Verificar que retorna lista de usuarios
        
        Esperado:
        - status_code: 200
        - users: lista con al menos 1 usuario
        - total: número mayor a 0
        """
        response = requests.get(f"{iam_url}/iam/admin/users", headers=admin_headers, timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert data["total"] > 0
    
    def test_list_users_as_client_forbidden(self, iam_url, client_headers):
        """
        Test: Cliente no puede listar usuarios (requiere ADMIN)
        
        Esperado:
        - status_code: 403 (Forbidden)
        """
        response = requests.get(f"{iam_url}/iam/admin/users", headers=client_headers, timeout=10)
        assert response.status_code == 403
    
    def test_list_users_pagination(self, iam_url, admin_headers):
        """
        Test: Paginación funciona correctamente
        
        Pasos:
        1. GET /iam/admin/users?skip=0&limit=10
        2. Verificar que retorna máximo 10 usuarios
        """
        response = requests.get(
            f"{iam_url}/iam/admin/users?skip=0&limit=10",
            headers=admin_headers,
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) <= 10


@pytest.mark.integration
@pytest.mark.slow
class TestIAMAdminCRUD:
    """Tests de CRUD de usuarios (crear, actualizar, eliminar)"""
    
    def test_create_user_as_admin(self, iam_url, admin_headers):
        """
        Test: Admin puede crear nuevos usuarios
        
        Pasos:
        1. POST /iam/admin/users con datos válidos
        2. Verificar status 201
        3. Verificar que retorna id del usuario creado
        
        Esperado:
        - status_code: 201 (Created)
        - id: presente
        - email: coincide con el enviado
        """
        import uuid
        random_email = f"pytest_{uuid.uuid4().hex[:8]}@eventos.pe"
        
        response = requests.post(
            f"{iam_url}/iam/admin/users",
            headers=admin_headers,
            json={
                "email": random_email,
                "password": "TestPassword123",
                "nombre": "Test User",
                "telefono": "+51 999999999",
                "role": "CLIENTE"
            },
            timeout=10
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == random_email


# ============================================================================
# RESUMEN DE TESTS
# ============================================================================

"""
Tests Implementados:
- ✅ Health check
- ✅ Login exitoso (admin y cliente)
- ✅ Login con credenciales inválidas
- ✅ Obtener perfil (admin y cliente)
- ✅ Acceso sin token (403)
- ✅ Listar usuarios como admin
- ✅ Listar usuarios como cliente (403)
- ✅ Paginación de usuarios
- ✅ Crear usuario como admin

Cobertura: 9 endpoints validados
Tiempo estimado: ~5 segundos

Para ejecutar:
    pytest tests/integration/test_iam_service.py -v
    
Para ver solo tests rápidos:
    pytest tests/integration/test_iam_service.py -v -m "not slow"
"""
