#!/usr/bin/env python3
"""
verify_password.py

Verifica si una contraseña coincide con un password_hash bcrypt-sha256.
Uso rápido: ejecutar desde el repo con Python 3:
  python tools/verify_password.py --hash "$bcrypt-sha256$..." --password "test123"

El script también puede conectarse a la BD si se proporcionan las credenciales.
"""
import argparse
import sys


def verify_with_passlib(stored_hash, password):
    try:
        from passlib.hash import bcrypt_sha256
    except Exception as e:
        print("MISSING: passlib library (pip install 'passlib[bcrypt]')")
        return 2
    try:
        ok = bcrypt_sha256.verify(password, stored_hash)
        print("Stored hash:", stored_hash)
        print("Password to test:", password)
        print("Verify result:", ok)
        return 0 if ok else 1
    except Exception as e:
        print("ERROR verifying hash:", e)
        return 2


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hash", help="Stored hash to verify (passlib bcrypt-sha256 format)")
    p.add_argument("--password", required=True, help="Plain password to test (e.g. 'test123')")
    args = p.parse_args()

    if not args.hash:
        print("ERROR: --hash is required for this quick check")
        sys.exit(2)

    rc = verify_with_passlib(args.hash, args.password)
    sys.exit(rc)


if __name__ == "__main__":
    main()
