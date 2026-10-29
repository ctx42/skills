<script setup lang="ts">
import { useRoute } from "vue-router";
import AppLayout from "../components/AppLayout.vue";

/** A path no page lives at: says so and links to the devices. */
const route = useRoute();
</script>

<template>
  <AppLayout title="Page not found">
    <p>No page lives at <code>{{ route.path }}</code>.</p>
    <RouterLink :to="{ name: 'devices' }">Go to the devices</RouterLink>
  </AppLayout>
</template>
