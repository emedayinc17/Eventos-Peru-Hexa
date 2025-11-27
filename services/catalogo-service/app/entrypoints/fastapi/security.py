# entrypoints/fastapi/security.py
from typing import Any, Dict, Optional
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from ev_shared.config import Settings
from ev_shared.security import decode_jwt

# auto_error=True hace que falte-> 403 inmediatamente
bearer_scheme = HTTPBearer(auto_error=True)

def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    settings: Settings = Depends(lambda: Settings()),
) -> Dict[str, Any]:
    """
    Valida el JWT (firma + expiración) y devuelve los claims del usuario.
    Lanza 401 si no es válido.
    """
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    except RuntimeError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT configuration missing (JWT_SECRET).")


def _decode_token(settings: Settings, token: str) -> Dict[str, Any]:
    """
    Decodifica y valida JWT token.
    Lanza HTTPException si es inválido.
    """
    try:
        payload = decode_jwt(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    except RuntimeError:
        raise HTTPException(status_code=500, detail="JWT_SECRET no configurado")

    # Validar claims mínimos
    if "sub" not in payload or "role" not in payload:
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
        "email": payload.get("username") or payload.get("email"),
        "role": payload.get("role"),
    }


def require_role(required: str):
    """
    Dependency para validar rol específico.
    Uso en rutas admin:
      admin = Depends(require_role("ADMIN"))
    """
    def guard(user: Dict[str, Any] = Depends(get_current_user)):
        role = (user.get("role") or "").upper()
        if role != required.upper():
            raise HTTPException(status_code=403, detail="Sin permisos")
        return user
    return guard
