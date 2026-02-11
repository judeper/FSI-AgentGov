---
phase: 3
plan: 3
status: complete
---

# Plan 03-03 Summary: Power Automate Daily Compliance Scan Flow

## Objective

Created a complete Power Automate cloud flow definition (Logic App workflow schema) that runs daily CA policy compliance validation via Azure Automation, verifies Dataverse audit records, and routes severity-classified alerts to Teams and email.

## What Was Done

### File Created

| File | Action | Lines |
|------|--------|-------|
| `src/caa-daily-compliance-flow.json` | CREATE | 1,331 |

### Flow Architecture

The flow definition follows the Logic App workflow schema (`2016-06-01`) and implements the full daily compliance scan lifecycle:

```
Recurrence (06:00 UTC daily)
  → Initialize 12 variables (config + card accumulators)
  → Scope_Try
      → Generate Job ID (GUID)
      → Create Azure Automation Job (HTTP PUT)
          Runbook: Start-CAAValidationRunbook
          Params: TenantId, ClientId, CertificateThumbprint, ConfigPath, DataverseUrl
      → Wait_Loop (Until Completed/Failed/Suspended, 30s delay, 2h timeout)
      → Check_Job_Status (If Completed)
          TRUE → Get_Job_Output → Parse_Results
              → Compute severity badge/color/style
              → Build violation/drift adaptive card arrays (Apply_to_Each)
              → Verify_Dataverse_Record (query + fallback create)
              → Check_Alert_Required (If true)
                  → Post Teams adaptive card
                  → Send HTML email alert
          FALSE → Send job failure email + Teams notification
  → Scope_Catch (on Scope_Try failure/timeout)
      → Send CRITICAL flow error email
```

### Connection References

| Logical Name | Connector | Usage |
|-------------|-----------|-------|
| `fsi_cr_dataverse_conditionalaccessautomation` | Dataverse | Validation history query/fallback write |
| `fsi_cr_office365_conditionalaccessautomation` | Office 365 | Alert + error emails |
| `fsi_cr_teams_conditionalaccessautomation` | Teams | Adaptive card + failure notifications |

### Key Design Decisions

1. **Audit-first verification**: Flow does NOT duplicate the Dataverse write (the runbook handles it). Flow only verifies the record exists and creates a fallback if the runbook crashed before writing.
2. **Managed Identity auth**: HTTP actions to Azure Management API use `ManagedServiceIdentity` authentication — no secrets stored in the flow.
3. **Sequential card building**: Apply_to_Each loops for violations and drift items run sequentially (`operationOptions: Sequential`) to preserve ordering in the adaptive card.
4. **Dual alert paths**: Job failure (automation-level) routes via simple Teams/email. Compliance violations (data-level) route via the full adaptive card + HTML email.
5. **No hardcoded values**: All tenant-specific values are initialized as variables, intended to be bound to Dataverse environment variables at deployment.

### Parse_Results Schema

Matches the Start-CAAValidationRunbook output exactly (Plan 03-01):
- Scalar fields: CheckedAt, TenantId, TotalPolicies, PassedCount, FailedCount, WarningCount, DriftCount, OverallSeverity, OverallStatus, ComplianceRate, AlertRequired, AlertSeverity
- Arrays: ZoneSummary[], Violations[], DriftItems[]
- Error fields: Error, ErrorDetails (optional, present on runbook error)

### Adaptive Card Integration

- Card body matches `src/adaptive-card-caa-alert.json` template structure (Plan 03-02)
- Scalar variables resolved via Parse_Results body expressions
- Violation/drift sections built dynamically via Apply_to_Each → AppendToArrayVariable
- Severity badge/color/style computed from OverallSeverity with threshold-based mapping
- Zone data extracted by array index (ZoneSummary guaranteed zone-ordered by runbook)

## Verification Checklist

- [x] Flow JSON validates against Logic App workflow schema
- [x] Daily recurrence trigger at 06:00 UTC
- [x] Azure Automation job creation with runbook `Start-CAAValidationRunbook`
- [x] Job polling loop: 30s delay, 240 iterations max, PT2H timeout
- [x] Parse_Results schema matches Plan 03-01 JSON output schema
- [x] Validation history record verified (written by runbook; fallback write if missing)
- [x] Teams adaptive card posted only when `AlertRequired=true`
- [x] Email sent only when `AlertRequired=true`
- [x] Error scope catches flow failures and sends CRITICAL email
- [x] All connection references use correct `fsi_cr_*` logical names
- [x] No hardcoded tenant-specific values (all parameterized via variables)
- [x] JSON syntax valid (python json.load verification)
- [x] `mkdocs build --strict` passes

## Commit

```
feat(caa): add Power Automate daily compliance scan flow definition
```

## Dependencies

- **03-01** (Start-CAAValidationRunbook): Runbook output schema consumed by Parse_Results
- **03-02** (Adaptive Card Template): Card structure replicated in Compose_Adaptive_Card with expression-based variable substitution
