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
  TruckIcon,
  UserGroupIcon,
  ClipboardDocumentCheckIcon,
  ArrowRightOnRectangleIcon,
  ChevronDownIcon,
} from '@heroicons/vue/24/outline';

const authStore = useAuthStore();
const router = useRouter();
const mobileMenuOpen = ref(false);
const userMenuOpen = ref(false);

const adminNavigation = [
  { name: 'Dashboard', href: '/admin/dashboard', icon: HomeIcon },
  { name: 'Tipos Evento', href: '/admin/tipos-evento', icon: CalendarDaysIcon },
  { name: 'Servicios', href: '/admin/servicios', icon: WrenchScrewdriverIcon },
  { name: 'Paquetes', href: '/admin/paquetes', icon: ArchiveBoxIcon },
  { name: 'Proveedores', href: '/admin/proveedores', icon: TruckIcon },
  { name: 'Pedidos', href: '/admin/pedidos', icon: ClipboardDocumentCheckIcon },
  { name: 'Usuarios', href: '/admin/usuarios', icon: UserGroupIcon },
];

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};

const getInitials = (name: string) => {
  if (!name) return 'U';
  const parts = name.split(' ');
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
};
</script>

<template>
  <nav class="bg-gray-900 w-full relative z-50">
    <div class="flex h-16 items-center justify-between mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex items-center gap-8">
          <RouterLink to="/admin/dashboard" class="flex-shrink-0">
            <span class="text-2xl font-bold text-white">EventosPeru</span>
          </RouterLink>
          <div class="hidden md:block">
            <div class="flex items-baseline space-x-2">
              <RouterLink
                v-for="item in adminNavigation"
                :key="item.name"
                :to="item.href"
                class="flex items-center rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white transition-colors whitespace-nowrap"
                active-class="bg-gray-700 text-white"
              >
                <component :is="item.icon" class="mr-2 h-5 w-5" />
                {{ item.name }}
              </RouterLink>
            </div>
          </div>
      </div>
      
      <!-- Desktop User Menu -->
      <div class="hidden md:block">
          <div class="ml-4 flex items-center md:ml-6 relative">
            <button 
              @click="userMenuOpen = !userMenuOpen"
              class="flex items-center gap-3 max-w-xs rounded-full bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800 p-1 pr-3 transition-colors hover:bg-gray-700"
            >
              <div class="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-white font-bold">
                {{ getInitials(authStore.userFullName) }}
              </div>
              <div class="flex flex-col items-start hidden lg:flex">
                <span class="text-gray-200 font-medium truncate max-w-[150px]">{{ authStore.userFullName }}</span>
              </div>
              <ChevronDownIcon class="h-4 w-4 text-gray-400" />
            </button>

            <!-- Dropdown -->
            <div 
              v-if="userMenuOpen"
              class="absolute right-0 top-full mt-2 w-56 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50"
            >
              <div class="px-4 py-3 border-b border-gray-100">
                <p class="text-sm text-gray-900 font-medium truncate">{{ authStore.userFullName }}</p>
                <p class="text-xs text-gray-500 truncate">{{ authStore.user?.email }}</p>
              </div>
              
              <button
                @click="handleLogout"
                class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
              >
                <ArrowRightOnRectangleIcon class="h-4 w-4" />
                Cerrar Sesión
              </button>
            </div>
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
    <div v-if="mobileMenuOpen" class="md:hidden bg-gray-900">
      <div class="space-y-1 px-2 pb-3 pt-2 sm:px-3">
        <RouterLink
          v-for="item in adminNavigation"
          :key="item.name"
          :to="item.href"
          class="block rounded-md px-3 py-2 text-base font-medium text-gray-300 hover:bg-gray-700 hover:text-white"
          active-class="bg-gray-700 text-white"
          @click="mobileMenuOpen = false"
        >
          <div class="flex items-center">
            <component :is="item.icon" class="mr-3 h-5 w-5" />
            {{ item.name }}
          </div>
        </RouterLink>
      </div>
      <div class="border-t border-gray-700 pb-3 pt-4">
        <div class="px-5 flex items-center gap-3">
          <div class="h-10 w-10 rounded-full bg-primary-600 flex items-center justify-center text-white font-bold text-lg">
            {{ getInitials(authStore.userFullName) }}
          </div>
          <div>
            <div class="text-base font-medium text-white">{{ authStore.userFullName }}</div>
            <div class="text-sm font-medium text-gray-400">{{ authStore.user?.email }}</div>
          </div>
        </div>
        <div class="mt-3 px-2">
          <button
            type="button"
            class="block w-full rounded-md px-3 py-2 text-left text-base font-medium text-gray-400 hover:bg-gray-700 hover:text-white flex items-center gap-2"
            @click="handleLogout"
          >
            <ArrowRightOnRectangleIcon class="h-5 w-5" />
            Cerrar Sesión
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>
