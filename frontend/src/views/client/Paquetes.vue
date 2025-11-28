<template>
  <div class="py-8 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Paquetes de Eventos</h1>
        <p class="text-gray-600">
          Explora nuestros paquetes prediseñados y encuentra el perfecto para tu evento
        </p>
      </div>

      <!-- Filters -->
      <div class="mb-6 flex flex-wrap gap-4">
        <div class="w-full sm:w-64">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Tipo de Evento
          </label>
          <select
            v-model="selectedTipoId"
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          >
            <option :value="null">Todos los tipos</option>
            <option 
              v-for="tipo in catalogStore.tiposEvento" 
              :key="tipo.id" 
              :value="tipo.id"
            >
              {{ tipo.nombre }}
            </option>
          </select>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p class="mt-4 text-gray-600">Cargando paquetes...</p>
      </div>

      <!-- Empty State -->
      <div 
        v-else-if="filteredPaquetes.length === 0" 
        class="text-center py-12 bg-gray-50 rounded-lg"
      >
        <div class="text-6xl mb-4">📦</div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          No hay paquetes disponibles
        </h3>
        <p class="text-gray-600">
          {{ selectedTipoId ? 'No se encontraron paquetes para este tipo de evento' : 'Aún no hay paquetes registrados' }}
        </p>
      </div>

      <!-- Paquetes Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card 
          v-for="paquete in filteredPaquetes" 
          :key="paquete.id"
          class="hover:shadow-lg transition-shadow duration-200"
        >
          <!-- Tipo Badge -->
          <div class="mb-4">
            <span class="inline-block px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
              {{ getTipoNombre(paquete.tipo_evento_id) }}
            </span>
          </div>

          <!-- Paquete Info -->
          <h3 class="text-xl font-bold text-gray-900 mb-2">
            {{ paquete.nombre }}
          </h3>
          <p class="text-gray-600 mb-4 line-clamp-3">
            {{ paquete.descripcion }}
          </p>

          <!-- Servicios Incluidos -->
          <div class="mb-4">
            <h4 class="text-sm font-semibold text-gray-700 mb-2">
              Servicios Incluidos ({{ paquete.servicios_ids?.length || 0 }})
            </h4>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(servicioId, index) in getFirstServiciosIds(paquete.servicios_ids)"
                :key="servicioId"
                class="inline-block px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
              >
                {{ getServicioNombre(servicioId) }}
              </span>
              <span
                v-if="paquete.servicios_ids && paquete.servicios_ids.length > 3"
                class="inline-block px-2 py-1 bg-gray-200 text-gray-600 text-xs rounded-full font-medium"
              >
                +{{ paquete.servicios_ids.length - 3 }} más
              </span>
            </div>
          </div>

          <!-- Price -->
          <div class="flex items-end justify-between pt-4 border-t">
            <div>
              <p class="text-sm text-gray-500">Desde</p>
              <p class="text-2xl font-bold text-primary-600">
                S/ {{ formatPrice(paquete.precio_base) }}
              </p>
            </div>
            <Button 
              variant="primary"
              @click="selectPaquete(paquete)"
            >
              Seleccionar
            </Button>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCatalogStore } from '@/stores/catalog';
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';
import type { Paquete } from '@/types';

const router = useRouter();
const catalogStore = useCatalogStore();

const loading = ref(false);
const selectedTipoId = ref<number | null>(null);

// Computed
const filteredPaquetes = computed(() => {
  let result = catalogStore.paquetes;
  
  if (selectedTipoId.value !== null) {
    result = result.filter(p => p.tipo_evento_id === selectedTipoId.value);
  }
  
  return result;
});

// Methods
const getTipoNombre = (tipoId: number): string => {
  const tipo = catalogStore.tiposEvento.find(t => t.id === tipoId);
  return tipo?.nombre || 'N/A';
};

const getServicioNombre = (servicioId: number): string => {
  const servicio = catalogStore.servicios.find(s => s.id === servicioId);
  return servicio?.nombre || 'N/A';
};

const getFirstServiciosIds = (ids?: number[]): number[] => {
  if (!ids) return [];
  return ids.slice(0, 3);
};

const formatPrice = (price: number): string => {
  return price.toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const selectPaquete = (paquete: Paquete) => {
  router.push({
    path: '/cliente/pedido/nuevo',
    query: { 
      paquete_id: paquete.id.toString(),
      tipo_evento_id: paquete.tipo_evento_id.toString()
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
