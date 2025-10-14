# repositories patched for absolute imports
from typing import Iterable, Dict, Any
from sqlalchemy import text
from ev_shared.config import Settings
from ev_shared.db import session_scope
from app.domain.ports import ProveedoresRepository

class SqlProveedoresRepository(ProveedoresRepository):
    def __init__(self, settings: Settings):
        self.settings = settings

    def list_items(self, limit: int = 100) -> Iterable[Dict[str, Any]]:
        sql = text("""SELECT id, nombre, email, telefono, rating_prom, status FROM ev_proveedores.proveedor WHERE is_deleted=0 AND status=1 LIMIT :lim""")
        with session_scope(self.settings) as s:
            rows = [dict(row._mapping) for row in s.execute(sql, { 'lim': limit })]
        return rows
