from typing import Optional
from sqlalchemy import text
from fastapi import HTTPException

class RoleReaderAdapter:
    def get_role_code_for_user(self, s, user_id: str) -> Optional[str]:
        row = s.execute(
            text("""
                SELECT r.codigo AS role
                  FROM ev_iam.usuario_rol ur
                  JOIN ev_iam.rol r ON r.id = ur.rol_id
                 WHERE ur.usuario_id = :uid
                   AND r.status = 1
                 ORDER BY CASE r.codigo WHEN 'ADMIN' THEN 1 ELSE 2 END
                 LIMIT 1
            """),
            {"uid": user_id}
        ).mappings().first()
        return row["role"] if row else None

    def set_single_role_for_user(self, s, user_id: str, role_code: str) -> None:
        rid_row = s.execute(
            text("SELECT id FROM ev_iam.rol WHERE codigo=:c AND status=1 LIMIT 1"),
            {"c": role_code}
        ).mappings().first()
        if not rid_row:
            raise HTTPException(status_code=400, detail=f"Rol '{role_code}' no existe o está inactivo")
        role_id = rid_row["id"]
        s.execute(text("DELETE FROM ev_iam.usuario_rol WHERE usuario_id=:uid"), {"uid": user_id})
        s.execute(
            text("""
                INSERT INTO ev_iam.usuario_rol (id, usuario_id, rol_id, created_at)
                VALUES (UUID(), :uid, :rid, NOW())
            """),
            {"uid": user_id, "rid": role_id}
        )
