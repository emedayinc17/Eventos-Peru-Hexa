<script setup lang="ts">
import { RouterLink } from 'vue-router';
import { CalendarIcon, UserGroupIcon, SparklesIcon } from '@heroicons/vue/24/outline';

const features = [
  {
    title: 'Bodas',
    description: 'Desde S/ 8,000',
    icon: SparklesIcon,
    link: '/paquetes?tipo=1',
  },
  {
    title: 'Quinceañeras',
    description: 'Desde S/ 5,000',
    icon: UserGroupIcon,
    link: '/paquetes?tipo=2',
  },
  {
    title: 'Cumpleaños',
    description: 'Desde S/ 2,000',
    icon: CalendarIcon,
    link: '/paquetes?tipo=3',
  },
];
</script>

<template>
  <div>
    <!-- Hero Section -->
    <div class="relative bg-gradient-to-r from-primary-600 to-primary-800 text-white">
      <div class="mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
        <div class="text-center">
          <h1 class="text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl">
            Organiza el Evento de tus Sueños
          </h1>
          <p class="mt-6 text-xl text-primary-100">
            Bodas • Quinceañeras • Cumpleaños
          </p>
          <div class="mt-10 flex justify-center gap-4">
            <RouterLink
              to="/paquetes"
              class="rounded-md bg-white px-6 py-3 text-base font-semibold text-primary-600 shadow-sm hover:bg-primary-50 transition-colors"
            >
              Explorar Paquetes
            </RouterLink>
            <RouterLink
              to="/login"
              class="rounded-md border-2 border-white px-6 py-3 text-base font-semibold text-white hover:bg-white hover:text-primary-600 transition-colors"
            >
              Crear Cuenta
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- Services Section -->
    <div class="py-16 bg-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Nuestros Servicios
          </h2>
          <p class="mt-4 text-lg text-gray-600">
            Encuentra el paquete perfecto para tu evento
          </p>
        </div>

        <div class="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="feature in features"
            :key="feature.title"
            class="card hover:shadow-xl transition-shadow cursor-pointer"
            @click="$router.push(feature.link)"
          >
            <component
              :is="feature.icon"
              class="h-12 w-12 text-primary-600 mb-4"
            />
            <h3 class="text-xl font-semibold text-gray-900">
              {{ feature.title }}
            </h3>
            <p class="mt-2 text-3xl font-bold text-primary-600">
              {{ feature.description }}
            </p>
            <RouterLink
              :to="feature.link"
              class="mt-4 inline-block text-primary-600 hover:text-primary-700 font-medium"
            >
              Ver más →
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- How it Works -->
    <div class="py-16 bg-gray-50">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            ¿Cómo funciona?
          </h2>
        </div>
        <div class="grid gap-8 md:grid-cols-3">
          <div class="text-center">
            <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary-600 text-white text-2xl font-bold">
              1
            </div>
            <h3 class="mt-4 text-lg font-semibold">Elige tu tipo de evento</h3>
            <p class="mt-2 text-gray-600">Selecciona entre bodas, quinceañeras, cumpleaños y más</p>
          </div>
          <div class="text-center">
            <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary-600 text-white text-2xl font-bold">
              2
            </div>
            <h3 class="mt-4 text-lg font-semibold">Selecciona paquete o servicios</h3>
            <p class="mt-2 text-gray-600">Elige un paquete o arma tu evento a la carta</p>
          </div>
          <div class="text-center">
            <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary-600 text-white text-2xl font-bold">
              3
            </div>
            <h3 class="mt-4 text-lg font-semibold">Confirma y recibe cotización</h3>
            <p class="mt-2 text-gray-600">Revisa tu pedido y recibe confirmación inmediata</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
