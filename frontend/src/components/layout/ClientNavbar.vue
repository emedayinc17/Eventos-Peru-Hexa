<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores';
import {
  Bars3Icon,
  XMarkIcon,
  HomeIcon,
  ShoppingBagIcon,
  ClipboardDocumentListIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  PlusIcon,
} from '@heroicons/vue/24/outline';

const authStore = useAuthStore();
const router = useRouter();
const mobileMenuOpen = ref(false);

const clientNavigation = [
  { name: 'Dashboard', href: '/cliente/dashboard', icon: HomeIcon },
  { name: 'Paquetes', href: '/cliente/paquetes', icon: ShoppingBagIcon },
  { name: 'Mis Pedidos', href: '/cliente/pedidos', icon: ClipboardDocumentListIcon },
  { name: 'Perfil', href: '/perfil', icon: UserCircleIcon },
];

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<template>
  <nav class="bg-white shadow w-full">
    <div class="flex h-16 justify-between mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex">
          <RouterLink to="/cliente/dashboard" class="flex flex-shrink-0 items-center">
            <span class="text-2xl font-bold text-primary-600">EventosPeru</span>
          </RouterLink>
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <RouterLink
              v-for="item in clientNavigation"
              :key="item.name"
              :to="item.href"
              class="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-sm font-medium text-gray-900 hover:border-primary-500 hover:text-primary-600 transition-colors"
              active-class="border-primary-500 text-primary-600"
            >
              <component :is="item.icon" class="mr-2 h-5 w-5" />
              {{ item.name }}
            </RouterLink>
          </div>
      </div>
      <div class="hidden sm:ml-6 sm:flex sm:items-center">
          <span class="text-sm text-gray-700 mr-4 hidden lg:inline">
            Hola, <strong>{{ authStore.userFullName }}</strong>
          </span>
              <!-- Quick create order button visible on desktop -->
              <RouterLink to="/cliente/pedido/nuevo" class="inline-flex items-center mr-3 rounded-md bg-primary-600 px-3 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700">
                <PlusIcon class="mr-2 h-5 w-5" />
                Crear Pedido
              </RouterLink>
          <button
            type="button"
            class="inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
            @click="handleLogout"
          >
            <ArrowRightOnRectangleIcon class="mr-2 h-5 w-5" />
            Cerrar Sesión
          </button>
      </div>
      <div class="-mr-2 flex items-center sm:hidden">
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500"
            @click="mobileMenuOpen = !mobileMenuOpen"
          >
            <span class="sr-only">Abrir menú</span>
            <Bars3Icon v-if="!mobileMenuOpen" class="block h-6 w-6" />
            <XMarkIcon v-else class="block h-6 w-6" />
          </button>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-if="mobileMenuOpen" class="sm:hidden">
      <div class="space-y-1 pb-3 pt-2">
        <RouterLink
          v-for="item in clientNavigation"
          :key="item.name"
          :to="item.href"
          class="block border-l-4 border-transparent py-2 pl-3 pr-4 text-base font-medium text-gray-600 hover:border-primary-500 hover:bg-gray-50 hover:text-primary-600"
          active-class="border-primary-500 bg-primary-50 text-primary-600"
          @click="mobileMenuOpen = false"
        >
          {{ item.name }}
        </RouterLink>
          <!-- Quick create visible in mobile menu -->
          <RouterLink to="/cliente/pedido/nuevo" class="block border-l-4 border-transparent py-2 pl-3 pr-4 text-base font-medium text-gray-600 hover:border-primary-500 hover:bg-gray-50 hover:text-primary-600" @click="mobileMenuOpen = false">
            Crear Pedido
          </RouterLink>
      </div>
      <div class="border-t border-gray-200 pb-3 pt-4">
        <div class="px-4">
          <div class="text-base font-medium text-gray-800">{{ authStore.userFullName }}</div>
          <div class="text-sm font-medium text-gray-500">{{ authStore.user?.email }}</div>
        </div>
        <div class="mt-3">
          <button
            type="button"
            class="block w-full px-4 py-2 text-left text-base font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-800"
            @click="handleLogout"
          >
            Cerrar Sesión
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>
