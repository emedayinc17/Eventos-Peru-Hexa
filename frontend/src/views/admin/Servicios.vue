<template>
  <div class="max-w-7xl mx-auto py-8 px-4">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Gestión de Servicios</h1>
        <p class="text-gray-600 mt-1">Administre los servicios disponibles</p>
      </div>
      <Button variant="primary" @click="openCreateModal">
        + Nuevo Servicio
      </Button>
    </div>

    <!-- Search Bar -->
    <Card class="mb-6">
      <SearchBar 
        v-model="searchQuery"
        placeholder="Buscar servicios por nombre o categoría..."
      />
    </Card>

    <!-- Table -->
    <Card :padding="false">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nombre
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Categoría
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tipo Evento
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Precio
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
            <tr v-if="catalogStore.loading" class="hover:bg-gray-50">
              <td colspan="6" class="px-6 py-12 text-center">
                <Loading text="Cargando servicios..." />
              </td>
            </tr>
            <tr v-else-if="filteredServicios.length === 0" class="hover:bg-gray-50">
              <td colspan="6" class="px-6 py-12 text-center text-gray-500">
                No se encontraron servicios
              </td>
            </tr>
            <tr v-else v-for="servicio in filteredServicios" :key="servicio.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ servicio.nombre }}</div>
                <div class="text-sm text-gray-500">{{ servicio.descripcion }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                  {{ servicio.categoria || 'Sin categoría' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ getTipoEventoName(servicio.tipo_evento_id) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary-600">
                S/ {{ servicio.precio_unitario?.toFixed(2) || '0.00' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="servicio.disponible ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  {{ servicio.disponible ? 'Disponible' : 'No disponible' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                <button
                  @click="openEditModal(servicio)"
                  class="text-primary-600 hover:text-primary-900"
                >
                  Editar
                </button>
                <button
                  @click="confirmDelete(servicio)"
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
      :title="isEdit ? 'Editar Servicio' : 'Nuevo Servicio'"
      max-width="lg"
    >
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Nombre del Servicio <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.nombre"
            type="text"
            required
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            placeholder="Ej: Fotografía Premium"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Descripción <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="form.descripcion"
            rows="3"
            required
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            placeholder="Describe el servicio..."
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
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
              <option value="OTROS">Otros</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Evento <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.tipo_evento_id"
              required
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              <option :value="null">Seleccione tipo</option>
              <option 
                v-for="tipo in catalogStore.tiposEvento" 
                :key="tipo.id"
                :value="tipo.id"
              >
                {{ tipo.nombre }}
              </option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Precio Unitario (S/) <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="form.precio_unitario"
              type="number"
              step="0.01"
              min="0"
              required
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>

          <div class="flex items-center mt-8">
            <input
              v-model="form.disponible"
              type="checkbox"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label class="ml-2 block text-sm text-gray-900">
              Disponible
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
import { useCatalogStore } from '@/stores/catalog';
import { useUiStore } from '@/stores/ui';
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';
import SearchBar from '@/components/common/SearchBar.vue';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';

const catalogStore = useCatalogStore();
const ui = useUiStore();

const searchQuery = ref('');
const showModal = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const selectedServicio = ref<any>(null);

const form = reactive({
  nombre: '',
  descripcion: '',
  categoria: '',
  tipo_evento_id: null as number | null,
  precio_unitario: 0,
  disponible: true,
});

// Filtered servicios
const filteredServicios = computed(() => {
  if (!searchQuery.value) {
    return catalogStore.servicios;
  }
  const query = searchQuery.value.toLowerCase();
  return catalogStore.servicios.filter(s => 
    s.nombre.toLowerCase().includes(query) ||
    s.descripcion?.toLowerCase().includes(query) ||
    s.categoria?.toLowerCase().includes(query)
  );
});

// Helper functions
const getTipoEventoName = (tipoId: number) => {
  const tipo = catalogStore.tiposEvento.find(t => t.id === tipoId);
  return tipo?.nombre || 'Desconocido';
};

const openCreateModal = () => {
  isEdit.value = false;
  selectedServicio.value = null;
  resetForm();
  showModal.value = true;
};

const openEditModal = (servicio: any) => {
  isEdit.value = true;
  selectedServicio.value = servicio;
  form.nombre = servicio.nombre;
  form.descripcion = servicio.descripcion || '';
  form.categoria = servicio.categoria || '';
  form.tipo_evento_id = servicio.tipo_evento_id;
  form.precio_unitario = servicio.precio_unitario || 0;
  form.disponible = servicio.disponible ?? true;
  showModal.value = true;
};

const resetForm = () => {
  form.nombre = '';
  form.descripcion = '';
  form.categoria = '';
  form.tipo_evento_id = null;
  form.precio_unitario = 0;
  form.disponible = true;
};

const handleSubmit = async () => {
  try {
    submitting.value = true;

    if (isEdit.value && selectedServicio.value) {
      await catalogStore.updateServicio(selectedServicio.value.id, form);
    } else {
      await catalogStore.createServicio(form);
    }

    showModal.value = false;
    resetForm();
    await catalogStore.fetchServicios(true); // Force refresh
  } catch (error: any) {
    ui.showToast('Error: ' + (error.response?.data?.detail || error.message), 'error');
  } finally {
    submitting.value = false;
  }
};

const confirmDelete = async (servicio: any) => {
  const ok = await ui.showConfirm(`¿Está seguro de eliminar el servicio "${servicio.nombre}"?`, 'Eliminar servicio');
  if (!ok) return;
  try {
    await catalogStore.deleteServicio(servicio.id);
    await catalogStore.fetchServicios(true);
    ui.showToast('Servicio eliminado', 'success');
  } catch (error: any) {
    ui.showToast('Error al eliminar: ' + (error.response?.data?.detail || error.message), 'error');
  }
};

onMounted(async () => {
  await catalogStore.fetchTiposEvento();
  await catalogStore.fetchServicios();
});
</script>
