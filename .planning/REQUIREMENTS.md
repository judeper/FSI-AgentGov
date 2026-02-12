# Requirements: v17 — Agent Security Configuration Governance

## Overview

Automate per-agent authentication enforcement, publishing restriction validation, and zone-based access configuration governance — closing the manual attestation gap across Controls 1.1, 3.7, and 3.8. Converts 6 manual-only SSPM checks to automated validation, creates the phantom `restrict-agent-publishing.ps1` governance script, and adds zone-policy compliance verification for agent access settings.

**Source:** Three pending todos from v16 research:
- [Agent-Level Auth Enforcement Automation](todos/pending/2026-02-12-agent-auth-enforcement-automation.md)
- [Create restrict-agent-publishing.ps1](todos/pending/2026-02-12-restrict-agent-publishing-script.md)
- [Zone-Based Agent Access Validation](todos/pending/2026-02-12-zone-based-agent-access-validation.md)

## Requirement Categories

| Code | Category | Count |
|------|----------|-------|
| AUTH | Agent Authentication Enforcement | 3 |
| PUB | Publishing Restriction Governance | 3 |
| ZAV | Zone Access Validation | 3 |
| FRM | Framework Integration | 3 |
| **Total** | | **12** |

## AUTH — Agent Authentication Enforcement

- [x] **AUTH-01:** PowerShell script reads per-agent authentication configuration via BAP/PPAC REST endpoints — connects to Power Platform, enumerates agents per environment, retrieves auth mode/enforcement/sharing settings
- [x] **AUTH-02:** Validate 6 SSPM items (SSPM-1.1-01 through SSPM-1.1-06) with zone-based logic — Zone 1 permissive (warn only), Zone 2/3 enforce "Always" auth timing, "No Authentication" flagged in all zones, sharing scope "Anyone" flagged in Zone 2/3
- [x] **AUTH-03:** Drift detection for agent auth setting changes with SHA-256 evidence export — comparison against previous scan baseline, JSON output with integrity hashing for Dataverse ingestion

## PUB — Publishing Restriction Governance

- [x] **PUB-01:** Create `restrict-agent-publishing.ps1` validating 6 publishing restriction criteria — Environment Maker role removal, authorized security groups, Share with Everyone disabled, DLP connector blocking, Managed Environment sharing limits, approval workflow active (Zone 2/3)
- [x] **PUB-02:** SHA-256 evidence export and JSON output for downstream integration — structured JSON with per-check pass/fail, evidence hashes, timestamp; compatible with Dataverse ingestion patterns
- [x] **PUB-03:** Integration with `Invoke-HardeningBaselineCheck.ps1` for items 1-6 — hardening baseline items 1-6 reclassified from "Manual Attestation" to "Automated" or "Semi-Automated"; baseline script calls or references the new validation

## ZAV — Zone Access Validation

- [x] **ZAV-01:** Automate M365 Admin Center agent access settings verification per zone — script reads agent access control configuration, compares to zone policy (Zone 1: all agents, Zone 2: Org + MS verified, Zone 3: Org only with approval)
- [x] **ZAV-02:** Validate Admin Exclusion Groups and deployment group configuration — verify `CopilotForM365AdminExclude` Entra group exists and is populated; validate staged deployment group configuration per zone
- [x] **ZAV-03:** Drift detection with periodic validation and Teams notification support — comparison output suitable for daily scheduling; structured results compatible with existing alerting patterns (adaptive cards)

## FRM — Framework Integration

- [x] **FRM-01:** Update Controls 1.1, 3.7, 3.8 with automation solution references — tip admonitions linking to new governance scripts; verification criteria updated to reflect automation availability
- [x] **FRM-02:** Update solutions-index.md, hardening baseline, and governance README — solutions catalog entry added; hardening baseline items 1-6 status updated; `scripts/governance/README.md` reflects actual script
- [x] **FRM-03:** All validations pass — `mkdocs build --strict`, `verify_controls.py` 62/62, `verify_language_rules.py` 0 violations

## Traceability Matrix

| Requirement | Todo Source | Controls | Regulatory |
|-------------|-----------|----------|------------|
| AUTH-01, AUTH-02, AUTH-03 | agent-auth-enforcement-automation | 1.1, 2.8 | FINRA 4511, SEC 17a-3/4, GLBA 501(b), SOX 302 |
| PUB-01, PUB-02, PUB-03 | restrict-agent-publishing-script | 1.1, 2.1, 3.7 | FINRA 4511, SEC 17a-4, SOX 302/404, GLBA 501(b) |
| ZAV-01, ZAV-02, ZAV-03 | zone-based-agent-access-validation | 3.8, 1.1, 2.1 | FINRA 3110, SOX 404, GLBA 501(b), OCC 2011-12 |
| FRM-01, FRM-02, FRM-03 | All three todos | 1.1, 3.7, 3.8 | All applicable |

## Out of Scope

| Item | Reason |
|------|--------|
| Power Automate flow orchestration | Scripts are standalone; flow integration deferred to future milestone |
| New Dataverse tables | Use existing validation patterns; new tables deferred |
| Remediation automation | Detection/validation only — manual remediation for this milestone |
| Canvas app UI for results | CLI/JSON output sufficient |
| Managed identity / production-grade auth | Lab-grade implementation; expandable later |
| Real-time monitoring | Scheduled/on-demand sufficient per framework constraints |

## Priority Summary

- **P1 (8):** AUTH-01, AUTH-02, AUTH-03, PUB-01, PUB-02, ZAV-01, FRM-01, FRM-02, FRM-03
- **P2 (3):** PUB-03, ZAV-02, ZAV-03

---
*Requirements defined: 2026-02-12*
*Milestone: v17 — Agent Security Configuration Governance*
