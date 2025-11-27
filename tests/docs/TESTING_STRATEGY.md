# Estructura de Testing - Eventos Perú

**Versión**: 1.0.0  
**Fecha**: 27 de Noviembre, 2025  
**Estado**: ✅ Implementado

---

## 📋 Estructura Propuesta

```
eventos-peru-hexagonal/
├── tests/                                    # 🆕 Tests centralizados del sistema
│   ├── README.md                            # Documentación de tests
│   ├── conftest.py                          # Configuración compartida pytest
│   ├── pytest.ini                           # Configuración pytest global
│   │
│   ├── unit/                                # Tests unitarios (caja blanca)
│   │   ├── test_iam_security.py            # JWT, hashing, tokens
│   │   ├── test_catalogo_logic.py          # Lógica de negocio catálogo
│   │   ├── test_proveedores_holds.py       # Lógica de holds
│   │   └── test_contratacion_states.py     # Estados de pedido
│   │
│   ├── integration/                         # Tests de integración por servicio
│   │   ├── test_iam_service.py             # Endpoints IAM completos
│   │   ├── test_catalogo_service.py        # Endpoints Catálogo completos
│   │   ├── test_proveedores_service.py     # Endpoints Proveedores completos
│   │   └── test_contratacion_service.py    # Endpoints Contratación completos
│   │
│   ├── e2e/                                 # Tests end-to-end (flujos completos)
│   │   ├── test_client_flow.py             # Flujo completo cliente
│   │   ├── test_admin_flow.py              # Flujo completo admin
│   │   └── test_integrated_flow.py         # Flujo integrado (todos los servicios)
│   │
│   ├── security/                            # Tests de seguridad
│   │   ├── test_authentication.py          # Autenticación JWT
│   │   ├── test_authorization.py           # Roles y permisos (RBAC)
│   │   └── test_endpoints_by_role.py       # Validación endpoint por rol
│   │
│   └── performance/                         # Tests de rendimiento (opcional)
│       └── test_load.py                    # Tests de carga (locust/pytest-benchmark)
│
└── services/
    ├── iam-service/test/                   # Tests específicos de IAM
    │   ├── README.md
    │   ├── conftest.py
    │   └── test_iam_unit.py               # Solo tests unitarios del servicio
    │
    ├── catalogo-service/test/
    │   └── test_catalogo_unit.py
    │
    ├── proveedores-service/test/
    │   └── test_proveedores_unit.py
    │
    └── contratacion-service/test/
        └── test_contratacion_unit.py
```

---

## 🎯 Tipos de Tests

### 1. Tests Unitarios (`tests/unit/`)

**Propósito**: Validar lógica de negocio aislada (sin BD, sin HTTP)

**Características**:
- ✅ Rápidos (<100ms cada uno)
- ✅ Sin dependencias externas
- ✅ Usan mocks/stubs
- ✅ Alta cobertura de código

**Ejemplo**:
```python
# tests/unit/test_iam_security.py
def test_password_hashing():
    """Valida que el hash bcrypt funciona correctamente"""
    plain = "MyPassword123"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_creation():
    """Valida creación de JWT con claims correctos"""
    token = create_token(subject="user123", claims={"role": "ADMIN"})
    decoded = decode_token(token)
    assert decoded["sub"] == "user123"
    assert decoded["role"] == "ADMIN"
```

---

### 2. Tests de Integración (`tests/integration/`)

**Propósito**: Validar endpoints individuales de cada servicio

**Características**:
- ✅ Requiere servicios corriendo
- ✅ Prueba HTTP + BD
- ✅ Un servicio a la vez
- ✅ Autenticación real

**Estructura**:
```python
# tests/integration/test_iam_service.py
class TestIAMAuth:
    def test_login_success(self, admin_credentials):
        """Login exitoso retorna token válido"""
        response = client.post("/iam/auth/login", json=admin_credentials)
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_invalid_password(self):
        """Login con contraseña incorrecta retorna 401"""
        response = client.post("/iam/auth/login", json={
            "email": "admin@eventos.pe",
            "password": "WrongPassword"
        })
        assert response.status_code == 401

class TestIAMAdmin:
    def test_list_users_as_admin(self, admin_token):
        """Admin puede listar usuarios"""
        response = client.get("/iam/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        assert "users" in response.json()
```

---

### 3. Tests E2E (`tests/e2e/`)

**Propósito**: Validar flujos completos end-to-end

**Características**:
- ✅ Todos los servicios corriendo
- ✅ Flujos de usuario reales
- ✅ Comunicación inter-servicios
- ✅ Validación completa

**Flujos**:
1. **Cliente Completo**: Login → Consultar catálogo → Crear pedido → Ver estado
2. **Admin Completo**: Login → Ver pedidos → Cotizar → Aprobar → Asignar proveedor
3. **Integrado**: Cliente crea pedido → Admin lo gestiona → Proveedores asignados

**Estructura**:
```python
# tests/e2e/test_client_flow.py
def test_client_complete_flow():
    """Flujo completo: Cliente crea y consulta pedido"""
    
    # Paso 1: Login
    client_token = login_as_client()
    assert client_token is not None
    
    # Paso 2: Consultar catálogo
    paquetes = get_paquetes(client_token)
    assert len(paquetes) > 0
    
    # Paso 3: Crear pedido
    pedido_id = create_pedido(client_token, paquetes[0]['id'])
    assert pedido_id is not None
    
    # Paso 4: Consultar pedido creado
    pedido = get_pedido(client_token, pedido_id)
    assert pedido['estado'] == 'DRAFT'
    
    # Paso 5: Listar mis pedidos
    mis_pedidos = get_mis_pedidos(client_token)
    assert any(p['id'] == pedido_id for p in mis_pedidos)
```

---

### 4. Tests de Seguridad (`tests/security/`)

**Propósito**: Validar autenticación, autorización y control de acceso

**Características**:
- ✅ Validación JWT
- ✅ Roles y permisos (RBAC)
- ✅ Endpoints protegidos
- ✅ Tokens expirados/inválidos

**Estructura**:
```python
# tests/security/test_authorization.py
def test_admin_endpoints_require_admin_role():
    """Endpoints admin rechazan token de cliente"""
    client_token = login_as_client()
    
    # Cliente intenta acceder endpoint admin
    response = client.get("/iam/admin/users", headers={"Authorization": f"Bearer {client_token}"})
    assert response.status_code == 403

def test_client_can_only_see_own_pedidos():
    """Cliente solo puede ver sus propios pedidos"""
    client1_token = login_as("cliente1@eventos.pe", "password")
    client2_token = login_as("cliente2@eventos.pe", "password")
    
    # Cliente 1 crea pedido
    pedido_id = create_pedido(client1_token)
    
    # Cliente 2 intenta acceder pedido de Cliente 1
    response = client.get(f"/contratacion/pedidos/{pedido_id}", headers={"Authorization": f"Bearer {client2_token}"})
    assert response.status_code == 403
```

---

## 🚀 Ejecución de Tests

### Todos los Tests

```powershell
# Ejecutar todos los tests
pytest tests/

# Con reporte HTML
pytest tests/ --html=tests/reports/report.html --self-contained-html

# Con cobertura
pytest tests/ --cov=services --cov-report=html
```

### Tests por Tipo

```powershell
# Solo unitarios (rápidos)
pytest tests/unit/ -v

# Solo integración (requiere servicios corriendo)
pytest tests/integration/ -v

# Solo E2E (flujos completos)
pytest tests/e2e/ -v

# Solo seguridad
pytest tests/security/ -v
```

### Tests por Servicio

```powershell
# Solo IAM
pytest tests/integration/test_iam_service.py -v

# Solo Catálogo
pytest tests/integration/test_catalogo_service.py -v

# Solo Proveedores
pytest tests/integration/test_proveedores_service.py -v

# Solo Contratación
pytest tests/integration/test_contratacion_service.py -v
```

### Tests Específicos

```powershell
# Un test específico
pytest tests/e2e/test_client_flow.py::test_client_complete_flow -v

# Tests que contengan palabra clave
pytest tests/ -k "login" -v
```

---

## 📝 Configuración Compartida

### `tests/conftest.py`

Fixtures compartidas para todos los tests:

```python
import pytest
import requests
from typing import Dict

# URLs de servicios
IAM_URL = "http://127.0.0.1:8010"
CATALOGO_URL = "http://127.0.0.1:8020"
PROVEEDORES_URL = "http://127.0.0.1:8030"
CONTRATACION_URL = "http://127.0.0.1:8040"

# Credenciales de prueba
ADMIN_EMAIL = "admin@eventos.pe"
ADMIN_PASSWORD = "Evoluti0n"
CLIENT_EMAIL = "jorge.martinez711@eventos.pe"
CLIENT_PASSWORD = "Evoluti0n"

@pytest.fixture(scope="session")
def admin_token():
    """Token de administrador (reutilizable en toda la sesión)"""
    response = requests.post(
        f"{IAM_URL}/iam/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    return response.json()["access_token"]

@pytest.fixture(scope="session")
def client_token():
    """Token de cliente (reutilizable en toda la sesión)"""
    response = requests.post(
        f"{IAM_URL}/iam/auth/login",
        json={"email": CLIENT_EMAIL, "password": CLIENT_PASSWORD}
    )
    return response.json()["access_token"]

@pytest.fixture
def admin_headers(admin_token):
    """Headers con token admin"""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def client_headers(client_token):
    """Headers con token cliente"""
    return {"Authorization": f"Bearer {client_token}"}
```

### `tests/pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Tests unitarios (rápidos, sin dependencias)
    integration: Tests de integración (requiere servicios)
    e2e: Tests end-to-end (flujos completos)
    security: Tests de seguridad
    slow: Tests lentos (>1s)
    smoke: Tests de humo (críticos)
```

---

## 📊 Reportes

### Generar Reporte HTML

```powershell
pytest tests/ --html=tests/reports/report_$(Get-Date -Format 'yyyyMMdd_HHmmss').html --self-contained-html
```

### Generar Reporte de Cobertura

```powershell
pytest tests/ --cov=services --cov-report=html --cov-report=term
# Ver en: htmlcov/index.html
```

### Generar Reporte JUnit (CI/CD)

```powershell
pytest tests/ --junitxml=tests/reports/junit.xml
```

---

## 🎯 Ventajas de Esta Estructura

### ✅ Separación Clara

- **Unit**: Lógica de negocio (sin servicios)
- **Integration**: Endpoints individuales (un servicio)
- **E2E**: Flujos completos (todos los servicios)
- **Security**: Autenticación y autorización

### ✅ Reutilización

- Fixtures compartidas (`conftest.py`)
- Helpers comunes
- Credenciales centralizadas

### ✅ Escalabilidad

- Fácil agregar nuevos tests
- Organización por tipo y servicio
- Independencia entre tests

### ✅ CI/CD Ready

- Compatible con GitHub Actions
- Reportes JUnit
- Cobertura de código
- Tests paralelos

### ✅ Documentación

- README por carpeta
- Tests auto-documentados
- Ejemplos claros

---

## 📚 Documentación por Test

Cada test debe incluir:

```python
def test_login_success():
    """
    Test: Login exitoso retorna token válido
    
    Pre-condiciones:
    - Usuario admin@eventos.pe existe en BD
    - Contraseña es "Evoluti0n"
    
    Pasos:
    1. POST /iam/auth/login con credenciales válidas
    2. Verificar status code 200
    3. Verificar que response contiene access_token
    4. Verificar que token es válido (puede decodificarse)
    
    Post-condiciones:
    - Token puede usarse para endpoints autenticados
    - Token expira en 120 minutos
    
    Esperado:
    - status_code: 200
    - access_token: presente y válido
    - token_type: "bearer"
    """
    response = client.post("/iam/auth/login", json={
        "email": "admin@eventos.pe",
        "password": "Evoluti0n"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verificar que el token es válido
    token = data["access_token"]
    decoded = decode_token(token)
    assert decoded["sub"] is not None
```

---

## 🔄 Migración desde Estructura Actual

### Paso 1: Crear Nueva Estructura

```powershell
# Crear carpetas
New-Item -Path "tests/unit" -ItemType Directory -Force
New-Item -Path "tests/integration" -ItemType Directory -Force
New-Item -Path "tests/e2e" -ItemType Directory -Force
New-Item -Path "tests/security" -ItemType Directory -Force
```

### Paso 2: Mover Tests Existentes

```powershell
# Mover test_e2e_flows.py
Move-Item tools/test_e2e_flows.py tests/e2e/

# Mover validate_endpoints_by_role.py
Move-Item tools/validate_endpoints_by_role.py tests/security/test_endpoints_by_role.py
```

### Paso 3: Refactorizar Tests de Servicios

```powershell
# Crear tests de integración desde tests de servicios
# Los tests en services/*/test/ se convierten en tests/integration/
```

---

## 📌 Recomendaciones

### ✅ DO

- ✅ Usar fixtures de pytest para reutilizar código
- ✅ Documentar cada test con docstrings
- ✅ Agrupar tests relacionados en clases
- ✅ Usar markers para categorizar (`@pytest.mark.integration`)
- ✅ Limpiar datos después de cada test
- ✅ Usar variables de entorno para configuración
- ✅ Ejecutar tests en orden lógico

### ❌ DON'T

- ❌ Tests con dependencias entre sí
- ❌ Hardcodear URLs o credenciales
- ❌ Tests sin documentación
- ❌ Modificar datos de producción
- ❌ Tests lentos en suite unitaria
- ❌ Ignorar fallos intermitentes

---

## 🎯 Próximos Pasos

1. ✅ Crear estructura de carpetas `tests/`
2. ✅ Migrar tests existentes
3. ✅ Crear `conftest.py` compartido
4. ✅ Agregar tests de seguridad
5. ✅ Configurar cobertura de código
6. ✅ Integrar con CI/CD
7. ✅ Agregar tests de performance (opcional)

---

**Última Actualización**: 27 de Noviembre, 2025
