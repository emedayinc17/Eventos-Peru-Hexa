export interface Pedido {
  id: number | string;
  usuario_id?: number | string;
  cliente_id?: number | string; // Alias for usuario_id in some contexts
  tipo_evento_id: number | string;
  tipo_evento_nombre?: string;
  fecha_evento: string;
  num_personas: number; // Backend uses num_personas
  num_invitados?: number; // Frontend alias
  paquete_id?: number | string;
  paquete_nombre?: string;
  servicios_adicionales?: (number | string)[];
  comentarios?: string;
  notas?: string; // Backend uses notas
  estado: number; // 0=DRAFT, 1=COTIZADO, 2=APROBADO, 3=ASIGNADO, 4=CONFIRMADO, 5=CANCELADO, 6=COMPLETADO
  monto_total?: number;
  total?: number;
  created_at?: string;
  updated_at?: string;
}

export interface CreatePedidoRequest {
  tipo_evento_id: number | string;
  fecha_evento: string;
  num_personas: number;
  paquete_id?: number | string;
  items?: any[]; // For custom orders
  notas?: string;
  hora_inicio?: string;
  hora_fin?: string;
  ubicacion?: string;
}

export interface UpdatePedidoRequest {
  estado?: number;
  fecha_evento?: string;
  num_personas?: number;
  notas?: string;
}

export interface PedidoDetalle extends Pedido {
  paquete?: {
    id: number | string;
    nombre: string;
    precio_base: number;
  };
  items?: Array<{
    id: number | string;
    nombre: string;
    precio_unitario: number;
    cantidad: number;
    subtotal: number;
  }>;
  reservas?: any[];
}
