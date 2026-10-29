<script setup lang="ts">
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import { computed } from "vue";
import type { Device, Site } from "../api";
import { type DateZone, formatDate } from "../format";

/**
 * The `devices`, one row each, sortable by every column: the serial number,
 * linking to the device's page, the site's name from `sites` (its ID when
 * `sites` lacks it), the model, and when the device last reported, in
 * `zone`.
 */
const props = defineProps<{
  devices: Device[];
  sites: Map<string, Site>;
  zone: DateZone;
}>();

/** A device as a row: its fields, and the site's name to sort by. */
interface Row extends Device {
  site: string;
}

/** The rows, one per device. */
const rows = computed<Row[]>(() =>
  props.devices.map((device) => ({
    ...device,
    site: props.sites.get(device.site_id)?.name ?? device.site_id,
  })),
);
</script>

<template>
  <DataTable :value="rows" data-key="id" sort-field="serial" :sort-order="1">
    <Column field="serial" header="Serial" sortable>
      <template #body="{ data }: { data: Row }">
        <RouterLink :to="{ name: 'device', params: { id: data.id } }">
          {{ data.serial }}
        </RouterLink>
      </template>
    </Column>
    <Column field="site" header="Site" sortable />
    <Column field="model" header="Model" sortable />
    <Column field="last_seen" header="Last seen" sortable>
      <template #body="{ data }: { data: Row }">
        {{ formatDate(data.last_seen, zone) }}
      </template>
    </Column>
  </DataTable>
</template>
