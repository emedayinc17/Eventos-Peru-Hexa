import apiClient from './client';
import type { Proveedor, CreateProveedorRequest, ProveedorDisponible, ApiResponse } from '@/types';

const PROVIDERS_BASE = '/proveedores';
const ADMIN_BASE = '/proveedores/v1/admin/proveedores';

export const providersApi = {
  async getProveedores(): Promise<ApiResponse<Proveedor>> {
    // GET /proveedores/v1/admin/proveedores
    const response = await apiClient.get<ApiResponse<Proveedor>>(`${ADMIN_BASE}`);
    return response.data;
  },

  async getProveedor(id: number | string): Promise<Proveedor> {
    // GET /proveedores/v1/admin/proveedores/{id} - Nota: Este endpoint no existe explícitamente en router_admin, 
    // pero getProveedores devuelve la lista. Si se necesita detalle individual, habría que agregarlo.
    // Por ahora, asumimos que se usa la lista.
    // Si se requiere, se puede filtrar en cliente o agregar endpoint.
    // Dejaremos esto apuntando a admin por si se implementa.
    const response = await apiClient.get<Proveedor>(`${ADMIN_BASE}/${id}`);
    return response.data;
  },

  async createProveedor(data: CreateProveedorRequest): Promise<Proveedor> {
    const response = await apiClient.post<Proveedor>(`${ADMIN_BASE}`, data);
    return response.data;
  },

  async updateProveedor(id: number | string, data: Partial<CreateProveedorRequest>): Promise<Proveedor> {
    const response = await apiClient.put<Proveedor>(`${ADMIN_BASE}/${id}`, data);
    return response.data;
  },

  async deleteProveedor(id: number | string): Promise<void> {
    await apiClient.delete(`${ADMIN_BASE}/${id}`);
  },

  async getProveedoresDisponibles(servicioId: string, fechaEvento: string): Promise<ApiResponse<ProveedorDisponible>> {
    // GET /proveedores/v1/proveedores/disponibles (público)
    const params: any = { fecha: fechaEvento };
    if (servicioId) params.servicio_id = servicioId;
    const response = await apiClient.get<ApiResponse<ProveedorDisponible>>(
      `${PROVIDERS_BASE}/v1/proveedores/disponibles`,
      { params }
    );
    return response.data;
  },

  async getAllProveedoresPublic(): Promise<any[]> {
    // GET /proveedores/v1/proveedores (public list)
    const response = await apiClient.get(`${PROVIDERS_BASE}/v1/proveedores`);
    return response.data || [];
  },
};
