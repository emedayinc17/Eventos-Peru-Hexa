from dataclasses import dataclass


@dataclass
class CreatePaqueteUseCase:
    repository: object

    def execute(self, session, *, codigo: str, nombre: str, items: list, moneda: str = "PEN", descripcion: str | None = None, monto: float | None = None) -> dict:
        # items: list of dicts {opcion_servicio_id, cantidad}
        return self.repository.create_paquete(session, codigo=codigo, nombre=nombre, items=items, moneda=moneda, descripcion=descripcion, monto=monto)
