---
control_id: "2.12"
title: "PowerShell Setup — Control 2.12: Supervision and Oversight (FINRA Rule 3110)"
pillar: "2 — Management"
playbook_type: "powershell-setup"
powershell_edition: "7.4 LTS Core"
clouds_supported: "Commercial"
last_updated: "2026-04-15"
version: "v1.4"
ui_verified: "April 2026"
prerequisites:
  - "PowerShell 7.4 LTS Core (Windows, Linux, or macOS)"
  - "Microsoft.Graph 2.25.0+ (pinned) and Microsoft.Graph.Beta 2.25.0+"
  - "ExchangeOnlineManagement 3.5.0+ for unified audit queries"
  - "Microsoft.PowerApps.Administration.PowerShell (pinned) for Power Automate approval history"
  - "Pester 5.5+ for the Rule 3120 testing harness (§9)"
  - "Az.Accounts 2.15+ and Az.OperationalInsights 3.6+ for Sentinel forwarding verification (§12)"
  - "Entra Global Reader (baseline); PIM-elevated Compliance Administrator for audit reads; Power Platform Administrator for Power Automate reads"
scopes_required:
  - "AuditLog.Read.All"
  - "Directory.Read.All"
  - "Application.Read.All"
  - "Policy.Read.All"
  - "AccessReview.Read.All"
  - "AgentIdentity.Read.All  # where exposed by tenant; helpers degrade gracefully"
related_controls: ["1.2", "1.7", "2.6", "2.13", "2.25", "2.26", "3.1", "3.4", "3.6"]
---

# PowerShell Setup — Control 2.12: Supervision and Oversight (FINRA Rule 3110)

> **Control under management:** [`2.12 — Supervision and Oversight (FINRA Rule 3110)`](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)
>
> **Sister playbooks:** [Portal Walkthrough](./portal-walkthrough.md) · [Verification & Testing](./verification-testing.md) · [Troubleshooting](./troubleshooting.md)
>
> **Shared baseline (authoritative):** [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) — module pinning, mutation safety, evidence emission, SHA-256 manifest format. **Read the baseline before running any command in this file.**

This playbook automates the operational PowerShell surface for **Control 2.12 — Supervision and Oversight (FINRA Rule 3110)**. It covers review-queue health monitoring, HITL reviewer-decision extraction, Microsoft Agent Framework `request_info()` evidence export, principal-registration (CRD) verification, sampling-protocol execution, the Rule 3120 annual-testing harness (Pester), Rule 2210 communication classification, quarterly sponsor attestation, and SIEM forwarding. Every helper in this file uses the cmdlet prefix `Sup212` so that operators can distinguish 2.12 helpers from sister controls (`Agt225`, `Agt226`, `Orph36`) at a glance in transcripts and SIEM rules.

> **Hedged-language reminder.** Every helper and every evidence bundle in this playbook **supports compliance with** FINRA Rule 3110 (Supervision), FINRA Rule 3120 (Supervisory Control System), FINRA Rule 2210 (Communications with the Public), FINRA Rule 4511 (Books and Records), FINRA Regulatory Notice 24-09 (Gen AI / LLM Guidance), SEC Rules 17a-3 / 17a-4 (Recordkeeping and WORM), SOX §§ 302 / 404 (Internal Controls), and NYDFS 23 NYCRR 500. It does **not** "ensure" or "guarantee" compliance, and it does **not substitute** for the registered principal's supervisory review or for the firm's Written Supervisory Procedures (WSPs). In FINRA Rule 3110 terms, the scripts in this file produce the evidence the principal attests to — the principal's judgment remains the control.

> **Non-substitution anchor.** Controls [2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) and [2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) reference this control as the supervisory anchor. Microsoft Agent 365 admin approvals and Entra Agent ID sponsorship are **lifecycle / identity** controls; they do not discharge the firm's Rule 3110 supervisory obligation. The helpers in this file treat Agent 365 approval history and Entra sponsorship state as **inputs** to principal supervision, never as replacements for it.

## Scope

This playbook operationalizes the verification criteria enumerated in the Control 2.12 document (criteria #1–#8). It is **not** a substitute for reading that control; in particular, the definitions of "high-risk action", "qualified principal", "Zone 3", the communication-type decision tree, and the sampling-rate table live in the control document, not here. This file automates the **evidence production** and **operating-effectiveness testing** around those definitions.

| Verification criterion (Control 2.12) | Primary helper in this file |
|---|---|
| #1 WSP addendum coverage | `Invoke-Sup212WspCoverageTest` (§9.3) — metadata read only; authoring stays in the firm's DMS |
| #2 HITL configuration — Zone 3 commercial | `Get-Sup212CopilotStudioHandoffConfig` (§4.2), `Get-Sup212AgentFrameworkHitlConfig` (§6.2) |
| #3 Principal registration verification | `Test-Sup212PrincipalRegistration` (§7) |
| #4 Review queue SLA | `Measure-Sup212ReviewQueueSla` (§4.3) |
| #5 Reviewer-decision audit trail | `Get-Sup212ReviewerDecisionAudit` (§5) |
| #6 Rule 3120 annual test | `Invoke-Sup212Rule3120Harness` (§9) |
| #7 Rule 2210 classification evidence | `Invoke-Sup212Rule2210Classifier` (§10) |
| #8 Agent Framework evidence retention | `Export-Sup212AgentFrameworkEvidence` (§6.3) |

## Audience

Primary operators are the **AI Administrator** (Microsoft admin-surface configuration and telemetry reads), the **AI Governance Lead** (orchestration, evidence-pack integrity, operating-effectiveness reporting), and the **Compliance Officer** (Rule 3120 testing sign-off, principal-registration attestation). The **Designated Principal / Qualified Supervisor** is the signer of evidence produced by these scripts, not an operator of them — the script produces the artifact; the principal reads and signs. The **Agent Owner** is responsible for ensuring each agent in scope is registered in [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) / [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) so that the §3–§5 helpers have a complete registry to iterate.

Canonical role names are defined in [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). Use the short forms: **Compliance Officer**, **Designated Principal / Qualified Supervisor**, **AI Governance Lead**, **AI Administrator**, **Agent Owner**.

---

## §0 — Wrong-Shell Trap and False-Clean Defect Catalogue

Before any helper in this playbook is dot-sourced, the operator must internalize the specific failure modes that produce **false-clean** supervisory signals. A false-clean signal on a supervision control is materially worse than a red signal: under FINRA Rule 3110 a documented gap is an exception to be remediated, but a false-clean record filed to WORM and signed by a principal is a misrepresentation of the firm's books and records under Rule 4511 and SEC 17a-4(b)(4). Every helper below is written to refuse empty results as evidence of a clean control state.

### 0.1 The wrong-shell trap

Copilot Studio admin reads, Power Automate approval-history reads, and Agent Framework event-stream reads all require the **modern Microsoft Graph SDK on PowerShell 7.4+**. Windows PowerShell 5.1 cannot load the pinned `Microsoft.Graph` 2.25 module family because of .NET Framework dependency mismatches, and it will silently load older 1.x versions if they are present on the operator's module path. Those older modules return `@()` for several of the agent surfaces this playbook reads, and `@()` is indistinguishable from "no flagged outputs this quarter" — the exact false-clean pattern this control is designed to prevent.

`Assert-Sup212ShellHost` (defined in §3.1) is the first action of every helper. It:

1. Verifies `$PSVersionTable.PSEdition -eq 'Core'` and `$PSVersionTable.PSVersion -ge [version]'7.4'`.
2. Verifies the loaded `Microsoft.Graph.Authentication` module is `>= 2.25.0`.
3. Verifies no `Microsoft.Graph` module **older than 2.25** is installed anywhere on `$env:PSModulePath`, because import-order ambiguity has bitten operators who have both 1.28 and 2.25 present side by side.
4. Verifies `ExchangeOnlineManagement >= 3.5.0` and `Pester >= 5.5.0` when §5 or §9 helpers are on the call stack.
5. On any failure, throws a terminating `[System.InvalidOperationException]` whose message contains the literal token `Sup212-WrongShell` so SIEM correlation rules can fire on it deterministically.

### 0.2 False-clean defect catalogue

| # | Defect | Symptom | Root cause | Structural guard in this playbook |
|---|---|---|---|---|
| 0.1 | Wrong PowerShell host | `Get-MgAuditLog*` returns `@()` | PS 5.1 loaded Graph 1.28 alongside 2.25 | `Assert-Sup212ShellHost` (§3.1) |
| 0.2 | Read-only token used against audit surfaces | `403` swallowed, helper logs `Anomaly` then masks as `Clean` on retry | Operator ran without Compliance Administrator PIM elevation | `Test-Sup212GraphScopes` (§3.4) preflights scope grants |
| 0.3 | Paged audit response truncated at 100 | Reviewer-decision count undercounts in active quarters | Operator forgot `-All` on `Invoke-MgGraphRequest` | `Invoke-Sup212PagedQuery` (§3.5) paginates and asserts `@odata.count` |
| 0.4 | Throttled call returned empty body | Helper interprets HTTP 429 with empty JSON as zero decisions | No retry/backoff wrapper | `Invoke-Sup212Throttled` (§3.6) |
| 0.5 | Purview audit 30-minute ingestion lag | Recent HITL decisions appear missing | Unified audit log has up to a 30-minute (sometimes longer) ingestion delay | `Get-Sup212ReviewerDecisionAudit` (§5) accepts `-LookbackBufferMinutes` (default 45) and refuses to run against a `-End` within the buffer unless `-AcceptIngestionLag` is set |
| 0.6 | Power Automate approval history filtered by owner | Approvals initiated under a service-principal owner are invisible | Default `Get-AdminFlowApproval` scope is tenant-user-visible only | `Get-Sup212PowerAutomateApprovalHistory` (§4.4) iterates all environments with `-AdminMode` and emits `Anomaly` if any environment returns `403` rather than silently skipping |
| 0.7 | Reviewer UPN null in audit row | Decision row written before approver context resolved; renders as `(unknown)` | Race in M365 audit ingestion when approval auto-completes | `Get-Sup212ReviewerDecisionAudit` joins `Get-MgAuditLogDirectoryAudit` and emits `Anomaly` (never `Clean`) when UPN is null |
| 0.8 | Agent Framework request ID unmatched | Evidence export completes with zero rows for active flows | Operator queried the wrong workflow identifier or event stream | `Export-Sup212AgentFrameworkEvidence` (§6.3) cross-references the Agent Framework run manifest and emits `Anomaly` if request count is zero but run activity is non-zero |
| 0.9 | CRD lookup silently degraded | Principal registration "verified" against an empty cache | Automated CRD/WebCRD access not licensed; helper fell back to a manual file that was never populated | `Test-Sup212PrincipalRegistration` (§7) returns `NotApplicable` with `Reason='CrdAccessNotAvailable'` rather than `Clean`; operators must then run the documented manual-process path and populate the attestation store |
| 0.10 | Sampling RNG seeded with clock-second | Two parallel runs produce identical samples | `Get-Random` seeded with `[int](Get-Date).Second` | `Get-Sup212SamplePopulation` (§8) uses `[System.Security.Cryptography.RandomNumberGenerator]` and records the seed in the evidence manifest |
| 0.11 | Pester harness marked green on `Skipped` | Rule 3120 report shows all tests "passing" though half ran `-Skip` | Operator used `-SkipRemainingOnFailure` or environment gating without auditing skip count | `Invoke-Sup212Rule3120Harness` (§9) refuses to emit `Clean` if `Skipped > 0`; skip count is surfaced in the test report header |
| 0.12 | Access review auto-approved on reviewer non-response | Quarterly sponsor attestation shows 100% completion with zero real decisions | Default Entra access-review setting: "If reviewers don't respond: Approve" | `Get-Sup212SponsorAttestation` (§11) surfaces `defaultDecision` and `defaultDecisionEnabled` and flags auto-approval as `Anomaly` |
| 0.13 | SIEM forwarding silent drop | Supervision events absent from Sentinel | Data Collection Rule filters out the relevant `Operation` values | `Test-Sup212SiemForwarding` (§12) emits a canary event with a known correlation ID and verifies it appears in the target workspace; no appearance → `Anomaly`, not `Clean` |
| 0.14 | Empty result conflated with "no findings" | Helper returns `$null` or `@()`; downstream evidence pack says "Clean" | Helpers must distinguish `Clean` from `NotApplicable` from `Error` | **Every** helper returns `[pscustomobject]` with explicit `Status` ∈ {`Clean`, `Anomaly`, `Pending`, `NotApplicable`, `Error`} and non-empty `Reason` whenever `Status -ne 'Clean'` |

> **Operator discipline.** Every helper in §§3–12 returns a structured object with a `Status` field. **No helper ever returns `$null` or `@()` as a clean signal.** When there is genuinely no data to report (e.g., no HITL decisions in a quarter because the tenant has no Zone 3 agents), the helper returns a single object with `Status='NotApplicable'` and a populated `Reason` — and the §14 evidence packer requires an explicit affirmative affirmation in the evidence manifest that `NotApplicable` reflects reality, not an instrumentation gap.

---

## §1 — Module Inventory, Graph Scopes, and RBAC Matrix

### 1.1 Module pinning

Every module this playbook uses is pinned against the version verified during the April 2026 UI-verification pass. Operators in regulated tenants must install from an internal PSGallery mirror rather than the public gallery directly; substitute `-Repository <YourInternalFeed>` and verify the package SHA-256 against the values published in [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md).

```powershell
#Requires -Version 7.4
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$pinned = @{
    'Microsoft.Graph'                             = '2.25.0'
    'Microsoft.Graph.Beta'                        = '2.25.0'
    'Microsoft.Graph.Authentication'              = '2.25.0'
    'ExchangeOnlineManagement'                    = '3.5.0'
    'Microsoft.PowerApps.Administration.PowerShell' = '2.0.188'
    'Pester'                                      = '5.5.0'
    'Az.Accounts'                                 = '2.15.0'
    'Az.OperationalInsights'                      = '3.6.0'
}

foreach ($name in $pinned.Keys) {
    $installed = Get-Module -ListAvailable -Name $name |
        Where-Object { $_.Version -eq [version]$pinned[$name] }
    if (-not $installed) {
        Install-Module -Name $name `
            -RequiredVersion $pinned[$name] `
            -Repository PSGallery `
            -Scope CurrentUser `
            -AllowClobber `
            -AcceptLicense `
            -Force
    }
}
Import-Module Microsoft.Graph.Authentication -RequiredVersion 2.25.0 -Force
```


### 1.2 Graph scope matrix

| Scope | Required for | Helper | Failure mode if missing |
|---|---|---|---|
| `AuditLog.Read.All` | Reviewer-decision audit, Agent Framework event stream | `Get-Sup212ReviewerDecisionAudit`, `Export-Sup212AgentFrameworkEvidence` | `403` on audit reads; helpers emit `Error` with `Sup212-MissingScope` |
| `Directory.Read.All` | Resolving reviewer UPNs, principal-directory lookups | `Resolve-Sup212ReviewerUpn` | Reviewer column rendered as `(unresolved)`; helper emits `Anomaly` |
| `Application.Read.All` | Resolving agent app registrations | `Get-Sup212AgentInventoryJoin` | `403` on `/applications` reads |
| `Policy.Read.All` | Conditional Access policies for HITL gating | `Get-Sup212HitlConditionalAccessPolicy` | Helper emits `NotApplicable` with `Reason='Policy.Read.AllNotGranted'` |
| `AccessReview.Read.All` | Quarterly sponsor-attestation reads | `Get-Sup212SponsorAttestation` | Helper emits `NotApplicable` — not `Clean` — so that the sponsor path is not silently skipped |
| `AgentIdentity.Read.All` | Sponsorship relationship enumeration (where tenant exposes it) | `Get-Sup212SponsorAttestation` | Helper degrades to directory-only enumeration, tags `Reason='AgentIdentityScopeUnavailable'` |

`Test-Sup212GraphScopes` (§3.4) interrogates the live token and returns one row per required scope with a `Granted` boolean; the bootstrap aborts unless all scopes **except** `AgentIdentity.Read.All` are granted.

### 1.3 Power Platform / Exchange / Az scope matrix

| API surface | Required for | Role / license |
|---|---|---|
| `Microsoft.PowerApps.Administration.PowerShell` — `Add-PowerAppsAccount -Endpoint prod` | Power Automate approval history (§4.4) | Power Platform Administrator (PIM-elevated) |
| `ExchangeOnlineManagement` — `Connect-ExchangeOnline` then `Search-UnifiedAuditLog` | Copilot Studio transcript metadata and cross-check (§4.2) | Compliance Administrator (PIM-elevated); `AuditLog` role on the EXO principal |
| `Az.OperationalInsights` — `Invoke-AzOperationalInsightsQuery` | Sentinel forwarding verification (§12) | Reader on the Log Analytics workspace |
| Agent Framework evidence endpoint (HTTPS) | `request_info()` event stream export (§6) | App registration with certificate-based auth; the endpoint URL is firm-specific and must be configured in §3.7 |

### 1.4 RBAC matrix

| Activity | Minimum role | PIM elevation | Notes |
|---|---|---|---|
| Read Copilot Studio handoff configuration | Power Platform Administrator (read) | No — for read only | PIM required if the same session mutates environment settings |
| Read Power Automate approval history (admin mode) | Power Platform Administrator | **Yes** | `-AdminMode` toggles the tenant-wide scope |
| Read unified audit log (Purview) | Compliance Administrator | **Yes** | Required for §5 and §6 |
| Read Entra directory / app registrations | Entra Global Reader | No | Sufficient for §4 config reads |
| Run Rule 3120 Pester harness | AI Governance Lead (no admin role needed for pure test logic) | No | The harness consumes evidence files; it does not call admin APIs |
| Forward evidence to Sentinel | Reader on workspace + Monitoring Metrics Publisher on DCE | No | Out-of-scope for Entra RBAC |

Canonical role names: **Compliance Officer**, **Designated Principal / Qualified Supervisor**, **AI Governance Lead**, **AI Administrator**, **Agent Owner**. See [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md).

### 1.5 PIM elevation pattern

Compliance Administrator and Power Platform Administrator are PIM-bound for audit reads because these roles can also be used to **export** customer content at scale; justification capture is required. Every §5, §6, and §11 helper captures the PIM elevation ticket in its evidence manifest:

```powershell
function Get-Sup212PimJustification {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $RoleName,
        [Parameter(Mandatory)] [string] $TicketId,
        [Parameter(Mandatory)] [string] $Justification
    )
    if ($Justification.Length -lt 24) {
        throw "Sup212-WeakJustification: PIM justification must be >= 24 chars; got $($Justification.Length)."
    }
    if ($TicketId -notmatch '^(CHG|INC|TASK|JIRA-)\S+$') {
        throw "Sup212-BadTicketId: Expected CHG*, INC*, TASK*, or JIRA-* format; got '$TicketId'."
    }
    [pscustomobject]@{
        Role          = $RoleName
        TicketId      = $TicketId
        Justification = $Justification
        CapturedAt    = (Get-Date).ToUniversalTime().ToString('o')
    }
}
```

Every evidence bundle in this playbook references the `PimJustification` object that was live at the moment of capture. Omitting the justification object fails the §13 evidence-pack integrity check.

---

## §2 — Preview Gating and Cmdlet Availability

Between the November 2025 Copilot Studio preview and the April 2026 verification pass, Microsoft renamed several cmdlets and surfaces. Two classes of defects follow from mid-flight renames: (a) missing cmdlets swallowed by a broad `try`/`catch` and masked as `Clean`; (b) preview surfaces treated as GA and relied on for principal evidence. Every helper that calls a module cmdlet first invokes `Get-Sup212CmdletAvailability`:

```powershell
function Get-Sup212CmdletAvailability {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string[]] $CmdletName
    )
    foreach ($name in $CmdletName) {
        $cmd = Get-Command -Name $name -ErrorAction SilentlyContinue
        [pscustomobject]@{
            CmdletName = $name
            Available  = [bool]$cmd
            Module     = if ($cmd) { $cmd.ModuleName } else { $null }
            Version    = if ($cmd) { $cmd.Module.Version.ToString() } else { $null }
        }
    }
}
```

When a required cmdlet is unavailable, the calling helper emits `Status='NotApplicable'`, `Reason="CmdletMissing:<name>"`, and a portal-export fallback URI in the evidence record — it **never** silently returns `Clean`.

### 2.1 Preview-gating preflight

Agent 365 autonomous-agent identities remain in Preview at the May 1, 2026 GA milestone (see Control 2.12 control document § "Autonomous Agents, Zone 3, and Agent 365 Preview Scope"). This playbook **does not** emit any helper that relies on autonomous-agent preview surfaces; `Test-Sup212PreviewGating` returns `NotApplicable` with `Reason='AutonomousAgentsOutOfScope'` if an operator attempts to pass `-IncludeAutonomous`.

```powershell
function Test-Sup212PreviewGating {
    [CmdletBinding()]
    param(
        [switch] $IncludeAutonomous
    )
    if ($IncludeAutonomous) {
        return [pscustomobject]@{
            Surface = 'AutonomousAgentIdentities'
            Status  = 'NotApplicable'
            Reason  = 'AutonomousAgentsOutOfScope — see Control 2.12 control doc and Control 2.25 preview-gating note.'
        }
    }
    [pscustomobject]@{
        Surface = 'CopilotStudioHitl,AgentFrameworkHitl,PowerAutomateApprovals'
        Status  = 'Clean'
        Reason  = ''
    }
}
```

---

---

## §3 — Connection Helper (Commercial)

The bootstrap helpers establish the session, validate scopes, capture the PIM justification, and emit a structured `Sup212Session` object that every subsequent helper consumes. Four rules are non-negotiable:

1. **Every session is initialized with `Disconnect-*` first** so cached cross-tenant tokens cannot leak into evidence.
2. **Throttling is wrapped at the bootstrap layer** so §4–§12 callers never need to write their own retry loops.
3. **Every session carries a `RunId`** (a GUID generated at `Initialize-Sup212Session`) that is emitted into every evidence file, every audit correlation, and every SIEM record. The `RunId` is the unit of evidence integrity.

### 3.1 Assert-Sup212ShellHost

```powershell
function Assert-Sup212ShellHost {
    [CmdletBinding()]
    param(
        [switch] $RequirePester,
        [switch] $RequireExchange,
        [switch] $RequirePowerPlatform
    )

    if ($PSVersionTable.PSEdition -ne 'Core') {
        throw [System.InvalidOperationException]::new(
            "Sup212-WrongShell: PowerShell Core (7.4+) required; got $($PSVersionTable.PSEdition)")
    }
    if ($PSVersionTable.PSVersion -lt [version]'7.4') {
        throw [System.InvalidOperationException]::new(
            "Sup212-WrongShell: PS 7.4+ required; got $($PSVersionTable.PSVersion)")
    }

    $auth = Get-Module -Name Microsoft.Graph.Authentication -ListAvailable |
        Sort-Object Version -Descending | Select-Object -First 1
    if (-not $auth -or $auth.Version -lt [version]'2.25.0') {
        throw [System.InvalidOperationException]::new(
            "Sup212-WrongShell: Microsoft.Graph.Authentication 2.25.0+ required.")
    }

    $stale = Get-Module -ListAvailable -Name Microsoft.Graph |
        Where-Object { $_.Version -lt [version]'2.25.0' }
    if ($stale) {
        throw [System.InvalidOperationException]::new(
            "Sup212-WrongShell: Stale Microsoft.Graph $($stale[0].Version) present alongside 2.25; remove stale version to remove import-order ambiguity.")
    }

    $loadedDesktopGraph = Get-Module -Name 'Microsoft.Graph*' |
        Where-Object { $_.Path -match 'WindowsPowerShell\\v1\.0' }
    if ($loadedDesktopGraph) {
        throw [System.InvalidOperationException]::new(
            "Sup212-WrongShell: Microsoft.Graph modules loaded from Windows PowerShell 5.1 path; shell is contaminated. Restart pwsh 7.4 cleanly.")
    }

    if ($RequirePester) {
        $pester = Get-Module -Name Pester -ListAvailable |
            Sort-Object Version -Descending | Select-Object -First 1
        if (-not $pester -or $pester.Version -lt [version]'5.5.0') {
            throw [System.InvalidOperationException]::new(
                "Sup212-WrongShell: Pester 5.5+ required for Rule 3120 harness.")
        }
    }
    if ($RequireExchange) {
        $exo = Get-Module -Name ExchangeOnlineManagement -ListAvailable |
            Sort-Object Version -Descending | Select-Object -First 1
        if (-not $exo -or $exo.Version -lt [version]'3.5.0') {
            throw [System.InvalidOperationException]::new(
                "Sup212-WrongShell: ExchangeOnlineManagement 3.5+ required for unified audit reads.")
        }
    }
    if ($RequirePowerPlatform) {
        $pp = Get-Module -Name Microsoft.PowerApps.Administration.PowerShell -ListAvailable |
            Sort-Object Version -Descending | Select-Object -First 1
        if (-not $pp) {
            throw [System.InvalidOperationException]::new(
                "Sup212-WrongShell: Microsoft.PowerApps.Administration.PowerShell required for Power Automate approval history reads.")
        }
    }

    [pscustomobject]@{
        Status        = 'Clean'
        PSVersion     = $PSVersionTable.PSVersion.ToString()
        GraphVersion  = $auth.Version.ToString()
        CheckedAt     = (Get-Date).ToUniversalTime().ToString('o')
        Reason        = ''
    }
}
```

### 3.2 Resolve-Sup212CloudProfile

This helper returns the commercial Microsoft 365 Global profile used by this framework. The function name is retained so existing orchestration scripts do not break, but endpoint selection is intentionally fixed to commercial cloud.

```powershell
function Resolve-Sup212CloudProfile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $TenantId,
        [string] $TenantDomainHint
    )

    [pscustomobject]@{
        TenantId          = $TenantId
        EnvName           = 'Global'
        GraphEnv          = 'Global'
        ExoEnv            = 'O365Default'
        PowerAppsEndpoint = 'prod'
        ResolvedAt        = (Get-Date).ToUniversalTime().ToString('o')
    }
}
```

### 3.3 Initialize-Sup212Session

```powershell
function Initialize-Sup212Session {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $TenantId,
        [string] $TenantDomainHint,
        [string] $RunId = ([guid]::NewGuid().ToString()),
        [Parameter(Mandatory)] [pscustomobject] $PimJustification,
        [string[]] $RequestedScopes = @(
            'AuditLog.Read.All',
            'Directory.Read.All',
            'Application.Read.All',
            'Policy.Read.All',
            'AccessReview.Read.All',
            'AgentIdentity.Read.All'
        ),
        [switch] $ConnectExchange,
        [switch] $ConnectPowerPlatform
    )

    $null = Assert-Sup212ShellHost `
        -RequireExchange:$ConnectExchange `
        -RequirePowerPlatform:$ConnectPowerPlatform

    $cloud = Resolve-Sup212CloudProfile `
        -TenantId $TenantId `
        -TenantDomainHint $TenantDomainHint `

    Disconnect-MgGraph -ErrorAction SilentlyContinue | Out-Null
    Connect-MgGraph -TenantId $TenantId -Scopes $RequestedScopes `
        -Environment $cloud.GraphEnv -NoWelcome -ErrorAction Stop

    $scopeReport = Test-Sup212GraphScopes -RequestedScopes $RequestedScopes
    $missing = $scopeReport | Where-Object {
        -not $_.Granted -and $_.Scope -ne 'AgentIdentity.Read.All'
    }
    if ($missing) {
        Disconnect-MgGraph | Out-Null
        throw [System.UnauthorizedAccessException]::new(
            "Sup212-MissingScopes: $($missing.Scope -join ', ')")
    }

    if ($ConnectExchange) {
        Connect-ExchangeOnline -ExchangeEnvironmentName $cloud.ExoEnv `
            -ShowBanner:$false -ErrorAction Stop
    }
    if ($ConnectPowerPlatform) {
        Add-PowerAppsAccount -Endpoint $cloud.PowerAppsEndpoint | Out-Null
    }

    [pscustomobject]@{
        RunId                    = $RunId
        TenantId                 = $TenantId
        Cloud                    = $cloud
        ScopesGranted            = ($scopeReport | Where-Object Granted).Scope
        ScopesMissing            = ($scopeReport | Where-Object { -not $_.Granted }).Scope
        PimJustification         = $PimJustification
        ExchangeConnected        = [bool]$ConnectExchange
        PowerPlatformConnected   = [bool]$ConnectPowerPlatform
        InitializedAt            = (Get-Date).ToUniversalTime().ToString('o')
        Status                   = 'Clean'
        Reason                   = ''
    }
}
```

### 3.4 Test-Sup212GraphScopes

```powershell
function Test-Sup212GraphScopes {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string[]] $RequestedScopes
    )
    $ctx = Get-MgContext
    if (-not $ctx) {
        throw [System.InvalidOperationException]::new(
            "Sup212-NoContext: Connect-MgGraph has not been called.")
    }
    $granted = $ctx.Scopes
    foreach ($scope in $RequestedScopes) {
        [pscustomobject]@{
            Scope   = $scope
            Granted = ($granted -contains $scope)
        }
    }
}
```

### 3.5 Invoke-Sup212PagedQuery

Every Graph audit read in this playbook uses this helper so that paging is asserted, not assumed. It refuses to return partial results when `@odata.count` disagrees with the assembled row count.

```powershell
function Invoke-Sup212PagedQuery {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $Uri,
        [int] $MaxPages = 1000
    )
    $rows = [System.Collections.Generic.List[object]]::new()
    $page = 0
    $next = $Uri
    $expected = $null

    while ($next -and $page -lt $MaxPages) {
        $page++
        $resp = Invoke-Sup212Throttled {
            Invoke-MgGraphRequest -Method GET -Uri $next -OutputType PSObject
        }
        if ($null -ne $resp.'@odata.count' -and $null -eq $expected) {
            $expected = [int]$resp.'@odata.count'
        }
        if ($resp.value) { $rows.AddRange($resp.value) }
        $next = $resp.'@odata.nextLink'
    }

    if ($null -ne $expected -and $rows.Count -ne $expected) {
        return [pscustomobject]@{
            Status = 'Anomaly'
            Reason = "Sup212-PagingMismatch: expected=$expected got=$($rows.Count)"
            Rows   = $rows
            Pages  = $page
        }
    }
    [pscustomobject]@{
        Status = 'Clean'
        Reason = ''
        Rows   = $rows
        Pages  = $page
    }
}
```

### 3.6 Invoke-Sup212Throttled

```powershell
$script:Sup212ThrottleState = @{
    Retries    = 5
    MaxBackoff = [TimeSpan]::FromSeconds(60)
}

function Invoke-Sup212Throttled {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [scriptblock] $ScriptBlock
    )
    $attempt = 0
    $backoff = [TimeSpan]::FromSeconds(1)
    while ($true) {
        try {
            return & $ScriptBlock
        } catch {
            $attempt++
            $status = $_.Exception.Response.StatusCode.value__
            $isRetry = ($status -in 429, 503, 504) -or ($_.Exception.Message -match 'timed out')
            if (-not $isRetry -or $attempt -ge $script:Sup212ThrottleState.Retries) {
                throw
            }
            $retryAfter = $_.Exception.Response.Headers.RetryAfter.Delta
            $sleep = if ($retryAfter) { $retryAfter } else { $backoff }
            if ($sleep -gt $script:Sup212ThrottleState.MaxBackoff) {
                $sleep = $script:Sup212ThrottleState.MaxBackoff
            }
            Write-Verbose "Sup212-Throttle: attempt=$attempt status=$status sleep=$($sleep.TotalSeconds)s"
            Start-Sleep -Seconds ([int]$sleep.TotalSeconds)
            $backoff = [TimeSpan]::FromSeconds([math]::Min($backoff.TotalSeconds * 2, 60))
        }
    }
}
```

### 3.7 Configuration file for endpoint-dependent helpers

The Agent Framework event stream, Sentinel data-collection endpoint, and supervision-register list URL are firm-specific. Capture them once in `sup212.config.json` next to the playbook; the §6, §11, and §12 helpers require the file. Missing fields are surfaced as `NotApplicable`, not `Clean`.

```json
{
  "agentFrameworkEvidenceEndpoint": "https://agf-evidence.contoso.corp/api/v1/supervision/requests",
  "agentFrameworkClientId": "00000000-0000-0000-0000-000000000000",
  "agentFrameworkCertThumbprint": "",
  "supervisionRegisterListUrl": "https://contoso.sharepoint.com/sites/ai-governance/Lists/SupervisionRegister",
  "sentinelWorkspaceId": "",
  "sentinelDataCollectionEndpointUri": "",
  "sentinelDcrImmutableId": "",
  "sentinelStreamName": "Custom-Sup212Supervision_CL"
}
```

### 3.8 New-Sup212EvidenceManifest

Every section that writes an artifact to disk emits an evidence record through this helper. The manifest format aligns with the SHA-256 manifest in the shared baseline.

```powershell
function New-Sup212EvidenceManifest {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object]   $Session,
        [Parameter(Mandatory)] [string]   $Criterion,
        [Parameter(Mandatory)] [string]   $Status,
        [string]   $Reason = '',
        [string[]] $Artifacts = @(),
        [string[]] $RegulatorMappings = @('FINRA-3110','FINRA-3120','FINRA-2210','FINRA-4511','SEC-17a-4','SOX-404'),
        [hashtable] $Extras = @{}
    )

    $hashes = foreach ($path in $Artifacts) {
        if (Test-Path $path) {
            [pscustomobject]@{
                path   = $path
                sha256 = (Get-FileHash -Path $path -Algorithm SHA256).Hash
                bytes  = (Get-Item $path).Length
            }
        }
    }

    $manifest = [ordered]@{
        control_id         = '2.12'
        run_id             = $Session.RunId
        run_timestamp      = (Get-Date).ToUniversalTime().ToString('o')
        tenant_id          = $Session.TenantId
        cloud              = $Session.Cloud.EnvName
        namespace          = 'fsi-agentgov.supervision.rule3110'
        criterion          = $Criterion
        status             = $Status
        reason             = $Reason
        evidence_artifacts = $hashes
        regulator_mappings = $RegulatorMappings
        pim_justification  = $Session.PimJustification
        schema_version     = '1.0'
    }
    foreach ($k in $Extras.Keys) { $manifest[$k] = $Extras[$k] }

    [pscustomobject]$manifest
}
```

---

## §4 — Review Queue Health Monitoring (Verification Criteria #2 and #4)

The supervisory review queue is the operational surface over which FINRA Rule 3110 supervision runs in the Microsoft estate. Copilot Studio's **human-agent handoff** and **approval actions** patterns route outputs matching the firm-defined high-risk criteria to a qualified reviewer; Power Automate approval actions fill equivalent roles for workflows outside Copilot Studio. `§4` produces two artifacts:

- A **configuration-export bundle** (criterion #2) that proves each Zone 3 agent has HITL wiring present, the trigger criteria match the WSP, and a test transcript exists.
- A **SLA measurement report** (criterion #4) with median and 95th-percentile time-to-review per zone, and per-agent exception rows for decisions that breached SLA — flagged as incidents under [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).

Both artifacts are signed, hashed, and emitted through `New-Sup212EvidenceManifest`.

### 4.1 Get-Sup212Zone3AgentInventory

Scope for the queue helpers is bounded by the authoritative agent registry maintained in [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) and [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md). This helper reads the Zone 3 subset from a firm-configured registry URL (defined in `sup212.config.json`) and returns a typed collection. It refuses to run without a registry — **a script that does not know which agents are in scope cannot produce supervision evidence**.

```powershell
function Get-Sup212Zone3AgentInventory {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [string] $RegistryCsvPath
    )

    if (-not (Test-Path $RegistryCsvPath)) {
        return [pscustomobject]@{
            Status = 'Error'
            Reason = "Sup212-NoRegistry: registry CSV not found at $RegistryCsvPath. Populate from Control 3.1 export."
        }
    }

    $rows = Import-Csv -Path $RegistryCsvPath |
        Where-Object { $_.Zone -eq '3' -and $_.Status -eq 'Active' }

    if (-not $rows -or $rows.Count -eq 0) {
        return [pscustomobject]@{
            Status = 'NotApplicable'
            Reason = 'Tenant has no Active Zone 3 agents registered under Control 3.1. Confirm this reflects reality with Agent Owner before signing.'
            Rows   = @()
        }
    }

    [pscustomobject]@{
        Status = 'Clean'
        Reason = ''
        Rows   = $rows
    }
}
```

### 4.2 Get-Sup212CopilotStudioHandoffConfig

For each Zone 3 agent, this helper reads the Copilot Studio bot definition (via the Power Platform admin API) and extracts the handoff / approval configuration. The helper emits `Anomaly` — not `Clean` — when the configuration is missing, when the trigger criteria are empty, or when no test transcript exists.

```powershell
function Get-Sup212CopilotStudioHandoffConfig {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [object[]] $Agents,
        [string] $TestTranscriptRoot = './evidence/2.12/handoff-transcripts'
    )

    $results = foreach ($agent in $Agents) {
        try {
            $envId = $agent.PowerPlatformEnvironmentId
            $botId = $agent.CopilotStudioBotId
            $def = Invoke-Sup212Throttled {
                Get-PowerAppEnvironment -EnvironmentName $envId |
                    Out-Null
                # Copilot Studio bot definition export — replace with documented cmdlet or REST call per your tenant:
                Invoke-MgGraphRequest -Method GET `
                    -Uri "https://api.powerplatform.com/copilotstudio/environments/$envId/bots/$botId?api-version=2025-04-01"
            }

            $handoff = $def.properties.supervision.handoff
            $approvals = $def.properties.supervision.approvalActions
            $transcriptPath = Join-Path $TestTranscriptRoot "$botId.transcript.json"
            $transcriptPresent = Test-Path $transcriptPath

            $isMissing = -not $handoff -and -not $approvals
            $isEmpty = ($handoff -and -not $handoff.triggers) -or
                       ($approvals -and -not $approvals.triggers)

            $status = if ($isMissing) { 'Anomaly' }
                      elseif ($isEmpty) { 'Anomaly' }
                      elseif (-not $transcriptPresent) { 'Anomaly' }
                      else { 'Clean' }

            $reason = switch ($status) {
                'Anomaly' {
                    if ($isMissing) { 'No handoff or approval configuration found.' }
                    elseif ($isEmpty) { 'Handoff / approval configuration present but trigger list empty.' }
                    elseif (-not $transcriptPresent) { "Test transcript missing at $transcriptPath." }
                }
                default { '' }
            }

            [pscustomobject]@{
                AgentId            = $agent.AgentId
                AgentName          = $agent.AgentName
                BotId              = $botId
                HandoffConfigured  = [bool]$handoff
                ApprovalConfigured = [bool]$approvals
                HandoffTriggers    = if ($handoff) { $handoff.triggers -join ';' } else { '' }
                ApprovalTriggers   = if ($approvals) { $approvals.triggers -join ';' } else { '' }
                TestTranscriptPath = if ($transcriptPresent) { $transcriptPath } else { '' }
                Status             = $status
                Reason             = $reason
            }
        } catch {
            [pscustomobject]@{
                AgentId = $agent.AgentId; AgentName = $agent.AgentName; BotId = $agent.CopilotStudioBotId
                HandoffConfigured=$null; ApprovalConfigured=$null; HandoffTriggers=''; ApprovalTriggers=''
                TestTranscriptPath=''; Status='Error'; Reason=$_.Exception.Message
            }
        }
    }

    $results
}
```

**Note on the Copilot Studio export endpoint.** The exact REST URI for programmatic Copilot Studio bot-definition export is subject to change between Copilot Studio releases; verify it against current Microsoft Learn documentation and your tenant's admin API version before scheduling this helper unattended. The §4.2 helper treats a 404 on that URI as `Error`, not `Clean`.

### 4.3 Measure-Sup212ReviewQueueSla (Criterion #4)

This helper aggregates decision latency from Power Automate approval history and Copilot Studio transcripts into a single SLA report. Median, 95th-percentile, and per-zone thresholds come from the firm's WSP; this helper accepts them as parameters and does not hard-code a rate.

```powershell
function Measure-Sup212ReviewQueueSla {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [datetime] $Start,
        [Parameter(Mandatory)] [datetime] $End,
        [Parameter(Mandatory)] [hashtable] $SlaMinutesByZone,   # @{ '2' = 480; '3' = 60 }
        [string] $OutputPath = "./evidence/2.12/queue-sla-$($Session.RunId).json"
    )

    $decisions = Get-Sup212PowerAutomateApprovalHistory -Session $Session -Start $Start -End $End

    if ($decisions.Status -ne 'Clean' -and $decisions.Status -ne 'NotApplicable') {
        return [pscustomobject]@{
            Status = 'Error'
            Reason = "ApprovalHistoryFailed: $($decisions.Reason)"
        }
    }

    if ($decisions.Rows.Count -eq 0) {
        $empty = [pscustomobject]@{
            Status  = 'NotApplicable'
            Reason  = 'No approval decisions in window. Confirm this reflects reality before signing — zero can be genuine (no Zone 3 activity) or an instrumentation gap.'
            Window  = @{ Start=$Start.ToString('o'); End=$End.ToString('o') }
        }
        $empty | ConvertTo-Json -Depth 6 | Out-File -FilePath $OutputPath -Encoding utf8
        return $empty
    }

    $rows = $decisions.Rows | ForEach-Object {
        $latency = ($_.ResolvedAtUtc - $_.CreatedAtUtc).TotalMinutes
        $zone = $_.AgentZone
        $threshold = $SlaMinutesByZone[$zone]
        $breached = if ($threshold) { $latency -gt $threshold } else { $false }
        [pscustomobject]@{
            ApprovalId   = $_.ApprovalId
            AgentId      = $_.AgentId
            AgentZone    = $zone
            CreatedAtUtc = $_.CreatedAtUtc
            ResolvedAtUtc= $_.ResolvedAtUtc
            LatencyMin   = [math]::Round($latency, 2)
            Threshold    = $threshold
            Breached     = $breached
            ReviewerUpn  = $_.ReviewerUpn
            Decision     = $_.Decision
        }
    }

    $byZone = $rows | Group-Object AgentZone | ForEach-Object {
        $lats = $_.Group.LatencyMin | Sort-Object
        $n = $lats.Count
        $median = if ($n -gt 0) { $lats[[int][math]::Floor($n/2)] } else { $null }
        $p95idx = if ($n -gt 0) { [int][math]::Ceiling(0.94 * $n) - 1 } else { 0 }
        $p95 = if ($n -gt 0) { $lats[[math]::Max(0, $p95idx)] } else { $null }
        $breachCount = ($_.Group | Where-Object Breached).Count
        [pscustomobject]@{
            Zone          = $_.Name
            DecisionCount = $n
            MedianMin     = $median
            P95Min        = $p95
            Breaches      = $breachCount
            BreachRatePct = if ($n -gt 0) { [math]::Round(100 * $breachCount / $n, 2) } else { 0 }
            Threshold     = $SlaMinutesByZone[$_.Name]
        }
    }

    $anyBreach = ($rows | Where-Object Breached).Count -gt 0
    $status = if ($anyBreach) { 'Anomaly' } else { 'Clean' }
    $reason = if ($anyBreach) { "SLA breaches present — open incidents under Control 3.4." } else { '' }

    $report = [pscustomobject]@{
        RunId        = $Session.RunId
        Window       = @{ Start=$Start.ToString('o'); End=$End.ToString('o') }
        SlaMinutes   = $SlaMinutesByZone
        ByZone       = $byZone
        Decisions    = $rows
        Status       = $status
        Reason       = $reason
        GeneratedAt  = (Get-Date).ToUniversalTime().ToString('o')
    }

    $report | ConvertTo-Json -Depth 8 | Out-File -FilePath $OutputPath -Encoding utf8
    $report
}
```

### 4.4 Get-Sup212PowerAutomateApprovalHistory

Power Automate approval history is the authoritative record for review decisions raised through approval actions. Tenant-wide reads require `-AdminMode` on `Get-AdminFlowApproval`; without it, approvals initiated under service-principal owners are invisible (defect #0.6).

```powershell
function Get-Sup212PowerAutomateApprovalHistory {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [datetime] $Start,
        [Parameter(Mandatory)] [datetime] $End
    )
    if (-not $Session.PowerPlatformConnected) {
        return [pscustomobject]@{
            Status='Error'; Reason='Sup212-NoPowerPlatform: Initialize-Sup212Session with -ConnectPowerPlatform.'; Rows=@()
        }
    }

    $envs = Invoke-Sup212Throttled { Get-AdminPowerAppEnvironment }
    $all  = [System.Collections.Generic.List[object]]::new()
    $denied = [System.Collections.Generic.List[string]]::new()

    foreach ($env in $envs) {
        try {
            $apps = Invoke-Sup212Throttled {
                Get-AdminFlowApproval -EnvironmentName $env.EnvironmentName -AdminMode:$true
            }
            foreach ($a in $apps) {
                if ($a.CreatedTime -ge $Start -and $a.CreatedTime -le $End) {
                    $all.Add([pscustomobject]@{
                        EnvironmentId = $env.EnvironmentName
                        ApprovalId    = $a.ApprovalId
                        Title         = $a.Title
                        AgentId       = $a.Properties.agentId
                        AgentZone     = $a.Properties.agentZone
                        CreatedAtUtc  = $a.CreatedTime.ToUniversalTime()
                        ResolvedAtUtc = if ($a.CompletedTime) { $a.CompletedTime.ToUniversalTime() } else { $null }
                        ReviewerUpn   = $a.Response.Responder.UserPrincipalName
                        Decision      = $a.Response.Response
                        Rationale     = $a.Response.Comments
                    })
                }
            }
        } catch {
            if ($_.Exception.Message -match '403|Forbidden') {
                $denied.Add($env.EnvironmentName)
            } else {
                throw
            }
        }
    }

    $status = if ($denied.Count -gt 0) { 'Anomaly' } elseif ($all.Count -eq 0) { 'NotApplicable' } else { 'Clean' }
    $reason = if ($denied.Count -gt 0) { "AccessDenied on $($denied.Count) environment(s): $($denied -join ',')" }
              elseif ($all.Count -eq 0) { "No approvals in window." }
              else { '' }

    [pscustomobject]@{
        Status          = $status
        Reason          = $reason
        Rows            = $all
        EnvironmentsDenied = $denied
    }
}
```

### 4.5 Export-Sup212QueueHealthBundle

The signed JSON bundle combines the configuration-export artifact (criterion #2) and the SLA report (criterion #4) into a single evidence bundle with a SHA-256 manifest.

```powershell
function Export-Sup212QueueHealthBundle {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [object[]] $ConfigRows,
        [Parameter(Mandatory)] [object]   $SlaReport,
        [string] $BundleRoot = "./evidence/2.12/queue-health-$($Session.RunId)"
    )

    if (-not $PSCmdlet.ShouldProcess($BundleRoot, 'Emit signed queue-health bundle')) { return }

    New-Item -ItemType Directory -Path $BundleRoot -Force | Out-Null
    $configPath = Join-Path $BundleRoot 'config-export.json'
    $slaPath    = Join-Path $BundleRoot 'sla-report.json'

    $ConfigRows | ConvertTo-Json -Depth 6 | Out-File -FilePath $configPath -Encoding utf8
    $SlaReport  | ConvertTo-Json -Depth 8 | Out-File -FilePath $slaPath -Encoding utf8

    $anomalies = @($ConfigRows | Where-Object { $_.Status -ne 'Clean' }).Count +
                 $(if ($SlaReport.Status -ne 'Clean') { 1 } else { 0 })
    $status = if ($anomalies -gt 0) { 'Anomaly' } else { 'Clean' }
    $reason = if ($anomalies -gt 0) { "$anomalies anomaly row(s) in bundle — see SLA breach and/or config defects." } else { '' }

    $manifest = New-Sup212EvidenceManifest `
        -Session $Session `
        -Criterion 'queue-health' `
        -Status $status -Reason $reason `
        -Artifacts @($configPath, $slaPath) `
        -Extras @{ criteria = @('#2', '#4') }

    $manifestPath = Join-Path $BundleRoot 'manifest.json'
    $manifest | ConvertTo-Json -Depth 6 | Out-File -FilePath $manifestPath -Encoding utf8
    $manifest
}
```

---

## §5 — HITL Reviewer-Decision Audit Extraction (Verification Criterion #5)

Criterion #5 requires a random sample of N=25 reviewer decisions per quarter where every row has non-null `ReviewerUpn`, `Timestamp`, `Decision` ∈ {Approve, Reject, Escalate}, and `Rationale`, traceable to the original agent interaction and (for Agent Framework flows) to the originating request ID and checkpoint. This section automates extraction from the Purview unified audit log and the Entra directory-audit log, joins the two, runs non-null validation, and emits a signed quarterly extract.

The helpers in this section are **read-only against audit surfaces**. They do not mutate state. They require `AuditLog.Read.All` plus PIM-elevated Compliance Administrator for the unified audit read.

### 5.1 Ingestion-lag guard

Unified-audit-log rows for AI activity are subject to ingestion delays that can exceed 30 minutes. A query that ends in the past five minutes will routinely undercount. Every §5 helper enforces a **lookback buffer** — it refuses to run against an `-End` within the buffer unless the operator explicitly passes `-AcceptIngestionLag`, in which case the manifest records the acceptance.

```powershell
function Assert-Sup212AuditIngestionBuffer {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [datetime] $End,
        [int] $LookbackBufferMinutes = 45,
        [switch] $AcceptIngestionLag
    )
    $now = (Get-Date).ToUniversalTime()
    $threshold = $now.AddMinutes(-$LookbackBufferMinutes)
    if ($End -gt $threshold -and -not $AcceptIngestionLag) {
        throw [System.InvalidOperationException]::new(
            "Sup212-IngestionLag: End ($End) is within $LookbackBufferMinutes-minute ingestion buffer. Pass -AcceptIngestionLag to override; the acceptance will be recorded in the evidence manifest.")
    }
    [pscustomobject]@{
        Now                     = $now.ToString('o')
        End                     = $End.ToString('o')
        LookbackBufferMinutes   = $LookbackBufferMinutes
        AcceptedWithinBuffer    = [bool]$AcceptIngestionLag
    }
}
```

### 5.2 Get-Sup212ReviewerDecisionAudit

This helper pulls AI-activity rows from the Purview unified audit log and joins them to the Entra directory-audit log to resolve reviewer UPN where the audit row has only an object ID. It is the canonical source for criterion #5.

```powershell
function Get-Sup212ReviewerDecisionAudit {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [datetime] $Start,
        [Parameter(Mandatory)] [datetime] $End,
        [int] $LookbackBufferMinutes = 45,
        [switch] $AcceptIngestionLag,
        [ValidateSet('UnifiedAudit','PowerPlatform','Both')]
        [string] $Source = 'Both'
    )

    $buffer = Assert-Sup212AuditIngestionBuffer -End $End `
        -LookbackBufferMinutes $LookbackBufferMinutes `
        -AcceptIngestionLag:$AcceptIngestionLag

    if (-not $Session.ExchangeConnected -and $Source -ne 'PowerPlatform') {
        return [pscustomobject]@{
            Status='Error'; Reason='Sup212-NoExo: Initialize-Sup212Session with -ConnectExchange for unified audit reads.'; Rows=@()
        }
    }

    $rows = [System.Collections.Generic.List[object]]::new()

    if ($Source -in 'UnifiedAudit','Both') {
        $ua = Invoke-Sup212Throttled {
            Search-UnifiedAuditLog -StartDate $Start -EndDate $End `
                -RecordType AI -ResultSize 5000 -SessionCommand ReturnLargeSet
        }
        foreach ($row in $ua) {
            $d = $row.AuditData | ConvertFrom-Json -ErrorAction SilentlyContinue
            if (-not $d) { continue }
            if ($d.Operation -notmatch 'Review|Approve|Reject|Escalate|Handoff|ApprovalResponse') { continue }
            $rows.Add([pscustomobject]@{
                Source        = 'UnifiedAudit'
                RecordId      = $row.Identity
                TimestampUtc  = ([datetime]$row.CreationDate).ToUniversalTime()
                Operation     = $d.Operation
                ReviewerId    = $d.UserId
                ReviewerUpn   = $d.UserPrincipalName
                AgentId       = $d.AgentId
                ConversationId= $d.ConversationId
                RequestId     = $d.RequestId
                CheckpointId  = $d.CheckpointId
                Decision      = $d.Decision
                Rationale     = $d.Justification
            })
        }
    }

    if ($Source -in 'PowerPlatform','Both') {
        $pp = Get-Sup212PowerAutomateApprovalHistory -Session $Session -Start $Start -End $End
        if ($pp.Status -eq 'Clean' -or $pp.Status -eq 'NotApplicable') {
            foreach ($a in $pp.Rows) {
                if (-not $a.ResolvedAtUtc) { continue }
                $rows.Add([pscustomobject]@{
                    Source         = 'PowerAutomate'
                    RecordId       = $a.ApprovalId
                    TimestampUtc   = $a.ResolvedAtUtc
                    Operation      = 'ApprovalResponse'
                    ReviewerId     = $null
                    ReviewerUpn    = $a.ReviewerUpn
                    AgentId        = $a.AgentId
                    ConversationId = $null
                    RequestId      = $null
                    CheckpointId   = $null
                    Decision       = $a.Decision
                    Rationale      = $a.Rationale
                })
            }
        }
    }

    # Resolve UPN where only object ID is present
    $needsResolve = $rows | Where-Object { -not $_.ReviewerUpn -and $_.ReviewerId }
    foreach ($r in $needsResolve) {
        try {
            $u = Invoke-Sup212Throttled { Get-MgUser -UserId $r.ReviewerId -Property UserPrincipalName }
            $r.ReviewerUpn = $u.UserPrincipalName
        } catch {
            # Leave UPN null; will be flagged in validation
        }
    }

    # Non-null validation — emit Anomaly rows (never Clean) for null UPN / null Decision / null Rationale
    $validated = $rows | ForEach-Object {
        $missing = @()
        if (-not $_.ReviewerUpn) { $missing += 'ReviewerUpn' }
        if (-not $_.Decision)    { $missing += 'Decision' }
        if (-not $_.Rationale)   { $missing += 'Rationale' }
        if (-not $_.TimestampUtc){ $missing += 'TimestampUtc' }
        $_ | Add-Member -NotePropertyName NonNullValidation `
                        -NotePropertyValue (if ($missing) { 'Anomaly' } else { 'Clean' }) -PassThru |
            Add-Member -NotePropertyName MissingFields `
                        -NotePropertyValue $missing -PassThru
    }

    $anomalies = ($validated | Where-Object NonNullValidation -eq 'Anomaly').Count
    $status = if ($validated.Count -eq 0) { 'NotApplicable' }
              elseif ($anomalies -gt 0)   { 'Anomaly' }
              else                        { 'Clean' }
    $reason = if ($validated.Count -eq 0) { 'No reviewer decisions in window.' }
              elseif ($anomalies -gt 0)   { "$anomalies of $($validated.Count) row(s) failed non-null validation." }
              else                        { '' }

    [pscustomobject]@{
        Status           = $status
        Reason           = $reason
        Rows             = $validated
        Window           = @{ Start=$Start.ToString('o'); End=$End.ToString('o') }
        IngestionBuffer  = $buffer
        TotalRows        = $validated.Count
        AnomalyRows      = $anomalies
    }
}
```

### 5.3 Export-Sup212QuarterlyDecisionSample

Pulls a random sample of N=25 decisions per quarter (criterion #5 sample size), signs and hashes the sample, and emits the evidence bundle. Sampling uses a cryptographic RNG seed recorded in the manifest so that the sample is deterministically reproducible from the seed + full population.

```powershell
function Export-Sup212QuarterlyDecisionSample {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [datetime] $Start,
        [Parameter(Mandatory)] [datetime] $End,
        [int] $SampleSize = 25,
        [string] $BundleRoot = "./evidence/2.12/reviewer-decisions-$($Session.RunId)"
    )

    $decisions = Get-Sup212ReviewerDecisionAudit -Session $Session -Start $Start -End $End

    if ($decisions.Status -eq 'Error') { return $decisions }

    if ($decisions.Rows.Count -lt $SampleSize -and $decisions.Rows.Count -gt 0) {
        Write-Warning "Sup212: population ($($decisions.Rows.Count)) smaller than sample size ($SampleSize); using full population."
        $SampleSize = $decisions.Rows.Count
    }

    $sampleResult = Get-Sup212SamplePopulation -Population $decisions.Rows -SampleSize $SampleSize

    if (-not $PSCmdlet.ShouldProcess($BundleRoot, 'Emit signed quarterly decision sample')) { return }
    New-Item -ItemType Directory -Path $BundleRoot -Force | Out-Null
    $populationPath = Join-Path $BundleRoot 'population.json'
    $samplePath     = Join-Path $BundleRoot 'sample.json'
    $decisions.Rows  | ConvertTo-Json -Depth 6 | Out-File -FilePath $populationPath -Encoding utf8
    $sampleResult.Sample | ConvertTo-Json -Depth 6 | Out-File -FilePath $samplePath -Encoding utf8

    $manifest = New-Sup212EvidenceManifest `
        -Session $Session `
        -Criterion 'reviewer-decision-audit' `
        -Status $decisions.Status -Reason $decisions.Reason `
        -Artifacts @($populationPath, $samplePath) `
        -Extras @{
            criterion_number = '#5'
            sample_size      = $SampleSize
            population_size  = $decisions.Rows.Count
            anomaly_rows     = $decisions.AnomalyRows
            sample_seed_b64  = $sampleResult.SeedBase64
            window           = $decisions.Window
            ingestion_buffer = $decisions.IngestionBuffer
        }
    $manifestPath = Join-Path $BundleRoot 'manifest.json'
    $manifest | ConvertTo-Json -Depth 8 | Out-File -FilePath $manifestPath -Encoding utf8
    $manifest
}
```

---

## §6 — Agent Framework Evidence Export (Verification Criterion #8)

Microsoft Agent Framework's human-in-the-loop pattern uses `RequestPort` / `request_info()` to pause an executor, preserve state in a checkpoint, emit a request to an external supervisor, and resume the workflow with the reviewer's response payload. For FINRA Rule 3110 purposes, the evidence unit is the tuple **(request ID, checkpoint state at pause, reviewer response payload, final executor output)**, retained for six years per [Control 2.13](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md).

This section produces an **idempotent** export of that tuple. Idempotency is required because the export feeds a WORM store; re-running the export must not create duplicate entries, must not overwrite previously signed records, and must detect when an existing record was tampered with by comparing content hashes.

### 6.1 Get-Sup212AgentFrameworkConfig

Reads the endpoint configuration from `sup212.config.json` and validates it. Missing / placeholder fields return `NotApplicable` — not `Clean` — so the orchestrator in §13 refuses to mark criterion #8 as satisfied when the Agent Framework path is unwired.

```powershell
function Get-Sup212AgentFrameworkConfig {
    [CmdletBinding()]
    param(
        [string] $ConfigPath = './sup212.config.json'
    )
    if (-not (Test-Path $ConfigPath)) {
        return [pscustomobject]@{ Status='NotApplicable'; Reason="Config missing at $ConfigPath."; Config=$null }
    }
    $c = Get-Content $ConfigPath -Raw | ConvertFrom-Json
    $missing = @()
    foreach ($f in 'agentFrameworkEvidenceEndpoint','agentFrameworkClientId','agentFrameworkCertThumbprint') {
        if (-not $c.$f) { $missing += $f }
    }
    if ($missing) {
        return [pscustomobject]@{
            Status='NotApplicable'
            Reason="AgentFrameworkUnwired: missing fields in sup212.config.json — $($missing -join ',')"
            Config=$c
        }
    }
    [pscustomobject]@{ Status='Clean'; Reason=''; Config=$c }
}
```

### 6.2 Get-Sup212AgentFrameworkHitlConfig

Per-flow helper that verifies the HITL pattern is wired: every production workflow in scope has at least one `RequestPort` node, a response handler, and checkpointing enabled. Missing wiring → `Anomaly`, not `Clean`.

```powershell
function Get-Sup212AgentFrameworkHitlConfig {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [object] $AgfConfig,
        [Parameter(Mandatory)] [string[]] $WorkflowIds
    )
    $cfg = $AgfConfig.Config
    $results = foreach ($wfId in $WorkflowIds) {
        try {
            $def = Invoke-Sup212Throttled {
                Invoke-RestMethod -Method GET `
                    -Uri ("$($cfg.agentFrameworkEvidenceEndpoint.TrimEnd('/'))/workflows/$wfId") `
                    -Authentication Certificate `
                    -CertificateThumbprint $cfg.agentFrameworkCertThumbprint
            }
            $hasRequestPort = [bool]($def.nodes | Where-Object Type -eq 'RequestPort')
            $hasResponseHandler = [bool]($def.nodes | Where-Object Type -eq 'ResponseHandler')
            $hasCheckpointing = [bool]$def.checkpointing.enabled
            $status = if ($hasRequestPort -and $hasResponseHandler -and $hasCheckpointing) { 'Clean' } else { 'Anomaly' }
            $reason = if ($status -eq 'Clean') { '' } else {
                $gaps = @()
                if (-not $hasRequestPort)      { $gaps += 'NoRequestPort' }
                if (-not $hasResponseHandler)  { $gaps += 'NoResponseHandler' }
                if (-not $hasCheckpointing)    { $gaps += 'CheckpointingDisabled' }
                "HITL wiring gaps: $($gaps -join ',')"
            }
            [pscustomobject]@{
                WorkflowId         = $wfId
                HasRequestPort     = $hasRequestPort
                HasResponseHandler = $hasResponseHandler
                HasCheckpointing   = $hasCheckpointing
                Status             = $status
                Reason             = $reason
            }
        } catch {
            [pscustomobject]@{
                WorkflowId=$wfId; HasRequestPort=$null; HasResponseHandler=$null; HasCheckpointing=$null
                Status='Error'; Reason=$_.Exception.Message
            }
        }
    }
    $results
}
```

### 6.3 Export-Sup212AgentFrameworkEvidence (idempotent)

Pulls the `(requestId, checkpointState, responsePayload, finalOutput)` tuple for every HITL request resolved in the window, compares each tuple against any previously exported record under the same `requestId`, and writes **only new** records — plus an integrity report flagging any tuple whose hash disagrees with a previously exported record (which indicates either export-pipeline corruption or tampering in the source system). Both cases emit `Anomaly` and open an incident under [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).

```powershell
function Export-Sup212AgentFrameworkEvidence {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [datetime] $Start,
        [Parameter(Mandatory)] [datetime] $End,
        [Parameter(Mandatory)] [object]   $AgfConfig,
        [string] $BundleRoot = "./evidence/2.12/agf-hitl-$($Session.RunId)",
        [string] $PriorExportIndex = './evidence/2.12/agf-index.json'
    )

    if ($AgfConfig.Status -ne 'Clean') {
        return [pscustomobject]@{
            Status = $AgfConfig.Status
            Reason = "AgentFrameworkConfig: $($AgfConfig.Reason)"
        }
    }

    $cfg = $AgfConfig.Config
    $requests = Invoke-Sup212Throttled {
        Invoke-RestMethod -Method GET `
            -Uri ("$($cfg.agentFrameworkEvidenceEndpoint.TrimEnd('/'))/requests?start=$($Start.ToString('o'))&end=$($End.ToString('o'))") `
            -Authentication Certificate `
            -CertificateThumbprint $cfg.agentFrameworkCertThumbprint
    }

    # Cross-check: if run activity is non-zero but request count is zero, flag as Anomaly (defect #0.8)
    $runActivity = Invoke-Sup212Throttled {
        Invoke-RestMethod -Method GET `
            -Uri ("$($cfg.agentFrameworkEvidenceEndpoint.TrimEnd('/'))/runs/count?start=$($Start.ToString('o'))&end=$($End.ToString('o'))") `
            -Authentication Certificate `
            -CertificateThumbprint $cfg.agentFrameworkCertThumbprint
    }

    if (($requests.Count -eq 0) -and ($runActivity.count -gt 0)) {
        return [pscustomobject]@{
            Status = 'Anomaly'
            Reason = "Sup212-AgfCorrelationMismatch: zero HITL requests but $($runActivity.count) runs in window. Confirm RequestPort wiring is present (see §6.2)."
        }
    }

    if (-not $PSCmdlet.ShouldProcess($BundleRoot, 'Emit signed Agent Framework evidence bundle')) { return }
    New-Item -ItemType Directory -Path $BundleRoot -Force | Out-Null

    $index = if (Test-Path $PriorExportIndex) { Get-Content $PriorExportIndex -Raw | ConvertFrom-Json -AsHashtable } else { @{} }
    $newCount = 0
    $tamperCount = 0
    $tamperRows = [System.Collections.Generic.List[object]]::new()

    foreach ($r in $requests) {
        $tuple = [ordered]@{
            requestId         = $r.requestId
            workflowId        = $r.workflowId
            pausedAtUtc       = $r.pausedAtUtc
            resumedAtUtc      = $r.resumedAtUtc
            checkpointState   = $r.checkpointState
            reviewerResponse  = $r.responsePayload
            finalOutput       = $r.finalOutput
            reviewerUpn       = $r.reviewerUpn
            decision          = $r.decision
            rationale         = $r.rationale
        }
        $json = ($tuple | ConvertTo-Json -Depth 10 -Compress)
        $hash = [BitConverter]::ToString(
            [System.Security.Cryptography.SHA256]::HashData([System.Text.Encoding]::UTF8.GetBytes($json))
        ).Replace('-', '').ToLowerInvariant()

        if ($index.ContainsKey($r.requestId)) {
            if ($index[$r.requestId].sha256 -ne $hash) {
                $tamperCount++
                $tamperRows.Add([pscustomobject]@{
                    RequestId      = $r.requestId
                    PriorSha256    = $index[$r.requestId].sha256
                    CurrentSha256  = $hash
                    PriorExportRef = $index[$r.requestId].exportPath
                })
            }
            continue   # idempotent: skip already-exported
        }

        $exportPath = Join-Path $BundleRoot "$($r.requestId).json"
        $json | Out-File -FilePath $exportPath -Encoding utf8 -NoNewline
        $index[$r.requestId] = @{ sha256=$hash; exportPath=$exportPath; exportedAtUtc=(Get-Date).ToUniversalTime().ToString('o') }
        $newCount++
    }

    $index | ConvertTo-Json -Depth 6 | Out-File -FilePath $PriorExportIndex -Encoding utf8
    $tamperPath = Join-Path $BundleRoot 'integrity-report.json'
    $tamperRows | ConvertTo-Json -Depth 4 | Out-File -FilePath $tamperPath -Encoding utf8

    $status = if ($tamperCount -gt 0) { 'Anomaly' } else { 'Clean' }
    $reason = if ($tamperCount -gt 0) { "Integrity mismatch on $tamperCount request(s) — open Control 3.4 incident." } else { '' }

    $manifest = New-Sup212EvidenceManifest `
        -Session $Session `
        -Criterion 'agent-framework-evidence' `
        -Status $status -Reason $reason `
        -Artifacts @($tamperPath, $PriorExportIndex) `
        -Extras @{
            criterion_number   = '#8'
            requests_in_window = $requests.Count
            runs_in_window     = $runActivity.count
            new_records        = $newCount
            tamper_count       = $tamperCount
        }

    $manifestPath = Join-Path $BundleRoot 'manifest.json'
    $manifest | ConvertTo-Json -Depth 8 | Out-File -FilePath $manifestPath -Encoding utf8
    $manifest
}
```

---

## §7 — Principal Registration Verification (Verification Criterion #3)

Criterion #3 requires that for 100% of designated principals listed in the WSP addendum, the firm can produce current CRD verification (Series 24 for broker-dealer supervisory scope; Series 66 / 65 for RIA supervisory scope) dated within the last 90 days. CRD (Central Registration Depository) and WebCRD are FINRA-operated systems; **programmatic access is not available to all firms**, and the PowerShell helpers here cannot reach FINRA Gateway directly. The helper pattern below supports both automated extraction (where the firm has contracted CRD data-feed access) and the documented manual process (CRD printout / WebCRD attestation loaded from a secured staging location).

### 7.1 Test-Sup212PrincipalRegistration

```powershell
function Test-Sup212PrincipalRegistration {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object]   $Session,
        [Parameter(Mandatory)] [object[]] $Principals,          # @(@{ Upn=..; FullName=..; CrdNumber=..; RequiredExam=..; Scope=..; })
        [ValidateSet('CrdFeed','ManualAttestation')]
        [string] $Mode = 'ManualAttestation',
        [string] $AttestationStoreRoot = './evidence/2.12/principal-registrations',
        [int]    $FreshnessDays = 90
    )

    $results = foreach ($p in $Principals) {
        $now = (Get-Date).ToUniversalTime()
        $freshnessCutoff = $now.AddDays(-$FreshnessDays)

        switch ($Mode) {
            'CrdFeed' {
                # Placeholder: firms with contracted CRD data feeds replace this with the vendor client call.
                # The helper returns NotApplicable (not Clean) if the feed is not wired — defect #0.10.
                [pscustomobject]@{
                    Upn           = $p.Upn
                    FullName      = $p.FullName
                    CrdNumber     = $p.CrdNumber
                    RequiredExam  = $p.RequiredExam
                    Scope         = $p.Scope
                    Status        = 'NotApplicable'
                    Reason        = 'CrdAccessNotAvailable: wire the vendor-specific CRD feed client, or use -Mode ManualAttestation.'
                }
            }
            'ManualAttestation' {
                $attPath = Join-Path $AttestationStoreRoot "$($p.CrdNumber).json"
                if (-not (Test-Path $attPath)) {
                    [pscustomobject]@{
                        Upn=$p.Upn; FullName=$p.FullName; CrdNumber=$p.CrdNumber
                        RequiredExam=$p.RequiredExam; Scope=$p.Scope
                        Status='Anomaly'
                        Reason="ManualAttestationMissing at $attPath. Load the CRD/WebCRD extract through the documented manual process."
                    }
                    continue
                }
                $a = Get-Content $attPath -Raw | ConvertFrom-Json
                $asOf = [datetime]$a.asOfUtc
                $examOk = $a.currentExams -contains $p.RequiredExam
                $freshOk = $asOf -ge $freshnessCutoff
                $signerOk = [bool]$a.signerUpn
                $status = if ($examOk -and $freshOk -and $signerOk) { 'Clean' } else { 'Anomaly' }
                $r = @()
                if (-not $examOk)   { $r += "RequiredExam $($p.RequiredExam) not in attestation." }
                if (-not $freshOk)  { $r += "AttestationStale: asOf=$($asOf.ToString('o')); cutoff=$($freshnessCutoff.ToString('o'))." }
                if (-not $signerOk) { $r += 'SignerUpnMissing on attestation.' }

                [pscustomobject]@{
                    Upn          = $p.Upn
                    FullName     = $p.FullName
                    CrdNumber    = $p.CrdNumber
                    RequiredExam = $p.RequiredExam
                    Scope        = $p.Scope
                    AsOfUtc      = $a.asOfUtc
                    CurrentExams = $a.currentExams
                    SignerUpn    = $a.signerUpn
                    Status       = $status
                    Reason       = ($r -join ' ')
                }
            }
        }
    }

    $results
}
```

### 7.2 Export-Sup212PrincipalAttestationBundle

Rolls the per-principal results into a signed quarterly attestation record and emits evidence via the manifest helper.

```powershell
function Export-Sup212PrincipalAttestationBundle {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [object[]] $PrincipalResults,
        [string] $BundleRoot = "./evidence/2.12/principal-registration-$($Session.RunId)"
    )
    if (-not $PSCmdlet.ShouldProcess($BundleRoot, 'Emit principal-attestation bundle')) { return }
    New-Item -ItemType Directory -Path $BundleRoot -Force | Out-Null
    $p = Join-Path $BundleRoot 'principals.json'
    $PrincipalResults | ConvertTo-Json -Depth 6 | Out-File -FilePath $p -Encoding utf8

    $anomalies = ($PrincipalResults | Where-Object Status -eq 'Anomaly').Count
    $status = if ($anomalies -gt 0) { 'Anomaly' } else { 'Clean' }
    $reason = if ($anomalies -gt 0) { "$anomalies principal(s) failed registration check." } else { '' }

    $manifest = New-Sup212EvidenceManifest `
        -Session $Session -Criterion 'principal-registration' `
        -Status $status -Reason $reason -Artifacts @($p) `
        -Extras @{ criterion_number='#3'; principal_count=$PrincipalResults.Count; anomaly_count=$anomalies }
    $manifest | ConvertTo-Json -Depth 6 | Out-File -FilePath (Join-Path $BundleRoot 'manifest.json') -Encoding utf8
    $manifest
}
```

---

## §8 — Sampling Protocol Runner

Criterion #7 (Rule 2210) and the zone-specific sampling rates in the control document require a reproducible random sample from the agent output pool. This section provides a cryptographically-seeded sampler, a supervision-register writer that records disposition, and a disposition tracker that reconciles sampled items against reviewer decisions.

### 8.1 Get-Sup212SamplePopulation

```powershell
function Get-Sup212SamplePopulation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object[]] $Population,
        [Parameter(Mandatory)] [int]      $SampleSize,
        [byte[]] $SeedBytes      # optional — for replay
    )

    if ($SampleSize -lt 0) {
        throw "Sup212-BadSampleSize: $SampleSize"
    }
    if ($Population.Count -eq 0) {
        return [pscustomobject]@{
            Status='NotApplicable'; Reason='Empty population.'; Sample=@(); SeedBase64=$null
        }
    }
    if ($SampleSize -ge $Population.Count) {
        return [pscustomobject]@{
            Status='Clean'; Reason='SampleSizeGePopulation — returning full population.'; Sample=$Population; SeedBase64=$null
        }
    }

    if (-not $SeedBytes) {
        $SeedBytes = [byte[]]::new(32)
        [System.Security.Cryptography.RandomNumberGenerator]::Fill($SeedBytes)
    }
    $seedB64 = [Convert]::ToBase64String($SeedBytes)

    # Deterministic Fisher-Yates driven by SHA-256 of seed + index
    $n = $Population.Count
    $indices = 0..($n - 1)
    for ($i = $n - 1; $i -gt 0; $i--) {
        $buf = [System.Text.Encoding]::UTF8.GetBytes("$seedB64|$i")
        $hash = [System.Security.Cryptography.SHA256]::HashData($buf)
        $j = [bitconverter]::ToUInt32($hash, 0) % ($i + 1)
        $tmp = $indices[$i]; $indices[$i] = $indices[$j]; $indices[$j] = $tmp
    }
    $sample = $indices[0..($SampleSize - 1)] | ForEach-Object { $Population[$_] }

    [pscustomobject]@{
        Status      = 'Clean'
        Reason      = ''
        Sample      = $sample
        SeedBase64  = $seedB64
        Algorithm   = 'FisherYates-SHA256'
        SampleSize  = $SampleSize
        Population  = $Population.Count
    }
}
```

### 8.2 Write-Sup212SupervisionRegister

Appends each sampled item to the supervision register (a SharePoint list or CSV). Each entry carries the sampling seed, sample index, and initial disposition `Pending`; reviewers later update disposition through the §4 / §5 review paths, and `Test-Sup212SamplingDisposition` reconciles them.

```powershell
function Write-Sup212SupervisionRegister {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [object[]] $SampleRows,
        [Parameter(Mandatory)] [string]   $SeedBase64,
        [string] $RegisterCsvPath = './evidence/2.12/supervision-register.csv'
    )
    if (-not $PSCmdlet.ShouldProcess($RegisterCsvPath, 'Append supervision register rows')) { return }
    $dir = Split-Path -Parent $RegisterCsvPath
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }

    $rows = $SampleRows | ForEach-Object {
        [pscustomobject]@{
            RunId          = $Session.RunId
            SampledAtUtc   = (Get-Date).ToUniversalTime().ToString('o')
            SampleSeedB64  = $SeedBase64
            AgentId        = $_.AgentId
            ConversationId = $_.ConversationId
            RequestId      = $_.RequestId
            Zone           = $_.AgentZone
            Disposition    = 'Pending'
            ReviewerUpn    = ''
            DecisionAtUtc  = ''
            Decision       = ''
            Rationale      = ''
        }
    }
    if (Test-Path $RegisterCsvPath) {
        $rows | Export-Csv -Path $RegisterCsvPath -Append -NoTypeInformation -Encoding utf8
    } else {
        $rows | Export-Csv -Path $RegisterCsvPath -NoTypeInformation -Encoding utf8
    }
    [pscustomobject]@{ Status='Clean'; Reason=''; Appended=$rows.Count; Path=$RegisterCsvPath }
}
```

### 8.3 Test-Sup212SamplingDisposition

Reconciles pending register rows against reviewer decisions; rows still `Pending` beyond the zone SLA window are flagged as `Anomaly`.

```powershell
function Test-Sup212SamplingDisposition {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $RegisterCsvPath,
        [Parameter(Mandatory)] [hashtable] $SlaMinutesByZone
    )
    if (-not (Test-Path $RegisterCsvPath)) {
        return [pscustomobject]@{ Status='Error'; Reason='RegisterMissing' }
    }
    $reg = Import-Csv $RegisterCsvPath
    $now = (Get-Date).ToUniversalTime()
    $pending = foreach ($r in ($reg | Where-Object Disposition -eq 'Pending')) {
        $age = ($now - ([datetime]$r.SampledAtUtc).ToUniversalTime()).TotalMinutes
        $threshold = $SlaMinutesByZone[$r.Zone]
        [pscustomobject]@{
            AgentId=$r.AgentId; Zone=$r.Zone; AgeMin=[math]::Round($age,1); Threshold=$threshold
            Breached = ($threshold -and $age -gt $threshold)
        }
    }
    $breaches = ($pending | Where-Object Breached).Count
    [pscustomobject]@{
        Status   = if ($breaches -gt 0) { 'Anomaly' } else { 'Clean' }
        Reason   = if ($breaches -gt 0) { "$breaches pending sample(s) past zone SLA." } else { '' }
        Pending  = $pending
    }
}
```

---

## §9 — Rule 3120 Annual-Testing Harness (Verification Criterion #6)

FINRA Rule 3120 requires annual testing of the firm's supervisory controls with documented **design effectiveness**, **operating effectiveness**, **exceptions**, and **remediation**. This section packages the tests as Pester 5 suites organized into named namespaces. Each namespace tests one area of the control; the harness refuses to mark results `Clean` when any test was `Skipped` (defect #0.11).

### 9.1 Namespace map

| Namespace | Area | Typical `It` count |
|---|---|---|
| `WSP`       | WSP addendum coverage (criterion #1) | 4–6 |
| `HITL`      | HITL trigger firing (criterion #2) | 6–10 |
| `QUEUE`     | Review queue SLA adherence (criterion #4) | 4–6 |
| `REVIEWER`  | Reviewer-decision non-null validation (criterion #5) | 3–5 |
| `PRINCIPAL` | Principal registration freshness (criterion #3) | 2–4 |
| `SAMPLING`  | Sampling-protocol reproducibility and rate (criterion #7 support) | 3–5 |
| `R3120`     | Self-test: does the harness itself run? | 1–2 |
| `R2210`     | Communication-classification coverage (criterion #7) | 4–6 |
| `SPONSOR`   | Sponsor attestation quarterly-review freshness (criterion #8 support) | 2–4 |
| `AGF`       | Agent Framework evidence integrity (criterion #8) | 3–5 |
| `SIEM`      | SIEM forwarding canary (criterion support for 1.7/3.4 linkage) | 2–3 |

### 9.2 Invoke-Sup212Rule3120Harness

```powershell
function Invoke-Sup212Rule3120Harness {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [string] $TestRoot  = './tests/2.12',
        [string] $BundleRoot = "./evidence/2.12/rule-3120-$($Session.RunId)",
        [string[]] $Namespace = @('WSP','HITL','QUEUE','REVIEWER','PRINCIPAL','SAMPLING','R3120','R2210','SPONSOR','AGF','SIEM')
    )
    $null = Assert-Sup212ShellHost -RequirePester

    if (-not $PSCmdlet.ShouldProcess($BundleRoot, 'Run Rule 3120 Pester harness')) { return }
    New-Item -ItemType Directory -Path $BundleRoot -Force | Out-Null

    $cfg = New-PesterConfiguration
    $cfg.Run.Path = $TestRoot
    $cfg.Run.PassThru = $true
    $cfg.Filter.Tag = $Namespace
    $cfg.Output.Verbosity = 'Detailed'
    $cfg.TestResult.Enabled = $true
    $cfg.TestResult.OutputFormat = 'NUnitXml'
    $cfg.TestResult.OutputPath = (Join-Path $BundleRoot 'pester-results.xml')

    $result = Invoke-Pester -Configuration $cfg

    $status = if ($result.FailedCount -gt 0)   { 'Anomaly' }
              elseif ($result.SkippedCount -gt 0) { 'Anomaly' }
              elseif ($result.TotalCount -eq 0)   { 'NotApplicable' }
              else                                { 'Clean' }
    $reason = if ($result.FailedCount -gt 0)   { "$($result.FailedCount) test(s) failed." }
              elseif ($result.SkippedCount -gt 0) { "$($result.SkippedCount) test(s) skipped — harness refuses Clean when skips are present." }
              elseif ($result.TotalCount -eq 0)   { 'No tests discovered — confirm $TestRoot is populated.' }
              else                                { '' }

    $summary = [pscustomobject]@{
        Passed   = $result.PassedCount
        Failed   = $result.FailedCount
        Skipped  = $result.SkippedCount
        Total    = $result.TotalCount
        Duration = $result.Duration.ToString()
        Namespaces = $Namespace
        Status   = $status
        Reason   = $reason
    }
    $summary | ConvertTo-Json -Depth 4 | Out-File -FilePath (Join-Path $BundleRoot 'summary.json') -Encoding utf8

    $manifest = New-Sup212EvidenceManifest `
        -Session $Session -Criterion 'rule-3120-annual-test' `
        -Status $status -Reason $reason `
        -Artifacts @((Join-Path $BundleRoot 'pester-results.xml'), (Join-Path $BundleRoot 'summary.json')) `
        -Extras @{ criterion_number='#6'; passed=$result.PassedCount; failed=$result.FailedCount; skipped=$result.SkippedCount }
    $manifest | ConvertTo-Json -Depth 6 | Out-File -FilePath (Join-Path $BundleRoot 'manifest.json') -Encoding utf8
    $manifest
}
```

### 9.3 Example Pester files (excerpt)

Keep each namespace in its own `.Tests.ps1` file under `./tests/2.12/`.

`WSP.Tests.ps1`:

```powershell
Describe 'WSP addendum coverage' -Tag 'WSP' {
    BeforeAll {
        $wsp = Get-Content './evidence/2.12/wsp-addendum.metadata.json' -Raw | ConvertFrom-Json
    }
    It 'names Control 2.12 explicitly' {
        $wsp.controlsReferenced | Should -Contain '2.12'
    }
    It 'enumerates supervision activities for every zone' {
        $wsp.zonesCovered | Sort-Object | Should -Be @('1','2','3')
    }
    It 'designates principals by name and registration' {
        ($wsp.designatedPrincipals | Measure-Object).Count | Should -BeGreaterThan 0
        $wsp.designatedPrincipals | ForEach-Object { $_.crdNumber | Should -Not -BeNullOrEmpty }
    }
    It 'was approved by a registered principal within the last 12 months' {
        ([datetime]::UtcNow - [datetime]$wsp.approvedAtUtc).TotalDays | Should -BeLessThan 366
        $wsp.approverCrdNumber | Should -Not -BeNullOrEmpty
    }
}
```

`HITL.Tests.ps1`:

```powershell
Describe 'HITL trigger firing' -Tag 'HITL' {
    BeforeAll {
        $cfg = Get-Content './evidence/2.12/queue-health/config-export.json' -Raw | ConvertFrom-Json
    }
    It 'every Zone 3 agent has at least one handoff or approval trigger' {
        foreach ($row in $cfg) {
            ($row.HandoffTriggers -or $row.ApprovalTriggers) | Should -BeTrue -Because "Agent $($row.AgentName) must have HITL wiring."
        }
    }
    It 'no Zone 3 agent is in Status=Error' {
        ($cfg | Where-Object Status -eq 'Error') | Should -BeNullOrEmpty
    }
}
```

`R2210.Tests.ps1` and the remaining namespaces follow the same shape — each asserts the presence and integrity of an evidence artifact produced by the `§3`–`§12` helpers, never the absence of an error.

---

## §10 — Rule 2210 Classification Pipeline (Verification Criterion #7)

FINRA Rule 2210 distinguishes **Correspondence** (≤25 retail investors in any 30 calendar-day period), **Retail Communication** (>25 retail investors), and **Institutional Communication** (institutional investors only). Each bucket carries a different supervisory requirement; Retail Communication requires **principal pre-use approval** unless one of the 2210(b)(1) exclusions applies (e.g., previously-approved templated content). This section classifies customer-facing outputs, attaches pre-use-approval evidence for Retail Communications, and emits criterion #7 evidence.

### 10.1 Invoke-Sup212Rule2210Classifier

```powershell
function Invoke-Sup212Rule2210Classifier {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object]   $Session,
        [Parameter(Mandatory)] [object[]] $Outputs,             # rows with { AgentId, OutputId, AudienceType, RetailCountIn30d, Body }
        [Parameter(Mandatory)] [string]   $PreApprovalCsvPath   # rows with { TemplateId/OutputId, ApprovalId, ApproverCrdNumber, ApprovedAtUtc, ExclusionCitation }
    )
    if (-not (Test-Path $PreApprovalCsvPath)) {
        return [pscustomobject]@{ Status='Error'; Reason="PreApprovalCsvMissing at $PreApprovalCsvPath." }
    }
    $approvals = Import-Csv $PreApprovalCsvPath

    $rows = foreach ($o in $Outputs) {
        $classification = switch ($o.AudienceType) {
            'InstitutionalOnly' { 'Institutional' }
            default {
                if ([int]$o.RetailCountIn30d -le 25) { 'Correspondence' } else { 'Retail' }
            }
        }
        $approval = $null
        $exclusion = $null
        $status = 'Clean'
        $reason = ''

        if ($classification -eq 'Retail') {
            $approval = $approvals | Where-Object { $_.OutputId -eq $o.OutputId -or $_.TemplateId -eq $o.TemplateId } | Select-Object -First 1
            if (-not $approval) {
                $status = 'Anomaly'
                $reason = 'RetailCommunicationWithoutPrincipalPreApproval — attach approval or document Rule 2210(b)(1) exclusion.'
            } else {
                if (-not $approval.ApproverCrdNumber) {
                    $status = 'Anomaly'; $reason = 'ApproverCrdNumberMissing on pre-approval row.'
                }
                if ($approval.ExclusionCitation) {
                    $exclusion = $approval.ExclusionCitation
                }
            }
        }

        [pscustomobject]@{
            AgentId        = $o.AgentId
            OutputId       = $o.OutputId
            AudienceType   = $o.AudienceType
            RetailCount30d = [int]$o.RetailCountIn30d
            Classification = $classification
            ApprovalId     = if ($approval) { $approval.ApprovalId } else { $null }
            ApproverCrd    = if ($approval) { $approval.ApproverCrdNumber } else { $null }
            ExclusionCitation = $exclusion
            Status         = $status
            Reason         = $reason
        }
    }

    $anomalies = ($rows | Where-Object Status -eq 'Anomaly').Count
    [pscustomobject]@{
        Status = if ($rows.Count -eq 0) { 'NotApplicable' } elseif ($anomalies -gt 0) { 'Anomaly' } else { 'Clean' }
        Reason = if ($rows.Count -eq 0) { 'No outputs supplied.' } elseif ($anomalies -gt 0) { "$anomalies classification anomaly row(s)." } else { '' }
        Rows   = $rows
        ClassificationSummary = $rows | Group-Object Classification | ForEach-Object {
            [pscustomobject]@{ Type=$_.Name; Count=$_.Count }
        }
    }
}
```

### 10.2 Export-Sup212Rule2210Bundle

```powershell
function Export-Sup212Rule2210Bundle {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [object] $ClassificationResult,
        [string] $BundleRoot = "./evidence/2.12/rule-2210-$($Session.RunId)"
    )
    if (-not $PSCmdlet.ShouldProcess($BundleRoot, 'Emit Rule 2210 classification bundle')) { return }
    New-Item -ItemType Directory -Path $BundleRoot -Force | Out-Null
    $p = Join-Path $BundleRoot 'classifications.json'
    $ClassificationResult | ConvertTo-Json -Depth 6 | Out-File -FilePath $p -Encoding utf8

    $manifest = New-Sup212EvidenceManifest `
        -Session $Session -Criterion 'rule-2210-classification' `
        -Status $ClassificationResult.Status -Reason $ClassificationResult.Reason `
        -Artifacts @($p) `
        -Extras @{ criterion_number='#7'; summary=$ClassificationResult.ClassificationSummary }
    $manifest | ConvertTo-Json -Depth 6 | Out-File -FilePath (Join-Path $BundleRoot 'manifest.json') -Encoding utf8
    $manifest
}
```

---

## §11 — Sponsor Attestation Runner

The sponsorship model documented in Control 2.26 (Entra Agent ID — Identity Governance for Agents) is operationalized through quarterly Entra access reviews targeting Zone 3 agents. This section pulls the review status, flags auto-approval (defect #0.12), and emits a signed quarterly attestation evidence bundle.

### 11.1 Get-Sup212SponsorAttestation

```powershell
function Get-Sup212SponsorAttestation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [string] $AccessReviewScheduleId
    )

    $schedule = Invoke-Sup212Throttled {
        Invoke-MgGraphRequest -Method GET `
            -Uri "https://graph.microsoft.com/v1.0/identityGovernance/accessReviews/definitions/$AccessReviewScheduleId"
    }
    $instances = (Invoke-Sup212PagedQuery `
        -Uri "https://graph.microsoft.com/v1.0/identityGovernance/accessReviews/definitions/$AccessReviewScheduleId/instances").Rows

    $defaultDecision = $schedule.settings.defaultDecision
    $defaultDecisionEnabled = $schedule.settings.defaultDecisionEnabled
    $autoApprovalAnomaly = ($defaultDecisionEnabled -eq $true -and $defaultDecision -eq 'Approve')

    $perInstance = foreach ($i in $instances) {
        $decisions = (Invoke-Sup212PagedQuery `
            -Uri "https://graph.microsoft.com/v1.0/identityGovernance/accessReviews/definitions/$AccessReviewScheduleId/instances/$($i.id)/decisions").Rows
        $autoCount = ($decisions | Where-Object { $_.justification -match 'auto|Not reviewed|default' }).Count
        [pscustomobject]@{
            InstanceId        = $i.id
            Status            = $i.status
            StartDateTime     = $i.startDateTime
            EndDateTime       = $i.endDateTime
            DecisionCount     = $decisions.Count
            AutoDecisionCount = $autoCount
        }
    }

    $status = if ($autoApprovalAnomaly) { 'Anomaly' } else { 'Clean' }
    $reason = if ($autoApprovalAnomaly) { 'AccessReviewAutoApprovalEnabled — defaultDecisionEnabled=true and defaultDecision=Approve. Reconfigure before relying on reviews for FINRA 3110 evidence.' } else { '' }

    [pscustomobject]@{
        ScheduleId              = $AccessReviewScheduleId
        DefaultDecision         = $defaultDecision
        DefaultDecisionEnabled  = $defaultDecisionEnabled
        Instances               = $perInstance
        Status                  = $status
        Reason                  = $reason
    }
}
```

### 11.2 Export-Sup212SponsorAttestationBundle

```powershell
function Export-Sup212SponsorAttestationBundle {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [object] $AttestationResult,
        [string] $BundleRoot = "./evidence/2.12/sponsor-attestation-$($Session.RunId)"
    )
    if (-not $PSCmdlet.ShouldProcess($BundleRoot, 'Emit sponsor-attestation bundle')) { return }
    New-Item -ItemType Directory -Path $BundleRoot -Force | Out-Null
    $p = Join-Path $BundleRoot 'attestation.json'
    $AttestationResult | ConvertTo-Json -Depth 6 | Out-File -FilePath $p -Encoding utf8
    $manifest = New-Sup212EvidenceManifest `
        -Session $Session -Criterion 'sponsor-attestation' `
        -Status $AttestationResult.Status -Reason $AttestationResult.Reason `
        -Artifacts @($p) -Extras @{ criterion_number='#8-support'; schedule_id=$AttestationResult.ScheduleId }
    $manifest | ConvertTo-Json -Depth 6 | Out-File -FilePath (Join-Path $BundleRoot 'manifest.json') -Encoding utf8
    $manifest
}
```

---

## §12 — SIEM Forwarding to Microsoft Sentinel

Supervision events — HITL decisions, escalations, SLA breaches, Rule 3120 test results — must be forwarded to the firm's SIEM for correlation with the broader controls in [Pillar 1 — Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and incident operations in [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md). This section ships events to Sentinel via the Logs Ingestion API with an integrity hash per batch, and verifies end-to-end plumbing with a canary.

### 12.1 Send-Sup212SentinelEvents

```powershell
function Send-Sup212SentinelEvents {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory)] [object]   $Session,
        [Parameter(Mandatory)] [object[]] $Events,
        [string] $ConfigPath = './sup212.config.json'
    )
    $c = Get-Content $ConfigPath -Raw | ConvertFrom-Json
    foreach ($f in 'sentinelDataCollectionEndpointUri','sentinelDcrImmutableId','sentinelStreamName') {
        if (-not $c.$f) {
            return [pscustomobject]@{ Status='NotApplicable'; Reason="SentinelUnwired: $f missing in $ConfigPath." }
        }
    }

    $token = (Get-AzAccessToken -ResourceUrl 'https://monitor.azure.com').Token
    if (-not $token) {
        return [pscustomobject]@{ Status='Error'; Reason='AzAccessTokenMissing — run Connect-AzAccount.' }
    }

    # Enrich every event with RunId, controlId, and a per-batch integrity hash
    $batchId = [guid]::NewGuid().ToString()
    $enriched = $Events | ForEach-Object {
        [ordered]@{
            TimeGenerated = (Get-Date).ToUniversalTime().ToString('o')
            ControlId     = '2.12'
            RunId         = $Session.RunId
            BatchId       = $batchId
            TenantCloud   = $Session.Cloud.EnvName
            EventType     = $_.EventType
            Payload       = $_.Payload
            PayloadSha256 = [BitConverter]::ToString(
                [System.Security.Cryptography.SHA256]::HashData(
                    [System.Text.Encoding]::UTF8.GetBytes(($_.Payload | ConvertTo-Json -Depth 10 -Compress))
                )
            ).Replace('-','').ToLowerInvariant()
        }
    }

    if (-not $PSCmdlet.ShouldProcess($c.sentinelDataCollectionEndpointUri, "Forward $($enriched.Count) event(s)")) { return }

    $body = $enriched | ConvertTo-Json -Depth 10 -AsArray
    $uri = "$($c.sentinelDataCollectionEndpointUri.TrimEnd('/'))/dataCollectionRules/$($c.sentinelDcrImmutableId)/streams/$($c.sentinelStreamName)?api-version=2023-01-01"

    try {
        Invoke-Sup212Throttled {
            Invoke-RestMethod -Method POST -Uri $uri -Body $body `
                -ContentType 'application/json' `
                -Headers @{ Authorization = "Bearer $token" }
        } | Out-Null
        [pscustomobject]@{
            Status='Clean'; Reason=''; BatchId=$batchId; EventCount=$enriched.Count
        }
    } catch {
        [pscustomobject]@{
            Status='Error'; Reason=$_.Exception.Message; BatchId=$batchId; EventCount=$enriched.Count
        }
    }
}
```

### 12.2 Test-Sup212SiemForwarding

End-to-end canary: emits a known-shape event and queries the target workspace for its appearance. Failure → `Anomaly`, not `Clean`.

```powershell
function Test-Sup212SiemForwarding {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [string] $ConfigPath = './sup212.config.json',
        [int]    $WaitSeconds = 180
    )
    $c = Get-Content $ConfigPath -Raw | ConvertFrom-Json
    if (-not $c.sentinelWorkspaceId) {
        return [pscustomobject]@{ Status='NotApplicable'; Reason='sentinelWorkspaceId missing in config.' }
    }
    $canaryId = [guid]::NewGuid().ToString()
    $send = Send-Sup212SentinelEvents -Session $Session -Events @(
        [pscustomobject]@{ EventType='Sup212Canary'; Payload=@{ canaryId=$canaryId } }
    )
    if ($send.Status -ne 'Clean') {
        return [pscustomobject]@{ Status='Error'; Reason="CanaryForwardFailed: $($send.Reason)" }
    }
    Start-Sleep -Seconds $WaitSeconds
    $kql = "$($c.sentinelStreamName) | where EventType == 'Sup212Canary' | where Payload contains '$canaryId' | take 1"
    $q = Invoke-AzOperationalInsightsQuery -WorkspaceId $c.sentinelWorkspaceId -Query $kql
    if ($q.Results.Count -eq 0) {
        return [pscustomobject]@{
            Status='Anomaly'
            Reason="CanaryNotObserved after $WaitSeconds s — Sentinel pipeline appears silently dropping events. Investigate DCR stream filters and table schema."
            CanaryId=$canaryId
        }
    }
    [pscustomobject]@{ Status='Clean'; Reason=''; CanaryId=$canaryId; Observed=$true }
}
```

---

## §13 — Scheduling (Power Automate + Scheduled Tasks)

None of the §4–§12 helpers are intended to run interactively in perpetuity. The following schedule aligns with the verification cadence enumerated in the control document and is the pattern we recommend.

| Helper | Cadence | Trigger | Runs as | Notes |
|---|---|---|---|---|
| `Export-Sup212QueueHealthBundle` (§4.5) | Daily 06:00 UTC | Scheduled task | Managed identity with Graph + Power Platform reader | 7-day rolling window |
| `Export-Sup212QuarterlyDecisionSample` (§5.3) | Quarterly T+2 (two business days after quarter-end) | Scheduled task | Managed identity with `AuditLog.Read.All` | Lookback buffer = 45 min |
| `Export-Sup212AgentFrameworkEvidence` (§6.3) | Every 6 hours | Scheduled task | App registration, cert-based auth | Idempotent; safe to re-run |
| `Test-Sup212PrincipalRegistration` (§7.1) | Quarterly T+1 | Scheduled task | Compliance Officer staging share | CRD feed OR manual attestation |
| `Invoke-Sup212Rule3120Harness` (§9.2) | Annually + on-demand | Pipeline (Azure DevOps / GitHub Actions) | Service principal | Full namespace set |
| `Invoke-Sup212Rule2210Classifier` (§10.1) | Weekly Monday 07:00 UTC | Power Automate scheduled cloud flow | Runs as marketing-review service account | Population source: marketing-review DB |
| `Get-Sup212SponsorAttestation` (§11.1) | Quarterly, aligned to access-review cadence | Scheduled task | Managed identity with `AccessReview.Read.All` |
| `Test-Sup212SiemForwarding` (§12.2) | Daily 07:00 UTC | Scheduled task | Reader on workspace | Canary event |

Example scheduled-task registration (Windows; mirror on Linux via `systemd` timers):

```powershell
$action  = New-ScheduledTaskAction -Execute 'pwsh.exe' `
    -Argument '-NoProfile -File C:\ops\fsi-agentgov\Run-Sup212Daily.ps1'
$trigger = New-ScheduledTaskTrigger -Daily -At '06:00'
$settings= New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName 'Sup212-Daily' -Action $action -Trigger $trigger `
    -Settings $settings -RunLevel Highest -User 'NT AUTHORITY\SYSTEM' -Force
```

`Run-Sup212Daily.ps1` orchestrates §4, §11, §12 and emits a daily manifest; the quarterly orchestrator `Run-Sup212Quarterly.ps1` adds §5, §7, and §10.

---

## §14 — Evidence Retention Discipline

Every artifact produced by this playbook is a books-and-records item under FINRA Rule 4511 and SEC Rule 17a-4(b)(4). Retention discipline:

- **Retention period:** 6 years from creation (or 6 years from resolution for Agent Framework request tuples). Easily accessible for the first 2 years.
- **Medium:** WORM-backed storage (Microsoft Purview retention policies, SharePoint/OneDrive retention labels configured for immutability, or a compliant 17a-4(f) audit-trail alternative). The `PimJustification` field and the SHA-256 artifact hashes in every manifest are the integrity anchors.
- **Chain-of-custody:** Every manifest carries `RunId`, `TenantId`, `Cloud.EnvName`, `PimJustification`, and per-artifact SHA-256. Any downstream copy must preserve the manifest; the **manifest**, not the artifact, is the authoritative evidence unit.
- **Never edit an emitted bundle.** Corrections run as a new `RunId` with a `supersedes` field in the manifest; the prior bundle stays in place. WORM enforces this at the storage layer but the discipline must be an operator habit.
- **SIEM forwarding** (§12) is additive, not a substitute for the WORM copy. The Sentinel record is the correlation layer; the WORM bundle is the regulatory record.

See [Control 2.13 — Documentation and Record-Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) for the firm-level retention policy and [Control 1.7 — Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for SIEM-side retention enforcement.

---

## §15 — Cross-References

**Control 2.12 sister playbooks:**

- [Portal Walkthrough](./portal-walkthrough.md) — UI configuration of Copilot Studio handoff, Power Automate approvals, and the supervision register.
- [Verification & Testing](./verification-testing.md) — Pester suites by namespace (WSP, HITL, QUEUE, REVIEWER, PRINCIPAL, SAMPLING, R3120, R2210, SPONSOR, AGF, SIEM), manual test scripts, and evidence-collection checklists.
- [Troubleshooting](./troubleshooting.md) — Common issues for each §3–§12 helper and their remediations.

**Related controls (framework):**

- [1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) — The registry that bounds §4 scope and links agent IDs to zone classification used in §4.3 SLA thresholds and §8 sampling rates.
- [1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — SIEM-side enforcement for §12 forwarding.
- [2.6 — Model Risk Management (OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7))](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) — Supervision is a component of MRM; §9 feeds MRM evidence.
- [2.13 — Documentation and Record-Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) — Retention policy for every artifact in §15.
- [2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — Agent 365 admin approvals reference this control as the supervisory anchor; admin approval is **not** principal supervision.
- [2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) — Sponsorship consumed by §11 for criterion #8 support; sponsorship is **not** principal supervision.
- [3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — The registry that bounds §4 scope.
- [3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — SLA breaches (§4.3) and Agent Framework integrity mismatches (§6.3) open incidents under 3.4.
- [3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — Orphaned agents re-enter §4 scope until reassignment.

**Shared references:**

- [PowerShell Authoring Baseline for FSI Implementations](../../_shared/powershell-baseline.md) — Module pinning, mutation safety, SHA-256 manifest format.
- [Role Catalog](../../../reference/role-catalog.md) — Canonical role names used throughout this playbook.
- [Regulatory Mappings](../../../reference/regulatory-mappings.md) — Regulation-to-control mapping.

**Canonical role names (short forms) used in this playbook:**

- Compliance Officer
- Designated Principal / Qualified Supervisor
- AI Governance Lead
- AI Administrator
- Agent Owner

**Non-substitution reminder.** Every helper in this playbook produces evidence that **supports compliance with** FINRA Rule 3110 (and related rules). None of the helpers — and none of the evidence bundles they produce — substitute for the Designated Principal's supervisory review, the firm's Written Supervisory Procedures, or the registered-principal qualifications required by FINRA Rule 3110. The control is the principal's judgment; this playbook produces the record.

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*


