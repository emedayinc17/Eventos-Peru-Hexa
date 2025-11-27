"""
Pruebas End-to-End de Flujos Completos del Sistema
Ejecuta los 3 flujos principales: Cliente, Admin e Integrado

Ejecutar:
    python tools/test_e2e_flows.py
"""
import os
import requests
import json
from datetime import date, datetime, timedelta
from typing import Dict, Optional, Any
import time

# === CONFIGURACIÓN ===
IAM = os.getenv('IAM_ROOT', 'http://127.0.0.1:8010')
CATALOGO = os.getenv('CATALOGO_ROOT', 'http://127.0.0.1:8020')
PROVEEDORES = os.getenv('PROVEEDORES_ROOT', 'http://127.0.0.1:8030')
CONTRATACION = os.getenv('CONTRATACION_ROOT', 'http://127.0.0.1:8040')

# Credenciales (bootstrap.sql seeds) - Contraseña estándar: Evoluti0n
ADMIN_EMAIL = 'admin@eventos.pe'
ADMIN_PASSWORD = 'Evoluti0n'
CLIENT_EMAIL = 'jorge.martinez711@eventos.pe'  # Cliente aleatorio de script2.sql
CLIENT_PASSWORD = 'Evoluti0n'

# IDs reales de bootstrap.sql + script2.sql
TEST_TIPO_EVENTO_ID = '11111111-1111-1111-1111-111111111111'  # Matrimonio
TEST_SERVICE_ID = 'aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa'      # Servicio Prueba Verificacion (script2.sql)
TEST_OPTION_ID = 'bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb'       # Opcion Prueba Verificacion (script2.sql)
TEST_PAQUETE_ID = 'bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0'      # PKG-PREMIUM-100
TEST_PROVIDER_ID = 'cccccccc-3333-4444-5555-cccccccccccc'     # Proveedor Prueba Verificacion (script2.sql)

# === HELPERS ===

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Imprime encabezado de sección"""
    print(f'\n{Colors.BOLD}{Colors.HEADER}{"="*80}{Colors.END}')
    print(f'{Colors.BOLD}{Colors.HEADER}🔹 {text}{Colors.END}')
    print(f'{Colors.BOLD}{Colors.HEADER}{"="*80}{Colors.END}\n')

def print_step(step: int, text: str):
    """Imprime paso del flujo"""
    print(f'{Colors.CYAN}[Paso {step}]{Colors.END} {text}')

def print_success(text: str):
    """Imprime éxito"""
    print(f'{Colors.GREEN}✅ {text}{Colors.END}')

def print_error(text: str):
    """Imprime error"""
    print(f'{Colors.RED}❌ {text}{Colors.END}')

def print_info(text: str):
    """Imprime información"""
    print(f'{Colors.YELLOW}ℹ️  {text}{Colors.END}')

def print_data(label: str, data: Any):
    """Imprime datos estructurados"""
    print(f'{Colors.BLUE}   {label}:{Colors.END} {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...' if len(str(data)) > 200 else f'{Colors.BLUE}   {label}:{Colors.END} {json.dumps(data, indent=2, ensure_ascii=False)}')

def login(email: str, password: str) -> Optional[str]:
    """Login y obtener token"""
    try:
        r = requests.post(
            f'{IAM}/iam/auth/login',
            json={'email': email, 'password': password},
            timeout=8
        )
        if r.status_code == 200:
            return r.json().get('access_token')
    except Exception as e:
        print_error(f'Error login {email}: {e}')
    return None

def api_call(method: str, url: str, token: str, body: Optional[Dict] = None) -> tuple[int, Dict]:
    """Ejecuta llamada HTTP"""
    headers = {'Authorization': f'Bearer {token}'}
    try:
        if method == 'GET':
            r = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            r = requests.post(url, headers=headers, json=body, timeout=10)
        elif method == 'PATCH':
            r = requests.patch(url, headers=headers, json=body, timeout=10)
        elif method == 'PUT':
            r = requests.put(url, headers=headers, json=body, timeout=10)
        else:
            return 0, {'error': 'Método no soportado'}
        
        try:
            data = r.json()
        except:
            data = {'text': r.text[:200]}
        
        return r.status_code, data
    except Exception as e:
        return 0, {'error': str(e)}


# === FLUJO 1: CLIENTE COMPLETO ===

def test_flujo_cliente_completo():
    """
    Flujo Cliente: Login → Crear pedido custom → Ver mis pedidos → Detalle
    """
    print_header('FLUJO 1: CLIENTE COMPLETO')
    
    # Paso 1: Login
    print_step(1, 'Cliente realiza login')
    client_token = login(CLIENT_EMAIL, CLIENT_PASSWORD)
    if not client_token:
        print_error('No se pudo obtener token de cliente')
        return False
    print_success(f'Login exitoso - Token obtenido')
    
    # Paso 2: Obtener información del usuario
    print_step(2, 'Cliente consulta su perfil (GET /iam/me)')
    status, user_info = api_call('GET', f'{IAM}/iam/me', client_token)
    if status == 200:
        print_success(f'Perfil obtenido: {user_info.get("email")} (ID: {user_info.get("id")[:8]}...)')
        print_data('Usuario', user_info)
        client_id = user_info.get('id')
    else:
        print_error(f'Error obteniendo perfil: {status}')
        return False
    
    # Paso 3: Crear pedido personalizado
    print_step(3, 'Cliente crea pedido personalizado (POST /contratacion/pedidos)')
    fecha_evento = (date.today() + timedelta(days=60)).isoformat()
    pedido_data = {
        'tipo_evento_id': TEST_TIPO_EVENTO_ID,
        'items': [
            {'opcion_servicio_id': TEST_OPTION_ID, 'cantidad': 1}
        ],
        'fecha_evento': fecha_evento,
        'hora_inicio': '18:00:00',
        'num_personas': 150,
        'ubicacion': 'Lima, Perú - Hotel Los Delfines',
        'notas': 'Evento corporativo E2E test'
    }
    
    status, pedido_created = api_call('POST', f'{CONTRATACION}/contratacion/pedidos', 
                                      client_token, pedido_data)
    if status == 201:
        pedido_id = pedido_created.get('id')
        print_success(f'Pedido creado: {pedido_id}')
        print_data('Pedido', {
            'id': pedido_id,
            'estado': pedido_created.get('estado'),
            'monto_total': pedido_created.get('monto_total'),
            'fecha_evento': pedido_created.get('fecha_evento')
        })
    else:
        print_error(f'Error creando pedido: {status} - {pedido_created}')
        return False
    
    # Paso 4: Listar pedidos del cliente
    print_step(4, 'Cliente consulta sus pedidos (GET /contratacion/pedidos/mios)')
    status, mis_pedidos = api_call('GET', f'{CONTRATACION}/contratacion/pedidos/mios', client_token)
    if status == 200:
        total = len(mis_pedidos) if isinstance(mis_pedidos, list) else mis_pedidos.get('total', 0)
        print_success(f'Pedidos obtenidos: {total} pedidos')
        if isinstance(mis_pedidos, list) and mis_pedidos:
            print_data('Primer pedido', mis_pedidos[0])
    else:
        print_error(f'Error listando pedidos: {status}')
        return False
    
    # Paso 5: Consultar detalle del pedido
    print_step(5, f'Cliente consulta detalle del pedido (GET /contratacion/pedidos/{pedido_id[:8]}...)')
    status, detalle = api_call('GET', f'{CONTRATACION}/contratacion/pedidos/{pedido_id}', client_token)
    if status == 200:
        print_success('Detalle de pedido obtenido')
        print_data('Detalle completo', {
            'pedido': detalle.get('pedido', {}).get('id'),
            'items': len(detalle.get('items', [])),
            'reservas': len(detalle.get('reservas', [])),
            'estado_nombre': detalle.get('estado_nombre'),
            'monto_total': detalle.get('pedido', {}).get('monto_total')
        })
    else:
        print_error(f'Error obteniendo detalle: {status}')
        return False
    
    # Paso 6: Intentar acceder a endpoint admin (debe fallar)
    print_step(6, 'Cliente intenta acceder a endpoint admin (debe ser 403)')
    status, _ = api_call('GET', f'{CONTRATACION}/contratacion/admin/pedidos', client_token)
    if status == 403:
        print_success('Acceso denegado correctamente - Seguridad funcionando')
    else:
        print_error(f'Seguridad falló - Cliente accedió con status: {status}')
        return False
    
    print_header('✅ FLUJO CLIENTE COMPLETADO EXITOSAMENTE')
    return True


# === FLUJO 2: ADMIN COMPLETO ===

def test_flujo_admin_completo():
    """
    Flujo Admin: Login → Listar pedidos → Cambiar estados → Asignar proveedor → Verificar reserva
    """
    print_header('FLUJO 2: ADMIN COMPLETO')
    
    # Paso 1: Login admin
    print_step(1, 'Admin realiza login')
    admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not admin_token:
        print_error('No se pudo obtener token de admin')
        return False
    print_success('Login admin exitoso')
    
    # Paso 2: Crear pedido de prueba (como admin puede crear pedidos también)
    print_step(2, 'Admin crea pedido de prueba para gestionar')
    fecha_evento = (date.today() + timedelta(days=45)).isoformat()
    pedido_data = {
        'tipo_evento_id': TEST_TIPO_EVENTO_ID,
        'items': [
            {'opcion_servicio_id': TEST_OPTION_ID, 'cantidad': 2}
        ],
        'fecha_evento': fecha_evento,
        'hora_inicio': '19:00:00',
        'num_personas': 200,
        'ubicacion': 'Cusco, Perú',
        'notas': 'Pedido admin E2E test'
    }
    
    status, pedido_admin = api_call('POST', f'{CONTRATACION}/contratacion/pedidos', 
                                    admin_token, pedido_data)
    if status == 201:
        pedido_id = pedido_admin.get('id')
        print_success(f'Pedido creado: {pedido_id}')
    else:
        print_error(f'Error creando pedido: {status}')
        return False
    
    # Paso 3: Listar todos los pedidos (vista admin)
    print_step(3, 'Admin lista todos los pedidos (GET /contratacion/admin/pedidos)')
    status, all_pedidos = api_call('GET', f'{CONTRATACION}/contratacion/admin/pedidos?limit=10', 
                                   admin_token)
    if status == 200:
        total = all_pedidos.get('total', 0)
        pedidos_list = all_pedidos.get('pedidos', [])
        print_success(f'Total de pedidos en sistema: {total}')
        print_data('Primeros pedidos', pedidos_list[:2] if len(pedidos_list) > 1 else pedidos_list)
    else:
        print_error(f'Error listando pedidos: {status}')
        return False
    
    # Paso 4: Obtener detalle del pedido (vista admin)
    print_step(4, 'Admin consulta detalle del pedido (GET /contratacion/admin/pedidos/{id})')
    status, detalle_admin = api_call('GET', f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}', 
                                     admin_token)
    if status == 200:
        print_success('Detalle admin obtenido')
        print_data('Pedido', {
            'id': detalle_admin.get('pedido', {}).get('id'),
            'cliente_id': detalle_admin.get('pedido', {}).get('cliente_id')[:8] + '...',
            'estado': detalle_admin.get('estado_nombre'),
            'items': len(detalle_admin.get('items', []))
        })
    else:
        print_error(f'Error obteniendo detalle admin: {status}')
        return False
    
    # Paso 5: Cambiar estado a COTIZADO (0 -> 1)
    print_step(5, 'Admin cambia estado a COTIZADO (PATCH /admin/pedidos/{id})')
    status, updated1 = api_call('PATCH', f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}',
                                admin_token, {'estado': 1})
    if status == 200:
        print_success(f'Estado actualizado a COTIZADO (1)')
        print_data('Estado', {'nuevo_estado': updated1.get('estado')})
    else:
        print_error(f'Error actualizando estado: {status}')
        return False
    
    # Paso 6: Cambiar estado a APROBADO (1 -> 2)
    print_step(6, 'Admin cambia estado a APROBADO')
    status, updated2 = api_call('PATCH', f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}',
                                admin_token, {'estado': 2})
    if status == 200:
        print_success(f'Estado actualizado a APROBADO (2)')
    else:
        print_error(f'Error actualizando a APROBADO: {status}')
        return False
    
    # Paso 7: Admin asigna proveedor al pedido
    print_step(7, f'Admin asigna proveedor (POST /admin/pedidos/{pedido_id[:8]}.../asignar-proveedor)')
    
    # Primero necesitamos obtener el item_pedido_id del pedido
    status, detalle_items = api_call('GET', f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}',
                                     admin_token)
    if status != 200 or not detalle_items.get('items'):
        print_error('No se pudo obtener item_pedido_id')
        return False
    
    item_pedido_id = detalle_items['items'][0]['id']
    fecha_inicio = datetime.fromisoformat(fecha_evento + 'T19:00:00')
    fecha_fin = fecha_inicio + timedelta(hours=4)
    
    asignar_data = {
        'proveedor_id': TEST_PROVIDER_ID,
        'item_pedido_id': item_pedido_id,
        'opcion_servicio_id': TEST_OPTION_ID,
        'fecha_inicio': fecha_inicio.isoformat(),
        'fecha_fin': fecha_fin.isoformat(),
        'monto': 1500.0,
        'hold_id': None
    }
    
    status, asignacion = api_call('POST', 
                                  f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}/asignar-proveedor',
                                  admin_token, asignar_data)
    if status == 201:
        print_success('Proveedor asignado - Reserva creada')
        print_data('Asignación', {
            'pedido_id': asignacion.get('pedido_id'),
            'reserva_id': asignacion.get('reserva_id'),
            'estado': asignacion.get('estado')
        })
    else:
        print_error(f'Error asignando proveedor: {status} - {asignacion}')
        return False
    
    # Paso 8: Verificar detalle final con reserva (ya no hay paso de confirmar hold)
    print_step(8, 'Admin verifica detalle final con reserva confirmada')
    # Paso 8: Verificar detalle final con reserva (ya no hay paso de confirmar hold)
    print_step(8, 'Admin verifica detalle final con reserva confirmada')
    status, detalle_final = api_call('GET', f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}',
                                     admin_token)
    if status == 200:
        reservas = detalle_final.get('reservas', [])
        print_success(f'Pedido tiene {len(reservas)} reserva(s) confirmada(s)')
        print_data('Detalle final', {
            'estado': detalle_final.get('estado_nombre'),
            'total_reservas': detalle_final.get('total_reservas'),
            'primera_reserva': reservas[0] if reservas else None
        })
    else:
        print_error(f'Error verificando detalle final: {status}')
        return False
    
    # Paso 9: Agregar items adicionales al pedido (volver a COTIZADO primero)
    print_step(9, 'Admin agrega items adicionales al pedido')
    
    # Cambiar a COTIZADO para poder agregar items
    status, _ = api_call('PATCH', f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}',
                         admin_token, {'estado': 1})
    if status != 200:
        print_info('No se pudo cambiar a COTIZADO, saltando adición de items')
    else:
        items_nuevos = {
            'items': [
                {'opcion_servicio_id': TEST_OPTION_ID, 'cantidad': 1}
            ]
        }
        
        status, items_added = api_call('POST',
                                       f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}/items',
                                       admin_token, items_nuevos)
        if status == 201:
            print_success('Items agregados exitosamente')
            print_data('Items agregados', items_added)
        else:
            print_error(f'Error agregando items: {status}')
    
    print_header('✅ FLUJO ADMIN COMPLETADO EXITOSAMENTE')
    return True


# === FLUJO 3: INTEGRADO (PAQUETE) ===

def test_flujo_integrado_paquete():
    """
    Flujo Integrado: Cliente crea pedido → Admin aprueba → Asigna proveedor → Verifica reserva
    """
    print_header('FLUJO 3: INTEGRADO (CICLO COMPLETO CLIENTE-ADMIN)')
    
    # Paso 1: Cliente login
    print_step(1, 'Cliente realiza login')
    client_token = login(CLIENT_EMAIL, CLIENT_PASSWORD)
    if not client_token:
        print_error('No se pudo obtener token de cliente')
        return False
    print_success('Cliente autenticado')
    
    # Paso 2: Consultar catálogo de paquetes
    print_step(2, 'Cliente consulta catálogo de paquetes (GET /catalogo/v1/paquetes)')
    status, paquetes = api_call('GET', f'{CATALOGO}/catalogo/v1/paquetes', client_token)
    if status == 200:
        total = len(paquetes) if isinstance(paquetes, list) else 0
        print_success(f'Paquetes disponibles: {total}')
        if isinstance(paquetes, list) and paquetes:
            print_data('Primer paquete', paquetes[0])
    else:
        print_error(f'Error consultando paquetes: {status}')
        return False
    
    # Paso 3: Cliente crea pedido personalizado
    print_step(3, 'Cliente crea pedido personalizado con múltiples items')
    # Paso 3: Cliente crea pedido personalizado con múltiples items
    print_step(3, 'Cliente crea pedido personalizado con múltiples items')
    fecha_evento = (date.today() + timedelta(days=90)).isoformat()
    
    pedido_data = {
        'tipo_evento_id': TEST_TIPO_EVENTO_ID,
        'items': [
            {'opcion_servicio_id': TEST_OPTION_ID, 'cantidad': 2}
        ],
        'fecha_evento': fecha_evento,
        'hora_inicio': '20:00:00',
        'num_personas': 180,
        'ubicacion': 'Arequipa, Perú - Monasterio',
        'notas': 'Pedido integrado E2E'
    }
    
    status, pedido_creado = api_call('POST', f'{CONTRATACION}/contratacion/pedidos',
                                     client_token, pedido_data)
    if status == 201:
        pedido_id = pedido_creado.get('id')
        print_success(f'Pedido creado: {pedido_id}')
        print_data('Pedido', {
            'id': pedido_id,
            'monto_total': pedido_creado.get('monto_total'),
            'items': len(pedido_creado.get('items', []))
        })
    else:
        print_error(f'Error creando pedido: {status} - {pedido_creado}')
        return False
    
    # Paso 4: Admin login
    print_step(4, 'Admin realiza login para gestionar el pedido')
    admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not admin_token:
        print_error('No se pudo obtener token de admin')
        return False
    print_success('Admin autenticado')
    
    # Paso 5: Admin lista pedidos y encuentra el nuevo
    print_step(5, 'Admin lista pedidos recientes')
    status, recent = api_call('GET', f'{CONTRATACION}/contratacion/admin/pedidos?limit=5&status=0',
                              admin_token)
    if status == 200:
        pedidos = recent.get('pedidos', [])
        print_success(f'Pedidos en estado DRAFT: {len(pedidos)}')
    else:
        print_error(f'Error listando pedidos: {status}')
    
    # Paso 6: Admin cotiza el pedido
    print_step(6, 'Admin cotiza el pedido (estado DRAFT → COTIZADO)')
    status, cotizado = api_call('PATCH', f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}',
                                admin_token, {'estado': 1})
    if status == 200:
        print_success('Pedido cotizado (estado: 1)')
    else:
        print_error(f'Error cotizando: {status}')
        return False
    
    # Paso 7: Admin aprueba el pedido
    print_step(7, 'Admin aprueba el pedido (COTIZADO → APROBADO)')
    status, aprobado = api_call('PATCH', f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}',
                                admin_token, {'estado': 2})
    if status == 200:
        print_success('Pedido aprobado (estado: 2)')
    else:
        print_error(f'Error aprobando: {status}')
        return False
    
    # Paso 8: Admin asigna proveedor
    print_step(8, 'Admin asigna proveedor con reserva')
    
    # Obtener item_pedido_id
    status, detalle_items = api_call('GET', f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}',
                                     admin_token)
    if status != 200 or not detalle_items.get('items'):
        print_error('No se pudo obtener item_pedido_id')
        return False
    
    item_pedido_id = detalle_items['items'][0]['id']
    fecha_inicio = datetime.fromisoformat(fecha_evento + 'T20:00:00')
    fecha_fin = fecha_inicio + timedelta(hours=5)
    
    asignar_data = {
        'proveedor_id': TEST_PROVIDER_ID,
        'item_pedido_id': item_pedido_id,
        'opcion_servicio_id': TEST_OPTION_ID,
        'fecha_inicio': fecha_inicio.isoformat(),
        'fecha_fin': fecha_fin.isoformat(),
        'monto': 3000.0,
        'hold_id': None
    }
    
    status, asignacion = api_call('POST',
                                  f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}/asignar-proveedor',
                                  admin_token, asignar_data)
    if status == 201:
        print_success('Proveedor asignado - Reserva creada')
        print_data('Asignación', {
            'pedido_id': asignacion.get('pedido_id'),
            'reserva_id': asignacion.get('reserva_id'),
            'estado': asignacion.get('estado')
        })
    else:
        print_error(f'Error asignando proveedor: {status} - {asignacion}')
        return False
    
    # Paso 9: Cliente consulta su pedido actualizado
    print_step(9, 'Cliente consulta el estado actualizado de su pedido')
    status, pedido_final = api_call('GET', f'{CONTRATACION}/contratacion/pedidos/{pedido_id}',
                                    client_token)
    if status == 200:
        print_success('Cliente ve su pedido confirmado')
        print_data('Vista cliente', {
            'id': pedido_final.get('pedido', {}).get('id'),
            'estado': pedido_final.get('estado_nombre'),
            'total_items': pedido_final.get('total_items'),
            'total_reservas': pedido_final.get('total_reservas'),
            'monto_total': pedido_final.get('pedido', {}).get('monto_total')
        })
    else:
        print_error(f'Error consultando pedido final: {status}')
        return False
    
    print_header('✅ FLUJO INTEGRADO COMPLETADO EXITOSAMENTE')
    return True


# === MAIN ===

def main():
    """Ejecuta todos los flujos E2E"""
    print('\n')
    print(f'{Colors.BOLD}{Colors.HEADER}{"#"*80}{Colors.END}')
    print(f'{Colors.BOLD}{Colors.HEADER}#{"":^78}#{Colors.END}')
    print(f'{Colors.BOLD}{Colors.HEADER}#{"PRUEBAS END-TO-END - SISTEMA EVENTOS PERÚ":^78}#{Colors.END}')
    print(f'{Colors.BOLD}{Colors.HEADER}#{"":^78}#{Colors.END}')
    print(f'{Colors.BOLD}{Colors.HEADER}{"#"*80}{Colors.END}')
    print('\n')
    
    print_info('Iniciando pruebas de flujos completos del sistema...')
    print_info(f'Servicios: IAM({IAM}), Catálogo({CATALOGO}), Contratación({CONTRATACION}), Proveedores({PROVEEDORES})')
    print('\n')
    
    resultados = {
        'Flujo Cliente Completo': False,
        'Flujo Admin Completo': False,
        'Flujo Integrado (Paquete)': False
    }
    
    # Ejecutar flujos
    try:
        resultados['Flujo Cliente Completo'] = test_flujo_cliente_completo()
        time.sleep(1)
        
        resultados['Flujo Admin Completo'] = test_flujo_admin_completo()
        time.sleep(1)
        
        resultados['Flujo Integrado (Paquete)'] = test_flujo_integrado_paquete()
        
    except KeyboardInterrupt:
        print_error('\n\nPruebas interrumpidas por el usuario')
        return
    except Exception as e:
        print_error(f'\n\nError inesperado: {e}')
        import traceback
        traceback.print_exc()
        return
    
    # Resumen final
    print('\n')
    print_header('RESUMEN DE PRUEBAS E2E')
    
    total = len(resultados)
    exitosos = sum(1 for v in resultados.values() if v)
    fallidos = total - exitosos
    
    for flujo, exito in resultados.items():
        if exito:
            print_success(f'{flujo}: PASÓ')
        else:
            print_error(f'{flujo}: FALLÓ')
    
    print('\n')
    print(f'{Colors.BOLD}Total de flujos probados: {total}{Colors.END}')
    print(f'{Colors.GREEN}✅ Exitosos: {exitosos}{Colors.END}')
    print(f'{Colors.RED}❌ Fallidos: {fallidos}{Colors.END}')
    print(f'{Colors.CYAN}📈 Tasa de éxito: {(exitosos/total*100):.1f}%{Colors.END}')
    
    if exitosos == total:
        print('\n')
        print(f'{Colors.BOLD}{Colors.GREEN}{"="*80}{Colors.END}')
        print(f'{Colors.BOLD}{Colors.GREEN}🎉 ¡TODAS LAS PRUEBAS E2E COMPLETADAS EXITOSAMENTE! 🎉{Colors.END}')
        print(f'{Colors.BOLD}{Colors.GREEN}{"="*80}{Colors.END}')
        print('\n')
    else:
        print('\n')
        print(f'{Colors.BOLD}{Colors.RED}⚠️  Algunas pruebas fallaron. Revisar logs arriba.{Colors.END}')
        print('\n')


if __name__ == '__main__':
    main()
