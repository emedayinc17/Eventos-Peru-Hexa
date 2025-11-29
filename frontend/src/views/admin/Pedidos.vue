<template>
  <div class="w-full h-full p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Gestión de Pedidos</h1>
        <p class="text-gray-600 text-sm mt-1">Supervisión y control de todas las solicitudes de eventos</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
      <div class="flex flex-wrap gap-4 items-center">
        <div class="flex-1 min-w-[200px] md:max-w-md">
          <SearchBar 
            v-model="searchQuery"
            placeholder="Buscar por ID, cliente o email..."
          />
        </div>
        <select
          v-model="filterEstado"
          class="rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
          <option value="">Todos los estados</option>
          <option value="PENDIENTE">Pendiente</option>
          <option value="CONFIRMADO">Confirmado</option>
          <option value="EN_PROGRESO">En Progreso</option>
          <option value="COMPLETADO">Completado</option>
          <option value="CANCELADO">Cancelado</option>
        </select>
        <Button variant="secondary" @click="loadPedidos" class="flex items-center gap-2">
          <ArrowPathIcon class="w-4 h-4" />
          Actualizar
        </Button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Cliente</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Evento</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Fecha</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Total</th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="ordersStore.loading">
              <td colspan="7" class="px-6 py-12 text-center">
                <Loading text="Cargando pedidos..." />
              </td>
            </tr>
            <tr v-else-if="filteredPedidos.length === 0">
              <td colspan="7" class="px-6 py-12 text-center text-gray-500">
                <div class="flex flex-col items-center justify-center">
                  <ClipboardDocumentListIcon class="w-12 h-12 text-gray-300 mb-2" />
                  <p>No se encontraron pedidos</p>
                </div>
              </td>
            </tr>
            <tr v-else v-for="pedido in paginatedPedidos" :key="pedido.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                #{{ pedido.id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ pedido.usuario_nombre || `Usuario #${pedido.usuario_id}` }}</div>
                <div class="text-xs text-gray-500" v-if="pedido.usuario_email">{{ pedido.usuario_email }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ pedido.tipo_evento_nombre }}
                <span class="text-xs text-gray-400 block">{{ pedido.num_invitados }} invitados</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(pedido.fecha_evento) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <select
                  v-model="pedido.estado"
                  @change="updateEstado(pedido)"
                  class="text-xs rounded-full border-0 font-medium px-3 py-1 cursor-pointer focus:ring-2 focus:ring-offset-1 focus:ring-indigo-500"
                  :class="getEstadoClass(pedido.estado)"
                >
                  <option :value="0">Borrador</option>
                  <option :value="1">Cotizado</option>
                  <option :value="2">Aprobado</option>
                  <option :value="3">Asignado</option>
                  <option :value="4">Confirmado</option>
                  <option :value="5">Cancelado</option>
                  <option :value="6">Completado</option>
                </select>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                S/ {{ pedido.total?.toFixed(2) || '0.00' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end gap-2">
                  <button
                    @click="viewDetails(pedido)"
                    class="p-1 text-gray-400 hover:text-primary-600 transition-colors rounded-full hover:bg-primary-50"
                    title="Ver detalles"
                  >
                    <EyeIcon class="w-5 h-5" />
                  </button>
                  <button
                    @click="confirmDelete(pedido)"
                    class="p-1 text-gray-400 hover:text-red-600 transition-colors rounded-full hover:bg-red-50"
                    title="Cancelar pedido"
                  >
                    <XCircleIcon class="w-5 h-5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- Pagination -->
    <div class="bg-gray-50 px-6 py-3 border-t border-gray-200 flex items-center justify-between mt-3">
      <div class="text-sm text-gray-500">
        Mostrando {{ (currentPage - 1) * pageSize + 1 }} a {{ Math.min(currentPage * pageSize, filteredPedidos.length) }} de {{ filteredPedidos.length }} pedidos
      </div>
      <div class="flex gap-2">
        <Button 
          variant="secondary" 
          size="sm" 
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          Anterior
        </Button>
        <Button 
          variant="secondary" 
          size="sm" 
          :disabled="currentPage >= totalPages"
          @click="currentPage++"
        >
          Siguiente
        </Button>
      </div>
    </div>
    <!-- Details Modal -->
    <Modal 
      :open="showDetailsModal" 
      @close="showDetailsModal = false"
      title="Detalles del Pedido" 
      maxWidth="2xl"
    >
      <div v-if="selectedPedido" class="space-y-6">
        <!-- Header Info -->
        <div class="flex justify-between items-start border-b pb-4">
          <div>
            <h3 class="text-lg font-medium text-gray-900">Pedido #{{ selectedPedido.id }}</h3>
            <p class="text-sm text-gray-500">{{ formatDateTime(selectedPedido.created_at) }}</p>
          </div>
          <span 
            class="px-3 py-1 rounded-full text-sm font-medium"
            :class="getEstadoBadgeClass(selectedPedido.estado)"
          >
            {{ estadoLabels[selectedPedido.estado] || 'Desconocido' }}
          </span>
        </div>

        <!-- Grid Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <div>
              <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Cliente</h4>
              <p class="font-medium text-gray-900">{{ selectedPedido.usuario_nombre || `Usuario #${selectedPedido.usuario_id}` }}</p>
              <p class="text-sm text-gray-500">{{ selectedPedido.usuario_email || '-' }}</p>
            </div>
            <div>
              <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Evento</h4>
              <p class="font-medium text-gray-900">{{ selectedPedido.tipo_evento_nombre }}</p>
              <p class="text-sm text-gray-500">{{ selectedPedido.num_invitados }} invitados</p>
            </div>
          </div>
          
          <div class="space-y-4">
            <div>
              <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Fecha Programada</h4>
              <p class="font-medium text-gray-900">{{ formatDate(selectedPedido.fecha_evento) }}</p>
            </div>
            <div>
              <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Total Estimado</h4>
              <p class="text-xl font-bold text-primary-600">S/ {{ selectedPedido.total?.toFixed(2) }}</p>
            </div>
          </div>
        </div>

        <div v-if="selectedPedido.comentarios" class="bg-gray-50 p-4 rounded-lg border border-gray-100">
          <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Comentarios Especiales</h4>
          <p class="text-gray-700 italic text-sm">"{{ selectedPedido.comentarios }}"</p>
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t">
          <Button variant="secondary" @click="showDetailsModal = false">
            Cerrar
          </Button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useOrdersStore } from '@/stores/orders';
import { useUiStore } from '@/stores/ui';
import Button from '@/components/common/Button.vue';
import SearchBar from '@/components/common/SearchBar.vue';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { EyeIcon, XCircleIcon, ArrowPathIcon, ClipboardDocumentListIcon } from '@heroicons/vue/24/outline';

const ordersStore = useOrdersStore();
const ui = useUiStore();

const searchQuery = ref('');
const filterEstado = ref<number | ''>('');
const showDetailsModal = ref(false);
const selectedPedido = ref<any>(null);
// Pagination
const currentPage = ref(1);
const pageSize = ref(10);

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
  
  if (filterEstado.value !== '') {
    result = result.filter(p => p.estado === filterEstado.value);
  }
  
  return result;
});

// Paginated pedidos (client-side pagination)
const paginatedPedidos = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredPedidos.value.slice(start, end);
});

const totalPages = computed(() => Math.ceil(filteredPedidos.value.length / pageSize.value));

// Reset page when filters/search change
watch([searchQuery, filterEstado], () => {
  currentPage.value = 1;
});

const estadoLabels: Record<number, string> = {
  0: 'Borrador',
  1: 'Cotizado',
  2: 'Aprobado',
  3: 'Asignado',
  4: 'Confirmado',
  5: 'Cancelado',
  6: 'Completado'
};

// Helper functions
const getEstadoClass = (estado: number) => {
  const classes: Record<number, string> = {
    0: 'bg-gray-100 text-gray-800', // Draft
    1: 'bg-yellow-100 text-yellow-800', // Cotizado
    2: 'bg-blue-50 text-blue-800', // Aprobado
    3: 'bg-indigo-100 text-indigo-800', // Asignado
    4: 'bg-green-100 text-green-800', // Confirmado
    5: 'bg-red-100 text-red-800', // Cancelado
    6: 'bg-purple-100 text-purple-800', // Completado
  };
  return classes[estado] || 'bg-gray-100 text-gray-800';
};

const getEstadoBadgeClass = (estado: number) => {
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

const updateEstado = async (pedido: any) => {
  try {
    await ordersStore.updatePedido(pedido.id, { estado: Number(pedido.estado) });
    ui.showToast('Estado actualizado', 'success');
  } catch (error: any) {
    const msg = error.response?.data?.detail?.message || error.response?.data?.detail || error.message;
    ui.showToast('Error al actualizar estado: ' + msg, 'error');
    await loadPedidos(); // Reload to revert
  }
};

const viewDetails = (pedido: any) => {
  selectedPedido.value = pedido;
  showDetailsModal.value = true;
};

const confirmDelete = async (pedido: any) => {
  console.debug('[Pedidos] confirmDelete invoked', pedido);
  ui.showToast('Intentando cancelar pedido: ' + pedido.id, 'info', 1500);
  // Backend does not support DELETE for pedidos; use estado=CANCELADO (5)
  const ok = await ui.showConfirmWithFallback(`¿Está seguro de cancelar el pedido #${pedido.id}?`, 'Cancelar pedido');
  if (ok) {
    try {
      await ordersStore.updatePedido(pedido.id, { estado: 5 });
      await loadPedidos();
      ui.showToast('Pedido cancelado correctamente', 'success');
    } catch (error: any) {
      const msg = error.response?.data?.detail?.message || error.response?.data?.detail || error.message;
      ui.showToast('Error al cancelar: ' + msg, 'error');
    }
  }
};

const loadPedidos = async () => {
  // Load admin view of pedidos
  await ordersStore.fetchPedidos(undefined, undefined, true);
};

onMounted(async () => {
  await loadPedidos();
});
</script>
