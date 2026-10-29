import { defineConfig, devices } from "@playwright/test";

/** The port of the fake inventory (cmd/fake-upstream). */
const fakePort = 8291;

/** The port of the fleet server (cmd/fleet), backed by the fake. */
const appPort = 8292;

export default defineConfig({
  testDir: "e2e",
  forbidOnly: !!process.env.CI,
  reporter: "list",
  use: { ...devices["Desktop Chrome"], baseURL: `http://localhost:${appPort}` },
  projects: [{ name: "e2e" }],
  webServer: [
    {
      command: "go run ./cmd/fake-upstream",
      cwd: "..",
      url: `http://localhost:${fakePort}/sites`,
      env: { FAKE_ADDR: `localhost:${fakePort}` },
    },
    {
      // Serves the build in dist/: run `bun run build` first.
      command: "go run ./cmd/fleet",
      cwd: "..",
      url: `http://localhost:${appPort}/api/sites`,
      env: {
        FLEET_ADDR: `localhost:${appPort}`,
        FLEET_UPSTREAM_URL: `http://localhost:${fakePort}`,
      },
    },
  ],
});
