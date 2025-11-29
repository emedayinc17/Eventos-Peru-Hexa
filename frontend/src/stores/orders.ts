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
  async function fetchPedidos(usuarioId?: number | string, estado?: string, admin = false): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      const response = await ordersApi.getPedidos(usuarioId, estado, admin);
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

  async function fetchPedido(id: number | string): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      currentPedido.value = await ordersApi.getPedido(id, true);
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

  async function updatePedido(id: number | string, data: UpdatePedidoRequest): Promise<Pedido> {
    loading.value = true;
    error.value = null;

    try {
      const updated = await ordersApi.updatePedido(id, data);
      const index = pedidos.value.findIndex(p => String(p.id) === String(id));
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

  async function deletePedido(id: number | string): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      await ordersApi.deletePedido(id);
      // Update local state assuming CANCELADO (status 5)
      const index = pedidos.value.findIndex(p => String(p.id) === String(id));
      if (index !== -1) {
        pedidos.value[index].estado = 5; // CANCELADO
      }
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
