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
 *   A11Y-02  — All content data tables missing scope="col" on <th> cells.
 *              JAWS/NVDA cannot reliably associate headers with data cells
 *              in multi-column tables without the scope attribute. Fixed with
 *              a one-line querySelector loop. Scoped to avoid the Control
 *              Explorer table (which already has scope="col" set natively)
 *              and the assessment SPA tables (which set scope inline).
 *
 *   A11Y-03  — Search dialog missing accessible name and aria-modal="true".
 *              The <div role="dialog"> from Material has no aria-label and
 *              no aria-modal. Screen readers cannot announce it properly or
 *              confine virtual-cursor focus to the dialog when it opens.
 *
 * Why aria-hidden (not aria-label) for task-list checkboxes:
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
    // --- A11Y-02 (R4): Palette toggle radio inputs are 0×0 / opacity-0 but sit
    //     in the natural tab order (tabindex=0). A sighted keyboard user encounters
    //     two invisible focus stops between the logo and search field.
    //     Fix: set tabindex="-1" so they leave the tab sequence; keyboard access
    //     is retained through the visible wrapper element with its aria-label.
    ["__palette_0", "__palette_1"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el && el.getAttribute("tabindex") !== "-1") {
        el.setAttribute("tabindex", "-1");
      }
    });

    // --- Task-list checkboxes (F-A11Y-DOCS-LABEL-TASKLIST-04) ---
    document.querySelectorAll('.task-list-item input[type="checkbox"]').forEach(
      function (input) {
        if (input.hasAttribute("aria-hidden")) return;
        input.setAttribute("aria-hidden", "true");
        input.setAttribute("tabindex", "-1");
      },
    );

    // --- A11Y-02: Add scope="col" to all data-table <th> cells that lack it.
    //     Scoped to .md-content tables (the docs prose area) to avoid touching
    //     the Control Explorer table (ce-table) and assessment SPA tables
    //     which manage their own scope attributes.
    document.querySelectorAll(".md-content table thead th").forEach(
      function (th) {
        if (!th.getAttribute("scope")) {
          th.setAttribute("scope", "col");
        }
      },
    );

    // --- A11Y-03: Add accessible name + aria-modal to Material search dialog.
    //     Material renders <div role="dialog"> inside .md-search but omits
    //     aria-label and aria-modal. We add both defensively; if a future
    //     Material version adds them natively the setAttribute call is a no-op.
    var searchDialog = document.querySelector('.md-search [role="dialog"]');
    if (searchDialog) {
      if (!searchDialog.getAttribute("aria-label")) {
        searchDialog.setAttribute("aria-label", "Site search");
      }
      if (!searchDialog.getAttribute("aria-modal")) {
        searchDialog.setAttribute("aria-modal", "true");
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyA11yFixes);
  } else {
    applyA11yFixes();
  }

  // scrollable-region-focusable (WCAG 2.1.1): any horizontally-scrollable
  // wrapper (incl. SPA-rendered tables) needs keyboard access. Sweep + observe.
  function focusScrollers() {
    document.querySelectorAll(
      ".md-typeset__scrollwrap, .ce-root, .ag-chart-container, .ag-card table, .md-typeset table"
    ).forEach(function (el) {
      if (el.scrollWidth > el.clientWidth + 1 && !el.hasAttribute("tabindex")) {
        el.setAttribute("tabindex", "0");
        if (!el.getAttribute("role")) el.setAttribute("role", "group");
      }
    });
  }
  focusScrollers();
  if (typeof MutationObserver !== "undefined") {
    new MutationObserver(focusScrollers).observe(document.body, { childList: true, subtree: true });
  }

  if (typeof document$ !== "undefined" && document$ && document$.subscribe) {
    document$.subscribe(applyA11yFixes);
  }
})();
