---
phase: 04-evidence-export-framework-integration
plan: CMM-03
title: "Documentation suite (SCHEMA.md, EVIDENCE_EXPORT.md, TROUBLESHOOTING.md, README update, CHANGELOG)"
type: execute
wave: 2
depends_on: ["04-CMM-01", "04-CMM-02"]
files_modified:
  - FSI-AgentGov-Solutions/content-moderation-monitor/docs/SCHEMA.md
  - FSI-AgentGov-Solutions/content-moderation-monitor/docs/EVIDENCE_EXPORT.md
  - FSI-AgentGov-Solutions/content-moderation-monitor/docs/TROUBLESHOOTING.md
  - FSI-AgentGov-Solutions/content-moderation-monitor/docs/PREREQUISITES.md
  - FSI-AgentGov-Solutions/content-moderation-monitor/README.md
  - FSI-AgentGov-Solutions/content-moderation-monitor/CHANGELOG.md
autonomous: true

must_haves:
  truths:
    - "SCHEMA.md documents all three Dataverse tables (fsi_moderationbaselines, fsi_moderationvalidationhistory, fsi_moderationviolations) with column definitions"
    - "SCHEMA.md documents shared option sets (fsi_acv_zone, fsi_acv_severity), 7 environment variables (fsi_CMM_*), and 3 connection references"
    - "EVIDENCE_EXPORT.md provides step-by-step instructions for interactive and service principal evidence export, zone filtering, baseline inclusion, and verification"
    - "EVIDENCE_EXPORT.md includes JSON evidence schema reference with per-agent violation fields"
    - "TROUBLESHOOTING.md covers deployment, authentication, validation, drift detection, evidence export, and Power Automate flow issues"
    - "README.md status reflects v1.0.0 and includes evidence export in Quick Start and Solution Components"
    - "CHANGELOG.md includes [1.0.0] release entry with Phase 4 evidence export and framework integration additions"
    - "PREREQUISITES.md includes MSAL.PS module requirement for evidence export"
  artifacts:
    - path: "FSI-AgentGov-Solutions/content-moderation-monitor/docs/SCHEMA.md"
      provides: "Dataverse schema reference documentation"
      contains: "fsi_moderationbaselines"
    - path: "FSI-AgentGov-Solutions/content-moderation-monitor/docs/EVIDENCE_EXPORT.md"
      provides: "Evidence export operations guide"
      contains: "Export-ContentModerationEvidence"
    - path: "FSI-AgentGov-Solutions/content-moderation-monitor/docs/TROUBLESHOOTING.md"
      provides: "Troubleshooting guide for operators"
      contains: "Common Issues"
    - path: "FSI-AgentGov-Solutions/content-moderation-monitor/README.md"
      provides: "Updated README with v1.0.0 status and Phase 4 content"
      contains: "Export-ContentModerationEvidence"
    - path: "FSI-AgentGov-Solutions/content-moderation-monitor/CHANGELOG.md"
      provides: "v1.0.0 release notes"
      contains: "[1.0.0]"
  key_links:
    - from: "README.md Quick Start"
      to: "Export-ContentModerationEvidence.ps1"
      via: "Step 5-6 script reference"
      pattern: "Export-ContentModerationEvidence"
    - from: "README.md Documentation section"
      to: "docs/EVIDENCE_EXPORT.md"
      via: "link in documentation list"
      pattern: "EVIDENCE_EXPORT"
    - from: "EVIDENCE_EXPORT.md"
      to: "Test-EvidenceIntegrity.ps1"
      via: "verification instructions"
      pattern: "Test-EvidenceIntegrity"
    - from: "README.md Documentation section"
      to: "docs/SCHEMA.md"
      via: "link in documentation list"
      pattern: "SCHEMA"
    - from: "TROUBLESHOOTING.md"
      to: "Export-ContentModerationEvidence.ps1"
      via: "evidence export troubleshooting"
      pattern: "Export-ContentModerationEvidence"
---

# Plan 04-CMM-03: Documentation Suite

## Goal

Create the complete documentation suite for the Content Moderation Governance Monitor solution and update the README/CHANGELOG to reflect v1.0.0 completion. This gives administrators all the reference material needed to deploy, operate, and troubleshoot the solution.

**Depends on CMM-01** (evidence export script names referenced in docs) and **CMM-02** (Control 1.8 and solutions-index.md entries referenced in README).

## Tasks

### Task 1: Create docs/SCHEMA.md (Dataverse schema reference)

**File:** `content-moderation-monitor/docs/SCHEMA.md`

Replace the existing stub with full Dataverse schema documentation. Document all tables, columns, option sets, environment variables, and connection references.

**Structure:**

```markdown
# Dataverse Schema Reference

## Overview
Three tables, shared option sets, 7 environment variables, 3 connection references.

## Tables

### fsi_moderationbaselines
Per-agent baseline records. All columns with type, required flag, and description.
Key columns: fsi_agent_id, fsi_agent_name, fsi_moderation_level, fsi_is_active, fsi_captured_at, fsi_captured_by, fsi_raw_json.

### fsi_moderationvalidationhistory (Immutable)
Organization-owned scan summary records. All columns with type/description.
Key columns: fsi_run_id, fsi_total_agents, fsi_compliant_count, fsi_violation_count, fsi_overall_status, fsi_summary_json.
Note: Records are created once and never updated (audit trail).

### fsi_moderationviolations
Per-agent violation records with severity and regulatory context. All columns.
Key columns: fsi_agent_id, fsi_agent_name, fsi_expected_level, fsi_actual_level, fsi_severity, fsi_regulatory_context.

## Shared Option Sets

### fsi_acv_zone
Values: 0 (Unclassified), 1 (Personal Productivity), 2 (Team Collaboration), 3 (Enterprise Managed)

### fsi_acv_severity
Values: 1 (Passed), 2 (Warning), 3 (GracePeriod), 4 (Failed), 5 (Error)

## Environment Variables

Table of all 7 fsi_CMM_* variables:
fsi_CMM_ScanFrequencyHours, fsi_CMM_GracePeriodHours, fsi_CMM_IncludeSandbox, fsi_CMM_IncludeDrafts, fsi_CMM_BaselineAgeThresholdDays, fsi_CMM_TeamsGroupId, fsi_CMM_TeamsChannelId

## Connection References

Table of 3 references:
fsi_cr_dataverse_moderationmonitor, fsi_cr_office365_moderationmonitor, fsi_cr_teams_moderationmonitor

## Entity Relationship Diagram
ASCII diagram showing table relationships (baselines → violations via agent_id, history → violations via run_id).
```

Target: ~130 lines. Focus on what administrators need for deployment and maintenance.

**Acceptance Criteria:**
- [ ] All three tables documented with complete column definitions
- [ ] Shared option sets (fsi_acv_zone, fsi_acv_severity) documented with values
- [ ] 7 environment variables documented with schema name, type, default, purpose
- [ ] 3 connection references documented
- [ ] Entity relationship diagram included
- [ ] No "ensures compliance" language

### Task 2: Create docs/EVIDENCE_EXPORT.md (evidence export guide)

**File:** `content-moderation-monitor/docs/EVIDENCE_EXPORT.md`

Replace the existing stub with step-by-step evidence export guide. Follow the AAM evidence-export pattern adapted for per-agent CMM data.

**Structure:**

```markdown
# Evidence Export Guide

## Overview
Content moderation evidence export produces JSON files with SHA-256 integrity hashes for FINRA/SEC examination support. Exports include per-agent moderation validation results, violations, and baselines.

## Prerequisites
- Dataverse deployed with validation history records (Phase 2+)
- PowerShell 7.0+
- MSAL.PS module (Install-Module MSAL.PS)
- Appropriate Dataverse permissions

## Export Content Moderation Evidence

### Interactive Mode
.\Export-ContentModerationEvidence.ps1 -DataverseUrl "https://org.crm.dynamics.com" -TenantId "..." -OutputDirectory ".\exports" -Interactive

### Service Principal Mode
.\Export-ContentModerationEvidence.ps1 -DataverseUrl "https://org.crm.dynamics.com" -TenantId "..." -OutputDirectory ".\exports" -ClientId "..." -CertificateThumbprint "..."

### Export with Zone Filter
-Zone 3 for Zone 3 only (enterprise managed agents)

### Export with Baseline Inclusion
-IncludeBaselines adds active per-agent moderation baselines to evidence package

### Parameters Reference
Table of all parameters with descriptions, types, and defaults.

### Output Files
cmm-evidence-{zone}-{timestamp}.json — evidence data
cmm-evidence-{zone}-{timestamp}.json.sha256 — integrity hash

## Verify Evidence Integrity

### Single File
.\Test-EvidenceIntegrity.ps1 -EvidenceFilePath ".\exports\cmm-evidence-All-20260210.json"

### Batch Verification
Get-ChildItem .\exports\*.json | ForEach-Object { .\Test-EvidenceIntegrity.ps1 -EvidenceFilePath $_.FullName }

### Cross-Platform Verification
sha256sum -c exports/cmm-evidence-All-20260210.json.sha256

## Evidence JSON Schema
Full JSON structure reference with per-agent fields:
- metadata (solution, version, date range, counts)
- summary (scan totals, agent counts, severity breakdown)
- validations (scan history records)
- violations (per-agent: agentId, agentName, expectedLevel, actualLevel, severity, regulatoryContext)
- baselines (per-agent: agentId, agentName, moderationLevel, capturedBy, capturedAt)

## Recommended Export Schedule
- Monthly: Routine compliance monitoring
- Quarterly: Regulatory examination preparation (recommended 90+ day range)
- On-demand: Incident investigation or audit request

## Troubleshooting
Table of common evidence export issues: empty exports, auth failures, hash mismatches, missing baselines.
```

Target: ~150 lines. Focus on actionable steps.

**Acceptance Criteria:**
- [ ] Covers interactive and service principal export modes
- [ ] Zone filtering and baseline inclusion documented with examples
- [ ] Verification section with single, batch, and cross-platform examples
- [ ] JSON schema reference with per-agent violation fields
- [ ] Recommended export schedule included
- [ ] No "ensures compliance" language

### Task 3: Create docs/TROUBLESHOOTING.md

**File:** `content-moderation-monitor/docs/TROUBLESHOOTING.md`

Replace the existing stub with comprehensive troubleshooting guide covering all solution components.

**Structure:**

```markdown
# Troubleshooting Guide

## Deployment Issues
| Issue | Cause | Resolution |
Tables not created, environment variables missing, connection reference errors, deploy.py failures, permission errors.

## Authentication Issues
| Issue | Cause | Resolution |
Certificate auth failures, MSAL token errors, Dataverse 401/403, interactive auth popup issues.

## Validation Issues
| Issue | Cause | Resolution |
No agents found, unknown moderation level, zone lookup failures, bot metadata query errors, sandbox environments included unexpectedly.

## Drift Detection Issues
| Issue | Cause | Resolution |
No baseline found, drift always detected, baseline deactivation failures, runbook timeout on large agent counts.

## Evidence Export Issues
| Issue | Cause | Resolution |
Empty evidence file, hash mismatch after copy, ConvertTo-Json truncation (missing -Depth 10), zone filter returns no results, pagination timeout.

## Power Automate Flow Issues
| Issue | Cause | Resolution |
Flow not triggering, adaptive card not posting, connection reference not configured, JSON parsing errors in flow.

## Related Documentation
Links to PREREQUISITES.md, SCHEMA.md, EVIDENCE_EXPORT.md, FLOW_SETUP.md.
```

Target: ~110 lines. CMM-specific issues include "Unknown moderation level" (bot configuration parsing), agent enumeration failures, and per-agent baseline management.

**Acceptance Criteria:**
- [ ] 6 issue categories covering all solution phases
- [ ] Each issue has Cause and Resolution columns
- [ ] CMM-specific issues (moderation level parsing, agent enumeration) included
- [ ] Links to other documentation files
- [ ] No "ensures compliance" language

### Task 4: Update docs/PREREQUISITES.md

**File:** `content-moderation-monitor/docs/PREREQUISITES.md`

Add MSAL.PS module requirement for evidence export (Phase 4 addition). The file is already populated from Phase 1 — append only.

**Addition:** Under the PowerShell Modules section, add:
```markdown
- **MSAL.PS** (v4.37+) — Required for evidence export authentication (`Install-Module MSAL.PS`)
```

**Acceptance Criteria:**
- [ ] MSAL.PS requirement added to PowerShell Modules section
- [ ] Existing content preserved
- [ ] No duplicate entries

### Task 5: Update README.md

**File:** `content-moderation-monitor/README.md`

Update to reflect v1.0.0 completion with Phase 4 evidence export features.

**Changes:**
1. Update status badge/text from "v0.3.0" to "v1.0.0"
2. Add evidence export to Features list:
   - SHA-256 integrity-hashed compliance evidence export
   - Per-agent moderation evidence with regulatory metadata
3. Add Quick Start steps 5-6:
   - Step 5: Export compliance evidence (`Export-ContentModerationEvidence.ps1`)
   - Step 6: Verify evidence integrity (`Test-EvidenceIntegrity.ps1`)
4. Update Solution Components tree to include evidence export scripts
5. Add EVIDENCE_EXPORT.md and SCHEMA.md to Documentation links section

**Acceptance Criteria:**
- [ ] Version reflects v1.0.0
- [ ] Evidence export features listed
- [ ] Quick Start includes export and verification steps
- [ ] Solution components tree includes new scripts
- [ ] Documentation section links include SCHEMA.md and EVIDENCE_EXPORT.md

### Task 6: Update CHANGELOG.md

**File:** `content-moderation-monitor/CHANGELOG.md`

Add [1.0.0] release entry at the top of the changelog (above existing [0.3.0] entry).

**Content:**
```markdown
## [1.0.0] - 2026-02-10

### Added — Phase 4: Evidence Export & Framework Integration
- `Export-ContentModerationEvidence.ps1` — SHA-256 integrity-hashed compliance evidence export
- `Get-CMMValidationResults.ps1` — Dataverse query helper for validation history and violations
- `Test-EvidenceIntegrity.ps1` — Evidence integrity verification utility
- Control 1.8 tip admonition linking to Content Moderation Governance Monitor
- solutions-index.md catalog entry with components, regulatory alignment, and repository link
- `docs/SCHEMA.md` — Complete Dataverse schema reference
- `docs/EVIDENCE_EXPORT.md` — Step-by-step evidence export guide
- `docs/TROUBLESHOOTING.md` — Comprehensive troubleshooting guide covering all solution components
- Updated `docs/PREREQUISITES.md` with MSAL.PS requirement for evidence export

### Changed
- README.md updated to v1.0.0 with evidence export features, Quick Start steps, and solution components
```

**Acceptance Criteria:**
- [ ] [1.0.0] entry exists at top of changelog
- [ ] All Phase 4 deliverables listed (scripts, framework integration, docs)
- [ ] Date is current
- [ ] Follows existing changelog format

## Verification

1. All 6 documentation files exist with substantive content (not stubs)
2. SCHEMA.md documents all 3 tables, option sets, env vars, connection refs
3. EVIDENCE_EXPORT.md covers all export modes and verification methods
4. TROUBLESHOOTING.md covers 6 issue categories
5. README.md reflects v1.0.0 with evidence export features
6. CHANGELOG.md has [1.0.0] release entry
7. No "ensures compliance" or "guarantees" language in any file

## Success Criteria

- Complete documentation suite enables an administrator to deploy, configure, operate, export evidence, and troubleshoot the CMM solution without external assistance
- All cross-references between documentation files are correct (SCHEMA.md ↔ EVIDENCE_EXPORT.md ↔ TROUBLESHOOTING.md ↔ README.md)
- v1.0.0 status is consistently reflected across README.md and CHANGELOG.md

## Output

After completion, create `.planning/phases/04-evidence-export-framework-integration/04-CMM-03-SUMMARY.md`

Git operations: Commit to FSI-AgentGov-Solutions repository.
