# ACM Deep Audit — Executive Summary

**Audit Date:** 2026-02-16
**Solution:** Audit Compliance Manager (ACM) v1.0.0
**Scope:** Full audit — both FSI-AgentGov (docs) and FSI-AgentGov-Solutions (scripts/templates)
**Auditor:** Automated multi-agent deep audit (10 parallel review agents)
**Prior Audit:** v23 comprehensive audit (2026-02-14) — found 2 critical ALCA bugs, both remediated

---

## Key Metrics

| Category | Files Reviewed | P0 | P1 | P2 | Total |
|----------|---------------|-----|-----|-----|-------|
| Regression Gate | 4 scripts | 2 | 1 | 0 | 3 |
| Batch A — Auth & Module Core | 5 scripts | 2 | 12 | 11 | 25 |
| Batch B — Detection Pipeline | 5 scripts | 1 | 10 | 12 | 23 |
| Batch C — Remediation & Evidence | 6 scripts | 0 | 8 | 12 | 20 |
| Batch D — Validation Test Scripts | 6 scripts | 6 | 16 | 15 | 37 |
| Batch E+F — Runbooks & Python | 10 scripts | 2 | 6 | 9 | 17 |
| Batch G — Solution Docs & Templates | 16 files | 2 | 10 | 10 | 22 |
| Batch H — Framework Docs | 9 files | 0 | 1 | 6 | 7 |
| Stale Reference Scan | Both repos | 0 | 12 | 0 | 12 |
| Learn URL Validation | 8 files | 0 | 0 | 0 | 0 |
| Requirements Traceability | 21 reqs | 0 | 0 | 0 | 0 |
| **TOTAL** | **~45 files** | **15** | **76** | **75** | **166** |

## v23 Regression Gate Results

| Check | Result |
|-------|--------|
| PATCH not PUT for EntityDefinitions | ✅ PASS |
| AccessToken passed to Add-PowerAppsAccount | ✅ PASS |
| PS 5.1 compatibility | ❌ FAIL — PSM1 still requires 7.2, Connect-PowerPlatform requires 7.0 |
| Valid RecordTypes only | ✅ PASS |

## Top 10 Critical Findings

| # | Severity | Component | Finding |
|---|----------|-----------|---------|
| 1 | **P0** | AuditComplianceHelpers.psm1 | `#Requires -Version 7.2` but runbooks declare PS 5.1 — module won't load |
| 2 | **P0** | Check-AuditLoggingCompliance.ps1 | `Get-Date -AsUTC` (PS 7.1+) used in script declaring 5.1 compat |
| 3 | **P0** | acv_client.py | No pagination in `query()` — >5000 Dataverse records silently dropped |
| 4 | **P0** | alca_client.py | PUT in retry methods + POST retries can create duplicate records |
| 5 | **P0** | DELIVERY-CHECKLIST.md | Entirely stale — still branded ALCA, uses old paths, excludes ACV deliverables |
| 6 | **P0** | README.md | Quick Start references 2 Python scripts that don't exist |
| 7 | **P0** | AuditComplianceHelpers.psd1 | ProjectUri/LicenseUri point to wrong GitHub org (microsoft vs judeper) |
| 8 | **P0** | Connect-PowerPlatform.ps1 | SecureString reconverted to plaintext unnecessarily for MSAL |
| 9 | **P0** | Test-*.ps1 (all 5) | All validators require PS 7.0+ — systemic PS version conflict |
| 10 | **P1** | Check-AuditLoggingCompliance.ps1 | `Get-AdminConfig` cmdlet doesn't exist — Purview check always returns $false |

## Root Cause Analysis

Two systemic issues account for ~60% of all findings:

1. **PS Version Incoherence (31 findings):** The solution cannot decide between PS 5.1 and PS 7.x. The module requires 7.2, some scripts declare 5.1, validators require 7.0, and the private auth scripts require 7.0. This creates a broken dependency chain.

2. **Incomplete ACM Merger Cleanup (34 findings):** ALCA and ACV were physically consolidated into `audit-compliance-manager/` but documentation was largely carried over verbatim. DELIVERY-CHECKLIST, SOLUTION-DOCUMENTATION, and 5+ doc titles still reference old solution names. All `src/` paths need updating to `scripts/`/`templates/`.

## Requirements Traceability

All 21 v21 ALCA requirements (MOD/DET/REM/DVS/DPL/FLW/TST/FRM) are **fully delivered** and preserved in the ACM merger. See `acm-audit-requirements-traceability.md` for the complete matrix.

## Learn URL Validation

All 6 Microsoft Learn URLs in Control 1.7 are valid and returning current content.

## Recommendations

1. **Immediate (P0):** Align all scripts to a single PS version target (recommend 7.2 given `Get-Date -AsUTC` usage) and update all `#Requires` statements accordingly.
2. **Immediate (P0):** Add Dataverse pagination to Python client `query()` methods.
3. **Before next release (P1):** Complete ACM merger cleanup — rewrite DELIVERY-CHECKLIST, update SOLUTION-DOCUMENTATION, fix all `src/` → `scripts/`/`templates/` paths.
4. **Before next release (P1):** Fix `Get-AdminConfig` (non-existent cmdlet) in detection script.
5. **Planned (P2):** Create Pester tests for the 5 validation scripts (currently zero coverage).

---

*Report generated: 2026-02-16 | Audit methodology: Parallel multi-agent deep review with regression gate*
