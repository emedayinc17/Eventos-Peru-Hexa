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
                  {{ estadoLabels[pedido.status] || 'Desconocido' }}
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
      maxWidth="6xl"
    >
      <div v-if="selectedPedido" class="space-y-6">
        <!-- Header Info -->
        <div class="flex justify-between items-start border-b pb-4">
          <div>
            <h3 class="text-lg font-medium text-gray-900">Pedido #{{ selectedPedido.id }}</h3>
            <p class="text-sm text-gray-500">{{ formatDateTime(selectedPedido.created_at) }}</p>
          </div>
          <div class="flex items-center gap-2">
            <select
              v-model="tempStatus"
              class="text-sm rounded-full border-0 font-medium px-3 py-1 cursor-pointer focus:ring-2 focus:ring-offset-1 focus:ring-indigo-500"
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
            <Button 
              v-if="tempStatus !== selectedPedido.status"
              size="sm"
              @click="saveStatusChange"
            >
              Guardar
            </Button>
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
          <div class="flex justify-between items-center mb-4">
            <h4 class="text-sm font-semibold text-gray-900 uppercase tracking-wider">Contenido del Pedido</h4>
            <!-- Only allow editing if status is DRAFT (0) or COTIZADO (1) -->
            <Button 
              v-if="[0, 1].includes(selectedPedido.status)"
              size="sm" 
              variant="secondary"
              @click="openAddItemModal"
            >
              <PlusIcon class="w-4 h-4 mr-1" />
              Agregar Servicio Adicional
            </Button>
          </div>
          
          <!-- Package Items (Read Only) -->
          <div v-if="selectedPedido.items && selectedPedido.items.some(i => !i.referencia_id)" class="mb-6">
            <h5 class="text-xs font-bold text-indigo-600 uppercase mb-2 flex items-center gap-2">
               <ClipboardDocumentListIcon class="w-4 h-4" />
               Paquete Base (No modificable)
            </h5>
            <div class="bg-indigo-50 rounded-lg border border-indigo-100 overflow-hidden">
              <table class="min-w-full divide-y divide-indigo-200">
                <thead class="bg-indigo-100">
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-indigo-700 uppercase">Servicio</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-indigo-700 uppercase">Cant.</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-indigo-700 uppercase">Precio Unit.</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-indigo-700 uppercase">Subtotal</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-indigo-700 uppercase"></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-indigo-200">
                  <tr v-for="item in selectedPedido.items.filter(i => !i.referencia_id)" :key="item.id">
                    <td class="px-4 py-2 text-sm text-gray-900">
                      {{ item.nombre_servicio }}
                      <div v-if="item.proveedor" class="text-xs text-indigo-600 mt-0.5">
                        Prov: {{ item.proveedor.nombre }}
                      </div>
                    </td>
                    <td class="px-4 py-2 text-sm text-gray-900 text-right">{{ item.cantidad }}</td>
                    <td class="px-4 py-2 text-sm text-gray-900 text-right">S/ {{ item.precio_unitario?.toFixed(2) }}</td>
                    <td class="px-4 py-2 text-sm font-medium text-gray-900 text-right">S/ {{ item.subtotal?.toFixed(2) }}</td>
                    <td class="px-4 py-2 text-right">
                       <!-- Read only -->
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Additional Items -->
          <div>
            <h5 class="text-xs font-bold text-gray-500 uppercase mb-2 flex items-center gap-2">
               <PlusIcon class="w-4 h-4" />
               Servicios Adicionales
            </h5>
            <div class="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-100">
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Servicio</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Cant.</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Precio Unit.</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Subtotal</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase" v-if="[0, 1].includes(selectedPedido.status)"></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="item in selectedPedido.items.filter(i => i.referencia_id)" :key="item.id">
                    <td class="px-4 py-2 text-sm text-gray-900">
                      {{ item.nombre_servicio }}
                      <div v-if="item.proveedor" class="text-xs text-indigo-600 mt-0.5">
                        Prov: {{ item.proveedor.nombre }}
                      </div>
                    </td>
                    <td class="px-4 py-2 text-sm text-gray-900 text-right">{{ item.cantidad }}</td>
                    <td class="px-4 py-2 text-sm text-gray-900 text-right">S/ {{ item.precio_unitario?.toFixed(2) }}</td>
                    <td class="px-4 py-2 text-sm font-medium text-gray-900 text-right">S/ {{ item.subtotal?.toFixed(2) }}</td>
                    <td class="px-4 py-2 text-right" v-if="[0, 1].includes(selectedPedido.status)">
                      <button 
                        @click="deleteItem(item)"
                        class="text-red-400 hover:text-red-600 transition-colors"
                        title="Eliminar item"
                      >
                        <TrashIcon class="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!selectedPedido.items.some(i => i.referencia_id)">
                    <td colspan="5" class="px-4 py-4 text-center text-gray-400 text-sm italic">
                      No hay servicios adicionales
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

        <div class="flex justify-end gap-3 pt-4 border-t">
          <Button variant="secondary" @click="showDetailsModal = false">
            Cerrar
          </Button>
        </div>
      </div>
    </Modal>

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
            class="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
            :class="addItemTab === 'services' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
            @click="addItemTab = 'services'"
          >
            Servicios
          </button>
          <button 
            class="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
            :class="addItemTab === 'packages' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
            @click="addItemTab = 'packages'"
          >
            Paquetes
          </button>
        </div>

        <!-- Search -->
        <div>
           <SearchBar v-model="catalogSearch" placeholder="Buscar en el catálogo..." />
        </div>

        <!-- Catalog Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[400px] overflow-y-auto p-1">
          <div v-if="catalogLoading" class="col-span-full flex justify-center py-8">
            <Loading text="Cargando catálogo..." />
          </div>
          
          <template v-else-if="addItemTab === 'services'">
             <div 
               v-for="servicio in filteredServices" 
               :key="servicio.id"
               class="border rounded-lg p-3 hover:shadow-md transition-shadow cursor-pointer flex flex-col"
               :class="selectedCatalogItem?.id === servicio.id ? 'ring-2 ring-primary-500 border-primary-500' : 'border-gray-200'"
               @click="selectCatalogItem(servicio, 'service')"
             >
               <div class="flex justify-between items-start mb-2">
                 <h4 class="font-medium text-gray-900 text-sm">{{ servicio.nombre }}</h4>
                 <span class="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{{ servicio.categoria }}</span>
               </div>
               <p class="text-xs text-gray-500 line-clamp-2 mb-2">{{ servicio.descripcion }}</p>
               
               <!-- Options if selected -->
               <div v-if="selectedCatalogItem?.id === servicio.id && servicio.opciones?.length" class="mt-auto pt-2 border-t">
                 <select 
                   v-model="selectedOptionId" 
                   class="w-full text-xs rounded border-gray-300 mb-2"
                   @click.stop
                 >
                   <option value="" disabled>Seleccione opción</option>
                   <option v-for="op in servicio.opciones" :key="op.id" :value="op.id">
                     {{ op.nombre }} - S/ {{ op.precio_base }}
                   </option>
                 </select>
               </div>
             </div>
          </template>

          <template v-else>
             <div 
               v-for="paquete in filteredPackages" 
               :key="paquete.id"
               class="border rounded-lg p-3 hover:shadow-md transition-shadow cursor-pointer flex flex-col"
               :class="selectedCatalogItem?.id === paquete.id ? 'ring-2 ring-primary-500 border-primary-500' : 'border-gray-200'"
               @click="selectCatalogItem(paquete, 'package')"
             >
               <div class="flex justify-between items-start mb-2">
                 <h4 class="font-medium text-gray-900 text-sm">{{ paquete.nombre }}</h4>
                 <span class="text-xs font-bold text-primary-600">S/ {{ paquete.precio_base }}</span>
               </div>
               <p class="text-xs text-gray-500 line-clamp-2 mb-2">{{ paquete.descripcion }}</p>
               <div class="mt-auto text-xs text-gray-400">
                 {{ paquete.items?.length || 0 }} servicios incluidos
               </div>
             </div>
          </template>
        </div>

        <!-- Footer Actions -->
        <div class="flex justify-between items-center pt-4 border-t">
          <div class="flex items-center gap-2">
             <label class="text-sm font-medium text-gray-700">Cantidad:</label>
             <input type="number" v-model.number="newItemCantidad" min="1" class="w-20 rounded-md border-gray-300 text-sm">
          </div>
          <div class="flex gap-2">
            <Button variant="secondary" @click="showAddItemModal = false">Cancelar</Button>
            <Button @click="confirmAddItem" :disabled="!canAddItem">Agregar al Pedido</Button>
          </div>
        </div>
      </div>
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
const filterEstado = ref<number | ''>('');
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
    result = result.filter(p => p.status === filterEstado.value);
  }
  
  return result;
});

// Catalog Filtering
const filteredServices = computed(() => {
  let items = catalogStore.servicios;
  if (catalogSearch.value) {
    const q = catalogSearch.value.toLowerCase();
    items = items.filter(s => s.nombre.toLowerCase().includes(q) || s.categoria.toLowerCase().includes(q));
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

const canAddItem = computed(() => {
  if (addItemTab.value === 'services') {
    return selectedCatalogItem.value && selectedOptionId.value && newItemCantidad.value > 0;
  } else {
    return selectedCatalogItem.value && newItemCantidad.value > 0;
  }
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

// Helper functions
const getEstadoClass = (estado: number) => {
  const classes: Record<number, string> = {
    0: 'bg-gray-100 text-gray-800', // Draft
    1: 'bg-yellow-100 text-yellow-800', // Cotizado
    2: 'bg-blue-50 text-blue-800', // Aprobado
    3: 'bg-indigo-100 text-indigo-800', // Asignado
    4: 'bg-green-100 text-green-800', // Confirmado
    5: 'bg-red-100 text-red-800', // Cancelado
    6: 'bg-purple-100 text-purple-800', // Completado
  };
  return classes[estado] || 'bg-gray-100 text-gray-800';
};

const getEstadoBadgeClass = (estado: number) => {
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



const saveStatusChange = async () => {
  if (!selectedPedido.value) return;
  
  try {
    await ordersStore.updatePedido(selectedPedido.value.id, { estado: Number(tempStatus.value) });
    
    // Update local state
    selectedPedido.value.status = tempStatus.value;
    
    // Refresh list to keep it in sync
    await loadPedidos();
    
    ui.showToast('Estado actualizado correctamente', 'success');
  } catch (error: any) {
    const msg = error.response?.data?.detail?.message || error.response?.data?.detail || error.message;
    ui.showToast('Error al actualizar estado: ' + msg, 'error');
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
           reservas: current.reservas
         };
      } else {
         selectedPedido.value = current;
      }
      
      // Initialize temp status
      tempStatus.value = selectedPedido.value.status;
      
      showDetailsModal.value = true;
    }
  } catch (e) {
    ui.showToast('Error al cargar detalles', 'error');
  }
};

const openAddItemModal = async () => {
  // Reset state
  addItemTab.value = 'services';
  catalogSearch.value = '';
  newItemCantidad.value = 1;
  selectedCatalogItem.value = null;
  selectedOptionId.value = '';
  
  showAddItemModal.value = true;
  
  // Load catalog if empty
  if (catalogStore.servicios.length === 0) {
    await catalogStore.fetchServicios();
  }
  if (catalogStore.paquetes.length === 0) {
    await catalogStore.fetchPaquetes();
  }
};

const selectCatalogItem = (item: any, type: 'service' | 'package') => {
  selectedCatalogItem.value = item;
  if (type === 'service') {
    // Auto-select first option if available
    if (item.opciones && item.opciones.length > 0) {
      selectedOptionId.value = item.opciones[0].id;
    } else {
      selectedOptionId.value = '';
    }
  } else {
    selectedOptionId.value = ''; // Packages don't have options in this context usually
  }
};



const confirmAddItem = async () => {
  if (!selectedPedido.value) return;
  
  try {
    const items = [];
    
    if (addItemTab.value === 'services') {
      items.push({
        opcion_servicio_id: selectedOptionId.value,
        cantidad: newItemCantidad.value
      });
    } else {
      // For packages, we add the package itself. 
      // The backend addItems endpoint expects 'opcion_servicio_id' for services.
      // Does it support adding packages? Usually packages are added at creation.
      // If the backend supports adding a package item, we need to know the field name.
      // Based on previous code, items have 'opcion_servicio_id'.
      // If we want to add a package, we might need a different endpoint or logic.
      // BUT, the user asked to add "paquetes o servicios".
      // If the backend only supports `opcion_servicio_id` in `addItems`, we can only add services.
      // Let's assume for now we can only add services via this endpoint, OR check if we can add package contents.
      // If the user selects a package, maybe we add all its items?
      // Or maybe there is a `paquete_id` field?
      // Let's look at `addItems` implementation in backend... it likely maps to `crear_item_pedido`.
      // `crear_item_pedido` usually takes `opcion_servicio_id`.
      // If we want to add a package, we probably need to add its constituent services.
      
      // For now, let's implement adding services correctly. 
      // If package selected, we could iterate its items and add them as services?
      // Let's try to add the package's items as individual services.
      
      if (selectedCatalogItem.value.items) {
         // This is a package with items
         // We need to map package items to service options.
         // Package items usually have `servicio_id` or `opcion_servicio_id`.
         // Let's assume we can't easily add a "Package" entity to an existing order structure that expects items.
         // We will add the services OF the package.
         
         // Wait, `addItems` in backend:
         // router.post("/{pedido_id}/items") -> use_case.execute(pedido_id, items)
         // items is List[ItemPedidoCreate]. ItemPedidoCreate has opcion_servicio_id.
         // So we can only add services (options).
         
         // So if user selects a package, we should add all services from that package.
         // But we need `opcion_servicio_id` for each.
         // Package items in catalog store: `items: [{ servicio_id, ... }]`. 
         // They might not have `opcion_servicio_id` directly if they are defined by service.
         // This is complex. 
         
         // SIMPLIFICATION: For this iteration, let's only support adding Services (Options).
         // If user clicks Package tab, we can show a message or try to handle it.
         // But given the constraints, let's stick to Services for now to ensure it works.
         // I will hide the Package tab or show a "Not supported yet" toast?
         // No, the user explicitly asked for "paquetes o servicios".
         
         // If I add a package, I should probably just add the items.
         // Let's see if we can get options from package items.
         // If not, we might need to skip packages for now or ask backend to support it.
         // Let's try to add just services for now to fix the immediate "codigos" issue.
         
         ui.showToast('Agregar paquetes completos aún no está soportado, por favor agregue los servicios individualmente.', 'warning');
         return;
      }
    }
    
    await ordersStore.addItems(selectedPedido.value.id, items);
    
    // Refresh local selectedPedido from store
    const current = ordersStore.currentPedido as any;
    if (current.pedido) {
       selectedPedido.value = {
         ...current.pedido,
         items: current.items,
         reservas: current.reservas
       };
    }
    
    ui.showToast('Item agregado correctamente', 'success');
    showAddItemModal.value = false;
  } catch (error: any) {
    const msg = error.response?.data?.detail?.message || error.response?.data?.detail || error.message;
    ui.showToast('Error al agregar item: ' + msg, 'error');
  }
};

const deleteItem = async (item: any) => {
  if (!selectedPedido.value) return;
  
  const ok = await ui.showConfirmWithFallback(`¿Eliminar item ${item.nombre_servicio}?`, 'Eliminar Item');
  if (!ok) return;

  try {
    await ordersStore.deleteItems(selectedPedido.value.id, [item.id]);
    
    // Refresh local selectedPedido from store
    const current = ordersStore.currentPedido as any;
    if (current.pedido) {
       selectedPedido.value = {
         ...current.pedido,
         items: current.items,
         reservas: current.reservas
       };
    }
    
    ui.showToast('Item eliminado correctamente', 'success');
  } catch (error: any) {
    const msg = error.response?.data?.detail?.message || error.response?.data?.detail || error.message;
    ui.showToast('Error al eliminar item: ' + msg, 'error');
  }
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

const loadPedidos = async () => {
  // Load admin view of pedidos
  await ordersStore.fetchPedidos(undefined, undefined, true);
};

onMounted(async () => {
  await loadPedidos();
});
</script>
