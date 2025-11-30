export interface Pedido {
  id: number | string;
  usuario_id?: number | string;
  cliente_id?: number | string;
  cliente_nombre?: string;
  cliente_email?: string;
  tipo_evento_id: number | string;
  tipo_evento_nombre?: string;
  fecha_evento: string;
  hora_inicio?: string;
  hora_fin?: string;
  num_personas: number;
  ubicacion?: string;
  paquete_id?: number | string;
  paquete_nombre?: string;
  servicios_adicionales?: (number | string)[];
  notas?: string;
  status: number; // 0=DRAFT, 1=COTIZADO, etc.
  estado?: number; // Alias
  monto_total: number;
  moneda?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ItemPedido {
  id: number | string;
  pedido_id?: number | string;
  opcion_servicio_id?: number | string;
  nombre_servicio: string;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
  tipo_item?: string | number; // 'SERVICIO', 'PAQUETE' or 1, 2
  referencia_id?: string;
  proveedor?: {
    id: string;
    nombre: string;
  };
}

export interface PedidoDetalle {
  pedido: Pedido;
  items: ItemPedido[];
  reservas: any[];
  paquete_items?: any[];
  estado_nombre?: string;
  total_items: number;
  total_reservas: number;
}

export interface CreatePedidoRequest {
  tipo_evento_id: number | string;
  fecha_evento: string;
  num_personas: number;
  paquete_id?: number | string;
  items?: any[];
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
