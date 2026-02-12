# Requirements: v18 — MIME Type Restrictions for File Uploads

## Overview

Add a new Control 1.25 (MIME Type Restrictions for File Uploads) to the framework and build the companion solution in FSI-AgentGov-Solutions. Prevents malicious or high-risk file types from being uploaded to Power Platform environments, Dataverse, or accessed by Copilot Studio agents through zone-based MIME configuration, server-side magic bytes validation, Purview DLP integration, and Sentinel monitoring.

**Source:** [Control 1.20 MIME Type Restrictions - Production Ready.pdf](../maintainers-local/Control%201.20%20MIME%20Type%20Restrictions%20-%20Production%20Ready.pdf) — production-ready solution spec authored 2026-02-12. Reassigned from 1.20 → **1.25** (1.20 is already Network Isolation and Private Connectivity).

**Accuracy notes from research:**
- Spec uses Control ID 1.20 — reassigned to 1.25 (next available in Pillar 1)
- Spec language violates FSI rules ("ensures compliance") — must be rewritten with hedged language
- Framework control count changes from 62 to 63
- `PowerPlatformAdministratorActivity` KQL table name needs verification (may be `PowerPlatformAdminActivity`)
- Complementary to File Upload Security (v8, per-agent toggle) and Hardening Baseline items 28-29 (basic MIME check)

## Requirement Categories

| Code | Category | Count |
|------|----------|-------|
| CTL | Control Documentation | 3 |
| MOD | PowerShell Module & Zone Templates | 3 |
| PLG | Dataverse Plugin (Zone 3) | 2 |
| MON | DLP Policy + Sentinel Monitoring | 3 |
| EXC | Exception Management | 2 |
| FRM | Framework Integration | 3 |
| **Total** | | **16** |

## CTL — Control Documentation

- [ ] **CTL-01:** Create Control 1.25 documentation in `docs/controls/pillar-1-security/1.25-mime-type-restrictions.md` following 10-section template — header metadata, objective, FSI rationale, control description (Zone 1 baseline/Zone 2 recommended/Zone 3 regulated statements), key configuration points, zone-specific requirements table, roles & responsibilities, related controls, implementation playbooks, verification criteria, additional resources, footer metadata
- [ ] **CTL-02:** Create 4 playbooks in `docs/playbooks/control-implementations/1.25/` — portal-walkthrough (PPAC Privacy + Security settings configuration), powershell-setup (FsiMimeControl module usage), verification-testing (compliance checks per zone), troubleshooting (common pitfalls from spec)
- [ ] **CTL-03:** Create `docs/images/1.25/EXPECTED.md` screenshot specification — PPAC blocked extensions field, PPAC blocked MIME types field, PPAC allowed MIME types field, compliance test output

## MOD — PowerShell Module & Zone Templates

- [ ] **MOD-01:** Create `FsiMimeControl.psm1` PowerShell module with 3 cmdlets — `Get-FsiMimeConfig` (read current MIME configuration from Dataverse Web API), `Set-FsiMimeConfig` (apply zone template or custom configuration with `-WhatIf` support), `Test-FsiMimeCompliance` (validate environment against zone requirements with pass/fail/warning output)
- [ ] **MOD-02:** Create zone template JSON files (zone1.json, zone2.json, zone3.json) — Zone 1: Microsoft default blocked extensions only; Zone 2: blocked extensions + blocked MIME types + explicit allowlist; Zone 3: comprehensive blocklist + strict allowlist + `requireServerSideValidation`/`requireDlpIntegration`/`requireSentinelMonitoring` flags
- [ ] **MOD-03:** Create Pester test suite (`FsiMimeControl.Tests.ps1`) — unit tests for Get/Set/Test cmdlets, mock Dataverse Web API responses, validate zone template loading, test compliance check logic

## PLG — Dataverse Plugin (Zone 3)

- [ ] **PLG-01:** Create `ValidateMimeTypePlugin.cs` with config-driven magic bytes validation — PE/ELF/Mach-O executable header detection, OpenXML content type validation (DOCX/XLSX/PPTX), configurable enforcement mode (Block vs LogOnly), correlation ID tracing, max file size guard (10MB default)
- [ ] **PLG-02:** Create plugin deployment and test scripts — `register-plugin.ps1` for Plugin Registration Tool automation, `test-plugin.ps1` for integration testing with malicious file samples, `MimeConfig.json` configuration file with default Zone 3 allowlist

## MON — DLP Policy + Sentinel Monitoring

- [ ] **MON-01:** Create Purview DLP policy template (`dlp-policy-template.json`) — blocks executable file patterns (*.exe, *.bat, *.cmd, *.ps1, *.vbs, *.js, *.jar, *.dll, *.msi, *.scr, *.hta) in Power Platform locations, generates incident reports to security operations, configurable environment filter
- [ ] **MON-02:** Create Sentinel KQL queries — `query-mime-blocks.kql` (blocked upload attempts with file extension/user/environment aggregation over 30 days), `query-exception-usage.kql` (unusual file type uploads correlated with exception register over 90 days)
- [ ] **MON-03:** Create Sentinel analytics alert rule template (`high-volume-blocks.json`) — ARM template for scheduled rule detecting >10 blocked upload attempts per user per hour, MITRE ATT&CK mapping (T1566, T1204), entity mapping for Account, incident grouping by user

## EXC — Exception Management

- [ ] **EXC-01:** Create exception register template and validation script — `mime-type-exceptions.csv` with columns (Requestor, Department, Date, MimeType, Extensions, BusinessJustification, Alternatives, RiskAssessment, MitigatingControls, Approver, ApprovalDate, ReviewDate, Status), `validate-exceptions.ps1` to compare allowed MIME types against register
- [ ] **EXC-02:** Create exception request template (`exception-template.md`) — markdown form with required fields for business justification, alternatives considered, risk assessment, mitigating controls, approval chain

## FRM — Framework Integration

- [ ] **FRM-01:** Update framework references — CONTROL-INDEX.md (add 1.25 row), mkdocs.yml navigation (add under Pillar 1), update "62 controls" references to "63 controls" across framework docs (copilot-instructions, AGENTS.md, README, getting-started)
- [ ] **FRM-02:** Add solutions-index.md catalog entry — overview row (MIME Type Restrictions, v1.0.0, Completed), detail section (components, regulatory alignment, version history), cross-reference from related controls (1.5, 1.10, 1.11, 1.13, 1.14, 3.3, 3.7, 4.3)
- [ ] **FRM-03:** All validations pass — `mkdocs build --strict`, `verify_controls.py` 63/63, `verify_language_rules.py` 0 violations

## Traceability Matrix

| Requirement | Spec Section | Controls | Regulatory |
|-------------|-------------|----------|------------|
| CTL-01, CTL-02, CTL-03 | Control Statement, Overview | 1.25 (new) | FINRA 4511/3110, SEC 17a-4, GLBA 501(b), OCC 2011-12, SEC 33-11216 |
| MOD-01, MOD-02, MOD-03 | PowerShell Module, Zone Templates | 1.25 | FINRA 4511, SEC 17a-4 |
| PLG-01, PLG-02 | Dataverse Plugin (Zone 3) | 1.25 | SEC 17a-4, GLBA 501(b), OCC 2011-12 |
| MON-01, MON-02, MON-03 | Purview DLP, Sentinel Monitoring | 1.25, 1.5, 1.10 | FINRA 3110, SEC 33-11216, SOX 302/404 |
| EXC-01, EXC-02 | Exception Management | 1.25 | FINRA 3110, SOX 302 |
| FRM-01, FRM-02, FRM-03 | Framework Integration | 1.25, 1.5, 1.10, 1.11, 1.13, 1.14, 3.3, 3.7, 4.3 | All applicable |

## Out of Scope

| Item | Reason |
|------|--------|
| Renaming existing Control 1.20 | 1.20 remains Network Isolation; new control is 1.25 |
| Real-time file scanning | Batch/scheduled validation sufficient per framework constraints |
| Power Automate flow orchestration | PowerShell module is standalone; flow wrapping deferred |
| Managed identity / production-grade auth | Lab-grade implementation consistent with v4-v17 |
| GitHub Actions CI for Pester tests | Optional enhancement noted in spec; deferred |
| Automatic remediation of MIME settings | Detection/validation only — remediation requires approval workflow |

## Priority Summary

- **P1 (10):** CTL-01, CTL-02, MOD-01, MOD-02, MON-01, MON-02, MON-03, FRM-01, FRM-02, FRM-03
- **P2 (6):** CTL-03, MOD-03, PLG-01, PLG-02, EXC-01, EXC-02

---
*Requirements defined: 2026-02-12*
*Milestone: v18 — MIME Type Restrictions for File Uploads*
