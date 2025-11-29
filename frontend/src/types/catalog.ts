export interface TipoEvento {
  id: number;
  nombre: string;
  descripcion: string;
  created_at?: string;
}

export interface Servicio {
  id: number;
  nombre: string;
  descripcion?: string;
  categoria?: 'DECORACION' | 'CATERING' | 'FOTOGRAFIA' | 'VIDEO' | 'ENTRETENIMIENTO' | 'OTRO';
  precio_unitario?: number;
  disponible: boolean;
  tipo_evento_id?: number;
}

export interface Opcion {
  id: number;
  nombre: string;
  descripcion?: string;
  servicio_id: number;
  precio_adicional: number;
}

export interface Paquete {
  id: number;
  nombre: string;
  descripcion: string;
  // `precio_base` may be provided by frontend/admin, but backend exposes
  // `monto_total_vigente` / `monto_total` — keep both as optional to be safe
  precio_base?: number;
  monto_total_vigente?: number;
  monto_total?: number;
  moneda?: string;
  tipo_evento_id: number;
  tipo_evento_nombre?: string;
  servicios?: Servicio[];
  created_at?: string;
}

export interface CreateTipoEventoRequest {
  nombre: string;
  descripcion: string;
}

export interface CreateServicioRequest {
  nombre: string;
  descripcion?: string;
  categoria: string;
  precio_unitario: number;
  disponible?: boolean;
  tipo_evento_id?: number;
}

export interface CreatePaqueteRequest {
  nombre: string;
  descripcion: string;
  precio_base: number;
  tipo_evento_id: number;
  servicios_ids?: number[];
}

export interface ApiResponse<T> {
  data: T[];
  total?: number;
}
