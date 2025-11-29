<template>
  <div class="max-w-7xl mx-auto py-8 px-4">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Mis Pedidos</h1>
        <p class="text-gray-600 mt-1">Historial y estado de tus pedidos</p>
      </div>
      <Button variant="primary" @click="router.push('/cliente/pedido/nuevo')">
        + Crear Nuevo Pedido
      </Button>
    </div>

    <!-- Filters -->
    <Card class="mb-6">
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Filtrar por Estado
          </label>
          <select
            v-model="filterEstado"
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          >
            <option value="">Todos</option>
            <option value="PENDIENTE">Pendiente</option>
            <option value="CONFIRMADO">Confirmado</option>
            <option value="EN_PROGRESO">En Progreso</option>
            <option value="COMPLETADO">Completado</option>
            <option value="CANCELADO">Cancelado</option>
          </select>
        </div>
        <div class="flex items-end">
          <Button variant="secondary" @click="loadPedidos">
            🔄 Actualizar
          </Button>
        </div>
      </div>
    </Card>

    <!-- Loading State -->
    <div v-if="ordersStore.loading" class="flex justify-center py-12">
      <Loading size="lg" text="Cargando pedidos..." />
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredPedidos.length === 0" class="text-center py-12">
      <div class="mx-auto h-24 w-24 text-gray-400 mb-4">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No tienes pedidos</h3>
      <p class="text-gray-500 mb-6">Comienza creando tu primer pedido</p>
      <Button variant="primary" @click="router.push('/cliente/pedido/nuevo')">
        Crear Pedido
      </Button>
    </div>

    <!-- Pedidos List -->
    <div v-else class="space-y-4">
      <Card 
        v-for="pedido in filteredPedidos" 
        :key="pedido.id"
        class="hover:shadow-lg transition-shadow"
      >
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <!-- Left: Info -->
          <div class="flex-1">
            <div class="flex items-start justify-between mb-2">
              <div>
                <h3 class="text-lg font-semibold text-gray-900">
                  {{ getEventIcon(pedido.tipo_evento_nombre) }} {{ pedido.tipo_evento_nombre }}
                </h3>
                <p class="text-sm text-gray-500">Pedido #{{ pedido.id }}</p>
              </div>
              <span 
                class="px-3 py-1 rounded-full text-sm font-medium"
                :class="getEstadoBadgeClass(pedido.estado)"
              >
                {{ pedido.estado }}
              </span>
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div>
                <span class="text-gray-500">Fecha Evento:</span>
                <p class="font-medium">{{ formatDate(pedido.fecha_evento) }}</p>
              </div>
              <div>
                <span class="text-gray-500">Invitados:</span>
                <p class="font-medium">{{ pedido.num_invitados }} personas</p>
              </div>
              <div>
                <span class="text-gray-500">Total:</span>
                <p class="font-bold text-primary-600">S/ {{ pedido.total?.toFixed(2) || '0.00' }}</p>
              </div>
              <div>
                <span class="text-gray-500">Creado:</span>
                <p class="font-medium">{{ formatDate(pedido.created_at) }}</p>
              </div>
            </div>
          </div>

          <!-- Right: Actions -->
          <div class="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" @click="viewDetails(pedido)">
              Ver Detalles
            </Button>
            <Button 
              v-if="pedido.estado === 'PENDIENTE'" 
              variant="danger" 
              size="sm"
              @click="confirmCancel(pedido)"
            >
              Cancelar
            </Button>
          </div>
        </div>
      </Card>
    </div>

    <!-- Details Modal -->
    <Modal v-model:open="showDetailsModal" title="Detalles del Pedido" max-width="2xl">
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
import { useRouter } from 'vue-router';
import { useOrdersStore } from '@/stores/orders';
import { useAuthStore } from '@/stores/auth';
import { useUiStore } from '@/stores/ui';
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const router = useRouter();
const ordersStore = useOrdersStore();
const authStore = useAuthStore();
const ui = useUiStore();

const filterEstado = ref('');
const showDetailsModal = ref(false);
const selectedPedido = ref<any>(null);

// Filtered pedidos
const filteredPedidos = computed(() => {
  if (!filterEstado.value) {
    return ordersStore.pedidos;
  }
  return ordersStore.pedidos.filter(p => p.estado === filterEstado.value);
});

// Helper functions
const getEstadoBadgeClass = (estado: string) => {
  const classes: Record<string, string> = {
    PENDIENTE: 'bg-yellow-100 text-yellow-800',
    CONFIRMADO: 'bg-green-100 text-green-800',
    EN_PROGRESO: 'bg-blue-100 text-blue-800',
    COMPLETADO: 'bg-purple-100 text-purple-800',
    CANCELADO: 'bg-red-100 text-red-800',
  };
  return classes[estado] || 'bg-gray-100 text-gray-800';
};

const getEventIcon = (tipoEvento: string) => {
  const icons: Record<string, string> = {
    'Boda': '💒',
    'Quinceañera': '👗',
    'Cumpleaños': '🎂',
    'Corporativo': '🏢',
    'Conferencia': '🎤',
  };
  return icons[tipoEvento] || '🎉';
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

const viewDetails = (pedido: any) => {
  selectedPedido.value = pedido;
  showDetailsModal.value = true;
};

const confirmCancel = async (pedido: any) => {
  const ok = await ui.showConfirmWithFallback(`¿Está seguro de cancelar el pedido #${pedido.id}?`, 'Cancelar pedido');
  if (!ok) return;
  try {
    // map cancel to deletePedido which sets estado=CANCELADO on backend
    await ordersStore.deletePedido(pedido.id);
    await loadPedidos();
    ui.showToast('Pedido cancelado', 'success');
  } catch (error: any) {
    ui.showToast('Error al cancelar el pedido: ' + (error.response?.data?.detail || error.message), 'error');
  }
};

const loadPedidos = async () => {
  if (authStore.user) {
    await ordersStore.fetchPedidos(authStore.user.id);
  }
};

onMounted(async () => {
  await loadPedidos();
});
</script>
