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
    
    _users_cache = {}
    _users_cache_time = {}
    CACHE_TTL = 300  # 5 minutes

    def get_user_details(self, user_id: str, token: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el detalle de un usuario por ID.
        Requiere token de ADMIN.
        GET /iam/admin/users/{id}
        Uses in-memory cache.
        """
        import time
        now = time.time()
        
        # Check cache
        if user_id in self._users_cache:
            if now - self._users_cache_time.get(user_id, 0) < self.CACHE_TTL:
                return self._users_cache[user_id]
            else:
                # Expired
                del self._users_cache[user_id]
                del self._users_cache_time[user_id]

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
                data = resp.json()
                
                # Update cache
                self._users_cache[user_id] = data
                self._users_cache_time[user_id] = now
                
                return data
        except Exception as e:
            logger.error(f"Error al consultar IAM user {user_id}: {e}")
            return None
