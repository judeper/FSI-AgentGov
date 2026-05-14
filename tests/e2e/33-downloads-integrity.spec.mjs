/**
 * 33 — Downloads integrity
 *
 * Finding (Phase 0D): The /downloads/ index page links to 6 role-based Excel
 * checklists. No prior test covered this surface. A broken link or corrupt
 * .xlsx file silently fails customers whose primary offline deliverable is one
 * of these files.
 *
 * Assertions:
 *   A. The /downloads/ index page loads (HTTP 200 + DOM ready).
 *   B. Every <a href="*.xlsx"> on the page returns HTTP 200 to a HEAD request.
 *      Why: a dead link is the most common failure mode after a rename/delete.
 *   C. Every .xlsx body parses as a valid SheetJS workbook (≥1 sheet).
 *      Why: catches truncated uploads and files accidentally replaced with
 *      wrong content.
 *   D. First sheet has ≥5 non-empty rows of data.
 *      Why: an empty template or export stub should not reach customers.
 *   E. Content marker: at least one cell in the first sheet matches the
 *      framework control-ID pattern (/^[1-4]\.\d{1,2}$/) OR contains one of
 *      the tokens "FSI", "Pillar", or "Zone" (case-insensitive).
 *      Why: guards against a placeholder or wrong file being served.
 *   F. Count of .xlsx links on the /downloads/ page == count of .xlsx files
 *      in docs/downloads/ on disk.
 *      Why: catches "file deleted but link still lives" AND "file added but
 *      never linked from the index".
 *
 * Tags: @regression @docs-content
 * NOT tagged @smoke — downloading and parsing 6 binary files adds ~10s.
 */

import { test } from "@playwright/test";
import { readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { expect } from "./_harness.mjs";
import XLSX from "xlsx";

const here = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(here, "..", "..");
const DOWNLOADS_SRC_DIR = join(REPO_ROOT, "docs", "downloads");

/** Control-ID pattern: "1.1" through "4.29" */
const CONTROL_ID_RE = /^[1-4]\.\d{1,2}$/;
/** Loose FSI-framework content markers present in every checklist */
const FSI_MARKER_RE = /FSI|Pillar|Zone/i;

/** Count .xlsx files physically present in docs/downloads/ */
function countDiskXlsx() {
  return readdirSync(DOWNLOADS_SRC_DIR).filter((f) => f.endsWith(".xlsx"))
    .length;
}

/**
 * Returns true if any cell in the first sheet of `workbook` satisfies the
 * content-marker heuristic (control ID regex OR FSI/Pillar/Zone text).
 */
function hasContentMarker(workbook) {
  const sheetName = workbook.SheetNames[0];
  const ws = workbook.Sheets[sheetName];
  const rows = XLSX.utils.sheet_to_json(ws, { header: 1 });
  for (const row of rows) {
    for (const cell of row) {
      const v = String(cell ?? "").trim();
      if (CONTROL_ID_RE.test(v)) return true;
      if (FSI_MARKER_RE.test(v)) return true;
    }
  }
  return false;
}

test.describe("Downloads integrity @regression @docs-content", () => {
  test(
    "all .xlsx downloads are reachable, parse correctly, and link count matches disk",
    async ({ page, request }, testInfo) => {
      // 6 files × ~5s download/parse budget; give CI extra headroom.
      testInfo.setTimeout(60_000);

      // baseURL is http://127.0.0.1:PORT/assessment/ — navigate to site root
      // path /downloads/ which MkDocs publishes from docs/downloads/index.md.
      const response = await page.goto("/downloads/", {
        waitUntil: "domcontentloaded",
      });
      expect(
        response?.status(),
        "/downloads/ page did not return HTTP 200",
      ).toBe(200);

      // Collect every fully-resolved href that ends in .xlsx.
      const xlsxUrls = await page.$$eval(
        'a[href$=".xlsx"]',
        (anchors) => anchors.map((a) => a.href),
      );

      // (A) At least one link found — page rendered correctly.
      expect(
        xlsxUrls.length,
        "No .xlsx links found on /downloads/ — page may have failed to render",
      ).toBeGreaterThan(0);

      // (F) Linked count must match disk count.
      const diskCount = countDiskXlsx();
      expect(
        xlsxUrls.length,
        `Linked .xlsx count (${xlsxUrls.length}) ≠ disk count (${diskCount}). ` +
          "Either a file was deleted without removing its link, or a file " +
          "was added to docs/downloads/ without being linked from the index.",
      ).toBe(diskCount);

      // Per-file assertions — collect all failures before asserting so the
      // error message lists every broken file in one run.
      const failures = [];

      for (const url of xlsxUrls) {
        const label = url.split("/").pop() ?? url;

        // (B) HEAD must succeed.
        const headResp = await request.head(url);
        if (!headResp.ok()) {
          failures.push(`${label}: HEAD returned HTTP ${headResp.status()}`);
          continue;
        }

        // Download body.
        const getResp = await request.get(url);
        if (!getResp.ok()) {
          failures.push(`${label}: GET returned HTTP ${getResp.status()}`);
          continue;
        }

        const bodyBuf = await getResp.body();

        // (C) Parse with SheetJS.
        let workbook;
        try {
          workbook = XLSX.read(bodyBuf, { type: "buffer" });
        } catch (err) {
          failures.push(`${label}: SheetJS parse error — ${err.message}`);
          continue;
        }

        if (workbook.SheetNames.length === 0) {
          failures.push(`${label}: workbook contains 0 sheets`);
          continue;
        }

        // (D) First sheet ≥5 non-empty rows.
        const firstWs = workbook.Sheets[workbook.SheetNames[0]];
        const allRows = XLSX.utils.sheet_to_json(firstWs, { header: 1 });
        const nonEmptyRows = allRows.filter(
          (r) =>
            Array.isArray(r) &&
            r.some((c) => c !== null && c !== undefined && c !== ""),
        );
        if (nonEmptyRows.length < 5) {
          failures.push(
            `${label}: first sheet has only ${nonEmptyRows.length} non-empty row(s) (required ≥5)`,
          );
          continue;
        }

        // (E) Content marker.
        if (!hasContentMarker(workbook)) {
          failures.push(
            `${label}: no content marker — expected a cell matching ` +
              `/^[1-4]\\.\\d{1,2}$/ or containing "FSI", "Pillar", or "Zone"`,
          );
        }
      }

      expect(
        failures,
        [
          `${failures.length} download(s) failed validation:`,
          ...failures.map((f) => `  • ${f}`),
        ].join("\n"),
      ).toEqual([]);
    },
  );
});
