# Plan 03-03 Summary: Integration Verification and CHANGELOG

**Phase:** 03 - Automation and Alerting v6
**Plan:** 03/03
**Wave:** 3
**Status:** Complete
**Executed:** 2025-07-17

## Dependency Graph

```
Plan 03-01 (Core Scripts) ──► Plan 03-02 (Alert & Orchestration) ──► Plan 03-03 (Integration & QA)
       ✅ Complete                      ✅ Complete                         ✅ Complete
```

## Deliverables

| # | Task | File | Status |
|---|------|------|--------|
| 1 | Verify drift detection logic | `Start-AccessValidationRunbook.ps1` | ✅ Verified |
| 2 | Verify Dataverse write path | `access-validation-flow.json` | ✅ Verified |
| 3 | Validate FLOW_SETUP.md coverage | `FLOW_SETUP.md` | ✅ Already complete |
| 4 | Add v0.3.0 CHANGELOG entry | `CHANGELOG.md` | ✅ Updated |
| 5 | Fix ZoneSummary mismatch | `Start-AccessValidationRunbook.ps1` | ✅ Fixed |

## Commit

| Hash | Message | Files |
|------|---------|-------|
| `71e58a7` | fix(aam): enrich ZoneSummary for flow/card consumption, add v0.3.0 | 2 files, 89 insertions |

## Verification Results

### Task 1: Drift Detection Logic

All acceptance criteria met:

- **3 settings compared:** `bot-limitSharingMode`, `bot-authoringSharingDisabled`, `bot-publishedBotLimitSharingMode` - all present in drift detection loop (lines ~340-360)
- **Direction classification:** Correctly implemented via `Get-DriftDirection` and `Get-SharingDriftDirection` helper functions with restrictiveness ordering (NoSharing=1 → NoRestriction=4)
- **Edge cases handled:**
  - No active baseline → `IsFirstRun = true`, drift detection skipped
  - Dataverse query failure → catch block fails open (`HasDrift = false, IsFirstRun = true`)
  - Multiple zones → drift evaluated per-environment (foreach loop processes independently)
  - Overall direction priority: Weakened > Strengthened > Changed

### Task 2: Dataverse Write Path

All acceptance criteria met:

- **Column mapping complete:** 7 columns mapped (fsi_name, fsi_run_id, fsi_overall_status, fsi_violation_count, fsi_total_environments, fsi_summary_json, fsi_validation_time) - all match create_dataverse_schema.py column SchemaNames
- **Action ordering correct:** Parse_Results → Write_Validation_History → Check_Alert_Required
- **Entity set name:** `fsi_accessvalidationhistory` - consistent with AAMClient.psm1 usage (line 214)
- **Alert resilience:** `Check_Alert_Required` has `runAfter: ["Succeeded", "Failed"]` on Write_Validation_History - alerting proceeds even if Dataverse write fails
- **Missing picklist columns:** `fsi_zone` and `fsi_severity` have `ApplicationRequired` level in schema, but this is form-level enforcement only (not API-level). Both AAMClient.psm1 `Write-AAMValidationHistory` and flow omit these without error. Confirmed valid per Dataverse Web API behavior.

### Task 3: FLOW_SETUP.md Coverage

Step 4 ("Validation History Write") was already included when FLOW_SETUP.md was created in Plan 03-02. Contains:
- Purpose statement referencing FINRA 4511 and SEC 17a-3
- Dataverse table name and connection reference
- Column mapping table
- Troubleshooting table covering 403/404/400 error codes
- Explanation of why write runs before alerting

No additional changes needed.

### Task 5: ZoneSummary Structural Mismatch (Found During Verification)

**Issue discovered:** The orchestrator (`Test-AgentAccessCompliance.ps1`) produces `ZoneSummary` as flat integer counts (`Zone1 = 3`), but the flow `Parse_Results` schema and adaptive card expect `Zone1: { Total, Compliant, Violations }`.

**Root cause:** The orchestrator was designed before the flow/card schema, and Phase 3 adopted the enriched format for per-zone detail in alerts. The runbook bridges this gap.

**Fix applied:** Added `#region Build enriched ZoneSummary` block in the runbook that:
1. Counts non-compliant environments per zone from `$scanResult.Environments`
2. Uses orchestrator's zone totals from `$scanResult.ZoneSummary`
3. Computes `Compliant = Total - ViolationEnvCount` per zone
4. Emits `[PSCustomObject]$enrichedZoneSummary` with correct structure

### End-to-End Structural Consistency

| Component | Output Property | Value Type | Consistent? |
|-----------|----------------|------------|-------------|
| Runbook → Flow | RunType | string | ✅ |
| Runbook → Flow | Timestamp | string (ISO 8601) | ✅ |
| Runbook → Flow | TotalEnvironments | integer | ✅ |
| Runbook → Flow | OverallStatus | string | ✅ |
| Runbook → Flow | Reason | string | ✅ |
| Runbook → Flow → Card | ZoneSummary.Zone{N}.Total | integer | ✅ (after fix) |
| Runbook → Flow → Card | ZoneSummary.Zone{N}.Compliant | integer | ✅ (after fix) |
| Runbook → Flow → Card | ZoneSummary.Zone{N}.Violations | integer | ✅ (after fix) |
| Runbook → Flow → Card | Violations[].EnvironmentName | string | ✅ |
| Runbook → Flow → Card | Violations[].Zone | string | ✅ |
| Runbook → Flow → Card | Violations[].Setting | string | ✅ |
| Runbook → Flow → Card | Drift[].Direction | string\|null | ✅ |
| Runbook → Flow → Card | Drift[].Changes[].Setting | string | ✅ |
| Runbook → Flow → Card | Drift[].Changes[].BaselineValue | string | ✅ |
| Runbook → Flow → Card | Drift[].Changes[].CurrentValue | string | ✅ |
| Runbook → Flow | AlertRequired | boolean | ✅ |
| Runbook → Flow → Card | AlertSeverity | string | ✅ |

## Notes

- The entity set name inconsistency across tables (`fsi_accessbaselines` has 's', `fsi_accessvalidationhistory` does not) is a Phase 2 artifact. Both the AAMClient and flow use the same singular form consistently. Deferring standardization to avoid breaking deployed schemas.
- CHANGELOG v0.3.0 date set to 2025-07-17 (execution date). Prior v0.2.0 and v0.1.0 entries used 2026-02-09 dates (from Phase 1/2); not modified.
