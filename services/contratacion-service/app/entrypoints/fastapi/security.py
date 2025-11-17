# entrypoints/fastapi/security.py — Contratación
from typing import Any, Dict, Optional
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from ev_shared.config import Settings
from ev_shared.security import decode_jwt

# Mantenemos el esquema Bearer para que Swagger muestre "Authorize"
bearer_scheme = HTTPBearer(auto_error=True)

# --- Compat: tu helper actual (no lo quitamos) ---
def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    settings: Settings = Depends(lambda: Settings()),
) -> Dict[str, Any]:
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    except RuntimeError:
        raise HTTPException(status_code=500, detail="JWT configuration missing (JWT_SECRET).")

# --- Requeridos por router.py ---
def _decode_token(settings: Settings, token: str) -> Dict[str, Any]:
    try:
        payload = decode_jwt(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    except RuntimeError:
        raise HTTPException(status_code=500, detail="JWT_SECRET no configurado")

    # Chequeos mínimos de claims que usa el MVP
    # Aceptamos 'username' o 'email' para compatibilidad con tokens antiguos/variantes
    if "sub" not in payload or ("username" not in payload and "email" not in payload) or "role" not in payload:
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
