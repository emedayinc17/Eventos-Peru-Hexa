export interface Pedido {
  id: number;
  usuario_id?: number;
  tipo_evento_id: number;
  tipo_evento_nombre?: string;
  fecha_evento: string;
  num_invitados: number;
  paquete_id?: number;
  paquete_nombre?: string;
  servicios_adicionales?: number[];
  comentarios?: string;
  estado: 'PENDIENTE' | 'CONFIRMADO' | 'CANCELADO' | 'COMPLETADO';
  total: number;
  created_at?: string;
  updated_at?: string;
}

export interface CreatePedidoRequest {
  tipo_evento_id: number;
  fecha_evento: string;
  num_invitados: number;
  paquete_id?: number;
  servicios_adicionales?: number[];
  comentarios?: string;
}

export interface UpdatePedidoRequest {
  estado?: 'PENDIENTE' | 'CONFIRMADO' | 'CANCELADO' | 'COMPLETADO';
  fecha_evento?: string;
  num_invitados?: number;
  comentarios?: string;
}

export interface PedidoDetalle extends Pedido {
  paquete?: {
    id: number;
    nombre: string;
    precio_base: number;
  };
  servicios?: Array<{
    id: number;
    nombre: string;
    precio_unitario: number;
  }>;
}
