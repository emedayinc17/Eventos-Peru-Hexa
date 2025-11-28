import apiClient from './client';
import type { Proveedor, CreateProveedorRequest, ProveedorDisponible, ApiResponse } from '@/types';

const PROVIDERS_BASE = '/proveedores';

export const providersApi = {
  async getProveedores(): Promise<ApiResponse<Proveedor>> {
    const response = await apiClient.get<ApiResponse<Proveedor>>(`${PROVIDERS_BASE}/proveedores`);
    return response.data;
  },

  async getProveedor(id: number): Promise<Proveedor> {
    const response = await apiClient.get<Proveedor>(`${PROVIDERS_BASE}/proveedores/${id}`);
    return response.data;
  },

  async createProveedor(data: CreateProveedorRequest): Promise<Proveedor> {
    const response = await apiClient.post<Proveedor>(`${PROVIDERS_BASE}/proveedores`, data);
    return response.data;
  },

  async updateProveedor(id: number, data: Partial<CreateProveedorRequest>): Promise<Proveedor> {
    const response = await apiClient.put<Proveedor>(`${PROVIDERS_BASE}/proveedores/${id}`, data);
    return response.data;
  },

  async deleteProveedor(id: number): Promise<void> {
    await apiClient.delete(`${PROVIDERS_BASE}/proveedores/${id}`);
  },

  async getProveedoresDisponibles(fechaEvento: string): Promise<ApiResponse<ProveedorDisponible>> {
    const response = await apiClient.get<ApiResponse<ProveedorDisponible>>(
      `${PROVIDERS_BASE}/disponibles`,
      { params: { fecha_evento: fechaEvento } }
    );
    return response.data;
  },
};
