<script setup lang="ts">
import SelectButton from "primevue/selectbutton";
import AppLayout from "../components/AppLayout.vue";
import { dateZones } from "../format";
import { useSettingsStore } from "../stores/settings";

/** The display settings: where dates show. */
const settings = useSettingsStore();
</script>

<template>
  <AppLayout title="Settings">
    <p id="zone-label">Show dates in</p>
    <!-- UX: never ask before switching the date zone; it applies at once and switching back undoes it. -->
    <SelectButton
      v-model="settings.zone"
      :options="dateZones"
      option-label="label"
      option-value="value"
      :allow-empty="false"
      aria-labelledby="zone-label"
    />
  </AppLayout>
</template>
