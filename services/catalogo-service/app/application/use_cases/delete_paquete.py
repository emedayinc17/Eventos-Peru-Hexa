from dataclasses import dataclass


@dataclass
class DeletePaqueteUseCase:
    repository: object

    def execute(self, session, *, paquete_id: str):
        return self.repository.delete_paquete(session, paquete_id=paquete_id)
