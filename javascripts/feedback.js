/*
 * Per-page "Was this page helpful?" feedback control.
 *
 * Injects a small block near the bottom of each content page with
 * 👍 Yes / 👎 No buttons. Clicking either opens a prefilled GitHub issue
 * in a new tab (a normal link navigation — no fetch/POST, CSP-safe) and
 * records an aggregate counter in localStorage.
 *
 * CSP: script-src 'self' 'unsafe-inline'; connect-src 'self' https://api.github.com.
 * No external libraries. Vanilla JS only.
 *
 * Re-initializes cleanly under Material instant-loading navigation by
 * subscribing to the `document$` observable when present, else falling
 * back to DOMContentLoaded. Guards against double-injection.
 */
(function () {
  "use strict";

  var REPO_URL = "https://github.com/judeper/FSI-AgentGov";
  var BLOCK_ID = "fsi-feedback";
  var STORAGE_PREFIX = "fsi.feedback.";

  function normalizePath(path) {
    if (!path) {
      return "/";
    }
    // Treat ".../" and ".../index.html" as the same location.
    return path.replace(/index\.html$/, "").replace(/\/+$/, "/") || "/";
  }

  // Pages where the feedback block should NOT appear: homepage and 404.
  function isExcludedPage() {
    var path = window.location.pathname || "/";

    // 404 page: GitHub Pages serves 404.html for unknown paths.
    if (/(^|\/)404\.html$/.test(path) || /(^|\/)404\/?$/.test(path)) {
      return true;
    }

    var current = normalizePath(path);

    // Homepage: compare against the Material logo/home link, which always
    // points at the site root (handles GitHub Pages sub-path deployments).
    var homeLink =
      document.querySelector(".md-header__button.md-logo[href]") ||
      document.querySelector("a.md-logo[href]") ||
      document.querySelector('.md-nav__item .md-nav__link[href$="."]');
    if (homeLink) {
      var homePath = normalizePath(
        new URL(homeLink.getAttribute("href"), window.location.href).pathname
      );
      if (current === homePath) {
        return true;
      }
    }

    // Fallback: bare site root with no extra path segments.
    if (current === "/" || current === "/index.html") {
      return true;
    }
    return false;
  }

  function pageKey() {
    var path = window.location.pathname || "/";
    return path.replace(/[^a-zA-Z0-9._/-]/g, "_");
  }

  function getCount(key) {
    try {
      var raw = window.localStorage.getItem(key);
      var n = parseInt(raw, 10);
      return isNaN(n) ? 0 : n;
    } catch (e) {
      return 0;
    }
  }

  function recordEvent(verdict) {
    // verdict is "yes" or "no"
    try {
      var key = STORAGE_PREFIX + pageKey() + "." + verdict;
      window.localStorage.setItem(key, String(getCount(key) + 1));
    } catch (e) {
      // localStorage may be unavailable (private mode); fail silently.
    }
  }

  function buildIssueUrl(verdict) {
    var title = document.title || "Documentation page";
    var pageUrl = window.location.href;
    var helpful = verdict === "yes" ? "Yes" : "No";
    var body =
      "Page: " + pageUrl + "\n" +
      "Helpful: " + helpful + "\n\n" +
      "What could be better?\n";
    return (
      REPO_URL +
      "/issues/new" +
      "?labels=" + encodeURIComponent("docs-feedback") +
      "&title=" + encodeURIComponent("Docs feedback: " + title) +
      "&body=" + encodeURIComponent(body)
    );
  }

  function makeButton(verdict, label) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "fsi-feedback__btn fsi-feedback__btn--" + verdict;
    btn.setAttribute("data-verdict", verdict);
    btn.setAttribute("aria-label", label);
    btn.textContent = label;
    btn.addEventListener("click", function () {
      recordEvent(verdict);
      var url = buildIssueUrl(verdict);
      window.open(url, "_blank", "noopener,noreferrer");
      // Provide a non-disruptive confirmation for keyboard/screen-reader users.
      var status = document.getElementById(BLOCK_ID + "-status");
      if (status) {
        status.textContent =
          "Thanks for your feedback! A prefilled issue opened in a new tab.";
      }
    });
    return btn;
  }

  function buildBlock() {
    var section = document.createElement("section");
    section.id = BLOCK_ID;
    section.className = "fsi-feedback";
    section.setAttribute("aria-labelledby", BLOCK_ID + "-heading");

    var heading = document.createElement("h2");
    heading.id = BLOCK_ID + "-heading";
    heading.className = "fsi-feedback__heading";
    heading.textContent = "Was this page helpful?";
    section.appendChild(heading);

    var group = document.createElement("div");
    group.className = "fsi-feedback__buttons";
    group.setAttribute("role", "group");
    group.setAttribute("aria-labelledby", BLOCK_ID + "-heading");
    group.appendChild(makeButton("yes", "\uD83D\uDC4D Yes"));
    group.appendChild(makeButton("no", "\uD83D\uDC4E No"));
    section.appendChild(group);

    var status = document.createElement("p");
    status.id = BLOCK_ID + "-status";
    status.className = "fsi-feedback__status";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    section.appendChild(status);

    return section;
  }

  function inject() {
    if (isExcludedPage()) {
      return;
    }
    // Guard against double-injection (instant loading / repeated init).
    if (document.getElementById(BLOCK_ID)) {
      return;
    }
    var content =
      document.querySelector(".md-content__inner") ||
      document.querySelector(".md-content") ||
      document.querySelector("article") ||
      document.querySelector("main");
    if (!content) {
      return;
    }
    content.appendChild(buildBlock());
  }

  if (
    typeof window.document$ !== "undefined" &&
    window.document$ &&
    typeof window.document$.subscribe === "function"
  ) {
    window.document$.subscribe(inject);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inject);
  } else {
    inject();
  }
})();
