import { defineStore } from 'pinia';
import { ref } from 'vue';
import { ordersApi } from '@/api';
import type { Pedido, CreatePedidoRequest, UpdatePedidoRequest, PedidoDetalle } from '@/types';

export const useOrdersStore = defineStore('orders', () => {
  // State
  const pedidos = ref<Pedido[]>([]);
  const currentPedido = ref<PedidoDetalle | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Draft order state (para wizard)
  const draftOrder = ref<Partial<CreatePedidoRequest>>({});

  // Actions
  async function fetchPedidos(usuarioId?: number, estado?: string): Promise<void> {
    loading.value = true;
    error.value = null;
    
    try {
      // Try client 'mis pedidos' first; if empty and caller wants admin, caller can pass admin=true
      const response = await ordersApi.getPedidos(usuarioId, estado);
      // response may be { items: [...] } or array or ApiResponse
      if (Array.isArray(response)) {
        pedidos.value = response;
      } else if (response && response.items) {
        pedidos.value = response.items;
      } else if (response && response.data) {
        pedidos.value = response.data;
      } else {
        pedidos.value = [];
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al cargar pedidos';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchPedido(id: number): Promise<void> {
    loading.value = true;
    error.value = null;
    
    try {
      currentPedido.value = await ordersApi.getPedido(id);
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al cargar pedido';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createPedido(data: CreatePedidoRequest): Promise<Pedido> {
    loading.value = true;
    error.value = null;
    
    try {
      const newPedido = await ordersApi.createPedido(data);
      pedidos.value.unshift(newPedido);
      clearDraft();
      return newPedido;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al crear pedido';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updatePedido(id: number, data: UpdatePedidoRequest): Promise<Pedido> {
    loading.value = true;
    error.value = null;
    
    try {
      const updated = await ordersApi.updatePedido(id, data);
      const index = pedidos.value.findIndex(p => p.id === id);
      if (index !== -1) {
        pedidos.value[index] = updated;
      }
      return updated;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al actualizar pedido';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deletePedido(id: number): Promise<void> {
    loading.value = true;
    error.value = null;
    
    try {
      await ordersApi.deletePedido(id);
      pedidos.value = pedidos.value.filter(p => p.id !== id);
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al eliminar pedido';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Draft management (para wizard de creación)
  function updateDraft(data: Partial<CreatePedidoRequest>): void {
    draftOrder.value = { ...draftOrder.value, ...data };
  }

  function clearDraft(): void {
    draftOrder.value = {};
  }

  function getDraft(): Partial<CreatePedidoRequest> {
    return draftOrder.value;
  }

  return {
    // State
    pedidos,
    currentPedido,
    loading,
    error,
    draftOrder,
    // Actions
    fetchPedidos,
    fetchPedido,
    createPedido,
    updatePedido,
    deletePedido,
    updateDraft,
    clearDraft,
    getDraft,
  };
});
