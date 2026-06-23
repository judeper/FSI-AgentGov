/*
 * Control Explorer -- interactive filter/sort/search over the FSI-AgentGov
 * governance control catalog.
 *
 * Constraints honored:
 *   - Vanilla JS only. No external libraries, no CDN, no web fonts.
 *   - CSP-safe: same-origin fetch of the data JSON (connect-src 'self'); no
 *     eval, no inline event handlers, no remote requests. All control data is
 *     inserted via textContent (never innerHTML) so it cannot inject markup.
 *   - WCAG 2.1 AA: labelled controls, fieldset/legend facet groups, aria-live
 *     result count, sortable headers expose aria-sort, full keyboard support.
 *   - Re-inits cleanly under Material instant-loading navigation (document$).
 *   - Deep-linking: active search/filters/sort are encoded in the URL query
 *     string and restored on load so a filtered view is shareable.
 */
(function () {
  "use strict";

  var CONTAINER_ID = "control-explorer";
  var DATA_FILE = "javascripts/control-explorer-data.json";
  var SCRIPT_MARK = "control-explorer.js";
  // Citations that are proposed/monitored (not yet adopted) — surfaced distinctly
  // so a flat badge doesn't imply adopted-rule status to an FSI audience.
  var PROPOSED_REGS = { "FINRA-25-07": true };

  var AUTOMATION_ORDER = ["Automatable", "Partial", "Manual", "unspecified"];
  var PILLAR_ORDER = ["Security", "Management", "Reporting", "SharePoint"];

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

  // ---- URL state (deep-linking) ----
  var FIELDS = {
    q: "search",
    pillar: "pillar",
    zone: "zone",
    reg: "reg",
    role: "role",
    auto: "auto",
    sort: "sort",
    dir: "dir"
  };

  function readState() {
    var params = new URLSearchParams(window.location.search);
    return {
      search: params.get("q") || "",
      pillar: splitParam(params.get("pillar")),
      zone: splitParam(params.get("zone")),
      reg: splitParam(params.get("reg")),
      role: splitParam(params.get("role")),
      auto: splitParam(params.get("auto")),
      sort: params.get("sort") === "title" ? "title" : "id",
      dir: params.get("dir") === "desc" ? "desc" : "asc"
    };
  }

  function splitParam(v) {
    if (!v) return [];
    return v.split(",").map(function (s) { return s.trim(); })
            .filter(function (s) { return s.length; });
  }

  function writeState(state) {
    var params = new URLSearchParams();
    if (state.search) params.set("q", state.search);
    if (state.pillar.length) params.set("pillar", state.pillar.join(","));
    if (state.zone.length) params.set("zone", state.zone.join(","));
    if (state.reg.length) params.set("reg", state.reg.join(","));
    if (state.role.length) params.set("role", state.role.join(","));
    if (state.auto.length) params.set("auto", state.auto.join(","));
    if (state.sort !== "id") params.set("sort", state.sort);
    if (state.dir !== "asc") params.set("dir", state.dir);
    var qs = params.toString();
    var url = window.location.pathname + (qs ? "?" + qs : "") +
              window.location.hash;
    try {
      window.history.replaceState(null, "", url);
    } catch (e) { /* history may be unavailable in some embeds */ }
  }

  // ---- small DOM helpers ----
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

  function uniqueSorted(values, order) {
    var seen = {};
    values.forEach(function (v) { if (v != null && v !== "") seen[v] = true; });
    var list = Object.keys(seen);
    if (order) {
      list.sort(function (a, b) {
        var ia = order.indexOf(a), ib = order.indexOf(b);
        if (ia === -1) ia = order.length;
        if (ib === -1) ib = order.length;
        if (ia !== ib) return ia - ib;
        return a < b ? -1 : a > b ? 1 : 0;
      });
    } else {
      list.sort();
    }
    return list;
  }

  function compareIds(a, b) {
    var pa = a.split(".").map(Number), pb = b.split(".").map(Number);
    for (var i = 0; i < Math.max(pa.length, pb.length); i++) {
      var da = pa[i] || 0, db = pb[i] || 0;
      if (da !== db) return da - db;
    }
    return 0;
  }

  // ---- main renderer ----
  function render(container, controls) {
    container.textContent = "";
    container.classList.add("ce-root");

    var state = readState();

    // facet vocabularies derived from the data
    var pillars = uniqueSorted(
      controls.map(function (c) { return c.pillarName; }), PILLAR_ORDER);
    var zones = uniqueSorted(
      controls.reduce(function (a, c) {
        return a.concat((c.zones || []).map(String)); }, []))
      .sort(function (a, b) { return Number(a) - Number(b); });
    var regs = uniqueSorted(
      controls.reduce(function (a, c) {
        return a.concat(c.regulations || []); }, []));
    var roles = uniqueSorted(
      controls.reduce(function (a, c) { return a.concat(c.roles || []); }, []));
    var autos = uniqueSorted(
      controls.map(function (c) { return c.automation; }), AUTOMATION_ORDER);

    var liveCount = el("p", {
      "class": "ce-count",
      "role": "status",
      "aria-live": "polite",
      "aria-atomic": "true"
    });

    // ---- search box ----
    var searchId = "ce-search";
    var searchInput = el("input", {
      "type": "search",
      "id": searchId,
      "class": "ce-search-input",
      "placeholder": "Filter by control ID or title\u2026",
      "autocomplete": "off",
      "spellcheck": "false",
      "value": state.search
    });
    var searchLabel = el("label", {
      "for": searchId, "class": "ce-label", "text": "Search controls"
    });
    var searchWrap = el("div", { "class": "ce-search" },
      [searchLabel, searchInput]);

    // ---- facet groups ----
    var facetState = {
      pillar: state.pillar, zone: state.zone, reg: state.reg,
      role: state.role, auto: state.auto
    };

    function facetGroup(legend, key, values, opts) {
      opts = opts || {};
      var fs = el("fieldset", { "class": "ce-facet" });
      fs.appendChild(el("legend", { "class": "ce-facet-legend", "text": legend }));

      var optionsWrap = el("div", {
        "class": "ce-facet-options" + (opts.scroll ? " ce-facet-scroll" : "")
      });

      // optional in-facet filter for long lists (e.g. roles)
      if (opts.filterable) {
        var fId = "ce-facet-filter-" + key;
        var fLabel = el("label", {
          "for": fId, "class": "ce-visually-hidden",
          "text": "Filter " + legend + " options"
        });
        var fInput = el("input", {
          "type": "search", "id": fId, "class": "ce-facet-filter",
          "placeholder": "Filter " + legend.toLowerCase() + "\u2026",
          "autocomplete": "off"
        });
        fInput.addEventListener("input", function () {
          var term = fInput.value.toLowerCase();
          var labels = optionsWrap.querySelectorAll(".ce-check");
          labels.forEach(function (lb) {
            var t = (lb.getAttribute("data-value") || "").toLowerCase();
            lb.style.display = (!term || t.indexOf(term) !== -1) ? "" : "none";
          });
        });
        fs.appendChild(fLabel);
        fs.appendChild(fInput);
      }

      values.forEach(function (v) {
        var cbId = "ce-" + key + "-" +
          String(v).replace(/[^a-z0-9]+/gi, "-");
        var cb = el("input", {
          "type": "checkbox", "id": cbId, "class": "ce-checkbox", "value": v
        });
        if (facetState[key].indexOf(String(v)) !== -1) cb.checked = true;
        cb.addEventListener("change", function () {
          var arr = facetState[key];
          var sv = String(v);
          var pos = arr.indexOf(sv);
          if (cb.checked && pos === -1) arr.push(sv);
          else if (!cb.checked && pos !== -1) arr.splice(pos, 1);
          update();
        });
        var label = el("label", {
          "class": "ce-check", "for": cbId, "data-value": String(v)
        }, [cb, el("span", { "text": opts.labelFn ? opts.labelFn(v) : String(v) })]);
        optionsWrap.appendChild(label);
      });

      fs.appendChild(optionsWrap);
      return fs;
    }

    var facets = el("div", { "class": "ce-facets" }, [
      facetGroup("Pillar", "pillar", pillars),
      facetGroup("Zone", "zone", zones, {
        labelFn: function (z) { return "Zone " + z; }
      }),
      facetGroup("Regulation", "reg", regs, { scroll: true, filterable: true }),
      facetGroup("Role", "role", roles, { scroll: true, filterable: true }),
      facetGroup("Automation", "auto", autos)
    ]);

    // ---- reset button ----
    var resetBtn = el("button", {
      "type": "button", "class": "ce-reset", "text": "Clear all filters"
    });
    resetBtn.addEventListener("click", function () {
      state.search = "";
      facetState.pillar = []; facetState.zone = []; facetState.reg = [];
      facetState.role = []; facetState.auto = [];
      searchInput.value = "";
      var checks = container.querySelectorAll(".ce-checkbox");
      checks.forEach(function (c) { c.checked = false; });
      var filters = container.querySelectorAll(".ce-facet-filter");
      filters.forEach(function (f) {
        f.value = "";
        f.dispatchEvent(new Event("input"));
      });
      update();
    });

    // ---- results table ----
    var sortState = { sort: state.sort, dir: state.dir };
    var table = el("table", { "class": "ce-table" });
    var caption = el("caption", { "class": "ce-visually-hidden",
      "text": "Governance controls matching the current filters" });
    table.appendChild(caption);
    var thead = el("thead");
    var headRow = el("tr");

    function sortableTh(label, key) {
      var th = el("th", { "scope": "col" });
      var btn = el("button", {
        "type": "button", "class": "ce-sort-btn", "text": label
      });
      var indicator = el("span", { "class": "ce-sort-ind", "aria-hidden": "true" });
      btn.appendChild(indicator);
      btn.addEventListener("click", function () {
        if (sortState.sort === key) {
          sortState.dir = sortState.dir === "asc" ? "desc" : "asc";
        } else {
          sortState.sort = key; sortState.dir = "asc";
        }
        update();
      });
      th.appendChild(btn);
      th._key = key; th._ind = indicator;
      return th;
    }

    var thId = sortableTh("ID", "id");
    var thTitle = sortableTh("Control", "title");
    headRow.appendChild(thId);
    headRow.appendChild(thTitle);
    headRow.appendChild(el("th", { "scope": "col", "text": "Pillar" }));
    headRow.appendChild(el("th", { "scope": "col", "text": "Zones" }));
    headRow.appendChild(el("th", { "scope": "col", "text": "Regulations" }));
    thead.appendChild(headRow);
    table.appendChild(thead);
    var tbody = el("tbody");
    table.appendChild(tbody);

    var emptyMsg = el("p", { "class": "ce-empty", "hidden": "hidden",
      "text": "No controls match the current filters. Try clearing some." });

    // ---- filtering + sorting + paint ----
    function matches(c) {
      var term = state.search.trim().toLowerCase();
      if (term) {
        var hay = (c.id + " " + c.title).toLowerCase();
        if (hay.indexOf(term) === -1) return false;
      }
      if (facetState.pillar.length &&
          facetState.pillar.indexOf(c.pillarName) === -1) return false;
      if (facetState.auto.length &&
          facetState.auto.indexOf(c.automation) === -1) return false;
      if (facetState.zone.length &&
          !facetState.zone.some(function (z) {
            return (c.zones || []).map(String).indexOf(z) !== -1; }))
        return false;
      if (facetState.reg.length &&
          !facetState.reg.some(function (r) {
            return (c.regulations || []).indexOf(r) !== -1; }))
        return false;
      if (facetState.role.length &&
          !facetState.role.some(function (r) {
            return (c.roles || []).indexOf(r) !== -1; }))
        return false;
      return true;
    }

    var base = resolveBase();

    function badge(text, cls) {
      return el("span", { "class": "ce-badge " + cls, "text": text });
    }

    function paint() {
      var rows = controls.filter(matches);
      rows.sort(function (a, b) {
        var r;
        if (sortState.sort === "title") {
          r = a.title.toLowerCase() < b.title.toLowerCase() ? -1 :
              a.title.toLowerCase() > b.title.toLowerCase() ? 1 : 0;
        } else {
          r = compareIds(a.id, b.id);
        }
        return sortState.dir === "desc" ? -r : r;
      });

      tbody.textContent = "";
      rows.forEach(function (c) {
        var tr = el("tr");
        tr.appendChild(el("td", { "class": "ce-cell-id", "text": c.id }));

        var link = el("a", { "class": "ce-control-link", "href": base + c.url },
          c.title);
        tr.appendChild(el("td", null, [link]));

        tr.appendChild(el("td", null,
          [badge(c.pillarName || "\u2014", "ce-badge-pillar")]));

        var zoneCell = el("td");
        (c.zones || []).forEach(function (z) {
          zoneCell.appendChild(badge("Z" + z, "ce-badge-zone"));
        });
        if (!(c.zones || []).length) zoneCell.textContent = "\u2014";
        tr.appendChild(zoneCell);

        var regCell = el("td");
        if ((c.regulations || []).length) {
          c.regulations.forEach(function (r) {
            if (PROPOSED_REGS[r]) {
              regCell.appendChild(badge(r + " (proposed)", "ce-badge-reg ce-badge-reg-proposed"));
            } else {
              regCell.appendChild(badge(r, "ce-badge-reg"));
            }
          });
        } else {
          regCell.appendChild(badge("unspecified", "ce-badge-muted"));
        }
        tr.appendChild(regCell);

        tbody.appendChild(tr);
      });

      // result count (live region)
      liveCount.textContent = rows.length + " of " + controls.length +
        " control" + (controls.length === 1 ? "" : "s") + " shown";
      emptyMsg.hidden = rows.length !== 0;

      // sort indicators + aria-sort
      [thId, thTitle].forEach(function (th) {
        var active = sortState.sort === th._key;
        th.setAttribute("aria-sort", active ?
          (sortState.dir === "asc" ? "ascending" : "descending") : "none");
        th._ind.textContent = active ?
          (sortState.dir === "asc" ? " \u25B2" : " \u25BC") : "";
      });
    }

    function update() {
      state.search = searchInput.value;
      state.pillar = facetState.pillar;
      state.zone = facetState.zone;
      state.reg = facetState.reg;
      state.role = facetState.role;
      state.auto = facetState.auto;
      state.sort = sortState.sort;
      state.dir = sortState.dir;
      writeState(state);
      paint();
    }

    var searchTimer = null;
    searchInput.addEventListener("input", function () {
      if (searchTimer) window.clearTimeout(searchTimer);
      searchTimer = window.setTimeout(update, 120);
    });

    // ---- assemble layout ----
    var sidebar = el("div", { "class": "ce-sidebar" }, [
      el("h2", { "class": "ce-sidebar-title", "text": "Filters" }),
      resetBtn,
      facets
    ]);
    var results = el("div", { "class": "ce-results" }, [
      liveCount, table, emptyMsg
    ]);
    var layout = el("div", { "class": "ce-layout" }, [sidebar, results]);

    container.appendChild(searchWrap);
    container.appendChild(layout);

    paint();
  }

  // ---- boot ----
  function init() {
    var container = document.getElementById(CONTAINER_ID);
    if (!container || container.getAttribute("data-ce-ready") === "1") {
      if (container) {
        // re-init for instant navigation: clear stale ready flag and rebuild
        container.removeAttribute("data-ce-ready");
      } else {
        return;
      }
    }
    if (!container) return;

    var base = resolveBase();
    fetch(base + DATA_FILE, { credentials: "same-origin" })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (data) {
        var controls = Array.isArray(data) ? data : (data.controls || []);
        container.setAttribute("data-ce-ready", "1");
        render(container, controls);
      })
      .catch(function (err) {
        container.textContent = "";
        container.appendChild(el("p", { "class": "ce-error",
          "text": "Unable to load the control catalog. Please refresh the page." }));
        if (window.console) window.console.error("Control Explorer:", err);
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
