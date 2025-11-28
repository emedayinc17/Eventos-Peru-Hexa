<template>
  <div class="max-w-7xl mx-auto py-8 px-4">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Gestión de Paquetes</h1>
        <p class="text-gray-600 mt-1">Administre los paquetes de eventos</p>
      </div>
      <Button variant="primary" @click="openCreateModal">
        + Nuevo Paquete
      </Button>
    </div>

    <!-- Search & Filter -->
    <Card class="mb-6">
      <div class="flex gap-4">
        <div class="flex-1">
          <SearchBar 
            v-model="searchQuery"
            placeholder="Buscar paquetes por nombre..."
          />
        </div>
        <select
          v-model="filterTipo"
          class="rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        >
          <option value="">Todos los tipos</option>
          <option v-for="tipo in catalogStore.tiposEvento" :key="tipo.id" :value="tipo.id">
            {{ tipo.nombre }}
          </option>
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
                Paquete
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tipo Evento
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Servicios Incluidos
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Precio Base
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="catalogStore.loading">
              <td colspan="5" class="px-6 py-12 text-center">
                <Loading text="Cargando paquetes..." />
              </td>
            </tr>
            <tr v-else-if="filteredPaquetes.length === 0">
              <td colspan="5" class="px-6 py-12 text-center text-gray-500">
                No se encontraron paquetes
              </td>
            </tr>
            <tr v-else v-for="paquete in filteredPaquetes" :key="paquete.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">{{ paquete.nombre }}</div>
                <div class="text-sm text-gray-500">{{ paquete.descripcion }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ getTipoEventoName(paquete.tipo_evento_id) }}
              </td>
              <td class="px-6 py-4">
                <div class="flex flex-wrap gap-1">
                  <span 
                    v-for="servicio in paquete.servicios?.slice(0, 3)" 
                    :key="servicio.id"
                    class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800"
                  >
                    {{ servicio.nombre }}
                  </span>
                  <span v-if="(paquete.servicios?.length || 0) > 3" class="text-xs text-gray-500 self-center">
                    +{{ (paquete.servicios?.length || 0) - 3 }} más
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary-600">
                S/ {{ paquete.precio_base?.toFixed(2) || '0.00' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                <button
                  @click="openEditModal(paquete)"
                  class="text-primary-600 hover:text-primary-900"
                >
                  Editar
                </button>
                <button
                  @click="confirmDelete(paquete)"
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
      :title="isEdit ? 'Editar Paquete' : 'Nuevo Paquete'"
      max-width="2xl"
    >
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Nombre del Paquete <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.nombre"
            type="text"
            required
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            placeholder="Ej: Paquete Boda Clásica"
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
            placeholder="Describe el paquete..."
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Evento <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.tipo_evento_id"
              @change="onTipoEventoChange"
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

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Precio Base (S/) <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="form.precio_base"
              type="number"
              step="0.01"
              min="0"
              required
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
        </div>

        <!-- Multi-select Servicios -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Servicios Incluidos <span class="text-red-500">*</span>
          </label>
          <div class="border rounded-lg p-4 max-h-64 overflow-y-auto bg-gray-50">
            <div v-if="availableServicios.length === 0" class="text-center text-gray-500 py-4">
              Seleccione un tipo de evento para ver servicios disponibles
            </div>
            <div v-else class="space-y-2">
              <label 
                v-for="servicio in availableServicios" 
                :key="servicio.id"
                class="flex items-start p-2 hover:bg-white rounded cursor-pointer"
              >
                <input
                  type="checkbox"
                  :value="servicio.id"
                  v-model="form.servicios_ids"
                  class="mt-1 text-primary-600 focus:ring-primary-500 rounded"
                />
                <div class="ml-3 flex-1">
                  <div class="text-sm font-medium text-gray-900">{{ servicio.nombre }}</div>
                  <div class="text-xs text-gray-500">
                    {{ servicio.categoria }} - S/ {{ servicio.precio_unitario?.toFixed(2) }}
                  </div>
                </div>
              </label>
            </div>
          </div>
          <p class="text-sm text-gray-500 mt-1">
            {{ form.servicios_ids.length }} servicio(s) seleccionado(s)
          </p>
        </div>

        <div class="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="secondary" type="button" @click="showModal = false">
            Cancelar
          </Button>
          <Button variant="primary" type="submit" :loading="submitting" :disabled="form.servicios_ids.length === 0">
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
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';
import SearchBar from '@/components/common/SearchBar.vue';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';
import { useUiStore } from '@/stores/ui';

const catalogStore = useCatalogStore();
const ui = useUiStore();

const searchQuery = ref('');
const filterTipo = ref<number | ''>('');
const showModal = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const selectedPaquete = ref<any>(null);

const form = reactive({
  nombre: '',
  descripcion: '',
  tipo_evento_id: null as number | null,
  precio_base: 0,
  servicios_ids: [] as number[],
});

// Filtered paquetes
const filteredPaquetes = computed(() => {
  let result = catalogStore.paquetes;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(p => 
      p.nombre.toLowerCase().includes(query) ||
      p.descripcion?.toLowerCase().includes(query)
    );
  }
  
  if (filterTipo.value) {
    result = result.filter(p => p.tipo_evento_id === filterTipo.value);
  }
  
  return result;
});

// Available servicios for selected tipo_evento
const availableServicios = computed(() => {
  if (!form.tipo_evento_id) return [];
  return catalogStore.servicios.filter(s => s.tipo_evento_id === form.tipo_evento_id);
});

// Helper functions
const getTipoEventoName = (tipoId: number) => {
  const tipo = catalogStore.tiposEvento.find(t => t.id === tipoId);
  return tipo?.nombre || 'Desconocido';
};

const onTipoEventoChange = () => {
  // Clear selected servicios when tipo changes
  form.servicios_ids = [];
};

const openCreateModal = () => {
  isEdit.value = false;
  selectedPaquete.value = null;
  resetForm();
  showModal.value = true;
};

const openEditModal = (paquete: any) => {
  isEdit.value = true;
  selectedPaquete.value = paquete;
  form.nombre = paquete.nombre;
  form.descripcion = paquete.descripcion || '';
  form.tipo_evento_id = paquete.tipo_evento_id;
  form.precio_base = paquete.precio_base || 0;
  form.servicios_ids = paquete.servicios?.map((s: any) => s.id) || [];
  showModal.value = true;
};

const resetForm = () => {
  form.nombre = '';
  form.descripcion = '';
  form.tipo_evento_id = null;
  form.precio_base = 0;
  form.servicios_ids = [];
};

const handleSubmit = async () => {
  try {
    submitting.value = true;

    if (isEdit.value && selectedPaquete.value) {
      await catalogStore.updatePaquete(selectedPaquete.value.id, form);
    } else {
      await catalogStore.createPaquete(form);
    }

    showModal.value = false;
    resetForm();
    await catalogStore.fetchPaquetes(true);
  } catch (error: any) {
    ui.showToast('Error: ' + (error.response?.data?.detail || error.message), 'error');
  } finally {
    submitting.value = false;
  }
};

const confirmDelete = async (paquete: any) => {
  const ok = await ui.showConfirm(`¿Está seguro de eliminar el paquete "${paquete.nombre}"?`, 'Eliminar paquete');
  if (!ok) return;
  try {
    await catalogStore.deletePaquete(paquete.id);
    await catalogStore.fetchPaquetes(true);
    ui.showToast('Paquete eliminado', 'success');
  } catch (error: any) {
    ui.showToast('Error al eliminar: ' + (error.response?.data?.detail || error.message), 'error');
  }
};

onMounted(async () => {
  await catalogStore.fetchTiposEvento();
  await catalogStore.fetchServicios();
  await catalogStore.fetchPaquetes();
});
</script>
