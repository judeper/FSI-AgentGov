import { describe, it, expect } from "vitest";
import { bootSPA } from "./_bootSpa.mjs";

const STORAGE_KEY = "fsi-agentgov-assessment";

async function makeApp() {
  const { window } = bootSPA();
  const app = new window.AssessmentApp(window.document.getElementById("ag-app"));
  await app.loadData();
  return { app, window };
}

describe("answer selector + resume naming contracts", () => {
  it("renders stable data-answer buttons with descriptive names and aria-pressed state", async () => {
    const { app, window } = await makeApp();
    app.state = app.newState();
    app.state.scoping.organizationName = "Acme Bank";
    app.state.scoping.assessorName = "Tester";
    app.state.scoping.zones = [1, 2, 3];
    app.step = "phase1";
    app.render();

    const card = window.document.querySelector('[data-control-id="1.1"]');
    expect(card).toBeTruthy();

    const yesBtn = card.querySelector('button.ag-answer-btn[data-answer="yes"]');
    const noBtn = card.querySelector('button.ag-answer-btn[data-answer="no"]');
    expect(yesBtn).toBeTruthy();
    expect(noBtn).toBeTruthy();
    expect(yesBtn.textContent).toBe("Yes");
    expect(yesBtn.getAttribute("aria-label")).toMatch(/^Rate control 1\.1 .* — Yes$/);

    yesBtn.click();
    expect(yesBtn.getAttribute("aria-pressed")).toBe("true");
    expect(noBtn.getAttribute("aria-pressed")).toBe("false");
  });

  it("keeps banner resume name distinct from saved-list resume actions", async () => {
    const { app, window } = await makeApp();
    const saved = [
      {
        id: "id-older",
        name: "Older Bank — 2026-01-14",
        updatedAt: "2026-01-14T10:00:00.000Z",
        progress: 30,
      },
      {
        id: "id-newest",
        name: "Newest Bank — 2026-01-15",
        updatedAt: "2026-01-15T10:00:00.000Z",
        progress: 70,
      },
    ];
    window.localStorage.setItem(STORAGE_KEY + "-list", JSON.stringify(saved));

    app.state = app.newState();
    app.step = "welcome";
    app.render();

    const bannerBtn = window.document.querySelector(".ag-resume-banner button");
    expect(bannerBtn).toBeTruthy();
    expect(bannerBtn.getAttribute("aria-label"))
      .toBe("Resume most recent assessment: Newest Bank — 2026-01-15");

    const listLabels = Array.from(
      window.document.querySelectorAll(".ag-saved-list button.ag-btn-primary"),
    ).map((b) => b.getAttribute("aria-label"));
    expect(listLabels).toContain("Resume Newest Bank — 2026-01-15");
    expect(listLabels).toContain("Resume Older Bank — 2026-01-14");
    expect(listLabels).not.toContain(
      "Resume most recent assessment: Newest Bank — 2026-01-15",
    );
  });
});
