# Phase 5 Research: Documentation & Framework Integration for DEC

**Phase:** 5 — Documentation & Framework Integration
**Researched:** 2026-02-10
**Goal:** Update framework controls, solutions-index, DEC playbook, and complete solution documentation suite — validating with mkdocs build --strict

---

## 1. Control Tip Admonitions (DOC-01)

### Current State of DEC References in Controls

Four controls must have tip admonitions referencing DEC v2.0.0. Here is the current state of each:

#### Control 1.5 — Data Loss Prevention (DLP) and Sensitivity Labels

**File:** `docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md` (355 lines)

**Existing DEC reference (line 245-246):**
```markdown
!!! tip "Automation Available"
    See [Deny Event Correlation Report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report) in FSI-AgentGov-Solutions for aggregated DLP violation reporting across Purview Audit, DLP, and Application Insights.
```

**Location:** After Key Configuration Points section (line 245), before Zone-Specific Requirements section.

**Assessment:** Already has a tip admonition. Needs updating to:
- Reference v2.0.0
- Update description to mention Dataverse persistence, daily orchestration, zone-based alerting, and SHA-256 evidence export
- Expand capabilities list to match completed solution scope

#### Control 1.7 — Comprehensive Audit Logging and Compliance

**File:** `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md` (268 lines)

**Existing DEC references (lines 146-150):**
```markdown
!!! tip "Advanced Implementation: Deny Event Correlation Report"
    For daily operational reports correlating deny events across Purview Audit, DLP, and Application Insights, see [Deny Event Correlation Report](../../playbooks/advanced-implementations/deny-event-correlation-report/index.md).

    **Deployable Solution:** [deny-event-correlation-report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report) provides PowerShell extraction scripts and KQL queries.
```

**Location:** In the Related Controls section area (after the Related Controls table, line 146), before the Audit Configuration Validator tip (line 151).

**Assessment:** Already has a tip admonition but needs updating to:
- Reference v2.0.0
- Expand capabilities list (Dataverse persistence, Power Automate orchestration, Teams alerting, anomaly detection, evidence export)
- Match the format used by newer solution tip admonitions (e.g., Session Security Configurator pattern with capabilities bullet list)

#### Control 1.8 — Runtime Protection and External Threat Detection

**File:** `docs/controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md` (381 lines)

**Existing DEC reference (line 332):**
```markdown
- [Deny Event Correlation Report Playbook](../../playbooks/advanced-implementations/deny-event-correlation-report/index.md) - Multi-source correlation with Power BI dashboard
```

**Location:** In the "Correlation with Purview Audit" subsection under RAI Telemetry Capture (line 330-332), as a bullet link rather than a tip admonition.

**Assessment:** Has a plain link but NO tip admonition. Needs:
- A proper `!!! tip` admonition with DEC v2.0.0 details
- Best placement: after the Related Controls table (around line 245) similar to the Content Moderation Governance Monitor tip that follows at line 249
- Alternatively, replace/augment the existing bullet link at line 332

#### Control 3.4 — Incident Reporting and Root Cause Analysis

**File:** `docs/controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md` (134 lines)

**Existing DEC reference (line 90):**
```markdown
| [1.5 - DLP and Sensitivity Labels](../pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP violation correlation ([Deny Event Correlation Report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report)) |
```

**Location:** In the Related Controls table as an inline link.

**Assessment:** Has an inline link in the Related Controls table but NO tip admonition. Needs:
- A proper `!!! tip` admonition block
- Best placement: after the Related Controls table (after line 92), before Implementation Playbooks section

### Existing Tip Admonition Patterns

Two patterns are used across the codebase for solution tip admonitions:

**Pattern A: Simple (used by 1.5, 2.12, 3.3, 1.14, 2.4, etc.):**
```markdown
!!! tip "Automation Available"
    See [Solution Name](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/solution-slug) in FSI-AgentGov-Solutions for [brief description].
```

**Pattern B: Detailed with capabilities list (used by 1.23/SSC, 1.7/ACV, 1.8/CMM, 3.8/AAM):**
```markdown
!!! tip "Automated Validation: Solution Display Name"
    For [purpose description], see the **Solution Display Name** solution.

    **Capabilities:**

    - Capability 1
    - Capability 2
    - Capability 3
    - Capability 4
    - Capability 5

    **Deployable Solution:** [solution-slug](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/solution-slug) provides [component summary].
```

**Recommendation:** Use Pattern B for Controls 1.7, 1.8, and 3.4 (detailed, consistent with other v4-v8 solution tips). Update the existing Pattern A in Control 1.5 to Pattern B for consistency.

### Proposed Tip Admonition Text (DEC v2.0.0)

Based on the established Pattern B and the completed DEC solution scope from phases 1-4:

```markdown
!!! tip "Automated Validation: Deny Event Correlation Report"
    For daily operational reports correlating deny events across Purview Audit, DLP, and Application Insights with anomaly detection and zone-based alerting, see the **Deny Event Correlation Report** solution.

    **Capabilities:**

    - Multi-source deny event extraction (RAI telemetry, Purview Audit, Purview DLP)
    - Daily correlation engine with 7-day trend analysis and volume anomaly detection
    - Zone-based alerting with Teams adaptive cards and email notifications
    - Dataverse persistence with zone-based retention (90d/365d/730d)
    - SHA-256 integrity-hashed evidence export with regulatory alignment mapping

    **Deployable Solution:** [deny-event-correlation-report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report) provides PowerShell extraction scripts, Dataverse infrastructure, Power Automate orchestration flow, and evidence export pipeline.
```

**Variant for Control 1.5** (DLP-specific emphasis):
```markdown
!!! tip "Automated Validation: Deny Event Correlation Report"
    For aggregated DLP violation reporting correlating deny events across Purview Audit, DLP, and Application Insights with anomaly detection and zone-based alerting, see the **Deny Event Correlation Report** solution.

    **Capabilities:**

    - Multi-source deny event extraction (RAI telemetry, Purview Audit, Purview DLP)
    - Daily correlation engine with 7-day trend analysis and volume anomaly detection
    - Zone-based alerting with Teams adaptive cards and email notifications
    - Dataverse persistence with zone-based retention (90d/365d/730d)
    - SHA-256 integrity-hashed evidence export with regulatory alignment mapping

    **Deployable Solution:** [deny-event-correlation-report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report) provides PowerShell extraction scripts, Dataverse infrastructure, Power Automate orchestration flow, and evidence export pipeline.
```

**Variant for Control 3.4** (incident reporting emphasis):
```markdown
!!! tip "Automated Validation: Deny Event Correlation Report"
    For automated deny event detection and alerting supporting incident reporting workflows, see the **Deny Event Correlation Report** solution.

    **Capabilities:**

    - Multi-source deny event extraction (RAI telemetry, Purview Audit, Purview DLP)
    - Daily correlation engine with 7-day trend analysis and volume anomaly detection
    - Zone-based alerting with Teams adaptive cards and email notifications
    - Dataverse persistence with zone-based retention (90d/365d/730d)
    - SHA-256 integrity-hashed evidence export with regulatory alignment mapping

    **Deployable Solution:** [deny-event-correlation-report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report) provides PowerShell extraction scripts, Dataverse infrastructure, Power Automate orchestration flow, and evidence export pipeline.
```

### Placement Strategy

| Control | Current Reference | Action | Insert After |
|---------|------------------|--------|-------------|
| 1.5 | `!!! tip "Automation Available"` (line 245) | REPLACE existing tip with Pattern B | Same location (Key Config Points → Zone Requirements) |
| 1.7 | `!!! tip "Advanced Implementation"` (line 146) | REPLACE existing tip with Pattern B | Same location (after Related Controls table) |
| 1.8 | Bullet link at line 332 | ADD new Pattern B tip | After Related Controls table (line 245, before CMM tip at line 249) |
| 3.4 | Inline link in Related Controls table (line 90) | ADD new Pattern B tip | After Related Controls table (after line 92) |

---

## 2. Solutions-Index Update (DOC-02)

### Current DEC Entry

**File:** `docs/reference/solutions-index.md` (530 lines)

**Summary table entry (line 15):**
```markdown
| [Deny Event Correlation Report](#deny-event-correlation-report) | v1.1.0 | Work In Progress | Daily deny event correlation across Purview Audit, DLP, and Application Insights | 1.5, 1.7, 3.4 |
```

**Detail section (lines 103-122):**
```markdown
### Deny Event Correlation Report

Aggregates and correlates deny events from multiple Microsoft sources to provide unified visibility into blocked agent activities.

**Data Sources:**
- Purview Unified Audit Log
- DLP policy violations
- Application Insights RAI telemetry

**Components:**
- Power BI report template
- Data extraction scripts
- Correlation logic

**Framework Playbook:** [Deny Event Correlation Report](../playbooks/advanced-implementations/deny-event-correlation-report/index.md)

**Repository Link:** [deny-event-correlation-report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report)
```

**Version history table entry (line 517):**
```markdown
| Deny Event Correlation Report | v1.1.0 | January 2026 |
```

### Changes Required

1. **Summary table:** Update version to `v2.0.0`, status to `Completed`, add `1.8` to Related Controls
2. **Detail section:** Expand description, add regulatory alignment, update component list to reflect full v2.0.0 scope
3. **Version history:** Update to `v2.0.0` / `February 2026`

### Updated Detail Section (Proposed)

Based on the pattern used by other completed solutions (Session Security Configurator, Compliance Dashboard):

```markdown
### Deny Event Correlation Report

!!! success "Production Ready"
    v2.0.0 includes PowerShell extraction scripts, Dataverse infrastructure, Power Automate orchestration flow, Teams adaptive card alerting, evidence export pipeline, and comprehensive deployment documentation.

Aggregates and correlates deny events from multiple Microsoft sources to provide unified visibility into blocked agent activities with daily automated orchestration, anomaly detection, and zone-based alerting.

**Components:**

- PowerShell scripts for multi-source deny event extraction (RAI telemetry, Purview Audit, DLP)
- DECClient.psm1 shared module with Entra ID authentication and Dataverse integration
- Dataverse tables for deny events, correlations, alerts, and validation history
- Daily correlation engine with 7-day trend analysis and volume anomaly detection (>2σ)
- Power Automate orchestration flow (DEC-DailyOrchestrator) with Azure Automation
- Teams adaptive card alerts with severity routing (Critical/High → Teams + email, Warning → email)
- SHA-256 integrity-hashed evidence export with regulatory alignment mapping
- Zone-based retention rules (90d/365d/730d per zone)
- Compliance Dashboard feed integration via IntegrationConfig.psm1

**Regulatory Alignment:**

- FINRA 4511 (Books and Records — deny event retention)
- FINRA 3110 (Supervisory Systems — AI governance evidence)
- FINRA 25-07 (AI/ML Governance — deny event correlation)
- SEC 17a-3/4 (Recordkeeping — immutable evidence export)
- SOX 302/404 (Internal Controls — daily automated validation)
- GLBA 501(b) (Safeguards Rule — DLP enforcement evidence)

**Related Controls:**

- [1.5 - DLP and Sensitivity Labels](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)
- [1.7 - Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [1.8 - Runtime Protection](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md)
- [3.4 - Incident Reporting](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)

**Framework Playbook:** [Deny Event Correlation Report](../playbooks/advanced-implementations/deny-event-correlation-report/index.md)

**Repository Link:** [deny-event-correlation-report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report)
```

### Pattern Comparison with Other Completed Solutions

| Solution | Status | Has `!!! success` banner | Has Regulatory Alignment | Has Related Controls links |
|----------|--------|--------------------------|--------------------------|---------------------------|
| Session Security Configurator | Completed | No | Yes | Yes (links) |
| Compliance Dashboard | Completed | Yes (`!!! success`) | Yes | Yes (single link) |
| Scope Drift Monitor | Completed | Yes (`!!! success`) | Yes | Yes (single link) |
| **DEC v2.0.0 (proposed)** | Completed | Yes (`!!! success`) | Yes | Yes (4 links) |

---

## 3. DEC Solution Documentation Suite (DOC-03)

### Required Documents

Per the REQUIREMENTS.md, the suite consists of 7 documents:

| Document | File Name | Status | Location |
|----------|-----------|--------|----------|
| README | `README.md` | EXISTS (root) + EXISTS (docs/) — both need v2.0.0 rewrite | `deny-event-correlation-report/` |
| PREREQUISITES | `PREREQUISITES.md` | MISSING | `deny-event-correlation-report/docs/` |
| SCHEMA | `SCHEMA.md` | EXISTS (321 lines) — current | `deny-event-correlation-report/docs/` |
| EVIDENCE_EXPORT | `EVIDENCE_EXPORT.md` | MISSING | `deny-event-correlation-report/docs/` |
| FLOW_SETUP | `FLOW_SETUP.md` | EXISTS (446 lines) — current | `deny-event-correlation-report/docs/` |
| TROUBLESHOOTING | `TROUBLESHOOTING.md` | MISSING | `deny-event-correlation-report/docs/` |
| CHANGELOG | `CHANGELOG.md` | MISSING | `deny-event-correlation-report/` |

### Existing Documentation Inventory

Files in `maintainers-local/solutions-staging/deny-event-correlation-report/docs/`:
- `README.md` — Staging overview (needs v2.0.0 rewrite)
- `SCHEMA.md` — Dataverse schema reference (321 lines, current)
- `FLOW_SETUP.md` — DEC-DailyOrchestrator setup guide (446 lines, current)

Root-level:
- `README.md` — Solution root README (exists, minimal stub)

### Documents to Create

1. **PREREQUISITES.md** — Extract from FLOW_SETUP.md prerequisites section + add Dataverse requirements, Entra app registration details, PowerShell module dependencies
2. **EVIDENCE_EXPORT.md** — Document Export-DenyEventEvidence.ps1 usage, parameters, output format, SHA-256 verification, Test-EvidenceIntegrity.ps1
3. **TROUBLESHOOTING.md** — Common deployment, runtime, and evidence export issues with resolutions
4. **CHANGELOG.md** — Version history from v1.0.0 through v2.0.0

### Documents to Update

1. **Root README.md** — Full rewrite with v2.0.0 architecture overview, quick start, component inventory, directory structure
2. **docs/README.md** — Update from staging docs to proper documentation index

### Content Sources for New Documents

| Document | Primary Source Material |
|----------|----------------------|
| PREREQUISITES | FLOW_SETUP.md §1, Phase 1 RESEARCH.md, Phase 2 RESEARCH.md |
| EVIDENCE_EXPORT | Phase 4 Plan 04-01 (Export-DenyEventEvidence.ps1), 04-01-SUMMARY.md |
| TROUBLESHOOTING | FLOW_SETUP.md §6, common patterns from other solution TROUBLESHOOTING docs |
| CHANGELOG | Phase 1-4 SUMMARY files, ROADMAP.md requirement completion timeline |

### Note on Scope

DOC-03 specifies the docs suite for "FSI-AgentGov-Solutions" — these files are staged locally in `maintainers-local/solutions-staging/` (gitignored) and transferred to the companion repo manually. The plan should create/update files in the staging directory.

---

## 4. Framework Playbook Update (DOC-04)

### Current Playbook Structure

**Directory:** `docs/playbooks/advanced-implementations/deny-event-correlation-report/`

**Files (6):**

| File | Title | Lines | Status |
|------|-------|-------|--------|
| `index.md` | Deny Event Correlation Report | 224 | v1.0/v1.1 — needs v2.0.0 refresh |
| `purview-audit-extraction.md` | Purview Audit Extraction | — | Existing (check if current) |
| `dlp-event-extraction.md` | DLP Event Extraction | — | Existing (check if current) |
| `app-insights-rai-telemetry.md` | App Insights RAI Telemetry | — | Existing (check if current) |
| `power-bi-correlation.md` | Power BI Correlation | — | Existing (check if current) |
| `deployment-guide.md` | Deployment Guide | 435 | Existing (check if current) |

### index.md Current Content Assessment

The overview playbook (`index.md`, 224 lines) reflects the v1.0/v1.1 architecture:
- **Solution Overview:** Shows stateless CSV pipeline with PowerShell → Azure Blob → Power BI
- **Implementation Kit:** References "PowerShell Scripts, KQL Queries, Power BI Template, Documentation"
- **Repository link:** Points to `v1.0.0`
- **Missing from v2.0.0:** Dataverse persistence, correlation engine, Power Automate orchestration, Teams alerting, anomaly detection, evidence export, zone-based retention

### Changes Required for index.md v2.0.0

1. **Solution Overview diagram:** Update Mermaid diagram to show Dataverse persistence layer, Power Automate orchestrator, alert routing
2. **Implementation Kit:** Update component table to include Dataverse schema, Power Automate flow, adaptive card template, evidence export scripts
3. **Version/status:** Update to v2.0.0, February 2026
4. **New sections:** Add Dataverse architecture overview, alert routing, evidence export
5. **Repository link:** Update to v2.0.0
6. **Playbook Structure table:** Add links to solution docs (SCHEMA, FLOW_SETUP, EVIDENCE_EXPORT)

### mkdocs.yml Navigation

Current nav entries (lines 540-546):
```yaml
      - Deny Event Correlation Report:
        - Overview: playbooks/advanced-implementations/deny-event-correlation-report/index.md
        - Purview Audit Extraction: playbooks/advanced-implementations/deny-event-correlation-report/purview-audit-extraction.md
        - DLP Event Extraction: playbooks/advanced-implementations/deny-event-correlation-report/dlp-event-extraction.md
        - App Insights RAI Telemetry: playbooks/advanced-implementations/deny-event-correlation-report/app-insights-rai-telemetry.md
        - Power BI Correlation: playbooks/advanced-implementations/deny-event-correlation-report/power-bi-correlation.md
        - Deployment Guide: playbooks/advanced-implementations/deny-event-correlation-report/deployment-guide.md
```

**Assessment:** No nav changes needed for DOC-04 — the playbook files already exist in mkdocs.yml. The index.md content update is sufficient.

---

## 5. Build Validation

### Current Build Status

Run `mkdocs build --strict` after all changes to validate:
- No broken links from updated tip admonitions
- No broken links from updated solutions-index
- No broken links from updated playbook index
- All existing nav entries still resolve

### Risk Areas

| Risk | File | Concern |
|------|------|---------|
| Link format in tip admonitions | Controls 1.5, 1.7, 1.8, 3.4 | External GitHub links — won't break mkdocs but should be verified |
| Internal playbook links | index.md | Links to sub-playbook pages must use correct relative paths |
| Related Controls links in solutions-index | solutions-index.md | Adding 1.8 to related controls requires adding the link |

---

## 6. Prior Phase Plan Format Reference

### YAML Frontmatter (established pattern)

```yaml
---
phase: 5
plan: 1
wave: 1
title: "Plan title"
depends_on: []
must_haves: ["DOC-01", "DOC-02"]
gap_closure: false
---
```

### Plan Structure (established pattern)

1. **H1 title:** `# Plan XX-YY: Title`
2. **Objective:** 1-2 sentence goal description
3. **Must-Haves Addressed:** Table mapping to REQUIREMENTS.md
4. **Context:** Relevant background (pattern sources, file locations)
5. **Tasks:** Numbered tasks with:
   - File path
   - Action (CREATE, MODIFY, REPLACE)
   - Details (what to change/create)
   - Acceptance criteria (checkboxes)
6. **Validation:** Build commands to run
7. **Deviations notes** (if any expected)

### Summary Structure (established pattern)

```yaml
---
phase: X
plan: Y
title: "Plan title"
status: complete
completed: YYYY-MM-DD
files_created: []
files_modified: []
---
```

Followed by:
1. **H1 title:** `# Plan XX-YY Summary: Title`
2. **Completed section:** Task-by-task summary
3. **Decisions Made** (if any)
4. **Artifacts** (file paths and line counts)

---

## 7. Technical Approach Recommendations

### Plan 05-01: Control Tip Admonitions + Solutions-Index (DOC-01, DOC-02)

**Wave 1** — Can be executed independently of Plans 05-02 and 05-03.

**Tasks:**
1. Replace tip admonition in Control 1.5 (Pattern A → Pattern B, DEC v2.0.0)
2. Replace tip admonition in Control 1.7 (update existing, expand to Pattern B)
3. Add tip admonition to Control 1.8 (new, Pattern B, after Related Controls)
4. Add tip admonition to Control 3.4 (new, Pattern B, after Related Controls)
5. Update solutions-index.md summary table (version, status, related controls)
6. Update solutions-index.md detail section (full rewrite per Completed pattern)
7. Update solutions-index.md version history table
8. Run `mkdocs build --strict`

**Key decisions:**
- All 4 controls get Pattern B format for consistency
- Control 1.8: Add tip after Related Controls table (line ~245), NOT at line 332 — the line 332 reference should be kept as supplementary context
- Control 3.4: Keep the inline DEC link in Related Controls table AND add the tip block after
- solutions-index.md: Add `!!! success "Production Ready"` banner matching Scope Drift Monitor/Compliance Dashboard pattern
- Add Control 1.8 to the Related Controls column in the summary table

### Plan 05-02: DEC Solution Documentation Suite (DOC-03)

**Wave 1** — Independent of Plan 05-01/05-03 (writes to gitignored staging directory).

**Tasks:**
1. Create `PREREQUISITES.md` in `maintainers-local/solutions-staging/deny-event-correlation-report/docs/`
2. Create `EVIDENCE_EXPORT.md` in same docs directory
3. Create `TROUBLESHOOTING.md` in same docs directory
4. Create `CHANGELOG.md` in `maintainers-local/solutions-staging/deny-event-correlation-report/`
5. Rewrite root `README.md` for v2.0.0
6. Update `docs/README.md` as documentation index

**Note:** These files are in `maintainers-local/` (gitignored) so they don't affect mkdocs build.

### Plan 05-03: Framework Playbook v2.0.0 Refresh + Build Validation (DOC-04)

**Wave 2** — Should run after Plan 05-01 (tip admonitions must be in place before final build validation).

**Tasks:**
1. Update `docs/playbooks/advanced-implementations/deny-event-correlation-report/index.md` with v2.0.0 architecture
2. Run `mkdocs build --strict` for final validation
3. Verify all cross-references resolve

---

## 8. Risks and Dependencies

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Tip admonition indentation errors break mkdocs build | Medium | High | Use exact 4-space indentation; validate immediately |
| solutions-index.md format inconsistency | Low | Low | Follow established Completed solution patterns |
| Broken relative links in updated playbook index.md | Medium | High | Verify all `../../` paths resolve; run strict build |
| SCHEMA.md / FLOW_SETUP.md already exist — overwrite risk | Low | Medium | Leave existing docs as-is; create only MISSING documents |
| Plan 05-02 writes to gitignored directory — not validated by mkdocs build | Certain | Low | Expected behavior; only Plans 05-01/05-03 need build validation |
| Control version footers may need updating after tip changes | Low | Low | Update "Updated: February 2026" footers on modified controls |

### Dependencies

| Plan | Depends On | Blocks |
|------|-----------|--------|
| 05-01 | Phases 1-4 complete (DEC solution exists) | 05-03 (build validation) |
| 05-02 | Phases 1-4 complete (artifacts exist to document) | None (gitignored) |
| 05-03 | 05-01 (tip admonitions in controls) | None (final step) |

---

## 9. File Inventory for All Changes

### Files to Modify (Plan 05-01)

| File | Change |
|------|--------|
| `docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md` | Replace tip admonition (lines 245-246) |
| `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md` | Replace tip admonition (lines 146-150) |
| `docs/controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md` | Add tip admonition after Related Controls (after line 245) |
| `docs/controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md` | Add tip admonition after Related Controls (after line 92) |
| `docs/reference/solutions-index.md` | Update DEC entry (lines 15, 103-122, 517) |

### Files to Modify (Plan 05-03)

| File | Change |
|------|--------|
| `docs/playbooks/advanced-implementations/deny-event-correlation-report/index.md` | v2.0.0 architecture refresh |

### Files to Create (Plan 05-02, gitignored)

| File | Content Source |
|------|---------------|
| `maintainers-local/solutions-staging/deny-event-correlation-report/docs/PREREQUISITES.md` | FLOW_SETUP.md §1, research docs |
| `maintainers-local/solutions-staging/deny-event-correlation-report/docs/EVIDENCE_EXPORT.md` | Phase 4 summaries |
| `maintainers-local/solutions-staging/deny-event-correlation-report/docs/TROUBLESHOOTING.md` | FLOW_SETUP.md §6, common patterns |
| `maintainers-local/solutions-staging/deny-event-correlation-report/CHANGELOG.md` | Phase 1-4 summaries, ROADMAP |

### Files to Rewrite (Plan 05-02, gitignored)

| File | Change |
|------|--------|
| `maintainers-local/solutions-staging/deny-event-correlation-report/README.md` | Full v2.0.0 rewrite |
| `maintainers-local/solutions-staging/deny-event-correlation-report/docs/README.md` | Update to documentation index |

---

## 10. DEC v2.0.0 Component Summary (for documentation reference)

Compiled from Phase 1-4 execution summaries:

### Scripts (12 files)

| Script | Purpose | Phase |
|--------|---------|-------|
| `Export-RaiTelemetry.ps1` | RAI telemetry extraction from App Insights | Phase 1 |
| `Export-CopilotDenyEvents.ps1` | Purview Audit CopilotInteraction extraction | Phase 1 |
| `Export-DlpCopilotEvents.ps1` | Purview DLP Copilot event extraction | Phase 1 |
| `Invoke-DailyDenyReport.ps1` | Daily orchestration script (all 3 sources + correlation + alerts) | Phase 1, updated Phase 3 |
| `Invoke-DenyEventCorrelation.ps1` | Correlation engine with trend analysis | Phase 2 |
| `Invoke-DECAlertEvaluation.ps1` | Alert evaluation (VolumeAnomaly, NewAgent, ZoneCritical, RoutineDeny) | Phase 3 |
| `Set-DECRetentionRules.ps1` | Zone-based Dataverse retention configuration | Phase 2 |
| `Export-DenyEventEvidence.ps1` | SHA-256 evidence export with regulatory alignment | Phase 4 |
| `Test-EvidenceIntegrity.ps1` | SHA-256 hash verification utility | Phase 4 |
| `private/DECClient.psm1` | Shared module (15 functions, Entra ID auth, Dataverse CRUD) | Phase 1-3 |
| `private/Get-DECValidationResults.ps1` | Dataverse query helper for evidence export | Phase 4 |

### Python (5 files)

| Script | Purpose | Phase |
|--------|---------|-------|
| `dec_client.py` | Dataverse Web API client (MSAL auth, retry) | Phase 2 |
| `create_dataverse_schema.py` | Table and column creation | Phase 2 |
| `create_environment_variables.py` | Environment variable creation | Phase 2 |
| `create_connection_references.py` | Connection reference creation | Phase 2 |
| `deploy.py` | Deployment orchestrator | Phase 2 |

### Templates (3 files)

| File | Purpose | Phase |
|------|---------|-------|
| `deny-event-baseline.json` | Default configuration with alerting thresholds | Phase 1, updated Phase 3 |
| `dec-daily-orchestrator-flow.json` | Power Automate cloud flow definition | Phase 3 |
| `adaptive-card-deny-alert.json` | Teams adaptive card template (3 alert types) | Phase 3 |

### Dataverse Tables (4)

| Table | Ownership | Purpose |
|-------|-----------|---------|
| `fsi_DenyEvent` | UserOwned | Primary deny event records from 3 sources |
| `fsi_DenyCorrelation` | UserOwned | Daily correlation summaries with trend data |
| `fsi_DenyAlert` | UserOwned | Alert history with severity classification |
| `fsi_DenyValidationHistory` | OrganizationOwned | Immutable validation audit log |

### Regulatory Alignment (6 regulations)

- FINRA 4511 (Books and Records)
- FINRA 3110 (Supervisory Systems)
- FINRA 25-07 (AI/ML Governance RFI)
- SEC 17a-3/4 (Recordkeeping)
- SOX 302/404 (Internal Controls)
- GLBA 501(b) (Safeguards Rule)

---

*Research completed: 2026-02-10*
