import { defineConfig } from "@playwright/test";

const PORT = parseInt(process.env.PW_PORT || "8765", 10);
const isCI = !!process.env.CI;

export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: /.*\.spec\.mjs/,
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: false,
  forbidOnly: isCI,
  retries: isCI ? 2 : 0,
  workers: isCI ? 1 : undefined,
  reporter: isCI
    ? [["github"], ["html", { open: "never" }]]
    : [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: `http://127.0.0.1:${PORT}/assessment/`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    actionTimeout: 5_000,
    navigationTimeout: 15_000,
  },
  snapshotDir: "tests/e2e/__snapshots__",
  webServer: {
    command:
      process.platform === "win32"
        ? `cmd /C "mkdocs build --quiet && python -m http.server ${PORT} --directory site --bind 127.0.0.1"`
        : `bash -c "mkdocs build --quiet && python3 -m http.server ${PORT} --directory site --bind 127.0.0.1"`,
    url: `http://127.0.0.1:${PORT}/assessment/`,
    reuseExistingServer: !isCI,
    timeout: 240_000,
    stdout: "pipe",
    stderr: "pipe",
  },
  globalSetup: "./tests/e2e/_globalSetup.mjs",
  projects: [
    { name: "chromium", use: { browserName: "chromium" } },
    // Firefox/WebKit added in later PR per Theme 5.
  ],
});
