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

/**
 * Click a button that re-renders the SPA. Uses dispatchEvent to bypass
 * Playwright's post-click stability check (which races against the
 * synchronous DOM rebuild that follows navigation buttons in this SPA).
 */
export async function navClick(page, name) {
  await page.getByRole("button", { name }).dispatchEvent("click");
}

/**
 * Helper: wait for a download triggered by an action and return its bytes. */
export async function expectDownload(page, action) {
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    action(),
  ]);
  const path = await download.path();
  return { suggestedName: download.suggestedFilename(), path };
}

/**
 * Selector Policy (see tests/e2e/README.md "Selector Policy"):
 *
 * 1. Prefer accessible-name + role selectors (`getByLabel`, `getByRole`)
 *    so the suite doubles as light a11y coverage and survives CSS churn.
 * 2. For repeated structural anchors (control cards, the SPA root), use
 *    the existing `data-control-id` and `id="assessment-app"` hooks the
 *    SPA already emits in `docs/javascripts/assessment-app.js`.
 * 3. Avoid `nth-child` / text-content selectors except where the SPA
 *    has no labelled affordance (e.g. the institution-type select had a
 *    label "Institution Type"; a future split would need a `data-testid`).
 *
 * Persona → SPA mapping
 *   persona.scoping.organizationName → "Organization Name" input
 *   persona.scoping.assessorName     → "Assessor Name" input
 *   persona.scoping.institutionType  → "Institution Type" select value
 *                                      ("bank" → "bank", etc.; matches
 *                                      the `value` attr on the option)
 *   persona.scoping.zones[]          → checkboxes inside fieldset
 *                                      "Active Governance Zones"
 *   persona.answers[controlId]       → "Yes"/"Partial"/"No"/"N/A" button
 *                                      inside `[data-control-id]` card.
 */

/** Map persona institutionType values → SPA option values. */
const INSTITUTION_TYPE_MAP = {
  bank: "bank",
  "broker-dealer": "broker-dealer",
  "investment-adviser": "adviser",
  adviser: "adviser",
  "dual-registered": "dual-registered",
  "insurance-carrier": "insurance",
  "insurance-wholesale": "insurance",
  insurance: "insurance",
};

/** Map persona answer strings → button accessible name. */
const ANSWER_LABEL = { yes: "Yes", partial: "Partial", no: "No", na: "N/A" };

/**
 * Walk the welcome → scoping flow and submit, leaving the page on Phase 1.
 * Assumes the page is already at `/assessment/` and the SPA has hydrated.
 *
 * Idempotency: dismisses any incidental confirm() dialogs that the SPA
 * may surface (e.g. the "save before results" prompt is downstream and
 * not triggered here, but we register a generic dismisser for safety).
 */
export async function seedScoping(page, persona) {
  const sc = persona.scoping;

  // Welcome → Scoping. Use dispatchEvent to avoid post-click stability
  // races when the SPA re-renders and detaches the button.
  // Also wait up to 15s for SPA hydration (fetch of assessment-data.json).
  const startBtn = page.getByRole("button", { name: "Start New Assessment" });
  await startBtn.waitFor({ timeout: 15_000 });
  await startBtn.dispatchEvent("click");

  // Wait for scoping form to render.
  await page.getByRole("heading", { name: "Assessment Scoping" }).waitFor();

  // Text inputs (labelled).
  if (sc.organizationName) {
    await page.getByLabel("Organization Name").fill(sc.organizationName);
  }
  if (sc.assessorName) {
    await page.getByLabel("Assessor Name").fill(sc.assessorName);
  }

  // Institution type — labelled select. The SPA renders TWO selects with
  // the visible label "Institution type" (the v1.4 sector calibration card
  // also calls itself "Institution type (sector calibration)"). Disambiguate
  // by exact label match on the original "Institution Type" (capital T).
  if (sc.institutionType) {
    const mapped = INSTITUTION_TYPE_MAP[sc.institutionType] || sc.institutionType;
    await page
      .getByLabel("Institution Type", { exact: true })
      .selectOption(mapped);
  }

  // Zones — checkboxes inside the "Active Governance Zones" fieldset.
  // <fieldset> + <legend> exposes role="group" with the legend as
  // accessible name; each checkbox has value="1"|"2"|"3".
  const zoneFieldset = page.getByRole("group", {
    name: "Active Governance Zones",
  });
  const wantedZones = new Set((sc.zones || []).map(Number));
  for (const z of [1, 2, 3]) {
    const cb = zoneFieldset.locator(`input[type="checkbox"][value="${z}"]`);
    const checked = await cb.isChecked();
    if (wantedZones.has(z) && !checked) await cb.check();
    else if (!wantedZones.has(z) && checked) await cb.uncheck();
  }

  // Submit. The click handler synchronously re-renders the SPA, which
  // detaches the "Begin Assessment" button — Playwright's default
  // post-click stability check times out on the now-detached node.
  // dispatchEvent fires the handler without waiting for stability.
  await page
    .getByRole("button", { name: "Begin Assessment" })
    .dispatchEvent("click");

  // Wait for Phase 1 to render.
  await page
    .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
    .waitFor();
}

/**
 * Click answer buttons for each control specified in persona.answers.
 * Stops at the bottom of Phase 1 (does NOT navigate to results).
 *
 * persona.answers shape: { "1.1": "yes", "1.2": "partial", ... }
 * If empty/missing, no clicks are performed (e.g. edge-empty persona).
 */
export async function clickThroughPhase1(page, persona) {
  const answers = persona.answers || {};
  const ids = Object.keys(answers);
  if (ids.length === 0) return;

  for (const id of ids) {
    const answer = answers[id];
    const labelText = ANSWER_LABEL[answer];
    if (!labelText) {
      throw new Error(
        `Unknown answer value '${answer}' for control ${id}; expected one of yes/partial/no/na`,
      );
    }
    const card = page.locator(`[data-control-id="${id}"]`);
    // Ensure the card is in the DOM. Pillar headers may be collapsed but
    // the cards are still rendered (only `.collapsed` hides them via CSS),
    // so we expand the parent if necessary.
    await card.first().waitFor({ state: "attached" });
    const pillar = card.locator(
      'xpath=ancestor::div[contains(@class,"ag-pillar-controls")]',
    );
    if ((await pillar.count()) > 0) {
      const isCollapsed = await pillar
        .first()
        .evaluate((el) => el.classList.contains("collapsed"));
      if (isCollapsed) {
        const header = pillar.locator(
          'xpath=preceding-sibling::div[contains(@class,"ag-pillar-header")][1]',
        );
        if ((await header.count()) > 0) await header.first().click();
      }
    }
    await card
      .getByRole("button", { name: labelText })
      .click();
  }
}

export { expect };
