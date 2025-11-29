<template>
  <div class="w-full h-full p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Gestión de Usuarios</h1>
        <p class="text-gray-600 text-sm mt-1">Administre los usuarios, roles y accesos del sistema</p>
      </div>
      <Button variant="primary" @click="openCreateModal" class="flex items-center gap-2">
        <PlusIcon class="w-5 h-5" />
        Nuevo Usuario
      </Button>
    </div>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[300px]">
          <SearchBar 
            v-model="searchQuery"
            placeholder="Buscar por nombre, email o teléfono..."
          />
        </div>
        <select
          v-model="filterRole"
          class="rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
        >
          <option value="">Todos los roles</option>
          <option value="CLIENTE">Cliente</option>
          <option value="ADMIN">Admin</option>
        </select>
        <select
          v-model="filterActivo"
          class="rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
        >
          <option value="">Todos los estados</option>
          <option value="true">Activos</option>
          <option value="false">Inactivos</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden flex flex-col h-[calc(100vh-300px)]">
      <div class="overflow-auto flex-1">
        <table class="min-w-full divide-y divide-gray-200 relative">
          <thead class="bg-gray-50 sticky top-0 z-10">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Usuario</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Contacto</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Rol</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="loading">
              <td colspan="5" class="px-6 py-12 text-center">
                <Loading text="Cargando usuarios..." />
              </td>
            </tr>
            <tr v-else-if="filteredUsers.length === 0">
              <td colspan="5" class="px-6 py-12 text-center text-gray-500">
                <div class="flex flex-col items-center justify-center">
                  <UserIcon class="w-12 h-12 text-gray-300 mb-2" />
                  <p>No se encontraron usuarios</p>
                </div>
              </td>
            </tr>
            <tr v-else v-for="user in paginatedUsers" :key="user.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="h-10 w-10 flex-shrink-0">
                    <div class="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold text-sm">
                      {{ getInitials(user) }}
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ user.nombre }} {{ user.apellido }}
                    </div>
                    <div class="text-xs text-gray-500 font-mono">ID: {{ user.id.substring(0, 8) }}...</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ user.email }}</div>
                <div class="text-sm text-gray-500">{{ user.telefono || '-' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2.5 py-0.5 text-xs font-medium rounded-full border"
                  :class="user.role === 'ADMIN' ? 'bg-purple-50 text-purple-700 border-purple-200' : 'bg-blue-50 text-blue-700 border-blue-200'"
                >
                  {{ user.role }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2.5 py-0.5 text-xs font-medium rounded-full border"
                  :class="user.status === 1 ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'"
                >
                  {{ user.status === 1 ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end gap-2">
                  <button
                    @click="openEditModal(user)"
                    class="p-1 text-gray-400 hover:text-primary-600 transition-colors rounded-full hover:bg-primary-50"
                    title="Editar"
                  >
                    <PencilIcon class="w-5 h-5" />
                  </button>
                  <button
                    @click="confirmDelete(user)"
                    class="p-1 text-gray-400 hover:text-red-600 transition-colors rounded-full hover:bg-red-50"
                    :disabled="user.id === authStore.user?.id"
                    :class="{ 'opacity-50 cursor-not-allowed': user.id === authStore.user?.id }"
                    title="Eliminar"
                  >
                    <TrashIcon class="w-5 h-5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Pagination -->
      <div class="bg-gray-50 px-6 py-3 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-500">
          Mostrando {{ (currentPage - 1) * pageSize + 1 }} a {{ Math.min(currentPage * pageSize, filteredUsers.length) }} de {{ filteredUsers.length }} usuarios
        </div>
        <div class="flex gap-2">
          <Button 
            variant="secondary" 
            size="sm" 
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            Anterior
          </Button>
          <Button 
            variant="secondary" 
            size="sm" 
            :disabled="currentPage >= totalPages"
            @click="currentPage++"
          >
            Siguiente
          </Button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Modal 
      :open="showModal" 
      @close="showModal = false"
      :title="isEdit ? 'Editar Usuario' : 'Nuevo Usuario'"
      maxWidth="lg"
    >
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Nombre <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.nombre"
              type="text"
              required
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Apellido <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.apellido"
              type="text"
              required
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Email <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.email"
            type="email"
            required
            :readonly="isEdit"
            :class="isEdit ? 'bg-gray-100 cursor-not-allowed text-gray-500' : ''"
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
          <p v-if="isEdit" class="text-xs text-gray-500 mt-1">
            El email no puede ser modificado
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Teléfono
          </label>
          <input
            v-model="form.telefono"
            type="tel"
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="+51 999 999 999"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Contraseña <span v-if="!isEdit" class="text-red-500">*</span>
          </label>
          <input
            v-model="form.password"
            type="password"
            :required="!isEdit"
            minlength="6"
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            :placeholder="isEdit ? 'Dejar en blanco para mantener actual' : ''"
          />
          <p class="text-xs text-gray-500 mt-1">Mínimo 6 caracteres</p>
        </div>

        <div class="grid grid-cols-2 gap-4 items-start">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Role <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.role"
              required
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            >
              <option value="CLIENTE">Cliente</option>
              <option value="ADMIN">Admin</option>
            </select>
          </div>

          <div class="flex items-center h-full pt-6">
            <label class="flex items-center cursor-pointer">
              <input
                v-model="form.activo"
                type="checkbox"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <span class="ml-2 text-sm text-gray-900">Usuario activo</span>
            </label>
          </div>
        </div>

        <div class="flex justify-end space-x-3 pt-4 border-t mt-6">
          <Button variant="secondary" type="button" @click="showModal = false">
            Cancelar
          </Button>
          <Button variant="primary" type="submit" :loading="submitting">
            {{ isEdit ? 'Actualizar' : 'Crear Usuario' }}
          </Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { iamApi } from '@/api';
import { useUiStore } from '@/stores/ui';
import Button from '@/components/common/Button.vue';
import SearchBar from '@/components/common/SearchBar.vue';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';
import { PencilIcon, TrashIcon, PlusIcon, UserIcon } from '@heroicons/vue/24/outline';

const authStore = useAuthStore();
const ui = useUiStore();

const users = ref<any[]>([]);
const loading = ref(false);
const searchQuery = ref('');
const filterRole = ref('');
const filterActivo = ref('');
const showModal = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const selectedUser = ref<any>(null);

// Pagination
const currentPage = ref(1);
const pageSize = ref(10);

const form = reactive({
  nombre: '',
  apellido: '',
  email: '',
  telefono: '',
  password: '',
  role: 'CLIENTE',
  activo: true,
});

// Filtered users
const filteredUsers = computed(() => {
  let result = users.value;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(u => 
      (u.nombre?.toLowerCase() || '').includes(query) ||
      (u.apellido?.toLowerCase() || '').includes(query) ||
      (u.email?.toLowerCase() || '').includes(query)
    );
  }
  
  if (filterRole.value) {
    result = result.filter(u => u.role === filterRole.value);
  }
  
  if (filterActivo.value) {
    const isActive = filterActivo.value === 'true';
    // Backend returns status: 1 (active) or 0 (inactive)
    result = result.filter(u => (u.status === 1) === isActive);
  }
  
  return result;
});

// Paginated users
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredUsers.value.slice(start, end);
});

const totalPages = computed(() => Math.ceil(filteredUsers.value.length / pageSize.value));

// Reset page on filter change
watch([searchQuery, filterRole, filterActivo], () => {
  currentPage.value = 1;
});

// Helper functions
const getInitials = (user: any) => {
  const n = user.nombre?.charAt(0) || '';
  const a = user.apellido?.charAt(0) || '';
  return `${n}${a}`.toUpperCase() || '?';
};

const loadUsers = async () => {
  try {
    loading.value = true;
    // Fetch a large number to support client-side filtering/pagination
    const response = await iamApi.getUsers({ limit: 1000, offset: 0 });
    users.value = Array.isArray(response) ? response : (response as any).data || [];
  } catch (error: any) {
    ui.showToast('Error al cargar usuarios: ' + (error.response?.data?.detail || error.message), 'error');
  } finally {
    loading.value = false;
  }
};

const openCreateModal = () => {
  isEdit.value = false;
  selectedUser.value = null;
  resetForm();
  showModal.value = true;
};

const openEditModal = (user: any) => {
  isEdit.value = true;
  selectedUser.value = user;
  
  // Split full name into nombre/apellido
  const parts = (user.nombre || '').split(' ');
  form.nombre = parts[0] || '';
  form.apellido = parts.slice(1).join(' ') || '';
  
  form.email = user.email;
  form.telefono = user.telefono || '';
  form.role = user.role;
  form.activo = user.status === 1;
  form.password = '';
  showModal.value = true;
};

const resetForm = () => {
  form.nombre = '';
  form.apellido = '';
  form.email = '';
  form.telefono = '';
  form.password = '';
  form.role = 'CLIENTE';
  form.activo = true;
};

const handleSubmit = async () => {
  try {
    submitting.value = true;

    const fullName = `${form.nombre} ${form.apellido}`.trim();

    const payload: any = {
      nombre: fullName,
      telefono: form.telefono || null,
      role: form.role,
      status: form.activo ? 1 : 0,
    };

    if (isEdit.value && selectedUser.value) {
      if (form.password) {
        payload.password = form.password;
      }
      await iamApi.updateUser(selectedUser.value.id, payload);
    } else {
      payload.email = form.email;
      payload.password = form.password;
      await iamApi.createUser(payload);
    }

    showModal.value = false;
    resetForm();
    await loadUsers();
    ui.showToast(isEdit.value ? 'Usuario actualizado' : 'Usuario creado', 'success');
  } catch (error: any) {
    ui.showToast('Error: ' + (error.response?.data?.detail || error.message), 'error');
  } finally {
    submitting.value = false;
  }
};

const confirmDelete = async (user: any) => {
  if (user.id === authStore.user?.id) {
    ui.showToast('No puedes eliminar tu propio usuario', 'error');
    return;
  }

  const ok = await ui.showConfirmWithFallback(`¿Está seguro de eliminar al usuario "${user.nombre} ${user.apellido || ''}"?`, 'Eliminar usuario');
  if (!ok) return;
  try {
    await iamApi.deleteUser(user.id);
    await loadUsers();
    ui.showToast('Usuario eliminado', 'success');
  } catch (error: any) {
    ui.showToast('Error al eliminar: ' + (error.response?.data?.detail || error.message), 'error');
  }
};

onMounted(async () => {
  await loadUsers();
});
</script>
