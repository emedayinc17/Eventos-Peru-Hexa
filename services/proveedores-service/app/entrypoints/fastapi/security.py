# entrypoints/fastapi/security.py
from typing import Any, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError  # python-jose (errors)
import logging
from ev_shared.config import Settings
from ev_shared.security import decode_jwt

logger = logging.getLogger(__name__)
import hashlib

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
        # Log non-sensitive fingerprint of configured JWT secret to help debug mismatches
        try:
            s = Settings()
            js = getattr(s, 'JWT_SECRET', None)
            if js:
                fp = hashlib.sha256(js.encode('utf-8')).hexdigest()[:12]
                logger.debug("require_user JWT secret fingerprint=%s length=%s", fp, len(js))
            else:
                logger.debug("require_user JWT secret missing or empty")
        except Exception:
            logger.debug("require_user could not compute JWT secret fingerprint")
        return payload
    except JWTError as e:
        # Log the exact JWT error at debug level to aid diagnosis (do not log the token)
        try:
            logger.debug("decode_jwt raised JWTError: %r", e)
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    except RuntimeError:
        # decode_jwt raises RuntimeError if JWT_SECRET not configured
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT configuration missing (JWT_SECRET).")
