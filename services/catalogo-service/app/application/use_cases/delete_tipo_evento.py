from dataclasses import dataclass


@dataclass
class DeleteTipoEventoUseCase:
    repository: object

    def execute(self, session, *, tipo_id: str) -> None:
        """Marca un tipo de evento como eliminado (soft delete)."""
        self.repository.delete_tipo(session, tipo_id=tipo_id)
