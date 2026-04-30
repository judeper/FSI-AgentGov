import { test } from "@playwright/test";
import { readFileSync } from "node:fs";
import {
  clearPageStorage,
  expect,
  expectDownload,
  freezeTime,
  loadPersona,
  navClick,
  seedScoping,
} from "./_harness.mjs";

/**
 * 08 — Export CSV (gap list) + formula injection defense (E2E regression)
 *
 * INSPECTION FINDING (assessment-app.js exportCSV, ~L3808):
 *   - The CSV export is a GAP-LIST CSV. Header row:
 *       Control ID,Title,Pillar,Status,Score,Risk Priority,Regulations,Notes
 *   - Filename: sanitize(assessmentName) + "-gaps.csv".
 *   - One row per control returned by `getGapControls()` (controls
 *     answered "no" or "partial").
 *   - Every cell flows through `sanitizeCell`, then a CSV-quote pass
 *     that escapes embedded `"` and newlines.
 *   - sanitizeCell prefixes a TAB on cells starting with =+-@\t\r\n.
 *
 * Test path: drive scoping + a small set of answers that include a "no"
 * response carrying a formula-injection notes payload. Export, read the
 * CSV from disk, verify header + row count + the TAB prefix on the
 * malicious notes cell.
 *
 * The edge-malicious persona is appropriate here: its answer for "1.2"
 * is `no` with the unicode-trick notes string, but for the formula
 * injection check we install a separate `=cmd|...` notes string on a
 * "no" answer (1.3) so it lands in the gap list.
 */

const ATTACK_NOTES = '=cmd|" /c calc"!A1';

async function answerControl(page, controlId, label) {
  const card = page.locator(`[data-control-id="${controlId}"]`);
  await card.first().waitFor({ state: "attached" });
  const pillar = card.locator(
    'xpath=ancestor::div[contains(@class,"ag-pillar-controls")]',
  );
  if ((await pillar.count()) > 0) {
    const collapsed = await pillar
      .first()
      .evaluate((el) => el.classList.contains("collapsed"));
    if (collapsed) {
      const header = pillar.locator(
        'xpath=preceding-sibling::div[contains(@class,"ag-pillar-header")][1]',
      );
      if ((await header.count()) > 0) await header.first().click();
    }
  }
  await card.getByRole("button", { name: label, exact: true }).click();
}

/** Minimal CSV parser — header-aware, handles quoted fields with escaped quotes. */
function parseCsv(text) {
  const rows = [];
  let i = 0;
  let field = "";
  let row = [];
  let inQuotes = false;
  while (i < text.length) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i += 2;
          continue;
        }
        inQuotes = false;
        i += 1;
        continue;
      }
      field += c;
      i += 1;
      continue;
    }
    if (c === '"') { inQuotes = true; i += 1; continue; }
    if (c === ",") { row.push(field); field = ""; i += 1; continue; }
    if (c === "\n") { row.push(field); rows.push(row); row = []; field = ""; i += 1; continue; }
    if (c === "\r") { i += 1; continue; }
    field += c;
    i += 1;
  }
  // flush trailing field/row
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

test.describe("export CSV @regression", () => {
  test("gap-list CSV header, row count, formula injection defense @regression", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));
    await freezeTime(page);

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    // Use minimal-ciso scoping but custom answers so we control which
    // controls land in the gap list.
    const persona = loadPersona("minimal-ciso");
    await seedScoping(page, persona);

    // Three "no" answers (= 3 gaps) and one "yes" (excluded). Note: 1.5
    // "partial" is also a gap per getGapControls (any non-yes/non-na).
    await answerControl(page, "1.1", "Yes"); // not a gap
    await answerControl(page, "1.2", "No"); // gap
    await answerControl(page, "1.3", "No"); // gap (carries attack notes)
    await answerControl(page, "1.4", "Partial"); // gap

    // Plant the formula-injection payload in 1.3's notes.
    await page.locator("#ag-notes-1\\.3").fill(ATTACK_NOTES);
    await page.waitForTimeout(700);

    await navClick(page, "View Results");
    await page.locator(".ag-score-big").first().waitFor();
    await navClick(page, "Export Results");
    await page.getByRole("heading", { name: "Export Results" }).waitFor();

    const { suggestedName, path } = await expectDownload(page, async () => {
      await navClick(page, /Export as Gap List/);
    });
    expect(suggestedName).toMatch(/-gaps\.csv$/);

    const text = readFileSync(path, "utf8");
    const rows = parseCsv(text);

    // Header row.
    expect(rows[0]).toEqual([
      "Control ID",
      "Title",
      "Pillar",
      "Status",
      "Score",
      "Risk Priority",
      "Regulations",
      "Notes",
    ]);

    // Body rows match answered-gap count (3 gaps). Anything else means
    // either the gap-detection logic shifted (regression) or the CSV
    // body got mangled.
    const body = rows.slice(1).filter((r) => r.length > 1 && r[0] !== "");
    expect(body.length).toBe(3);

    // Find the row for control 1.3 and verify the formula-injection
    // notes cell is neutralised via TAB prefix.
    const row13 = body.find((r) => r[0] === "1.3");
    expect(row13, "Row for control 1.3 (the attack carrier) must exist").toBeTruthy();
    expect(row13[3]).toBe("no"); // Status
    const notesCell = row13[7];
    expect(
      notesCell.startsWith("\t"),
      `CSV notes cell must be neutralised; got: ${JSON.stringify(notesCell)}`,
    ).toBe(true);
    expect(notesCell.slice(1)).toBe(ATTACK_NOTES);
    expect(/^[=+\-@]/.test(notesCell)).toBe(false);
  });
});
