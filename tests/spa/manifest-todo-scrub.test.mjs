/**
 * U-022 regression — manifest TODO placeholders must not leak into the
 * customer-facing SPA after mergeManifestIntoControls().
 *
 * The manifest at assessment/manifest/controls.json carries "TODO:"
 * authoring placeholders in priority / yesBar / partialBar / noBar and in
 * facilitatorNotes.{ask,followUp} for controls whose facilitator content
 * has not yet been authored. The SPA must scrub those placeholders at
 * merge time so the drawer, agenda exports, and any other consumer never
 * render the literal "TODO:" text to customers.
 */
import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { bootApp } from "./_bootSpa.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const MANIFEST_PATH = join(here, "..", "..", "assessment", "manifest", "controls.json");

function isTodo(value) {
  return typeof value === "string" && value.trim().startsWith("TODO:");
}

describe("U-022 — manifest TODO placeholders are scrubbed before reaching the SPA", () => {
  it("source manifest still carries TODO placeholders (authoring backlog intact)", () => {
    const manifest = JSON.parse(readFileSync(MANIFEST_PATH, "utf8"));
    const anyTodo = manifest.some(
      (c) =>
        isTodo(c.priority) ||
        isTodo(c.yesBar) ||
        isTodo(c.partialBar) ||
        isTodo(c.noBar) ||
        (c.facilitatorNotes && (isTodo(c.facilitatorNotes.ask) || isTodo(c.facilitatorNotes.followUp)))
    );
    // If this assertion ever flips to false it means the authoring backlog
    // has been fully drained — at that point this whole spec can be retired.
    expect(anyTodo).toBe(true);
  });

  it("merged controls expose no TODO text in yesBar/partialBar/noBar", async () => {
    const { app } = await bootApp({});
    expect(Array.isArray(app.data.controls)).toBe(true);
    for (const c of app.data.controls) {
      expect(isTodo(c.yesBar), `yesBar leaked TODO for ${c.id}: ${c.yesBar}`).toBe(false);
      expect(isTodo(c.partialBar), `partialBar leaked TODO for ${c.id}: ${c.partialBar}`).toBe(false);
      expect(isTodo(c.noBar), `noBar leaked TODO for ${c.id}: ${c.noBar}`).toBe(false);
    }
  });

  it("merged controls expose no TODO text in facilitatorNotes.ask / followUp", async () => {
    const { app } = await bootApp({});
    for (const c of app.data.controls) {
      const fn = c.facilitatorNotes || {};
      expect(isTodo(fn.ask), `facilitatorNotes.ask leaked TODO for ${c.id}: ${fn.ask}`).toBe(false);
      expect(isTodo(fn.followUp), `facilitatorNotes.followUp leaked TODO for ${c.id}: ${fn.followUp}`).toBe(false);
    }
  });

  it("merged controls never expose a TODO priority", async () => {
    const { app } = await bootApp({});
    for (const c of app.data.controls) {
      expect(isTodo(c.manifestPriority), `manifestPriority leaked TODO for ${c.id}`).toBe(false);
      // Authored priorities (when present) must match the documented vocabulary.
      if (typeof c.manifestPriority === "string" && c.manifestPriority) {
        expect(["critical", "high", "medium", "low"]).toContain(c.manifestPriority);
      }
    }
  });

  it("unauthored bar fields collapse to empty strings (SPA truthy guards skip them)", async () => {
    const { app, manifest } = await bootApp({});
    const todoByIdField = new Map();
    for (const m of manifest) {
      todoByIdField.set(m.id, {
        yesBar: isTodo(m.yesBar),
        partialBar: isTodo(m.partialBar),
        noBar: isTodo(m.noBar),
      });
    }
    for (const c of app.data.controls) {
      const flags = todoByIdField.get(c.id) || {};
      if (flags.yesBar) expect(c.yesBar).toBe("");
      if (flags.partialBar) expect(c.partialBar).toBe("");
      if (flags.noBar) expect(c.noBar).toBe("");
    }
  });
});
