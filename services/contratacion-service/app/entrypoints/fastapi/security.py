# entrypoints/fastapi/security.py — Contratación
from typing import Any, Dict, Optional
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from ev_shared.config import Settings

# Mantenemos el esquema Bearer para que Swagger muestre "Authorize"
bearer_scheme = HTTPBearer(auto_error=True)

# --- Compat: tu helper actual (no lo quitamos) ---
def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    settings: Settings = Depends(lambda: Settings()),
) -> Dict[str, Any]:
    token = credentials.credentials
    secret = getattr(settings, "JWT_SECRET", None)
    algo = getattr(settings, "JWT_ALG", getattr(settings, "JWT_ALGORITHM", "HS256"))
    if not secret:
        raise HTTPException(status_code=500, detail="JWT configuration missing (JWT_SECRET).")
    try:
        payload = jwt.decode(token, secret, algorithms=[algo])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

# --- Requeridos por router.py ---
def _decode_token(settings: Settings, token: str) -> Dict[str, Any]:
    secret = getattr(settings, "JWT_SECRET", None)
    algo = getattr(settings, "JWT_ALG", getattr(settings, "JWT_ALGORITHM", "HS256"))
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET no configurado")
    try:
        payload = jwt.decode(token, secret, algorithms=[algo])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    # Chequeos mínimos de claims que usa el MVP
    if "sub" not in payload or "username" not in payload or "role" not in payload:
        raise HTTPException(status_code=401, detail="Token inválido (claims)")
    return payload

def get_current_user(
    authorization: Optional[str] = Header(None),
    settings: Settings = Depends(lambda: Settings()),
) -> Dict[str, Any]:
    """
    Extrae y valida Authorization: Bearer <token>
    Devuelve un dict homogéneo: {id, email, role}
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Falta Authorization Bearer")
    token = authorization.split(" ", 1)[1]
    payload = _decode_token(settings, token)
    return {
        "id": payload.get("sub"),
        "email": payload.get("username"),
        "role": payload.get("role"),  # 'ADMIN' / 'CLIENTE' o 'admin' / 'cliente' según IAM; comparamos case-insensitive
    }

def require_role(required: str):
    """
    Uso en rutas admin:
      admin = Depends(require_role("admin"))
    """
    def guard(user: Dict[str, Any] = Depends(get_current_user)):
        role = (user.get("role") or "").lower()
        if role != required.lower():
            raise HTTPException(status_code=403, detail="Sin permisos")
        return user
    return guard
