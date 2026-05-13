import { test } from "@playwright/test";
import { readFileSync } from "node:fs";
import {
  clearPageStorage,
  clickThroughPhase1,
  expect,
  expectDownload,
  freezeTime,
  loadPersona,
  navClick,
  seedScoping,
} from "./_harness.mjs";

/**
 * 06 — Export JSON schema + filename + freezeTime determinism (E2E regression)
 *
 * Sibling to 11-import-roundtrip but with stricter schema assertions on
 * the export envelope, filename pattern, and `_metadata.exportedAt`
 * determinism via freezeTime.
 *
 * SPA contract (assessment-app.js exportJSON, ~L3790):
 *   filename = sanitize(state.assessmentName || "assessment") + ".json"
 *   where assessmentName = `<org> — <YYYY-MM-DD>` (Begin Assessment).
 *   The sanitize step replaces every char outside [a-zA-Z0-9-_] with "-",
 *   so "Acme Bank — 2026-01-15" becomes "Acme-Bank---2026-01-15".
 *
 * Envelope contract (additive — original state keys remain at top):
 *   _metadata          { exportSchemaVersion:1, schemaType:"full",
 *                        frameworkVersion:"1.6.2", manifestSchemaVersion,
 *                        exportedAt, exportedBy }
 *   _computedScores    { overall, perPillar:{1..4}, perControl:{...} }
 *   assessmentStatus   "draft" | "in-progress" | "final"
 *   ...this.state      (responses, scoping, assessmentId, assessmentName, ...)
 */
test.describe("export JSON @regression", () => {
  test("envelope schema, filename pattern, deterministic exportedAt @regression", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));
    // Freeze BEFORE navigation so both assessmentName ("<org> — <date>")
    // and _metadata.exportedAt resolve to the frozen instant.
    await freezeTime(page, "2026-01-15T12:00:00.000Z");

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    const persona = loadPersona("minimal-ciso");
    await seedScoping(page, persona);
    await clickThroughPhase1(page, persona);
    await navClick(page, "View Results");
    await page.locator(".ag-score-big").first().waitFor();

    // Navigate to Export and capture the JSON download.
    await navClick(page, "Export Results");
    await page.getByRole("heading", { name: "Export Results" }).waitFor();
    const { suggestedName, path } = await expectDownload(page, async () => {
      await navClick(page, /Export as Full Assessment/);
    });

    // Filename pattern: assessmentName sanitized + ".json".
    // assessmentName = "Acme Bank — 2026-01-15" (em-dash) →
    //   sanitize → "Acme-Bank---2026-01-15.json".
    expect(suggestedName).toBe("Acme-Bank---2026-01-15.json");

    const rawText = readFileSync(path, "utf8");
    const parsed = JSON.parse(rawText); // throws if invalid JSON

    // _metadata block — exportSchemaVersion is numeric (per
    // EXPORT_SCHEMA_VERSION = 1), schemaType "full", frameworkVersion
    // matches the SPA constant.
    expect(parsed._metadata).toBeTruthy();
    expect(parsed._metadata.schemaType).toBe("full");
    expect(parsed._metadata.exportSchemaVersion).toBe(1);
    expect(parsed._metadata.frameworkVersion).toBe("1.6.2");
    // freezeTime determinism: exportedAt is the frozen instant.
    expect(parsed._metadata.exportedAt).toBe("2026-01-15T12:00:00.000Z");
    expect(parsed._metadata.exportedBy).toBe("Jane Doe");

    // _computedScores — overall is a number (or null when no answers).
    expect(parsed._computedScores).toBeTruthy();
    expect(typeof parsed._computedScores.overall === "number"
      || parsed._computedScores.overall === null).toBe(true);
    expect(parsed._computedScores.perPillar).toBeTruthy();
    for (const p of [1, 2, 3, 4]) {
      expect(parsed._computedScores.perPillar).toHaveProperty(String(p));
    }

    // assessmentStatus is one of the allowed enum values.
    expect(["draft", "in-progress", "final"]).toContain(parsed.assessmentStatus);

    // Top-level state keys (per importer compatibility contract).
    expect(parsed.assessmentId).toBeTruthy();
    expect(parsed.assessmentName).toBe("Acme Bank — 2026-01-15");
    expect(parsed.scoping).toBeTruthy();
    expect(parsed.scoping.organizationName).toBe("Acme Bank");
    expect(parsed.scoping.assessorName).toBe("Jane Doe");
    expect(parsed.scoping.institutionType).toBe("bank");
    expect(parsed.scoping.zones).toEqual([1]);
    expect(parsed.responses).toBeTruthy();
    expect(parsed.responses["1.4"].answer).toBe("yes");
    expect(parsed.responses["1.5"].answer).toBe("partial");
    expect(parsed.responses["1.7"].answer).toBe("no");
    expect(parsed.responses["1.11"].answer).toBe("yes");
    expect(parsed.responses["2.1"].answer).toBe("partial");
  });
});
