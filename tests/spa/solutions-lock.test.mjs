import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const LOCK_PATH = join(here, "..", "..", "assessment", "data", "solutions-lock.json");

describe("assessment/data/solutions-lock.json", () => {
  const lock = JSON.parse(readFileSync(LOCK_PATH, "utf8"));

  it("declares schemaVersion starting with '1.4.' or '1.5.'", () => {
    expect(typeof lock.schemaVersion).toBe("string");
    const sv = lock.schemaVersion;
    const accepted = sv.startsWith("1.4.") || sv.startsWith("1.5.");
    expect(accepted, `unexpected schemaVersion ${sv}; expected 1.4.x or 1.5.x`).toBe(true);
  });

  it("solutions field is an object (may be empty placeholder)", () => {
    expect(lock.solutions).not.toBeNull();
    expect(typeof lock.solutions).toBe("object");
    expect(Array.isArray(lock.solutions)).toBe(false);
  });

  it("missing-solution lookup returns undefined gracefully", () => {
    const sol = lock.solutions["does-not-exist-xyz"];
    expect(sol).toBeUndefined();
  });

  it("any present solution entry is an object (forward-compat shape check)", () => {
    for (const [key, value] of Object.entries(lock.solutions)) {
      expect(key, "solution key is non-empty").toMatch(/^[a-z0-9][a-z0-9-]*$/);
      expect(typeof value, `solution ${key} is object`).toBe("object");
      expect(value).not.toBeNull();
    }
  });
});
