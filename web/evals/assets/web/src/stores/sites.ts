/** The sites, loaded once and shared by the pages that name them. */
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { sites as loadSites, type Site } from "../api";

/** The sites store. */
export const useSitesStore = defineStore("sites", () => {
  /** The sites; empty until loaded. */
  const sites = ref<Site[]>([]);

  /** The sites by ID; empty until loaded. */
  const byId = computed(() => new Map(sites.value.map((s) => [s.id, s])));

  /** The load in flight; null when none runs. */
  let running: Promise<void> | null = null;

  /**
   * Loads the sites unless they are loaded; callers during a load share it.
   * A failure leaves them empty, and the next load retries.
   */
  function load(): Promise<void> {
    // PERF: never keep the sites in browser storage; they change between visits.
    if (sites.value.length > 0) return Promise.resolve();
    running ??= (async () => {
      try {
        sites.value = await loadSites();
      } catch {
        // Sites then show as IDs.
      } finally {
        running = null;
      }
    })();
    return running;
  }

  return { sites, byId, load };
});
