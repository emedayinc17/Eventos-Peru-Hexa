<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores';

const authStore = useAuthStore();

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await authStore.fetchProfile();
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

    <div class="grid grid-cols-1 gap-4 sm:gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-6 sm:mb-8">
      <div class="card hover:shadow-lg transition-shadow">
        <h3 class="text-sm sm:text-base font-semibold mb-2 text-gray-700">Próximos Eventos</h3>
        <p class="text-2xl sm:text-3xl font-bold text-primary-600">2</p>
        <p class="text-xs text-gray-500 mt-1">Eventos pendientes</p>
      </div>
      <div class="card hover:shadow-lg transition-shadow">
        <h3 class="text-sm sm:text-base font-semibold mb-2 text-gray-700">Total Gastado</h3>
        <p class="text-2xl sm:text-3xl font-bold text-primary-600">S/ 25,000</p>
        <p class="text-xs text-gray-500 mt-1">Monto acumulado</p>
      </div>
      <div class="card hover:shadow-lg transition-shadow sm:col-span-2 lg:col-span-1">
        <h3 class="text-sm sm:text-base font-semibold mb-2 text-gray-700">Pedidos Completados</h3>
        <p class="text-2xl sm:text-3xl font-bold text-primary-600">5</p>
        <p class="text-xs text-gray-500 mt-1">Eventos realizados</p>
      </div>
    </div>

    <div class="card">
      <h2 class="text-lg sm:text-xl font-semibold mb-4">Próximos Eventos</h2>
      <p class="text-sm sm:text-base text-gray-500 mb-4">No hay eventos próximos</p>
      <router-link
        to="/cliente/pedido/nuevo"
        class="inline-flex items-center justify-center w-full sm:w-auto btn-primary text-sm sm:text-base"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Crear Nuevo Pedido
      </router-link>
    </div>
  </div>
</template>
