<template>
  <div class="min-h-screen bg-gray-50/50 pb-12">
    <!-- Header Background -->
    <div class="h-48 bg-gradient-to-r from-primary-600 to-primary-800 w-full relative overflow-hidden">
      <div class="absolute inset-0 bg-pattern opacity-10"></div>
      <div class="absolute -bottom-10 -left-10 w-40 h-40 bg-white opacity-10 rounded-full blur-2xl"></div>
      <div class="absolute top-10 right-10 w-60 h-60 bg-primary-400 opacity-20 rounded-full blur-3xl"></div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-20 relative z-10">
      <div class="flex flex-col md:flex-row gap-8">
        
        <!-- Left Column: Profile Card -->
        <div class="w-full md:w-1/3 lg:w-1/4 flex-shrink-0">
          <div class="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100 sticky top-24">
            <div class="p-8 text-center">
              <div class="relative inline-block">
                <div class="h-32 w-32 rounded-full bg-gradient-to-br from-primary-100 to-primary-50 flex items-center justify-center mx-auto mb-4 border-4 border-white shadow-lg">
                  <span class="text-5xl font-bold text-primary-600 tracking-wider">
                    {{ initials }}
                  </span>
                </div>
                <div class="absolute bottom-2 right-2 h-6 w-6 bg-green-500 border-4 border-white rounded-full" title="Activo"></div>
              </div>
              
              <h2 class="text-2xl font-bold text-gray-900 mt-2">
                {{ authStore.userFullName }}
              </h2>
              <p class="text-sm text-gray-500 flex items-center justify-center gap-1 mt-1">
                <EnvelopeIcon class="w-4 h-4" />
                {{ authStore.user?.email }}
              </p>
              
              <div class="mt-6 flex flex-wrap justify-center gap-2">
                <span 
                  class="px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase"
                  :class="authStore.isAdmin ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'"
                >
                  {{ authStore.user?.role }}
                </span>
                <span class="px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase bg-green-100 text-green-700">
                  Verificado
                </span>
              </div>
            </div>
            
            <div class="border-t border-gray-100 bg-gray-50/50 p-4">
              <div class="text-xs text-center text-gray-400">
                Miembro desde {{ formatDate(authStore.user?.created_at) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Forms -->
        <div class="flex-1 space-y-8">
          
          <!-- Personal Information -->
          <div class="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div class="px-6 py-5 border-b border-gray-100 flex items-center justify-between bg-gray-50/30">
              <div class="flex items-center gap-3">
                <div class="p-2 bg-primary-100 rounded-lg text-primary-600">
                  <UserCircleIcon class="w-6 h-6" />
                </div>
                <div>
                  <h3 class="text-lg font-bold text-gray-900">Información Personal</h3>
                  <p class="text-sm text-gray-500">Actualiza tus datos de contacto</p>
                </div>
              </div>
            </div>
            
            <div class="p-6 md:p-8">
              <form @submit.prevent="handleSubmit" class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="space-y-2">
                    <label class="text-sm font-medium text-gray-700">Nombre</label>
                    <div class="relative">
                      <input
                        v-model="form.nombre"
                        type="text"
                        required
                        class="pl-10 w-full rounded-xl border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 transition-all"
                        placeholder="Tu nombre"
                      />
                      <UserIcon class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    </div>
                  </div>
                  
                  <div class="space-y-2">
                    <label class="text-sm font-medium text-gray-700">Apellido</label>
                    <div class="relative">
                      <input
                        v-model="form.apellido"
                        type="text"
                        required
                        class="pl-10 w-full rounded-xl border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 transition-all"
                        placeholder="Tu apellido"
                      />
                      <UserIcon class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="space-y-2">
                    <label class="text-sm font-medium text-gray-700">Email</label>
                    <div class="relative">
                      <input
                        :value="authStore.user?.email"
                        type="email"
                        readonly
                        class="pl-10 w-full rounded-xl border-gray-200 bg-gray-50 text-gray-500 shadow-sm cursor-not-allowed"
                      />
                      <EnvelopeIcon class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    </div>
                    <p class="text-xs text-gray-400 ml-1">Para cambiar tu email, contacta a soporte.</p>
                  </div>

                  <div class="space-y-2">
                    <label class="text-sm font-medium text-gray-700">Teléfono</label>
                    <div class="relative">
                      <input
                        v-model="form.telefono"
                        type="tel"
                        class="pl-10 w-full rounded-xl border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 transition-all"
                        placeholder="+51 999 999 999"
                      />
                      <PhoneIcon class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    </div>
                  </div>
                </div>

                <div class="flex justify-end pt-4 border-t border-gray-100">
                  <div class="flex gap-3">
                    <Button 
                      v-if="hasChanges"
                      variant="secondary" 
                      type="button"
                      @click="resetForm"
                      class="rounded-xl"
                    >
                      Cancelar
                    </Button>
                    <Button 
                      variant="primary" 
                      type="submit"
                      :loading="submitting"
                      :disabled="!hasChanges"
                      class="rounded-xl px-6 shadow-lg shadow-primary-500/30"
                    >
                      Guardar Cambios
                    </Button>
                  </div>
                </div>
              </form>
            </div>
          </div>

          <!-- Security Section -->
          <div class="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div class="px-6 py-5 border-b border-gray-100 flex items-center justify-between bg-gray-50/30">
              <div class="flex items-center gap-3">
                <div class="p-2 bg-orange-100 rounded-lg text-orange-600">
                  <ShieldCheckIcon class="w-6 h-6" />
                </div>
                <div>
                  <h3 class="text-lg font-bold text-gray-900">Seguridad</h3>
                  <p class="text-sm text-gray-500">Gestiona tu contraseña y acceso</p>
                </div>
              </div>
            </div>

            <div class="p-6 md:p-8">
              <form @submit.prevent="handlePasswordChange" class="space-y-6">
                <div class="space-y-2">
                  <label class="text-sm font-medium text-gray-700">Contraseña Actual</label>
                  <div class="relative">
                    <input
                      v-model="passwordForm.currentPassword"
                      type="password"
                      required
                      class="pl-10 w-full rounded-xl border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 transition-all"
                      placeholder="••••••••"
                    />
                    <KeyIcon class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="space-y-2">
                    <label class="text-sm font-medium text-gray-700">Nueva Contraseña</label>
                    <div class="relative">
                      <input
                        v-model="passwordForm.newPassword"
                        type="password"
                        required
                        minlength="6"
                        class="pl-10 w-full rounded-xl border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 transition-all"
                        placeholder="Mínimo 6 caracteres"
                      />
                      <KeyIcon class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    </div>
                  </div>

                  <div class="space-y-2">
                    <label class="text-sm font-medium text-gray-700">Confirmar Contraseña</label>
                    <div class="relative">
                      <input
                        v-model="passwordForm.confirmPassword"
                        type="password"
                        required
                        class="pl-10 w-full rounded-xl border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 transition-all"
                        placeholder="Repite la nueva contraseña"
                      />
                      <KeyIcon class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    </div>
                  </div>
                </div>
                
                <div v-if="passwordForm.newPassword && passwordForm.confirmPassword && !passwordsMatch" 
                     class="text-sm text-red-500 flex items-center gap-2 bg-red-50 p-3 rounded-lg border border-red-100">
                  <span class="font-bold">!</span> Las contraseñas no coinciden
                </div>

                <div class="flex justify-end pt-4 border-t border-gray-100">
                  <Button 
                    variant="primary" 
                    type="submit"
                    :loading="changingPassword"
                    :disabled="!passwordsMatch || !passwordForm.currentPassword"
                    class="rounded-xl px-6 bg-gray-900 hover:bg-gray-800 shadow-lg shadow-gray-900/20"
                  >
                    Actualizar Contraseña
                  </Button>
                </div>
              </form>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- Success Modal -->
    <Modal v-model="showSuccessModal" title="¡Todo listo!">
      <div class="text-center py-6">
        <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-6 animate-bounce">
          <svg class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 class="text-xl font-bold text-gray-900 mb-2">
          Operación Exitosa
        </h3>
        <p class="text-gray-500 mb-8">
          {{ successMessage }}
        </p>
        <Button variant="primary" @click="showSuccessModal = false" class="w-full justify-center rounded-xl py-3 text-lg">
          Entendido
        </Button>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useUiStore } from '@/stores/ui';
import Button from '@/components/common/Button.vue';
import Modal from '@/components/common/Modal.vue';
import { 
  UserCircleIcon, 
  EnvelopeIcon, 
  PhoneIcon, 
  ShieldCheckIcon, 
  KeyIcon,
  UserIcon
} from '@heroicons/vue/24/outline';

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
  const parts = (authStore.user.nombre || '').split(' ');
  const n = parts[0]?.charAt(0) || '';
  const a = parts.length > 1 ? parts[1].charAt(0) : '';
  return `${n}${a}`.toUpperCase();
});

const hasChanges = computed(() => {
  if (!authStore.user) return false;
  
  const currentParts = (authStore.user.nombre || '').split(' ');
  const currentNombre = currentParts[0] || '';
  const currentApellido = currentParts.slice(1).join(' ') || '';
  
  return form.nombre !== currentNombre ||
         form.apellido !== currentApellido ||
         form.telefono !== (authStore.user.telefono || '');
});

const passwordsMatch = computed(() => {
  return passwordForm.newPassword === passwordForm.confirmPassword;
});

// Methods
const formatDate = (dateString: string | undefined) => {
  if (!dateString) return 'recientemente';
  return new Date(dateString).toLocaleDateString('es-PE', { year: 'numeric', month: 'long' });
};

const loadUserData = () => {
  if (authStore.user) {
    const parts = (authStore.user.nombre || '').split(' ');
    form.nombre = parts[0] || '';
    form.apellido = parts.slice(1).join(' ') || '';
    form.telefono = authStore.user.telefono || '';
  }
};

const resetForm = () => {
  loadUserData();
};

const handleSubmit = async () => {
  try {
    submitting.value = true;

    const fullName = `${form.nombre} ${form.apellido}`.trim();

    await authStore.updateProfile({
      nombre: fullName,
      telefono: form.telefono || null,
    });

    successMessage.value = 'Tu información personal ha sido actualizada correctamente.';
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

    await authStore.changePassword(passwordForm.currentPassword, passwordForm.newPassword);

    // For now, show success
    successMessage.value = 'Tu contraseña ha sido cambiada exitosamente. Por favor, inicia sesión nuevamente.';
    showSuccessModal.value = true;

    // Reset password form
    passwordForm.currentPassword = '';
    passwordForm.newPassword = '';
    passwordForm.confirmPassword = '';

    // Optional: Auto logout after password change
    setTimeout(() => {
      authStore.logout();
    }, 3000);

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

<style scoped>
.bg-pattern {
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
</style>
