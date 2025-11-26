/**
 * ADAPTADOR - Contratación Service
 * Implementa la comunicación con el microservicio de contratación
 */

import axiosClient from '../lib/axios';
import { API_CONFIG } from '../lib/config';
import { Pedido, CrearPedidoRequest, AsignarProveedorRequest } from '../types';

class ContratacionService {
    private baseURL = API_CONFIG.CONTRATACION;

    /**
     * Crear un nuevo pedido
     */
    async crearPedido(data: CrearPedidoRequest): Promise<Pedido> {
        const response = await axiosClient.post<Pedido>(
            `${this.baseURL}/pedidos`,
            data
        );
        return response.data;
    }

    /**
     * Listar pedidos del cliente autenticado
     */
    async getMisPedidos(): Promise<Pedido[]> {
        const response = await axiosClient.get<Pedido[]>(
            `${this.baseURL}/pedidos/mios`
        );
        return response.data;
    }

    /**
     * Obtener detalle de un pedido
     */
    async getPedidoById(pedidoId: string): Promise<Pedido> {
        const response = await axiosClient.get<Pedido>(
            `${this.baseURL}/pedidos/${pedidoId}`
        );
        return response.data;
    }

    // ========== ADMIN ENDPOINTS ==========

    /**
     * Listar todos los pedidos (ADMIN)
     */
    async getAllPedidos(limit = 50, offset = 0): Promise<Pedido[]> {
        const response = await axiosClient.get<Pedido[]>(
            `${this.baseURL}/admin/pedidos`,
            { params: { limit, offset } }
        );
        return response.data;
    }

    /**
     * Obtener detalle de pedido (ADMIN)
     */
    async getAdminPedidoById(pedidoId: string): Promise<Pedido> {
        const response = await axiosClient.get<Pedido>(
            `${this.baseURL}/admin/pedidos/${pedidoId}`
        );
        return response.data;
    }

    /**
     * Cambiar estado de un pedido (ADMIN)
     */
    async cambiarEstadoPedido(
        pedidoId: string,
        estado: 'BORRADOR' | 'COTIZADO' | 'RESERVADO' | 'CONFIRMADO' | 'CANCELADO'
    ): Promise<Pedido> {
        const response = await axiosClient.patch<Pedido>(
            `${this.baseURL}/admin/pedidos/${pedidoId}`,
            { estado }
        );
        return response.data;
    }

    /**
     * Asignar proveedor a un item del pedido (ADMIN)
     */
    async asignarProveedor(
        pedidoId: string,
        data: AsignarProveedorRequest
    ): Promise<Pedido> {
        const response = await axiosClient.post<Pedido>(
            `${this.baseURL}/admin/pedidos/${pedidoId}/asignar-proveedor`,
            data
        );
        return response.data;
    }

    /**
     * Health check del servicio
     */
    async healthCheck(): Promise<{ status: string }> {
        const response = await axiosClient.get<{ status: string }>(
            `${this.baseURL}/health`
        );
        return response.data;
    }
}

// Exportar instancia singleton
export const contratacionService = new ContratacionService();
