# app/infrastructure/security/jwt_adapter.py
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

class JwtError(Exception):
    pass

def create_token(*, subject: str, claims: dict | None, secret: str, expires_minutes: int, algorithm: str = "HS256") -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=expires_minutes)).timestamp())}
    if claims:
        payload.update(claims)
    return jwt.encode(payload, secret, algorithm=algorithm)

def decode_token(token: str, secret: str, algorithms: list[str] | None = None) -> dict:
    try:
        return jwt.decode(token, secret, algorithms=algorithms or ["HS256"])
    except JWTError as e:
        raise JwtError(str(e)) from e
