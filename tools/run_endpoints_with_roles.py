"""Ejecuta todos los endpoints listados en OpenAPI para tres escenarios:
 - sin autenticación
 - con token de CLIENTE
 - con token de ADMIN

Genera un resumen en `docs/E2E_ENDPOINTS_REPORT_ES.md`.
"""
import os
import requests
import json
from datetime import date

ROOTS = {
    'iam': os.getenv('IAM_ROOT', 'http://127.0.0.1:8010'),
    'catalogo': os.getenv('CATALOGO_ROOT', 'http://127.0.0.1:8020'),
    'proveedores': os.getenv('PROVEEDORES_ROOT', 'http://127.0.0.1:8030'),
    'contratacion': os.getenv('CONTRATACION_ROOT', 'http://127.0.0.1:8040'),
}

CLIENT_EMAIL = os.getenv('TEST_CLIENT_EMAIL', 'demo@eventos.pe')
CLIENT_PASSWORD = os.getenv('TEST_CLIENT_PASSWORD', 'Admin_2025!')
ADMIN_EMAIL = os.getenv('TEST_ADMIN_EMAIL', 'admin@eventos.pe')
ADMIN_PASSWORD = os.getenv('TEST_ADMIN_PASSWORD', 'Admin_2025!')

REPORT_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs', 'E2E_ENDPOINTS_REPORT_ES.md')


def login(root, email, password):
    url = root.rstrip('/') + '/iam/auth/login'
    try:
        r = requests.post(url, json={'email': email, 'password': password}, timeout=8)
        if r.status_code == 200:
            data = r.json()
            return data.get('access_token') or data.get('token') or data.get('accessToken')
        return None
    except Exception:
        return None


def fetch_openapi(root, name=None):
    """Try several candidate locations for openapi.json: root, root/{name}, root/{name}/v1"""
    candidates = [root.rstrip('/') + '/openapi.json']
    if name:
        candidates.append(root.rstrip('/') + f'/{name}/openapi.json')
        candidates.append(root.rstrip('/') + f'/{name}/v1/openapi.json')
    for url in candidates:
        try:
            r = requests.get(url, timeout=6)
            if r.status_code == 200:
                return r.json()
        except Exception:
            continue
    return None


def get_first_id(root, list_path):
    try:
        r = requests.get(root.rstrip('/') + list_path, timeout=6)
        if r.status_code == 200:
            data = r.json()
            # may be {'items': [...]} or list
            if isinstance(data, dict) and 'items' in data and data['items']:
                return data['items'][0].get('id')
            if isinstance(data, list) and data:
                return data[0].get('id')
    except Exception:
        return None
    return None


def call_op(root, method, path, token=None):
    url = root.rstrip('/') + path
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    try:
        if method.lower() == 'get':
            r = requests.get(url, headers=headers, timeout=10)
        else:
            # enviar cuerpo mínimo no destructivo; caller may override via global spec mapping
            body = call_op._next_body if hasattr(call_op, '_next_body') else {}
            # reset after use
            if hasattr(call_op, '_next_body'):
                delattr(call_op, '_next_body')
            r = requests.request(method.upper(), url, headers=headers, json=body, timeout=12)
        try:
            content = r.json()
        except Exception:
            content = r.text[:300]
        return r.status_code, content
    except Exception as e:
        return 'error', str(e)


def main():
    client_token = login(ROOTS['iam'], CLIENT_EMAIL, CLIENT_PASSWORD)
    admin_token = login(ROOTS['iam'], ADMIN_EMAIL, ADMIN_PASSWORD)

    report_lines = []
    report_lines.append('# Informe E2E: endpoints probados con roles\n')
    report_lines.append(f'- Fecha: {date.today().isoformat()}\n')
    report_lines.append(f'- Cliente: `{CLIENT_EMAIL}` -> token: {"Si" if client_token else "No"}\n')
    report_lines.append(f'- Admin: `{ADMIN_EMAIL}` -> token: {"Si" if admin_token else "No"}\n')

    for name, root in ROOTS.items():
        report_lines.append(f'\n## Servicio: {name} ({root})\n')
        spec = fetch_openapi(root, name)
        if not spec:
            report_lines.append('OpenAPI no disponible\n')
            continue
        paths = spec.get('paths', {})
        for path, ops in paths.items():
            for method, meta in ops.items():
                # construir body mínimo a partir del spec.requestBody si existe
                rb = meta.get('requestBody')
                if rb:
                    try:
                        # intentar extraer schema->properties para application/json
                        content = rb.get('content', {})
                        app_json = content.get('application/json') or next(iter(content.values()), None)
                        schema = app_json.get('schema') if app_json else None
                    except Exception:
                        schema = None
                    if schema:
                            # generar ejemplo sencillo a partir del schema
                            def build_example(sch):
                                t = sch.get('type')
                                if t == 'object':
                                    props = {}
                                    for k, v in (sch.get('properties') or {}).items():
                                        props[k] = build_example(v)
                                    return props
                                if t == 'array':
                                    items = sch.get('items') or {'type': 'string'}
                                    return [build_example(items)]
                                if t == 'integer' or t == 'number':
                                    return 1
                                if t == 'boolean':
                                    return True
                                # default string
                                return 'x'

                            try:
                                body_example = build_example(schema)
                            except Exception:
                                body_example = {}
                            # Si la generación a partir del schema no produjo propiedades,
                            # aplicar heurísticas por ruta para endpoints admin comunes.
                            if isinstance(body_example, dict) and not body_example:
                                # heuristics for common admin endpoints in catalogo
                                if '/admin/tipos' in path:
                                    body_example = {'nombre': 'AutoTipo'}
                                elif '/admin/servicios' in path:
                                    tipo_id = get_first_id(root, '/catalogo/v1/tipos')
                                    body_example = {'nombre': 'AutoServicio', 'tipo_evento_id': tipo_id or 'tipo-1'}
                                elif '/admin/opciones' in path:
                                    servicio_id = get_first_id(root, '/catalogo/v1/servicios')
                                    body_example = {'servicio_id': servicio_id or 'serv-1', 'nombre': 'AutoOpcion', 'moneda': 'PEN', 'monto': 100.0}
                                elif '/admin/paquetes' in path:
                                    body_example = {'codigo': f'PKG-{date.today().isoformat()}', 'nombre': 'AutoPaquete', 'items': []}
                    else:
                        body_example = {}
                else:
                    body_example = {}

                # probar sin auth, con cliente, con admin
                # attach generated body to call_op for next non-GET call
                if body_example:
                    call_op._next_body = body_example
                status_no, body_no = call_op(root, method, path, token=None)

                if body_example:
                    call_op._next_body = body_example
                status_cli, body_cli = call_op(root, method, path, token=client_token)

                if body_example:
                    call_op._next_body = body_example
                status_admin, body_admin = call_op(root, method, path, token=admin_token)
                line = f'- {method.upper():6} {path:40} -> no_auth={status_no} client={status_cli} admin={status_admin}'
                report_lines.append(line)

    # escribir informe
    report_path = os.path.abspath(REPORT_PATH)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print('Informe generado en', report_path)


if __name__ == '__main__':
    main()
