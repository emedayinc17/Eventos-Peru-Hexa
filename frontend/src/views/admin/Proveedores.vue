<template>
  <div class="w-full h-full p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Gestión de Proveedores</h1>
        <p class="text-gray-600 text-sm mt-1">Administre los proveedores de servicios externos</p>
      </div>
      <Button variant="primary" @click="openCreateModal" class="flex items-center gap-2">
        <PlusIcon class="w-5 h-5" />
        Nuevo Proveedor
      </Button>
    </div>

    <!-- Search Bar -->
    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
      <div class="w-full md:w-1/3">
        <SearchBar 
          v-model="searchQuery"
          placeholder="Buscar proveedores por nombre, email o categoría..."
        />
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Proveedor</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Contacto</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Categoría</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="providersStore.loading">
              <td colspan="5" class="px-6 py-12 text-center">
                <Loading text="Cargando proveedores..." />
              </td>
            </tr>
            <tr v-else-if="filteredProveedores.length === 0">
              <td colspan="5" class="px-6 py-12 text-center text-gray-500">
                <div class="flex flex-col items-center justify-center">
                  <UserGroupIcon class="w-12 h-12 text-gray-300 mb-2" />
                  <p>No se encontraron proveedores</p>
                </div>
              </td>
            </tr>
            <tr v-else v-for="proveedor in filteredProveedores" :key="proveedor.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ proveedor.nombre }}</div>
                <div class="text-xs text-gray-500" v-if="proveedor.ruc">RUC: {{ proveedor.ruc }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex flex-col gap-1">
                  <div class="text-sm text-gray-900 flex items-center gap-1" v-if="proveedor.email">
                    <EnvelopeIcon class="w-3 h-3 text-gray-400" /> {{ proveedor.email }}
                  </div>
                  <div class="text-sm text-gray-500 flex items-center gap-1" v-if="proveedor.telefono">
                    <PhoneIcon class="w-3 h-3 text-gray-400" /> {{ proveedor.telefono }}
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2.5 py-0.5 text-xs font-medium rounded-full bg-purple-50 text-purple-700 border border-purple-200">
                  {{ proveedor.categoria || 'Sin categoría' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2.5 py-0.5 text-xs font-medium rounded-full border"
                  :class="proveedor.activo ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'"
                >
                  {{ proveedor.activo ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end gap-2">
                  <button
                    @click="openEditModal(proveedor)"
                    class="p-1 text-gray-400 hover:text-primary-600 transition-colors rounded-full hover:bg-primary-50"
                    title="Editar"
                  >
                    <PencilIcon class="w-5 h-5" />
                  </button>
                  <button
                    @click="confirmDelete(proveedor)"
                    class="p-1 text-gray-400 hover:text-red-600 transition-colors rounded-full hover:bg-red-50"
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
    </div>

    <!-- Create/Edit Modal -->
    <Modal 
      :open="showModal" 
      @close="showModal = false"
      :title="isEdit ? 'Editar Proveedor' : 'Nuevo Proveedor'"
      maxWidth="lg"
    >
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Nombre del Proveedor <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.nombre"
            type="text"
            required
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="Ej: Eventos Premium SAC"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              RUC
            </label>
            <input
              v-model="form.ruc"
              type="text"
              maxlength="11"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              placeholder="20123456789"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Categoría <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.categoria"
              required
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            >
              <option value="">Seleccione categoría</option>
              <option value="FOTOGRAFIA">Fotografía</option>
              <option value="VIDEO">Video</option>
              <option value="CATERING">Catering</option>
              <option value="DECORACION">Decoración</option>
              <option value="ENTRETENIMIENTO">Entretenimiento</option>
              <option value="TRANSPORTE">Transporte</option>
              <option value="MUSICA">Música</option>
              <option value="OTROS">Otros</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              v-model="form.email"
              type="email"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              placeholder="contacto@proveedor.com"
            />
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
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Persona de Contacto
          </label>
          <input
            v-model="form.contacto"
            type="text"
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="Nombre del contacto principal"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Dirección
          </label>
          <textarea
            v-model="form.direccion"
            rows="2"
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="Dirección completa del proveedor"
          ></textarea>
        </div>

        <div class="flex items-center pt-2">
          <label class="flex items-center cursor-pointer">
            <input
              v-model="form.activo"
              type="checkbox"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <span class="ml-2 text-sm text-gray-900">Proveedor activo</span>
          </label>
        </div>

        <div class="flex justify-end space-x-3 pt-4 border-t mt-4">
          <Button variant="secondary" type="button" @click="showModal = false">
            Cancelar
          </Button>
          <Button variant="primary" type="submit" :loading="submitting">
            {{ isEdit ? 'Actualizar' : 'Crear Proveedor' }}
          </Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue';
import { useProvidersStore } from '@/stores/providers';
import { useUiStore } from '@/stores/ui';
import Button from '@/components/common/Button.vue';
import SearchBar from '@/components/common/SearchBar.vue';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';
import { PencilIcon, TrashIcon, PlusIcon, UserGroupIcon, EnvelopeIcon, PhoneIcon } from '@heroicons/vue/24/outline';

const providersStore = useProvidersStore();
const ui = useUiStore();

const searchQuery = ref('');
const showModal = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const selectedProveedor = ref<any>(null);

const form = reactive({
  nombre: '',
  ruc: '',
  contacto: '',
  telefono: '',
  email: '',
  direccion: '',
  categoria: '',
  activo: true,
});

// Filtered proveedores
const filteredProveedores = computed(() => {
  if (!searchQuery.value) {
    return providersStore.proveedores;
  }
  const query = searchQuery.value.toLowerCase();
  return providersStore.proveedores.filter(p => 
    p.nombre.toLowerCase().includes(query) ||
    p.email?.toLowerCase().includes(query) ||
    p.categoria?.toLowerCase().includes(query) ||
    p.ruc?.includes(query)
  );
});

const openCreateModal = () => {
  isEdit.value = false;
  selectedProveedor.value = null;
  resetForm();
  showModal.value = true;
};

const openEditModal = (proveedor: any) => {
  isEdit.value = true;
  selectedProveedor.value = proveedor;
  form.nombre = proveedor.nombre;
  form.ruc = proveedor.ruc || '';
  form.contacto = proveedor.contacto || '';
  form.telefono = proveedor.telefono || '';
  form.email = proveedor.email || '';
  form.direccion = proveedor.direccion || '';
  form.categoria = proveedor.categoria || '';
  form.activo = proveedor.activo ?? true;
  showModal.value = true;
};

const resetForm = () => {
  form.nombre = '';
  form.ruc = '';
  form.contacto = '';
  form.telefono = '';
  form.email = '';
  form.direccion = '';
  form.categoria = '';
  form.activo = true;
};

const handleSubmit = async () => {
  try {
    submitting.value = true;

    if (isEdit.value && selectedProveedor.value) {
      await providersStore.updateProveedor(selectedProveedor.value.id, form);
      ui.showToast('Proveedor actualizado exitosamente', 'success');
    } else {
      await providersStore.createProveedor(form);
      ui.showToast('Proveedor creado exitosamente', 'success');
    }

    showModal.value = false;
    resetForm();
    await providersStore.fetchProveedores(true); // Force refresh
  } catch (error: any) {
    ui.showToast('Error: ' + (error.response?.data?.detail || error.message), 'error');
  } finally {
    submitting.value = false;
  }
};

const confirmDelete = async (proveedor: any) => {
  const ok = await ui.showConfirmWithFallback(`¿Está seguro de eliminar el proveedor "${proveedor.nombre}"?`, 'Eliminar proveedor');
  if (!ok) return;
  try {
    await providersStore.deleteProveedor(proveedor.id);
    await providersStore.fetchProveedores(true);
    ui.showToast('Proveedor eliminado', 'success');
  } catch (error: any) {
    ui.showToast('Error al eliminar: ' + (error.response?.data?.detail || error.message), 'error');
  }
};

onMounted(async () => {
  await providersStore.fetchProveedores();
});
</script>
