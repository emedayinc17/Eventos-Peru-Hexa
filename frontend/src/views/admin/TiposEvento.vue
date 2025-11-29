<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useCatalogStore } from '@/stores';
import { Button, Modal, Input, SearchBar } from '@/components/common';
import type { TipoEvento } from '@/types';
import { useUiStore } from '@/stores/ui';
import { PencilIcon, TrashIcon, PlusIcon, TagIcon } from '@heroicons/vue/24/outline';

const catalogStore = useCatalogStore();
const ui = useUiStore();
const searchQuery = ref('');
const showModal = ref(false);
const editingItem = ref<TipoEvento | null>(null);

const form = ref({
  nombre: '',
  descripcion: '',
});

const filteredItems = computed(() => {
  if (!searchQuery.value) return catalogStore.tiposEvento;
  const query = searchQuery.value.toLowerCase();
  return catalogStore.tiposEvento.filter(item => 
    item.nombre.toLowerCase().includes(query) || 
    item.descripcion.toLowerCase().includes(query)
  );
});

onMounted(async () => {
  await catalogStore.fetchTiposEvento();
});

const openCreateModal = () => {
  editingItem.value = null;
  form.value = { nombre: '', descripcion: '' };
  showModal.value = true;
};

const openEditModal = (item: TipoEvento) => {
  editingItem.value = item;
  form.value = { nombre: item.nombre, descripcion: item.descripcion };
  showModal.value = true;
};

const handleSave = async () => {
  try {
    if (editingItem.value) {
      await catalogStore.updateTipoEvento(editingItem.value.id, form.value);
    } else {
      await catalogStore.createTipoEvento(form.value);
    }
    showModal.value = false;
    ui.showToast('Tipo de evento guardado', 'success');
  } catch (error) {
    console.error('Error al guardar:', error);
    ui.showToast('Error al guardar tipo de evento', 'error');
  }
};

const handleDelete = async (item: TipoEvento) => {
  console.debug('[TiposEvento] handleDelete invoked', item);
  ui.showToast('Intentando eliminar: ' + item.nombre, 'info', 1500);
  const ok = await ui.showConfirmWithFallback(`¿Eliminar "${item.nombre}"?`, 'Eliminar tipo');
  if (!ok) return;
  try {
    await catalogStore.deleteTipoEvento(item.id);
    ui.showToast('Tipo eliminado', 'success');
  } catch (error) {
    console.error('Error al eliminar:', error);
    ui.showToast('Error al eliminar tipo', 'error');
  }
};
</script>

<template>
  <div class="w-full h-full p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Tipos de Evento</h1>
        <p class="text-gray-600 text-sm mt-1">Categorías base para los eventos del sistema</p>
      </div>
      <Button @click="openCreateModal" class="flex items-center gap-2">
        <PlusIcon class="w-5 h-5" />
        Nuevo Tipo
      </Button>
    </div>

    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
      <div class="w-full md:w-1/3">
        <SearchBar v-model="searchQuery" placeholder="Buscar tipos de evento..." />
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-16">Icono</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Nombre</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Descripción</th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="catalogStore.loading">
              <td colspan="4" class="px-6 py-12 text-center text-gray-500">Cargando...</td>
            </tr>
            <tr v-else-if="filteredItems.length === 0">
              <td colspan="4" class="px-6 py-12 text-center text-gray-500">No se encontraron tipos de evento</td>
            </tr>
            <tr v-else v-for="item in filteredItems" :key="item.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600">
                  <TagIcon class="w-4 h-4" />
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ item.nombre }}</div>
                <div class="text-xs text-gray-400 font-mono mt-0.5">{{ item.id.substring(0, 8) }}...</div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-500">{{ item.descripcion }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end gap-2">
                  <button 
                    @click="openEditModal(item)" 
                    class="p-1 text-gray-400 hover:text-primary-600 transition-colors rounded-full hover:bg-primary-50"
                    title="Editar"
                  >
                    <PencilIcon class="w-5 h-5" />
                  </button>
                  <button 
                    @click="handleDelete(item)" 
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

    <Modal :open="showModal" :title="editingItem ? 'Editar Tipo de Evento' : 'Nuevo Tipo de Evento'" @close="showModal = false">
      <form @submit.prevent="handleSave" class="space-y-4">
        <Input v-model="form.nombre" label="Nombre" required placeholder="Ej. Matrimonio, Conferencia" />
        <Input v-model="form.descripcion" label="Descripción" type="textarea" placeholder="Breve descripción del tipo de evento" />
      </form>
      <template #footer>
        <Button variant="secondary" @click="showModal = false">Cancelar</Button>
        <Button @click="handleSave" :loading="catalogStore.loading">Guardar</Button>
      </template>
    </Modal>
  </div>
</template>
