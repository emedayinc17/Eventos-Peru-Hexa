#!/usr/bin/env python3
"""
validate_auth_flow.py

Simple smoke-test script to validate authentication and authorization flows
against the EventosPeru API Gateway.

Checks performed:
 - Login for admin and client (POST /api/iam/auth/login)
 - Validate /api/iam/me with returned token
 - Client token -> GET /api/contratacion/cliente/mis-pedidos (expect 200)
 - Client token -> GET /api/contratacion/admin/pedidos (expect 401/403)
 - Admin token  -> GET /api/contratacion/admin/pedidos (expect 200)

Usage:
  python tools/validate_auth_flow.py --base https://eventos.emeday.inc \
      --admin-email admin@eventos.pe --admin-pass Secret123 \
      --client-email demo@eventos.pe --client-pass Demo123

The script returns exit code 0 if all expected checks pass, non-zero otherwise.
"""
from __future__ import annotations
import argparse
import sys
import requests
from typing import Optional, Dict, Any


def login(session: requests.Session, base: str, email: str, password: str, verify: bool) -> Optional[Dict[str, Any]]:
    url = f"{base.rstrip('/')}/api/iam/auth/login"
    payload = {"username": email, "password": password}
    try:
        r = session.post(url, json=payload, timeout=15, verify=verify)
    except Exception as e:
        print(f"ERROR: login request failed for {email}: {e}")
        return None
    try:
        data = r.json()
    except Exception:
        data = {"raw_text": r.text}
    print(f"[login] {email}: status={r.status_code} body={data}")
    if r.status_code != 200:
        return None
    return data


def call_get(session: requests.Session, base: str, path: str, token: str, verify: bool) -> requests.Response:
    url = f"{base.rstrip('/')}{path if path.startswith('/') else '/' + path}"
    headers = {"Authorization": f"Bearer {token}"}
    return session.get(url, headers=headers, timeout=15, verify=verify)


def check_flow(base: str, admin_email: str, admin_pass: str, client_email: str, client_pass: str, verify: bool) -> int:
    session = requests.Session()
    results = []

    print("\n== LOGIN PHASE ==")
    admin_login = login(session, base, admin_email, admin_pass, verify)
    client_login = login(session, base, client_email, client_pass, verify)

    if not admin_login:
        print("FAIL: admin login failed")
        return 2
    if not client_login:
        print("FAIL: client login failed")
        return 3

    admin_token = admin_login.get('access_token') or admin_login.get('token') or admin_login.get('accessToken')
    client_token = client_login.get('access_token') or client_login.get('token') or client_login.get('accessToken')

    if not admin_token:
        print("FAIL: admin token missing in login response")
        return 4
    if not client_token:
        print("FAIL: client token missing in login response")
        return 5

    print('\n== VERIFY /api/iam/me ==')
    for who, tok in [('admin', admin_token), ('client', client_token)]:
        try:
            r = call_get(session, base, '/api/iam/me', tok, verify)
            print(f"/api/iam/me ({who}): status={r.status_code} body={safe_json(r)}")
            if r.status_code != 200:
                print(f"WARN: /api/iam/me returned {r.status_code} for {who}")
        except Exception as e:
            print(f"ERROR calling /api/iam/me for {who}: {e}")

    print('\n== CLIENT endpoint tests ==')
    # client token should be able to call cliente/mis-pedidos
    try:
        r = call_get(session, base, '/api/contratacion/cliente/mis-pedidos', client_token, verify)
        print(f"client -> /cliente/mis-pedidos: status={r.status_code} body_sample={safe_json(r, maxlen=200)}")
        if r.status_code == 200:
            results.append(('client_mis_pedidos', True))
        else:
            results.append(('client_mis_pedidos', False, r.status_code, safe_json(r)))
    except Exception as e:
        print(f"ERROR calling client endpoint: {e}")
        results.append(('client_mis_pedidos', False, 'exception', str(e)))

    print('\n== ADMIN endpoint tests ==')
    # client token should NOT be allowed to admin endpoint
    try:
        r = call_get(session, base, '/api/contratacion/admin/pedidos', client_token, verify)
        print(f"client -> /admin/pedidos: status={r.status_code} body_sample={safe_json(r, maxlen=200)}")
        if r.status_code in (401, 403):
            results.append(('client_admin_pedidos_blocked', True))
        else:
            results.append(('client_admin_pedidos_blocked', False, r.status_code, safe_json(r)))
    except Exception as e:
        print(f"ERROR calling admin endpoint with client token: {e}")
        results.append(('client_admin_pedidos_blocked', False, 'exception', str(e)))

    # admin token should be allowed to admin endpoint
    try:
        r = call_get(session, base, '/api/contratacion/admin/pedidos', admin_token, verify)
        print(f"admin -> /admin/pedidos: status={r.status_code} body_sample={safe_json(r, maxlen=200)}")
        if r.status_code == 200:
            results.append(('admin_admin_pedidos_allowed', True))
        else:
            results.append(('admin_admin_pedidos_allowed', False, r.status_code, safe_json(r)))
    except Exception as e:
        print(f"ERROR calling admin endpoint with admin token: {e}")
        results.append(('admin_admin_pedidos_allowed', False, 'exception', str(e)))

    # Summarize
    print('\n== SUMMARY ==')
    failed = False
    for row in results:
        if row[1] is True:
            print(f"OK: {row[0]}")
        else:
            failed = True
            print(f"FAIL: {row[0]} details: {row[2:]}")

    if failed:
        print('\nOne or more checks failed. See details above.')
        return 10
    print('\nAll checks passed ✔')
    return 0


def safe_json(resp: requests.Response, maxlen: int = 800) -> Any:
    try:
        j = resp.json()
        s = str(j)
        if len(s) > maxlen:
            return s[:maxlen] + '...'
        return j
    except Exception:
        text = getattr(resp, 'text', '')
        if len(text) > maxlen:
            return text[:maxlen] + '...'
        return text


def parse_args():
    p = argparse.ArgumentParser(description='Validate auth + authorization flow via API Gateway')
    p.add_argument('--base', required=False, default='http://localhost:8000', help='Base URL of API Gateway (e.g. https://eventos.emeday.inc)')
    p.add_argument('--admin-email', required=True, help='Admin email to login')
    p.add_argument('--admin-pass', required=True, help='Admin password')
    p.add_argument('--client-email', required=True, help='Client/demo email')
    p.add_argument('--client-pass', required=True, help='Client/demo password')
    p.add_argument('--insecure', action='store_true', help='Disable SSL verification')
    return p.parse_args()


def main():
    args = parse_args()
    verify = not args.insecure
    rc = check_flow(args.base, args.admin_email, args.admin_pass, args.client_email, args.client_pass, verify)
    sys.exit(rc)


if __name__ == '__main__':
    main()
