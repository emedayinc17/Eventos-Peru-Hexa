from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt
from passlib.context import CryptContext
from .config import load_settings

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return _pwd.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)

def make_jwt(subject: str, claims: Optional[Dict[str, Any]] = None) -> str:
    s = load_settings()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=int(s.JWT_EXPIRES_MIN))
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    if claims:
        payload.update(claims)
    token = jwt.encode(payload, s.JWT_SECRET, algorithm="HS256")
    return token
