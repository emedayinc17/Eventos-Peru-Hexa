# created by emeday 2025
"""JWT y hashing de contraseñas."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import uuid
from jose import jwt
from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return _pwd.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)

def create_access_token(subject: str, *, secret: str, algorithm: str = "HS256",
                        expires_minutes: int = 60, extra: Optional[Dict[str, Any]] = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": subject, "iat": int(now.timestamp()), "jti": uuid.uuid4().hex}
    if expires_minutes:
        exp = now + timedelta(minutes=expires_minutes)
        payload["exp"] = int(exp.timestamp())
    if extra:
        payload.update(extra)
    return jwt.encode(payload, secret, algorithm=algorithm)
