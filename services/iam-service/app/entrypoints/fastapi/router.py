# router.py — IAM Service (Hexagonal MVP)
# Rutas públicas: /auth/login, /auth/register, /health
# Rutas protegidas (Bearer): /me, /admin/**
from fastapi import APIRouter, HTTPException, status, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy import text
import json

from ev_shared.config import Settings
from ev_shared.db import session_scope
from ev_shared.security.passwords import verify_password, hash_password

# DTOs (defínelos en app/entrypoints/fastapi/schemas.py)
from .schemas import (
    Health,
    LoginRequest,
    TokenResponse,
    RegisterRequest,
    UsuarioOut,
    CrearUsuarioAdminRequest,
    UpdateUsuarioRequest,
)

# ---------- Settings provider ----------
def get_settings() -> Settings:
    return Settings()

# ---------- Security (Bearer) ----------
bearer_scheme = HTTPBearer(auto_error=True)

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
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Extrae y valida Authorization: Bearer <token>.
    Devuelve un dict homogéneo: {id, email, role}
    """
    token = creds.credentials
    payload = _decode_token(settings, token)
    return {
        "id": payload.get("sub"),
        "email": payload.get("username"),
        "role": payload.get("role"),
    }

def require_role(required: str):
    """
    Uso:
      admin = Depends(require_role("ADMIN"))
    """
    req = (required or "").upper()
    def guard(user: Dict[str, Any] = Depends(get_current_user)):
        role = (user.get("role") or "").upper()
        if role != req:
            raise HTTPException(status_code=403, detail="Sin permisos")
        return user
    return guard

# ---------- Helpers de rol ----------
def _get_role_code_for_user(s, user_id: str) -> Optional[str]:
    """
    Retorna el codigo de rol principal del usuario (prioriza ADMIN si hay varios).
    """
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

def _resolve_role_id_by_code(s, code: str) -> Optional[str]:
    row = s.execute(
        text("SELECT id FROM ev_iam.rol WHERE codigo=:c AND status=1 LIMIT 1"),
        {"c": code}
    ).mappings().first()
    return row["id"] if row else None

def _set_single_role_for_user(s, user_id: str, role_code: str):
    """
    Upsert simple: borra roles previos y asigna el indicado (MVP).
    """
    role_id = _resolve_role_id_by_code(s, role_code)
    if not role_id:
        raise HTTPException(status_code=400, detail=f"Rol '{role_code}' no existe o está inactivo")
    s.execute(text("DELETE FROM ev_iam.usuario_rol WHERE usuario_id=:uid"), {"uid": user_id})
    s.execute(
        text("""
            INSERT INTO ev_iam.usuario_rol (id, usuario_id, rol_id, created_at)
            VALUES (UUID(), :uid, :rid, NOW())
        """),
        {"uid": user_id, "rid": role_id}
    )

# ---------- Auditoría ----------
def _audit(s, actor_id: Optional[str], entidad: str, entidad_id: str, accion: str, metadata: Optional[Dict[str, Any]] = None):
    """
    Inserta un evento en ev_iam.evento_audit.
    """
    s.execute(
        text("""
            INSERT INTO ev_iam.evento_audit
                (id, fecha_hora, actor_id, entidad, entidad_id, accion, metadata)
            VALUES (UUID(), NOW(), :actor, :ent, :eid, :acc, CAST(:meta AS JSON))
        """),
        {
            "actor": actor_id,
            "ent": entidad,
            "eid": entidad_id,
            "acc": accion,
            "meta": json.dumps(metadata or {})
        }
    )

# ---------- Router ----------
def build_api_router(settings: Settings) -> APIRouter:
    r = APIRouter(tags=["iam"])

    # Health (pública)
    @r.get("/health", response_model=Health, operation_id="iam_health", openapi_extra={"security": []})
    def health():
        return {"status": "ok"}

    # ---------- AUTH (público) ----------
    @r.post("/auth/login", response_model=TokenResponse, operation_id="iam_login", openapi_extra={"security": []})
    def login(data: LoginRequest = Body(...)):
        """
        Login por email + password.
        - Verifica hash (bcrypt).
        - Resuelve rol por join a rol (prioriza ADMIN).
        - Emite JWT con claims: sub, username, role, exp, iat.
        - Registra intento de login (éxito/falla) y audita LOGIN.
        """
        secret, algorithm, expires_min = _get_jwt_conf(settings)
        ip = None  # si quieres, captura IP desde un middleware/proxy

        with session_scope(settings) as s:
            u = s.execute(
                text("""
                    SELECT id, email, password_hash
                      FROM ev_iam.usuario
                     WHERE email = :e
                       AND status = 1
                       AND is_deleted = 0
                     LIMIT 1
                """),
                {"e": data.email}
            ).mappings().first()

            # fallo: credenciales
            if not u or not u.get("password_hash") or not verify_password(data.password, u["password_hash"]):
                s.execute(
                    text("""
                        INSERT INTO ev_iam.login_intento
                            (id, usuario_id, email, ip, exito)
                        VALUES (UUID(), NULL, :e, :ip, 0)
                    """),
                    {"e": data.email, "ip": ip}
                )
                # audit opcional de intento fallido (sin entidad_id real)
                _audit(s, None, "login", "00000000-0000-0000-0000-000000000000", "LOGIN_FALLIDO",
                       {"email": data.email})
                raise HTTPException(status_code=401, detail="Credenciales inválidas")

            role_code = _get_role_code_for_user(s, u["id"]) or "CLIENTE"

            # éxito: registra intento + last_login
            s.execute(
                text("""
                    INSERT INTO ev_iam.login_intento
                        (id, usuario_id, email, ip, exito)
                    VALUES (UUID(), :uid, :e, :ip, 1)
                """),
                {"uid": u["id"], "e": u["email"], "ip": ip}
            )
            s.execute(
                text("UPDATE ev_iam.usuario SET last_login=NOW() WHERE id=:id LIMIT 1"),
                {"id": u["id"]}
            )
            _audit(s, actor_id=u["id"], entidad="login", entidad_id=u["id"], accion="LOGIN",
                   metadata={"email": u["email"], "role": role_code})

        sub = str(u["id"])
        now = datetime.utcnow()
        exp = now + timedelta(minutes=expires_min)
        payload = {
            "sub": sub,
            "username": u["email"],
            "role": role_code,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "scope": "access_token",
        }
        token = jwt.encode(payload, secret, algorithm=algorithm)
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expires_min * 60,
            "role": role_code,
        }

    @r.post("/auth/register", response_model=UsuarioOut, operation_id="iam_register", openapi_extra={"security": []})
    def register(data: RegisterRequest = Body(...)):
        """
        Auto-registro de cliente:
        - Crea usuario con password hasheado.
        - Asigna rol CLIENTE por defecto.
        - Audita USUARIO_CREAR.
        """
        with session_scope(settings) as s:
            exists = s.execute(
                text("SELECT id FROM ev_iam.usuario WHERE email=:e AND is_deleted=0 LIMIT 1"),
                {"e": data.email}
            ).first()
            if exists:
                raise HTTPException(status_code=409, detail="Email ya registrado")

        pwd_hash = hash_password(data.password)

        with session_scope(settings) as s:
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

            row = s.execute(
                text("""SELECT id, email, nombre, telefono, status
                          FROM ev_iam.usuario
                         WHERE email=:e AND is_deleted=0
                         LIMIT 1"""),
                {"e": data.email}
            ).mappings().first()

            user_id = row["id"]
            _set_single_role_for_user(s, user_id, "CLIENTE")
            role_code = _get_role_code_for_user(s, user_id) or "CLIENTE"

            _audit(s, actor_id=user_id, entidad="usuario", entidad_id=user_id, accion="USUARIO_CREAR",
                   metadata={"email": row["email"], "role": role_code})

        return UsuarioOut(
            id=str(row["id"]),
            email=row["email"],
            nombre=row["nombre"],
            telefono=row["telefono"],
            role=role_code,
            status=row["status"],
        )

    # ---------- PROFILE (protegido) ----------
    @r.get(
        "/me",
        response_model=UsuarioOut,
        operation_id="iam_me",
        openapi_extra={"security": [{"HTTPBearer": []}]},
    )
    def me(user=Depends(get_current_user)):
        """
        Perfil del usuario autenticado.
        """
        with session_scope(settings) as s:
            row = s.execute(
                text("""SELECT id, email, nombre, telefono, status
                          FROM ev_iam.usuario
                         WHERE id=:id AND is_deleted=0
                         LIMIT 1"""),
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

    # ---------- ADMIN (protegido) ----------
    @r.post(
        "/admin/users",
        response_model=UsuarioOut,
        operation_id="iam_admin_create_user",
        openapi_extra={"security": [{"HTTPBearer": []}]},
    )
    def admin_create_user(
        data: CrearUsuarioAdminRequest = Body(...),
        admin=Depends(require_role("ADMIN")),
    ):
        """
        Crea usuario y le asigna un rol (ADMIN/CLIENTE). Audita USUARIO_CREAR.
        """
        with session_scope(settings) as s:
            exists = s.execute(
                text("SELECT id FROM ev_iam.usuario WHERE email=:e AND is_deleted=0 LIMIT 1"),
                {"e": data.email}
            ).first()
            if exists:
                raise HTTPException(status_code=409, detail="Email ya registrado")

        pwd_hash = hash_password(data.password)

        with session_scope(settings) as s:
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

            u = s.execute(
                text("""SELECT id, email, nombre, telefono, status
                          FROM ev_iam.usuario
                         WHERE email=:e AND is_deleted=0
                         LIMIT 1"""),
                {"e": data.email}
            ).mappings().first()

            _set_single_role_for_user(s, u["id"], data.role)
            role_code = _get_role_code_for_user(s, u["id"]) or "CLIENTE"

            _audit(s, actor_id=admin["id"], entidad="usuario", entidad_id=u["id"], accion="USUARIO_CREAR",
                   metadata={"email": u["email"], "role": role_code})

        return UsuarioOut(
            id=str(u["id"]),
            email=u["email"],
            nombre=u["nombre"],
            telefono=u["telefono"],
            role=role_code,
            status=u["status"],
        )

    @r.get(
        "/admin/users",
        response_model=List[UsuarioOut],
        operation_id="iam_admin_list_users",
        openapi_extra={"security": [{"HTTPBearer": []}]},
    )
    def admin_list_users(
        limit: int = 50,
        offset: int = 0,
        admin=Depends(require_role("ADMIN")),
    ):
        with session_scope(settings) as s:
            rows = s.execute(
                text("""
                    SELECT u.id, u.email, u.nombre, u.telefono, u.status,
                           (
                             SELECT r.codigo
                               FROM ev_iam.usuario_rol ur
                               JOIN ev_iam.rol r ON r.id = ur.rol_id AND r.status = 1
                              WHERE ur.usuario_id = u.id
                              ORDER BY CASE r.codigo WHEN 'ADMIN' THEN 1 ELSE 2 END
                              LIMIT 1
                           ) AS role
                      FROM ev_iam.usuario u
                     WHERE u.is_deleted = 0
                     ORDER BY u.created_at DESC
                     LIMIT :lim OFFSET :off
                """),
                {"lim": limit, "off": offset}
            ).mappings().all()

        return [
            UsuarioOut(
                id=str(rw["id"]),
                email=rw["email"],
                nombre=rw["nombre"],
                telefono=rw["telefono"],
                role=rw["role"] or "CLIENTE",
                status=rw["status"],
            )
            for rw in rows
        ]

    @r.get(
        "/admin/users/{id}",
        response_model=UsuarioOut,
        operation_id="iam_admin_get_user",
        openapi_extra={"security": [{"HTTPBearer": []}]},
    )
    def admin_get_user(id: str, admin=Depends(require_role("ADMIN"))):
        with session_scope(settings) as s:
            row = s.execute(
                text("""SELECT id, email, nombre, telefono, status
                          FROM ev_iam.usuario
                         WHERE id=:id AND is_deleted=0
                         LIMIT 1"""),
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

    @r.patch(
        "/admin/users/{id}",
        response_model=UsuarioOut,
        operation_id="iam_admin_patch_user",
        openapi_extra={"security": [{"HTTPBearer": []}]},
    )
    def admin_patch_user(
        id: str,
        data: UpdateUsuarioRequest = Body(...),
        admin=Depends(require_role("ADMIN")),
    ):
        """
        Actualiza campos parciales y/o rol. Audita USUARIO_ACTUALIZAR con metadata de cambios.
        """
        sets = []
        params: Dict[str, Any] = {"id": id}
        changed: Dict[str, Any] = {}

        if data.nombre is not None:
            sets.append("nombre=:nombre")
            params["nombre"] = data.nombre
            changed["nombre"] = data.nombre
        if data.telefono is not None:
            sets.append("telefono=:telefono")
            params["telefono"] = data.telefono
            changed["telefono"] = data.telefono
        if data.status is not None:
            sets.append("status=:status")
            params["status"] = int(data.status)
            changed["status"] = int(data.status)

        with session_scope(settings) as s:
            if sets:
                sql = text(f"""
                    UPDATE ev_iam.usuario
                       SET {', '.join(sets)}, updated_at=NOW()
                     WHERE id=:id AND is_deleted=0
                     LIMIT 1
                """)
                res = s.execute(sql, params)
                if res.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Usuario no encontrado")

            role_changed = False
            if data.role is not None:
                _set_single_role_for_user(s, id, data.role)
                changed["role"] = data.role
                role_changed = True

            row = s.execute(
                text("""SELECT id, email, nombre, telefono, status
                          FROM ev_iam.usuario
                         WHERE id=:id AND is_deleted=0
                         LIMIT 1"""),
                {"id": id}
            ).mappings().first()
            if not row:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            role_code = _get_role_code_for_user(s, row["id"]) or "CLIENTE"

            if changed or role_changed:
                _audit(s, actor_id=admin["id"], entidad="usuario", entidad_id=id, accion="USUARIO_ACTUALIZAR",
                       metadata=changed)

        return UsuarioOut(
            id=str(row["id"]),
            email=row["email"],
            nombre=row["nombre"],
            telefono=row["telefono"],
            role=role_code,
            status=row["status"],
        )

    @r.delete(
        "/admin/users/{id}",
        status_code=status.HTTP_204_NO_CONTENT,
        operation_id="iam_admin_delete_user",
        openapi_extra={"security": [{"HTTPBearer": []}]},
    )
    def admin_delete_user(id: str, admin=Depends(require_role("ADMIN"))):
        """
        Soft-delete: is_deleted=1 y status=0. Audita USUARIO_ELIMINAR.
        """
        with session_scope(settings) as s:
            res = s.execute(
                text("""
                    UPDATE ev_iam.usuario
                       SET is_deleted=1,
                           status=0,
                           updated_at=NOW()
                     WHERE id=:id AND is_deleted=0
                     LIMIT 1
                """),
                {"id": id}
            )
            if res.rowcount == 0:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            _audit(s, actor_id=admin["id"], entidad="usuario", entidad_id=id, accion="USUARIO_ELIMINAR",
                   metadata={"reason": "soft_delete"})

        return

    return r
