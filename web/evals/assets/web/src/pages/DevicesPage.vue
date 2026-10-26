<script setup lang="ts">
import InputText from "primevue/inputtext";
import ProgressSpinner from "primevue/progressspinner";
import Select from "primevue/select";
import { computed, onMounted, useTemplateRef, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { devices as loadDevices } from "../api";
import AppLayout from "../components/AppLayout.vue";
import DeviceTable from "../components/DeviceTable.vue";
import LoadError from "../components/LoadError.vue";
import { useRead } from "../read";
import { queryText } from "../router";
import { useSettingsStore } from "../stores/settings";
import { useSitesStore } from "../stores/sites";

/**
 * The devices, narrowed to one site by the site picker and to serial
 * numbers containing the search text, which "/" focuses. Both live in the
 * query string (`site`, `q`), left out while empty, so a link reproduces
 * the view; picking another site reads that site's devices.
 */
const route = useRoute();
const router = useRouter();
const settings = useSettingsStore();
const sites = useSitesStore();

/** The devices of the site picked. */
const read = useRead("devices", [], () => loadDevices(site.value));
const { data: devs, busy, error } = read;

/** The page layout, to move the focus within it. */
const layout = useTemplateRef<InstanceType<typeof AppLayout>>("layout");

/** The ID of the site picked; "" for every site. */
const site = computed({
  get: () => queryText(route.query.site),
  set: (next: string) => keepQuery({ site: next }),
});

/** The text serial numbers must contain. */
const search = computed({
  get: () => queryText(route.query.q),
  set: (next: string) => keepQuery({ q: next }),
});

/** The site picker's choices: every site, then each site by name. */
const choices = computed(() => [
  { label: "All sites", value: "" },
  ...sites.sites.map((s) => ({ label: s.name, value: s.id })),
]);

/** The devices of the site picked whose serial contains the search text. */
const shown = computed(() => {
  const want = search.value.trim().toLowerCase();
  return devs.value.filter((device) =>
    device.serial.toLowerCase().includes(want),
  );
});

/** Replaces the query values in `next`, leaving empty ones out. */
function keepQuery(next: Record<string, string>) {
  const qry = { ...route.query, ...next };
  for (const [key, value] of Object.entries(qry)) {
    // Delete the key when the value is empty.
    if (!value) delete qry[key];
  }
  void router.replace({ query: qry });
}

/**
 * Reads again after a failure; the button asking for it goes away, so the
 * focus moves to the page heading.
 */
async function retry() {
  await read.run();
  layout.value?.focusHeading();
}

/** Moves the focus to the search box on "/", unless typing elsewhere. */
function onKey(event: KeyboardEvent) {
  if (event.key !== "/" || event.target instanceof HTMLInputElement) return;
  event.preventDefault();
  document.getElementById("search")?.focus();
}

watch(site, () => void read.run(), { immediate: true });

onMounted(() => {
  void read.run();
  void sites.load();
  window.addEventListener("keydown", onKey);
});
</script>

<template>
  <AppLayout ref="layout" title="Devices" wide>
    <div class="filters">
      <div class="field">
        <label id="site-label" for="site">Site</label>
        <Select
          v-model="site"
          input-id="site"
          :options="choices"
          option-label="label"
          option-value="value"
          aria-labelledby="site-label"
        />
      </div>
      <div class="field">
        <label for="search">Search</label>
        <InputText id="search" v-model="search" placeholder="Serial number" />
      </div>
    </div>
    <ProgressSpinner v-if="busy" aria-label="Loading devices" />
    <LoadError v-else-if="error" :message="error" @retry="retry" />
    <p v-else-if="shown.length === 0" class="empty" role="status">
      No devices match.
    </p>
    <DeviceTable
      v-else
      :devices="shown"
      :sites="sites.byId"
      :zone="settings.zone"
    />
  </AppLayout>
</template>

<style scoped>
.filters {
  display: flex;
  min-width: 44rem;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.empty {
  color: var(--p-text-muted-color);
}
</style>
