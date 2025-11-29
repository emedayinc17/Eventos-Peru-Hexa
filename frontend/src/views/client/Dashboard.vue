<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useOrdersStore } from '@/stores/orders';
import { useRouter } from 'vue-router';
import { 
  CalendarIcon, 
  CurrencyDollarIcon, 
  CheckCircleIcon,
  ClockIcon,
  PlusIcon 
} from '@heroicons/vue/24/outline';

const authStore = useAuthStore();
const ordersStore = useOrdersStore();
const router = useRouter();

const loading = ref(true);

// Computed properties for statistics
const totalPedidos = computed(() => ordersStore.pedidos.length);

const pedidosPendientes = computed(() => {
  return ordersStore.pedidos.filter(p => 
    p.estado === 1 || p.estado === 2 // PENDIENTE o EN_PROCESO
  ).length;
});

const pedidosCompletados = computed(() => {
  return ordersStore.pedidos.filter(p => p.estado === 4).length; // COMPLETADO
});

const totalGastado = computed(() => {
  return ordersStore.pedidos
    .filter(p => p.estado === 4) // Solo pedidos completados
    .reduce((sum, p) => sum + (p.monto_total || 0), 0);
});

const proximosPedidos = computed(() => {
  return ordersStore.pedidos
    .filter(p => p.estado === 1 || p.estado === 2) // PENDIENTE o EN_PROCESO
    .sort((a, b) => {
      const dateA = new Date(a.fecha_evento || a.created_at);
      const dateB = new Date(b.fecha_evento || b.created_at);
      return dateA.getTime() - dateB.getTime();
    })
    .slice(0, 5); // Mostrar solo los próximos 5
});

// Helper functions
const getEstadoBadgeClass = (estado: number) => {
  const classes = {
    1: 'bg-yellow-100 text-yellow-800',
    2: 'bg-blue-100 text-blue-800',
    3: 'bg-purple-100 text-purple-800',
    4: 'bg-green-100 text-green-800',
    5: 'bg-red-100 text-red-800',
  };
  return classes[estado as keyof typeof classes] || 'bg-gray-100 text-gray-800';
};

const getEstadoText = (estado: number) => {
  const texts = {
    1: 'Pendiente',
    2: 'En Proceso',
    3: 'Confirmado',
    4: 'Completado',
    5: 'Cancelado',
  };
  return texts[estado as keyof typeof texts] || 'Desconocido';
};

const formatDate = (dateString: string) => {
  if (!dateString) return 'Sin fecha';
  const date = new Date(dateString);
  return date.toLocaleDateString('es-PE', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('es-PE', {
    style: 'currency',
    currency: 'PEN',
  }).format(amount);
};

const viewPedido = (pedidoId: number | string) => {
  router.push(`/cliente/pedidos/${pedidoId}`);
};

// Load data on mount
onMounted(async () => {
  try {
    loading.value = true;
    if (authStore.isAuthenticated) {
      await authStore.fetchProfile();
      // Fetch client's pedidos (not admin)
      await ordersStore.fetchPedidos();
    }
  } catch (error) {
    console.error('Error loading dashboard data:', error);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div>
    <div class="mb-4 sm:mb-6">
      <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">
        Bienvenido, {{ authStore.userFullName }}
      </h1>
      <p class="text-sm sm:text-base text-gray-600 mt-1">Panel de Cliente</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 gap-4 sm:gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-6 sm:mb-8">
        <div class="card hover:shadow-lg transition-shadow">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm sm:text-base font-semibold mb-2 text-gray-700">Total Pedidos</h3>
              <p class="text-2xl sm:text-3xl font-bold text-primary-600">{{ totalPedidos }}</p>
              <p class="text-xs text-gray-500 mt-1">Todos los pedidos</p>
            </div>
            <CalendarIcon class="w-12 h-12 text-primary-200" />
          </div>
        </div>

        <div class="card hover:shadow-lg transition-shadow">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm sm:text-base font-semibold mb-2 text-gray-700">Pendientes</h3>
              <p class="text-2xl sm:text-3xl font-bold text-yellow-600">{{ pedidosPendientes }}</p>
              <p class="text-xs text-gray-500 mt-1">En proceso</p>
            </div>
            <ClockIcon class="w-12 h-12 text-yellow-200" />
          </div>
        </div>

        <div class="card hover:shadow-lg transition-shadow">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm sm:text-base font-semibold mb-2 text-gray-700">Total Gastado</h3>
              <p class="text-2xl sm:text-3xl font-bold text-green-600">{{ formatCurrency(totalGastado) }}</p>
              <p class="text-xs text-gray-500 mt-1">Monto acumulado</p>
            </div>
            <CurrencyDollarIcon class="w-12 h-12 text-green-200" />
          </div>
        </div>

        <div class="card hover:shadow-lg transition-shadow">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-sm sm:text-base font-semibold mb-2 text-gray-700">Completados</h3>
              <p class="text-2xl sm:text-3xl font-bold text-blue-600">{{ pedidosCompletados }}</p>
              <p class="text-xs text-gray-500 mt-1">Eventos realizados</p>
            </div>
            <CheckCircleIcon class="w-12 h-12 text-blue-200" />
          </div>
        </div>
      </div>

      <!-- Próximos Eventos -->
      <div class="card">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg sm:text-xl font-semibold">Próximos Eventos</h2>
          <router-link
            to="/cliente/pedido/nuevo"
            class="inline-flex items-center justify-center btn-primary text-sm"
          >
            <PlusIcon class="w-5 h-5 mr-2" />
            Nuevo Pedido
          </router-link>
        </div>

        <!-- Empty State -->
        <div v-if="proximosPedidos.length === 0" class="text-center py-8">
          <CalendarIcon class="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p class="text-sm sm:text-base text-gray-500 mb-4">No tienes eventos próximos</p>
          <router-link
            to="/cliente/pedido/nuevo"
            class="inline-flex items-center justify-center btn-primary text-sm sm:text-base"
          >
            <PlusIcon class="w-5 h-5 mr-2" />
            Crear Nuevo Pedido
          </router-link>
        </div>

        <!-- Pedidos List -->
        <div v-else class="space-y-4">
          <div
            v-for="pedido in proximosPedidos"
            :key="pedido.id"
            class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
            @click="viewPedido(pedido.id)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <h3 class="font-semibold text-gray-900">Pedido #{{ pedido.id }}</h3>
                  <span
                    class="px-2 py-1 text-xs font-semibold rounded-full"
                    :class="getEstadoBadgeClass(pedido.estado)"
                  >
                    {{ getEstadoText(pedido.estado) }}
                  </span>
                </div>
                
                <div class="space-y-1 text-sm text-gray-600">
                  <p v-if="pedido.fecha_evento">
                    <CalendarIcon class="w-4 h-4 inline mr-1" />
                    Fecha del evento: {{ formatDate(pedido.fecha_evento) }}
                  </p>
                  <p v-if="pedido.tipo_evento_nombre">
                    Tipo: {{ pedido.tipo_evento_nombre }}
                  </p>
                  <p v-if="pedido.paquete_nombre">
                    Paquete: {{ pedido.paquete_nombre }}
                  </p>
                </div>
              </div>

              <div class="text-right ml-4">
                <p class="text-lg font-bold text-primary-600">
                  {{ formatCurrency(pedido.monto_total || 0) }}
                </p>
                <p class="text-xs text-gray-500 mt-1">
                  Creado: {{ formatDate(pedido.created_at) }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Ver Todos -->
        <div v-if="proximosPedidos.length > 0" class="mt-6 text-center">
          <router-link
            to="/cliente/pedidos"
            class="text-primary-600 hover:text-primary-700 font-medium text-sm"
          >
            Ver todos los pedidos →
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

