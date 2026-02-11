# Research: Phase 2 — Dataverse Infrastructure (CAA v10)

**Researched:** 2026-02-10
**Confidence:** HIGH (sixth iteration of proven ACV→SSC→AAM→CMM→FUS→CAA pattern)

## Phase Goal

CA policy baselines, validation history, and violation records are stored in Dataverse for persistent, queryable state across automated runs.

## Must-Haves

| # | Must-Have | Source |
|---|----------|--------|
| 1 | Three Dataverse tables (baseline, history [immutable], violations) with shared option sets | SC-1 |
| 2 | Environment variables (`fsi_CAA_*` prefix) for zone-specific CA policy thresholds | SC-2 |
| 3 | Connection references (`fsi_cr_*` naming) for Dataverse, Office 365, Teams, Graph | SC-3 |
| 4 | Python deployment scripts (idempotent, dry-run) following ACV/SSC/AAM pattern | SC-4 |

## Existing Tier 2 Pattern (Proven 5x)

### Standard 6-File Deployment Set

| File | Purpose |
|------|---------|
| `caa_client.py` | Dataverse Web API client (MSAL auth, retry, dry-run) |
| `create_dataverse_schema.py` | Table + shared option set deployment |
| `create_environment_variables.py` | Environment variable deployment |
| `create_connection_references.py` | Connection reference definitions |
| `deploy.py` | Orchestrator with full/selective modes |
| `requirements.txt` | `msal>=1.30.0`, `requests>=2.32.0` |

### CAAClient.psm1 Stubs (Phase 1)

8 function stubs awaiting Phase 2 implementation:

| # | Function | Purpose |
|---|----------|---------|
| 1 | `Connect-CAADataverse` | Establish Dataverse connection |
| 2 | `Get-CAAConnection` | Return connection status |
| 3 | `Get-CAAEnvironmentVariable` | Query `fsi_CAA_{Name}` env vars |
| 4 | `Get-CAAActiveBaseline` | Query active baselines |
| 5 | `Write-CAAValidationHistory` | POST immutable audit record |
| 6 | `Write-CAAViolation` | POST per-policy violation |
| 7 | `Save-CAABaseline` | POST new baseline, deactivate previous |
| 8 | `Get-CAALastValidation` | Query most recent validation |

### Shared Option Sets (owned by ACV, reused by all)

**`fsi_acv_zone`:** 0=Unclassified, 1=Zone 1, 2=Zone 2, 3=Zone 3
**`fsi_acv_severity`:** 1=Passed, 2=Warning, 3=GracePeriod, 4=Failed, 5=Error

Reuse pattern: check existence → reuse if found → create with canonical definition if not.

## CAA-Specific Schema Considerations

Unlike AAM/CMM/FUS (Power Platform environment/agent level), CAA operates at **Entra ID tenant level** against **CA policies**:

- **Baseline granularity:** Per-CA-policy (not per-environment)
- **Baseline columns:** `fsi_policy_id` (GUID), `fsi_policy_display_name`, `fsi_policy_state`, `fsi_conditions_json`, `fsi_grant_controls_json`, `fsi_session_controls_json`
- **Violation columns:** `fsi_policy_id`, `fsi_violation_type` (PolicyDisabled, ConditionWeakened, GrantControlRemoved, etc.), `fsi_expected_value`, `fsi_actual_value`
- **Validation history:** `fsi_total_policies` (not `fsi_total_environments`)

## Environment Variables

| Schema Name | Display Name | Type | Default | Purpose |
|-------------|-------------|------|---------|---------|
| `fsi_CAA_GracePeriodHours` | CAA - Grace Period (Hours) | Decimal | 48 | Hours before new policies validated |
| `fsi_CAA_ScanFrequencyHours` | CAA - Scan Frequency (Hours) | Decimal | 24 | Automated scan interval |
| `fsi_CAA_BaselineMaxAgeDays` | CAA - Maximum Baseline Age (Days) | Decimal | 30 | Stale baseline alert threshold |
| `fsi_CAA_DriftSeverityEscalation` | CAA - Drift Severity Escalation | String | true | Zone 3 drift severity +1 |
| `fsi_CAA_IncludeReportOnlyPolicies` | CAA - Include Report-Only Policies | String | true | Report-only CA policy inclusion |
| `fsi_CAA_TeamsGroupId` | CAA - Teams Alert Group ID | String | (blank) | Teams group GUID |
| `fsi_CAA_TeamsChannelId` | CAA - Teams Alert Channel ID | String | (blank) | Teams channel GUID |

## Connection References

| Logical Name | Connector ID | Purpose |
|-------------|-------------|---------|
| `fsi_cr_dataverse_conditionalaccessautomation` | `shared_commondataserviceforapps` | Baselines, history, violations |
| `fsi_cr_office365_conditionalaccessautomation` | `shared_office365` | Email alerts |
| `fsi_cr_teams_conditionalaccessautomation` | `shared_teams` | Adaptive card alerts |
| `fsi_cr_graph_conditionalaccessautomation` | `shared_microsoftgraphconnector` | CA policy reads in Power Automate |

**Note:** Graph connection reference is new to the pattern. Connector ID needs validation.

## Risks

| Risk | Mitigation |
|------|-----------|
| Graph connector ID uncertainty | Verify before deployment; OR deploy 3 proven + Graph placeholder |
| Entity set pluralization on history | Set `EntitySetName` explicitly |
| CAAClient.psm1 property key alignment | Cross-reference column schemas against stub signatures |
| Tenant-level vs environment-level granularity | Schema uses `fsi_policy_id` not `fsi_environment_guid` |

## Recommended Wave Structure

- **Wave 1:** Python client, requirements, three-table schema (foundation)
- **Wave 2:** Environment variables, connection references, deploy.py orchestrator
- **Wave 3:** CAAClient.psm1 stub implementation, Test-PolicyCompliance Dataverse wiring

---
*Research completed: 2026-02-10*
