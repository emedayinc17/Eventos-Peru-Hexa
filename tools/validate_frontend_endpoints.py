#!/usr/bin/env python3
"""
validate_frontend_endpoints.py
Automated validation of frontend ↔ backend alignment.

What it does:
- Parses `frontend-vanilla/config.js` to obtain service base URLs
- Attempts to login using demo credentials and checks `/me`
- Calls health/list endpoints for catálogo, proveedores, contratacion
- Saves `validation_report.json` in the repo root with results

Run:
  python tools/validate_frontend_endpoints.py

"""
import re
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'frontend-vanilla' / 'config.js'
REPORT = ROOT / 'validation_report.json'

DEFAULTS = {
    'IAM_API_BASE': 'http://127.0.0.1:8010/iam',
    'CATALOGO_API_BASE': 'http://127.0.0.1:8020/catalogo',
    'PROVEEDORES_API_BASE': 'http://127.0.0.1:8030/proveedores',
    'CONTRATACION_API_BASE': 'http://127.0.0.1:8040/contratacion'
}

DEMO_CRED = { 'email': 'demo@eventos.pe', 'password': 'Admin_2025!' }


def parse_config(path):
    text = path.read_text(encoding='utf-8')
    res = {}
    for key in DEFAULTS.keys():
        m = re.search(rf"window\.{key}\s*=\s*window\.{key}\s*\|\|\s*\"([^\"]+)\"", text)
        if not m:
            # fallback: look for assignment simpler
            m2 = re.search(rf"window\.{key}\s*=\s*\"([^\"]+)\"", text)
            if m2:
                res[key] = m2.group(1).strip()
            else:
                res[key] = DEFAULTS[key]
        else:
            res[key] = m.group(1).strip()
    return res


def safe_request(method, url, **kwargs):
    try:
        r = requests.request(method, url, timeout=8, **kwargs)
        try:
            body = r.json()
        except Exception:
            body = r.text
        return { 'ok': r.ok, 'status': r.status_code, 'body': body }
    except requests.exceptions.RequestException as e:
        return { 'ok': False, 'error': str(e) }


def main():
    cfg = parse_config(CONFIG)
    report = { 'timestamp': datetime.now(timezone.utc).isoformat(), 'checks': {} }

    iam = cfg['IAM_API_BASE']
    cat = cfg['CATALOGO_API_BASE']
    prov = cfg['PROVEEDORES_API_BASE']
    cont = cfg['CONTRATACION_API_BASE']

    # 1) IAM login
    url = f"{iam.rstrip('/')}/auth/login"
    r = safe_request('POST', url, json=DEMO_CRED)
    report['checks']['iam_login'] = { 'url': url, **r }

    token = None
    if r.get('ok') and isinstance(r.get('body'), dict):
        body = r['body']
        token = body.get('access_token') or body.get('accessToken') or body.get('token') or body.get('access_token_value')
        report['checks']['iam_login']['extracted_token'] = bool(token)

    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"

    # 2) IAM /me
    url = f"{iam.rstrip('/')}/me"
    r = safe_request('GET', url, headers=headers)
    report['checks']['iam_me'] = { 'url': url, **r }

    # 3) IAM health
    url = f"{iam.rstrip('/')}/health"
    report['checks']['iam_health'] = safe_request('GET', url)

    # 4) Catalogo paquetes list
    url = f"{cat.rstrip('/')}/v1/catalogo/paquetes"
    report['checks']['catalogo_paquetes'] = safe_request('GET', url)

    # 5) Catalogo paquete by id (seed id from bootstrap.sql)
    seed_pkg = 'bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0'
    url = f"{cat.rstrip('/')}/v1/catalogo/paquetes/{seed_pkg}"
    report['checks']['catalogo_paquete_detail'] = safe_request('GET', url)

    # 6) Proveedores health
    url = f"{prov.rstrip('/')}/health"
    report['checks']['proveedores_health'] = safe_request('GET', url)

    # 7) Proveedores disponibles (today)
    today = datetime.now(timezone.utc).date().isoformat()
    url = f"{prov.rstrip('/')}/v1/proveedores/disponibles?fecha={today}&limit=1"
    report['checks']['proveedores_disponibles'] = safe_request('GET', url)

    # 8) Contratacion health
    url = f"{cont.rstrip('/')}/health"
    report['checks']['contratacion_health'] = safe_request('GET', url)

    # 9) Contratacion misPedidos (requires auth)
    # Nota: el frontend usa ahora rutas bajo /v1/, no /v1/contratacion
    url = f"{cont.rstrip('/')}/pedidos/mios"
    r = safe_request('GET', url, headers=headers)
    report['checks']['contratacion_mis_pedidos'] = { 'url': url, **r }

    # Save report
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Validation complete — report saved to: {REPORT}")

    # Exit non-zero if any critical check failed (login or core services down)
    critical_fail = False
    if not report['checks']['iam_login'].get('ok'):
        critical_fail = True
    if not report['checks']['catalogo_paquetes'].get('ok'):
        critical_fail = True
    if not report['checks']['proveedores_health'].get('ok'):
        critical_fail = True

    if critical_fail:
        print('One or more critical checks failed. See report.')
        sys.exit(2)


if __name__ == '__main__':
    main()
