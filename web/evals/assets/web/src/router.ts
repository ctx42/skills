/** Routes, and reading the query string of a route. */
import {
  createRouter,
  createWebHistory,
  type LocationQueryValue,
  type RouterHistory,
} from "vue-router";

// Each page loads on its first visit, so a visit loads only the code of the
// pages it shows.
const DevicePage = () => import("./pages/DevicePage.vue");
const DevicesPage = () => import("./pages/DevicesPage.vue");
const NotFoundPage = () => import("./pages/NotFoundPage.vue");
const SettingsPage = () => import("./pages/SettingsPage.vue");
const SitePage = () => import("./pages/SitePage.vue");
const SitesPage = () => import("./pages/SitesPage.vue");

/** Returns the application router keeping its place in `history`. */
export function createAppRouter(history: RouterHistory = createWebHistory()) {
  return createRouter({
    history,
    routes: [
      { path: "/", name: "devices", component: DevicesPage },
      { path: "/devices/:id", name: "device", component: DevicePage },
      { path: "/sites", name: "sites", component: SitesPage },
      { path: "/sites/:id", name: "site", component: SitePage },
      { path: "/settings", name: "settings", component: SettingsPage },
      { path: "/:path(.*)*", name: "not-found", component: NotFoundPage },
    ],
  });
}

/**
 * Returns the query parameter value `value` as text: "" when it is missing or
 * given without a value, and its first value when given more than once.
 */
export function queryText(
  value: LocationQueryValue | LocationQueryValue[] | undefined,
): string {
  const first = Array.isArray(value) ? value[0] : value;
  return first ?? "";
}
