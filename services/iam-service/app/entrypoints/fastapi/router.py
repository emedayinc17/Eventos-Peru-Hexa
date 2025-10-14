# router.py — IAM Service (Hexagonal MVP, DTOs en schemas.py)
from fastapi import APIRouter, HTTPException, status, Depends, Header, Body
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy import text

from ev_shared.config import Settings
from ev_shared.db import session_scope
from ev_shared.security.passwords import verify_password, hash_password

# DTOs
from .schemas import (
    Health,
    LoginRequest,
    TokenResponse,
    RegisterRequest,
    UsuarioOut,
    CrearUsuarioAdminRequest,
    UpdateUsuarioRequest,
)

# -------- Provider para Settings --------
def get_settings() -> Settings:
    return Settings()

# -------- Helpers de rol (acorde al schema normalizado) --------
def _get_role_code_for_user(s, user_id: str) -> Optional[str]:
    """
    Devuelve el código de rol principal del usuario (ej. 'ADMIN', 'CLIENTE').
    Prioriza ADMIN sobre otros si hay múltiples roles.
    """
    row = s.execute(
        text("""
            SELECT r.codigo AS role
            FROM ev_iam.usuario_rol ur
            JOIN ev_iam.rol r ON r.id = ur.rol_id
            WHERE ur.usuario_id = :uid AND r.status = 1
            ORDER BY CASE r.codigo WHEN 'ADMIN' THEN 1 ELSE 2 END
            LIMIT 1
        """),
        {"uid": user_id}
    ).mappings().first()
    return row["role"] if row else None

def _resolve_role_id_by_code(s, code: str) -> Optional[str]:
    """
    Retorna el ID de rol para un código dado (p. ej. 'ADMIN' / 'CLIENTE').
    """
    row = s.execute(
        text("SELECT id FROM ev_iam.rol WHERE codigo = :c AND status = 1 LIMIT 1"),
        {"c": code}
    ).mappings().first()
    return row["id"] if row else None

def _set_single_role_for_user(s, user_id: str, role_code: str):
    """
    Reemplaza (upsert) la relación usuario_rol del usuario por el rol indicado.
    """
    rol_id = _resolve_role_id_by_code(s, role_code)
    if not rol_id:
        raise HTTPException(status_code=400, detail=f"Rol '{role_code}' no existe o está inactivo")
    # Elimina roles previos y asigna uno único (MVP)
    s.execute(text("DELETE FROM ev_iam.usuario_rol WHERE usuario_id = :uid"), {"uid": user_id})
    s.execute(
        text("""
            INSERT INTO ev_iam.usuario_rol (id, usuario_id, rol_id)
            VALUES (UUID(), :uid, :rid)
        """),
        {"uid": user_id, "rid": rol_id}
    )

# -------- JWT utils --------
def _get_jwt_conf(settings: Settings):
    secret = getattr(settings, "JWT_SECRET", None)
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET no configurado")
    algorithm = getattr(settings, "JWT_ALG", getattr(settings, "JWT_ALGORITHM", "HS256"))
    expires_min = int(getattr(settings, "JWT_EXPIRES_MIN", 60))
    return secret, algorithm, expires_min

def _decode_token(settings: Settings, token: str) -> Dict[str, Any]:
    secret, algorithm, _ = _get_jwt_conf(settings)
    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

def get_current_user(
    authorization: Optional[str] = Header(None),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Falta Authorization Bearer")
    token = authorization.split(" ", 1)[1]
    payload = _decode_token(settings, token)
    return {
        "id": payload.get("sub"),
        "email": payload.get("username"),
        "role": payload.get("role"),
    }

def require_role(required: str):
    def role_guard(user: Dict[str, Any] = Depends(get_current_user)):
        if user.get("role") != required:
            raise HTTPException(status_code=403, detail="Sin permisos")
        return user
    return role_guard

# -------- Router --------
def build_api_router(settings: Settings) -> APIRouter:
    r = APIRouter(tags=["iam"])

    # Health (pública)
    @r.get("/health", response_model=Health, operation_id="iam_router_health")
    def health():
        return {"status": "ok"}

    # AUTH: login (público)
    @r.post("/auth/login", response_model=TokenResponse, operation_id="iam_login")
    def login(data: LoginRequest = Body(...)):
        """
        Login por email + password_hash.
        Rol se obtiene vía join usuario_rol -> rol (prioriza ADMIN).
        """
        secret, algorithm, expires_min = _get_jwt_conf(settings)
        with session_scope(settings) as s:
            u = s.execute(
                text("""
                    SELECT id, email, password_hash
                    FROM ev_iam.usuario
                    WHERE email = :e AND status = 1 AND is_deleted = 0
                    LIMIT 1
                """),
                {"e": data.email}
            ).mappings().first()

            if not u or not u.get("password_hash"):
                raise HTTPException(status_code=401, detail="Credenciales inválidas")
            if not verify_password(data.password, u["password_hash"]):
                raise HTTPException(status_code=401, detail="Credenciales inválidas")

            role_code = _get_role_code_for_user(s, u["id"]) or "CLIENTE"

        sub = str(u["id"])
        expire = datetime.utcnow() + timedelta(minutes=expires_min)
        payload = {
            "sub": sub,
            "username": u["email"],  # compatibilidad downstream
            "role": role_code,       # claim de rol (MVP)
            "exp": expire,
            "iat": datetime.utcnow(),
            "scope": "access_token",
        }
        token = jwt.encode(payload, secret, algorithm=algorithm)
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expires_min * 60,
            "role": role_code,
        }

    # AUTH: self-register (público) → crea cliente
    @r.post("/auth/register", response_model=UsuarioOut, operation_id="iam_register")
    def register(data: RegisterRequest = Body(...)):
        with session_scope(settings) as s:
            exists = s.execute(
                text("SELECT id FROM ev_iam.usuario WHERE email=:e AND is_deleted=0 LIMIT 1"),
                {"e": data.email}
            ).first()
            if exists:
                raise HTTPException(status_code=409, detail="Email ya registrado")

        pwd_hash = hash_password(data.password)
        with session_scope(settings) as s:
            # crea usuario
            s.execute(text("""
                INSERT INTO ev_iam.usuario
                    (id, email, password_hash, nombre, telefono, status, is_deleted, created_at)
                VALUES (UUID(), :email, :ph, :nombre, :telefono, 1, 0, NOW())
            """), {
                "email": data.email,
                "ph": pwd_hash,
                "nombre": data.nombre,
                "telefono": data.telefono
            })
            # obtiene id
            row = s.execute(
                text("""SELECT id, email, nombre, telefono, status
                        FROM ev_iam.usuario WHERE email=:e AND is_deleted=0 LIMIT 1"""),
                {"e": data.email}
            ).mappings().first()
            user_id = row["id"]

            # asigna rol CLIENTE por defecto
            _set_single_role_for_user(s, user_id, "CLIENTE")
            role_code = _get_role_code_for_user(s, user_id) or "CLIENTE"

        return UsuarioOut(
            id=str(row["id"]),
            email=row["email"],
            nombre=row["nombre"],
            telefono=row["telefono"],
            role=role_code,
            status=row["status"],
        )

    # PROFILE: /me (protegido)
    @r.get("/me", response_model=UsuarioOut, operation_id="iam_me")
    def me(user=Depends(get_current_user)):
        with session_scope(settings) as s:
            row = s.execute(
                text("""SELECT id, email, nombre, telefono, status
                        FROM ev_iam.usuario WHERE id=:id AND is_deleted=0 LIMIT 1"""),
                {"id": user["id"]}
            ).mappings().first()
            if not row:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            role_code = _get_role_code_for_user(s, row["id"]) or "CLIENTE"

        return UsuarioOut(
            id=str(row["id"]),
            email=row["email"],
            nombre=row["nombre"],
            telefono=row["telefono"],
            role=role_code,
            status=row["status"],
        )

    # ---------- ADMIN ----------
    # Crear usuario (ADMIN)  -> POST /admin/users
    @r.post("/admin/users", response_model=UsuarioOut, operation_id="iam_admin_create_user")
    def admin_create_user(
        data: CrearUsuarioAdminRequest = Body(...),
        admin=Depends(require_role("ADMIN"))
    ):
        # valida duplicidad email
        with session_scope(settings) as s:
            exists = s.execute(
                text("SELECT id FROM ev_iam.usuario WHERE email=:e AND is_deleted=0 LIMIT 1"),
                {"e": data.email}
            ).first()
            if exists:
                raise HTTPException(status_code=409, detail="Email ya registrado")

        pwd_hash = hash_password(data.password)
        with session_scope(settings) as s:
            # crea usuario
            s.execute(text("""
                INSERT INTO ev_iam.usuario
                    (id, email, password_hash, nombre, telefono, status, is_deleted, created_at)
                VALUES (UUID(), :email, :ph, :nombre, :telefono, 1, 0, NOW())
            """), {
                "email": data.email,
                "ph": pwd_hash,
                "nombre": data.nombre,
                "telefono": data.telefono,
            })
            # obtiene id
            u = s.execute(
                text("""SELECT id, email, nombre, telefono, status
                        FROM ev_iam.usuario WHERE email=:e AND is_deleted=0 LIMIT 1"""),
                {"e": data.email}
            ).mappings().first()
            user_id = u["id"]

            # asigna rol indicado (ADMIN/CLIENTE)
            _set_single_role_for_user(s, user_id, data.role)
            role_code = _get_role_code_for_user(s, user_id) or "CLIENTE"

        return UsuarioOut(
            id=str(u["id"]),
            email=u["email"],
            nombre=u["nombre"],
            telefono=u["telefono"],
            role=role_code,
            status=u["status"],
        )

    # Listar usuarios (ADMIN) con rol (join)
    @r.get("/admin/users", response_model=List[UsuarioOut], operation_id="iam_admin_list_users")
    def admin_list_users(
        limit: int = 50, offset: int = 0,
        admin=Depends(require_role("ADMIN"))
    ):
        with session_scope(settings) as s:
            rows = s.execute(
                text("""
                    SELECT u.id, u.email, u.nombre, u.telefono, u.status,
                           (
                             SELECT r.codigo
                             FROM ev_iam.usuario_rol ur
                             JOIN ev_iam.rol r ON r.id = ur.rol_id AND r.status=1
                             WHERE ur.usuario_id = u.id
                             ORDER BY CASE r.codigo WHEN 'ADMIN' THEN 1 ELSE 2 END
                             LIMIT 1
                           ) AS role
                    FROM ev_iam.usuario u
                    WHERE u.is_deleted=0
                    ORDER BY u.created_at DESC
                    LIMIT :lim OFFSET :off
                """),
                {"lim": limit, "off": offset}
            ).mappings().all()

        return [
            UsuarioOut(
                id=str(r["id"]),
                email=r["email"],
                nombre=r["nombre"],
                telefono=r["telefono"],
                role=r["role"] or "CLIENTE",
                status=r["status"],
            )
            for r in rows
        ]

    # Obtener usuario (ADMIN) con rol
    @r.get("/admin/users/{id}", response_model=UsuarioOut, operation_id="iam_admin_get_user")
    def admin_get_user(id: str, admin=Depends(require_role("ADMIN"))):
        with session_scope(settings) as s:
            row = s.execute(
                text("""SELECT id, email, nombre, telefono, status
                        FROM ev_iam.usuario WHERE id=:id AND is_deleted=0 LIMIT 1"""),
                {"id": id}
            ).mappings().first()
            if not row:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            role_code = _get_role_code_for_user(s, row["id"]) or "CLIENTE"

        return UsuarioOut(
            id=str(row["id"]),
            email=row["email"],
            nombre=row["nombre"],
            telefono=row["telefono"],
            role=role_code,
            status=row["status"],
        )

    # Actualizar usuario (parcial) + (opcional) cambiar rol
    @r.patch("/admin/users/{id}", response_model=UsuarioOut, operation_id="iam_admin_patch_user")
    def admin_patch_user(
        id: str,
        data: UpdateUsuarioRequest = Body(...),
        admin=Depends(require_role("ADMIN"))
    ):
        sets = []
        params: Dict[str, Any] = {"id": id}
        if data.nombre is not None:
            sets.append("nombre=:nombre")
            params["nombre"] = data.nombre
        if data.telefono is not None:
            sets.append("telefono=:telefono")
            params["telefono"] = data.telefono
        if data.status is not None:
            sets.append("status=:status")
            params["status"] = int(data.status)

        with session_scope(settings) as s:
            if sets:
                sql = text(f"UPDATE ev_iam.usuario SET {', '.join(sets)} WHERE id=:id AND is_deleted=0 LIMIT 1")
                res = s.execute(sql, params)
                if res.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Usuario no encontrado")

            if data.role is not None:
                _set_single_role_for_user(s, id, data.role)

            row = s.execute(
                text("""SELECT id, email, nombre, telefono, status
                        FROM ev_iam.usuario WHERE id=:id AND is_deleted=0 LIMIT 1"""),
                {"id": id}
            ).mappings().first()
            if not row:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            role_code = _get_role_code_for_user(s, row["id"]) or "CLIENTE"

        return UsuarioOut(
            id=str(row["id"]),
            email=row["email"],
            nombre=row["nombre"],
            telefono=row["telefono"],
            role=role_code,
            status=row["status"],
        )

    # Eliminar (soft-delete)
    @r.delete("/admin/users/{id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="iam_admin_delete_user")
    def admin_delete_user(id: str, admin=Depends(require_role("ADMIN"))):
        with session_scope(settings) as s:
            res = s.execute(
                text("UPDATE ev_iam.usuario SET is_deleted=1 WHERE id=:id AND is_deleted=0 LIMIT 1"),
                {"id": id}
            )
            if res.rowcount == 0:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return

    return r
