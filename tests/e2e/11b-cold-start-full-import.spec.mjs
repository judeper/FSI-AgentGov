import { test } from "@playwright/test";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";
import {
  clearAllStorage,
  clearPageStorage,
  expect,
  freezeTime,
} from "./_harness.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const FIXTURE = join(here, "fixtures", "exports", "full-cco-export.json");

/**
 * 11b — Cold-start full-assessment import (E2E regression)
 *
 * Sibling to 11-import-roundtrip. That spec exports → re-imports the SAME
 * JSON in the SAME browser. This one verifies the COLD-start import flow:
 *
 *   - No prior `state` (importState falls into the `!this.state` branch).
 *   - Empty resume list on welcome.
 *   - User imports a JSON they received from elsewhere.
 *
 * Catches regressions in any code path that incorrectly assumes a "current
 * assessment" exists pre-import (the destructive-gate confirm in
 * importState relies on `this.state && this.state.responses`; a regression
 * making `this.state` mandatory would break cold-start imports).
 *
 * Fixture: tests/e2e/fixtures/exports/full-cco-export.json — see the
 * sibling README.md for the regen procedure. The fixture matches the
 * full-cco persona's scoping + a representative spread of Phase 1 answers.
 */

const STORAGE_KEY = "fsi-agentgov-assessment";

test.describe("cold-start full-assessment import @regression", () => {
  test("imports JSON into fresh browser, persists across reload, collision is non-corrupting @regression", async ({
    page,
    context,
  }) => {
    page.on("dialog", (d) => d.accept().catch(() => {}));
    await freezeTime(page);

    // -- Phase 1: COLD-START IMPORT -----------------------------------
    await clearAllStorage(context);
    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    // Welcome must be visible AND empty: no resume list, no current state.
    // The mkdocs page has its own h1 with the same text as the SPA welcome
    // h2; scope inside #assessment-app to disambiguate.
    await page
      .locator("#assessment-app")
      .getByRole("heading", { name: "Governance Readiness Assessment" })
      .waitFor({ timeout: 15_000 });
    await expect(page.locator(".ag-saved-list")).toHaveCount(0);

    // Confirm fixture is well-formed before we feed it to the SPA.
    const exported = JSON.parse(readFileSync(FIXTURE, "utf8"));
    expect(exported.assessmentId).toBeTruthy();
    expect(exported.scoping?.organizationName).toBe("Globex Financial");
    expect(Object.keys(exported.responses).length).toBeGreaterThanOrEqual(5);

    // Import via the welcome "Resume or Import Saved Assessment" button.
    const chooserPromise = page.waitForEvent("filechooser");
    await page
      .getByRole("button", { name: "Resume or Import Saved Assessment" })
      .dispatchEvent("click");
    const chooser = await chooserPromise;
    await chooser.setFiles(FIXTURE);

    // After a successful cold-start import the SPA navigates to Phase 1.
    await page
      .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();

    // localStorage now reflects the imported state (under the per-id slot).
    const importedId = exported.assessmentId;
    const slot = await page.evaluate(
      ([k, id]) => {
        const raw = localStorage.getItem(k + "-data-" + id);
        return raw ? JSON.parse(raw) : null;
      },
      [STORAGE_KEY, importedId],
    );
    expect(slot, "per-id slot for imported assessment must exist").not.toBeNull();
    expect(slot.assessmentId).toBe(importedId);
    expect(slot.scoping.organizationName).toBe("Globex Financial");
    expect(slot.responses["1.1"]?.answer).toBe("yes");
    expect(slot.responses["1.7"]?.answer).toBe("no");

    // -- Phase 2: PERSISTENCE ACROSS RELOAD ----------------------------
    // Use page.goto("/assessment/") instead of page.reload() to simulate the
    // customer "fresh-URL visit" flow that lands on welcome. AS8's URL routing
    // would otherwise preserve ?step= across page.reload() and auto-resume into
    // phase1, bypassing the welcome-list resume probe below.
    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await page
      .locator("#assessment-app")
      .getByRole("heading", { name: "Governance Readiness Assessment" })
      .waitFor({ timeout: 15_000 });

    // Welcome list shows the imported assessment as resumable.
    const resumeBtn = page.getByRole("button", {
      name: "Resume " + (exported.assessmentName || "Untitled"),
    });
    await expect(resumeBtn).toHaveCount(1);

    // -- Phase 3: COLLISION PROBE --------------------------------------
    // Import a SECOND JSON whose assessmentId equals the existing one but
    // whose responses differ. Goal: prove the post-import state is the
    // new payload's responses verbatim — not a Frankenstein merge of the
    // two — and that the SPA does not silently corrupt either side.
    //
    // Observed SPA behaviour (assessment-app.js L1037-L1050, importState):
    //   - importingDifferent = (parsed.assessmentId !== this.state.assessmentId)
    //   - On a same-id collision, importingDifferent is FALSE, so the
    //     destructive-gate confirm() is NOT shown. The state is replaced
    //     wholesale by the validated/sanitised parsed payload — overrides
    //     and responses keys from the prior import are GONE in the new
    //     `clean` object (importState builds clean.responses fresh).
    //   - Net effect: deterministic full-overwrite, no merge, no prompt.
    //   - This is the documented "Same-id round-trip is not destructive"
    //     contract. A future change toward a merge strategy would have to
    //     update both the SPA comment and this spec's expectation.
    const collisionDir = join(tmpdir(), "fsi-agentgov-e2e");
    mkdirSync(collisionDir, { recursive: true });
    const collisionPath = join(collisionDir, "full-cco-collision.json");
    const collidingPayload = {
      ...exported,
      assessmentName: "Globex Financial — collision",
      updatedAt: "2026-02-01T00:00:00.000Z",
      responses: {
        // Different answer set from the first import.
        "1.1": { answer: "no", notes: "collision-1.1", evidenceRef: "" },
        "2.1": { answer: "yes", notes: "collision-2.1", evidenceRef: "" },
      },
    };
    writeFileSync(collisionPath, JSON.stringify(collidingPayload, null, 2));

    // Resume the original first so importState has `this.state` set.
    await resumeBtn.dispatchEvent("click");
    await page
      .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();

    // Trigger a second import. Since this.state has answered controls and
    // the parsed.assessmentId matches, importingDifferent is false → no
    // confirm() prompt is expected. We still keep the dialog handler in
    // place (set at top of test) for safety.
    const chooser2Promise = page.waitForEvent("filechooser");
    // Navigate back to welcome to re-trigger triggerImport. Use the
    // back-to-scoping → back-to-welcome path used elsewhere in the suite.
    await page.getByRole("button", { name: "Back to Scoping" }).dispatchEvent("click");
    await page.getByRole("heading", { name: "Assessment Scoping" }).waitFor();
    await page.getByRole("button", { name: "Back", exact: true }).dispatchEvent("click");
    await page
      .locator("#assessment-app")
      .getByRole("heading", { name: "Governance Readiness Assessment" })
      .waitFor();
    await page
      .getByRole("button", { name: "Resume or Import Saved Assessment" })
      .dispatchEvent("click");
    const chooser2 = await chooser2Promise;
    await chooser2.setFiles(collisionPath);

    await page
      .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();

    // Post-collision state: the per-id slot reflects the SECOND payload
    // exclusively. No keys from the original imported responses survive.
    const postCollision = await page.evaluate(
      ([k, id]) => {
        const raw = localStorage.getItem(k + "-data-" + id);
        return raw ? JSON.parse(raw) : null;
      },
      [STORAGE_KEY, importedId],
    );
    expect(postCollision, "per-id slot must still exist after collision").not.toBeNull();
    expect(postCollision.assessmentId).toBe(importedId);

    // Consistent single-source state — keys from the first import are gone.
    const responseKeys = Object.keys(postCollision.responses).sort();
    expect(responseKeys).toEqual(["1.1", "2.1"]);
    expect(postCollision.responses["1.1"].answer).toBe("no");
    expect(postCollision.responses["1.1"].notes).toBe("collision-1.1");
    expect(postCollision.responses["2.1"].answer).toBe("yes");

    // No Frankenstein: the discarded original keys (1.7, 1.4, 1.11, ...)
    // must NOT be present.
    expect(postCollision.responses["1.7"]).toBeUndefined();
    expect(postCollision.responses["1.4"]).toBeUndefined();
    expect(postCollision.responses["1.11"]).toBeUndefined();
  });
});
