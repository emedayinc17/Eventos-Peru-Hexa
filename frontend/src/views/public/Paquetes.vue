<template>
  <div class="py-12 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Nuestros Paquetes</h1>
        <p class="text-lg text-gray-600 max-w-3xl mx-auto">
          Descubre nuestros paquetes prediseñados para todo tipo de eventos. 
          Cada paquete incluye una selección de servicios premium para que tu evento sea perfecto.
        </p>
      </div>

      <!-- Filters -->
      <div class="mb-8 flex flex-wrap gap-4 items-center justify-between">
        <div class="flex flex-wrap gap-4">
          <!-- Tipo Filter -->
          <div class="w-full sm:w-64">
            <select
              v-model="selectedTipoId"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              <option :value="null">Todos los eventos</option>
              <option 
                v-for="tipo in catalogStore.tiposEvento" 
                :key="tipo.id" 
                :value="tipo.id"
              >
                {{ tipo.nombre }}
              </option>
            </select>
          </div>

          <!-- Search -->
          <div class="w-full sm:w-64">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar paquete..."
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
        </div>

        <div class="text-sm text-gray-500">
          {{ filteredPaquetes.length }} paquete(s) encontrado(s)
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
        <div class="text-6xl mb-4">🔍</div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          No se encontraron paquetes
        </h3>
        <p class="text-gray-600">
          {{ searchQuery ? 'Intenta con otros términos de búsqueda' : 'No hay paquetes disponibles en este momento' }}
        </p>
      </div>

      <!-- Paquetes Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        <Card 
          v-for="paquete in filteredPaquetes" 
          :key="paquete.id"
          class="hover:shadow-xl transition-all duration-200 cursor-pointer"
          @click="viewPaqueteDetail(paquete.id)"
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

          <!-- Servicios Count -->
          <div class="mb-4">
            <div class="flex items-center gap-2 text-sm text-gray-600">
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              <span>{{ paquete.servicios_ids?.length || 0 }} servicios incluidos</span>
            </div>
          </div>

          <!-- Price and CTA -->
          <div class="flex items-end justify-between pt-4 border-t">
            <div>
              <p class="text-sm text-gray-500">Desde</p>
              <p class="text-2xl font-bold text-primary-600">
                S/ {{ formatPrice(paquete.precio_base) }}
              </p>
            </div>
            <Button 
              variant="primary"
              size="sm"
              @click.stop="viewPaqueteDetail(paquete.id)"
            >
              Ver Detalle
            </Button>
          </div>
        </Card>
      </div>

      <!-- CTA Section -->
      <div v-if="!loading" class="text-center py-12 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-2xl">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">
          ¿Listo para planear tu evento?
        </h2>
        <p class="text-gray-600 mb-6">
          Crea una cuenta para personalizar tu paquete y comenzar a planificar
        </p>
        <div class="flex gap-4 justify-center">
          <Button 
            variant="primary"
            @click="router.push('/login?redirect=/cliente/paquetes')"
          >
            Iniciar Sesión
          </Button>
          <Button 
            variant="secondary"
            @click="router.push('/login?register=true')"
          >
            Crear Cuenta
          </Button>
        </div>
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

const router = useRouter();
const catalogStore = useCatalogStore();

const loading = ref(false);
const selectedTipoId = ref<number | null>(null);
const searchQuery = ref('');

// Computed
const filteredPaquetes = computed(() => {
  let result = catalogStore.paquetes;
  
  // Filter by tipo
  if (selectedTipoId.value !== null) {
    result = result.filter(p => p.tipo_evento_id === selectedTipoId.value);
  }
  
  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(p => 
      p.nombre.toLowerCase().includes(query) ||
      p.descripcion.toLowerCase().includes(query)
    );
  }
  
  return result;
});

// Methods
const getTipoNombre = (tipoId: number): string => {
  const tipo = catalogStore.tiposEvento.find(t => t.id === tipoId);
  return tipo?.nombre || 'N/A';
};

const formatPrice = (price: number): string => {
  return price.toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const viewPaqueteDetail = (paqueteId: number) => {
  router.push(`/paquetes/${paqueteId}`);
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
