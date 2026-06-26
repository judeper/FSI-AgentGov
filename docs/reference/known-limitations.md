---
description: "A short, honest record of behaviors customers may encounter that are not bugs in this framework but are worth knowing before they show up in a compliance…"
---
# Known Limitations

A short, honest record of behaviors customers may encounter that are
not bugs in this framework but are worth knowing before they show up
in a compliance archive or auditor walkthrough.

This page complements the framework documentation. Items here are
**not** a deferred-defect backlog — those are tracked in the audit
findings register. These are limitations of upstream platforms or
browsers that we cannot fix in our own code.

---

## Browser print-to-PDF and right-to-left (RTL) scripts

**Affected feature:** Assessment SPA → "Print to PDF" via the browser
print dialog (Chromium, Edge, Safari, Firefox).

**Symptom:** When a results page contains Arabic, Hebrew, Urdu, Farsi,
or other RTL script (for example, in the `Organization name` field or
in scoping notes), the PDF saved by the browser may contain those
glyphs as **Unicode Presentation Forms** (the visual-order glyphs
U+FB50–U+FEFF) rather than the **logical-order Unicode** code points
the user typed. The PDF *looks* correct on screen but:

- Text search inside the PDF returns no matches for the original
  word.
- Screen readers (NVDA, JAWS, VoiceOver) read the presentation-form
  glyphs as their codepoint names rather than the intended word.
- Compliance archive search (ProofPoint Compliance Gateway, Smarsh
  Enterprise Archive, Global Relay) cannot index the RTL content
  for retrieval during e-discovery.

**Why this happens:** Browser print pipelines flatten complex-script
text into the visual-order glyph stream they send to the PDF writer.
This is a known limitation of all major browsers' built-in print-to-PDF
path; it is not specific to this framework.

**Workaround for RTL compliance archives:**

1. Export results as **JSON** or **Markdown** from the SPA's Export
   panel (these formats preserve logical Unicode).
2. Convert to PDF using a tool with proper complex-script support:
   - **[LibreOffice](https://www.libreoffice.org/)** —
     `soffice --headless --convert-to pdf assessment.md` produces
     a search-indexable PDF.
   - **[Pandoc](https://pandoc.org/) with XeLaTeX** —
     `pandoc assessment.md --pdf-engine=xelatex -V mainfont="Amiri"`
     for high-quality RTL typography.
3. Archive the PDF produced by step 2.

Markdown is **not** itself a WORM-archivable format in
ProofPoint / Smarsh / Global Relay; the PDF produced from step 2 is.

**Tracking:** F-RUNTIME-PDF-ARABIC-RTL-CORRUPTION-01 (closed AS18c
as a documented browser limitation, not a code defect).

---

*Updated: May 2026 | Framework version: v1.6.2*
