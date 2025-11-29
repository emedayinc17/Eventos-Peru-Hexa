from dataclasses import dataclass


@dataclass
class UpdateServicioUseCase:
    repository: object

    def execute(self, session, *, servicio_id: str, nombre: str | None = None, descripcion: str | None = None, tipo_evento_id: str | None = None, status: int | None = None) -> dict:
        return self.repository.update_servicio(session, servicio_id=servicio_id, nombre=nombre, descripcion=descripcion, tipo_evento_id=tipo_evento_id, status=status)
