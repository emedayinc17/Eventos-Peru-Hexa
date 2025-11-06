from typing import Optional, Any, Dict, List
from app.infrastructure.persistence import repo_users as impl

class UserRepositoryAdapter:
    def get_by_email(self, s, email: str) -> Optional[Dict[str, Any]]:
        return impl.get_by_email(s, email)

    def get_active_by_email(self, s, email: str) -> Optional[Dict[str, Any]]:
        return impl.get_active_by_email(s, email)

    def get_by_id(self, s, user_id: str) -> Optional[Dict[str, Any]]:
        return impl.get_by_id(s, user_id)

    def list_users(self, s, *, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        return impl.list_users(s, limit=limit, offset=offset)

    def create_user(self, s, *, email: str, password_hash: str, nombre: Optional[str], telefono: Optional[str]) -> str:
        return impl.create_user(s, email=email, password_hash=password_hash, nombre=nombre, telefono=telefono)

    def touch_last_login(self, s, user_id: str) -> None:
        return impl.touch_last_login(s, user_id)

    def update_user_fields(self, s, user_id: str, changes: Dict[str, Any]) -> int:
        return impl.update_user_fields(s, user_id, changes)

    def soft_delete(self, s, user_id: str) -> int:
        return impl.soft_delete(s, user_id)
