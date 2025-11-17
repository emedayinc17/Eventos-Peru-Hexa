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


def decode_jwt(token: str, leeway: int = 60, algorithms: Optional[list[str]] = None) -> Dict[str, Any]:
    """
    Decode a JWT using settings from ev_shared.config.load_settings().
    Use manual exp check with leeway for compatibility with different jose versions.
    Raises jose.JWTError on signature/parse failure or RuntimeError if secret missing.
    """
    s = load_settings()
    secret = getattr(s, "JWT_SECRET", None)
    algo = getattr(s, "JWT_ALG", getattr(s, "JWT_ALGORITHM", "HS256"))
    if not secret:
        raise RuntimeError("JWT_SECRET not configured in settings")
    used_algorithms = algorithms or [algo]

    try:
        payload = jwt.decode(token, secret, algorithms=used_algorithms, options={"verify_exp": False})
    except Exception as e:
        # Let jose raise a JWTError (or other) to callers
        raise

    exp = payload.get("exp")
    if exp is not None:
        from datetime import datetime, timezone
        try:
            exp_ts = int(exp)
            now_ts = int(datetime.now(timezone.utc).timestamp())
            if now_ts > exp_ts + int(leeway):
                from jose import JWTError as _JWTError
                raise _JWTError("Token expired")
        except ValueError:
            from jose import JWTError as _JWTError
            raise _JWTError("Invalid exp claim")

    return payload
