
"""
tools/hash_password.py
----------------------
CLI para generar hashes bcrypt_sha256.
Usage:
    python tools/hash_password.py "MiClave"
Synopsis: created by emeday 2025
"""
import sys
import os

# Agregar la ruta raíz del proyecto al Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ev_shared.security.passwords import hash_password

def main():
    if len(sys.argv) < 2:
        print("Uso: python tools/hash_password.py <password>")
        sys.exit(1)
    pw = sys.argv[1]
    print(hash_password(pw))

if __name__ == "__main__":
    main()
