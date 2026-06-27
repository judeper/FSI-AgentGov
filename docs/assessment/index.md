---
description: "Interactive governance readiness assessment for Microsoft 365 AI agents. Score your controls in the browser — no data leaves your device."
search:
  boost: 2
---
# Governance Readiness Assessment

All data stays in your browser — nothing is uploaded.

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

The Governance Readiness Assessment helps organizations evaluate their implementation of the [FSI Agent Governance Framework](../framework/index.md). It scores 78 of the 79 framework controls (see note below), producing a personalized scorecard, gap analysis, and remediation roadmap — entirely in your browser.

!!! note "78 of 79 controls scored"
    Control 2.27 (Consumption-Entitlement Governance) is present in the full framework manifest but is not yet included in the browser assessment. It will be added in an upcoming release.

### How It Works

1. **Scoping** — Configure your organization type, active governance zones, and adoption phase
2. **Phase 1 Assessment** — Rate each control's implementation status (Yes / Partial / No / N/A)
3. **Phase 2 Drill-Down** — Answer detailed sub-questions for gap controls to refine scores
4. **Results Dashboard** — View executive scorecard, regulatory exposure, and remediation roadmap
5. **Export** — Download results as Excel workbook, JSON, CSV, or print to PDF

JSON exports include a `_metadata` + `_computedScores` envelope (framework version, schema version, pre-computed pillar/overall scores, derived `assessmentStatus`) so downstream tools can consume scores without recomputing them. See [`assessment/data/README.md`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/data/README.md#portal-export-schema) for the full schema.

### Verification Drawer

The Phase 1 assessment includes a per-control "How to verify" drawer with Yes/Partial/No implementation criteria. Additional verification metadata — portal paths, PowerShell commands, expected evidence, and collector field mappings — is available for controls where the manifest has been fully authored; many controls currently show placeholder metadata that will be completed in upcoming releases.

!!! note "Assessment surface distinction"
    The browser assessment SPA is a self-assessment questionnaire. The Python assessment engine (in `assessment/`) is a telemetry-driven scorer that evaluates collected tenant data against manifest `pass_condition` values. Both share `assessment/manifest/controls.json` as a common source of truth but serve different audiences.

### Scoring Methodology

- **Yes** = 1.0 (fully implemented)
- **Partial** = 0.5 (refined by drill-down sub-questions)
- **No** = 0.0 (not implemented)
- **N/A** = excluded from scoring

Aggregate scores: `score = sum(controlScores) / count(applicableControls) × 100`

**RAG thresholds:** Green (80%+), Amber (50–79%), Red (below 50%)

Gap controls are prioritized for remediation using: `riskPriority = (1 − score) × regulatoryWeight × zoneWeight × phaseWeight`

### Data Privacy

All assessment data stays in your browser. No data is sent to any server. Use "Save to File" (JSON export) as the primary artifact for sharing and archival.

!!! note "Disclaimer"
    Scores reflect self-reported implementation status and do not constitute a compliance certification. This tool helps support governance readiness review and is not a substitute for professional compliance guidance.
