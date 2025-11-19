# created by emeday 2025 - corrected hex alignment
from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any, List

class ContratacionRepository(ABC):
    @abstractmethod
    def list_items(self, limit: int = 100) -> Iterable[Dict[str, Any]]:
        raise NotImplementedError()
    
    @abstractmethod
    def list_all_pedidos_admin(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Lista TODOS los pedidos del sistema para ADMIN"""
        raise NotImplementedError()