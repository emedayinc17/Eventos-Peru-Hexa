/**
 * Custom hook para gestión de pedidos
 */

import { useState, useEffect } from 'react';
import { Pedido, CrearPedidoRequest } from '../types';
import { contratacionService } from '../services/contratacionService';

export const usePedidos = () => {
    const [pedidos, setPedidos] = useState<Pedido[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadMisPedidos = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await contratacionService.getMisPedidos();
            setPedidos(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Error al cargar pedidos');
            console.error('Error loading pedidos:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const crearPedido = async (data: CrearPedidoRequest): Promise<Pedido> => {
        setIsLoading(true);
        setError(null);
        try {
            const pedido = await contratacionService.crearPedido(data);
            setPedidos((prev) => [pedido, ...prev]);
            return pedido;
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Error al crear pedido';
            setError(errorMsg);
            console.error('Error creating pedido:', err);
            throw new Error(errorMsg);
        } finally {
            setIsLoading(false);
        }
    };

    const getPedidoById = async (id: string): Promise<Pedido> => {
        setIsLoading(true);
        setError(null);
        try {
            const pedido = await contratacionService.getPedidoById(id);
            return pedido;
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Error al obtener pedido';
            setError(errorMsg);
            console.error('Error getting pedido:', err);
            throw new Error(errorMsg);
        } finally {
            setIsLoading(false);
        }
    };

    return {
        pedidos,
        isLoading,
        error,
        loadMisPedidos,
        crearPedido,
        getPedidoById,
    };
};
