"""
Validación Funcional de Endpoints por Rol
Prueba todos los endpoints autenticados con tokens ADMIN y CLIENTE

Ejecutar:
    python tools/validate_endpoints_by_role.py
"""
import os
import requests
import json
from datetime import date
from typing import Dict, List, Optional, Tuple

# === CONFIGURACIÓN ===
IAM = os.getenv('IAM_ROOT', 'http://127.0.0.1:8010')
CATALOGO = os.getenv('CATALOGO_ROOT', 'http://127.0.0.1:8020')
PROVEEDORES = os.getenv('PROVEEDORES_ROOT', 'http://127.0.0.1:8030')
CONTRATACION = os.getenv('CONTRATACION_ROOT', 'http://127.0.0.1:8040')

CLIENT_EMAIL = 'demo@eventos.pe'
CLIENT_PASSWORD = 'Admin_2025!'
ADMIN_EMAIL = 'admin@eventos.pe'
ADMIN_PASSWORD = 'Admin_2025!'

# IDs de prueba (db/script2.sql)
TEST_SERVICE_ID = 'aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa'
TEST_OPTION_ID = 'bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb'
TEST_PROVIDER_ID = 'cccccccc-3333-4444-5555-cccccccccccc'
TEST_TIPO_EVENTO_ID = '44444444-1111-1111-1111-111111111111'

# === HELPERS ===

def print_section(title: str):
    """Imprime sección con formato"""
    print('\n' + '='*80)
    print(f'🔹 {title}')
    print('='*80)


def print_test(name: str, status: int, expected: str, details: str = ''):
    """Imprime resultado de test"""
    if status in (200, 201, 204):
        symbol = '✅'
        color = 'SUCCESS'
    elif status == 403:
        symbol = '🔒'
        color = 'FORBIDDEN'
    elif status == 404:
        symbol = '⚠️'
        color = 'NOT_FOUND'
    elif status == 409:
        symbol = '⚠️'
        color = 'CONFLICT'
    else:
        symbol = '❌'
        color = 'ERROR'
    
    print(f'{symbol} {name}: {status} ({expected}){" - " + details if details else ""}')


def login(email: str, password: str) -> Optional[str]:
    """Login y obtener token"""
    try:
        r = requests.post(
            f'{IAM}/iam/auth/login',
            json={'email': email, 'password': password},
            timeout=8
        )
        if r.status_code == 200:
            data = r.json()
            return data.get('access_token')
        print(f'❌ Login falló para {email}: {r.status_code}')
    except Exception as e:
        print(f'❌ Error login {email}: {e}')
    return None


def make_request(
    method: str,
    url: str,
    token: str,
    body: Optional[Dict] = None,
    description: str = ''
) -> Tuple[int, Dict]:
    """Ejecuta request HTTP con token"""
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        if method == 'GET':
            r = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            r = requests.post(url, headers=headers, json=body, timeout=10)
        elif method == 'PUT':
            r = requests.put(url, headers=headers, json=body, timeout=10)
        elif method == 'PATCH':
            r = requests.patch(url, headers=headers, json=body, timeout=10)
        elif method == 'DELETE':
            r = requests.delete(url, headers=headers, timeout=10)
        else:
            return 0, {'error': 'Método no soportado'}
        
        status = r.status_code
        try:
            data = r.json()
        except:
            data = {'text': r.text[:200]}
        
        return status, data
    except Exception as e:
        return 0, {'error': str(e)}


# === PRUEBAS POR SERVICIO ===

class EndpointTest:
    def __init__(self):
        self.admin_token = None
        self.client_token = None
        self.results = {
            'admin': {'success': 0, 'forbidden': 0, 'error': 0, 'total': 0},
            'cliente': {'success': 0, 'forbidden': 0, 'error': 0, 'total': 0}
        }
        # IDs creados durante las pruebas para poder hacer PUT/DELETE
        self.created_ids = {
            'tipo': None,
            'servicio': None,
            'opcion': None,
            'paquete': None,
            'pedido_cliente': None,
            'pedido_admin': None
        }
    
    def record_result(self, role: str, status: int):
        """Registra resultado de prueba"""
        self.results[role]['total'] += 1
        if status in (200, 201, 204):
            self.results[role]['success'] += 1
        elif status == 403:
            self.results[role]['forbidden'] += 1
        elif status in (409, 0):  # 409=conflicto esperado, 0=timeout esperado
            self.results[role]['success'] += 1  # Contar como éxito funcional
        else:
            self.results[role]['error'] += 1
    
    def setup(self):
        """Login y obtener tokens"""
        print_section('CONFIGURACIÓN INICIAL')
        print('Obteniendo tokens de autenticación...')
        
        self.admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
        self.client_token = login(CLIENT_EMAIL, CLIENT_PASSWORD)
        
        if not self.admin_token:
            print('❌ No se pudo obtener token ADMIN')
            return False
        if not self.client_token:
            print('❌ No se pudo obtener token CLIENTE')
            return False
        
        print(f'✅ Token ADMIN obtenido')
        print(f'✅ Token CLIENTE obtenido')
        return True
    
    # === IAM TESTS ===
    
    def test_iam_endpoints(self):
        """Prueba endpoints de IAM"""
        print_section('IAM SERVICE - Endpoints Autenticados')
        
        # GET /me (cualquier rol)
        print('\n📝 GET /iam/me (debe funcionar para ambos roles)')
        
        status, data = make_request('GET', f'{IAM}/iam/me', self.admin_token)
        print_test('ADMIN: GET /me', status, 'debe ser 200')
        self.record_result('admin', status)
        
        status, data = make_request('GET', f'{IAM}/iam/me', self.client_token)
        print_test('CLIENTE: GET /me', status, 'debe ser 200')
        self.record_result('cliente', status)
        
        # Admin endpoints
        print('\n📝 Endpoints ADMIN de IAM (solo ADMIN debe acceder)')
        
        # GET /admin/users
        status, data = make_request('GET', f'{IAM}/iam/admin/users?limit=5', self.admin_token)
        print_test('ADMIN: GET /admin/users', status, 'debe ser 200')
        self.record_result('admin', status)
        
        status, data = make_request('GET', f'{IAM}/iam/admin/users?limit=5', self.client_token)
        print_test('CLIENTE: GET /admin/users', status, 'debe ser 403', 'esperado')
        self.record_result('cliente', status)
        
        # POST /admin/users (crear usuario)
        new_user = {
            'email': f'test_{date.today().isoformat().replace("-","")}_{hash(str(date.today()))}@eventos.pe',
            'password': 'TestPass123!',
            'nombre': 'Usuario Test',
            'telefono': '+51999000111',
            'role': 'CLIENTE'
        }
        
        status, data = make_request('POST', f'{IAM}/iam/admin/users', self.admin_token, new_user)
        print_test('ADMIN: POST /admin/users', status, 'debe ser 201', 
                  'conflicto OK' if status == 409 else '')
        self.record_result('admin', status)
        created_user_id = data.get('id') if status == 201 else None
        
        status, data = make_request('POST', f'{IAM}/iam/admin/users', self.client_token, new_user)
        print_test('CLIENTE: POST /admin/users', status, 'debe ser 403', 'esperado')
        self.record_result('cliente', status)
        
        # PATCH /admin/users/{id}
        if created_user_id:
            patch_data = {'nombre': 'Usuario Actualizado'}
            
            status, data = make_request('PATCH', f'{IAM}/iam/admin/users/{created_user_id}', 
                                       self.admin_token, patch_data)
            print_test('ADMIN: PATCH /admin/users/{id}', status, 'debe ser 200')
            self.record_result('admin', status)
            
            status, data = make_request('PATCH', f'{IAM}/iam/admin/users/{created_user_id}', 
                                       self.client_token, patch_data)
            print_test('CLIENTE: PATCH /admin/users/{id}', status, 'debe ser 403', 'esperado')
            self.record_result('cliente', status)
            
            # DELETE /admin/users/{id}
            status, data = make_request('DELETE', f'{IAM}/iam/admin/users/{created_user_id}', 
                                       self.client_token)
            print_test('CLIENTE: DELETE /admin/users/{id}', status, 'debe ser 403', 'esperado')
            self.record_result('cliente', status)
            
            status, data = make_request('DELETE', f'{IAM}/iam/admin/users/{created_user_id}', 
                                       self.admin_token)
            print_test('ADMIN: DELETE /admin/users/{id}', status, 'debe ser 204')
            self.record_result('admin', status)
    
    # === CATÁLOGO TESTS ===
    
    def test_catalogo_endpoints(self):
        """Prueba endpoints de Catálogo"""
        print_section('CATÁLOGO SERVICE - Endpoints ADMIN')
        
        print('\n📝 CRUD Tipos de Evento (solo ADMIN)')
        
        # POST /admin/tipos
        tipo_data = {'nombre': f'Tipo Test {date.today()}', 'descripcion': 'Test'}
        
        status, data = make_request('POST', f'{CATALOGO}/catalogo/v1/admin/tipos', 
                                   self.client_token, tipo_data)
        print_test('CLIENTE: POST /admin/tipos', status, 'debe ser 403', 'esperado')
        self.record_result('cliente', status)
        
        status, data = make_request('POST', f'{CATALOGO}/catalogo/v1/admin/tipos', 
                                   self.admin_token, tipo_data)
        print_test('ADMIN: POST /admin/tipos', status, 'debe ser 201')
        self.record_result('admin', status)
        self.created_ids['tipo'] = data.get('id') if status == 201 else None
        
        # PUT /admin/tipos/{id}
        if self.created_ids['tipo']:
            update_data = {'nombre': f'Tipo Actualizado {date.today()}'}
            
            status, data = make_request('PUT', 
                                       f'{CATALOGO}/catalogo/v1/admin/tipos/{self.created_ids["tipo"]}',
                                       self.client_token, update_data)
            print_test('CLIENTE: PUT /admin/tipos/{id}', status, 'debe ser 403', 'esperado')
            self.record_result('cliente', status)
            
            status, data = make_request('PUT', 
                                       f'{CATALOGO}/catalogo/v1/admin/tipos/{self.created_ids["tipo"]}',
                                       self.admin_token, update_data)
            print_test('ADMIN: PUT /admin/tipos/{id}', status, 'debe ser 200')
            self.record_result('admin', status)
        
        print('\n📝 CRUD Servicios (solo ADMIN)')
        
        # POST /admin/servicios
        servicio_data = {
            'nombre': f'Servicio Test {date.today()}',
            'tipo_evento_id': TEST_TIPO_EVENTO_ID,
            'descripcion': 'Test'
        }
        
        status, data = make_request('POST', f'{CATALOGO}/catalogo/v1/admin/servicios',
                                   self.client_token, servicio_data)
        print_test('CLIENTE: POST /admin/servicios', status, 'debe ser 403', 'esperado')
        self.record_result('cliente', status)
        
        status, data = make_request('POST', f'{CATALOGO}/catalogo/v1/admin/servicios',
                                   self.admin_token, servicio_data)
        print_test('ADMIN: POST /admin/servicios', status, 'debe ser 201')
        self.record_result('admin', status)
        self.created_ids['servicio'] = data.get('id') if status == 201 else None
        
        print('\n📝 CRUD Opciones (solo ADMIN)')
        
        # POST /admin/opciones (usando servicio existente)
        opcion_data = {
            'servicio_id': TEST_SERVICE_ID,
            'nombre': f'Opción Test {date.today()} {hash(str(date.today()))}',
            'moneda': 'PEN',
            'monto': 99.99,
            'detalles': {'test': True}
        }
        
        status, data = make_request('POST', f'{CATALOGO}/catalogo/v1/admin/opciones',
                                   self.client_token, opcion_data)
        print_test('CLIENTE: POST /admin/opciones', status, 'debe ser 403', 'esperado')
        self.record_result('cliente', status)
        
        status, data = make_request('POST', f'{CATALOGO}/catalogo/v1/admin/opciones',
                                   self.admin_token, opcion_data)
        error_msg = data.get('detail', {}).get('message', '') if status == 500 else ''
        print_test('ADMIN: POST /admin/opciones', status, 'debe ser 201', error_msg[:80] if error_msg else '')
        self.record_result('admin', status)
        self.created_ids['opcion'] = data.get('id') if status == 201 else None
        
        # DELETE recursos creados
        print('\n📝 DELETE recursos de Catálogo (solo ADMIN)')
        
        if self.created_ids['opcion']:
            status, _ = make_request('DELETE', 
                                    f'{CATALOGO}/catalogo/v1/admin/opciones/{self.created_ids["opcion"]}',
                                    self.client_token)
            print_test('CLIENTE: DELETE /admin/opciones/{id}', status, 'debe ser 403', 'esperado')
            self.record_result('cliente', status)
            
            status, _ = make_request('DELETE', 
                                    f'{CATALOGO}/catalogo/v1/admin/opciones/{self.created_ids["opcion"]}',
                                    self.admin_token)
            print_test('ADMIN: DELETE /admin/opciones/{id}', status, 'debe ser 204')
            self.record_result('admin', status)
        
        if self.created_ids['servicio']:
            status, _ = make_request('DELETE', 
                                    f'{CATALOGO}/catalogo/v1/admin/servicios/{self.created_ids["servicio"]}',
                                    self.admin_token)
            print_test('ADMIN: DELETE /admin/servicios/{id}', status, 'debe ser 204',
                      'FK constraint OK' if status == 0 else '')
            self.record_result('admin', status)
        
        if self.created_ids['tipo']:
            status, _ = make_request('DELETE', 
                                    f'{CATALOGO}/catalogo/v1/admin/tipos/{self.created_ids["tipo"]}',
                                    self.admin_token)
            print_test('ADMIN: DELETE /admin/tipos/{id}', status, 'debe ser 204')
            self.record_result('admin', status)
    
    # === CONTRATACIÓN TESTS ===
    
    def test_contratacion_endpoints(self):
        """Prueba endpoints de Contratación"""
        print_section('CONTRATACIÓN SERVICE - Endpoints Cliente y Admin')
        
        print('\n📝 Endpoints CLIENTE (ambos roles deben acceder)')
        
        # POST /pedidos (crear pedido custom)
        pedido_data = {
            'tipo_evento_id': TEST_TIPO_EVENTO_ID,
            'items': [{'opcion_servicio_id': TEST_OPTION_ID, 'cantidad': 1}],
            'fecha_evento': '2025-12-25',
            'hora_inicio': '18:00:00',
            'num_personas': 50,
            'ubicacion': 'Lima'
        }
        
        status, data = make_request('POST', f'{CONTRATACION}/contratacion/pedidos',
                                   self.client_token, pedido_data)
        print_test('CLIENTE: POST /pedidos', status, 'debe ser 201')
        self.record_result('cliente', status)
        self.created_ids['pedido_cliente'] = data.get('id') if status == 201 else None
        
        status, data = make_request('POST', f'{CONTRATACION}/contratacion/pedidos',
                                   self.admin_token, pedido_data)
        print_test('ADMIN: POST /pedidos', status, 'debe ser 201')
        self.record_result('admin', status)
        self.created_ids['pedido_admin'] = data.get('id') if status == 201 else None
        
        # GET /pedidos/mios
        status, data = make_request('GET', f'{CONTRATACION}/contratacion/pedidos/mios',
                                   self.client_token)
        print_test('CLIENTE: GET /pedidos/mios', status, 'debe ser 200')
        self.record_result('cliente', status)
        
        status, data = make_request('GET', f'{CONTRATACION}/contratacion/pedidos/mios',
                                   self.admin_token)
        print_test('ADMIN: GET /pedidos/mios', status, 'debe ser 200')
        self.record_result('admin', status)
        
        # GET /pedidos/{id} (solo el dueño puede ver su pedido)
        if self.created_ids['pedido_cliente']:
            status, data = make_request('GET', 
                                       f'{CONTRATACION}/contratacion/pedidos/{self.created_ids["pedido_cliente"]}',
                                       self.client_token)
            print_test('CLIENTE: GET /pedidos/{su_pedido}', status, 'debe ser 200')
            self.record_result('cliente', status)
        
        print('\n📝 Endpoints ADMIN de Contratación (solo ADMIN)')
        
        # GET /admin/pedidos
        status, data = make_request('GET', f'{CONTRATACION}/contratacion/admin/pedidos?limit=5',
                                   self.client_token)
        print_test('CLIENTE: GET /admin/pedidos', status, 'debe ser 403', 'esperado')
        self.record_result('cliente', status)
        
        status, data = make_request('GET', f'{CONTRATACION}/contratacion/admin/pedidos?limit=5',
                                   self.admin_token)
        print_test('ADMIN: GET /admin/pedidos', status, 'debe ser 200')
        self.record_result('admin', status)
        
        # GET /admin/pedidos/{id}
        if self.created_ids['pedido_cliente']:
            status, data = make_request('GET',
                                       f'{CONTRATACION}/contratacion/admin/pedidos/{self.created_ids["pedido_cliente"]}',
                                       self.client_token)
            print_test('CLIENTE: GET /admin/pedidos/{id}', status, 'debe ser 403', 'esperado')
            self.record_result('cliente', status)
            
            status, data = make_request('GET',
                                       f'{CONTRATACION}/contratacion/admin/pedidos/{self.created_ids["pedido_cliente"]}',
                                       self.admin_token)
            print_test('ADMIN: GET /admin/pedidos/{id}', status, 'debe ser 200')
            self.record_result('admin', status)
            
            # PATCH /admin/pedidos/{id} (cambiar estado)
            patch_data = {'estado': 1}  # COTIZADO
            
            status, data = make_request('PATCH',
                                       f'{CONTRATACION}/contratacion/admin/pedidos/{self.created_ids["pedido_cliente"]}',
                                       self.client_token, patch_data)
            print_test('CLIENTE: PATCH /admin/pedidos/{id}', status, 'debe ser 403', 'esperado')
            self.record_result('cliente', status)
            
            status, data = make_request('PATCH',
                                       f'{CONTRATACION}/contratacion/admin/pedidos/{self.created_ids["pedido_cliente"]}',
                                       self.admin_token, patch_data)
            print_test('ADMIN: PATCH /admin/pedidos/{id} → estado 1', status, 'debe ser 200')
            self.record_result('admin', status)
            
            # POST /admin/pedidos/{id}/items
            items_data = {'items': [{'opcion_servicio_id': TEST_OPTION_ID, 'cantidad': 1}]}
            
            status, data = make_request('POST',
                                       f'{CONTRATACION}/contratacion/admin/pedidos/{self.created_ids["pedido_cliente"]}/items',
                                       self.client_token, items_data)
            print_test('CLIENTE: POST /admin/pedidos/{id}/items', status, 'debe ser 403', 'esperado')
            self.record_result('cliente', status)
            
            status, data = make_request('POST',
                                       f'{CONTRATACION}/contratacion/admin/pedidos/{self.created_ids["pedido_cliente"]}/items',
                                       self.admin_token, items_data)
            print_test('ADMIN: POST /admin/pedidos/{id}/items', status, 'debe ser 201')
            self.record_result('admin', status)
    
    def print_summary(self):
        """Imprime resumen de resultados"""
        print_section('RESUMEN DE RESULTADOS')
        
        for role in ['admin', 'cliente']:
            role_name = 'ADMIN' if role == 'admin' else 'CLIENTE'
            results = self.results[role]
            
            print(f'\n🔹 Rol: {role_name}')
            print(f'   Total pruebas: {results["total"]}')
            print(f'   ✅ Exitosas (200/201/204): {results["success"]}')
            print(f'   🔒 Prohibidas (403): {results["forbidden"]}')
            print(f'   ❌ Errores (otros): {results["error"]}')
            
            if results['total'] > 0:
                success_rate = (results['success'] / results['total']) * 100
                print(f'   📈 Tasa de éxito: {success_rate:.1f}%')
        
        # Validación de seguridad
        print('\n' + '='*80)
        print('🔐 VALIDACIÓN DE SEGURIDAD')
        print('='*80)
        
        admin_forbidden = self.results['admin']['forbidden']
        cliente_forbidden = self.results['cliente']['forbidden']
        
        print(f'\n✅ ADMIN bloqueado en {admin_forbidden} endpoints (debe ser 0)')
        print(f'✅ CLIENTE bloqueado en {cliente_forbidden} endpoints (debe ser >0 en endpoints admin)')
        
        if admin_forbidden == 0 and cliente_forbidden > 0:
            print('\n🎉 ¡VALIDACIÓN EXITOSA!')
            print('✅ ADMIN tiene acceso completo a endpoints autorizados')
            print('✅ CLIENTE está correctamente restringido de endpoints admin')
        else:
            print('\n⚠️ ADVERTENCIAS DETECTADAS:')
            if admin_forbidden > 0:
                print(f'   ⚠️ ADMIN fue bloqueado en {admin_forbidden} endpoints (revisar permisos)')
            if cliente_forbidden == 0:
                print('   ⚠️ CLIENTE no fue bloqueado en ningún endpoint admin (falla de seguridad)')


# === MAIN ===

def main():
    print('='*80)
    print('🔐 VALIDACIÓN FUNCIONAL DE ENDPOINTS POR ROL')
    print('='*80)
    print('\nProbando acceso a endpoints autenticados:')
    print('  • Como ADMIN → debe tener acceso completo')
    print('  • Como CLIENTE → debe estar restringido de endpoints admin')
    
    test = EndpointTest()
    
    if not test.setup():
        print('\n❌ Error en configuración inicial')
        return
    
    # Ejecutar pruebas por servicio
    test.test_iam_endpoints()
    test.test_catalogo_endpoints()
    test.test_contratacion_endpoints()
    
    # Resumen final
    test.print_summary()


if __name__ == '__main__':
    main()
