# Created by emeday, 2025
# Thin adapter the IAM service can import, keeping the hexagonal boundaries.
# It delegates to the shared library so we have a single password policy.

#from ev_shared.security.passwords import hash_password, verify_password, identify_scheme
#
#__all__ = ["hash_password", "verify_password", "identify_scheme"]

# app/infrastructure/security/password_adapter.py
from ev_shared.security.passwords import verify_password as _verify, hash_password as _hash

def verify_password(plain: str, hashed: str) -> bool:
    return _verify(plain, hashed)

def hash_password(plain: str) -> str:
    return _hash(plain)
