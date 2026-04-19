import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const MANIFEST_PATH = join(here, "..", "..", "assessment", "manifest", "controls.json");

describe("manifest/controls.json", () => {
  const manifest = JSON.parse(readFileSync(MANIFEST_PATH, "utf8"));

  it("contains exactly 78 controls", () => {
    expect(Array.isArray(manifest)).toBe(true);
    expect(manifest.length).toBe(78);
  });

  it("every control has id, title, pillar, and a solutions array", () => {
    for (const c of manifest) {
      expect(typeof c.id, `id for ${JSON.stringify(c).slice(0, 80)}`).toBe("string");
      expect(c.id).toMatch(/^[1-4]\.\d+$/);
      expect(typeof c.title, `title for ${c.id}`).toBe("string");
      expect(c.title.length).toBeGreaterThan(0);
      expect([1, 2, 3, 4]).toContain(c.pillar);
      expect(Array.isArray(c.solutions), `solutions for ${c.id}`).toBe(true);
    }
  });

  it("every solutions[] entry is a kebab-case slug", () => {
    const slug = /^[a-z0-9][a-z0-9-]*$/;
    for (const c of manifest) {
      for (const s of c.solutions) {
        expect(typeof s, `solution in ${c.id}`).toBe("string");
        expect(s, `solution slug in ${c.id}`).toMatch(slug);
      }
    }
  });

  it("every control has zonesApplicable as a non-empty subset of [1,2,3]", () => {
    for (const c of manifest) {
      expect(Array.isArray(c.zonesApplicable), `zonesApplicable for ${c.id}`).toBe(true);
      expect(c.zonesApplicable.length).toBeGreaterThan(0);
      for (const z of c.zonesApplicable) {
        expect([1, 2, 3]).toContain(z);
      }
      // No duplicates
      expect(new Set(c.zonesApplicable).size).toBe(c.zonesApplicable.length);
    }
  });
});
