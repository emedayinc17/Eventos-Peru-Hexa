# repositories patched for absolute imports
from typing import Iterable, Dict, Any
from sqlalchemy import text
from ev_shared.config import Settings
from ev_shared.db import session_scope
from app.domain.ports import ContratacionRepository

class SqlContratacionRepository(ContratacionRepository):
    def __init__(self, settings: Settings):
        self.settings = settings

    def list_items(self, limit: int = 100) -> Iterable[Dict[str, Any]]:
        sql = text("""SELECT id, cliente_id, fecha_evento, hora_inicio, status, monto_total, moneda FROM ev_contratacion.pedido_evento ORDER BY created_at DESC LIMIT :lim""")
        with session_scope(self.settings) as s:
            rows = [dict(row._mapping) for row in s.execute(sql, { 'lim': limit })]
        return rows
# === Outbox de correo (ev_mensajeria.email_outbox) ===
from datetime import datetime
from typing import Dict, Any, Iterable, List, Optional
from sqlalchemy import text
from ev_shared.db import session_scope
from ev_shared.config import Settings

class EmailOutboxSql:
    """
    Utilidades para operar con ev_mensajeria.email_outbox usando SQL crudo,
    manteniendo el estilo actual del servicio (text() + session_scope).
    """
    def __init__(self, settings: Settings):
        self.settings = settings

    def enqueue(self, to_email: str, subject: str, body: str,
                template: Optional[str] = None,
                payload_json: Optional[Dict[str, Any]] = None,
                correlation_id: Optional[str] = None,
                scheduled_at: Optional[datetime] = None,
                created_by: Optional[str] = None) -> Dict[str, Any]:
        sql = text("""
            INSERT INTO ev_mensajeria.email_outbox
                (id, to_email, subject, body, template, payload_json, status, attempts,
                 scheduled_at, correlation_id, created_at, created_by)
            VALUES (UUID(), :to_email, :subject, :body, :template, :payload_json, 0, 0,
                    :scheduled_at, :correlation_id, CURRENT_TIMESTAMP, :created_by)
        """)
        params = {
            "to_email": to_email,
            "subject": subject,
            "body": body,
            "template": template,
            "payload_json": payload_json,
            "scheduled_at": scheduled_at,
            "correlation_id": correlation_id,
            "created_by": created_by,
        }
        with session_scope(self.settings) as s:
            s.execute(sql, params)
            # devuelve lo mínimo útil para trazabilidad
            row = s.execute(text("SELECT LAST_INSERT_ID()")).first()  # no aplica a UUID: lo dejamos None
        # Como la PK es UUID generado por MySQL en SQL, recuperamos con un select ordenado
        with session_scope(self.settings) as s:
            sel = text("""
                SELECT id, to_email, subject, status, attempts, scheduled_at, correlation_id, created_at
                FROM ev_mensajeria.email_outbox
                WHERE to_email=:to_email
                ORDER BY created_at DESC
                LIMIT 1
            """)
            r = s.execute(sel, {"to_email": to_email}).mappings().first()
            return dict(r) if r else {"to_email": to_email, "subject": subject, "status": 0}

    def mark_sent(self, outbox_id: str, when: Optional[datetime] = None) -> None:
        sql = text("""
            UPDATE ev_mensajeria.email_outbox
               SET status=1, sent_at=COALESCE(:when, NOW()), last_attempt_at=COALESCE(:when, NOW())
             WHERE id=:id
             LIMIT 1
        """)
        with session_scope(self.settings) as s:
            s.execute(sql, {"id": outbox_id, "when": when})

    def mark_error(self, outbox_id: str, error_msg: str) -> None:
        sql = text("""
            UPDATE ev_mensajeria.email_outbox
               SET status=2,
                   attempts = attempts + 1,
                   last_attempt_at = NOW(),
                   error_msg = LEFT(:msg, 500)
             WHERE id=:id
             LIMIT 1
        """)
        with session_scope(self.settings) as s:
            s.execute(sql, {"id": outbox_id, "msg": error_msg})

    def pick_pending(self, limit: int = 50) -> List[Dict[str, Any]]:
        sql = text("""
            SELECT id, to_email, subject, body, template, payload_json, attempts,
                   scheduled_at, created_at, correlation_id
              FROM ev_mensajeria.email_outbox
             WHERE status IN (0,3)   -- 0=PEND, 3=REINTENTO
             ORDER BY COALESCE(scheduled_at, created_at) ASC
             LIMIT :lim
        """)
        with session_scope(self.settings) as s:
            rows = s.execute(sql, {"lim": limit}).mappings().all()
            return [dict(r) for r in rows]
