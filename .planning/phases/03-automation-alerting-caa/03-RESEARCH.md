# Research: Phase 3 — Automation & Alerting (CAA v10)

**Researched:** 2026-02-10
**Confidence:** HIGH (seventh iteration of proven ACV→SSC→AAM→CMM→FUS→CAA pattern, Phase 1+2 complete)

## Phase Goal

CA policy compliance is automatically validated daily with drift detection, and operators receive classified alerts when policies deviate from zone requirements or are modified outside automation.

## Must-Haves

| # | Must-Have | Source |
|---|----------|--------|
| 1 | Power Automate daily compliance scan flow with Azure Automation runbook execution and Dataverse persistence | SC-1 |
| 2 | Multi-dimensional drift detection against stored Dataverse baselines in automated scan | SC-2 |
| 3 | Teams adaptive card alerts with zone-based severity classification (Zone 3 CRITICAL, Zone 2 HIGH, Zone 1 WARNING) | SC-3 |
| 4 | ELM provisioning hook verifying zone CA policy coverage on new environment provisioning | SC-4 |

## Current State (Phase 1+2 Complete)

### PowerShell Module (v1.1.0)

| File | Purpose | Status |
|------|---------|--------|
| `Test-PolicyCompliance.ps1` | 6 compliance checks + opt-in Dataverse persistence + drift analysis via `-BaselinePath` | Complete |
| `Deploy-CAPolicies.ps1` | Zone-appropriate CA policy deployment with WhatIf support | Complete |
| `Watch-PolicyDrift.ps1` | Drift monitoring orchestrator with summary banner and exit codes | Complete |
| `Export-PolicyBaseline.ps1` | Baseline capture from Graph API with ShouldProcess | Complete |
| `Register-ServicePrincipal.ps1` | Certificate-based auth setup with Key Vault integration | Complete |
| `CAAClient.psm1` | 8 Dataverse functions (Connect, Read, Write) — all stubs implemented | Complete |
| `conditional-access-automation.psd1` | Module manifest v1.1.0, exports 5 functions | Complete |

### Python Deployment (Phase 2)

| File | Purpose | Status |
|------|---------|--------|
| `caa_client.py` | Dataverse Web API client (MSAL auth, retry, dry-run) | Complete |
| `create_dataverse_schema.py` | 3 tables deployed (Baseline, ValidationHistory, Violation) | Complete |
| `create_environment_variables.py` | 7 env vars with `fsi_CAA_*` prefix | Complete |
| `create_connection_references.py` | 4 connection refs with `fsi_cr_*` naming | Complete |
| `deploy.py` | Orchestrator with selective modes and dry-run | Complete |

### Private Helpers (Companion Repo)

| File | Function | Used By |
|------|----------|---------|
| `Connect-GraphSession.ps1` | Graph session auth helper | Test-PolicyCompliance, Deploy-CAPolicies |
| `Get-ZoneClassification.ps1` | Zone lookup (ELM + naming fallback) | Deploy-CAPolicies |
| `Test-ParameterValidation.ps1` | Input validation | All public functions |
| `Get-PolicyBaseline.ps1` | `Get-CAAPolicyBaseline` — normalized policy snapshots | Watch-PolicyDrift, Test-PolicyCompliance |
| `Compare-PolicyBaseline.ps1` | `Compare-CAAPolicyBaseline` — 5-dimension comparison | Watch-PolicyDrift, Test-PolicyCompliance |

### Dataverse Tables (Phase 2)

| Table | Type | Columns | Purpose |
|-------|------|---------|---------|
| `fsi_CAPolicyBaseline` | UserOwned | 13 | Per-policy configuration snapshots |
| `fsi_CAPolicyValidationHistory` | OrganizationOwned | 11 | Immutable audit trail |
| `fsi_CAPolicyViolation` | UserOwned | 13 | Individual violation records |

### Environment Variables (Phase 2)

| Schema Name | Type | Default |
|-------------|------|---------|
| `fsi_CAA_GracePeriodHours` | Decimal | 48 |
| `fsi_CAA_ScanFrequencyHours` | Decimal | 24 |
| `fsi_CAA_BaselineMaxAgeDays` | Decimal | 30 |
| `fsi_CAA_DriftSeverityEscalation` | String | true |
| `fsi_CAA_IncludeReportOnlyPolicies` | String | true |
| `fsi_CAA_TeamsGroupId` | String | (blank) |
| `fsi_CAA_TeamsChannelId` | String | (blank) |

### Connection References (Phase 2)

| Logical Name | Connector |
|-------------|-----------|
| `fsi_cr_dataverse_conditionalaccessautomation` | shared_commondataserviceforapps |
| `fsi_cr_office365_conditionalaccessautomation` | shared_office365 |
| `fsi_cr_teams_conditionalaccessautomation` | shared_teams |
| `fsi_cr_graph_conditionalaccessautomation` | shared_microsoftgraphconnector |

## Technical Approach

### AUT-01: Daily Compliance Scan Flow

**Architecture:**
```
Power Automate Recurrence (06:00 UTC daily)
  → Initialize variables (DataverseUrl, TenantId, ClientId, CertThumbprint,
     SubscriptionId, ResourceGroup, AutomationAccount, TeamsGroupId, TeamsChannelId)
  → Scope_Try:
      → Create Azure Automation Job (Start-CAAValidationRunbook)
      → Do Until: Job completes (30s polling, 2h timeout)
      → If Failed → send CRITICAL alert
      → Get Job Output (JSON)
      → Parse Results (CAA-specific schema)
      → Write Validation History to Dataverse (audit-first, before alerting)
      → If AlertRequired → Route to Teams card + Email
  → Scope_Catch:
      → Send CRITICAL error email on flow failure
```

**Key difference from v8:** The `fsi_cr_graph_conditionalaccessautomation` connection reference is NOT used by the flow directly. CAA reads Graph API through Azure Automation (certificate-based auth in the runbook), not through a Power Automate Graph connector. The Graph connection ref exists for potential future direct-from-flow policy reads.

### AUT-02: Drift Detection in Automated Context

**Already implemented in Phase 1** — `Test-PolicyCompliance.ps1` Check 6 performs drift analysis when `-BaselinePath` is provided. The runbook wrapper extends this:

1. Reads active baselines from Dataverse (`Get-CAAActiveBaseline`) instead of requiring a local file path
2. Performs drift detection as part of every automated scan (not optional)
3. Classifies violations by type with structured output

**Violation types:**
- `PolicyDisabled` — policy state changed to disabled
- `ConditionWeakened` — user/application conditions narrowed
- `GrantControlRemoved` — MFA or block control removed
- `SessionControlWeakened` — sign-in frequency increased, persistent browser enabled
- `PolicyMissing` — expected policy not found
- `BreakGlassExclusionMissing` — break-glass account not excluded

**Drift severity mapping:**

| Violation Type | Base Severity | Zone 3 Escalation |
|----------------|---------------|-------------------|
| PolicyDisabled | 4 (Failed) | 5 (Error) = CRITICAL |
| GrantControlRemoved | 4 (Failed) | 5 (Error) = CRITICAL |
| ConditionWeakened | 3 (GracePeriod) | 4 (Failed) = HIGH |
| PolicyMissing | 4 (Failed) | 5 (Error) = CRITICAL |
| SessionControlWeakened | 3 (GracePeriod) | 4 (Failed) = HIGH |
| BreakGlassExclusionMissing | 4 (Failed) | 5 (Error) = CRITICAL |

### AUT-03: Teams Adaptive Card Alerts

**Card structure (Adaptive Card v1.4):**
```
╔═══════════════════════════════════════════════════╗
║ [ALERT] CA Policy Compliance — {SEVERITY}         ║
╠═══════════════════════════════════════════════════╣
║ Run Summary                                       ║
║   Status: {OverallStatus}  Time: {CheckedAt}      ║
║   Policies: {TotalPolicies}  Gaps: {TotalGaps}    ║
║   Drift: {DriftCount}  Severity: {OverallSeverity}║
╠═══════════════════════════════════════════════════╣
║ Zone Compliance                                   ║
║   Zone 1: {Pass}/{Total}  WARNING                 ║
║   Zone 2: {Pass}/{Total}  HIGH                    ║
║   Zone 3: {Pass}/{Total}  CRITICAL                ║
╠═══════════════════════════════════════════════════╣
║ Violations                                        ║
║   • PolicyDisabled: {PolicyName} · Zone {N}       ║
║   • DriftDetected: {PolicyName} · {Direction}     ║
╠═══════════════════════════════════════════════════╣
║ [View in Entra Portal] [Run Manual Check] [Docs]  ║
╚═══════════════════════════════════════════════════╝
```

### AUT-04: ELM Provisioning Hook

**Critical difference from other solutions:** CAA operates at the Entra ID tenant level, not per-environment. CA policies target applications and security groups — not single environments. The hook follows a **verify-on-provision** pattern:

```
ELM ProvisioningCompleted event
  → CAA Provisioning Hook (child flow)
  → Get environment zone from ELM request
  → Run targeted compliance check:
      1. Verify zone CA policies exist and are enabled
      2. Verify break-glass exclusions are intact
      3. Verify grant/session controls meet zone requirements
  → If gaps found:
      → Write violations to Dataverse
      → Send zone-appropriate severity alert
  → If all clear:
      → Log verification record to validation history
```

## Differences from v8 (FUS) Pattern

| Aspect | v8 FUS | v10 CAA |
|--------|--------|---------|
| **Scope** | Per-environment + per-agent scanning | Per-tenant scanning (one Entra, 8 expected policies) |
| **API** | Power Platform Admin API | Graph API `conditionalAccessPolicies` (via Azure Automation) |
| **Drift model** | Binary (file upload enabled/disabled) | Multi-dimensional (state, conditions, grants, sessions, add/remove) |
| **Runbook complexity** | Per-environment loop, per-agent results | Single tenant scan, per-policy results |
| **ELM hook** | Not in v8 Phase 3 | AUT-04: verify-on-provision pattern |
| **Plan count** | 3 plans | 4 plans |
| **Wave order** | Flow+Card (W1) → Runbook (W2) | Runbook+Card (W1) → Flow+ELM (W2) |

### Why wave order is reversed from v8

In v8, the runbook was an adapter wrapping a compliance script for Azure Automation execution. In CAA, the runbook is the **primary execution engine** because all Graph API policy reads flow through it. The flow is a thin orchestrator. Building the runbook first ensures the JSON output schema is defined before the flow's `Parse_Results` action is configured.

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Missing private helper scripts in worktree | HIGH | Runbook wrapper dot-sources module; helpers exist in companion repo and are in module's NestedModules |
| Tenant-level vs environment-level mismatch | MEDIUM | Flow scans one tenant per run (simpler than multi-environment loop); ELM hook runs targeted zone verification |
| Azure Automation infrastructure dependency | MEDIUM | Document prerequisites; `Register-ServicePrincipal.ps1` handles cert setup; runbook deployment can be scripted |
| Graph API permissions | MEDIUM | Default to `Policy.Read.All` (read-only verify); document `Policy.ReadWrite.ConditionalAccess` as optional for deploy-on-provision |
| ELM hook design (CA policies not 1:1 with environments) | MEDIUM | Frame as "verify on provision" — confirm zone coverage exists, not deploy per-environment |

## Recommended Wave Structure

### Wave 1 (independent, parallel)

| Plan | Title | Requirements |
|------|-------|-------------|
| 03-01 | Azure Automation Runbook Wrapper | AUT-01 (partial), AUT-02 |
| 03-02 | Teams Adaptive Card Template | AUT-03 |

### Wave 2 (depends on Wave 1)

| Plan | Title | Requirements |
|------|-------|-------------|
| 03-03 | Power Automate Daily Compliance Flow | AUT-01 |
| 03-04 | ELM Provisioning Hook Flow | AUT-04 |

---
*Research completed: 2026-02-10*
