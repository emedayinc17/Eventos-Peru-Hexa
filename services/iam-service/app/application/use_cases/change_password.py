from typing import Dict, Any
from fastapi import HTTPException, status
from sqlalchemy import text
import json
from ev_shared.db import session_scope
from ev_shared.config import Settings
from app.domain.ports import UserRepositoryPort
from app.infrastructure.security.password_adapter import hash_password, verify_password

class ChangePasswordUseCase:
    def __init__(self, *, settings: Settings, user_repo: UserRepositoryPort):
        self.settings = settings
        self.user_repo = user_repo

    def execute(self, *, user_id: str, current_password: str, new_password: str) -> bool:
        with session_scope(self.settings) as s:
            # 1. Get user to verify current password
            row = self.user_repo.get_by_id(s, user_id)
            if not row:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

            stored_hash = row["password_hash"]
            if not verify_password(current_password, stored_hash):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña actual incorrecta")

            # 2. Validate new password
            if len(new_password) < 6:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La nueva contraseña debe tener al menos 6 caracteres")

            # 3. Update password
            hashed_password = hash_password(new_password)
            s.execute(
                text("""
                    UPDATE ev_iam.usuario 
                    SET password_hash = :password 
                    WHERE id = :user_id
                """),
                {"password": hashed_password, "user_id": user_id}
            )

            # 4. Audit
            try:
                s.execute(
                    text("""
                        INSERT INTO ev_iam.evento_audit
                            (id, fecha_hora, actor_id, entidad, entidad_id, accion, metadata)
                        VALUES (UUID(), NOW(), :actor, 'usuario', :entidad_id, 'PASSWORD_CAMBIAR', '{}')
                    """),
                    {"actor": user_id, "entidad_id": user_id}
                )
            except Exception:
                pass

        return True
