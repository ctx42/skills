/**
 * The user's display settings, kept in the browser so they outlive a visit.
 * A browser that blocks storage keeps them for the visit only.
 */
import { defineStore } from "pinia";
import { ref, watch } from "vue";
import { type DateZone, isDateZone } from "../format";

/** The storage key the settings live under. */
export const settingsKey = "fleet.settings";

/** Returns the date zone kept in the browser, or "utc". */
function loadZone(): DateZone {
  try {
    const kept: unknown = JSON.parse(localStorage.getItem(settingsKey) ?? "{}");
    const zone =
      typeof kept === "object" && kept !== null && "zone" in kept
        ? kept.zone
        : "";
    return isDateZone(zone) ? zone : "utc";
  } catch {
    return "utc";
  }
}

/** The display settings store. */
export const useSettingsStore = defineStore("settings", () => {
  /** Where dates show; "utc" unless the user chose otherwise. */
  const zone = ref<DateZone>(loadZone());

  watch(zone, (next) => {
    try {
      // The default is kept as no entry at all.
      if (next === "utc") {
        localStorage.removeItem(settingsKey);
      } else {
        localStorage.setItem(settingsKey, JSON.stringify({ zone: next }));
      }
    } catch {
      // Blocked storage: the choice holds for this visit.
    }
  });

  return { zone };
});
