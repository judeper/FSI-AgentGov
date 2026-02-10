# Phase 03 Verification: Automation and Alerting v6

**Phase:** 03 - Automation and Alerting
**Verified:** 2025-07-17
**Verifier:** copilot

## Phase Goal

> Deliver the automation layer for the Agent Access Governance Monitor: Azure Automation runbook wrapper, operator baseline capture, Power Automate flow with adaptive card alerting, and Dataverse persistence — enabling daily unattended validation with drift detection and multi-channel alert routing.

## Verification Checklist

### Plan 03-01: Core Scripts (Wave 1) ✅

| Criterion | Result | Evidence |
|-----------|--------|----------|
| AAMClient exports 8 functions | ✅ Pass | `Save-AAMBaseline` and `Get-AAMLastValidation` added, Export-ModuleMember confirms 8 |
| Start-AccessValidationRunbook.ps1 parses | ✅ Pass | PS5.1 ParseFile: 0 errors (em dashes fixed) |
| Invoke-AccessBaselineCapture.ps1 parses | ✅ Pass | PS5.1 ParseFile: 0 errors (?? operators and em dashes fixed) |
| Save-AAMBaseline supports -WhatIf | ✅ Pass | ShouldProcess declared, baseline rotation with WhatIf preview |
| Get-AAMLastValidation queries correct table | ✅ Pass | Uses `fsi_accessvalidationhistory` with $top=1 orderby desc |
| 3 atomic commits | ✅ Pass | `da31a5f`, `b20e8f1`, `8b184b5` |

### Plan 03-02: Alert & Orchestration Layer (Wave 2) ✅

| Criterion | Result | Evidence |
|-----------|--------|----------|
| adaptive-card-access-alert.json valid JSON | ✅ Pass | ConvertFrom-Json succeeds |
| access-validation-flow.json valid JSON | ✅ Pass | ConvertFrom-Json succeeds |
| Adaptive card uses Schema 1.4 | ✅ Pass | `"version": "1.4"` in card definition |
| Flow trigger: daily 6AM UTC | ✅ Pass | Recurrence: Day/1, hours: [6], minutes: [0], UTC |
| Write_Validation_History before Check_Alert_Required | ✅ Pass | runAfter ordering verified |
| Check_Alert_Required runAfter includes Failed | ✅ Pass | `["Succeeded", "Failed"]` confirmed |
| Scope_Catch handles flow failures | ✅ Pass | Runs on `["Failed", "Skipped", "TimedOut"]` |
| FLOW_SETUP.md covers import, config, testing | ✅ Pass | 7 Steps + troubleshooting section |
| FLOW_SETUP.md has Validation History Write section | ✅ Pass | Step 4 with column mapping and error codes |
| 1 atomic commit | ✅ Pass | `25b29d6` (3 files, 1244 insertions) |

### Plan 03-03: Integration Verification (Wave 3) ✅

| Criterion | Result | Evidence |
|-----------|--------|----------|
| All 3 settings compared in drift detection | ✅ Pass | bot-limitSharingMode, bot-authoringSharingDisabled, bot-publishedBotLimitSharingMode |
| Drift direction classified (Weakened/Strengthened/Changed) | ✅ Pass | Get-DriftDirection with ordered maps; Weakened priority in overall direction |
| No baseline → IsFirstRun=true | ✅ Pass | Explicit check before comparison |
| Dataverse query failure → fail open | ✅ Pass | Catch block sets HasDrift=false, IsFirstRun=true |
| Runbook output keys match flow Parse_Results schema | ✅ Pass | 10/10 top-level keys match; nested arrays match |
| ZoneSummary enriched for flow/card | ✅ Pass | Fixed: flat integers → {Total, Compliant, Violations} per zone |
| Adaptive card placeholders match runbook output | ✅ Pass | 27 placeholders all have corresponding output properties |
| Dataverse column names match schema | ✅ Pass | 7 columns verified against create_dataverse_schema.py |
| CHANGELOG v0.3.0 entry | ✅ Pass | 7 Added items, 2 Changed items |
| 1 atomic commit | ✅ Pass | `71e58a7` (2 files, 89 insertions) |

### Cross-Phase Validation ✅

| Criterion | Result | Evidence |
|-----------|--------|----------|
| mkdocs build --strict | ✅ Pass | Built in 48.72s, 0 errors, 0 warnings |
| verify_controls.py | ✅ Pass | Docs anchor validation passed |
| FSI language rules | ✅ Pass | No overclaim language in FLOW_SETUP.md or CHANGELOG |
| All Phase 3 files committed | ✅ Pass | git status shows no uncommitted Phase 3 files |

## Issues Found and Resolved

| Issue | Severity | Resolution |
|-------|----------|------------|
| ZoneSummary structural mismatch | High | Runbook enriches flat integer counts to per-zone objects with Total/Compliant/Violations |
| Em dash encoding (U+2014) breaks PS5.1 parser | High | Replaced with ASCII dashes in both scripts (Wave 1) |
| PS7 `??` operator in PS5.1-required script | Medium | Replaced with `if/else` pattern in Invoke-AccessBaselineCapture.ps1 |

## Artifacts Summary

| Repository | File | Lines | Commit |
|-----------|------|-------|--------|
| Solutions | `scripts/private/AAMClient.psm1` | 464 | `da31a5f` |
| Solutions | `scripts/Start-AccessValidationRunbook.ps1` | ~520 | `b20e8f1`, `71e58a7` |
| Solutions | `scripts/Invoke-AccessBaselineCapture.ps1` | 402 | `8b184b5` |
| Solutions | `src/adaptive-card-access-alert.json` | ~250 | `25b29d6` |
| Solutions | `src/access-validation-flow.json` | 605 | `25b29d6` |
| Solutions | `docs/FLOW_SETUP.md` | ~280 | `25b29d6` |
| Solutions | `CHANGELOG.md` | ~60 | `71e58a7` |

## Deferred Items

| Item | Reason | Suggested Phase |
|------|--------|----------------|
| Entity set name standardization (validationhistory singular vs baselines/violations plural) | Phase 2 deployed schema; changing would break existing data | Future cleanup |
| End-to-end tenant test with live Dataverse | No tenant access in CI | Manual validation |
