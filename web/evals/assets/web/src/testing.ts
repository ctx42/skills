/**
 * Test helpers: a fake `fetch` answering canned responses, and fixtures.
 * Only test files import this module.
 */
import { flushPromises, mount, type VueWrapper } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import PrimeVue from "primevue/config";
import { type Mock, vi } from "vitest";
import type { Component } from "vue";
import { createMemoryHistory } from "vue-router";
import type { Device, Site } from "./api";
import { createAppRouter } from "./router";
import { primeVueOptions } from "./theme";

/**
 * Navigates the application router to `path`, then mounts `component` with
 * `props` and with Pinia, the router, and PrimeVue installed as in the
 * application, and waits for what it reads on mounting. Set up
 * {@link fakeFetch} first.
 */
export async function mountAt(
  component: Component,
  path: string,
  props: Record<string, unknown> = {},
) {
  const pinia = createPinia();
  setActivePinia(pinia);
  const router = createAppRouter(createMemoryHistory());
  await router.push(path);
  const wrapper = mount(component, {
    props,
    attachTo: document.body,
    global: { plugins: [pinia, router, [PrimeVue, primeVueOptions]] },
  });
  await flushPromises();
  return { wrapper, router };
}

/** Returns the button of `wrapper` reading `text`; fails when none does. */
export function buttonNamed(wrapper: VueWrapper, text: string) {
  const button = wrapper.findAll("button").find((b) => b.text() === text);
  if (!button) throw new Error(`no button "${text}"`);
  return button;
}

/** Canned answers keyed by `"METHOD /path"`; an Error is thrown instead. */
export type Answers = Record<string, Response | Error>;

/**
 * Replaces the global `fetch` with one answering from `answers`; a request
 * `answers` lacks fails the test.
 */
export function fakeFetch(answers: Answers): Mock<typeof fetch> {
  const fake = vi.fn<typeof fetch>(async (input, init) => {
    const key = `${init?.method ?? "GET"} ${String(input)}`;
    const answer = answers[key];
    if (answer === undefined) throw new Error(`unexpected fetch: ${key}`);
    if (answer instanceof Error) throw answer;
    return answer.clone();
  });
  vi.stubGlobal("fetch", fake);
  return fake;
}

/** Returns a JSON response. */
export function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

/** Returns a response whose body never arrives: what it answers loads on. */
export function stalled(): Response {
  return new Response(new ReadableStream(), { status: 200 });
}

/** Returns the error `fetch` throws when the server cannot be reached. */
export function networkError(): TypeError {
  return new TypeError("Failed to fetch");
}

/** Returns a storage whose every call throws, as a blocked one does. */
export function blockedStorage(): Storage {
  const blocked = () => {
    throw new Error("blocked");
  };
  return {
    getItem: blocked,
    setItem: blocked,
    removeItem: blocked,
  } as unknown as Storage;
}

/** The sites of the tests. */
export const testSites: Site[] = [
  { id: "s1", name: "North Yard", city: "Zurich" },
  { id: "s2", name: "Harbour", city: "Basel" },
];

/** The devices of the tests; d2 never reported, d3 is at an unknown site. */
export const testDevices: Device[] = [
  {
    id: "d1",
    serial: "SN-0001",
    site_id: "s1",
    model: "T-100",
    added: "2026-01-05T08:00:00Z",
    last_seen: "2026-10-20T07:15:00Z",
  },
  {
    id: "d2",
    serial: "SN-0002",
    site_id: "s2",
    model: "T-200",
    added: "2026-03-02T14:00:00Z",
    last_seen: null,
  },
  {
    id: "d3",
    serial: "XN-0003",
    site_id: "s9",
    model: "H-10",
    added: "2026-04-18T06:45:00Z",
    last_seen: "2026-10-22T05:00:00Z",
  },
];

/** The request listing the sites. */
export const sitesPath = "GET /api/sites";

/** Returns the request listing the devices of site `site`, or of all. */
export function devicesPath(site = "") {
  return site ? `GET /api/devices?site=${site}` : "GET /api/devices";
}

/** Returns the answer listing `sites`. */
export function sitesAnswers(sites = testSites): Answers {
  return { [sitesPath]: json(200, { data: sites }) };
}

/** Returns the answer listing `devices` as those of site `site`. */
export function devicesAnswers(devices = testDevices, site = ""): Answers {
  return { [devicesPath(site)]: json(200, { data: devices }) };
}
