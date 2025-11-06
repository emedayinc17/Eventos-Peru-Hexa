from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy import text

from ev_shared.db import session_scope
from ev_shared.config import Settings

from app.domain.ports import UserRepositoryPort, RoleReaderPort
from app.infrastructure.security.password_adapter import hash_password

class RegisterUserUseCase:
    def __init__(self, *, settings: Settings, user_repo: UserRepositoryPort, role_reader: RoleReaderPort):
        self.settings = settings
        self.user_repo = user_repo
        self.role_reader = role_reader

    def execute(self, *, email: str, password: str, nombre: Optional[str], telefono: Optional[str]) -> Dict[str, Any]:
        email = email.strip().lower()

        with session_scope(self.settings) as s:
            if self.user_repo.get_by_email(s, email):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ya registrado")

        ph = hash_password(password)

        with session_scope(self.settings) as s:
            user_id = self.user_repo.create_user(s, email=email, password_hash=ph, nombre=nombre, telefono=telefono)
            self.role_reader.set_single_role_for_user(s, user_id, "CLIENTE")
            row = self.user_repo.get_by_id(s, user_id)
            role_code = self.role_reader.get_role_code_for_user(s, user_id) or "CLIENTE"

            try:
                s.execute(
                    text("""
                        INSERT INTO ev_iam.evento_audit
                            (id, fecha_hora, actor_id, entidad, entidad_id, accion, metadata)
                        VALUES (UUID(), NOW(), :actor, 'usuario', :actor, 'USUARIO_CREAR', JSON_OBJECT('email', :e, 'role', :r))
                    """),
                    {"actor": user_id, "e": row["email"], "r": role_code}
                )
            except Exception:
                pass

        return {
            "id": str(row["id"]),
            "email": row["email"],
            "nombre": row.get("nombre"),
            "telefono": row.get("telefono"),
            "role": role_code,
            "status": row["status"],
        }
