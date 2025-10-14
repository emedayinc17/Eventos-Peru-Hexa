# application queries patched for absolute imports
from dataclasses import dataclass
from ev_shared.config import Settings
from app.domain.ports import CatalogoRepository
from app.domain.models import Item
from app.infrastructure.db.sqlalchemy.repositories import SqlCatalogoRepository

@dataclass
class ServiceContainer:
    settings: Settings
    repo: CatalogoRepository

def get_container(settings: Settings) -> ServiceContainer:
    return ServiceContainer(settings=settings, repo=SqlCatalogoRepository(settings))

class ListItems:
    def __init__(self, repo: CatalogoRepository):
        self.repo = repo
    def execute(self, limit: int = 100):
        return list(self.repo.list_items(limit=limit))
