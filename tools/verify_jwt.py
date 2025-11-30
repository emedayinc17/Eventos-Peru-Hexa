#!/usr/bin/env python3
"""
verify_jwt.py

Helper to inspect JWT claims and optionally verify signature using a provided secret.

Usage:
  python tools/verify_jwt.py --token <JWT> [--secret <JWT_SECRET>] [--alg HS256]

If no secret is provided the script decodes header/payload without verification.
"""
from __future__ import annotations
import argparse
import base64
import json
import sys
from typing import Any


def b64decode_segment(seg: str) -> bytes:
    # pad
    seg = seg.replace('-', '+').replace('_', '/')
    padding = len(seg) % 4
    if padding:
        seg += '=' * (4 - padding)
    return base64.b64decode(seg)


def decode_no_verify(token: str) -> dict:
    parts = token.split('.')
    if len(parts) < 2:
        raise ValueError('Invalid JWT format')
    header = json.loads(b64decode_segment(parts[0]).decode('utf-8', errors='ignore'))
    payload = json.loads(b64decode_segment(parts[1]).decode('utf-8', errors='ignore'))
    return {'header': header, 'payload': payload}


def try_verify_with_jose(token: str, secret: str, alg: str) -> bool:
    try:
        from jose import jwt as _jwt
        _jwt.decode(token, secret, algorithms=[alg])
        return True
    except Exception as e:
        print('jose verification failed:', repr(e))
        return False


def try_verify_with_pyjwt(token: str, secret: str, alg: str) -> bool:
    try:
        import jwt as _jwt
        _jwt.decode(token, secret, algorithms=[alg])
        return True
    except Exception as e:
        print('pyjwt verification failed:', repr(e))
        return False


def main():
    p = argparse.ArgumentParser(description='Inspect and optionally verify JWT token')
    p.add_argument('--token', required=True, help='JWT token string')
    p.add_argument('--secret', required=False, help='Secret to verify signature (HS algorithms)')
    p.add_argument('--alg', required=False, default='HS256', help='Alg to use for verification (default HS256)')
    args = p.parse_args()

    token = args.token.strip()
    try:
        data = decode_no_verify(token)
    except Exception as e:
        print('Failed to decode token:', e)
        sys.exit(2)

    print('\n=== HEADER ===')
    print(json.dumps(data['header'], indent=2, ensure_ascii=False))
    print('\n=== PAYLOAD ===')
    print(json.dumps(data['payload'], indent=2, ensure_ascii=False))

    if args.secret:
        print('\n=== VERIFY SIGNATURE ===')
        secret = args.secret
        alg = args.alg
        ok = None
        # Try jose first (used in repo), fallback to pyjwt
        ok = try_verify_with_jose(token, secret, alg)
        if not ok:
            ok = try_verify_with_pyjwt(token, secret, alg)
        if ok:
            print('Signature verification: OK')
            sys.exit(0)
        else:
            print('Signature verification: FAILED')
            sys.exit(3)
    else:
        print('\nNo secret provided — only decoded header/payload shown.')
        sys.exit(0)


if __name__ == '__main__':
    main()
