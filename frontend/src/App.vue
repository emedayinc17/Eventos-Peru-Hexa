<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores';

const authStore = useAuthStore();

onMounted(() => {
  authStore.initializeAuth();
});
</script>

<template>
  <router-view />
  <!-- Global UI helpers -->
  <ConfirmDialog />
  <ToastContainer />
</template>

<script setup lang="ts">
// register components
import ConfirmDialog from '@/components/common/ConfirmDialog.vue';
import ToastContainer from '@/components/common/ToastContainer.vue';
</script>
