# Troubleshooting — Control 3.5: Cost Allocation and Budget Tracking

> **Companion playbooks.** [Portal walkthrough](portal-walkthrough.md) · [PowerShell setup](powershell-setup.md) · [Verification & testing](verification-testing.md)
>
> **Sibling control references.** [Control 3.5 — Cost Allocation and Budget Tracking](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) · [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) · [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) · [Control 2.1 — Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md) · [Control 2.6 — Model Risk Management (OCC 2011-12, SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md)
>
> **Last UI verified:** April 2026.

---

!!! warning "Hedged language"
    The mitigations below **support compliance with** SOX 302/404, GLBA 501(b), OCC 2011-12, FINRA Rules 4511 and 3110, and SEC Rule 17a-4(b)(4). They do not "ensure" or "guarantee" compliance. Implementation requires named owners, quarterly drills, and recalibration as Microsoft surfaces evolve.

---

## Table of contents

| § | Scenario |
|---|----------|
| 0 | Triage tree and severity matrix |
| 1 | Diagnostic data collection — `Get-Fsi35*` helper catalogue |
| 2 | Scenario 1 — Costs not appearing in Cost Management |
| 3 | Scenario 2 — Variance >5 % between ledger and invoice |
| 4 | Scenario 3 — Untagged spend appears at month-end |
| 5 | Scenario 4 — Budget alerts not firing (or not received) |
| 6 | Scenario 5 — Budget alert fired but spend continued |
| 7 | Scenario 6 — Copilot billing policy assigned to wrong group |
| 8 | Scenario 7 — Copilot billing policy hit the 50-policy tenant limit |
| 9 | Scenario 8 — Cost Management export landed in mutable storage |
| 10 | Scenario 9 — Cost Management export missing days |
| 11 | Scenario 10 — Microsoft Graph license-utilization data is stale |
| 12 | Scenario 11 — Power Platform capacity returns empty (wrong shell) |
| 13 | Scenario 12 — Rate card missing or unsigned for the period |
| 14 | Scenario 13 — Chargeback ledger differs from BU's own records |
| 15 | Scenario 14 — Chargeback PDF not retained in WORM store |
| 16 | Scenario 15 — Power BI dashboard refresh failure |
| 17 | Scenario 16 — Sovereign-cloud surface absent (GCC / GCC High / DoD) |
| 18 | Scenario 17 — `New-AzCostManagementBudget` cmdlet not found |
| 19 | Scenario 18 — Audit Committee briefing missed AI-spend material increase |
| 20 | §SOV — Sovereign-cloud manual compensating controls |
| 21 | Escalation matrix |

---

## §0 Triage Tree and Severity Matrix

```text
Cost-governance defect detected
├── Spend >100% budget AND no enforcement triggered      ─► Sev-Critical (CFO + AI Gov + Compliance)
├── Variance >5% on chargeback close                     ─► Sev-High     (Finance + AI Gov, variance memo)
├── WORM retention not bound for export OR ledger        ─► Sev-High     (Compliance, Records Mgr)
├── Tag-policy NonCompliant >2 weekly cycles             ─► Sev-Medium   (Power Platform Admin)
├── Copilot policy assigned to wrong scope               ─► Sev-Medium   (AI Admin, change ticket required)
├── License utilization stale >7d (Graph lag)            ─► Sev-Low      (Platform engineering)
└── Sovereign-cloud surface absent (compensating ctrl OK)─► Sev-Info     (document, exercise quarterly)
```

| Severity | Notification window | Required artifacts |
|----------|---------------------|--------------------|
| Sev-Critical | Within 4 hours | Variance memo, root-cause memo, remediation plan, AI Governance Committee briefing record |
| Sev-High | Within 24 hours | Variance memo, remediation ticket |
| Sev-Medium | Within 5 business days | Remediation ticket |
| Sev-Low | Next monthly close | Operating-cadence note |
| Sev-Info | Next quarterly review | Documented in change log |

---

## §1 Diagnostic Data Collection — `Get-Fsi35*` Helper Catalogue

```powershell
# 1. Confirm shell host and module versions
Assert-Fsi35ShellHost -RequiredHost Core74
Test-Fsi35ModuleMatrix | Format-Table

# 2. Confirm sovereign cloud detection
Resolve-Fsi35CloudProfile -TenantId $env:FSI_TENANT

# 3. Confirm RBAC at scope
Test-Fsi35Rbac -SubscriptionId $env:FSI_SUB -Mode Read

# 4. End-to-end self-test
Invoke-Fsi35SelfTest `
    -SubscriptionId $env:FSI_SUB `
    -RequiredCostCenters @('CC-1001','CC-1002','CC-1003','CC-1004') `
    -ExportStorageAccountResourceId $env:FSI_EXPORT_SA_ID `
    -ExportContainerName 'cost-mgmt-exports' `
    -ScopeForTagPolicy $env:FSI_MG | ConvertTo-Json -Depth 6

# 5. Quick sanity query
Invoke-Fsi35CostQuery -Scope "/subscriptions/$env:FSI_SUB" `
    -From (Get-Date).AddDays(-7) -To (Get-Date) -GroupBy @('ServiceName')
```

The self-test rollup status (`Clean` / `Anomaly` / `Pending` / `NotApplicable` / `Error`) tells you which scenario below to consult first.

---

## §2 Scenario 1 — Costs Not Appearing in Cost Management

**Symptom.** A subscription with known AI workload activity (Copilot Studio messages, AI Builder credits, deployed Azure OpenAI) shows zero or near-zero cost in Cost Management for the period.

**Root causes (ordered by frequency).**

1. **Billing latency.** Cost Management lags real-time consumption by 8–48 hours; longer at month boundary.
2. **Wrong scope.** Querying at the subscription scope when the spend is at a sibling subscription within the same management group.
3. **PAYG billing policy invoiced to a different subscription.** The Copilot billing policy may be wired to a different Azure subscription than the one the operator is querying.
4. **`Cost Management Reader` role not assigned at the right scope.**
5. **Throttling returned HTTP 200 with empty rows** (see [Defect #4 in PowerShell §0](powershell-setup.md#02-false-clean-defect-catalogue-fsi35-specific)).

**Diagnostic.**

```powershell
# Confirm scope
Get-AzContext | Format-List Subscription, Tenant

# Confirm role
Test-Fsi35Rbac -SubscriptionId $env:FSI_SUB -Mode Read

# Test query at management-group scope to see if spend lives elsewhere
$mgScope = "/providers/Microsoft.Management/managementGroups/$env:FSI_MG"
Invoke-Fsi35CostQuery -Scope $mgScope -From (Get-Date).AddDays(-7) -To (Get-Date) `
    -GroupBy @('SubscriptionId','ServiceName')

# Check Copilot billing policy → subscription mapping
Invoke-MgGraphRequest -Method GET -Uri 'https://graph.microsoft.com/beta/copilot/billingPolicies' |
    Select-Object -ExpandProperty value | Select displayName, billingScope
```

**Resolution.**

- If billing latency: wait 48 h; rerun.
- If wrong scope: query at the management-group scope.
- If billing policy maps to an unexpected subscription: open a change ticket; confirm the mapping is intentional; update the §1.3 BU mapping table.
- If RBAC: request `Cost Management Reader` via PIM at the correct scope.

---

## §3 Scenario 2 — Variance >5 % Between Ledger and Invoice

**Symptom.** `Test-Fsi-Control35-InvoiceVariance` returns `Status='Anomaly'` with `VariancePct` > 5.

**Root causes.**

1. **Untagged spend not on the ledger.** The chargeback aggregates by tag; untagged resources are missed.
2. **Reservation amortization timing.** Amortized cost spreads reserved-instance pre-payments; the invoice is per-charge. Variances of 1–3 % from amortization are normal; >5 % is investigation-worthy.
3. **Cost-export missed days.** A scheduled export failed; the ledger is incomplete (see Scenario 9).
4. **Marketplace charges not visible to Cost Management.** Some third-party marketplace SKUs invoice separately.
5. **Currency rounding** at high transaction volumes.

**Diagnostic / resolution.**

```powershell
# 1. Pull untagged spend
$bu = Get-Fsi-CostByBusinessUnit -Scope $mgScope -From $start -To $end
$bu.Untagged   # Non-zero?

# 2. Compare amortized vs actual
Invoke-AzCostManagementQuery -Scope $mgScope -Type 'ActualCost' ...
Invoke-AzCostManagementQuery -Scope $mgScope -Type 'AmortizedCost' ...
# Difference = reservation effect; document.

# 3. Look for missed export days
$exports = Get-AzStorageBlob -Container 'cost-mgmt-exports' -Context $ctx |
    Where-Object Name -match "$year/$month"
$expectedDays = (Get-Date).DayOfMonth
($exports.Count) -ge $expectedDays  # If false → Scenario 9
```

**Action.**

- Open a variance memo regardless — FINRA 4511 wants a written record of any reconciliation exception.
- Resolve untagged spend before re-issuing the chargeback (do not silently bucket to `SHARED`).
- For marketplace charges, add a manual adjustment line to the ledger with documentation.

---

## §4 Scenario 3 — Untagged Spend Appears at Month-End

**Symptom.** `Get-Fsi-CostByBusinessUnit` returns `Untagged > 0`. Tag-policy compliance was reportedly clean during the month.

**Root causes.**

1. Resources created before the tag-policy `Deny` effect was applied (legacy / brownfield).
2. Resources created in subscriptions outside the policy assignment scope.
3. Resources created via legacy automation that bypassed Azure Resource Manager validation (rare).
4. **Tag inheritance not enabled** — resource group is tagged but the resource is not, and the inheritance policy is missing.

**Resolution.**

```powershell
# 1. Find untagged resources
Get-AzResource | Where-Object { -not $_.Tags.CostCenter } |
    Select Name, ResourceType, ResourceGroupName, Location

# 2. Apply tag inheritance from RG (one-shot remediation)
$assignment = Get-AzPolicyAssignment | Where-Object { $_.Properties.DisplayName -match 'Inherit' }
Start-AzPolicyRemediation -Name "remediate-tag-inherit-$(Get-Date -Format yyyyMMdd)" `
    -PolicyAssignmentId $assignment.PolicyAssignmentId
```

**Action.**

- Block chargeback issuance until untagged spend is resolved.
- If urgent close pressure: issue chargeback with an explicit `UNTAGGED-INVESTIGATION` line and document the deferral.

---

## §5 Scenario 4 — Budget Alerts Not Firing (or Not Received)

**Symptom.** Spend exceeded a threshold; no alert email received.

**Root causes.**

1. Wrong Azure budget scope (BU resource group is outside the budget filter).
2. Recipient list points to an old distribution group.
3. Microsoft delivery delay (alerts can take up to 8 h).
4. Email gateway filtered as spam.
5. Budget category set to `Usage` not `Cost`, so the threshold is unit-based not currency-based.

**Resolution.**

```powershell
Get-AzConsumptionBudget -ResourceGroupName $rg | Format-List `
    Name, Amount, Category, TimeGrain, CurrentSpend, Notification
```

Confirm:
- `Category = 'Cost'`
- Each notification's `ContactEmails` resolves
- `Threshold` is set as percentage (50 / 75 / 90 / 100)
- The scope filter matches the resource group housing the BU's spend

Test deliverability via the TC-5 quarterly drill.

---

## §6 Scenario 5 — Budget Alert Fired but Spend Continued

**Symptom.** Alert at 100 % was delivered; spend kept rising; month-end exceeded budget by 30 %.

**Root cause.** **Azure budgets are notification-only** — they do not enforce. The firm's enforcement mechanism (suspend agents, deactivate billing policy, remove from Entra ID group) was not triggered.

**Resolution.**

- Document the gap — this is an examiner finding waiting to happen.
- Implement an enforcement workflow:
  - **Soft enforcement:** an action group on the Azure budget alert that triggers a Logic App / Power Automate flow which deactivates the relevant Copilot billing policy or removes the BU's Entra ID group membership.
  - **Hard enforcement:** require pre-approval before any new agent in the affected environment.
- Document the enforcement owner in the budget description.
- Backfill: variance memo for the over-spend, with named accountability and the corrective action.

!!! danger "Examiner-facing risk"
    Sustained over-spend without enforcement is a SOX 404 ITGC weakness and an OCC 2011-12 third-party-risk concern. Address before the next exam cycle.

---

## §7 Scenario 6 — Copilot Billing Policy Assigned to Wrong Group

**Symptom.** A BU's chargeback understates (or overstates) consumption; users are unexpectedly metered against another BU's subscription.

**Root cause.** Copilot billing policy scope was assigned to the wrong Entra ID security group at creation, OR the security group's membership was changed without coordinating with cost governance.

**Resolution.**

- The Copilot billing policy's **scope assignment is immutable**. To change scope, the policy must be **deleted and recreated**.
- Open a change ticket (FINRA 3110 supervisory artifact).
- Coordinate the cutover: delete the misassigned policy → users immediately fall back to per-user M365 Copilot license metering or to other policies → recreate with correct scope.
- Update the §1.3 BU mapping table and the `copilot-billing-policy-register.csv`.
- Issue a corrective chargeback for prior periods if the misassignment was material.

---

## §8 Scenario 7 — Copilot Billing Policy Hit the 50-Policy Tenant Limit

**Symptom.** Cannot create a new Copilot billing policy; portal returns "policy limit reached."

**Root cause.** Tenants support up to **50 active Copilot billing policies**. The firm has accumulated retired or experimental policies that were never cleaned up.

**Resolution.**

- Audit the active policy register against the live tenant list.
- Identify policies marked `Retired` in the register that are still live.
- Delete retired policies (note: scope is immutable; deletion is the only "change scope" mechanism).
- Consolidate by joining smaller BUs onto a single policy with a parent security group.

---

## §9 Scenario 8 — Cost Management Export Landed in Mutable Storage

**Symptom.** `Test-Fsi-Control35-ExportImmutability` returns `Status='Anomaly'` with `Reason='Immutability policy missing'`.

**Root cause.** The export was created against a Storage container without an immutability policy, OR the policy expired / was removed.

**Resolution.**

- Treat all exports written to the mutable container as **operational data, not records**.
- Migrate exports to a properly-bound container:

```powershell
# Apply immutability policy
Set-AzRmStorageContainerImmutabilityPolicy `
    -ResourceGroupName $rg -StorageAccountName $sa `
    -ContainerName 'cost-mgmt-exports-immutable' `
    -ImmutabilityPeriod 2190
# Lock after burn-in
Lock-AzRmStorageContainerImmutabilityPolicy `
    -ResourceGroupName $rg -StorageAccountName $sa `
    -ContainerName 'cost-mgmt-exports-immutable' `
    -Etag $policy.Etag
# Recreate export
New-Fsi-CostExport -ExportName 'monthly-amortized' -Scope $mgScope `
    -StorageAccountResourceId $newSaId -ContainerName 'cost-mgmt-exports-immutable'
```

- File a Records Management exception memo for the period the export was non-records-grade. Cross-reference Control 1.9.

---

## §10 Scenario 9 — Cost Management Export Missing Days

**Symptom.** Daily-export blob count for the period is less than the number of days in the period.

**Root causes.**

1. Microsoft service incident on a particular day.
2. Storage account credentials rotated; export failed silently.
3. Export configuration was modified mid-period.

**Resolution.**

```powershell
# Identify missing dates
$blobs = Get-AzStorageBlob -Container 'cost-mgmt-exports-immutable' -Context $ctx |
    Where-Object Name -match "$year/$month"
$expectedDates = 1..[datetime]::DaysInMonth($year, $month)
$presentDates  = $blobs.Name | ForEach-Object { ($_ -replace '.*?(\d{2})\.parquet','$1') -as [int] } | Sort-Object -Unique
$missing = $expectedDates | Where-Object { $_ -notin $presentDates }
```

- Re-run the export for the missing date range with `New-AzCostManagementExport -RunOnce` (verify cmdlet name in your Az.CostManagement version).
- Document the gap and the backfill in the run's evidence row.

---

## §11 Scenario 10 — Graph License-Utilization Data Is Stale

**Symptom.** `Get-Fsi-CopilotLicenseUtilization` returns `Status='Pending'` with `Reason='Report refresh older than 72h'`.

**Root cause.** Microsoft Graph reports lag 24–72 h. Outside the window can indicate a tenant-wide reporting issue.

**Resolution.**

- Wait one cycle (24 h) and re-run.
- If still stale, file a Microsoft support ticket; reference the Graph reports endpoint.
- Suppress reclamation actions until data is fresh — acting on stale data leads to revoking active users' licenses.

---

## §12 Scenario 11 — Power Platform Capacity Returns Empty (Wrong Shell)

**Symptom.** `Get-AdminPowerAppEnvironment` returns `@()` against a tenant with known active environments.

**Root cause.** Running under PowerShell 7.4 instead of Windows PowerShell 5.1. `Microsoft.PowerApps.Administration.PowerShell` is Desktop-edition only.

**Resolution.** Run from a 5.1 sidecar:

```powershell
# Launch Windows PowerShell 5.1 explicitly
powershell.exe -NoProfile -File .\Get-Fsi-PowerPlatformCapacity.ps1 -OutputPath .\pp-capacity.json
```

Pipe the JSON output into the Pester suite running under PS 7.4 (Verification §2 TC-8).

---

## §13 Scenario 12 — Rate Card Missing or Unsigned for the Period

**Symptom.** `Get-Fsi35RateCard` returns `Status='Error'` (file not found) or `Status='Anomaly'` (missing signature metadata).

**Root cause.** Quarterly rate-card refresh was missed by the Controller, OR the signed file was uploaded without the `signedBy`/`signedDate` JSON fields.

**Resolution.**

- Block monthly close — do not issue chargeback against an unsigned rate card; it would not survive a SOX 404 walkthrough.
- Escalate to the Controller for sign-off.
- If the prior period's card is still valid by the firm's policy (e.g., "rates remain in force until superseded"), use the prior card and document the deferral in the run's evidence row.

---

## §14 Scenario 13 — Chargeback Ledger Differs from BU's Own Records

**Symptom.** BU finance partner disputes the monthly chargeback.

**Root causes.**

1. BU is double-counting (e.g., includes per-user Copilot seats already invoiced separately).
2. Cost-allocation taxonomy mismatch — BU's chart-of-accounts mapping was changed without updating §1.3.
3. The BU's own consumption tracking has lag or scope errors.
4. A cost-center reorganisation was effective mid-period.

**Resolution.**

- Walk through the ledger row using the §1.3 BU mapping table.
- Reconcile to the Cost Management view filtered by `CostCenter` tag.
- If the dispute is valid: revise the ledger, re-issue, retain both versions in evidence with a memo.
- If the dispute is invalid: respond with the rate-card and the ledger derivation; retain the response.

---

## §15 Scenario 14 — Chargeback PDF Not Retained in WORM Store

**Symptom.** Compliance Officer cannot find a retained chargeback PDF for a prior month during quarterly evidence sample.

**Root cause.** Retention label not applied; PDF was saved to a personal OneDrive or a non-labelled SharePoint library.

**Resolution.**

- Locate the original ledger CSV in the immutable Storage container (it should still exist if §9 is solid).
- Re-render the PDF.
- Apply the `FSI-Records-FinancialBooks` Purview retention label.
- Document the gap and remediation in the run's evidence row.
- Audit the close-month workflow: the close cannot be marked complete until the labelled PDF lands in the records library.

---

## §16 Scenario 15 — Power BI Dashboard Refresh Failure

**Symptom.** Power BI cost dashboard shows stale data; daily refresh failed.

**Root causes.**

1. Service principal credentials expired.
2. Cost Management connector permissions changed.
3. Workspace not in Premium / Premium-Per-User and dataset hit the refresh limit.

**Resolution.**

- Power BI is a downstream visualisation surface — chargeback is **not** dependent on the dashboard. Issue chargeback from the underlying Cost Management ledger.
- Restore Power BI on its own cadence; document the dashboard outage but do not block the financial close.

---

## §17 Scenario 16 — Sovereign-Cloud Surface Absent

**Symptom.** A surface this control depends on (e.g., M365 Copilot PAYG billing policies) is not generally available in your sovereign cloud.

**Root cause.** Sovereign-cloud parity gap.

**Resolution.** Route to **§SOV** below — implement the documented manual compensating control, exercise quarterly, retain the same evidence shape.

---

## §18 Scenario 17 — `New-AzCostManagementBudget` Cmdlet Not Found

**Symptom.** Script errors with "The term 'New-AzCostManagementBudget' is not recognized."

**Root cause.** **`New-AzCostManagementBudget` is not a GA cmdlet.** Earlier drafts of this playbook referenced it incorrectly.

**Resolution.** Use **`New-AzConsumptionBudget`** (Az.Billing module) instead. See [PowerShell §7.1](powershell-setup.md#71-create--update-budget-new-azconsumptionbudget). Update any local helpers that may have been copied from the older draft.

---

## §19 Scenario 18 — Audit Committee Briefing Missed Material Spend Increase

**Symptom.** AI spend increased >25 % YoY; not surfaced to Audit Committee in the quarterly safeguards briefing.

**Root causes.**

1. Audit Committee briefing template did not include AI cost line item.
2. AI Governance Lead was not invited to the briefing prep.
3. Materiality threshold for "report to AC" was set higher than the AI line warranted at the time of definition; AI now exceeds it.

**Resolution.**

- File a corrective briefing memo to the Audit Committee chair within 5 business days.
- Update the AC briefing template to include an "AI services consumption" line with YoY comparison.
- Recalibrate the materiality threshold for the AI line specifically.
- Cross-reference Control 2.6 (Model Risk Management) — material AI spend changes may also feed model-risk reassessment.

---

## §SOV Sovereign-Cloud Manual Compensating Controls

For tenants in GCC / GCC High / DoD where one or more of these surfaces is not at parity:

| Missing surface | Manual compensating control |
|-----------------|------------------------------|
| **M365 Copilot PAYG billing policies** | Per-seat chargeback driven by license assignment counts; rate per assigned seat per month from the rate card. Audit license assignments via Microsoft Graph (`LicenseAssignment.Read.All`) on the same monthly cadence. |
| **M365 Copilot Credit policies** | Manual prepaid pool tracking in a SharePoint list with quarterly Finance reconciliation. |
| **Cost Management Power BI connector** | Manual export to Excel; chargeback ledger built in Excel with formula audit; retain Excel + PDF. |
| **Storage immutability in DoD region** | Use immutability in Commercial-mirror tenant for evidence retention if permitted by data-residency policy; otherwise retain as records via tape archive or third-party 17a-4(f) vendor. Coordinate with General Counsel on residency. |
| **Microsoft 365 high-usage-users report** | Manual top-N analysis from license activity report; document the methodology. |

**Cadence.** Same as Commercial — monthly close, quarterly evidence pack. The compensating control's evidence shape must match the canonical schema (Verification §1) so the examiner can read sovereign and Commercial evidence interchangeably.

**Re-verify parity quarterly** via the [Microsoft 365 Government roadmap](https://aka.ms/m365gov-roadmap) and the [Azure Government services availability](https://learn.microsoft.com/en-us/azure/azure-government/documentation-government-services-supportstatus). When parity arrives, run the cutover and retire the manual compensating control with documented sign-off.

---

## §21 Escalation Matrix and Evidence-Collection Summary

| Issue | Escalate To | Response Time | Evidence to Capture |
|-------|-------------|---------------|---------------------|
| Spend over 100 % budget without enforcement | CFO / Controller + AI Governance Committee | 4 hours | Variance memo, alert evidence, root-cause memo |
| WORM binding missing for current period | Compliance Officer + Records Manager | 24 hours | Records-management exception memo, remediation ticket |
| Copilot policy misassignment material to chargeback | AI Administrator + Finance | 24 hours | Change ticket, corrected ledger, BU notification |
| Tag-policy non-compliance sustained >2 weeks | Power Platform Admin + AI Governance Lead | 5 BD | Compliance report, remediation tickets per resource |
| SOX 404 walkthrough finding | External auditor liaison + Internal Audit | Per audit calendar | Worked-example PDF, sign-off, management response |
| Sovereign parity gap impacts close | Microsoft account team + AI Governance Lead | Quarterly | Compensating-control documentation, exercise evidence |

All escalations land in the firm's incident or change-management system. The evidence captured here feeds the next quarterly evidence pack.

---

[Back to Control 3.5](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) · [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Verification & Testing](verification-testing.md)

---

*Updated: April 2026 | Version: v1.3.3*
