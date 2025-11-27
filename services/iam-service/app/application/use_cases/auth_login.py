from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy import text
import logging

from ev_shared.db import session_scope
from ev_shared.config import Settings

from app.domain.ports import UserRepositoryPort, RoleReaderPort
from app.infrastructure.security.password_adapter import verify_password
from app.infrastructure.security.jwt_adapter import create_token

logger = logging.getLogger(__name__)

class AuthLoginUseCase:
    def __init__(self, *, settings: Settings, user_repo: UserRepositoryPort, role_reader: RoleReaderPort):
        self.settings = settings
        self.user_repo = user_repo
        self.role_reader = role_reader

    def execute(self, *, email: str, password: str, ip: Optional[str] = None) -> Dict[str, Any]:
        secret = getattr(self.settings, "JWT_SECRET")
        alg = getattr(self.settings, "JWT_ALG", getattr(self.settings, "JWT_ALGORITHM", "HS256"))
        exp_min = int(getattr(self.settings, "JWT_EXPIRES_MIN", 60))

        with session_scope(self.settings) as s:
            u = self.user_repo.get_active_by_email(s, email)
            if not u or not u.get("password_hash") or not verify_password(password, u["password_hash"]):
                s.execute(
                    text("""
                        INSERT INTO ev_iam.login_intento (id, usuario_id, email, ip, exito)
                        VALUES (UUID(), NULL, :e, :ip, 0)
                    """),
                    {"e": email, "ip": ip}
                )
                try:
                    s.execute(
                        text("""
                            INSERT INTO ev_iam.evento_audit
                                (id, fecha_hora, actor_id, entidad, entidad_id, accion, metadata)
                            VALUES (UUID(), NOW(), NULL, 'login', '00000000-0000-0000-0000-000000000000', 'LOGIN_FALLIDO', JSON_OBJECT('email', :e))
                        """),
                        {"e": email}
                    )
                except Exception:
                    pass
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

            role_code = self.role_reader.get_role_code_for_user(s, u["id"]) or "CLIENTE"

            s.execute(
                text("""
                    INSERT INTO ev_iam.login_intento (id, usuario_id, email, ip, exito)
                    VALUES (UUID(), :uid, :e, :ip, 1)
                """),
                {"uid": u["id"], "e": u["email"], "ip": ip}
            )
            self.user_repo.touch_last_login(s, u["id"])
            try:
                s.execute(
                    text("""
                        INSERT INTO ev_iam.evento_audit
                            (id, fecha_hora, actor_id, entidad, entidad_id, accion, metadata)
                        VALUES (UUID(), NOW(), :actor, 'login', :actor, 'LOGIN', JSON_OBJECT('email', :e, 'role', :r))
                    """),
                    {"actor": u["id"], "e": u["email"], "r": role_code}
                )
            except Exception:
                pass

        token = create_token(
            subject=str(u["id"]),
            claims={"username": u["email"], "role": role_code, "scope": "access_token"},
            secret=secret,
            expires_minutes=exp_min,
            algorithm=alg,
        )
        try:
            logger.debug("create_token used secret length=%s", len(secret) if secret is not None else 0)
        except Exception:
            logger.debug("create_token used secret <unprintable>")
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": exp_min * 60,
            "role": role_code,
        }
