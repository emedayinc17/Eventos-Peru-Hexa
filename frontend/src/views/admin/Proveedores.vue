<template>
  <div class="max-w-7xl mx-auto py-8 px-4">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Gestión de Proveedores</h1>
        <p class="text-gray-600 mt-1">Administre los proveedores de servicios</p>
      </div>
      <Button variant="primary" @click="openCreateModal">
        + Nuevo Proveedor
      </Button>
    </div>

    <!-- Search Bar -->
    <Card class="mb-6">
      <SearchBar 
        v-model="searchQuery"
        placeholder="Buscar proveedores por nombre, email o categoría..."
      />
    </Card>

    <!-- Table -->
    <Card :padding="false">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Proveedor
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Contacto
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Categoría
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
            <tr v-if="providersStore.loading" class="hover:bg-gray-50">
              <td colspan="5" class="px-6 py-12 text-center">
                <Loading text="Cargando proveedores..." />
              </td>
            </tr>
            <tr v-else-if="filteredProveedores.length === 0" class="hover:bg-gray-50">
              <td colspan="5" class="px-6 py-12 text-center text-gray-500">
                No se encontraron proveedores
              </td>
            </tr>
            <tr v-else v-for="proveedor in filteredProveedores" :key="proveedor.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ proveedor.nombre }}</div>
                <div class="text-sm text-gray-500" v-if="proveedor.ruc">RUC: {{ proveedor.ruc }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900" v-if="proveedor.email">
                  📧 {{ proveedor.email }}
                </div>
                <div class="text-sm text-gray-500" v-if="proveedor.telefono">
                  📞 {{ proveedor.telefono }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                  {{ proveedor.categoria || 'Sin categoría' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="proveedor.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  {{ proveedor.activo ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                <button
                  @click="openEditModal(proveedor)"
                  class="text-primary-600 hover:text-primary-900"
                >
                  Editar
                </button>
                <button
                  @click="confirmDelete(proveedor)"
                  class="text-red-600 hover:text-red-900"
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
      :title="isEdit ? 'Editar Proveedor' : 'Nuevo Proveedor'"
      max-width="lg"
    >
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Nombre del Proveedor <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.nombre"
            type="text"
            required
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            placeholder="Ej: Eventos Premium SAC"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              RUC
            </label>
            <input
              v-model="form.ruc"
              type="text"
              maxlength="11"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="20123456789"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Categoría <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.categoria"
              required
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
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
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              v-model="form.email"
              type="email"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="contacto@proveedor.com"
            />
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
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Persona de Contacto
          </label>
          <input
            v-model="form.contacto"
            type="text"
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            placeholder="Nombre del contacto principal"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Dirección
          </label>
          <textarea
            v-model="form.direccion"
            rows="2"
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            placeholder="Dirección completa del proveedor"
          ></textarea>
        </div>

        <div class="flex items-center">
          <input
            v-model="form.activo"
            type="checkbox"
            class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label class="ml-2 block text-sm text-gray-900">
            Proveedor activo
          </label>
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
import { useProvidersStore } from '@/stores/providers';
import { useUiStore } from '@/stores/ui';
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';
import SearchBar from '@/components/common/SearchBar.vue';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';

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
  const ok = await ui.showConfirm(`¿Está seguro de eliminar el proveedor "${proveedor.nombre}"?`, 'Eliminar proveedor');
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
