export default async function globalSetup() {
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
