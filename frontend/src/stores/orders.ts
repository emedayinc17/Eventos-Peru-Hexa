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

  // Cache for pedido details
  const pedidoDetailsCache = ref<Record<string, { data: PedidoDetalle, timestamp: number }>>({});
  const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

  async function fetchPedido(id: number | string, admin = false, forceRefresh = false): Promise<void> {
    const pedidoId = String(id);
    const now = Date.now();

    // Check cache
    if (!forceRefresh && pedidoDetailsCache.value[pedidoId] && (now - pedidoDetailsCache.value[pedidoId].timestamp < CACHE_TTL)) {
      currentPedido.value = pedidoDetailsCache.value[pedidoId].data;
      return;
    }

    loading.value = true;
    error.value = null;

    try {
      const data = await ordersApi.getPedido(id, admin);
      currentPedido.value = data;
      // Update cache
      pedidoDetailsCache.value[pedidoId] = { data, timestamp: now };
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

      // Invalidate cache for this pedido
      if (pedidoDetailsCache.value[String(id)]) {
        delete pedidoDetailsCache.value[String(id)];
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

      // Invalidate cache
      if (pedidoDetailsCache.value[String(id)]) {
        delete pedidoDetailsCache.value[String(id)];
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

      // Invalidate cache so next fetch gets fresh data
      if (pedidoDetailsCache.value[String(id)]) {
        delete pedidoDetailsCache.value[String(id)];
      }

      // Result contains updated pedido info, we might want to refresh the current pedido
      if (currentPedido.value && String((currentPedido.value as any).pedido?.id || (currentPedido.value as any).id) === String(id)) {
        // Refresh details (force refresh)
        await fetchPedido(id, true, true);
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

      // Invalidate cache
      if (pedidoDetailsCache.value[String(id)]) {
        delete pedidoDetailsCache.value[String(id)];
      }

      // Refresh details
      if (currentPedido.value && String((currentPedido.value as any).pedido?.id || (currentPedido.value as any).id) === String(id)) {
        await fetchPedido(id, true, true);
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
