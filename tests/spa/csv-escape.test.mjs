/**
 * CSV cell escape / formula-injection contract tests.
 *
 * The SPA sanitizes CSV cells via `sanitizeCell` (module-private) and the
 * inline `csvField` helper inside exportCSV. We test through the public
 * exportCSV path: inject a known-bad value into state, run exportCSV, then
 * parse the captured Blob.
 *
 * Cases marked [XFAIL] document the *desired* behavior of the upcoming
 * spa-fix-formula-injection patch and skip cleanly until it ships.
 */
import { describe, it, expect } from "vitest";
import { bootApp } from "./_bootSpa.mjs";

async function exportCsvWithNotes(notesByControl) {
  const answerControls = Object.keys(notesByControl).map(id => ({ id, answer: "no" }));
  const { app, captured } = await bootApp({ answerControls });
  for (const [id, notes] of Object.entries(notesByControl)) {
    app.state.responses[id].notes = notes;
  }
  app.exportCSV();
  return captured[captured.length - 1].blob.__text;
}

/** Quote-aware CSV row parser. */
function parseCsvRow(line) {
  const fields = [];
  let cur = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; }
      else if (ch === '"') { inQuotes = false; }
      else { cur += ch; }
    } else {
      if (ch === ",") { fields.push(cur); cur = ""; }
      else if (ch === '"' && cur === "") { inQuotes = true; }
      else { cur += ch; }
    }
  }
  fields.push(cur);
  return fields;
}

/** Returns the notes column value for a given control id from the CSV. */
function notesFor(csv, controlId) {
  const lines = csv.split("\n");
  for (const line of lines.slice(1)) {
    const fields = parseCsvRow(line);
    if (fields[0] === controlId) return fields[fields.length - 1];
  }
  return null;
}

/** Returns the raw CSV line for a control id (before quote/comma parsing). */
function rawLineFor(csv, controlId) {
  const lines = csv.split("\n");
  return lines.find(l => l.startsWith(controlId + ",") || l.startsWith('"' + controlId + '"'));
}

/** Match either of the two formula-prefix conventions (apostrophe or TAB). */
const FORMULA_PREFIX_RE = /^['\t]/;

describe("CSV cell escape / formula injection", () => {
  it("field with comma is double-quoted", async () => {
    const csv = await exportCsvWithNotes({ "1.1": "hello, world" });
    expect(rawLineFor(csv, "1.1")).toContain('"hello, world"');
    expect(notesFor(csv, "1.1")).toBe("hello, world");
  });

  it("field with embedded quote has internal quotes doubled", async () => {
    const csv = await exportCsvWithNotes({ "1.1": 'a"b' });
    expect(rawLineFor(csv, "1.1")).toContain('"a""b"');
    expect(notesFor(csv, "1.1")).toBe('a"b');
  });

  it("field with newline is double-quoted (CR/LF flattened to space)", async () => {
    const csv = await exportCsvWithNotes({ "1.1": "line1\nline2" });
    expect(rawLineFor(csv, "1.1")).toContain('"line1 line2"');
  });

  it("field with carriage return is double-quoted", async () => {
    const csv = await exportCsvWithNotes({ "1.1": "before\rafter" });
    expect(rawLineFor(csv, "1.1")).toContain('"');
  });

  it("formula-injection leading chars (=, +, -, @, TAB, CR) are prefixed", async () => {
    // Run each case in isolation so a misordered field can't masquerade as
    // another control's notes.
    for (const note of ["=cmd|'/c calc'!A1", "+1+1", "-2+3", "@SUM(A1)", "\tinjected", "\rinjected"]) {
      const csv = await exportCsvWithNotes({ "1.1": note });
      const got = notesFor(csv, "1.1");
      expect(got, `note ${JSON.stringify(note)}`).toMatch(FORMULA_PREFIX_RE);
    }
  });

  // [XFAIL: spa-fix-formula-injection] BOM/zero-width prefix stripping is a
  // planned hardening. Today's sanitizeCell only inspects the FIRST char, so
  // a leading \uFEFF bypasses the formula-prefix guard. Activate this test
  // once the sanitizeCell rewrite (strip \uFEFF\u200B\u200C\u200D before the
  // leading-char check) lands.
  it.skip("[XFAIL: spa-fix-formula-injection] BOM / zero-width chars at start are stripped before formula-prefix check", async () => {
    for (const note of ["\uFEFF=cmd", "\u200B=cmd", "\u200C+1+1", "\u200D-2+3"]) {
      const csv = await exportCsvWithNotes({ "1.1": note });
      const got = notesFor(csv, "1.1");
      expect(got).toMatch(/^['\t][=+\-@]/);
      expect(got.charCodeAt(0)).not.toBe(0xFEFF);
    }
  });
});
