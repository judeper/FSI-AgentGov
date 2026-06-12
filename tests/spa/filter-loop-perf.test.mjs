/**
 * Filter-loop performance guardrail.
 *
 * Boots the SPA, populates state with all 79 controls answered, then calls
 * getGapControls() 100 times in a loop. Asserts wall time < 500ms — generous
 * enough that the current N²-ish behavior on 79 controls passes, but tight
 * enough that a future regression (or removal of spa-fix-perf-loop) trips.
 */
import { describe, it, expect } from "vitest";
import { bootApp } from "./_bootSpa.mjs";

describe("getGapControls() performance guardrail", () => {
  it("100 iterations on 79 fully-answered controls completes in < 500ms", async () => {
    const { app } = await bootApp();
    // Answer every control with a mix of answers so most/all become "gaps".
    const answers = ["yes", "partial", "no", "yes", "no"];
    app.data.controls.forEach((c, i) => {
      app.state.responses[c.id] = { answer: answers[i % answers.length], notes: "", evidenceRef: "" };
    });
    // Apply a roleFilter that excludes ~30+ controls (per spec). The current
    // SPA reads roleFilter from state; even if no controls match the filter
    // string, getGapControls still returns a useful set so the loop is
    // meaningful.
    app.state.roleFilter = "Power Platform Admin";

    const t0 = Date.now();
    let lastLen = 0;
    for (let i = 0; i < 100; i++) {
      lastLen = app.getGapControls().length;
    }
    const elapsed = Date.now() - t0;

    expect(lastLen).toBeGreaterThan(0);
    expect(elapsed, `getGapControls x100 took ${elapsed}ms`).toBeLessThan(500);
  });
});
