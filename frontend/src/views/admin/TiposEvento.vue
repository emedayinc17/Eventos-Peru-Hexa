<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useCatalogStore } from '@/stores';
import { Table, Button, Modal, Input, SearchBar } from '@/components/common';
import type { TipoEvento, TableColumn } from '@/types';
import { useUiStore } from '@/stores/ui';

const catalogStore = useCatalogStore();
const ui = useUiStore();
const searchQuery = ref('');
const showModal = ref(false);
const editingItem = ref<TipoEvento | null>(null);

const form = ref({
  nombre: '',
  descripcion: '',
});

const columns: TableColumn[] = [
  { key: 'id', label: 'ID', width: '80px' },
  { key: 'nombre', label: 'Nombre' },
  { key: 'descripcion', label: 'Descripción' },
];

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
  const ok = await ui.showConfirm(`¿Eliminar "${item.nombre}"?`, 'Eliminar tipo');
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
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Tipos de Evento</h1>
      <Button @click="openCreateModal">+ Nuevo Tipo</Button>
    </div>

    <div class="card">
      <div class="mb-4">
        <SearchBar v-model="searchQuery" placeholder="Buscar tipos de evento..." />
      </div>

      <Table :columns="columns" :data="catalogStore.tiposEvento" :loading="catalogStore.loading">
        <template #actions="{ row }">
          <button @click="openEditModal(row)" class="text-primary-600 hover:text-primary-900 mr-4">
            Editar
          </button>
          <button @click="handleDelete(row)" class="text-red-600 hover:text-red-900">
            Eliminar
          </button>
        </template>
      </Table>
    </div>

    <Modal :open="showModal" :title="editingItem ? 'Editar Tipo de Evento' : 'Nuevo Tipo de Evento'" @close="showModal = false">
      <form @submit.prevent="handleSave" class="space-y-4">
        <Input v-model="form.nombre" label="Nombre" required />
        <Input v-model="form.descripcion" label="Descripción" type="textarea" required />
      </form>
      <template #footer>
        <Button variant="outline" @click="showModal = false">Cancelar</Button>
        <Button @click="handleSave" :loading="catalogStore.loading">Guardar</Button>
      </template>
    </Modal>
  </div>
</template>
