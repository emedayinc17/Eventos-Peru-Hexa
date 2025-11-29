# router.py — IAM Service (Hexagonal MVP) — Phase 4 (all use cases)
from fastapi import APIRouter, HTTPException, status, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, List
from ev_shared.config import Settings

from app.infrastructure.security.jwt_adapter import decode_token, JwtError
from app.infrastructure.persistence.repo_users_port import UserRepositoryAdapter
from app.infrastructure.roles.role_reader_adapter import RoleReaderAdapter

from app.application.use_cases.auth_login import AuthLoginUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.get_profile import GetProfileUseCase
from app.application.use_cases.admin_list_users import AdminListUsersUseCase
from app.application.use_cases.admin_get_user import AdminGetUserUseCase
from app.application.use_cases.admin_create_user import AdminCreateUserUseCase
from app.application.use_cases.admin_patch_user import AdminPatchUserUseCase
from app.application.use_cases.admin_delete_user import AdminDeleteUserUseCase
from app.application.use_cases.update_profile import UpdateProfileUseCase
from app.application.use_cases.change_password import ChangePasswordUseCase

from .schemas import (
    Health,
    LoginRequest,
    TokenResponse,
    RegisterRequest,
    UsuarioOut,
    CrearUsuarioAdminRequest,
    UpdateUsuarioRequest,
    UpdateProfileRequest,
    ChangePasswordRequest,
)

def get_settings() -> Settings:
    return Settings()

def make_login_uc(settings: Settings) -> AuthLoginUseCase:
    return AuthLoginUseCase(settings=settings, user_repo=UserRepositoryAdapter(), role_reader=RoleReaderAdapter())

def make_register_uc(settings: Settings) -> RegisterUserUseCase:
    return RegisterUserUseCase(settings=settings, user_repo=UserRepositoryAdapter(), role_reader=RoleReaderAdapter())

def make_profile_uc(settings: Settings) -> GetProfileUseCase:
    return GetProfileUseCase(settings=settings, user_repo=UserRepositoryAdapter(), role_reader=RoleReaderAdapter())

def make_update_profile_uc(settings: Settings) -> UpdateProfileUseCase:
    return UpdateProfileUseCase(settings=settings, user_repo=UserRepositoryAdapter(), role_reader=RoleReaderAdapter())

def make_change_password_uc(settings: Settings) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(settings=settings, user_repo=UserRepositoryAdapter())

def make_admin_list_uc(settings: Settings) -> AdminListUsersUseCase:
    return AdminListUsersUseCase(settings=settings, user_repo=UserRepositoryAdapter(), role_reader=RoleReaderAdapter())

def make_admin_get_uc(settings: Settings) -> AdminGetUserUseCase:
    return AdminGetUserUseCase(settings=settings, user_repo=UserRepositoryAdapter(), role_reader=RoleReaderAdapter())

def make_admin_create_uc(settings: Settings) -> AdminCreateUserUseCase:
    return AdminCreateUserUseCase(settings=settings, user_repo=UserRepositoryAdapter(), role_reader=RoleReaderAdapter())

def make_admin_patch_uc(settings: Settings) -> AdminPatchUserUseCase:
    return AdminPatchUserUseCase(settings=settings, user_repo=UserRepositoryAdapter(), role_reader=RoleReaderAdapter())

def make_admin_delete_uc(settings: Settings) -> AdminDeleteUserUseCase:
    return AdminDeleteUserUseCase(settings=settings, user_repo=UserRepositoryAdapter())

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
        payload = decode_token(token, secret=secret, algorithms=[algorithm])
        return payload
    except JwtError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    token = creds.credentials
    payload = _decode_token(settings, token)
    return {
        "id": payload.get("sub"),
        "email": payload.get("username"),
        "role": payload.get("role"),
    }

def require_role(required: str):
    req = (required or "").upper()
    def guard(user: Dict[str, Any] = Depends(get_current_user)):
        role = (user.get("role") or "").upper()
        if role != req:
            raise HTTPException(status_code=403, detail="Sin permisos")
        return user
    return guard

def build_api_router(settings: Settings) -> APIRouter:
    r = APIRouter(tags=["iam"])

    @r.get("/health", response_model=Health, operation_id="iam_health", openapi_extra={"security": []})
    def health():
        return {"status": "ok"}

    @r.post("/auth/login", response_model=TokenResponse, operation_id="iam_login", openapi_extra={"security": []})
    def login(data: LoginRequest = Body(...), settings: Settings = Depends(get_settings)):
        uc = make_login_uc(settings)
        return uc.execute(email=data.email.strip().lower(), password=data.password, ip=None)

    @r.post("/auth/register", response_model=UsuarioOut, operation_id="iam_register", openapi_extra={"security": []})
    def register(data: RegisterRequest = Body(...), settings: Settings = Depends(get_settings)):
        uc = make_register_uc(settings)
        res = uc.execute(email=data.email, password=data.password, nombre=data.nombre, telefono=data.telefono)
        return UsuarioOut(**res)

    @r.get("/me", response_model=UsuarioOut, operation_id="iam_me", openapi_extra={"security": [{"HTTPBearer": []}]})
    def me(user=Depends(get_current_user), settings: Settings = Depends(get_settings)):
        uc = make_profile_uc(settings)
        res = uc.execute(user_id=user["id"])
        return UsuarioOut(**res)

    @r.put("/auth/profile", response_model=UsuarioOut, operation_id="iam_update_profile", openapi_extra={"security": [{"HTTPBearer": []}]})
    def update_profile(data: UpdateProfileRequest = Body(...), user=Depends(get_current_user), settings: Settings = Depends(get_settings)):
        uc = make_update_profile_uc(settings)
        changes = data.model_dump(exclude_unset=True)
        res = uc.execute(user_id=user["id"], changes=changes)
        return UsuarioOut(**res)

    @r.post("/auth/change-password", status_code=status.HTTP_204_NO_CONTENT, operation_id="iam_change_password", openapi_extra={"security": [{"HTTPBearer": []}]})
    def change_password(data: ChangePasswordRequest = Body(...), user=Depends(get_current_user), settings: Settings = Depends(get_settings)):
        uc = make_change_password_uc(settings)
        uc.execute(user_id=user["id"], current_password=data.current_password, new_password=data.new_password)
        return

    @r.get("/admin/users", response_model=List[UsuarioOut], operation_id="iam_admin_list_users", openapi_extra={"security": [{"HTTPBearer": []}]})
    def admin_list_users(limit: int = 50, offset: int = 0, admin=Depends(require_role("ADMIN")), settings: Settings = Depends(get_settings)):
        uc = make_admin_list_uc(settings)
        items = uc.execute(limit=limit, offset=offset)
        return [UsuarioOut(**it) for it in items]

    @r.get("/admin/users/{id}", response_model=UsuarioOut, operation_id="iam_admin_get_user", openapi_extra={"security": [{"HTTPBearer": []}]})
    def admin_get_user(id: str, admin=Depends(require_role("ADMIN")), settings: Settings = Depends(get_settings)):
        uc = make_admin_get_uc(settings)
        res = uc.execute(user_id=id)
        return UsuarioOut(**res)

    @r.post("/admin/users", response_model=UsuarioOut, operation_id="iam_admin_create_user", openapi_extra={"security": [{"HTTPBearer": []}]})
    def admin_create_user(data: CrearUsuarioAdminRequest = Body(...), admin=Depends(require_role("ADMIN")), settings: Settings = Depends(get_settings)):
        uc = make_admin_create_uc(settings)
        res = uc.execute(email=data.email, password=data.password, nombre=data.nombre, telefono=data.telefono, role_code=data.role, actor_id=admin["id"])
        return UsuarioOut(**res)

    @r.patch("/admin/users/{id}", response_model=UsuarioOut, operation_id="iam_admin_patch_user", openapi_extra={"security": [{"HTTPBearer": []}]})
    def admin_patch_user(id: str, data: UpdateUsuarioRequest = Body(...), admin=Depends(require_role("ADMIN")), settings: Settings = Depends(get_settings)):
        changes: Dict[str, Any] = {}
        
        # Debug para ver qué datos llegan
        print(f"🎯 [PATCH ENDPOINT] Datos recibidos para usuario {id}:")
        print(f"   - nombre: {data.nombre}")
        print(f"   - telefono: {data.telefono}") 
        print(f"   - status: {data.status}")
        print(f"   - role: {data.role}")
        print(f"   - password: {'***' if data.password else 'None'}")
        
        # Mapear campos normales
        if data.nombre is not None:
            changes["nombre"] = data.nombre
        if data.telefono is not None:
            changes["telefono"] = data.telefono
        if data.status is not None:
            changes["status"] = int(data.status)
        
        # ✅ AGREGAR ESTO: Incluir password si viene
        if data.password is not None:
            changes["password"] = data.password
            print(f"🔐 [PATCH ENDPOINT] Password incluido en changes: {'***' if data.password else 'Empty'}")

        uc = make_admin_patch_uc(settings)
        res = uc.execute(user_id=id, changes=changes, new_role=data.role, actor_id=admin["id"])
        return UsuarioOut(**res)

    @r.delete("/admin/users/{id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="iam_admin_delete_user", openapi_extra={"security": [{"HTTPBearer": []}]})
    def admin_delete_user(id: str, admin=Depends(require_role("ADMIN")), settings: Settings = Depends(get_settings)):
        uc = make_admin_delete_uc(settings)
        uc.execute(user_id=id, actor_id=admin["id"])
        return

    return r
