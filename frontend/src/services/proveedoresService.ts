/**
 * ADAPTADOR - Proveedores Service
 * Implementa la comunicación con el microservicio de proveedores
 */

import axiosClient from '../lib/axios';
import { API_CONFIG } from '../lib/config';
import { ProveedorDisponible } from '../types';

class ProveedoresService {
    private baseURL = API_CONFIG.PROVEEDORES;

    /**
     * Buscar proveedores disponibles para un servicio y fecha
     */
    async getProveedoresDisponibles(
        servicioId: string,
        fecha: string
    ): Promise<ProveedorDisponible[]> {
        const response = await axiosClient.get<ProveedorDisponible[]>(
            `${this.baseURL}/v1/proveedores/disponibles`,
            {
                params: {
                    servicio_id: servicioId,
                    fecha
                }
            }
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
export const proveedoresService = new ProveedoresService();
