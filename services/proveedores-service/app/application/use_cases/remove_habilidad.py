from dataclasses import dataclass


@dataclass
class RemoveHabilidadUseCase:
    repository: object

    def execute(self, session, *, proveedor_id: str, servicio_id: str) -> None:
        return self.repository.remove_habilidad(session, proveedor_id=proveedor_id, servicio_id=servicio_id)
