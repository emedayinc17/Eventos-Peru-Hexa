<template>
  <div class="w-full h-full p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Gestión de Servicios</h1>
        <p class="text-gray-600 text-sm mt-1">Administre los servicios disponibles para los eventos</p>
      </div>
      <Button variant="primary" @click="openCreateModal" class="flex items-center gap-2">
        <PlusIcon class="w-5 h-5" />
        Nuevo Servicio
      </Button>
    </div>

    <!-- Search Bar + Estado Filter -->
    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div class="w-full md:w-1/3">
          <SearchBar 
            v-model="searchQuery"
            placeholder="Buscar servicios por nombre o categoría..."
          />
        </div>

        <div class="flex items-center gap-2">
          <label class="text-sm text-gray-600">Estado</label>
          <select v-model="statusFilter" class="rounded border-gray-300 text-sm">
            <option value="all">Todos</option>
            <option value="available">Disponible</option>
            <option value="unavailable">No disponible</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Nombre</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Categoría</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Tipo Evento</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Precio</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="catalogStore.loading">
              <td colspan="6" class="px-6 py-12 text-center">
                <Loading text="Cargando servicios..." />
              </td>
            </tr>
            <tr v-else-if="filteredServicios.length === 0">
              <td colspan="6" class="px-6 py-12 text-center text-gray-500">
                <div class="flex flex-col items-center justify-center">
                  <CubeIcon class="w-12 h-12 text-gray-300 mb-2" />
                  <p>No se encontraron servicios</p>
                </div>
              </td>
            </tr>
            <tr v-else v-for="servicio in paginatedServicios" :key="servicio.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ servicio.nombre }}</div>
                <div class="text-xs text-gray-500 truncate max-w-xs">{{ servicio.descripcion }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div>
                  <template v-if="getCategoria(servicio)">
                    <span class="px-2.5 py-0.5 text-xs font-medium rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                      {{ getCategoria(servicio) || 'Sin categoría' }}
                    </span>
                  </template>
                  <template v-else-if="isOpcionesLoading(servicio)">
                    <div class="h-4 w-28 bg-gray-200 rounded animate-pulse"></div>
                  </template>
                  <template v-else>
                    <span class="px-2.5 py-0.5 text-xs font-medium rounded-full bg-gray-50 text-gray-500 border border-gray-100">Sin categoría</span>
                  </template>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ getTipoEventoName(servicio.tipo_evento_id) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                <template v-if="getPrecio(servicio) && getPrecio(servicio) > 0">
                  S/ {{ getPrecio(servicio).toFixed(2) }}
                </template>
                <template v-else-if="isOpcionesLoading(servicio)">
                  <div class="h-4 w-16 bg-gray-200 rounded animate-pulse inline-block"></div>
                </template>
                <template v-else>
                  S/ 0.00
                </template>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2.5 py-0.5 text-xs font-medium rounded-full border"
                  :class="servicio.disponible ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'"
                >
                  {{ servicio.disponible ? 'Disponible' : 'No disponible' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end gap-2">
                  <button
                    @click="openEditModal(servicio)"
                    class="p-1 text-gray-400 hover:text-primary-600 transition-colors rounded-full hover:bg-primary-50"
                    title="Editar"
                  >
                    <PencilIcon class="w-5 h-5" />
                  </button>
                  <button
                    @click="confirmDelete(servicio)"
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

      <!-- Pagination controls -->
      <div class="px-4 py-3 bg-white border-t border-gray-200 flex items-center justify-between">
        <div class="flex items-center gap-3 text-sm text-gray-600">
          <span>Mostrar</span>
          <select v-model="pageSize" class="rounded border-gray-300 text-sm">
            <option :value="5">5</option>
            <option :value="10">10</option>
            <option :value="20">20</option>
          </select>
          <span>de {{ totalServicios }} servicios</span>
        </div>

        <div class="flex items-center gap-2">
          <button class="px-3 py-1 rounded border" :disabled="currentPage <= 1" @click="currentPage = Math.max(1, Number(currentPage) - 1)">Anterior</button>
          <div class="text-sm">Página {{ currentPage }} / {{ totalPages }}</div>
          <button class="px-3 py-1 rounded border" :disabled="currentPage >= totalPages" @click="currentPage = Math.min(totalPages, Number(currentPage) + 1)">Siguiente</button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Modal 
      :open="showModal" 
      @close="showModal = false"
      :title="isEdit ? 'Editar Servicio' : 'Nuevo Servicio'"
      maxWidth="lg"
    >
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Nombre del Servicio <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.nombre"
            type="text"
            required
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="Ej: Fotografía Premium"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Descripción <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="form.descripcion"
            rows="3"
            required
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="Describe el servicio..."
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
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
              <option value="OTRO">Otros</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Evento <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.tipo_evento_id"
              required
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
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

        <div class="grid grid-cols-2 gap-4 items-start">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Precio Unitario (S/) <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="form.precio_unitario"
              type="number"
              step="0.01"
              min="0"
              required
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
            <select
              v-model="form.disponible"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            >
              <option :value="true">Disponible</option>
              <option :value="false">No disponible</option>
            </select>
          </div>
        </div>

        <div class="flex justify-end space-x-3 pt-4 border-t mt-6">
          <Button variant="secondary" type="button" @click="showModal = false">
            Cancelar
          </Button>
          <Button variant="primary" type="submit" :loading="submitting">
            {{ isEdit ? 'Actualizar' : 'Crear Servicio' }}
          </Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue';
import { useCatalogStore } from '@/stores/catalog';
import { useUiStore } from '@/stores/ui';
import Button from '@/components/common/Button.vue';
import SearchBar from '@/components/common/SearchBar.vue';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';
import { PencilIcon, TrashIcon, PlusIcon, CubeIcon } from '@heroicons/vue/24/outline';

const catalogStore = useCatalogStore();
const ui = useUiStore();

const searchQuery = ref('');
const statusFilter = ref('all'); // 'all' | 'available' | 'unavailable'
const currentPage = ref(1);
const pageSize = ref(10); // default page size; can be 5/10/20
// Helpers para paginación híbrida
const totalServicios = computed(() => catalogStore.serviciosServerSide ? catalogStore.serviciosTotal : filteredServicios.value.length);
const isServerSide = computed(() => catalogStore.serviciosServerSide);
const showModal = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const selectedServicio = ref<any>(null);

const form = reactive({
  nombre: '',
  descripcion: '',
  categoria: '',
  tipo_evento_id: null as string | number | null,
  precio_unitario: 0,
  disponible: true,
});

// Filtered servicios (search across all cached servicios + status filter)
const filteredServicios = computed(() => {
  // Apply status filter first
  const lista = catalogStore.servicios.filter((s: any) => {
    if (statusFilter.value === 'available' && !s.disponible) return false;
    if (statusFilter.value === 'unavailable' && s.disponible) return false;
    return true;
  });

  if (!searchQuery.value) {
    return lista;
  }
  const query = searchQuery.value.toLowerCase();
  return lista.filter((s: any) => 
    String(s.nombre).toLowerCase().includes(query) ||
    String(s.descripcion || '').toLowerCase().includes(query) ||
    String(s.categoria || '').toLowerCase().includes(query)
  );
});

// Pagination helpers (híbrido)
const totalPages = computed(() => Math.max(1, Math.ceil(totalServicios.value / Number(pageSize.value))));
const paginatedServicios = computed(() => {
  if (isServerSide.value) {
    // Ya vienen paginados desde el backend
    return catalogStore.servicios;
  } else {
    const p = Number(currentPage.value) || 1;
    const size = Number(pageSize.value) || 10;
    const start = (p - 1) * size;
    return filteredServicios.value.slice(start, start + size);
  }
});

// Helper functions
const getTipoEventoName = (tipoId: number | string) => {
  const tipo = catalogStore.tiposEvento.find(t => String(t.id) === String(tipoId));
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
  // Normalize to boolean in case backend returns 0/1 or '0'/'1'
  form.disponible = !!servicio.disponible;
  // If the servicio lacks categoria/precio, try to fill from cache first
  try {
    const id = String(servicio.id);
    const cached = catalogStore.opcionesCache[id];
    if ((!form.categoria || form.categoria === '') && Array.isArray(cached) && cached.length > 0) {
      form.categoria = (cached[0].detalles && cached[0].detalles.categoria) || cached[0].categoria || form.categoria;
    }
    if ((!form.precio_unitario || Number(form.precio_unitario) === 0) && Array.isArray(cached) && cached.length > 0) {
      const op = cached[0];
      const monto = op.monto ?? op.precio_unitario ?? null;
      if (monto !== null) form.precio_unitario = Number(monto);
    }
  } catch (e) {
    // ignore
  }

  // Ensure opciones cache for this servicio is populated (non-blocking UI). When it resolves,
  // update the form fields if they are still empty so the modal shows the correct categoria/precio.
  const svcId = String(servicio.id);
  catalogStore.fetchOpcionesForServicio(svcId).then((ops: any[]) => {
      if (ops && ops.length > 0) {
      const op = ops[0];
      if ((!form.categoria || form.categoria === '') && (op.detalles?.categoria || op.categoria)) {
        form.categoria = op.detalles?.categoria || op.categoria || form.categoria;
      }
      const monto = op.monto ?? op.precio_unitario ?? null;
      if ((!form.precio_unitario || Number(form.precio_unitario) === 0) && monto !== null) {
        form.precio_unitario = Number(monto);
      }
        // Also normalize disponible if opciones carries an explicit flag (rare)
        if (op.disponible !== undefined && (form.disponible === undefined || form.disponible === null)) {
          form.disponible = !!op.disponible;
        }
    }
  }).catch(() => {});

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
    // Debug payload snapshot
    console.debug('[Servicios] submit payload', JSON.parse(JSON.stringify(form)));

    if (isEdit.value && selectedServicio.value) {
      // Optimistic update: set local servicio disponible immediately so UI reflects the change
      const localId = String(selectedServicio.value.id);
      const idx = catalogStore.servicios.findIndex((s: any) => String(s.id) === localId);
      let previousDisponible: boolean | undefined = undefined;
      if (idx !== -1) {
        previousDisponible = !!catalogStore.servicios[idx].disponible;
        catalogStore.servicios[idx] = { ...catalogStore.servicios[idx], disponible: !!form.disponible } as any;
      }

      // Send request to backend
      const updated = await catalogStore.updateServicio(selectedServicio.value.id, form);

      // Force refresh opciones cache for this servicio so UI shows updated categoria/precio
      try {
        await catalogStore.fetchOpcionesForServicio(localId, { force: true });
      } catch (e) {
        // ignore
      }

      // If backend returned an updated object, apply it (authoritative)
      if (updated) {
        const merged = { ...catalogStore.servicios[idx], ...updated } as any;
        if (updated && updated.status !== undefined) {
          merged.disponible = Number(updated.status) === 1;
        } else {
          merged.disponible = !!merged.disponible;
        }
        if (idx !== -1) catalogStore.servicios[idx] = merged;
      } else {
        // If backend didn't return updated data, keep optimistic change (already applied). Log for debug.
        console.debug('[Servicios] update returned no body, keeping optimistic change');
      }
    } else {
      const created = await catalogStore.createServicio(form);
      // After creation, prefetch opciones for the new servicio (createServicio also tries to create opcion)
      try {
        await catalogStore.fetchOpcionesForServicio(String(created.id), { force: true });
      } catch (e) {
        // ignore
      }
    }

    showModal.value = false;
    resetForm();
    await catalogStore.fetchServicios({ forceRefresh: true }); // Force refresh
    ui.showToast(isEdit.value ? 'Servicio actualizado' : 'Servicio creado', 'success');
  } catch (error: any) {
    // Revert optimistic change if applicable
    if (isEdit.value && selectedServicio.value) {
      const localId = String(selectedServicio.value.id);
      const idx = catalogStore.servicios.findIndex((s: any) => String(s.id) === localId);
      if (idx !== -1) {
        // Refetch service list to restore authoritative state
        try {
          await catalogStore.fetchServicios();
        } catch (e) {
          // ignore
        }
      }
    }
    ui.showToast('Error: ' + (error.response?.data?.detail || error.message), 'error');
  } finally {
    submitting.value = false;
  }
};

const confirmDelete = async (servicio: any) => {
  const ok = await ui.showConfirmWithFallback(`¿Está seguro de eliminar el servicio "${servicio.nombre}"?`, 'Eliminar servicio');
  if (!ok) return;
  try {
    await catalogStore.deleteServicio(servicio.id);
    await catalogStore.fetchServicios(undefined, true);
    ui.showToast('Servicio eliminado', 'success');
  } catch (error: any) {
    ui.showToast('Error al eliminar: ' + (error.response?.data?.detail || error.message), 'error');
  }
};

onMounted(async () => {
  await catalogStore.fetchTiposEvento();
  await catalogStore.fetchServicios({ page: currentPage.value, pageSize: pageSize.value });
});

// Al cambiar página o tamaño, recargar servicios
watch([currentPage, pageSize], async () => {
  await catalogStore.fetchServicios({ page: currentPage.value, pageSize: pageSize.value });
});

const getCategoria = (servicio: any) => {
  if (servicio.categoria) return servicio.categoria;
  const cached = catalogStore.opcionesCache[String(servicio.id)];
  if (Array.isArray(cached) && cached.length > 0) {
    return (cached[0].detalles && cached[0].detalles.categoria) || cached[0].categoria || '';
  }
  return servicio.categoria || '';
};

const getPrecio = (servicio: any) => {
  if (servicio.precio_unitario !== undefined && servicio.precio_unitario !== null) return Number(servicio.precio_unitario);
  const cached = catalogStore.opcionesCache[String(servicio.id)];
  if (Array.isArray(cached) && cached.length > 0) {
    const op = cached[0];
    const monto = op.monto ?? op.precio_unitario ?? 0;
    return Number(monto || 0);
  }
  return 0;
};

const isOpcionesLoading = (servicio: any) => {
  return !!catalogStore.opcionesLoading[String(servicio.id)];
};

// Keep currentPage valid when pageSize or filtered length changes
watch(pageSize, () => { currentPage.value = 1; });
watch(() => filteredServicios.value.length, () => {
  if (Number(currentPage.value) > Number(totalPages.value)) {
    currentPage.value = Number(totalPages.value);
  }
});
</script>
