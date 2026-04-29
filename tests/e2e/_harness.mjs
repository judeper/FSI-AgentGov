import { expect } from "@playwright/test";
import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));

/** Load a persona fixture by name. Throws if not found. */
export function loadPersona(name) {
  const path = join(here, "fixtures", "personas", `${name}.json`);
  if (!existsSync(path)) throw new Error(`Persona not found: ${path}`);
  return JSON.parse(readFileSync(path, "utf8"));
}

/** Clear ALL site storage: localStorage, sessionStorage, IndexedDB, ServiceWorkers, cookies. */
export async function clearAllStorage(context) {
  await context.clearCookies();
  // localStorage / sessionStorage are per-page; iterate after navigation.
}

/** Per-page storage clear; call after first navigation. */
export async function clearPageStorage(page) {
  await page.evaluate(async () => {
    try { localStorage.clear(); } catch {}
    try { sessionStorage.clear(); } catch {}
    if ("indexedDB" in window && indexedDB.databases) {
      try {
        const dbs = await indexedDB.databases();
        await Promise.all(dbs.map((d) => new Promise((res) => {
          const req = indexedDB.deleteDatabase(d.name);
          req.onsuccess = req.onerror = req.onblocked = () => res();
        })));
      } catch {}
    }
    if ("serviceWorker" in navigator) {
      try {
        const regs = await navigator.serviceWorker.getRegistrations();
        await Promise.all(regs.map((r) => r.unregister()));
      } catch {}
    }
  });
}

/** Freeze Date.now() so timestamps in exports are deterministic. */
export async function freezeTime(page, isoTime = "2026-01-15T12:00:00.000Z") {
  const t = new Date(isoTime).getTime();
  await page.addInitScript((fixedT) => {
    const _Date = Date;
    function FrozenDate(...args) {
      if (args.length === 0) return new _Date(fixedT);
      return new _Date(...args);
    }
    FrozenDate.now = () => fixedT;
    FrozenDate.UTC = _Date.UTC;
    FrozenDate.parse = _Date.parse;
    FrozenDate.prototype = _Date.prototype;
    globalThis.Date = FrozenDate;
  }, t);
}

/** Helper: wait for a download triggered by an action and return its bytes. */
export async function expectDownload(page, action) {
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    action(),
  ]);
  const path = await download.path();
  return { suggestedName: download.suggestedFilename(), path };
}

/**
 * Helper: scope an assessment via the welcome screen.
 * STUB — first smoke spec PR will fill in selector specifics after
 * inspecting the SPA's DOM in a real browser. Do not guess selectors.
 */
export async function seedScoping(_page, _persona) {
  throw new Error(
    "seedScoping not yet implemented; first smoke spec will fill in selector specifics",
  );
}

/**
 * Helper: walk through Phase 1 answering controls per persona.
 * STUB — first smoke spec PR will fill in selector specifics.
 */
export async function clickThroughPhase1(_page, _persona) {
  throw new Error(
    "clickThroughPhase1 not yet implemented; first smoke spec will fill in selector specifics",
  );
}

export { expect };
