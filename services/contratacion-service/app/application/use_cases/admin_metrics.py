"""Use Case: Admin Metrics for Contratación

Retorna conteos agregados (total orders y por estado)."""
from typing import Any, Dict, Optional

class AdminMetricsUseCase:
    def __init__(self, pedido_repo):
        self.pedido_repo = pedido_repo

    def execute(self, session: Any, *, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Dict[str, Any]:
        total = self.pedido_repo.count_total_orders(session, from_date=from_date, to_date=to_date)
        by_status = self.pedido_repo.count_orders_by_status(session, from_date=from_date, to_date=to_date)
        return {
            "orders": int(total),
            "orders_by_status": by_status,
        }
