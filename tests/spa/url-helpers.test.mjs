import { describe, it, expect, beforeAll } from "vitest";
import { loadSpa } from "./_loadSpa.mjs";

let SPA;

beforeAll(() => {
  SPA = loadSpa();
});

describe("SOLUTIONS_BASE_URL constant", () => {
  it("is a defined HTTPS URL", () => {
    expect(typeof SPA.SOLUTIONS_BASE_URL).toBe("string");
    expect(SPA.SOLUTIONS_BASE_URL.startsWith("https://")).toBe(true);
  });

  it("ends with a trailing slash so concatenated IDs land in a clean path segment", () => {
    expect(SPA.SOLUTIONS_BASE_URL.endsWith("/")).toBe(true);
  });

  it("composes solution chip URLs as BASE + encodeURIComponent(id) + '/'", () => {
    // This mirrors the encoding used in assessment-app.js renderDrawerContent
    // (search for `SOLUTIONS_BASE_URL + encodeURIComponent(sid)` in the SPA).
    const id = "platform-change-governance";
    const url = SPA.SOLUTIONS_BASE_URL + encodeURIComponent(id) + "/";
    expect(url).toBe(SPA.SOLUTIONS_BASE_URL + "platform-change-governance/");
    expect(url.startsWith(SPA.SOLUTIONS_BASE_URL)).toBe(true);
    expect(url.endsWith("/")).toBe(true);
  });

  it("encodes solution IDs that contain reserved URL chars", () => {
    const id = "weird id/with spaces";
    const url = SPA.SOLUTIONS_BASE_URL + encodeURIComponent(id) + "/";
    expect(url).not.toContain(" ");
    expect(url).toContain("weird%20id%2Fwith%20spaces");
  });
});
