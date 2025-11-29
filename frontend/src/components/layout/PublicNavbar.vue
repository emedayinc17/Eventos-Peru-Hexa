<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { useAuthStore } from '@/stores';
import { Bars3Icon, XMarkIcon, UserIcon, HomeIcon, CalendarIcon, ShoppingBagIcon } from '@heroicons/vue/24/outline';

const authStore = useAuthStore();
const mobileMenuOpen = ref(false);

const publicNavigation = [
  { name: 'Inicio', href: '/', icon: HomeIcon },
  { name: 'Paquetes', href: '/paquetes', icon: ShoppingBagIcon },
  { name: 'Proveedores', href: '/proveedores', icon: CalendarIcon },
];
</script>

<template>
  <nav class="bg-white shadow-lg">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 justify-between">
        <div class="flex">
          <RouterLink to="/" class="flex flex-shrink-0 items-center">
            <span class="text-2xl font-bold text-primary-600">EventosPeru</span>
          </RouterLink>
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <RouterLink
              v-for="item in publicNavigation"
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
          <template v-if="authStore.isAuthenticated">
            <RouterLink
              :to="authStore.isAdmin ? '/admin/dashboard' : '/cliente/dashboard'"
              class="inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700"
            >
              <UserIcon class="mr-2 h-5 w-5" />
              {{ authStore.user?.nombre }}
            </RouterLink>
          </template>
          <template v-else>
            <div class="inline-flex items-center space-x-2">
              <RouterLink
                to="/login"
                class="inline-flex items-center rounded-md bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700"
              >
                Iniciar Sesión
              </RouterLink>

              <RouterLink
                :to="{ path: '/login', query: { register: 'true' } }"
                class="inline-flex items-center rounded-md border border-primary-600 px-3 py-2 text-sm font-semibold text-primary-600 bg-white hover:bg-primary-50"
              >
                Crear cuenta
              </RouterLink>
            </div>
          </template>
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
    </div>

    <!-- Mobile menu -->
    <div v-if="mobileMenuOpen" class="sm:hidden">
      <div class="space-y-1 pb-3 pt-2">
        <RouterLink
          v-for="item in publicNavigation"
          :key="item.name"
          :to="item.href"
          class="block border-l-4 border-transparent py-2 pl-3 pr-4 text-base font-medium text-gray-600 hover:border-primary-500 hover:bg-gray-50 hover:text-primary-600"
          active-class="border-primary-500 bg-primary-50 text-primary-600"
          @click="mobileMenuOpen = false"
        >
          {{ item.name }}
        </RouterLink>
      </div>
      <div class="border-t border-gray-200 pb-3 pt-4">
        <template v-if="authStore.isAuthenticated">
          <RouterLink
            :to="authStore.isAdmin ? '/admin/dashboard' : '/cliente/dashboard'"
            class="block px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-800"
            @click="mobileMenuOpen = false"
          >
            Mi Cuenta
          </RouterLink>
        </template>
        <template v-else>
          <RouterLink
            to="/login"
            class="block px-4 py-2 text-base font-medium text-primary-600 hover:bg-gray-100"
            @click="mobileMenuOpen = false"
          >
            Iniciar Sesión
          </RouterLink>
        </template>
      </div>
    </div>
  </nav>
</template>
