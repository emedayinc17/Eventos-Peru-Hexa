from dataclasses import dataclass


@dataclass
class UpdateTipoEventoUseCase:
    repository: object

    def execute(self, session, *, tipo_id: str, nombre: str | None = None, descripcion: str | None = None, updated_by: str | None = None) -> dict:
        """Actualiza un tipo de evento y devuelve el objeto actualizado."""
        return self.repository.update_tipo(session, tipo_id=tipo_id, nombre=nombre, descripcion=descripcion)
