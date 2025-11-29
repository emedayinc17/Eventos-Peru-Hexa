<template>
  <TransitionRoot :show="isOpen" as="template" @after-leave="query = ''" appear>
    <Dialog as="div" class="relative z-50" @close="close">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-gray-500 bg-opacity-25 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-10 overflow-y-auto p-4 sm:p-6 md:p-20">
        <TransitionChild
          as="template"
          enter="ease-out duration-300"
          enter-from="opacity-0 scale-95"
          enter-to="opacity-100 scale-100"
          leave="ease-in duration-200"
          leave-from="opacity-100 scale-100"
          leave-to="opacity-0 scale-95"
        >
          <DialogPanel
            class="mx-auto max-w-3xl transform divide-y divide-gray-100 overflow-hidden rounded-xl bg-white shadow-2xl ring-1 ring-black ring-opacity-5 transition-all"
          >
            <Combobox @update:modelValue="onSelect">
              <div class="relative">
                <MagnifyingGlassIcon
                  class="pointer-events-none absolute left-4 top-3.5 h-5 w-5 text-gray-400"
                  aria-hidden="true"
                />
                <ComboboxInput
                  class="h-12 w-full border-0 bg-transparent pl-11 pr-4 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm"
                  placeholder="Buscar paquetes, servicios, pedidos..."
                  @change="query = $event.target.value"
                  @keydown.esc="close"
                />
              </div>

              <ComboboxOptions
                v-if="query !== '' && (filteredPaquetes.length > 0 || filteredServicios.length > 0 || filteredPedidos.length > 0)"
                static
                class="max-h-96 scroll-py-3 overflow-y-auto p-3"
              >
                <!-- Paquetes -->
                <div v-if="filteredPaquetes.length > 0" class="mb-2">
                  <h2 class="bg-gray-100 px-4 py-2.5 text-xs font-semibold text-gray-900">
                    Paquetes
                  </h2>
                  <ComboboxOption
                    v-for="paquete in filteredPaquetes"
                    :key="'paquete-' + paquete.id"
                    :value="{ type: 'paquete', item: paquete }"
                    as="template"
                    v-slot="{ active }"
                  >
                    <li
                      :class="[
                        'flex cursor-pointer select-none items-center rounded-md px-4 py-2',
                        active && 'bg-primary-600 text-white',
                      ]"
                    >
                      <ArchiveBoxIcon
                        :class="['h-6 w-6 flex-none', active ? 'text-white' : 'text-gray-400']"
                        aria-hidden="true"
                      />
                      <div class="ml-3 flex-auto truncate">
                        <div :class="['text-sm font-medium', active ? 'text-white' : 'text-gray-900']">
                          {{ paquete.nombre }}
                        </div>
                        <div :class="['text-sm', active ? 'text-primary-200' : 'text-gray-500']">
                          S/ {{ paquete.precio_base?.toFixed(2) || '0.00' }}
                        </div>
                      </div>
                    </li>
                  </ComboboxOption>
                </div>

                <!-- Servicios -->
                <div v-if="filteredServicios.length > 0" class="mb-2">
                  <h2 class="bg-gray-100 px-4 py-2.5 text-xs font-semibold text-gray-900">
                    Servicios
                  </h2>
                  <ComboboxOption
                    v-for="servicio in filteredServicios"
                    :key="'servicio-' + servicio.id"
                    :value="{ type: 'servicio', item: servicio }"
                    as="template"
                    v-slot="{ active }"
                  >
                    <li
                      :class="[
                        'flex cursor-pointer select-none items-center rounded-md px-4 py-2',
                        active && 'bg-primary-600 text-white',
                      ]"
                    >
                      <WrenchScrewdriverIcon
                        :class="['h-6 w-6 flex-none', active ? 'text-white' : 'text-gray-400']"
                        aria-hidden="true"
                      />
                      <div class="ml-3 flex-auto truncate">
                        <div :class="['text-sm font-medium', active ? 'text-white' : 'text-gray-900']">
                          {{ servicio.nombre }}
                        </div>
                        <div :class="['text-sm', active ? 'text-primary-200' : 'text-gray-500']">
                          {{ servicio.categoria }}
                        </div>
                      </div>
                    </li>
                  </ComboboxOption>
                </div>

                <!-- Pedidos (solo para admin) -->
                <div v-if="filteredPedidos.length > 0 && authStore.isAdmin" class="mb-2">
                  <h2 class="bg-gray-100 px-4 py-2.5 text-xs font-semibold text-gray-900">
                    Pedidos
                  </h2>
                  <ComboboxOption
                    v-for="pedido in filteredPedidos"
                    :key="'pedido-' + pedido.id"
                    :value="{ type: 'pedido', item: pedido }"
                    as="template"
                    v-slot="{ active }"
                  >
                    <li
                      :class="[
                        'flex cursor-pointer select-none items-center rounded-md px-4 py-2',
                        active && 'bg-primary-600 text-white',
                      ]"
                    >
                      <ClipboardDocumentCheckIcon
                        :class="['h-6 w-6 flex-none', active ? 'text-white' : 'text-gray-400']"
                        aria-hidden="true"
                      />
                      <div class="ml-3 flex-auto truncate">
                        <div :class="['text-sm font-medium', active ? 'text-white' : 'text-gray-900']">
                          Pedido #{{ pedido.id }}
                        </div>
                        <div :class="['text-sm', active ? 'text-primary-200' : 'text-gray-500']">
                          {{ pedido.fecha_evento }} - {{ pedido.estado_nombre }}
                        </div>
                      </div>
                    </li>
                  </ComboboxOption>
                </div>
              </ComboboxOptions>

              <div v-if="query !== '' && filteredPaquetes.length === 0 && filteredServicios.length === 0 && filteredPedidos.length === 0" class="px-6 py-14 text-center text-sm sm:px-14">
                <ExclamationTriangleIcon class="mx-auto h-6 w-6 text-gray-400" aria-hidden="true" />
                <p class="mt-4 font-semibold text-gray-900">No se encontraron resultados</p>
                <p class="mt-2 text-gray-500">No encontramos nada con ese término de búsqueda.</p>
              </div>

              <div class="flex flex-wrap items-center bg-gray-50 px-4 py-2.5 text-xs text-gray-700">
                <kbd class="mx-1 flex h-5 w-5 items-center justify-center rounded border bg-white font-semibold sm:mx-2">
                  ↑
                </kbd>
                <kbd class="mx-1 flex h-5 w-5 items-center justify-center rounded border bg-white font-semibold sm:mx-2">
                  ↓
                </kbd>
                <span class="sm:hidden">para navegar</span>
                <span class="hidden sm:inline">para navegar,</span>
                <kbd class="mx-1 flex h-5 w-5 items-center justify-center rounded border bg-white font-semibold sm:mx-2">
                  ↵
                </kbd>
                <span class="sm:hidden">para seleccionar</span>
                <span class="hidden sm:inline">para seleccionar,</span>
                <kbd class="mx-1 flex h-5 w-5 items-center justify-center rounded border bg-white font-semibold sm:mx-2">
                  Esc
                </kbd>
                <span>para cerrar</span>
              </div>
            </Combobox>
          </DialogPanel>
        </TransitionChild>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import {
  Combobox,
  ComboboxInput,
  ComboboxOptions,
  ComboboxOption,
  Dialog,
  DialogPanel,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue';
import {
  MagnifyingGlassIcon,
  ArchiveBoxIcon,
  WrenchScrewdriverIcon,
  ClipboardDocumentCheckIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline';
import { useCatalogStore, useOrdersStore, useAuthStore } from '@/stores';

const props = defineProps<{
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const router = useRouter();
const catalogStore = useCatalogStore();
const ordersStore = useOrdersStore();
const authStore = useAuthStore();

const query = ref('');

// Load data when modal opens
watch(() => props.isOpen, async (isOpen) => {
  if (isOpen) {
    await catalogStore.fetchPaquetes();
    await catalogStore.fetchServicios();
    if (authStore.isAdmin) {
      // Load all orders for admin
      // await ordersStore.fetchPedidos();
    }
  }
});

// Filtered results
const filteredPaquetes = computed(() => {
  if (query.value === '') return [];
  const q = query.value.toLowerCase();
  return catalogStore.paquetes
    .filter(p => 
      p.nombre.toLowerCase().includes(q) ||
      p.descripcion?.toLowerCase().includes(q)
    )
    .slice(0, 5);
});

const filteredServicios = computed(() => {
  if (query.value === '') return [];
  const q = query.value.toLowerCase();
  return catalogStore.servicios
    .filter(s => 
      s.nombre.toLowerCase().includes(q) ||
      s.descripcion?.toLowerCase().includes(q) ||
      s.categoria?.toLowerCase().includes(q)
    )
    .slice(0, 5);
});

const filteredPedidos = computed(() => {
  if (query.value === '' || !authStore.isAdmin) return [];
  const q = query.value.toLowerCase();
  return ordersStore.pedidos
    .filter(p => 
      p.id.toString().includes(q) ||
      p.estado_nombre?.toLowerCase().includes(q)
    )
    .slice(0, 5);
});

const onSelect = (selected: any) => {
  if (!selected) return;
  
  const { type, item } = selected;
  
  switch (type) {
    case 'paquete':
      if (authStore.isAdmin) {
        router.push('/admin/paquetes');
      } else {
        router.push(`/paquetes/${item.id}`);
      }
      break;
    case 'servicio':
      if (authStore.isAdmin) {
        router.push('/admin/servicios');
      }
      break;
    case 'pedido':
      if (authStore.isAdmin) {
        router.push('/admin/pedidos');
      }
      break;
  }
  
  close();
};

const close = () => {
  emit('close');
};
</script>
