<template>
  <div class="max-w-7xl mx-auto py-8 px-4">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Gestión de Pedidos</h1>
        <p class="text-gray-600 mt-1">Administre todos los pedidos del sistema</p>
      </div>
    </div>

    <!-- Filters -->
    <Card class="mb-6">
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <SearchBar 
            v-model="searchQuery"
            placeholder="Buscar por ID o usuario..."
          />
        </div>
        <select
          v-model="filterEstado"
          class="rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        >
          <option value="">Todos los estados</option>
          <option value="PENDIENTE">Pendiente</option>
          <option value="CONFIRMADO">Confirmado</option>
          <option value="EN_PROGRESO">En Progreso</option>
          <option value="COMPLETADO">Completado</option>
          <option value="CANCELADO">Cancelado</option>
        </select>
        <Button variant="secondary" @click="loadPedidos">
          🔄 Actualizar
        </Button>
      </div>
    </Card>

    <!-- Table -->
    <Card :padding="false">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Cliente
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tipo Evento
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Fecha Evento
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Invitados
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="ordersStore.loading">
              <td colspan="8" class="px-6 py-12 text-center">
                <Loading text="Cargando pedidos..." />
              </td>
            </tr>
            <tr v-else-if="filteredPedidos.length === 0">
              <td colspan="8" class="px-6 py-12 text-center text-gray-500">
                No se encontraron pedidos
              </td>
            </tr>
            <tr v-else v-for="pedido in filteredPedidos" :key="pedido.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                #{{ pedido.id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ pedido.usuario_nombre || `Usuario #${pedido.usuario_id}` }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ pedido.tipo_evento_nombre }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(pedido.fecha_evento) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ pedido.num_invitados }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <select
                  v-model="pedido.estado"
                  @change="updateEstado(pedido)"
                  class="text-sm rounded-full border-0 font-medium px-3 py-1"
                  :class="getEstadoClass(pedido.estado)"
                >
                  <option value="PENDIENTE">Pendiente</option>
                  <option value="CONFIRMADO">Confirmado</option>
                  <option value="EN_PROGRESO">En Progreso</option>
                  <option value="COMPLETADO">Completado</option>
                  <option value="CANCELADO">Cancelado</option>
                </select>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary-600">
                S/ {{ pedido.total?.toFixed(2) || '0.00' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                <button
                  @click="viewDetails(pedido)"
                  class="text-primary-600 hover:text-primary-900"
                >
                  Ver
                </button>
                <button
                  @click="confirmDelete(pedido)"
                  class="text-red-600 hover:text-red-900"
                >
                  Eliminar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Details Modal -->
    <Modal v-model="showDetailsModal" title="Detalles del Pedido" max-width="2xl">
      <div v-if="selectedPedido" class="space-y-4">
        <div class="grid grid-cols-2 gap-4 pb-4 border-b">
          <div>
            <p class="text-sm text-gray-500">Pedido #</p>
            <p class="font-medium">{{ selectedPedido.id }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Estado</p>
            <span 
              class="inline-block px-3 py-1 rounded-full text-sm font-medium"
              :class="getEstadoBadgeClass(selectedPedido.estado)"
            >
              {{ selectedPedido.estado }}
            </span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Cliente</p>
            <p class="font-medium">{{ selectedPedido.usuario_nombre || `Usuario #${selectedPedido.usuario_id}` }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Email</p>
            <p class="font-medium">{{ selectedPedido.usuario_email || '-' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Tipo de Evento</p>
            <p class="font-medium">{{ selectedPedido.tipo_evento_nombre }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Fecha del Evento</p>
            <p class="font-medium">{{ formatDate(selectedPedido.fecha_evento) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Número de Invitados</p>
            <p class="font-medium">{{ selectedPedido.num_invitados }} personas</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Total</p>
            <p class="font-bold text-primary-600 text-lg">S/ {{ selectedPedido.total?.toFixed(2) }}</p>
          </div>
        </div>

        <div v-if="selectedPedido.comentarios" class="pb-4 border-b">
          <p class="text-sm text-gray-500 mb-1">Comentarios Especiales</p>
          <p class="text-gray-700 italic">"{{ selectedPedido.comentarios }}"</p>
        </div>

        <div class="pb-4 border-b">
          <p class="text-sm text-gray-500 mb-2">Creado el</p>
          <p class="font-medium">{{ formatDateTime(selectedPedido.created_at) }}</p>
        </div>

        <div class="flex justify-end gap-3 pt-4">
          <Button variant="secondary" @click="showDetailsModal = false">
            Cerrar
          </Button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useOrdersStore } from '@/stores/orders';
import { useUiStore } from '@/stores/ui';
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';
import SearchBar from '@/components/common/SearchBar.vue';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const ordersStore = useOrdersStore();
const ui = useUiStore();

const searchQuery = ref('');
const filterEstado = ref('');
const showDetailsModal = ref(false);
const selectedPedido = ref<any>(null);

// Filtered pedidos
const filteredPedidos = computed(() => {
  let result = ordersStore.pedidos;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(p => 
      p.id.toString().includes(query) ||
      p.usuario_nombre?.toLowerCase().includes(query) ||
      p.usuario_email?.toLowerCase().includes(query)
    );
  }
  
  if (filterEstado.value) {
    result = result.filter(p => p.estado === filterEstado.value);
  }
  
  return result;
});

// Helper functions
const getEstadoClass = (estado: string) => {
  const classes: Record<string, string> = {
    PENDIENTE: 'bg-yellow-100 text-yellow-800',
    CONFIRMADO: 'bg-green-100 text-green-800',
    EN_PROGRESO: 'bg-blue-100 text-blue-800',
    COMPLETADO: 'bg-purple-100 text-purple-800',
    CANCELADO: 'bg-red-100 text-red-800',
  };
  return classes[estado] || 'bg-gray-100 text-gray-800';
};

const getEstadoBadgeClass = (estado: string) => {
  return getEstadoClass(estado);
};

const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return '';
  try {
    return format(new Date(dateStr), 'd MMM yyyy', { locale: es });
  } catch {
    return dateStr;
  }
};

const formatDateTime = (dateStr: string | undefined) => {
  if (!dateStr) return '';
  try {
    return format(new Date(dateStr), "d 'de' MMMM 'de' yyyy, HH:mm", { locale: es });
  } catch {
    return dateStr;
  }
};

// Map UI state labels to backend numeric codes
const estadoMap: Record<string, number> = {
  PENDIENTE: 0,
  CONFIRMADO: 2,
  EN_PROGRESO: 3,
  COMPLETADO: 4,
  CANCELADO: 5,
};

const updateEstado = async (pedido: any) => {
  try {
    const codigo = estadoMap[pedido.estado] ?? null;
    if (codigo === null) throw new Error('Estado inválido');
    await ordersStore.updatePedido(pedido.id, { estado: codigo });
  } catch (error: any) {
    ui.showToast('Error al actualizar estado: ' + (error.response?.data?.detail || error.message), 'error');
    await loadPedidos(); // Reload to revert
  }
};

const viewDetails = (pedido: any) => {
  selectedPedido.value = pedido;
  showDetailsModal.value = true;
};

const confirmDelete = async (pedido: any) => {
  // Backend does not support DELETE for pedidos; use estado=CANCELADO
  const ok = await ui.showConfirm(`¿Está seguro de cancelar el pedido #${pedido.id}?`, 'Cancelar pedido');
  if (ok) {
    try {
      await ordersStore.updatePedido(pedido.id, { estado: estadoMap.CANCELADO });
      await loadPedidos();
      ui.showToast('Pedido cancelado correctamente', 'success');
    } catch (error: any) {
      ui.showToast('Error al cancelar: ' + (error.response?.data?.detail || error.message), 'error');
    }
  }
};

const loadPedidos = async () => {
  await ordersStore.fetchPedidos(); // Load all pedidos (no user filter)
};

onMounted(async () => {
  await loadPedidos();
});
</script>
