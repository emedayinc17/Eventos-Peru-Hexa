from dataclasses import dataclass


@dataclass
class CreateProveedorUseCase:
    repository: object

    def execute(self, session, *, nombre: str, email: str | None = None, telefono: str | None = None, categoria: str | None = None, ruc: str | None = None, contacto: str | None = None, direccion: str | None = None, activo: bool | None = None) -> dict:
        return self.repository.create_proveedor(session, nombre=nombre, email=email, telefono=telefono, categoria=categoria, ruc=ruc, contacto=contacto, direccion=direccion, activo=activo)
