# Roadmap: Inactivity Timeout Enforcement (v19)

## Overview

Add Control 2.22 (Inactivity Timeout Enforcement) to the Management Pillar with a companion solution — automated validation and enforcement of Power Platform user inactivity timeout settings across multiple environments with zone-based policy-driven maximum duration requirements, Dataverse persistence, Cloud Flow detection, and PowerShell remediation.

**Source:** v19 requirements (14 requirements across 5 categories). Control ID 2.22 (next available in Pillar 2). Framework goes from 63 to 64 controls; Pillar 2 from 21 to 22 controls; playbook count from 252 to 256.

**Execution model:** 5 phases. Phases 1–4 are independent (parallel-eligible). Phase 5 depends on all. Within each phase, plans target non-overlapping file sets for parallel execution.

## Phases

- [x] **Phase 1: Control Documentation & Playbooks** — Control 2.22 document (10-section template), 4 implementation playbooks, screenshot specification
- [x] **Phase 2: Dataverse Data Model** — 3 table schemas (environmentpolicy, compliance, errorlog), environment variables, connection references
- [ ] **Phase 3: Cloud Flow & Validation Logic** — Detection flow template with BAP Admin API integration, policy lookup, per-environment compliance evaluation, guarded notification
- [ ] **Phase 4: PowerShell Remediation** — `Set-InactivityTimeout.ps1` with BAP Admin API PATCH, remediation audit records, validation test script
- [ ] **Phase 5: Framework Integration & Validation** — CONTROL-INDEX, mkdocs.yml, "64 controls" updates, solutions-index entry, full build validation

## Phase Details

### Phase 1: Control Documentation & Playbooks
**Goal:** Create Control 2.22 documentation following the 10-section template, 4 implementation playbooks, and screenshot specification
**Depends on:** Nothing (independent)
**Requirements:** CTL-01, CTL-02, CTL-03
**Success Criteria:**
  1. `docs/controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md` follows 10-section template with header/footer metadata, zone-specific requirements (Zone 1 optional/Zone 2 required ≤120 min/Zone 3 required ≤60 min), regulatory references (GLBA 501(b), SOX 302, FINRA 4511, NIST 800-53 AC-11/AC-12)
  2. 4 playbooks in `docs/playbooks/control-implementations/2.22/` — portal-walkthrough (PPAC Privacy + Security settings → inactivity timeout configuration), powershell-setup (Set-InactivityTimeout.ps1 usage with EnvironmentName parameter), verification-testing (Detect-InactivityTimeout-NonCompliance flow output validation, Dataverse compliance records review), troubleshooting (MissingPolicy, 401/403/404/429 errors, BAP API connectivity)
  3. `docs/images/2.22/EXPECTED.md` lists required screenshots — PPAC Environment Settings Privacy + Security page, inactivity timeout toggle and duration field, compliance scan results in Dataverse, notification email sample
  4. All documentation uses FSI-safe language (hedged, no overclaims)
**Plans:** 2 (A = control document, B = playbooks + EXPECTED.md)

### Phase 2: Dataverse Data Model
**Goal:** Create Dataverse table schemas for environment policy, compliance records, and error logging with environment variables and connection references
**Depends on:** Nothing (independent)
**Requirements:** DVM-01, DVM-02, DVM-03
**Success Criteria:**
  1. `fsi_environmentpolicy` table schema — `fsi_environmentid` (Text PK, EnvironmentName), `fsi_environmentdisplayname` (Text), `fsi_zone` (Choice: Zone1/Zone2/Zone3), `fsi_requiredmaxduration` (Whole Number, minutes), `fsi_notes` (Multi-line Text); reuse `fsi_acv_zone` shared option set where compatible
  2. `fsi_inactivitytimeout_compliance` table schema — immutable compliance records (one per environment per scan, never update in place); columns: `fsi_environmentid`, `fsi_environmentname`, `fsi_environmenttype`, `fsi_inactivitytimeoutenabled`, `fsi_timeoutduration`, `fsi_requiredmaxduration`, `fsi_compliancestatus` (Choice: Compliant/Non-Compliant/Unknown), `fsi_lastscandate`, `fsi_notes`; index on `(fsi_environmentid, fsi_lastscandate)`
  3. `fsi_inactivitytimeout_errorlog` table schema — `fsi_environmentid`, `fsi_errortype` (401/403/404/429/MissingPolicy/ParseError), `fsi_errorraw`, `fsi_timestamp`
  4. Environment variables (concurrency limit, notification recipients) and connection references (Dataverse, BAP Admin API) defined
**Plans:** 2 (A = policy + compliance table schemas + environment variables + connection references, B = errorlog table schema + seed data configuration)

### Phase 3: Cloud Flow & Validation Logic
**Goal:** Create the Detect-InactivityTimeout-NonCompliance flow template with BAP Admin API integration, policy-driven compliance evaluation, and guarded notification
**Depends on:** Nothing (independent — flow template references Dataverse schema but does not require it at build time)
**Requirements:** FLW-01, FLW-02, FLW-03
**Success Criteria:**
  1. Flow template enumerates environments via Power Platform for Admins V2, loads `fsi_environmentpolicy` rows, builds lookup keyed by EnvironmentName
  2. Per-environment evaluation with configurable concurrency (default 5) — no policy → Unknown + MissingPolicy error log; BAP API fail → Unknown + error log; timeout disabled → Non-Compliant; duration > required max → Non-Compliant; otherwise → Compliant; persist as new immutable compliance row
  3. Guarded notification — email only when Non-Compliant count > 0 OR Unknown count > 0; includes environment, zone, actual duration, required max, and status; no empty notifications
  4. Service principal auth with scope `https://api.bap.microsoft.com/.default`; scheduled daily at 06:00 UTC
**Plans:** 2 (A = flow template core — enumeration + policy lookup + evaluation logic, B = notification logic + error handling + concurrency configuration)

### Phase 4: PowerShell Remediation
**Goal:** Create Set-InactivityTimeout.ps1 for BAP Admin API PATCH remediation with audit record writing and validation testing
**Depends on:** Nothing (independent — can be coded and tested independently of flow and schema)
**Requirements:** REM-01, REM-02
**Success Criteria:**
  1. `Set-InactivityTimeout.ps1` with mandatory `-EnvironmentName` parameter (canonical Power Platform Environment Name), `-TimeoutDuration` (ValidateRange 5-120, default 120), `-WarningDuration` (ValidateRange 1-30, default 5); PATCH BAP Admin API privacy settings endpoint; `#Requires -Version 7.0`, `SupportsShouldProcess`, `-WhatIf` support
  2. Remediation audit record writing — optionally write records to Dataverse compliance table with action taken, before/after values, and timestamp
  3. Validation test script to confirm PATCH was applied correctly by re-reading the API response
**Plans:** 2 (A = Set-InactivityTimeout.ps1 script, B = remediation audit records + validation test script)

### Phase 5: Framework Integration & Validation
**Goal:** Update framework references, solutions catalog, and validate all artifacts against build and verification scripts
**Depends on:** Phases 1–4 (all control documentation and solution artifacts must exist before framework references them)
**Requirements:** FRM-01, FRM-02, FRM-03
**Success Criteria:**
  1. CONTROL-INDEX.md includes Control 2.22 row; mkdocs.yml navigation updated under Pillar 2 Management after 2.21; all "63 controls" references updated to "64 controls" across copilot-instructions, AGENTS.md, README, getting-started, framework docs; "21 management controls" → "22 management controls"; playbook count "252" → "256"
  2. `solutions-index.md` includes Inactivity Timeout Enforcement entry with status, components, regulatory alignment (GLBA 501(b), SOX 302, FINRA 4511, NIST 800-53 AC-11/AC-12), control mappings; cross-references from related controls (1.23, 3.7, 3.8); hardening baseline item 30 updated from [3.7] to [2.22, 3.7]
  3. `mkdocs build --strict` passes, `verify_controls.py` 64/64, `verify_language_rules.py` 0 violations
**Plans:** 2 (A = CONTROL-INDEX + mkdocs.yml + "64 controls" updates + solutions-index entry, B = build validation + cross-reference verification)

## Progress

| Phase | Plans Complete | Status |
|-------|---------------|--------|
| 1. Control Documentation & Playbooks | 2/2 | Complete |
| 2. Dataverse Data Model | 2/2 | Complete |
| 3. Cloud Flow & Validation Logic | 2/2 | Complete |
| 4. PowerShell Remediation | 0/2 | Not Started |
| 5. Framework Integration & Validation | 0/2 | Not Started |

## Parallel Execution Guide

Phases 1–4 are **independent** — no shared file targets, parallel-eligible. Phase 5 depends on 1–4.

```
Phase 1 (CTL) ──┐
Phase 2 (DVM) ──┤
Phase 3 (FLW) ──┼── Phase 5 (FRM)
Phase 4 (REM) ──┘
```

Within each phase, plans target non-overlapping file sets:

| Phase | Plan A Files | Plan B Files | Parallel? |
|-------|-------------|-------------|-----------|
| 1 | `docs/controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md` | `docs/playbooks/control-implementations/2.22/*`, `docs/images/2.22/EXPECTED.md` | Yes |
| 2 | `create_timeout_dataverse_schema.py` (policy + compliance tables), env vars, conn refs | `create_timeout_errorlog_schema.py`, seed data | Yes |
| 3 | Flow template core (enumeration + policy lookup + evaluation) | Notification logic + error handling | Yes |
| 4 | `Set-InactivityTimeout.ps1` | Remediation audit records + `Test-InactivityTimeoutRemediation.ps1` | Yes |
| 5 | `CONTROL-INDEX.md`, `mkdocs.yml`, framework docs, `solutions-index.md` | Build validation (read-only) | Yes |

## File Manifest

### Created (new files)

| Phase | File | Purpose |
|-------|------|---------|
| 1 | `docs/controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md` | Control 2.22 documentation (10-section template) |
| 1 | `docs/playbooks/control-implementations/2.22/portal-walkthrough.md` | PPAC Privacy + Security settings walkthrough |
| 1 | `docs/playbooks/control-implementations/2.22/powershell-setup.md` | Set-InactivityTimeout.ps1 usage guide |
| 1 | `docs/playbooks/control-implementations/2.22/verification-testing.md` | Compliance scan validation procedures |
| 1 | `docs/playbooks/control-implementations/2.22/troubleshooting.md` | MissingPolicy, API errors, connectivity |
| 1 | `docs/images/2.22/EXPECTED.md` | Screenshot specification |
| 2 | `scripts/create_timeout_dataverse_schema.py` | Dataverse schema (environmentpolicy + compliance tables) |
| 2 | `scripts/create_timeout_environment_variables.py` | Environment variables (concurrency, notification) |
| 2 | `scripts/create_timeout_connection_references.py` | Connection references (Dataverse, BAP Admin API) |
| 2 | `scripts/create_timeout_errorlog_schema.py` | Dataverse schema (errorlog table) |
| 3 | `src/detect-inactivity-timeout-noncompliance.json` | Cloud Flow template (detection + evaluation) |
| 4 | `scripts/governance/Set-InactivityTimeout.ps1` | PowerShell remediation script (BAP API PATCH) |
| 4 | `scripts/governance/Test-InactivityTimeoutRemediation.ps1` | Validation test script |

### Modified (existing files)

| Phase | File | Change |
|-------|------|--------|
| 5 | `docs/controls/CONTROL-INDEX.md` | Add Control 2.22 row |
| 5 | `mkdocs.yml` | Add 2.22 nav entry under Pillar 2 + playbook nav entries |
| 5 | `.github/copilot-instructions.md` | Update "63 controls" → "64 controls" |
| 5 | `AGENTS.md` | Update "63 controls" → "64 controls" |
| 5 | `README.md` | Update "63 controls" → "64 controls" |
| 5 | `docs/getting-started/*.md` | Update control count references if present |
| 5 | `docs/reference/solutions-index.md` | Add Inactivity Timeout Enforcement catalog entry |
| 5 | Hardening baseline playbook | Update item 30 control reference [3.7] → [2.22, 3.7] |

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| CTL-01 | 1 | 01-01 | Control 2.22 document (10-section template) |
| CTL-02 | 1 | 01-02 | 4 implementation playbooks |
| CTL-03 | 1 | 01-02 | Screenshot specification (EXPECTED.md) |
| DVM-01 | 2 | 02-01 | fsi_environmentpolicy table schema + env vars + conn refs |
| DVM-02 | 2 | 02-01 | fsi_inactivitytimeout_compliance table schema |
| DVM-03 | 2 | 02-02 | fsi_inactivitytimeout_errorlog table schema + seed data |
| FLW-01 | 3 | 03-01 | Detection flow — enumeration + policy lookup |
| FLW-02 | 3 | 03-01 | Per-environment compliance evaluation logic |
| FLW-03 | 3 | 03-02 | Guarded notification + error handling |
| REM-01 | 4 | 04-01 | Set-InactivityTimeout.ps1 (BAP API PATCH) |
| REM-02 | 4 | 04-02 | Remediation audit records + validation test script |
| FRM-01 | 5 | 05-01 | CONTROL-INDEX + mkdocs + "64 controls" updates |
| FRM-02 | 5 | 05-01 | Solutions-index catalog entry + hardening baseline update |
| FRM-03 | 5 | 05-02 | Build validation (mkdocs + verify scripts) |

**Total: 14/14 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-12*
*Depth: comprehensive*
*Phases: 5 (documentation → dataverse → flow → remediation → framework integration)*
