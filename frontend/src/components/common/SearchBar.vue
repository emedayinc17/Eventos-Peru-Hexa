<script setup lang="ts">
import { ref, watch } from 'vue';
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline';

export interface SearchBarProps {
  modelValue: string;
  placeholder?: string;
  debounce?: number;
}

const props = withDefaults(defineProps<SearchBarProps>(), {
  placeholder: 'Buscar...',
  debounce: 300,
});

const emit = defineEmits<{
  'update:modelValue': [value: string];
  search: [value: string];
}>();

const localValue = ref(props.modelValue);
let debounceTimeout: ReturnType<typeof setTimeout> | null = null;

watch(() => props.modelValue, (newVal) => {
  localValue.value = newVal;
});

const handleInput = (event: Event) => {
  const value = (event.target as HTMLInputElement).value;
  localValue.value = value;
  emit('update:modelValue', value);
  
  if (debounceTimeout) {
    clearTimeout(debounceTimeout);
  }
  
  debounceTimeout = setTimeout(() => {
    emit('search', value);
  }, props.debounce);
};
</script>

<template>
  <div class="relative">
    <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
      <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
    </div>
    <input
      type="text"
      :value="localValue"
      :placeholder="placeholder"
      class="block w-full rounded-md border-0 py-2 pl-10 pr-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
      @input="handleInput"
    />
  </div>
</template>
