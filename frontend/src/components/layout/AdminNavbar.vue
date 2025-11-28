<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores';
import {
  Bars3Icon,
  XMarkIcon,
  HomeIcon,
  CalendarDaysIcon,
  WrenchScrewdriverIcon,
  ArchiveBoxIcon,
  UserGroupIcon,
  ClipboardDocumentCheckIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/vue/24/outline';

const authStore = useAuthStore();
const router = useRouter();
const mobileMenuOpen = ref(false);

const adminNavigation = [
  { name: 'Dashboard', href: '/admin/dashboard', icon: HomeIcon },
  { name: 'Tipos Evento', href: '/admin/tipos-evento', icon: CalendarDaysIcon },
  { name: 'Servicios', href: '/admin/servicios', icon: WrenchScrewdriverIcon },
  { name: 'Paquetes', href: '/admin/paquetes', icon: ArchiveBoxIcon },
  { name: 'Pedidos', href: '/admin/pedidos', icon: ClipboardDocumentCheckIcon },
  { name: 'Usuarios', href: '/admin/usuarios', icon: UserGroupIcon },
];

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<template>
  <nav class="bg-gray-900 w-full">
    <div class="flex h-16 items-center justify-between mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex items-center">
          <RouterLink to="/admin/dashboard" class="flex-shrink-0">
            <span class="text-2xl font-bold text-white">EventosPeru Admin</span>
          </RouterLink>
          <div class="hidden md:block">
            <div class="ml-10 flex items-baseline space-x-4">
              <RouterLink
                v-for="item in adminNavigation"
                :key="item.name"
                :to="item.href"
                class="flex items-center rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
                active-class="bg-gray-700 text-white"
              >
                <component :is="item.icon" class="mr-2 h-5 w-5" />
                {{ item.name }}
              </RouterLink>
            </div>
          </div>
      </div>
      <div class="hidden md:block">
          <div class="ml-4 flex items-center md:ml-6">
            <span class="text-sm text-gray-300 mr-4 hidden lg:inline">
              {{ authStore.userFullName }}
            </span>
            <button
              type="button"
              class="inline-flex items-center rounded-md bg-gray-800 px-3 py-2 text-sm font-medium text-white hover:bg-gray-700"
              @click="handleLogout"
            >
              <ArrowRightOnRectangleIcon class="mr-2 h-5 w-5" />
              Cerrar Sesión
            </button>
          </div>
      </div>
      <div class="-mr-2 flex md:hidden">
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-md bg-gray-800 p-2 text-gray-400 hover:bg-gray-700 hover:text-white"
            @click="mobileMenuOpen = !mobileMenuOpen"
          >
            <span class="sr-only">Abrir menú</span>
            <Bars3Icon v-if="!mobileMenuOpen" class="block h-6 w-6" />
            <XMarkIcon v-else class="block h-6 w-6" />
          </button>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-if="mobileMenuOpen" class="md:hidden">
      <div class="space-y-1 px-2 pb-3 pt-2 sm:px-3">
        <RouterLink
          v-for="item in adminNavigation"
          :key="item.name"
          :to="item.href"
          class="block rounded-md px-3 py-2 text-base font-medium text-gray-300 hover:bg-gray-700 hover:text-white"
          active-class="bg-gray-700 text-white"
          @click="mobileMenuOpen = false"
        >
          {{ item.name }}
        </RouterLink>
      </div>
      <div class="border-t border-gray-700 pb-3 pt-4">
        <div class="px-5">
          <div class="text-base font-medium text-white">{{ authStore.userFullName }}</div>
          <div class="text-sm font-medium text-gray-400">{{ authStore.user?.email }}</div>
        </div>
        <div class="mt-3 px-2">
          <button
            type="button"
            class="block w-full rounded-md px-3 py-2 text-left text-base font-medium text-gray-400 hover:bg-gray-700 hover:text-white"
            @click="handleLogout"
          >
            Cerrar Sesión
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>
