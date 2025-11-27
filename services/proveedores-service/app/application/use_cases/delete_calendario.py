from dataclasses import dataclass


@dataclass
class DeleteCalendarioUseCase:
    repository: object

    def execute(self, session, *, calendario_id: str) -> None:
        return self.repository.delete_calendario(session, calendario_id=calendario_id)
