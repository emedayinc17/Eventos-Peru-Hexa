"""Cliente HTTP para comunicarse con Catálogo-service"""
import httpx
from typing import Dict, Any, Optional
from ev_shared.config import Settings


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
        url = f"{self.base_url}/catalogo/v1/catalogo/paquetes/{paquete_id}"
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url)
                if resp.status_code == 404:
                    return None
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
    
    
    def get_tipo_evento(self, tipo_evento_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un tipo de evento.
        GET /catalogo/v1/catalogo/tipos-evento
        """
        url = f"{self.base_url}/catalogo/v1/catalogo/tipos"
        
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
