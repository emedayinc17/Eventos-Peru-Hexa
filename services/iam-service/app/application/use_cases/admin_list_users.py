from typing import List, Dict, Any
from ev_shared.db import session_scope
from ev_shared.config import Settings
from app.domain.ports import UserRepositoryPort, RoleReaderPort

class AdminListUsersUseCase:
    def __init__(self, *, settings: Settings, user_repo: UserRepositoryPort, role_reader: RoleReaderPort):
        self.settings = settings
        self.user_repo = user_repo
        self.role_reader = role_reader

    def execute(self, *, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        with session_scope(self.settings) as s:
            base = self.user_repo.list_users(s, limit=limit, offset=offset)
            out: List[Dict[str, Any]] = []
            for rw in base:
                role_code = self.role_reader.get_role_code_for_user(s, rw["id"]) or "CLIENTE"
                out.append({
                    "id": str(rw["id"]),
                    "email": rw["email"],
                    "nombre": rw["nombre"],
                    "telefono": rw["telefono"],
                    "role": role_code,
                    "status": rw["status"],
                })
        return out
