import apiClient from './client';
import type {
  Pedido,
  CreatePedidoRequest,
  UpdatePedidoRequest,
  PedidoDetalle,
  ApiResponse,
} from '@/types';

const ORDERS_BASE = '/contratacion';

export const ordersApi = {
  // List pedidos for client (mis pedidos) or all (admin)
  async getPedidos(usuarioId?: number | string, estado?: string, admin = false): Promise<any> {
    const params: Record<string, string | number> = {};
    if (usuarioId) params.usuario_id = usuarioId;
    if (estado) params.estado = estado;
    params._t = Date.now(); // Prevent caching

    const path = admin ? `${ORDERS_BASE}/admin/pedidos` : `${ORDERS_BASE}/cliente/mis-pedidos`;
    const response = await apiClient.get(path, { params });
    // Some endpoints return { items: [...] } others return array
    return response.data || response;
  },

  async getPedido(id: number | string, admin = false): Promise<PedidoDetalle> {
    const path = admin ? `${ORDERS_BASE}/admin/pedidos/${id}` : `${ORDERS_BASE}/cliente/mis-pedidos/${id}`;
    const response = await apiClient.get<PedidoDetalle>(path);
    return response.data;
  },

  async createPedido(data: CreatePedidoRequest): Promise<Pedido> {
    const response = await apiClient.post<Pedido>(`${ORDERS_BASE}/pedidos`, data);
    return response.data;
  },

  // Use PATCH for partial updates (backend expects PATCH for estado changes)
  async updatePedido(id: number | string, data: UpdatePedidoRequest): Promise<Pedido> {
    const response = await apiClient.patch<Pedido>(`${ORDERS_BASE}/admin/pedidos/${id}`, data);
    return response.data;
  },

  // Backend does not expose DELETE for pedidos; map delete to setting estado=CANCELADO
  async deletePedido(id: number | string): Promise<void> {
    await apiClient.patch(`${ORDERS_BASE}/admin/pedidos/${id}`, { estado: 5 });
  },

  async addItems(id: number | string, items: any[]): Promise<any> {
    const response = await apiClient.post(`${ORDERS_BASE}/admin/pedidos/${id}/items`, { items });
    return response.data;
  },

  async deleteItems(id: number | string, itemIds: string[]): Promise<any> {
    const response = await apiClient.delete(`${ORDERS_BASE}/admin/pedidos/${id}/items`, {
      data: { item_ids: itemIds }
    });
    return response.data;
  },
};
