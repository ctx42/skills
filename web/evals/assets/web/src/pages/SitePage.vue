<script setup lang="ts">
import ProgressSpinner from "primevue/progressspinner";
import { computed, useTemplateRef, watch } from "vue";
import { useRoute } from "vue-router";
import { site as loadSite, type Site } from "../api";
import AppLayout from "../components/AppLayout.vue";
import LoadError from "../components/LoadError.vue";
import { useRead } from "../read";

/**
 * One site, the one the `id` route parameter names: its name as the title,
 * its city, and a link to the list of its devices. An unknown ID says so.
 */
const route = useRoute();

/** The ID the route names. */
const id = computed(() => String(route.params.id));

/** The site; null until read, and when the server has none. */
const read = useRead<Site | null>("site", null, () => loadSite(id.value));
const { data: site, busy, error } = read;

/** The page layout, to move the focus within it. */
const layout = useTemplateRef<InstanceType<typeof AppLayout>>("layout");

/**
 * Reads again after a failure; the button asking for it goes away, so the
 * focus moves to the page heading.
 */
async function retry() {
  await read.run();
  layout.value?.focusHeading();
}

watch(id, () => void read.run(), { immediate: true });
</script>

<template>
  <AppLayout ref="layout" :title="site?.name ?? 'Site'">
    <ProgressSpinner v-if="busy" aria-label="Loading site" />
    <LoadError v-else-if="error" :message="error" @retry="retry" />
    <p v-else-if="site === null" role="status">No site has the ID {{ id }}.</p>
    <template v-else>
      <p class="city">{{ site.city }}</p>
      <RouterLink :to="{ name: 'devices', query: { site: site.id } }">
        Devices at this site
      </RouterLink>
    </template>
  </AppLayout>
</template>

<style scoped>
.city {
  color: var(--p-text-muted-color);
}
</style>
