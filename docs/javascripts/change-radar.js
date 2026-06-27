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

  var CONTAINER_ID = "change-radar";
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

  function statusModifier(status) {
    return (status || "").toLowerCase().indexOf("develop") !== -1 ? "cr-badge--planned" : "cr-badge--available";
  }

  function buildStaleness(generatedAt) {
    var age = daysSince(generatedAt);
    var stale = age != null && age > STALE_DAYS;
    var banner = el("div", {
      "class": "cr-staleness" + (stale ? " cr-staleness--warn" : ""),
      "role": "status"
    });
    if (stale) {
      banner.appendChild(el("strong", { text: "This feed may be out of date. " }));
      banner.appendChild(document.createTextNode(
        "Last curated " + formatDate(generatedAt) + " (" + age + " days ago). Verify items against the Microsoft 365 roadmap."
      ));
    } else {
      banner.appendChild(el("strong", { text: "Curated as of " + formatDate(generatedAt) + ". " }));
      banner.appendChild(document.createTextNode(
        "Mappings are community-suggested and maintainer-reviewed; verify against your own control set and Microsoft's official notice."
      ));
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
        el("span", { "class": "cr-ext", "aria-hidden": "true", text: " \u2197" })]);

    var head = el("div", { "class": "cr-card__head" }, [
      el("h3", { "class": "cr-card__title" }, [titleLink]),
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
        el("p", { "class": "cr-card__summary", text: item.summary || "" }),
        meta,
        controls,
        review
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
    var products = uniqueSorted(items.reduce(function (acc, i) {
      return acc.concat(i.products || []);
    }, []));
    var controlIds = uniqueSorted(items.reduce(function (acc, i) {
      return acc.concat((i.controls || []).map(function (c) { return c.id; }));
    }, []));

    var search = el("input", {
      "id": "cr-search", "type": "search", "class": "cr-input",
      "placeholder": "e.g. audit, sharing, 1.7",
      "autocomplete": "off"
    });
    var searchField = el("div", { "class": "cr-field cr-field--grow" }, [
      el("label", { "for": "cr-search", "text": "Search changes" }), search
    ]);

    var statusSel = labelledSelect("cr-status", "Status",
      [{ value: "", label: "All statuses" }].concat(statuses.map(function (s) { return { value: s, label: s }; })));
    var productSel = labelledSelect("cr-product", "Product",
      [{ value: "", label: "All products" }].concat(products.map(function (p) { return { value: p, label: p }; })));
    var controlSel = labelledSelect("cr-control", "Affected control",
      [{ value: "", label: "All controls" }].concat(controlIds.map(function (c) { return { value: c, label: "Control " + c }; })));

    var toolbar = el("div", { "class": "cr-toolbar", "role": "search", "aria-label": "Filter Change Radar" }, [
      searchField, statusSel.wrap, productSel.wrap, controlSel.wrap
    ]);

    var count = el("p", { "class": "cr-count", "role": "status", "aria-live": "polite" });
    var list = el("ul", { "class": "cr-list", "aria-label": "Roadmap changes" });
    var empty = el("p", { "class": "cr-empty", "hidden": "hidden", text: "No changes match your filters." });

    function apply() {
      var term = search.value.trim().toLowerCase();
      var fStatus = statusSel.select.value;
      var fProduct = productSel.select.value;
      var fControl = controlSel.select.value;
      var shown = 0;
      list.textContent = "";
      items.forEach(function (item) {
        if (fStatus && item.status !== fStatus) return;
        if (fProduct && (item.products || []).indexOf(fProduct) === -1) return;
        if (fControl && (item.controls || []).map(function (c) { return c.id; }).indexOf(fControl) === -1) return;
        if (term) {
          var hay = [
            item.title, item.summary, item.whatToReview,
            (item.products || []).join(" "),
            (item.controls || []).map(function (c) { return c.id + " " + (c.title || ""); }).join(" ")
          ].join(" ").toLowerCase();
          if (hay.indexOf(term) === -1) return;
        }
        list.appendChild(card(item));
        shown++;
      });
      empty.hidden = shown !== 0;
      count.textContent = "Showing " + shown + " of " + items.length + " change" + (items.length === 1 ? "" : "s") + ".";
    }

    [search].forEach(function (n) { n.addEventListener("input", apply); });
    [statusSel.select, productSel.select, controlSel.select].forEach(function (n) {
      n.addEventListener("change", apply);
    });

    var region = el("div", { "class": "cr-results", "role": "region", "aria-labelledby": "cr-heading" }, [
      count, empty, list
    ]);

    container.appendChild(toolbar);
    container.appendChild(region);
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
