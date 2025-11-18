# entrypoints/fastapi/security.py
from typing import Any, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError  # python-jose
from ev_shared.config import Settings

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
    secret = getattr(settings, "JWT_SECRET", None)
    algo = getattr(settings, "JWT_ALGORITHM", "HS256")

    if not secret:
        # Falla segura si no hay clave configurada
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT configuration missing (JWT_SECRET).",
        )

    try:
        payload = jwt.decode(token, secret, algorithms=[algo])
        return payload  # puedes mapear a un dto si quieres
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
