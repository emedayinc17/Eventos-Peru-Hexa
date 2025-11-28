<template>
  <div class="max-w-7xl mx-auto py-8 px-4">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Gestión de Usuarios</h1>
        <p class="text-gray-600 mt-1">Administre los usuarios del sistema</p>
      </div>
      <Button variant="primary" @click="openCreateModal">
        + Nuevo Usuario
      </Button>
    </div>

    <!-- Filters -->
    <Card class="mb-6">
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <SearchBar 
            v-model="searchQuery"
            placeholder="Buscar por nombre o email..."
          />
        </div>
        <select
          v-model="filterRole"
          class="rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        >
          <option value="">Todos los roles</option>
          <option value="CLIENTE">Cliente</option>
          <option value="ADMIN">Admin</option>
        </select>
        <select
          v-model="filterActivo"
          class="rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        >
          <option value="">Todos los estados</option>
          <option value="true">Activos</option>
          <option value="false">Inactivos</option>
        </select>
      </div>
    </Card>

    <!-- Table -->
    <Card :padding="false">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Usuario
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Teléfono
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Role
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="loading">
              <td colspan="6" class="px-6 py-12 text-center">
                <Loading text="Cargando usuarios..." />
              </td>
            </tr>
            <tr v-else-if="filteredUsers.length === 0">
              <td colspan="6" class="px-6 py-12 text-center text-gray-500">
                No se encontraron usuarios
              </td>
            </tr>
            <tr v-else v-for="user in filteredUsers" :key="user.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="h-10 w-10 flex-shrink-0">
                    <div class="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                      <span class="text-primary-600 font-medium">
                        {{ getInitials(user) }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ user.nombre }} {{ user.apellido }}
                    </div>
                    <div class="text-sm text-gray-500">ID: {{ user.id }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ user.email }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ user.telefono || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="user.role === 'ADMIN' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'"
                >
                  {{ user.role }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="user.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  {{ user.activo ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                <button
                  @click="openEditModal(user)"
                  class="text-primary-600 hover:text-primary-900"
                >
                  Editar
                </button>
                <button
                  @click="confirmDelete(user)"
                  class="text-red-600 hover:text-red-900"
                  :disabled="user.id === authStore.user?.id"
                >
                  Eliminar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Create/Edit Modal -->
    <Modal 
      v-model="showModal" 
      :title="isEdit ? 'Editar Usuario' : 'Nuevo Usuario'"
      max-width="lg"
    >
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
            Email <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.email"
            type="email"
            required
            :readonly="isEdit"
            :class="isEdit ? 'bg-gray-100 cursor-not-allowed' : ''"
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          />
          <p v-if="isEdit" class="text-sm text-gray-500 mt-1">
            El email no puede ser modificado
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

        <div v-if="!isEdit">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Contraseña <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.password"
            type="password"
            :required="!isEdit"
            minlength="6"
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          />
          <p class="text-sm text-gray-500 mt-1">Mínimo 6 caracteres</p>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Role <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.role"
              required
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              <option value="CLIENTE">Cliente</option>
              <option value="ADMIN">Admin</option>
            </select>
          </div>

          <div class="flex items-center mt-8">
            <input
              v-model="form.activo"
              type="checkbox"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label class="ml-2 block text-sm text-gray-900">
              Usuario activo
            </label>
          </div>
        </div>

        <div class="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="secondary" type="button" @click="showModal = false">
            Cancelar
          </Button>
          <Button variant="primary" type="submit" :loading="submitting">
            {{ isEdit ? 'Actualizar' : 'Crear' }}
          </Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { iamApi } from '@/api';
import { useUiStore } from '@/stores/ui';
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';
import SearchBar from '@/components/common/SearchBar.vue';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';

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
      u.nombre.toLowerCase().includes(query) ||
      u.apellido.toLowerCase().includes(query) ||
      u.email.toLowerCase().includes(query)
    );
  }
  
  if (filterRole.value) {
    result = result.filter(u => u.role === filterRole.value);
  }
  
  if (filterActivo.value) {
    const isActive = filterActivo.value === 'true';
    result = result.filter(u => u.activo === isActive);
  }
  
  return result;
});

// Helper functions
const getInitials = (user: any) => {
  return `${user.nombre.charAt(0)}${user.apellido.charAt(0)}`.toUpperCase();
};

const loadUsers = async () => {
  try {
    loading.value = true;
    const response = await iamApi.getUsers();
    users.value = response.data || response;
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
  form.nombre = user.nombre;
  form.apellido = user.apellido;
  form.email = user.email;
  form.telefono = user.telefono || '';
  form.role = user.role;
  form.activo = user.activo ?? true;
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

    const payload: any = {
      nombre: form.nombre,
      apellido: form.apellido,
      telefono: form.telefono || null,
      role: form.role,
      activo: form.activo,
    };

    if (isEdit.value && selectedUser.value) {
      await iamApi.updateUser(selectedUser.value.id, payload);
    } else {
      payload.email = form.email;
      payload.password = form.password;
      await iamApi.createUser(payload);
    }

    showModal.value = false;
    resetForm();
    await loadUsers();
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

  const ok = await ui.showConfirm(`¿Está seguro de eliminar al usuario "${user.nombre} ${user.apellido}"?`, 'Eliminar usuario');
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
