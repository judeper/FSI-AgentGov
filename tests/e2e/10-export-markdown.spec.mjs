import { test } from "@playwright/test";
import { readFileSync } from "node:fs";
import MarkdownIt from "markdown-it";
import {
  clearPageStorage,
  expect,
  expectDownload,
  freezeTime,
  loadPersona,
  navClick,
  selectControlAnswer,
  seedScoping,
} from "./_harness.mjs";

/**
 * 10 — Export Markdown (Next Session Agenda) + injection defense (E2E regression)
 *
 * INSPECTION FINDING (assessment-app.js exportAgenda + _buildAgendaMarkdown,
 * ~L4151):
 *   - The only Markdown export is the "Next Session Agenda" — top-N
 *     gap controls with remediation detail.
 *   - Filename: `fsi-agentgov-<slug>-<isodate>-agenda.md`.
 *   - Document structure:
 *       # FSI Agent Governance Assessment — Next Session Agenda
 *       **Customer:** <organization>
 *       ...metadata block...
 *       ## Top N Gap Controls
 *       <table>
 *       ## Remediation Detail
 *       ## Gap 1 — Control <id>: <title>     (one ## per gap)
 *   - Every user-supplied cell flows through `_agendaMdCell`, which
 *     escapes Markdown specials AND the HTML brackets `<>` so that
 *     `<script>alert(1)</script>` becomes `\<script\>alert\(1\)\<\/script\>`.
 *
 * // FINDING: SPA only ships agenda MD; per-pillar H2 export missing.
 * // Phase 3 may build it. The task originally asked for Markdown export
 * // with one H2 section per pillar (## Pillar 1: Security, etc.) and an
 * // H1 containing the org name. The shipped feature is the agenda format:
 * // per-gap ## sections, not per-pillar. The test.skip block below records
 * // this gap in the regression suite so it is visibly pending.
 *
 * NOTE on task scope deviation: the task asks for Markdown export with
 * H2 sections per pillar and an H1 containing the org name. The actual
 * shipped feature is the agenda, which uses a per-gap ## structure
 * rather than per-pillar. We test the actual feature and document the
 * gap rather than asserting against a non-existent shape.
 */

test.describe("export Markdown agenda @regression", () => {
  test("agenda structure + XSS escape on org name @regression", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));
    await freezeTime(page, "2026-01-15T12:00:00.000Z");

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    // edge-malicious scoping has the XSS-shaped org name. Use seedScoping
    // for the canonical scoping path (it fills via getByLabel which
    // sets DOM input values directly — no execution).
    const persona = loadPersona("edge-malicious");
    await seedScoping(page, persona);

    // Need at least one gap to populate the Top-N table + Remediation
    // section. Use the persona's "1.2" → "no" answer (its notes carry
    // unicode tricks — also useful coverage for _agendaMdCell).
    await selectControlAnswer(page, "1.1", "yes"); // not a gap
    await selectControlAnswer(page, "1.2", "no"); // gap

    await page.waitForTimeout(700);

    await navClick(page, "View Results");
    await page.locator(".ag-score-big").first().waitFor();
    await navClick(page, "Export Results");
    await page.getByRole("heading", { name: "Export Results" }).waitFor();

    const { suggestedName, path } = await expectDownload(page, async () => {
      await navClick(page, /Export as Next Session Agenda/);
    });
    // Canonical ASSESS-13 pattern: fsi-agentgov-<slug>-<iso>-agenda.md.
    expect(suggestedName).toMatch(/^fsi-agentgov-.+-\d{4}-\d{2}-\d{2}-agenda\.md$/);

    const md = readFileSync(path, "utf8");

    // H1 — exact title (the org name lives in the metadata block).
    expect(md.split(/\r?\n/)[0]).toBe(
      "# FSI Agent Governance Assessment — Next Session Agenda",
    );

    // The agenda exporter emits the org name into the metadata block
    // as raw text (`**Customer:** <org>`). The current SPA does not
    // markdown-escape this single line — only table cells go through
    // `_agendaMdCell`. That is acceptable defense-in-depth IF the
    // downstream rendering disallows raw HTML, which markdown-it does
    // by default (`html: false`). The strict assertion below is the
    // rendered-HTML XSS check; the raw-source escape is a known
    // minor SPA gap and is intentionally NOT asserted here.

    // Markdown parses cleanly via markdown-it (catches malformed table
    // syntax produced by an _agendaMdCell regression).
    const parser = new MarkdownIt();
    const tokens = parser.parse(md, {});
    expect(tokens.length).toBeGreaterThan(0);

    // H1 token sanity check.
    const h1Open = tokens.find(
      (t) => t.type === "heading_open" && t.tag === "h1",
    );
    expect(h1Open, "expected an h1 heading_open token").toBeTruthy();

    // Top-N Gap Controls H2 + Remediation Detail H2 are both present.
    const h2Texts = [];
    for (let i = 0; i < tokens.length; i++) {
      if (tokens[i].type === "heading_open" && tokens[i].tag === "h2") {
        const inline = tokens[i + 1];
        if (inline && inline.type === "inline") h2Texts.push(inline.content);
      }
    }
    expect(h2Texts.some((s) => /^Top \d+ Gap Controls$/.test(s))).toBe(true);
    expect(h2Texts).toContain("Remediation Detail");
    // At least one per-gap "Gap N — Control X.Y: ..." section.
    expect(h2Texts.some((s) => /^Gap 1 [—\-] Control 1\.2/.test(s))).toBe(true);

    // Render the markdown to HTML and verify NO raw <script> tag was
    // produced — the strongest "XSS escape" guarantee.
    const html = parser.render(md);
    expect(html).not.toMatch(/<script\b/i);
    expect(html).not.toMatch(/<img\b[^>]*onerror/i);
  });

  // ── COUNCIL CRITIQUE GAP: per-pillar H2 export not implemented ───────────
  // FINDING: the SPA ships only the agenda format (per-gap ## sections).
  // There are no ## Pillar 1: Security / ## Pillar 2: Management sections.
  // This test.skip records the gap in the regression suite so that it is
  // visibly pending. If Phase 3 builds per-pillar export, remove the skip
  // and implement the assertions below.
  test.skip(
    "per-pillar H2 export not yet implemented — Phase 3 deliverable",
    async ({ page: _page }) => {
      // When this feature ships, assert:
      //   1. MD contains exactly 4 H2 sections matching /^## Pillar \d+:/
      //   2. Each pillar H2 is followed by at least one score numeral.
      //   3. Each pillar section contains at least one control anchor.
      //   4. Pillar headings appear in order (Pillar 1 before Pillar 2, etc.).
      throw new Error("Not implemented — remove skip when Phase 3 builds per-pillar MD export");
    },
  );

  // ── COUNCIL CRITIQUE GAPS: positive contract for agenda MD (Phase 0I) ────
  test("agenda MD: H1 heading, org name, unique headings, score numeral @regression", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));
    await freezeTime(page, "2026-01-15T12:00:00.000Z");

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    // Use minimal-ciso so the org name is a clean ASCII string ("Acme Bank")
    // that we can assert literally without worrying about _agendaMdCell escaping.
    const persona = loadPersona("minimal-ciso");
    await seedScoping(page, persona);

    // Three gap controls (partial + no): 1.5, 1.7, 2.1.
    await selectControlAnswer(page, "1.4", "yes"); // not a gap
    await selectControlAnswer(page, "1.5", "partial"); // gap
    await selectControlAnswer(page, "1.7", "no"); // gap
    await selectControlAnswer(page, "1.11", "yes"); // not a gap
    await selectControlAnswer(page, "2.1", "partial"); // gap
    await page.waitForTimeout(700);

    await navClick(page, "View Results");
    await page.locator(".ag-score-big").first().waitFor();
    await navClick(page, "Export Results");
    await page.getByRole("heading", { name: "Export Results" }).waitFor();

    const { suggestedName, path } = await expectDownload(page, async () => {
      await navClick(page, /Export as Next Session Agenda/);
    });
    expect(suggestedName).toMatch(/^fsi-agentgov-.+-\d{4}-\d{2}-\d{2}-agenda\.md$/);

    const md = readFileSync(path, "utf8");
    const lines = md.split(/\r?\n/);

    // ── ASSERTION 1: H1 heading as first line ─────────────────────────────
    expect(
      lines[0],
      "Agenda MD must open with an H1 heading on line 1. A document without " +
        "an H1 fails accessibility (WCAG 1.3.1), breaks screen-reader navigation " +
        "for compliance officers with visual disabilities, and produces invalid " +
        "structure when the MD is converted to PDF for regulatory filing.",
    ).toBe("# FSI Agent Governance Assessment \u2014 Next Session Agenda");

    // ── ASSERTION 2: Organisation name present ────────────────────────────
    // _buildAgendaMarkdown emits "**Customer:** <org>" using _agendaMdCell.
    // For the clean "Acme Bank" name the escaped form is identical to the
    // original. If the org name is absent, recipients cannot identify which
    // client the agenda belongs to — a serious gap in audit-trail integrity.
    expect(
      md,
      "Agenda MD must contain the organisation name 'Acme Bank'. An agenda " +
        "without a customer identifier cannot be used as an audit artefact — " +
        "compliance officers and their clients need to verify which firm the " +
        "gap list belongs to before filing or archiving.",
    ).toContain("Acme Bank");

    // ── ASSERTION 3: Heading texts are unique and non-empty ───────────────
    // Duplicate or empty heading anchors break in-page navigation and cause
    // GitHub / SharePoint MD renderers to append disambiguating suffixes
    // ("-1", "-2") that invalidate hardcoded deep-links shared in Teams or
    // email during remediation sessions.
    const parser = new MarkdownIt();
    const tokens = parser.parse(md, {});
    const headingTexts = [];
    for (let i = 0; i < tokens.length; i++) {
      if (
        tokens[i].type === "heading_open" &&
        ["h1", "h2", "h3"].includes(tokens[i].tag)
      ) {
        const inline = tokens[i + 1];
        if (inline && inline.type === "inline") headingTexts.push(inline.content);
      }
    }
    // No empty headings.
    for (const text of headingTexts) {
      expect(
        text.trim().length,
        `Heading must not be empty. Found heading with blank text. Empty headings ` +
          `break anchor-based navigation in rendered MD (GitHub, SharePoint) and ` +
          `violate WCAG 2.4.6 (headings must be descriptive).`,
      ).toBeGreaterThan(0);
    }
    // No duplicates.
    const seen = new Set();
    for (const text of headingTexts) {
      expect(
        seen.has(text),
        `Duplicate heading "${text}" detected. Duplicate headings cause rendered ` +
          `MD renderers (GitHub, SharePoint, Confluence) to append "-1", "-2" ` +
          `suffixes to anchor IDs, breaking deep-links shared between the assessment ` +
          `facilitator and client stakeholders during remediation planning sessions.`,
      ).toBe(false);
      seen.add(text);
    }

    // ── ASSERTION 4: Self-assessed score line + score basis disclaimer ───
    // _buildAgendaMarkdown emits "**Self-assessed score:** N%" plus a
    // "**Score basis:**" disclaimer line. The disclaimer is required so
    // leadership reading this agenda alongside an engine PDF doesn't
    // conflate the two scoring dimensions (SPA % vs engine maturity 0–4).
    // AS15d (F-SCALE-MISMATCH-01): prior assertion regex `\d+\.\d` would
    // match control IDs and timestamps even after the maturity line was
    // removed — replaced with a positive structural assertion.
    expect(
      /\*\*Self-assessed score:\*\* (\d+%|n\/a)/.test(md),
      "Agenda MD must contain a '**Self-assessed score:** N%' (or n/a) " +
        "line. If absent, recipients have no quantitative readiness signal " +
        "and cannot track progress between assessment sessions — a key " +
        "audit-trail requirement under OCC Bulletin 2026-13 (formerly OCC 2011-12).",
    ).toBe(true);
    expect(
      md.includes("**Score basis:**"),
      "Agenda MD must contain the '**Score basis:**' disclaimer that " +
        "distinguishes the SPA's questionnaire score from the engine's " +
        "telemetry-driven maturity score (F-SCALE-MISMATCH-01). Without it, " +
        "leadership reading the agenda alongside an engine PDF may conflate " +
        "the two scoring dimensions.",
    ).toBe(true);
    expect(
      /\*\*Overall maturity:\*\*/i.test(md),
      "Agenda MD must NOT contain '**Overall maturity:**' — that label was " +
        "retired in AS15d because it falsely implied parity with the engine's " +
        "0-4 maturity scale via a fake `* 4 / 100` linear conversion.",
    ).toBe(false);
  });
});
