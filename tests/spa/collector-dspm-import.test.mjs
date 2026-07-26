import { describe, expect, it } from "vitest";
import { bootSPA } from "./_bootSpa.mjs";

async function makeApp(existingAnswer) {
  const { window } = bootSPA();
  const app = new window.AssessmentApp(window.document.getElementById("ag-app"));
  await app.loadData();
  app.state = app.newState();
  if (existingAnswer) {
    app.state.responses["1.6"] = {
      answer: existingAnswer,
      notes: "Reviewer note",
      evidenceRef: "manual",
    };
  }
  return { app, window };
}

function rawDspm(dspmForAi) {
  return {
    _metadata: { collector: "Collect-Purview" },
    dspmForAi,
  };
}

function canonicalDspm(overrides = {}) {
  return {
    CollectionStatus: "collected",
    Detected: true,
    PolicyCount: 1,
    DiagnosticPolicyCount: 1,
    PolicyDiagnostics: [{ Qualifies: true }],
    ...overrides,
  };
}

describe("raw Purview DSPM collector import contract", () => {
  it("imports canonical positive evidence as yes", async () => {
    const { app } = await makeApp();

    const result = app.applyCollectorPayload(rawDspm(canonicalDspm()), "purview.json");

    expect(result).toEqual({ imported: 1, skipped: 0 });
    expect(app.state.responses["1.6"].answer).toBe("yes");
  });

  it("imports canonical collected negative evidence as no", async () => {
    const { app } = await makeApp();
    const evidence = canonicalDspm({
      Detected: false,
      PolicyCount: 0,
      DiagnosticPolicyCount: 1,
      PolicyDiagnostics: [{ Qualifies: false }],
    });

    const result = app.applyCollectorPayload(rawDspm(evidence), "purview.json");

    expect(result).toEqual({ imported: 1, skipped: 0 });
    expect(app.state.responses["1.6"].answer).toBe("no");
  });

  it.each([undefined, null, "", "partial", "failed", "unavailable", "error", "unknown"])(
    "skips %s collection status and preserves the existing answer",
    async (CollectionStatus) => {
      const { app } = await makeApp("partial");

      const result = app.applyCollectorPayload(
        rawDspm(canonicalDspm({ CollectionStatus })),
        "purview.json",
      );

      expect(result).toEqual({ imported: 0, skipped: 1 });
      expect(app.state.responses["1.6"]).toEqual({
        answer: "partial",
        notes: "Reviewer note",
        evidenceRef: "manual",
      });
    },
  );

  it("skips legacy three-field positive evidence", async () => {
    const { app } = await makeApp("no");

    const result = app.applyCollectorPayload(rawDspm({
      Detected: true,
      PolicyCount: 1,
      PolicyNames: ["Legacy substring match"],
    }), "purview.json");

    expect(result).toEqual({ imported: 0, skipped: 1 });
    expect(app.state.responses["1.6"].answer).toBe("no");
  });

  it.each([
    ["string policy count", { PolicyCount: "1" }],
    ["string diagnostic count", { DiagnosticPolicyCount: "1" }],
    ["truthy detected string", { Detected: "true" }],
    ["false-looking detected string", {
      Detected: "false",
      PolicyCount: 0,
      PolicyDiagnostics: [{ Qualifies: false }],
    }],
    ["negative policy count", { PolicyCount: -1 }],
    ["diagnostic count mismatch", { DiagnosticPolicyCount: 2 }],
    ["detected/count mismatch", {
      Detected: true,
      PolicyCount: 0,
      DiagnosticPolicyCount: 0,
      PolicyDiagnostics: [],
    }],
    ["qualifying count mismatch", {
      PolicyCount: 2,
      DiagnosticPolicyCount: 2,
      PolicyDiagnostics: [{ Qualifies: true }, { Qualifies: false }],
    }],
    ["malformed diagnostics", { PolicyDiagnostics: [null] }],
  ])("skips malformed or inconsistent evidence: %s", async (_label, overrides) => {
    const { app } = await makeApp("partial");

    const result = app.applyCollectorPayload(
      rawDspm(canonicalDspm(overrides)),
      "purview.json",
    );

    expect(result).toEqual({ imported: 0, skipped: 1 });
    expect(app.state.responses["1.6"].answer).toBe("partial");
  });

  it("keeps generic status mapping unchanged for non-DSPM score entries", async () => {
    const { app } = await makeApp();

    const result = app.applyCollectorPayload({
      controls: [{ id: "1.5", status: "pass" }],
    }, "scores.json");

    expect(result).toEqual({ imported: 1, skipped: 0 });
    expect(app.state.responses["1.5"].answer).toBe("yes");
  });

  it("summarizes the canonical Note as one safe, length-limited line", async () => {
    const { app, window } = await makeApp();
    const note = "  First line\r\nsecond\tline <script>window.pwned=true</script>  " +
      "x".repeat(5000);

    app.applyCollectorPayload(
      rawDspm(canonicalDspm({ Note: note })),
      "purview.json",
    );
    app.step = "phase1";
    app.render();

    const importedNote = app.state.responses["1.6"].notes;
    expect(importedNote.startsWith(
      "[Imported]: First line second line <script>window.pwned=true</script>",
    )).toBe(true);
    expect(importedNote).not.toMatch(/[\r\n\t]/);
    expect(importedNote.length).toBe(4000);
    expect(window.pwned).toBeUndefined();
    expect(window.document.querySelectorAll("script")).toHaveLength(0);
  });
});
