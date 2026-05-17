# Verification & Testing — Control 3.5: Cost Allocation and Budget Tracking

> **Examiner-defensible evidence package** for Control 3.5. This playbook produces, signs, and retains the artifacts required to demonstrate to FINRA, the SEC, the OCC, the Federal Reserve, the FDIC (FFIEC member agencies), state banking regulators, external auditors performing SOX 404 walkthroughs, and the firm's Audit Committee that AI-agent-related Microsoft consumption is captured, attributed, charged back, retained as books-and-records under SEC Rule 17a-4(b)(4) / FINRA Rule 4511, and reconciled to invoices on the firm's financial close cadence.
>
> **Scope:** Microsoft 365 Commercial, GCC, GCC High, and DoD tenants. China (21Vianet) is out of scope. Where Microsoft 365 Copilot PAYG / Credit billing policies, the Cost Management connector, or the Storage immutability surface have parity gaps in sovereign clouds, this playbook routes the test to the §SOV manual compensating-control namespace; see TC-12.
>
> **Companion controls:**
>
> - Source of `CostCenter` / `BusinessUnit` / `Owner` tags: [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
> - Usage volume that drives consumption: [Control 3.2 — Usage Analytics and Activity Monitoring](../../../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md)
> - Environment structure that bounds attribution: [Control 2.1 — Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md)
> - WORM retention surface for chargeback artifacts: [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)
> - Model-risk cost-benefit input: [Control 2.6 — Model Risk Management](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md)
>
> **Last UI Verified:** April 2026 against Microsoft 365 admin center, Power Platform admin center, Azure portal (Cost Management + Billing), Microsoft Purview portal, and Microsoft Graph reports `v1.0` surfaces. Re-verify each cycle before relying on automated paths.

---

!!! warning "Non-Substitution — Tooling Supports, It Does Not Replace"
    The Pester suites, evidence-pack assembler, and SHA-256 manifest emitters in this playbook are **financial-evidence collection surfaces**. They support compliance with — and do not replace:

    - The firm's **written cost-allocation methodology**, approved by the Controller / CFO and subject to external-audit walkthrough each fiscal year.
    - **Books-and-records retention** under SEC Rule 17a-4(b)(4) — chargeback ledgers, rate cards, variance memos, and the underlying Cost Management exports must land in WORM-equivalent storage. A Pester `Should -Pass` against a non-immutable target is **not** an evidence record.
    - **Registered-principal supervisory review** under FINRA Rule 3110 of changes to billing policies, rate cards, and the cost-allocation taxonomy.
    - **External auditor sign-off** on SOX 404 ITGC walkthroughs.
    - **Hard cost caps.** No test in this playbook stops spend; tests confirm that *notification* surfaces are configured and firing.

    A clean PASS across TC-1 through TC-12 produces an examiner-defensible evidence package. It does not by itself ensure compliance with any single regulation.

!!! warning "Sovereign Cloud Availability — GCC, GCC High, DoD"
    The following surfaces touched by this playbook may have parity gaps as of April 2026; tests detect and route to TC-12 (manual compensating control) rather than failing:

    - **Microsoft 365 Copilot PAYG billing policies** — verify GA in target sovereign cloud
    - **Microsoft 365 Copilot Credit policies (April 2026 GA)** — sovereign GA dates pending
    - **Cost Management Power BI connector** — generally available; verify dataset coverage
    - **Storage immutability policy in DoD regions** — verify region-by-region

---

## Document Conventions

| Convention | Value |
|------------|-------|
| PowerShell baseline | PS 7.4+ Core; `#Requires -Version 7.4`. See [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md). |
| Test framework | Pester 5.5+. Every `Should` has an explicit `-Because` clause for examiner traceability. |
| Output discipline | No `Write-Host` in evidence-emitting scripts. All evidence is `[pscustomobject]` via `Write-Output`, then JSON-serialised with `ConvertTo-Json -Depth 10`. |
| Hedged regulatory language | Tests **support compliance with** the cited regulations. They do not "ensure," "guarantee," or "prevent." |
| Run identifier | Every test run is tagged `AGT35-yyyyMMdd-HHmmss-<8charGuid>`; the tag is embedded in every evidence record and artifact filename. |
| Evidence retention | 6 years on WORM-equivalent storage for the full signed evidence pack — aligning to FINRA Rule 4511 / SEC Rule 17a-4(b)(4)(f). The firm's records-retention schedule may extend this. |
| Variance threshold | ±5 % between Cost Management ledger total and the Microsoft Customer Agreement / EA invoice for the same period. Threshold is a default; the Controller may set a tighter or looser threshold and document the rationale. |
| Canonical roles | Per [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). Use the canonical short names (`AI Administrator`, `Power Platform Admin`, `Compliance Officer`, etc.). |
| Cadence | TC-1 / TC-2 / TC-3 monthly; TC-4 / TC-5 / TC-6 quarterly; TC-7 / TC-8 quarterly; TC-9 / TC-10 monthly; TC-11 annual; TC-12 quarterly (sovereign tenants) |

---

## §0 Pre-Test Prerequisites

### 0.1 Operator role prerequisites

| Test | Required role | Scope |
|------|---------------|-------|
| TC-1 to TC-3 (Cost queries, exports, immutability) | `Cost Management Reader` + read on the Storage account | Subscription / management group |
| TC-4 (Budget coverage) | `Cost Management Reader` | Subscription |
| TC-5 (Tag-policy compliance) | `Resource Policy Reader` | Management group |
| TC-6 (Copilot billing policy register) | `AI Administrator` (read-only) | Tenant |
| TC-7 (License utilization) | Microsoft Graph `Reports.Read.All`, `LicenseAssignment.Read.All` | Tenant |
| TC-8 (Power Platform capacity) | `Power Platform Admin` (PIM-elevated) | Tenant |
| TC-9 (Rate-card retrieval) | Read on rate-card storage | Storage container |
| TC-10 (Chargeback ledger) | Aggregate of TC-1 + TC-9 | All |
| TC-11 (SOX 404 sample walkthrough) | `Compliance Officer` + observer | Documented |
| TC-12 (Sovereign compensating control) | Per-cloud — see TC-12 section | Per cloud |

All Pester suites are read-only with respect to production financial data; mutation tests run only in the dedicated cost-test sandbox subscription tagged `Environment=CostTest`.

### 0.2 Bootstrap

```powershell
#Requires -Version 7.4
. ./Initialize-Fsi35Session.ps1   # from PowerShell setup §2

$session = Initialize-Fsi35Session -TenantId $env:FSI_TENANT -SubscriptionId $env:FSI_SUB
if ($session.Status -ne 'Clean') { throw "Bootstrap failed: $($session.Reason)" }

$RunId = "AGT35-$((Get-Date).ToString('yyyyMMdd-HHmmss'))-$((New-Guid).Guid.Substring(0,8))"
$EvidenceRoot = Join-Path $env:FSI_EVIDENCE_ROOT $RunId
New-Item -ItemType Directory -Path $EvidenceRoot -Force | Out-Null
```

---

## §1 Evidence Schema

Every test emits one row of the canonical schema. The schema is the contract between this playbook and the examiner-facing evidence pack.

```json
{
  "RunId":            "AGT35-20260505-080132-a1b2c3d4",
  "Control":          "3.5",
  "TestCase":         "TC-1",
  "TestCaseTitle":    "Cost Management variance vs invoice",
  "Status":           "Clean | Anomaly | Pending | NotApplicable | Error",
  "Reason":           "<empty when Clean>",
  "Cloud":            "Commercial | GCC | GCCHigh | DoD",
  "Scope":            "/providers/Microsoft.Management/managementGroups/...",
  "PeriodStart":      "2026-04-01T00:00:00Z",
  "PeriodEnd":        "2026-04-30T23:59:59Z",
  "InvoiceTotalUSD":  12345.67,
  "LedgerTotalUSD":   12289.10,
  "VariancePct":      -0.46,
  "EvidenceArtifacts":[
    { "file":"ledger-2026-04.csv",      "sha256":"…", "sizeBytes":… },
    { "file":"variance-memo-2026-04.pdf","sha256":"…", "sizeBytes":… }
  ],
  "OperatorUPN":      "ai-admin@example.com",
  "CapturedUtc":      "2026-05-05T08:01:32Z",
  "ToolingHash":      "<sha256 of the helper module bundle>",
  "Note":             "<free-text caveat or explanation>"
}
```

The `ToolingHash` lets the examiner reproduce the run three years later against the same helper bundle.

---

## §2 Test Cases

### TC-1 — Cost Management ledger variance vs invoice

**Objective.** Confirm the Cost Management amortized-cost ledger for the period is within ±5 % of the Microsoft invoice. Demonstrates the firm has captured all Microsoft AI consumption in its books and can reconcile to Microsoft's invoicing system.

**Cadence.** Monthly, by the 5th business day after invoice receipt.

**Steps.**

1. Pull invoice total for the period (manual: from EA portal or MCA Invoices). Record as `InvoiceTotalUSD`.
2. Run `Get-Fsi-MonthlyChargeback -ManagementGroupId $mg -Year 2026 -Month 4 ...`.
3. Run `Test-Fsi-Control35-InvoiceVariance -LedgerTotal $ledger.Total -InvoiceTotal $invoice`.
4. Emit evidence row.

**Pester.**

```powershell
Describe 'TC-1: Cost ledger reconciles to Microsoft invoice within 5%' {
    BeforeAll {
        $script:ledger = Get-Fsi-MonthlyChargeback `
            -ManagementGroupId $env:FSI_MG -Year 2026 -Month 4 `
            -RateCardStorageAccount $env:FSI_RC_SA -RateCardContainer 'rate-cards'
        $script:invoice = [decimal]$env:FSI_APR_INVOICE_USD
        $script:result  = Test-Fsi-Control35-InvoiceVariance -LedgerTotal $ledger.Total -InvoiceTotal $invoice
    }

    It 'Ledger totalled cleanly (no untagged spend)' -Because 'SOX 404 requires complete attribution; untagged spend breaks the audit trail' {
        $ledger.Status | Should -Be 'Clean'
    }

    It 'Variance within ±5%' -Because 'Variance >5% indicates incomplete cost capture or rate-card error; both are SOX 404 deficiencies' {
        $result.Status | Should -Be 'Clean'
    }

    It 'Variance memo exists when variance > threshold' {
        if ($result.Status -eq 'Anomaly') {
            $memoPath = Join-Path $env:FSI_EVIDENCE_ROOT "variance-memo-2026-04.pdf"
            Test-Path $memoPath | Should -BeTrue -Because 'FINRA 4511 requires written record of financial reconciliation exceptions'
        }
    }
}
```

**Failure modes.**

- `Status='Anomaly'` with `VariancePct > 5` — open variance memo, escalate to Finance + AI Governance Lead.
- `Status='Anomaly'` with `Reason='Untagged spend present'` — block chargeback issuance until tagging is remediated; do not silently absorb to `SHARED`.
- `Status='Error'` with HTTP 429 — retry after backoff; if persistent, contact Microsoft support with correlation IDs.

---

### TC-2 — Cost-export immutability binding

**Objective.** Confirm the Storage container receiving Cost Management exports has an active immutability policy with retention ≥6 years. Demonstrates the exports qualify as 17a-4(b)(4) records.

**Cadence.** Monthly (configuration drift detection).

**Pester.**

```powershell
Describe 'TC-2: Cost export container is immutable' {
    BeforeAll {
        $script:imm = Test-Fsi-Control35-ExportImmutability `
            -StorageAccountResourceId $env:FSI_EXPORT_SA_ID `
            -ContainerName 'cost-mgmt-exports'
    }

    It 'Immutability policy is present' -Because '17a-4(b)(4) requires non-rewriteable, non-erasable storage of financial records' {
        $imm.Status | Should -Be 'Clean'
    }

    It 'Immutability policy is Locked (not Unlocked)' -Because 'Unlocked policies can be shortened or removed; locked is records-grade' {
        $imm.PolicyState | Should -Be 'Locked'
    }

    It 'Retention ≥ 2190 days (6 years)' -Because 'FINRA 4511 / 17a-4 default retention period for financial records' {
        $imm.RetentionDays | Should -BeGreaterOrEqual 2190
    }
}
```

---

### TC-3 — Tag-policy compliance ≥99 %

**Objective.** Confirm Azure Policy enforces the cost-allocation tag set; non-compliant resources are flagged within one weekly cycle.

**Cadence.** Monthly.

```powershell
Describe 'TC-3: Cost-allocation tags enforced' {
    BeforeAll {
        $script:r = Test-Fsi-Control35-TagPolicyCompliance -ScopeId $env:FSI_MG
    }

    It 'Tag-enforcement assignments exist for required tags' {
        $r.AssignmentsCount | Should -BeGreaterOrEqual 5 -Because 'CostCenter, BusinessUnit, Zone, Owner, Application all required'
    }

    It 'Non-compliant resource count ≤ 1% of total' {
        # Examiner-facing — exact threshold per firm risk appetite
        $r.NonCompliantCount | Should -BeLessOrEqual ([math]::Ceiling(($env:FSI_TOTAL_RESOURCES) * 0.01))
    }
}
```

**Failure mode.** Sustained non-compliance is an examiner-visible defect. Any resource non-compliant for >2 weekly cycles must have a remediation ticket linked in the evidence row.

---

### TC-4 — Budget coverage ≥1-per-BU

**Objective.** Every business unit with active AI consumption has at least one Azure budget at the 100 % threshold.

```powershell
Describe 'TC-4: Budget coverage per BU' {
    It 'No required cost center is missing a budget' -Because 'Budgets are the firm''s notification trip-wire; missing budgets = silent overruns' {
        $r = Test-Fsi-Control35-BudgetCoverage -RequiredCostCenters @(
            'CC-1001','CC-1002','CC-1003','CC-1004'
        )
        $r.Status | Should -Be 'Clean'
    }
}
```

---

### TC-5 — Threshold alerts have fired (live or drill)

**Objective.** Confirm the alert distribution path is operational. Test in drill mode: create a $1 budget at the 1 % threshold against an idle resource group, generate $0.02 of spend, confirm the alert email is delivered to all configured recipients.

**Cadence.** Quarterly.

**Procedure.**

1. Create test budget `Fsi35-Drill-Q-{quarter}` at $1.00 monthly with 1 / 50 / 75 / 100 % thresholds.
2. Trigger spend by deploying a single B1s VM for 1 hour (≈ $0.01).
3. Wait up to 8 hours for budget alert to fire (Microsoft SLA varies).
4. Confirm receipt at: BU-owner mailbox, Finance shared mailbox, AI Governance Lead, Compliance Officer.
5. Capture screenshots / message IDs as evidence; include in the run's evidence pack.
6. Delete the drill budget and the B1s VM.

**Pester (assertion-only; the drill is manual).**

```powershell
Describe 'TC-5: Budget alerts deliverable' {
    It 'Drill alert was received by all recipients' {
        # Operator records receipt manually; this test reads the operator's signed evidence form
        $form = Get-Content "$env:FSI_EVIDENCE_ROOT/tc5-drill-form.json" | ConvertFrom-Json
        $form.AllRecipientsConfirmed | Should -BeTrue -Because 'Notification-only controls require deliverability proof'
    }
}
```

---

### TC-6 — Copilot billing policy register matches portal

**Objective.** The firm-maintained register of Copilot billing policies matches the live tenant configuration.

```powershell
Describe 'TC-6: Copilot billing policy register reconciles' {
    BeforeAll {
        # Live policies via Graph (read-only)
        $script:livePolicies = Invoke-MgGraphRequest -Method GET -Uri 'https://graph.microsoft.com/beta/copilot/billingPolicies'
        $script:registerPath = "$env:FSI_REGISTERS/copilot-billing-policy-register.csv"
        $script:register      = Import-Csv $registerPath
    }

    It 'No policy in the live tenant is missing from the register' -Because 'Unregistered policies indicate an out-of-process change (FINRA 3110 finding)' {
        $missing = $livePolicies.value | Where-Object { $_.id -notin $register.PolicyId }
        $missing.Count | Should -Be 0
    }

    It 'No retired policy in the register is still live' -Because 'Stale policy assignments may invoice the wrong cost center' {
        $stale = $register | Where-Object { $_.Status -eq 'Retired' -and $_.PolicyId -in $livePolicies.value.id }
        $stale.Count | Should -Be 0
    }

    It 'Active policy count ≤ 50 (tenant maximum)' {
        ($livePolicies.value | Where-Object state -eq 'enabled').Count | Should -BeLessOrEqual 50
    }
}
```

---

### TC-7 — License utilization (idle Copilot seats)

```powershell
Describe 'TC-7: Copilot license utilization' {
    BeforeAll {
        $script:u = Get-Fsi-CopilotLicenseUtilization -Days 30
    }

    It 'Report data is fresh (within 72h lag)' {
        $u.Status | Should -Be 'Clean' -Because 'Stale data leads to incorrect reclamation decisions'
    }

    It 'Utilization is reported (not null)' {
        $u.UtilizationPct | Should -BeGreaterOrEqual 0
    }

    It 'Idle-seat report is produced' {
        $u.IdleOver30Days | Should -BeOfType [int]
    }
}
```

The idle-seat list is consumed by the monthly reclamation process. The test does not assert a target utilization — that is a firm risk-appetite decision.

---

### TC-8 — Power Platform capacity headroom

```powershell
Describe 'TC-8: Power Platform capacity headroom' {
    BeforeAll {
        # Run from a PS 5.1 sidecar; the sidecar emits JSON the test consumes
        $script:cap = Get-Content "$env:FSI_EVIDENCE_ROOT/pp-capacity.json" | ConvertFrom-Json
    }

    It 'No environment exceeds 95% of any capacity bucket' -Because 'New agents will fail to deploy at saturation' {
        $bad = $cap.Rows | Where-Object {
            $_.DatabaseSizeMB / $_.DatabaseQuotaMB -gt 0.95
        }
        $bad.Count | Should -Be 0
    }
}
```

---

### TC-9 — Rate card current and signed

```powershell
Describe 'TC-9: Rate card valid for the period' {
    It 'Rate card exists for the current period' {
        $card = Get-Fsi35RateCard -StorageAccountName $env:FSI_RC_SA `
                    -ContainerName 'rate-cards' -EffectiveDate (Get-Date -Format 'yyyy-MM-01')
        $card.Status | Should -Be 'Clean'
    }

    It 'Rate card is signed by an authorised approver' -Because 'CFO/Controller sign-off is a SOX 404 control' {
        $card = Get-Fsi35RateCard -StorageAccountName $env:FSI_RC_SA `
                    -ContainerName 'rate-cards' -EffectiveDate (Get-Date -Format 'yyyy-MM-01')
        $card.SignedBy | Should -BeIn @('controller@example.com','cfo@example.com')
    }
}
```

---

### TC-10 — Monthly chargeback ledger end-to-end

```powershell
Describe 'TC-10: Monthly chargeback ledger end-to-end' {
    BeforeAll {
        $script:ledger = Get-Fsi-MonthlyChargeback `
            -ManagementGroupId $env:FSI_MG -Year 2026 -Month 4 `
            -RateCardStorageAccount $env:FSI_RC_SA -RateCardContainer 'rate-cards'
    }

    It 'Ledger produced cleanly' { $ledger.Status | Should -Be 'Clean' }

    It 'Every required cost center is on the ledger' {
        $required = @('CC-1001','CC-1002','CC-1003','CC-1004')
        $missing = $required | Where-Object { $_ -notin $ledger.Ledger.CostCenter }
        $missing.Count | Should -Be 0
    }

    It 'Chargeback IDs follow the canonical format' {
        $ledger.Ledger.ChargebackId | ForEach-Object {
            $_ | Should -Match '^CB-\d{6}-CC-\d{4}$'
        }
    }
}
```

---

### TC-11 — Annual SOX 404 evidence sample walkthrough

**Objective.** Produce one complete worked example for external audit: one billing policy → one budget → one ledger row → one variance memo → one signed evidence manifest.

**Cadence.** Annual (or per external auditor request).

**Procedure.**

1. Pick one cost center at random from the active register.
2. Walk the auditor through:
   - The chart-of-accounts entry for the cost center
   - The Entra ID security group bound to the Copilot billing policy
   - The Azure budget threshold and notification distribution
   - One month's Cost Management ledger row for that cost center
   - The variance memo for the period (or the absence-of-variance attestation)
   - The signed PDF chargeback delivered to the BU owner
   - The retention label applied and the immutable storage location
3. Capture: the auditor's question list, the operator's responses, and the auditor sign-off.

**Evidence row Status.** `Clean` only if the auditor signs the worksheet without exceptions.

---

### TC-12 — Sovereign cloud compensating control

**Objective.** For tenants in GCC / GCC High / DoD where one or more surfaces this playbook depends on are not at parity, demonstrate the firm has a documented manual compensating control, exercises it on the same cadence, and produces equivalent evidence.

**Cadence.** Quarterly for sovereign tenants.

**Procedure.**

1. Identify which surfaces are non-parity for the current cloud (consult Microsoft account team, [Microsoft 365 Government roadmap](https://aka.ms/m365gov-roadmap), and the [Azure Government services availability](https://learn.microsoft.com/en-us/azure/azure-government/compare-azure-government-global-azure)).
2. For each gap, document the manual compensating control:
   - **No M365 Copilot PAYG in DoD** → manual seat-based chargeback driven by license assignment; rate per assigned seat per month.
   - **No Cost Management Power BI connector for the relevant scope** → manual export to Excel; chargeback ledger built in Excel with formula audit.
3. Run the manual procedure for the period.
4. Emit an evidence row with `Status='Clean'` and `Cloud='GCCHigh'` (etc.); the `Note` field describes which surface was substituted.

---

## §3 Evidence-Pack Assembly

```powershell
$evidence = @(
    'tc1-variance.json',
    'tc2-immutability.json',
    'tc3-tagpolicy.json',
    'tc4-budget-coverage.json',
    'tc5-drill-form.json',
    'tc6-policy-register.json',
    'tc7-license-util.json',
    'tc8-pp-capacity.json',
    'tc9-rate-card.json',
    'tc10-ledger.csv',
    'tc11-sox-walkthrough.pdf',
    'tc12-sovereign-compensating.json'
) | ForEach-Object { Join-Path $EvidenceRoot $_ } | Where-Object { Test-Path $_ }

$manifest = New-Fsi-Control35-EvidenceManifest `
                -Files $evidence `
                -OutputManifestPath (Join-Path $EvidenceRoot 'manifest.json') `
                -RunId $RunId

# Upload the entire $EvidenceRoot to the immutable storage container.
$ctx = New-AzStorageContext -StorageAccountName $env:FSI_EVIDENCE_SA -UseConnectedAccount
Get-ChildItem $EvidenceRoot -Recurse | ForEach-Object {
    Set-AzStorageBlobContent -Context $ctx -Container 'evidence' `
        -File $_.FullName -Blob "control-3.5/$RunId/$($_.Name)" -Force
}
```

---

## §4 Examiner Walkthrough — Reading the Evidence Pack

Hand the examiner the following, in order:

1. **`manifest.json`** — proves what was emitted, when, by whom, and the SHA-256 of every artifact.
2. **`tc1-variance.json`** — the headline reconciliation. Examiner should focus on `VariancePct` and the absence/presence of a variance memo.
3. **`tc2-immutability.json`** — proves the records-retention binding. Examiner will likely cross-check against the firm's records-retention schedule.
4. **`tc10-ledger.csv`** — the actual chargeback for the period.
5. **`tc11-sox-walkthrough.pdf`** — for SOX 404 sample-of-one.
6. **All others** — supporting context.

The examiner's most common follow-up: "Show me a non-Clean run from the past 12 months and what the firm did about it." Maintain a running register of `Anomaly` / `Error` runs and the corresponding remediation tickets.

---

## §5 Cross-Control Referrals Generated by This Playbook

| Trigger | Referral target | Notes |
|---------|-----------------|-------|
| TC-3 sustained non-compliance | Control 3.1 (Agent Inventory) | Tag values are owned by the inventory metadata model |
| TC-6 unregistered live policy | Control 2.12 (Supervision FINRA 3110) | Out-of-process change to a financial control |
| TC-1 variance >5 % | Control 3.7 (Anomaly Detection) | Persistent variance may indicate consumption-pattern anomalies |
| TC-7 idle seats >25 % of assigned | Control 2.5 (License Optimization) — if the firm tracks separately | Operational efficiency referral |
| TC-2 immutability not Locked | Control 1.9 (Data Retention) | Records-management surface owner |
| TC-12 sovereign compensating-control gap | Control 2.21 (Sovereign Cloud Operations) — if defined | Tenant-level control |

---

## §6 Negative Tests and Anti-Patterns

The following negative tests confirm the playbook fails-loud rather than fails-silent:

```powershell
Describe 'NEG-1: Helpers refuse to fabricate cost data' {
    It 'Stub helpers cannot run in production mode' {
        $env:FSI_MODE = 'Production'
        { Get-Fsi35StubChargeback } | Should -Throw -ExpectedMessage '*Fsi35-WrongMode*'
    }
}

Describe 'NEG-2: Empty Cost Management response is not "Clean / spend = 0" silently' {
    It 'Helper returns Status=Clean, RowCount=0 with explicit Reason on empty payload' {
        # Mock an empty Cost Management response
        $r = Invoke-Fsi35CostQuery -Scope $emptyScope -From (Get-Date).AddDays(-7) -To (Get-Date)
        $r.Status   | Should -Be 'Clean'
        $r.RowCount | Should -Be 0
        # Caller MUST decide whether 0 is plausible — the helper does not assume.
    }
}

Describe 'NEG-3: Wrong-shell trap fires before any data is read' {
    It 'PS 7.4 host throws when sidecar required' {
        if ($PSVersionTable.PSEdition -eq 'Core') {
            { Assert-Fsi35ShellHost -RequiredHost Sidecar51 } | Should -Throw '*Fsi35-WrongShell*'
        }
    }
}

Describe 'NEG-4: Mutable export storage is rejected' {
    It 'New-Fsi-CostExport refuses to bind to a non-immutable container' {
        $r = New-Fsi-CostExport -ExportName 'test' -Scope $sub `
                -StorageAccountResourceId $mutableSaId -ContainerName 'mutable-container' -WhatIf
        $r.Status | Should -Be 'Anomaly' -Because 'Records-grade evidence requires immutability binding'
    }
}
```

---

## Cross-references

- [Portal Walkthrough](portal-walkthrough.md)
- [PowerShell Setup](powershell-setup.md)
- [Troubleshooting](troubleshooting.md)
- [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md)
- [Control 3.5 — Cost Allocation and Budget Tracking](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md)
- [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)
- [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)

---

[Back to Control 3.5](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) · [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
