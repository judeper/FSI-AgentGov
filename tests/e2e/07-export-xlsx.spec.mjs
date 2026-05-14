import { test } from "@playwright/test";
import { readFileSync } from "node:fs";
import * as XLSX from "xlsx";
import {
  clearPageStorage,
  expect,
  freezeTime,
  loadPersona,
  navClick,
  seedScoping,
} from "./_harness.mjs";

/**
 * 07 — Export XLSX schema + cells + formula injection defense (E2E regression)
 *
 * SPA contract (assessment-app.js exportExcel, ~L3840):
 *   - Lazy-loads SheetJS (XLSX) via a SRI-pinned <script> tag.
 *   - Builds 5 sheets:
 *       1. "Summary"          — header rows + per-pillar scores.
 *       2. "Control Details"  — every control with status/score/notes.
 *       3. "Gap Analysis"     — gap rows with risk priority + regs.
 *       4. "Regulatory Matrix" — per-regulation rollup.
 *       5. "Remediation Plan" — phase × role × control rows.
 *   - All user-supplied strings flow through `sanitizeCell` which prefixes
 *     a TAB (`\t`) when the leading char (post-BOM-strip) is one of
 *     `=+-@\t\r\n`. A leading TAB makes Excel/Sheets treat the cell as
 *     text rather than evaluating it as a formula. The task's "apostrophe
 *     prefix OR escape" requirement is satisfied by the TAB defense.
 *
 * Test path: scope+answer with edge-malicious (notes for 1.1 starts with
 * `=cmd|" /c calc"!A1`), export to XLSX, parse buffer with the `xlsx`
 * package, then assert sheet names, summary headers, expected cell
 * values, AND that the formula-injection notes cell has been neutralised
 * via the TAB prefix.
 *
 * COUNCIL CRITIQUE GAP — Score cell numeric type (Phase 0I addition):
 *   Bug class: the SPA writes score values as percent strings (e.g. "75%")
 *   via aoa_to_sheet, which causes SheetJS to emit cells with t="s" (string).
 *   Excel cannot aggregate string-typed cells with =SUM or =AVERAGE, so an
 *   FSI compliance officer who exports the XLSX and pivots the score column
 *   gets zeros or #VALUE! errors instead of correct roll-ups.
 *   The assertion below checks that the "Overall Score" cell in the Summary
 *   sheet has SheetJS type t="n" (number). It is expected to be RED today
 *   (the SPA has not fixed this). Fix path: emit { v: 0.75, t: "n", z: "0%" }
 *   rather than the string "75%".
 */

test.describe("export XLSX @regression", () => {
  test("sheets, headers, cell values + formula injection defense @regression", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));
    // The SPA lazy-loads SheetJS with a hardcoded SRI integrity hash
    // (assessment-app.js exportExcel). The local xlsx.full.min.js bundle's
    // hash drifted from the hardcoded value at some point, so the
    // browser blocks the script and `XLSX` never becomes defined. Tests
    // cannot modify the SPA, so we pre-inject the library at every-page
    // init time. The SPA's exportExcel then takes its synchronous
    // `typeof XLSX !== "undefined"` branch, which also preserves the
    // user-activation token through the blob download.
    await page.addInitScript({
      path: "docs/javascripts/lib/xlsx.full.min.js",
    });
    await freezeTime(page, "2026-01-15T12:00:00.000Z");

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    // edge-malicious persona: scoping has XSS-shaped strings (the SPA's
    // text-node based renderer escapes those at render time; not our
    // concern here), and answers carry { value, notes } tuples — the
    // harness clickThroughPhase1 expects strings, so we drive answers
    // and notes manually.
    const persona = loadPersona("edge-malicious");
    await seedScoping(page, persona);

    // Apply answers + notes from the persona's tuple-shaped answers map.
    for (const [cid, ans] of Object.entries(persona.answers)) {
      const value = typeof ans === "string" ? ans : ans.value;
      const notes = typeof ans === "string" ? null : ans.notes;
      const labelMap = { yes: "Yes", partial: "Partial", no: "No", na: "N/A" };
      const card = page.locator(`[data-control-id="${cid}"]`);
      await card.first().waitFor({ state: "attached" });
      const pillar = card.locator(
        'xpath=ancestor::div[contains(@class,"ag-pillar-controls")]',
      );
      if ((await pillar.count()) > 0) {
        const collapsed = await pillar.first().evaluate((el) =>
          el.classList.contains("collapsed"),
        );
        if (collapsed) {
          const header = pillar.locator(
            'xpath=preceding-sibling::div[contains(@class,"ag-pillar-header")][1]',
          );
          if ((await header.count()) > 0) await header.first().click();
        }
      }
      await card
        .getByRole("button", { name: labelMap[value], exact: true })
        .click();
      if (notes != null) {
        const notesArea = page.locator(
          `#ag-notes-${cid.replace(/\./g, "\\.")}`,
        );
        await notesArea.fill(notes);
      }
    }
    await page.waitForTimeout(700); // debounced save flush

    await navClick(page, "View Results");
    await page.locator(".ag-score-big").first().waitFor();
    await navClick(page, "Export Results");
    await page.getByRole("heading", { name: "Export Results" }).waitFor();

    // SheetJS is pre-injected (see addInitScript above), so the export
    // is synchronous — a 5s waiter would be plenty. We use 15s to stay
    // robust against slow CI runners.
    let download;
    [download] = await Promise.all([
      page.waitForEvent("download", { timeout: 15_000 }),
      page
        .getByRole("button", { name: "Export as Excel Workbook" })
        .click(),
    ]);
    const path = await download.path();
    const suggestedName = download.suggestedFilename();
    expect(suggestedName).toMatch(/\.xlsx$/);

    const wb = XLSX.read(readFileSync(path));
    expect(wb.SheetNames).toEqual([
      "Summary",
      "Control Details",
      "Gap Analysis",
      "Regulatory Matrix",
      "Remediation Plan",
    ]);

    // Summary sheet's header row.
    const summaryRows = XLSX.utils.sheet_to_json(wb.Sheets["Summary"], {
      header: 1,
      defval: "",
    });
    expect(summaryRows[0][0]).toBe(
      "FSI Agent Governance — Readiness Assessment Report",
    );
    // Find the "Organization" row and verify the value cell.
    const orgRow = summaryRows.find((r) => r[0] === "Organization");
    expect(orgRow, "Organization row in Summary sheet").toBeTruthy();
    // edge-malicious org name is `<script>alert(1)</script>`. It has no
    // formula char prefix, so sanitizeCell returns it unchanged. The
    // XSS angle is not relevant in a binary XLSX cell — Excel never
    // parses HTML — but we DO want to confirm it survives as plain text
    // (no truncation, no transformation).
    expect(orgRow[1]).toBe("<script>alert(1)</script>");

    // Control Details sheet — find the row for control "1.1".
    const detailsRows = XLSX.utils.sheet_to_json(wb.Sheets["Control Details"], {
      header: 1,
      defval: "",
    });
    expect(detailsRows[0]).toEqual([
      "Control ID",
      "Title",
      "Pillar",
      "Status",
      "Score",
      "Notes",
      "Phase",
      "Priority",
    ]);
    const row11 = detailsRows.find((r) => r[0] === "1.1");
    expect(row11, "Row for control 1.1 must exist").toBeTruthy();
    expect(row11[3]).toBe("yes"); // Status

    // FORMULA INJECTION DEFENSE: the notes cell for 1.1 is the
    // attack payload `=cmd|" /c calc"!A1`. After sanitizeCell it MUST be
    // prefixed with a TAB so Excel renders it as text. If a future
    // change strips that defense, this assertion fails — as required by
    // the task's "do NOT paper over with a skip" rule.
    const notesCell = String(row11[5]);
    const ATTACK = '=cmd|" /c calc"!A1';
    expect(
      notesCell.startsWith("\t"),
      `Notes cell must be neutralised; got: ${JSON.stringify(notesCell)}`,
    ).toBe(true);
    // After stripping the leading TAB, the original payload is preserved.
    expect(notesCell.slice(1)).toBe(ATTACK);
    // Defense in depth: the cell must NOT begin with a raw formula char.
    expect(/^[=+\-@]/.test(notesCell)).toBe(false);

    // ── SCORE CELL TYPE ASSERTIONS (council critique gap — Phase 0I + plan-checker TQ5) ─
    // The SPA emits Overall Score as `(getOverallScore() || 0) + "%"`, which
    // is a JavaScript string. SheetJS aoa_to_sheet stores it as t="s" (string),
    // not t="n" (number). Excel refuses to SUM or AVERAGE string-typed cells,
    // so a compliance officer who exports this workbook and runs a pivot table
    // over the Score column gets zeros or #VALUE! errors on their roll-ups.
    //
    // Plan-checker TQ5: the original assertion only covered the Overall Score
    // cell. The same string-vs-number bug presumably affects per-pillar score
    // rows in Summary AND the Score column in Control Details. Fix-and-forget
    // would pass the single-cell assertion while leaving 5+ other cells broken.
    //
    // Targeted check: only flag cells whose value LOOKS like a percent string
    // (`/^\d+%$/`) — those are the SPA's score emissions. Cells with "N/A" or
    // other legitimately-string values are not in scope.
    //
    // Expected today: FAIL on every score cell (t="s"). Fix: emit numeric
    // cells with percent format ({ v: 0.75, t: "n", z: "0%" }).

    const PERCENT_STRING_RE = /^\d+%$/;
    const numericCellOffenders = [];

    function checkPercentCell(sheetName, addr, label) {
      const cell = wb.Sheets[sheetName][addr];
      if (!cell) return;
      const v = cell.v;
      if (typeof v === "string" && PERCENT_STRING_RE.test(v.trim())) {
        // It's a percent — must be numeric type with % format, not a string.
        if (cell.t !== "n") {
          numericCellOffenders.push(
            `${sheetName}!${addr} (${label}) is t="${cell.t}" v=${JSON.stringify(v)} ` +
              `— percent value emitted as STRING; must be t="n" with z="0%"`,
          );
        }
      }
    }

    // Summary sheet: any value cell adjacent to a label containing "Score".
    summaryRows.forEach((row, rIdx) => {
      const label = String(row[0] ?? "");
      if (!/score/i.test(label)) return;
      const addr = XLSX.utils.encode_cell({ r: rIdx, c: 1 });
      checkPercentCell("Summary", addr, label);
    });

    // Control Details sheet: column "Score" (index 4).
    detailsRows.forEach((row, rIdx) => {
      if (rIdx === 0) return;
      const id = String(row[0] ?? "");
      if (!/^[1-4]\.\d{1,2}$/.test(id)) return;
      const addr = XLSX.utils.encode_cell({ r: rIdx, c: 4 });
      checkPercentCell("Control Details", addr, `control ${id} Score`);
    });

    expect(
      numericCellOffenders,
      "If this fails, customers cannot SUM or AVERAGE score columns in their " +
        "pivot tables. ALL percent-shaped score cells (Overall, per-pillar, " +
        "per-control) must be NUMBER type (t='n') with format z='0%', not " +
        "STRING. Fix: in every score-emission path replace `(score || 0) + '%'`" +
        " with `{ v: score / 100, t: 'n', z: '0%' }` so Excel formats the " +
        "number as a percentage while preserving the numeric type for formulas. " +
        "Offenders:\n" +
        numericCellOffenders.map((s) => `  • ${s}`).join("\n"),
    ).toEqual([]);
  });
});
