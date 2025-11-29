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

// Helper to resolve a backend base URL that is absolute. If VITE_API_BASE_URL
// is set to a relative path (e.g. '/api') during local dev, use a sensible
// absolute fallback to avoid axios/baseURL concatenation that yields
// '/api/api/...' (observed in dev env). Prefer an env value that starts with
// 'http' otherwise fallback to 'http://localhost:8020'.
const resolveBackendBase = () => {
  const env = (import.meta.env.VITE_API_BASE_URL as string) || '';
  if (env && (env.startsWith('http://') || env.startsWith('https://'))) return env.replace(/\/+$/, '');
  return 'http://localhost:8020';
};

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

  async updateTipoEvento(id: number | string, data: CreateTipoEventoRequest): Promise<TipoEvento> {
    const response = await apiClient.put<TipoEvento>(`${CATALOG_BASE}/admin/tipos/${id}`, data);
    return response.data;
  },

  async deleteTipoEvento(id: number | string): Promise<void> {
    await apiClient.delete(`${CATALOG_BASE}/admin/tipos/${id}`);
  },

  // Servicios
  async getServicios(opts?: { tipoEventoId?: number | string; limit?: number; offset?: number }): Promise<{ items: Servicio[]; total: number }> {
    const params: any = {};
    if (opts?.tipoEventoId) params.tipo_evento_id = opts.tipoEventoId;
    if (opts?.limit !== undefined) params.limit = opts.limit;
    if (opts?.offset !== undefined) params.offset = opts.offset;
    const response = await apiClient.get(`${CATALOG_BASE}/servicios`, { params });
    const raw: any = response.data || response;
    if (Array.isArray(raw)) {
      return { items: raw, total: raw.length };
    }
    if (raw && (raw.items || raw.data)) {
      const items = raw.items || raw.data || [];
      const total = raw.total ?? items.length;
      return { items, total };
    }
    return { items: [], total: 0 };
  },

  async getServicio(id: number | string): Promise<Servicio> {
    const response = await apiClient.get<Servicio>(`${CATALOG_BASE}/servicios/${id}`);
    return response.data;
  },

  async createServicio(data: CreateServicioRequest): Promise<Servicio> {
    const response = await apiClient.post<Servicio>(`${CATALOG_BASE}/admin/servicios`, data);
    return response.data;
  },

  async updateServicio(id: number | string, data: Partial<CreateServicioRequest>): Promise<Servicio> {
    // The backend expects `status` (int) for service availability. If frontend sends `disponible` (boolean),
    // convert it to `status` to persist correctly (1 = disponible, 0 = no disponible).
    const payload: any = { ...data };
    if (payload.disponible !== undefined) {
      payload.status = payload.disponible ? 1 : 0;
      delete payload.disponible;
    }
    const response = await apiClient.put<Servicio>(`${CATALOG_BASE}/admin/servicios/${id}`, payload);
    return response.data;
  },

  async deleteServicio(id: number | string): Promise<void> {
    await apiClient.delete(`${CATALOG_BASE}/admin/servicios/${id}`);
  },

  // Paquetes
  async getPaquetes(opts?: { tipoEventoId?: number | string; limit?: number; offset?: number }): Promise<{ items: Paquete[]; total: number }> {
    const params: any = {};
    if (opts?.tipoEventoId) params.tipo_evento_id = opts.tipoEventoId;
    if (opts?.limit !== undefined) params.limit = opts.limit;
    if (opts?.offset !== undefined) params.offset = opts.offset;
    const response = await apiClient.get(`${CATALOG_BASE}/paquetes`, { params });
    const raw: any = response.data || response;
    const mapPaquete = (p: any) => ({
      ...p,
      precio_base: p.precio_base ?? p.monto_total_vigente ?? p.monto_total ?? p.monto ?? null,
      moneda: p.moneda ?? p.currency ?? 'PEN',
    });
    if (Array.isArray(raw)) {
      return { items: raw.map(mapPaquete), total: raw.length };
    }
    if (raw && (raw.items || raw.data)) {
      const items = (raw.items || raw.data || []).map(mapPaquete);
      const total = raw.total ?? items.length;
      return { items, total };
    }
    return { items: [], total: 0 };
  },

  async getPaquete(id: number | string): Promise<Paquete> {
    const response = await apiClient.get<Paquete>(`${CATALOG_BASE}/paquetes/${id}`);
    const p: any = response.data;
    if (p) {
      p.precio_base = p.precio_base ?? p.monto_total_vigente ?? p.monto_total ?? p.monto ?? null;
      p.moneda = p.moneda ?? p.currency ?? 'PEN';
    }
    return p as Paquete;
  },

  async createPaquete(data: CreatePaqueteRequest): Promise<Paquete> {
    const url = `${CATALOG_BASE}/admin/paquetes`;
    try {
      console.debug('[catalogApi] createPaquete request', url, data);
      const response = await apiClient.post<Paquete>(url, data);
      console.debug('[catalogApi] createPaquete response', response && response.data);
      return response.data;
    } catch (e) {
      console.error('[catalogApi] createPaquete error', e);
      throw e;
    }
  },

  async updatePaquete(id: number | string, data: Partial<CreatePaqueteRequest>): Promise<Paquete> {
    const url = `${CATALOG_BASE}/admin/paquetes/${id}`;
    try {
      console.debug('[catalogApi] updatePaquete request', url, data);
      const response = await apiClient.put<Paquete>(url, data);
      console.debug('[catalogApi] updatePaquete response', response && response.data);
      return response.data;
    } catch (e) {
      console.error('[catalogApi] updatePaquete error', e);
      throw e;
    }
  },

  async deletePaquete(id: number | string): Promise<void> {
    await apiClient.delete(`${CATALOG_BASE}/admin/paquetes/${id}`);
  },
  // Opciones (opcion_servicio + precio)
  async getOpciones(servicioId: string): Promise<any[]> {
    try {
      const response = await apiClient.get(`${CATALOG_BASE}/opciones`, {
        params: { servicio_id: servicioId },
        headers: { 'X-Suppress-Error': '1' },
      });
      return response.data || [];
    } catch (e) {
      // Return empty array on error; caller already handles logging per-item.
      // We suppress global logging via the header above so this won't spam users.
      console.debug('[catalogApi] getOpciones failed (silenced)', servicioId, e);
      return [];
    }
  },

  async createOpcion(data: { servicio_id: string; nombre: string; moneda?: string; monto: number; detalles?: any; }): Promise<any> {
    const url = `${CATALOG_BASE}/admin/opciones`;
    try {
      console.debug('[catalogApi] createOpcion request', url, data);
      const response = await apiClient.post(url, data);
      console.debug('[catalogApi] createOpcion response', response && response.data);
      return response.data;
    } catch (e) {
      console.error('[catalogApi] createOpcion error', e);
      throw e;
    }
  },

  async updateOpcion(id: string, data: { nombre?: string; moneda?: string; monto?: number; detalles?: any; }): Promise<any> {
    const url = `${CATALOG_BASE}/admin/opciones/${id}`;
    try {
      console.debug('[catalogApi] updateOpcion request', url, data);
      const response = await apiClient.put(url, data);
      console.debug('[catalogApi] updateOpcion response', response && response.data);
      return response.data;
    } catch (e) {
      console.error('[catalogApi] updateOpcion error', e);
      throw e;
    }
  },

  async deleteOpcion(id: string): Promise<void> {
    const url = `${CATALOG_BASE}/admin/opciones/${id}`;
    try {
      console.debug('[catalogApi] deleteOpcion request', url);
      await apiClient.delete(url);
    } catch (e) {
      console.error('[catalogApi] deleteOpcion error', e);
      throw e;
    }
  },
};
