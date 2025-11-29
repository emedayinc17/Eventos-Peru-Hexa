<template>
  <div class="w-full h-full p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Gestión de Paquetes</h1>
        <p class="text-gray-600 text-sm mt-1">Administre los paquetes de eventos y sus servicios incluidos</p>
      </div>
      <Button variant="primary" @click="openCreateModal" class="flex items-center gap-2">
        <PlusIcon class="w-5 h-5" />
        Nuevo Paquete
      </Button>
    </div>

    <!-- Search & Filter -->
    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div class="flex-1 md:max-w-md">
          <SearchBar 
            v-model="searchQuery"
            placeholder="Buscar paquetes por nombre..."
          />
        </div>

        <div class="flex items-center gap-3">
          <select
            v-model="filterTipo"
            class="rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          >
            <option value="">Todos los tipos</option>
            <option v-for="tipo in catalogStore.tiposEvento" :key="tipo.id" :value="tipo.id">
              {{ tipo.nombre }}
            </option>
          </select>

          <select v-model="statusFilter" class="rounded-lg border-gray-300 shadow-sm sm:text-sm">
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
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Paquete</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Tipo Evento</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Servicios Incluidos</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Precio Base</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Acciones</th>
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
                <div class="flex flex-col items-center justify-center">
                  <ArchiveBoxIcon class="w-12 h-12 text-gray-300 mb-2" />
                  <p>No se encontraron paquetes</p>
                </div>
              </td>
            </tr>
            <tr v-else v-for="paquete in paginatedPaquetes" :key="paquete.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">{{ paquete.nombre }}</div>
                <div class="text-xs text-gray-500 truncate max-w-xs">{{ paquete.descripcion }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ paquete.tipo_evento_nombre || getTipoEventoName(paquete.tipo_evento_id) }}
              </td>
              <td class="px-6 py-4">
                <div class="flex flex-wrap gap-1">
                  <span 
                    v-for="servicio in (catalogStore.paquetesCache[String(paquete.id)]?.servicios || paquete.servicios || []).slice(0, 3)" 
                    :key="servicio.id"
                    class="px-2 py-0.5 text-xs font-medium rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100"
                  >
                    {{ servicio.nombre }}
                  </span>
                  <span v-if="((catalogStore.paquetesCache[String(paquete.id)]?.servicios || paquete.servicios || []).length || 0) > 3" class="px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-600 border border-gray-200">
                    +{{ ((catalogStore.paquetesCache[String(paquete.id)]?.servicios || paquete.servicios || []).length || 0) - 3 }} más
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                S/ {{ paquete.precio_base?.toFixed(2) || '0.00' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2.5 py-0.5 text-xs font-medium rounded-full border"
                  :class="(paquete.status === undefined ? 'bg-gray-50 text-gray-600 border-gray-100' : (Number(paquete.status) === 1 ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'))"
                >
                  {{ paquete.status === undefined ? 'Desconocido' : (Number(paquete.status) === 1 ? 'Activo' : 'Inactivo') }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end gap-2">
                  <button
                    @click="openEditModal(paquete)"
                    class="p-1 text-gray-400 hover:text-primary-600 transition-colors rounded-full hover:bg-primary-50"
                    title="Editar"
                  >
                    <PencilIcon class="w-5 h-5" />
                  </button>
                  <button
                    @click="confirmDelete(paquete)"
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
    <div v-if="lastRequestUrl" class="fixed top-20 right-6 z-50">
      <div class="bg-yellow-50 border border-yellow-200 text-yellow-800 px-3 py-2 rounded shadow-sm text-sm">
        Request URL: <span class="font-mono">{{ lastRequestUrl }}</span>
      </div>
    </div>
    <Modal 
      v-model:open="showModal"
      :title="isEdit ? 'Editar Paquete' : 'Nuevo Paquete'"
      maxWidth="2xl"
    >
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Nombre del Paquete <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.nombre"
            type="text"
            required
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="Ej: Paquete Boda Clásica"
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
            placeholder="Describe el paquete..."
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Evento <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.tipo_evento_id"
              @change="onTipoEventoChange"
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

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Precio Base (S/) <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="form.precio_base"
              type="number"
              step="0.01"
              min="0"
              required
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            />
          </div>
        </div>

        <!-- Multi-select Servicios -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Servicios Incluidos <span class="text-red-500">*</span>
          </label>
          <input 
            v-if="form.tipo_evento_id"
            v-model="servicioSearch"
            type="text"
            placeholder="Buscar servicios por nombre o categoría..."
            class="w-full mb-2 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
          />
          <div class="border border-gray-300 rounded-lg overflow-hidden">
            <div class="bg-gray-50 px-4 py-2 border-b border-gray-200 text-xs font-medium text-gray-500 uppercase">
              Seleccione los servicios
            </div>
            <div class="max-h-60 overflow-y-auto p-2 bg-white">
              <div v-if="loadingServiciosInModal" class="text-center text-gray-500 py-8">
                <svg class="w-6 h-6 mx-auto animate-spin mb-2" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                </svg>
                <p class="text-sm">Cargando servicios...</p>
              </div>
              <div v-else-if="availableServicios.length === 0" class="text-center text-gray-500 py-8">
                <p class="text-sm">Seleccione un tipo de evento para ver servicios disponibles</p>
              </div>
              <div v-else class="space-y-1">
                <label 
                  v-for="servicio in availableServicios" 
                  :key="servicio.id"
                  class="flex items-start p-2 hover:bg-gray-50 rounded-md cursor-pointer transition-colors"
                  :class="{'bg-indigo-50': form.servicios_ids.includes(servicio.id)}"
                >
                  <input
                    type="checkbox"
                    :value="servicio.id"
                    v-model="form.servicios_ids"
                    class="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <div class="ml-3 flex-1">
                    <div class="text-sm font-medium text-gray-900">{{ servicio.nombre }}</div>
                    <div class="flex justify-between items-center mt-0.5">
                      <span class="text-xs text-gray-500">{{ servicio.categoria }}</span>
                      <div class="flex items-center gap-2">
                        <span class="text-xs font-medium text-gray-900">S/ {{ servicio.precio_unitario?.toFixed(2) }}</span>
                        <!-- Warning icon if servicio has no opciones resolved -->
                        <span v-if="!servicioTieneOpciones(servicio.id) && !servicioOpcionesLoading(servicio.id)" title="No tiene opciones registradas. Se creará automáticamente una opción por defecto al hacer clic." class="text-yellow-600 flex items-center gap-2">
                          <ExclamationTriangleIcon class="w-4 h-4" />
                          <button @click.stop="createOpcionDirecta(servicio)" type="button" class="text-xs text-yellow-800 hover:underline">Crear opción</button>
                        </span>
                        <span v-else-if="servicioOpcionesLoading(servicio.id)" title="Cargando opciones..." class="text-gray-400">
                          <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                          </svg>
                        </span>
                        <span v-else-if="creatingOpcion[String(servicio.id)]" class="text-gray-500 text-xs">Creando...</span>
                      </div>
                    </div>
                  </div>
                </label>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-2 border-t border-gray-200 text-xs text-gray-500 flex justify-between">
              <span>{{ form.servicios_ids.length }} servicio(s) seleccionado(s)</span>
              <span v-if="form.servicios_ids.length > 0" class="font-medium text-primary-700 cursor-pointer hover:underline" @click="form.servicios_ids = []">Limpiar selección</span>
            </div>
          </div>
        </div>

        <div class="flex justify-end space-x-3 pt-4 border-t mt-6">
          <Button variant="secondary" type="button" @click="showModal = false">
            Cancelar
          </Button>
          <Button variant="primary" type="submit" :loading="submitting" :disabled="!isPaqueteFormValid">
            {{ isEdit ? 'Actualizar' : 'Crear Paquete' }}
          </Button>
        </div>
        <div v-if="Object.keys(paqueteFormErrors).length > 0" class="text-sm text-red-600 mt-2">
          <div v-if="paqueteFormErrors.nombre">{{ paqueteFormErrors.nombre }}</div>
          <div v-if="paqueteFormErrors.descripcion">{{ paqueteFormErrors.descripcion }}</div>
          <div v-if="paqueteFormErrors.tipo">{{ paqueteFormErrors.tipo }}</div>
          <div v-if="paqueteFormErrors.precio">{{ paqueteFormErrors.precio }}</div>
          <div v-if="paqueteFormErrors.servicios">{{ paqueteFormErrors.servicios }}</div>
        </div>
      </form>
    </Modal>
    <!-- Modal para crear Opción de Servicio -->
    <div v-if="lastRequestUrl" class="fixed top-40 right-6 z-50">
      <div class="bg-yellow-50 border border-yellow-200 text-yellow-800 px-3 py-2 rounded shadow-sm text-sm">
        Request URL: <span class="font-mono">{{ lastRequestUrl }}</span>
      </div>
    </div>
    <!-- Modal de opción eliminado: ahora la creación es directa y automática -->

    <!-- Pagination controls (hybrid) -->
    <div class="mt-4">
      <div class="px-4 py-3 bg-white border-t border-gray-200 flex items-center justify-between">
        <div class="flex items-center gap-3 text-sm text-gray-600">
          <span>Mostrar</span>
          <select v-model="pageSize" class="rounded border-gray-300 text-sm">
            <option :value="5">5</option>
            <option :value="10">10</option>
            <option :value="20">20</option>
          </select>
          <span>de {{ totalPaquetes }} paquetes</span>
        </div>
        <div class="flex items-center gap-2">
          <button class="px-3 py-1 rounded border" :disabled="currentPage <= 1" @click="currentPage = Math.max(1, Number(currentPage) - 1)">Anterior</button>
          <div class="text-sm">Página {{ currentPage }} / {{ totalPages }}</div>
          <button class="px-3 py-1 rounded border" :disabled="currentPage >= totalPages" @click="currentPage = Math.min(totalPages, Number(currentPage) + 1)">Siguiente</button>
        </div>
    </div>
  </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch, nextTick } from 'vue';
import { useCatalogStore } from '@/stores/catalog';
import { catalogApi } from '@/api';
import Button from '@/components/common/Button.vue';
import SearchBar from '@/components/common/SearchBar.vue';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';
import { useUiStore } from '@/stores/ui';
import { PencilIcon, TrashIcon, PlusIcon, ArchiveBoxIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline';

const catalogStore = useCatalogStore();
const ui = useUiStore();

const searchQuery = ref('');
const filterTipo = ref<string | number | ''>('');
const currentPage = ref(1);
const pageSize = ref(10);
const statusFilter = ref('all'); // 'all' | 'available' | 'unavailable'
const showModal = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const selectedPaquete = ref<any>(null);

const form = reactive({
  nombre: '',
  descripcion: '',
  tipo_evento_id: null as string | number | null,
  precio_base: 0,
  servicios_ids: [] as (string | number)[],
});

// Hybrid pagination helpers
const filteredPaquetes = computed(() => {
  let result = catalogStore.paquetes;
  // Status filter
  if (statusFilter.value === 'available') {
    result = result.filter((p: any) => Number(p.status) === 1 || p.status === true || p.disponible === true);
  } else if (statusFilter.value === 'unavailable') {
    result = result.filter((p: any) => Number(p.status) === 0 || p.status === false || p.disponible === false);
  }
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter((p: any) => 
      String(p.nombre).toLowerCase().includes(query) ||
      String(p.descripcion || '').toLowerCase().includes(query)
    );
  }
  if (filterTipo.value) {
    result = result.filter((p: any) => String(p.tipo_evento_id) === String(filterTipo.value));
  }
  return result;
});

const isServerSide = computed(() => catalogStore.paquetesServerSide);
const totalPaquetes = computed(() => isServerSide.value ? catalogStore.paquetesTotal : filteredPaquetes.value.length);
const totalPages = computed(() => Math.max(1, Math.ceil(totalPaquetes.value / Number(pageSize.value))));
const paginatedPaquetes = computed(() => {
  if (isServerSide.value) {
    return catalogStore.paquetes;
  } else {
    const p = Number(currentPage.value) || 1;
    const size = Number(pageSize.value) || 10;
    const start = (p - 1) * size;
    return filteredPaquetes.value.slice(start, start + size);
  }
});

// Available servicios for selected tipo_evento
const servicioSearch = ref('');

// Local loading flag for servicios when the modal requests them
const loadingServiciosInModal = ref(false);

const availableServicios = computed(() => {
  if (!form.tipo_evento_id) return [];
  
  // Filter by tipo_evento first
  let result = catalogStore.servicios.filter(s => String(s.tipo_evento_id) === String(form.tipo_evento_id));
  
  // Filter by search query
  if (servicioSearch.value) {
    const query = servicioSearch.value.toLowerCase();
    result = result.filter(s => 
      s.nombre.toLowerCase().includes(query) || 
      s.categoria?.toLowerCase().includes(query)
    );
  }
  
  return result;
});

// Helpers to check opciones cache/loading per servicio
const servicioOpcionesLoading = (servicioId: string | number) => {
  const id = String(servicioId);
  return !!(catalogStore.opcionesLoading && catalogStore.opcionesLoading[id]);
};

const servicioTieneOpciones = (servicioId: string | number) => {
  const id = String(servicioId);
  const arr = catalogStore.opcionesCache ? catalogStore.opcionesCache[id] : undefined;
  return Array.isArray(arr) && arr.length > 0;
};

const creatingOpcion = ref<Record<string, boolean>>({});

// Modal-driven creación de opción (mejor UX que window.prompt)
const showOpcionModal = ref(false);
const opcionServicioSelected = ref<any>(null);
const opcionForm = reactive({ nombre: '', monto: 0, moneda: 'PEN' });


// Nueva función: crear opción directa (sin modal)
const createOpcionDirecta = async (servicio: any) => {
  const sid = String(servicio.id);
  if (creatingOpcion.value[sid]) return;
  creatingOpcion.value = { ...creatingOpcion.value, [sid]: true };
  try {
    // Datos por defecto
    const payload = {
      servicio_id: sid,
      nombre: `${servicio.nombre} - opción`,
      moneda: 'PEN',
      monto: Number(servicio.precio_unitario ?? 0),
      detalles: {},
    };
    // Validación mínima
    if (!payload.nombre || payload.monto <= 0) {
      ui.showToast('No se puede crear opción: datos incompletos', 'error');
      return;
    }
    // Crear opción
    await catalogApi.createOpcion(payload);
    ui.showToast('Opción creada automáticamente', 'success');
    // Refrescar opciones en background
    catalogStore.fetchOpcionesForServicio(sid, { force: true }).catch(() => {});
  } catch (e: any) {
    ui.showToast('Error al crear opción: ' + (e.response?.data?.detail || e.message), 'error');
  } finally {
    const copy = { ...creatingOpcion.value };
    delete copy[sid];
    creatingOpcion.value = copy;
  }
};

const isSubmittingOpcion = ref(false);
// Show last request URL in UI for debugging (absolute URL as sent by the browser)
const lastRequestUrl = ref('');

// Validation for opcion form
const opcionFormErrors = ref<{ nombre?: string; monto?: string; permiso?: string }>({});
const isOpcionFormValid = computed(() => {
  opcionFormErrors.value = {};
  if (!opcionServicioSelected.value) {
    opcionFormErrors.value.permiso = 'Servicio no seleccionado';
  }
  if (!opcionForm.nombre || String(opcionForm.nombre).trim().length < 3) {
    opcionFormErrors.value.nombre = 'Nombre mínimo 3 caracteres';
  }
  if (opcionForm.monto === null || opcionForm.monto === undefined || Number(opcionForm.monto) <= 0) {
    opcionFormErrors.value.monto = 'Monto debe ser mayor que 0';
  }
  return Object.keys(opcionFormErrors.value).length === 0;
});

const submitCreateOpcion = async () => {
  const servicio = opcionServicioSelected.value;
  if (!servicio) return;
  const sid = String(servicio.id);
  if (creatingOpcion.value[sid] || isSubmittingOpcion.value) return;

  creatingOpcion.value = { ...creatingOpcion.value, [sid]: true };
  isSubmittingOpcion.value = true;
  console.debug('[Paquetes] submitCreateOpcion start', { servicioId: sid, nombre: opcionForm.nombre, monto: opcionForm.monto, moneda: opcionForm.moneda });

  // Validación rápida antes de cerrar modal
  if (!isOpcionFormValid.value) {
    ui.showToast('Por favor corrija los errores del formulario', 'error');
    isSubmittingOpcion.value = false;
    const copy = { ...creatingOpcion.value };
    delete copy[sid];
    creatingOpcion.value = copy;
    return null;
  }

  // Cerrar el modal inmediatamente para UX ágil
  showOpcionModal.value = false;
  await nextTick();

  // Guardar datos del form antes de limpiar
  const payload = { servicio_id: sid, nombre: opcionForm.nombre, moneda: opcionForm.moneda, monto: Number(opcionForm.monto), detalles: {} };
  opcionServicioSelected.value = null;
  opcionForm.nombre = '';
  opcionForm.monto = 0;
  opcionForm.moneda = 'PEN';

  // Petición y refresco en background
  (async () => {
    try {
      // Ensure admin token present
      const token = localStorage.getItem('access_token');
      if (!token) {
        ui.showToast('Debes iniciar sesión como administrador para crear opciones', 'error');
        return;
      }
      lastRequestUrl.value = window.location.origin + '/api/catalogo/v1/admin/opciones';
      const created = await catalogApi.createOpcion(payload);
      ui.showToast('Opción creada', 'success');
      // Refresca opciones en background
      catalogStore.fetchOpcionesForServicio(sid, { force: true }).catch((err: any) => {
        console.warn('[Paquetes] fetchOpcionesForServicio post-create failed', err);
      });
      console.debug('[Paquetes] submitCreateOpcion success', created);
    } catch (e: any) {
      console.error('[Paquetes] createOpcion failed', e);
      ui.showToast('Error al crear opción: ' + (e.response?.data?.detail || e.message || String(e)), 'error');
    } finally {
      const copy = { ...creatingOpcion.value };
      delete copy[sid];
      creatingOpcion.value = copy;
      isSubmittingOpcion.value = false;
    }
  })();
};

// Paquete form validations
const paqueteFormErrors = ref<{ nombre?: string; descripcion?: string; tipo?: string; servicios?: string; precio?: string }>({});
const isPaqueteFormValid = computed(() => {
  paqueteFormErrors.value = {};
  if (!form.nombre || String(form.nombre).trim().length < 3) paqueteFormErrors.value.nombre = 'Nombre mínimo 3 caracteres';
  if (!form.descripcion || String(form.descripcion).trim().length < 3) paqueteFormErrors.value.descripcion = 'Descripción mínima 3 caracteres';
  if (!form.tipo_evento_id) paqueteFormErrors.value.tipo = 'Seleccione un tipo de evento';
  if (!form.precio_base || Number(form.precio_base) <= 0) paqueteFormErrors.value.precio = 'Precio base debe ser mayor que 0';
  if (!Array.isArray(form.servicios_ids) || form.servicios_ids.length === 0) paqueteFormErrors.value.servicios = 'Seleccione al menos un servicio';
  return Object.keys(paqueteFormErrors.value).length === 0;
});

// Helper functions
const getTipoEventoName = (tipoId: number | string) => {
  const tipo = catalogStore.tiposEvento.find(t => String(t.id) === String(tipoId));
  return tipo?.nombre || 'Desconocido';
};

const onTipoEventoChange = async () => {
  // Clear selected servicios when tipo changes
  form.servicios_ids = [];
  servicioSearch.value = '';
  // Fetch servicios specifically for this tipo to ensure we have them all
  if (form.tipo_evento_id) {
    loadingServiciosInModal.value = true;
    try {
      await catalogStore.fetchServicios(Number(form.tipo_evento_id), true);
    } catch (e: any) {
      ui.showToast('Error al cargar servicios: ' + (e.response?.data?.detail || e.message), 'error');
    } finally {
      loadingServiciosInModal.value = false;
    }
  }
};

// Auto-calculate price when services change
// Auto-calculate price when services change
watch(() => form.servicios_ids, (newIds) => {
  // If we are in edit mode and just opened the modal (loading initial values), we might not want to overwrite the price.
  // However, tracking that state is complex. For now, let's allow auto-calc but maybe we can improve it later if requested.
  // The user specifically asked for "when creating a new package".
  // Let's check if we are editing and if the price is already set to something else? 
  // A simple approach: Always calculate sum. If the user wants a different price, they can edit it AFTER selecting services.
  // But if they select a service, it will overwrite their manual edit.
  
  if (!newIds) return;

  let total = 0;
  const allServices = catalogStore.servicios;
  
  newIds.forEach(sid => {
    const s = allServices.find(serv => String(serv.id) === String(sid));
    if (s && s.precio_unitario) {
      total += Number(s.precio_unitario);
    }
  });
  
  // Only update if total > 0 (to avoid resetting to 0 if data isn't loaded yet)
  if (total > 0) {
    form.precio_base = total;
  }
}, { deep: true });

const openCreateModal = () => {
  isEdit.value = false;
  selectedPaquete.value = null;
  resetForm();
  showModal.value = true;
};

const openEditModal = async (paquete: any) => {
  isEdit.value = true;
  selectedPaquete.value = paquete;
  form.nombre = paquete.nombre;
  form.descripcion = paquete.descripcion || '';
  form.tipo_evento_id = paquete.tipo_evento_id;
  form.precio_base = paquete.precio_base || 0;
  servicioSearch.value = '';

  // Ensure services for the tipo_evento are loaded
  if (form.tipo_evento_id) {
    await catalogStore.fetchServicios(Number(form.tipo_evento_id));
  }

  // Fetch paquete detalle to obtain opcion_servicio -> servicio mapping and prefill servicios_ids
  try {
    const detalle = await catalogStore.getPaquete(paquete.id);
    // detalle.items is expected to contain opcion_servicio_id and servicio_id (we added this in backend)
    if (Array.isArray(detalle.items) && detalle.items.length > 0) {
      // Map to servicio ids when possible
      const servicioIds: (string | number)[] = [];
      for (const it of detalle.items) {
        if (it.servicio_id) {
          servicioIds.push(it.servicio_id);
        } else if (it.opcion_servicio_id) {
          // If only opcion id available, try to resolve to servicio by searching opcionesCache
          // Scan opcionesCache for matching opcion id
          const match = Object.entries(catalogStore.opcionesCache).find(([_k, arr]: any) => Array.isArray(arr) && arr.some((o: any) => String(o.id) === String(it.opcion_servicio_id)));
          if (match) {
            const svcId = (match[0]);
            servicioIds.push(svcId);
          }
        }
      }
      form.servicios_ids = servicioIds;
    } else {
      form.servicios_ids = paquete.servicios?.map((s: any) => s.id) || [];
    }
  } catch (e) {
    // fallback
    form.servicios_ids = paquete.servicios?.map((s: any) => s.id) || [];
  }

  showModal.value = true;
};

const resetForm = () => {
  form.nombre = '';
  form.descripcion = '';
  form.tipo_evento_id = null;
  form.precio_base = 0;
  form.servicios_ids = [];
  servicioSearch.value = '';
};

const handleSubmit = async () => {
  try {
    submitting.value = true;

    console.debug('[Paquetes] handleSubmit start', { isEdit: isEdit.value, form: { ...form } });

    // Build items payload expected by backend: list of { opcion_servicio_id, cantidad }
    const itemsPayload: any[] = [];
    const unresolvedServicios: string[] = [];
    for (const sid of form.servicios_ids) {
      // Try to find opcion in cache
      let opciones = catalogStore.opcionesCache[String(sid)];
      if (!Array.isArray(opciones) || opciones.length === 0) {
        // fetch opciones for servicio
        try {
          opciones = await catalogStore.fetchOpcionesForServicio(String(sid));
        } catch (e) {
          opciones = [];
        }
      }
      const opcionId = (Array.isArray(opciones) && opciones.length > 0) ? opciones[0].id : null;
      if (opcionId) {
        itemsPayload.push({ opcion_servicio_id: String(opcionId), cantidad: 1 });
      } else {
        // Record unresolved servicio and do NOT send a fallback id
        unresolvedServicios.push(String(sid));
      }
    }

    // If any servicio couldn't resolve to an opcion, try to create one automatically
    if (unresolvedServicios.length > 0) {
      ui.showToast(`Creando opciones automáticas para ${unresolvedServicios.length} servicio(s)...`, 'info');
      
      for (const sid of unresolvedServicios) {
        const servicio = catalogStore.servicios.find((s: any) => String(s.id) === String(sid));
        if (!servicio) {
           console.warn(`[Paquetes] Service ${sid} not found in store, skipping auto-creation`);
           continue;
        }
        
        try {
           const newOptionPayload = {
              servicio_id: String(sid),
              nombre: `${servicio.nombre} - opción`,
              moneda: 'PEN',
              monto: Number(servicio.precio_unitario ?? 0),
              detalles: {},
           };
           
           // Create option
           const createdOpt = await catalogApi.createOpcion(newOptionPayload);
           
           // Add to items payload
           itemsPayload.push({ opcion_servicio_id: String(createdOpt.id), cantidad: 1 });
           
           // Refresh cache for future use (non-blocking)
           catalogStore.fetchOpcionesForServicio(String(sid), { force: true }).catch(() => {});
           
        } catch (err) {
           console.error(`[Paquetes] Failed to auto-create option for service ${sid}`, err);
           ui.showToast(`Error al crear opción automática para ${servicio.nombre}`, 'error');
           submitting.value = false;
           return;
        }
      }
    }

    const payload: any = {
      nombre: form.nombre,
      descripcion: form.descripcion,
      tipo_evento_id: form.tipo_evento_id,
      precio_base: form.precio_base,
      items: itemsPayload,
    };

    let result: any = null;
    if (isEdit.value && selectedPaquete.value) {
      result = await catalogStore.updatePaquete(selectedPaquete.value.id, payload);
      console.debug('[Paquetes] updatePaquete result', result);
    } else {
      result = await catalogStore.createPaquete(payload);
      console.debug('[Paquetes] createPaquete result', result);
    }

    // Close modal and refresh list
    showModal.value = false;
    resetForm();
    try {
      await catalogStore.fetchPaquetes({ forceRefresh: true });
    } catch (e) {
      console.warn('[Paquetes] fetchPaquetes after submit failed', e);
    }
    ui.showToast(isEdit.value ? 'Paquete actualizado' : 'Paquete creado', 'success');
  } catch (error: any) {
    ui.showToast('Error: ' + (error.response?.data?.detail || error.message), 'error');
  } finally {
    submitting.value = false;
  }
};

const confirmDelete = async (paquete: any) => {
  console.debug('[Paquetes] confirmDelete invoked', paquete);
  ui.showToast('Intentando eliminar: ' + paquete.nombre, 'info', 1500);
  const ok = await ui.showConfirmWithFallback(`¿Está seguro de eliminar el paquete "${paquete.nombre}"?`, 'Eliminar paquete');
  if (!ok) return;
  try {
    await catalogStore.deletePaquete(paquete.id);
    await catalogStore.fetchPaquetes({ forceRefresh: true });
    ui.showToast('Paquete eliminado', 'success');
  } catch (error: any) {
    ui.showToast('Error al eliminar: ' + (error.response?.data?.detail || error.message), 'error');
  }
};

// Hybrid pagination: fetch correct page from backend if server-side, else use client-side
const fetchPaquetesForPage = async () => {
  if (isServerSide.value) {
    await catalogStore.fetchPaquetes({
      page: Number(currentPage.value),
      pageSize: Number(pageSize.value),
      forceRefresh: true,
    });
  } else {
    await catalogStore.fetchPaquetes({ forceRefresh: true });
  }
};

onMounted(async () => {
  console.log('[Paquetes] onMounted - fetching data...');
  await catalogStore.fetchTiposEvento();
  await catalogStore.fetchServicios();
  await fetchPaquetesForPage();
  console.log('[Paquetes] onMounted - done');
});

// Watchers for page/size/filter changes
watch([currentPage, pageSize, isServerSide], async () => {
  await fetchPaquetesForPage();
});

// Keep currentPage valid when pageSize or totalPaquetes changes
watch(pageSize, () => { currentPage.value = 1; });
watch(totalPaquetes, () => {
  if (Number(currentPage.value) > Number(totalPages.value)) {
    currentPage.value = Number(totalPages.value);
  }
});
</script>
