/**
 * Markdown agenda cell escape contract tests.
 *
 * The current `_agendaMdCell` only escapes pipes and newlines (table-cell
 * safety). Broader escaping (HTML tag chars, link syntax, backticks, emphasis)
 * is *desired* but not yet implemented — those tests skip until a future
 * spa-fix-md-escape patch lands.
 *
 * We test through the public `_buildAgendaMarkdown` helper.
 */
import { describe, it, expect } from "vitest";
import { bootApp } from "./_bootSpa.mjs";

let mdAvailable = false;
let MarkdownIt;
try {
  MarkdownIt = (await import(/* @vite-ignore */ "markdown-it")).default;
  mdAvailable = true;
} catch {
  mdAvailable = false;
}

async function buildAgenda({ id = "1.1", title = "Test Control", notes = "" } = {}) {
  const { app } = await bootApp({ answerControls: [{ id, answer: "no" }] });
  app.state.responses[id].notes = notes;
  // Inject a malicious title via the manifest data already loaded.
  const ctrl = app.data.controls.find(c => c.id === id);
  if (ctrl) ctrl.title = title;
  return app._buildAgendaMarkdown();
}

describe("agenda markdown cell escape", () => {
  it("flattens newlines inside table cells", async () => {
    const md = await buildAgenda({ title: "line1\nline2" });
    expect(md).toMatch(/\| 1\.1 \| line1 line2 \|/);
  });

  it("escapes pipe characters inside table cells", async () => {
    const md = await buildAgenda({ title: "a|b|c" });
    expect(md).toContain("a\\|b\\|c");
  });

  // [XFAIL: spa-fix-md-escape] HTML / link / backtick / emphasis escaping
  // isn't implemented yet — _agendaMdCell only neutralizes newlines and pipes
  // (table-cell safety). Activate when the broader escape patch lands.
  it.skip("[XFAIL: spa-fix-md-escape] escapes <script> tag chars", async () => {
    const md = await buildAgenda({ title: "<script>alert(1)</script>" });
    expect(md).not.toContain("<script>");
    expect(md).toMatch(/&lt;|\\</);
  });

  it.skip("[XFAIL: spa-fix-md-escape] escapes [link](url) brackets/parens", async () => {
    const md = await buildAgenda({ title: "[click](http://evil)" });
    expect(md).toMatch(/\\\[click\\\]\\\(http:\/\/evil\\\)/);
  });

  it.skip("[XFAIL: spa-fix-md-escape] escapes backticks", async () => {
    const md = await buildAgenda({ title: "`code`" });
    expect(md).toContain("\\`code\\`");
  });

  it.skip("[XFAIL: spa-fix-md-escape] escapes underscore-only emphasis", async () => {
    const md = await buildAgenda({ title: "_emph_" });
    expect(md).toContain("\\_emph\\_");
  });

  it("markdown-it on safe agenda input does not produce HTML tags", async () => {
    if (!mdAvailable) {
      console.warn("markdown-it not installed — skipping rendered-output check");
      return;
    }
    // This assertion holds today only for inputs that don't include raw HTML
    // (newlines/pipes are already neutralized). For raw-HTML payloads, see
    // the XFAIL block above.
    const md = await buildAgenda({ title: "safe | text" });
    const renderer = new MarkdownIt({ html: false });
    const html = renderer.render(md);
    expect(html).not.toMatch(/<script/i);
  });
});
