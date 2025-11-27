from dataclasses import dataclass


@dataclass
class AddCalendarioUseCase:
    repository: object

    def execute(self, session, *, proveedor_id: str, tipo: int, inicio, fin, motivo: str | None = None) -> dict:
        return self.repository.add_calendario(session, proveedor_id=proveedor_id, tipo=tipo, inicio=inicio, fin=fin, motivo=motivo)
