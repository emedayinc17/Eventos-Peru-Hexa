<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores';
import Button from '@/components/common/Button.vue';
import Input from '@/components/common/Input.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const form = ref({
  email: '',
  password: '',
});

const errors = ref<Record<string, string>>({});
const loading = ref(false);

const validate = (): boolean => {
  errors.value = {};
  
  if (!form.value.email) {
    errors.value.email = 'El email es requerido';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    errors.value.email = 'Email inválido';
  }
  
  if (!form.value.password) {
    errors.value.password = 'La contraseña es requerida';
  }
  
  return Object.keys(errors.value).length === 0;
};

const handleSubmit = async () => {
  if (!validate()) return;
  
  loading.value = true;
  
  try {
    const success = await authStore.login(form.value);
    
    if (success) {
      // Redirigir según rol o a la página de redirección
      const redirect = route.query.redirect as string;
      
      if (redirect) {
        router.push(redirect);
      } else if (authStore.isAdmin) {
        router.push('/admin/dashboard');
      } else {
        router.push('/cliente/dashboard');
      }
    } else {
      errors.value.general = authStore.error || 'Credenciales inválidas';
    }
  } catch (error) {
    errors.value.general = 'Error al iniciar sesión. Por favor intenta de nuevo.';
  } finally {
    loading.value = false;
  }
};

const quickLogin = async (role: 'admin' | 'cliente') => {
  errors.value = {};
  
  if (role === 'admin') {
    form.value.email = 'admin@eventos.pe';
    form.value.password = 'Evoluti0n';
  } else {
    form.value.email = 'test.cliente@eventos.pe';
    form.value.password = 'test123';
  }
  
  // Esperar un momento para que el usuario vea los datos llenados (opcional)
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // Ejecutar login automáticamente
  await handleSubmit();
};
</script>

<template>
  <div class="flex min-h-full flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <h2 class="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
        Iniciar Sesión
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        O
        <router-link to="/" class="font-medium text-primary-600 hover:text-primary-500">
          volver al inicio
        </router-link>
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white px-4 py-8 shadow sm:rounded-lg sm:px-10">
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <div v-if="errors.general" class="rounded-md bg-red-50 p-4">
            <p class="text-sm text-red-800">{{ errors.general }}</p>
          </div>

          <Input
            v-model="form.email"
            label="Email"
            type="email"
            placeholder="tu@email.com"
            :error="errors.email"
            required
          />

          <Input
            v-model="form.password"
            label="Contraseña"
            type="password"
            placeholder="••••••••"
            :error="errors.password"
            required
          />

          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                class="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-600"
              />
              <label for="remember-me" class="ml-2 block text-sm text-gray-900">
                Recordarme
              </label>
            </div>

            <div class="text-sm">
              <a href="#" class="font-medium text-primary-600 hover:text-primary-500">
                ¿Olvidaste tu contraseña?
              </a>
            </div>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            :loading="loading"
            :disabled="loading"
            full-width
          >
            Iniciar Sesión
          </Button>
        </form>

        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300" />
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="bg-white px-2 text-gray-500">Acceso Rápido de Prueba</span>
            </div>
          </div>

          <div class="mt-4 grid grid-cols-2 gap-3">
            <button
              type="button"
              @click="quickLogin('admin')"
              :disabled="loading"
              class="flex items-center justify-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg class="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Admin
            </button>

            <button
              type="button"
              @click="quickLogin('cliente')"
              :disabled="loading"
              class="flex items-center justify-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Cliente
            </button>
          </div>

          <p class="mt-3 text-center text-xs text-gray-500">
            Haz clic en un botón para acceder rápidamente
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
