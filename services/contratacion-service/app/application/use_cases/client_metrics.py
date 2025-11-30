"""Use Case: Client Metrics for Contratación

Retorna conteos relevantes para un cliente (p. ej. total de pedidos del cliente)."""
from typing import Any, Dict, Optional

class ClientMetricsUseCase:
    def __init__(self, pedido_repo):
        self.pedido_repo = pedido_repo

    def execute(self, session: Any, cliente_id: str, *, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Dict[str, Any]:
        total = self.pedido_repo.count_orders_for_client(session, cliente_id, from_date=from_date, to_date=to_date)
        return {
            "my_orders": int(total)
        }
