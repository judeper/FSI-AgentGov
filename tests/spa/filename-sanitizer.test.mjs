/**
 * AS18b (F-RUNTIME-EXPORT-FILENAME-UNICODE-STRIPPED-01) — export filename
 * sanitizer correctness.
 *
 * Background: the SPA's three export paths (JSON, CSV, XLSX) and the agenda
 * MD export build their download filenames from `state.assessmentName` (which
 * the SPA autofills as `${organizationName} — ${ISODate}` at line 2336 of
 * assessment-app.js when the user leaves it blank). The legacy regex
 * `/[^a-zA-Z0-9-_]/g → "-"` was ASCII-only, which:
 *
 *   1. Mojibake'd Unicode org names ("Société Générale" → "Soci-t--G-n-rale",
 *      العربية → "-------", 中文 → "--", 🏦 → "--").
 *   2. Stripped the em-dash autofill separator, producing
 *      "Acme-Corp---2026-05-15.json" (triple-dash artifact).
 *   3. Was open to CVE-2021-42574 ("Trojan Source") class attacks: an org
 *      name containing U+202E (RIGHT-TO-LEFT OVERRIDE) like
 *      "invoice<U+202E>gpj.exe" passes the legacy filter (the override char
 *      is non-alnum so it gets replaced with "-") — but the new sanitizer
 *      explicitly enumerates bidi overrides for defense-in-depth and
 *      correctness when other unsafe ranges are added.
 *
 * The new sanitizer (`_sanitizeFilenameStem`) preserves Unicode letters
 * while stripping Windows-illegal chars, control chars (incl. U+007F DEL),
 * bidi-override marks (CVE-2021-42574), path separators, and shell metas;
 * collapses whitespace + multi-dash; trims leading/trailing dashes + dots;
 * and guards against Windows reserved device names (CON, NUL, COM1-9,
 * LPT1-9) by prefixing with underscore. The reserved-name guard catches
 * BOTH the bare form ("CON") AND the with-extension form ("CON.txt") because
 * Windows refuses to open either (see Microsoft's filesystem naming docs).
 */
import { describe, it, expect, beforeAll } from "vitest";
import { loadSpa } from "./_loadSpa.mjs";

let SPA;

beforeAll(() => {
  SPA = loadSpa();
});

describe("_sanitizeFilenameStem (AS18b)", () => {
  it("is exported from the SPA module so vitest can import it", () => {
    expect(typeof SPA._sanitizeFilenameStem).toBe("function");
  });

  describe("Unicode preservation", () => {
    it("preserves Latin-1 supplement (Société Générale)", () => {
      expect(SPA._sanitizeFilenameStem("Société Générale")).toBe("Société-Générale");
    });

    it("preserves Arabic script", () => {
      // العربية → "العربية" (single token, no whitespace to collapse)
      expect(SPA._sanitizeFilenameStem("العربية")).toBe("العربية");
    });

    it("preserves CJK", () => {
      expect(SPA._sanitizeFilenameStem("中文")).toBe("中文");
    });

    it("preserves emoji", () => {
      expect(SPA._sanitizeFilenameStem("Bank 🏦")).toBe("Bank-🏦");
    });

    it("preserves a multi-script org name as a whole", () => {
      // mixed: Latin + Arabic + CJK + emoji; whitespace collapses to single dash
      expect(SPA._sanitizeFilenameStem("Société Générale العربية 中文 🏦"))
        .toBe("Société-Générale-العربية-中文-🏦");
    });
  });

  describe("Windows-illegal char stripping", () => {
    it.each([
      ["a<b", "a-b"],
      ["a>b", "a-b"],
      ['a"b', "a-b"],
      ["a:b", "a-b"],
      ["a/b", "a-b"],
      ["a\\b", "a-b"],
      ["a|b", "a-b"],
      ["a?b", "a-b"],
      ["a*b", "a-b"],
    ])("strips %j → %j", (input, expected) => {
      expect(SPA._sanitizeFilenameStem(input)).toBe(expected);
    });
  });

  describe("Control char + DEL stripping", () => {
    it("strips C0 control chars (U+0000-U+001F)", () => {
      expect(SPA._sanitizeFilenameStem("a\x00b\x01c\x1Fd")).toBe("a-b-c-d");
    });

    it("strips U+007F DEL (boundary case missed by [\\u0000-\\u001f] alone)", () => {
      expect(SPA._sanitizeFilenameStem("a\x7Fb")).toBe("a-b");
    });
  });

  describe("Bidi-override stripping (CVE-2021-42574 'Trojan Source')", () => {
    it("strips U+202E (RIGHT-TO-LEFT OVERRIDE) - real attack: invoice.exe disguised as invoice.jpg", () => {
      // "invoice<U+202E>gpj.exe" displays in Explorer as "invoiceexe.jpg"
      const out = SPA._sanitizeFilenameStem("invoice\u202Egpj.exe");
      expect(out).not.toContain("\u202E");
      expect(out).toBe("invoice-gpj.exe");
    });

    it.each([
      "\u202A", // LRE
      "\u202B", // RLE
      "\u202C", // PDF (Pop Directional Formatting)
      "\u202D", // LRO
      "\u202E", // RLO
      "\u2066", // LRI
      "\u2067", // RLI
      "\u2068", // FSI
      "\u2069", // PDI
    ])("strips bidi mark U+%s", (mark) => {
      const out = SPA._sanitizeFilenameStem("a" + mark + "b");
      expect(out).not.toContain(mark);
      expect(out).toBe("a-b");
    });
  });

  describe("Whitespace + dash collapse", () => {
    it("collapses runs of whitespace to single dash", () => {
      expect(SPA._sanitizeFilenameStem("Acme   Corp\t\nLimited")).toBe("Acme-Corp-Limited");
    });

    it("collapses runs of dashes to single dash", () => {
      expect(SPA._sanitizeFilenameStem("Acme---Corp")).toBe("Acme-Corp");
    });

    it("trims leading/trailing dashes and dots (Windows-corner-case safe)", () => {
      expect(SPA._sanitizeFilenameStem("...Acme...")).toBe("Acme");
      expect(SPA._sanitizeFilenameStem("---Acme---")).toBe("Acme");
      expect(SPA._sanitizeFilenameStem(".-.Acme.-.")).toBe("Acme");
    });
  });

  describe("Em-dash autofill case (assessment-app.js:2336)", () => {
    it("flattens 'OrgName — ISODate' autofill cleanly (no triple-dash artifact)", () => {
      // Legacy regex stripped the em-dash + spaces and produced "Acme-Corp---2026-05-15"
      // (three dashes from " — "). New sanitizer keeps the em-dash through the first
      // pass (it's a Unicode letter-class punctuation, not whitespace), then the
      // dash-collapse pass eliminates the artifact.
      // Actually em-dash is U+2014 - it's punctuation, not whitespace, not stripped
      // by our regex. The space-em-space pattern collapses via \s+ → "-" twice
      // around the em-dash, giving "Acme-Corp-—-2026-05-15".
      expect(SPA._sanitizeFilenameStem("Acme Corp — 2026-05-15"))
        .toBe("Acme-Corp-—-2026-05-15");
    });
  });

  describe("Empty / fallback handling", () => {
    it("returns 'assessment' for null / undefined / empty string", () => {
      expect(SPA._sanitizeFilenameStem(null)).toBe("assessment");
      expect(SPA._sanitizeFilenameStem(undefined)).toBe("assessment");
      expect(SPA._sanitizeFilenameStem("")).toBe("assessment");
    });

    it("returns 'assessment' when input sanitizes to nothing (only metas + dots)", () => {
      // Legacy regex would have produced "-" or "" here; new sanitizer falls back.
      expect(SPA._sanitizeFilenameStem("///***")).toBe("assessment");
      expect(SPA._sanitizeFilenameStem("...")).toBe("assessment");
      expect(SPA._sanitizeFilenameStem("---")).toBe("assessment");
      expect(SPA._sanitizeFilenameStem("   ")).toBe("assessment");
    });

    it("coerces non-string inputs", () => {
      expect(SPA._sanitizeFilenameStem(123)).toBe("123");
      expect(SPA._sanitizeFilenameStem({ toString: () => "obj" })).toBe("obj");
    });
  });

  describe("Windows reserved device names", () => {
    it.each([
      ["CON", "_CON"],
      ["con", "_con"],
      ["PRN", "_PRN"],
      ["AUX", "_AUX"],
      ["NUL", "_NUL"],
      ["COM1", "_COM1"],
      ["COM9", "_COM9"],
      ["LPT1", "_LPT1"],
      ["LPT9", "_LPT9"],
    ])("prefixes bare reserved name %j with underscore → %j", (input, expected) => {
      expect(SPA._sanitizeFilenameStem(input)).toBe(expected);
    });

    it.each([
      // Per https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file
      // Windows refuses to open reserved names followed by an extension too:
      // "NUL.txt" is not recommended.
      ["CON.txt", "_CON.txt"],
      ["con.json", "_con.json"],
      ["PRN.csv", "_PRN.csv"],
      ["AUX.xlsx", "_AUX.xlsx"],
      ["NUL.md", "_NUL.md"],
      ["COM1.log", "_COM1.log"],
      ["LPT9.pdf", "_LPT9.pdf"],
      // Multiple extensions: still reserved on the first dot-segment.
      ["CON.tar.gz", "_CON.tar.gz"],
    ])("prefixes reserved-name-with-extension %j with underscore → %j", (input, expected) => {
      expect(SPA._sanitizeFilenameStem(input)).toBe(expected);
    });

    it("does NOT prefix names that merely contain a reserved name as substring", () => {
      // "Concorde" starts with "CON" but is not the full token
      expect(SPA._sanitizeFilenameStem("Concorde")).toBe("Concorde");
      // "COM10" is not in the reserved list (only COM1-9)
      expect(SPA._sanitizeFilenameStem("COM10")).toBe("COM10");
      // "MyCON.txt" contains CON but isn't anchored at the start
      expect(SPA._sanitizeFilenameStem("MyCON.txt")).toBe("MyCON.txt");
      // "Auxiliary" starts with "AUX" but isn't the bare token or
      // followed immediately by a dot
      expect(SPA._sanitizeFilenameStem("Auxiliary")).toBe("Auxiliary");
    });
  });
});

describe("_agendaSlug (AS18b)", () => {
  it("is exported from the SPA module", () => {
    expect(typeof SPA._agendaSlug).toBe("function");
  });

  it("preserves Unicode letters (lowercased)", () => {
    expect(SPA._agendaSlug("Société Générale")).toBe("société-générale");
  });

  it("collapses whitespace and lowercases", () => {
    expect(SPA._agendaSlug("Acme  Corp Limited")).toBe("acme-corp-limited");
  });

  it("strips bidi overrides + Windows-illegal chars", () => {
    expect(SPA._agendaSlug("Acme/Corp\u202EXY")).toBe("acme-corp-xy");
  });

  it("returns empty string for null / empty input (caller falls back to date)", () => {
    expect(SPA._agendaSlug(null)).toBe("");
    expect(SPA._agendaSlug("")).toBe("");
  });

  it("truncates at 60 chars", () => {
    const long = "x".repeat(100);
    expect(SPA._agendaSlug(long).length).toBe(60);
  });
});
