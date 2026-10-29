<script setup lang="ts">
import ProgressSpinner from "primevue/progressspinner";
import { computed, onMounted, useTemplateRef } from "vue";
import { useRoute } from "vue-router";
import { type Device, device as loadDevice } from "../api";
import AppLayout from "../components/AppLayout.vue";
import LoadError from "../components/LoadError.vue";
import { formatDate } from "../format";
import { useRead } from "../read";
import { useSettingsStore } from "../stores/settings";
import { useSitesStore } from "../stores/sites";

/**
 * One device, the one the `id` route parameter names: its serial number as
 * the title, then its site, model, and when it was added and last reported.
 * An unknown ID says so.
 */
const route = useRoute();
const settings = useSettingsStore();
const sites = useSitesStore();

/** The ID the route names. */
const id = computed(() => String(route.params.id));

/** The device; null until read, and when the server has none. */
const read = useRead<Device | null>("device", null, () => loadDevice(id.value));
const { data: device, busy, error } = read;

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

/** Copies the serial number of `serial` to the clipboard. */
async function copySerial(serial: string) {
  await navigator.clipboard.writeText(serial);
}

/** Returns the name of the site with ID `at`, or the ID when unknown. */
function siteName(at: string) {
  return sites.byId.get(at)?.name ?? at;
}

onMounted(() => {
  void read.run();
  void sites.load();
});
</script>

<template>
  <AppLayout ref="layout" :title="device?.serial ?? 'Device'">
    <ProgressSpinner v-if="busy" aria-label="Loading device" />
    <LoadError v-else-if="error" :message="error" @retry="retry" />
    <p v-else-if="device === null" role="status">
      No device has the ID {{ id }}.
    </p>
    <dl v-else class="facts">
      <dt>Serial</dt>
      <dd>
        {{ device.serial }}
        <button type="button" class="copy" @click="copySerial(device.serial)">
          <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">
            <path d="M4 4h8v10H4z M6 2h8v10" fill="none" stroke="currentColor" />
          </svg>
        </button>
      </dd>
      <dt>Site</dt>
      <dd>
        <RouterLink :to="{ name: 'devices', query: { site: device.site_id } }">
          {{ siteName(device.site_id) }}
        </RouterLink>
      </dd>
      <dt>Model</dt>
      <dd>{{ device.model }}</dd>
      <dt>Added</dt>
      <dd>{{ formatDate(device.added, settings.zone) }}</dd>
      <dt>Last seen</dt>
      <dd>{{ formatDate(device.last_seen, settings.zone) }}</dd>
    </dl>
  </AppLayout>
</template>

<style scoped>
.copy {
  margin-left: 0.5rem;
  padding: 0.125rem;
  border: 0;
  background: none;
  color: var(--p-primary-color);
  cursor: pointer;
}

.facts {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 0.5rem 1.5rem;
  margin: 0;
}

dt {
  color: var(--p-text-muted-color);
}

dd {
  margin: 0;
}
</style>
