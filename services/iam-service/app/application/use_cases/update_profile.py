from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy import text
import json
from ev_shared.db import session_scope
from ev_shared.config import Settings
from app.domain.ports import UserRepositoryPort, RoleReaderPort

class UpdateProfileUseCase:
    def __init__(self, *, settings: Settings, user_repo: UserRepositoryPort, role_reader: RoleReaderPort):
        self.settings = settings
        self.user_repo = user_repo
        self.role_reader = role_reader

    def execute(self, *, user_id: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        with session_scope(self.settings) as s:
            # Prevent updating sensitive fields via this use case
            if 'password' in changes:
                del changes['password']
            if 'role' in changes:
                del changes['role']
            if 'email' in changes:
                del changes['email'] # Usually email change requires verification, so skipping for now

            if not changes:
                # No changes to apply
                row = self.user_repo.get_by_id(s, user_id)
                if not row:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
                role_code = self.role_reader.get_role_code_for_user(s, row["id"]) or "CLIENTE"
                return {
                    "id": str(row["id"]),
                    "email": row["email"],
                    "nombre": row["nombre"],
                    "telefono": row["telefono"],
                    "role": role_code,
                    "status": row["status"],
                }

            updated = self.user_repo.update_user_fields(s, user_id, changes)
            if not updated:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

            # Get updated user
            row = self.user_repo.get_by_id(s, user_id)
            role_code = self.role_reader.get_role_code_for_user(s, row["id"]) or "CLIENTE"

            # Audit
            try:
                s.execute(
                    text("""
                        INSERT INTO ev_iam.evento_audit
                            (id, fecha_hora, actor_id, entidad, entidad_id, accion, metadata)
                        VALUES (UUID(), NOW(), :actor, 'usuario', :entidad_id, 'PERFIL_ACTUALIZAR', CAST(:meta AS JSON))
                    """),
                    {"actor": user_id, "entidad_id": user_id, "meta": json.dumps(changes)}
                )
            except Exception:
                pass

        return {
            "id": str(row["id"]),
            "email": row["email"],
            "nombre": row["nombre"],
            "telefono": row["telefono"],
            "role": role_code,
            "status": row["status"],
        }
