#!/usr/bin/env python3
import requests
from jose import jwt, JWTError
import re

IAM_LOGIN_URL = "http://127.0.0.1:8010/iam/auth/login"
# FIX: avoid hardcoded absolute Windows paths; resolve .env relative to repository root
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[1]
IAM_ENV = str((REPO_ROOT / 'services' / 'iam-service' / '.env').resolve())
CONTR_ENV = str((REPO_ROOT / 'services' / 'contratacion-service' / '.env').resolve())

EMAIL = "demo@eventos.pe"
PASSWORD = "Admin_2025!"


def read_secret(env_path):
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                m = re.match(r"JWT_SECRET\s*=\s*(.+)", line)
                if m:
                    return m.group(1).strip()
    except FileNotFoundError:
        return None
    return None


def try_decode(token, secret, label):
    if not secret:
        print(f"[{label}] secret not found")
        return
    try:
        print(f"Trying decode with {label} (len={len(secret)})")
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        print(f"  -> success, payload keys: {list(payload.keys())}")
    except Exception as e:
        print(f"  -> decode failed with {label}: {type(e).__name__}: {e}")


if __name__ == '__main__':
    print("Logging into IAM...", IAM_LOGIN_URL)
    resp = requests.post(IAM_LOGIN_URL, json={"email": EMAIL, "password": PASSWORD}, timeout=10)
    print("Login status:", resp.status_code)
    try:
        data = resp.json()
    except Exception:
        print("Login response not JSON:", resp.text)
        raise SystemExit(1)
    token = data.get('access_token') or data.get('token')
    if not token:
        print("No token returned, response:", data)
        raise SystemExit(2)
    print("Token (trunc):", token[:80])

    iam_secret = read_secret(IAM_ENV)
    contr_secret = read_secret(CONTR_ENV)

    try_decode(token, iam_secret, 'IAM .env')
    try_decode(token, contr_secret, 'Contratacion .env')

    # Also try decoding using ev_shared config loader (if available)
    try:
        from ev_shared.config import load_settings
        s = load_settings()
        print("ev_shared.load_settings() JWT_SECRET (len):", len(getattr(s, 'JWT_SECRET', ''))) 
        try_decode(token, getattr(s, 'JWT_SECRET', None), 'ev_shared.load_settings (cwd)')
    except Exception as e:
        print("Could not import ev_shared.config:", e)
