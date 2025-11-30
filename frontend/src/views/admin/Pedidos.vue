<template>
  <div class="w-full h-full p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Gestión de Pedidos</h1>
        <p class="text-gray-600 text-sm mt-1">Supervisión y control de todas las solicitudes de eventos</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
      <div class="flex flex-wrap gap-4 items-center">
        <div class="flex-1 min-w-[200px] md:max-w-md">
          <SearchBar 
            v-model="searchQuery"
            placeholder="Buscar por ID, cliente o email..."
          />
        </div>
        <select
          v-model="filterEstado"
          class="rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
          <option value="">Todos los estados</option>
          <option value="PENDIENTE">Pendiente</option>
          <option value="CONFIRMADO">Confirmado</option>
          <option value="EN_PROGRESO">En Progreso</option>
          <option value="COMPLETADO">Completado</option>
          <option value="CANCELADO">Cancelado</option>
        </select>
        <Button variant="secondary" @click="loadPedidos" class="flex items-center gap-2">
          <ArrowPathIcon class="w-4 h-4" />
          Actualizar
        </Button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Cliente</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Evento</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Fecha</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Total</th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="ordersStore.loading">
              <td colspan="7" class="px-6 py-12 text-center">
                <Loading text="Cargando pedidos..." />
              </td>
            </tr>
            <tr v-else-if="filteredPedidos.length === 0">
              <td colspan="7" class="px-6 py-12 text-center text-gray-500">
                <div class="flex flex-col items-center justify-center">
                  <ClipboardDocumentListIcon class="w-12 h-12 text-gray-300 mb-2" />
                  <p>No se encontraron pedidos</p>
                </div>
              </td>
            </tr>
            <tr v-else v-for="pedido in paginatedPedidos" :key="pedido.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                #{{ pedido.id.substring(0, 8) }}...
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ pedido.cliente_nombre || `Usuario #${pedido.cliente_id}` }}</div>
                <div class="text-xs text-gray-500" v-if="pedido.cliente_email">{{ pedido.cliente_email }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ pedido.tipo_evento_nombre }}
                <span class="text-xs text-gray-400 block">{{ pedido.num_personas }} invitados</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(pedido.fecha_evento) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-3 py-1 rounded-full text-xs font-medium"
                  :class="getEstadoBadgeClass(pedido.status)"
                >
                  {{ getEstadoLabel(pedido.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                S/ {{ pedido.monto_total?.toFixed(2) || '0.00' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end gap-2">
                  <button
                    @click="viewDetails(pedido)"
                    class="text-primary-600 hover:text-primary-900 font-medium text-sm flex items-center gap-1"
                  >
                    Gestionar
                    <PencilIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- Pagination -->
    <div class="bg-gray-50 px-6 py-3 border-t border-gray-200 flex items-center justify-between mt-3">
      <div class="text-sm text-gray-500">
        Mostrando {{ (currentPage - 1) * pageSize + 1 }} a {{ Math.min(currentPage * pageSize, filteredPedidos.length) }} de {{ filteredPedidos.length }} pedidos
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
    <!-- Details Modal -->
    <Modal 
      :open="showDetailsModal" 
      @close="showDetailsModal = false"
      title="Gestión de Pedido" 
      maxWidth="7xl"
    >
      <div v-if="selectedPedido" class="space-y-6">
        <div class="flex justify-between items-start border-b pb-4">
          <div>
            <h3 class="text-lg font-medium text-gray-900">Pedido #{{ selectedPedido.id }}</h3>
            <p class="text-sm text-gray-500">{{ formatDateTime(selectedPedido.created_at) }}</p>
          </div>
          <div class="flex items-center gap-2">
             <!-- Status Selector moved here but Save button removed (moved to bottom) -->
             <div class="flex flex-col items-end">
                <label class="text-xs text-gray-500 mb-1">Estado del Pedido</label>
                <select
                  v-model="tempStatus"
                  class="text-sm rounded-md border-gray-300 font-medium px-3 py-1 cursor-pointer focus:ring-2 focus:ring-offset-1 focus:ring-indigo-500"
                  :class="getEstadoBadgeClass(tempStatus)"
                >
                  <option :value="0">Borrador</option>
                  <option :value="1">Cotizado</option>
                  <option :value="2">Aprobado</option>
                  <option :value="3">Asignado</option>
                  <option :value="4">Confirmado</option>
                  <option :value="5">Cancelado</option>
                  <option :value="6">Completado</option>
                </select>
             </div>
          </div>
        </div>

        <!-- Grid Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <div>
              <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Cliente</h4>
              <p class="font-medium text-gray-900">{{ selectedPedido.cliente_nombre || `Usuario #${selectedPedido.cliente_id}` }}</p>
              <p class="text-sm text-gray-500">{{ selectedPedido.cliente_email || '-' }}</p>
            </div>
            <div>
              <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Evento</h4>
              <p class="font-medium text-gray-900">{{ selectedPedido.tipo_evento_nombre }}</p>
              <p class="text-sm text-gray-500">{{ selectedPedido.num_personas }} invitados</p>
            </div>
          </div>
          
          <div class="space-y-4">
            <div>
              <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Fecha Programada</h4>
              <p class="font-medium text-gray-900">{{ formatDate(selectedPedido.fecha_evento) }}</p>
            </div>
            <div>
              <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Total Estimado</h4>
              <p class="text-xl font-bold text-primary-600">S/ {{ selectedPedido.monto_total?.toFixed(2) }}</p>
            </div>

          </div>
        </div>

        <!-- Items List -->
        <div class="border-t pt-4">
          <div class="flex justify-between items-center mb-6">
            <h4 class="text-lg font-bold text-gray-900">Contenido del Pedido</h4>
          </div>
          
          <!-- Package Info (Read Only List) -->
          <div v-if="selectedPedido.paquete_nombre" class="bg-indigo-50 p-4 rounded-lg border border-indigo-100 mb-6">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2">
                <ClipboardDocumentListIcon class="w-5 h-5 text-indigo-600" />
                <h3 class="font-bold text-indigo-900">
                  Paquete Base: {{ selectedPedido.paquete_nombre }}
                </h3>
              </div>
              <span class="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded border border-indigo-200">
                No modificable
              </span>
            </div>
            
            <p class="text-xs text-indigo-700 mb-3">
              Los siguientes items están incluidos en el paquete base y no pueden ser modificados individualmente:
            </p>
            
            <ul class="grid grid-cols-1 md:grid-cols-2 gap-y-2 gap-x-4">
              <!-- Show items from catalog definition if available (preferred for clean display) -->
              <template v-if="selectedPedido.paquete_items && selectedPedido.paquete_items.length > 0">
                <li 
                  v-for="item in selectedPedido.paquete_items" 
                  :key="item.opcion_servicio_id" 
                  class="text-sm text-indigo-900 flex items-start gap-2"
                >
                  <span class="mt-1.5 w-1.5 h-1.5 rounded-full bg-indigo-500 flex-shrink-0"></span>
                  <span>
                    {{ item.servicio_nombre || item.nombre_servicio || item.nombre }}
                    <span class="text-indigo-500 text-xs font-medium ml-1">x{{ item.cantidad }}</span>
                  </span>
                </li>
              </template>
              <!-- Fallback to order items marked as PAQUETE -->
              <template v-else>
                <li 
                  v-for="item in selectedPedido.items.filter(i => i.tipo_item === 'PAQUETE' || i.tipo_item === 2)" 
                  :key="item.id" 
                  class="text-sm text-indigo-900 flex items-start gap-2"
                >
                  <span class="mt-1.5 w-1.5 h-1.5 rounded-full bg-indigo-500 flex-shrink-0"></span>
                  <span>
                    {{ item.nombre_servicio }}
                    <span class="text-indigo-500 text-xs font-medium ml-1">x{{ item.cantidad }}</span>
                  </span>
                </li>
              </template>
            </ul>
          </div>

          <!-- Additional Items -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2">
                <div class="p-2 bg-gray-100 rounded-lg">
                  <PlusIcon class="w-5 h-5 text-gray-600" />
                </div>
                <div>
                  <h5 class="text-sm font-bold text-gray-900 uppercase tracking-wide">
                    Servicios Adicionales
                  </h5>
                  <p class="text-xs text-gray-500">
                    Agregados extra al paquete
                  </p>
                </div>
              </div>
              <Button 
                v-if="[0, 1].includes(selectedPedido.status)"
                size="sm" 
                @click="openAddItemModal"
                class="shadow-sm"
              >
                <PlusIcon class="w-4 h-4 mr-1" />
                Agregar Servicio
              </Button>
            </div>

            <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Servicio</th>
                    <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Cant.</th>
                    <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Precio Unit.</th>
                    <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Subtotal</th>
                    <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider" v-if="[0, 1].includes(selectedPedido.status)">Acciones</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="item in filteredAdditionalItems" :key="item.id" class="hover:bg-gray-50 transition-colors">
                    <td class="px-4 py-3 text-sm text-gray-900">
                      <div class="font-medium flex items-center gap-2">
                        {{ item.nombre_servicio }}
                        <span v-if="item.is_new" class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-700 uppercase tracking-wide">Nuevo</span>
                      </div>
                      <div v-if="item.proveedor" class="text-xs text-indigo-600 mt-0.5 flex items-center gap-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                        Prov: {{ item.proveedor.nombre }}
                      </div>
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-900 text-right font-medium">{{ item.cantidad }}</td>
                    <td class="px-4 py-3 text-sm text-gray-500 text-right">S/ {{ item.precio_unitario?.toFixed(2) }}</td>
                    <td class="px-4 py-3 text-sm font-bold text-gray-900 text-right">S/ {{ item.subtotal?.toFixed(2) }}</td>
                    <td class="px-4 py-3 text-right" v-if="[0, 1].includes(selectedPedido.status)">
                      <button 
                        @click="deleteItem(item)"
                        class="p-1 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-all"
                        title="Eliminar item"
                      >
                        <TrashIcon class="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                  <tr v-if="filteredAdditionalItems.length === 0">
                    <td colspan="5" class="px-4 py-8 text-center text-gray-400 text-sm">
                      <div class="flex flex-col items-center justify-center gap-2">
                        <div class="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center">
                          <PlusIcon class="w-5 h-5 text-gray-300" />
                        </div>
                        <p>No hay servicios adicionales</p>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-if="selectedPedido.comentarios" class="bg-gray-50 p-4 rounded-lg border border-gray-100">
          <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Comentarios Especiales</h4>
          <p class="text-gray-700 italic text-sm">"{{ selectedPedido.comentarios }}"</p>
        </div>

        <div class="flex justify-end gap-3 pt-6 border-t mt-6">
          <Button variant="secondary" @click="showDetailsModal = false">
            Cancelar
          </Button>
          <Button @click="saveOrderChanges">
            Guardar Cambios
          </Button>
        </div>
      </div>
    <!-- Add Item Modal with Catalog Selection -->
    <Modal
      v-if="showAddItemModal"
      :open="showAddItemModal"
      @close="showAddItemModal = false"
      title="Agregar Item al Pedido"
      maxWidth="4xl"
    >
      <div class="space-y-6 min-h-[400px]">
        <!-- Tabs for Service vs Package -->
        <div class="flex border-b border-gray-200">
          <button 
            class="px-4 py-2 text-sm font-medium border-b-2 transition-colors border-primary-500 text-primary-600"
          >
            Servicios
          </button>
          <!-- Packages tab hidden until backend support is implemented -->
        </div>

        <!-- Search -->
        <div>
           <SearchBar v-model="catalogSearch" placeholder="Buscar en el catálogo..." />
        </div>

        <!-- Catalog Table -->
        <div class="border rounded-lg overflow-hidden flex-1 min-h-[300px]">
          <div class="overflow-y-auto max-h-[400px]">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50 sticky top-0">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-10">
                    <!-- Checkbox header could go here for select all -->
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Servicio</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoría</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Opción</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Precio</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-if="catalogLoading">
                  <td colspan="5" class="px-4 py-8 text-center"><Loading /></td>
                </tr>
                <template v-else v-for="servicio in filteredServices" :key="servicio.id">
                  <!-- Render a row for each option of the service -->
                  <tr 
                    v-for="opcion in servicio.opciones" 
                    :key="opcion.id"
                    class="hover:bg-gray-50 cursor-pointer transition-colors"
                    @click.stop="toggleCatalogItem(servicio, opcion.id)"
                  >
                    <td class="px-4 py-3">
                      <input 
                        type="checkbox" 
                        class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                        :checked="selectedCatalogItems.has(`${servicio.id}|${opcion.id}`)"
                        readonly
                      >
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-900 font-medium">{{ servicio.nombre }}</td>
                    <td class="px-4 py-3 text-sm text-gray-500">
                      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                        {{ servicio.categoria }}
                      </span>
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-600">{{ opcion.nombre }}</td>
                    <td class="px-4 py-3 text-sm text-gray-900 text-right font-medium">S/ {{ opcion.monto }}</td>
                  </tr>
                </template>
                <tr v-if="!catalogLoading && filteredServices.length === 0">
                  <td colspan="5" class="px-4 py-8 text-center text-gray-500">No se encontraron servicios</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="flex justify-between items-center pt-4 border-t">
          <div class="text-sm text-gray-600">
            {{ selectedCatalogItems.size }} item(s) seleccionado(s)
          </div>
          <div class="flex gap-2">
            <Button variant="secondary" @click="showAddItemModal = false">Cancelar</Button>
            <Button @click="confirmAddItem" :disabled="selectedCatalogItems.size === 0">
              Agregar Seleccionados
            </Button>
          </div>
        </div>
      </div>
    </Modal>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useCatalogStore } from '@/stores/catalog';
import { useOrdersStore } from '@/stores/orders';
import { useUiStore } from '@/stores/ui';
import Button from '@/components/common/Button.vue';
import SearchBar from '@/components/common/SearchBar.vue';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { EyeIcon, XCircleIcon, ArrowPathIcon, ClipboardDocumentListIcon, TrashIcon, PlusIcon, PencilIcon } from '@heroicons/vue/24/outline';

const ordersStore = useOrdersStore();
const catalogStore = useCatalogStore();
const ui = useUiStore();

const searchQuery = ref('');
const filterEstado = ref<number | string | ''>('');
const showDetailsModal = ref(false);
const selectedPedido = ref<any>(null);

// Add Item Modal State
const showAddItemModal = ref(false);
const addItemTab = ref<'services' | 'packages'>('services');
const catalogSearch = ref('');
const newItemCantidad = ref(1);
const selectedCatalogItem = ref<any>(null);
const selectedOptionId = ref<string>('');
const tempStatus = ref<number>(0);
const itemsToDelete = ref<string[]>([]);
const itemsToAdd = ref<any[]>([]); // Stores local items to be added { opcion_servicio_id, cantidad, ...displayProps }
const selectedCatalogItems = ref<Set<string>>(new Set()); // For multi-select in modal


const catalogLoading = computed(() => catalogStore.loading);

// Pagination
const currentPage = ref(1);
const pageSize = ref(10);

// Filtered pedidos
const filteredPedidos = computed(() => {
  let result = ordersStore.pedidos;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(p => 
      p.id.toString().includes(query) ||
      p.cliente_nombre?.toLowerCase().includes(query) ||
      p.cliente_email?.toLowerCase().includes(query)
    );
  }
  
  if (filterEstado.value !== '') {
    // Compare as strings to tolerate numeric or string status coming from backend
    result = result.filter(p => String(p.status) === String(filterEstado.value));
  }
  
  return result;
});

// Catalog Filtering
const filteredServices = computed(() => {
  // Map services to include options from cache
  let items = catalogStore.servicios.map(s => ({
    ...s,
    opciones: catalogStore.opcionesCache[String(s.id)] || []
  }));

  // Filter by event type (same category as the order)
  if (selectedPedido.value && selectedPedido.value.tipo_evento_id) {
    const typeId = String(selectedPedido.value.tipo_evento_id);
    items = items.filter(s => !s.tipo_evento_id || String(s.tipo_evento_id) === typeId);
  }

  if (catalogSearch.value) {
    const q = catalogSearch.value.toLowerCase();
    items = items.filter(s => s.nombre.toLowerCase().includes(q) || s.categoria?.toLowerCase().includes(q));
  }
  return items;
});

const filteredPackages = computed(() => {
  let items = catalogStore.paquetes;
  if (catalogSearch.value) {
    const q = catalogSearch.value.toLowerCase();
    items = items.filter(p => p.nombre.toLowerCase().includes(q));
  }
  return items;
});

// Paginated pedidos (client-side pagination)
const paginatedPedidos = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredPedidos.value.slice(start, end);
});

const totalPages = computed(() => Math.ceil(filteredPedidos.value.length / pageSize.value));

// Reset page when filters/search change
watch([searchQuery, filterEstado], () => {
  currentPage.value = 1;
});

const estadoLabels: Record<number, string> = {
  0: 'Borrador',
  1: 'Cotizado',
  2: 'Aprobado',
  3: 'Asignado',
  4: 'Confirmado',
  5: 'Cancelado',
  6: 'Completado'
};

// Support for string status values that some backends may return
const estadoStringLabels: Record<string, string> = {
  PENDIENTE: 'Pendiente',
  CONFIRMADO: 'Confirmado',
  EN_PROGRESO: 'En Progreso',
  COMPLETADO: 'Completado',
  CANCELADO: 'Cancelado'
};

const getEstadoLabel = (estado: number | string | undefined) => {
  if (estado === undefined || estado === null) return 'Desconocido';
  if (typeof estado === 'number') {
    return estadoLabels[estado] ?? 'Desconocido';
  }
  // try numeric-looking string
  const asNum = Number(estado);
  if (!Number.isNaN(asNum) && estadoLabels[asNum]) return estadoLabels[asNum];
  // otherwise use mapping for known string keys
  const up = String(estado).toUpperCase();
  return estadoStringLabels[up] ?? humanizeStatusString(up);
};

const humanizeStatusString = (s: string) => {
  // Convert 'EN_PROGRESO' -> 'En Progreso', 'PENDING' -> 'Pending' fallback
  const parts = s.replace(/_/g, ' ').toLowerCase().split(' ');
  return parts.map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(' ');
};

// Helper functions
const getEstadoClass = (estado: number | string | undefined) => {
  // numeric mapping
  const numClasses: Record<number, string> = {
    0: 'bg-gray-100 text-gray-800', // Draft
    1: 'bg-yellow-100 text-yellow-800', // Cotizado
    2: 'bg-blue-50 text-blue-800', // Aprobado
    3: 'bg-indigo-100 text-indigo-800', // Asignado
    4: 'bg-green-100 text-green-800', // Confirmado
    5: 'bg-red-100 text-red-800', // Cancelado
    6: 'bg-purple-100 text-purple-800', // Completado
  };

  if (estado === undefined || estado === null) return 'bg-gray-100 text-gray-800';
  if (typeof estado === 'number') return numClasses[estado] ?? 'bg-gray-100 text-gray-800';

  // string statuses mapping
  const up = String(estado).toUpperCase();
  const strMap: Record<string, string> = {
    PENDIENTE: 'bg-yellow-100 text-yellow-800',
    CONFIRMADO: 'bg-green-100 text-green-800',
    EN_PROGRESO: 'bg-indigo-100 text-indigo-800',
    COMPLETADO: 'bg-purple-100 text-purple-800',
    CANCELADO: 'bg-red-100 text-red-800'
  };
  // numeric-like string
  const asNum = Number(up);
  if (!Number.isNaN(asNum) && numClasses[asNum]) return numClasses[asNum];
  return strMap[up] ?? 'bg-gray-100 text-gray-800';
};

const getEstadoBadgeClass = (estado: number | string | undefined) => {
  return getEstadoClass(estado);
};

const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return '';
  try {
    return format(new Date(dateStr), 'd MMM yyyy', { locale: es });
  } catch {
    return dateStr;
  }
};

const formatDateTime = (dateStr: string | undefined) => {
  if (!dateStr) return '';
  try {
    return format(new Date(dateStr), "d 'de' MMMM 'de' yyyy, HH:mm", { locale: es });
  } catch {
    return dateStr;
  }
};



const loadPedidos = async () => {
  // Load admin view of pedidos
  await ordersStore.fetchPedidos(undefined, undefined, true);
};

const saveOrderChanges = async () => {
  if (!selectedPedido.value) return;
  
  try {
    // Process deferred deletions first
    if (itemsToDelete.value.length > 0) {
      await ordersStore.deleteItems(selectedPedido.value.id, itemsToDelete.value);
      itemsToDelete.value = []; // Reset
    }

    // Process deferred additions
    if (itemsToAdd.value.length > 0) {
      const payload = itemsToAdd.value.map(i => ({
        opcion_servicio_id: i.opcion_servicio_id,
        cantidad: i.cantidad
      }));
      await ordersStore.addItems(selectedPedido.value.id, payload);
      itemsToAdd.value = []; // Reset
    }

    // Only update status if changed
    if (tempStatus.value !== selectedPedido.value.status) {
      await ordersStore.updatePedido(selectedPedido.value.id, { estado: Number(tempStatus.value) });
      
      // Update local state
      selectedPedido.value.status = tempStatus.value;
      
      // Refresh list to keep it in sync
      await loadPedidos();
      
      ui.showToast('Pedido actualizado correctamente', 'success');
    } else if (itemsToDelete.value.length === 0 && itemsToAdd.value.length === 0) {
      ui.showToast('No hubo cambios para guardar', 'info');
    } else {
       // Just refreshed due to deletions/additions
       await loadPedidos();
       ui.showToast('Cambios guardados correctamente', 'success');
    }
    
    showDetailsModal.value = false;
  } catch (error: any) {
    const msg = error.response?.data?.detail?.message || error.response?.data?.detail || error.message;
    ui.showToast('Error al actualizar pedido: ' + msg, 'error');
  }
};

const viewDetails = async (pedido: any) => {
  // Fetch full details including items
  try {
    await ordersStore.fetchPedido(pedido.id, true);
    if (ordersStore.currentPedido) {
      const current = ordersStore.currentPedido as any;
      if (current.pedido) {
         selectedPedido.value = {
           ...current.pedido,
           items: current.items,
           reservas: current.reservas,
           paquete_items: current.paquete_items || []
         };
      } else {
         selectedPedido.value = current;
      }
      
      // Initialize temp status
      tempStatus.value = selectedPedido.value.status;
      itemsToDelete.value = []; // Reset deleted items tracking
      itemsToAdd.value = []; // Reset added items tracking
      
      showDetailsModal.value = true;
    }
  } catch (e) {
    ui.showToast('Error al cargar detalles', 'error');
  }
};

const filteredAdditionalItems = computed(() => {
  if (!selectedPedido.value || !selectedPedido.value.items) return [];
  
  const pkgItems = selectedPedido.value.paquete_items || [];
  const pkgOptionIds = new Set(pkgItems.map((pi: any) => pi.opcion_servicio_id));
  
  const existing = selectedPedido.value.items.filter((i: any) => {
    // Exclude if explicitly marked as PAQUETE
    if (i.tipo_item === 'PAQUETE' || i.tipo_item === 2) return false;
    
    // Exclude if it matches an item in the package definition (for cases where data is inconsistent)
    if (pkgOptionIds.has(i.opcion_servicio_id)) return false;
    
    // Exclude items marked for deletion
    if (itemsToDelete.value.includes(i.id)) return false;

    return true;
  });

  // Append locally added items (enriched for display)
  return [...existing, ...itemsToAdd.value];
});

const openAddItemModal = async () => {
  // Reset state
  addItemTab.value = 'services';
  catalogSearch.value = '';
  selectedCatalogItems.value = new Set();
  
  showAddItemModal.value = true;
  
  // Load catalog if empty
  if (catalogStore.servicios.length === 0) {
    await catalogStore.fetchServicios();
  }
  if (catalogStore.paquetes.length === 0) {
    await catalogStore.fetchPaquetes();
  }

  // Prefetch options for all services to ensure they appear in the table
  const ids = catalogStore.servicios.map(s => s.id);
  // Use concurrency to avoid overwhelming the backend, but ensure data loads
  catalogStore.prefetchOpcionesWithConcurrency(ids);
};

const toggleCatalogItem = (servicio: any, opcionId: string) => {
  const key = `${servicio.id}|${opcionId}`;
  if (selectedCatalogItems.value.has(key)) {
    selectedCatalogItems.value.delete(key);
  } else {
    selectedCatalogItems.value.add(key);
  }
};

const confirmAddItem = async () => {
  if (!selectedPedido.value) return;
  
  const newItems: any[] = [];
  
  // Iterate over selected keys "serviceId|optionId"
  for (const key of selectedCatalogItems.value) {
    const [svcId, optId] = key.split('|');
    const service = catalogStore.servicios.find(s => String(s.id) === svcId);
    if (service) {
      const options = catalogStore.opcionesCache[String(service.id)] || [];
      const option = options.find(o => String(o.id) === optId);
      if (option) {
        newItems.push({
          id: `temp-${Date.now()}-${Math.random()}`, // Temp ID
          opcion_servicio_id: option.id,
          nombre_servicio: `${service.nombre} - ${option.nombre}`,
          cantidad: 1, // Default to 1, editable in grid later if needed
          precio_unitario: option.monto,
          subtotal: option.monto * 1,
          tipo_item: 'SERVICIO',
          is_new: true // Flag for UI styling
        });
      }
    }
  }

  if (newItems.length === 0) {
    ui.showToast('Seleccione al menos un item', 'warning');
    return;
  }

  // Add to local state
  itemsToAdd.value.push(...newItems);
  
  // Update local total
  if (selectedPedido.value.monto_total !== undefined) {
    const addedTotal = newItems.reduce((sum, item) => sum + item.subtotal, 0);
    selectedPedido.value.monto_total += addedTotal;
  }

  ui.showToast(`${newItems.length} item(s) agregado(s) temporalmente`, 'info');
  showAddItemModal.value = false;
};

const deleteItem = async (item: any) => {
  if (!selectedPedido.value) return;
  
  // Soft delete: just mark for deletion and remove from UI
  if (item.is_new) {
     // If it's a new local item, just remove it from itemsToAdd
     itemsToAdd.value = itemsToAdd.value.filter(i => i.id !== item.id);
  } else {
     itemsToDelete.value.push(item.id);
  }
  
  // Recalculate total locally for better UX (optional, but nice)
  if (selectedPedido.value.monto_total && item.subtotal) {
      selectedPedido.value.monto_total -= item.subtotal;
  }
  
  ui.showToast('Item marcado para eliminar. Guarde los cambios para confirmar.', 'info');
};

const confirmDelete = async (pedido: any) => {
  console.debug('[Pedidos] confirmDelete invoked', pedido);
  ui.showToast('Intentando cancelar pedido: ' + pedido.id, 'info', 1500);
  // Backend does not support DELETE for pedidos; use estado=CANCELADO (5)
  const ok = await ui.showConfirmWithFallback(`¿Está seguro de cancelar el pedido #${pedido.id}?`, 'Cancelar pedido');
  if (ok) {
    try {
      await ordersStore.updatePedido(pedido.id, { estado: 5 });
      await loadPedidos();
      ui.showToast('Pedido cancelado correctamente', 'success');
    } catch (error: any) {
      const msg = error.response?.data?.detail?.message || error.response?.data?.detail || error.message;
      ui.showToast('Error al cancelar: ' + msg, 'error');
    }
  }
};

onMounted(async () => {
  await loadPedidos();
});
</script>
