import { defineStore } from 'pinia';
import { ref } from 'vue';
import { catalogApi } from '@/api';
import type { TipoEvento, Servicio, Paquete, CreateTipoEventoRequest, CreateServicioRequest, CreatePaqueteRequest } from '@/types';

export const useCatalogStore = defineStore('catalog', () => {
  // State
  const tiposEvento = ref<TipoEvento[]>([]);
  const servicios = ref<Servicio[]>([]);
  const paquetes = ref<Paquete[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Cache timestamps
  const lastFetchTipos = ref<number>(0);
  const lastFetchServicios = ref<number>(0);
  const lastFetchPaquetes = ref<number>(0);
  const CACHE_TTL = 5 * 60 * 1000; // 5 minutos

  // Actions - Tipos de Evento
  async function fetchTiposEvento(forceRefresh = false): Promise<void> {
    const now = Date.now();
    if (!forceRefresh && tiposEvento.value.length > 0 && now - lastFetchTipos.value < CACHE_TTL) {
      return; // Usar cache
    }

    loading.value = true;
    error.value = null;
    
    try {
      const response = await catalogApi.getTiposEvento();
      // `catalogApi.getTiposEvento()` may return either an array or an ApiResponse object.
      const raw: any = response;
      if (Array.isArray(raw)) {
        tiposEvento.value = raw;
      } else if (raw && (raw.data || raw.items)) {
        tiposEvento.value = raw.data || raw.items || [];
      } else {
        tiposEvento.value = [];
      }
      lastFetchTipos.value = now;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al cargar tipos de evento';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createTipoEvento(data: CreateTipoEventoRequest): Promise<TipoEvento> {
    loading.value = true;
    error.value = null;
    
    try {
      const newTipo = await catalogApi.createTipoEvento(data);
      tiposEvento.value.push(newTipo);
      return newTipo;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al crear tipo de evento';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateTipoEvento(id: number, data: CreateTipoEventoRequest): Promise<TipoEvento> {
    loading.value = true;
    error.value = null;
    
    try {
      const updated = await catalogApi.updateTipoEvento(id, data);
      const index = tiposEvento.value.findIndex(t => t.id === id);
      if (index !== -1) {
        tiposEvento.value[index] = updated;
      }
      return updated;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al actualizar tipo de evento';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteTipoEvento(id: number): Promise<void> {
    loading.value = true;
    error.value = null;
    
    try {
      await catalogApi.deleteTipoEvento(id);
      tiposEvento.value = tiposEvento.value.filter(t => t.id !== id);
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al eliminar tipo de evento';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Actions - Servicios
  async function fetchServicios(tipoEventoId?: number, forceRefresh = false): Promise<void> {
    const now = Date.now();
    if (!forceRefresh && servicios.value.length > 0 && now - lastFetchServicios.value < CACHE_TTL && !tipoEventoId) {
      return; // Usar cache solo si no hay filtro
    }

    loading.value = true;
    error.value = null;
    
    try {
      const response = await catalogApi.getServicios(tipoEventoId);
      const rawServicios: any = response;
      if (Array.isArray(rawServicios)) {
        servicios.value = rawServicios;
      } else if (rawServicios && (rawServicios.data || rawServicios.items)) {
        servicios.value = rawServicios.data || rawServicios.items || [];
      } else {
        servicios.value = [];
      }
      if (!tipoEventoId) {
        lastFetchServicios.value = now;
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al cargar servicios';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createServicio(data: CreateServicioRequest): Promise<Servicio> {
    loading.value = true;
    error.value = null;
    
    try {
      const newServicio = await catalogApi.createServicio(data);
      servicios.value.push(newServicio);
      return newServicio;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al crear servicio';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateServicio(id: number, data: Partial<CreateServicioRequest>): Promise<Servicio> {
    loading.value = true;
    error.value = null;
    
    try {
      const updated = await catalogApi.updateServicio(id, data);
      const index = servicios.value.findIndex(s => s.id === id);
      if (index !== -1) {
        servicios.value[index] = updated;
      }
      return updated;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al actualizar servicio';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteServicio(id: number): Promise<void> {
    loading.value = true;
    error.value = null;
    
    try {
      await catalogApi.deleteServicio(id);
      servicios.value = servicios.value.filter(s => s.id !== id);
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al eliminar servicio';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Actions - Paquetes
  async function fetchPaquetes(tipoEventoId?: number, forceRefresh = false): Promise<void> {
    const now = Date.now();
    if (!forceRefresh && paquetes.value.length > 0 && now - lastFetchPaquetes.value < CACHE_TTL && !tipoEventoId) {
      return; // Usar cache solo si no hay filtro
    }

    loading.value = true;
    error.value = null;
    
    try {
      const response = await catalogApi.getPaquetes(tipoEventoId);
      const rawPaquetes: any = response;
      if (Array.isArray(rawPaquetes)) {
        paquetes.value = rawPaquetes;
      } else if (rawPaquetes && (rawPaquetes.data || rawPaquetes.items)) {
        paquetes.value = rawPaquetes.data || rawPaquetes.items || [];
      } else {
        paquetes.value = [];
      }
      if (!tipoEventoId) {
        lastFetchPaquetes.value = now;
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al cargar paquetes';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createPaquete(data: CreatePaqueteRequest): Promise<Paquete> {
    loading.value = true;
    error.value = null;
    
    try {
      const newPaquete = await catalogApi.createPaquete(data);
      paquetes.value.push(newPaquete);
      return newPaquete;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al crear paquete';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updatePaquete(id: number, data: Partial<CreatePaqueteRequest>): Promise<Paquete> {
    loading.value = true;
    error.value = null;
    
    try {
      const updated = await catalogApi.updatePaquete(id, data);
      const index = paquetes.value.findIndex(p => p.id === id);
      if (index !== -1) {
        paquetes.value[index] = updated;
      }
      return updated;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al actualizar paquete';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deletePaquete(id: number): Promise<void> {
    loading.value = true;
    error.value = null;
    
    try {
      await catalogApi.deletePaquete(id);
      paquetes.value = paquetes.value.filter(p => p.id !== id);
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al eliminar paquete';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    // State
    tiposEvento,
    servicios,
    paquetes,
    loading,
    error,
    // Actions
    fetchTiposEvento,
    createTipoEvento,
    updateTipoEvento,
    deleteTipoEvento,
    fetchServicios,
    createServicio,
    updateServicio,
    deleteServicio,
    fetchPaquetes,
    createPaquete,
    updatePaquete,
    deletePaquete,
  };
});
