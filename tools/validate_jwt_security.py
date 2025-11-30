"""
Script de Validación de Seguridad JWT
Prueba todos los endpoints protegidos contra accesos no autorizados

Tests:
1. Sin token → 401
2. Token inválido → 401
3. Token con firma incorrecta → 401
4. Token expirado → 401
5. Token con rol incorrecto → 403
6. Token válido con rol correcto → 200/201/204

Ejecutar:
    python tools/validate_jwt_security.py
"""
import os
import requests
import time
from datetime import datetime, timedelta
from jose import jwt
from typing import Dict, List, Tuple, Optional

# === CONFIGURACIÓN ===
IAM = os.getenv('IAM_ROOT', 'http://127.0.0.1:8010')
CATALOGO = os.getenv('CATALOGO_ROOT', 'http://127.0.0.1:8020')
PROVEEDORES = os.getenv('PROVEEDORES_ROOT', 'http://127.0.0.1:8030')
CONTRATACION = os.getenv('CONTRATACION_ROOT', 'http://127.0.0.1:8040')

CLIENT_EMAIL = 'demo@eventos.pe'
CLIENT_PASSWORD = 'Admin_2025!'
ADMIN_EMAIL = 'admin@eventos.pe'
ADMIN_PASSWORD = 'Admin_2025!'

# JWT Secret: prefer env or ev_shared settings. For local dev the script
# previously had a hardcoded secret; we keep a fallback for local testing
# but print a clear warning so CI/CD or production deployments use Vault.
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

if not JWT_SECRET:
    try:
        # Try loading shared settings (if this script is run with project path available)
        from ev_shared.config import load_settings
        s = load_settings()
        JWT_SECRET = getattr(s, 'JWT_SECRET', None) or JWT_SECRET
        JWT_ALGORITHM = getattr(s, 'JWT_ALG', getattr(s, 'JWT_ALGORITHM', JWT_ALGORITHM))
    except Exception:
        # ignore if ev_shared not importable
        pass

if not JWT_SECRET:
    # Fallback to the old hardcoded secret for local convenience, but warn loudly.
    JWT_SECRET = 'a040a67e53c324bb01e72d86e732e5db25cdc99a8c6bc29e20355e5c44bfcbfc'
    print('\n⚠️  WARNING: No JWT_SECRET configured via env or ev_shared settings.\n' \
          'This script will use an insecure hardcoded secret for local testing only.\n' \
          'In production, set the `JWT_SECRET` via Vault and do NOT use hardcoded secrets.\n')

# === HELPERS ===

def login(email: str, password: str) -> Optional[str]:
    """Login y obtener token válido"""
    try:
        r = requests.post(
            f'{IAM}/iam/auth/login',
            json={'email': email, 'password': password},
            timeout=8
        )
        if r.status_code == 200:
            data = r.json()
            return data.get('access_token')
    except Exception as e:
        print(f'❌ Error login {email}: {e}')
    return None


def create_fake_token(role: str = 'CLIENTE', expired: bool = False) -> str:
    """Crea un token JWT con firma correcta pero claims custom"""
    exp = datetime.utcnow() - timedelta(hours=1) if expired else datetime.utcnow() + timedelta(hours=1)
    payload = {
        'sub': 'fake-user-id',
        'username': 'fake@eventos.pe',
        'role': role,
        'exp': exp
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_invalid_token() -> str:
    """Crea un token con firma incorrecta"""
    payload = {
        'sub': 'fake-user-id',
        'username': 'fake@eventos.pe',
        'role': 'ADMIN',
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, 'wrong-secret-key', algorithm=JWT_ALGORITHM)


# === PRUEBAS ===

class SecurityTest:
    def __init__(self, service: str, method: str, path: str, required_role: str = None, needs_body: bool = False):
        self.service = service
        self.method = method
        self.path = path
        self.required_role = required_role
        self.needs_body = needs_body
        self.results = []
    
    def get_url(self) -> str:
        base = {
            'IAM': IAM,
            'CATALOGO': CATALOGO,
            'PROVEEDORES': PROVEEDORES,
            'CONTRATACION': CONTRATACION
        }[self.service]
        return f'{base}{self.path}'
    
    def get_body(self) -> Optional[Dict]:
        """Retorna body mínimo si el endpoint lo requiere"""
        if not self.needs_body:
            return None
        
        # Bodies mínimos por endpoint
        if 'tipos' in self.path and self.method == 'POST':
            return {'nombre': 'Test Tipo'}
        elif 'servicios' in self.path and self.method == 'POST':
            return {'nombre': 'Test Servicio', 'tipo_evento_id': '44444444-1111-1111-1111-111111111111'}
        elif 'opciones' in self.path and self.method == 'POST':
            return {'servicio_id': 'aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa', 'nombre': 'Test Opcion', 'moneda': 'PEN', 'monto': 100}
        elif 'paquetes' in self.path and self.method == 'POST':
            return {'codigo': 'TEST001', 'nombre': 'Test Paquete', 'items': []}
        elif 'items' in self.path and self.method == 'POST':
            return {'items': []}
        elif 'items' in self.path and self.method == 'DELETE':
            return {'item_ids': []}
        elif 'estado' in self.path or self.method == 'PATCH':
            return {'estado': 1}
        elif 'asignar-proveedor' in self.path:
            return {
                'proveedor_id': 'cccccccc-3333-4444-5555-cccccccccccc',
                'item_pedido_id': 'fake-item-id',
                'opcion_servicio_id': 'bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb',
                'fecha_inicio': '2025-12-20T14:00:00',
                'fecha_fin': '2025-12-20T18:00:00',
                'monto': 1500.0
            }
        return {}
    
    def test(self, token: Optional[str], expected_status: int, test_name: str):
        """Ejecuta una prueba de seguridad"""
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        body = self.get_body()
        url = self.get_url()
        
        try:
            if self.method == 'GET':
                r = requests.get(url, headers=headers, timeout=5)
            elif self.method == 'POST':
                r = requests.post(url, headers=headers, json=body, timeout=5)
            elif self.method == 'PUT':
                r = requests.put(url, headers=headers, json=body, timeout=5)
            elif self.method == 'PATCH':
                r = requests.patch(url, headers=headers, json=body, timeout=5)
            elif self.method == 'DELETE':
                r = requests.delete(url, headers=headers, json=body, timeout=5)
            else:
                raise ValueError(f'Método no soportado: {self.method}')
            
            status = r.status_code
            passed = status == expected_status
            
            result = {
                'test': test_name,
                'expected': expected_status,
                'actual': status,
                'passed': passed
            }
            self.results.append(result)
            
            symbol = '✅' if passed else '❌'
            print(f'{symbol} {test_name}: esperado {expected_status}, obtenido {status}')
            
        except Exception as e:
            result = {
                'test': test_name,
                'expected': expected_status,
                'actual': f'ERROR: {str(e)}',
                'passed': False
            }
            self.results.append(result)
            print(f'❌ {test_name}: ERROR - {e}')
    
    def run_all_tests(self, client_token: str, admin_token: str):
        """Ejecuta todas las pruebas de seguridad para este endpoint"""
        print(f'\n🔒 Probando: {self.method} {self.path} (Rol requerido: {self.required_role or "Cualquiera"})')
        
        # Test 1: Sin token
        self.test(None, 401, '1. Sin token')
        
        # Test 2: Token inválido
        self.test('invalid-token-format', 401, '2. Token inválido')
        
        # Test 3: Token con firma incorrecta
        invalid_token = create_invalid_token()
        self.test(invalid_token, 401, '3. Firma incorrecta')
        
        # Test 4: Token expirado
        expired_token = create_fake_token(role='ADMIN', expired=True)
        self.test(expired_token, 401, '4. Token expirado')
        
        # Test 5: Rol incorrecto
        if self.required_role == 'ADMIN':
            self.test(client_token, 403, '5. Rol CLIENTE (esperado ADMIN)')
        elif self.required_role == 'CLIENTE':
            # Si requiere CLIENTE, probar con token que no sea CLIENTE
            fake_cliente = create_fake_token(role='OTRO_ROL')
            self.test(fake_cliente, 403, '5. Rol incorrecto')
        
        # Test 6: Token válido con rol correcto
        if self.required_role == 'ADMIN':
            # Aquí el 404 es aceptable porque el recurso fake no existe
            # Lo importante es que NO sea 401/403 (pasó la autenticación)
            self.test(admin_token, None, '6. Token ADMIN válido (esperado éxito o 404)')
        elif self.required_role == 'CLIENTE':
            self.test(client_token, None, '6. Token CLIENTE válido (esperado éxito o 404)')
        else:
            # Endpoint protegido pero sin rol específico
            self.test(client_token, None, '6. Token válido (esperado éxito o 404)')


# === DEFINICIÓN DE ENDPOINTS A PROBAR ===

def get_protected_endpoints() -> List[SecurityTest]:
    """Lista de todos los endpoints protegidos del sistema"""
    tests = []
    
    # === IAM: Endpoints con autenticación ===
    tests.append(SecurityTest('IAM', 'GET', '/iam/me', required_role=None))
    tests.append(SecurityTest('IAM', 'GET', '/iam/admin/users', required_role='ADMIN'))
    tests.append(SecurityTest('IAM', 'GET', '/iam/admin/users/fake-id', required_role='ADMIN'))
    tests.append(SecurityTest('IAM', 'POST', '/iam/admin/users', required_role='ADMIN', needs_body=True))
    tests.append(SecurityTest('IAM', 'PATCH', '/iam/admin/users/fake-id', required_role='ADMIN', needs_body=True))
    tests.append(SecurityTest('IAM', 'DELETE', '/iam/admin/users/fake-id', required_role='ADMIN'))
    
    # === CATÁLOGO: Endpoints admin ===
    tests.append(SecurityTest('CATALOGO', 'POST', '/catalogo/v1/admin/tipos', required_role='ADMIN', needs_body=True))
    tests.append(SecurityTest('CATALOGO', 'PUT', '/catalogo/v1/admin/tipos/fake-id', required_role='ADMIN', needs_body=True))
    tests.append(SecurityTest('CATALOGO', 'DELETE', '/catalogo/v1/admin/tipos/fake-id', required_role='ADMIN'))
    
    tests.append(SecurityTest('CATALOGO', 'POST', '/catalogo/v1/admin/servicios', required_role='ADMIN', needs_body=True))
    tests.append(SecurityTest('CATALOGO', 'PUT', '/catalogo/v1/admin/servicios/fake-id', required_role='ADMIN', needs_body=True))
    tests.append(SecurityTest('CATALOGO', 'DELETE', '/catalogo/v1/admin/servicios/fake-id', required_role='ADMIN'))
    
    tests.append(SecurityTest('CATALOGO', 'POST', '/catalogo/v1/admin/opciones', required_role='ADMIN', needs_body=True))
    tests.append(SecurityTest('CATALOGO', 'PUT', '/catalogo/v1/admin/opciones/fake-id', required_role='ADMIN', needs_body=True))
    tests.append(SecurityTest('CATALOGO', 'DELETE', '/catalogo/v1/admin/opciones/fake-id', required_role='ADMIN'))
    
    tests.append(SecurityTest('CATALOGO', 'POST', '/catalogo/v1/admin/paquetes', required_role='ADMIN', needs_body=True))
    tests.append(SecurityTest('CATALOGO', 'PUT', '/catalogo/v1/admin/paquetes/fake-id', required_role='ADMIN', needs_body=True))
    tests.append(SecurityTest('CATALOGO', 'DELETE', '/catalogo/v1/admin/paquetes/fake-id', required_role='ADMIN'))
    
    # === CONTRATACIÓN: Endpoints cliente y admin ===
    tests.append(SecurityTest('CONTRATACION', 'GET', '/contratacion/pedidos/mios', required_role=None))
    tests.append(SecurityTest('CONTRATACION', 'GET', '/contratacion/pedidos/fake-id', required_role=None))
    
    tests.append(SecurityTest('CONTRATACION', 'GET', '/contratacion/admin/pedidos', required_role='ADMIN'))
    tests.append(SecurityTest('CONTRATACION', 'GET', '/contratacion/admin/pedidos/fake-id', required_role='ADMIN'))
    tests.append(SecurityTest('CONTRATACION', 'PATCH', '/contratacion/admin/pedidos/fake-id', required_role='ADMIN', needs_body=True))
    tests.append(SecurityTest('CONTRATACION', 'POST', '/contratacion/admin/pedidos/fake-id/items', required_role='ADMIN', needs_body=True))
    tests.append(SecurityTest('CONTRATACION', 'DELETE', '/contratacion/admin/pedidos/fake-id/items', required_role='ADMIN', needs_body=True))
    tests.append(SecurityTest('CONTRATACION', 'POST', '/contratacion/admin/pedidos/fake-id/asignar-proveedor', required_role='ADMIN', needs_body=True))
    
    return tests


# === MAIN ===

def main():
    print('='*80)
    print('🔐 VALIDACIÓN DE SEGURIDAD JWT')
    print('='*80)
    print('\nObteniendo tokens de autenticación...')
    
    # 1. Obtener tokens reales
    client_token = login(CLIENT_EMAIL, CLIENT_PASSWORD)
    admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    
    if not client_token:
        print('❌ No se pudo obtener token de cliente')
        return
    if not admin_token:
        print('❌ No se pudo obtener token de admin')
        return
    
    print(f'✅ Token cliente obtenido (longitud: {len(client_token)})')
    print(f'✅ Token admin obtenido (longitud: {len(admin_token)})')
    
    # 2. Ejecutar pruebas
    tests = get_protected_endpoints()
    print(f'\n📋 Total de endpoints a probar: {len(tests)}')
    print(f'🎯 Total de pruebas a ejecutar: {len(tests) * 6}')
    
    for test in tests:
        test.run_all_tests(client_token, admin_token)
        time.sleep(0.1)  # Pequeña pausa entre tests
    
    # 3. Resumen
    print('\n' + '='*80)
    print('📊 RESUMEN DE RESULTADOS')
    print('='*80)
    
    total_tests = sum(len(t.results) for t in tests)
    passed = sum(1 for t in tests for r in t.results if r['passed'])
    failed = total_tests - passed
    
    print(f'\nTotal pruebas: {total_tests}')
    print(f'✅ Pasadas: {passed}')
    print(f'❌ Fallidas: {failed}')
    print(f'📈 Tasa de éxito: {(passed/total_tests*100):.1f}%')
    
    # 4. Detalles de fallas
    if failed > 0:
        print('\n⚠️  DETALLES DE FALLAS:')
        for test in tests:
            for result in test.results:
                if not result['passed']:
                    print(f'  ❌ {test.service} {test.method} {test.path} - {result["test"]}')
                    print(f'      Esperado: {result["expected"]}, Obtenido: {result["actual"]}')
    else:
        print('\n🎉 ¡TODOS LOS TESTS PASARON!')
        print('✅ La seguridad JWT está correctamente implementada')


if __name__ == '__main__':
    main()
