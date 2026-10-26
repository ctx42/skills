<script setup lang="ts">
import { useTemplateRef, watchEffect } from "vue";

/**
 * A page: the header with the application name and its navigation, then
 * the page heading, `title`, which also names the browser tab, and the
 * `default` slot, the page's content. `focusHeading()` moves the focus to
 * the heading, for a page whose focused control went away.
 */
const props = defineProps<{
  /** The page heading. */
  title: string;
  wide?: boolean;
}>();

defineSlots<{ default(): unknown }>();

defineExpose({ focusHeading });

/** The page heading. */
const heading = useTemplateRef<HTMLHeadingElement>("heading");

/** Moves the focus to the page heading. */
function focusHeading() {
  heading.value?.focus();
}

watchEffect(() => {
  document.title = `${props.title} · Fleet`;
});
</script>

<template>
  <header class="header">
    <RouterLink :to="{ name: 'devices' }" class="brand">Fleet</RouterLink>
    <nav aria-label="Main">
      <RouterLink :to="{ name: 'devices' }">Devices</RouterLink>
      <RouterLink :to="{ name: 'sites' }">Sites</RouterLink>
      <RouterLink :to="{ name: 'settings' }">Settings</RouterLink>
    </nav>
  </header>
  <main class="main" :class="{ wide }">
    <h1 ref="heading" tabindex="-1">{{ title }}</h1>
    <slot />
  </main>
</template>

<style scoped>
.header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 24px;
  padding: 12px 24px;
  border-bottom: 1px solid var(--p-content-border-color);
}

.brand {
  font-weight: 700;
  text-decoration: none;
  color: var(--p-text-color);
}

nav {
  display: flex;
  gap: 1rem;
}

nav a {
  color: var(--p-primary-color);
}

nav a.router-link-exact-active {
  font-weight: 600;
}

.main {
  max-width: 72rem;
  padding: 1rem 1.5rem;
}

.main.wide {
  max-width: none;
}

h1 {
  margin: 0 0 1rem;
  font-size: 1.5rem;
}
</style>
