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

  // Draft order state (para wizard) - inicializar con valores por defecto
  const defaultDraft: Partial<CreatePedidoRequest> = {
    tipo_evento_id: null,
    paquete_id: null,
    fecha_evento: undefined,
    num_personas: 0,
    num_invitados: 0,
    servicios_adicionales: [],
    comentarios: '',
    ubicacion: '',
    hora_inicio: '',
    hora_fin: '',
  };

  const draftOrder = ref<Partial<CreatePedidoRequest>>({ ...defaultDraft });

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

  async function fetchPedido(id: number | string, admin = false): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      currentPedido.value = await ordersApi.getPedido(id, admin);
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
      // Ensure the newly created pedido has an initial estado (first state)
      if (newPedido && (newPedido as any).estado === undefined) {
        // Use string 'PENDIENTE' as initial display state; backend should override when available
        (newPedido as any).estado = 'PENDIENTE';
      }
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
        // Merge update into existing to preserve enriched fields (like cliente_nombre)
        pedidos.value[index] = { ...pedidos.value[index], ...updated };
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

  async function addItems(id: number | string, items: any[]): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      await ordersApi.addItems(id, items);
      // Result contains updated pedido info, we might want to refresh the current pedido
      if (currentPedido.value && String((currentPedido.value as any).pedido?.id || (currentPedido.value as any).id) === String(id)) {
        // Refresh details
        await fetchPedido(id);
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al agregar items';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteItems(id: number | string, itemIds: string[]): Promise<void> {
    loading.value = true;
    error.value = null;
    try {
      await ordersApi.deleteItems(id, itemIds);
      // Refresh details
      if (currentPedido.value && String((currentPedido.value as any).pedido?.id || (currentPedido.value as any).id) === String(id)) {
        await fetchPedido(id);
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al eliminar items';
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
    draftOrder.value = { ...defaultDraft };
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
    addItems,
    deleteItems,
    updateDraft,
    clearDraft,
    getDraft,
  };
});
