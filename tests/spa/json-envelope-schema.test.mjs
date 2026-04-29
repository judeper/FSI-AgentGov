/**
 * JSON envelope schema contract tests.
 *
 * Validates the v1.4.1 export-JSON envelope shape. Uses ajv if installed for
 * strict JSON-schema validation; otherwise falls back to hand-rolled
 * assertions (which cover the same constraints).
 */
import { describe, it, expect, beforeAll } from "vitest";
import { bootApp } from "./_bootSpa.mjs";

let ajvAvailable = false;
let Ajv;
try {
  Ajv = (await import(/* @vite-ignore */ "ajv")).default;
  ajvAvailable = true;
} catch {
  ajvAvailable = false;
}

const envelopeSchema = {
  type: "object",
  required: ["_metadata", "_computedScores", "assessmentStatus", "assessmentId", "responses", "scoping", "completedSteps"],
  properties: {
    _metadata: {
      type: "object",
      required: ["frameworkVersion", "exportedAt"],
      properties: {
        frameworkVersion: { type: "string", minLength: 1 },
        exportedAt: { type: "string", pattern: "^\\d{4}-\\d{2}-\\d{2}T" },
      },
    },
    _computedScores: {
      type: "object",
      required: ["overall", "perPillar", "perControl"],
      properties: {
        perPillar: { type: "object" },
        perControl: { type: "object" },
      },
    },
    assessmentStatus: { type: "string", enum: ["draft", "in-progress", "final"] },
  },
};

describe("export-JSON envelope schema", () => {
  let envelope;

  beforeAll(async () => {
    const { app, captured } = await bootApp({
      answerControls: [
        { id: "1.1", answer: "yes" },
        { id: "1.2", answer: "no" },
        { id: "2.1", answer: "partial" },
      ],
    });
    app.exportJSON();
    envelope = JSON.parse(captured[captured.length - 1].blob.__text);
  });

  it("validates against the envelope JSON schema (ajv if available)", () => {
    if (!ajvAvailable) {
      console.warn("ajv not installed — falling back to hand-rolled assertions");
      return;
    }
    const ajv = new Ajv({ allErrors: true, strict: false });
    const validate = ajv.compile(envelopeSchema);
    const ok = validate(envelope);
    if (!ok) console.error(validate.errors);
    expect(ok).toBe(true);
  });

  it("_metadata.frameworkVersion is a non-empty string", () => {
    expect(typeof envelope._metadata.frameworkVersion).toBe("string");
    expect(envelope._metadata.frameworkVersion.length).toBeGreaterThan(0);
  });

  it("_metadata.exportedAt is ISO-8601", () => {
    expect(envelope._metadata.exportedAt).toMatch(
      /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})$/
    );
    const d = new Date(envelope._metadata.exportedAt);
    expect(Number.isFinite(d.getTime())).toBe(true);
  });

  it("_metadata.frameworkVersion matches semver-like \\d+.\\d+.\\d+", () => {
    expect(envelope._metadata.frameworkVersion).toMatch(/^\d+\.\d+\.\d+/);
  });

  it("_computedScores.overall is null or a number 0-100", () => {
    const o = envelope._computedScores.overall;
    if (o !== null) {
      expect(typeof o).toBe("number");
      expect(o).toBeGreaterThanOrEqual(0);
      expect(o).toBeLessThanOrEqual(100);
    }
  });

  it("_computedScores.perPillar covers pillars 1-4", () => {
    const pp = envelope._computedScores.perPillar;
    // The current SPA emits an OBJECT keyed "1".."4". The roadmap discusses
    // an alternative array form with {pillar, score} entries; accept either.
    if (Array.isArray(pp)) {
      expect(pp).toHaveLength(4);
      pp.forEach(entry => {
        expect(entry).toHaveProperty("pillar");
        expect(entry).toHaveProperty("score");
      });
    } else {
      expect(Object.keys(pp).sort()).toEqual(["1", "2", "3", "4"]);
    }
  });

  it("_computedScores.perControl is an object keyed by control id", () => {
    expect(typeof envelope._computedScores.perControl).toBe("object");
    expect(Array.isArray(envelope._computedScores.perControl)).toBe(false);
    expect(envelope._computedScores.perControl).toHaveProperty("1.1");
    expect(envelope._computedScores.perControl).toHaveProperty("1.2");
  });

  it("assessmentStatus is one of {draft, in-progress, final}", () => {
    expect(["draft", "in-progress", "final"]).toContain(envelope.assessmentStatus);
  });

  it("preserves all original state keys at top level (importer back-compat)", () => {
    for (const key of [
      "assessmentId", "assessmentName", "createdAt", "updatedAt",
      "scoping", "responses", "drilldown", "completedSteps",
    ]) {
      expect(envelope, `missing top-level key: ${key}`).toHaveProperty(key);
    }
  });
});
