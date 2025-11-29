<template>
  <div class="max-w-7xl mx-auto py-8 px-4">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Mis Pedidos</h1>
        <p class="text-gray-600 mt-1">Historial y estado de tus pedidos</p>
      </div>
      <Button variant="primary" @click="router.push('/cliente/pedido/nuevo')">
        + Crear Nuevo Pedido
      </Button>
    </div>

    <!-- Filters -->
    <Card class="mb-6">
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Filtrar por Estado
          </label>
          <select
            v-model="filterEstado"
            class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          >
            <option value="">Todos</option>
            <option value="PENDIENTE">Pendiente</option>
            <option value="CONFIRMADO">Confirmado</option>
            <option value="EN_PROGRESO">En Progreso</option>
            <option value="COMPLETADO">Completado</option>
            <option value="CANCELADO">Cancelado</option>
          </select>
        </div>
        <div class="flex items-end">
          <Button variant="secondary" @click="loadPedidos">
            🔄 Actualizar
          </Button>
        </div>
      </div>
    </Card>

    <!-- Loading State -->
    <div v-if="ordersStore.loading" class="flex justify-center py-12">
      <Loading size="lg" text="Cargando pedidos..." />
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredPedidos.length === 0" class="text-center py-12">
      <div class="mx-auto h-24 w-24 text-gray-400 mb-4">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No tienes pedidos</h3>
      <p class="text-gray-500 mb-6">Comienza creando tu primer pedido</p>
      <Button variant="primary" @click="router.push('/cliente/pedido/nuevo')">
        Crear Pedido
      </Button>
    </div>

    <!-- Pedidos List -->
    <div v-else class="space-y-4">
      <Card 
        v-for="pedido in filteredPedidos" 
        :key="pedido.id"
        class="hover:shadow-lg transition-shadow"
      >
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <!-- Left: Info -->
          <div class="flex-1">
            <div class="flex items-start justify-between mb-2">
              <div>
                <h3 class="text-lg font-semibold text-gray-900">
                  {{ getEventIcon(getTipoEventoNombre(pedido)) }} {{ getTipoEventoNombre(pedido) }}
                </h3>
                <p class="text-sm text-gray-500">Pedido #{{ pedido.id }}</p>
                <p v-if="getPaqueteName(pedido)" class="text-sm text-gray-500">Paquete: {{ getPaqueteName(pedido) }}</p>
              </div>
              <span 
                class="px-3 py-1 rounded-full text-sm font-medium"
                :class="getEstadoBadgeClass(getPedidoEstadoNombre(pedido))"
              >
                {{ getPedidoEstadoNombre(pedido) }}
              </span>
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div>
                <span class="text-gray-500">Fecha Evento:</span>
                <p class="font-medium">{{ formatDate(pedido.fecha_evento) }}</p>
              </div>
              <div>
                <span class="text-gray-500">Invitados:</span>
                <p class="font-medium">{{ (pedido.num_invitados ?? pedido.num_personas ?? pedido.num_personas) }} personas</p>
              </div>
              <div>
                <span class="text-gray-500">Total:</span>
                <p class="font-bold text-primary-600">S/ {{ (pedido.total ?? pedido.monto_total ?? pedido.monto ?? 0).toFixed ? (pedido.total ?? pedido.monto_total ?? pedido.monto ?? 0).toFixed(2) : String(pedido.total ?? pedido.monto_total ?? pedido.monto ?? '0.00') }}</p>
              </div>
              <div>
                <span class="text-gray-500">Creado:</span>
                <p class="font-medium">{{ formatDate(pedido.created_at) }}</p>
              </div>
            </div>
          </div>

          <!-- Right: Actions -->
          <div class="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" @click="viewDetails(pedido)">
              Ver Detalles
            </Button>
            <Button 
              v-if="pedido.estado === 'PENDIENTE'" 
              variant="danger" 
              size="sm"
              @click="confirmCancel(pedido)"
            >
              Cancelar
            </Button>
          </div>
        </div>
      </Card>
    </div>

    <!-- Details Modal -->
    <Modal v-model:open="showDetailsModal" title="Detalles del Pedido" max-width="2xl">
      <div v-if="selectedPedido" class="space-y-4">
        <div class="grid grid-cols-2 gap-4 pb-4 border-b">
          <div>
            <p class="text-sm text-gray-500">Pedido #</p>
            <p class="font-medium">{{ selectedPedido.id }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Estado</p>
            <span 
              class="inline-block px-3 py-1 rounded-full text-sm font-medium"
              :class="getEstadoBadgeClass(selectedPedido.estado)"
            >
              {{ selectedPedido.estado }}
            </span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Tipo de Evento</p>
            <p class="font-medium">{{ selectedPedido.tipo_evento_nombre }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Fecha del Evento</p>
            <p class="font-medium">{{ formatDate(selectedPedido.fecha_evento) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Número de Invitados</p>
            <p class="font-medium">{{ selectedPedido.num_invitados }} personas</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Total</p>
            <p class="font-bold text-primary-600 text-lg">S/ {{ selectedPedido.total?.toFixed(2) }}</p>
          </div>
        </div>

        <div v-if="selectedPedido.comentarios" class="pb-4 border-b">
          <p class="text-sm text-gray-500 mb-1">Comentarios Especiales</p>
          <p class="text-gray-700 italic">"{{ selectedPedido.comentarios }}"</p>
        </div>

        <div class="pb-4 border-b">
          <p class="text-sm text-gray-500 mb-2">Creado el</p>
          <p class="font-medium">{{ formatDateTime(selectedPedido.created_at) }}</p>
        </div>

        <!-- Paquete e Items -->
        <div class="pt-4 border-t">
          <h4 class="text-md font-semibold mb-2">Resumen de Items</h4>

          <div v-if="selectedPedido.paquete_nombre" class="mb-3">
            <p class="text-sm text-gray-500">Paquete</p>
            <p class="font-medium">{{ selectedPedido.paquete_nombre }}</p>
          </div>

          <div v-if="selectedPedido.items && selectedPedido.items.length > 0" class="space-y-3">
            <div v-for="item in selectedPedido.items" :key="item.id" class="p-3 border rounded">
              <div class="flex justify-between items-start">
                <div>
                  <div class="font-medium">{{ item.nombre_servicio || item.nombre || item.nombre_servicio }}</div>
                  <div class="text-sm text-gray-500">Cantidad: {{ item.cantidad || item.cantidad }}</div>
                </div>
                <div class="text-right">
                  <div class="font-semibold">S/ {{ (item.subtotal || (item.precio_unitario * (item.cantidad || 1)) || 0).toFixed(2) }}</div>
                </div>
              </div>

              <div class="mt-2 text-sm text-gray-600">
                <div v-if="item.proveedor">
                  <p class="font-medium">Proveedor asignado: {{ item.proveedor.nombre || item.proveedor.razon_social || item.proveedor.business_name }}</p>
                  <p>Contacto: {{ item.proveedor.email || item.proveedor.telefono || '-' }}</p>
                </div>
                <div v-else>
                  <p class="text-sm text-gray-500">Proveedor: <span class="font-medium">Sin proveedor asignado</span></p>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-sm text-gray-500">No hay items registrados para este pedido.</div>
        </div>

        <div class="flex justify-end gap-3 pt-4">
          <Button variant="secondary" @click="showDetailsModal = false">
            Cerrar
          </Button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useOrdersStore } from '@/stores/orders';
import { useAuthStore } from '@/stores/auth';
import { useUiStore } from '@/stores/ui';
import { useProvidersStore } from '@/stores/providers';
import { providersApi } from '@/api';
import { useCatalogStore } from '@/stores/catalog';
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const router = useRouter();
const ordersStore = useOrdersStore();
const authStore = useAuthStore();
const ui = useUiStore();

const filterEstado = ref('');
const showDetailsModal = ref(false);
const selectedPedido = ref<any>(null);
const providersStore = useProvidersStore();
const catalogStore = useCatalogStore();

// Filtered pedidos
const filteredPedidos = computed(() => {
  if (!filterEstado.value) {
    return ordersStore.pedidos;
  }
  return ordersStore.pedidos.filter(p => p.estado === filterEstado.value);
});

// Helper functions
const getEstadoBadgeClass = (estado: string) => {
  const classes: Record<string, string> = {
    PENDIENTE: 'bg-yellow-100 text-yellow-800',
    CONFIRMADO: 'bg-green-100 text-green-800',
    EN_PROGRESO: 'bg-blue-100 text-blue-800',
    COMPLETADO: 'bg-purple-100 text-purple-800',
    CANCELADO: 'bg-red-100 text-red-800',
  };
  return classes[estado] || 'bg-gray-100 text-gray-800';
};

const getEventIcon = (tipoEvento: string) => {
  const icons: Record<string, string> = {
    'Boda': '💒',
    'Quinceañera': '👗',
    'Cumpleaños': '🎂',
    'Corporativo': '🏢',
    'Conferencia': '🎤',
  };
  return icons[tipoEvento] || '🎉';
};

const getTipoEventoNombre = (pedido: any) => {
  if (!pedido) return '';
  if (pedido.tipo_evento_nombre) return pedido.tipo_evento_nombre;
  const tipoId = pedido.tipo_evento_id ?? pedido.tipo_evento;
  if (!tipoId) return '';
  const te = catalogStore.tiposEvento?.find((t: any) => String(t.id) === String(tipoId));
  return te?.nombre || '';
};

const getPedidoEstadoNombre = (pedido: any) => {
  if (!pedido) return 'DESCONOCIDO';
  // Prefer explicit name fields
  const raw = pedido.estado ?? pedido.estado_nombre ?? pedido.status ?? pedido.estadoValue ?? pedido.estado_value ?? null;
  if (raw === null || raw === undefined) return 'DESCONOCIDO';
  // If it's a string like 'PENDIENTE' or 'pendiente'
  if (typeof raw === 'string') {
    const s = String(raw).toUpperCase();
    // Normalize common variants
    if (s.includes('PEND') || s === 'DRAFT' || s.includes('COTIZ')) return 'PENDIENTE';
    if (s.includes('CONFIRM')) return 'CONFIRMADO';
    if (s.includes('EN_PROG') || s.includes('PROGRES')) return 'EN_PROGRESO';
    if (s.includes('COMP')) return 'COMPLETADO';
    if (s.includes('CANCEL')) return 'CANCELADO';
    return s;
  }
  // If numeric, map to names (best-effort)
  const n = Number(raw);
  switch (n) {
    case 0:
    case 1:
      return 'PENDIENTE';
    case 2:
      return 'CONFIRMADO';
    case 3:
      return 'EN_PROGRESO';
    case 4:
      return 'COMPLETADO';
    case 5:
      return 'CANCELADO';
    default:
      return String(raw);
  }
};

const getPaqueteName = (pedido: any) => {
  if (!pedido || !pedido.paquete_id) return null;
  const pkg = catalogStore.paquetes.find((p: any) => String(p.id) === String(pedido.paquete_id));
  return pkg ? pkg.nombre : null;
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

const viewDetails = async (pedido: any) => {
  try {
    // Cargar detalle completo desde backend
    await ordersStore.fetchPedido(pedido.id);
    const detalle = ordersStore.currentPedido;

    // Asegurar catálogos/proveedores cargados para enriquecer la vista
    await Promise.all([
      catalogStore.fetchPaquetes(),
      catalogStore.fetchTiposEvento(),
    ]);

    // Cargar proveedores desde endpoint público (evita usar ruta admin y 403)
    let publicProveedores: any[] = [];
    try {
      publicProveedores = await providersApi.getAllProveedoresPublic();
    } catch (e) {
      console.warn('No se pudo cargar proveedores públicos, usando cache local', e);
      publicProveedores = providersStore.proveedores || [];
    }

    // Soportar dos formas de respuesta del backend:
    // 1) { pedido: {...}, items: [...], reservas: [...] }
    // 2) objeto plano con campos y arrays en el root
    const pedidoObj = detalle?.pedido || detalle || {};
    const reservas: any[] = detalle?.reservas || detalle?.reservas_list || detalle?.reservas || [];
    const items: any[] = detalle?.items || pedidoObj.items || [];

    const proveedoresMap: Record<string, any> = {};
    publicProveedores.forEach((p: any) => { proveedoresMap[String(p.id)] = p; });

    // Enriquecer items con proveedor asignado (intenta varias claves posibles en reservas)
    const itemsEnriched = items.map((it: any) => {
      // buscar reserva asociada probando varias claves
      const reserva = reservas.find((r: any) => {
        const maybeIds = [r.item_pedido_id, r.item_id, r.itemId, r.itemPedidoId, r.item];
        return maybeIds.some(id => id !== undefined && String(id) === String(it.id));
      }) || null;

      // detectar id de proveedor en reserva usando varias claves
      const proveedorId = reserva?.proveedor_id ?? reserva?.provider_id ?? reserva?.proveedorId ?? reserva?.providerId ?? null;
      const proveedor = proveedorId ? proveedoresMap[String(proveedorId)] : (reserva && reserva.proveedor ? reserva.proveedor : null);

      // Normalizar precio y cantidad con fallbacks
      const cantidad = it.cantidad ?? it.quantity ?? it.cant ?? 1;
      const precioUnit = it.subtotal ? (it.subtotal / Math.max(1, cantidad)) : (it.precio_unitario ?? it.precio ?? it.monto ?? it.price ?? 0);
      const subtotal = it.subtotal ?? (precioUnit * cantidad) ?? 0;

      return { ...it, cantidad, precio_unitario: precioUnit, subtotal, reserva: reserva || null, proveedor: proveedor || null };
    });

    // Encontrar paquete nombre si aplica
    let paqueteNombre = pedidoObj.paquete_nombre || null;
    if (!paqueteNombre && (pedidoObj.paquete_id || pedidoObj.paquete)) {
      const pkgId = pedidoObj.paquete_id ?? pedidoObj.paquete?.id;
      const pkg = catalogStore.paquetes.find((p: any) => String(p.id) === String(pkgId));
      paqueteNombre = pkg?.nombre || pedidoObj.paquete?.nombre || null;
    }

    // Estado y total con múltiples posibles nombres
    const estadoVal = pedidoObj.estado_nombre || pedidoObj.estado || pedidoObj.status || pedidoObj.estado_value || 'DESCONOCIDO';
    const totalVal = pedidoObj.monto_total ?? pedidoObj.total ?? pedidoObj.monto ?? 0;

    // Si tipo_evento_nombre no viene, intentar resolverlo desde el catálogo usando tipo_evento_id
    let tipoEventoNombre = pedidoObj.tipo_evento_nombre ?? null;
    if (!tipoEventoNombre && pedidoObj.tipo_evento_id) {
      const te = catalogStore.tipos_evento?.find((t: any) => String(t.id) === String(pedidoObj.tipo_evento_id));
      tipoEventoNombre = te?.nombre || tipoEventoNombre;
    }

    selectedPedido.value = {
      ...pedidoObj,
      tipo_evento_nombre: tipoEventoNombre,
      items: itemsEnriched,
      reservas,
      paquete_nombre: paqueteNombre,
      estado: estadoVal,
      total: Number(totalVal ?? 0),
      comentarios: pedidoObj.notas || pedidoObj.comentarios || pedidoObj.notas_extra || '',
      created_at: pedidoObj.created_at || pedidoObj.createdAt || new Date().toISOString(),
    };

    showDetailsModal.value = true;
  } catch (err: any) {
    ui.showToast('No se pudo cargar el detalle del pedido: ' + (err.response?.data?.detail || err.message), 'error');
  }
};

const confirmCancel = async (pedido: any) => {
  const ok = await ui.showConfirmWithFallback(`¿Está seguro de cancelar el pedido #${pedido.id}?`, 'Cancelar pedido');
  if (!ok) return;
  try {
    // map cancel to deletePedido which sets estado=CANCELADO on backend
    await ordersStore.deletePedido(pedido.id);
    await loadPedidos();
    ui.showToast('Pedido cancelado', 'success');
  } catch (error: any) {
    ui.showToast('Error al cancelar el pedido: ' + (error.response?.data?.detail || error.message), 'error');
  }
};

const loadPedidos = async () => {
  if (authStore.user) {
    await ordersStore.fetchPedidos(authStore.user.id);
  }
};

onMounted(async () => {
  await loadPedidos();
  // Preload catalog info to enrich list (paquetes, tipos)
  try {
    await Promise.all([
      catalogStore.fetchPaquetes(),
      catalogStore.fetchTiposEvento(),
    ]);
  } catch (e) {
    // ignore errors; list still works without catalog enrichment
    console.warn('No se pudieron cargar catálogos para MisPedidos', e);
  }
});
</script>
