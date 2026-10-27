<script setup lang="ts">
import ProgressSpinner from "primevue/progressspinner";
import { computed, onMounted, ref, useTemplateRef } from "vue";
import { sites as loadSites } from "../api";
import AppLayout from "../components/AppLayout.vue";
import LoadError from "../components/LoadError.vue";
import { useRead } from "../read";

/** The sites, by city, each linking to the list of its devices. */
const read = useRead("sites", [], async () => {
  const all = await loadSites();
  return [...all].sort((a, b) => a.name.localeCompare(b.name));
});
const { data: sites, busy, error } = read;

/** The text a site's city must contain to be listed. */
const city = ref("");

/** The sites whose city contains the city filter's text. */
const shown = computed(() => {
  const want = city.value.trim().toLowerCase();
  return sites.value.filter((site) => site.city.toLowerCase().includes(want));
});

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

onMounted(() => void read.run());
</script>

<template>
  <AppLayout ref="layout" title="Sites">
    <ProgressSpinner v-if="busy" aria-label="Loading sites" />
    <LoadError v-else-if="error" :message="error" @retry="retry" />
    <p v-else-if="sites.length === 0" role="status">No sites yet.</p>
    <template v-else>
      <input v-model="city" class="city-filter" placeholder="City" />
      <!-- UX: never show device counts on the site list; they go stale between visits. -->
      <ul class="sites">
        <li v-for="site in shown" :key="site.id">
          <RouterLink class="name" :to="`/?site=${site.id}`">
            {{ site.name }}
          </RouterLink>
          <span class="city">{{ site.city }}</span>
          <RouterLink :to="{ name: 'site', params: { id: site.id } }">
            Details
          </RouterLink>
        </li>
      </ul>
    </template>
  </AppLayout>
</template>

<style scoped>
.sites {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0;
  list-style: none;
}

.city {
  margin: 0 0.75rem;
  color: #b8b8b8;
}

.name {
  display: inline-block;
  max-width: 4rem;
  overflow: hidden;
  white-space: nowrap;
  vertical-align: bottom;
}
</style>
