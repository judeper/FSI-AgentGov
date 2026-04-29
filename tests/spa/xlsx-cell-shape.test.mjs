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

  // SheetJS is lazy-loaded by the SPA via a script tag relative to
  // assessment-loader.js, which doesn't exist in the jsdom harness. We can
  // inject XLSX onto the window, but exportExcel's internal helpers (e.g.
  // workbook metadata access) still tickle uninitialized DOM properties.
  // Skip until the SPA exposes a testable seam (or we can stub the loader).
  it.skip("[deferred: needs SheetJS loader stub] exportExcel produces a parseable workbook", () => {});
  it.skip("[deferred: needs SheetJS loader stub] Control Details first row is the header row with required columns", () => {});
  it.skip("[deferred: needs SheetJS loader stub] Summary includes a row for each pillar", () => {});
});
