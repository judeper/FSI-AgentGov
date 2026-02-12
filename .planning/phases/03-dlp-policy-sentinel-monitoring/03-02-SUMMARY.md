---
phase: 3
plan: 2
title: "Sentinel analytics alert rule ARM template"
status: complete
completed: 2026-02-12
---

# Summary 03-02: Sentinel Analytics Alert Rule ARM Template

## Status: COMPLETE

## Files Created

| File | Purpose |
|------|---------|
| `src/high-volume-blocks.json` | ARM template for Microsoft Sentinel scheduled analytics rule detecting high-volume blocked file upload attempts |

## What Was Done

Created a deployable ARM template (`src/high-volume-blocks.json`) for a Microsoft Sentinel scheduled analytics rule with the following characteristics:

- **Detection logic:** KQL query against `PowerPlatformDlpActivity_CL` table detecting >10 blocked upload attempts per user per hour
- **MITRE ATT&CK mapping:** InitialAccess (T1566 — Phishing) and Execution (T1204 — User Execution)
- **Entity mapping:** Account entity mapped via `UserPrincipalName` → `FullName`
- **Incident grouping:** Incidents grouped by Account with 5-hour lookback, selected matching method
- **Alert details override:** Dynamic display name and description using `{{UserPrincipalName}}`, `{{BlockCount}}`, and `{{EnvironmentName}}` placeholders
- **Custom details:** `EnvironmentName` and `BlockCount` surfaced in alert custom fields
- **Tags/metadata:** Control reference 1.25, FSI Agent Governance framework, version 1.0.0
- **Parameters:** `workspaceName` (required) and `location` (defaults to resource group location)

## Verification Results

- **JSON validity:** Valid, parseable JSON
- **All 25 acceptance criteria:** PASSED
- **FSI language rules:** No prohibited phrases detected
- **KQL query:** Syntactically valid with correct aggregation pattern
- **MITRE ATT&CK codes:** T1566 and T1204 correctly referenced
- **Entity mapping:** Account type with FullName identifier
- **Incident grouping:** Configured by Account entity per specification

## Decisions Made

1. **KQL filter conditions:** Used `ActionType_s == "BlockUpload" or ActionType_s == "FilePolicyViolation"` as the filter condition since the custom log table (`PowerPlatformDlpActivity_CL`) uses `_s` suffix for string columns per Log Analytics custom log conventions. These action types cover both direct DLP blocks and policy violations.
2. **Suppression:** Set `suppressionEnabled: false` and `suppressionDuration: PT1H` to allow all incidents to surface. Customers can enable suppression if alert fatigue occurs.
3. **Unique rule name:** Used `uniqueString(resourceGroup().id)` in the alert rule name to avoid naming collisions across deployments.
4. **Outputs:** Added `alertRuleId` and `alertRuleName` outputs for downstream automation or cross-template references.

## Deviations from Plan

None. All must-have requirements and acceptance criteria were met as specified.

## Issues Encountered

None.
