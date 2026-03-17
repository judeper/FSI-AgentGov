/**
 * FSI-AgentGov Governance Readiness Assessment Tool
 *
 * Client-side SPA that walks users through a scoped assessment of the
 * 72-control governance framework and produces scorecards, gap analysis,
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

  /** Sanitize a string for CSV/Excel to prevent formula injection. */
  function sanitizeCell(val) {
    if (typeof val !== "string") return val;
    // Prefix dangerous leading characters that trigger formula execution
    if (/^[=+\-@\t\r]/.test(val)) return "'" + val;
    return val;
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
    this.loadData().then(function () {
      self.render();
    });
  };

  AssessmentApp.prototype.destroy = function () {
    this.charts.forEach(function (c) { try { c.destroy(); } catch (e) { /* */ } });
    this.charts = [];
    this._observers.forEach(function (o) { try { o.disconnect(); } catch (e) { /* */ } });
    this._observers = [];
  };

  AssessmentApp.prototype.loadData = function () {
    var self = this;
    var base = "";
    var scripts = document.querySelectorAll('script[src*="assessment-loader"]');
    if (scripts.length) {
      var src = scripts[scripts.length - 1].src;
      base = src.substring(0, src.lastIndexOf("/") + 1);
    }
    return fetch(base + "assessment-data.json")
      .then(function (r) {
        if (!r.ok) throw new Error("Failed to load assessment data: " + r.status);
        return r.json();
      })
      .then(function (d) { self.data = d; })
      .catch(function (err) {
        console.error(err);
        self.el.innerHTML =
          '<div class="admonition failure"><p class="admonition-title">Error</p>' +
          "<p>Could not load assessment data. Run <code>python scripts/extract_assessment_data.py</code> first.</p></div>";
        throw err;
      });
  };

  /* ================================================================
     STATE MANAGEMENT
     ================================================================ */
  AssessmentApp.prototype.newState = function () {
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
      responses: {},      // controlId → { answer, notes }
      drilldown: {},      // controlId → { subQuestionId → answer }
      completedSteps: [],
    };
  };

  AssessmentApp.prototype.saveToStorage = function () {
    if (!this.state) return;
    this.state.updatedAt = new Date().toISOString();
    try {
      // Save current assessment
      localStorage.setItem(STORAGE_KEY + "-current", JSON.stringify(this.state));
      // Update saved list
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
    } catch (e) { /* localStorage quota */ }
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
      var data = JSON.parse(localStorage.getItem(STORAGE_KEY + "-current"));
      if (data && (!id || data.assessmentId === id) && this.validateState(data)) {
        this.state = data;
        return true;
      }
    } catch (e) { /* */ }
    return false;
  };

  AssessmentApp.prototype.deleteSaved = function (id) {
    var list = this.getSavedList().filter(function (s) { return s.id !== id; });
    localStorage.setItem(STORAGE_KEY + "-list", JSON.stringify(list));
    try {
      var current = JSON.parse(localStorage.getItem(STORAGE_KEY + "-current"));
      if (current && current.assessmentId === id) {
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
      };
      // Copy responses safely
      for (var k in parsed.responses) {
        if (!Object.prototype.hasOwnProperty.call(parsed.responses, k)) continue;
        clean.responses[k] = parsed.responses[k];
      }
      if (parsed.drilldown) {
        for (var d in parsed.drilldown) {
          if (!Object.prototype.hasOwnProperty.call(parsed.drilldown, d)) continue;
          clean.drilldown[d] = parsed.drilldown[d];
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
    return this.data.controls.filter(function (c) {
      var score = self.getControlScore(c.id);
      return score !== null && score < 1.0;
    }).sort(function (a, b) {
      return self.getRiskPriority(b) - self.getRiskPriority(a);
    });
  };

  /* ================================================================
     RENDERING — MAIN ROUTER
     ================================================================ */
  AssessmentApp.prototype.render = function () {
    this.destroy(); // Clean up charts
    this.el.innerHTML = "";
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

  AssessmentApp.prototype.goToStep = function (step) {
    this.step = step;
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
      "Approximately 10 controls are excluded from Zone 1 scoring, while all 72 apply to Zone 3."));

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
      "Assess your organization's readiness across the 72-control FSI Agent Governance Framework. " +
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
              self.goToStep("phase1");
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
      "All 72 controls will be included but prioritized based on your profile."
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
    var zoneLink = h("a", { href: getBasePath() + "framework/zones-and-tiers/", target: "_blank" }, "Learn about zones");
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

    // Navigation
    var btns = h("div", { className: "ag-btn-group" });
    btns.appendChild(h("button", {
      className: "ag-btn ag-btn-secondary",
      onClick: function () { self.goToStep("welcome"); }
    }, "Back"));
    btns.appendChild(h("button", {
      className: "ag-btn ag-btn-primary",
      onClick: function () {
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
      "aria-describedby": hint ? inputId + "-hint" : null,
    });
    input.addEventListener("input", function () { onChange(input.value); });
    wrap.appendChild(input);
    return wrap;
  };

  AssessmentApp.prototype.selectField = function (label, options, value, onChange) {
    var selectId = "ag-select-" + label.toLowerCase().replace(/\s+/g, "-");
    var wrap = h("div", { className: "ag-field" });
    wrap.appendChild(h("label", { className: "ag-label", htmlFor: selectId }, label));
    var sel = h("select", { className: "ag-select", id: selectId });
    options.forEach(function (o) {
      var opt = h("option", { value: o.value }, o.label);
      if (o.value === value) opt.selected = true;
      sel.appendChild(opt);
    });
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

    // Progress
    var answered = Object.keys(this.state.responses).length;
    var total = this.data.controls.length;
    var pct = Math.round((answered / total) * 100);
    var progressText = h("div", { className: "ag-progress-text" },
      answered + " of " + total + " controls answered (" + pct + "%)");
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
      className: "ag-info-btn",
      onClick: function () { self.showScoringModal(); }
    }, "\u2139 How Scoring Works"));
    wrap.appendChild(topBtns);

    // Group by pillar
    var pillars = [
      { num: 1, name: "Pillar 1 — Security" },
      { num: 2, name: "Pillar 2 — Management" },
      { num: 3, name: "Pillar 3 — Reporting" },
      { num: 4, name: "Pillar 4 — SharePoint" },
    ];

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
        controlsContainer.appendChild(self.renderControlCard(ctrl));
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
  };

  AssessmentApp.prototype.renderControlCard = function (ctrl) {
    var self = this;
    var resp = this.state.responses[ctrl.id] || {};
    var cls = "ag-control-card";
    if (resp.answer === "yes") cls += " answered";
    else if (resp.answer === "partial") cls += " partial";
    else if (resp.answer === "no") cls += " gap";

    var card = h("div", { className: cls });

    // Header
    var header = h("div", { className: "ag-control-header" });
    var left = h("div", { style: "flex:1" });
    var titleLine = h("div", { style: "display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap" });
    titleLine.appendChild(h("span", { className: "ag-control-id" }, ctrl.id));
    titleLine.appendChild(h("span", { className: "ag-control-title" }, ctrl.title));
    left.appendChild(titleLine);

    // Badges
    var badges = h("div", { className: "ag-control-badges", style: "margin-top:0.3rem" });
    if (ctrl.adoptionPhase) {
      var pCls = "ag-badge ag-badge-" + ctrl.adoptionPhase.priority.toLowerCase();
      badges.appendChild(h("span", { className: pCls }, "Phase " + ctrl.adoptionPhase.phase + " " + ctrl.adoptionPhase.priority));
    }
    if (ctrl.solutions.length > 0) {
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

    // Answer buttons
    var answerGroup = h("div", { className: "ag-answer-group", role: "group", "aria-label": "Implementation status for " + ctrl.id });
    ANSWERS.forEach(function (a) {
      var bcls = "ag-answer-btn";
      var isPressed = resp.answer === a.value;
      if (isPressed) bcls += " " + a.cls;
      var btn = h("button", {
        className: bcls,
        "aria-pressed": isPressed ? "true" : "false",
        onClick: function () {
          self.state.responses[ctrl.id] = self.state.responses[ctrl.id] || {};
          self.state.responses[ctrl.id].answer = a.value;
          self.saveToStorage();
          // Update card styling
          card.className = "ag-control-card" +
            (a.value === "yes" ? " answered" : a.value === "partial" ? " partial" : a.value === "no" ? " gap" : "");
          // Update button states
          answerGroup.querySelectorAll(".ag-answer-btn").forEach(function (b) {
            b.className = "ag-answer-btn";
            b.setAttribute("aria-pressed", "false");
          });
          btn.className = "ag-answer-btn " + a.cls;
          btn.setAttribute("aria-pressed", "true");
          // Update progress
          self.updateProgress();
        }
      }, a.label);
      answerGroup.appendChild(btn);
    });
    card.appendChild(answerGroup);

    // Notes toggle
    var notesVisible = !!resp.notes;
    var notesBtn = h("button", {
      className: "ag-notes-toggle",
      "aria-expanded": notesVisible ? "true" : "false",
      "aria-controls": "ag-notes-" + ctrl.id,
    }, resp.notes ? "Edit notes" : "Add notes");
    var notesArea = h("textarea", {
      className: "ag-textarea",
      id: "ag-notes-" + ctrl.id,
      style: "display:" + (notesVisible ? "block" : "none") + ";margin-top:0.4rem",
      placeholder: "Notes (optional)",
      value: resp.notes || "",
      "aria-label": "Notes for control " + ctrl.id,
    });
    notesArea.value = resp.notes || "";
    notesArea.addEventListener("input", function () {
      self.state.responses[ctrl.id] = self.state.responses[ctrl.id] || {};
      self.state.responses[ctrl.id].notes = notesArea.value;
      self._debouncedSave();
    });
    notesBtn.addEventListener("click", function () {
      var showing = notesArea.style.display !== "none";
      notesArea.style.display = showing ? "none" : "block";
      notesBtn.textContent = showing ? (notesArea.value ? "Edit notes" : "Add notes") : "Hide notes";
      notesBtn.setAttribute("aria-expanded", showing ? "false" : "true");
      if (!showing) notesArea.focus();
    });
    card.appendChild(notesBtn);
    card.appendChild(notesArea);

    return card;
  };

  AssessmentApp.prototype.updateProgress = function () {
    var answered = Object.keys(this.state.responses).length;
    var total = this.data.controls.length;
    var pct = Math.round((answered / total) * 100);
    var msg = answered + " of " + total + " controls answered (" + pct + "%)";
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

  /* ---- JSON export ---- */
  AssessmentApp.prototype.exportJSON = function () {
    var blob = new Blob([JSON.stringify(this.state, null, 2)], { type: "application/json" });
    var name = (this.state.assessmentName || "assessment").replace(/[^a-zA-Z0-9-_]/g, "-");
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
    var csv = rows.map(function (r) { return r.join(","); }).join("\n");
    var blob = new Blob([csv], { type: "text/csv" });
    var name = (this.state.assessmentName || "assessment").replace(/[^a-zA-Z0-9-_]/g, "-");
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
        ["Overall Score", (self.getOverallScore() || 0) + "%"],
        ["Controls Assessed", Object.keys(self.state.responses).length + " / " + self.data.totalControls],
        ["Gaps Identified", self.getGapControls().length],
        [],
        ["Pillar", "Score"],
      ];
      [1, 2, 3, 4].forEach(function (p) {
        summaryData.push([
          "Pillar " + p + " — " + self.data.pillars[String(p)].name,
          (self.getPillarScore(p) || 0) + "%",
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
          score !== null ? Math.round(score * 100) + "%" : "N/A",
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
          score !== null ? Math.round(score * 100) + "%" : "",
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
          score !== null ? score + "%" : "N/A",
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
      var name = (self.state.assessmentName || "assessment").replace(/[^a-zA-Z0-9-_]/g, "-");
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
     EXPOSE GLOBALLY
     ================================================================ */
  window.AssessmentApp = AssessmentApp;
})();
