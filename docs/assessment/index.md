# Governance Readiness Assessment

**Scoring:** Yes (1.0) · Partial (0.5) · No (0.0) · N/A (excluded)

**RAG:** Green 80%+ · Amber 50–79% · Red <50%

All data stays in your browser.

<div id="assessment-app" class="assessment-container">
  <noscript>
    <div class="admonition warning">
      <p class="admonition-title">JavaScript Required</p>
      <p>The Governance Readiness Assessment tool requires JavaScript to run.
      Please enable JavaScript in your browser to use this tool.</p>
    </div>
  </noscript>
  <div class="assessment-loading">
    <p>Loading assessment tool...</p>
  </div>
</div>

---

## About This Tool

The Governance Readiness Assessment is an interactive tool that helps organizations evaluate their implementation of the [FSI Agent Governance Framework](../framework/index.md) across all 72 controls. It produces a personalized scorecard, gap analysis, and remediation roadmap.

### How It Works

1. **Scoping** — Configure your organization type, active governance zones, and adoption phase
2. **Phase 1 Assessment** — Rate each control's implementation status (Yes / Partial / No / N/A)
3. **Phase 2 Drill-Down** — Answer detailed sub-questions for gap controls to refine scores
4. **Results Dashboard** — View executive scorecard, regulatory exposure, and remediation roadmap
5. **Export** — Download results as Excel workbook, JSON, CSV, or print to PDF

### Scoring Methodology

- **Yes** = 1.0 (fully implemented)
- **Partial** = 0.5 (refined by drill-down sub-questions)
- **No** = 0.0 (not implemented)
- **N/A** = excluded from scoring

Aggregate scores are calculated as: `score = sum(controlScores) / count(applicableControls) x 100`

**RAG thresholds:** Green (80%+), Amber (50–79%), Red (below 50%)

**Zone-specific scoring:** Zone scores exclude controls whose zone requirements are optional, awareness-only, or N/A.

- **Zone 1** (Personal Productivity) — approximately 10 controls excluded from scoring
- **Zone 3** (Enterprise Managed) — all 72 controls apply

This prevents penalizing organizations for enterprise-only controls that do not apply to personal productivity agents.

### Risk Priority

Gap controls are prioritized for remediation using: `riskPriority = (1 - score) x regulatoryWeight x zoneWeight x phaseWeight`

- Regulatory weight: 3.0 (4+ regulations), 2.0 (2-3), 1.0 (1)
- Zone weight: 3.0 (Zone 3), 2.0 (Zone 2), 1.0 (Zone 1)
- Phase weight: 3.0 (current phase), 2.0 (next phase), 1.0 (future)

### Collaboration

The governance lead can export role-specific sections as JSON files for relevant admins to complete independently, then import completed sections back with conflict detection.

### Data Privacy

All assessment data stays in your browser. No data is sent to any server. Use "Save to File" (JSON export) as the primary artifact for sharing and archival. Browser localStorage is used only as a convenience cache.

!!! note "Disclaimer"
    This tool helps support governance readiness assessment. It does not constitute legal advice, is not a compliance certification, and should not be used as a substitute for professional compliance guidance.
