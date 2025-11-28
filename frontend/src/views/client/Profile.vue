<template>
  <div class="max-w-4xl mx-auto py-8 px-4">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">Mi Perfil</h1>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Profile Info Card -->
      <div class="lg:col-span-1">
        <Card>
          <div class="text-center">
            <div class="mx-auto h-24 w-24 rounded-full bg-primary-100 flex items-center justify-center mb-4">
              <span class="text-4xl font-bold text-primary-600">
                {{ initials }}
              </span>
            </div>
            <h2 class="text-xl font-semibold text-gray-900">
              {{ authStore.userFullName }}
            </h2>
            <p class="text-sm text-gray-500 mt-1">{{ authStore.user?.email }}</p>
            <span 
              class="inline-block mt-3 px-3 py-1 rounded-full text-sm font-medium"
              :class="authStore.isAdmin ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'"
            >
              {{ authStore.user?.role }}
            </span>
          </div>
        </Card>
      </div>

      <!-- Edit Form Card -->
      <div class="lg:col-span-2">
        <Card>
          <h3 class="text-lg font-semibold text-gray-900 mb-6">Información Personal</h3>
          
          <form @submit.prevent="handleSubmit" class="space-y-6">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Nombre <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="form.nombre"
                  type="text"
                  required
                  class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Apellido <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="form.apellido"
                  type="text"
                  required
                  class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                :value="authStore.user?.email"
                type="email"
                readonly
                class="w-full rounded-lg border-gray-300 bg-gray-100 shadow-sm cursor-not-allowed"
              />
              <p class="text-sm text-gray-500 mt-1">
                El email no puede ser modificado. Contacte al administrador si necesita cambiarlo.
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Teléfono
              </label>
              <input
                v-model="form.telefono"
                type="tel"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                placeholder="+51 999 999 999"
              />
            </div>

            <div class="flex justify-end gap-3 pt-6 border-t">
              <Button 
                variant="secondary" 
                type="button"
                @click="resetForm"
              >
                Cancelar
              </Button>
              <Button 
                variant="primary" 
                type="submit"
                :loading="submitting"
                :disabled="!hasChanges"
              >
                Guardar Cambios
              </Button>
            </div>
          </form>
        </Card>

        <!-- Change Password Card -->
        <Card class="mt-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-6">Cambiar Contraseña</h3>
          
          <form @submit.prevent="handlePasswordChange" class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Contraseña Actual <span class="text-red-500">*</span>
              </label>
              <input
                v-model="passwordForm.currentPassword"
                type="password"
                required
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Nueva Contraseña <span class="text-red-500">*</span>
              </label>
              <input
                v-model="passwordForm.newPassword"
                type="password"
                required
                minlength="6"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
              <p class="text-sm text-gray-500 mt-1">Mínimo 6 caracteres</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Confirmar Nueva Contraseña <span class="text-red-500">*</span>
              </label>
              <input
                v-model="passwordForm.confirmPassword"
                type="password"
                required
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
              <p v-if="passwordForm.newPassword && passwordForm.confirmPassword && !passwordsMatch" 
                 class="text-sm text-red-600 mt-1">
                Las contraseñas no coinciden
              </p>
            </div>

            <div class="flex justify-end pt-6 border-t">
              <Button 
                variant="primary" 
                type="submit"
                :loading="changingPassword"
                :disabled="!passwordsMatch || !passwordForm.currentPassword"
              >
                Cambiar Contraseña
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>

    <!-- Success Modal -->
    <Modal v-model="showSuccessModal" title="¡Cambios Guardados!">
      <div class="text-center py-6">
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
          <svg class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          Perfil actualizado exitosamente
        </h3>
        <p class="text-sm text-gray-500">
          {{ successMessage }}
        </p>
        <div class="mt-6">
          <Button variant="primary" @click="showSuccessModal = false">
            Aceptar
          </Button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useUiStore } from '@/stores/ui';
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';
import Modal from '@/components/common/Modal.vue';

const authStore = useAuthStore();
const ui = useUiStore();

const submitting = ref(false);
const changingPassword = ref(false);
const showSuccessModal = ref(false);
const successMessage = ref('');

const form = reactive({
  nombre: '',
  apellido: '',
  telefono: '',
});

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
});

// Computed
const initials = computed(() => {
  if (!authStore.user) return '??';
  return `${authStore.user.nombre.charAt(0)}${authStore.user.apellido.charAt(0)}`.toUpperCase();
});

const hasChanges = computed(() => {
  if (!authStore.user) return false;
  return form.nombre !== authStore.user.nombre ||
         form.apellido !== authStore.user.apellido ||
         form.telefono !== (authStore.user.telefono || '');
});

const passwordsMatch = computed(() => {
  return passwordForm.newPassword === passwordForm.confirmPassword;
});

// Methods
const loadUserData = () => {
  if (authStore.user) {
    form.nombre = authStore.user.nombre;
    form.apellido = authStore.user.apellido;
    form.telefono = authStore.user.telefono || '';
  }
};

const resetForm = () => {
  loadUserData();
};

const handleSubmit = async () => {
  try {
    submitting.value = true;

    await authStore.updateProfile({
      nombre: form.nombre,
      apellido: form.apellido,
      telefono: form.telefono || null,
    });

    successMessage.value = 'Tu información personal ha sido actualizada.';
    showSuccessModal.value = true;
  } catch (error: any) {
    ui.showToast('Error al actualizar perfil: ' + (error.response?.data?.detail || error.message), 'error', 6000);
  } finally {
    submitting.value = false;
  }
};

const handlePasswordChange = async () => {
  if (!passwordsMatch.value) {
    ui.showToast('Las contraseñas no coinciden', 'error');
    return;
  }

  try {
    changingPassword.value = true;

    // TODO: Implement password change API call
    // await authStore.changePassword(passwordForm.currentPassword, passwordForm.newPassword);

    // For now, show success
    successMessage.value = 'Tu contraseña ha sido cambiada exitosamente. Por favor, inicia sesión nuevamente.';
    showSuccessModal.value = true;

    // Reset password form
    passwordForm.currentPassword = '';
    passwordForm.newPassword = '';
    passwordForm.confirmPassword = '';

    // Optional: Auto logout after password change
    // setTimeout(() => {
    //   authStore.logout();
    //   router.push('/login');
    // }, 2000);

    ui.showToast('Funcionalidad de cambio de contraseña pendiente de implementación en el backend', 'info');
  } catch (error: any) {
    ui.showToast('Error al cambiar contraseña: ' + (error.response?.data?.detail || error.message), 'error', 6000);
  } finally {
    changingPassword.value = false;
  }
};

onMounted(() => {
  loadUserData();
});
</script>
