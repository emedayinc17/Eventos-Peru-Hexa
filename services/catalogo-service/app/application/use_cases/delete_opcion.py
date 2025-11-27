from dataclasses import dataclass


@dataclass
class DeleteOpcionUseCase:
    repository: object

    def execute(self, session, *, opcion_id: str):
        self.repository.delete_opcion(session, opcion_id=opcion_id)
