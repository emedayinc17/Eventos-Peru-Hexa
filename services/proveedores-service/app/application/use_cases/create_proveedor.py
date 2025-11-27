from dataclasses import dataclass


@dataclass
class CreateProveedorUseCase:
    repository: object

    def execute(self, session, *, nombre: str, email: str | None = None, telefono: str | None = None) -> dict:
        return self.repository.create_proveedor(session, nombre=nombre, email=email, telefono=telefono)
