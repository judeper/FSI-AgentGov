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
 *
 * COUNCIL CRITIQUE GAPS — UTF-8 BOM + CRLF + accent round-trip (Phase 0I):
 *   Bug class A — Missing UTF-8 BOM:
 *     The SPA creates the CSV Blob without a BOM prefix. Excel on Windows
 *     opens BOM-less CSV files using the system locale encoding (typically
 *     Windows-1252 on en-US machines). Non-ASCII characters such as accented
 *     letters in customer or organisation names become garbage: "Société
 *     Générale" → "SociÃ©tÃ© GÃ©nÃ©rale". FSI customers who share gap
 *     reports with their compliance team across mixed Excel versions will
 *     have corrupted firm names in exported records.
 *     Expected today: FAIL (no BOM). Fix: prepend "\uFEFF" to the CSV string.
 *
 *   Bug class B — LF-only line endings:
 *     The SPA joins rows with "\n". Excel on Windows expects CRLF (\r\n) in
 *     CSV files. In some regional configurations (Japanese, Korean, certain
 *     European locales) LF-only CSV files cause all rows to be imported into
 *     a single cell, making the gap report unreadable.
 *     Expected today: FAIL (LF only). Fix: join rows with "\r\n".
 *
 *   Accent round-trip (informational):
 *     If BOM and CRLF are present, the UTF-8 bytes for accented characters
 *     should decode correctly in Node.js. This assertion verifies that the
 *     SPA does not double-encode non-ASCII content. If BOM is missing this
 *     test still passes at the byte level — the assertion is GREEN today but
 *     the Excel-visible corruption (Bug class A) remains.
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

    const text = readFileSync(path, "utf8").replace(/^\uFEFF/, "");
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

  // ── COUNCIL CRITIQUE GAPS: UTF-8 BOM + CRLF + accent round-trip ─────────
  test("UTF-8 BOM, CRLF line endings, and accented-org round-trip @regression", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));
    await freezeTime(page);

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    // Clone minimal-ciso and inject the accented organisation name so the
    // non-ASCII string flows through the SPA's CSV pipeline. The org name
    // itself is NOT written to the gap-list CSV body (the CSV format contains
    // only gap-control rows), so we also plant it in the notes field of a gap
    // control (1.7 = "no") to verify the encoding round-trip through csvField.
    const persona = loadPersona("minimal-ciso");
    const accentPersona = JSON.parse(JSON.stringify(persona));
    accentPersona.scoping.organizationName = "Société Générale";
    await seedScoping(page, accentPersona);

    // Two gap controls: 1.5 (partial) and 1.7 (no). Notes on 1.7 carry the
    // accented string so it appears in the exported CSV body.
    await answerControl(page, "1.5", "Partial");
    await answerControl(page, "1.7", "No");
    await page.locator("#ag-notes-1\\.7").fill("Société Générale — review note");
    await page.waitForTimeout(700);

    await navClick(page, "View Results");
    await page.locator(".ag-score-big").first().waitFor();
    await navClick(page, "Export Results");
    await page.getByRole("heading", { name: "Export Results" }).waitFor();

    const { path } = await expectDownload(page, async () => {
      await navClick(page, /Export as Gap List/);
    });

    // Read as raw bytes (Buffer) so we can inspect the BOM independently of
    // Node's string-level UTF-8 decoding, which masks a missing BOM.
    const raw = readFileSync(path);

    // ── ASSERTION 1: UTF-8 BOM (bytes 0xEF 0xBB 0xBF) ──────────────────────
    // Without a BOM, Excel on Windows opens the file in the system locale
    // encoding (often Windows-1252). "Société Générale" renders as
    // "SociÃ©tÃ© GÃ©nÃ©rale". An FSI firm whose name contains accented
    // characters will have its name corrupted in every gap report exported
    // from this tool and opened natively in Excel.
    // Expected today: FAIL — the SPA emits `new Blob([csv], {type:"text/csv"})`
    // with no BOM. Fix: prepend "\uFEFF" to the csv string before the Blob.
    expect(
      [raw[0], raw[1], raw[2]],
      "CSV must begin with UTF-8 BOM bytes [0xEF, 0xBB, 0xBF]. Without a BOM, " +
        "Excel on Windows interprets the file in the system locale encoding " +
        "(typically Windows-1252) and mangles all non-ASCII characters — " +
        "'Société Générale' becomes 'SociÃ©tÃ© GÃ©nÃ©rale'. FSI customers " +
        "sharing gap reports across mixed Excel versions will have corrupted " +
        "firm names in exported compliance records. " +
        "Fix: change exportCSV to prepend '\\uFEFF' to the csv string.",
    ).toEqual([0xef, 0xbb, 0xbf]);

    // Decode as UTF-8 for the remaining assertions (strip BOM if present so
    // the header-row check works regardless of BOM fix status).
    const text = raw.toString("utf8").replace(/^\uFEFF/, "");

    // ── ASSERTION 2: Accented string round-trip ──────────────────────────────
    // Verify the SPA does not double-encode non-ASCII content. Even without a
    // BOM, the raw UTF-8 bytes for "Société Générale" should be present and
    // decodable by Node's UTF-8 decoder. If the SPA serialises through a
    // non-UTF-8 path (e.g. encodeURIComponent without decode, or TextEncoder
    // with wrong label) the bytes would be corrupted at the source and no BOM
    // would rescue them.
    // NOTE: This assertion is likely GREEN today — Node decodes the UTF-8
    // bytes correctly even without a BOM. The Excel-visible corruption (BOM
    // assertion above) is the primary customer-impact bug; this assertion
    // verifies the byte content is correct, so that fixing the BOM is
    // sufficient.
    expect(
      text,
      "CSV body must contain the literal accented string 'Société Générale' " +
        "(planted in control 1.7 notes). If this fails, the SPA double-encoded " +
        "non-ASCII characters or stripped them — either defect corrupts FSI " +
        "customer names and organisation references in downstream compliance " +
        "reporting systems that import the gap report.",
    ).toContain("Société Générale");

    // ── ASSERTION 3: CRLF line endings ──────────────────────────────────────
    // Excel on Windows uses CRLF as the row delimiter when parsing CSV. An
    // LF-only file opens correctly in English-locale Excel but collapses all
    // rows into a single cell in some regional configurations (Japanese,
    // Korean, several European locales). FSI compliance officers running gap
    // analysis on a regional Windows machine will see an unreadable blob.
    // Expected today: FAIL — the SPA joins rows with "\n" (LF only).
    // Fix: change `rows.join("\n")` to `rows.join("\r\n")` in exportCSV.
    expect(
      text.includes("\r\n"),
      "CSV must use CRLF (\\r\\n) line endings. LF-only line endings mangle " +
        "row parsing in regional Excel configurations on Windows. A compliance " +
        "officer opening this gap report in Japanese or Korean Excel, or in " +
        "some European locale settings, will see every row concatenated into a " +
        "single cell, making the report completely unreadable. " +
        "Fix: change rows.join('\\n') to rows.join('\\r\\n') in exportCSV.",
    ).toBe(true);
  });
});
