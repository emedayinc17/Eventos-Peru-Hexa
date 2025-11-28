<script setup lang="ts">
import AdminNavbar from './AdminNavbar.vue';
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <AdminNavbar />
    <main class="py-4 sm:py-6 lg:py-8">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <router-view />
      </div>
    </main>
  </div>
</template>
