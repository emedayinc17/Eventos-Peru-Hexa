# app/infrastructure/persistence/repo_users.py
from typing import Optional, Any, Dict, List
from sqlalchemy import text

USERS_TABLE = "ev_iam.usuario"

def get_by_email(s, email: str) -> Optional[Dict[str, Any]]:
    # Sin filtrar status: útil para validaciones generales
    q = text(f"""
        SELECT id, email, password_hash, nombre, telefono, status, is_deleted, created_at, updated_at, last_login
          FROM {USERS_TABLE}
         WHERE email = :e AND is_deleted = 0
         LIMIT 1
    """)
    row = s.execute(q, {"e": email}).mappings().first()
    return dict(row) if row else None

def get_active_by_email(s, email: str) -> Optional[Dict[str, Any]]:
    # Para login: exige status=1 e is_deleted=0 (como tu SQL original del router)
    q = text(f"""
        SELECT id, email, password_hash, nombre, telefono, status, is_deleted, created_at, updated_at, last_login
          FROM {USERS_TABLE}
         WHERE email = :e AND status = 1 AND is_deleted = 0
         LIMIT 1
    """)
    row = s.execute(q, {"e": email}).mappings().first()
    return dict(row) if row else None

def get_by_id(s, user_id: str) -> Optional[Dict[str, Any]]:
    q = text(f"""
        SELECT id, email, password_hash, nombre, telefono, status, is_deleted, created_at, updated_at, last_login
          FROM {USERS_TABLE}
         WHERE id = :id AND is_deleted = 0
         LIMIT 1
    """)
    row = s.execute(q, {"id": user_id}).mappings().first()
    return dict(row) if row else None

def list_users(s, *, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    q = text(f"""
        SELECT u.id, u.email, u.nombre, u.telefono, u.status
          FROM {USERS_TABLE} u
         WHERE u.is_deleted = 0
         ORDER BY u.created_at DESC
         LIMIT :lim OFFSET :off
    """)
    rows = s.execute(q, {"lim": limit, "off": offset}).mappings().all()
    return [dict(r) for r in rows]

def create_user(s, *, email: str, password_hash: str, nombre: Optional[str], telefono: Optional[str]) -> str:
    q = text(f"""
        INSERT INTO {USERS_TABLE}
            (id, email, password_hash, nombre, telefono, status, is_deleted, created_at)
        VALUES (UUID(), :email, :ph, :nombre, :telefono, 1, 0, NOW())
    """)
    s.execute(q, {"email": email, "ph": password_hash, "nombre": nombre, "telefono": telefono})
    row = s.execute(
        text(f"SELECT id FROM {USERS_TABLE} WHERE email=:e AND is_deleted=0 LIMIT 1"),
        {"e": email}
    ).mappings().first()
    return str(row["id"])

def touch_last_login(s, user_id: str) -> None:
    q = text(f"UPDATE {USERS_TABLE} SET last_login=NOW() WHERE id=:id LIMIT 1")
    s.execute(q, {"id": user_id})

def update_user_fields(s, user_id: str, changes: Dict[str, Any]) -> int:
    if not changes:
        return 0
    sets = ", ".join([f"{k} = :{k}" for k in changes.keys()])
    q = text(f"""
        UPDATE {USERS_TABLE}
           SET {sets}, updated_at = NOW()
         WHERE id = :id AND is_deleted = 0
         LIMIT 1
    """)
    params = dict(changes)
    params["id"] = user_id
    res = s.execute(q, params)
    return res.rowcount or 0

def soft_delete(s, user_id: str) -> int:
    q = text(f"""
        UPDATE {USERS_TABLE}
           SET is_deleted = 1,
               status = 0,
               updated_at = NOW()
         WHERE id = :id AND is_deleted = 0
         LIMIT 1
    """)
    res = s.execute(q, {"id": user_id})
    return res.rowcount or 0
