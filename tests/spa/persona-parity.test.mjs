/**
 * Persona round-trip parity tests.
 *
 * For each persona fixture under tests/e2e/fixtures/personas/*.json:
 *   1. Boot the SPA
 *   2. Apply the persona's recorded answers
 *   3. Call exportJSON()
 *   4. Assert the resulting _computedScores matches the persona's recorded
 *      scores within ±0.5 (round-trip parity)
 *
 * Personas haven't been generated yet (Phase C scaffold); this spec activates
 * once `scripts/update-personas.mjs` lands and writes the fixtures.
 */
import { describe, it, expect, beforeAll } from "vitest";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { bootApp } from "./_bootSpa.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const PERSONAS_DIR = join(here, "..", "e2e", "fixtures", "personas");

const haveFixtures = existsSync(PERSONAS_DIR);
const personaFiles = haveFixtures
  ? readdirSync(PERSONAS_DIR).filter(f => f.endsWith(".json"))
  : [];

describe("persona round-trip parity", () => {
  if (!haveFixtures || personaFiles.length === 0) {
    it.skip("personas not yet generated; run scripts/update-personas.mjs after Phase C scaffold lands", () => {});
    return;
  }

  for (const file of personaFiles) {
    describe(file, () => {
      let persona, envelope;

      beforeAll(async () => {
        persona = JSON.parse(readFileSync(join(PERSONAS_DIR, file), "utf8"));
        const answerControls = Object.entries(persona.responses || {})
          .filter(([, r]) => r && r.answer)
          .map(([id, r]) => ({ id, answer: r.answer }));
        const { app, captured } = await bootApp({ answerControls });
        if (persona.scoping) Object.assign(app.state.scoping, persona.scoping);
        app.exportJSON();
        envelope = JSON.parse(captured[captured.length - 1].blob.__text);
      });

      it("overall score matches recorded value within ±0.5", () => {
        if (persona.expectedScores?.overall == null) return;
        expect(Math.abs(envelope._computedScores.overall - persona.expectedScores.overall))
          .toBeLessThanOrEqual(0.5);
      });

      it("per-pillar scores match recorded values within ±0.5", () => {
        const expected = persona.expectedScores?.perPillar;
        if (!expected) return;
        for (const k of Object.keys(expected)) {
          const got = Array.isArray(envelope._computedScores.perPillar)
            ? envelope._computedScores.perPillar.find(p => String(p.pillar) === String(k))?.score
            : envelope._computedScores.perPillar[k];
          if (expected[k] == null || got == null) continue;
          expect(Math.abs(got - expected[k])).toBeLessThanOrEqual(0.5);
        }
      });
    });
  }
});
