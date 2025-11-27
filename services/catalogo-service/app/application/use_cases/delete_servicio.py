from dataclasses import dataclass


@dataclass
class DeleteServicioUseCase:
    repository: object

    def execute(self, session, *, servicio_id: str):
        self.repository.delete_servicio(session, servicio_id=servicio_id)
