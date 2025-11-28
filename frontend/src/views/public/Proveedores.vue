<template>
  <div class="py-12 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Nuestros Proveedores</h1>
        <p class="text-lg text-gray-600 max-w-3xl mx-auto">
          Trabajamos con los mejores proveedores de servicios para eventos en Perú. 
          Cada uno seleccionado cuidadosamente para garantizar la calidad de tu evento.
        </p>
      </div>

      <!-- Search and Filters -->
      <div class="mb-8 flex flex-wrap gap-4">
        <div class="w-full sm:w-96">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar proveedor..."
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          />
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p class="mt-4 text-gray-600">Cargando proveedores...</p>
      </div>

      <!-- Empty State -->
      <div 
        v-else-if="filteredProveedores.length === 0" 
        class="text-center py-12 bg-gray-50 rounded-lg"
      >
        <div class="text-6xl mb-4">👥</div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          No se encontraron proveedores
        </h3>
        <p class="text-gray-600">
          {{ searchQuery ? 'Intenta con otros términos de búsqueda' : 'Información de proveedores disponible próximamente' }}
        </p>
      </div>

      <!-- Proveedores Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        <Card 
          v-for="proveedor in filteredProveedores" 
          :key="proveedor.id"
          class="hover:shadow-lg transition-shadow duration-200"
        >
          <!-- Avatar/Logo Placeholder -->
          <div class="mb-4 h-24 w-24 rounded-full bg-gradient-to-br from-primary-100 to-secondary-100 flex items-center justify-center mx-auto">
            <span class="text-3xl font-bold text-primary-600">
              {{ getInitials(proveedor.nombre_comercial) }}
            </span>
          </div>

          <!-- Proveedor Info -->
          <div class="text-center mb-4">
            <h3 class="text-xl font-bold text-gray-900 mb-1">
              {{ proveedor.nombre_comercial }}
            </h3>
            <p class="text-sm text-gray-500">
              {{ proveedor.razon_social }}
            </p>
          </div>

          <!-- Contact -->
          <div class="space-y-2 mb-4 text-sm">
            <div v-if="proveedor.email" class="flex items-center gap-2 text-gray-600">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span class="truncate">{{ proveedor.email }}</span>
            </div>
            <div v-if="proveedor.telefono" class="flex items-center gap-2 text-gray-600">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <span>{{ proveedor.telefono }}</span>
            </div>
          </div>

          <!-- Status -->
          <div class="flex justify-center pt-4 border-t">
            <span 
              class="inline-block px-3 py-1 rounded-full text-sm font-medium"
              :class="proveedor.activo ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'"
            >
              {{ proveedor.activo ? 'Activo' : 'Inactivo' }}
            </span>
          </div>
        </Card>
      </div>

      <!-- CTA Section -->
      <div v-if="!loading" class="text-center py-12 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-2xl">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">
          ¿Eres un proveedor de servicios?
        </h2>
        <p class="text-gray-600 mb-6">
          Únete a nuestra red de proveedores y llega a más clientes
        </p>
        <Button 
          variant="primary"
          @click="router.push('/login?register=true')"
        >
          Registrarse como Proveedor
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { providersApi } from '@/api';
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';

interface Proveedor {
  id: number;
  usuario_id: number;
  razon_social: string;
  nombre_comercial: string;
  ruc: string;
  email: string;
  telefono: string;
  activo: boolean;
}

const router = useRouter();

const loading = ref(false);
const proveedores = ref<Proveedor[]>([]);
const searchQuery = ref('');

// Computed
const filteredProveedores = computed(() => {
  if (!searchQuery.value.trim()) return proveedores.value;
  
  const query = searchQuery.value.toLowerCase();
  return proveedores.value.filter(p => 
    p.nombre_comercial.toLowerCase().includes(query) ||
    p.razon_social.toLowerCase().includes(query) ||
    p.ruc.includes(query)
  );
});

// Methods
const getInitials = (name: string): string => {
  const words = name.split(' ');
  if (words.length >= 2) {
    return `${words[0].charAt(0)}${words[1].charAt(0)}`.toUpperCase();
  }
  return name.substring(0, 2).toUpperCase();
};

const loadProveedores = async () => {
  loading.value = true;
  try {
    const response = await providersApi.getProveedores();
    proveedores.value = response.data || [];
  } catch (error: any) {
    console.error('Error loading proveedores:', error);
    // Si falla la API, mostrar empty state
    proveedores.value = [];
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadProveedores();
});
</script>
