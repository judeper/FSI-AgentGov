/**
 * Assessment Loader — ~2KB global script
 *
 * Detects the assessment page and lazy-loads the main application plus
 * dependencies (Chart.js, SheetJS). Uses MkDocs Material's document$
 * observable to handle navigation.instant page transitions.
 *
 * Loaded on every page but does nothing unless #assessment-app exists.
 */
(function () {
  "use strict";

  var appInstance = null;
  var loading = false;
  var basePath = "";

  /** Resolve the base URL for lazy-loaded scripts. */
  function getBasePath() {
    if (basePath) return basePath;
    var scripts = document.querySelectorAll('script[src*="assessment-loader"]');
    if (scripts.length) {
      var src = scripts[scripts.length - 1].src;
      basePath = src.substring(0, src.lastIndexOf("/") + 1);
    } else {
      // Fallback: derive from current page
      var loc = window.location;
      basePath = loc.protocol + "//" + loc.host + loc.pathname.replace(/\/[^/]*$/, "/javascripts/");
    }
    return basePath;
  }

  /** Load assessment CSS dynamically (only on assessment page). */
  function loadCSS() {
    var id = "ag-assessment-css";
    if (document.getElementById(id)) return;
    var base = getBasePath();
    // CSS is in ../stylesheets/ relative to javascripts/
    var cssUrl = base.replace(/javascripts\/$/, "stylesheets/assessment.css");
    var link = document.createElement("link");
    link.id = id;
    link.rel = "stylesheet";
    link.href = cssUrl;
    document.head.appendChild(link);
  }

  /** SRI hashes for vendored libraries (sha256). */
  var SRI_HASHES = {
    "lib/chart.min.js": "sha256-IGtui7APx7uix+6AykHbPp4FunvgqjWr66nP1TV/XQ4=",
  };

  /** Load a script and return a Promise. */
  function loadScript(url, integrity) {
    return new Promise(function (resolve, reject) {
      var existing = document.querySelector('script[src="' + url + '"]');
      if (existing && !existing.dataset.failed) { resolve(); return; }
      if (existing) existing.remove();
      var s = document.createElement("script");
      s.src = url;
      if (integrity) {
        s.integrity = integrity;
        s.crossOrigin = "anonymous";
      }
      s.onload = resolve;
      s.onerror = function () {
        s.dataset.failed = "true";
        reject(new Error("Failed to load " + url));
      };
      document.head.appendChild(s);
    });
  }

  /** Load all assessment dependencies in parallel. */
  function loadDependencies() {
    var base = getBasePath();
    return Promise.all([
      loadScript(base + "assessment-app.js"),
      loadScript(base + "lib/chart.min.js", SRI_HASHES["lib/chart.min.js"])
    ]);
  }

  /** Attempt to initialize or destroy the assessment app. */
  function tryInit() {
    var container = document.getElementById("assessment-app");

    // Navigated away — destroy existing instance and remove CSS
    if (!container && appInstance) {
      try { appInstance.destroy(); } catch (e) { /* ignore */ }
      appInstance = null;
      // spa-test-hook: keep window.__assessmentApp in sync so E2E tests
      // observe the cleanup.
      try { delete window.__assessmentApp; } catch (e) { window.__assessmentApp = null; }
      var css = document.getElementById("ag-assessment-css");
      if (css) css.remove();
      return;
    }

    // AS8 (F-SPA-BACK-NO-ROUTING-01): detect DOM swap. Material's
    // `navigation.instant` re-fetches the page on browser back/forward
    // when the URL query changes (e.g. ?step=results → ?step=phase1)
    // and swaps the document body, leaving our appInstance bound to a
    // detached `<div id="assessment-app">`. We must destroy the stale
    // instance and re-init against the new container so the SPA reads
    // the updated `?step=` from the URL and renders the correct screen.
    // Without this, browser back appears to do nothing.
    if (container && appInstance && appInstance.el !== container) {
      try { appInstance.destroy(); } catch (e) { /* ignore */ }
      appInstance = null;
      try { delete window.__assessmentApp; } catch (e) { window.__assessmentApp = null; }
      // Fall through to the init branch below to create a fresh instance
      // bound to the new DOM.
    }

    // Not on assessment page, or already initialized
    if (!container || appInstance || loading) return;

    loading = true;
    loadCSS();
    loadDependencies()
      .then(function () {
        // Re-check container still exists (user may have navigated away)
        var el = document.getElementById("assessment-app");
        if (!el) { loading = false; return; }
        if (typeof window.AssessmentApp === "function") {
          appInstance = new window.AssessmentApp(el);
          appInstance.init();
          // spa-test-hook: expose the live instance so Playwright @regression
          // specs can read app.step / app.state without DOM scraping.
          window.__assessmentApp = appInstance;
        } else {
          console.error("AssessmentApp not found after loading dependencies");
        }
        loading = false;
      })
      .catch(function (err) {
        console.error("Assessment loader error:", err);
        loading = false;
        var el = document.getElementById("assessment-app");
        if (el) {
          el.innerHTML =
            '<div class="admonition failure"><p class="admonition-title">Error</p>' +
            "<p>Failed to load the assessment tool. Please refresh the page.</p></div>";
        }
      });
  }

  // MkDocs Material's lifecycle hook (fires on every instant navigation).
  // document$ is an RxJS BehaviorSubject that replays the latest value on subscribe,
  // so even if it fired before this script parsed, we still get the initial event.
  if (typeof document$ !== "undefined") {
    document$.subscribe(tryInit);
  } else {
    // Fallback: Material not loaded (custom theme or SSR)
    document.addEventListener("DOMContentLoaded", tryInit);
    // Safety: if DOM is already ready (script loaded after DOMContentLoaded)
    if (document.readyState !== "loading") {
      tryInit();
    }
  }
})();
