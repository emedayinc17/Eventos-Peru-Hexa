#!/usr/bin/env python3
"""
Simple validator for the public providers endpoint.
Usage:
  python tools/check_providers_public.py --base http://localhost:5173/api

Exit codes:
  0 - OK, endpoint returned >=1 provider
  1 - OK but no providers returned
  2 - Request failed (HTTP error / network error)
"""
import argparse
import json
import sys
import urllib.request
import urllib.error


def parse_args():
    p = argparse.ArgumentParser(description="Check public providers endpoint and print a short report")
    p.add_argument("--base", default=None, help="Base API URL (default: env VITE_API_BASE_URL or http://localhost:5173/api)")
    p.add_argument("--sample", type=int, default=5, help="How many sample providers to print")
    p.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout seconds")
    return p.parse_args()


def choose_base(cli_base):
    if cli_base:
        return cli_base.rstrip('/')
    import os
    env = os.environ.get('VITE_API_BASE_URL') or os.environ.get('API_BASE_URL')
    if env:
        return env.rstrip('/')
    return 'http://localhost:5173/api'


def fetch(url, timeout):
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
            body = resp.read()
            # try decode
            try:
                data = json.loads(body.decode('utf-8'))
            except Exception:
                data = body.decode('utf-8', errors='ignore')
            return status, data
    except urllib.error.HTTPError as e:
        # read body if present
        try:
            body = e.read().decode('utf-8')
        except Exception:
            body = ''
        return e.code, {'error': body}
    except Exception as e:
        return None, {'exception': str(e)}


def normalize_list(raw):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        # try common wrappers
        for k in ('data', 'items', 'proveedores', 'results'):
            if k in raw and isinstance(raw[k], list):
                return raw[k]
    return []


def short(v, maxlen=60):
    if v is None:
        return ''
    s = str(v)
    if len(s) <= maxlen:
        return s
    return s[:maxlen-1] + '…'


def main():
    args = parse_args()
    base = choose_base(args.base)
    url = f"{base}/proveedores/v1/proveedores"
    print(f"Checking public providers endpoint: {url}")

    status, data = fetch(url, args.timeout)
    if status is None:
        print("ERROR: Network error or timeout:", data)
        sys.exit(2)
    if status >= 400:
        print(f"ERROR: HTTP {status} returned by server.")
        print('Response body:', data)
        sys.exit(2)

    items = normalize_list(data)
    count = len(items)
    print(f"OK: HTTP {status}. Providers returned: {count}")

    if count == 0:
        sys.exit(1)

    print('\nSample providers:')
    for i, p in enumerate(items[:args.sample], start=1):
        pid = p.get('id') or p.get('proveedor_id') or ''
        name = p.get('nombre_comercial') or p.get('nombre') or p.get('razon_social') or ''
        email = p.get('email') or ''
        phone = p.get('telefono') or ''
        direccion = p.get('direccion') or ''
        contacto = p.get('contacto') or ''
        rating = p.get('rating_prom')
        print(f"{i}. id={pid} name={short(name)} rating={rating} email={short(email)} phone={short(phone)} direccion={short(direccion)} contacto={short(contacto)}")

    # Basic validation for rating field existence
    ratings_present = any(('rating_prom' in p) for p in items)
    if not ratings_present:
        print('\nWARNING: No "rating_prom" field found in returned items. Check backend field names.')
    sys.exit(0)


if __name__ == '__main__':
    main()
