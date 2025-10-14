# application queries patched for absolute imports
from dataclasses import dataclass
from ev_shared.config import Settings
from app.domain.ports import ProveedoresRepository
from app.domain.models import Item
from app.infrastructure.db.sqlalchemy.repositories import SqlProveedoresRepository

@dataclass
class ServiceContainer:
    settings: Settings
    repo: ProveedoresRepository

def get_container(settings: Settings) -> ServiceContainer:
    return ServiceContainer(settings=settings, repo=SqlProveedoresRepository(settings))

class ListItems:
    def __init__(self, repo: ProveedoresRepository):
        self.repo = repo
    def execute(self, limit: int = 100):
        return list(self.repo.list_items(limit=limit))
