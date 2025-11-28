<template>
  <div class="max-w-4xl mx-auto py-8 px-4">
    <h1 class="text-3xl font-bold text-gray-900 mb-2">Crear Nuevo Pedido</h1>
    <p class="text-gray-600 mb-8">Complete los siguientes pasos para crear su pedido</p>

    <!-- Progress Steps -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div 
          v-for="step in steps" 
          :key="step.number"
          class="flex items-center"
          :class="{ 'flex-1': step.number < steps.length }"
        >
          <div class="flex items-center">
            <div 
              class="flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all"
              :class="[
                currentStep > step.number 
                  ? 'bg-primary-500 border-primary-500 text-white' 
                  : currentStep === step.number
                  ? 'border-primary-500 text-primary-500'
                  : 'border-gray-300 text-gray-400'
              ]"
            >
              <CheckIcon v-if="currentStep > step.number" class="w-6 h-6" />
              <span v-else>{{ step.number }}</span>
            </div>
            <span 
              class="ml-2 text-sm font-medium"
              :class="currentStep >= step.number ? 'text-gray-900' : 'text-gray-500'"
            >
              {{ step.title }}
            </span>
          </div>
          <div 
            v-if="step.number < steps.length"
            class="flex-1 h-0.5 mx-4"
            :class="currentStep > step.number ? 'bg-primary-500' : 'bg-gray-300'"
          ></div>
        </div>
      </div>
    </div>

    <!-- Step Content -->
    <Card class="mb-6">
      <!-- Step 1: Tipo Evento y Paquete -->
      <div v-if="currentStep === 1">
        <h2 class="text-xl font-semibold mb-6">Detalles del Evento</h2>
        
        <div class="space-y-6">
          <!-- Tipo de Evento -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Evento <span class="text-red-500">*</span>
            </label>
            <select
              v-model="draft.tipo_evento_id"
              @change="onTipoEventoChange"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              required
            >
              <option :value="null">Seleccione un tipo de evento</option>
              <option 
                v-for="tipo in catalogStore.tiposEvento" 
                :key="tipo.id"
                :value="tipo.id"
              >
                {{ tipo.nombre }}
              </option>
            </select>
          </div>

          <!-- Paquete -->
          <div v-if="draft.tipo_evento_id">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Seleccione un Paquete (Opcional)
            </label>
            <div class="space-y-3">
              <label class="flex items-start p-4 border-2 rounded-lg cursor-pointer transition-all hover:border-primary-200">
                <input
                  type="radio"
                  v-model="draft.paquete_id"
                  :value="null"
                  class="mt-1 text-primary-600 focus:ring-primary-500"
                />
                <div class="ml-3">
                  <div class="font-medium">Sin paquete (servicios a la carta)</div>
                  <div class="text-sm text-gray-500">Seleccione servicios individuales en el siguiente paso</div>
                </div>
              </label>

              <label 
                v-for="paquete in filteredPaquetes" 
                :key="paquete.id"
                class="flex items-start p-4 border-2 rounded-lg cursor-pointer transition-all hover:border-primary-200"
                :class="draft.paquete_id === paquete.id ? 'border-primary-500 bg-primary-50' : 'border-gray-200'"
              >
                <input
                  type="radio"
                  v-model="draft.paquete_id"
                  :value="paquete.id"
                  class="mt-1 text-primary-600 focus:ring-primary-500"
                />
                <div class="ml-3 flex-1">
                  <div class="font-medium">{{ paquete.nombre }}</div>
                  <div class="text-sm text-gray-600 mt-1">{{ paquete.descripcion }}</div>
                  <div class="text-lg font-bold text-primary-600 mt-2">
                    S/ {{ paquete.precio_base?.toFixed(2) || '0.00' }}
                  </div>
                  <div v-if="paquete.servicios && paquete.servicios.length > 0" class="mt-2 flex flex-wrap gap-1">
                    <span 
                      v-for="servicio in paquete.servicios.slice(0, 3)" 
                      :key="servicio.id"
                      class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800"
                    >
                      ✓ {{ servicio.nombre }}
                    </span>
                    <span v-if="paquete.servicios.length > 3" class="text-xs text-gray-500">
                      +{{ paquete.servicios.length - 3 }} más
                    </span>
                  </div>
                </div>
              </label>
            </div>
          </div>

          <!-- Fecha del Evento -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Fecha del Evento <span class="text-red-500">*</span>
            </label>
            <input
              v-model="draft.fecha_evento"
              type="date"
              :min="minDate"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              required
            />
            <p class="text-sm text-gray-500 mt-1">Mínimo 30 días de anticipación</p>
          </div>

          <!-- Número de Invitados -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Número de Invitados <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="draft.num_invitados"
              type="number"
              min="10"
              max="1000"
              step="10"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              required
            />
            <p class="text-sm text-gray-500 mt-1">Entre 10 y 1000 personas</p>
          </div>
        </div>
      </div>

      <!-- Step 2: Servicios Adicionales -->
      <div v-if="currentStep === 2">
        <h2 class="text-xl font-semibold mb-6">Servicios Adicionales</h2>
        
        <div class="space-y-6">
          <div v-if="availableServicios.length === 0">
            <p class="text-gray-500 text-center py-8">
              No hay servicios adicionales disponibles para este tipo de evento.
            </p>
          </div>

          <div v-else>
            <!-- Group by category -->
            <div 
              v-for="categoria in serviciosByCategory" 
              :key="categoria.name"
              class="mb-6"
            >
              <h3 class="text-lg font-medium text-gray-900 mb-3">{{ categoria.name }}</h3>
              <div class="space-y-3">
                <label 
                  v-for="servicio in categoria.servicios" 
                  :key="servicio.id"
                  class="flex items-start p-4 border-2 rounded-lg cursor-pointer transition-all hover:border-primary-200"
                  :class="[
                    isServicioSelected(servicio.id) ? 'border-primary-500 bg-primary-50' : 'border-gray-200',
                    !servicio.disponible ? 'opacity-50 cursor-not-allowed' : ''
                  ]"
                >
                  <input
                    type="checkbox"
                    :value="servicio.id"
                    v-model="draft.servicios_adicionales"
                    :disabled="!servicio.disponible"
                    class="mt-1 text-primary-600 focus:ring-primary-500 rounded"
                  />
                  <div class="ml-3 flex-1">
                    <div class="flex items-center justify-between">
                      <div class="font-medium">{{ servicio.nombre }}</div>
                      <div class="text-lg font-bold text-primary-600">
                        S/ {{ servicio.precio_unitario?.toFixed(2) || '0.00' }}
                      </div>
                    </div>
                    <p class="text-sm text-gray-600 mt-1">{{ servicio.descripcion }}</p>
                    <span 
                      v-if="!servicio.disponible" 
                      class="inline-block mt-2 px-2 py-1 text-xs rounded-full bg-red-100 text-red-800"
                    >
                      No disponible
                    </span>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <!-- Comentarios -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Comentarios Especiales (Opcional)
            </label>
            <textarea
              v-model="draft.comentarios"
              rows="4"
              maxlength="500"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Ej: Preferencia por colores pasteles, alergia a flores..."
            ></textarea>
            <p class="text-sm text-gray-500 mt-1">
              {{ draft.comentarios?.length || 0 }}/500 caracteres
            </p>
          </div>
        </div>

        <!-- Price Summary -->
        <div class="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 class="font-semibold mb-3">Resumen de Precio</h3>
          <div class="space-y-2">
            <div v-if="selectedPaquete" class="flex justify-between">
              <span>Subtotal Paquete:</span>
              <span class="font-medium">S/ {{ selectedPaquete.precio_base?.toFixed(2) }}</span>
            </div>
            <div v-if="draft.servicios_adicionales.length > 0">
              <div class="text-sm font-medium mb-1">Servicios Adicionales:</div>
              <div 
                v-for="servicioId in draft.servicios_adicionales" 
                :key="servicioId"
                class="flex justify-between text-sm ml-4"
              >
                <span>- {{ getServicioName(servicioId) }}</span>
                <span>S/ {{ getServicioPrice(servicioId)?.toFixed(2) }}</span>
              </div>
            </div>
            <div class="border-t border-gray-300 pt-2 mt-2 flex justify-between text-lg font-bold">
              <span>TOTAL:</span>
              <span class="text-primary-600">S/ {{ totalPrice.toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 3: Confirmación -->
      <div v-if="currentStep === 3">
        <h2 class="text-xl font-semibold mb-6">Confirmar Pedido</h2>
        
        <div class="space-y-4">
          <Card>
            <h3 class="font-semibold text-lg mb-4">Resumen de tu Pedido</h3>
            
            <div class="space-y-3">
              <div class="flex justify-between py-2 border-b">
                <span class="text-gray-600">Tipo de Evento:</span>
                <span class="font-medium">{{ getTipoEventoName() }}</span>
              </div>
              <div class="flex justify-between py-2 border-b">
                <span class="text-gray-600">Fecha:</span>
                <span class="font-medium">{{ formatDate(draft.fecha_evento) }}</span>
              </div>
              <div class="flex justify-between py-2 border-b">
                <span class="text-gray-600">Invitados:</span>
                <span class="font-medium">{{ draft.num_invitados }} personas</span>
              </div>
              
              <div v-if="selectedPaquete" class="py-2 border-b">
                <div class="font-medium mb-2">Paquete Seleccionado:</div>
                <div class="ml-4 space-y-1">
                  <div class="font-semibold text-primary-600">
                    {{ selectedPaquete.nombre }} - S/ {{ selectedPaquete.precio_base?.toFixed(2) }}
                  </div>
                  <div class="text-sm text-gray-600">Incluye:</div>
                  <ul class="list-disc list-inside text-sm text-gray-600 ml-2">
                    <li v-for="servicio in selectedPaquete.servicios" :key="servicio.id">
                      {{ servicio.nombre }}
                    </li>
                  </ul>
                </div>
              </div>
              
              <div v-if="draft.servicios_adicionales.length > 0" class="py-2 border-b">
                <div class="font-medium mb-2">Servicios Adicionales:</div>
                <ul class="ml-4 space-y-1">
                  <li 
                    v-for="servicioId in draft.servicios_adicionales" 
                    :key="servicioId"
                    class="flex justify-between text-sm"
                  >
                    <span>• {{ getServicioName(servicioId) }}</span>
                    <span class="text-gray-600">S/ {{ getServicioPrice(servicioId)?.toFixed(2) }}</span>
                  </li>
                </ul>
              </div>
              
              <div v-if="draft.comentarios" class="py-2 border-b">
                <div class="font-medium mb-1">Comentarios:</div>
                <p class="text-sm text-gray-600 italic ml-4">"{{ draft.comentarios }}"</p>
              </div>
              
              <div class="flex justify-between py-3 text-xl font-bold bg-primary-50 -mx-6 px-6 mt-4">
                <span>TOTAL A PAGAR:</span>
                <span class="text-primary-600">S/ {{ totalPrice.toFixed(2) }}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </Card>

    <!-- Navigation Buttons -->
    <div class="flex justify-between">
      <Button
        v-if="currentStep > 1"
        variant="secondary"
        @click="previousStep"
      >
        ← Atrás
      </Button>
      <div v-else></div>

      <div class="flex gap-3">
        <Button
          variant="ghost"
          @click="cancelWizard"
        >
          Cancelar
        </Button>
        <Button
          v-if="currentStep < 3"
          variant="primary"
          @click="nextStep"
          :disabled="!canProceed"
        >
          Siguiente →
        </Button>
        <Button
          v-else
          variant="primary"
          @click="confirmOrder"
          :loading="submitting"
        >
          Confirmar Pedido
        </Button>
      </div>
    </div>

    <!-- Success Modal -->
    <Modal v-model="showSuccessModal" title="¡Pedido Creado Exitosamente!">
      <div class="text-center py-6">
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
          <CheckIcon class="h-6 w-6 text-green-600" />
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">
          Tu pedido ha sido creado
        </h3>
        <p class="text-sm text-gray-500 mb-6">
          Pedido #{{ createdOrderId }} - Estado: PENDIENTE
        </p>
        <div class="flex gap-3 justify-center">
          <Button variant="secondary" @click="goToOrders">
            Ver Mis Pedidos
          </Button>
          <Button variant="primary" @click="createAnother">
            Crear Otro Pedido
          </Button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCatalogStore } from '@/stores/catalog';
import { useOrdersStore } from '@/stores/orders';
import { useUiStore } from '@/stores/ui';
import { CheckIcon } from '@heroicons/vue/24/outline';
import Card from '@/components/common/Card.vue';
import Button from '@/components/common/Button.vue';
import Modal from '@/components/common/Modal.vue';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const router = useRouter();
const catalogStore = useCatalogStore();
const ordersStore = useOrdersStore();
const ui = useUiStore();

const currentStep = ref(1);
const submitting = ref(false);
const showSuccessModal = ref(false);
const createdOrderId = ref<number | null>(null);

const steps = [
  { number: 1, title: 'Tipo Evento' },
  { number: 2, title: 'Servicios' },
  { number: 3, title: 'Confirmar' },
];

// Draft order from store
const draft = computed(() => ordersStore.getDraft());

// Min date (30 days from today)
const minDate = computed(() => {
  const date = new Date();
  date.setDate(date.getDate() + 30);
  return date.toISOString().split('T')[0];
});

// Filtered paquetes based on tipo_evento
const filteredPaquetes = computed(() => {
  if (!draft.value.tipo_evento_id) return [];
  return catalogStore.paquetes.filter(
    p => p.tipo_evento_id === draft.value.tipo_evento_id
  );
});

// Selected paquete
const selectedPaquete = computed(() => {
  if (!draft.value.paquete_id) return null;
  return catalogStore.paquetes.find(p => p.id === draft.value.paquete_id);
});

// Available servicios (not in paquete)
const availableServicios = computed(() => {
  if (!draft.value.tipo_evento_id) return [];
  
  const paqueteServicioIds = selectedPaquete.value?.servicios?.map(s => s.id) || [];
  
  return catalogStore.servicios.filter(s => 
    s.tipo_evento_id === draft.value.tipo_evento_id &&
    !paqueteServicioIds.includes(s.id)
  );
});

// Group servicios by category
const serviciosByCategory = computed(() => {
  const categories: Record<string, any[]> = {};
  
  availableServicios.value.forEach(servicio => {
    const cat = servicio.categoria || 'Otros';
    if (!categories[cat]) {
      categories[cat] = [];
    }
    categories[cat].push(servicio);
  });
  
  return Object.entries(categories).map(([name, servicios]) => ({
    name,
    servicios,
  }));
});

// Total price calculation
const totalPrice = computed(() => {
  let total = 0;
  
  // Add paquete price
  if (selectedPaquete.value) {
    total += selectedPaquete.value.precio_base || 0;
  }
  
  // Add servicios adicionales
  draft.value.servicios_adicionales.forEach(servicioId => {
    const servicio = catalogStore.servicios.find(s => s.id === servicioId);
    if (servicio) {
      total += servicio.precio_unitario || 0;
    }
  });
  
  return total;
});

// Validation
const canProceed = computed(() => {
  if (currentStep.value === 1) {
    return draft.value.tipo_evento_id && 
           draft.value.fecha_evento && 
           draft.value.num_invitados >= 10;
  }
  return true;
});

// Methods
const onTipoEventoChange = async () => {
  // Reset paquete when tipo changes
  ordersStore.updateDraft({ paquete_id: null, servicios_adicionales: [] });
  
  // Load paquetes and servicios for this tipo
  if (draft.value.tipo_evento_id) {
    await catalogStore.fetchPaquetes();
    await catalogStore.fetchServicios();
  }
};

const isServicioSelected = (servicioId: number) => {
  return draft.value.servicios_adicionales.includes(servicioId);
};

const getServicioName = (servicioId: number) => {
  const servicio = catalogStore.servicios.find(s => s.id === servicioId);
  return servicio?.nombre || 'Desconocido';
};

const getServicioPrice = (servicioId: number) => {
  const servicio = catalogStore.servicios.find(s => s.id === servicioId);
  return servicio?.precio_unitario || 0;
};

const getTipoEventoName = () => {
  const tipo = catalogStore.tiposEvento.find(t => t.id === draft.value.tipo_evento_id);
  return tipo?.nombre || 'Desconocido';
};

const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return '';
  try {
    return format(new Date(dateStr), "d 'de' MMMM 'de' yyyy", { locale: es });
  } catch {
    return dateStr;
  }
};

const nextStep = () => {
  if (canProceed.value && currentStep.value < 3) {
    currentStep.value++;
  }
};

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--;
  }
};

const cancelWizard = async () => {
  const ok = await ui.showConfirm('¿Está seguro de cancelar? Se perderán los datos ingresados.', 'Cancelar');
  if (ok) {
    ordersStore.clearDraft();
    router.push('/cliente/dashboard');
  }
};

const confirmOrder = async () => {
  try {
    submitting.value = true;
    
    const orderData = {
      tipo_evento_id: draft.value.tipo_evento_id!,
      fecha_evento: draft.value.fecha_evento!,
      num_invitados: draft.value.num_invitados!,
      paquete_id: draft.value.paquete_id,
      servicios_adicionales: draft.value.servicios_adicionales,
      comentarios: draft.value.comentarios,
    };
    
    const createdOrder = await ordersStore.createPedido(orderData);
    createdOrderId.value = createdOrder.id;
    
    // Clear draft and show success
    ordersStore.clearDraft();
    showSuccessModal.value = true;
  } catch (error: any) {
    ui.showToast('Error al crear el pedido: ' + (error.response?.data?.detail || error.message), 'error', 6000);
  } finally {
    submitting.value = false;
  }
};

const goToOrders = () => {
  showSuccessModal.value = false;
  router.push('/cliente/pedidos');
};

const createAnother = () => {
  showSuccessModal.value = false;
  currentStep.value = 1;
  ordersStore.clearDraft();
};

onMounted(async () => {
  // Load catalog data
  await catalogStore.fetchTiposEvento();
  await catalogStore.fetchPaquetes();
  await catalogStore.fetchServicios();
});
</script>