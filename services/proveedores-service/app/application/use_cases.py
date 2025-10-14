# created by emeday 2025
"""
Application Layer - Use Cases
Proveedores Service
Arquitectura Hexagonal - Application Layer
"""
from typing import Dict, Any, List
from sqlalchemy import text
from ev_shared import Settings, session_scope

class ProveedoresUseCases:
    """
    Casos de uso del dominio de Proveedores
    Orquesta la lógica de negocio sin depender de detalles de infraestructura
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def listar_proveedores(
        self, 
        limit: int = 100, 
        offset: int = 0,
        status: int = None
    ) -> Dict[str, Any]:
        """
        UC-PROV-001: Listar Proveedores
        Retorna la lista de proveedores con filtros opcionales
        """
        sql_base = """
            SELECT 
                id, nombre, email, telefono, 
                rating_prom, total_reviews, status, 
                created_at, updated_at
            FROM ev_proveedores.proveedor 
            WHERE is_deleted=0
        """
        
        params = {"lim": limit, "off": offset}
        
        if status is not None:
            sql_base += " AND status=:status"
            params["status"] = status
        
        sql_base += " ORDER BY nombre LIMIT :lim OFFSET :off"
        
        with session_scope(self.settings) as session:
            result = session.execute(text(sql_base), params)
            items = [dict(row._mapping) for row in result]
        
        return {
            "items": items,
            "total": len(items),
            "limit": limit,
            "offset": offset
        }
    
    def obtener_proveedor(self, proveedor_id: int) -> Dict[str, Any]:
        """
        UC-PROV-002: Obtener Proveedor por ID
        Retorna los detalles completos de un proveedor
        """
        sql = text("""
            SELECT 
                id, nombre, email, telefono, 
                direccion, ciudad, pais,
                rating_prom, total_reviews,
                status, created_at, updated_at
            FROM ev_proveedores.proveedor 
            WHERE id=:pid AND is_deleted=0
        """)
        
        with session_scope(self.settings) as session:
            result = session.execute(sql, {"pid": proveedor_id})
            row = result.mappings().first()
            
            if not row:
                raise ValueError(f"Proveedor {proveedor_id} no encontrado")
            
            return dict(row)
    
    def listar_servicios_proveedor(
        self, 
        proveedor_id: int, 
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        UC-PROV-003: Listar Servicios de un Proveedor
        Retorna todos los servicios ofrecidos por un proveedor específico
        """
        sql = text("""
            SELECT 
                s.id, s.nombre, s.descripcion, 
                s.precio_base, s.moneda, 
                s.disponibilidad, s.status,
                s.created_at, s.updated_at
            FROM ev_proveedores.servicio_proveedor s
            WHERE s.proveedor_id=:pid 
              AND s.is_deleted=0 
              AND s.status=1
            ORDER BY s.nombre
            LIMIT :lim
        """)
        
        with session_scope(self.settings) as session:
            result = session.execute(sql, {"pid": proveedor_id, "lim": limit})
            servicios = [dict(row._mapping) for row in result]
        
        return {
            "proveedor_id": proveedor_id,
            "servicios": servicios,
            "total": len(servicios)
        }
    
    def buscar_proveedores_por_servicio(
        self, 
        servicio_nombre: str, 
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        UC-PROV-004: Buscar Proveedores por Servicio
        Encuentra proveedores que ofrecen un servicio específico
        """
        sql = text("""
            SELECT DISTINCT
                p.id, p.nombre, p.email, p.telefono,
                p.rating_prom, p.ciudad
            FROM ev_proveedores.proveedor p
            JOIN ev_proveedores.servicio_proveedor s ON p.id = s.proveedor_id
            WHERE p.is_deleted=0 
              AND p.status=1
              AND s.is_deleted=0
              AND s.status=1
              AND s.nombre LIKE :servicio
            ORDER BY p.rating_prom DESC, p.nombre
            LIMIT :lim
        """)
        
        with session_scope(self.settings) as session:
            result = session.execute(
                sql, 
                {"servicio": f"%{servicio_nombre}%", "lim": limit}
            )
            items = [dict(row._mapping) for row in result]
        
        return {
            "servicio_buscado": servicio_nombre,
            "proveedores": items,
            "total": len(items)
        }
    
    def obtener_proveedores_top_rated(self, limit: int = 10) -> Dict[str, Any]:
        """
        UC-PROV-005: Obtener Proveedores Mejor Calificados
        Retorna los proveedores con mejor rating
        """
        sql = text("""
            SELECT 
                id, nombre, email, telefono,
                rating_prom, total_reviews, ciudad
            FROM ev_proveedores.proveedor
            WHERE is_deleted=0 
              AND status=1
              AND rating_prom IS NOT NULL
              AND total_reviews >= 5
            ORDER BY rating_prom DESC, total_reviews DESC
            LIMIT :lim
        """)
        
        with session_scope(self.settings) as session:
            result = session.execute(sql, {"lim": limit})
            items = [dict(row._mapping) for row in result]
        
        return {
            "top_proveedores": items,
            "total": len(items)
        }
