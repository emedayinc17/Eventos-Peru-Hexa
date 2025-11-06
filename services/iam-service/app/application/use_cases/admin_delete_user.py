from fastapi import HTTPException, status
from sqlalchemy import text
from ev_shared.db import session_scope
from ev_shared.config import Settings
from app.domain.ports import UserRepositoryPort

class AdminDeleteUserUseCase:
    def __init__(self, *, settings: Settings, user_repo: UserRepositoryPort):
        self.settings = settings
        self.user_repo = user_repo

    def execute(self, *, user_id: str, actor_id: str) -> None:
        with session_scope(self.settings) as s:
            deleted = self.user_repo.soft_delete(s, user_id)
            if not deleted:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            try:
                s.execute(
                    text("""
                        INSERT INTO ev_iam.evento_audit
                            (id, fecha_hora, actor_id, entidad, entidad_id, accion, metadata)
                        VALUES (UUID(), NOW(), :actor, 'usuario', :entidad_id, 'USUARIO_ELIMINAR', JSON_OBJECT('reason', 'soft_delete'))
                    """),
                    {"actor": actor_id, "entidad_id": user_id}
                )
            except Exception:
                pass
