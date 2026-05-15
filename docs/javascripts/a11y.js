/* docs/javascripts/a11y.js
 * ----------------------------------------------------------------------------
 * Accessibility shim for docs that mkdocs-material 9.7.6 + pymdownx.tasklist
 * does not handle natively.
 *
 * Closes:
 *   F-A11Y-DOCS-LABEL-TASKLIST-04  — pymdownx GFM task-list <input type="checkbox" disabled>
 *                                     is wrapped in <label class="task-list-control">
 *                                     but the label has only the visual indicator
 *                                     <span> as content (no accessible name).
 *                                     Screen readers announce the input as
 *                                     "checkbox unchecked" with no purpose context.
 *
 * Why aria-hidden (not aria-label):
 *   These checkboxes are `disabled` AND `clickable_checkbox: false` in mkdocs.yml
 *   (display-only — they communicate nothing the LI text doesn't already carry).
 *   `aria-hidden="true"` is the most honest WCAG description of their role:
 *   the visual indicator is decorative, the LI text IS the meaningful content.
 *   Screen readers read "list item: <LI text>" and skip the visual indicator
 *   entirely.
 *
 * Material 9 instant-nav re-applies after each soft navigation via the
 * documented `document$` observable. We subscribe so the fix re-applies on
 * every page swap.
 *
 * Same-origin script under /javascripts/ — covered by the existing
 * `script-src 'self'` CSP without changes.
 */
(function () {
  function applyA11yFixes() {
    document.querySelectorAll('.task-list-item input[type="checkbox"]').forEach(
      function (input) {
        if (input.hasAttribute("aria-hidden")) return;
        input.setAttribute("aria-hidden", "true");
        input.setAttribute("tabindex", "-1");
      },
    );
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyA11yFixes);
  } else {
    applyA11yFixes();
  }

  if (typeof document$ !== "undefined" && document$ && document$.subscribe) {
    document$.subscribe(applyA11yFixes);
  }
})();
