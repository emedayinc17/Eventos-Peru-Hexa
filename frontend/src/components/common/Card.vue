<script setup lang="ts">
export interface CardProps {
  title?: string;
  padding?: boolean;
  hover?: boolean;
}

withDefaults(defineProps<CardProps>(), {
  padding: true,
  hover: false,
});
</script>

<template>
  <div
    :class="[
      'bg-white rounded-lg shadow-md',
      padding ? 'p-6' : '',
      hover ? 'hover:shadow-lg transition-shadow duration-200' : '',
    ]"
  >
    <h3 v-if="title" class="text-lg font-semibold text-gray-900 mb-4">
      {{ title }}
    </h3>
    <slot></slot>
  </div>
</template>
