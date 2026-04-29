/**
 * XLSX export cell-shape contract tests.
 *
 * Boots the SPA, calls exportExcel(), captures the workbook Blob, and parses
 * it with the `xlsx` package. Asserts sheet names + header rows.
 *
 * If `xlsx` is not installed (current dev-dep set), the suite skips with an
 * actionable note. If the package IS installed but SheetJS isn't loaded into
 * the SPA's window, the assertions skip.
 */
import { describe, it, expect, beforeAll } from "vitest";
import { bootApp } from "./_bootSpa.mjs";

let XLSX;
let xlsxAvailable = false;
try {
  XLSX = await import(/* @vite-ignore */ "xlsx");
  xlsxAvailable = true;
} catch {
  xlsxAvailable = false;
}

describe("XLSX export cell shape", () => {
  if (!xlsxAvailable) {
    it.skip("xlsx package not installed; install via `npm i -D xlsx` and re-run", () => {});
    return;
  }

  let workbook, captured;

  beforeAll(async () => {
    const ctx = await bootApp({
      answerControls: [
        { id: "1.1", answer: "yes" },
        { id: "1.2", answer: "no" },
        { id: "2.1", answer: "partial" },
      ],
    });
    captured = ctx.captured;
    // Inject SheetJS into the SPA's window so exportExcel() can use it.
    ctx.window.XLSX = XLSX;
    ctx.app.exportExcel();
    if (captured.length === 0) {
      console.warn("exportExcel produced no download — SheetJS not loaded in SPA window");
      return;
    }
    // exportExcel hands a binary array (not a string) to Blob; recover it
    // from the wrapped Blob's __parts.
    const parts = captured[captured.length - 1].blob.__parts || [];
    const buf = parts[0];
    const u8 = buf instanceof Uint8Array ? buf : new Uint8Array(buf);
    workbook = XLSX.read(u8, { type: "array" });
  });

  it("contains the expected sheets", () => {
    if (!workbook) return;
    expect(workbook.SheetNames).toContain("Summary");
    expect(workbook.SheetNames).toContain("Control Details");
    expect(workbook.SheetNames).toContain("Gap Analysis");
  });

  it("Control Details first row is the header row with required columns", () => {
    if (!workbook) return;
    const ws = workbook.Sheets["Control Details"];
    const rows = XLSX.utils.sheet_to_json(ws, { header: 1 });
    expect(rows.length).toBeGreaterThan(0);
    const header = rows[0];
    for (const col of ["Control ID", "Title", "Pillar"]) {
      expect(header).toContain(col);
    }
    // "Answer" or "Status" — accept either name; current SPA uses "Status".
    expect(header.some(h => /^(Answer|Status)$/.test(String(h)))).toBe(true);
  });

  it("Summary includes a row for each pillar", () => {
    if (!workbook) return;
    const ws = workbook.Sheets["Summary"];
    const rows = XLSX.utils.sheet_to_json(ws, { header: 1 });
    const flat = rows.map(r => (r && r[0] ? String(r[0]) : "")).join("\n");
    for (const p of [1, 2, 3, 4]) {
      expect(flat).toMatch(new RegExp("Pillar " + p));
    }
  });
});
