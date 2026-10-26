/** Starts the application in the page's `#app` element. */
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";
import { createApp } from "vue";
import App from "./App.vue";
import { createAppRouter } from "./router";
import { primeVueOptions } from "./theme";

createApp(App)
  .use(createPinia())
  .use(createAppRouter())
  .use(PrimeVue, primeVueOptions)
  .mount("#app");
