---
phase: 04-evidence-export-framework-integration
plan: AAM-03
title: "Documentation suite (SCHEMA.md, EVIDENCE_EXPORT.md, TROUBLESHOOTING.md, README update, CHANGELOG)"
type: execute
wave: 2
depends_on: ["04-AAM-01", "04-AAM-02"]
files_modified:
  - FSI-AgentGov-Solutions/agent-access-monitor/docs/SCHEMA.md
  - FSI-AgentGov-Solutions/agent-access-monitor/docs/EVIDENCE_EXPORT.md
  - FSI-AgentGov-Solutions/agent-access-monitor/docs/TROUBLESHOOTING.md
  - FSI-AgentGov-Solutions/agent-access-monitor/README.md
  - FSI-AgentGov-Solutions/agent-access-monitor/CHANGELOG.md
autonomous: true

must_haves:
  truths:
    - "SCHEMA.md documents all three Dataverse tables (fsi_accessbaselines, fsi_accessvalidationhistory, fsi_accessviolations) with column definitions"
    - "EVIDENCE_EXPORT.md provides step-by-step instructions for evidence export, verification, and scheduled collection"
    - "TROUBLESHOOTING.md covers common deployment, authentication, validation, and evidence export issues"
    - "README.md status reflects v1.0.0 Complete and includes evidence export in Quick Start and Solution Components"
    - "CHANGELOG.md includes [1.0.0] release entry with Phase 4 evidence export additions"
  artifacts:
    - path: "FSI-AgentGov-Solutions/agent-access-monitor/docs/SCHEMA.md"
      provides: "Dataverse schema reference documentation"
      contains: "fsi_accessbaselines"
    - path: "FSI-AgentGov-Solutions/agent-access-monitor/docs/EVIDENCE_EXPORT.md"
      provides: "Evidence export operations guide"
      contains: "Export-AgentAccessEvidence"
    - path: "FSI-AgentGov-Solutions/agent-access-monitor/docs/TROUBLESHOOTING.md"
      provides: "Troubleshooting guide for operators"
      contains: "Common Issues"
    - path: "FSI-AgentGov-Solutions/agent-access-monitor/README.md"
      provides: "Updated README with v1.0.0 status and Phase 4 content"
      contains: "Export-AgentAccessEvidence"
    - path: "FSI-AgentGov-Solutions/agent-access-monitor/CHANGELOG.md"
      provides: "v1.0.0 release notes"
      contains: "[1.0.0]"
  key_links:
    - from: "README.md Quick Start"
      to: "Export-AgentAccessEvidence.ps1"
      via: "Step 5 script reference"
      pattern: "Export-AgentAccessEvidence"
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
---

# Plan 04-AAM-03: Documentation Suite

## Goal

Create the complete documentation suite for the Agent Access Governance Monitor solution and update the README/CHANGELOG to reflect v1.0.0 completion. This gives administrators all the reference material needed to deploy, operate, and troubleshoot the solution.

## Tasks

### Task 1: Create docs/SCHEMA.md (Dataverse schema reference)

**File:** `agent-access-monitor/docs/SCHEMA.md`

Document all Dataverse tables, columns, option sets, and relationships used by the AAM solution. Follow the pattern established by the ACV solution's schema documentation.

**Structure:**
```markdown
# Dataverse Schema Reference

## Overview
Brief description: 3 tables, shared option sets, environment variables.

## Tables

### fsi_accessbaselines
Purpose, all columns with type/description, relationships.

### fsi_accessvalidationhistory
Purpose, all columns with type/description, immutability note.

### fsi_accessviolations
Purpose, all columns with type/description, relationships.

## Option Sets

### fsi_acv_zone (shared)
Values: 1 (Personal Productivity), 2 (Team Collaboration), 3 (Enterprise Managed)

### fsi_acv_severity (shared)
Values: Critical, High, Warning, Info

## Environment Variables

Table of all 6 fsi_AAM_* variables with schema name, type, default, purpose.

## Connection References

Table of fsi_cr_* connection references with connector and purpose.

## Entity Relationship Diagram
ASCII diagram showing table relationships.
```

Keep under 120 lines. Focus on what administrators need to know.

**Acceptance Criteria:**
- [ ] All three tables documented with column definitions
- [ ] Option sets and environment variables documented
- [ ] Connection references listed
- [ ] No "ensures compliance" language

### Task 2: Create docs/EVIDENCE_EXPORT.md (evidence export guide)

**File:** `agent-access-monitor/docs/EVIDENCE_EXPORT.md`

Step-by-step guide for evidence export operations. Follow the ACV evidence-export-guide.md pattern adapted for AAM.

**Structure:**
```markdown
# Evidence Export Guide

## Overview
Evidence export produces JSON files with SHA-256 integrity hashes for compliance examinations.

## Prerequisites
- Dataverse deployed with validation history records
- PowerShell 7.0+
- MSAL.PS module

## Export Compliance Evidence

### Interactive Mode
PowerShell example with -Interactive flag.

### Service Principal Mode
PowerShell example with -CertificateThumbprint and -ClientId.

### Export with Zone Filter
Example filtering to Zone 3 only.

### Export with Baseline Inclusion
Example with -IncludeBaselines flag.

### Parameters Reference
Table of all parameters with descriptions and defaults.

### Output Files
Description of JSON structure and .sha256 format.

## Verify Evidence Integrity

### Single File
Test-EvidenceIntegrity.ps1 example.

### Batch Verification
Get-ChildItem pipeline example.

### Cross-Platform
sha256sum -c example for Linux/macOS.

## Evidence Schema
JSON schema with field descriptions for metadata, summary, validations, violations, baselines.

## Recommended Export Schedule
- Monthly for ongoing compliance
- Quarterly for regulatory examinations
- On-demand for investigations

## Troubleshooting
Table of common evidence export issues (empty exports, auth failures, hash mismatches).
```

Keep under 150 lines. Focus on actionable steps.

**Acceptance Criteria:**
- [ ] Covers interactive and service principal export modes
- [ ] Zone filtering and baseline inclusion documented
- [ ] Verification section with single, batch, and cross-platform examples
- [ ] JSON schema reference included
- [ ] No "ensures compliance" language

### Task 3: Create docs/TROUBLESHOOTING.md

**File:** `agent-access-monitor/docs/TROUBLESHOOTING.md`

Common issues guide covering deployment, authentication, validation, and evidence export troubleshooting.

**Structure:**
```markdown
# Troubleshooting Guide

## Deployment Issues
| Issue | Cause | Resolution |
Tables not created, env vars missing, connection ref errors, deploy.py failures.

## Authentication Issues
MSAL errors, certificate issues, insufficient permissions, interactive auth failures.

## Validation Issues
No environments returned, zone classification errors, false positive violations, grace period not applied.

## Drift Detection Issues
Baseline not found, validation history not persisting, flow trigger failures.

## Evidence Export Issues
Empty exports, truncated JSON (-Depth), hash mismatches, output directory permissions.

## Power Automate Flow Issues
Flow not triggering, adaptive card not sent, Dataverse write failures, connection auth expired.

## Related Documentation
Links to PREREQUISITES.md, SCHEMA.md, EVIDENCE_EXPORT.md, FLOW_SETUP.md.
```

Keep under 120 lines. Focus on resolution steps.

**Acceptance Criteria:**
- [ ] Covers 6 issue categories
- [ ] Each issue has Cause and Resolution columns
- [ ] Links to related documentation
- [ ] No "ensures compliance" language

### Task 4: Update README.md with Phase 4 content and completed status

**File:** `agent-access-monitor/README.md`

**Changes:**
1. **Add evidence export to Features table:**
   Add rows for SHA-256 evidence export and hash verification.

2. **Add Step 5 to Quick Start:**
   ```powershell
   # 5. Export compliance evidence
   ./scripts/Export-AgentAccessEvidence.ps1 -DataverseUrl https://org.crm.dynamics.com `
       -TenantId <your-tenant-id> -OutputDirectory ./exports -Interactive

   # 6. Verify evidence integrity
   ./scripts/Test-EvidenceIntegrity.ps1 -EvidenceFilePath ./exports/aam-evidence-All-20250717-120000.json
   ```

3. **Update Solution Components tree:**
   Add the three new scripts and three new docs to the tree:
   ```
   ├── scripts/
   │   ├── Export-AgentAccessEvidence.ps1     # Evidence export
   │   ├── Test-EvidenceIntegrity.ps1         # Hash verification
   │   └── private/
   │       ├── Get-AAMValidationResults.ps1   # Evidence query helper
   ```
   ```
   └── docs/
       ├── SCHEMA.md
       ├── EVIDENCE_EXPORT.md
       └── TROUBLESHOOTING.md
   ```

4. **Update Related Controls table:**
   Add note about evidence export and regulatory examination support.

**Acceptance Criteria:**
- [ ] Features table includes evidence export rows
- [ ] Quick Start includes export and verify steps
- [ ] Solution Components tree shows all scripts and docs
- [ ] No "ensures compliance" language

### Task 5: Update CHANGELOG.md with v1.0.0 release

**File:** `agent-access-monitor/CHANGELOG.md`

Add new `[1.0.0]` release entry at the top (before [0.3.0]):

```markdown
## [1.0.0] - {execution-date}

### Added - Phase 4: Evidence Export & Framework Integration

#### Evidence Export
- **Export-AgentAccessEvidence.ps1** — Main evidence export script
  - Zone-based filtering (All/1/2/3)
  - Date range support with -FromDate and -ToDate
  - Optional baseline inclusion with -IncludeBaselines
  - JSON output with -Depth 10 (prevents nested object truncation)
  - SHA-256 companion hash files in standard format
  - Interactive and certificate-based authentication modes

- **Get-AAMValidationResults.ps1** (private) — Dataverse query helper
  - Queries fsi_accessvalidationhistory and fsi_accessviolations
  - OData filtering with pagination support

- **Test-EvidenceIntegrity.ps1** — SHA-256 hash verification utility
  - Single file and batch verification modes
  - Cross-platform hash format compatibility

#### Documentation
- **SCHEMA.md** — Dataverse schema reference (3 tables, option sets, env vars)
- **EVIDENCE_EXPORT.md** — Evidence export operations guide
- **TROUBLESHOOTING.md** — Common issues and resolutions

#### Framework Integration
- Control 3.8 tip admonition linking to solution
- solutions-index.md catalog entry with regulatory alignment
```

**Acceptance Criteria:**
- [ ] [1.0.0] entry exists with correct date
- [ ] Phase 4 additions grouped by Evidence Export, Documentation, Framework Integration
- [ ] All 3 new scripts listed with descriptions

## Verification

All documentation files exist and README/CHANGELOG are updated:
1. `docs/SCHEMA.md` — Dataverse schema reference
2. `docs/EVIDENCE_EXPORT.md` — Evidence export guide
3. `docs/TROUBLESHOOTING.md` — Troubleshooting guide
4. `README.md` — Updated with v1.0.0 and Phase 4 content
5. `CHANGELOG.md` — v1.0.0 release entry

## Success Criteria

- SCHEMA.md documents all 3 tables, option sets, environment variables, connection references
- EVIDENCE_EXPORT.md provides actionable export and verification instructions
- TROUBLESHOOTING.md covers 6 issue categories with resolutions
- README.md features table, Quick Start, and Solution Components reflect Phase 4
- CHANGELOG.md has [1.0.0] release entry with all Phase 4 additions
- All documentation follows FSI language rules (no "ensures compliance")

## Output

After completion, create `.planning/phases/04-evidence-export-framework-integration/04-AAM-03-SUMMARY.md`

Git operations: Commit to FSI-AgentGov-Solutions repository.
