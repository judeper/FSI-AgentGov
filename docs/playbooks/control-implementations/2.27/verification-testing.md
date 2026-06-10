# Verification & Testing — Control 2.27: Consumption-Entitlement Governance

> **Examiner-defensible evidence package** for Control 2.27. This playbook produces and retains the artifacts required to demonstrate to FINRA, SEC, OCC, and internal audit that every metered Microsoft Copilot agent in scope has a governed consumption pathway, an evaluated and materialized entitlement decision per `(agent, user)`, per-agent spend caps where applicable, and a signed-off pre-enforcement coverage-gap analysis — all retained and forwarded to the SIEM.
>
> **What this control governs (read first).** Control 2.27 governs the **entitlement *decision*** — *which user may incur metered Copilot spend on which agent, under which billing or credit policy, on which surface*. It does **not**, on its own, satisfy any regulation; organizations should verify their configuration meets their specific obligations and tailor zone thresholds to their documented risk appetite. The verification procedures below evidence that the decision was made, recorded, and reviewable — they are not a claim about any particular spend outcome.
>
> **Companion solution:** [Copilot Billing Governance](https://judeper.github.io/FSI-AgentGov-Solutions/solutions/copilot-billing-governance/) (`v0.1.0-preview`) 🔎 implements the switch-on-pathway entitlement engine (`Invoke-EntitlementEvaluation.ps1`), the policy inventory reader (`Get-BillingPolicyInventory.ps1`), the Dataverse schema (`fsi_cbg*` tables), and the Pester suite (`EntitlementEngine.Tests.ps1`) cited throughout. Verify availability — the solution is preview.
>
> **Companion controls:** [3.5 Cost Allocation and Budget Tracking](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) consumes the materialized decisions and coverage-gap aggregates this playbook produces. [1.18 Application-Level Authorization and RBAC](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) supplies the functional-access input on which the entitlement decision builds.
>
> **🔎 Live-verification window.** Microsoft consumption-billing surfaces are changing rapidly. The Copilot Credits consumption-billing model becomes the operative metering path for several agent surfaces from **June 16, 2026** 🔎 (the same day the Work IQ API moves to Copilot-Credits consumption billing). Verify the tenant ceilings (PAYG 50 / credit 10), the per-feature credit rates, the `$0.01`/credit and 25,000-credits-per-month figures, the June 2026 Licensing Guide footnote numbering (6 & 7), and whether a programmatic cap/credit-policy **write API** yet exists, against Microsoft licensing documentation before relying on the figures below.
>
> **Last UI verified:** June 2026 against the Microsoft 365 admin center, Power Platform admin center pay-as-you-go billing, and Microsoft Graph `v1.0` group endpoints.

---

## Document Conventions

| Convention | Value |
|---|---|
| PowerShell baseline | PowerShell 7.2+ Core; the engine and tests declare `#Requires -Version 7.2` |
| Test framework | Pester 5.0+ (`EntitlementEngine.Tests.ps1`) |
| Output discipline | No `Write-Host`. The engine emits structured objects and serializes the run to JSON via `-OutputPath`. Evidence is the JSON, not console text. |
| Dataverse naming | Logical names are the `SchemaName` lowercased, with **no** inter-word underscores (e.g., `fsi_cbgcoveragegap`, `fsi_blockeduserscount`). Always query logical names. |
| Option-set values | `fsi_cbg_*` global option sets begin at `100000000` and increment by 1 in declared order (see §1.3). |
| Evidence retention | Six years minimum (FINRA Rule 4511 / SEC Rule 17a-4(b)(4)) for Zone 3; align Zone 2 to a minimum of one year (see §9). |

> **Regulatory framing.** This playbook **supports compliance with** recordkeeping, IT general control, and oversight expectations under **SOX §404**, **GLBA §501(b)** (Safeguards Rule), **FINRA Rule 4511**, **SEC Rule 17a-4(b)(4)**, and third-party-spend oversight informed by **OCC Bulletin 2023-17** (Interagency Guidance on Third-Party Relationships). It does **not** by itself satisfy any regulation; organizations should verify findings against their own legal and regulatory obligations.
>
> !!! note "Model-risk guidance is adjacent context only"
>     **OCC Bulletin 2026-13 (formerly OCC 2011-12)** and **Federal Reserve SR 26-2 (formerly SR 11-7)** are model-risk-management guidance and, in their 2026 restatements, **expressly exclude generative and agentic AI from scope**. They appear here only as adjacent technology-risk context; do **not** represent this control or its evidence as satisfying SR 26-2 / OCC 2026-13 model-risk obligations.

---

## §0 Pre-Test Prerequisites

### 0.1 Operator prerequisites

The operator running this playbook holds the role assignments below, scoped to the tenant under test, and activated through Privileged Identity Management (PIM) for the duration of the run. The verification procedures are **read-only** against Dataverse and Microsoft Graph; they do not mutate policy or cap state.

| Role (doc-body canonical) | Required for |
|---|---|
| AI Administrator | Reading Microsoft Copilot PAYG and prepaid credit billing-policy state (criterion 1); Copilot usage exports. Prefer over Entra Global Admin (least privilege; PIM for JIT). |
| Entra User Admin | Reading the admission-gated security-group registry and the Graph group properties `securityEnabled` / `mailEnabled` (criterion 2). |
| Power Platform Admin | Reading the `fsi_cbg*` Dataverse tables that hold materialized decisions, caps, coverage-gap aggregates, and the group registry (criteria 2–8). |
| AI Governance Lead | Convenes the coverage-gap review; counter-signs the would-be-blocked sign-off before enforcement is activated (criterion 7). |
| Finance / Controller | Approves the cap thresholds and spend appetite; signs off the cost-estimate basis for SOX 404 ITGC (criteria 5, 7). |
| Compliance Officer | Confirms retention configuration and SIEM ingestion (criterion 8). |

### 0.2 Module and script baseline

```powershell
#Requires -Version 7.2
#Requires -Modules @{ ModuleName='Microsoft.Graph.Groups';         ModuleVersion='2.0.0' }
#Requires -Modules @{ ModuleName='Microsoft.Graph.Authentication'; ModuleVersion='2.0.0' }
#Requires -Modules @{ ModuleName='Pester';                         ModuleVersion='5.0.0' }

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
```

Companion-solution scripts referenced (from `copilot-billing-governance/scripts/`):

| Script | Role in verification |
|---|---|
| `Get-BillingPolicyInventory.ps1` | Policy-object inventory and ceiling headroom (criterion 1). |
| `Invoke-EntitlementEvaluation.ps1` | Switch-on-pathway classification, entitlement evaluation, and the per-agent coverage-gap aggregate (criteria 3, 4, 5, 6). |
| `EntitlementEngine.Tests.ps1` | Pester 5 contract suite that pins the decision/pathway integers used as evidence patterns (§10). |

> **Authentication is managed-identity-first.** Supply a Dataverse bearer token (`-AccessToken`) and, for live platform reads, a Power Platform billing-API token (`-BillingApiAccessToken`, resource `https://api.bap.microsoft.com/`) acquired from a managed identity or workload-identity federation. The scripts provide an `Az.Accounts` interactive fallback for dev-only workstation runs; do not use it for examination evidence.

### 0.3 Pre-flight gates (must pass before §2–§9 execute)

| Gate | ID | Purpose | Failure behavior |
|---|---|---|---|
| Module presence | CBG-PRE-01 | Confirms the modules above are loaded at the pinned versions | HALT |
| Graph context | CBG-PRE-02 | Confirms `Connect-MgGraph` established with `Group.Read.All` (read-only) | HALT |
| Dataverse reachability | CBG-PRE-03 | Confirms the `fsi_cbg*` entity sets respond to a `$top=1` read on the environment under test | HALT |
| Engine input availability | CBG-PRE-04 | Confirms an `(agent, user)` input fixture is present (`-InputPath`) with `configuredTier` / `createdIn` populated by the upstream solutions | HALT with upstream pointer |
| Zone tag presence | CBG-PRE-05 | Confirms every in-scope agent carries a zone classification (Team / Enterprise) so zone gating in §1.1 can be applied | HALT |

Tag each run with a deterministic `runId` of the form `CBG227-yyyyMMdd-HHmmss-<8charGuid>`, embedded in every evidence artifact filename.

### 0.4 Upstream dependency note

`configuredTier` (the **authoritative** pathway signal) is produced by the **work-iq-usage-detection** solution; `createdIn` (the **last-resort fallback** signal) is produced by **copilot-agent-inventory** (Azure Resource Graph `PowerPlatformResources`). Until both siblings have run for the tenant, the engine operates on sample/fixture inputs and criterion 3 cannot be attested as live. The Work IQ GA / consumption-billing switch is **June 16, 2026** 🔎.

---

## §1 Criterion Catalog & Manifest Cross-Walk

### 1.1 The eight Verification Criteria and their zone applicability

The eight criteria below are taken verbatim from [Control 2.27 → Verification Criteria](../../../controls/pillar-2-management/2.27-consumption-entitlement-governance.md#verification-criteria) (the authoritative source). All eight are required for a Zone 3 attestation. Criteria **1–4 and 6** apply to Zone 2. Criterion **1** applies to Zone 1 at a **documentation level only**, and only where metered consumption exists.

| # | Criterion (abbreviated) | Section | Zone 1 | Zone 2 | Zone 3 |
|---|---|---|---|---|---|
| 1 | Both consumption policy objects inventoried; configuration + ceilings (50/10) + credit-rate basis recorded | §2 | Doc-level (if metered) | ✓ | ✓ |
| 2 | Admission-gated registry populated; every group `securityEnabled` and **not** `mailEnabled` | §3 | — | ✓ | ✓ |
| 3 | Every Z2/Z3 metered agent classified to a pathway; `unmapped` = 0 or each recorded as anomaly with owner | §4 | — | ✓ | ✓ |
| 4 | Entitlement contract evaluated across the `(agent, user)` population; decisions materialized; `ZeroRatingResolved` posture recorded | §5 | — | ✓ | ✓ |
| 5 | Per-agent caps configured for all Z3 metered agents; enforcement mode recorded; no false hard-stop claim | §6 | — | — | ✓ |
| 6 | Pre-enforcement coverage-gap run monitor-only for all metered agents; per-agent rows present | §7 | — | ✓ | ✓ |
| 7 | Would-be-blocked population reviewed + signed off before enforcement; spend estimate reconciled | §8 | — | — | ✓ |
| 8 | Decisions + coverage-gap evidence retained (FINRA 4511 six-year min, SEC 17a-4(b)(4)) and forwarded to SIEM | §9 | — | — | ✓ |

### 1.2 Manifest cross-walk (assessment checks `2.27.a`–`2.27.d`)

The assessment manifest (`assessment/manifest/controls.json`) scores Control 2.27 through **four** automated checks. The table maps each check to the criteria it evidences, the companion-solution probe it runs, and the zones in which it is required. Criteria **1** and **8** are evidenced at a **documentation / configuration level** and do not have a dedicated automated manifest check — they underpin and bracket the four automated checks (the policy scope the checks operate on, and the retention/forwarding of their output).

| Manifest check | `pass_condition` | Evidences criteria | Probe (`api_call`) | Zones required |
|---|---|---|---|---|
| `2.27.a` | `entitlement_contract_evaluated` | **3 + 4** (each metered agent classified to a pathway **and** the entitlement contract evaluated) | `Invoke-EntitlementEvaluation.ps1` | Zone 2, Zone 3 |
| `2.27.b` | `per_agent_caps_configured` | **5** (per-agent metered spend caps configured; enforce **or** detect-and-alert) | `Invoke-EntitlementEvaluation.ps1` | Zone 3 |
| `2.27.c` | `coverage_gap_analysis_run` | **6 + 7** (pre-enforcement coverage-gap run monitor-only; sign-off gates enforcement) | `Invoke-EntitlementEvaluation.ps1` | Zone 2, Zone 3 |
| `2.27.d` | `policy_scope_groups_registered` | **2** (scope groups registered; `securityEnabled` and **not** `mailEnabled`) | `Get-MgGroup` | Zone 2, Zone 3 |
| *(doc-level)* | policy inventory recorded | **1** | `Get-BillingPolicyInventory.ps1` | Zone 1 (doc), Zone 2, Zone 3 |
| *(doc-level)* | retention + SIEM confirmed | **8** | Retention policy config + SIEM ingestion query | Zone 3 |

**Zone scoring (from the manifest `zone_thresholds` block — confirmed against `controls.json`).** Maturity is reached at a *minimum number of checks passed*, **not** at the count of checks that happen to apply in a zone:

| Zone | Applicable automated checks | Minimum checks passed to attain maturity | Maturity score |
|---|---|---|---|
| Zone 1 | none of `a`–`d` apply (all require Zone 2+); criterion 1 documented where metered consumption exists | **1** | 1 |
| Zone 2 | `a`, `c`, `d` (three available) | **2** | 2 |
| Zone 3 | `a`, `b`, `c`, `d` (all four) | **4** | 4 |

> **Read the Zone 2 row carefully.** Zone 2 has **three** applicable checks (`a`, `c`, `d`) but the maturity threshold is a **minimum of two passed**. Do not mistake "2/2" for "two applicable checks"; record all three results and attest maturity at ≥ 2.

### 1.3 Option-set integer reference (decision-integer evidence)

Every materialized decision and coverage-gap row carries integer-valued option sets. These integers are the evidence: an examiner can re-derive any decision from the inputs and confirm the stored integer matches. The values below are mirrored from the engine's `$script:Pathway`, `$script:Decision`, `$script:BlockReason`, `$script:SpendScope` maps and the schema generator `create_cbg_dataverse_schema.py`; they are pinned by `EntitlementEngine.Tests.ps1`.

| Option set | Logical name | Member | Integer |
|---|---|---|---|
| Pathway | `fsi_cbg_pathway` | `none` | `100000000` |
| | | `mcp-cs` | `100000001` |
| | | `mcp-agentbuilder` | `100000002` |
| | | `api-direct` | `100000003` |
| | | `metered` | `100000004` |
| | | `unmapped` | `100000005` |
| Decision | `fsi_cbg_decision` | Allow | `100000000` |
| | | Block | `100000001` |
| | | Allow - Eligibility N/A | `100000002` |
| | | Fail-open - Anomaly | `100000003` |
| | | Fail-closed - Zero-rating Unresolved | `100000004` |
| Block Reason | `fsi_cbg_blockreason` | No eligible cohort | `100000000` |
| | | Missing license | `100000001` |
| | | Zero-rating unresolved – fail-closed | `100000002` |
| | | Not in credit scope | `100000003` |
| | | Policy cap exceeded | `100000004` |
| | | Unmapped pathway | `100000005` |
| Spend Scope | `fsi_cbg_spendscope` | Chat – Credit-eligible | `100000000` |
| | | SharePoint – PAYG-only | `100000001` |
| | | Mixed | `100000002` |
| Enforcement Mode | `fsi_cbg_enforcementmode` | Detect-and-alert | `100000000` |
| | | Hard-stop | `100000001` |
| Zone Classification | `fsi_cbg_zoneclassification` | Team (Zone 2) | `100000000` |
| | | Enterprise (Zone 3) | `100000001` |

### 1.4 Engine evidence-record shape (canonical)

`Invoke-EntitlementEvaluation.ps1 -OutputPath <file>` writes one JSON envelope per run. The envelope is the primary evidence artifact:

```json
{
  "EvaluatedAt": "2026-06-09T22:41:55.0000000Z",
  "ZeroRatingResolved": true,
  "CacheTtlMinutes": 1440,
  "DecisionCount": 1,
  "AgentCount": 1,
  "Decisions": [
    {
      "fsi_agentid": "agent-0001",
      "fsi_userupn": "user@contoso.com",
      "fsi_pathway": 100000001,
      "fsi_decision": 100000000,
      "fsi_decisionreason": null,
      "fsi_spendscope": 100000000
    }
  ],
  "CoverageGaps": [
    {
      "fsi_agentid": "agent-0001",
      "fsi_agentname": "Fixture Agent",
      "fsi_pathway": 100000001,
      "fsi_eligibleusers": 1,
      "fsi_blockeduserscount": 0,
      "fsi_blockedsampleupns": "[]",
      "fsi_blockreasonsummary": null,
      "fsi_spendscope": 100000000,
      "fsi_groupsizepartition": 1,
      "fsi_monitoronly": true,
      "fsi_analyzedat": "2026-06-09T22:41:55.0000000Z",
      "fsi_retainuntil": "2026-12-09T22:41:55.0000000Z"
    }
  ]
}
```

`Decisions[]` rows materialize to the `fsi_cbgentitlementmaterialized` table; `CoverageGaps[]` rows materialize to `fsi_cbgcoveragegap`. Each section below names the exact fields it asserts.

---

## §2 Criterion 1 — Policy-Object Inventory & Configuration

### 2.1 Criterion mapping

Evidences **criterion 1**: both Microsoft Copilot consumption policy objects in use are inventoried; the selected configuration (credit-only, credit + PAYG, or PAYG-only) is documented; the tenant ceilings (**PAYG 50 / credit 10**) and the per-feature credit-rate basis are recorded. This is documentation-level evidence — it establishes the policy scope the automated checks `2.27.a`–`2.27.d` operate within.

### 2.2 Pre-conditions

- CBG-PRE-01..03 returned `PASS`.
- The reconciled Dataverse rows in `fsi_cbgbillingpolicy` (entity set `fsi_cbgbillingpolicies`) and `fsi_cbgcreditpolicy` (entity set `fsi_cbgcreditpolicies`) exist, or a live platform read is authorized.

### 2.3 Procedure

```powershell
# Proven path: reconciled Dataverse store
$inv = .\Get-BillingPolicyInventory.ps1 `
        -EnvironmentUrl 'https://contoso.crm.dynamics.com' `
        -AccessToken $dataverseToken

$inv | ConvertTo-Json -Depth 6 | Set-Content "policy-inventory-$runId.json" -Encoding UTF8
```

Add `-FromPlatform -BillingApiAccessToken $bapToken` to read PAYG policies live from the Power Platform billing-policy admin API. The credit-policy live read is **unproven** 🔎 and falls back to the reconciled Dataverse rows; the `Source` field records which path produced the inventory.

### 2.4 Expected evidence

`policy-inventory-<runId>.json` with the shape:

```json
{
  "PayAsYouGo": { "Count": 3, "Ceiling": 50, "Headroom": 47, "AtCeiling": false, "Policies": [ ... ] },
  "Credit":     { "Count": 1, "Ceiling": 10, "Headroom": 9,  "AtCeiling": false, "Policies": [ ... ] },
  "Source": "dataverse",
  "EvaluatedAt": "2026-06-09T22:41:55.0000000Z"
}
```

A short **configuration note** accompanies the export, recording: the selected configuration (credit-only / credit + PAYG / PAYG-only); that the credit policy is **Chat-only today** while SharePoint-grounded consumption stays on PAYG; and the per-feature credit-rate basis used for §8 estimates (Classic 1 · Generative 2 · Agent action 5 · Tenant-graph grounding 10 · Agent flow 13 per 100 actions; `$0.01`/credit; prepaid pack 25,000 credits/month non-rolling 🔎).

### 2.5 Pass / fail thresholds

| Result | Condition |
|---|---|
| **PASS** | Both policy objects inventoried; `Count <= Ceiling` for each; configuration and credit-rate basis documented. |
| **WARN** | `AtCeiling = true` for either object (no headroom for additional policies). |
| **FAIL** | An in-use policy object is absent from the inventory, or the configuration / ceilings / credit-rate basis are undocumented. |

### 2.6 Sample failing record

```json
{ "control_id": "2.27", "criterion": 1, "status": "FAIL",
  "assertion": "Both consumption policy objects inventoried with documented ceilings",
  "observed": { "PayAsYouGo": { "Count": 50, "Ceiling": 50, "AtCeiling": true }, "Credit": { "Count": 0 } },
  "remediation_ref": "TRG-CBG-INVENTORY-01" }
```

### 2.7 Zone applicability

Zone 1 — documentation level only, where metered consumption exists. Zone 2 and Zone 3 — required.

### 2.8 Regulator mapping

Supports SOX §404 (documented spend-authorization scope), GLBA §501(b) (oversight of the service-consumption relationship), and the third-party-spend framing of OCC Bulletin 2023-17.

---

## §3 Criterion 2 — Admission-Gated Group Registry (`2.27.d`)

### 3.1 Criterion mapping

Evidences **criterion 2** and the manifest check **`2.27.d` `policy_scope_groups_registered`** (probe `Get-MgGroup`): the admission-gated security-group registry is populated for all entitlement scope groups, and **every registered group is `securityEnabled` and not `mailEnabled`**. A mail-enabled distribution group is rejected at admission. This registry is the source of the "in credit scope / in eligible cohort / in API audience" checks the entitlement engine relies on, so an incorrectly admitted group corrupts every downstream decision.

### 3.2 Pre-conditions

- CBG-PRE-02 returned `PASS` with `Group.Read.All`.
- The registry table `fsi_cbgapprovedgrouppolicy` (entity set `fsi_cbgapprovedgrouppolicies`) holds one row per approved group, with `fsi_groupid`, `fsi_grouplayer` (Maker / Audience / Billing), `fsi_securityenabled`, `fsi_mailenabled`, and `fsi_isactive`.

### 3.3 Verification procedure

Two independent reads must agree: the **registry assertion** (what was admitted) and the **live Graph property** (what the group actually is). Drift between them is a finding.

```powershell
# Read the active registry rows from Dataverse, then re-check each group live in Graph.
$registry = Get-CbgApprovedGroups -EnvironmentUrl $env -AccessToken $dvToken |
            Where-Object { $_.fsi_isactive }

$violations = foreach ($row in $registry) {
    $g = Get-MgGroup -GroupId $row.fsi_groupid -Property 'id,securityEnabled,mailEnabled,groupTypes' -ErrorAction Stop
    if (-not $g.SecurityEnabled -or $g.MailEnabled) {
        [pscustomobject]@{
            GroupId         = $g.Id
            Layer           = $row.fsi_grouplayer
            SecurityEnabled = $g.SecurityEnabled
            MailEnabled     = $g.MailEnabled
            RegistrySays    = @{ securityEnabled = $row.fsi_securityenabled; mailEnabled = $row.fsi_mailenabled }
        }
    }
}

$violations | ConvertTo-Json -Depth 5 | Set-Content "group-registry-check-$runId.json" -Encoding UTF8
```

> **Pester assertion pattern** (mirrors the registry-admission rule): for each active registry row, `$g.SecurityEnabled | Should -BeTrue` and `$g.MailEnabled | Should -BeFalse`.

### 3.4 Expected evidence

| Artifact | Content |
|---|---|
| `group-registry-export-<runId>.json` | All active `fsi_cbgapprovedgrouppolicy` rows: group id, layer, `securityEnabled`, `mailEnabled`, zone. |
| `group-registry-check-<runId>.json` | The live-Graph property re-check. A **PASS** is an **empty array** (`[]`) — zero mail-enabled and zero non-security-enabled scope groups. |

### 3.5 Pass / fail thresholds

| Result | Condition |
|---|---|
| **PASS** | Every active registry group is `securityEnabled = true` **and** `mailEnabled = false`; the violations array is empty. |
| **FAIL** | Any active scope group is mail-enabled, or is not security-enabled, or the registry value disagrees with the live Graph property. |

### 3.6 Zone applicability

Zone 2 and Zone 3. (Not applicable to Zone 1.)

### 3.7 Regulator mapping

Supports GLBA §501(b) (administrative safeguard over who is scoped to spend) and SOX §404 (the access basis for the spend-authorization control). Pairs with Control 1.18 for the underlying functional-authorization input.

---

## §4 Criterion 3 — Pathway Classification (`2.27.a`, part)

### 4.1 Criterion mapping

Evidences **criterion 3** and the classification half of manifest check **`2.27.a`**: every Zone 2 and Zone 3 metered agent is classified to a consumption pathway (`none`, `mcp-cs`, `mcp-agentbuilder`, `api-direct`, `metered`, `unmapped`); the count of `unmapped` agents is either **zero** or each `unmapped` agent is **recorded as an anomaly with a follow-up owner**. The engine classifies `configuredTier` **first** (authoritative) and consults `createdIn` **only as a last-resort fallback**.

### 4.2 Verification procedure

```powershell
$result = .\Invoke-EntitlementEvaluation.ps1 -InputPath .\agents.fixture.json -OutputPath ".\eval-$runId.json"

# Pathway distribution; unmapped (100000005) must be zero or fully triaged.
$result.Decisions |
    Group-Object fsi_pathway |
    Select-Object @{n='pathway';e={[int]$_.Name}}, Count |
    Sort-Object pathway
```

### 4.3 Expected evidence

A **pathway classification report** — the distribution of `fsi_pathway` integers across the in-scope agent population, plus, for any `unmapped` (`100000005`) agent, the anomaly record and the named follow-up owner. Note that `unmapped` does **not** deny the user: the agent's users resolve to **Fail-open - Anomaly** (`100000003`), recorded for triage (see §5 and §11).

### 4.4 Pass / fail thresholds

| Result | Condition |
|---|---|
| **PASS** | Every Z2/Z3 metered agent carries a pathway integer; `unmapped` count is `0`, **or** each `unmapped` agent has an anomaly record with an owner. |
| **FAIL** | Any Z2/Z3 metered agent is unclassified, or an `unmapped` agent has no triage owner. |

### 4.5 Authoritative-signal regression (must hold)

The shipped suite pins the load-bearing precedence rule: a `NotConfigured` tier classifies to `none` (`100000000`) **even when `createdIn` reads `Copilot Studio`** — `configuredTier` wins so the non-metered agent majority is not pushed into the stricter `mcp-cs` arm. If this regression fails, classification is untrustworthy and the criterion fails regardless of distribution counts.

### 4.6 Zone applicability

Zone 2 and Zone 3.

---

## §5 Criterion 4 — Entitlement Contract Evaluation (`2.27.a`)

### 5.1 Criterion mapping

Evidences **criterion 4** and the evaluation half of manifest check **`2.27.a`**: the entitlement contract has been evaluated across the in-scope `(agent, user)` population; decisions are **materialized and auditable** to `fsi_cbgentitlementmaterialized`; and the **`ZeroRatingResolved` posture is recorded per run** (echoed on the envelope and carried on each `fsi_cbgentitlement` rule). This is the keystone criterion — the full decision matrix is verified in §10.

### 5.2 Verification procedure

```powershell
# Default posture: ZeroRatingResolved defaults to $true per the June 2026 Licensing Guide (footnotes 6 & 7).
$resolved   = .\Invoke-EntitlementEvaluation.ps1 -InputPath .\population.json -OutputPath ".\eval-resolved-$runId.json"

# Conservative posture: revert to fail-closed to see which licensed mcp-cs users are not covered by zero-rating.
$failClosed = .\Invoke-EntitlementEvaluation.ps1 -InputPath .\population.json -ZeroRatingResolved:$false -OutputPath ".\eval-failclosed-$runId.json"

$resolved.ZeroRatingResolved   # -> True  (recorded on the envelope)
$failClosed.ZeroRatingResolved  # -> False
```

### 5.3 Expected evidence

A **materialized decision export** — the `Decisions[]` array, one row per `(agent, user)`, each carrying `fsi_agentid`, `fsi_userupn`, `fsi_pathway`, `fsi_decision`, `fsi_decisionreason` (null for allows), and `fsi_spendscope`. The envelope's `ZeroRatingResolved` field records the posture used. Each row maps to a `fsi_cbgentitlementmaterialized` record (with `fsi_ttlexpiresat` derived from `-CacheTtlMinutes`, default 1440) so a decision is auditable without replaying inputs.

### 5.4 Pass / fail thresholds

| Result | Condition |
|---|---|
| **PASS** | `DecisionCount` equals the in-scope `(agent, user)` count; every row carries a decision integer from §1.3; the `ZeroRatingResolved` posture is recorded. |
| **FAIL** | Any `(agent, user)` pair is unevaluated, carries an out-of-set decision integer, or the posture is unrecorded. |

### 5.5 The zero-rating caveat (state it; do not over-claim)

`ZeroRatingResolved` defaulting to `true` means a Copilot-licensed user on a Microsoft 365 surface **under their own identity** (`surfaceZeroRated = true`) is **Allowed** with no credit scope required — per footnotes 6 & 7 🔎 (the zero-rating substance is confirmed on [Microsoft Learn — Copilot Studio billing and licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing); the footnote numbering is unverified). "Resolved" does **not** mean "always allow": a licensed user whose surface is **not** zero-rated and who is **not** in credit scope still resolves to **Fail-closed - Zero-rating Unresolved** (`100000004`). The generative-answer-with-tenant-grounding and beyond-fair-use refinements remain credit-metered — a per-tenant credit-**cost** caveat, not a change to the base allow/deny. Confirm the fair-usage specifics per tenant.

### 5.6 Zone applicability

Zone 2 and Zone 3.

---

## §6 Criterion 5 — Per-Agent Spend Caps (`2.27.b`)

### 6.1 Criterion mapping

Evidences **criterion 5** and manifest check **`2.27.b` `per_agent_caps_configured`**: per-agent metered spend caps are configured for **all Zone 3 metered agents**, with the **enforcement mode recorded** for each — and **no Zone 3 agent is documented as having a programmatic hard-stop where the underlying write API is unproven**.

### 6.2 Verification procedure

```powershell
# Read the per-agent cap records and confirm every Z3 metered agent has one with a recorded enforcement mode.
$caps = Get-CbgAgentCaps -EnvironmentUrl $env -AccessToken $dvToken   # reads fsi_cbgagentcaps

$caps | Select-Object fsi_agentid,
                      fsi_monthlycreditcap,
                      @{n='enforcementMode';e={[int]$_.fsi_enforcementmode}},  # 100000000=Detect-and-alert, 100000001=Hard-stop
                      fsi_capenforced,
                      @{n='zone';e={[int]$_.fsi_zoneclassification}}
```

### 6.3 Expected evidence

A **cap-record export** — `fsi_cbgagentcap` rows with `fsi_agentid`, `fsi_monthlycreditcap`, `fsi_creditsconsumedmtd`, `fsi_enforcementmode`, `fsi_capenforced`, and `fsi_zoneclassification`. Each Zone 3 metered agent has exactly one cap record.

### 6.4 The detect-and-alert caveat (load-bearing — do not overstate)

Because a public **write API for credit-policy and per-agent cap enforcement may not yet exist** 🔎, enforcement is designed to **degrade to detect-and-alert** where a hard-stop cannot be applied programmatically: the cap is recorded and breaches are surfaced, but consumption is **not** programmatically halted. A cap row with `fsi_enforcementmode = 100000001` (Hard-stop) is only valid evidence if the operator can demonstrate a working hard-stop mechanism for that surface; otherwise it must read `100000000` (Detect-and-alert). **Do not represent detect-and-alert as a hard-stop.**

### 6.5 Pass / fail thresholds

| Result | Condition |
|---|---|
| **PASS** | Every Z3 metered agent has a cap record with a recorded enforcement mode; any `Hard-stop` mode is backed by a demonstrated mechanism. |
| **WARN** | A Z3 agent records `Detect-and-alert` where the operator intended a hard-stop (expected until the write API is proven 🔎). |
| **FAIL** | A Z3 metered agent has no cap record, no recorded enforcement mode, or a `Hard-stop` claim with no working mechanism. |

### 6.6 Zone applicability

Zone 3 only. (Zone 2 caps are *recommended*, not required — see the control's Zone-Specific Requirements.)

---

## §7 Criterion 6 — Coverage-Gap Analysis, Monitor-Only (`2.27.c`)

### 7.1 Criterion mapping

Evidences **criterion 6** and the monitor-only half of manifest check **`2.27.c` `coverage_gap_analysis_run`**: a pre-enforcement coverage-gap analysis has been run in **monitor-only** mode for all metered agents; per-agent gap rows are present with eligible-user count, would-be-blocked count, a **capped** blocked-UPN sample, and the dominant block reason.

### 7.2 Verification procedure

```powershell
$result = .\Invoke-EntitlementEvaluation.ps1 -InputPath .\population.json -OutputPath ".\eval-$runId.json"

# Every coverage-gap row MUST be monitor-only before enforcement is activated.
$notMonitorOnly = @($result.CoverageGaps | Where-Object { -not $_.fsi_monitoronly })
$notMonitorOnly.Count | Should -Be 0   # any non-monitor-only row pre-enforcement is a FAIL
```

`-SampleCap` (default 20) bounds the UPN sample; `-GroupSizeThreshold` (default 500) flags large audiences for partitioning; `-RetentionDays` (default 183) sets `fsi_retainuntil`.

### 7.3 Expected evidence — the per-agent aggregate shape

A **coverage-gap export** — the `CoverageGaps[]` array, **one row per agent** (not per agent × user — aggregating per agent keeps the output bounded and avoids a 10⁶–10⁷-row blow-up). Each `fsi_cbgcoveragegap` row carries:

| Field | Meaning |
|---|---|
| `fsi_agentid` / `fsi_agentname` | The analyzed agent |
| `fsi_pathway` | Classified pathway integer |
| `fsi_eligibleusers` | Count of eligible users |
| `fsi_blockeduserscount` | Count of would-be-blocked users |
| `fsi_blockedsampleupns` | **Capped** JSON array of blocked UPNs (always a JSON array — see §11) |
| `fsi_blockreasonsummary` | Dominant block-reason integer across the blocked cohort (null when none blocked) |
| `fsi_spendscope` | Surface-aware scope (Chat vs SharePoint) |
| `fsi_groupsizepartition` | Intended-audience size used to partition large groups above threshold T |
| `fsi_monitoronly` | **`true`** for every row pre-enforcement |
| `fsi_analyzedat` / `fsi_retainuntil` | Analysis timestamp and retention horizon |

### 7.4 Pass / fail thresholds

| Result | Condition |
|---|---|
| **PASS** | Every metered agent has exactly one coverage-gap row; **all** rows have `fsi_monitoronly = true`; counts and sample are present and internally consistent (see §11). |
| **FAIL** | A metered agent has no gap row, any row is not monitor-only before enforcement, or `fsi_eligibleusers + fsi_blockeduserscount` does not equal the agent's evaluated population. |

### 7.5 Zone applicability

Zone 2 and Zone 3.

---

## §8 Criterion 7 — Sign-Off & Spend-Estimate Reconciliation (`2.27.c` gate)

### 8.1 Criterion mapping

Evidences **criterion 7** — the governance gate on manifest check **`2.27.c`**: the would-be-blocked population has been **reviewed and signed off before any enforcement was activated**; a coverage-gap **spend estimate** has been produced from the per-feature credit rates and **reconciled** against the Microsoft 365 admin center / Azure cost reporting, with the explicit caveat that the figures are **estimates and not a billing-accurate invoice**.

### 8.2 Verification procedure

1. Sum `fsi_blockeduserscount` across all `fsi_cbgcoveragegap` rows from §7 — this is the would-be-blocked population.
2. Convene the coverage-gap review (AI Governance Lead; Business Unit Owner for affected cohorts; Finance / Controller for the cap thresholds and appetite).
3. Produce a spend estimate from the per-feature credit rates (Classic 1 · Generative 2 · Agent action 5 · Tenant-graph grounding 10 · Agent flow 13/100 🔎) at `$0.01`/credit.
4. Reconcile the estimate against the Microsoft 365 admin center and Azure cost reporting; record the variance.
5. Capture the sign-off **before** flipping any agent's `fsi_monitoronly` to enforcement.

### 8.3 Expected evidence

| Artifact | Content |
|---|---|
| `coverage-gap-signoff-<runId>.json` | The would-be-blocked total, the named approver(s), the timestamp, and an explicit "enforcement activation approved" decision dated **before** the first enforcement change. |
| `spend-estimate-reconciliation-<runId>.json` | The credit-rate-based estimate, the admin-center / Azure cost figure, the variance, and the **estimate-not-invoice** caveat in the body. |

### 8.4 Pass / fail thresholds

| Result | Condition |
|---|---|
| **PASS** | A dated sign-off exists, timestamped before any enforcement activation; the reconciliation note carries the estimate, the reconciled figure, and the caveat. |
| **FAIL** | Enforcement was activated without a prior dated sign-off, or no reconciliation note exists, or the note presents the estimate as a billing-accurate invoice. |

### 8.5 Zone applicability

Zone 3 only. (Zone 2 runs the monitor-only coverage-gap of §7 but does not activate enforcement, so the sign-off-before-enforcement gate is a Zone 3 requirement.)

---

## §9 Criterion 8 — Retention & SIEM Forwarding

### 9.1 Criterion mapping

Evidences **criterion 8**: entitlement decisions and coverage-gap evidence are retained under a policy aligned to **FINRA 4511 (six-year minimum)** and **SEC 17a-4(b)(4)**, and are **forwarded to the organization's SIEM**.

### 9.2 Verification procedure

1. Confirm the retention horizon on the materialized records: `fsi_cbgentitlementmaterialized` decisions and `fsi_cbgcoveragegap` aggregates (the latter carries `fsi_retainuntil`, derived from `-RetentionDays`) are retained for ≥ six years on the storage tier, ideally WORM-protected.
2. Confirm SIEM ingestion: query the SIEM index that receives the exported run envelopes and confirm the latest `runId` is present.

### 9.3 Expected evidence

| Artifact | Content |
|---|---|
| `retention-policy-<runId>.json` | The storage/retention configuration showing ≥ six-year retention on the decision and coverage-gap stores. |
| `siem-ingestion-<runId>.json` | A SIEM query result confirming the run envelope (by `runId`) was ingested, with the ingestion timestamp. |

> **`-RetentionDays` is a deployment parameter, not the records-retention horizon.** Its default (183 days) sets the coverage-gap aggregate's operational `fsi_retainuntil`; it is **not** the FINRA 4511 six-year evidence-retention period. The six-year horizon is applied at the storage/SIEM tier on the exported evidence artifacts — set the deployment parameter and the storage retention deliberately and independently. ("Decide late": tune the operational horizon from observed cadence; fix the evidence horizon to the regulatory minimum.)

### 9.4 Pass / fail thresholds

| Result | Condition |
|---|---|
| **PASS** | Decision and coverage-gap evidence retained ≥ six years; the latest run is confirmed in the SIEM. |
| **FAIL** | Retention < six years, or the run is absent from the SIEM. |

### 9.5 Zone applicability

Zone 3 (six-year minimum + SIEM). Zone 2 applies a minimum one-year retention per the control's Zone-Specific Requirements.

---

## §10 Entitlement-Contract Test-Scenario Matrix

This is the decision-integer evidence set. Each row is a deterministic `(agent, user)` scenario from the shipped Pester suite `EntitlementEngine.Tests.ps1`; the expected `fsi_pathway` and `fsi_decision` integers are the ones the suite asserts (all currently green). Reproduce any row by writing the fixture to `-InputPath`, invoking the engine, and reading the materialized integer back. Inputs are user flags on the intended-user object (`hasCopilotLicense`, `surfaceZeroRated`, `inCreditScopeGroup`, `inApiAudienceGroup`, `inEligibleCohort`); `—` means "not relevant to the arm".

| # | Scenario | `configuredTier` | `createdIn` | Lic | ZeroRated | CreditScope | ApiAud | Cohort | `ZeroRatingResolved` | → Pathway | → Decision | Block reason |
|---|---|---|---|:--:|:--:|:--:|:--:|:--:|:--:|---|---|---|
| 1 | Non-metered majority | `NotConfigured` | `Copilot Studio` | — | — | — | — | — | default | `none` 100000000 | **Allow - Eligibility N/A** 100000002 | — |
| 2 | Adjacent tier | `Adjacent` | *(empty)* | — | — | — | — | — | default | `none` 100000000 | **Allow - Eligibility N/A** 100000002 | — |
| 3 | mcp-cs licensed, zero-rated surface | `NativeMcpCopilotStudio` | `Copilot Studio` | ✓ | ✓ | — | — | — | default (true) | `mcp-cs` 100000001 | **Allow** 100000000 | — |
| 4 | mcp-cs licensed, not zero-rated, **in credit scope** | `NativeMcpCopilotStudio` | `Copilot Studio` | ✓ | ✗ | ✓ | — | — | default (true) | `mcp-cs` 100000001 | **Allow** 100000000 | — |
| 5 | mcp-cs licensed, not zero-rated, **no credit scope** | `NativeMcpCopilotStudio` | `Copilot Studio` | ✓ | ✗ | ✗ | — | — | default (true) | `mcp-cs` 100000001 | **Fail-closed - Zero-rating Unresolved** 100000004 | Zero-rating unresolved 100000002 |
| 6 | mcp-cs licensed, zero-rated, **conservative posture** | `NativeMcpCopilotStudio` | `Copilot Studio` | ✓ | ✓ | ✗ | — | — | **false** | `mcp-cs` 100000001 | **Fail-closed - Zero-rating Unresolved** 100000004 | Zero-rating unresolved 100000002 |
| 7 | mcp-cs **unlicensed** | `NativeMcpCopilotStudio` | `Copilot Studio` | ✗ | — | — | — | — | default | `mcp-cs` 100000001 | **Block** 100000001 | Missing license 100000001 |
| 8 | mcp-agentbuilder licensed (createdIn fallback) | *(empty)* | `Microsoft 365 Copilot Agent Builder` | ✓ | — | — | — | — | default | `mcp-agentbuilder` 100000002 | **Allow** 100000000 | — |
| 9 | mcp-agentbuilder **unlicensed** | *(empty)* | `Microsoft 365 Copilot Agent Builder` | ✗ | — | — | — | — | default | `mcp-agentbuilder` 100000002 | **Block** 100000001 | Missing license 100000001 |
| 10 | api-direct **in** audience cohort | `NativeApiDirect` | `API` | — | — | — | ✓ | — | default | `api-direct` 100000003 | **Allow** 100000000 | — |
| 11 | api-direct **not in** cohort | `NativeApiDirect` | `API` | — | — | — | ✗ | — | default | `api-direct` 100000003 | **Block** 100000001 | No eligible cohort 100000000 |
| 12 | metered **in** eligible cohort | `metered` | *(empty)* | — | — | — | — | ✓ | default | `metered` 100000004 | **Allow** 100000000 | — |
| 13 | metered **not in** cohort (the bounded ELSE) | `metered` | *(empty)* | — | — | — | — | ✗ | default | `metered` 100000004 | **Block** 100000001 | No eligible cohort 100000000 |
| 14 | unmapped (unrecognized tier **and** surface) | `ZZZUnknownTierZZZ` | `ZZZUnknownSurfaceZZZ` | — | — | — | — | — | default | `unmapped` 100000005 | **Fail-open - Anomaly** 100000003 | *(recorded, not denied)* |

**Reading the matrix.** Rows 1–2 are the **non-metered agent majority** — `configuredTier` is authoritative, so they classify to `none` and Allow even when `createdIn` looks like Copilot Studio. Row 5 is the most counter-intuitive: "resolved" zero-rating still requires an actual zero-rated surface **or** credit scope, so a licensed user on a non-zero-rated surface with no credit scope **fails closed**. Row 14 is the safety property — a classifier defect **fails open** and is recorded as an anomaly; a detection bug must not deny a user.

> **Block-reason integers** are mirrored from the engine's `$script:BlockReason` map: No eligible cohort `100000000`, Missing license `100000001`, Zero-rating unresolved `100000002`. The coverage-gap suite independently pins `No eligible cohort = 100000000` via `fsi_blockreasonsummary`.

---

## §11 Coverage-Gap Verification Deep-Dive

The coverage-gap aggregate is the load-bearing "who would be blocked" deliverable. Three properties must hold; the shipped suite pins all three.

### 11.1 Eligible vs. would-be-blocked semantics (verify precisely)

The aggregate's `fsi_eligibleusers` / `fsi_blockeduserscount` split is **not** "Allow vs everything else". The engine treats three decisions as **eligible (not blocked)** and two as **would-be-blocked**:

| Counts as **eligible** (`fsi_eligibleusers`) | Counts as **would-be-blocked** (`fsi_blockeduserscount`) |
|---|---|
| Allow `100000000` | Block `100000001` |
| Allow - Eligibility N/A `100000002` | Fail-closed - Zero-rating Unresolved `100000004` |
| **Fail-open - Anomaly `100000003`** | |

The critical, easily-missed point: **Fail-open - Anomaly is counted as eligible, not blocked** — a detection defect must not inflate the would-be-blocked population or deny a user. Conversely, **Fail-closed - Zero-rating Unresolved *is* counted as would-be-blocked**, because that user is not covered. An examiner re-deriving the counts must apply this same split.

### 11.2 Pre-enforcement monitor-only invariant

Every `fsi_cbgcoveragegap` row is emitted with `fsi_monitoronly = true`. No gap row takes an enforcement action. Confirm zero rows have `fsi_monitoronly = false` before any sign-off (§8) flips an agent to enforcement.

### 11.3 The blocked-UPN sample is always a JSON array (all cardinalities)

`fsi_blockedsampleupns` is a JSON **array string** for every cardinality — the suite pins all three cases because each is a distinct serialization trap:

| Blocked count | `fsi_blockedsampleupns` value | Why it matters |
|---|---|---|
| **0** (all allowed) | `"[]"` — the literal empty-array string | Never null / empty; the zero-blocked case is explicit evidence, not an absence of evidence. |
| **1** | `"[\"solo-blocked@contoso.com\"]"` — one-element array | A single element must **not** serialize as a bare string; the sample is bounded by `-SampleCap` (default 20). |
| **n > 1** | `"[\"blocked1@contoso.com\",\"blocked2@contoso.com\"]"` | Capped at `-SampleCap`; preserves investigability without a per-pair row blow-up. |

> **Worked example (from the suite).** An `api-direct` agent with one user in the API audience cohort and two outside it yields `fsi_eligibleusers = 1`, `fsi_blockeduserscount = 2`, a two-element `fsi_blockedsampleupns` array, and `fsi_blockreasonsummary = 100000000` (No eligible cohort). The all-allowed single-user agent yields `fsi_eligibleusers = 1`, `fsi_blockeduserscount = 0`, `fsi_blockedsampleupns = "[]"`, and a null `fsi_blockreasonsummary`.

### 11.4 Bounded-by-design assertion

The aggregate is per **agent**, not per agent × user. For a population of A agents and U users, the output is **A rows**, each with a sample capped at `-SampleCap`. Confirm the export row count equals the metered-agent count, not the `(agent, user)` count.

---

## §12 Evidence Pack Assembly & Retention

Each run produces several JSON artifacts. The operator assembles them into a single pack an examiner can ingest as one unit. The companion engine emits the JSON; **assembly, signing, and WORM retention are the operator's responsibility** under the organization's evidence policy (the solution does not ship a signing component).

### 12.1 Pack structure

```
evidence-pack-CBG227-20260609-224155-a1b2c3d4/
├── manifest.json                                  # Top-level descriptor (schema below)
├── policy-inventory-<runId>.json                  # §2  (criterion 1)
├── group-registry-export-<runId>.json             # §3  (criterion 2)
├── group-registry-check-<runId>.json              # §3  (criterion 2 — 2.27.d)
├── eval-resolved-<runId>.json                     # §4,§5,§7 (criteria 3,4,6 — 2.27.a/c)
├── eval-failclosed-<runId>.json                   # §5  (conservative posture)
├── cap-records-<runId>.json                       # §6  (criterion 5 — 2.27.b)
├── coverage-gap-signoff-<runId>.json              # §8  (criterion 7)
├── spend-estimate-reconciliation-<runId>.json     # §8  (criterion 7)
├── retention-policy-<runId>.json                  # §9  (criterion 8)
├── siem-ingestion-<runId>.json                    # §9  (criterion 8)
├── pester/EntitlementEngine-<runId>.xml           # §10 (JUnit XML, contract suite)
└── README.md                                      # Plain-text examiner orientation
```

### 12.2 `manifest.json` — criteria & check coverage

```json
{
  "pack_version": "1.0",
  "control_id": "2.27",
  "run_id": "CBG227-20260609-224155-a1b2c3d4",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "zone": "3",
  "produced_at": "2026-06-09T22:45:00Z",
  "zero_rating_resolved": true,
  "criteria_coverage": {
    "1": "PASS", "2": "PASS", "3": "PASS", "4": "PASS",
    "5": "WARN", "6": "PASS", "7": "PASS", "8": "PASS"
  },
  "manifest_checks": {
    "2.27.a": "PASS", "2.27.b": "WARN", "2.27.c": "PASS", "2.27.d": "PASS"
  },
  "zone_maturity": { "zone": 3, "checks_passed": 3, "min_required": 4, "attained": false }
}
```

> The `WARN` on criterion 5 / `2.27.b` in this illustrative manifest reflects the realistic preview state: caps recorded as **detect-and-alert** because the hard-stop write API is unproven 🔎. A `WARN` here is expected and acceptable as evidence **provided** the enforcement mode is honestly recorded; it must not be papered over as a `Hard-stop`.

### 12.3 Retention

| Tier | Content | Retention | Protection |
|---|---|---|---|
| Primary | Full evidence pack | 6 years (FINRA 4511 / SEC 17a-4(b)(4)) | WORM / immutable |
| Mirror | SIEM index (parsed `manifest.json` + `criteria_coverage` + `manifest_checks`) | 6 years | Immutable index |

---

## §13 Failure Triage Matrix

| ID | Trigger | Containment / remediation | Cross-reference |
|---|---|---|---|
| `TRG-CBG-INVENTORY-01` | Criterion 1: a policy object is missing from the inventory, or `AtCeiling = true` with no headroom | Reconcile `fsi_cbgbillingpolicy` / `fsi_cbgcreditpolicy`; document the configuration and ceilings; raise headroom review with the AI Administrator | §2; [Troubleshooting](troubleshooting.md) |
| `TRG-CBG-MAILGROUP-01` | Criterion 2 / `2.27.d`: an active registry group is `mailEnabled = true` or `securityEnabled = false` | Remove the group from active scope; replace with a security-enabled, non-mail-enabled group; re-run the live Graph check until the violations array is `[]` | §3 |
| `TRG-CBG-UNMAPPED-01` | Criterion 3: a Z2/Z3 metered agent classifies to `unmapped` (`100000005`) with no owner | Open an anomaly record with a named follow-up owner; investigate the missing/contradictory `configuredTier` + `createdIn` signals upstream. Users **remain Fail-open - Anomaly (allowed)** during triage | §4, §11.1 |
| `TRG-CBG-FAILCLOSED-01` | Criterion 4: a licensed `mcp-cs` user resolves to **Fail-closed - Zero-rating Unresolved** (`100000004`) unexpectedly | Confirm the surface zero-rating posture and credit-scope membership; if the footnote-7 case applies, confirm `surfaceZeroRated`; otherwise add the user to credit scope. This is a correct conservative outcome, not a bug | §5.5 |
| `TRG-CBG-MISSINGLIC-01` | Criterion 4: an `mcp-cs` / `mcp-agentbuilder` user resolves to **Block / Missing license** (`100000001`) | Assign a Microsoft 365 Copilot license, or remove the user from the intended audience; re-evaluate | §5, §10 (rows 7, 9) |
| `TRG-CBG-FALSEHARDSTOP-01` | Criterion 5 / `2.27.b`: a Z3 cap records `Hard-stop` (`100000001`) with no demonstrated mechanism | Correct the enforcement mode to `Detect-and-alert` (`100000000`) until a write API is proven 🔎; never represent detect-and-alert as a hard-stop | §6.4 |
| `TRG-CBG-NOTMONITOR-01` | Criterion 6 / `2.27.c`: a coverage-gap row is **not** monitor-only before sign-off | Halt enforcement activation; restore monitor-only; obtain the §8 sign-off before any enforcement flip | §7, §8 |
| `TRG-CBG-NOSIGNOFF-01` | Criterion 7: enforcement was activated without a prior dated sign-off | Roll enforcement back to monitor-only; convene the coverage-gap review; capture the dated sign-off and reconciliation before re-activating | §8 |
| `TRG-CBG-RETENTION-01` | Criterion 8: retention < 6 years or the run is absent from the SIEM | Extend storage retention to the FINRA 4511 minimum; confirm SIEM forwarding of the run envelope by `runId` | §9 |

---

## §14 Zone Scorecard & Manifest Cross-Walk Summary

Use this scorecard to attest a zone. "Applicable checks" is the set of automated manifest checks that apply; "maturity threshold" is the **minimum** number that must pass (from the manifest `zone_thresholds` block).

| | Zone 1 — Personal | Zone 2 — Team | Zone 3 — Enterprise |
|---|---|---|---|
| Criteria in scope | 1 (doc-level, if metered) | 1, 2, 3, 4, 6 | 1–8 (all) |
| Applicable automated checks | none of `a`–`d` | `a`, `c`, `d` | `a`, `b`, `c`, `d` |
| Maturity threshold (min checks passed) | 1 | 2 | 4 |
| Maturity score at threshold | 1 | 2 | 4 |
| Retention | Standard tenant | ≥ 1 year | ≥ 6 years + SIEM |

**Attestation rule.** A zone is attested when the in-scope criteria are evidenced (§2–§9), the applicable manifest checks meet or exceed the maturity threshold, and — for Zone 3 — the coverage-gap sign-off (§8) is dated **before** any enforcement activation. Record the realistic preview caveat where it applies: per-agent caps degrade to **detect-and-alert** until a programmatic write API is proven 🔎; do not over-attest a hard-stop.

---

## Footer

| | |
|---|---|
| **Control** | [2.27 — Consumption-Entitlement Governance](../../../controls/pillar-2-management/2.27-consumption-entitlement-governance.md) |
| **Sister playbooks** | [Portal Walkthrough](portal-walkthrough.md) · [PowerShell Setup](powershell-setup.md) · [Troubleshooting](troubleshooting.md) |
| **Companion solution** | [Copilot Billing Governance](https://judeper.github.io/FSI-AgentGov-Solutions/solutions/copilot-billing-governance/) 🔎 (preview) |
| **Last UI verified** | June 2026 |
| **Document version** | v1.0 |
| **Updated** | June 2026 |

> This playbook **supports compliance with** FINRA Rule 4511, SEC Rule 17a-4(b)(4), SOX §404, GLBA §501(b), and the third-party-spend framing of OCC Bulletin 2023-17. It governs the **entitlement decision** and does **not** by itself satisfy any regulation; organizations should verify findings against their own legal and regulatory obligations and tailor zone thresholds to their documented risk appetite. Model-risk guidance (OCC Bulletin 2026-13, formerly OCC 2011-12; Federal Reserve SR 26-2, formerly SR 11-7) is adjacent context only and is **not** satisfied by this control.
