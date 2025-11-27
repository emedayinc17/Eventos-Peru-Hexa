from dataclasses import dataclass


@dataclass
class DeleteProveedorUseCase:
    repository: object

    def execute(self, session, *, proveedor_id: str):
        return self.repository.delete_proveedor(session, proveedor_id=proveedor_id)
