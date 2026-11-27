/*
 * Change Radar — client-side renderer (progressive enhancement).
 *
 * Fetches docs/javascripts/change-radar-data.json (generated from
 * data/change-radar/items.json by scripts/gen_change_radar_data.py) and renders
 * an accessible, filterable feed of Microsoft 365 agent-platform roadmap changes
 * mapped to FSI Agent Governance controls.
 *
 * Design notes:
 *  - CSP-safe: external file (no inline handlers), no external resources, DOM
 *    built via createElement/textContent (never innerHTML with feed data).
 *  - Accessible: labelled controls, role="status" staleness + count live regions,
 *    a semantic list of <article> cards, keyboard-operable native inputs/links.
 *  - Staleness guard: a visible "as of" date, escalating to a warning when the
 *    feed has not been regenerated within STALE_DAYS.
 */
(function () {
  "use strict";

  var CONTAINER_ID = "change-radar-feed";
  var DATA_FILE = "javascripts/change-radar-data.json";
  var SCRIPT_MARK = "change-radar.js";
  var STALE_DAYS = 45; // curated feed cadence is monthly; warn past ~6 weeks.

  function resolveBase() {
    var scripts = document.querySelectorAll("script[src]");
    for (var i = 0; i < scripts.length; i++) {
      var abs = scripts[i].src || scripts[i].getAttribute("src") || "";
      if (abs.indexOf(SCRIPT_MARK) !== -1) {
        var marker = "/javascripts/";
        var idx = abs.indexOf(marker);
        if (idx !== -1) return abs.slice(0, idx + 1);
      }
    }
    return new URL(".", document.baseURI).href;
  }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === "text") node.textContent = attrs[k];
        else if (k === "class") node.className = attrs[k];
        else node.setAttribute(k, attrs[k]);
      });
    }
    if (children) {
      (Array.isArray(children) ? children : [children]).forEach(function (c) {
        if (c == null) return;
        node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
      });
    }
    return node;
  }

  function uniqueSorted(values) {
    var seen = {};
    var out = [];
    values.forEach(function (v) {
      if (v && !seen[v]) { seen[v] = 1; out.push(v); }
    });
    out.sort();
    return out;
  }

  // Numeric sort for dotted control IDs so "1.7" precedes "1.14".
  function cmpControlId(a, b) {
    var pa = a.split(".").map(Number), pb = b.split(".").map(Number);
    return (pa[0] - pb[0]) || ((pa[1] || 0) - (pb[1] || 0));
  }

  function formatDate(iso) {
    var d = new Date(iso);
    if (isNaN(d.getTime())) return iso || "unknown";
    return d.toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
  }

  function daysSince(iso) {
    var d = new Date(iso);
    if (isNaN(d.getTime())) return null;
    return Math.floor((Date.now() - d.getTime()) / 86400000);
  }

  // Bucket an item's GA month (YYYY-MM) into a timeframe relative to today.
  function classifyTimeframe(gaDate) {
    if (!gaDate) return "later";
    var d = new Date(gaDate + "-01T00:00:00Z");
    if (isNaN(d.getTime())) return "later";
    var now = Date.now();
    if (d.getTime() <= now) return "ga";
    return d.getTime() <= now + 90 * 86400000 ? "soon" : "later";
  }

  function statusModifier(status) {
    return (status || "").toLowerCase().indexOf("develop") !== -1 ? "cr-badge--planned" : "cr-badge--available";
  }

  function buildStaleness(generatedAt) {
    var age = daysSince(generatedAt);
    var stale = age != null && age > STALE_DAYS;
    var banner = el("div", {
      "class": "cr-staleness" + (stale ? " cr-staleness--warn" : ""),
      "role": "note"
    });
    if (stale) {
      banner.appendChild(el("strong", { text: "This feed may be out of date. " }));
      banner.appendChild(document.createTextNode(
        "Last curated " + formatDate(generatedAt) + " (" + age + " days ago). Verify items against the Microsoft 365 roadmap."
      ));
    } else {
      banner.appendChild(el("strong", { text: "Curated as of " + formatDate(generatedAt) + "." }));
      banner.appendChild(document.createTextNode(" Filter and search the watch list below."));
    }
    return banner;
  }

  function labelledSelect(id, labelText, options) {
    var sel = el("select", { "id": id, "class": "cr-select md-select" });
    options.forEach(function (opt) {
      sel.appendChild(el("option", { "value": opt.value, "text": opt.label }));
    });
    var wrap = el("div", { "class": "cr-field" }, [
      el("label", { "for": id, "text": labelText }),
      sel
    ]);
    return { wrap: wrap, select: sel };
  }

  function controlChip(ctrl) {
    var href = ctrl.url || "#";
    var link = el("a", {
      "class": "cr-chip",
      "href": href,
      "title": ctrl.rationale || (ctrl.id + " " + (ctrl.title || ""))
    }, [
      el("span", { "class": "cr-chip__id", text: ctrl.id }),
      el("span", { "class": "cr-chip__title", text: ctrl.title || "" })
    ]);
    return link;
  }

  function card(item) {
    var titleLink = el("a", {
      "href": item.roadmapUrl || "#",
      "target": "_blank",
      "rel": "noopener noreferrer"
    }, [item.title || "Untitled change",
        el("span", { "class": "cr-ext", "aria-hidden": "true", text: " \u2197" }),
        el("span", { "class": "cr-visually-hidden", text: " (opens in new tab)" })]);

    var head = el("div", { "class": "cr-card__head" }, [
      el("h4", { "class": "cr-card__title" }, [titleLink]),
      el("span", { "class": "cr-badge " + statusModifier(item.status), text: item.status || "" })
    ]);

    var meta = el("p", { "class": "cr-card__meta" }, [
      item.timing ? el("span", { "class": "cr-card__timing", text: item.timing }) : null,
      (item.products && item.products.length)
        ? el("span", { "class": "cr-card__products", text: item.products.join(", ") })
        : null
    ]);

    var controls = el("div", { "class": "cr-card__controls" });
    controls.appendChild(el("span", { "class": "cr-card__label", text: "Affected controls: " }));
    (item.controls || []).forEach(function (c) { controls.appendChild(controlChip(c)); });

    var review = el("p", { "class": "cr-card__review" }, [
      el("span", { "class": "cr-card__label", text: "What to review: " }),
      document.createTextNode(item.whatToReview || "")
    ]);

    return el("li", { "class": "cr-card" }, [
      el("article", { "class": "cr-card__inner", "aria-label": item.title || "Change" }, [
        head,
        controls,
        review,
        el("p", { "class": "cr-card__summary", text: item.summary || "" }),
        meta
      ])
    ]);
  }

  function render(container, doc) {
    var items = (doc && doc.items) || [];
    container.textContent = "";

    container.appendChild(buildStaleness(doc && doc.generatedAt));

    container.appendChild(el("h2", { "class": "cr-heading", "id": "cr-heading", text: "Roadmap watch" }));

    // ---- filter controls ----
    var statuses = uniqueSorted(items.map(function (i) { return i.status; }));
    var pillars = uniqueSorted(items.reduce(function (acc, i) { return acc.concat(i.pillars || []); }, []));
    var regulations = uniqueSorted(items.reduce(function (acc, i) { return acc.concat(i.regulations || []); }, []));
    var products = uniqueSorted(items.reduce(function (acc, i) { return acc.concat(i.products || []); }, []));
    var controlIds = items.reduce(function (acc, i) {
      return acc.concat((i.controls || []).map(function (c) { return c.id; }));
    }, []).filter(function (v, idx, arr) { return arr.indexOf(v) === idx; }).sort(cmpControlId);

    var search = el("input", {
      "id": "cr-search", "type": "search", "class": "cr-input",
      "placeholder": "e.g. audit, sharing, 1.7",
      "autocomplete": "off"
    });
    var searchField = el("div", { "class": "cr-field cr-field--grow" }, [
      el("label", { "for": "cr-search", "text": "Search changes" }), search
    ]);

    function opts(values, allLabel, fmt) {
      return [{ value: "", label: allLabel }].concat(values.map(function (v) {
        return { value: v, label: fmt ? fmt(v) : v };
      }));
    }
    var pillarSel = labelledSelect("cr-pillar", "Pillar", opts(pillars, "All pillars"));
    var regSel = labelledSelect("cr-regulation", "Regulation", opts(regulations, "All regulations"));
    var statusSel = labelledSelect("cr-status", "Status", opts(statuses, "All statuses"));
    var timeframeSel = labelledSelect("cr-timeframe", "GA timeframe", [
      { value: "", label: "Any timeframe" },
      { value: "ga", label: "Already GA" },
      { value: "soon", label: "Next 90 days" },
      { value: "later", label: "Later" }
    ]);
    var controlSel = labelledSelect("cr-control", "Affected control", opts(controlIds, "All controls", function (c) { return "Control " + c; }));
    var productSel = labelledSelect("cr-product", "Product", opts(products, "All products"));
    // Compliance-relevant facets lead; Product is an admin/dev axis, so it trails.
    var selects = [pillarSel, regSel, statusSel, timeframeSel, controlSel, productSel];
    var urlKeys = { pillar: pillarSel, regulation: regSel, status: statusSel, timeframe: timeframeSel, control: controlSel, product: productSel };

    var toolbar = el("div", { "class": "cr-toolbar", "role": "search", "aria-label": "Filter Change Radar" }, [
      searchField, pillarSel.wrap, regSel.wrap, statusSel.wrap, timeframeSel.wrap, controlSel.wrap, productSel.wrap
    ]);

    var count = el("p", { "class": "cr-count", "role": "status", "aria-live": "polite" });
    var groups = el("div", { "class": "cr-groups" });
    var clearBtn = el("button", { "type": "button", "class": "cr-clear", text: "Clear all filters" });
    var empty = el("p", { "class": "cr-empty", "hidden": "hidden" }, [
      document.createTextNode("No changes match your filters. "), clearBtn
    ]);

    function matches(item, term, f) {
      if (f.status && item.status !== f.status) return false;
      if (f.pillar && (item.pillars || []).indexOf(f.pillar) === -1) return false;
      if (f.regulation && (item.regulations || []).indexOf(f.regulation) === -1) return false;
      if (f.product && (item.products || []).indexOf(f.product) === -1) return false;
      if (f.control && (item.controls || []).map(function (c) { return c.id; }).indexOf(f.control) === -1) return false;
      if (f.timeframe && classifyTimeframe(item.gaDate) !== f.timeframe) return false;
      if (term) {
        var hay = [
          item.title, item.summary, item.whatToReview,
          (item.products || []).join(" "), (item.pillars || []).join(" "), (item.regulations || []).join(" "),
          (item.controls || []).map(function (c) { return c.id + " " + (c.title || ""); }).join(" ")
        ].join(" ").toLowerCase();
        if (hay.indexOf(term) === -1) return false;
      }
      return true;
    }

    function renderGroup(label, arr) {
      if (!arr.length) return;
      var ul = el("ul", { "class": "cr-list", "aria-label": label });
      arr.forEach(function (it) { ul.appendChild(card(it)); });
      groups.appendChild(el("section", { "class": "cr-group" }, [
        el("h3", { "class": "cr-group__heading", text: label + " (" + arr.length + ")" }),
        ul
      ]));
    }

    function apply() {
      var term = search.value.trim().toLowerCase();
      var f = {};
      Object.keys(urlKeys).forEach(function (k) { f[k] = urlKeys[k].select.value; });
      var matched = items.filter(function (item) { return matches(item, term, f); });
      var available = matched.filter(function (i) { return statusModifier(i.status) === "cr-badge--available"; });
      var coming = matched.filter(function (i) { return statusModifier(i.status) !== "cr-badge--available"; });
      // Available: newest GA first; Coming: soonest GA first.
      available.sort(function (a, b) { return (b.gaDate || "").localeCompare(a.gaDate || ""); });
      coming.sort(function (a, b) { return (a.gaDate || "").localeCompare(b.gaDate || ""); });
      groups.textContent = "";
      renderGroup("Available now", available);
      renderGroup("Coming soon", coming);
      empty.hidden = matched.length !== 0;
      count.textContent = "Showing " + matched.length + " of " + items.length + " change" + (items.length === 1 ? "" : "s") + ".";
      writeUrlState();
    }

    function writeUrlState() {
      var params = new URLSearchParams();
      if (search.value.trim()) params.set("q", search.value.trim());
      Object.keys(urlKeys).forEach(function (k) {
        var v = urlKeys[k].select.value;
        if (v) params.set(k, v);
      });
      var qs = params.toString();
      try { history.replaceState(null, "", qs ? "?" + qs : location.pathname + location.hash); } catch (e) { /* history unavailable */ }
    }

    function readUrlState() {
      var params = new URLSearchParams(location.search);
      var q = params.get("q");
      if (q) search.value = q;
      Object.keys(urlKeys).forEach(function (k) {
        var v = params.get(k);
        if (!v) return;
        var sel = urlKeys[k].select;
        var ok = [].some.call(sel.options, function (o) { return o.value === v; });
        if (ok) sel.value = v;
      });
    }

    function clearAll() {
      search.value = "";
      selects.forEach(function (s) { s.select.value = ""; });
      apply();
      search.focus();
    }

    search.addEventListener("input", apply);
    selects.forEach(function (s) { s.select.addEventListener("change", apply); });
    clearBtn.addEventListener("click", clearAll);

    var region = el("div", { "class": "cr-results", "role": "region", "aria-labelledby": "cr-heading" }, [
      count, empty, groups
    ]);

    container.appendChild(toolbar);
    container.appendChild(region);
    readUrlState();
    apply();
  }

  function init() {
    var container = document.getElementById(CONTAINER_ID);
    if (!container) return;
    if (container.getAttribute("data-cr-ready") === "1") {
      container.removeAttribute("data-cr-ready");
    }
    var base = resolveBase();
    fetch(base + DATA_FILE, { credentials: "same-origin" })
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(function (doc) {
        container.setAttribute("data-cr-ready", "1");
        render(container, doc);
      })
      .catch(function (err) {
        container.textContent = "";
        container.appendChild(el("div", { "class": "cr-staleness cr-staleness--warn", "role": "alert" }, [
          el("strong", { text: "The Change Radar feed could not be loaded. " }),
          document.createTextNode("Please refresh, or browse the "),
          el("a", { "href": "https://www.microsoft.com/microsoft-365/roadmap" }, ["Microsoft 365 roadmap"]),
          document.createTextNode(" directly. (" + (err && err.message ? err.message : "error") + ")")
        ]));
      });
  }

  if (typeof window !== "undefined" && window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
