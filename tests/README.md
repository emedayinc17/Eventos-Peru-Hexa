# Tests - Sistema Eventos Perú

**Versión**: 1.0.0  
**Fecha**: 27 de Noviembre, 2025  
**Estado**: ✅ Completo

---

## 📁 Estructura de Tests

```
tests/
├── README.md                           # Este archivo
├── conftest.py                         # Configuración compartida (fixtures)
├── pytest.ini                          # Configuración de pytest
│
├── unit/                               # Tests unitarios (sin BD, sin HTTP)
│   └── (pendiente implementación)
│
├── integration/                        # Tests de integración por servicio
│   ├── test_iam_service.py            # ✅ IAM Service (9 tests)
│   ├── test_catalogo_service.py       # 🔄 Pendiente
│   ├── test_proveedores_service.py    # 🔄 Pendiente
│   └── test_contratacion_service.py   # 🔄 Pendiente
│
├── e2e/                                # Tests end-to-end (flujos completos)
│   └── test_complete_flows.py         # ✅ 3 flujos (23 pasos)
│
├── security/                           # Tests de seguridad
│   └── test_authorization.py          # ✅ Validación por roles (27 endpoints)
│
└── reports/                            # Reportes generados
    └── .gitkeep
```

---

## 🎯 Tipos de Tests

### 1. Tests Unitarios (`unit/`)

**Estado**: 🔄 Pendiente  
**Propósito**: Validar lógica de negocio aislada  
**Requiere**: Nada (sin dependencias externas)  
**Tiempo**: <100ms por test

**Ejemplo**:
```python
def test_password_hashing():
    """Valida que bcrypt funciona correctamente"""
    plain = "MyPassword123"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True
```

### 2. Tests de Integración (`integration/`)

**Estado**: ✅ IAM completado, otros pendientes  
**Propósito**: Validar endpoints individuales  
**Requiere**: Servicios corriendo  
**Tiempo**: <1s por test

**Implementados**:
- ✅ **IAM Service**: 9 tests
  - Health check
  - Login (admin/cliente)
  - Perfil de usuario
  - Listar usuarios (admin)
  - Crear usuario (admin)

**Pendientes**:
- 🔄 Catálogo Service
- 🔄 Proveedores Service
- 🔄 Contratación Service

### 3. Tests E2E (`e2e/`)

**Estado**: ✅ Completo  
**Propósito**: Validar flujos completos  
**Requiere**: Todos los servicios corriendo  
**Tiempo**: ~45 segundos

**Flujos Implementados**:
- ✅ **Flujo Cliente**: 6 pasos
  1. Login cliente
  2. Consultar perfil
  3. Crear pedido
  4. Listar mis pedidos
  5. Consultar detalle
  6. Intentar acceso admin (403)

- ✅ **Flujo Admin**: 8 pasos
  1. Login admin
  2. Crear pedido
  3. Listar todos los pedidos
  4. Consultar detalle
  5. Cambiar a COTIZADO
  6. Cambiar a APROBADO
  7. Asignar proveedor
  8. Verificar reserva

- ✅ **Flujo Integrado**: 9 pasos
  1. Cliente: Login
  2. Cliente: Consultar catálogo
  3. Cliente: Crear pedido
  4. Admin: Login
  5. Admin: Listar pedidos
  6. Admin: Cotizar
  7. Admin: Aprobar
  8. Admin: Asignar proveedor
  9. Cliente: Ver pedido actualizado

**Resultado**: 100% éxito (3/3 flujos)

### 4. Tests de Seguridad (`security/`)

**Estado**: ✅ Completo  
**Propósito**: Validar autenticación y autorización  
**Requiere**: Servicios corriendo  
**Tiempo**: ~30 segundos

**Validaciones**:
- ✅ **Endpoints ADMIN**: 16/16 accesibles solo con rol ADMIN
- ✅ **Endpoints CLIENTE**: 11/11 bloqueados para clientes
- ✅ Tokens JWT válidos/inválidos
- ✅ RBAC (Role-Based Access Control)

---

## 🚀 Ejecución de Tests

### Todos los Tests

```powershell
# Ejecutar todos los tests
pytest tests/ -v

# Con reporte HTML
pytest tests/ --html=tests/reports/report.html --self-contained-html

# Con cobertura
pytest tests/ --cov=services --cov-report=html --cov-report=term
```

### Tests por Tipo

```powershell
# Solo integración
pytest tests/integration/ -v

# Solo E2E
pytest tests/e2e/ -v

# Solo seguridad
pytest tests/security/ -v
```

### Tests Específicos

```powershell
# IAM Service
pytest tests/integration/test_iam_service.py -v

# Flujos E2E
pytest tests/e2e/test_complete_flows.py -v

# Autorización
pytest tests/security/test_authorization.py -v
```

### Filtros Útiles

```powershell
# Solo tests rápidos (excluir slow)
pytest tests/ -v -m "not slow"

# Solo tests de integración
pytest tests/ -v -m "integration"

# Tests que contengan "login"
pytest tests/ -k "login" -v

# Detener en primer fallo
pytest tests/ -x -v
```

---

## 📊 Estado Actual

| Categoría | Tests | Estado | Cobertura |
|-----------|-------|--------|-----------|
| **Unit** | 0 | 🔄 Pendiente | 0% |
| **Integration - IAM** | 9 | ✅ Completo | 100% |
| **Integration - Catálogo** | 0 | 🔄 Pendiente | 0% |
| **Integration - Proveedores** | 0 | 🔄 Pendiente | 0% |
| **Integration - Contratación** | 0 | 🔄 Pendiente | 0% |
| **E2E** | 3 flujos (23 pasos) | ✅ Completo | 100% |
| **Security** | 27 endpoints | ✅ Completo | 100% |

**Total**: ~40 tests implementados

---

## 📝 Convenciones

### Nomenclatura de Tests

```python
def test_<funcionalidad>_<condición>_<resultado_esperado>():
    """Descripción clara del test"""
    pass

# Ejemplos:
def test_login_valid_credentials_returns_token():
    """Login con credenciales válidas retorna token JWT"""
    pass

def test_get_profile_without_token_returns_403():
    """Acceder a perfil sin token retorna 403 Forbidden"""
    pass
```

### Documentación de Tests

Cada test debe incluir docstring con:
- **Descripción**: ¿Qué valida el test?
- **Pre-condiciones**: ¿Qué debe existir antes?
- **Pasos**: ¿Qué hace el test?
- **Esperado**: ¿Cuál es el resultado esperado?

```python
def test_example():
    """
    Test: Descripción breve
    
    Pre-condiciones:
    - Usuario existe en BD
    - Servicio está corriendo
    
    Pasos:
    1. Hacer login
    2. Obtener token
    3. Validar token
    
    Esperado:
    - status_code: 200
    - access_token: presente
    """
    pass
```

### Markers

Usa markers de pytest para categorizar:

```python
@pytest.mark.integration
def test_endpoint():
    """Test de integración"""
    pass

@pytest.mark.e2e
@pytest.mark.slow
def test_complete_flow():
    """Test E2E que tarda varios segundos"""
    pass

@pytest.mark.security
def test_authorization():
    """Test de seguridad"""
    pass
```

---

## 🔧 Configuración

### Variables de Entorno

```powershell
# Opcional: Cambiar URLs de servicios
$env:IAM_URL = "http://127.0.0.1:8010"
$env:CATALOGO_URL = "http://127.0.0.1:8020"
$env:PROVEEDORES_URL = "http://127.0.0.1:8030"
$env:CONTRATACION_URL = "http://127.0.0.1:8040"
```

### Fixtures Globales

Disponibles en todos los tests (ver `conftest.py`):

- `admin_token`: Token JWT de administrador
- `client_token`: Token JWT de cliente
- `admin_headers`: Headers con token admin
- `client_headers`: Headers con token cliente
- `iam_url`, `catalogo_url`, `proveedores_url`, `contratacion_url`
- `test_service_id`, `test_option_id`, `test_provider_id`

**Uso**:
```python
def test_example(admin_headers, iam_url):
    response = requests.get(f"{iam_url}/iam/me", headers=admin_headers)
    assert response.status_code == 200
```

---

## 📈 Reportes

### Reporte HTML

```powershell
# Generar reporte HTML
pytest tests/ --html=tests/reports/report.html --self-contained-html

# Abrir reporte
Start-Process tests/reports/report.html
```

### Reporte de Cobertura

```powershell
# Generar cobertura
pytest tests/ --cov=services --cov-report=html

# Ver reporte
Start-Process htmlcov/index.html
```

### Reporte JUnit (CI/CD)

```powershell
# Para integración con CI/CD
pytest tests/ --junitxml=tests/reports/junit.xml
```

---

## 🎯 Próximos Pasos

1. ✅ ~~Estructura de carpetas creada~~
2. ✅ ~~Configuración pytest (conftest.py, pytest.ini)~~
3. ✅ ~~Tests de integración IAM~~
4. ✅ ~~Tests E2E migrados~~
5. ✅ ~~Tests de seguridad migrados~~
6. 🔄 Tests de integración Catálogo
7. 🔄 Tests de integración Proveedores
8. 🔄 Tests de integración Contratación
9. 🔄 Tests unitarios (lógica de negocio)
10. 🔄 Integración con CI/CD

---

## 📚 Referencias

### Documentación de Testing
- [`docs/TESTING_STRATEGY.md`](docs/TESTING_STRATEGY.md) - Estrategia completa de testing
- [`docs/IMPLEMENTATION_SUMMARY.md`](docs/IMPLEMENTATION_SUMMARY.md) - Resumen de implementación

### Documentación del Proyecto
- [`../docs/API_DOCUMENTATION.md`](../docs/API_DOCUMENTATION.md) - Documentación de API
- [`../docs/TEST_E2E_REPORT.md`](../docs/TEST_E2E_REPORT.md) - Reporte E2E detallado

### Herramientas
- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-html](https://pytest-html.readthedocs.io/)

---

**Última Actualización**: 27 de Noviembre, 2025  
**Mantenido por**: Emeday Inc.
