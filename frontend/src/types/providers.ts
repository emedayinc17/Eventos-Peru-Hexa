export interface Proveedor {
  id: number;
  nombre: string;
  ruc?: string;
  contacto?: string;
  telefono?: string;
  email?: string;
  direccion?: string;
  categoria: string;
  activo: boolean;
  created_at?: string;
}

export interface CreateProveedorRequest {
  nombre: string;
  ruc?: string;
  contacto?: string;
  telefono?: string;
  email?: string;
  direccion?: string;
  categoria: string;
  activo?: boolean;
}

export interface ProveedorDisponible extends Proveedor {
  disponible: boolean;
  servicios?: string[];
}
