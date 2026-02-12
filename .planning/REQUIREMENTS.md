# Requirements: v19 — Inactivity Timeout Enforcement (Policy-Driven Maximum)

## Overview

Add a new Control 2.22 (Inactivity Timeout Enforcement) to the Management Pillar and build the companion solution — automated validation and enforcement of Power Platform user inactivity timeout settings across multiple environments with zone-based policy-driven maximum duration requirements, Dataverse persistence, and PowerShell remediation.

**Source:** AI Implementation Specification — "Inactivity Timeout Enforcement (Policy-Driven Maximum)" provided 2026-02-12. Defines deterministic, auditable, zone-aware inactivity timeout validation for regulated Financial Services environments.

**Accuracy notes from research:**
- Control ID 2.22 confirmed as next available in Pillar 2 (currently 2.1-2.21, 21 controls)
- Framework control count changes from 63 to 64; Pillar 2 from 21 to 22
- Playbook count changes from 252 to 256 (4 new playbooks for 2.22)
- Hardening baseline item 30 already references inactivity timeout at flat ≤120 minutes — new control adds zone-based differentiation (Zone 2: ≤120, Zone 3: ≤60)
- Control 3.7 (PPAC Security Posture) references inactivity timeout in its hardening checklist — needs cross-reference to 2.22
- Session Security Configurator (v5, Control 1.23) is complementary but different scope: CA-based session policies (Graph API) vs PP environment privacy settings (BAP Admin API)
- API endpoint: `GET/PATCH https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{EnvironmentName}/settings/privacy?api-version=2021-04-01`
- Canonical identifier `EnvironmentName` (Power Platform Environment Name) — NOT display name, NOT Dataverse row GUID
- Spec language must be rewritten with hedged FSI-safe language where needed

## Requirement Categories

| Code | Category | Count |
|------|----------|-------|
| CTL | Control Documentation | 3 |
| DVM | Dataverse Data Model | 3 |
| FLW | Cloud Flow & Validation Logic | 3 |
| REM | PowerShell Remediation | 2 |
| FRM | Framework Integration | 3 |
| **Total** | | **14** |

## CTL — Control Documentation

- [ ] **CTL-01:** Create Control 2.22 documentation in `docs/controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md` following 10-section template — header metadata (Control ID 2.22, Pillar: Management, Regulatory: GLBA 501(b), SOX 302, FINRA 4511, NIST 800-53 AC-11/AC-12), objective (automated inactivity timeout validation with zone-based policy enforcement), FSI rationale, control description (policy-driven with `fsi_environmentpolicy` table, BAP Admin API retrieval, zone-aware compliance evaluation), key configuration points, zone-specific requirements table (Zone 1: Optional, Zone 2: Required ≤120 min, Zone 3: Required ≤60 min), roles & responsibilities, related controls (1.23, 3.7, 3.8), implementation playbooks, verification criteria, additional resources, footer metadata
- [ ] **CTL-02:** Create 4 playbooks in `docs/playbooks/control-implementations/2.22/` — portal-walkthrough (PPAC Privacy + Security settings → inactivity timeout configuration), powershell-setup (Set-InactivityTimeout.ps1 usage with EnvironmentName parameter), verification-testing (Detect-InactivityTimeout-NonCompliance flow output validation, Dataverse compliance records review), troubleshooting (MissingPolicy, 401/403/404/429 errors, BAP API connectivity)
- [ ] **CTL-03:** Create `docs/images/2.22/EXPECTED.md` screenshot specification — PPAC Environment Settings Privacy + Security page, inactivity timeout toggle and duration field, compliance scan results in Dataverse, notification email sample

## DVM — Dataverse Data Model

- [ ] **DVM-01:** Create `fsi_environmentpolicy` table schema script — `fsi_environmentid` (Text PK, EnvironmentName), `fsi_environmentdisplayname` (Text), `fsi_zone` (Choice: Zone1/Zone2/Zone3), `fsi_requiredmaxduration` (Whole Number, minutes), `fsi_notes` (Multi-line Text); reuse `fsi_acv_zone` shared option set where compatible
- [ ] **DVM-02:** Create `fsi_inactivitytimeout_compliance` table schema script — one record per environment per scan, never update in place; columns: `fsi_environmentid` (Text), `fsi_environmentname` (Text), `fsi_environmenttype` (Choice), `fsi_inactivitytimeoutenabled` (Boolean), `fsi_timeoutduration` (Whole Number), `fsi_requiredmaxduration` (Whole Number), `fsi_compliancestatus` (Choice: Compliant/Non-Compliant/Unknown), `fsi_lastscandate` (DateTime), `fsi_notes` (Multi-line Text); index on `(fsi_environmentid, fsi_lastscandate)`
- [ ] **DVM-03:** Create `fsi_inactivitytimeout_errorlog` table schema script — columns: `fsi_environmentid` (Text), `fsi_errortype` (Text: 401/403/404/429/MissingPolicy/ParseError), `fsi_errorraw` (Multi-line Text), `fsi_timestamp` (DateTime)

## FLW — Cloud Flow & Validation Logic

- [ ] **FLW-01:** Create `Detect-InactivityTimeout-NonCompliance` flow template — scheduled daily at 06:00 UTC, Step 1: enumerate environments via Power Platform for Admins V2 (store EnvironmentName, display name, type), Step 2: load all `fsi_environmentpolicy` rows and build lookup keyed by EnvironmentName
- [ ] **FLW-02:** Implement per-environment evaluation with configurable concurrency (default 5 via environment variable) — mandatory policy resolution (no policy row → ComplianceStatus=Unknown, note "No explicit policy found for environment", error log entry with errortype=MissingPolicy, do NOT evaluate against any default threshold); BAP Admin API privacy settings retrieval (`api.bap.microsoft.com`, service principal auth, scope `https://api.bap.microsoft.com/.default`); compliance determination (API fail → Unknown + error log; timeout disabled → Non-Compliant; duration > required max → Non-Compliant; otherwise → Compliant); persist result as new row in compliance table (never update existing)
- [ ] **FLW-03:** Implement guarded notification — send email only when Non-Compliant count > 0 OR Unknown count > 0; include environment, zone, actual duration, required max, and status in notification; no empty notifications

## REM — PowerShell Remediation

- [ ] **REM-01:** Create `Set-InactivityTimeout.ps1` with mandatory `EnvironmentName` parameter (canonical Power Platform Environment Name identifier), `TimeoutDuration` (ValidateRange 5-120, default 120), `WarningDuration` (ValidateRange 1-30, default 5); PATCH BAP Admin API privacy settings endpoint; log success/failure; `#Requires -Version 7.0`, `SupportsShouldProcess`, `-WhatIf` support
- [ ] **REM-02:** Create remediation audit record writing capability — optionally write remediation records to Dataverse compliance table with action taken, before/after values, and timestamp; create validation test script to confirm PATCH was applied

## FRM — Framework Integration

- [ ] **FRM-01:** Update framework references — CONTROL-INDEX.md (add 2.22 row), mkdocs.yml navigation (add under Pillar 2 Management after 2.21), update "63 controls" → "64 controls" across framework docs (copilot-instructions, AGENTS.md, README, getting-started, framework docs), update "21 management controls" → "22 management controls", update playbook count "252" → "256"
- [ ] **FRM-02:** Add solutions-index.md catalog entry — overview row (Inactivity Timeout Enforcement, v1.0.0, Completed), detail section (components, regulatory alignment: GLBA 501(b), SOX 302, FINRA 4511, NIST 800-53 AC-11/AC-12), cross-references from related controls (1.23, 3.7, 3.8); update hardening baseline item 30 control reference from [3.7] to [2.22, 3.7]
- [ ] **FRM-03:** All validations pass — `mkdocs build --strict`, `verify_controls.py` 64/64, `verify_language_rules.py` 0 violations

## Traceability Matrix

| Requirement | Spec Section | Controls | Regulatory |
|-------------|-------------|----------|------------|
| CTL-01, CTL-02, CTL-03 | §2 Control Objective, §3 Policy & Zoning | 2.22 (new) | GLBA 501(b), SOX 302, FINRA 4511, NIST 800-53 AC-11/AC-12 |
| DVM-01, DVM-02, DVM-03 | §4 Dataverse Data Model | 2.22 | GLBA 501(b), SEC 17a-4 (audit trail), SOX 302 |
| FLW-01, FLW-02, FLW-03 | §5 Cloud Flow – Validation Logic | 2.22, 3.7 | GLBA 501(b), SOX 302, FINRA 4511 |
| REM-01, REM-02 | §6 PowerShell Remediation Script | 2.22 | GLBA 501(b), SOX 302, FINRA 4511 |
| FRM-01, FRM-02, FRM-03 | §7 Solution Naming, §8 Completion | 2.22, 1.23, 3.7, 3.8 | All applicable |

## Out of Scope

| Item | Reason |
|------|--------|
| Session expiration / total session lifetime | Separate setting (hardening baseline item 31); different validation logic |
| Conditional Access session policies | Covered by SSC (v5, Control 1.23) — CA policies validated via Graph API |
| Auto-remediation without approval | Detection/validation only; Set-InactivityTimeout.ps1 requires manual invocation |
| Managed identity / production-grade auth | Lab-grade implementation consistent with v4-v18 pattern |
| Real-time monitoring / webhook triggers | Batch/daily scheduled scan per framework constraint |
| Session security for model-driven apps | Scoped to Power Platform environment-level privacy settings |

## Priority Summary

- **P1 (10):** CTL-01, CTL-02, DVM-01, DVM-02, FLW-01, FLW-02, FLW-03, FRM-01, FRM-02, FRM-03
- **P2 (4):** CTL-03, DVM-03, REM-01, REM-02

---
*Requirements defined: 2026-02-12*
*Milestone: v19 — Inactivity Timeout Enforcement (Policy-Driven Maximum)*
