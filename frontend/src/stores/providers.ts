import { defineStore } from 'pinia';
import { ref } from 'vue';
import { providersApi } from '@/api';
import type { Proveedor, CreateProveedorRequest } from '@/types';

export const useProvidersStore = defineStore('providers', () => {
  // State
  const proveedores = ref<Proveedor[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Cache timestamp
  const lastFetch = ref<number>(0);
  const CACHE_TTL = 5 * 60 * 1000; // 5 minutos

  // Actions
  async function fetchProveedores(forceRefresh = false): Promise<void> {
    const now = Date.now();
    if (!forceRefresh && proveedores.value.length > 0 && now - lastFetch.value < CACHE_TTL) {
      return; // Usar cache
    }

    loading.value = true;
    error.value = null;
    
    try {
      const response = await providersApi.getProveedores();
      // Handle different response formats
      const raw: any = response;
      if (Array.isArray(raw)) {
        proveedores.value = raw;
      } else if (raw && (raw.data || raw.items || raw.proveedores)) {
        proveedores.value = raw.data || raw.items || raw.proveedores || [];
      } else {
        proveedores.value = [];
      }
      lastFetch.value = now;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al cargar proveedores';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createProveedor(data: CreateProveedorRequest): Promise<Proveedor> {
    loading.value = true;
    error.value = null;
    
    try {
      const newProveedor = await providersApi.createProveedor(data);
      proveedores.value.push(newProveedor);
      return newProveedor;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al crear proveedor';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateProveedor(id: number, data: Partial<CreateProveedorRequest>): Promise<Proveedor> {
    loading.value = true;
    error.value = null;
    
    try {
      const updated = await providersApi.updateProveedor(id, data);
      const index = proveedores.value.findIndex(p => p.id === id);
      if (index !== -1) {
        proveedores.value[index] = updated;
      }
      return updated;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al actualizar proveedor';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteProveedor(id: number): Promise<void> {
    loading.value = true;
    error.value = null;
    
    try {
      await providersApi.deleteProveedor(id);
      proveedores.value = proveedores.value.filter(p => p.id !== id);
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al eliminar proveedor';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    // State
    proveedores,
    loading,
    error,
    // Actions
    fetchProveedores,
    createProveedor,
    updateProveedor,
    deleteProveedor,
  };
});
