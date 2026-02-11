---
phase: 3
plan: 4
status: complete
---

# Plan 03-04 Summary: ELM Provisioning Hook Child Flow

## Objective

Created a Power Automate child flow triggered by the ELM ProvisioningCompleted event that runs a zone-scoped CA policy compliance check, writes violations to Dataverse as provisioning-triggered records, and routes severity-classified alerts based on the provisioned environment's governance zone.

## What Was Done

### File Created

| File | Action | Lines |
|------|--------|-------|
| `src/caa-provisioning-hook-flow.json` | CREATE | 1,380 |

### Flow Architecture

The flow is a child flow (manual trigger with typed input/output parameters) following the Logic App workflow schema (`2016-06-01`). It implements the verify-on-provision pattern:

```
Manual Trigger (child flow — called by ELM parent)
  Inputs: EnvironmentId, EnvironmentName, Zone, ProvisionedBy, ProvisionedAt
  → Initialize 10 variables (config + output state)
  → Compute zone severity/style/label
  → Scope_Try
      → Generate Job ID (GUID)
      → Create Azure Automation Job (HTTP PUT)
          Runbook: Start-CAAValidationRunbook
          Params: TenantId, ClientId, CertificateThumbprint, ConfigPath,
                  DataverseUrl, Zone (from input), Scope = "Targeted"
      → Wait_Loop (30s delay, 60 iterations max, PT30M timeout)
      → Check_Job_Status (If Completed)
          TRUE → Get_Job_Output → Parse_Results
              → Evaluate_Verification_Outcome
                  Passed: FailedCount=0 → status=Passed, severity=Passed
                  Failed: FailedCount>0 → status=Failed, severity from zone
              → Verify_Dataverse_Record (query + fallback with ProvisioningHookFallback source)
              → Write_Violations_to_Dataverse (each gap → fsi_CAPolicyViolation with provisioning tags)
              → Check_Alert_Required (If true)
                  → Post provisioning-context adaptive card to Teams
                  → Send zone-severity HTML email
          FALSE → Set status=Error, send CRITICAL job failure email + Teams
  → Scope_Catch (on Scope_Try failure/timeout)
      → Set status=Error, send CRITICAL flow error email
  → Return_Output (Response action)
      Outputs: VerificationStatus, GapsFound, AlertSent, Severity
```

### Connection References

| Logical Name | Connector | Usage |
|-------------|-----------|-------|
| `fsi_cr_dataverse_conditionalaccessautomation` | Dataverse | Validation record verify/fallback, violation writes |
| `fsi_cr_office365_conditionalaccessautomation` | Office 365 | Provisioning alert + error emails |
| `fsi_cr_teams_conditionalaccessautomation` | Teams | Provisioning adaptive card + failure notifications |

### Key Design Decisions

1. **Verify-on-provision pattern**: CA policies target applications and security groups at the tenant level, not individual environments. The hook verifies zone coverage is intact, not deploys per-environment policies.
2. **Zone-scoped runbook invocation**: Passes `-Zone` and `-Scope Targeted` to Start-CAAValidationRunbook, restricting compliance checks to the provisioned zone only.
3. **Shorter timeout**: 30-minute job timeout (PT30M, 60 iterations) versus the daily scan's 2-hour timeout — targeted scans cover a single zone with fewer policies.
4. **Zone-based severity mapping**: Zone 3 → Critical (attention), Zone 2 → High (warning), Zone 1 → Warning (accent). Severity drives adaptive card container styling and email subject classification.
5. **Provisioning-tagged violations**: Each `fsi_CAPolicyViolation` record includes `fsi_scan_trigger: Provisioning`, `fsi_environment_id`, and `fsi_environment_name` for audit trail linkage.
6. **Fallback source differentiation**: Fallback validation records use `fsi_source: ProvisioningHookFallback` (distinct from the daily scan's `FlowFallback`) for clear audit trail separation.
7. **Child flow contract**: Typed inputs (EnvironmentId, EnvironmentName, Zone, ProvisionedBy, ProvisionedAt) and typed outputs (VerificationStatus, GapsFound, AlertSent, Severity) via Request/Response actions.
8. **No hardcoded values**: All tenant-specific configuration initialized as variables, matching the daily scan's environment variable binding pattern.

### Parse_Results Schema

Extended from the daily scan schema (Plan 03-03) to include provisioning-specific fields:
- All scalar/array fields from Plan 03-01 output schema
- Additional fields: `ScanScope` (string), `ProvisioningTriggered` (boolean)
- Same required fields as daily scan for backward compatibility

### Provisioning Alert Card

- Header displays `[PROVISIONING]` prefix (vs daily scan's `[ALERT]`)
- Provisioning Context section shows environment name, ID, zone, provisioner, timestamp
- Severity badge/color/style computed from input Zone (not OverallSeverity)
- Actions include "View Environment" link to Power Platform Admin Center
- Zone label resolved at flow start for consistent display throughout

### Output Contract

| Field | Type | Values |
|-------|------|--------|
| VerificationStatus | String | Passed, Failed, Error |
| GapsFound | Integer | 0+ (count of compliance gaps) |
| AlertSent | Boolean | true if alert dispatched |
| Severity | String | Critical, High, Warning, Passed |

## Verification Checklist

- [x] Child flow with manual trigger (Request) and response action (Response)
- [x] Typed input parameters: EnvironmentId, EnvironmentName, Zone, ProvisionedBy, ProvisionedAt
- [x] Typed output parameters: VerificationStatus, GapsFound, AlertSent, Severity
- [x] Azure Automation job with `-Zone` and `-Scope Targeted` parameters
- [x] Job polling: 30s delay, 60 iterations max, PT30M timeout
- [x] Parse_Results schema includes ScanScope and ProvisioningTriggered fields
- [x] Verification outcome evaluation: Passed (FailedCount=0) vs Failed (gaps found)
- [x] Validation history record verified with ProvisioningHookFallback source
- [x] Individual violation records written to fsi_CAPolicyViolation with provisioning tags
- [x] Zone severity mapping: Zone 3 → Critical, Zone 2 → High, Zone 1 → Warning
- [x] Teams adaptive card posted only when AlertRequired=true
- [x] Email sent only when AlertRequired=true with zone-severity subject
- [x] Job failure path sets status=Error and sends CRITICAL notifications
- [x] Error scope catches flow failures and sends CRITICAL email
- [x] All connection references use correct `fsi_cr_*` logical names
- [x] No hardcoded tenant-specific values (all parameterized via variables)
- [x] JSON syntax valid (python json.load verification)

## Commit

```
feat(caa): add ELM provisioning hook child flow for zone CA verification
```

## Dependencies

- **03-01** (Start-CAAValidationRunbook): Runbook accepts `-Zone` and `-Scope Targeted` parameters; output schema consumed by Parse_Results
- **03-02** (Adaptive Card Template): Card structure adapted for provisioning context with zone-specific severity styling
- **03-03** (Daily Compliance Scan): Connection references, variable initialization, and Dataverse verification patterns reused
