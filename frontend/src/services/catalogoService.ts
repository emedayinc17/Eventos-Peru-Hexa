/**
 * ADAPTADOR - Catálogo Service
 * Implementa la comunicación con el microservicio de catálogo
 */

import axiosClient from '../lib/axios';
import { API_CONFIG } from '../lib/config';
import { TipoEvento, Servicio, OpcionServicio, Paquete, PaqueteDetalle } from '../types';

class CatalogoService {
    private baseURL = API_CONFIG.CATALOGO;

    /**
     * Listar tipos de evento
     */
    async getTiposEvento(limit = 50, offset = 0): Promise<TipoEvento[]> {
        const response = await axiosClient.get<TipoEvento[]>(
            `${this.baseURL}/v1/catalogo/tipos`,
            { params: { limit, offset } }
        );
        return response.data;
    }

    /**
     * Listar servicios (opcionalmente filtrados por tipo de evento)
     */
    async getServicios(tipoEventoId?: string, limit = 50, offset = 0): Promise<Servicio[]> {
        const response = await axiosClient.get<Servicio[]>(
            `${this.baseURL}/v1/catalogo/servicios`,
            {
                params: {
                    tipo_evento_id: tipoEventoId,
                    limit,
                    offset
                }
            }
        );
        return response.data;
    }

    /**
     * Listar opciones de un servicio
     */
    async getOpciones(servicioId: string, limit = 50, offset = 0): Promise<OpcionServicio[]> {
        const response = await axiosClient.get<OpcionServicio[]>(
            `${this.baseURL}/v1/catalogo/opciones`,
            {
                params: {
                    servicio_id: servicioId,
                    limit,
                    offset
                }
            }
        );
        return response.data;
    }

    /**
     * Listar paquetes
     */
    async getPaquetes(limit = 50, offset = 0): Promise<Paquete[]> {
        const response = await axiosClient.get<Paquete[]>(
            `${this.baseURL}/v1/catalogo/paquetes`,
            { params: { limit, offset } }
        );
        return response.data;
    }

    /**
     * Obtener detalle de un paquete
     */
    async getPaqueteDetalle(paqueteId: string): Promise<PaqueteDetalle> {
        const response = await axiosClient.get<PaqueteDetalle>(
            `${this.baseURL}/v1/catalogo/paquetes/${paqueteId}`
        );
        return response.data;
    }
}

// Exportar instancia singleton
export const catalogoService = new CatalogoService();
