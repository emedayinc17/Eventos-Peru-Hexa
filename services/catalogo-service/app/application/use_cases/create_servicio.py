from dataclasses import dataclass


@dataclass
class CreateServicioUseCase:
    repository: object

    def execute(self, session, *, nombre: str, tipo_evento_id: str, descripcion: str | None = None):
        return self.repository.create_servicio(session, nombre=nombre, tipo_evento_id=tipo_evento_id, descripcion=descripcion)
