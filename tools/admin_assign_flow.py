"""Flujo automatizado ADMIN:
- Crear pedido custom como CLIENTE
- Obtener detalle del pedido como ADMIN
- Cambiar estado a APROBADO (2) como ADMIN
- Llamar /admin/pedidos/{id}/asignar-proveedor para asignar TEST_PROVIDER_ID

Requiere que los servicios estén arriba y que existan los IDs de prueba en la BD (ver db/script2.sql).
"""
import os
import requests
from datetime import datetime, timedelta, date
import time

IAM = os.getenv('IAM_ROOT', 'http://127.0.0.1:8010')
CATALOGO = os.getenv('CATALOGO_ROOT', 'http://127.0.0.1:8020')
PROVEEDORES = os.getenv('PROVEEDORES_ROOT', 'http://127.0.0.1:8030')
CONTRATACION = os.getenv('CONTRATACION_ROOT', 'http://127.0.0.1:8040')

CLIENT_EMAIL = os.getenv('TEST_CLIENT_EMAIL', 'demo@eventos.pe')
CLIENT_PASSWORD = os.getenv('TEST_CLIENT_PASSWORD', 'Admin_2025!')
ADMIN_EMAIL = os.getenv('TEST_ADMIN_EMAIL', 'admin@eventos.pe')
ADMIN_PASSWORD = os.getenv('TEST_ADMIN_PASSWORD', 'Admin_2025!')

TEST_SERVICE_ID = os.getenv('TEST_SERVICE_ID', 'aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa')
TEST_OPTION_ID = os.getenv('TEST_OPTION_ID', 'bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb')
TEST_PROVIDER_ID = os.getenv('TEST_PROVIDER_ID', 'cccccccc-3333-4444-5555-cccccccccccc')


def login(root, email, password):
    try:
        r = requests.post(root.rstrip('/') + '/iam/auth/login', json={'email': email, 'password': password}, timeout=8)
        if r.status_code == 200:
            data = r.json()
            return data.get('access_token') or data.get('token') or data.get('accessToken')
        print('Login failed', email, r.status_code, r.text)
    except Exception as e:
        print('Login exception', e)
    return None


def crear_pedido_cliente(token, opcion_id):
    url = CONTRATACION.rstrip('/') + '/contratacion/pedidos'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    payload = {
        'tipo_evento_id': '44444444-1111-1111-1111-111111111111',
        'items': [{'opcion_servicio_id': opcion_id, 'cantidad': 1}],
        'fecha_evento': date.today().isoformat(),
        'hora_inicio': '18:00:00',
        'num_personas': 2,
        'ubicacion': 'Lima'
    }
    r = requests.post(url, json=payload, headers=headers, timeout=12)
    print('Crear pedido cliente:', r.status_code)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text


def admin_detalle(token, pedido_id):
    url = CONTRATACION.rstrip('/') + f'/contratacion/admin/pedidos/{pedido_id}'
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers, timeout=10)
    print('Admin detalle:', r.status_code)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text


def admin_patch_estado(token, pedido_id, estado):
    url = CONTRATACION.rstrip('/') + f'/contratacion/admin/pedidos/{pedido_id}'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    r = requests.patch(url, json={'estado': estado}, headers=headers, timeout=10)
    print('Admin patch estado:', r.status_code)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text


def admin_asignar_proveedor(token, pedido_id, item_pedido_id, opcion_servicio_id, proveedor_id, monto):
    url = CONTRATACION.rstrip('/') + f'/contratacion/admin/pedidos/{pedido_id}/asignar-proveedor'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    # usar fechas próximas
    inicio = (datetime.utcnow() + timedelta(days=7)).isoformat()
    fin = (datetime.utcnow() + timedelta(days=7, hours=4)).isoformat()
    payload = {
        'proveedor_id': proveedor_id,
        'item_pedido_id': item_pedido_id,
        'opcion_servicio_id': opcion_servicio_id,
        'fecha_inicio': inicio,
        'fecha_fin': fin,
        'monto': monto,
    }
    r = requests.post(url, json=payload, headers=headers, timeout=15)
    print('Admin asignar proveedor:', r.status_code)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text


def main():
    print('Inicio flujo admin assign...')
    client_token = login(IAM, CLIENT_EMAIL, CLIENT_PASSWORD)
    admin_token = login(IAM, ADMIN_EMAIL, ADMIN_PASSWORD)
    if not client_token:
        print('No client token - abort')
        return
    if not admin_token:
        print('No admin token - abort')
        return

    # Crear pedido
    st, created = crear_pedido_cliente(client_token, TEST_OPTION_ID)
    if st not in (200,201):
        print('No se pudo crear pedido, status', st, created)
        return
    pedido_id = created.get('id') or created.get('pedido')
    print('Pedido creado id=', pedido_id)

    # Obtener detalle admin para extraer item_pedido_id
    time.sleep(1)
    st, detalle = admin_detalle(admin_token, pedido_id)
    if st != 200:
        print('No se pudo obtener detalle admin:', st, detalle)
        return
    # buscar primer item
    items = detalle.get('items') if isinstance(detalle, dict) else None
    if not items:
        print('No items en detalle:', items)
        return
    item_pedido_id = items[0].get('id')
    monto = items[0].get('precio_unit') or items[0].get('precio_total') or 1500.0
    print('Item encontrado id=', item_pedido_id, 'monto=', monto)

    # Cambiar estado: intentar 0->1 then 1->2 si es necesario
    st, res = admin_patch_estado(admin_token, pedido_id, 1)
    if st not in (200, 204):
        print('Advertencia: no se pudo poner en estado 1, status', st, res)
    else:
        print('Pedido puesto en estado 1')

    st, res = admin_patch_estado(admin_token, pedido_id, 2)
    if st not in (200, 204):
        print('No se pudo poner en APROBADO:', st, res)
        return
    print('Pedido puesto en APROBADO')

    # Llamar asignar proveedor
    st, res = admin_asignar_proveedor(admin_token, pedido_id, item_pedido_id, TEST_OPTION_ID, TEST_PROVIDER_ID, monto)
    print('Resultado asignar proveedor:', st, res)


if __name__ == '__main__':
    main()
