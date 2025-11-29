from dataclasses import dataclass


@dataclass
class UpdateProveedorUseCase:
    repository: object

    def execute(self, session, *, proveedor_id: str, nombre: str | None = None, email: str | None = None, telefono: str | None = None, categoria: str | None = None, ruc: str | None = None, contacto: str | None = None, direccion: str | None = None, activo: bool | None = None):
        return self.repository.update_proveedor(session, proveedor_id=proveedor_id, nombre=nombre, email=email, telefono=telefono, categoria=categoria, ruc=ruc, contacto=contacto, direccion=direccion, activo=activo)
