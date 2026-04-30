import { test, expect } from "@playwright/test";

const PROD = process.env.PROD_URL;
test.skip(!PROD, "prod-probe only runs with PROD_URL set");

test("@prod-probe assessment SPA loads on production", async ({ page }) => {
  const errors = [];
  const IGNORE_PATTERNS = [
    /Content Security Policy directive 'frame-ancestors' is ignored/i,
    /api\.github\.com\/repos\/.+\/(releases\/latest|$|FSI-AgentGov$).*Content Security Policy/i,
    /violates the following Content Security Policy directive: "connect-src/i,
  ];
  const isIgnorable = (text) => IGNORE_PATTERNS.some((re) => re.test(text));
  page.on("pageerror", (e) => {
    if (!isIgnorable(e.message)) errors.push(`pageerror: ${e.message}`);
  });
  page.on("console", (msg) => {
    if (msg.type() === "error" && !isIgnorable(msg.text())) {
      errors.push(`console: ${msg.text()}`);
    }
  });

  await page.goto(`${PROD}assessment/`, {
    waitUntil: "domcontentloaded",
    timeout: 30_000,
  });

  await expect(page.getByRole("heading", { level: 1 })).toBeVisible({
    timeout: 15_000,
  });

  const verResp = await page.request.get(`${PROD}version.json`);
  expect(verResp.status()).toBe(200);
  const ver = await verResp.json();
  expect(ver.sha).toBeTruthy();
  expect(ver.builtAt).toBeTruthy();

  if (errors.length) {
    throw new Error(`Production console/page errors:\n${errors.join("\n")}`);
  }
});
