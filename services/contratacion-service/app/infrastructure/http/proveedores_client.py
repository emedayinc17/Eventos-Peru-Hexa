"""Cliente HTTP para comunicarse con Proveedores-service (internal endpoints)"""
import httpx
from typing import Dict, Any, Optional
from ev_shared.config import Settings


class ProveedoresClient:
    def __init__(self, settings: Settings):
        self.base_url = settings.PROVEEDORES_SERVICE_URL
        self.service_token = settings.INTERNAL_SERVICE_TOKEN

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Service-Token": self.service_token,
        }

    def crear_hold(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /internal/holds"""
        url = f"{self.base_url}/internal/holds"
        # Defensive: allow datetime objects in payload; convert to ISO strings
        body = dict(payload or {})
        if body.get("inicio") is not None:
            try:
                if hasattr(body["inicio"], "isoformat"):
                    body["inicio"] = body["inicio"].isoformat()
            except Exception:
                body["inicio"] = str(body["inicio"])
        if body.get("fin") is not None:
            try:
                if hasattr(body["fin"], "isoformat"):
                    body["fin"] = body["fin"].isoformat()
            except Exception:
                body["fin"] = str(body["fin"])

        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=body, headers=self._headers())
            if resp.status_code == 409:
                raise ValueError("PROVEEDOR_NO_DISPONIBLE")
            resp.raise_for_status()
            return resp.json()

    def confirmar_hold(self, hold_id: str) -> Dict[str, Any]:
        """PATCH /internal/holds/{hold_id}/confirm"""
        url = f"{self.base_url}/internal/holds/{hold_id}/confirm"
        with httpx.Client(timeout=10.0) as client:
            resp = client.patch(url, headers=self._headers())
            if resp.status_code == 410:
                raise ValueError("HOLD_EXPIRADO")
            resp.raise_for_status()
            return resp.json()

    def liberar_hold(self, hold_id: str):
        """DELETE /internal/holds/{hold_id}"""
        url = f"{self.base_url}/internal/holds/{hold_id}"
        with httpx.Client(timeout=10.0) as client:
            resp = client.delete(url, headers=self._headers())
            resp.raise_for_status()

    def obtener_hold(self, hold_id: str) -> Optional[Dict[str, Any]]:
        """GET /internal/holds/{hold_id}"""
        url = f"{self.base_url}/internal/holds/{hold_id}"
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=self._headers())
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()
