
"""
ev_shared.security.passwords
----------------------------
Hash y verificación de contraseñas usando bcrypt_sha256.
- Permite contraseñas largas (evita límite 72 bytes de bcrypt puro)
- Soporta hashes legacy bcrypt ($2a/$2b/$2y$) y rehash a bcrypt_sha256
Synopsis: created by emeday 2025
"""
from passlib.hash import bcrypt_sha256, bcrypt

def is_bcrypt(hash_: str) -> bool:
    return hash_.startswith("$2a$") or hash_.startswith("$2b$") or hash_.startswith("$2y$")

def is_bcrypt_sha256(hash_: str) -> bool:
    return hash_.startswith("$bcrypt-sha256$")

def hash_password(plain: str) -> str:
    return bcrypt_sha256.hash(plain)

def verify_password(plain: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False
    if is_bcrypt_sha256(stored_hash):
        return bcrypt_sha256.verify(plain, stored_hash)
    if is_bcrypt(stored_hash):
        return bcrypt.verify(plain, stored_hash)
    # formato no soportado
    return False

def needs_rehash(stored_hash: str) -> bool:
    if not stored_hash:
        return False
    # Se fuerza migración de bcrypt -> bcrypt_sha256
    if is_bcrypt(stored_hash):
        return True
    if is_bcrypt_sha256(stored_hash):
        return bcrypt_sha256.needs_update(stored_hash)
    return True
