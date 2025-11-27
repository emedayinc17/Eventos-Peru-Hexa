from dataclasses import dataclass


@dataclass
class CreateTipoEventoUseCase:
    repository: object

    def execute(self, session, *, nombre: str, descripcion: str | None = None, created_by: str | None = None) -> dict:
        """Crea un tipo de evento y retorna su id/nombre."""
        return self.repository.create_tipo(session, nombre=nombre, descripcion=descripcion)
