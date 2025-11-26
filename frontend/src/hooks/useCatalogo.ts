/**
 * Custom hook para gestión del catálogo
 */

import { useState } from 'react';
import { TipoEvento, Servicio, OpcionServicio, Paquete, PaqueteDetalle } from '../types';
import { catalogoService } from '../services/catalogoService';

export const useCatalogo = () => {
    const [tiposEvento, setTiposEvento] = useState<TipoEvento[]>([]);
    const [servicios, setServicios] = useState<Servicio[]>([]);
    const [opciones, setOpciones] = useState<OpcionServicio[]>([]);
    const [paquetes, setPaquetes] = useState<Paquete[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadTiposEvento = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await catalogoService.getTiposEvento();
            setTiposEvento(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Error al cargar tipos de evento');
            console.error('Error loading tipos evento:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const loadServicios = async (tipoEventoId?: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await catalogoService.getServicios(tipoEventoId);
            setServicios(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Error al cargar servicios');
            console.error('Error loading servicios:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const loadOpciones = async (servicioId: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await catalogoService.getOpciones(servicioId);
            setOpciones(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Error al cargar opciones');
            console.error('Error loading opciones:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const loadPaquetes = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await catalogoService.getPaquetes();
            setPaquetes(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Error al cargar paquetes');
            console.error('Error loading paquetes:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const getPaqueteDetalle = async (paqueteId: string): Promise<PaqueteDetalle> => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await catalogoService.getPaqueteDetalle(paqueteId);
            return data;
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Error al cargar detalle del paquete';
            setError(errorMsg);
            console.error('Error loading paquete detalle:', err);
            throw new Error(errorMsg);
        } finally {
            setIsLoading(false);
        }
    };

    return {
        tiposEvento,
        servicios,
        opciones,
        paquetes,
        isLoading,
        error,
        loadTiposEvento,
        loadServicios,
        loadOpciones,
        loadPaquetes,
        getPaqueteDetalle,
    };
};
