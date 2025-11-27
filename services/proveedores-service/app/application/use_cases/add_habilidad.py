from dataclasses import dataclass


@dataclass
class AddHabilidadUseCase:
    repository: object

    def execute(self, session, *, proveedor_id: str, servicio_id: str, nivel: int = 1) -> dict:
        return self.repository.add_habilidad(session, proveedor_id=proveedor_id, servicio_id=servicio_id, nivel=nivel)
