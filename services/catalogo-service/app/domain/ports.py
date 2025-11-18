# created by emeday 2025 - corrected hex alignment
from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any

class CatalogoRepository(ABC):
    @abstractmethod
    def list_items(self, limit: int = 100) -> Iterable[Dict[str, Any]]:
        raise NotImplementedError()
