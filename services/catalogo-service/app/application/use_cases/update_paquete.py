from dataclasses import dataclass


@dataclass
class UpdatePaqueteUseCase:
    repository: object

    def execute(self, session, *, paquete_id: str, nombre: str | None = None, items: list | None = None, moneda: str | None = None):
        """Actualiza datos de un paquete: nombre, items (reemplaza), y moneda opcionalmente."""
        return self.repository.update_paquete(session, paquete_id=paquete_id, nombre=nombre, items=items, moneda=moneda)
