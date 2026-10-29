/** PrimeVue setup: the built-in Material preset, in its light look. */
import Material from "@primeuix/themes/material";
import type { PrimeVueConfiguration } from "primevue/config";
import { markRaw } from "vue";

/** The options the application installs PrimeVue with. */
export const primeVueOptions: PrimeVueConfiguration = {
  // The preset is large and never changes: kept out of reactivity.
  theme: { preset: markRaw(Material), options: { darkModeSelector: false } },
};
