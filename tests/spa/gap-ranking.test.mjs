import { describe, it } from "vitest";

// E7 (priority starter set) is shipped — see spa-v14-summary.md — but the
// _topGapControls(state, limit) ranking helper described in the test plan
// does NOT exist in docs/javascripts/assessment-app.js as of v1.4 SPA RC.
// Skipping these tests until the gap-ranking helper lands in a follow-up.
describe.skip("_topGapControls (gap ranking)", () => {
  it("ranks 'no' answers first by priority asc, then 'partial', capped at limit", () => {
    // TODO: enable when assessment-app.js exposes _topGapControls.
  });
});
