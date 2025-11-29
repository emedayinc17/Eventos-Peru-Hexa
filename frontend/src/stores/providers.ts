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

  // LocalStorage helpers
  function loadFromStorage() {
    try {
      const storedProveedores = localStorage.getItem('providers.list');
      if (storedProveedores) proveedores.value = JSON.parse(storedProveedores);

      const storedTimestamp = localStorage.getItem('providers.timestamp');
      if (storedTimestamp) lastFetch.value = Number(storedTimestamp);
    } catch (e) {
      console.error('Error loading providers from localStorage', e);
    }
  }

  function saveToStorage() {
    try {
      localStorage.setItem('providers.list', JSON.stringify(proveedores.value));
      localStorage.setItem('providers.timestamp', String(lastFetch.value));
    } catch (e) {
      console.error('Error saving providers to localStorage', e);
    }
  }

  // Initialize from storage
  loadFromStorage();

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
        proveedores.value = raw.map((p: any) => ({
          ...p,
          // normalize active flag: backend uses `status` (1 = active)
          activo: p.activo !== undefined ? p.activo : (p.status !== undefined ? Number(p.status) === 1 : !!p.activo),
        }));
      } else if (raw && (raw.data || raw.items || raw.proveedores)) {
        const arr = raw.data || raw.items || raw.proveedores || [];
        proveedores.value = arr.map((p: any) => ({
          ...p,
          activo: p.activo !== undefined ? p.activo : (p.status !== undefined ? Number(p.status) === 1 : !!p.activo),
        }));
      } else {
        proveedores.value = [];
      }
      lastFetch.value = now;
      saveToStorage();
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
      // Force refresh to update list and storage
      await fetchProveedores(true);
      return newProveedor;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al crear proveedor';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateProveedor(id: number | string, data: Partial<CreateProveedorRequest>): Promise<Proveedor> {
    loading.value = true;
    error.value = null;

    try {
      const updated = await providersApi.updateProveedor(id, data);
      // Force refresh to update list and storage
      await fetchProveedores(true);
      return updated;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al actualizar proveedor';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteProveedor(id: number | string): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      await providersApi.deleteProveedor(id);
      // Force refresh to update list and storage
      await fetchProveedores(true);
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
