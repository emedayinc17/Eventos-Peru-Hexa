/**
 * CAPA DE DOMINIO - Tipos y entidades
 * Estos tipos reflejan los modelos del backend
 */

// ============= IAM SERVICE =============
export interface Usuario {
    id: string;
    email: string;
    nombre_completo: string;
    rol: 'ADMIN' | 'CLIENT';
    activo: boolean;
    created_at: string;
    updated_at: string;
}

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface RegisterData {
    email: string;
    password: string;
    nombre_completo: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
}

// ============= CATÁLOGO SERVICE =============
export interface TipoEvento {
    id: string;
    nombre: string;
    descripcion: string;
    activo: boolean;
}

export interface Servicio {
    id: string;
    tipo_evento_id: string;
    nombre: string;
    descripcion: string;
    activo: boolean;
}

export interface OpcionServicio {
    id: string;
    servicio_id: string;
    nombre: string;
    descripcion: string;
    monto: number;
    activo: boolean;
}

export interface Paquete {
    id: string;
    nombre: string;
    descripcion: string;
    monto_total: number;
    activo: boolean;
}

export interface PaqueteDetalle extends Paquete {
    items: PaqueteItem[];
}

export interface PaqueteItem {
    id: string;
    paquete_id: string;
    opcion_servicio_id: string;
    cantidad: number;
    precio_unit_vigente: number;
    servicio_nombre?: string;
    opcion_nombre?: string;
}

// ============= PROVEEDORES SERVICE =============
export interface Proveedor {
    id: string;
    nombre: string;
    email: string;
    telefono: string;
    activo: boolean;
}

export interface ProveedorDisponible {
    proveedor_id: string;
    nombre: string;
    email: string;
}

// ============= CONTRATACIÓN SERVICE =============
export interface Pedido {
    id: string;
    cliente_id: string;
    estado: 'BORRADOR' | 'COTIZADO' | 'RESERVADO' | 'CONFIRMADO' | 'CANCELADO';
    monto_total: number;
    fecha_evento?: string;
    lugar_evento?: string;
    created_at: string;
    updated_at: string;
    items?: PedidoItem[];
}

export interface PedidoItem {
    id: string;
    pedido_id: string;
    opcion_servicio_id: string;
    cantidad: number;
    precio_unitario: number;
    proveedor_id?: string;
    servicio_nombre?: string;
    opcion_nombre?: string;
}

export interface CrearPedidoRequest {
    paquete_id?: string;
    items?: {
        opcion_servicio_id: string;
        cantidad: number;
    }[];
    fecha_evento?: string;
    lugar_evento?: string;
}

export interface AsignarProveedorRequest {
    item_id: string;
    proveedor_id: string;
    fecha_inicio: string;
    fecha_fin: string;
}
