import { test } from "@playwright/test";
import { expect, getResumeBannerButton, getSavedListResumeButton } from "./_harness.mjs";

/**
 * 30 — Storage namespace migration (E2E regression)
 *
 * Verifies AssessmentApp.prototype._migrateLegacySavedAssessments (PR #144,
 * iter3-2-001) runs at SPA boot and lifts a pre-fix legacy `-current` blob
 * into its per-id slot (STORAGE_KEY+"-data-<id>"). Also asserts:
 *
 *   - After migration, the user can Resume the legacy assessment from the
 *     welcome screen and see their original answers/scoping.
 *   - Re-running the migration is idempotent: a second SPA boot does not
 *     clobber, duplicate, or corrupt the migrated slot. The natural guard
 *     is the `if (perIdKey == null)` check (assessment-app.js L329) — this
 *     spec proves that guard holds end-to-end.
 *
 * SEED STRATEGY: page.addInitScript runs BEFORE every page load, including
 * before the SPA's init() executes the migration. We use it to plant the
 * legacy-only state shape (a `-current` blob + a `-list` entry, but NO
 * `-data-<id>` slot — the exact shape produced by the pre-fix SPA).
 *
 * SPA literal STORAGE_KEY value (docs/javascripts/assessment-app.js L16):
 *   "fsi-agentgov-assessment"
 */

const STORAGE_KEY = "fsi-agentgov-assessment";
const LEGACY_ID = "legacy-001";

/** A minimum-viable legacy state shape: passes validateState, has answers. */
function buildLegacyState() {
  return {
    assessmentId: LEGACY_ID,
    assessmentName: "Legacy Bank — 2025-09-01",
    schemaVersion: "1.4.0",
    createdAt: "2025-09-01T10:00:00.000Z",
    updatedAt: "2025-09-01T10:30:00.000Z",
    scoping: {
      organizationName: "Legacy Bank",
      assessorName: "Pre-PR-144 User",
      assessorRole: "AI Governance Lead",
      institutionType: "bank",
      zones: [1, 2],
      adoptionPhase: 0,
      regulations: [],
      scope: "full",
    },
    responses: {
      "1.1": { answer: "yes", notes: "legacy-note-11", evidenceRef: "" },
      "1.5": { answer: "partial", notes: "", evidenceRef: "" },
    },
    drilldown: {},
    overrides: {},
    completedSteps: ["scoping"],
    selectedSector: "",
    roleFilter: "",
    priorityMode: "full",
    priorityExpanded: false,
    assessmentStatus: "in-progress",
  };
}

/** A legacy `-list` entry (welcome's saved-assessments list pre-PR-144). */
function buildLegacyListEntry(legacyState) {
  return [{
    id: legacyState.assessmentId,
    name: legacyState.assessmentName,
    updatedAt: legacyState.updatedAt,
    createdAt: legacyState.createdAt,
    progress: 3,
  }];
}

async function readAllRelevantStorage(page) {
  return await page.evaluate((k) => ({
    current: localStorage.getItem(k + "-current"),
    list: localStorage.getItem(k + "-list"),
    perId: localStorage.getItem(k + "-data-legacy-001"),
    allKeys: Object.keys(localStorage)
      .filter((key) => key.startsWith(k))
      .sort(),
  }), STORAGE_KEY);
}

test.describe("storage namespace migration @regression", () => {
  test("legacy `-current` is migrated to per-id slot, idempotently @regression", async ({ page }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    const legacyState = buildLegacyState();
    const legacyJson = JSON.stringify(legacyState);
    const legacyList = buildLegacyListEntry(legacyState);

    // Plant pre-PR-144 legacy state BEFORE the SPA boots. addInitScript
    // re-runs on every page load, so reload() below also re-applies it
    // — but the migration's idempotence guard (perIdKey == null) means
    // re-applying does not corrupt the post-migration state because we
    // ALSO re-plant the per-id slot via the same script's check.
    //
    // Critical: we want the FIRST page load to see ONLY the legacy keys
    // (no per-id slot) so the migration runs. On the SECOND load we want
    // to preserve the post-migration state to assert idempotence — the
    // SPA itself will have written the per-id slot after first init().
    // We do NOT clear localStorage between reloads; the addInitScript
    // only seeds when keys are missing.
    await page.addInitScript(({ k, json, listJson, legacyKey }) => {
      // Only seed legacy keys if they are absent AND the per-id slot is
      // also absent — i.e., a truly fresh fixture. After the SPA's first
      // run it will have populated the per-id slot; we leave it alone.
      try {
        if (!localStorage.getItem(k + "-current") &&
            !localStorage.getItem(legacyKey)) {
          localStorage.setItem(k + "-current", json);
          localStorage.setItem(k + "-list", listJson);
        }
      } catch (_) { /* ignore in non-storage contexts */ }
    }, {
      k: STORAGE_KEY,
      json: legacyJson,
      listJson: JSON.stringify(legacyList),
      legacyKey: STORAGE_KEY + "-data-" + LEGACY_ID,
    });

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    // Wait for the SPA to hydrate: the welcome heading is rendered post-init.
    // mkdocs emits its own h1 with the same text — scope to #assessment-app.
    await page
      .locator("#assessment-app")
      .getByRole("heading", { name: "Governance Readiness Assessment" })
      .waitFor({ timeout: 15_000 });

    // Migration assertions ------------------------------------------------
    const after1 = await readAllRelevantStorage(page);
    expect(after1.perId, "per-id slot must be populated by migration").not.toBeNull();
    const migrated = JSON.parse(after1.perId);
    expect(migrated.assessmentId).toBe(LEGACY_ID);
    expect(migrated.scoping.organizationName).toBe("Legacy Bank");
    expect(migrated.responses["1.1"]?.answer).toBe("yes");

    // `-current` is intentionally retained as a "most recently edited"
    // pointer (back-compat) per assessment-app.js L319.
    expect(after1.current).not.toBeNull();
    const current = JSON.parse(after1.current);
    expect(current.assessmentId).toBe(LEGACY_ID);

    // -- Idempotence: reload → migration runs again, state unchanged -----
    await page.reload({ waitUntil: "domcontentloaded" });
    await page
      .locator("#assessment-app")
      .getByRole("heading", { name: "Governance Readiness Assessment" })
      .waitFor({ timeout: 15_000 });

    const after2 = await readAllRelevantStorage(page);
    expect(after2.perId).toBe(after1.perId);
    expect(after2.current).toBe(after1.current);
    expect(after2.list).toBe(after1.list);
    expect(after2.allKeys).toEqual(after1.allKeys);

    // -- Resume legacy-001 from welcome --------------------------------
    await expect(
      getResumeBannerButton(page, "Legacy Bank — 2025-09-01"),
    ).toHaveCount(1);
    await expect(
      getSavedListResumeButton(page, "Legacy Bank — 2025-09-01"),
    ).toHaveCount(1);
    await getSavedListResumeButton(page, "Legacy Bank — 2025-09-01").dispatchEvent("click");
    await page.getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();

    // Confirm the loaded state has the legacy answers/scoping.
    const loaded = await page.evaluate((k) => {
      const raw = localStorage.getItem(k + "-current");
      return raw ? JSON.parse(raw) : null;
    }, STORAGE_KEY);
    expect(loaded.assessmentId).toBe(LEGACY_ID);
    expect(loaded.scoping.organizationName).toBe("Legacy Bank");
    expect(loaded.responses["1.1"]?.answer).toBe("yes");
    expect(loaded.responses["1.5"]?.answer).toBe("partial");
  });
});
