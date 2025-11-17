# entrypoints/fastapi/security.py
from typing import Any, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError  # python-jose (errors)
from ev_shared.config import Settings
from ev_shared.security import decode_jwt

# auto_error=True hace que falte-> 403 inmediatamente
bearer_scheme = HTTPBearer(auto_error=True)

def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    settings: Settings = Depends(lambda: Settings()),  # usa tu loader si tienes otro
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
        # decode_jwt raises RuntimeError if JWT_SECRET not configured
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT configuration missing (JWT_SECRET).")
