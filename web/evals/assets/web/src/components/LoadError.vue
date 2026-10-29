<script setup lang="ts">
import Button from "primevue/button";
import Message from "primevue/message";

/**
 * A read that failed: its `message` and a button to read again, which
 * emits `retry`.
 */
defineProps<{ message: string }>();

const emit = defineEmits<{ retry: [] }>();
</script>

<template>
  <div class="load-error">
    <Message severity="error">{{ message }}</Message>
    <Button label="Try again" severity="secondary" @click="emit('retry')" />
  </div>
</template>

<style scoped>
.load-error {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
}
</style>
