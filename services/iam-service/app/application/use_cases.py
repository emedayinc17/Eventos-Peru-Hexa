# created by emeday 2025
from dataclasses import dataclass
from typing import Dict, Any
from ev_shared.security.jwt import verify_password, create_access_token

@dataclass
class LoginCommand:
    email: str
    password: str

class LoginUser:
    def __init__(self, repo, settings):
        self.repo = repo
        self.settings = settings

    def execute(self, cmd: LoginCommand) -> Dict[str, Any]:
        u = self.repo.find_by_email(cmd.email)
        if not u:
            return {"ok": False, "error": "Usuario o clave inválidos"}
        if u["is_deleted"] or int(u["status"]) != 1:
            return {"ok": False, "error": "Usuario inactivo"}
        if not verify_password(cmd.password, u["password_hash"]):
            return {"ok": False, "error": "Usuario o clave inválidos"}
        token = create_access_token(
            subject=u["id"],
            secret=self.settings.JWT_SECRET,
            algorithm=self.settings.JWT_ALG,
            expires_minutes=int(self.settings.JWT_EXPIRE_MIN),
            extra={"email": u["email"], "role": "user"}
        )
        return {"ok": True, "access_token": token, "token_type": "bearer"}
