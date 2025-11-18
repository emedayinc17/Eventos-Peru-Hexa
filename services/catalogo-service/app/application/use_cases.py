# created by emeday 2025
"""
Application Layer - Use Cases
Catálogo Service
Arquitectura Hexagonal - Application Layer
"""
from typing import List, Dict, Any
from sqlalchemy import text
from ev_shared import Settings, session_scope

class CatalogoUseCases:
    """
    Casos de uso del dominio de Catálogo
    Orquesta la lógica de negocio sin depender de detalles de infraestructura
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def listar_tipos_evento(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        UC-CAT-001: Listar Tipos de Evento
        Retorna todos los tipos de evento activos disponibles
        """
        sql = text("""
            SELECT id, nombre, descripcion, status, created_at, updated_at
            FROM ev_catalogo.tipo_evento 
            WHERE status=1 AND is_deleted=0 
            ORDER BY nombre
            LIMIT :lim OFFSET :off
        """)
        
        with session_scope(self.settings) as session:
            result = session.execute(sql, {"lim": limit, "off": offset})
            items = [dict(row._mapping) for row in result]
        
        return {
            "items": items,
            "total": len(items),
            "limit": limit,
            "offset": offset
        }
    
    def obtener_tipo_evento(self, tipo_id: int) -> Dict[str, Any]:
        """
        UC-CAT-002: Obtener Tipo de Evento por ID
        Retorna los detalles de un tipo de evento específico
        """
        sql = text("""
            SELECT id, nombre, descripcion, status, created_at, updated_at
            FROM ev_catalogo.tipo_evento 
            WHERE id=:tid AND status=1 AND is_deleted=0
        """)
        
        with session_scope(self.settings) as session:
            result = session.execute(sql, {"tid": tipo_id})
            row = result.mappings().first()
            
            if not row:
                raise ValueError(f"Tipo de evento {tipo_id} no encontrado")
            
            return dict(row)
    
    def listar_opciones_con_precios(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        UC-CAT-003: Listar Opciones con Precios Vigentes
        Retorna todas las opciones de servicio con sus precios actuales
        """
        sql = text("""
            SELECT 
                o.id as opcion_id,
                o.tipo_evento_id,
                o.nombre as nombre_opcion,
                o.descripcion as descripcion_opcion,
                o.categoria,
                p.id as precio_id,
                p.monto,
                p.moneda,
                p.fecha_inicio,
                p.fecha_fin
            FROM ev_catalogo.v_opcion_con_precio_vigente v
            JOIN ev_catalogo.opcion_servicio o ON v.opcion_id = o.id
            JOIN ev_catalogo.precio p ON v.precio_id = p.id
            WHERE o.status=1 AND o.is_deleted=0
            ORDER BY o.nombre
            LIMIT :lim OFFSET :off
        """)
        
        with session_scope(self.settings) as session:
            result = session.execute(sql, {"lim": limit, "off": offset})
            items = [dict(row._mapping) for row in result]
        
        return {
            "items": items,
            "total": len(items),
            "limit": limit,
            "offset": offset
        }
    
    def buscar_opciones_por_tipo_evento(self, tipo_evento_id: int) -> Dict[str, Any]:
        """
        UC-CAT-004: Buscar Opciones por Tipo de Evento
        Retorna todas las opciones disponibles para un tipo de evento específico
        """
        sql = text("""
            SELECT 
                o.id as opcion_id,
                o.nombre,
                o.descripcion,
                o.categoria,
                p.monto,
                p.moneda
            FROM ev_catalogo.opcion_servicio o
            LEFT JOIN ev_catalogo.precio p ON o.id = p.opcion_id 
                AND p.status=1 
                AND p.is_deleted=0
                AND CURDATE() BETWEEN p.fecha_inicio AND COALESCE(p.fecha_fin, '9999-12-31')
            WHERE o.tipo_evento_id=:tid 
              AND o.status=1 
              AND o.is_deleted=0
            ORDER BY o.categoria, o.nombre
        """)
        
        with session_scope(self.settings) as session:
            result = session.execute(sql, {"tid": tipo_evento_id})
            items = [dict(row._mapping) for row in result]
        
        return {
            "tipo_evento_id": tipo_evento_id,
            "opciones": items,
            "total": len(items)
        }
