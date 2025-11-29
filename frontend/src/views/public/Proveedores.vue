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

      <!-- Filters: rating only -->
      <div class="mb-8 flex flex-wrap gap-4 items-center">
        <div class="w-56">
          <label class="block text-sm text-gray-600 mb-1">Rating mínimo</label>
          <select v-model.number="minRating" class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500">
            <option :value="0">Todos</option>
            <option :value="3">3+</option>
            <option :value="3.5">3.5+</option>
            <option :value="4">4+</option>
            <option :value="4.5">4.5+</option>
          </select>
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
          Información de proveedores disponible próximamente
        </p>
      </div>

      <!-- Proveedores Grid -->
      <div v-else-if="!errorMsg" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
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

            <!-- Rating -->
            <div class="flex items-center justify-center mt-2 space-x-2">
              <div class="flex items-center">
                <template v-for="n in 5">
                  <svg v-if="(Math.round(proveedor.rating_prom || 0)) >= n" :key="`star-on-${n}-${proveedor.id}`" class="h-4 w-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.95a1 1 0 00.95.69h4.162c.969 0 1.371 1.24.588 1.81l-3.37 2.45a1 1 0 00-.364 1.118l1.287 3.95c.3.92-.755 1.688-1.54 1.118l-3.37-2.45a1 1 0 00-1.176 0l-3.37 2.45c-.784.57-1.84-.197-1.54-1.118l1.287-3.95a1 1 0 00-.364-1.118L2.063 9.377c-.783-.57-.38-1.81.588-1.81h4.162a1 1 0 00.95-.69l1.286-3.95z" />
                  </svg>
                  <svg v-else :key="`star-off-${n}-${proveedor.id}`" class="h-4 w-4 text-gray-300" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.95a1 1 0 00.95.69h4.162c.969 0 1.371 1.24.588 1.81l-3.37 2.45a1 1 0 00-.364 1.118l1.287 3.95c.3.92-.755 1.688-1.54 1.118l-3.37-2.45a1 1 0 00-1.176 0l-3.37 2.45c-.784.57-1.84-.197-1.54-1.118l1.287-3.95a1 1 0 00-.364-1.118L2.063 9.377c-.783-.57-.38-1.81.588-1.81h4.162a1 1 0 00.95-.69l1.286-3.95z" />
                  </svg>
                </template>
              </div>
              <div class="text-sm text-gray-600">{{ (proveedor.rating_prom || 0).toFixed(1) }}</div>
            </div>
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

      <!-- Error message + CTA Section -->
      <div v-if="errorMsg" class="text-center py-6 bg-red-50 rounded-lg mb-6">
        <div class="text-red-700 font-medium">Error cargando proveedores: {{ errorMsg }}</div>
        <div class="text-sm text-gray-600 mt-2">Intenta refrescar la página o revisa los logs del servidor.</div>
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
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { providersApi } from '@/api';
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';

interface Proveedor {
  id: number;
  usuario_id?: number;
  razon_social: string;
  nombre_comercial: string;
  email?: string;
  telefono?: string;
  activo?: boolean;
  direccion?: string;
  contacto?: string;
  rating_prom?: number;
}

const router = useRouter();

const loading = ref(false);
const proveedores = ref<Proveedor[]>([]);
const minRating = ref<number>(0);

// visibleProveedores se actualiza en vivo cuando cambia proveedores o minRating
const visibleProveedores = ref<Proveedor[]>([]);
const errorMsg = ref<string | null>(null);

// No service/date filters: we load all public providers

// Computed
const filteredProveedores = computed(() => visibleProveedores.value);

const updateVisible = () => {
  let list = proveedores.value.slice();
  if (minRating.value && minRating.value > 0) {
    list = list.filter(p => (p.rating_prom || 0) >= minRating.value);
  }
  visibleProveedores.value = list;
};

// Recalcular cuando cambian proveedores o el filtro
watch([proveedores, minRating], () => updateVisible(), { deep: true });

// Methods
const getInitials = (name: string): string => {
  const words = name.split(' ');
  if (words.length >= 2) {
    return `${words[0].charAt(0)}${words[1].charAt(0)}`.toUpperCase();
  }
  return name.substring(0, 2).toUpperCase();
};

const mapPublicToProveedor = (p: any): Proveedor => {
  // Map public API fields to UI shape
  return {
    id: p.id,
    nombre_comercial: p.nombre_comercial || p.nombre || p.razon_social || 'Proveedor',
    razon_social: p.razon_social || p.nombre || '',
    email: p.email,
    telefono: p.telefono,
    activo: p.status === undefined ? true : (Number(p.status) === 1),
    direccion: p.direccion,
    contacto: p.contacto,
    // Normalize rating_prom: accept numbers or strings with comma or dot decimals
    rating_prom: ((): number => {
      if (p.rating_prom === null || p.rating_prom === undefined) return 0;
      if (typeof p.rating_prom === 'number') return p.rating_prom;
      const s = String(p.rating_prom).trim().replace(',', '.');
      const n = parseFloat(s);
      return Number.isFinite(n) ? n : 0;
    })(),
  } as Proveedor;
};

const loadProveedores = async () => {
  loading.value = true;
  try {
    const response = await providersApi.getAllProveedoresPublic();
    const arr = Array.isArray(response) ? response : (response.data || response.items || []);
    proveedores.value = arr.map(mapPublicToProveedor);
    // Ensure visible list is computed immediately after load
    try { updateVisible(); } catch (e) { /* silent */ }
    errorMsg.value = null;
  } catch (error: any) {
    console.error('Error loading proveedores (public all):', error);
    proveedores.value = [];
    errorMsg.value = error?.message || 'Error del servidor';
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await loadProveedores();
});
</script>
