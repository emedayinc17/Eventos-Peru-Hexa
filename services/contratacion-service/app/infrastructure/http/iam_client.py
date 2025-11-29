"""Cliente HTTP para comunicarse con IAM-service"""
import logging
import httpx
from typing import Dict, Any, Optional, List
from ev_shared.config import Settings

logger = logging.getLogger(__name__)

class IamClient:
    """Cliente para consultas al servicio de IAM"""
    
    def __init__(self, settings: Settings):
        self.base_url = settings.IAM_SERVICE_URL
        self.timeout = 10.0
    
    def get_user_details(self, user_id: str, token: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el detalle de un usuario por ID.
        Requiere token de ADMIN.
        GET /iam/admin/users/{id}
        """
        base = self.base_url.rstrip('/')
        # Normalize URL
        if base.endswith('/iam'):
            url = f"{base}/admin/users/{user_id}"
        else:
            url = f"{base}/iam/admin/users/{user_id}"
            
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"Error al consultar IAM user {user_id}: {e}")
            return None
