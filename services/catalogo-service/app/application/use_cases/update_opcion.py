from dataclasses import dataclass


@dataclass
class UpdateOpcionUseCase:
    repository: object

    def execute(self, session, *, opcion_id: str, nombre: str | None = None, moneda: str | None = None, monto: float | None = None, detalles: str | None = None) -> dict:
        return self.repository.update_opcion(session, opcion_id=opcion_id, nombre=nombre, moneda=moneda, monto=monto, detalles=detalles)
