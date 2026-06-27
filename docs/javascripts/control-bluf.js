/*
 * Control "At a glance" (BLUF) summary card.
 *
 * Inserts a compact, scannable summary region immediately after the H1 on every
 * control page so a reader instantly sees pillar, zones, automation,
 * regulations, and roles -- before the 10-section detail body.
 *
 * Constraints honored:
 *   - Vanilla JS only. No external libraries, no CDN, no web fonts.
 *   - CSP-safe: same-origin fetch of the catalog JSON (connect-src 'self'); no
 *     eval, no inline handlers, no remote requests. ALL control data is placed
 *     via textContent / DOM nodes (never innerHTML) so it cannot inject markup.
 *   - Runs only on control detail pages (path contains "/controls/pillar-").
 *   - Re-inits cleanly under Material instant-loading navigation (document$),
 *     guarding against double-injection.
 *   - Accessible: labelled region, real text labels, natural focus order.
 *   - Catalog JSON is fetched once and cached on window across navigations.
 */
(function () {
  "use strict";

  var SCRIPT_MARK = "control-bluf.js";
  var DATA_FILE = "javascripts/control-explorer-data.json";
  var CACHE_KEY = "__fsiControlCatalog";
  var PROMISE_KEY = "__fsiControlCatalogPromise";
  var SECTION_ID = "fsi-bluf";

  var MAX_REGS = 6;
  var MAX_ROLES = 3;

  // Citations that are proposed/monitored (not yet adopted) get a distinct
  // marker so a flat chip doesn't imply adopted-rule status to an FSI audience.
  var PROPOSED_REGS = { "FINRA-25-07": true };
  function regDecorate(v) {
    var s = String(v);
    return PROPOSED_REGS[s]
      ? { text: s + " (proposed)", cls: "bluf__chip--proposed" }
      : { text: s, cls: "" };
  }

  // ---- base-path resolution (works under GitHub Pages sub-path deploys) ----
  function resolveBase() {
    var scripts = document.querySelectorAll("script[src]");
    for (var i = 0; i < scripts.length; i++) {
      var src = scripts[i].getAttribute("src") || "";
      var abs = scripts[i].src || src;
      if (abs.indexOf(SCRIPT_MARK) !== -1) {
        var marker = "/javascripts/";
        var idx = abs.indexOf(marker);
        if (idx !== -1) {
          return abs.slice(0, idx + 1); // includes trailing slash
        }
      }
    }
    // Fallback: relative to current document directory.
    return new URL(".", document.baseURI).href;
  }

  // Resolve the site base ONCE, at initial full-page load, while this script's
  // own src still resolves correctly. Under Material instant-loading the browser
  // re-resolves the relative <script src> against the new (deeper) page URL, so a
  // per-navigation resolveBase() would return the wrong base (e.g. ".../controls/")
  // and 404 the catalog fetch -- which then poisons the cached promise for the
  // whole session. Capturing here keeps the base correct across instant-nav.
  var SITE_BASE = resolveBase();

  // ---- small DOM helper ----
  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === "text") { node.textContent = attrs[k]; }
        else if (k === "class") { node.className = attrs[k]; }
        else { node.setAttribute(k, attrs[k]); }
      });
    }
    if (children) {
      (Array.isArray(children) ? children : [children]).forEach(function (c) {
        if (c == null) return;
        node.appendChild(typeof c === "string" ?
          document.createTextNode(c) : c);
      });
    }
    return node;
  }

  function isControlPage() {
    var path = window.location.pathname || "";
    return path.indexOf("/controls/pillar-") !== -1;
  }

  // ---- determine the control id (e.g. "1.1") ----
  function controlIdFromPage() {
    var h1 = document.querySelector(".md-content__inner h1, article h1, main h1, h1");
    if (h1) {
      var m = (h1.textContent || "").match(/Control\s+(\d+\.\d+)/i);
      if (m) return m[1];
    }
    // Fallback: extract X.Y from the URL slug.
    var path = window.location.pathname || "";
    var um = path.match(/\/(\d+\.\d+)/);
    return um ? um[1] : null;
  }

  function findControl(controls, id) {
    for (var i = 0; i < controls.length; i++) {
      if (String(controls[i].id) === String(id)) return controls[i];
    }
    return null;
  }

  // ---- card builders ----
  function chip(text, cls) {
    return el("span", { "class": "bluf__chip" + (cls ? " " + cls : ""), "text": text });
  }

  function field(label, valueNodes) {
    var dt = el("dt", { "class": "bluf__label", "text": label });
    var dd = el("dd", { "class": "bluf__value" },
      Array.isArray(valueNodes) ? valueNodes : [valueNodes]);
    return [dt, dd];
  }

  function zonesText(zones) {
    var z = (zones || []).slice().map(Number).sort(function (a, b) { return a - b; });
    if (!z.length) return "\u2014";
    return z.join(" \u00B7 ");
  }

  function buildChips(values, max, moreClass, decorate) {
    var frag = el("span", { "class": "bluf__chips" });
    var list = values || [];
    var shown = list.slice(0, max);
    shown.forEach(function (v) {
      if (decorate) { var d = decorate(v); frag.appendChild(chip(d.text, d.cls)); }
      else { frag.appendChild(chip(String(v))); }
    });
    var extra = list.length - shown.length;
    if (extra > 0) {
      frag.appendChild(chip("+" + extra + " more", moreClass || "bluf__chip--more"));
    }
    if (!list.length) { frag.appendChild(el("span", { "class": "bluf__muted", "text": "\u2014" })); }
    return frag;
  }

  function buildCard(control, base) {
    var section = el("section", {
      "id": SECTION_ID,
      "class": "bluf",
      "role": "region",
      "aria-label": "Control at a glance"
    });

    var dl = el("dl", { "class": "bluf__grid" });

    field("Pillar", el("span", { "class": "bluf__pillar", "text": control.pillarName || "\u2014" }))
      .forEach(function (n) { dl.appendChild(n); });

    field("Zones", el("span", { "text": zonesText(control.zones) }))
      .forEach(function (n) { dl.appendChild(n); });

    field("Automation", chip(control.automation || "unspecified", "bluf__chip--auto"))
      .forEach(function (n) { dl.appendChild(n); });

    field("Regulations", buildChips(control.regulations, MAX_REGS, null, regDecorate))
      .forEach(function (n) { dl.appendChild(n); });

    field("Roles", buildChips(control.roles, MAX_ROLES))
      .forEach(function (n) { dl.appendChild(n); });

    section.appendChild(dl);

    // ---- footer action row ----
    var explorerUrl = base + "controls/explorer/";
    if (control.pillarName) {
      explorerUrl += "?pillar=" + encodeURIComponent(control.pillarName);
    }
    var link = el("a", {
      "class": "bluf__action",
      "href": explorerUrl
    }, "Filter in Control Explorer \u2192");
    var footer = el("div", { "class": "bluf__footer" }, [link]);
    section.appendChild(footer);

    return section;
  }

  function insertCard(control, base) {
    var h1 = document.querySelector(".md-content__inner h1, article h1, main h1, h1");
    if (!h1 || !h1.parentNode) return;
    var card = buildCard(control, base);
    if (h1.nextSibling) {
      h1.parentNode.insertBefore(card, h1.nextSibling);
    } else {
      h1.parentNode.appendChild(card);
    }
  }

  // ---- boot ----
  function init() {
    if (!isControlPage()) return;
    // Guard against double-injection (instant loading / repeated init).
    if (document.getElementById(SECTION_ID)) return;

    var id = controlIdFromPage();
    if (!id) return;

    var base = SITE_BASE;

    function withData(controls) {
      // The DOM may have been replaced by instant-nav before the fetch
      // resolved; re-check the page and guard before inserting.
      if (!isControlPage() || document.getElementById(SECTION_ID)) return;
      var current = controlIdFromPage();
      if (!current) return;
      var control = findControl(controls, current);
      if (!control) return; // graceful: render nothing
      insertCard(control, base);
    }

    if (window[CACHE_KEY] && Array.isArray(window[CACHE_KEY])) {
      withData(window[CACHE_KEY]);
      return;
    }

    // Single-flight: cache the in-flight promise so concurrent inits (e.g.
    // document$ firing twice before the first fetch resolves) reuse one request.
    if (!window[PROMISE_KEY]) {
      window[PROMISE_KEY] = fetch(base + DATA_FILE, { credentials: "same-origin" })
        .then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status);
          return r.json();
        })
        .then(function (data) {
          var controls = Array.isArray(data) ? data : (data.controls || []);
          window[CACHE_KEY] = controls;
          return controls;
        });
    }

    window[PROMISE_KEY]
      .then(withData)
      .catch(function (err) {
        // Non-fatal: the page is fully usable without the summary card.
        // Reset the single-flight cache so a later navigation can retry rather
        // than reusing this rejected promise for the rest of the session.
        window[PROMISE_KEY] = null;
        if (window.console) window.console.error("Control BLUF:", err);
      });
  }

  if (typeof window.document$ !== "undefined" &&
      window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
