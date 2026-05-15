/**
 * FSI-AgentGov Governance Readiness Assessment Tool
 *
 * Client-side SPA that walks users through a scoped assessment of the
 * 78-control governance framework and produces scorecards, gap analysis,
 * and remediation roadmaps.
 *
 * @version 1.0.0
 */
(function () {
  "use strict";

  /* ================================================================
     CONSTANTS
     ================================================================ */
  var STORAGE_KEY = "fsi-agentgov-assessment";
  var STEPS = [
    { id: "welcome", label: "Welcome", num: 1 },
    { id: "scoping", label: "Scoping", num: 2 },
    { id: "phase1", label: "Phase 1", num: 3 },
    { id: "phase2", label: "Phase 2", num: 4 },
    { id: "results", label: "Results", num: 5 },
    { id: "export", label: "Export", num: 6 },
  ];
  var ANSWERS = [
    { value: "yes", label: "Yes", cls: "selected" },
    { value: "partial", label: "Partial", cls: "selected-partial" },
    { value: "no", label: "No", cls: "selected-no" },
    { value: "na", label: "N/A", cls: "selected" },
  ];

  /* ---- v1.4 Phase B constants (E1–E9) ---- */
  var SOLUTIONS_BASE_URL = "https://judeper.github.io/FSI-AgentGov-Solutions/solutions/";
  var STARTER_PRIORITY_IDS = ["2.1", "1.4", "1.5", "1.7", "1.11"];

  /* ---- v1.4.1 export envelope constants ----
   * FRAMEWORK_VERSION: kept in sync manually with package.json + mkdocs.yml.
   * EXPORT_SCHEMA_VERSION: bump on any breaking change to exportJSON output shape.
   * Downstream tools (e.g. FSI-Assessment-Agent) key off both fields to detect drift.
   */
  var FRAMEWORK_VERSION = "1.6.2";
  var EXPORT_SCHEMA_VERSION = 1;
  var ROLE_FILTER_KEY = "ag.roleFilter";
  var SECTOR_KEY = "ag.selectedSector";
  var ROLE_FILTER_OPTIONS = [
    { value: "", labelKey: "filter.role.all", fallback: "All roles" },
    { value: "Power Platform Admin" },
    { value: "Purview Compliance Admin" },
    { value: "Security Admin" },
    { value: "SharePoint Admin" },
    { value: "Entra Global Admin" },
    { value: "Compliance Officer" },
    { value: "Governance Lead" },
    { value: "Other" },
  ];
  var SECTOR_OPTIONS = [
    { value: "", labelKey: "scoping.sector.placeholder", fallback: "Select institution type…" },
    { value: "bank", labelKey: "scoping.sector.bank", fallback: "Bank" },
    { value: "broker-dealer", labelKey: "scoping.sector.brokerDealer", fallback: "Broker-dealer" },
    { value: "investment-adviser", labelKey: "scoping.sector.investmentAdviser", fallback: "Investment adviser" },
    { value: "insurance-carrier", labelKey: "scoping.sector.insuranceCarrier", fallback: "Insurance carrier" },
    { value: "insurance-wholesale", labelKey: "scoping.sector.insuranceWholesale", fallback: "Insurance wholesale/broker" },
    { value: "credit-union", labelKey: "scoping.sector.creditUnion", fallback: "Credit union" },
    { value: "holding-company", labelKey: "scoping.sector.holdingCompany", fallback: "Holding company" },
    { value: "other", labelKey: "scoping.sector.other", fallback: "Other" },
  ];

  /* ---- i18n ---- */
  var I18N = {};
  function t(key, fallback) {
    if (I18N && Object.prototype.hasOwnProperty.call(I18N, key)) return I18N[key];
    return fallback != null ? fallback : key;
  }
  function tFmt(key, fallback, vars) {
    var s = t(key, fallback);
    if (!vars) return s;
    return s.replace(/\{(\w+)\}/g, function (_, k) {
      return Object.prototype.hasOwnProperty.call(vars, k) ? String(vars[k]) : "{" + k + "}";
    });
  }
  function isFacilitatorMode() {
    try {
      return /[?&]mode=facilitate(\b|&|$)/.test(window.location.search);
    } catch (e) { return false; }
  }

  /* ================================================================
     UTILITY HELPERS
     ================================================================ */
  function h(tag, attrs, children) {
    var el = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v === null || v === undefined) return; // Skip null/undefined
        if (k === "className") el.className = v;
        else if (k.indexOf("on") === 0)
          el.addEventListener(k.slice(2).toLowerCase(), v);
        else if (k === "htmlFor") el.setAttribute("for", v);
        else el.setAttribute(k, v);
      });
    }
    if (children !== undefined && children !== null) {
      if (Array.isArray(children)) {
        children.forEach(function (c) {
          if (c == null) return;
          el.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
        });
      } else if (typeof children === "string") {
        el.textContent = children;
      } else {
        el.appendChild(children);
      }
    }
    return el;
  }

  function uuid() {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      var r = (Math.random() * 16) | 0;
      return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
    });
  }

  function fmtDate(iso) {
    if (!iso) return "—";
    var d = new Date(iso);
    return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }

  function ragClass(pct) {
    if (pct >= 80) return "green";
    if (pct >= 50) return "amber";
    return "red";
  }

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  function debounce(fn, ms) {
    var timer;
    return function () {
      var ctx = this, args = arguments;
      clearTimeout(timer);
      timer = setTimeout(function () { fn.apply(ctx, args); }, ms);
    };
  }

  /** Sanitize a string for CSV/Excel to prevent formula injection.
   *  IMPORTANT: strip BOM/zero-width prefix BEFORE testing the leading char so
   *  attackers can't bypass the check via "\uFEFF=cmd|...". After stripping,
   *  if the cell starts with =, +, -, @, TAB, CR, or LF prefix with a TAB so
   *  Excel/Sheets treat it as text. */
  function sanitizeCell(val) {
    if (typeof val !== "string") return val;
    var stripped = val.replace(/^[\uFEFF\u200B\u200C\u200D]+/, "");
    if (/^[=+\-@\t\r\n]/.test(stripped)) return "\t" + stripped;
    return stripped;
  }

  /** Build an Excel numeric percent cell from a 0..1 fraction.
   *  Returns "" (empty cell) for null/undefined/non-finite inputs.
   *  Out-of-range fractions are clamped to [0, 1] so a forgotten /100 conversion
   *  cannot produce a wildly-wrong "7500%" display in customer-facing reports.
   *  Cells emitted this way are SUM/AVERAGE-aggregable in Excel pivot tables;
   *  string-typed "75%" cells are not. */
  function pctCell(frac) {
    if (frac === null || frac === undefined) return "";
    if (typeof frac !== "number" || !isFinite(frac)) return "";
    var v = frac < 0 ? 0 : frac > 1 ? 1 : frac;
    return { v: v, t: "n", z: "0%" };
  }

  // ---- Collector payload validation (security) --------------------------
  // Note: object-literal `__proto__` sets the prototype rather than an own
  // property. Use Object.create(null) + bracket assignment so the key lookup
  // via hasOwnProperty matches the string "__proto__".
  var _COLLECTOR_FORBIDDEN_KEYS = Object.create(null);
  _COLLECTOR_FORBIDDEN_KEYS["__proto__"] = 1;
  _COLLECTOR_FORBIDDEN_KEYS["constructor"] = 1;
  _COLLECTOR_FORBIDDEN_KEYS["prototype"] = 1;
  var _COLLECTOR_AUTOMATION = { automated: 1, manual: 1, hybrid: 1 };
  function validateCollectorPayload(p) {
    if (!p || typeof p !== "object" || Array.isArray(p)) return false;
    var keys = Object.keys(p);
    for (var i = 0; i < keys.length; i++) {
      if (Object.prototype.hasOwnProperty.call(_COLLECTOR_FORBIDDEN_KEYS, keys[i])) return false;
    }
    if (typeof p.controlId !== "string" || !/^\d+\.\d+$/.test(p.controlId)) return false;
    if (p.evidenceRef !== undefined &&
        (typeof p.evidenceRef !== "string" || p.evidenceRef.length > 500)) return false;
    if (p.notes !== undefined &&
        (typeof p.notes !== "string" || p.notes.length > 2000)) return false;
    if (p.automationStatus !== undefined &&
        (typeof p.automationStatus !== "string" ||
         !Object.prototype.hasOwnProperty.call(_COLLECTOR_AUTOMATION, p.automationStatus))) return false;
    for (var j = 0; j < keys.length; j++) {
      var v = p[keys[j]];
      if (typeof v === "string" && /<script/i.test(v)) return false;
    }
    return true;
  }

  // Recursively check for __proto__/constructor/prototype OWN keys (depth-bounded).
  function _hasForbiddenKey(node, depth) {
    if (depth === undefined) depth = 0;
    if (depth > 32) return false;
    if (!node || typeof node !== "object") return false;
    var keys = Object.keys(node);
    for (var i = 0; i < keys.length; i++) {
      if (Object.prototype.hasOwnProperty.call(_COLLECTOR_FORBIDDEN_KEYS, keys[i])) return true;
      if (_hasForbiddenKey(node[keys[i]], depth + 1)) return true;
    }
    return false;
  }

  // Field-by-field copy of an allowlisted drilldown response.
  var _DRILL_SEVERITY = { low: 1, medium: 1, high: 1, critical: 1 };
  function _safeCopyDrilldown(src) {
    if (!src || typeof src !== "object" || Array.isArray(src)) return null;
    if (Object.prototype.hasOwnProperty.call(src, "__proto__") ||
        Object.prototype.hasOwnProperty.call(src, "constructor") ||
        Object.prototype.hasOwnProperty.call(src, "prototype")) return null;
    var out = {};
    if (typeof src.notes === "string") out.notes = src.notes.slice(0, 2000);
    if (typeof src.evidenceRef === "string") out.evidenceRef = src.evidenceRef.slice(0, 500);
    if (typeof src.automationStatus === "string" &&
        Object.prototype.hasOwnProperty.call(_COLLECTOR_AUTOMATION, src.automationStatus)) {
      out.automationStatus = src.automationStatus;
    }
    if (typeof src.severity === "string" &&
        Object.prototype.hasOwnProperty.call(_DRILL_SEVERITY, src.severity)) {
      out.severity = src.severity;
    }
    Object.keys(src).forEach(function (k) {
      if (k === "notes" || k === "evidenceRef" || k === "automationStatus" || k === "severity") return;
      if (Object.prototype.hasOwnProperty.call(_COLLECTOR_FORBIDDEN_KEYS, k)) return;
      var v = src[k];
      if (v === "yes" || v === "no") out[k] = v;
    });
    return out;
  }

  // Tiny FNV-1a 32-bit hash for deterministic filename suffixes.
  function _shortHash(s) {
    s = String(s);
    var h = 0x811c9dc5;
    for (var i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) >>> 0;
    }
    return ("00000000" + h.toString(16)).slice(-8);
  }

  function _truncateFilename(stem) {
    var s = String(stem || "");
    if (s.length <= 80) return s;
    return s.slice(0, 80) + "-" + _shortHash(s);
  }

  function downloadBlob(blob, filename) {
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  }

  function getBasePath() {
    // Calculate base path for playbook links relative to site root
    var path = window.location.pathname;
    // If we're at /FSI-AgentGov/assessment/ then base is /FSI-AgentGov/
    var match = path.match(/^(\/[^/]*\/)/);
    return match ? match[1] : "/";
  }

  /**
   * Normalize a manifest URL so it resolves correctly when the site is
   * published under a project-page sub-path (e.g. /FSI-AgentGov/).
   *
   * The manifest stores absolute paths like "/playbooks/..." which the
   * browser would resolve to https://judeper.github.io/playbooks/...
   * (404). Prefix with the discovered base path to fix.
   *
   * Pass-through for empty values, fully-qualified URLs, and relative
   * paths (which already resolve correctly relative to the current page).
   */
  function withBasePath(url) {
    if (!url) return "";
    if (/^[a-z][a-z0-9+.-]*:\/\//i.test(url)) return url; // http(s):, mailto:, etc.
    if (url.charAt(0) !== "/") return url; // already relative
    return getBasePath().replace(/\/$/, "") + url;
  }

  /* ================================================================
     AssessmentApp CLASS
     ================================================================ */
  function AssessmentApp(container) {
    this.el = container;
    this.data = null;           // assessment-data.json contents
    this.state = null;          // current assessment state
    this.charts = [];           // Chart.js instances to destroy on cleanup
    this.step = "welcome";
    this._observers = [];
    this._savePrompted = false; // Track if save prompt has been shown
    this._debouncedSave = debounce(this.saveToStorage.bind(this), 500);
  }

  AssessmentApp.prototype.init = function () {
    var self = this;
    this._bindMaterialSearchGuard();
    this._injectPrintStyles();
    this._migrateLegacySavedAssessments();
    this.loadData().then(function () {
      self.render();
    });
  };

  /**
   * One-time migration: prior to the saved-list fix the SPA stored only the
   * single most recently edited assessment in `STORAGE_KEY + "-current"`.
   * Older entries shown in the welcome saved-assessments list pointed to
   * data that did not exist, so clicking "Resume" silently no-op'd.
   *
   * Per-assessment slots at `STORAGE_KEY + "-data-" + id` are now the source
   * of truth. On first run after deploy we copy the legacy `-current` blob
   * into its per-id slot if the slot is empty. We deliberately leave
   * `-current` in place so the migration is idempotent and a downgrade does
   * not lose data.
   */
  AssessmentApp.prototype._migrateLegacySavedAssessments = function () {
    try {
      var raw = localStorage.getItem(STORAGE_KEY + "-current");
      if (raw) {
        var parsed = JSON.parse(raw);
        if (parsed && typeof parsed === "object" && parsed.assessmentId) {
          var perIdKey = STORAGE_KEY + "-data-" + parsed.assessmentId;
          if (localStorage.getItem(perIdKey) == null) {
            localStorage.setItem(perIdKey, raw);
          }
        }
      }
    } catch (e) { /* migration is best-effort */ }
    // spa-fix-filter-namespace: one-shot migration of legacy global filter
    // keys (ROLE_FILTER_KEY, SECTOR_KEY) onto the per-assessment namespace
    // for the most-recent current assessment. If there is no current
    // assessment we discard the legacy keys to prevent leakage into a
    // newly-created assessment. Guarded by a flag so we run at most once.
    try {
      var migFlag = STORAGE_KEY + "-filter-migration-v1";
      if (localStorage.getItem(migFlag) === "1") return;
      var legacyRole = localStorage.getItem(ROLE_FILTER_KEY);
      var legacySector = localStorage.getItem(SECTOR_KEY);
      var curRaw = localStorage.getItem(STORAGE_KEY + "-current");
      var curId = null;
      if (curRaw) {
        try {
          var cur = JSON.parse(curRaw);
          if (cur && cur.assessmentId) curId = cur.assessmentId;
        } catch (_) { /* */ }
      }
      if (curId) {
        if (legacyRole != null &&
            localStorage.getItem(ROLE_FILTER_KEY + "-" + curId) == null) {
          localStorage.setItem(ROLE_FILTER_KEY + "-" + curId, legacyRole);
        }
        if (legacySector != null &&
            localStorage.getItem(SECTOR_KEY + "-" + curId) == null) {
          localStorage.setItem(SECTOR_KEY + "-" + curId, legacySector);
        }
      }
      // Always remove the global keys after migration to stop them leaking
      // into a freshly created assessment.
      if (legacyRole != null) localStorage.removeItem(ROLE_FILTER_KEY);
      if (legacySector != null) localStorage.removeItem(SECTOR_KEY);
      localStorage.setItem(migFlag, "1");
    } catch (e) { /* migration is best-effort */ }
  };

  // Inject @page + print-only CSS once per page (spa-fix-print-hygiene).
  AssessmentApp.prototype._injectPrintStyles = function () {
    if (typeof document === "undefined") return;
    if (document.getElementById("ag-print-styles")) return;
    var style = document.createElement("style");
    style.id = "ag-print-styles";
    style.textContent = "@page { margin: 1cm; size: letter; }\n" +
      "@media print {\n" +
      "  .ag-no-print { display: none !important; }\n" +
      "  header, .md-header, .md-tabs, .md-sidebar, .md-footer, footer { display: none !important; }\n" +
      "  body, .md-main, .md-main__inner, .md-content, .md-content__inner, .ag-content { margin: 0 !important; padding: 0 !important; max-width: none !important; }\n" +
      "  a[href]:after { content: none !important; }\n" +
      "}\n" +
      ".ag-quota-banner { position: sticky; top: 0; background: #fee; color: #800; padding: 8px 12px; z-index: 10000; border-bottom: 2px solid #800; display: flex; justify-content: space-between; align-items: center; gap: 1rem; }\n" +
      ".ag-quota-banner button { background: #800; color: #fff; border: 0; padding: 4px 10px; cursor: pointer; border-radius: 3px; }\n" +
      ".ag-phase2-rolefilter-banner { background: #fff8e1; color: #6d4c00; padding: 8px 12px; border-left: 4px solid #f59e0b; margin: 0 0 1rem; border-radius: 3px; }\n";
    if (document.head) document.head.appendChild(style);
    if (typeof window !== "undefined" && window.addEventListener) {
      var self = this;
      window.addEventListener("beforeprint", function () {
        self._origTitle = document.title;
        var org = (self.state && self.state.scoping && self.state.scoping.organizationName) || "";
        document.title = "FSI Agent Governance Assessment" + (org ? " — " + org : "");
      });
      window.addEventListener("afterprint", function () {
        if (self._origTitle) document.title = self._origTitle;
      });
    }
  };

  /**
   * Edit F — Prevent Material for MkDocs' global search shortcuts (s, /, f)
   * from stealing focus while the user is typing into an assessment field.
   *
   * Material binds these shortcuts on the document via a bubble-phase keydown
   * listener. We attach a CAPTURE-phase listener on the assessment container
   * so we see the event first; if the target is an editable element inside
   * the SPA, we stopPropagation() so Material's handler never fires. We
   * deliberately do NOT call preventDefault() — the keystroke must still
   * reach the input so the character gets typed.
   */
  AssessmentApp.prototype._bindMaterialSearchGuard = function () {
    if (!this.el || this._searchGuardBound) return;
    var container = this.el;
    var TRIGGER_KEYS = { "s": true, "/": true, "f": true };
    var handler = function (event) {
      var key = event.key;
      if (!key || !TRIGGER_KEYS[key.toLowerCase()]) return;
      // Ignore when modifier keys are pressed (real shortcuts like Ctrl+F).
      if (event.ctrlKey || event.metaKey || event.altKey) return;
      var target = event.target;
      if (!target || !target.matches) return;
      var isEditable =
        target.matches("input, textarea, select") ||
        target.isContentEditable ||
        (target.closest && target.closest("[contenteditable='true']"));
      if (!isEditable) return;
      if (!container.contains(target)) return;
      // Block Material's global handler; keep default behavior so the key
      // is typed into the field normally.
      event.stopPropagation();
    };
    container.addEventListener("keydown", handler, true);
    this._searchGuardHandler = handler;
    this._searchGuardBound = true;
  };

  AssessmentApp.prototype.destroy = function () {
    this.charts.forEach(function (c) { try { c.destroy(); } catch (e) { /* */ } });
    this.charts = [];
    this._observers.forEach(function (o) { try { o.disconnect(); } catch (e) { /* */ } });
    this._observers = [];
    if (this._searchGuardBound && this.el && this._searchGuardHandler) {
      this.el.removeEventListener("keydown", this._searchGuardHandler, true);
      this._searchGuardBound = false;
      this._searchGuardHandler = null;
    }
  };

  AssessmentApp.prototype.loadData = function () {
    var self = this;
    var base = "";
    var scripts = document.querySelectorAll('script[src*="assessment-loader"]');
    if (scripts.length) {
      var src = scripts[scripts.length - 1].src;
      base = src.substring(0, src.lastIndexOf("/") + 1);
    }
    // Resolve site root for /assessment/data/ assets.
    // base is .../javascripts/  (or absolute origin for mkdocs use_directory_urls).
    var siteRoot = base.replace(/javascripts\/?$/, "");
    var dataBase = siteRoot + "assessment/data/";
    var i18nBase = siteRoot + "assessment/i18n/";

    var fetchJSON = function (url, label) {
      // 8s timeout via AbortController + ONE retry on network/timeout failure
      // (spa-fix-fetch-resilience). cache:'no-store' so a stale CDN response
      // can't pin the SPA in a broken state.
      function attempt() {
        var controller = (typeof AbortController !== "undefined") ? new AbortController() : null;
        var timer = controller ? setTimeout(function () { controller.abort(); }, 8000) : null;
        var opts = { cache: "no-store" };
        if (controller) opts.signal = controller.signal;
        return fetch(url, opts).then(function (r) {
          if (timer) clearTimeout(timer);
          if (!r.ok) throw new Error(label + " HTTP " + r.status);
          return r.json();
        }, function (err) {
          if (timer) clearTimeout(timer);
          throw err;
        });
      }
      return attempt().catch(function (err) {
        // Don't retry an HTTP error like 404 — same URL would 404 again.
        if (err && /HTTP \d{3}/.test(String(err.message || ""))) throw err;
        return attempt();
      });
    };

    // Primary load: legacy assessment-data.json (still required for pillars,
    // regulatoryMappings, roleAssignments, adoptionPhases, etc.).
    var pData = fetchJSON(base + "assessment-data.json", "assessment-data.json")
      .then(function (d) { self.data = d; })
      .catch(function (err) {
        console.error(err);
        self.el.innerHTML =
          '<div class="admonition failure"><p class="admonition-title">Error</p>' +
          "<p>Could not load assessment data. Run <code>python scripts/extract_assessment_data.py</code> first.</p>" +
          '<p><button type="button" class="ag-btn ag-btn-primary" id="ag-retry-load">Retry</button></p></div>';
        var btn = self.el.querySelector("#ag-retry-load");
        if (btn) btn.addEventListener("click", function () { self.init(); });
        throw err;
      });

    // v1.4 Phase B: extended controls manifest (single source of truth for E1–E9 metadata).
    var pManifest = fetchJSON(dataBase + "controls.json", "controls.json")
      .then(function (m) { self.manifest = Array.isArray(m) ? m : (m && m.controls) || []; })
      .catch(function (err) {
        console.warn("loadControlsManifest:", err);
        self.manifest = [];
      });

    // v1.4 Phase B: solutions lock (chip metadata).
    var pSolutionsLock = fetchJSON(dataBase + "solutions-lock.json", "solutions-lock.json")
      .then(function (lock) {
        self.solutionsLock = (lock && typeof lock === "object")
          ? { schemaVersion: lock.schemaVersion || null, solutions: (lock.solutions && typeof lock.solutions === "object") ? lock.solutions : {} }
          : { schemaVersion: null, solutions: {} };
      })
      .catch(function (err) {
        console.warn("loadSolutionsLock:", err);
        self.solutionsLock = { schemaVersion: null, solutions: {} };
      });

    // v1.4 Phase B: i18n strings (English fallbacks live next to t() call sites).
    var pI18n = fetchJSON(i18nBase + "en.json", "i18n/en.json")
      .then(function (strings) {
        if (strings && typeof strings === "object") {
          Object.keys(strings).forEach(function (k) {
            if (k.charAt(0) !== "_" && typeof strings[k] === "string") I18N[k] = strings[k];
          });
        }
      })
      .catch(function (err) {
        console.warn("loadI18n:", err);
      });

    return pData.then(function () {
      // Wait for the optional resources but never let them block initialization.
      return Promise.all([pManifest, pSolutionsLock, pI18n]).then(function () {
        self.mergeManifestIntoControls();
        // O(1) lookup so getGapControls / applyRoleFilter / drilldown hot paths
        // don't linear-scan 78 controls per call (spa-fix-perf-loop).
        if (self.data && Array.isArray(self.data.controls)) {
          self.controlsById = new Map();
          self.data.controls.forEach(function (c) {
            if (c && c.id) self.controlsById.set(c.id, c);
          });
        }
      });
    });
  };

  /**
   * Merge v1.4 manifest fields (yesBar/partialBar/noBar/sectorYesBar/verifyIn/
   * verifyPowerShell/evidenceExpected/controlDocUrl/portalPlaybookUrl/solutions/
   * facilitatorNotes/zonesApplicable) onto the legacy control objects loaded
   * from assessment-data.json. Existing fields are preserved when the manifest
   * value is missing or a TODO placeholder.
   */
  AssessmentApp.prototype.mergeManifestIntoControls = function () {
    if (!this.data || !Array.isArray(this.data.controls)) return;
    if (!Array.isArray(this.manifest) || this.manifest.length === 0) return;
    var byId = {};
    this.manifest.forEach(function (m) { if (m && m.id) byId[m.id] = m; });
    this.data.controls.forEach(function (c) {
      var m = byId[c.id];
      if (!m) return;
      // Manifest is authoritative for these new fields.
      c.yesBar = m.yesBar || "";
      c.partialBar = m.partialBar || "";
      c.noBar = m.noBar || "";
      c.sectorYesBar = m.sectorYesBar || {};
      c.verifyIn = Array.isArray(m.verifyIn) ? m.verifyIn : [];
      c.verifyPowerShell = m.verifyPowerShell || "";
      c.evidenceExpected = Array.isArray(m.evidenceExpected) ? m.evidenceExpected : [];
      c.controlDocUrl = withBasePath(m.controlDocUrl || "");
      c.portalPlaybookUrl = withBasePath(m.portalPlaybookUrl || "");
      c.facilitatorNotes = m.facilitatorNotes || {};
      c.zonesApplicable = Array.isArray(m.zonesApplicable) && m.zonesApplicable.length
        ? m.zonesApplicable.slice() : (c.zones || [1, 2, 3]);
      // Prefer manifest solutions IDs (v1.4 source of truth) when non-empty.
      if (Array.isArray(m.solutions) && m.solutions.length) c.solutions = m.solutions.slice();
      // Roles: keep legacy assignedRoles for backward compat; expose manifest roles too.
      if (Array.isArray(m.roles) && m.roles.length) c.manifestRoles = m.roles.slice();
    });
  };

  /* ================================================================
     v1.4 PHASE B HELPERS — applicability, role filter, drawer, timer
     ================================================================ */

  /** True if `ctrl.zonesApplicable` does not intersect the active scoping zones. */
  AssessmentApp.prototype.isControlExcluded = function (ctrl) {
    if (!this.state) return false;
    var override = this.state.overrides && this.state.overrides[ctrl.id];
    if (override && override.applicable) return false;
    var activeZones = (this.state.scoping && this.state.scoping.zones) || [];
    if (!activeZones.length) return false;
    var applicable = ctrl.zonesApplicable || ctrl.zones || [1, 2, 3];
    for (var i = 0; i < applicable.length; i++) {
      if (activeZones.indexOf(applicable[i]) >= 0) return false;
    }
    return true;
  };

  /**
   * Auto-mark excluded controls as N/A. Idempotent — only flips controls that
   * have no answer yet (so user-set answers are preserved).
   */
  AssessmentApp.prototype.applyZoneExclusions = function () {
    if (!this.state || !this.data || !Array.isArray(this.data.controls)) return;
    var self = this;
    var changed = false;
    this.data.controls.forEach(function (c) {
      if (!self.isControlExcluded(c)) return;
      var resp = self.state.responses[c.id];
      if (!resp || !resp.answer) {
        self.state.responses[c.id] = {
          answer: "na",
          notes: resp ? (resp.notes || "") : "",
          evidenceRef: resp ? (resp.evidenceRef || "") : "",
          autoNa: true,
        };
        changed = true;
      }
    });
    if (changed) this._debouncedSave();
  };

  /** True if the supplied role filter matches the control's role list. */
  AssessmentApp.prototype.controlMatchesRoleFilter = function (ctrl, roleFilter) {
    if (!roleFilter) return true;
    var roles = (ctrl.manifestRoles && ctrl.manifestRoles.length)
      ? ctrl.manifestRoles
      : (ctrl.roles || ctrl.assignedRoles || []);
    if (!roles || !roles.length) return false;
    var rfLower = roleFilter.toLowerCase();
    for (var i = 0; i < roles.length; i++) {
      var r = String(roles[i] || "").toLowerCase();
      // Allow loose match (manifest roles may have parentheticals).
      if (r === rfLower) return true;
      if (r.indexOf(rfLower) === 0) return true;
      if (r.indexOf(rfLower) >= 0) return true;
    }
    return false;
  };

  /**
   * Render the per-row "How to verify" drawer body (E1). Lazy-called on first
   * open to keep initial Phase 1 render under 500ms.
   */
  AssessmentApp.prototype.renderDrawerContent = function (ctrl) {
    var self = this;
    var sector = this.state.selectedSector || "";
    var wrap = h("div", { className: "ag-drawer-inner" });

    // Pass / partial / fail criteria bars
    var hasBars = ctrl.yesBar || ctrl.partialBar || ctrl.noBar;
    if (hasBars) {
      var sec = h("div", { className: "ag-drawer-section" });
      sec.appendChild(h("h4", null, t("drawer.title", "How to verify")));
      var dl = h("dl", { className: "ag-drawer-bar" });
      if (ctrl.yesBar) {
        dl.appendChild(h("dt", { className: "bar-yes" }, t("drawer.yesBar", "Yes — pass criteria")));
        dl.appendChild(h("dd", null, ctrl.yesBar));
      }
      if (ctrl.partialBar) {
        dl.appendChild(h("dt", { className: "bar-partial" }, t("drawer.partialBar", "Partial — partial coverage criteria")));
        dl.appendChild(h("dd", null, ctrl.partialBar));
      }
      if (ctrl.noBar) {
        dl.appendChild(h("dt", { className: "bar-no" }, t("drawer.noBar", "No — gap criteria")));
        dl.appendChild(h("dd", null, ctrl.noBar));
      }
      sec.appendChild(dl);
      wrap.appendChild(sec);
    }

    // Sector-specific yesBar
    var sectorYes = "";
    if (sector && ctrl.sectorYesBar && typeof ctrl.sectorYesBar[sector] === "string") {
      var s = ctrl.sectorYesBar[sector];
      if (s && s.indexOf("TODO:") !== 0) sectorYes = s;
    }
    if (sectorYes) {
      var secSec = h("div", { className: "ag-drawer-section" });
      secSec.appendChild(h("h4", null, t("drawer.sectorYesBar", "Sector-specific pass criteria")));
      secSec.appendChild(h("p", { style: "margin:0;font-size:0.85rem" }, sectorYes));
      wrap.appendChild(secSec);
    }

    // Verify-in portal buttons
    if (Array.isArray(ctrl.verifyIn) && ctrl.verifyIn.length) {
      var portalSec = h("div", { className: "ag-drawer-section" });
      portalSec.appendChild(h("h4", null, t("drawer.verifyIn", "Verify in:")));
      var btns = h("div", { className: "ag-drawer-portal-btns" });
      ctrl.verifyIn.forEach(function (entry) {
        if (!entry) return;
        var url = typeof entry === "string" ? entry : entry.url;
        var label = typeof entry === "string" ? entry : (entry.label || entry.name || entry.url);
        if (!url) return;
        btns.appendChild(h("a", {
          className: "ag-drawer-portal-btn",
          href: url,
          target: "_blank",
          rel: "noopener noreferrer",
        }, label));
      });
      portalSec.appendChild(btns);
      wrap.appendChild(portalSec);
    }

    // PowerShell snippet
    if (ctrl.verifyPowerShell && String(ctrl.verifyPowerShell).trim() &&
        String(ctrl.verifyPowerShell).indexOf("TODO:") !== 0) {
      var psSec = h("div", { className: "ag-drawer-section" });
      var psHeader = h("h4", null, t("drawer.powershell", "PowerShell verification"));
      var copyBtn = h("button", {
        className: "ag-drawer-copy-btn",
        type: "button",
        "aria-label": t("drawer.copySnippet", "Copy") + " PowerShell snippet",
      }, t("drawer.copySnippet", "Copy"));
      psHeader.appendChild(copyBtn);
      psSec.appendChild(psHeader);
      var pre = h("pre", { className: "ag-drawer-pre" }, ctrl.verifyPowerShell);
      psSec.appendChild(pre);
      copyBtn.addEventListener("click", function () {
        var ok = false;
        try {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(ctrl.verifyPowerShell);
            ok = true;
          }
        } catch (e) { /* fall through */ }
        if (!ok) {
          // Fallback: select the <pre> text.
          var range = document.createRange();
          range.selectNodeContents(pre);
          var sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(range);
          try { document.execCommand("copy"); } catch (e2) { /* */ }
          sel.removeAllRanges();
        }
        copyBtn.textContent = t("drawer.copied", "Copied");
        setTimeout(function () { copyBtn.textContent = t("drawer.copySnippet", "Copy"); }, 1500);
      });
      wrap.appendChild(psSec);
    }

    // Evidence checklist
    if (Array.isArray(ctrl.evidenceExpected) && ctrl.evidenceExpected.length) {
      var evSec = h("div", { className: "ag-drawer-section" });
      evSec.appendChild(h("h4", null, t("drawer.evidence", "Evidence to capture")));
      var ul = h("ul", { className: "ag-drawer-evidence" });
      ctrl.evidenceExpected.forEach(function (item) {
        if (!item) return;
        ul.appendChild(h("li", null, String(item)));
      });
      evSec.appendChild(ul);
      wrap.appendChild(evSec);
    }

    // Doc + playbook links
    if (ctrl.controlDocUrl || ctrl.portalPlaybookUrl) {
      var linkSec = h("div", { className: "ag-drawer-section" });
      if (ctrl.controlDocUrl) {
        linkSec.appendChild(h("a", {
          className: "ag-drawer-link",
          href: ctrl.controlDocUrl,
          target: "_blank",
          rel: "noopener",
        }, t("drawer.viewControlDoc", "View full control doc") + " →"));
      }
      if (ctrl.portalPlaybookUrl) {
        linkSec.appendChild(h("a", {
          className: "ag-drawer-link",
          href: ctrl.portalPlaybookUrl,
          target: "_blank",
          rel: "noopener",
        }, t("drawer.portalPlaybook", "Portal playbook") + " →"));
      }
      wrap.appendChild(linkSec);
    }

    // Deployable solutions
    if (Array.isArray(ctrl.solutions) && ctrl.solutions.length) {
      var solSec = h("div", { className: "ag-drawer-section" });
      solSec.appendChild(h("h4", null, t("drawer.solutions", "Deployable solutions")));
      var lock = (this.solutionsLock && this.solutionsLock.solutions) || {};
      ctrl.solutions.forEach(function (sid) {
        if (!sid) return;
        var entry = lock[sid];
        if (entry && typeof entry === "object") {
          var chip = h("a", {
            className: "ag-solution-chip",
            href: SOLUTIONS_BASE_URL + encodeURIComponent(sid) + "/",
            target: "_blank",
            rel: "noopener noreferrer",
            title: sid,
          });
          chip.appendChild(document.createTextNode(entry.name || sid));
          if (entry.tier) {
            chip.appendChild(h("span", {
              className: "ag-tier-badge tier-" + entry.tier,
            }, entry.tier));
          }
          if (entry.version) {
            chip.appendChild(h("span", { className: "ag-version-pill" }, "v" + entry.version));
          }
          solSec.appendChild(chip);
        } else {
          solSec.appendChild(h("span", {
            className: "ag-solution-chip-pending",
            title: sid,
          }, sid + " " + t("drawer.solutionPending", "(no companion solution by design)")));
        }
      });
      wrap.appendChild(solSec);
    }

    if (!wrap.firstChild) {
      wrap.appendChild(h("p", { style: "font-size:0.82rem;color:var(--md-default-fg-color--light);margin:0" },
        "No verification metadata available for this control yet."));
    }

    return wrap;
  };

  /** Bind keyboard handling (Esc + Tab focus trap) for an open drawer. */
  AssessmentApp.prototype._bindDrawerKeyboard = function (drawer, toggleBtn) {
    var keyHandler = function (e) {
      if (e.key === "Escape") {
        e.preventDefault();
        drawer.classList.remove("ag-drawer-open");
        toggleBtn.setAttribute("aria-expanded", "false");
        toggleBtn.focus();
        return;
      }
      if (e.key === "Tab") {
        var focusables = drawer.querySelectorAll(
          'a[href],button:not([disabled]),textarea,input,select,[tabindex]:not([tabindex="-1"])'
        );
        if (!focusables.length) return;
        var first = focusables[0];
        var last = focusables[focusables.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    drawer.addEventListener("keydown", keyHandler);
  };

  /** Format mm:ss for the facilitator session timer. */
  function fmtTimer(secs) {
    var m = Math.floor(secs / 60);
    var s = secs % 60;
    return (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
  }

  /** Build (and persist) the facilitator session timer. */
  AssessmentApp.prototype.renderSessionTimer = function () {
    var self = this;
    if (!this._timer) this._timer = { secs: 0, running: false, intervalId: null };
    var wrap = h("div", { className: "ag-session-timer", role: "timer", "aria-label": t("facilitator.timerLabel", "Session timer") });
    wrap.appendChild(h("span", { style: "font-weight:600" }, t("facilitator.timerLabel", "Session timer") + ":"));
    var display = h("span", { className: "ag-session-timer-display" }, fmtTimer(self._timer.secs));
    wrap.appendChild(display);
    var startBtn = h("button", { type: "button" },
      self._timer.running ? t("facilitator.timerPause", "Pause") : (self._timer.secs > 0 ? t("facilitator.timerResume", "Resume") : t("facilitator.timerStart", "Start"))
    );
    var resetBtn = h("button", { type: "button" }, t("facilitator.timerReset", "Reset"));
    wrap.appendChild(startBtn);
    wrap.appendChild(resetBtn);

    var tick = function () {
      self._timer.secs++;
      display.textContent = fmtTimer(self._timer.secs);
    };
    var stop = function () {
      if (self._timer.intervalId) {
        clearInterval(self._timer.intervalId);
        self._timer.intervalId = null;
      }
      self._timer.running = false;
    };
    startBtn.addEventListener("click", function () {
      if (self._timer.running) {
        stop();
        startBtn.textContent = t("facilitator.timerResume", "Resume");
      } else {
        self._timer.running = true;
        self._timer.intervalId = setInterval(tick, 1000);
        startBtn.textContent = t("facilitator.timerPause", "Pause");
      }
    });
    resetBtn.addEventListener("click", function () {
      stop();
      self._timer.secs = 0;
      display.textContent = fmtTimer(0);
      startBtn.textContent = t("facilitator.timerStart", "Start");
    });
    // Cleanup on destroy
    this._observers.push({ disconnect: stop });
    return wrap;
  };


  /* ================================================================
     STATE MANAGEMENT
     ================================================================ */
  AssessmentApp.prototype.newState = function () {
    // spa-fix-filter-namespace: filter view-state is now per-assessment
    // (namespaced under ROLE_FILTER_KEY+"-"+id and SECTOR_KEY+"-"+id) so a
    // brand-new assessment must NOT inherit the previous assessment's
    // filter from the legacy global keys. Initialize empty; the user's
    // most recent per-assessment filters are restored in loadFromStorage.
    var savedRole = "";
    var savedSector = "";
    return {
      assessmentId: uuid(),
      assessmentName: "",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      scoping: {
        organizationName: "",
        assessorName: "",
        assessorRole: "",
        institutionType: "",
        zones: [1, 2, 3],
        adoptionPhase: 0,
        regulations: [],
        scope: "full",
      },
      // v1.4 Phase B additions
      selectedSector: savedSector,
      roleFilter: savedRole,
      priorityMode: "full",      // "starter" | "full"
      priorityExpanded: false,   // user clicked "Continue to full Phase 1"
      overrides: {},             // controlId → { applicable: true, note: "..." }
      responses: {},      // controlId → { answer, notes, evidenceRef }
      drilldown: {},      // controlId → { subQuestionId → answer }
      completedSteps: [],
    };
  };

  AssessmentApp.prototype.saveToStorage = function () {
    if (!this.state) return;
    this.state.updatedAt = new Date().toISOString();
    // spa-fix-resume-step: persist the wizard step alongside answers so
    // Resume restores the user to where they left off (scoping → phase1 →
    // phase2 → results → export). Do NOT overwrite a previously-saved
    // step with "welcome" — Resume by definition takes the user OUT of
    // welcome, so persisting "welcome" would erase the user's actual
    // working position when they click the welcome indicator.
    if (this.step && this.step !== "welcome") {
      this.state.step = this.step;
    }
    try {
      var serialized = JSON.stringify(this.state);
      // Per-assessment slot is the source of truth for restoration (iter3-2-001 P0).
      localStorage.setItem(STORAGE_KEY + "-data-" + this.state.assessmentId, serialized);
      // `-current` retained as a "most recently edited" pointer for back-compat.
      localStorage.setItem(STORAGE_KEY + "-current", serialized);
      var list = this.getSavedList();
      var idx = list.findIndex(function (s) { return s.id === this.state.assessmentId; }.bind(this));
      var entry = {
        id: this.state.assessmentId,
        name: this.state.assessmentName || this.state.scoping.organizationName || "Untitled",
        updatedAt: this.state.updatedAt,
        createdAt: this.state.createdAt,
        progress: this.getProgressPct(),
      };
      if (idx >= 0) list[idx] = entry;
      else list.push(entry);
      localStorage.setItem(STORAGE_KEY + "-list", JSON.stringify(list));
      // Successful save clears any prior quota banner.
      if (this._quotaError) {
        this._quotaError = false;
        if (this.el) this.render();
      }
    } catch (e) {
      // spa-fix-quota-banner: surface QuotaExceededError so user can act.
      var name = e && e.name;
      var code = e && e.code;
      if (name === "QuotaExceededError" || name === "NS_ERROR_DOM_QUOTA_REACHED" ||
          code === 22 || code === 1014) {
        this._quotaError = true;
        if (this.el) this.render();
      }
    }
  };

  AssessmentApp.prototype.getSavedList = function () {
    try {
      var raw = JSON.parse(localStorage.getItem(STORAGE_KEY + "-list") || "[]");
      if (!Array.isArray(raw)) return [];
      return raw.filter(function (item) {
        return item && typeof item === "object" && typeof item.id === "string";
      });
    } catch (e) { return []; }
  };

  AssessmentApp.prototype.loadFromStorage = function (id) {
    try {
      // Prefer the per-assessment slot (iter3-2-001 P0); falls back to
      // `-current` for assessments that pre-date the per-id slot OR when
      // caller did not supply an id.
      var raw = null;
      if (id) raw = localStorage.getItem(STORAGE_KEY + "-data-" + id);
      if (!raw) raw = localStorage.getItem(STORAGE_KEY + "-current");
      if (!raw) return false;
      var data = JSON.parse(raw);
      if (data && (!id || data.assessmentId === id) && this.validateState(data)) {
        this.state = data;
        // spa-fix-resume-step: restore wizard step from saved data. Only
        // honor "completed analysis" steps (results, export) on Resume —
        // for in-progress steps (welcome, scoping, phase1, phase2) Resume
        // always lands on phase1 (the working area). This avoids surfacing
        // half-filled scoping screens AND restores users who had reached
        // results/export to where they left off.
        var savedStep = (typeof data.step === "string") ? data.step : "";
        this.step = (savedStep === "results" || savedStep === "export") ? savedStep : "phase1";
        // spa-fix-filter-namespace: pull the assessment's per-id filter view
        // state into transient state so the UI re-shows what the user had
        // previously. Missing keys clear the filter (no leakage).
        try {
          var aid = data.assessmentId;
          if (aid) {
            var savedRole = localStorage.getItem(ROLE_FILTER_KEY + "-" + aid);
            var savedSector = localStorage.getItem(SECTOR_KEY + "-" + aid);
            this.state.roleFilter = savedRole || "";
            this.state.selectedSector = savedSector || "";
          }
        } catch (_) { /* */ }
        return true;
      }
    } catch (e) { /* */ }
    return false;
  };

  AssessmentApp.prototype.deleteSaved = function (id) {
    // spa-fix-destructive-gate: offer JSON export first if the target
    // assessment has answered controls. Reads from per-id slot (preferred)
    // and falls back to `-current` for legacy state.
    try {
      var rawTarget = localStorage.getItem(STORAGE_KEY + "-data-" + id) ||
                       localStorage.getItem(STORAGE_KEY + "-current");
      var target = rawTarget ? JSON.parse(rawTarget) : null;
      if (target && target.assessmentId === id &&
          target.responses && Object.keys(target.responses).length > 0) {
        if (typeof confirm === "function" &&
            confirm("This assessment has answered controls. Click OK to export it to JSON before deleting, or Cancel to delete without exporting.")) {
          var prevState = this.state;
          this.state = target;
          try { this.exportJSON(); } catch (_) { /* keep deleting even if export fails */ }
          this.state = prevState;
        }
      }
    } catch (_) { /* */ }
    var list = this.getSavedList().filter(function (s) { return s.id !== id; });
    localStorage.setItem(STORAGE_KEY + "-list", JSON.stringify(list));
    try {
      // Always remove the per-id slot for the deleted assessment.
      localStorage.removeItem(STORAGE_KEY + "-data-" + id);
      // spa-fix-filter-namespace: clear per-assessment filter view state.
      localStorage.removeItem(ROLE_FILTER_KEY + "-" + id);
      localStorage.removeItem(SECTOR_KEY + "-" + id);
      var cur2 = JSON.parse(localStorage.getItem(STORAGE_KEY + "-current"));
      if (cur2 && cur2.assessmentId === id) {
        localStorage.removeItem(STORAGE_KEY + "-current");
      }
    } catch (e) { /* */ }
  };

  AssessmentApp.prototype.getProgressPct = function () {
    if (!this.state || !this.data) return 0;
    var total = this.data.controls.length;
    var answered = Object.keys(this.state.responses).length;
    return Math.round((answered / total) * 100);
  };

  AssessmentApp.prototype.validateState = function (parsed) {
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return false;
    if (typeof parsed.assessmentId !== "string") return false;
    if (!parsed.scoping || typeof parsed.scoping !== "object") return false;
    if (!parsed.responses || typeof parsed.responses !== "object") return false;
    // Validate responses values
    var validAnswers = { yes: 1, partial: 1, no: 1, na: 1 };
    for (var k in parsed.responses) {
      if (!Object.prototype.hasOwnProperty.call(parsed.responses, k)) continue;
      var r = parsed.responses[k];
      if (r && r.answer && !validAnswers[r.answer]) return false;
    }
    return true;
  };

  AssessmentApp.prototype.importState = function (json) {
    try {
      var parsed = typeof json === "string" ? JSON.parse(json) : json;
      // spa-fix-destructive-gate: warn before replacing a non-empty assessment
      // with one from a DIFFERENT source. Same-id round-trip is not destructive.
      var importingDifferent = !this.state || !parsed || !this.state.assessmentId ||
        (parsed.assessmentId && parsed.assessmentId !== this.state.assessmentId);
      if (importingDifferent && this.state && this.state.responses &&
          Object.keys(this.state.responses).length > 0) {
        var orgName = (this.state.scoping && this.state.scoping.organizationName) || "the current assessment";
        if (typeof confirm === "function") {
          var go = confirm("Importing will replace your current assessment for " + orgName +
            ". Click OK to export the current assessment first, or Cancel to abandon the import.");
          if (!go) return false;
          try { this.exportJSON(); } catch (_) { /* keep going */ }
        }
      }
      // spa-fix-prototype-pollution: hard-reject __proto__/constructor/prototype keys.
      if (_hasForbiddenKey(parsed)) {
        throw new Error("Invalid assessment file: forbidden keys present");
      }
      // Deep structural validation
      if (!this.validateState(parsed)) {
        throw new Error("Invalid assessment file structure");
      }
      // Sanitize: prevent prototype pollution by only copying known keys
      var sc = parsed.scoping || {};
      var clean = {
        assessmentId: String(parsed.assessmentId),
        assessmentName: String(parsed.assessmentName || ""),
        createdAt: parsed.createdAt || new Date().toISOString(),
        updatedAt: parsed.updatedAt || new Date().toISOString(),
        scoping: {
          organizationName: String(sc.organizationName || ""),
          assessorName: String(sc.assessorName || ""),
          assessorRole: String(sc.assessorRole || ""),
          institutionType: String(sc.institutionType || ""),
          zones: Array.isArray(sc.zones) ? sc.zones.filter(function (z) { return [1, 2, 3].indexOf(z) >= 0; }) : [1, 2, 3],
          adoptionPhase: [0, 1, 2].indexOf(parseInt(sc.adoptionPhase, 10)) >= 0 ? parseInt(sc.adoptionPhase, 10) : 0,
          regulations: Array.isArray(sc.regulations) ? sc.regulations.map(String) : [],
          scope: String(sc.scope || "full"),
        },
        responses: {},
        drilldown: {},
        completedSteps: Array.isArray(parsed.completedSteps) ? parsed.completedSteps : [],
        // v1.4 Phase B
        selectedSector: typeof parsed.selectedSector === "string" ? parsed.selectedSector : "",
        roleFilter: typeof parsed.roleFilter === "string" ? parsed.roleFilter : "",
        priorityMode: parsed.priorityMode === "starter" ? "starter" : "full",
        priorityExpanded: !!parsed.priorityExpanded,
        overrides: (parsed.overrides && typeof parsed.overrides === "object") ? parsed.overrides : {},
      };
      // Copy responses safely
      for (var k in parsed.responses) {
        if (!Object.prototype.hasOwnProperty.call(parsed.responses, k)) continue;
        var rr = parsed.responses[k];
        if (rr && typeof rr === "object" && !Array.isArray(rr)) {
          clean.responses[k] = {
            answer: rr.answer || null,
            notes: typeof rr.notes === "string" ? rr.notes : "",
            evidenceRef: typeof rr.evidenceRef === "string" ? rr.evidenceRef : "",
          };
          if (rr.autoNa) clean.responses[k].autoNa = true;
          if (rr.importedFromCollector) clean.responses[k].importedFromCollector = true;
        } else {
          clean.responses[k] = rr;
        }
      }
      if (parsed.drilldown) {
        for (var d in parsed.drilldown) {
          if (!Object.prototype.hasOwnProperty.call(parsed.drilldown, d)) continue;
          if (Object.prototype.hasOwnProperty.call(_COLLECTOR_FORBIDDEN_KEYS, d)) continue;
          var safeDd = _safeCopyDrilldown(parsed.drilldown[d]);
          if (safeDd) clean.drilldown[d] = safeDd;
        }
      }
      // Section import (role-specific)
      if (parsed.sectionExport) {
        if (!this.state) {
          alert("Start or resume an assessment first before importing a section.");
          return false;
        }
        return this.importSection(parsed);
      }
      this.state = clean;
      this.saveToStorage();
      return true;
    } catch (e) {
      alert("Error importing assessment: " + e.message);
      return false;
    }
  };

  AssessmentApp.prototype.importSection = function (sectionData) {
    if (!sectionData.responses || typeof sectionData.responses !== "object") return false;
    var validAnswers = { yes: 1, partial: 1, no: 1, na: 1 };
    var conflicts = [];
    var imported = 0;
    var self = this;
    Object.keys(sectionData.responses).forEach(function (cid) {
      if (!Object.prototype.hasOwnProperty.call(sectionData.responses, cid)) return;
      var raw = sectionData.responses[cid];
      if (!raw || typeof raw !== "object") return;
      // Sanitize incoming response
      var incoming = { answer: validAnswers[raw.answer] ? raw.answer : "", notes: String(raw.notes || "") };
      var existing = self.state.responses[cid];
      if (existing && existing.answer && existing.answer !== incoming.answer) {
        conflicts.push(cid);
      }
      self.state.responses[cid] = incoming;
      imported++;
    });
    if (sectionData.drilldown && typeof sectionData.drilldown === "object") {
      Object.keys(sectionData.drilldown).forEach(function (cid) {
        if (!Object.prototype.hasOwnProperty.call(sectionData.drilldown, cid)) return;
        var dd = sectionData.drilldown[cid];
        if (!dd || typeof dd !== "object") return;
        // Sanitize drilldown: only yes/no values
        var clean = {};
        Object.keys(dd).forEach(function (k) {
          if (Object.prototype.hasOwnProperty.call(dd, k) && (dd[k] === "yes" || dd[k] === "no")) {
            clean[k] = dd[k];
          }
        });
        self.state.drilldown[cid] = clean;
      });
    }
    this.saveToStorage();
    if (conflicts.length > 0) {
      alert(
        "Imported " + imported + " responses. " +
        conflicts.length + " conflict(s) detected for: " + conflicts.join(", ") +
        ". The imported answers have overwritten previous values."
      );
    }
    return true;
  };

  /* ================================================================
     E3 — COLLECTOR EVIDENCE IMPORT
     ================================================================
     Accepts JSON files from `assessment/output/scores.json` (scoring
     engine output) OR per-collector raw JSON from
     `assessment/output/collected/*.json`. Auto-detects shape:
       - scores.json: top-level `controls: [ {id, maturity_score,
         maturity_label, confidence, ...} ]`
       - per-collector: top-level `_metadata.collector` plus arbitrary
         data keys; entries are matched to manifest controls via the
         `collectorField` value.
  ================================================================= */

  // Map collector status / score → SPA answer. Returns null when the
  // input is unknown / missing so callers leave existing answers alone.
  function mapCollectorToAnswer(entry) {
    if (!entry || typeof entry !== "object") return null;
    var status = (entry.status || entry.maturity_label || "").toString().toLowerCase().replace(/[\s-]+/g, "_");
    var score = (typeof entry.maturity_score === "number") ? entry.maturity_score
              : (typeof entry.score === "number") ? entry.score : null;
    if (status === "not_applicable" || status === "na" || status === "n_a") return "na";
    if (status === "pass" || status === "passed") return "yes";
    if (status === "partial" || status === "partially_implemented") return "partial";
    if (status === "fail" || status === "failed" || status === "not_implemented") return "no";
    if (status === "unknown" || status === "needs_manual" || status === "needs_review") return null;
    if (score === null) return null;
    if (score >= 4) return "yes";
    if (score >= 2) return "partial";
    if (score >= 0) return "no";
    return null;
  }

  // Build a one-line evidence summary from a control entry for the notes
  // textarea. Tries common fields seen in fixtures and per-collector data.
  function summarizeCollectorEvidence(entry) {
    if (!entry || typeof entry !== "object") return "";
    if (typeof entry.evidence === "string" && entry.evidence) return entry.evidence;
    if (Array.isArray(entry.checks) && entry.checks.length > 0) {
      var passed = entry.checks.filter(function (c) { return c && c.passed === true; }).length;
      var applicable = entry.checks.filter(function (c) { return c && c.applicable !== false; }).length;
      var first = entry.checks.find(function (c) { return c && c.evidence; });
      var head = passed + "/" + applicable + " checks passed";
      return first ? head + "; " + first.evidence : head;
    }
    if (typeof entry.maturity_label === "string") {
      return "Maturity: " + entry.maturity_label +
        (typeof entry.maturity_score === "number" ? " (score " + entry.maturity_score + ")" : "");
    }
    return "";
  }

  // Replace any prior "[Imported]: …" line in `existing` with the new
  // imported line so re-imports do not duplicate notes. Preserves any
  // other user-entered note content.
  function mergeImportedNote(existing, importedLine) {
    var prior = (existing || "").replace(/\r\n/g, "\n");
    var lines = prior ? prior.split("\n") : [];
    var kept = lines.filter(function (l) { return l.indexOf("[Imported]:") !== 0; });
    if (importedLine) kept.unshift("[Imported]: " + importedLine);
    return kept.join("\n").trim();
  }

  AssessmentApp.prototype.openCollectorImport = function () {
    var self = this;
    if (!this.state) {
      alert("Start or resume an assessment first before importing collector evidence.");
      return;
    }
    var hasUserAnswers = Object.keys(this.state.responses || {}).some(function (k) {
      var r = self.state.responses[k];
      return r && r.answer && !r.autoNa && !r.importedFromCollector;
    });
    if (hasUserAnswers) {
      var msg = t("import_confirm_overwrite",
        "Importing will overwrite existing answers for matched controls. Continue?");
      if (!confirm(msg)) return;
    }
    var input = document.createElement("input");
    input.type = "file";
    input.accept = ".json,application/json";
    input.multiple = true;
    input.style.display = "none";
    input.addEventListener("change", function () {
      var files = Array.prototype.slice.call(input.files || []);
      if (files.length === 0) { document.body.removeChild(input); return; }
      self.importCollectorFiles(files).then(function () {
        try { document.body.removeChild(input); } catch (e) { /* */ }
      });
    });
    document.body.appendChild(input);
    input.click();
  };

  AssessmentApp.prototype.importCollectorFiles = function (files) {
    var self = this;
    var totalImported = 0;
    var totalSkipped = 0;
    var fileCount = 0;
    var readOne = function (file) {
      return new Promise(function (resolve) {
        var reader = new FileReader();
        reader.onerror = function () {
          self.showToast(tFmt("import_error", "Could not import {file}: {message}",
            { file: file.name, message: "read failed" }), "error");
          resolve();
        };
        reader.onload = function () {
          try {
            var parsed = JSON.parse(reader.result);
            var result = self.applyCollectorPayload(parsed, file.name);
            totalImported += result.imported;
            totalSkipped += result.skipped;
            fileCount++;
          } catch (err) {
            self.showToast(tFmt("import_error", "Could not import {file}: {message}",
              { file: file.name, message: err && err.message ? err.message : "parse error" }), "error");
          }
          resolve();
        };
        try { reader.readAsText(file); }
        catch (e) {
          self.showToast(tFmt("import_error", "Could not import {file}: {message}",
            { file: file.name, message: e.message }), "error");
          resolve();
        }
      });
    };
    return files.reduce(function (p, f) {
      return p.then(function () { return readOne(f); });
    }, Promise.resolve()).then(function () {
      self.saveToStorage();
      self.render();
      self.showToast(tFmt("import_summary",
        "Imported {imported} controls from {files} file(s). {skipped} skipped (no manifest match).",
        { imported: totalImported, files: fileCount, skipped: totalSkipped }), "info");
    });
  };

  // Detect payload shape and apply matching control entries to state.
  // Returns { imported, skipped }.
  AssessmentApp.prototype.applyCollectorPayload = function (payload, fileName) {
    var self = this;
    var imported = 0;
    var skipped = 0;
    if (!payload || typeof payload !== "object") {
      return { imported: 0, skipped: 0 };
    }
    var meta = payload._metadata || {};
    var collectorName = meta.collector ||
      (payload.collectorName) ||
      (Array.isArray(payload.controls) ? "scores.json" : (fileName || "collector"));
    var timestamp = meta.timestamp || payload.timestamp || new Date().toISOString();

    var entries = []; // { id?, collectorField?, entry }

    // Shape A: scores.json — top-level `controls` array of per-control objects with `id`.
    if (Array.isArray(payload.controls)) {
      payload.controls.forEach(function (c) {
        if (c && c.id) entries.push({ id: String(c.id), entry: c });
      });
    }
    // Shape B: scores.json variant where `controls` is keyed by id.
    else if (payload.controls && typeof payload.controls === "object") {
      Object.keys(payload.controls).forEach(function (k) {
        var c = payload.controls[k];
        if (c && typeof c === "object") entries.push({ id: String(k), entry: c });
      });
    }
    // Shape C: per-collector file. Only useful if any manifest control
    // declares a `collectorField` matching one of the top-level keys.
    else {
      var dataRoot = (payload.data && typeof payload.data === "object") ? payload.data : payload;
      Object.keys(dataRoot).forEach(function (k) {
        if (k === "_metadata" || k === "collectorName") return;
        entries.push({ collectorField: k, entry: dataRoot[k] });
      });
    }

    if (entries.length === 0) return { imported: 0, skipped: 0 };

    entries.forEach(function (item) {
      var ctrl = self.findControlForImport(item);
      if (!ctrl) { skipped++; return; }
      var answer = mapCollectorToAnswer(item.entry);
      if (!answer) { skipped++; return; }
      var summary = summarizeCollectorEvidence(item.entry);
      // spa-fix-collector-injection: if the entry self-describes as a per-control
      // collector record (has controlId), validate it before trusting any
      // string fields we copy onto state.
      if (item.entry && typeof item.entry === "object" &&
          Object.prototype.hasOwnProperty.call(item.entry, "controlId") &&
          !validateCollectorPayload(item.entry)) {
        skipped++;
        return;
      }
      var prior = self.state.responses[ctrl.id] || {};
      var safeNotes = mergeImportedNote(prior.notes, summary);
      if (typeof safeNotes !== "string") safeNotes = "";
      if (safeNotes.length > 4000) safeNotes = safeNotes.slice(0, 4000);
      var safeRef = "Collector: " + collectorName + " @ " + timestamp;
      if (safeRef.length > 500) safeRef = safeRef.slice(0, 500);
      var merged = {
        answer: answer,
        notes: safeNotes,
        evidenceRef: safeRef,
        importedFromCollector: true,
      };
      // Preserve override autoNa flag absence; explicitly clear autoNa
      // because the import is now the authoritative answer.
      self.state.responses[ctrl.id] = merged;
      imported++;
    });
    return { imported: imported, skipped: skipped };
  };

  AssessmentApp.prototype.findControlForImport = function (item) {
    if (!this.data || !Array.isArray(this.data.controls)) return null;
    var id = item.id;
    var cf = item.collectorField;
    if (id && this.controlsById && this.controlsById.has(id)) return this.controlsById.get(id);
    for (var i = 0; i < this.data.controls.length; i++) {
      var c = this.data.controls[i];
      if (id && c.id === id) return c;
      if (cf && c.collectorField && c.collectorField === cf) return c;
    }
    return null;
  };

  /* ---- Toast helper (used by E3; safe no-op fallback) ---- */
  AssessmentApp.prototype.showToast = function (message, kind) {
    if (!message) return;
    var host = document.querySelector(".ag-toast-host");
    if (!host) {
      host = document.createElement("div");
      host.className = "ag-toast-host";
      host.setAttribute("aria-live", "polite");
      host.setAttribute("aria-atomic", "true");
      document.body.appendChild(host);
    }
    var toast = document.createElement("div");
    toast.className = "ag-toast" + (kind === "error" ? " ag-toast-error" : " ag-toast-info");
    toast.setAttribute("role", kind === "error" ? "alert" : "status");
    toast.textContent = message;
    host.appendChild(toast);
    setTimeout(function () {
      toast.classList.add("ag-toast-leaving");
      setTimeout(function () {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 400);
    }, kind === "error" ? 6000 : 4500);
  };

  /* ================================================================
     SCORING
     ================================================================ */
  AssessmentApp.prototype.getControlScore = function (controlId) {
    var resp = this.state.responses[controlId];
    if (!resp || !resp.answer) return null;
    if (resp.answer === "na") return null;
    if (resp.answer === "yes") return 1.0;
    if (resp.answer === "no") return 0.0;
    // Partial — refine with drilldown if available
    var dd = this.state.drilldown[controlId];
    if (dd) {
      var keys = Object.keys(dd);
      if (keys.length > 0) {
        var yes = keys.filter(function (k) { return dd[k] === "yes"; }).length;
        return yes / keys.length;
      }
    }
    return 0.5;
  };

  AssessmentApp.prototype.getAggregateScore = function (controlIds) {
    var self = this;
    var total = 0;
    var count = 0;
    controlIds.forEach(function (cid) {
      var score = self.getControlScore(cid);
      if (score !== null) {
        total += score;
        count++;
      }
    });
    return count > 0 ? Math.round((total / count) * 100) : null;
  };

  AssessmentApp.prototype.getPillarScore = function (pillarNum) {
    var ids = this.data.controls
      .filter(function (c) { return c.pillar === pillarNum; })
      .map(function (c) { return c.id; });
    return this.getAggregateScore(ids);
  };

  AssessmentApp.prototype.getOverallScore = function () {
    var ids = this.data.controls.map(function (c) { return c.id; });
    return this.getAggregateScore(ids);
  };

  AssessmentApp.prototype.getRegulationScore = function (regKey) {
    var mapping = this.data.regulatoryMappings[regKey];
    if (!mapping) return null;
    return this.getAggregateScore(mapping.controls);
  };

  AssessmentApp.prototype.getZoneScore = function (zoneNum) {
    var self = this;
    var total = 0;
    var count = 0;
    this.data.controls.forEach(function (c) {
      if (c.zones.indexOf(zoneNum) < 0) return;
      // Use zone weights: skip controls that are optional/N/A for this zone
      var weight = (c.zoneWeights && c.zoneWeights[String(zoneNum)] !== undefined)
        ? c.zoneWeights[String(zoneNum)] : 1;
      if (weight === 0) return;
      var score = self.getControlScore(c.id);
      if (score !== null) {
        total += score;
        count++;
      }
    });
    return count > 0 ? Math.round((total / count) * 100) : null;
  };

  AssessmentApp.prototype.getRiskPriority = function (control) {
    var score = this.getControlScore(control.id);
    if (score === null || score === 1.0) return 0;
    var regWeight = control.regulations.length >= 4 ? 3 : control.regulations.length >= 2 ? 2 : 1;
    var maxZone = Math.max.apply(null, control.zones);
    var zoneWeight = maxZone === 3 ? 3 : maxZone === 2 ? 2 : 1;
    var currentPhase = this.state.scoping.adoptionPhase || 0;
    var phaseWeight = 1;
    if (control.adoptionPhase) {
      var cp = control.adoptionPhase.phase;
      if (cp === currentPhase) phaseWeight = 3;
      else if (cp === currentPhase + 1) phaseWeight = 2;
    }
    return (1 - score) * regWeight * zoneWeight * phaseWeight;
  };

  AssessmentApp.prototype.getGapControls = function () {
    var self = this;
    var allGaps = this.data.controls.filter(function (c) {
      var score = self.getControlScore(c.id);
      return score !== null && score < 1.0;
    });
    var roleFilter = (this.state && this.state.roleFilter) || "";
    var filteredGaps = allGaps;
    if (roleFilter) {
      filteredGaps = allGaps.filter(function (c) {
        return self.controlMatchesRoleFilter(c, roleFilter);
      });
      // spa-fix-phase2-filter: if applying the role filter would zero out
      // gaps, fall back to all gaps and expose the count via _phase2RoleFilterHidden
      // so the renderer can show an explanatory banner.
      if (filteredGaps.length === 0 && allGaps.length > 0) {
        this._phase2RoleFilterHidden = allGaps.length;
        filteredGaps = allGaps;
      } else {
        this._phase2RoleFilterHidden = 0;
      }
    } else {
      this._phase2RoleFilterHidden = 0;
    }
    return filteredGaps.sort(function (a, b) {
      return self.getRiskPriority(b) - self.getRiskPriority(a);
    });
  };

  /* ---- v1.4.1 export-envelope helpers ----
   * Consumed by exportJSON / exportRoleSection. Snapshot-only — never mutated
   * onto this.state, never persisted to localStorage, dropped on import.
   */

  /**
   * Derive the assessmentStatus enum from current state. Snapshot at export time.
   * Returns one of: "draft", "in-progress", "final".
   *  - "final"        if completedSteps includes the explicit "full"/"complete"
   *                   sentinel (set by Step 6 export confirmation in a future patch)
   *  - "in-progress"  if any control has a response
   *  - "draft"        otherwise
   */
  AssessmentApp.prototype.deriveAssessmentStatus = function () {
    if (!this.state) return "draft";
    var steps = this.state.completedSteps || [];
    if (steps.indexOf("full") >= 0 || steps.indexOf("complete") >= 0) return "final";
    var responses = this.state.responses || {};
    for (var k in responses) {
      if (Object.prototype.hasOwnProperty.call(responses, k) && responses[k] && responses[k].answer) {
        return "in-progress";
      }
    }
    return "draft";
  };

  /**
   * Compute per-control / per-pillar / overall scores at export time.
   * Mirrors the same numbers the Results dashboard renders. Snapshot-only.
   * Returns null for any aggregate where no controls are scoreable (matches
   * getAggregateScore semantics so consumers can render "n/a" cleanly).
   */
  AssessmentApp.prototype.computeExportScores = function () {
    if (!this.data || !Array.isArray(this.data.controls)) return null;
    var self = this;
    var perControl = {};
    this.data.controls.forEach(function (c) {
      perControl[c.id] = self.getControlScore(c.id); // null | 0..1
    });
    return {
      overall: this.getOverallScore(),
      perPillar: {
        "1": this.getPillarScore(1),
        "2": this.getPillarScore(2),
        "3": this.getPillarScore(3),
        "4": this.getPillarScore(4)
      },
      perControl: perControl
    };
  };

  /**
   * Build the _metadata envelope shared by full and section exports.
   */
  AssessmentApp.prototype.buildExportMetadata = function (schemaType) {
    return {
      exportSchemaVersion: EXPORT_SCHEMA_VERSION,
      schemaType: schemaType,
      frameworkVersion: FRAMEWORK_VERSION,
      manifestSchemaVersion: (this.solutionsLock && this.solutionsLock.schemaVersion) || null,
      exportedAt: new Date().toISOString(),
      exportedBy: (this.state && this.state.scoping && this.state.scoping.assessorName) || ""
    };
  };

  /* ================================================================
     RENDERING — MAIN ROUTER
     ================================================================ */
  AssessmentApp.prototype.render = function () {
    this.destroy(); // Clean up charts
    this.el.innerHTML = "";
    if (this._quotaError) this.el.appendChild(this._renderQuotaBanner());
    this.el.appendChild(this.renderSteps());
    var content = h("div", { className: "ag-content" });
    switch (this.step) {
      case "welcome": this.renderWelcome(content); break;
      case "scoping": this.renderScoping(content); break;
      case "phase1":  this.renderPhase1(content); break;
      case "phase2":  this.renderPhase2(content); break;
      case "results": this.renderResults(content); break;
      case "export":  this.renderExport(content); break;
    }
    this.el.appendChild(content);
  };

  AssessmentApp.prototype._renderQuotaBanner = function () {
    var self = this;
    var banner = h("div", { className: "ag-quota-banner ag-no-print", role: "alert" });
    banner.appendChild(h("span", null,
      "Browser storage is full. Your latest changes may not have been saved. " +
      "Export your assessment to JSON, then clear old saved assessments to free space."
    ));
    var dismiss = h("button", {
      type: "button",
      "aria-label": "Dismiss storage warning",
      onClick: function () { self._quotaError = false; self.render(); }
    }, "Dismiss");
    banner.appendChild(dismiss);
    return banner;
  };

  AssessmentApp.prototype.goToStep = function (step) {
    this.step = step;
    // spa-fix-resume-step: persist the step to storage immediately so a
    // browser refresh / Resume restores the user to the same wizard step.
    if (this.state) {
      try { this.saveToStorage(); } catch (_) { /* */ }
    }
    this.render();
    this.el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  AssessmentApp.prototype.renderSteps = function () {
    var self = this;
    var nav = h("nav", { className: "ag-steps", role: "navigation", "aria-label": "Assessment steps" });
    STEPS.forEach(function (s) {
      var cls = "ag-step-indicator";
      var current = s.id === self.step;
      var isCompleted = self.state && self.state.completedSteps && self.state.completedSteps.indexOf(s.id) >= 0;
      if (current) cls += " active";
      else if (isCompleted) cls += " completed";
      var prefix = isCompleted && !current ? "\u2713 " : s.num + ". ";
      var el = h("button", {
        className: cls,
        title: isCompleted ? s.label + " (completed)" : current ? s.label + " (current step)" : s.label,
        "aria-current": current ? "step" : null,
        onClick: function () { if (self.state || s.id === "welcome") self.goToStep(s.id); }
      }, prefix + s.label);
      nav.appendChild(el);
    });
    return nav;
  };

  /* ================================================================
     MODAL
     ================================================================ */
  AssessmentApp.prototype.showModal = function (title, contentEl) {
    var backdrop = h("div", { className: "ag-modal-backdrop" });
    var modal = h("div", { className: "ag-modal", role: "dialog", "aria-modal": "true", "aria-label": title });
    var header = h("div", { className: "ag-modal-header" });
    header.appendChild(h("h3", null, title));
    var closeBtn = h("button", { className: "ag-modal-close", "aria-label": "Close" }, "\u00D7");
    header.appendChild(closeBtn);
    modal.appendChild(header);
    var body = h("div", { className: "ag-modal-body" });
    body.appendChild(contentEl);
    modal.appendChild(body);
    backdrop.appendChild(modal);

    var close = function () { if (backdrop.parentNode) backdrop.parentNode.removeChild(backdrop); };
    closeBtn.addEventListener("click", close);
    backdrop.addEventListener("click", function (e) { if (e.target === backdrop) close(); });
    backdrop.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });

    document.body.appendChild(backdrop);
    closeBtn.focus();
  };

  AssessmentApp.prototype.showScoringModal = function () {
    var content = h("div");
    content.appendChild(h("p", null,
      "Each control is scored based on your self-reported implementation status."));

    var dl = document.createElement("dl");
    var items = [
      ["Yes = 1.0", "Fully implemented and verified."],
      ["Partial = 0.5", "Some aspects implemented. Refined by Phase 2 drill-down sub-questions."],
      ["No = 0.0", "Not yet implemented."],
      ["N/A = excluded", "Not applicable to your organization; excluded from scoring."],
    ];
    items.forEach(function (pair) {
      dl.appendChild(h("dt", null, pair[0]));
      dl.appendChild(h("dd", null, pair[1]));
    });
    content.appendChild(dl);

    content.appendChild(h("p", { style: "margin-top:1rem;font-weight:600" }, "Aggregate Score Formula"));
    content.appendChild(h("p", null,
      "score = sum(controlScores) / count(applicableControls) \u00D7 100"));

    content.appendChild(h("p", { style: "margin-top:1rem;font-weight:600" }, "RAG Thresholds"));
    var ragDl = document.createElement("dl");
    ragDl.appendChild(h("dt", { style: "color:var(--ag-green)" }, "Green (80%+)"));
    ragDl.appendChild(h("dd", null, "Strong implementation; minor refinements may be needed."));
    ragDl.appendChild(h("dt", { style: "color:var(--ag-amber)" }, "Amber (50\u201379%)"));
    ragDl.appendChild(h("dd", null, "Partial implementation; focused remediation recommended."));
    ragDl.appendChild(h("dt", { style: "color:var(--ag-red)" }, "Red (below 50%)"));
    ragDl.appendChild(h("dd", null, "Significant gaps; prioritized remediation required."));
    content.appendChild(ragDl);

    content.appendChild(h("p", { style: "margin-top:1rem;font-weight:600" }, "Risk Priority"));
    content.appendChild(h("p", null,
      "riskPriority = (1 \u2212 score) \u00D7 regulatoryWeight \u00D7 zoneWeight \u00D7 phaseWeight"));
    var rpDl = document.createElement("dl");
    rpDl.appendChild(h("dt", null, "Regulatory weight"));
    rpDl.appendChild(h("dd", null, "3.0 (4+ regulations), 2.0 (2\u20133), 1.0 (0\u20131)"));
    rpDl.appendChild(h("dt", null, "Zone weight"));
    rpDl.appendChild(h("dd", null, "3.0 (Zone 3), 2.0 (Zone 2), 1.0 (Zone 1)"));
    rpDl.appendChild(h("dt", null, "Phase weight"));
    rpDl.appendChild(h("dd", null, "3.0 (current phase), 2.0 (next phase), 1.0 (future)"));
    content.appendChild(rpDl);

    content.appendChild(h("p", { style: "margin-top:1rem;font-weight:600" }, "Zone-Specific Scoring"));
    content.appendChild(h("p", null,
      "Zone scores exclude controls whose zone requirements are optional, awareness-only, or N/A. " +
      "Approximately 10 controls are excluded from Zone 1 scoring, while all 78 apply to Zone 3."));

    this.showModal("How Scoring Works", content);
  };

  /* ================================================================
     STEP 1: WELCOME
     ================================================================ */
  AssessmentApp.prototype.renderWelcome = function (parent) {
    var self = this;
    var wrap = h("div", { className: "ag-welcome" });

    wrap.appendChild(h("h2", null, "Governance Readiness Assessment"));
    wrap.appendChild(h("p", null,
      "Assess your organization's readiness across the 78-control FSI Agent Governance Framework. " +
      "This tool helps identify gaps and generates a personalized remediation roadmap."
    ));

    // Disclaimer
    wrap.appendChild(h("div", { className: "ag-disclaimer" },
      "This assessment helps support governance readiness. It does not constitute legal advice " +
      "and does not guarantee compliance with any regulation."
    ));

    // Scoring summary
    var scoringSummary = h("div", { className: "ag-scoring-summary" });
    var scoringDl = document.createElement("dl");
    scoringDl.style.margin = "0";
    [["Yes", "1.0"], ["Partial", "0.5"], ["No", "0.0"], ["N/A", "excluded"]].forEach(function (pair) {
      scoringDl.appendChild(h("dt", null, pair[0] + " ="));
      scoringDl.appendChild(h("dd", null, pair[1]));
    });
    scoringSummary.appendChild(scoringDl);
    var ragLine = h("div", { style: "margin-top:0.5rem" });
    ragLine.appendChild(h("span", { style: "font-weight:600" }, "RAG: "));
    ragLine.appendChild(h("span", { style: "color:var(--ag-green);font-weight:600" }, "Green 80%+ "));
    ragLine.appendChild(h("span", { style: "color:var(--ag-amber);font-weight:600" }, "Amber 50\u201379% "));
    ragLine.appendChild(h("span", { style: "color:var(--ag-red);font-weight:600" }, "Red <50%"));
    scoringSummary.appendChild(ragLine);
    var privacyNote = h("div", { className: "ag-privacy-note" },
      "Data Privacy: All assessment data stays in your browser. No data is sent to any server. " +
      "Use Save to File (JSON export) to share or archive results.");
    scoringSummary.appendChild(privacyNote);
    wrap.appendChild(scoringSummary);

    var btns = h("div", { className: "ag-btn-group", style: "justify-content: center" });
    btns.appendChild(h("button", {
      className: "ag-btn ag-btn-primary",
      onClick: function () {
        self.state = self.newState();
        self.goToStep("scoping");
      }
    }, "Start New Assessment"));

    // File import
    btns.appendChild(h("button", {
      className: "ag-btn ag-btn-secondary",
      onClick: function () { self.triggerImport(); }
    }, "Resume or Import Saved Assessment"));
    wrap.appendChild(btns);

    // Import helper text
    wrap.appendChild(h("p", { style: "font-size:0.78rem;color:var(--md-default-fg-color--light);max-width:600px;margin:0.5rem auto" },
      "Import a previously exported JSON file to resume an assessment or review completed results. " +
      "You can also import role-specific sections completed by other team members."));

    // Saved assessments from localStorage
    var saved = this.getSavedList();
    if (saved.length > 0) {
      wrap.appendChild(h("h3", { style: "margin-top:2rem;font-size:1rem" }, "Previous Assessments"));
      var list = h("ul", { className: "ag-saved-list" });
      saved.sort(function (a, b) { return new Date(b.updatedAt) - new Date(a.updatedAt); });
      saved.forEach(function (s) {
        var item = h("li", { className: "ag-saved-item" });
        var info = h("div");
        info.appendChild(h("strong", null, s.name || "Untitled"));
        info.appendChild(h("div", { className: "ag-saved-meta" },
          fmtDate(s.updatedAt) + " — " + (s.progress || 0) + "% complete"
        ));
        item.appendChild(info);
        var actions = h("div", { className: "ag-btn-group", style: "margin:0" });
        var savedName = s.name || "Untitled";
        actions.appendChild(h("button", {
          className: "ag-btn ag-btn-sm ag-btn-primary",
          "aria-label": "Resume " + savedName,
          onClick: function (e) {
            e.stopPropagation();
            if (self.loadFromStorage(s.id)) {
              // spa-fix-resume-step: respect the saved step (welcome →
              // scoping → phase1 → phase2 → results → export) instead of
              // forcing every Resume back to phase1.
              self.goToStep(self.step || "phase1");
            }
          }
        }, "Resume"));
        actions.appendChild(h("button", {
          className: "ag-btn ag-btn-sm ag-btn-danger",
          "aria-label": "Delete " + savedName,
          onClick: function (e) {
            e.stopPropagation();
            if (confirm("Delete this assessment?")) {
              self.deleteSaved(s.id);
              self.render();
            }
          }
        }, "Delete"));
        item.appendChild(actions);
        list.appendChild(item);
      });
      wrap.appendChild(list);
    }

    // spa-fix-clear-data-button: privacy notice + Clear all data action.
    var footer = h("div", { className: "ag-welcome-footer ag-no-print",
      style: "margin-top:2rem;padding-top:1rem;border-top:1px solid var(--md-default-fg-color--lightest);font-size:0.78rem;color:var(--md-default-fg-color--light);text-align:center" });
    footer.appendChild(h("p", { style: "margin:0 0 0.5rem" },
      "This assessment is stored only in your browser localStorage. We do not transmit your responses."
    ));
    var clearBtn = h("button", {
      type: "button",
      className: "ag-btn ag-btn-sm ag-btn-danger",
      onClick: function () {
        if (typeof confirm === "function" &&
            !confirm("Clear all FSI Agent Governance assessment data from this browser? This cannot be undone — export any assessments you want to keep first.")) return;
        try {
          var prefix = STORAGE_KEY;
          var toRemove = [];
          for (var i = 0; i < localStorage.length; i++) {
            var k = localStorage.key(i);
            if (k && k.indexOf(prefix) === 0) toRemove.push(k);
          }
          toRemove.forEach(function (k) { localStorage.removeItem(k); });
        } catch (_) { /* ignore */ }
        if (typeof location !== "undefined" && location.reload) location.reload();
      }
    }, "Clear all assessment data");
    footer.appendChild(clearBtn);
    wrap.appendChild(footer);

    parent.appendChild(wrap);
  };

  AssessmentApp.prototype.triggerImport = function () {
    var self = this;
    var input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = function () {
      var file = input.files[0];
      if (!file) return;
      var reader = new FileReader();
      reader.onload = function () {
        if (self.importState(reader.result)) {
          self.goToStep("phase1");
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  /* ================================================================
     STEP 2: SCOPING
     ================================================================ */
  AssessmentApp.prototype.renderScoping = function (parent) {
    var self = this;
    var sc = this.state.scoping;
    var wrap = h("div");

    wrap.appendChild(h("h2", { style: "font-size:1.3rem;margin-bottom:0.3rem" }, "Assessment Scoping"));
    wrap.appendChild(h("p", { className: "ag-card-subtitle" },
      "Configure the assessment scope for your organization. " +
      "All 78 controls will be included but prioritized based on your profile."
    ));

    var form = h("div", { className: "ag-card" });

    // Organization name
    form.appendChild(this.field("Organization Name", "text", sc.organizationName, function (v) { sc.organizationName = v; }));

    // Assessor
    form.appendChild(this.field("Assessor Name", "text", sc.assessorName, function (v) { sc.assessorName = v; }));
    form.appendChild(this.field("Assessor Role", "text", sc.assessorRole, function (v) { sc.assessorRole = v; },
      "e.g., AI Governance Lead, Compliance Officer"));

    // Institution type
    var instOptions = [
      { value: "", label: "Select institution type..." },
      { value: "broker-dealer", label: "Broker-Dealer (FINRA/SEC)" },
      { value: "bank", label: "Bank (OCC/Fed)" },
      { value: "adviser", label: "Investment Adviser (SEC)" },
      { value: "dual-registered", label: "Dual-Registered (FINRA + SEC)" },
      { value: "insurance", label: "Insurance Company" },
    ];
    form.appendChild(this.selectField("Institution Type", instOptions, sc.institutionType, function (v) {
      sc.institutionType = v;
      // Auto-populate regulations
      var inst = self.data.institutionTypes[v];
      if (inst) sc.regulations = inst.regulations.slice();
    }));

    // Zones
    var zoneHint = h("div", { className: "ag-check-hint" });
    zoneHint.appendChild(document.createTextNode("Select all zones your organization currently uses or plans to adopt. "));
    var zoneLink = h("a", { href: getBasePath() + "framework/zones-and-tiers/", target: "_blank", style: "text-decoration: underline;" }, "Learn about zones");
    zoneHint.appendChild(zoneLink);
    form.appendChild(this.checkboxGroup("Active Governance Zones", [
      { value: 1, label: "Zone 1 \u2014 Personal Productivity",
        description: "Low risk. Individual scope, M365 Graph only, self-service approval, minimal regulatory scrutiny.",
        checked: sc.zones.indexOf(1) >= 0 },
      { value: 2, label: "Zone 2 \u2014 Team Collaboration",
        description: "Medium risk. Department scope, internal data access, manager approval, moderate regulatory scrutiny.",
        checked: sc.zones.indexOf(2) >= 0 },
      { value: 3, label: "Zone 3 \u2014 Enterprise Managed",
        description: "High risk. Organization-wide, regulated/sensitive data, governance committee approval, full compliance required.",
        checked: sc.zones.indexOf(3) >= 0 },
    ], function (vals) { sc.zones = vals.map(Number); }, zoneHint));

    // Adoption phase
    var phaseOptions = [
      { value: "0", label: "Phase 0 — Foundation (0-60 days)" },
      { value: "1", label: "Phase 1 — Production Readiness (2-6 months)" },
      { value: "2", label: "Phase 2 — Advanced Governance (6-12 months)" },
    ];
    form.appendChild(this.selectField("Current Adoption Phase", phaseOptions, String(sc.adoptionPhase), function (v) {
      sc.adoptionPhase = parseInt(v, 10);
    }));

    // Assessment name
    form.appendChild(this.field("Assessment Name", "text", sc.organizationName ?
      sc.organizationName + " — " + new Date().toISOString().slice(0, 10) : "",
      function (v) { self.state.assessmentName = v; },
      "Name for this assessment (used in exports)"));

    wrap.appendChild(form);

    // ----- v1.4 Phase B additions: sector calibration (E5) + priority starter (E6) -----
    var phaseBCard = h("div", { className: "ag-card", style: "margin-top:1rem" });
    phaseBCard.appendChild(h("h3", { style: "margin-top:0;font-size:1rem" },
      "v1.4 Assessment Calibration"));
    phaseBCard.appendChild(h("p", {
      className: "ag-privacy-banner",
      style: "margin-bottom:0.75rem",
    }, t("privacy.banner", "All data stays in your browser — nothing is uploaded.")));

    // E5 — Sector select
    var sectorWrap = h("div", { className: "ag-field ag-sector-select" });
    var sectorId = "ag-sector-select";
    sectorWrap.appendChild(h("label", { className: "ag-label", htmlFor: sectorId },
      t("scoping.sector.label", "Institution type (sector calibration)")));
    sectorWrap.appendChild(h("span", { className: "ag-hint", id: sectorId + "-hint" },
      t("scoping.sector.hint",
        "Used to surface sector-specific pass criteria in each control's verification drawer.")));
    var sectorSel = h("select", {
      className: "ag-select",
      id: sectorId,
      "aria-describedby": sectorId + "-hint",
    });
    SECTOR_OPTIONS.forEach(function (o) {
      var label = o.labelKey ? t(o.labelKey, o.fallback || o.value) : o.value;
      var opt = h("option", { value: o.value }, label);
      if (o.value === (self.state.selectedSector || "")) opt.selected = true;
      sectorSel.appendChild(opt);
    });
    sectorSel.addEventListener("change", function () {
      self.state.selectedSector = sectorSel.value;
      // spa-fix-filter-namespace: persist sector under per-assessment slot
      // so two saved assessments can hold different sectors without leaking.
      try {
        var aid = (self.state && self.state.assessmentId) || "unscoped";
        localStorage.setItem(SECTOR_KEY + "-" + aid, sectorSel.value);
      } catch (e) { /* */ }
      self._debouncedSave();
    });
    sectorWrap.appendChild(sectorSel);
    phaseBCard.appendChild(sectorWrap);

    // E6 — Priority starter set radio
    var prioWrap = h("fieldset", { className: "ag-field ag-fieldset" });
    prioWrap.appendChild(h("legend", { className: "ag-label" },
      t("priorityRadio.label", "Phase 1 starting set")));
    var prioGroup = h("div", { className: "ag-priority-radio" });
    [
      { value: "starter", label: t("priorityRadio.starter",
          "Start with 5 Priority Foundation Controls (2.1, 1.4, 1.5, 1.7, 1.11)") },
      { value: "full", label: t("priorityRadio.full", "Full 78-control Phase 1") },
    ].forEach(function (opt) {
      var lbl = h("label", null);
      var radio = h("input", { type: "radio", name: "ag-priority-mode", value: opt.value });
      if ((self.state.priorityMode || "full") === opt.value) radio.checked = true;
      radio.addEventListener("change", function () {
        if (radio.checked) {
          self.state.priorityMode = opt.value;
          // Switching modes resets the expanded flag.
          self.state.priorityExpanded = false;
          self._debouncedSave();
        }
      });
      lbl.appendChild(radio);
      lbl.appendChild(document.createTextNode(" " + opt.label));
      prioGroup.appendChild(lbl);
    });
    prioWrap.appendChild(prioGroup);
    phaseBCard.appendChild(prioWrap);

    wrap.appendChild(phaseBCard);

    // Navigation
    var btns = h("div", { className: "ag-btn-group" });
    btns.appendChild(h("button", {
      className: "ag-btn ag-btn-secondary",
      onClick: function () { self.goToStep("welcome"); }
    }, "Back"));
    btns.appendChild(h("button", {
      className: "ag-btn ag-btn-primary",
      onClick: function () {
        // Defensive sync: if a <select> change event was missed (e.g. browser
        // autofill, programmatic value injection, or test harness), trust the
        // DOM as the source of truth before validating.
        var instSel = document.getElementById("ag-select-institution-type");
        if (instSel && instSel.value && instSel.value !== sc.institutionType) {
          sc.institutionType = instSel.value;
          var inst = self.data.institutionTypes[instSel.value];
          if (inst) sc.regulations = inst.regulations.slice();
        }
        if (!sc.organizationName) { alert("Please enter an organization name."); return; }
        if (!sc.institutionType) { alert("Please select an institution type."); return; }
        if (sc.zones.length === 0) { alert("Please select at least one zone."); return; }
        if (!self.state.assessmentName) {
          self.state.assessmentName = sc.organizationName + " — " + new Date().toISOString().slice(0, 10);
        }
        self.markStep("scoping");
        self.saveToStorage();
        self.goToStep("phase1");
      }
    }, "Begin Assessment"));
    wrap.appendChild(btns);

    parent.appendChild(wrap);
  };

  AssessmentApp.prototype.markStep = function (stepId) {
    if (!this.state.completedSteps) this.state.completedSteps = [];
    if (this.state.completedSteps.indexOf(stepId) < 0) {
      this.state.completedSteps.push(stepId);
    }
  };

  /* ---- Form helpers ---- */
  AssessmentApp.prototype.field = function (label, type, value, onChange, hint) {
    var inputId = "ag-field-" + label.toLowerCase().replace(/\s+/g, "-");
    var wrap = h("div", { className: "ag-field" });
    wrap.appendChild(h("label", { className: "ag-label", htmlFor: inputId }, label));
    if (hint) wrap.appendChild(h("span", { className: "ag-hint", id: inputId + "-hint" }, hint));
    var input = h("input", {
      className: "ag-input",
      type: type,
      value: value || "",
      id: inputId,
      maxlength: "120",
      "aria-describedby": hint ? inputId + "-hint" : null,
    });
    input.addEventListener("input", function () {
      // Defense-in-depth: enforce 120-char cap server-side too.
      if (input.value && input.value.length > 120) input.value = input.value.slice(0, 120);
      onChange(input.value);
    });
    wrap.appendChild(input);
    return wrap;
  };

  AssessmentApp.prototype.selectField = function (label, options, value, onChange) {
    var selectId = "ag-select-" + label.toLowerCase().replace(/\s+/g, "-");
    var wrap = h("div", { className: "ag-field" });
    wrap.appendChild(h("label", { className: "ag-label", htmlFor: selectId }, label));
    // autocomplete="off" + a unique randomized name suppress browser autofill,
    // which on <select> elements injects a visible label without firing the
    // change event listener below — leading to a state/DOM mismatch that
    // makes downstream validation falsely report "no selection".
    var sel = h("select", {
      className: "ag-select",
      id: selectId,
      name: selectId + "-" + Math.random().toString(36).slice(2, 8),
      autocomplete: "off",
    });
    options.forEach(function (o) {
      var opt = h("option", { value: o.value }, o.label);
      if (o.value === value) opt.selected = true;
      sel.appendChild(opt);
    });
    // Force the DOM value to match incoming state so the visible selection
    // and `sel.value` stay in lockstep at render time, even if the browser
    // tries to restore an autofilled value.
    sel.value = value || "";
    sel.addEventListener("change", function () { onChange(sel.value); });
    wrap.appendChild(sel);
    return wrap;
  };

  AssessmentApp.prototype.checkboxGroup = function (label, items, onChange, hint) {
    var fieldset = h("fieldset", { className: "ag-field ag-fieldset" });
    fieldset.appendChild(h("legend", { className: "ag-label" }, label));
    if (hint) {
      fieldset.appendChild(hint);
    }
    var group = h("div", { className: "ag-check-group" });
    items.forEach(function (item) {
      var lbl = h("label", { className: "ag-check-label" });
      var cb = h("input", { type: "checkbox", value: String(item.value) });
      cb.checked = item.checked;
      cb.addEventListener("change", function () {
        var vals = [];
        group.querySelectorAll("input:checked").forEach(function (el) { vals.push(el.value); });
        onChange(vals);
      });
      lbl.appendChild(cb);
      if (item.description) {
        var wrap = h("span", { className: "ag-check-label-content" });
        wrap.appendChild(h("span", null, item.label));
        wrap.appendChild(h("span", { className: "ag-check-desc" }, item.description));
        lbl.appendChild(wrap);
      } else {
        lbl.appendChild(document.createTextNode(item.label));
      }
      group.appendChild(lbl);
    });
    fieldset.appendChild(group);
    return fieldset;
  };

  /* ================================================================
     STEP 3: PHASE 1 — CONTROL-LEVEL ASSESSMENT
     ================================================================ */
  AssessmentApp.prototype.renderPhase1 = function (parent) {
    var self = this;
    var wrap = h("div");

    wrap.appendChild(h("h2", { style: "font-size:1.3rem;margin-bottom:0.3rem" }, "Phase 1: Control-Level Assessment"));
    wrap.appendChild(h("p", { className: "ag-card-subtitle" },
      "For each control, indicate your organization's implementation status."
    ));

    // Instructional callout
    var callout = h("div", { className: "ag-callout" });
    callout.appendChild(h("strong", null, "How to answer: "));
    callout.appendChild(document.createTextNode(
      "For each control, assess your organization\u2019s current implementation. "));
    callout.appendChild(h("strong", null, "Yes"));
    callout.appendChild(document.createTextNode(" = fully in place, "));
    callout.appendChild(h("strong", null, "Partial"));
    callout.appendChild(document.createTextNode(" = some aspects implemented (triggers detailed drill-down), "));
    callout.appendChild(h("strong", null, "No"));
    callout.appendChild(document.createTextNode(" = not yet started, "));
    callout.appendChild(h("strong", null, "N/A"));
    callout.appendChild(document.createTextNode(" = not applicable to your organization."));
    wrap.appendChild(callout);

    // ----- v1.4 Phase B: privacy banner (reaffirmed every step) -----
    wrap.appendChild(h("div", { className: "ag-privacy-banner" },
      t("privacy.banner", "All data stays in your browser — nothing is uploaded.")));

    // ----- E9 — Facilitator mode banner + session timer -----
    var facilitator = isFacilitatorMode();
    if (facilitator) {
      wrap.appendChild(h("div", { className: "ag-facilitator-banner" },
        t("facilitator.modeBanner",
          "Facilitator mode active — guided prompts and timing badges are shown.")));
      wrap.appendChild(this.renderSessionTimer());
    }

    // ----- E2 — Auto-mark excluded controls as N/A before computing progress -----
    this.applyZoneExclusions();

    // Progress
    // Edit H — split label into user-answered vs auto-N/A. Bar fill is
    // unchanged: auto-N/A still counts toward "completed" for scoping.
    var responses = this.state.responses || {};
    var responseKeys = Object.keys(responses);
    var answered = responseKeys.length;
    var total = this.data.controls.length;
    var pct = Math.round((answered / total) * 100);
    var userCount = 0;
    var autoNaCount = 0;
    responseKeys.forEach(function (k) {
      var r = responses[k];
      if (!r || !r.answer) return;
      if (r.autoNa) { autoNaCount++; } else { userCount++; }
    });
    var remaining = total - userCount - autoNaCount;
    if (remaining < 0) remaining = 0;
    var labelText = "Answered: " + userCount + " user / " + autoNaCount +
      " auto-N/A \u2014 " + remaining + " remaining";
    var progressText = h("div", { className: "ag-progress-text" }, labelText);
    wrap.appendChild(progressText);
    var progress = h("div", { className: "ag-progress" });
    progress.appendChild(h("div", {
      className: "ag-progress-bar",
      role: "progressbar",
      "aria-valuenow": String(pct),
      "aria-valuemin": "0",
      "aria-valuemax": "100",
      "aria-label": "Assessment progress",
      style: "width:" + pct + "%",
    }));
    wrap.appendChild(progress);

    // Live region for progress announcements
    var liveRegion = h("div", {
      className: "ag-sr-only",
      "aria-live": "polite",
      "aria-atomic": "true",
      id: "ag-progress-live",
    });
    wrap.appendChild(liveRegion);

    // Save button + scoring help
    var topBtns = h("div", { className: "ag-btn-group", style: "margin-bottom:1rem" });
    topBtns.appendChild(h("button", {
      className: "ag-btn ag-btn-sm ag-btn-secondary",
      onClick: function () { self.exportJSON(); }
    }, "Save to File"));
    topBtns.appendChild(h("button", {
      className: "ag-btn ag-btn-sm ag-btn-secondary ag-import-collector-btn",
      type: "button",
      onClick: function () { self.openCollectorImport(); }
    }, t("import_collector_button", "Import collector evidence")));
    topBtns.appendChild(h("button", {
      className: "ag-info-btn",
      onClick: function () { self.showScoringModal(); }
    }, "\u2139 How Scoring Works"));
    wrap.appendChild(topBtns);

    // ----- E4 — Role filter dropdown + count badge -----
    var filterWrap = h("div", { className: "ag-role-filter" });
    var filterId = "ag-role-filter-select";
    filterWrap.appendChild(h("label", { htmlFor: filterId },
      t("filter.role.label", "Filter by role") + ":"));
    var filterSel = h("select", { id: filterId, "aria-label": t("filter.role.label", "Filter by role") });
    var currentRoleFilter = self.state.roleFilter || "";
    ROLE_FILTER_OPTIONS.forEach(function (o) {
      var label = o.labelKey ? t(o.labelKey, o.fallback || o.value) : o.value;
      var opt = h("option", { value: o.value }, label);
      if (o.value === currentRoleFilter) opt.selected = true;
      filterSel.appendChild(opt);
    });
    var countBadge = h("span", { className: "ag-role-filter-count", id: "ag-role-filter-count" }, "");
    filterSel.addEventListener("change", function () {
      self.state.roleFilter = filterSel.value;
      // spa-fix-filter-namespace: persist role filter under per-assessment
      // slot to prevent leakage across assessments.
      try {
        var aid = (self.state && self.state.assessmentId) || "unscoped";
        localStorage.setItem(ROLE_FILTER_KEY + "-" + aid, filterSel.value);
      } catch (e) { /* */ }
      self._debouncedSave();
      self.applyRoleFilter();
    });
    filterWrap.appendChild(filterSel);
    filterWrap.appendChild(countBadge);
    wrap.appendChild(filterWrap);

    // ----- E6 — Determine starter-mode visible IDs -----
    var starterMode = (self.state.priorityMode === "starter") && !self.state.priorityExpanded;
    var starterContinueBtn = null;

    // Group by pillar
    var pillars = [
      { num: 1, name: "Pillar 1 — Security" },
      { num: 2, name: "Pillar 2 — Management" },
      { num: 3, name: "Pillar 3 — Reporting" },
      { num: 4, name: "Pillar 4 — SharePoint" },
    ];

    if (starterMode) {
      // Render the 5 priority controls in their pillar order, no pillar grouping.
      var starterCard = h("div", { className: "ag-pillar-group" });
      var starterHeader = h("div", { className: "ag-pillar-header ag-pillar-header-static" });
      starterHeader.appendChild(h("span", { className: "ag-pillar-name" },
        t("priorityRadio.starterHeading", "Priority foundation controls")));
      starterHeader.appendChild(h("span", { className: "ag-pillar-count" },
        STARTER_PRIORITY_IDS.length + " controls"));
      starterCard.appendChild(starterHeader);
      var starterBody = h("div", { className: "ag-pillar-controls" });
      STARTER_PRIORITY_IDS.forEach(function (cid) {
        var ctrl = null;
        for (var i = 0; i < self.data.controls.length; i++) {
          if (self.data.controls[i].id === cid) { ctrl = self.data.controls[i]; break; }
        }
        if (!ctrl) return;
        starterBody.appendChild(self.renderControlCard(ctrl, { facilitator: facilitator }));
      });
      starterCard.appendChild(starterBody);
      wrap.appendChild(starterCard);

      // "Continue to full Phase 1" button — enabled once all 5 starters answered.
      starterContinueBtn = h("button", {
        className: "ag-btn ag-btn-primary ag-priority-continue",
        type: "button",
      }, t("priorityRadio.continue", "Continue to full Phase 1"));
      var allStarterAnswered = STARTER_PRIORITY_IDS.every(function (cid) {
        var r = self.state.responses[cid];
        return r && r.answer;
      });
      starterContinueBtn.disabled = !allStarterAnswered;
      starterContinueBtn.addEventListener("click", function () {
        if (starterContinueBtn.disabled) return;
        self.state.priorityExpanded = true;
        self.saveToStorage();
        self.render();
      });
      wrap.appendChild(starterContinueBtn);
    } else {
      pillars.forEach(function (p) {
        var controls = self.data.controls.filter(function (c) { return c.pillar === p.num; });
        var answeredInPillar = controls.filter(function (c) { return self.state.responses[c.id]; }).length;
        var allAnswered = answeredInPillar === controls.length;

        var group = h("div", { className: "ag-pillar-group" });
        var header = h("div", {
          className: "ag-pillar-header" + (allAnswered ? " collapsed" : ""),
          role: "button",
          tabindex: "0",
          "aria-expanded": allAnswered ? "false" : "true",
          "aria-controls": "ag-pillar-" + p.num,
        });
        header.appendChild(h("span", { className: "ag-pillar-name" }, p.name));
        header.appendChild(h("span", { className: "ag-pillar-count" },
          answeredInPillar + "/" + controls.length));
        group.appendChild(header);

        var controlsContainer = h("div", {
          className: "ag-pillar-controls" + (allAnswered ? " collapsed" : ""),
          id: "ag-pillar-" + p.num,
        });
        controls.forEach(function (ctrl) {
          controlsContainer.appendChild(self.renderControlCard(ctrl, { facilitator: facilitator }));
        });
        group.appendChild(controlsContainer);

        // Toggle collapse
        var toggle = function () {
          var isCollapsed = controlsContainer.classList.contains("collapsed");
          if (isCollapsed) {
            controlsContainer.classList.remove("collapsed");
            header.classList.remove("collapsed");
            header.setAttribute("aria-expanded", "true");
          } else {
            controlsContainer.classList.add("collapsed");
            header.classList.add("collapsed");
            header.setAttribute("aria-expanded", "false");
          }
        };
        header.addEventListener("click", toggle);
        header.addEventListener("keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); }
        });

        wrap.appendChild(group);
      });
    }

    // Navigation
    var btns = h("div", { className: "ag-btn-group" });
    btns.appendChild(h("button", {
      className: "ag-btn ag-btn-secondary",
      onClick: function () { self.goToStep("scoping"); }
    }, "Back to Scoping"));

    var gaps = this.getGapControls();
    if (gaps.length > 0) {
      btns.appendChild(h("button", {
        className: "ag-btn ag-btn-primary",
        onClick: function () {
          self.markStep("phase1");
          self.saveToStorage();
          self.goToStep("phase2");
        }
      }, "Phase 2: Drill-Down (" + gaps.length + " gaps)"));
    }

    btns.appendChild(h("button", {
      className: "ag-btn ag-btn-primary",
      onClick: function () {
        self.markStep("phase1");
        self.saveToStorage();
        if (!self._savePrompted) {
          self._savePrompted = true;
          if (confirm("Would you like to save your assessment to a file before viewing results? " +
            "You can also export later from the Export page.")) {
            self.exportJSON();
          }
        }
        self.goToStep("results");
      }
    }, "View Results"));
    wrap.appendChild(btns);

    parent.appendChild(wrap);

    // Apply role filter visibility now that DOM is in the tree.
    self.applyRoleFilter();
  };

  /**
   * Hide/show control cards based on the current role filter and refresh
   * the count badge. Cards are not removed — purely a CSS display toggle so
   * the user can flip filters without re-rendering 78 rows.
   */
  AssessmentApp.prototype.applyRoleFilter = function () {
    if (!this.el) return;
    var roleFilter = (this.state && this.state.roleFilter) || "";
    var cards = this.el.querySelectorAll(".ag-control-card[data-control-id]");
    var visible = 0;
    var total = cards.length;
    var self = this;
    cards.forEach(function (card) {
      var cid = card.getAttribute("data-control-id");
      var ctrl = (self.controlsById && self.controlsById.get(cid)) || null;
      if (!ctrl) {
        for (var i = 0; i < self.data.controls.length; i++) {
          if (self.data.controls[i].id === cid) { ctrl = self.data.controls[i]; break; }
        }
      }
      if (!ctrl) return;
      var match = self.controlMatchesRoleFilter(ctrl, roleFilter);
      card.style.display = match ? "" : "none";
      if (match) visible++;
    });
    var badge = this.el.querySelector("#ag-role-filter-count");
    if (badge) {
      badge.textContent = tFmt("filter.role.count", "Showing {n} of {total}",
        { n: visible, total: total });
    }
  };


  AssessmentApp.prototype.renderControlCard = function (ctrl, options) {
    var self = this;
    options = options || {};
    var facilitator = !!options.facilitator;
    var resp = this.state.responses[ctrl.id] || {};
    var excluded = this.isControlExcluded(ctrl);
    var override = (this.state.overrides && this.state.overrides[ctrl.id]) || null;

    var cls = "ag-control-card";
    if (resp.answer === "yes") cls += " answered";
    else if (resp.answer === "partial") cls += " partial";
    else if (resp.answer === "no") cls += " gap";
    if (excluded) cls += " ag-row-excluded";

    var card = h("div", {
      className: cls,
      "data-control-id": ctrl.id,
    });

    // Header
    var header = h("div", { className: "ag-control-header" });
    var left = h("div", { style: "flex:1" });
    var titleLine = h("div", { style: "display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap" });
    titleLine.appendChild(h("span", { className: "ag-control-id" }, ctrl.id));
    titleLine.appendChild(h("span", { className: "ag-control-title" }, ctrl.title));
    // E9 — facilitator time-budget badge
    if (facilitator && ctrl.facilitatorNotes && typeof ctrl.facilitatorNotes.timeBudgetMinutes === "number") {
      titleLine.appendChild(h("span", { className: "ag-time-badge" },
        tFmt("facilitator.timeBadge", "{n} min", { n: ctrl.facilitatorNotes.timeBudgetMinutes })));
    }
    if (override && override.applicable) {
      titleLine.appendChild(h("span", { className: "ag-override-active-tag" },
        t("exclusion.overrideActive", "Override active — control marked applicable")));
    }
    if (resp && resp.importedFromCollector) {
      titleLine.appendChild(h("span", {
        className: "ag-imported-badge",
        title: resp.evidenceRef || "",
      }, t("import_badge_label", "From collector")));
    }
    left.appendChild(titleLine);

    // Badges
    var badges = h("div", { className: "ag-control-badges", style: "margin-top:0.3rem" });
    if (ctrl.adoptionPhase) {
      var pCls = "ag-badge ag-badge-" + ctrl.adoptionPhase.priority.toLowerCase();
      badges.appendChild(h("span", { className: pCls }, "Phase " + ctrl.adoptionPhase.phase + " " + ctrl.adoptionPhase.priority));
    }
    if (ctrl.solutions && ctrl.solutions.length > 0) {
      badges.appendChild(h("span", { className: "ag-badge ag-badge-solution" }, "Automation"));
    }
    left.appendChild(badges);
    header.appendChild(left);
    card.appendChild(header);

    // Objective (prefer question form if available)
    var displayText = ctrl.questionText || ctrl.objective;
    if (displayText) {
      card.appendChild(h("div", { className: "ag-control-objective" }, displayText));
    }

    // E2 — Excluded banner + override flow
    if (excluded) {
      var exclBanner = h("div", { className: "ag-exclusion-banner" },
        t("exclusion.banner",
          "This control's applicable zones do not intersect your active scoping zones. It has been auto-marked N/A."));
      card.appendChild(exclBanner);

      var overrideBtn = h("button", {
        className: "ag-override-btn",
        type: "button",
        "aria-expanded": "false",
      }, t("exclusion.override", "Override — mark as applicable"));
      var overrideForm = h("div", { style: "display:none;margin-top:0.4rem" });
      var overrideTextarea = h("textarea", {
        className: "ag-override-note",
        placeholder: t("exclusion.overrideNotePlaceholder",
          "Briefly note why this control should remain applicable…"),
        "aria-label": "Override note for " + ctrl.id,
        rows: "2",
      });
      var overrideSave = h("button", {
        className: "ag-btn ag-btn-sm ag-btn-primary",
        type: "button",
        style: "margin-top:0.3rem",
      }, t("exclusion.overrideSave", "Save override"));
      overrideForm.appendChild(overrideTextarea);
      overrideForm.appendChild(overrideSave);
      overrideBtn.addEventListener("click", function () {
        var open = overrideForm.style.display !== "none";
        overrideForm.style.display = open ? "none" : "block";
        overrideBtn.setAttribute("aria-expanded", open ? "false" : "true");
        if (!open) overrideTextarea.focus();
      });
      overrideSave.addEventListener("click", function () {
        var note = overrideTextarea.value.trim();
        if (!note) { alert("Please enter a brief override note."); return; }
        if (!self.state.overrides) self.state.overrides = {};
        self.state.overrides[ctrl.id] = { applicable: true, note: note };
        // Clear the auto-NA so the user can rate freely.
        if (self.state.responses[ctrl.id] && self.state.responses[ctrl.id].autoNa) {
          delete self.state.responses[ctrl.id];
        }
        self.saveToStorage();
        self.render();
      });
      card.appendChild(overrideBtn);
      card.appendChild(overrideForm);
    } else if (override && override.applicable) {
      // Allow removing override
      var removeOverrideBtn = h("button", {
        className: "ag-override-btn",
        type: "button",
      }, t("exclusion.overrideRemove", "Remove override"));
      removeOverrideBtn.addEventListener("click", function () {
        if (self.state.overrides) delete self.state.overrides[ctrl.id];
        self.saveToStorage();
        self.render();
      });
      card.appendChild(removeOverrideBtn);
    }

    // E9 — facilitator notes (ask + follow-up) above rating buttons
    if (facilitator && ctrl.facilitatorNotes) {
      var ask = ctrl.facilitatorNotes.ask;
      var fu = ctrl.facilitatorNotes.followUp;
      if (ask && String(ask).indexOf("TODO:") !== 0) {
        card.appendChild(h("blockquote", { className: "ag-facilitator-ask" }, ask));
      }
      if (fu && String(fu).indexOf("TODO:") !== 0) {
        card.appendChild(h("p", { className: "ag-facilitator-followup" },
          t("facilitator.followUp", "Follow-up:") + " " + fu));
      }
    }

    // Answer buttons (disabled when excluded without override)
    var answerGroup = h("div", { className: "ag-answer-group", role: "group", "aria-label": "Implementation status for " + ctrl.id });
    ANSWERS.forEach(function (a) {
      var bcls = "ag-answer-btn";
      var isPressed = resp.answer === a.value;
      if (isPressed) bcls += " " + a.cls;
      var btnAttrs = {
        className: bcls,
        "aria-pressed": isPressed ? "true" : "false",
        type: "button",
      };
      if (excluded) btnAttrs.disabled = "disabled";
      var btn = h("button", btnAttrs, a.label);
      if (!excluded) {
        btn.addEventListener("click", function () {
          self.state.responses[ctrl.id] = self.state.responses[ctrl.id] || {};
          self.state.responses[ctrl.id].answer = a.value;
          // Clear autoNa marker — user has now provided an explicit answer.
          delete self.state.responses[ctrl.id].autoNa;
          self.saveToStorage();
          card.className = "ag-control-card" +
            (a.value === "yes" ? " answered" : a.value === "partial" ? " partial" : a.value === "no" ? " gap" : "");
          if (excluded) card.className += " ag-row-excluded";
          card.setAttribute("data-control-id", ctrl.id);
          answerGroup.querySelectorAll(".ag-answer-btn").forEach(function (b) {
            b.className = "ag-answer-btn";
            b.setAttribute("aria-pressed", "false");
          });
          btn.className = "ag-answer-btn " + a.cls;
          btn.setAttribute("aria-pressed", "true");
          self.updateProgress();
          // Re-evaluate starter "Continue" button if in starter mode.
          self._refreshStarterContinue();
        });
      }
      answerGroup.appendChild(btn);
    });
    card.appendChild(answerGroup);

    // E1 — "How to verify" drawer toggle (lazy content)
    var drawerId = "ag-drawer-" + ctrl.id.replace(/\./g, "-");
    var drawerToggle = h("button", {
      className: "ag-drawer-toggle",
      type: "button",
      "aria-expanded": "false",
      "aria-controls": drawerId,
    }, t("drawer.toggleOpen", "How to verify"));
    var drawer = h("div", {
      className: "ag-drawer",
      id: drawerId,
      role: "region",
      "aria-label": "Verification details for " + ctrl.id,
      tabindex: "-1",
    });
    var drawerLoaded = false;
    drawerToggle.addEventListener("click", function () {
      var isOpen = drawer.classList.contains("ag-drawer-open");
      if (isOpen) {
        drawer.classList.remove("ag-drawer-open");
        drawerToggle.setAttribute("aria-expanded", "false");
        drawerToggle.textContent = t("drawer.toggleOpen", "How to verify");
        drawerToggle.focus();
      } else {
        if (!drawerLoaded) {
          drawer.appendChild(self.renderDrawerContent(ctrl));
          self._bindDrawerKeyboard(drawer, drawerToggle);
          drawerLoaded = true;
        }
        drawer.classList.add("ag-drawer-open");
        drawerToggle.setAttribute("aria-expanded", "true");
        drawerToggle.textContent = t("drawer.toggleClose", "Hide verification details");
        // Move focus into the drawer for keyboard users.
        var focusables = drawer.querySelectorAll(
          'a[href],button:not([disabled]),textarea,input,select,[tabindex]:not([tabindex="-1"])'
        );
        if (focusables.length) focusables[0].focus();
        else drawer.focus();
      }
    });
    card.appendChild(drawerToggle);
    card.appendChild(drawer);

    // E7 — Inline notes textarea + evidence reference input (always visible).
    var notesLabel = h("label", { className: "ag-row-input-label", htmlFor: "ag-notes-" + ctrl.id },
      t("row.notes", "Notes"));
    var notesArea = h("textarea", {
      className: "ag-textarea",
      id: "ag-notes-" + ctrl.id,
      style: "margin-top:0.2rem;display:block",
      placeholder: t("row.notesPlaceholder", "Notes (optional)"),
      "aria-label": "Notes for control " + ctrl.id,
      rows: "2",
    });
    notesArea.value = resp.notes || "";
    notesArea.addEventListener("input", function () {
      self.state.responses[ctrl.id] = self.state.responses[ctrl.id] || {};
      self.state.responses[ctrl.id].notes = notesArea.value;
      self._debouncedSave();
    });
    card.appendChild(notesLabel);
    card.appendChild(notesArea);

    var evLabel = h("label", { className: "ag-row-input-label", htmlFor: "ag-evref-" + ctrl.id },
      t("row.evidenceRef", "Evidence reference (file path or URL)"));
    var evInput = h("input", {
      className: "ag-evidence-ref",
      id: "ag-evref-" + ctrl.id,
      type: "text",
      placeholder: t("row.evidenceRefPlaceholder", "e.g., \\\\fileshare\\evidence\\1.1\\screenshot.png"),
      "aria-label": "Evidence reference for control " + ctrl.id,
      value: resp.evidenceRef || "",
    });
    evInput.value = resp.evidenceRef || "";
    evInput.addEventListener("input", function () {
      self.state.responses[ctrl.id] = self.state.responses[ctrl.id] || {};
      self.state.responses[ctrl.id].evidenceRef = evInput.value;
      self._debouncedSave();
    });
    card.appendChild(evLabel);
    card.appendChild(evInput);

    return card;
  };

  /** If in starter mode, recompute whether the "Continue to full Phase 1" button should be enabled. */
  AssessmentApp.prototype._refreshStarterContinue = function () {
    if (!this.state || this.state.priorityMode !== "starter" || this.state.priorityExpanded) return;
    if (!this.el) return;
    var btn = this.el.querySelector(".ag-priority-continue");
    if (!btn) return;
    var self = this;
    var allAnswered = STARTER_PRIORITY_IDS.every(function (cid) {
      var r = self.state.responses[cid];
      return r && r.answer;
    });
    btn.disabled = !allAnswered;
  };

  AssessmentApp.prototype.updateProgress = function () {
    // Edit H — split label into user-answered vs auto-N/A. Bar fill is
    // unchanged: auto-N/A still counts toward "completed" for scoping.
    var responses = this.state.responses || {};
    var responseKeys = Object.keys(responses);
    var answered = responseKeys.length;
    var total = this.data.controls.length;
    var pct = Math.round((answered / total) * 100);
    var userCount = 0;
    var autoNaCount = 0;
    responseKeys.forEach(function (k) {
      var r = responses[k];
      if (!r || !r.answer) return;
      if (r.autoNa) { autoNaCount++; } else { userCount++; }
    });
    var remaining = total - userCount - autoNaCount;
    if (remaining < 0) remaining = 0;
    var msg = "Answered: " + userCount + " user / " + autoNaCount +
      " auto-N/A \u2014 " + remaining + " remaining";
    var txt = this.el.querySelector(".ag-progress-text");
    if (txt) txt.textContent = msg;
    var bar = this.el.querySelector(".ag-progress-bar");
    if (bar) {
      bar.style.width = pct + "%";
      bar.setAttribute("aria-valuenow", pct);
    }
    // Announce milestone progress to screen readers (every 10%)
    if (pct % 10 === 0 || answered === total) {
      var live = this.el.querySelector("#ag-progress-live");
      if (live) live.textContent = msg;
    }
  };

  /* ================================================================
     STEP 4: PHASE 2 — DRILL-DOWN
     ================================================================ */
  AssessmentApp.prototype.renderPhase2 = function (parent) {
    var self = this;
    var wrap = h("div");
    var gaps = this.getGapControls();

    wrap.appendChild(h("h2", { style: "font-size:1.3rem;margin-bottom:0.3rem" }, "Phase 2: Gap Drill-Down"));
    wrap.appendChild(h("p", { className: "ag-card-subtitle" },
      "For each gap or partial control, answer detailed sub-questions to refine your score. " +
      "This phase is presented by pillar so sections can be delegated to the responsible admin."
    ));

    // Phase 2 reminder
    wrap.appendChild(h("div", { className: "ag-disclaimer", style: "background:var(--md-default-fg-color--lightest);border-left-color:var(--md-primary-fg-color)" },
      "Phase 2 refines Partial scores using verification criteria sub-questions. " +
      "This helps distinguish between partially-implemented controls and informs remediation planning."
    ));

    if (gaps.length === 0) {
      wrap.appendChild(h("div", { className: "ag-card" },
        h("p", null, "No gaps detected. All controls are fully implemented or marked N/A.")));
    } else {
      // Group by pillar
      var byPillar = {};
      gaps.forEach(function (c) {
        if (!byPillar[c.pillar]) byPillar[c.pillar] = [];
        byPillar[c.pillar].push(c);
      });

      // Export section button + scoring help
      var exportBtns = h("div", { className: "ag-btn-group", style: "margin-bottom:1rem" });
      exportBtns.appendChild(h("button", {
        className: "ag-btn ag-btn-sm ag-btn-secondary",
        onClick: function () { self.exportJSON(); }
      }, "Save to File"));
      exportBtns.appendChild(h("button", {
        className: "ag-info-btn",
        onClick: function () { self.showScoringModal(); }
      }, "\u2139 How Scoring Works"));
      wrap.appendChild(exportBtns);

      // Role-specific export
      var roles = Object.keys(this.data.roleAssignments);
      var roleBtns = h("div", { className: "ag-btn-group", style: "margin-bottom:1rem" });
      roleBtns.appendChild(h("span", { style: "font-size:0.82rem;align-self:center" }, "Export section for:"));
      roles.forEach(function (role) {
        roleBtns.appendChild(h("button", {
          className: "ag-btn ag-btn-sm ag-btn-secondary",
          onClick: function () { self.exportRoleSection(role); }
        }, role));
      });
      wrap.appendChild(roleBtns);

      Object.keys(byPillar).sort().forEach(function (pNum) {
        var pillarName = self.data.pillars[pNum].name;
        var controls = byPillar[pNum];

        var group = h("div", { className: "ag-pillar-group" });
        var header = h("div", { className: "ag-pillar-header ag-pillar-header-static" });
        header.appendChild(h("span", { className: "ag-pillar-name" },
          "Pillar " + pNum + " — " + pillarName));
        header.appendChild(h("span", { className: "ag-pillar-count" },
          controls.length + " gap" + (controls.length > 1 ? "s" : "")));
        group.appendChild(header);

        controls.forEach(function (ctrl) {
          group.appendChild(self.renderDrilldownCard(ctrl));
        });
        wrap.appendChild(group);
      });
    }

    // Navigation
    var btns = h("div", { className: "ag-btn-group" });
    btns.appendChild(h("button", {
      className: "ag-btn ag-btn-secondary",
      onClick: function () { self.goToStep("phase1"); }
    }, "Back to Phase 1"));
    btns.appendChild(h("button", {
      className: "ag-btn ag-btn-primary",
      onClick: function () {
        self.markStep("phase2");
        self.saveToStorage();
        if (!self._savePrompted) {
          self._savePrompted = true;
          if (confirm("Would you like to save your assessment to a file before viewing results? " +
            "You can also export later from the Export page.")) {
            self.exportJSON();
          }
        }
        self.goToStep("results");
      }
    }, "View Results"));
    wrap.appendChild(btns);

    parent.appendChild(wrap);
  };

  AssessmentApp.prototype.renderDrilldownCard = function (ctrl) {
    var self = this;
    var card = h("div", { className: "ag-card" });

    var header = h("div", { style: "margin-bottom:0.75rem" });
    var titleLine = h("div", { style: "display:flex;align-items:center;gap:0.5rem" });
    titleLine.appendChild(h("span", { className: "ag-control-id" }, ctrl.id));
    titleLine.appendChild(h("span", { className: "ag-control-title" }, ctrl.title));
    var resp = this.state.responses[ctrl.id] || {};
    var statusLabel = resp.answer === "partial" ? " (Partial)" : " (No)";
    titleLine.appendChild(h("span", { style: "font-size:0.8rem;color:var(--md-default-fg-color--light)" }, statusLabel));
    header.appendChild(titleLine);
    card.appendChild(header);

    // Generate sub-questions from verification criteria
    var questions = ctrl.verificationCriteria.slice(0, 12); // Cap at 12
    if (questions.length === 0) {
      card.appendChild(h("p", { style: "font-size:0.82rem;color:var(--md-default-fg-color--light)" },
        "No verification criteria available for drill-down."));
      return card;
    }

    if (!this.state.drilldown[ctrl.id]) this.state.drilldown[ctrl.id] = {};
    var dd = this.state.drilldown[ctrl.id];

    // Score display
    var scoreEl = h("div", {
      style: "font-size:0.82rem;margin-bottom:0.5rem;font-weight:600"
    });
    var updateScore = function () {
      var keys = Object.keys(dd);
      var answered = keys.filter(function (k) { return dd[k]; }).length;
      var yesCount = keys.filter(function (k) { return dd[k] === "yes"; }).length;
      if (answered > 0) {
        var pct = Math.round((yesCount / questions.length) * 100);
        scoreEl.textContent = "Refined score: " + pct + "% (" + yesCount + "/" + questions.length + " met)";
        scoreEl.style.color = pct >= 80 ? "var(--ag-green)" : pct >= 50 ? "var(--ag-amber)" : "var(--ag-red)";
      } else {
        scoreEl.textContent = "";
      }
    };
    card.appendChild(scoreEl);

    questions.forEach(function (q, idx) {
      var qId = "q" + idx;
      var row = h("div", { className: "ag-drilldown-q" });
      row.appendChild(h("span", { style: "flex:1;margin-right:0.5rem" }, q));
      var btns = h("div", { className: "ag-drilldown-btns" });

      ["yes", "no"].forEach(function (val) {
        var bcls = "ag-answer-btn ag-btn-sm";
        var isPressed = dd[qId] === val;
        if (isPressed) bcls += " " + (val === "yes" ? "selected" : "selected-no");
        var btn = h("button", {
          className: bcls,
          "aria-pressed": isPressed ? "true" : "false",
          onClick: function () {
            dd[qId] = val;
            self.saveToStorage();
            // Update button states in this row
            btns.querySelectorAll(".ag-answer-btn").forEach(function (b) {
              b.className = "ag-answer-btn ag-btn-sm";
              b.setAttribute("aria-pressed", "false");
            });
            btn.className = "ag-answer-btn ag-btn-sm " + (val === "yes" ? "selected" : "selected-no");
            btn.setAttribute("aria-pressed", "true");
            updateScore();
          }
        }, val === "yes" ? "Yes" : "No");
        btns.appendChild(btn);
      });

      row.appendChild(btns);
      card.appendChild(row);
    });

    updateScore();
    return card;
  };

  AssessmentApp.prototype.exportRoleSection = function (role) {
    var controlIds = this.data.roleAssignments[role] || [];
    var sectionData = {
      _metadata: this.buildExportMetadata("section"),
      assessmentId: this.state.assessmentId,
      sectionExport: {
        role: role,
        controlIds: controlIds,
        exportedAt: new Date().toISOString(),
        exportedBy: this.state.scoping.assessorName || "",
      },
      scoping: this.state.scoping,
      responses: {},
      drilldown: {},
    };
    var self = this;
    controlIds.forEach(function (cid) {
      if (self.state.responses[cid]) sectionData.responses[cid] = self.state.responses[cid];
      if (self.state.drilldown[cid]) sectionData.drilldown[cid] = self.state.drilldown[cid];
    });
    var blob = new Blob([JSON.stringify(sectionData, null, 2)], { type: "application/json" });
    var safeName = role.replace(/\s+/g, "-").toLowerCase();
    downloadBlob(blob, "assessment-section-" + safeName + ".json");
  };

  /* ================================================================
     STEP 5: RESULTS DASHBOARD
     ================================================================ */
  AssessmentApp.prototype.renderResults = function (parent) {
    var self = this;
    var wrap = h("div");

    // Print header (hidden on screen, shown in print)
    var printHeader = h("div", { className: "ag-print-header", style: "display:none" });
    printHeader.appendChild(h("h1", null, "Governance Readiness Assessment Report"));
    printHeader.appendChild(h("p", null,
      (this.state.assessmentName || "Assessment") + " — " + fmtDate(this.state.updatedAt)));
    printHeader.appendChild(h("p", null,
      "Organization: " + (this.state.scoping.organizationName || "—") +
      " | Assessor: " + (this.state.scoping.assessorName || "—")));
    wrap.appendChild(printHeader);

    wrap.appendChild(h("h2", { style: "font-size:1.3rem;margin-bottom:0.3rem" }, "Results Dashboard"));

    // Disclaimer
    wrap.appendChild(h("div", { className: "ag-disclaimer" },
      "This assessment helps support governance readiness. Scores reflect self-reported implementation " +
      "status and do not constitute a compliance certification."
    ));

    // Tabs
    var tabs = [
      { id: "scorecard", label: "Executive Scorecard" },
      { id: "regulatory", label: "Regulatory Exposure" },
      { id: "zones", label: "Zone Analysis" },
      { id: "gaps", label: "Gap Analysis" },
      { id: "responses", label: "Review Responses" },
      { id: "roadmap", label: "Remediation Roadmap" },
    ];
    var tabBar = h("div", { className: "ag-tabs", role: "tablist", "aria-label": "Results views" });
    var panels = h("div");

    var activateTab = function (tabEl, tabId) {
      tabBar.querySelectorAll(".ag-tab").forEach(function (b) {
        b.className = "ag-tab";
        b.setAttribute("aria-selected", "false");
        b.setAttribute("tabindex", "-1");
      });
      tabEl.className = "ag-tab active";
      tabEl.setAttribute("aria-selected", "true");
      tabEl.setAttribute("tabindex", "0");
      tabEl.focus();
      panels.querySelectorAll(".ag-tab-panel").forEach(function (p) { p.className = "ag-tab-panel"; });
      var panel = panels.querySelector('[data-tab="' + tabId + '"]');
      if (panel) panel.className = "ag-tab-panel active";
    };

    tabs.forEach(function (t, idx) {
      var tabId = "ag-tab-" + t.id;
      var panelId = "ag-panel-" + t.id;
      var tab = h("button", {
        className: "ag-tab" + (idx === 0 ? " active" : ""),
        role: "tab",
        id: tabId,
        "aria-selected": idx === 0 ? "true" : "false",
        "aria-controls": panelId,
        tabindex: idx === 0 ? "0" : "-1",
        onClick: function () { activateTab(tab, t.id); },
        onKeydown: function (e) {
          var tabEls = Array.prototype.slice.call(tabBar.querySelectorAll(".ag-tab"));
          var curIdx = tabEls.indexOf(tab);
          var nextIdx = -1;
          if (e.key === "ArrowRight" || e.key === "ArrowDown") {
            nextIdx = (curIdx + 1) % tabEls.length;
          } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
            nextIdx = (curIdx - 1 + tabEls.length) % tabEls.length;
          } else if (e.key === "Home") {
            nextIdx = 0;
          } else if (e.key === "End") {
            nextIdx = tabEls.length - 1;
          }
          if (nextIdx >= 0) {
            e.preventDefault();
            var nextTab = tabEls[nextIdx];
            var nextId = tabs[nextIdx].id;
            activateTab(nextTab, nextId);
          }
        }
      }, t.label);
      tabBar.appendChild(tab);

      var panel = h("div", {
        className: "ag-tab-panel" + (idx === 0 ? " active" : ""),
        "data-tab": t.id,
        role: "tabpanel",
        id: panelId,
        "aria-labelledby": tabId,
      });
      switch (t.id) {
        case "scorecard": self.renderScorecard(panel); break;
        case "regulatory": self.renderRegulatory(panel); break;
        case "zones": self.renderZones(panel); break;
        case "gaps": self.renderGaps(panel); break;
        case "responses": self.renderResponseReview(panel); break;
        case "roadmap": self.renderRoadmap(panel); break;
      }
      panels.appendChild(panel);
    });

    wrap.appendChild(tabBar);
    wrap.appendChild(panels);

    // Collaboration callout
    var collabCard = h("div", { className: "ag-collab-callout" });
    collabCard.appendChild(h("strong", null, "Delegate Sections to Team Members"));
    collabCard.appendChild(h("p", { style: "margin:0.3rem 0" },
      "Export role-specific sections as JSON for admins to complete independently. " +
      "Import completed sections back with conflict detection."));
    collabCard.appendChild(h("button", {
      className: "ag-btn ag-btn-sm ag-btn-secondary",
      onClick: function () { self.goToStep("phase2"); }
    }, "Go to Phase 2 (Section Export)"));
    wrap.appendChild(collabCard);

    // Re-render charts on dark mode toggle
    var observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (m) {
        if (m.attributeName === "data-md-color-scheme") {
          self.charts.forEach(function (c) { try { c.destroy(); } catch (e) { /* */ } });
          self.charts = [];
          // Re-render charts by finding canvases and recreating
          var radarCanvas = panels.querySelector('[data-tab="scorecard"] canvas');
          var zoneCanvas = panels.querySelector('[data-tab="zones"] canvas');
          if (radarCanvas) self.renderRadarChart(radarCanvas);
          if (zoneCanvas) self.renderZoneChart(zoneCanvas);
        }
      });
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-md-color-scheme"] });
    this._observers.push(observer);

    // Navigation
    var btns = h("div", { className: "ag-btn-group" });
    btns.appendChild(h("button", {
      className: "ag-btn ag-btn-secondary",
      onClick: function () { self.goToStep("phase1"); }
    }, "Back to Assessment"));
    btns.appendChild(h("button", {
      className: "ag-btn ag-btn-primary",
      onClick: function () {
        self.markStep("results");
        self.saveToStorage();
        self.goToStep("export");
      }
    }, "Export Results"));
    wrap.appendChild(btns);

    parent.appendChild(wrap);
  };

  /* ---- Scorecard tab ---- */
  AssessmentApp.prototype.renderScorecard = function (panel) {
    var overall = this.getOverallScore();
    var grid = h("div", { className: "ag-dashboard ag-dashboard-3col" });

    // Overall score
    var scoreCard = h("div", { className: "ag-card", style: "text-align:center" });
    scoreCard.appendChild(h("div", {
      className: "ag-score-big " + ragClass(overall || 0)
    }, (overall !== null ? overall + "%" : "—")));
    scoreCard.appendChild(h("div", { className: "ag-score-label" }, "Overall Score"));
    grid.appendChild(scoreCard);

    // Answered count
    var answered = Object.keys(this.state.responses).length;
    var total = this.data.controls.length;
    var countCard = h("div", { className: "ag-card", style: "text-align:center" });
    countCard.appendChild(h("div", { className: "ag-score-big", style: "color:var(--md-primary-fg-color)" },
      answered + "/" + total));
    countCard.appendChild(h("div", { className: "ag-score-label" }, "Controls Assessed"));
    grid.appendChild(countCard);

    // Gaps
    var gapCount = this.getGapControls().length;
    var gapCard = h("div", { className: "ag-card", style: "text-align:center" });
    gapCard.appendChild(h("div", {
      className: "ag-score-big " + (gapCount > 10 ? "red" : gapCount > 5 ? "amber" : "green")
    }, String(gapCount)));
    gapCard.appendChild(h("div", { className: "ag-score-label" }, "Gaps Identified"));
    grid.appendChild(gapCard);

    panel.appendChild(grid);

    // Pillar bars
    var self = this;
    var barSection = h("div", { className: "ag-card", style: "margin-top:1rem" });
    barSection.appendChild(h("div", { className: "ag-card-title" }, "Score by Pillar"));
    [1, 2, 3, 4].forEach(function (p) {
      var score = self.getPillarScore(p);
      var pct = score !== null ? score : 0;
      barSection.appendChild(self.renderRagBar(
        "Pillar " + p + " — " + self.data.pillars[String(p)].name, pct
      ));
    });
    panel.appendChild(barSection);

    // Radar chart
    var chartCard = h("div", { className: "ag-card", style: "margin-top:1rem" });
    chartCard.appendChild(h("div", { className: "ag-card-title" }, "Pillar Radar"));
    var chartWrap = h("div", { className: "ag-chart-container" });
    var canvas = h("canvas");
    chartWrap.appendChild(canvas);
    chartCard.appendChild(chartWrap);
    panel.appendChild(chartCard);

    // Render chart after DOM append
    var self2 = this;
    setTimeout(function () { self2.renderRadarChart(canvas); }, 50);
  };

  AssessmentApp.prototype.renderRagBar = function (label, pct) {
    var bar = h("div", { className: "ag-rag-bar" });
    bar.appendChild(h("span", { className: "ag-rag-label" }, label));
    var track = h("div", { className: "ag-rag-track" });
    track.appendChild(h("div", {
      className: "ag-rag-fill " + ragClass(pct),
      style: "width:" + clamp(pct, 0, 100) + "%"
    }));
    bar.appendChild(track);
    bar.appendChild(h("span", { className: "ag-rag-value" },
      (pct !== null ? pct + "%" : "—")));
    return bar;
  };

  AssessmentApp.prototype.renderRadarChart = function (canvas) {
    if (typeof Chart === "undefined") return;
    var self = this;
    var labels = [1, 2, 3, 4].map(function (p) {
      return "P" + p + " " + self.data.pillars[String(p)].name;
    });
    var scores = [1, 2, 3, 4].map(function (p) {
      return self.getPillarScore(p) || 0;
    });

    var isDark = document.documentElement.getAttribute("data-md-color-scheme") === "slate";
    var gridColor = isDark ? "rgba(255,255,255,0.15)" : "rgba(0,0,0,0.1)";
    var textColor = isDark ? "#ccc" : "#666";

    var chart = new Chart(canvas, {
      type: "radar",
      data: {
        labels: labels,
        datasets: [{
          label: "Score %",
          data: scores,
          backgroundColor: "rgba(63, 81, 181, 0.2)",
          borderColor: "rgba(63, 81, 181, 0.8)",
          borderWidth: 2,
          pointBackgroundColor: "rgba(63, 81, 181, 1)",
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { display: false } },
        scales: {
          r: {
            beginAtZero: true,
            max: 100,
            ticks: { stepSize: 20, color: textColor, backdropColor: "transparent" },
            grid: { color: gridColor },
            pointLabels: { color: textColor, font: { size: 11 } },
            angleLines: { color: gridColor },
          },
        },
      },
    });
    this.charts.push(chart);
  };

  /* ---- Regulatory tab ---- */
  var REGULATION_NOTES = {
    "FINRA AI Supervision and Governance":
      "Note: FINRA Regulatory Notice 25-07 addresses workplace modernization. " +
      "Its AI governance scope is limited to recordkeeping for AI-generated communications.",
  };

  AssessmentApp.prototype.renderRegulatory = function (panel) {
    var self = this;
    var card = h("div", { className: "ag-card" });
    card.appendChild(h("div", { className: "ag-card-title" }, "Compliance Score by Regulation"));
    card.appendChild(h("p", { className: "ag-card-subtitle" },
      "Scores based on controls mapped to each regulation."
    ));

    // Show regulations relevant to selected institution type first
    var activeRegs = this.state.scoping.regulations || [];
    var allRegs = Object.keys(this.data.regulatoryMappings);

    // Sort: active regs first (exact match), then alphabetical
    var sorted = allRegs.sort(function (a, b) {
      var aActive = activeRegs.indexOf(a) >= 0;
      var bActive = activeRegs.indexOf(b) >= 0;
      if (aActive && !bActive) return -1;
      if (!aActive && bActive) return 1;
      return a.localeCompare(b);
    });

    sorted.forEach(function (regKey) {
      var score = self.getRegulationScore(regKey);
      if (score === null) score = 0;
      var mapping = self.data.regulatoryMappings[regKey];
      card.appendChild(self.renderRagBar(
        regKey + " (" + mapping.controls.length + " controls)", score
      ));
      // Show contextual note if applicable
      if (REGULATION_NOTES[regKey]) {
        card.appendChild(h("div", {
          style: "font-size:0.75rem;color:var(--md-default-fg-color--light);margin:-0.3rem 0 0.5rem 130px;font-style:italic"
        }, REGULATION_NOTES[regKey]));
      }
    });

    panel.appendChild(card);
  };

  /* ---- Zones tab ---- */
  AssessmentApp.prototype.renderZones = function (panel) {
    var self = this;
    var card = h("div", { className: "ag-card" });
    card.appendChild(h("div", { className: "ag-card-title" }, "Score by Governance Zone"));

    var zoneNames = { 1: "Zone 1 — Personal Productivity", 2: "Zone 2 — Team Collaboration", 3: "Zone 3 — Enterprise Managed" };
    [1, 2, 3].forEach(function (z) {
      var score = self.getZoneScore(z);
      card.appendChild(self.renderRagBar(zoneNames[z], score !== null ? score : 0));
    });
    panel.appendChild(card);

    // Zone chart
    var chartCard = h("div", { className: "ag-card", style: "margin-top:1rem" });
    chartCard.appendChild(h("div", { className: "ag-card-title" }, "Zone Comparison"));
    var canvas = h("canvas", { style: "max-height:300px" });
    chartCard.appendChild(canvas);
    panel.appendChild(chartCard);

    var self2 = this;
    setTimeout(function () { self2.renderZoneChart(canvas); }, 50);
  };

  AssessmentApp.prototype.renderZoneChart = function (canvas) {
    if (typeof Chart === "undefined") return;
    var self = this;
    var isDark = document.documentElement.getAttribute("data-md-color-scheme") === "slate";
    var textColor = isDark ? "#ccc" : "#666";

    var chart = new Chart(canvas, {
      type: "bar",
      data: {
        labels: ["Zone 1\nPersonal", "Zone 2\nTeam", "Zone 3\nEnterprise"],
        datasets: [{
          label: "Score %",
          data: [1, 2, 3].map(function (z) { return self.getZoneScore(z) || 0; }),
          backgroundColor: [1, 2, 3].map(function (z) {
            var s = self.getZoneScore(z) || 0;
            return s >= 80 ? "rgba(46,125,50,0.7)" : s >= 50 ? "rgba(230,81,0,0.7)" : "rgba(198,40,40,0.7)";
          }),
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, max: 100, ticks: { color: textColor }, grid: { color: isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.06)" } },
          x: { ticks: { color: textColor }, grid: { display: false } },
        },
      },
    });
    this.charts.push(chart);
  };

  /* ---- Gaps tab ---- */
  AssessmentApp.prototype.renderGaps = function (panel) {
    var self = this;
    var gaps = this.getGapControls();

    var card = h("div", { className: "ag-card" });
    card.appendChild(h("div", { className: "ag-card-title" }, "Gap Analysis (" + gaps.length + " controls)"));
    card.appendChild(h("p", { className: "ag-card-subtitle" },
      "Controls sorted by risk priority (regulatory weight, zone exposure, and adoption phase)."
    ));

    if (gaps.length === 0) {
      card.appendChild(h("p", null, "No gaps detected."));
    } else {
      var wrap = h("div", { className: "ag-table-wrap" });
      var table = h("table", { className: "ag-table" });
      var thead = h("thead");
      var hrow = h("tr");
      ["Control", "Title", "Status", "Score", "Risk", "Regulations", "Playbooks"].forEach(function (col) {
        hrow.appendChild(h("th", null, col));
      });
      thead.appendChild(hrow);
      table.appendChild(thead);

      var tbody = h("tbody");
      var basePath = getBasePath();
      gaps.forEach(function (ctrl) {
        var score = self.getControlScore(ctrl.id);
        var resp = self.state.responses[ctrl.id] || {};
        var row = h("tr");
        row.appendChild(h("td", null, h("strong", null, ctrl.id)));
        row.appendChild(h("td", null, ctrl.title));
        row.appendChild(h("td", null, resp.answer || "—"));
        row.appendChild(h("td", null, score !== null ? Math.round(score * 100) + "%" : "—"));
        row.appendChild(h("td", null, self.getRiskPriority(ctrl).toFixed(1)));
        row.appendChild(h("td", null, ctrl.regulations.slice(0, 3).join(", ")));

        var links = h("td");
        var linkWrap = h("span", { className: "ag-roadmap-links" });
        linkWrap.appendChild(h("a", { href: basePath + ctrl.playbooks.portalWalkthrough }, "Portal"));
        linkWrap.appendChild(h("a", { href: basePath + ctrl.playbooks.powershellSetup }, "PS"));
        links.appendChild(linkWrap);
        row.appendChild(links);
        tbody.appendChild(row);
      });
      table.appendChild(tbody);
      wrap.appendChild(table);
      card.appendChild(wrap);
    }

    panel.appendChild(card);
  };

  /* ---- Response review tab ---- */
  AssessmentApp.prototype.renderResponseReview = function (panel) {
    var self = this;
    var card = h("div", { className: "ag-card" });
    card.appendChild(h("div", { className: "ag-card-title" }, "All Responses (" + this.data.controls.length + " controls)"));
    card.appendChild(h("p", { className: "ag-card-subtitle" },
      "Review every response. Click Edit to navigate back and change an answer."));

    var wrap = h("div", { className: "ag-table-wrap" });
    var table = h("table", { className: "ag-table" });
    var thead = h("thead");
    var hrow = h("tr");
    ["Control", "Title", "Response", "Score", "Notes", ""].forEach(function (col) {
      hrow.appendChild(h("th", null, col));
    });
    thead.appendChild(hrow);
    table.appendChild(thead);

    var tbody = h("tbody");
    this.data.controls.forEach(function (ctrl) {
      var resp = self.state.responses[ctrl.id] || {};
      var score = self.getControlScore(ctrl.id);
      var row = h("tr");
      row.appendChild(h("td", null, h("strong", null, ctrl.id)));
      row.appendChild(h("td", null, ctrl.title));
      row.appendChild(h("td", null, resp.answer || "\u2014"));
      row.appendChild(h("td", null, score !== null ? Math.round(score * 100) + "%" : "\u2014"));
      var notesTd = h("td", null);
      if (resp.notes) {
        notesTd.appendChild(h("span", { style: "font-size:0.78rem" },
          resp.notes.length > 60 ? resp.notes.substring(0, 60) + "\u2026" : resp.notes));
      }
      row.appendChild(notesTd);
      var editTd = h("td");
      editTd.appendChild(h("button", {
        className: "ag-edit-link",
        "aria-label": "Edit response for " + ctrl.id,
        onClick: function () {
          self.goToStep("phase1");
          // Scroll to and highlight the control card after render
          setTimeout(function () {
            var target = self.el.querySelector(".ag-control-id");
            var cards = self.el.querySelectorAll(".ag-control-card");
            for (var i = 0; i < cards.length; i++) {
              var idEl = cards[i].querySelector(".ag-control-id");
              if (idEl && idEl.textContent === ctrl.id) {
                cards[i].scrollIntoView({ behavior: "smooth", block: "center" });
                cards[i].classList.add("ag-highlight");
                // Expand parent pillar group if collapsed
                var pillarControls = cards[i].closest(".ag-pillar-controls");
                if (pillarControls && pillarControls.classList.contains("collapsed")) {
                  pillarControls.classList.remove("collapsed");
                  var pillarHeader = pillarControls.previousElementSibling;
                  if (pillarHeader) {
                    pillarHeader.classList.remove("collapsed");
                    pillarHeader.setAttribute("aria-expanded", "true");
                  }
                }
                setTimeout(function () { cards[i].classList.remove("ag-highlight"); }, 2000);
                break;
              }
            }
          }, 100);
        }
      }, "Edit"));
      row.appendChild(editTd);
      tbody.appendChild(row);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
    card.appendChild(wrap);
    panel.appendChild(card);
  };

  /* ---- Roadmap tab ---- */
  AssessmentApp.prototype.renderRoadmap = function (panel) {
    var self = this;
    var gaps = this.getGapControls();

    var card = h("div");
    card.appendChild(h("div", { className: "ag-card-title", style: "font-size:1.1rem;margin-bottom:0.5rem" },
      "Remediation Roadmap"));
    card.appendChild(h("p", { className: "ag-card-subtitle" },
      "Gaps grouped by responsible role, sequenced by adoption phase, sorted by risk priority."
    ));

    if (gaps.length === 0) {
      card.appendChild(h("div", { className: "ag-card" },
        h("p", null, "No gaps to remediate.")));
      panel.appendChild(card);
      return;
    }

    // Build role → phase → controls structure
    var rolePhaseMap = {};
    var basePath = getBasePath();

    gaps.forEach(function (ctrl) {
      var roles = ctrl.assignedRoles.length > 0 ? ctrl.assignedRoles : ["AI Governance Lead"];
      var phase = ctrl.adoptionPhase ? ctrl.adoptionPhase.phase : 2;

      roles.forEach(function (role) {
        if (!rolePhaseMap[role]) rolePhaseMap[role] = {};
        if (!rolePhaseMap[role][phase]) rolePhaseMap[role][phase] = [];
        rolePhaseMap[role][phase].push(ctrl);
      });
    });

    // Render by phase, then by role within each phase
    var phases = [0, 1, 2];
    phases.forEach(function (phaseNum) {
      var phaseData = self.data.adoptionPhases[String(phaseNum)];
      var hasGaps = false;
      Object.keys(rolePhaseMap).forEach(function (role) {
        if (rolePhaseMap[role][phaseNum] && rolePhaseMap[role][phaseNum].length > 0) hasGaps = true;
      });
      if (!hasGaps) return;

      var phaseSection = h("div", { className: "ag-roadmap-phase" });
      phaseSection.appendChild(h("div", { className: "ag-roadmap-phase-header" },
        "Phase " + phaseNum + ": " + (phaseData ? phaseData.name : "Other") +
        (phaseData ? " (" + phaseData.duration + ")" : "")));

      Object.keys(rolePhaseMap).sort().forEach(function (role) {
        var controls = rolePhaseMap[role][phaseNum];
        if (!controls || controls.length === 0) return;

        // Sort by risk priority within role
        controls.sort(function (a, b) {
          return self.getRiskPriority(b) - self.getRiskPriority(a);
        });

        var roleGroup = h("div", { className: "ag-roadmap-role-group" });
        roleGroup.appendChild(h("div", { className: "ag-roadmap-role-header" },
          role + " (" + controls.length + " item" + (controls.length > 1 ? "s" : "") + ")"));

        controls.forEach(function (ctrl) {
          var item = h("div", { className: "ag-roadmap-item" });

          var info = h("div", { style: "flex:1" });
          var titleLine = h("div");
          titleLine.appendChild(h("strong", null, ctrl.id + " "));
          titleLine.appendChild(document.createTextNode(ctrl.title));

          // Solution badge
          if (ctrl.solutions.length > 0) {
            titleLine.appendChild(document.createTextNode(" "));
            titleLine.appendChild(h("span", { className: "ag-badge ag-badge-solution" },
              "Automation: " + ctrl.solutions[0]));
          }
          info.appendChild(titleLine);

          // Links
          var links = h("div", { className: "ag-roadmap-links", style: "margin-top:0.2rem" });
          links.appendChild(h("a", { href: basePath + ctrl.playbooks.portalWalkthrough }, "Portal Walkthrough"));
          links.appendChild(h("a", { href: basePath + ctrl.playbooks.powershellSetup }, "PowerShell Setup"));
          links.appendChild(h("a", { href: basePath + ctrl.playbooks.verificationTesting }, "Verification"));
          links.appendChild(h("a", { href: basePath + ctrl.playbooks.troubleshooting }, "Troubleshooting"));
          info.appendChild(links);
          item.appendChild(info);

          roleGroup.appendChild(item);
        });

        phaseSection.appendChild(roleGroup);
      });

      card.appendChild(phaseSection);
    });

    // Effort estimates
    var effortCard = h("div", { className: "ag-card", style: "margin-top:1rem" });
    effortCard.appendChild(h("div", { className: "ag-card-title" }, "Estimated Effort by Phase"));
    var effortWrap = h("div", { className: "ag-table-wrap" });
    var effortTable = h("table", { className: "ag-table" });
    var eHead = h("tr");
    ["Phase", "Power Platform Admin", "Compliance", "Security", "AI Governance Lead"].forEach(function (col) {
      eHead.appendChild(h("th", null, col));
    });
    effortTable.appendChild(eHead);
    [0, 1, 2].forEach(function (p) {
      var est = self.data.effortEstimates[String(p)];
      if (!est) return;
      var row = h("tr");
      row.appendChild(h("td", null, h("strong", null, "Phase " + p)));
      row.appendChild(h("td", null, est["Power Platform Admin"] + " hrs"));
      row.appendChild(h("td", null, est["Compliance"] + " hrs"));
      row.appendChild(h("td", null, est["Security"] + " hrs"));
      row.appendChild(h("td", null, est["AI Governance Lead"] + " hrs"));
      effortTable.appendChild(row);
    });
    effortWrap.appendChild(effortTable);
    effortCard.appendChild(effortWrap);
    card.appendChild(effortCard);

    panel.appendChild(card);
  };

  /* ================================================================
     STEP 6: EXPORT
     ================================================================ */
  AssessmentApp.prototype.renderExport = function (parent) {
    var self = this;
    var wrap = h("div");
    wrap.appendChild(h("h2", { style: "font-size:1.3rem;margin-bottom:0.3rem" }, "Export Results"));
    wrap.appendChild(h("p", { className: "ag-card-subtitle" },
      "Download your assessment results in various formats."
    ));

    var grid = h("div", { className: "ag-export-grid" });

    // JSON export
    grid.appendChild(this.exportCard("JSON", "Full Assessment",
      "Complete state file for re-import and trend comparison",
      function () { self.exportJSON(); }));

    // Excel export
    grid.appendChild(this.exportCard("XLSX", "Excel Workbook",
      "Multi-sheet workbook with scorecard, gaps, and roadmap",
      function () { self.exportExcel(); }));

    // CSV export
    grid.appendChild(this.exportCard("CSV", "Gap List",
      "Lightweight gap list for spreadsheet import",
      function () { self.exportCSV(); }));

    // PDF (print)
    grid.appendChild(this.exportCard("PDF", "Print to PDF",
      "Open print dialog for browser print-to-PDF",
      function () {
        self.goToStep("results");
        setTimeout(function () { window.print(); }, 300);
      }));

    // E7 — Next Session Agenda (Markdown) export
    // TODO(E7-pdf): PDF export deferred — see follow-up issue
    grid.appendChild(this.exportCard("MD",
      t("export_agenda_button", "Next Session Agenda"),
      "Top-10 gap controls with remediation playbook for the next working session",
      function () { self.exportAgenda(); }));

    wrap.appendChild(grid);

    // Trend comparison
    wrap.appendChild(h("h3", { style: "font-size:1rem;margin-top:2rem" }, "Trend Comparison"));
    wrap.appendChild(h("p", { className: "ag-card-subtitle" },
      "Upload a previous assessment JSON to compare scores side-by-side."
    ));
    var compareBtn = h("button", {
      className: "ag-btn ag-btn-secondary",
      onClick: function () { self.triggerTrendCompare(); }
    }, "Upload Previous Assessment");
    wrap.appendChild(compareBtn);

    var compareResult = h("div", { id: "ag-trend-result" });
    wrap.appendChild(compareResult);

    // Navigation
    var btns = h("div", { className: "ag-btn-group" });
    btns.appendChild(h("button", {
      className: "ag-btn ag-btn-secondary",
      onClick: function () { self.goToStep("results"); }
    }, "Back to Results"));
    wrap.appendChild(btns);

    parent.appendChild(wrap);
  };

  AssessmentApp.prototype.exportCard = function (icon, title, desc, onClick) {
    var card = h("button", {
      className: "ag-export-card",
      type: "button",
      "aria-label": "Export as " + title,
      onClick: onClick,
    });
    card.appendChild(h("div", { className: "ag-export-icon" }, icon));
    card.appendChild(h("div", { className: "ag-export-label" }, title));
    card.appendChild(h("div", { className: "ag-export-desc" }, desc));
    return card;
  };

  /* ---- JSON export ----
   * v1.4.1: output is wrapped in a versioned envelope so downstream tools
   * (e.g. FSI-Assessment-Agent) can detect framework version, validate schema,
   * and consume pre-computed scores without re-implementing the algorithm.
   *
   * Envelope contract (additive — all original keys remain at top level for
   * backwards-compatible importers):
   *   _metadata          { exportSchemaVersion, schemaType:"full", frameworkVersion,
   *                        manifestSchemaVersion, exportedAt, exportedBy }
   *   _computedScores    { overall, perPillar:{1..4}, perControl:{id:0..1|null} }
   *   assessmentStatus   "draft" | "in-progress" | "final"  (snapshot at export)
   *   ...this.state      (responses, scoping, drilldown, overrides, completedSteps, etc.)
   *
   * NOTE: _metadata, _computedScores, and assessmentStatus are snapshot-only.
   * importAssessment() reads named state keys directly and ignores these fields,
   * which forces a recompute on import (the source-of-truth contract).
   */
  AssessmentApp.prototype.exportJSON = function () {
    var envelope = {
      _metadata: this.buildExportMetadata("full"),
      _computedScores: this.computeExportScores(),
      assessmentStatus: this.deriveAssessmentStatus()
    };
    // Copy state keys onto envelope (preserves importer compatibility).
    for (var k in this.state) {
      if (Object.prototype.hasOwnProperty.call(this.state, k)) {
        envelope[k] = this.state[k];
      }
    }
    var blob = new Blob([JSON.stringify(envelope, null, 2)], { type: "application/json" });
    var name = _truncateFilename((this.state.assessmentName || "assessment").replace(/[^a-zA-Z0-9-_]/g, "-"));
    downloadBlob(blob, name + ".json");
  };

  /* ---- CSV export ---- */
  AssessmentApp.prototype.exportCSV = function () {
    var self = this;
    var csvField = function (val) {
      val = sanitizeCell(String(val));
      // Escape newlines and quotes for CSV
      if (/[",\n\r]/.test(val)) {
        return '"' + val.replace(/"/g, '""').replace(/[\r\n]+/g, " ") + '"';
      }
      return val;
    };
    var rows = [["Control ID", "Title", "Pillar", "Status", "Score", "Risk Priority", "Regulations", "Notes"]];
    this.getGapControls().forEach(function (ctrl) {
      var resp = self.state.responses[ctrl.id] || {};
      var score = self.getControlScore(ctrl.id);
      rows.push([
        csvField(ctrl.id),
        csvField(ctrl.title),
        csvField(ctrl.pillarName),
        csvField(resp.answer || ""),
        csvField(score !== null ? Math.round(score * 100) + "%" : ""),
        csvField(self.getRiskPriority(ctrl).toFixed(1)),
        csvField(ctrl.regulations.join(", ")),
        csvField(resp.notes || ""),
      ]);
    });
    // CRLF line endings + UTF-8 BOM are required for Excel-on-Windows correctness:
    //   - CRLF: some regional Excel locales (Japanese, Korean, several European
    //     Windows configurations) collapse LF-only CSV into a single cell.
    //   - BOM: BOM-less CSV is opened in the system locale (typically Windows-1252),
    //     mojibaking accented org names ("Société Générale" → "SociÃ©tÃ© GÃ©nÃ©rale").
    //   - Trailing CRLF: RFC 4180-compliant; harmless for Excel + SheetJS readers.
    var csv = rows.map(function (r) { return r.join(","); }).join("\r\n") + "\r\n";
    var blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" });
    var name = _truncateFilename((this.state.assessmentName || "assessment").replace(/[^a-zA-Z0-9-_]/g, "-"));
    downloadBlob(blob, name + "-gaps.csv");
  };

  /* ---- Excel export ---- */
  AssessmentApp.prototype.exportExcel = function () {
    var self = this;

    // Lazy-load SheetJS
    var base = "";
    var scripts = document.querySelectorAll('script[src*="assessment-loader"]');
    if (scripts.length) {
      var src = scripts[scripts.length - 1].src;
      base = src.substring(0, src.lastIndexOf("/") + 1);
    }

    var doExport = function () {
      if (typeof XLSX === "undefined") {
        alert("SheetJS library not available. Please try the CSV export instead.");
        return;
      }
      var wb = XLSX.utils.book_new();

      // Sheet 1: Summary
      var summaryData = [
        ["FSI Agent Governance — Readiness Assessment Report"],
        [],
        ["Assessment Name", sanitizeCell(self.state.assessmentName || "")],
        ["Organization", sanitizeCell(self.state.scoping.organizationName || "")],
        ["Assessor", sanitizeCell(self.state.scoping.assessorName || "")],
        ["Institution Type", sanitizeCell(self.state.scoping.institutionType || "")],
        ["Date", fmtDate(self.state.updatedAt)],
        [],
        ["Overall Score", pctCell((self.getOverallScore() || 0) / 100)],
        ["Controls Assessed", Object.keys(self.state.responses).length + " / " + self.data.totalControls],
        ["Gaps Identified", self.getGapControls().length],
        [],
        ["Pillar", "Score"],
      ];
      [1, 2, 3, 4].forEach(function (p) {
        summaryData.push([
          "Pillar " + p + " — " + self.data.pillars[String(p)].name,
          pctCell((self.getPillarScore(p) || 0) / 100),
        ]);
      });
      var ws1 = XLSX.utils.aoa_to_sheet(summaryData);
      XLSX.utils.book_append_sheet(wb, ws1, "Summary");

      // Sheet 2: All Controls
      var ctrlData = [["Control ID", "Title", "Pillar", "Status", "Score", "Notes", "Phase", "Priority"]];
      self.data.controls.forEach(function (ctrl) {
        var resp = self.state.responses[ctrl.id] || {};
        var score = self.getControlScore(ctrl.id);
        ctrlData.push([
          ctrl.id, ctrl.title, ctrl.pillarName,
          resp.answer || "Not assessed",
          score !== null ? pctCell(score) : "N/A",
          sanitizeCell(resp.notes || ""),
          ctrl.adoptionPhase ? "Phase " + ctrl.adoptionPhase.phase : "",
          ctrl.adoptionPhase ? ctrl.adoptionPhase.priority : "",
        ]);
      });
      var ws2 = XLSX.utils.aoa_to_sheet(ctrlData);
      XLSX.utils.book_append_sheet(wb, ws2, "Control Details");

      // Sheet 3: Gap Analysis
      var gapData = [["Control ID", "Title", "Pillar", "Status", "Score", "Risk Priority", "Regulations", "Solutions", "Notes"]];
      self.getGapControls().forEach(function (ctrl) {
        var resp = self.state.responses[ctrl.id] || {};
        var score = self.getControlScore(ctrl.id);
        gapData.push([
          ctrl.id, ctrl.title, ctrl.pillarName,
          resp.answer || "",
          score !== null ? pctCell(score) : "",
          self.getRiskPriority(ctrl).toFixed(1),
          ctrl.regulations.join(", "),
          ctrl.solutions.join(", "),
          sanitizeCell(resp.notes || ""),
        ]);
      });
      var ws3 = XLSX.utils.aoa_to_sheet(gapData);
      XLSX.utils.book_append_sheet(wb, ws3, "Gap Analysis");

      // Sheet 4: Regulatory Matrix
      var regData = [["Regulation", "Controls Mapped", "Score"]];
      Object.keys(self.data.regulatoryMappings).forEach(function (regKey) {
        var mapping = self.data.regulatoryMappings[regKey];
        var score = self.getRegulationScore(regKey);
        regData.push([
          regKey,
          mapping.controls.length,
          score !== null ? pctCell(score / 100) : "N/A",
        ]);
      });
      var ws4 = XLSX.utils.aoa_to_sheet(regData);
      XLSX.utils.book_append_sheet(wb, ws4, "Regulatory Matrix");

      // Sheet 5: Remediation Plan by Role
      var remData = [["Phase", "Role", "Control ID", "Title", "Risk Priority", "Solution Available"]];
      var gaps = self.getGapControls();
      gaps.forEach(function (ctrl) {
        var roles = ctrl.assignedRoles.length > 0 ? ctrl.assignedRoles : ["AI Governance Lead"];
        var phase = ctrl.adoptionPhase ? ctrl.adoptionPhase.phase : 2;
        roles.forEach(function (role) {
          remData.push([
            "Phase " + phase, role, ctrl.id, ctrl.title,
            self.getRiskPriority(ctrl).toFixed(1),
            ctrl.solutions.length > 0 ? ctrl.solutions.join(", ") : "No",
          ]);
        });
      });
      var ws5 = XLSX.utils.aoa_to_sheet(remData);
      XLSX.utils.book_append_sheet(wb, ws5, "Remediation Plan");

      // Generate and download
      var buf = XLSX.write(wb, { bookType: "xlsx", type: "array" });
      var blob = new Blob([buf], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
      var name = _truncateFilename((self.state.assessmentName || "assessment").replace(/[^a-zA-Z0-9-_]/g, "-"));
      downloadBlob(blob, name + ".xlsx");
    };

    if (typeof XLSX !== "undefined") {
      doExport();
    } else {
      // Check if script is already loading
      var xlsxSrc = base + "lib/xlsx.full.min.js";
      var existing = document.querySelector('script[src="' + xlsxSrc + '"]');
      if (existing) {
        existing.addEventListener("load", doExport);
        return;
      }
      // Lazy load SheetJS with SRI
      var s = document.createElement("script");
      s.src = xlsxSrc;
      s.integrity = "sha256-yVBhl8r4CaB1tt7h2g02+xnacVj/6KiOewyWxdhiPJk=";
      s.crossOrigin = "anonymous";
      s.onload = doExport;
      s.onerror = function () { alert("Failed to load SheetJS library. Please try the CSV export."); };
      document.head.appendChild(s);
    }
  };

  /* ---- Trend comparison ---- */
  AssessmentApp.prototype.triggerTrendCompare = function () {
    var self = this;
    var input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = function () {
      var file = input.files[0];
      if (!file) return;
      var reader = new FileReader();
      reader.onload = function () {
        try {
          var prev = JSON.parse(reader.result);
          self.showTrendComparison(prev);
        } catch (e) {
          alert("Invalid JSON file: " + e.message);
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  AssessmentApp.prototype.showTrendComparison = function (prevState) {
    var container = document.getElementById("ag-trend-result");
    if (!container) return;
    container.innerHTML = "";

    // Validate uploaded file is a valid assessment
    if (!this.validateState(prevState)) {
      container.appendChild(h("div", { className: "ag-disclaimer" },
        "The uploaded file does not appear to be a valid assessment export."));
      return;
    }

    var self = this;
    var card = h("div", { className: "ag-card" });
    card.appendChild(h("div", { className: "ag-card-title" }, "Trend Comparison"));
    card.appendChild(h("p", { className: "ag-card-subtitle" },
      "Current vs. " + fmtDate(prevState.updatedAt)));

    var wrap = h("div", { className: "ag-table-wrap" });
    var table = h("table", { className: "ag-table" });
    var head = h("tr");
    ["Metric", "Previous", "Current", "Change"].forEach(function (col) {
      head.appendChild(h("th", null, col));
    });
    table.appendChild(head);

    // Calculate previous scores
    var prevScores = {};
    this.data.controls.forEach(function (ctrl) {
      var resp = prevState.responses && prevState.responses[ctrl.id];
      if (!resp || !resp.answer || resp.answer === "na") return;
      var score = resp.answer === "yes" ? 1.0 : resp.answer === "no" ? 0.0 : 0.5;
      prevScores[ctrl.id] = score;
    });

    var prevTotal = 0, prevCount = 0;
    Object.keys(prevScores).forEach(function (k) { prevTotal += prevScores[k]; prevCount++; });
    var prevOverall = prevCount > 0 ? Math.round((prevTotal / prevCount) * 100) : 0;
    var currOverall = self.getOverallScore() || 0;

    var addRow = function (label, prev, curr) {
      var row = h("tr");
      row.appendChild(h("td", null, label));
      row.appendChild(h("td", null, prev + "%"));
      row.appendChild(h("td", null, curr + "%"));
      var delta = curr - prev;
      var deltaStr = (delta >= 0 ? "+" : "") + delta + "%";
      row.appendChild(h("td", { style: "color:" + (delta > 0 ? "var(--ag-green)" : delta < 0 ? "var(--ag-red)" : "inherit") }, deltaStr));
      return row;
    };

    table.appendChild(addRow("Overall", prevOverall, currOverall));
    wrap.appendChild(table);
    card.appendChild(wrap);
    container.appendChild(card);
  };

  /* ================================================================
     E7 — NEXT SESSION AGENDA EXPORT (Markdown)
     ================================================================ */

  // Numeric weight for the manifest `priority` string. Lower = higher priority.
  var AGENDA_PRIORITY_WEIGHT = { critical: 0, high: 1, medium: 2, low: 3 };
  function _agendaPriorityWeight(p) {
    if (typeof p !== "string") return 5;
    var w = AGENDA_PRIORITY_WEIGHT[p.toLowerCase()];
    return (w === undefined) ? 4 : w;
  }

  function _agendaControlIdSortKey(id) {
    var parts = String(id || "").split(".");
    return [parseInt(parts[0], 10) || 0, parseInt(parts[1], 10) || 0];
  }

  function _cmpAgendaControlId(a, b) {
    var ka = _agendaControlIdSortKey(a.id);
    var kb = _agendaControlIdSortKey(b.id);
    if (ka[0] !== kb[0]) return ka[0] - kb[0];
    return ka[1] - kb[1];
  }

  /**
   * Top-N gap controls for the agenda, per E7 spec:
   *   1. Controls answered "no" first (sort by priority asc, then control ID).
   *   2. If fewer than `limit` "no" controls, fill with "partial" controls.
   *   3. Controls answered "na" (auto or manual) are excluded.
   *   4. Unanswered controls are excluded.
   */
  AssessmentApp.prototype._topGapControls = function (limit) {
    var lim = (typeof limit === "number" && limit > 0) ? limit : 10;
    var responses = (this.state && this.state.responses) || {};
    var noBucket = [];
    var partialBucket = [];
    (this.data && this.data.controls ? this.data.controls : []).forEach(function (c) {
      var resp = responses[c.id];
      if (!resp || !resp.answer) return;
      var ans = String(resp.answer).toLowerCase();
      if (ans === "no") noBucket.push(c);
      else if (ans === "partial") partialBucket.push(c);
    });
    var sortFn = function (a, b) {
      var pa = _agendaPriorityWeight(a.priority);
      var pb = _agendaPriorityWeight(b.priority);
      if (pa !== pb) return pa - pb;
      return _cmpAgendaControlId(a, b);
    };
    noBucket.sort(sortFn);
    partialBucket.sort(sortFn);
    var out = noBucket.slice(0, lim);
    if (out.length < lim) {
      out = out.concat(partialBucket.slice(0, lim - out.length));
    }
    return out;
  };

  function _agendaMdCell(v) {
    if (v === null || v === undefined) return "";
    // spa-fix-md-escape: neutralize Markdown emphasis, links, code, headings,
    // HTML tags, and table-pipe injection so user-supplied control titles can
    // never break out of a table cell or render styled / linked content in
    // the generated agenda.
    return String(v)
      .replace(/\r?\n/g, " ")
      .replace(/\\/g, "\\\\")
      .replace(/\|/g, "\\|")
      .replace(/[*_`~#>]/g, function (ch) { return "\\" + ch; })
      .replace(/[\[\]\(\)\{\}<>!]/g, function (ch) { return "\\" + ch; })
      .trim();
  }

  function _agendaSlug(s) {
    return String(s || "").toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .substring(0, 60);
  }

  function _agendaIsoDate(d) {
    var iso = (d || new Date()).toISOString();
    return iso.substring(0, 10);
  }

  function _agendaSkipTodo(s) {
    if (typeof s !== "string") return "";
    var trimmed = s.trim();
    if (!trimmed) return "";
    if (trimmed.indexOf("TODO:") === 0) return "";
    return trimmed;
  }

  /** Build the full agenda Markdown document for the current state. */
  AssessmentApp.prototype._buildAgendaMarkdown = function () {
    var self = this;
    var state = this.state || {};
    var scoping = state.scoping || {};
    var lock = (this.solutionsLock && typeof this.solutionsLock === "object")
      ? this.solutionsLock : { schemaVersion: null, solutions: {} };
    var lockSolutions = (lock.solutions && typeof lock.solutions === "object") ? lock.solutions : {};
    var gaps = this._topGapControls(10);

    var zoneTarget = "TBD";
    if (Array.isArray(scoping.zones) && scoping.zones.length) {
      zoneTarget = "Zone " + scoping.zones.slice().sort().join(", Zone ");
    }

    var overallPct = self.getOverallScore();
    var maturity = (overallPct === null || overallPct === undefined)
      ? "n/a"
      : (Math.round((overallPct / 100) * 4 * 10) / 10).toFixed(1);

    var lines = [];

    // Section 1 — Header
    lines.push("# FSI Agent Governance Assessment \u2014 Next Session Agenda");
    lines.push("");
    // spa-fix-md-escape: customer name is user-supplied; escape Markdown
    // special chars so names containing *, _, [, `, etc. don't break rendering.
    lines.push("**Customer:** " + _agendaMdCell(scoping.organizationName || "TBD"));
    lines.push("**Generated:** " + new Date().toISOString());
    lines.push("**Zone target:** " + zoneTarget);
    lines.push("**Sector:** " + (state.selectedSector || scoping.institutionType || "Not specified"));
    lines.push("**Overall maturity:** " + maturity + " / 4");
    lines.push("");

    // Section 2 — Top-N gap controls table
    lines.push("## Top " + gaps.length + " Gap Controls");
    lines.push("");
    if (!gaps.length) {
      lines.push("_No gap controls found \u2014 all answered controls passed or were marked N/A._");
      lines.push("");
    } else {
      lines.push("| Rank | Control ID | Title | Pillar | Current answer | Priority | Responsible role(s) |");
      lines.push("|---|---|---|---|---|---|---|");
      gaps.forEach(function (c, i) {
        var resp = (state.responses && state.responses[c.id]) || {};
        var roles = (Array.isArray(c.manifestRoles) && c.manifestRoles.length)
          ? c.manifestRoles
          : (Array.isArray(c.roles) ? c.roles : []);
        lines.push("| " + (i + 1) +
          " | " + _agendaMdCell(c.id) +
          " | " + _agendaMdCell(c.title) +
          " | " + _agendaMdCell(c.pillarName || ("Pillar " + c.pillar)) +
          " | " + _agendaMdCell(resp.answer || "") +
          " | " + _agendaMdCell(c.priority || "\u2014") +
          " | " + _agendaMdCell(roles.join("; ")) +
          " |");
      });
      lines.push("");
    }

    // Section 3 — Remediation sub-blocks
    if (gaps.length) {
      lines.push("## Remediation Detail");
      lines.push("");
      gaps.forEach(function (c, i) {
        lines.push("## Gap " + (i + 1) + " \u2014 Control " + _agendaMdCell(c.id) + ": " + _agendaMdCell(c.title || ""));
        lines.push("");

        var regs = Array.isArray(c.regulations) ? c.regulations.filter(Boolean) : [];
        var regText = regs.length ? regs.join(", ") + " support" : "Regulatory mappings pending";
        var obj = _agendaSkipTodo(c.objective) || "addresses a control gap identified in this assessment";
        lines.push("**Why this matters:** " + regText + "; " + obj);
        lines.push("");

        var yesBar = _agendaSkipTodo(c.yesBar);
        if (yesBar) {
          lines.push("**What \"good\" looks like:** " + yesBar);
          lines.push("");
        }

        lines.push("**Recommended remediation:**");
        lines.push("");
        var solutionIds = Array.isArray(c.solutions) ? c.solutions : [];
        if (!solutionIds.length) {
          lines.push("- _No companion solution by design — see the control doc for native-admin coverage._");
        } else {
          solutionIds.forEach(function (sid) {
            var sol = lockSolutions[sid];
            if (sol && typeof sol === "object") {
              var nm = sol.name || sid;
              var tier = sol.tier || "\u2014";
              var ver = sol.version || "\u2014";
              var desc = sol.description || sol.summary || "";
              lines.push("- **" + nm + "** (Tier " + tier + ", v" + ver + ")" +
                (desc ? " \u2014 " + desc : ""));
              lines.push("    Link: " + SOLUTIONS_BASE_URL + sid + "/");
            } else {
              lines.push("- _" + sid + "_ (no companion solution by design)");
            }
          });
        }
        lines.push("");

        var verifyParts = [];
        if (Array.isArray(c.verifyIn)) {
          c.verifyIn.forEach(function (entry) {
            if (!entry) return;
            if (typeof entry === "string") { verifyParts.push(entry); return; }
            var label = entry.portal || entry.label || entry.name || entry.url;
            if (label) verifyParts.push(label);
          });
        }
        var verifyLine;
        if (verifyParts.length) {
          verifyLine = verifyParts.join("; ");
        } else if (c.controlDocUrl) {
          verifyLine = c.controlDocUrl;
        } else {
          verifyLine = "See control documentation";
        }
        lines.push("**Verification:** " + verifyLine);
        lines.push("");

        var rolesArr = (Array.isArray(c.manifestRoles) && c.manifestRoles.length)
          ? c.manifestRoles
          : (Array.isArray(c.roles) ? c.roles : []);
        lines.push("**Roles needed:** " + (rolesArr.length ? rolesArr.join(", ") : "\u2014"));
        lines.push("");
        lines.push("---");
        lines.push("");
      });
    }

    // Section 4 — Discussion topics
    lines.push("## Discussion Topics for the Session");
    lines.push("");
    var topics = [];
    var seen = {};
    gaps.forEach(function (c) {
      if (topics.length >= 15) return;
      var fn = c.facilitatorNotes || {};
      var fu = _agendaSkipTodo(fn.followUp);
      if (fu && !seen[fu]) {
        seen[fu] = true;
        topics.push("- (" + c.id + ") " + fu);
      }
    });
    if (!topics.length) {
      lines.push("_No facilitator follow-up prompts available for the selected gap controls._");
    } else {
      topics.slice(0, 15).forEach(function (line) { lines.push(line); });
    }
    lines.push("");

    // Section 5 — Recommended time budget
    lines.push("## Recommended Time Budget");
    lines.push("");
    var totalMin = 0;
    var anyTime = false;
    var rows = [];
    gaps.forEach(function (c) {
      var fn = c.facilitatorNotes || {};
      var m = fn.timeBudgetMinutes;
      if (typeof m === "number" && isFinite(m) && m > 0) {
        anyTime = true;
        totalMin += m;
        rows.push("| " + _agendaMdCell(c.id) + " | " + _agendaMdCell(c.title) + " | " + m + " |");
      } else {
        rows.push("| " + _agendaMdCell(c.id) + " | " + _agendaMdCell(c.title) + " | \u2014 |");
      }
    });
    if (gaps.length) {
      lines.push("| Control | Title | Minutes |");
      lines.push("|---|---|---|");
      rows.forEach(function (r) { lines.push(r); });
      if (anyTime) {
        var hours = Math.round((totalMin / 60) * 10) / 10;
        lines.push("| **Subtotal** | | **" + totalMin + " min (~" + hours.toFixed(1) + " hrs)** |");
      } else {
        lines.push("| **Subtotal** | | _no time-budget metadata available_ |");
      }
    } else {
      lines.push("_No gap controls \u2014 no time budget computed._");
    }
    lines.push("");

    // Section 6 — Footer
    lines.push("---");
    lines.push("*Generated by FSI Agent Governance Framework v1.6 assessment tool*");
    lines.push("*Compatible with FSI-AgentGov-Solutions (solutions-lock schema " +
      (lock.schemaVersion || "unknown") + ")*");
    lines.push("");

    return lines.join("\n");
  };

  /** Lightweight, non-blocking toast. Auto-dismisses after ~5s. */
  AssessmentApp.prototype._showToast = function (msg) {
    if (!msg) return;
    try {
      var existing = document.getElementById("ag-toast");
      if (existing && existing.parentNode) existing.parentNode.removeChild(existing);
      var toast = document.createElement("div");
      toast.id = "ag-toast";
      toast.className = "ag-toast";
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");
      toast.textContent = msg;
      document.body.appendChild(toast);
      void toast.offsetWidth;
      toast.classList.add("ag-toast-visible");
      setTimeout(function () {
        toast.classList.remove("ag-toast-visible");
        setTimeout(function () {
          if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 400);
      }, 5000);
    } catch (e) { /* DOM unavailable - ignore */ }
  };

  /** Public handler: build the agenda MD and trigger a download + toast. */
  AssessmentApp.prototype.exportAgenda = function () {
    var md;
    try {
      md = this._buildAgendaMarkdown();
    } catch (e) {
      alert("Failed to build agenda: " + (e && e.message ? e.message : e));
      return;
    }
    var scoping = (this.state && this.state.scoping) || {};
    var prefix = t("export_agenda_filename_prefix", "fsi-agentgov-agenda");
    var slug = _agendaSlug(scoping.organizationName) || _agendaIsoDate();
    var filename = prefix + "-" + slug + "-" + _agendaIsoDate() + ".md";
    var blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
    downloadBlob(blob, filename);
    var toastMsg = tFmt("export_agenda_toast",
      "Agenda exported. Send to {org} stakeholders before next session.",
      { org: scoping.organizationName || "your" });
    this._showToast(toastMsg);
  };

  /* ================================================================
     EXPOSE GLOBALLY
     ================================================================ */
  window.AssessmentApp = AssessmentApp;

  // Test-only conditional export. Harmless in browsers (module is undefined).
  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      AssessmentApp: AssessmentApp,
      SOLUTIONS_BASE_URL: SOLUTIONS_BASE_URL,
      STARTER_PRIORITY_IDS: STARTER_PRIORITY_IDS,
      ROLE_FILTER_OPTIONS: ROLE_FILTER_OPTIONS,
      SECTOR_OPTIONS: SECTOR_OPTIONS,
      sanitizeCell: sanitizeCell,
      _agendaMdCell: _agendaMdCell,
      validateCollectorPayload: validateCollectorPayload,
      _hasForbiddenKey: _hasForbiddenKey,
      _truncateFilename: _truncateFilename,
    };
  }
})();
