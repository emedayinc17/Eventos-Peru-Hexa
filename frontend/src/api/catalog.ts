import apiClient from './client';
import type {
  TipoEvento,
  Servicio,
  Paquete,
  CreateTipoEventoRequest,
  CreateServicioRequest,
  CreatePaqueteRequest,
  ApiResponse,
} from '@/types';

const CATALOG_BASE = '/catalogo/v1';

export const catalogApi = {
  // Tipos de Evento
  async getTiposEvento(): Promise<ApiResponse<TipoEvento> | TipoEvento[]> {
    const response = await apiClient.get<ApiResponse<TipoEvento> | TipoEvento[]>(`${CATALOG_BASE}/tipos-evento`);
    return response.data || response;
  },

  async getTipoEvento(id: number): Promise<TipoEvento> {
    const response = await apiClient.get<TipoEvento>(`${CATALOG_BASE}/tipos-evento/${id}`);
    return response.data;
  },

  async createTipoEvento(data: CreateTipoEventoRequest): Promise<TipoEvento> {
    const response = await apiClient.post<TipoEvento>(`${CATALOG_BASE}/admin/tipos`, data);
    return response.data;
  },

  async updateTipoEvento(id: number, data: CreateTipoEventoRequest): Promise<TipoEvento> {
    const response = await apiClient.put<TipoEvento>(`${CATALOG_BASE}/admin/tipos/${id}`, data);
    return response.data;
  },

  async deleteTipoEvento(id: number): Promise<void> {
    await apiClient.delete(`${CATALOG_BASE}/admin/tipos/${id}`);
  },

  // Servicios
  async getServicios(tipoEventoId?: number): Promise<ApiResponse<Servicio> | Servicio[]> {
    const params = tipoEventoId ? { tipo_evento_id: tipoEventoId } : {};
    const response = await apiClient.get<ApiResponse<Servicio> | Servicio[]>(`${CATALOG_BASE}/servicios`, { params });
    return response.data || response;
  },

  async getServicio(id: number): Promise<Servicio> {
    const response = await apiClient.get<Servicio>(`${CATALOG_BASE}/servicios/${id}`);
    return response.data;
  },

  async createServicio(data: CreateServicioRequest): Promise<Servicio> {
    const response = await apiClient.post<Servicio>(`${CATALOG_BASE}/admin/servicios`, data);
    return response.data;
  },

  async updateServicio(id: number, data: Partial<CreateServicioRequest>): Promise<Servicio> {
    const response = await apiClient.put<Servicio>(`${CATALOG_BASE}/admin/servicios/${id}`, data);
    return response.data;
  },

  async deleteServicio(id: number): Promise<void> {
    await apiClient.delete(`${CATALOG_BASE}/admin/servicios/${id}`);
  },

  // Paquetes
  async getPaquetes(tipoEventoId?: number): Promise<ApiResponse<Paquete> | Paquete[]> {
    const params = tipoEventoId ? { tipo_evento_id: tipoEventoId } : {};
    const response = await apiClient.get<ApiResponse<Paquete> | Paquete[]>(`${CATALOG_BASE}/paquetes`, { params });
    const raw: any = response.data || response;
    // Normalize paquete shape: ensure `precio_base` exists (backend returns monto_total_vigente)
    const mapPaquete = (p: any) => ({
      ...p,
      precio_base: p.precio_base ?? p.monto_total_vigente ?? p.monto_total ?? p.monto ?? null,
      moneda: p.moneda ?? p.currency ?? 'PEN',
    });

    if (Array.isArray(raw)) return raw.map(mapPaquete);
    if (raw && raw.items) return { ...raw, items: raw.items.map(mapPaquete) } as any;
    return raw as any;
  },

  async getPaquete(id: number): Promise<Paquete> {
    const response = await apiClient.get<Paquete>(`${CATALOG_BASE}/paquetes/${id}`);
    const p: any = response.data;
    if (p) {
      p.precio_base = p.precio_base ?? p.monto_total_vigente ?? p.monto_total ?? p.monto ?? null;
      p.moneda = p.moneda ?? p.currency ?? 'PEN';
    }
    return p as Paquete;
  },

  async createPaquete(data: CreatePaqueteRequest): Promise<Paquete> {
    const response = await apiClient.post<Paquete>(`${CATALOG_BASE}/admin/paquetes`, data);
    return response.data;
  },

  async updatePaquete(id: number, data: Partial<CreatePaqueteRequest>): Promise<Paquete> {
    const response = await apiClient.put<Paquete>(`${CATALOG_BASE}/admin/paquetes/${id}`, data);
    return response.data;
  },

  async deletePaquete(id: number): Promise<void> {
    await apiClient.delete(`${CATALOG_BASE}/admin/paquetes/${id}`);
  },
};
