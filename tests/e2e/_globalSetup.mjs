import { execFileSync } from "child_process";
import { fileURLToPath } from "url";
import { dirname, resolve } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, "../..");

/**
 * Regenerate the render-expectations oracle before any spec reads it.
 * This prevents stale-fixture false passes when markdown sources change.
 */
function regenerateRenderExpectations() {
  const script = resolve(REPO_ROOT, "scripts/generate-render-expectations.mjs");
  const out = resolve(
    REPO_ROOT,
    "tests/e2e/fixtures/render-expectations.json",
  );
  execFileSync(process.execPath, [script, "--out", out], {
    cwd: REPO_ROOT,
    stdio: "inherit",
  });
}

export default async function globalSetup() {
  regenerateRenderExpectations();
  const port = parseInt(process.env.PW_PORT || "8765", 10);
  const url = `http://127.0.0.1:${port}/version.json`;
  let res;
  try {
    res = await fetch(url, { cache: "no-store" });
  } catch (e) {
    throw new Error(
      `Phase C globalSetup: failed to GET ${url}; is mkdocs serving? underlying: ${e.message}`,
    );
  }
  if (!res.ok)
    throw new Error(`Phase C globalSetup: ${url} returned ${res.status}`);
  const body = await res.json();
  if (!body.sha)
    throw new Error(
      `Phase C globalSetup: version.json missing sha; check overrides/hooks/cache_bust.py`,
    );
  process.env.E2E_BUILD_SHA = body.sha;
  console.log(`[globalSetup] build-SHA verified: ${body.sha}`);
}
