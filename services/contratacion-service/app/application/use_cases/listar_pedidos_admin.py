"""
Use Case: Listar Todos los Pedidos (Admin)
Lista todos los pedidos del sistema con filtros opcionales
"""
from typing import Any, List, Optional, Dict
from ...domain.models import Pedido
from ...domain.ports import PedidoRepository
# In a strict hexagonal architecture, these should be ports/interfaces.
# For this project, we are using the clients directly as pragmatic ports.
from ...infrastructure.http.iam_client import IamClient
from ...infrastructure.http.catalogo_client import CatalogoClient

class ListarPedidosAdminUseCase:
    """
    Lista todos los pedidos del sistema (admin).
    Caso de uso de consulta - solo lectura.
    Enriquece los datos con información de IAM y Catálogo.
    """
    
    def __init__(
        self, 
        pedido_repo: PedidoRepository,
        iam_client: IamClient,
        catalogo_client: CatalogoClient
    ):
        self.pedido_repo = pedido_repo
        self.iam_client = iam_client
        self.catalogo_client = catalogo_client
    
    def execute(
        self,
        session: Any,
        *,
        status: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
        auth_token: Optional[str] = None
    ) -> List[Pedido]:
        """
        Ejecuta el caso de uso: listar todos los pedidos.
        
        Args:
            session: Sesión de base de datos
            status: Filtro opcional por estado (0-5)
            limit: Cantidad máxima de resultados
            offset: Cantidad de registros a saltar (paginación)
            auth_token: Token JWT para autenticación con otros servicios
        
        Returns:
            Lista de todos los pedidos ordenados por fecha de creación
        """
        pedidos = self.pedido_repo.listar_todos(
            session,
            status=status,
            limit=limit,
            offset=offset
        )
        
        if not pedidos:
            return []
            
        # Enriquecimiento de datos (N+1 optimizado con sets)
        # 1. Obtener IDs únicos
        cliente_ids = {p.cliente_id for p in pedidos if p.cliente_id}
        tipo_evento_ids = {p.tipo_evento_id for p in pedidos if p.tipo_evento_id}
        
        # 2. Fetch data (Cache local simple)
        clientes_map: Dict[str, Any] = {}
        eventos_map: Dict[str, Any] = {}
        
        # Fetch Clientes from IAM
        if auth_token and cliente_ids:
            # TODO: Implementar endpoint bulk en IAM para evitar N requests
            # Por ahora, hacemos loop (ineficiente pero funcional para MVP)
            for cid in cliente_ids:
                try:
                    user_data = self.iam_client.get_user_details(cid, auth_token)
                    if user_data:
                        clientes_map[cid] = user_data
                except Exception:
                    pass # Fail silently on enrichment
        
        # Fetch Event Types from Catalogo
        if tipo_evento_ids:
             # Catalogo client get_tipo_evento fetches ALL and filters, so we can just fetch once if we cache?
             # Actually get_tipo_evento fetches all internally.
             # We can optimize by fetching all types once and mapping.
             # But get_tipo_evento implementation fetches all every time.
             # Let's just call it.
             for tid in tipo_evento_ids:
                 try:
                     tipo_data = self.catalogo_client.get_tipo_evento(tid)
                     if tipo_data:
                         eventos_map[tid] = tipo_data
                 except Exception:
                     pass

        # 3. Assign names
        for p in pedidos:
            # Cliente
            if p.cliente_id in clientes_map:
                c_data = clientes_map[p.cliente_id]
                # Update attributes directly (assuming Pedido is mutable or we set attrs)
                # Pedido is a dataclass or Pydantic model? It's a dataclass in domain/models.py
                # We can set attributes.
                p.cliente_nombre = c_data.get("nombre")
                p.cliente_email = c_data.get("email")
            
            # Evento
            if p.tipo_evento_id in eventos_map:
                e_data = eventos_map[p.tipo_evento_id]
                p.tipo_evento_nombre = e_data.get("nombre")
                
        return pedidos
