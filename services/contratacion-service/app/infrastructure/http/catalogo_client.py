"""Cliente HTTP para comunicarse con Catálogo-service"""
import logging
import httpx
from typing import Dict, Any, Optional
from ev_shared.config import Settings

logger = logging.getLogger(__name__)


class CatalogoClient:
    """Cliente para consultas al servicio de Catálogo"""
    
    def __init__(self, settings: Settings):
        self.base_url = settings.CATALOGO_SERVICE_URL
        self.timeout = 10.0
    
    def get_paquete_detalle(self, paquete_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el detalle completo de un paquete incluyendo sus items y precios.
        GET /catalogo/v1/catalogo/paquetes/{paquete_id}
        """
        base = self.base_url.rstrip('/')
        # base may already include the '/catalogo' prefix (legacy). Normalize to avoid duplication.
        # Correct endpoints exposed by catalogo-service are either:
        #  - <base>/v1/paquetes/{id}   when base already includes '/catalogo'
        #  - <base>/catalogo/v1/paquetes/{id} when base is root host:port
        if base.endswith('/catalogo'):
            url = f"{base}/v1/paquetes/{paquete_id}"
        else:
            url = f"{base}/catalogo/v1/paquetes/{paquete_id}"
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url)
                logger.debug("CatalogoClient GET %s -> %s", url, resp.status_code)
                if resp.status_code == 404:
                    logger.debug("CatalogoClient: paquete %s no encontrado (404)", paquete_id)
                    return None
                # If other non-success, log body at debug level for troubleshooting
                if resp.status_code >= 400:
                    try:
                        body = resp.text
                    except Exception:
                        body = '<unreadable body>'
                    logger.debug("CatalogoClient error body: %s", body)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"Error al consultar catálogo: {str(e)}")
    
    def get_opcion_servicio_precio(self, opcion_servicio_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el precio vigente de una opción de servicio.
        Consulta directamente la vista v_opcion_con_precio_vigente de la BD
        y hace join con servicio para obtener el nombre del servicio.
        """
        from sqlalchemy import text
        from ev_shared.db import session_scope
        from ev_shared.config import Settings
        
        settings = Settings()
        
        try:
            with session_scope(settings) as db_session:
                # Join view with servicio table to get service name
                # View columns: opcion_id, servicio_id, nombre, detalles, moneda, monto
                result = db_session.execute(
                    text("""
                        SELECT 
                            v.opcion_id,
                            v.nombre AS opcion_nombre,
                            v.servicio_id,
                            s.nombre AS servicio_nombre,
                            s.tipo_evento_id,
                            v.moneda,
                            v.monto
                        FROM ev_catalogo.v_opcion_con_precio_vigente v
                        JOIN ev_catalogo.servicio s ON s.id = v.servicio_id
                        WHERE v.opcion_id = :opcion_id
                        LIMIT 1
                    """),
                    {"opcion_id": opcion_servicio_id}
                ).mappings().first()
                
                if not result:
                    return None
                
                return {
                    "opcion_servicio_id": result["opcion_id"],
                    "nombre": result["opcion_nombre"],
                    "servicio_id": result["servicio_id"],
                    "nombre_servicio": result["servicio_nombre"],
                    "servicio_nombre": result["servicio_nombre"],
                    "tipo_evento_id": result["tipo_evento_id"],
                    "moneda": result["moneda"],
                    "monto": float(result["monto"]),
                    "precio": float(result["monto"]),
                }
        except Exception as e:
            raise RuntimeError(f"Error al consultar precio de opción: {str(e)}")
    
    # Compatibilidad con código legado / use-cases
    def obtener_precio_opcion(self, opcion_servicio_id: str) -> Optional[Dict[str, Any]]:
        """
        Wrapper para mantener compatibilidad con use-cases que llaman
        a `obtener_precio_opcion`. Delegates to `get_opcion_servicio_precio`.
        """
        return self.get_opcion_servicio_precio(opcion_servicio_id)
    
    
    def get_tipo_evento(self, tipo_evento_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un tipo de evento.
        GET /catalogo/v1/tipos (or /v1/tipos if base already contains /catalogo)
        """
        base = self.base_url.rstrip('/')
        if base.endswith('/catalogo'):
            url = f"{base}/v1/tipos"
        else:
            url = f"{base}/catalogo/v1/tipos"
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url)
                resp.raise_for_status()
                tipos = resp.json()
                
                # Buscar el tipo específico
                for tipo in tipos:
                    if tipo.get("id") == tipo_evento_id:
                        return tipo
                
                return None
        except httpx.HTTPError as e:
            raise RuntimeError(f"Error al consultar catálogo: {str(e)}")
