from typing import Dict, Any
from fastapi import HTTPException, status
from ev_shared.db import session_scope
from ev_shared.config import Settings
from app.domain.ports import UserRepositoryPort, RoleReaderPort

class GetProfileUseCase:
    def __init__(self, *, settings: Settings, user_repo: UserRepositoryPort, role_reader: RoleReaderPort):
        self.settings = settings
        self.user_repo = user_repo
        self.role_reader = role_reader

    def execute(self, *, user_id: str) -> Dict[str, Any]:
        with session_scope(self.settings) as s:
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
