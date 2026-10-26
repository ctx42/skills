import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vitest/config";

/**
 * Returns the URL of the Go server listening on `address`, as FLEET_ADDR sets
 * it; like the server, it falls back to ":8080". An address listening on all
 * interfaces is reached on localhost.
 */
function apiUrl(address = process.env.FLEET_ADDR || ":8080"): string {
  const colon = address.lastIndexOf(":");
  let host = address.slice(0, colon);
  if (["", "0.0.0.0", "::", "[::]"].includes(host)) {
    host = "localhost";
  }
  return `http://${host}:${address.slice(colon + 1)}`;
}

export default defineConfig({
  plugins: [vue()],
  server: {
    // The Go server (cmd/fleet) answers the API; the browser sees one origin.
    proxy: { "/api": apiUrl() },
  },
  test: {
    environment: "happy-dom",
    include: ["src/**/*.test.ts"],
    setupFiles: ["src/testSetup.ts"],
    unstubGlobals: true,
    restoreMocks: true,
    coverage: {
      provider: "v8",
      include: ["src/**/*.{ts,vue}"],
      // Test helpers and the entry point that only mounts the app.
      exclude: [
        "src/**/*.test.ts",
        "src/testing.ts",
        "src/testSetup.ts",
        "src/main.ts",
      ],
      reporter: ["text-summary", "text", "html"],
      // Just below the measured totals: a run losing coverage fails.
      thresholds: { lines: 99, statements: 99, functions: 99, branches: 95 },
      reportsDirectory: "coverage",
    },
  },
});
