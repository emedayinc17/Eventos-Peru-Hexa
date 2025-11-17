import sys
import os

# Agregar la ruta del proyecto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from passlib.hash import bcrypt_sha256
except ImportError:
    print("Instalando passlib...")
    os.system("pip install passlib")
    from passlib.hash import bcrypt_sha256

def hash_password(plain: str) -> str:
    """Hash usando bcrypt_sha256 (igual que tu app)"""
    return bcrypt_sha256.hash(plain)

def main():
    if len(sys.argv) < 2:
        print("Uso: python hash_password.py <password>")
        sys.exit(1)
    
    password = sys.argv[1]
    hashed = hash_password(password)
    print(hashed)

if __name__ == "__main__":
    main()