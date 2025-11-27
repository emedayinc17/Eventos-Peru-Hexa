from typing import Optional
import logging

from ev_shared.config import Settings
from ev_shared.db import session_scope

try:
    from ..infrastructure.db.repositories import MySQLHoldsRepository
except Exception:
    from services.proveedores_service.app.infrastructure.db.repositories import MySQLHoldsRepository

log = logging.getLogger("proveedores.worker")


def clear_expired_holds(settings: Optional[Settings] = None) -> int:
    """Busca holds expirados y los libera. Retorna el número de holds liberados."""
    released = 0
    settings = settings or Settings()

    repo = MySQLHoldsRepository()

    # Usar session_scope de ev_shared (contextmanager)
    try:
        with session_scope(settings) as session:
            expired = repo.list_expired_holds(session)
            log.info("Found %d expired holds", len(expired))
            for h in expired:
                try:
                    repo.liberar_hold(session, hold_id=h.id)
                    released += 1
                    log.info("Released expired hold %s", h.id)
                except Exception as e:
                    log.exception("Error releasing hold %s: %s", h.id, e)
    except Exception as e:
        log.exception("Error listing or releasing expired holds: %s", e)
    return released


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    count = clear_expired_holds()
    print(f"Released {count} expired holds")
    sys.exit(0)
