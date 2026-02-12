# Roadmap: MIME Type Restrictions for File Uploads (v18)

## Overview

Add Control 1.25 (MIME Type Restrictions for File Uploads) to the framework with a companion solution — PowerShell module for zone-based MIME configuration management, Dataverse plugin for server-side magic bytes validation (Zone 3), Purview DLP policy template, Sentinel monitoring queries/alerts, and exception management templates. Prevents malicious or high-risk file types from being uploaded to Power Platform environments, Dataverse, or accessed by Copilot Studio agents.

**Source:** v18 requirements (16 requirements across 6 categories). Control ID reassigned from 1.20→1.25 (1.20 is already Network Isolation and Private Connectivity). Framework goes from 62 to 63 controls.

**Execution model:** 5 phases. Phases 1–4 are independent (parallel-eligible). Phase 5 depends on all. Within each phase, plans target non-overlapping file sets for parallel execution.

## Phases

- [x] **Phase 1: Control Documentation & Playbooks** — Control 1.25 document (10-section template), 4 implementation playbooks, screenshot specification
- [ ] **Phase 2: PowerShell Module & Zone Templates** — `FsiMimeControl.psm1` with 3 cmdlets, zone template JSON files, Pester test suite
- [ ] **Phase 3: DLP Policy & Sentinel Monitoring** — Purview DLP policy template, Sentinel KQL queries, analytics alert rule ARM template
- [ ] **Phase 4: Dataverse Plugin & Exception Management** — `ValidateMimeTypePlugin.cs` with magic bytes validation, plugin deployment scripts, exception register template, validation script
- [ ] **Phase 5: Framework Integration & Validation** — CONTROL-INDEX, mkdocs.yml, "63 controls" updates, solutions-index entry, full build validation

## Phase Details

### Phase 1: Control Documentation & Playbooks
**Goal:** Create Control 1.25 documentation following the 10-section template, 4 implementation playbooks, and screenshot specification
**Depends on:** Nothing (independent)
**Requirements:** CTL-01, CTL-02, CTL-03
**Success Criteria:**
  1. `docs/controls/pillar-1-security/1.25-mime-type-restrictions.md` follows 10-section template with header/footer metadata, zone-specific requirements (Zone 1 baseline/Zone 2 recommended/Zone 3 regulated), regulatory references (FINRA 4511/3110, SEC 17a-4, GLBA 501(b), OCC 2011-12)
  2. 4 playbooks in `docs/playbooks/control-implementations/1.25/` — portal-walkthrough (PPAC Privacy + Security settings), powershell-setup (FsiMimeControl module usage), verification-testing (compliance checks per zone), troubleshooting (common pitfalls)
  3. `docs/images/1.25/EXPECTED.md` lists required screenshots — PPAC blocked extensions field, PPAC blocked MIME types field, PPAC allowed MIME types field, compliance test output
  4. All documentation uses FSI-safe language (hedged, no overclaims)
**Plans:** 2 (A = control document, B = playbooks + EXPECTED.md)

### Phase 2: PowerShell Module & Zone Templates
**Goal:** Build FsiMimeControl PowerShell module with zone-based MIME configuration management via Dataverse Web API
**Depends on:** Nothing (independent)
**Requirements:** MOD-01, MOD-02, MOD-03
**Success Criteria:**
  1. `FsiMimeControl.psm1` exports 3 cmdlets — `Get-FsiMimeConfig` (read MIME configuration from Dataverse Web API), `Set-FsiMimeConfig` (apply zone template or custom configuration with `-WhatIf` support), `Test-FsiMimeCompliance` (validate environment against zone requirements with pass/fail/warning output)
  2. Zone template JSON files (zone1.json, zone2.json, zone3.json) — Zone 1: Microsoft default blocked extensions only; Zone 2: blocked extensions + blocked MIME types + explicit allowlist; Zone 3: comprehensive blocklist + strict allowlist + `requireServerSideValidation`/`requireDlpIntegration`/`requireSentinelMonitoring` flags
  3. Pester test suite (`FsiMimeControl.Tests.ps1`) with unit tests for all 3 cmdlets, mock Dataverse Web API responses, zone template loading validation, compliance check logic
  4. Module follows conventions: `#Requires -Version 7.0`, `ErrorAction Stop`, `-OutputFormat`/`-OutputPath` parameters
**Plans:** 2 (A = module core + zone templates, B = Pester tests)

### Phase 3: DLP Policy & Sentinel Monitoring
**Goal:** Create Purview DLP policy template and Sentinel monitoring queries/alerts for MIME-based upload blocking
**Depends on:** Nothing (independent)
**Requirements:** MON-01, MON-02, MON-03
**Success Criteria:**
  1. `dlp-policy-template.json` blocks executable file patterns (*.exe, *.bat, *.cmd, *.ps1, *.vbs, *.js, *.jar, *.dll, *.msi, *.scr, *.hta) in Power Platform locations, generates incident reports, configurable environment filter
  2. Sentinel KQL queries — `query-mime-blocks.kql` (blocked upload attempts with file extension/user/environment aggregation over 30 days), `query-exception-usage.kql` (unusual file type uploads correlated with exception register over 90 days)
  3. Sentinel analytics alert rule ARM template (`high-volume-blocks.json`) — scheduled rule detecting >10 blocked upload attempts per user per hour, MITRE ATT&CK mapping (T1566, T1204), entity mapping for Account, incident grouping by user
**Plans:** 2 (A = DLP policy template + KQL queries, B = alert rule ARM template)

### Phase 4: Dataverse Plugin & Exception Management
**Goal:** Build Zone 3 Dataverse plugin for server-side MIME validation and create exception management templates
**Depends on:** Nothing (independent — zone templates from Phase 2 are referenced but not required at build time)
**Requirements:** PLG-01, PLG-02, EXC-01, EXC-02
**Success Criteria:**
  1. `ValidateMimeTypePlugin.cs` with config-driven magic bytes validation — PE/ELF/Mach-O executable header detection, OpenXML content type validation, configurable enforcement mode (Block vs LogOnly), correlation ID tracing, max file size guard (10MB default)
  2. Plugin deployment scripts — `register-plugin.ps1` for Plugin Registration Tool automation, `test-plugin.ps1` for integration testing, `MimeConfig.json` configuration with Zone 3 default allowlist
  3. Exception register template (`mime-type-exceptions.csv`) with required columns (Requestor, Department, Date, MimeType, Extensions, BusinessJustification, Alternatives, RiskAssessment, MitigatingControls, Approver, ApprovalDate, ReviewDate, Status)
  4. Exception validation script (`validate-exceptions.ps1`) comparing allowed MIME types against register; exception request template (`exception-template.md`) with required fields
**Plans:** 2 (A = plugin + deployment scripts, B = exception register + validation script + request template)

### Phase 5: Framework Integration & Validation
**Goal:** Update framework references, solutions catalog, and validate all artifacts against build and verification scripts
**Depends on:** Phases 1–4 (all control documentation and solution artifacts must exist before framework references them)
**Requirements:** FRM-01, FRM-02, FRM-03
**Success Criteria:**
  1. CONTROL-INDEX.md includes Control 1.25 row; mkdocs.yml navigation updated under Pillar 1 Security; all "62 controls" references updated to "63 controls" across copilot-instructions, AGENTS.md, README, getting-started docs
  2. `solutions-index.md` includes MIME Type Restrictions entry with status, components, regulatory alignment, control mappings, cross-references from related controls (1.5, 1.10, 1.11, 1.13, 1.14, 3.3, 3.7, 4.3)
  3. `mkdocs build --strict` passes, `verify_controls.py` 63/63, `verify_language_rules.py` 0 violations
**Plans:** 2 (A = CONTROL-INDEX + mkdocs.yml + "63 controls" updates + solutions-index entry, B = build validation + cross-reference verification)

## Progress

| Phase | Plans Complete | Status |
|-------|---------------|--------|
| 1. Control Documentation & Playbooks | 2/2 | Complete |
| 2. PowerShell Module & Zone Templates | 2/2 | Complete |
| 3. DLP Policy & Sentinel Monitoring | 0/2 | Not Started |
| 4. Dataverse Plugin & Exception Management | 0/2 | Not Started |
| 5. Framework Integration & Validation | 0/2 | Not Started |

## Parallel Execution Guide

Phases 1–4 are **independent** — no shared file targets, parallel-eligible. Phase 5 depends on 1–4.

```
Phase 1 (CTL) ──┐
Phase 2 (MOD) ──┤
Phase 3 (MON) ──┼── Phase 5 (FRM)
Phase 4 (PLG/EXC)┘
```

Within each phase, plans target non-overlapping file sets:

| Phase | Plan A Files | Plan B Files | Parallel? |
|-------|-------------|-------------|-----------|
| 1 | `docs/controls/pillar-1-security/1.25-mime-type-restrictions.md` | `docs/playbooks/control-implementations/1.25/*`, `docs/images/1.25/EXPECTED.md` | Yes |
| 2 | `FsiMimeControl.psm1`, `zone1.json`, `zone2.json`, `zone3.json` | `FsiMimeControl.Tests.ps1` | Yes |
| 3 | `dlp-policy-template.json`, `query-mime-blocks.kql`, `query-exception-usage.kql` | `high-volume-blocks.json` | Yes |
| 4 | `ValidateMimeTypePlugin.cs`, `register-plugin.ps1`, `test-plugin.ps1`, `MimeConfig.json` | `mime-type-exceptions.csv`, `validate-exceptions.ps1`, `exception-template.md` | Yes |
| 5 | `CONTROL-INDEX.md`, `mkdocs.yml`, framework docs, `solutions-index.md` | Build validation (read-only) | Yes |

## File Manifest

### Created (new files)

| Phase | File | Purpose |
|-------|------|---------|
| 1 | `docs/controls/pillar-1-security/1.25-mime-type-restrictions.md` | Control 1.25 documentation (10-section template) |
| 1 | `docs/playbooks/control-implementations/1.25/portal-walkthrough.md` | PPAC configuration walkthrough |
| 1 | `docs/playbooks/control-implementations/1.25/powershell-setup.md` | FsiMimeControl module usage guide |
| 1 | `docs/playbooks/control-implementations/1.25/verification-testing.md` | Zone compliance verification procedures |
| 1 | `docs/playbooks/control-implementations/1.25/troubleshooting.md` | Common pitfalls and resolution |
| 1 | `docs/images/1.25/EXPECTED.md` | Screenshot specification |
| 2 | `scripts/governance/FsiMimeControl.psm1` | PowerShell module (3 cmdlets) |
| 2 | `scripts/governance/mime-templates/zone1.json` | Zone 1 MIME template (baseline) |
| 2 | `scripts/governance/mime-templates/zone2.json` | Zone 2 MIME template (recommended) |
| 2 | `scripts/governance/mime-templates/zone3.json` | Zone 3 MIME template (regulated) |
| 2 | `scripts/governance/FsiMimeControl.Tests.ps1` | Pester test suite |
| 3 | `src/dlp-policy-template.json` | Purview DLP policy template |
| 3 | `src/query-mime-blocks.kql` | Sentinel KQL — blocked upload attempts |
| 3 | `src/query-exception-usage.kql` | Sentinel KQL — exception usage analysis |
| 3 | `src/high-volume-blocks.json` | Sentinel analytics alert rule ARM template |
| 4 | `src/ValidateMimeTypePlugin.cs` | Dataverse plugin (Zone 3 magic bytes validation) |
| 4 | `scripts/governance/register-plugin.ps1` | Plugin Registration Tool automation |
| 4 | `scripts/governance/test-plugin.ps1` | Plugin integration testing |
| 4 | `src/MimeConfig.json` | Plugin configuration (Zone 3 allowlist) |
| 4 | `scripts/governance/mime-type-exceptions.csv` | Exception register template |
| 4 | `scripts/governance/validate-exceptions.ps1` | Exception register validation script |
| 4 | `docs/templates/exception-template.md` | Exception request form template |

### Modified (existing files)

| Phase | File | Change |
|-------|------|--------|
| 5 | `docs/controls/CONTROL-INDEX.md` | Add Control 1.25 row |
| 5 | `mkdocs.yml` | Add 1.25 nav entry under Pillar 1 + playbook nav entries |
| 5 | `.github/copilot-instructions.md` | Update "62 controls" → "63 controls" |
| 5 | `AGENTS.md` | Update "62 controls" → "63 controls" |
| 5 | `README.md` | Update "62 controls" → "63 controls" |
| 5 | `docs/getting-started/*.md` | Update control count references if present |
| 5 | `docs/reference/solutions-index.md` | Add MIME Type Restrictions catalog entry |

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| CTL-01 | 1 | 01-01 | Control 1.25 document (10-section template) |
| CTL-02 | 1 | 01-02 | 4 implementation playbooks |
| CTL-03 | 1 | 01-02 | Screenshot specification (EXPECTED.md) |
| MOD-01 | 2 | 02-01 | FsiMimeControl.psm1 with 3 cmdlets |
| MOD-02 | 2 | 02-01 | Zone template JSON files (zone1/2/3) |
| MOD-03 | 2 | 02-02 | Pester test suite |
| MON-01 | 3 | 03-01 | DLP policy template |
| MON-02 | 3 | 03-01 | Sentinel KQL queries (2 queries) |
| MON-03 | 3 | 03-02 | Sentinel analytics alert rule ARM template |
| PLG-01 | 4 | 04-01 | ValidateMimeTypePlugin.cs (magic bytes validation) |
| PLG-02 | 4 | 04-01 | Plugin deployment + test scripts |
| EXC-01 | 4 | 04-02 | Exception register template + validation script |
| EXC-02 | 4 | 04-02 | Exception request template |
| FRM-01 | 5 | 05-01 | CONTROL-INDEX + mkdocs + "63 controls" updates |
| FRM-02 | 5 | 05-01 | Solutions-index catalog entry |
| FRM-03 | 5 | 05-02 | Build validation (mkdocs + verify scripts) |

**Total: 16/16 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-12*
*Depth: comprehensive*
*Phases: 5 (documentation → module → monitoring → plugin/exceptions → framework integration)*
