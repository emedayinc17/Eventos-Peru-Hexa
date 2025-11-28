<template>
  <div class="py-12 px-4">
    <div class="max-w-5xl mx-auto">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p class="mt-4 text-gray-600">Cargando detalles...</p>
      </div>

      <!-- Not Found -->
      <div v-else-if="!paquete" class="text-center py-12">
        <div class="text-6xl mb-4">❌</div>
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Paquete no encontrado</h2>
        <p class="text-gray-600 mb-6">
          El paquete que buscas no existe o no está disponible
        </p>
        <Button variant="primary" @click="router.push('/paquetes')">
          Ver Todos los Paquetes
        </Button>
      </div>

      <!-- Paquete Detail -->
      <div v-else>
        <!-- Breadcrumb -->
        <nav class="mb-6 flex items-center text-sm text-gray-500">
          <a href="/paquetes" class="hover:text-primary-600">Paquetes</a>
          <span class="mx-2">/</span>
          <span class="text-gray-900">{{ paquete.nombre }}</span>
        </nav>

        <!-- Header -->
        <div class="mb-8">
          <span class="inline-block px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800 mb-4">
            {{ tipoNombre }}
          </span>
          <h1 class="text-4xl font-bold text-gray-900 mb-4">
            {{ paquete.nombre }}
          </h1>
          <p class="text-lg text-gray-600">
            {{ paquete.descripcion }}
          </p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Main Content -->
          <div class="lg:col-span-2">
            <!-- Servicios Incluidos -->
            <Card>
              <h2 class="text-2xl font-bold text-gray-900 mb-6">
                Servicios Incluidos ({{ serviciosIncluidos.length }})
              </h2>

              <div v-if="serviciosIncluidos.length === 0" class="text-center py-8 text-gray-500">
                No se encontraron servicios para este paquete
              </div>

              <div v-else class="space-y-4">
                <div
                  v-for="servicio in serviciosIncluidos"
                  :key="servicio.id"
                  class="border rounded-lg p-4 hover:border-primary-300 transition-colors"
                >
                  <div class="flex justify-between items-start mb-2">
                    <h3 class="text-lg font-semibold text-gray-900">
                      {{ servicio.nombre }}
                    </h3>
                    <span class="text-primary-600 font-medium">
                      S/ {{ formatPrice(servicio.precio_unitario) }}
                    </span>
                  </div>
                  <p class="text-gray-600 text-sm mb-3">
                    {{ servicio.descripcion }}
                  </p>
                  <div class="flex gap-2">
                    <span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                      {{ servicio.categoria }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Value Calculation -->
              <div v-if="serviciosIncluidos.length > 0" class="mt-6 pt-6 border-t">
                <div class="space-y-2">
                  <div class="flex justify-between text-gray-600">
                    <span>Valor individual de servicios:</span>
                    <span>S/ {{ formatPrice(totalServiciosValue) }}</span>
                  </div>
                  <div class="flex justify-between text-gray-600">
                    <span>Precio del paquete:</span>
                    <span>S/ {{ formatPrice(paquete.precio_base) }}</span>
                  </div>
                  <div class="flex justify-between text-lg font-bold text-green-600 pt-2 border-t">
                    <span>Ahorro:</span>
                    <span>S/ {{ formatPrice(totalServiciosValue - paquete.precio_base) }}</span>
                  </div>
                </div>
              </div>
            </Card>

            <!-- Recommendations -->
            <Card class="mt-6">
              <h3 class="text-xl font-bold text-gray-900 mb-4">
                ¿Por qué elegir este paquete?
              </h3>
              <ul class="space-y-3">
                <li class="flex items-start gap-3">
                  <svg class="h-6 w-6 text-green-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span class="text-gray-700">Todos los servicios esenciales para tu evento en un solo paquete</span>
                </li>
                <li class="flex items-start gap-3">
                  <svg class="h-6 w-6 text-green-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span class="text-gray-700">Ahorra tiempo y dinero con nuestra selección curada</span>
                </li>
                <li class="flex items-start gap-3">
                  <svg class="h-6 w-6 text-green-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span class="text-gray-700">Posibilidad de agregar servicios adicionales según tus necesidades</span>
                </li>
              </ul>
            </Card>
          </div>

          <!-- Sidebar -->
          <div class="lg:col-span-1">
            <Card class="sticky top-6">
              <div class="mb-6">
                <p class="text-sm text-gray-500 mb-2">Precio desde</p>
                <p class="text-4xl font-bold text-primary-600">
                  S/ {{ formatPrice(paquete.precio_base) }}
                </p>
              </div>

              <div class="space-y-4 mb-6 pb-6 border-b">
                <div class="flex items-start gap-3">
                  <svg class="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ serviciosIncluidos.length }} Servicios</p>
                    <p class="text-xs text-gray-500">Incluidos en el paquete</p>
                  </div>
                </div>
                <div class="flex items-start gap-3">
                  <svg class="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <p class="text-sm font-medium text-gray-900">Personalizable</p>
                    <p class="text-xs text-gray-500">Agrega servicios adicionales</p>
                  </div>
                </div>
              </div>

              <!-- CTA Buttons -->
              <div class="space-y-3">
                <Button 
                  v-if="authStore.isAuthenticated"
                  variant="primary" 
                  class="w-full"
                  @click="selectPaquete"
                >
                  Seleccionar Paquete
                </Button>
                <template v-else>
                  <Button 
                    variant="primary" 
                    class="w-full"
                    @click="router.push('/login?redirect=' + encodeURIComponent(`/paquetes/${paqueteId}`))"
                  >
                    Iniciar Sesión para Continuar
                  </Button>
                  <Button 
                    variant="secondary" 
                    class="w-full"
                    @click="router.push('/login?register=true')"
                  >
                    Crear Cuenta
                  </Button>
                </template>
              </div>

              <!-- Contact Info -->
              <div class="mt-6 pt-6 border-t text-center">
                <p class="text-sm text-gray-600 mb-2">¿Necesitas ayuda?</p>
                <p class="text-sm font-medium text-primary-600">Contáctanos</p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCatalogStore } from '@/stores/catalog';
import { useAuthStore } from '@/stores/auth';
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';
import type { Paquete, Servicio } from '@/types';

const route = useRoute();
const router = useRouter();
const catalogStore = useCatalogStore();
const authStore = useAuthStore();

const loading = ref(false);
const paqueteId = computed(() => Number(route.params.id));

// Computed
const paquete = computed((): Paquete | undefined => {
  return catalogStore.paquetes.find(p => p.id === paqueteId.value);
});

const tipoNombre = computed(() => {
  if (!paquete.value) return '';
  const tipo = catalogStore.tiposEvento.find(t => t.id === paquete.value!.tipo_evento_id);
  return tipo?.nombre || 'N/A';
});

const serviciosIncluidos = computed((): Servicio[] => {
  if (!paquete.value?.servicios_ids) return [];
  return paquete.value.servicios_ids
    .map(id => catalogStore.servicios.find(s => s.id === id))
    .filter((s): s is Servicio => s !== undefined);
});

const totalServiciosValue = computed(() => {
  return serviciosIncluidos.value.reduce((sum, s) => sum + s.precio_unitario, 0);
});

// Methods
const formatPrice = (price: number): string => {
  return price.toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const selectPaquete = () => {
  if (!paquete.value) return;
  router.push({
    path: '/cliente/pedido/nuevo',
    query: { 
      paquete_id: paquete.value.id.toString(),
      tipo_evento_id: paquete.value.tipo_evento_id.toString()
    }
  });
};

const loadData = async () => {
  loading.value = true;
  try {
    await Promise.all([
      catalogStore.fetchTiposEvento(),
      catalogStore.fetchPaquetes(),
      catalogStore.fetchServicios(),
    ]);
  } catch (error) {
    console.error('Error loading data:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadData();
});
</script>
