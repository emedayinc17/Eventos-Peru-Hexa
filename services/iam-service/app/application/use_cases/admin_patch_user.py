from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy import text
import json
from ev_shared.db import session_scope
from ev_shared.config import Settings
from app.domain.ports import UserRepositoryPort, RoleReaderPort
# AGREGAR ESTA IMPORTACIÓN
from app.infrastructure.security.password_adapter import hash_password

class AdminPatchUserUseCase:
    def __init__(self, *, settings: Settings, user_repo: UserRepositoryPort, role_reader: RoleReaderPort):
        self.settings = settings
        self.user_repo = user_repo
        self.role_reader = role_reader

    def execute(self, *, user_id: str, changes: Dict[str, Any], new_role: Optional[str], actor_id: str) -> Dict[str, Any]:
        changed: Dict[str, Any] = {}

        with session_scope(self.settings) as s:
            # 1. Manejar el password por separado si está presente Y NO ESTÁ VACÍO
            password_change = None
            if changes and 'password' in changes:
                password_change = changes.pop('password')
                
                # Solo procesar si el password NO está vacío
                if password_change and password_change.strip():
                    if len(password_change) >= 6:
                        # ✅ USAR hash_password IGUAL QUE EN REGISTER
                        hashed_password = hash_password(password_change)
                        
                        # Actualizar password en la base de datos
                        result = s.execute(
                            text("""
                                UPDATE ev_iam.usuario 
                                SET password_hash = :password 
                                WHERE id = :user_id
                            """),
                            {"password": hashed_password, "user_id": user_id}
                        )
                        
                        if result.rowcount > 0:
                            changed['password'] = '***'
                        else:
                            raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Usuario no encontrado"
                            )
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="La contraseña debe tener al menos 6 caracteres"
                        )
                # Si password_change está vacío, NO HACER NADA

            # 2. Manejar los demás campos
            if changes:
                updated = self.user_repo.update_user_fields(s, user_id, changes)
                if not updated:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
                changed.update(changes)

            # 3. Manejar cambio de rol
            role_changed = False
            if new_role is not None:
                self.role_reader.set_single_role_for_user(s, user_id, new_role)
                changed["role"] = new_role
                role_changed = True

            # 4. Obtener usuario actualizado
            row = self.user_repo.get_by_id(s, user_id)
            if not row:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
            role_code = self.role_reader.get_role_code_for_user(s, row["id"]) or "CLIENTE"

            # 5. Auditoría
            if changed or role_changed:
                try:
                    s.execute(
                        text("""
                            INSERT INTO ev_iam.evento_audit
                                (id, fecha_hora, actor_id, entidad, entidad_id, accion, metadata)
                            VALUES (UUID(), NOW(), :actor, 'usuario', :entidad_id, 'USUARIO_ACTUALIZAR', CAST(:meta AS JSON))
                        """),
                        {"actor": actor_id, "entidad_id": user_id, "meta": json.dumps(changed)}
                    )
                except Exception:
                    pass

        return {
            "id": str(row["id"]),
            "email": row["email"],
            "nombre": row["nombre"],
            "telefono": row["telefono"],
            "role": role_code,
            "status": row["status"],
        }