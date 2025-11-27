from dataclasses import dataclass


@dataclass
class CreateOpcionUseCase:
    repository: object

    def execute(self, session, *, servicio_id: str, nombre: str, moneda: str, monto: float, detalles: str | None = None):
        return self.repository.create_opcion(session, servicio_id=servicio_id, nombre=nombre, moneda=moneda, monto=monto, detalles=detalles)
