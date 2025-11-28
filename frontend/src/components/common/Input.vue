<script setup lang="ts">
import { ref, watch } from 'vue';

export interface InputProps {
  modelValue: string | number;
  label?: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'date' | 'textarea';
  placeholder?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  rows?: number;
}

const props = withDefaults(defineProps<InputProps>(), {
  type: 'text',
  disabled: false,
  required: false,
  rows: 3,
});

const emit = defineEmits<{
  'update:modelValue': [value: string | number];
}>();

const inputValue = ref(props.modelValue);

watch(() => props.modelValue, (newVal) => {
  inputValue.value = newVal;
});

const updateValue = (event: Event) => {
  const target = event.target as HTMLInputElement | HTMLTextAreaElement;
  const value = props.type === 'number' ? Number(target.value) : target.value;
  inputValue.value = value;
  emit('update:modelValue', value);
};
</script>

<template>
  <div class="w-full">
    <label v-if="label" class="label">
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>
    
    <textarea
      v-if="type === 'textarea'"
      :value="inputValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :rows="rows"
      :class="[
        'input-field',
        error ? 'input-error' : '',
      ]"
      @input="updateValue"
    />
    
    <input
      v-else
      :type="type"
      :value="inputValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :class="[
        'input-field',
        error ? 'input-error' : '',
      ]"
      @input="updateValue"
    />
    
    <p v-if="error" class="error-message">
      {{ error }}
    </p>
  </div>
</template>
