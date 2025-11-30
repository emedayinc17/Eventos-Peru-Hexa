"""Admin dashboard check script

Purpose:
 - Authenticate against IAM (`/iam/auth/login`) using admin credentials
 - Call admin endpoints on the services to retrieve counts / sample data:
     - Contratación: `/v1/contratacion/admin/pedidos`
     - Proveedores: `/proveedores/v1/admin/proveedores`
     - IAM: `/iam/admin/users`
 - Print status codes and JSON / extracted counts to help debug why the dashboard shows null.

Usage:
 - Set environment variables to configure URLs and admin credentials (defaults shown):
     - IAM_URL (default: http://127.0.0.1:8010)
     - CONTRATACION_URL (default: http://127.0.0.1:8040)
     - PROVEEDORES_URL (default: http://127.0.0.1:8030)
     - GATEWAY_URL (default: http://127.0.0.1:8000)
     - ADMIN_EMAIL (default: admin@example.com)
     - ADMIN_PASSWORD (default: admin)

Run:
    python tools/admin_dashboard_check.py

This script is defensive: it will try direct service calls using the service URLs, and will fall back
to querying the gateway summary (`/api/admin/summary`) if direct calls are not configured.
"""
from __future__ import annotations

import os
import sys
import argparse
import json
from typing import Optional, Tuple

import requests


def get_env(name: str, default: Optional[str] = None) -> str:
    return os.getenv(name, default) if os.getenv(name, default) is not None else (default or "")


def login_iam(iam_url: str, email: str, password: str, timeout: int = 6) -> Optional[str]:
    url = f"{iam_url.rstrip('/')}/iam/auth/login"
    print(f"Logging in to IAM: {url} (user={email})")
    try:
        r = requests.post(url, json={"email": email, "password": password}, timeout=timeout)
    except Exception as e:
        print(f"  ERROR: request to IAM login failed: {e}")
        return None
    print(f"  IAM login status: {r.status_code}")
    if r.status_code != 200:
        print(f"  Response: {r.status_code} {r.text}")
        return None
    try:
        token = r.json().get("access_token") or r.json().get("token")
        if not token:
            print("  WARNING: login response did not contain access_token/token")
        return token
    except Exception as e:
        print(f"  ERROR parsing IAM login JSON: {e}")
        return None


def call_endpoint(method: str, url: str, token: Optional[str] = None, timeout: int = 6) -> Tuple[int, Optional[dict]]:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.request(method, url, headers=headers, timeout=timeout)
    except Exception as e:
        print(f"  ERROR: Request to {url} failed: {e}")
        return 0, None
    status = r.status_code
    try:
        body = r.json()
    except Exception:
        body = {"text": r.text}
    return status, body


def extract_count(body: Optional[dict]) -> Optional[int]:
    if body is None:
        return None
    # Common patterns
    if isinstance(body, dict):
        for k in ("total", "count", "results", "items", "data"):
            if k in body:
                v = body[k]
                if isinstance(v, int):
                    return v
                if isinstance(v, list):
                    return len(v)
                if isinstance(v, dict) and "total" in v and isinstance(v.get("total"), int):
                    return v.get("total")
        # maybe the response is a list under 'items' or top-level list
    if isinstance(body, list):
        return len(body)
    return None


def pretty_print(title: str, status: int, body: Optional[dict]):
    print(f"\n-- {title} --")
    print(f"Status: {status}")
    if body is None:
        print("Body: <no response body>")
        return
    try:
        print(json.dumps(body, indent=2, ensure_ascii=False)[:4000])
    except Exception:
        print(str(body))
    count = extract_count(body)
    print(f"Extracted count: {count}\n")


def main():
    parser = argparse.ArgumentParser(description="Admin dashboard quick checker")
    parser.add_argument("--no-login", action="store_true", help="Skip IAM login (use ADMIN_TOKEN env)")
    parser.add_argument("--email", "-e", help="Admin email for IAM login (overrides ADMIN_EMAIL env)")
    parser.add_argument("--password", "-p", help="Admin password for IAM login (overrides ADMIN_PASSWORD env)")
    args = parser.parse_args()

    IAM = get_env("IAM_URL", "http://127.0.0.1:8010")
    CONTRATACION = get_env("CONTRATACION_URL", "http://127.0.0.1:8040")
    PROVEEDORES = get_env("PROVEEDORES_URL", "http://127.0.0.1:8030")
    GATEWAY = get_env("GATEWAY_URL", "http://127.0.0.1:8000")
    ADMIN_EMAIL = args.email or get_env("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = args.password or get_env("ADMIN_PASSWORD", "admin")
    ADMIN_TOKEN = os.getenv("ADMIN_SERVICE_TOKEN") or os.getenv("ADMIN_TOKEN")

    print("Configuration:")
    print(f"  IAM: {IAM}")
    print(f"  CONTRATACION: {CONTRATACION}")
    print(f"  PROVEEDORES: {PROVEEDORES}")
    print(f"  GATEWAY: {GATEWAY}")

    token = ADMIN_TOKEN
    if not args.no_login and not token:
        token = login_iam(IAM, ADMIN_EMAIL, ADMIN_PASSWORD)
        if not token:
            print("\nCould not obtain admin token from IAM. You can set ADMIN_SERVICE_TOKEN env and rerun.")

    # Try direct service admin endpoints
    results = {}

    # Contratación: try multiple candidate admin endpoints (some deployments mount without /v1/contratacion)
    contratacion_candidates = [
        f"{CONTRATACION.rstrip('/')}/admin/metrics",
        f"{CONTRATACION.rstrip('/')}/metrics",
        f"{CONTRATACION.rstrip('/')}/admin/pedidos",
        f"{CONTRATACION.rstrip('/')}/v1/contratacion/admin/pedidos",
        f"{CONTRATACION.rstrip('/')}/v1/contratacion/admin/metrics",
        f"{CONTRATACION.rstrip('/')}/contratacion/admin/metrics",
    ]
    contr_status = 0
    contr_body = None
    contr_url = None
    for cand in contratacion_candidates:
        status, body = call_endpoint("GET", cand, token)
        if status and status < 400:
            contr_status = status
            contr_body = body
            contr_url = cand
            break
        # keep last seen
        contr_status = status
        contr_body = body
        contr_url = cand
    results["contratacion"] = {"url": contr_url, "status": contr_status, "body": contr_body}

    # Proveedores admin proveedores
    prov_url = f"{PROVEEDORES.rstrip('/')}/proveedores/v1/admin/proveedores"
    status, body = call_endpoint("GET", prov_url, token)
    results["proveedores"] = {"url": prov_url, "status": status, "body": body}

    # IAM admin users
    iam_url = f"{IAM.rstrip('/')}/iam/admin/users"
    status, body = call_endpoint("GET", iam_url, token)
    results["iam"] = {"url": iam_url, "status": status, "body": body}

    # Print concise output
    for k in ("contratacion", "proveedores", "iam"):
        entry = results[k]
        pretty_print(k, entry["status"], entry["body"])

    # If everything failed or token missing, try gateway summary as fallback
    if all(results[k]["status"] in (0, 401, 403, 404) for k in results) or not token:
        print("\nFallback: querying gateway /api/admin/summary")
        gw_url = f"{GATEWAY.rstrip('/')}/api/admin/summary"
        status, body = call_endpoint("GET", gw_url, token)
        pretty_print("gateway.summary", status, body)


if __name__ == "__main__":
    main()
