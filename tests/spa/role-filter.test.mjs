import { describe, it, expect, beforeAll } from "vitest";
import { loadSpa } from "./_loadSpa.mjs";

let SPA;
let app;

beforeAll(() => {
  SPA = loadSpa();
  app = new SPA.AssessmentApp(document.createElement("div"));
});

describe("controlMatchesRoleFilter", () => {
  it("matches every control when filter is empty", () => {
    expect(app.controlMatchesRoleFilter({ roles: ["Anyone"] }, "")).toBe(true);
    expect(app.controlMatchesRoleFilter({ roles: [] }, "")).toBe(true);
  });

  it("returns false when control has no roles and filter is set", () => {
    expect(app.controlMatchesRoleFilter({}, "Power Platform Admin")).toBe(false);
  });

  it("matches by exact role string", () => {
    const ctrl = { roles: ["Power Platform Admin", "Compliance Officer"] };
    expect(app.controlMatchesRoleFilter(ctrl, "Power Platform Admin")).toBe(true);
  });

  it("matches when role has a parenthetical qualifier (prefix)", () => {
    const ctrl = { manifestRoles: ["AI Administrator (preferred — MC1041454, Mar 2025)", "Compliance Officer"] };
    expect(app.controlMatchesRoleFilter(ctrl, "AI Administrator")).toBe(true);
  });

  it("matches case-insensitively", () => {
    const ctrl = { roles: ["Power Platform Admin"] };
    expect(app.controlMatchesRoleFilter(ctrl, "power platform admin")).toBe(true);
    expect(app.controlMatchesRoleFilter(ctrl, "POWER PLATFORM ADMIN")).toBe(true);
  });

  it("matches by substring (per-environment qualifier)", () => {
    const ctrl = { manifestRoles: ["Dataverse System Admin (per-environment)"] };
    expect(app.controlMatchesRoleFilter(ctrl, "Dataverse System Admin")).toBe(true);
  });

  it("returns false when no role contains the filter", () => {
    const ctrl = { roles: ["Power Platform Admin", "Compliance Officer"] };
    expect(app.controlMatchesRoleFilter(ctrl, "SharePoint Admin")).toBe(false);
  });

  it("prefers manifestRoles when both manifestRoles and roles are present", () => {
    const ctrl = {
      manifestRoles: ["SharePoint Admin"],
      roles: ["Other Role"],
      assignedRoles: ["Yet Another"],
    };
    expect(app.controlMatchesRoleFilter(ctrl, "SharePoint Admin")).toBe(true);
    expect(app.controlMatchesRoleFilter(ctrl, "Other Role")).toBe(false);
  });

  it("falls back to assignedRoles when no roles/manifestRoles", () => {
    const ctrl = { assignedRoles: ["Entra Global Admin"] };
    expect(app.controlMatchesRoleFilter(ctrl, "Entra Global Admin")).toBe(true);
  });
});
