/**
 * AS15d (F-SCALE-MISMATCH-01) — agenda export scoring-label correctness.
 *
 * Two independent scoring systems coexist in this repo:
 *   • SPA (assessment-app.js)     — self-assessed questionnaire, 0–100%
 *   • Python engine (score.py)    — telemetry-driven maturity, 0–4
 *
 * The agenda Markdown export previously dressed up the SPA's % score as a
 * fake "Overall maturity: 3.0 / 4" via `(pct / 100) * 4`, masking the
 * cross-system mismatch and giving leadership a number that didn't agree
 * with the engine reports.
 *
 * AS15d removes the fake conversion and labels the agenda's headline
 * honestly as a self-assessed % score, plus adds a "Score basis:"
 * disclaimer that explicitly tells the reader the SPA % and engine 0–4
 * are different dimensions.
 */
import { describe, it, expect } from "vitest";
import { bootApp } from "./_bootSpa.mjs";

async function buildAgendaWithAnswers(answers) {
  const { app } = await bootApp({ answerControls: answers });
  return { md: app._buildAgendaMarkdown(), app };
}

describe("agenda export — scale-mismatch labelling (AS15d)", () => {
  it("uses '**Self-assessed score:** N%' headline (no fake /4 conversion)", async () => {
    const { md } = await buildAgendaWithAnswers([
      { id: "1.1", answer: "yes" },
      { id: "1.2", answer: "no" },
    ]);
    expect(md).toMatch(/\*\*Self-assessed score:\*\* \d+%/);
  });

  it("does NOT contain '**Overall maturity:**' anywhere", async () => {
    // Retired in AS15d — falsely implied parity with engine's 0-4 scale.
    const { md } = await buildAgendaWithAnswers([
      { id: "1.1", answer: "yes" },
    ]);
    expect(md).not.toMatch(/\*\*Overall maturity:\*\*/i);
  });

  it("does NOT contain a fake `*4/100` conversion artifact (e.g. '/ 4' on the headline)", async () => {
    const { md } = await buildAgendaWithAnswers([
      { id: "1.1", answer: "yes" },
    ]);
    // Only inspect the headline line, not control-ID columns elsewhere
    // (control IDs like "1.4" can legitimately contain "/ 4" patterns).
    const headlineLine = md.split("\n").find(
      (l) => l.startsWith("**Self-assessed score:**"),
    );
    expect(headlineLine).toBeDefined();
    expect(headlineLine).not.toMatch(/\/ 4\b/);
  });

  it("includes a '**Score basis:**' disclaimer distinguishing SPA % from engine maturity", async () => {
    const { md } = await buildAgendaWithAnswers([
      { id: "1.1", answer: "yes" },
    ]);
    expect(md).toContain("**Score basis:**");
    // Disclaimer must mention BOTH dimensions and the not-comparable claim.
    expect(md).toMatch(/Self-assessed questionnaire score/);
    expect(md).toMatch(/Overall Maturity X \/ 4/);
    expect(md).toMatch(/not\s+directly comparable/);
  });

  it("disclaimer reports answered count separately from the headline score", async () => {
    // NB3 from rubber-duck: count and score must be visibly separate so
    // a reader doesn't read "X of Y answered" as the same number as the
    // headline %.
    const { md, app } = await buildAgendaWithAnswers([
      { id: "1.1", answer: "yes" },
      { id: "1.2", answer: "yes" },
      { id: "1.3", answer: "no" },
    ]);
    const totalCount = app.data.controls.length;
    expect(md).toContain("Controls answered: 3 of " + totalCount + ".");
  });

  it("emits 'n/a' (not a fake conversion) when overall score is unavailable", async () => {
    // No answers at all -> getOverallScore returns null -> headline must
    // fall back to "n/a" without inventing a 0.0 / 4 maturity.
    const { md } = await buildAgendaWithAnswers([]);
    expect(md).toMatch(/\*\*Self-assessed score:\*\* n\/a/);
    expect(md).not.toMatch(/\*\*Overall maturity:\*\*/);
  });

  it("non-timestamp body is deterministic for fixed answers (NB2: skip the Generated line)", async () => {
    // NB2 from rubber-duck: full string-equality is defeated by the
    // `**Generated:**` ISO timestamp. Strip that line, then require
    // structural equality across two consecutive runs of the same
    // answers — a surface-area-bounded determinism check.
    const stripGenerated = (s) =>
      s.split("\n").filter((l) => !l.startsWith("**Generated:**")).join("\n");
    const answers = [
      { id: "1.1", answer: "yes" },
      { id: "1.2", answer: "partial" },
      { id: "2.1", answer: "no" },
    ];
    const a = await buildAgendaWithAnswers(answers);
    const b = await buildAgendaWithAnswers(answers);
    expect(stripGenerated(a.md)).toBe(stripGenerated(b.md));
  });
});
