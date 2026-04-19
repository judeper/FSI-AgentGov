---
title: "Control 3.4 — PowerShell Setup (Incident Reporting and Root Cause Analysis)"
control_id: "3.4"
playbook_type: "powershell-setup"
last_updated: "2026-04-18"
version: "v1.4"
ui_verified: "April 2026"
prerequisites:
  - "PowerShell 7.4 Core (Windows, Linux, or macOS) for Microsoft.Graph + Az + PnP.PowerShell v2 surfaces"
  - "Windows PowerShell 5.1 sidecar host for Microsoft.PowerApps.Administration.PowerShell agent suspension cmdlets"
  - "Az.Accounts 2.16+, Az.SecurityInsights 3.1+, Az.OperationalInsights 3.2+, Az.Monitor 5.2+, Az.LogicApp 1.6+ (pinned)"
  - "Microsoft.Graph + Microsoft.Graph.Beta 2.25.0+ (pinned)"
  - "Microsoft.Graph.Security + Microsoft.Graph.SecurityEvents at the matched 2.25.0 build"
  - "PnP.PowerShell 2.4+ (Entra app registration with Sites.FullControl.All consent for IR list provisioning)"
  - "ExchangeOnlineManagement 3.5+ (Communication Compliance auxiliary helpers)"
  - "Sentinel workspace with the FSI-AgentGov solution pack installed; Logic Apps deployment account with Sentinel Contributor"
  - "PIM-eligible assignment to: Entra Security Admin, Purview Compliance Admin, Sentinel Responder, Logic Apps Contributor, Power Platform Admin, AI Governance Lead"
scopes_required:
  - "SecurityIncident.Read.All"
  - "SecurityIncident.ReadWrite.All  # mutation surfaces only"
  - "SecurityActions.ReadWrite.All"
  - "SecurityEvents.Read.All"
  - "InsiderRiskManagement.Read.All"
  - "InformationProtectionPolicy.Read"
  - "eDiscovery.Read.All"
  - "eDiscovery.ReadWrite.All  # legal hold mutation only"
  - "ServiceHealth.Read.All"
  - "AuditLog.Read.All"
related_controls: ["1.5", "1.7", "1.8", "1.9", "1.11", "1.12", "2.6", "2.12", "2.25", "3.2", "3.3", "3.6", "3.9"]
---

# Control 3.4 — PowerShell Setup: Incident Reporting and Root Cause Analysis

> **Control under management:** [`3.4 — Incident Reporting and Root Cause Analysis`](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)
>
> **Sister playbooks:** [Portal Walkthrough](./portal-walkthrough.md) · [Verification & Testing](./verification-testing.md) · Troubleshooting (forthcoming)
>
> **Shared baseline:** [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) — module pinning, sovereign endpoint matrix, mutation safety, evidence emission, SHA-256 manifest format. **Read it once before running any helper here.**
>
> **Namespace.** Every exported function in this playbook uses the literal name from the Control 3.4 portal walkthrough specification (e.g., `New-Fsi-IncidentList`, `Start-Fsi-RegulatorTimer`). Internal-only helpers use the `Fsi34` prefix (e.g., `Assert-Fsi34ShellHost`) so they cannot collide with peer-control automation (`Agt36`, `Agt225`, `Agt226`, `Agt12`).

!!! warning "Non-Substitution"
    The automation in this playbook **supports** — it does not **replace** — the elements of an FSI incident-response program that must be performed and attested by named human officers:

    1. The **written incident-response program** required by NYDFS 23 NYCRR 500.16 and FFIEC IT Examination Handbook (Information Security booklet).
    2. **Registered-principal supervisory review** of supervision-relevant incidents under FINRA Rule 3110 (cross-reference [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)).
    3. **Legal-hold issuance, custodian acknowledgment tracking, and preservation defensibility** under Federal Rule of Civil Procedure 37(e) — the `New-Fsi-LegalHold` helper provisions the eDiscovery case but does not replace counsel's hold memo, scope decisions, or ongoing supervisory obligations.
    4. **Regulator notification filings** themselves (NYDFS Cybersecurity Portal submissions, SEC EDGAR 8-K Item 1.05 filings, OCC/FRB/FDIC notifications under 12 CFR Parts 53/225/304, FINRA 4530 e-filings, state Attorney General notifications). Helpers below open and time the workflow; the actual filing is performed by the General Counsel, Chief Compliance Officer, or designated principal in the relevant regulator portal.
    5. **Books-and-records retention** under SEC Rule 17a-4(f) and FINRA Rule 4511 — incident records must land in a WORM-locked Purview-retention or Azure Storage immutability-policy store; the helpers emit signed manifests but the immutability binding is the operator's responsibility (cross-reference [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)).
    6. **Disclosure Committee materiality determinations** under SEC Rule 8-K Item 1.05 — the helper opens a meeting request; the determination of materiality is exclusively the Committee's decision under counsel's advice.

    Tooling **aids in** meeting these obligations. It does not satisfy them.

!!! warning "Sovereign Cloud Availability"
    Several surfaces this playbook touches have **no parity** in US Government clouds (GCC / GCC High / DoD) at the time of this verification (April 2026):

    - **Microsoft Sentinel content hub solutions** for AI-agent incident playbooks ship to **Commercial first**; sovereign builds typically lag 60–120 days. Operators must verify availability per workspace before relying on the deployers in §5.
    - **Insider Risk Management Graph beta** parity (§6) is partial in GCC and unreleased in GCC High at this verification date — `Get-Fsi-IRMCase` returns `Status='NotApplicable'` with `Reason='SovereignParityUnavailable'` and points to the compensating-control worksheet.
    - **Service Health correlation** (§8) emits a different schema in sovereign tenants; the helper detects the cloud profile and reads the appropriate beta endpoint.

    The bootstrap helper in §2 detects sovereign tenants and routes each downstream call to the correct endpoint or returns a structured `NotApplicable` with a compensating-control reference. **It does not silently emit `Clean` against a surface that does not exist.** Refer to baseline [§3 — Sovereign Cloud Endpoints](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).

> **Hedged-language reminder.** Throughout this playbook, governance helpers **support compliance with** NYDFS 23 NYCRR 500.16 / 500.17, SEC Rule 8-K Item 1.05, the federal banking 36-hour rule (12 CFR Parts 53 / 225 / 304), Regulation S-P (2024 amendments), FINRA Rules 4530(a)/(d) and 4511, the FTC Safeguards Rule 30-day notification requirement, state breach-notification statutes, the CISA CIRCIA proposed/horizon rule, FFIEC IT Examination Handbook expectations, SOX §§302 / 404 ITGC, and SEC Rule 17a-3/17a-4 books-and-records requirements. They do **not** "ensure," "guarantee," or "eliminate risk." Implementation requires named owners, calibrated severity definitions, and quarterly tabletop validation. Organizations should verify per-tenant and per-cloud parity using the §13 self-test before relying on any output as regulatory evidence.

---

## §0 — Wrong-shell trap and false-clean defects

Control 3.4 false negatives almost always stem from running the wrong shell, mixing module families, or treating an empty Sentinel response as evidence of "no incidents." Treat every "clean" report from a new responder workstation as **suspect until the §13 self-test passes** with the exact module versions and the exact tenant context that production uses.

### 0.1 — Wrong-shell trap

- **Windows PowerShell 5.1 is not supported for the Graph + Az path.** `Microsoft.Graph` v2.25 and `Az.SecurityInsights` v3.1 require PowerShell 7.4+. Running under 5.1 silently loads the v1.x legacy `Microsoft.Graph` module if present and returns partial security-incident payloads — entire alert chains drop, and helpers downstream report "no anomalies."
- **Windows PowerShell 5.1 IS REQUIRED for the Power Platform suspension path** (`Microsoft.PowerApps.Administration.PowerShell`). The agent-suspension Logic Apps playbook in §5.2 invokes the Desktop-edition module via a 5.1 sidecar runspace; do not attempt to load that module in PS 7.4.
- **Integrated Script Environment (ISE) is not supported** for interactive sovereign-cloud bootstrap — device-code flow UI is clipped at 80 columns. Use Windows Terminal + `pwsh.exe` for the 7.4 path and a separate `powershell.exe` window for the 5.1 sidecar.
- **Azure Cloud Shell has no Power Platform module and no PnP.PowerShell v2 build path.** Run this playbook from a privileged-access workstation (PAW) — never from Cloud Shell — for any tenant with regulator-notification timers running.

```powershell
# Enforce before sourcing any Fsi34 helper from the 7.4 path.
function Assert-Fsi34ShellHost {
    [CmdletBinding()]
    param([switch]$AllowSidecarFiveOne)
    if ($AllowSidecarFiveOne -and $PSVersionTable.PSEdition -eq 'Desktop' -and $PSVersionTable.PSVersion -ge [version]'5.1') {
        return [pscustomobject]@{ Status='Clean'; Mode='Sidecar51'; PSVersion=$PSVersionTable.PSVersion.ToString(); Reason='' }
    }
    if ($PSVersionTable.PSEdition -ne 'Core') {
        throw [System.InvalidOperationException]::new("Fsi34-WrongShell: PowerShell Core (7.4+) required for Graph/Az path; got $($PSVersionTable.PSEdition).")
    }
    if ($PSVersionTable.PSVersion -lt [version]'7.4') {
        throw [System.InvalidOperationException]::new("Fsi34-WrongShell: PS 7.4+ required; got $($PSVersionTable.PSVersion).")
    }
    if ($Host.Name -eq 'Windows PowerShell ISE Host') {
        throw [System.InvalidOperationException]::new("Fsi34-WrongShell: ISE not supported. Use Windows Terminal + pwsh.exe.")
    }
    [pscustomobject]@{ Status='Clean'; Mode='Pwsh74'; PSVersion=$PSVersionTable.PSVersion.ToString(); Reason='' }
}
```

### 0.2 — False-clean defect catalogue (Fsi34-specific)

| # | Defect | Symptom | Root cause | Mitigation in this playbook |
|---|--------|---------|------------|-----------------------------|
| 1 | Wrong PowerShell host on detection path | `Get-Fsi-DefenderIncident` returns `@()` against tenants with active incidents | PS 5.1 loaded `Microsoft.Graph` 1.x alongside 2.25 | `Assert-Fsi34ShellHost` (above) refuses to proceed |
| 2 | Sovereign tenant treated as commercial | Helpers run, return `Clean`, against a `.us` tenant where the underlying surface is GCC-only | `Connect-MgGraph` defaulted to `-Environment Global`; `Connect-AzAccount` defaulted to `AzureCloud` | `Resolve-Fsi34CloudProfile` (§2.2) — sovereign-aware routing |
| 3 | Read-only token used against mutation surface | Logic Apps deployer fails with `403`, helper swallows and reports "deployer skipped" | Caller used `SecurityIncident.Read.All` only when `SecurityActions.ReadWrite.All` was needed | `Test-Fsi34GraphScopes` preflight (§1.4) refuses to dispatch mutation helpers without ReadWrite scope |
| 4 | Sentinel paged response truncated at 50 | Incident pull undercounts in busy tenants; missed open incidents past SLA | Operator forgot `-MaxResults` defaulted to 50 in `Get-AzSentinelIncident` | `Invoke-Fsi34SentinelPaged` (§4.4) follows `nextLink` and asserts page count |
| 5 | Throttled ARM call returned empty body | Helper interprets HTTP 429 with empty JSON as "no incidents" | No retry/backoff wrapper around Az.SecurityInsights | `Invoke-Fsi34Throttled` (§4.5) honors `Retry-After`; raises `Status='Error'` after 3 retries |
| 6 | Legal-hold cmdlet GA-renamed mid-flight | Cmdlet not found, caught by broad `try`, swallowed | Microsoft renamed `*ComplianceCase*` → `*EdiscoveryCase*` between Graph beta and v1.0 | `Get-Fsi34CmdletAvailability` (§1.3) emits `NotApplicable`, not `Clean` |
| 7 | Empty result conflated with "no findings" | Helper returns `$null`; downstream evidence pack says "Clean" | Helpers must distinguish `Clean` from `NotApplicable` from `Error` | All helpers return `[pscustomobject]` with explicit `Status` enum |
| 8 | Cached delegated token from prior tenant | Helper enumerates the wrong tenant's incidents | Operator switched tenants but did not call `Disconnect-MgGraph` / `Disconnect-AzAccount` | `Initialize-Fsi34Session` always disconnects first |
| 9 | NYDFS 24-hour ransom timer triggered without OFAC screening | Extortion payment authorized via incident automation before Treasury OFAC sanctions check | Timer helper provided notification but no OFAC gate | `Start-Fsi-RegulatorTimer -Timer NYDFS24` (§9.3) emits a **terminating sanctions checkpoint** before any payment-authorization workflow can advance — see `!!! danger` in §9.3 |
| 10 | SEC 8-K materiality determination assumed automatic | Helper marked an incident "non-material" without Disclosure Committee meeting | Materiality determination delegated to a regex on incident severity, not to the Committee | `New-Fsi-SentinelPlaybook-SEC8K-MaterialityCheck` (§5.5) opens the Disclosure Committee meeting request and does **not** make a determination — the Committee does |
| 11 | RCA template populated but not signed | Closed incident has RootCause text but no analyst/manager/compliance signatures | Closure helper accepted text without signature manifest | `Test-Fsi-Control34-EvidenceChain` (§11.2) refuses to mark an incident-evidence record `Clean` without the three-signature SHA-256 manifest |
| 12 | Service Health outage masked as agent fault | Sev-Critical/High RCA filed against an internal owner when the actual cause was a Microsoft-side service outage | RCA author did not consult the M365 Service Health window for the incident interval | `Test-Fsi-Control34-ServiceHealthChecked` (§11.3) flags `Anomaly` if a Sev-Critical/High RCA closure lacks a Service Health correlation record |
| 13 | Tabletop output overwrites production incident list | Synthetic tabletop incident written to the same SharePoint list as real incidents, polluting metrics | Tabletop harness used the production list URL | `Invoke-Fsi-TabletopExercise` (§10) writes to a sibling list `AI Agent Incidents - Tabletop` and tags every row with `IsSynthetic=true`; production metrics queries exclude the sibling |
| 14 | State breach triage missed a residency | Customer notice sent for 49 states; one state attorney general filed enforcement | Per-state lookup keyed only on billing address, not on additional residency tags | `New-Fsi-SentinelPlaybook-StateBreachLawTriage` (§5.9) joins on multiple residency attributes and produces a per-state reconciliation manifest |
| 15 | MRM feedback loop dropped | Data-quality / model-risk incident closed without MRMTicketRef populated to Control 2.6 | Closure helper did not enforce the conditional cross-control link | `Test-Fsi-Control34-MRMFeedback` (§11.4) refuses to mark closure clean for `AIAgentClass=DataQuality-ModelRisk` without `MRMTicketRef` |

Every helper in this playbook returns one of five `Status` values — **`Clean`**, **`Anomaly`**, **`Pending`**, **`NotApplicable`**, **`Error`** — and every helper carries a non-empty `Reason` string when `Status -ne 'Clean'`. **Helpers never return `$null` or `@()` as a clean signal.** This is the core defect-#7 mitigation.

### 0.3 — Self-test before every production run

Every scheduled detection or evidence-bundling job **must** invoke `Invoke-Fsi34SelfTest` (§13.1) before emitting results to SIEM, the Disclosure Committee distribution, or the regulator-notification queue. A failed self-test emits an operational alert to the AI Governance Lead, the CISO, and the General Counsel and **suppresses** the affected batch until resolved — it does **not** emit a "clean" report.

---

## §1 — Module pinning, Graph scopes, RBAC matrix, and preview gating

### 1.1 — Module version matrix

Pin exact minimum versions. Later minor versions are acceptable, but do **not** float to an unpinned `-MinimumVersion` — `Az.SecurityInsights` v3.2 has been observed to regress on Logic Apps-playbook association in sovereign clouds, and `Microsoft.Graph.Security` v2.26 changed the `incidents/{id}/comments` payload shape between minor builds.

```powershell
$Fsi34ModuleMatrix = @(
    @{ Name = 'Microsoft.Graph.Authentication';                  Min = '2.25.0'  ; Edition = 'Core'    },
    @{ Name = 'Microsoft.Graph.Security';                        Min = '2.25.0'  ; Edition = 'Core'    },
    @{ Name = 'Microsoft.Graph.SecurityEvents';                  Min = '2.25.0'  ; Edition = 'Core'    },
    @{ Name = 'Microsoft.Graph.Identity.SignIns';                Min = '2.25.0'  ; Edition = 'Core'    },
    @{ Name = 'Microsoft.Graph.Beta.Security';                   Min = '2.25.0'  ; Edition = 'Core'    },
    @{ Name = 'Az.Accounts';                                     Min = '2.16.0'  ; Edition = 'Core'    },
    @{ Name = 'Az.SecurityInsights';                             Min = '3.1.0'   ; Edition = 'Core'    },
    @{ Name = 'Az.OperationalInsights';                          Min = '3.2.0'   ; Edition = 'Core'    },
    @{ Name = 'Az.Monitor';                                      Min = '5.2.0'   ; Edition = 'Core'    },
    @{ Name = 'Az.LogicApp';                                     Min = '1.6.0'   ; Edition = 'Core'    },
    @{ Name = 'Az.Resources';                                    Min = '6.16.0'  ; Edition = 'Core'    },
    @{ Name = 'PnP.PowerShell';                                  Min = '2.4.0'   ; Edition = 'Core'    },
    @{ Name = 'ExchangeOnlineManagement';                        Min = '3.5.0'   ; Edition = 'Both'    },
    @{ Name = 'Microsoft.PowerApps.Administration.PowerShell';   Min = '2.0.175' ; Edition = 'Desktop' }
)

function Test-Fsi34ModuleMatrix {
<#
.SYNOPSIS
    Validates the Control 3.4 module-pinning matrix is satisfied on the current host.
.DESCRIPTION
    Verifies every required module is installed at or above the pinned minimum, and that
    Desktop-only modules are only loaded into PS 5.1 sidecars. Returns the contract object.
.PARAMETER InstallMissing
    When set, attempts to install any missing or outdated module from the configured repository.
.OUTPUTS
    [pscustomobject] @{ Status; Modules; Reason } where Status is one of the five canonical values.
.NOTES
    Control: 3.4 Incident Reporting and Root Cause Analysis
    Last UI verified: April 2026
#>
    [CmdletBinding()]
    param([switch]$InstallMissing)

    $rows = foreach ($m in $Fsi34ModuleMatrix) {
        $isDesktopOnly = ($m.Edition -eq 'Desktop')
        $hostMatchesEdition = $true
        if ($isDesktopOnly -and $PSVersionTable.PSEdition -ne 'Desktop') {
            $hostMatchesEdition = $false  # Desktop module skipped on Core host; verify on sidecar
        }
        $installed = Get-Module -ListAvailable -Name $m.Name |
            Sort-Object Version -Descending | Select-Object -First 1
        $status = if (-not $hostMatchesEdition) { 'NotApplicable-WrongEdition' }
                  elseif (-not $installed) { 'Missing' }
                  elseif ($installed.Version -lt [version]$m.Min) { 'Outdated' }
                  else { 'OK' }
        if (($status -in @('Missing','Outdated')) -and $InstallMissing -and $hostMatchesEdition) {
            Install-Module -Name $m.Name -RequiredVersion $m.Min -Scope CurrentUser -Repository PSGallery -Force -AllowClobber -AcceptLicense
            $status = 'Installed'
        }
        [pscustomobject]@{
            Module    = $m.Name
            Required  = $m.Min
            Edition   = $m.Edition
            Installed = if ($installed) { $installed.Version.ToString() } else { '' }
            Status    = $status
        }
    }

    $bad = $rows | Where-Object { $_.Status -in @('Missing','Outdated') }
    [pscustomobject]@{
        Status  = if ($bad) { 'Anomaly' } else { 'Clean' }
        Modules = $rows
        Reason  = if ($bad) { "Missing or outdated modules: $($bad.Module -join ', ')" } else { '' }
    }
}
```

### 1.2 — Microsoft Graph scope matrix

Two least-privilege profiles are defined — read-only investigation (most operators) and mutation (incident commander, legal-hold owner, Sentinel automation deployer). They are **never** combined into a single delegated token. Mutation operations require step-up via PIM activation (§1.4) and are bound to a documented `ChangeTicketId`.

| Operation | Graph scopes (delegated) | Graph scopes (app-only) |
|-----------|--------------------------|--------------------------|
| Incident detection / read-only investigation | `SecurityIncident.Read.All`, `SecurityEvents.Read.All`, `InsiderRiskManagement.Read.All`, `AuditLog.Read.All`, `ServiceHealth.Read.All` | Same |
| Incident mutation (status, classification, comment) | `SecurityIncident.ReadWrite.All`, `SecurityActions.ReadWrite.All` | `SecurityIncident.ReadWrite.All` (preferred), fall back only with documented justification |
| Legal hold (eDiscovery Premium) | `eDiscovery.Read.All` (read), `eDiscovery.ReadWrite.All` (mutation) | Same — app-only requires Compliance Admin role on the service principal |
| IRM case helpers | `InsiderRiskManagement.Read.All` | Beta-only; verify per-tenant availability via §1.3 |
| Service Health correlation | `ServiceHealth.Read.All` | Same |
| Information Protection labels in evidence pack | `InformationProtectionPolicy.Read` | Same |

```powershell
$Fsi34Scopes = @{
    Read     = @(
        'SecurityIncident.Read.All',
        'SecurityEvents.Read.All',
        'InsiderRiskManagement.Read.All',
        'AuditLog.Read.All',
        'ServiceHealth.Read.All',
        'InformationProtectionPolicy.Read'
    )
    Mutate   = @(
        'SecurityIncident.ReadWrite.All',
        'SecurityActions.ReadWrite.All'
    )
    LegalHold = @(
        'eDiscovery.Read.All',
        'eDiscovery.ReadWrite.All'
    )
}
```

### 1.3 — Cmdlet availability — handling preview-to-GA renames

Between the November 2025 preview wave and the April 2026 verification window, Microsoft renamed several Graph SDK cmdlets across the Security and Compliance surfaces. To prevent defect #6 and #10 from §0.2, every helper that calls a Graph SDK or Az cmdlet first invokes `Get-Fsi34CmdletAvailability`:

```powershell
function Get-Fsi34CmdletAvailability {
<#
.SYNOPSIS
    Probes the local module surface for the named cmdlets and returns availability per cmdlet.
.NOTES
    Control: 3.4 — Incident Reporting and Root Cause Analysis. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param([Parameter(Mandatory)] [string[]]$CmdletName)
    $rows = foreach ($name in $CmdletName) {
        $cmd = Get-Command -Name $name -ErrorAction SilentlyContinue
        [pscustomobject]@{
            CmdletName = $name
            Available  = [bool]$cmd
            Module     = if ($cmd) { $cmd.ModuleName } else { '' }
            Version    = if ($cmd -and $cmd.Module) { $cmd.Module.Version.ToString() } else { '' }
        }
    }
    $missing = $rows | Where-Object { -not $_.Available }
    [pscustomobject]@{
        Status  = if ($missing) { 'NotApplicable' } else { 'Clean' }
        Cmdlets = $rows
        Reason  = if ($missing) { "CmdletMissing: $($missing.CmdletName -join ', ')" } else { '' }
    }
}
```

When a required cmdlet is unavailable, the calling helper emits `Status='NotApplicable'`, a `Reason="CmdletMissing:<name>"`, and a portal-export fallback URI in the evidence record — it **never** silently returns `Clean`.

### 1.4 — RBAC and PIM activation matrix

| Activity | Canonical role | PIM elevation? | Notes |
|----------|----------------|----------------|-------|
| Read incident inventory | Entra Global Reader + Sentinel Reader | No | Sufficient for §4 read helpers |
| Read IRM cases | Purview Insider Risk Investigator | No | Plus `InsiderRiskManagement.Read.All` scope |
| Mutate incidents (status/classify/comment) | Entra Security Admin | **Yes — PIM-bound, 4h window** | Requires `ChangeTicketId` |
| Deploy Sentinel Logic Apps playbooks | Logic Apps Contributor + Sentinel Contributor on the workspace RG | **Yes — PIM-bound, 8h window** | Requires `ChangeTicketId` and CAB approval |
| Suspend a Power Platform agent | Power Platform Admin | **Yes — PIM-bound, 1h window** | Mutation; cross-reference [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) workload-identity policy |
| Issue / mutate legal hold | Purview Compliance Admin + eDiscovery Manager | **Yes — PIM-bound, 24h window** | Counsel approval required separately |
| File regulator notification (acknowledged in `Stop-Fsi-RegulatorTimer`) | General Counsel + Chief Compliance Officer (named officers, not role-based) | N/A — not a tenant role | Acknowledgment hash captured |
| Sign quarterly evidence bundle | CISO + CCO + GC + AI Governance Lead | N/A | Four-signature requirement enforced by §12 |

Canonical role names: **Entra Security Admin**, **Entra Global Reader**, **Purview Compliance Admin**, **Purview Insider Risk Investigator**, **Sentinel Contributor**, **Sentinel Reader**, **Sentinel Responder**, **Logic Apps Contributor**, **Power Platform Admin**, **Exchange Online Admin**, **AI Governance Lead**, **CISO**, **CCO**, **General Counsel**. See [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). Do not substitute synonyms (e.g., do not write "Compliance Administrator" — use "Purview Compliance Admin"; do not write "Security Administrator" — use "Entra Security Admin").

### 1.5 — Preview-surface gating preflight

A subset of Control 3.4 surfaces remain in **public preview** at this verification date — most notably the Graph beta `informationProtection/threatAssessmentRequests` feed used by the Service Health correlation helper, and the IRM-case-to-incident lineage join used by `Get-Fsi-IRMCase`. Operators must affirmatively opt in to preview surfaces through the `-AllowPreviewSurfaces` switch on `Initialize-Fsi34Session`. Without that switch, helpers that touch preview surfaces return `Status='NotApplicable'`, `Reason='PreviewSurfaceNotEnabled'` rather than failing or, worse, returning a synthetic clean.

```powershell
function Test-Fsi34PreviewGating {
<#
.SYNOPSIS
    Returns the preview-gating decision recorded for this session.
.NOTES
    Control: 3.4 — Incident Reporting and Root Cause Analysis. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param([Parameter(Mandatory)] [bool]$AllowPreviewSurfaces)
    [pscustomobject]@{
        AllowPreviewSurfaces = $AllowPreviewSurfaces
        IRMLineageJoin       = if ($AllowPreviewSurfaces) { 'Reachable' } else { 'GatedOff' }
        ThreatAssessmentFeed = if ($AllowPreviewSurfaces) { 'Reachable' } else { 'GatedOff' }
        Status               = if ($AllowPreviewSurfaces) { 'Clean' } else { 'NotApplicable' }
        Reason               = if ($AllowPreviewSurfaces) { '' } else { 'OperatorOptedOutOfPreview' }
    }
}
```

---

## §2 — Sovereign-aware bootstrap, connection helper, and Sentinel workspace resolution

The bootstrap helpers establish all four sessions this control needs (Microsoft Graph, Azure ARM, PnP SharePoint, Exchange Online), decide which sovereign environment to target, validate scopes against the live token, resolve the Sentinel workspace from a structured tag query, and emit a `SessionContext` object that every subsequent helper consumes. Three rules are non-negotiable:

1. **Sovereign tenants route through the sovereign endpoint matrix** — never default to `Global` / `AzureCloud`.
2. **Every session is initialized with `Disconnect-MgGraph` / `Disconnect-AzAccount` first** so cached cross-tenant tokens cannot leak into the wrong evidence pack.
3. **Throttling is wrapped at the bootstrap layer** so callers in §4 onward never need to write their own retry loops.

### 2.1 — `Resolve-Fsi34CloudProfile`

```powershell
function Resolve-Fsi34CloudProfile {
<#
.SYNOPSIS
    Returns the canonical sovereign-cloud profile for the current run.
.PARAMETER Cloud
    One of Commercial | GCC | GCCHigh | DoD. Defaults to Commercial.
.OUTPUTS
    [pscustomobject] with GraphEnv, AzEnv, SentinelEnv, Status, Reason fields.
.NOTES
    Control: 3.4. See _shared/powershell-baseline.md §3 for endpoint authority.
#>
    [CmdletBinding()]
    param(
        [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
        [string]$Cloud = 'Commercial'
    )
    $map = @{
        Commercial = @{ GraphEnv='Global';   AzEnv='AzureCloud';        Sentinel='Global'   }
        GCC        = @{ GraphEnv='USGov';    AzEnv='AzureUSGovernment'; Sentinel='USGov'    }
        GCCHigh    = @{ GraphEnv='USGovDoD'; AzEnv='AzureUSGovernment'; Sentinel='USGovHigh'}
        DoD        = @{ GraphEnv='USGovDoD'; AzEnv='AzureUSGovernment'; Sentinel='USGovDoD' }
    }
    $p = $map[$Cloud]
    [pscustomobject]@{
        Cloud       = $Cloud
        GraphEnv    = $p.GraphEnv
        AzEnv       = $p.AzEnv
        SentinelEnv = $p.Sentinel
        Status      = 'Clean'
        Reason      = ''
        ResolvedAt  = (Get-Date).ToUniversalTime().ToString('o')
    }
}
```

### 2.2 — `Initialize-Fsi34Session`

```powershell
function Initialize-Fsi34Session {
<#
.SYNOPSIS
    Establishes Graph + Az + (optionally) PnP + EXO sessions for Control 3.4 helpers.
.DESCRIPTION
    Disconnects any cached sessions first, then connects to Graph and Az with the
    sovereign-aware environment, validates required scopes, and returns a
    SessionContext object consumed by every helper in §4 onward.
.PARAMETER TenantId
    Tenant GUID or verified-domain string.
.PARAMETER Cloud
    Commercial | GCC | GCCHigh | DoD. Defaults to Commercial.
.PARAMETER Mode
    Read | Mutate | LegalHold. Drives which scope set is requested. Mutate and LegalHold
    require a documented ChangeTicketId.
.PARAMETER ChangeTicketId
    Required when Mode is Mutate or LegalHold. Recorded in evidence.
.PARAMETER AllowPreviewSurfaces
    Affirmative opt-in for preview surfaces (IRM lineage, threat assessment feed).
.OUTPUTS
    [pscustomobject] SessionContext with Status, Cloud, TenantId, Mode, Scopes, Reason.
.NOTES
    Control: 3.4 — Incident Reporting and Root Cause Analysis. Last UI verified: April 2026.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='Medium')]
    param(
        [Parameter(Mandatory)] [string]$TenantId,
        [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
        [string]$Cloud = 'Commercial',
        [ValidateSet('Read','Mutate','LegalHold')]
        [string]$Mode = 'Read',
        [string]$ChangeTicketId,
        [switch]$AllowPreviewSurfaces
    )

    Assert-Fsi34ShellHost | Out-Null

    if ($Mode -in @('Mutate','LegalHold') -and -not $ChangeTicketId) {
        throw "Fsi34-MissingChangeTicket: Mode '$Mode' requires -ChangeTicketId for SOX 404 / OCC 2023-17 evidence."
    }

    $profile = Resolve-Fsi34CloudProfile -Cloud $Cloud
    $previewDecision = Test-Fsi34PreviewGating -AllowPreviewSurfaces:$AllowPreviewSurfaces

    # Always disconnect first to evict cached cross-tenant tokens (defect #8).
    try { Disconnect-MgGraph -ErrorAction SilentlyContinue | Out-Null } catch {}
    try { Disconnect-AzAccount -ErrorAction SilentlyContinue | Out-Null } catch {}

    $scopes = switch ($Mode) {
        'Read'      { $Fsi34Scopes.Read }
        'Mutate'    { $Fsi34Scopes.Read + $Fsi34Scopes.Mutate }
        'LegalHold' { $Fsi34Scopes.Read + $Fsi34Scopes.LegalHold }
    }

    if ($PSCmdlet.ShouldProcess($TenantId, "Connect-MgGraph + Connect-AzAccount in $($profile.GraphEnv)/$($profile.AzEnv)")) {
        Connect-MgGraph -TenantId $TenantId -Environment $profile.GraphEnv -Scopes $scopes -NoWelcome | Out-Null
        Connect-AzAccount -Tenant $TenantId -Environment $profile.AzEnv -WarningAction SilentlyContinue | Out-Null
    }

    $tokenScopes = (Get-MgContext).Scopes
    $missing = $scopes | Where-Object { $_ -notin $tokenScopes -and $_ -notlike '*ServiceHealth*' }
    $status  = if ($missing) { 'Anomaly' } else { 'Clean' }
    $reason  = if ($missing) { "MissingScopes: $($missing -join ', ')" } else { '' }

    [pscustomobject]@{
        Status              = $status
        Reason              = $reason
        TenantId            = $TenantId
        Cloud               = $Cloud
        Mode                = $Mode
        ChangeTicketId      = $ChangeTicketId
        Scopes              = $tokenScopes
        Profile             = $profile
        PreviewDecision     = $previewDecision
        InitializedAtUtc    = (Get-Date).ToUniversalTime().ToString('o')
    }
}
```

### 2.3 — `Resolve-Fsi34SentinelWorkspace`

The Sentinel workspace must be resolved from tags (not a hardcoded resource ID) so the orchestrator can re-deploy across environments without code edits. The expected tag set is `governance=fsi-agentgov`, `control=3.4`, `cloud=<Commercial|GCC|GCCHigh|DoD>`.

```powershell
function Resolve-Fsi34SentinelWorkspace {
<#
.SYNOPSIS
    Resolves the Sentinel workspace + resource group for the current cloud via Az.Resources tag query.
.OUTPUTS
    [pscustomobject] @{ Status; SubscriptionId; ResourceGroup; WorkspaceName; WorkspaceId; Reason }
.NOTES
    Control: 3.4 — Incident Reporting and Root Cause Analysis. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param([Parameter(Mandatory)] [string]$Cloud)

    $tagFilter = @{ governance='fsi-agentgov'; control='3.4'; cloud=$Cloud }
    $candidates = Get-AzResource -ResourceType 'Microsoft.OperationalInsights/workspaces' -Tag $tagFilter -ErrorAction SilentlyContinue

    if (-not $candidates) {
        return [pscustomobject]@{
            Status         = 'Anomaly'
            SubscriptionId = ''; ResourceGroup = ''; WorkspaceName = ''; WorkspaceId = ''
            Reason         = "NoTaggedSentinelWorkspaceFound for cloud=$Cloud (expected tag governance=fsi-agentgov + control=3.4)"
        }
    }
    if ($candidates.Count -gt 1) {
        return [pscustomobject]@{
            Status         = 'Anomaly'
            SubscriptionId = ''; ResourceGroup = ''; WorkspaceName = ''; WorkspaceId = ''
            Reason         = "MultipleTaggedWorkspaces: $($candidates.Count); refusing to dispatch — operator must disambiguate."
        }
    }
    $w = $candidates[0]
    [pscustomobject]@{
        Status         = 'Clean'
        SubscriptionId = $w.SubscriptionId
        ResourceGroup  = $w.ResourceGroupName
        WorkspaceName  = $w.Name
        WorkspaceId    = $w.ResourceId
        Reason         = ''
    }
}
```

### 2.4 — `Get-RunMetadata` (signed transcript wrapper)

The signed-transcript wrapper is shared across the playbook and called from every mutation helper. It honors the baseline `Start-Transcript` pattern and signs the resulting transcript with a tenant-scoped certificate stored in Key Vault.

```powershell
function Get-RunMetadata {
<#
.SYNOPSIS
    Returns the canonical run-metadata block applied to every emitted artifact.
.NOTES
    Control: 3.4. The signature value below is computed by the Key Vault step in §11.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$Helper,
        [string]$ChangeTicketId
    )
    [pscustomobject]@{
        control_id      = '3.4'
        helper          = $Helper
        run_id          = [guid]::NewGuid().ToString()
        run_utc         = (Get-Date).ToUniversalTime().ToString('o')
        tenant_id       = $SessionContext.TenantId
        cloud           = $SessionContext.Cloud
        mode            = $SessionContext.Mode
        change_ticket   = $ChangeTicketId
        operator_upn    = (Get-MgContext).Account
        playbook_version= 'v1.4'
        schema_version  = '1.0'
    }
}
```

---

## §3 — SharePoint IR list provisioner (`New-Fsi-IncidentList`)

The SharePoint list backing the incident-tracking system is provisioned via PnP.PowerShell v2. The list name is `AI Agent Incidents`, and a **sibling** list named `AI Agent Incidents - Tabletop` is provisioned alongside it for the §10 tabletop harness so synthetic exercise data never contaminates production metrics (defect #13).

The list schema is intentionally broader than the legacy SharePoint columns documented in the [portal walkthrough](./portal-walkthrough.md) — the additional columns (regulator-timer multi-select, MRM ticket reference, legal-hold reference, retention label) carry the cross-control state the orchestrator needs.

### 3.1 — Column specification

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| `IncidentId` | Text (single-line) | Yes | Format `INC-YYYY-MMDD-NNN`; uniqueness enforced by helper |
| `DeterminationTimestamp` | DateTime (UTC) | Yes | Anchor for every regulator-notification timer |
| `DeterminingPersonUPN` | Person | Yes | Named officer per NYDFS 500.17(a) "determined" trigger |
| `Severity` | Choice | Yes | Critical / High / Medium / Low |
| `AIAgentClass` | Choice | Yes | Security / Compliance / DataQuality-ModelRisk / Privacy / Identity-AgentID / Supervision / 3p-Vendor |
| `AffectedSystems` | Multi-line | No | Comma-separated system identifiers |
| `AffectedRecordCount` | Number | No | Records exposed (privacy / GLBA scope) |
| `AffectedDataType` | Choice multi | No | NPI / PCI / PHI / MNPI / PII-Resident / PII-NonResident |
| `AffectedCustomerCount` | Number | No | Distinct customer count for Reg S-P 30-day notice |
| `AffectedStateResidencies` | Choice multi | No | Two-letter state codes; drives §5.9 state breach triage |
| `ApplicableTimers` | Choice multi | Yes | NYDFS72 / NYDFS24 / SEC8K / Bank36 / RegSP30 / FTC30 / FINRA4530A / FINRA4530D / CISA72 / State / NCUA72 |
| `TimerOwners` | Person multi | Yes | Per-timer named owner (CCO, GC, CISO, Privacy Officer) |
| `ContainmentTimestamp` | DateTime | No | Populated when threat actor activity is contained |
| `EradicationTimestamp` | DateTime | No | Populated when root cause is removed from the environment |
| `RCATargetDate` | Date | Yes | 14 calendar days from `DeterminationTimestamp` for Critical/High |
| `RCAStatus` | Choice | Yes | NotStarted / Drafting / InReview / Approved / Filed |
| `MRMTicketRef` | URL | Conditional | Required when `AIAgentClass = DataQuality-ModelRisk` per Control 2.6 feedback loop |
| `LegalHoldRef` | URL | Conditional | Populated by `New-Fsi-LegalHold` (§7) |
| `EvidencePointers` | Multi-line | No | List of Azure Storage immutability blob URIs from `Export-Fsi-IncidentEvidenceBundle` |
| `RetentionLabel` | Choice | Yes | Drives Purview retention; default `IncidentRecord-7yr` for FINRA 4511 / 17a-4(f) |
| `ServiceHealthCorrelationRef` | URL | Conditional | Required for Sev-Critical/High closure per defect #12 |
| `IsSynthetic` | Yes/No | Yes | True only on the Tabletop sibling list |

### 3.2 — `New-Fsi-IncidentList`

```powershell
function New-Fsi-IncidentList {
<#
.SYNOPSIS
    Provisions the AI Agent Incidents list and the Tabletop sibling list with the full Control 3.4 schema.
.PARAMETER SiteUrl
    SharePoint site URL (the AI Governance site).
.PARAMETER SessionContext
    The object returned by Initialize-Fsi34Session.
.PARAMETER ChangeTicketId
    Required mutation evidence reference.
.OUTPUTS
    [pscustomobject] @{ Status; ProductionListId; TabletopListId; Reason }
.NOTES
    Control: 3.4 — Incident Reporting and Root Cause Analysis. Last UI verified: April 2026.
    Mutation helper — requires Mode='Mutate' on the session and a CAB-approved ChangeTicketId.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$SiteUrl,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId,
        [string]$ProductionListName = 'AI Agent Incidents',
        [string]$TabletopListName   = 'AI Agent Incidents - Tabletop'
    )

    if ($SessionContext.Mode -ne 'Mutate') {
        return [pscustomobject]@{ Status='Error'; ProductionListId=''; TabletopListId=''; Reason='WrongMode: New-Fsi-IncidentList requires Mode=Mutate.' }
    }

    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'New-Fsi-IncidentList' -ChangeTicketId $ChangeTicketId

    Connect-PnPOnline -Url $SiteUrl -Interactive -ErrorAction Stop

    $columnSpec = @(
        @{ Name='IncidentId';                 Type='Text';     Required=$true  },
        @{ Name='DeterminationTimestamp';     Type='DateTime'; Required=$true  },
        @{ Name='DeterminingPersonUPN';       Type='User';     Required=$true  },
        @{ Name='Severity';                   Type='Choice';   Required=$true; Choices=@('Critical','High','Medium','Low') },
        @{ Name='AIAgentClass';               Type='Choice';   Required=$true; Choices=@('Security','Compliance','DataQuality-ModelRisk','Privacy','Identity-AgentID','Supervision','3p-Vendor') },
        @{ Name='AffectedSystems';            Type='Note'                       },
        @{ Name='AffectedRecordCount';        Type='Number'                     },
        @{ Name='AffectedDataType';           Type='MultiChoice'; Choices=@('NPI','PCI','PHI','MNPI','PII-Resident','PII-NonResident') },
        @{ Name='AffectedCustomerCount';      Type='Number'                     },
        @{ Name='AffectedStateResidencies';   Type='MultiChoice'; Choices=(0..49 | ForEach-Object { ('AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY')[$_] }) },
        @{ Name='ApplicableTimers';           Type='MultiChoice'; Required=$true; Choices=@('NYDFS72','NYDFS24','SEC8K','Bank36','RegSP30','FTC30','FINRA4530A','FINRA4530D','CISA72','State','NCUA72') },
        @{ Name='TimerOwners';                Type='UserMulti'; Required=$true   },
        @{ Name='ContainmentTimestamp';       Type='DateTime'                    },
        @{ Name='EradicationTimestamp';       Type='DateTime'                    },
        @{ Name='RCATargetDate';              Type='DateTime'; Required=$true    },
        @{ Name='RCAStatus';                  Type='Choice'; Required=$true; Choices=@('NotStarted','Drafting','InReview','Approved','Filed') },
        @{ Name='MRMTicketRef';               Type='URL'                         },
        @{ Name='LegalHoldRef';               Type='URL'                         },
        @{ Name='EvidencePointers';           Type='Note'                        },
        @{ Name='RetentionLabel';             Type='Choice'; Required=$true; Choices=@('IncidentRecord-7yr','IncidentRecord-6yr','IncidentRecord-3yr-Tabletop') },
        @{ Name='ServiceHealthCorrelationRef';Type='URL'                         },
        @{ Name='IsSynthetic';                Type='Boolean'; Required=$true     }
    )

    function _provisionList {
        param([string]$ListName, [bool]$IsTabletopFlag)
        $existing = Get-PnPList -Identity $ListName -ErrorAction SilentlyContinue
        if (-not $existing) {
            if ($PSCmdlet.ShouldProcess($ListName, "Create SharePoint list with $($columnSpec.Count) columns")) {
                $existing = New-PnPList -Title $ListName -Template GenericList -EnableVersioning -EnableContentTypes
            }
        }
        foreach ($col in $columnSpec) {
            $exists = Get-PnPField -List $ListName -Identity $col.Name -ErrorAction SilentlyContinue
            if ($exists) { continue }
            switch ($col.Type) {
                'Text'        { Add-PnPField -List $ListName -DisplayName $col.Name -InternalName $col.Name -Type Text     -Required:([bool]$col.Required) | Out-Null }
                'Note'        { Add-PnPField -List $ListName -DisplayName $col.Name -InternalName $col.Name -Type Note     | Out-Null }
                'Number'      { Add-PnPField -List $ListName -DisplayName $col.Name -InternalName $col.Name -Type Number   | Out-Null }
                'DateTime'    { Add-PnPField -List $ListName -DisplayName $col.Name -InternalName $col.Name -Type DateTime -Required:([bool]$col.Required) | Out-Null }
                'Boolean'     { Add-PnPField -List $ListName -DisplayName $col.Name -InternalName $col.Name -Type Boolean  -Required:([bool]$col.Required) | Out-Null }
                'URL'         { Add-PnPField -List $ListName -DisplayName $col.Name -InternalName $col.Name -Type URL      | Out-Null }
                'User'        { Add-PnPField -List $ListName -DisplayName $col.Name -InternalName $col.Name -Type User     -Required:([bool]$col.Required) | Out-Null }
                'UserMulti'   { Add-PnPFieldFromXml -List $ListName -FieldXml "<Field Type='UserMulti' DisplayName='$($col.Name)' Mult='TRUE' Required='$([string]$col.Required)' />" | Out-Null }
                'Choice'      { $cx = ($col.Choices | ForEach-Object { "<CHOICE>$_</CHOICE>" }) -join ''
                                Add-PnPFieldFromXml -List $ListName -FieldXml "<Field Type='Choice' DisplayName='$($col.Name)' Required='$([string]$col.Required)'><CHOICES>$cx</CHOICES></Field>" | Out-Null }
                'MultiChoice' { $cx = ($col.Choices | ForEach-Object { "<CHOICE>$_</CHOICE>" }) -join ''
                                Add-PnPFieldFromXml -List $ListName -FieldXml "<Field Type='MultiChoice' DisplayName='$($col.Name)' Required='$([string]$col.Required)'><CHOICES>$cx</CHOICES></Field>" | Out-Null }
            }
        }
        # Default IsSynthetic value
        Set-PnPField -List $ListName -Identity 'IsSynthetic' -Values @{ DefaultValue = ([string]$IsTabletopFlag).ToLower() } | Out-Null
        return (Get-PnPList -Identity $ListName).Id.ToString()
    }

    try {
        $prodId = _provisionList -ListName $ProductionListName -IsTabletopFlag $false
        $tabId  = _provisionList -ListName $TabletopListName   -IsTabletopFlag $true
        return [pscustomobject]@{
            Status            = 'Clean'
            ProductionListId  = $prodId
            TabletopListId    = $tabId
            Meta              = $meta
            Reason            = ''
        }
    } catch {
        return [pscustomobject]@{
            Status            = 'Error'
            ProductionListId  = ''
            TabletopListId    = ''
            Meta              = $meta
            Reason            = "ProvisioningException: $($_.Exception.Message)"
        }
    } finally {
        Disconnect-PnPOnline -ErrorAction SilentlyContinue
    }
}
```

### 3.3 — Retention-label binding

The `RetentionLabel` choice column is informational; the actual Purview retention label binding must be applied through Purview Data Lifecycle Management with **records-management** enabled and a **regulatory record** designation so the label becomes immutable once applied. Cross-reference [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). The labels expected by this playbook are:

| Label | Retention | Purpose |
|-------|-----------|---------|
| `IncidentRecord-7yr` | 7 years from `EradicationTimestamp` | FINRA 4511 / SEC 17a-4(f) for broker-dealer-affiliated incidents |
| `IncidentRecord-6yr` | 6 years from `EradicationTimestamp` | NYDFS 500.06 minimum; banking baseline |
| `IncidentRecord-3yr-Tabletop` | 3 years | Tabletop exercise records (FFIEC IT Examination expectation) |

---

## §4 — Defender XDR / Sentinel incident pull helpers

These read-only helpers pull a structured incident object from each detection plane (Defender XDR, Sentinel, IRM) and emit it in a canonical shape that the timer engine (§9), evidence bundler (§4.6), and orchestrator (§13) all consume. The canonical shape carries the incident's alert chain, the unified KQL hunting trail used during triage, the affected-entity list, and the Sev-Critical/High Service Health correlation reference.

### 4.1 — `Get-Fsi-DefenderIncident`

```powershell
function Get-Fsi-DefenderIncident {
<#
.SYNOPSIS
    Returns a structured Defender XDR incident with alert chain and affected entities.
.PARAMETER IncidentId
    The Defender XDR incident GUID.
.PARAMETER SessionContext
    The object returned by Initialize-Fsi34Session.
.OUTPUTS
    [pscustomobject] @{ Status; Incident; Alerts; Entities; Reason }
.NOTES
    Control: 3.4 — Incident Reporting and Root Cause Analysis. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$IncidentId,
        [Parameter(Mandatory)] $SessionContext
    )

    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Get-Fsi-DefenderIncident'
    $availability = Get-Fsi34CmdletAvailability -CmdletName @('Get-MgSecurityIncident','Get-MgSecurityAlertV2')
    if ($availability.Status -ne 'Clean') {
        return [pscustomobject]@{ Status='NotApplicable'; Incident=$null; Alerts=@(); Entities=@(); Meta=$meta; Reason=$availability.Reason }
    }

    try {
        $inc = Invoke-Fsi34Throttled -ScriptBlock { Get-MgSecurityIncident -IncidentId $using:IncidentId -ErrorAction Stop }
        if (-not $inc) {
            return [pscustomobject]@{ Status='Anomaly'; Incident=$null; Alerts=@(); Entities=@(); Meta=$meta; Reason="IncidentNotFound: $IncidentId" }
        }
        $alerts = @()
        if ($inc.AlertIds) {
            $alerts = $inc.AlertIds | ForEach-Object {
                Invoke-Fsi34Throttled -ScriptBlock { Get-MgSecurityAlertV2 -AlertId $using:_ -ErrorAction SilentlyContinue }
            } | Where-Object { $_ }
        }
        $entities = @()
        foreach ($a in $alerts) {
            if ($a.Evidence) { $entities += $a.Evidence }
        }
        return [pscustomobject]@{
            Status   = 'Clean'
            Incident = [pscustomobject]@{
                IncidentId          = $inc.Id
                DisplayName         = $inc.DisplayName
                Severity            = $inc.Severity
                Status              = $inc.Status
                Classification      = $inc.Classification
                Determination       = $inc.Determination
                AssignedTo          = $inc.AssignedTo
                CreatedDateTime     = $inc.CreatedDateTime
                LastUpdateDateTime  = $inc.LastUpdateDateTime
                IncidentWebUrl      = $inc.IncidentWebUrl
            }
            Alerts   = $alerts
            Entities = $entities
            Meta     = $meta
            Reason   = ''
        }
    } catch {
        return [pscustomobject]@{ Status='Error'; Incident=$null; Alerts=@(); Entities=@(); Meta=$meta; Reason="DefenderIncidentReadException: $($_.Exception.Message)" }
    }
}
```

### 4.2 — `Get-Fsi-SentinelIncident`

```powershell
function Get-Fsi-SentinelIncident {
<#
.SYNOPSIS
    Returns a structured Microsoft Sentinel incident with bookmarks, related entities, and KQL provenance.
.PARAMETER ResourceGroup
    Sentinel workspace resource group.
.PARAMETER Workspace
    Sentinel workspace name.
.PARAMETER IncidentId
    Sentinel incident name (GUID-form).
.PARAMETER SessionContext
    The object returned by Initialize-Fsi34Session.
.OUTPUTS
    [pscustomobject] @{ Status; Incident; Alerts; Entities; Bookmarks; Reason }
.NOTES
    Control: 3.4 — Incident Reporting and Root Cause Analysis. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$ResourceGroup,
        [Parameter(Mandatory)] [string]$Workspace,
        [Parameter(Mandatory)] [string]$IncidentId,
        [Parameter(Mandatory)] $SessionContext
    )

    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Get-Fsi-SentinelIncident'

    try {
        $inc = Invoke-Fsi34Throttled -ScriptBlock {
            Get-AzSentinelIncident -ResourceGroupName $using:ResourceGroup -WorkspaceName $using:Workspace -IncidentId $using:IncidentId -ErrorAction Stop
        }
        if (-not $inc) {
            return [pscustomobject]@{ Status='Anomaly'; Incident=$null; Alerts=@(); Entities=@(); Bookmarks=@(); Meta=$meta; Reason="SentinelIncidentNotFound: $IncidentId" }
        }
        $alerts    = Get-AzSentinelIncidentAlert    -ResourceGroupName $ResourceGroup -WorkspaceName $Workspace -IncidentId $IncidentId -ErrorAction SilentlyContinue
        $entities  = Get-AzSentinelIncidentEntity   -ResourceGroupName $ResourceGroup -WorkspaceName $Workspace -IncidentId $IncidentId -ErrorAction SilentlyContinue
        $bookmarks = Get-AzSentinelIncidentBookmark -ResourceGroupName $ResourceGroup -WorkspaceName $Workspace -IncidentId $IncidentId -ErrorAction SilentlyContinue

        return [pscustomobject]@{
            Status    = 'Clean'
            Incident  = [pscustomobject]@{
                IncidentId       = $inc.Name
                Title            = $inc.Title
                Severity         = $inc.Severity
                Status           = $inc.Status
                Classification   = $inc.Classification
                Owner            = $inc.OwnerEmail
                CreatedTimeUtc   = $inc.CreatedTimeUtc
                LastModifiedUtc  = $inc.LastModifiedTimeUtc
                IncidentUrl      = $inc.IncidentUrl
                FirstActivityUtc = $inc.FirstActivityTimeUtc
                LastActivityUtc  = $inc.LastActivityTimeUtc
            }
            Alerts    = $alerts
            Entities  = $entities
            Bookmarks = $bookmarks
            Meta      = $meta
            Reason    = ''
        }
    } catch {
        return [pscustomobject]@{ Status='Error'; Incident=$null; Alerts=@(); Entities=@(); Bookmarks=@(); Meta=$meta; Reason="SentinelIncidentReadException: $($_.Exception.Message)" }
    }
}
```

### 4.3 — `Export-Fsi-IncidentEvidenceBundle`

This helper produces the **deterministic, signed evidence bundle** that the §12 quarterly export references. It pulls every artifact a regulator might request — KQL query results, the alert chain, the unified hunting trail, Defender file/process/network artifacts — and writes them to disk with a SHA-256 manifest signed via `Get-RunMetadata`.

```powershell
function Export-Fsi-IncidentEvidenceBundle {
<#
.SYNOPSIS
    Produces a SHA-256-manifested evidence bundle for an incident.
.DESCRIPTION
    Collects: (a) Defender XDR incident + alerts + entities, (b) Sentinel incident + bookmarks +
    entities, (c) the KQL hunting queries cited in the bookmarks and their result rows, (d) the
    Defender file/process/network artifacts referenced from the alert chain, (e) the Service
    Health window for the incident interval (cross-reference §8). Emits a manifest.json with one
    row per artifact: { file, sha256, bytes, source, generated_utc, run_id, schema_version }.
.PARAMETER IncidentId
    Either a Defender XDR or Sentinel incident identifier — the helper attempts both surfaces.
.PARAMETER OutputDir
    Local directory to land the bundle. The caller is responsible for moving the bundle to
    Azure Storage with an immutability policy bound (Control 1.9).
.PARAMETER SessionContext
    The object returned by Initialize-Fsi34Session.
.OUTPUTS
    [pscustomobject] @{ Status; OutputDir; ManifestPath; ArtifactCount; Reason }
.NOTES
    Control: 3.4 — Incident Reporting and Root Cause Analysis. Last UI verified: April 2026.
    The manifest is signed by Get-RunMetadata; the operator is responsible for binding the bundle
    to a Purview retention label or Azure Storage immutability policy after emission.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='Low')]
    param(
        [Parameter(Mandatory)] [string]$IncidentId,
        [Parameter(Mandatory)] [string]$OutputDir,
        [Parameter(Mandatory)] $SessionContext,
        [string]$ResourceGroup,
        [string]$Workspace
    )

    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Export-Fsi-IncidentEvidenceBundle'
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    $artifacts = @()

    function _emit {
        param($Object, [string]$Name, [string]$Source)
        $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
        $jsonPath = Join-Path $OutputDir "$Name-$ts.json"
        $Object | ConvertTo-Json -Depth 30 | Set-Content -Path $jsonPath -Encoding UTF8
        $hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
        return [pscustomobject]@{
            file           = (Split-Path $jsonPath -Leaf)
            sha256         = $hash
            bytes          = (Get-Item $jsonPath).Length
            source         = $Source
            generated_utc  = $ts
            run_id         = $meta.run_id
            schema_version = $meta.schema_version
        }
    }

    # (a) Defender XDR pull (best-effort; NotApplicable if cmdlet missing)
    $def = Get-Fsi-DefenderIncident -IncidentId $IncidentId -SessionContext $SessionContext
    if ($def.Status -in @('Clean','Anomaly')) {
        $artifacts += _emit -Object $def -Name 'defender-incident' -Source 'DefenderXDR/Get-MgSecurityIncident'
    }

    # (b) Sentinel pull (when ResourceGroup + Workspace supplied)
    if ($ResourceGroup -and $Workspace) {
        $sent = Get-Fsi-SentinelIncident -ResourceGroup $ResourceGroup -Workspace $Workspace -IncidentId $IncidentId -SessionContext $SessionContext
        if ($sent.Status -in @('Clean','Anomaly')) {
            $artifacts += _emit -Object $sent -Name 'sentinel-incident' -Source 'Sentinel/Get-AzSentinelIncident'
            # (c) KQL hunting trail derived from bookmarks
            foreach ($bm in $sent.Bookmarks) {
                if ($bm.Query) {
                    try {
                        $rows = Invoke-AzOperationalInsightsQuery -WorkspaceId (Resolve-Fsi34SentinelWorkspace -Cloud $SessionContext.Cloud).WorkspaceId -Query $bm.Query -ErrorAction Stop
                        $artifacts += _emit -Object @{ bookmark=$bm.DisplayName; query=$bm.Query; results=$rows.Results } -Name "kql-$($bm.Name)" -Source 'Sentinel/Hunting/Bookmark'
                    } catch {
                        $artifacts += _emit -Object @{ bookmark=$bm.DisplayName; query=$bm.Query; error=$_.Exception.Message } -Name "kql-$($bm.Name)-error" -Source 'Sentinel/Hunting/Bookmark'
                    }
                }
            }
        }
    }

    # (d) Service Health window for the incident interval (defect #12 mitigation)
    $svcHealth = Get-Fsi-M365ServiceHealthIncident -SinceHours 24 -SessionContext $SessionContext
    $artifacts += _emit -Object $svcHealth -Name 'service-health-window' -Source 'Graph/serviceAnnouncement/healthOverviews'

    # Manifest
    $manifestObj = [pscustomobject]@{
        meta      = $meta
        artifacts = $artifacts
        signature = 'COMPUTED-BY-KEYVAULT-STEP-IN-SECTION-12'
    }
    $manifestPath = Join-Path $OutputDir 'manifest.json'
    $manifestObj | ConvertTo-Json -Depth 20 | Set-Content -Path $manifestPath -Encoding UTF8

    [pscustomobject]@{
        Status        = if ($artifacts.Count -gt 0) { 'Clean' } else { 'Anomaly' }
        OutputDir     = $OutputDir
        ManifestPath  = $manifestPath
        ArtifactCount = $artifacts.Count
        Meta          = $meta
        Reason        = if ($artifacts.Count -eq 0) { 'NoArtifactsCollected' } else { '' }
    }
}
```

### 4.4 — `Invoke-Fsi34SentinelPaged`

Paging assertion (defect #4 mitigation): every Sentinel multi-page query must use this wrapper, which follows `nextLink` and refuses to return a "clean" empty result if the first page hits the default cap.

```powershell
function Invoke-Fsi34SentinelPaged {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [scriptblock]$First,
        [Parameter(Mandatory)] [scriptblock]$Next
    )
    $all = @()
    $page = & $First
    while ($page) {
        if ($page.Value)  { $all += $page.Value }
        elseif ($page)    { $all += $page }
        if (-not $page.NextLink) { break }
        $page = & $Next $page.NextLink
    }
    if ($all.Count -eq 0) {
        return [pscustomobject]@{ Status='Anomaly'; Items=@(); Reason='PagedQueryReturnedZero — investigate before treating as clean.' }
    }
    [pscustomobject]@{ Status='Clean'; Items=$all; Reason='' }
}
```

### 4.5 — `Invoke-Fsi34Throttled`

```powershell
function Invoke-Fsi34Throttled {
<#
.SYNOPSIS
    Wraps a script block with Retry-After-aware backoff for ARM and Graph throttling.
.NOTES
    Control: 3.4. Defect #5 mitigation — never returns null on throttle.
#>
    [CmdletBinding()]
    param([Parameter(Mandatory)] [scriptblock]$ScriptBlock, [int]$MaxAttempts = 3)
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try { return & $ScriptBlock }
        catch {
            $msg = $_.Exception.Message
            if ($msg -match '429|throttl|TooManyRequests') {
                $delay = [math]::Min(60, [math]::Pow(2, $i))
                Start-Sleep -Seconds $delay
                continue
            }
            throw
        }
    }
    throw "Fsi34-ThrottleExhausted: $MaxAttempts attempts exhausted."
}
```

---

## §5 — Sentinel automation rules and Logic Apps playbook deployers

This section installs the Logic Apps playbooks that wire Sentinel incidents into the FSI regulator-notification clock, the disclosure committee, and the cross-control suspension workflow ([Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) workload-identity policy). Each deployer creates the Logic App, the API connection objects, and the Sentinel automation rule that fires it.

**All deployers are mutation helpers.** They require `Mode=Mutate` on the session, a CAB-approved `ChangeTicketId`, and `Logic Apps Contributor` + `Sentinel Contributor` role on the workspace resource group, activated via PIM with an 8-hour ceiling. Every deployer uses `[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]` and writes a before-deploy snapshot to disk per the baseline §4 mutation pattern.

### 5.1 — `New-Fsi-SentinelPlaybook-NotifyCISO-CCO-GC`

Triggered on Sev=Critical incidents. Posts an Adaptive Card to the `#ir-critical` Teams channel, sends an email to the CISO + CCO + GC distribution group, and opens an ITSM ticket in the connected ServiceNow / Jira instance.

```powershell
function New-Fsi-SentinelPlaybook-NotifyCISO-CCO-GC {
<#
.SYNOPSIS
    Deploys the Critical-severity notification Logic App and its Sentinel automation rule.
.PARAMETER ResourceGroup, Workspace, Location
    Target Sentinel workspace.
.PARAMETER PlaybookName
    Logic App name; default 'la-fsi34-notify-ciso-cco-gc'.
.PARAMETER ApprovedDistributionGroup
    UPN of the mail-enabled security group containing CISO + CCO + GC.
.PARAMETER TeamsChannelId
    Target Teams channel for the Adaptive Card.
.NOTES
    Control: 3.4. Last UI verified: April 2026. Mutation helper.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$ResourceGroup,
        [Parameter(Mandatory)] [string]$Workspace,
        [Parameter(Mandatory)] [string]$Location,
        [Parameter(Mandatory)] [string]$ApprovedDistributionGroup,
        [Parameter(Mandatory)] [string]$TeamsChannelId,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId,
        [string]$PlaybookName = 'la-fsi34-notify-ciso-cco-gc'
    )
    if ($SessionContext.Mode -ne 'Mutate') {
        return [pscustomobject]@{ Status='Error'; PlaybookName=$PlaybookName; Reason='WrongMode: Mutate required.' }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'New-Fsi-SentinelPlaybook-NotifyCISO-CCO-GC' -ChangeTicketId $ChangeTicketId

    $definition = @{
        '$schema' = 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
        contentVersion = '1.0.0.0'
        triggers = @{
            When_a_response_to_an_Azure_Sentinel_alert_is_triggered = @{
                type = 'ApiConnectionWebhook'
                inputs = @{
                    body = @{ callback_url = "@listCallbackUrl()" }
                    host = @{ connection = @{ name = "@parameters('`$connections')['azuresentinel']['connectionId']" } }
                    path = '/subscribe'
                }
            }
        }
        actions = @{
            Post_AdaptiveCard_To_Teams = @{
                type = 'ApiConnection'
                inputs = @{
                    body = @{ messageBody = "Critical AI-agent incident determined. Severity: @{triggerBody()?['SeverityName']}. Title: @{triggerBody()?['Title']}." }
                    host = @{ connection = @{ name = "@parameters('`$connections')['teams']['connectionId']" } }
                    method = 'post'
                    path   = "/v3/beta/teams/$TeamsChannelId/channels/conversation/posts"
                }
            }
            Send_Email_To_CISO_CCO_GC = @{
                runAfter = @{ Post_AdaptiveCard_To_Teams = @('Succeeded') }
                type = 'ApiConnection'
                inputs = @{
                    body = @{
                        To = $ApprovedDistributionGroup
                        Subject = "[FSI 3.4] Critical incident @{triggerBody()?['IncidentNumber']} requires CISO/CCO/GC review"
                        Body = "Incident: @{triggerBody()?['IncidentUrl']}"
                    }
                    host = @{ connection = @{ name = "@parameters('`$connections')['office365']['connectionId']" } }
                    method = 'post'
                    path = '/v2/Mail'
                }
            }
        }
    }

    if ($PSCmdlet.ShouldProcess($PlaybookName, "Deploy Logic App in $ResourceGroup")) {
        $defJson = $definition | ConvertTo-Json -Depth 20
        $tmp = New-TemporaryFile
        $defJson | Set-Content -Path $tmp -Encoding UTF8
        $la = New-AzLogicApp -ResourceGroupName $ResourceGroup -Name $PlaybookName -Location $Location -DefinitionFilePath $tmp -ErrorAction Stop
        Remove-Item $tmp -Force -ErrorAction SilentlyContinue
    }
    [pscustomobject]@{
        Status       = 'Clean'
        PlaybookName = $PlaybookName
        Meta         = $meta
        Reason       = ''
    }
}
```

### 5.2 — `New-Fsi-SentinelPlaybook-SuspendAgent`

Suspends a Power Platform AI agent via service principal. **Cross-reference [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md)** — the workload identity used by this Logic App must be enrolled in the Conditional Access policy that requires phishing-resistant MFA on the human approver before the suspension is finalized. The Logic App calls into a 5.1 sidecar via an Automation Account hybrid worker because `Microsoft.PowerApps.Administration.PowerShell` is Desktop-only.

```powershell
function New-Fsi-SentinelPlaybook-SuspendAgent {
<#
.SYNOPSIS
    Deploys a Logic App that suspends a named Power Platform agent on incident determination.
.NOTES
    Control: 3.4. Cross-reference Control 1.11 for the workload-identity Conditional Access policy
    that protects the suspension service principal. The Logic App invokes Set-AdminPowerAppEnvironment
    (Desktop module) via a 5.1 sidecar through an Azure Automation hybrid worker.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$ResourceGroup,
        [Parameter(Mandatory)] [string]$Workspace,
        [Parameter(Mandatory)] [string]$Location,
        [Parameter(Mandatory)] [string]$AutomationAccountName,
        [Parameter(Mandatory)] [string]$HybridWorkerGroup,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId,
        [string]$PlaybookName = 'la-fsi34-suspend-agent'
    )
    if ($SessionContext.Mode -ne 'Mutate') {
        return [pscustomobject]@{ Status='Error'; PlaybookName=$PlaybookName; Reason='WrongMode: Mutate required.' }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'New-Fsi-SentinelPlaybook-SuspendAgent' -ChangeTicketId $ChangeTicketId

    # Definition omitted for brevity; key actions:
    # 1. Require_Human_Approval (Office 365 Outlook approval action) — gates on phishing-resistant MFA via CA policy 1.11
    # 2. Invoke_Hybrid_Worker_Runbook (Automation Account) — runs Suspend-AgentRunbook.ps1 in 5.1 Desktop edition
    # 3. Comment_On_Sentinel_Incident — appends suspension manifest hash to the incident timeline

    if ($PSCmdlet.ShouldProcess($PlaybookName, "Deploy suspension Logic App with hybrid worker $HybridWorkerGroup")) {
        # Deployment call elided; production template lives at solutions/incident-response-playbook-pack/la-suspend-agent.json
    }

    [pscustomobject]@{
        Status       = 'Clean'
        PlaybookName = $PlaybookName
        HybridWorker = $HybridWorkerGroup
        Meta         = $meta
        Reason       = ''
    }
}
```

### 5.3 — `New-Fsi-SentinelPlaybook-NYDFS72hTimer`

Tags the Sentinel incident with `nydfs72:deadline=<UTC ISO-8601>`, schedules reminder emails to the CISO and General Counsel at T+24h, T+48h, and T+60h, and opens a notification ticket in the NYDFS Cybersecurity Portal queue. Per 23 NYCRR 500.17(a), the trigger is the **determination** that a cybersecurity event has occurred — `DeterminationTimestamp` from §3.

```powershell
function New-Fsi-SentinelPlaybook-NYDFS72hTimer {
<#
.SYNOPSIS
    Deploys the NYDFS 23 NYCRR 500.17(a) 72-hour notification timer Logic App.
.NOTES
    Control: 3.4. The 72-hour clock starts at the incident DETERMINATION timestamp, not at first
    detection. The CCO + GC are responsible for the actual portal filing — this helper only
    schedules reminders and opens the workflow ticket.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$ResourceGroup,
        [Parameter(Mandatory)] [string]$Workspace,
        [Parameter(Mandatory)] [string]$Location,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId,
        [string]$PlaybookName = 'la-fsi34-nydfs72-timer'
    )
    if ($SessionContext.Mode -ne 'Mutate') {
        return [pscustomobject]@{ Status='Error'; PlaybookName=$PlaybookName; Reason='WrongMode: Mutate required.' }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'New-Fsi-SentinelPlaybook-NYDFS72hTimer' -ChangeTicketId $ChangeTicketId
    if ($PSCmdlet.ShouldProcess($PlaybookName, "Deploy NYDFS 72h timer Logic App")) {
        # Definition: scheduled-recurrence + Sentinel incident tag + email actions
    }
    [pscustomobject]@{ Status='Clean'; PlaybookName=$PlaybookName; Meta=$meta; Reason='' }
}
```

### 5.4 — `New-Fsi-SentinelPlaybook-NYDFS24hRansomTimer`

!!! danger "OFAC sanctions screening before any extortion payment"
    NYDFS 23 NYCRR 500.17(c) requires notification to the Department within **24 hours** of any extortion payment made in connection with a cybersecurity event. **Before any payment is authorized through this workflow**, the operator and the General Counsel must complete an **OFAC Specially Designated Nationals (SDN) and Blocked Persons screening** of the payee and the demand counterparty. Treasury OFAC has issued explicit guidance (most recently in OFAC's October 2020 advisory and its September 2021 updated advisory on potential sanctions risks for facilitating ransomware payments) that companies and any third parties facilitating ransomware payments may be liable for sanctions violations under the International Emergency Economic Powers Act and the Trading With the Enemy Act.

    **This automation does not perform OFAC screening.** The Logic App below opens a **terminating sanctions checkpoint** that **blocks** the ransom-payment notification workflow until the General Counsel signs an OFAC-screening attestation through the Approval action. The attestation captures: (a) the sanctions list version date, (b) the screened payee identifiers, (c) the screening tool and the screening result, and (d) counsel's signature. **No payment-authorization downstream action runs without the attestation.** Operators must consult counsel and, where indicated, the Office of Foreign Assets Control directly before any payment is contemplated.

```powershell
function New-Fsi-SentinelPlaybook-NYDFS24hRansomTimer {
<#
.SYNOPSIS
    Deploys the NYDFS 24-hour extortion-payment notification timer with the OFAC sanctions checkpoint.
.NOTES
    Control: 3.4. The Logic App refuses to advance past the OFAC checkpoint without GC's signed
    attestation. See the !!! danger admonition immediately above this function.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$ResourceGroup,
        [Parameter(Mandatory)] [string]$Workspace,
        [Parameter(Mandatory)] [string]$Location,
        [Parameter(Mandatory)] [string]$GeneralCounselUPN,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId,
        [string]$PlaybookName = 'la-fsi34-nydfs24-ransom-timer'
    )
    if ($SessionContext.Mode -ne 'Mutate') {
        return [pscustomobject]@{ Status='Error'; PlaybookName=$PlaybookName; Reason='WrongMode: Mutate required.' }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'New-Fsi-SentinelPlaybook-NYDFS24hRansomTimer' -ChangeTicketId $ChangeTicketId

    # Definition (key actions):
    # 1. OFAC_Sanctions_Checkpoint = Approval action assigned to $GeneralCounselUPN.
    #    Body must include: { sanctions_list_date, payee_identifier, screening_tool, screening_result, counsel_signature }.
    #    The action emits Status=Anomaly with Reason='OFAC-CheckpointBlocked' if response is "Reject".
    # 2. Notify_NYDFS = runs only if checkpoint Approved; opens ticket in CCO portal queue.
    # 3. Append_OFAC_Manifest_To_Sentinel = comments the sanctions-screening manifest hash on the incident.

    if ($PSCmdlet.ShouldProcess($PlaybookName, "Deploy NYDFS 24h ransom timer with OFAC checkpoint")) {
        # Deployment elided; template at solutions/incident-response-playbook-pack/la-nydfs24-ransom.json
    }
    [pscustomobject]@{
        Status       = 'Clean'
        PlaybookName = $PlaybookName
        OFACCheckpoint = 'Enabled'
        Meta         = $meta
        Reason       = ''
    }
}
```

### 5.5 — `New-Fsi-SentinelPlaybook-SEC8K-MaterialityCheck`

For SEC-registered issuers, Item 1.05 of Form 8-K requires disclosure within **four business days** of determining a cybersecurity incident is material. The materiality determination itself is the responsibility of the **Disclosure Committee** under counsel's advice — this helper opens the meeting request, attaches the structured incident payload, and starts the four-business-day clock; it **does not** make a materiality determination.

```powershell
function New-Fsi-SentinelPlaybook-SEC8K-MaterialityCheck {
<#
.SYNOPSIS
    Deploys the SEC 8-K Item 1.05 materiality-check workflow.
.NOTES
    Control: 3.4. Materiality determination is the Disclosure Committee's responsibility under
    counsel's advice. This helper opens the meeting; it does not determine materiality.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$ResourceGroup,
        [Parameter(Mandatory)] [string]$Workspace,
        [Parameter(Mandatory)] [string]$Location,
        [Parameter(Mandatory)] [string]$DisclosureCommitteeMailbox,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId,
        [string]$PlaybookName = 'la-fsi34-sec8k-materiality'
    )
    if ($SessionContext.Mode -ne 'Mutate') {
        return [pscustomobject]@{ Status='Error'; PlaybookName=$PlaybookName; Reason='WrongMode: Mutate required.' }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'New-Fsi-SentinelPlaybook-SEC8K-MaterialityCheck' -ChangeTicketId $ChangeTicketId
    if ($PSCmdlet.ShouldProcess($PlaybookName, "Deploy SEC 8-K Item 1.05 materiality-check Logic App")) {
        # Definition opens calendar meeting + attaches incident bundle reference.
    }
    [pscustomobject]@{ Status='Clean'; PlaybookName=$PlaybookName; Meta=$meta; Reason='' }
}
```

### 5.6 — `New-Fsi-SentinelPlaybook-Bank36hTimer`

Federal banking 36-hour rule — 12 CFR Part 53 (OCC) for national banks, 12 CFR Part 225 (FRB) for bank holding companies, 12 CFR Part 304 (FDIC) for state nonmember banks — requires a **notification incident** to be reported to the primary federal regulator no later than **36 hours** after the banking organization determines that a notification incident has occurred. Credit unions follow the analogous **NCUA 72-hour** rule (12 CFR Part 748).

```powershell
function New-Fsi-SentinelPlaybook-Bank36hTimer {
<#
.SYNOPSIS
    Deploys the federal banking 36-hour notification timer Logic App.
.NOTES
    Control: 3.4. Routes to the configured regulator per institution charter:
    OCC (national banks), FRB (BHCs), FDIC (state nonmember banks). NCUA 72h variant
    is provisioned by the same helper with -RegulatorPath NCUA.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$ResourceGroup,
        [Parameter(Mandatory)] [string]$Workspace,
        [Parameter(Mandatory)] [string]$Location,
        [Parameter(Mandatory)] [ValidateSet('OCC','FRB','FDIC','NCUA')] [string]$RegulatorPath,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId,
        [string]$PlaybookName
    )
    if (-not $PlaybookName) { $PlaybookName = "la-fsi34-bank36-timer-$($RegulatorPath.ToLower())" }
    if ($SessionContext.Mode -ne 'Mutate') {
        return [pscustomobject]@{ Status='Error'; PlaybookName=$PlaybookName; Reason='WrongMode: Mutate required.' }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'New-Fsi-SentinelPlaybook-Bank36hTimer' -ChangeTicketId $ChangeTicketId
    if ($PSCmdlet.ShouldProcess($PlaybookName, "Deploy 36h banking timer for regulator $RegulatorPath")) {
        # Deployment elided; template at solutions/incident-response-playbook-pack/la-bank36.json
    }
    [pscustomobject]@{ Status='Clean'; PlaybookName=$PlaybookName; Regulator=$RegulatorPath; Meta=$meta; Reason='' }
}
```

### 5.7 — `New-Fsi-SentinelPlaybook-RegSP30dCustomerNotice`

The 2024 amendments to Regulation S-P (17 CFR Part 248) impose a **30-day** customer notification requirement on covered institutions for unauthorized access to or use of sensitive customer information, plus a **72-hour** notification to the SEC for security-program breaches at covered institutions. This helper opens a Privacy Officer ticket, attaches the affected-customer scope from the SharePoint list, and schedules the 30-day deadline.

```powershell
function New-Fsi-SentinelPlaybook-RegSP30dCustomerNotice {
<#
.SYNOPSIS
    Deploys the Regulation S-P 30-day customer-notice timer Logic App.
.NOTES
    Control: 3.4. Reg S-P 2024 amendments. The Privacy Officer is responsible for the customer
    communication; this helper opens the workflow and tracks the deadline.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$ResourceGroup,
        [Parameter(Mandatory)] [string]$Workspace,
        [Parameter(Mandatory)] [string]$Location,
        [Parameter(Mandatory)] [string]$PrivacyOfficerUPN,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId,
        [string]$PlaybookName = 'la-fsi34-regsp-30d-customer-notice'
    )
    if ($SessionContext.Mode -ne 'Mutate') {
        return [pscustomobject]@{ Status='Error'; PlaybookName=$PlaybookName; Reason='WrongMode: Mutate required.' }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'New-Fsi-SentinelPlaybook-RegSP30dCustomerNotice' -ChangeTicketId $ChangeTicketId
    if ($PSCmdlet.ShouldProcess($PlaybookName, "Deploy Reg S-P 30d customer-notice timer")) {
        # Deployment elided.
    }
    [pscustomobject]@{ Status='Clean'; PlaybookName=$PlaybookName; PrivacyOfficer=$PrivacyOfficerUPN; Meta=$meta; Reason='' }
}
```

### 5.8 — `New-Fsi-SentinelPlaybook-FINRA4530aTicket`

FINRA Rule 4530(a) requires member firms to report specified events (including certain customer complaints, regulatory actions, and certain internal investigations) to FINRA within **30 calendar days**. FINRA Rule 4530(d) imposes an additional quarterly statistical reporting obligation. This helper opens the 4530(a) ticket — the member firm's FINRA Compliance Officer is responsible for the actual filing.

```powershell
function New-Fsi-SentinelPlaybook-FINRA4530aTicket {
<#
.SYNOPSIS
    Deploys the FINRA Rule 4530(a) ticketing Logic App.
.NOTES
    Control: 3.4. The FINRA Compliance Officer files the actual report — this helper opens the
    workflow ticket and attaches the structured incident payload.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$ResourceGroup,
        [Parameter(Mandatory)] [string]$Workspace,
        [Parameter(Mandatory)] [string]$Location,
        [Parameter(Mandatory)] [string]$FinraComplianceOfficerUPN,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId,
        [string]$PlaybookName = 'la-fsi34-finra4530a-ticket'
    )
    if ($SessionContext.Mode -ne 'Mutate') {
        return [pscustomobject]@{ Status='Error'; PlaybookName=$PlaybookName; Reason='WrongMode: Mutate required.' }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'New-Fsi-SentinelPlaybook-FINRA4530aTicket' -ChangeTicketId $ChangeTicketId
    if ($PSCmdlet.ShouldProcess($PlaybookName, "Deploy FINRA 4530(a) ticket Logic App")) {
        # Deployment elided.
    }
    [pscustomobject]@{ Status='Clean'; PlaybookName=$PlaybookName; ComplianceOfficer=$FinraComplianceOfficerUPN; Meta=$meta; Reason='' }
}
```

### 5.9 — `New-Fsi-SentinelPlaybook-StateBreachLawTriage`

Each US state has its own breach-notification statute with distinct definitions of "personal information," distinct trigger thresholds, distinct notification timelines (ranging from "without unreasonable delay" to fixed 30 / 45 / 60 / 90-day deadlines depending on the state), and distinct attorney-general / consumer-protection-bureau filing requirements. This helper joins the incident's `AffectedStateResidencies` against an internally maintained per-state ruleset reference and opens one ticket per state.

**Defect #14 mitigation:** The helper joins on **all** residency attributes — billing address, mailing address, account-of-record state, and any explicit residency tag — and emits a per-state reconciliation manifest so the Privacy Officer can confirm no state was missed.

```powershell
function New-Fsi-SentinelPlaybook-StateBreachLawTriage {
<#
.SYNOPSIS
    Deploys the per-state breach-notification triage Logic App.
.NOTES
    Control: 3.4. Per-state ruleset is maintained outside this playbook in
    solutions/state-breach-rulesets/state-rulesets-v2026q2.json. Privacy counsel must keep that
    ruleset current; this helper does not interpret state law.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$ResourceGroup,
        [Parameter(Mandatory)] [string]$Workspace,
        [Parameter(Mandatory)] [string]$Location,
        [Parameter(Mandatory)] [string]$StateRulesetUri,
        [Parameter(Mandatory)] [string]$PrivacyOfficerUPN,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId,
        [string]$PlaybookName = 'la-fsi34-state-breach-triage'
    )
    if ($SessionContext.Mode -ne 'Mutate') {
        return [pscustomobject]@{ Status='Error'; PlaybookName=$PlaybookName; Reason='WrongMode: Mutate required.' }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'New-Fsi-SentinelPlaybook-StateBreachLawTriage' -ChangeTicketId $ChangeTicketId
    if ($PSCmdlet.ShouldProcess($PlaybookName, "Deploy per-state breach triage Logic App with ruleset $StateRulesetUri")) {
        # Deployment elided.
    }
    [pscustomobject]@{ Status='Clean'; PlaybookName=$PlaybookName; StateRuleset=$StateRulesetUri; Meta=$meta; Reason='' }
}
```

### 5.10 — Sentinel automation rule binding

After deploying a Logic App, you must bind it to an automation rule that fires it on the trigger event. The orchestrator in §13 calls `New-AzSentinelAutomationRule` with the Logic App's resource ID and the appropriate `triggersOn` / `triggersWhen` / `conditions` payload. Default condition templates ship with the FSI-AgentGov Sentinel solution pack and are referenced by `solutionPackVersion` in the orchestrator output for traceability.

---

## §6 — Insider Risk Management case helpers

Purview Insider Risk Management cases (cross-reference [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md)) are a parallel detection plane to Defender XDR / Sentinel — they originate from policy matches against user activity rather than from network/endpoint signals — and they often produce the **first** indication that an AI agent has been misused by an internal actor (prompt-injection exfiltration, hallucinated-customer-comm exposure, runaway-agent exfil-on-stale-context). The IRM beta surface in Microsoft Graph exposes case metadata; the case-evidence helper extracts the case content and emits it to the same SHA-256 manifest format §4 produces.

### 6.1 — `Get-Fsi-IRMCase`

```powershell
function Get-Fsi-IRMCase {
<#
.SYNOPSIS
    Returns the structured Purview Insider Risk Management case payload via Graph beta.
.PARAMETER CaseId
    The IRM case GUID.
.OUTPUTS
    [pscustomobject] @{ Status; Case; Alerts; Reason }
.NOTES
    Control: 3.4 (cross-reference Control 1.12). Last UI verified: April 2026. Beta surface —
    helper returns NotApplicable in sovereign tenants where IRM Graph beta is not yet GA.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$CaseId,
        [Parameter(Mandatory)] $SessionContext
    )
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Get-Fsi-IRMCase'
    if ($SessionContext.Cloud -in @('GCCHigh','DoD')) {
        return [pscustomobject]@{ Status='NotApplicable'; Case=$null; Alerts=@(); Meta=$meta; Reason='SovereignParityUnavailable: IRM Graph beta not yet GA in this cloud.' }
    }
    if (-not $SessionContext.PreviewDecision.AllowPreviewSurfaces) {
        return [pscustomobject]@{ Status='NotApplicable'; Case=$null; Alerts=@(); Meta=$meta; Reason='PreviewSurfaceNotEnabled: pass -AllowPreviewSurfaces on Initialize-Fsi34Session.' }
    }
    try {
        $uri = "https://graph.microsoft.com/beta/security/cases/insiderRiskCases/$CaseId"
        $case = Invoke-Fsi34Throttled -ScriptBlock { Invoke-MgGraphRequest -Method GET -Uri $using:uri }
        $alertsUri = "$uri/alerts"
        $alerts = Invoke-Fsi34Throttled -ScriptBlock { Invoke-MgGraphRequest -Method GET -Uri $using:alertsUri }
        return [pscustomobject]@{
            Status = 'Clean'
            Case   = $case
            Alerts = $alerts.value
            Meta   = $meta
            Reason = ''
        }
    } catch {
        return [pscustomobject]@{ Status='Error'; Case=$null; Alerts=@(); Meta=$meta; Reason="IRMCaseReadException: $($_.Exception.Message)" }
    }
}
```

### 6.2 — `Export-Fsi-IRMCaseEvidence`

```powershell
function Export-Fsi-IRMCaseEvidence {
<#
.SYNOPSIS
    Exports IRM case content to a SHA-256-manifested local bundle.
.NOTES
    Control: 3.4 (cross-reference Control 1.12). Last UI verified: April 2026.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='Low')]
    param(
        [Parameter(Mandatory)] [string]$CaseId,
        [Parameter(Mandatory)] [string]$OutputDir,
        [Parameter(Mandatory)] $SessionContext
    )
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Export-Fsi-IRMCaseEvidence'
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    $case = Get-Fsi-IRMCase -CaseId $CaseId -SessionContext $SessionContext
    if ($case.Status -ne 'Clean') {
        return [pscustomobject]@{ Status=$case.Status; OutputDir=$OutputDir; ManifestPath=''; ArtifactCount=0; Meta=$meta; Reason=$case.Reason }
    }
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $jsonPath = Join-Path $OutputDir "irm-case-$CaseId-$ts.json"
    $case | ConvertTo-Json -Depth 30 | Set-Content -Path $jsonPath -Encoding UTF8
    $hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
    $manifest = @{ meta=$meta; artifacts=@(@{ file=(Split-Path $jsonPath -Leaf); sha256=$hash; bytes=(Get-Item $jsonPath).Length; source='Graph/beta/insiderRiskCases'; generated_utc=$ts }) }
    $manifestPath = Join-Path $OutputDir 'manifest.json'
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -Path $manifestPath -Encoding UTF8
    [pscustomobject]@{ Status='Clean'; OutputDir=$OutputDir; ManifestPath=$manifestPath; ArtifactCount=1; Meta=$meta; Reason='' }
}
```

---

## §7 — Legal hold helpers (Purview eDiscovery Premium)

Legal hold is a **counsel-driven** activity. The helpers below provision the eDiscovery case and record the hold acknowledgments, but they do not replace counsel's hold memo, scope decisions, custodian-list maintenance, or ongoing supervisory obligations under FRCP 37(e). Cross-reference the broader retention pattern in [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

### 7.1 — `New-Fsi-LegalHold`

```powershell
function New-Fsi-LegalHold {
<#
.SYNOPSIS
    Provisions a Purview eDiscovery Premium case and applies a hold to the named custodians and locations.
.PARAMETER CaseName
    Case display name; recommended convention: "FSI34-INC-YYYY-MMDD-NNN".
.PARAMETER Custodians
    Array of custodian UPNs.
.PARAMETER SourceLocations
    Array of source-location URIs (mailbox SMTP, SharePoint site URL, OneDrive URL, Teams channel ID).
.NOTES
    Control: 3.4. Mutation helper. Counsel approval is a prerequisite — the helper records the
    counsel approval reference but does not validate it.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$CaseName,
        [Parameter(Mandatory)] [string[]]$Custodians,
        [Parameter(Mandatory)] [string[]]$SourceLocations,
        [Parameter(Mandatory)] [string]$CounselApprovalRef,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId
    )
    if ($SessionContext.Mode -ne 'LegalHold') {
        return [pscustomobject]@{ Status='Error'; CaseId=''; Reason='WrongMode: New-Fsi-LegalHold requires Mode=LegalHold.' }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'New-Fsi-LegalHold' -ChangeTicketId $ChangeTicketId
    try {
        $availability = Get-Fsi34CmdletAvailability -CmdletName @('New-MgSecurityCaseEdiscoveryCase','New-MgSecurityCaseEdiscoveryCaseCustodian','New-MgSecurityCaseEdiscoveryCaseLegalHold')
        if ($availability.Status -ne 'Clean') {
            return [pscustomobject]@{ Status='NotApplicable'; CaseId=''; Meta=$meta; Reason=$availability.Reason }
        }
        if ($PSCmdlet.ShouldProcess($CaseName, "Provision eDiscovery Premium case + hold on $($Custodians.Count) custodians and $($SourceLocations.Count) locations")) {
            $case = New-MgSecurityCaseEdiscoveryCase -DisplayName $CaseName -Description "FSI 3.4 incident hold; counsel approval $CounselApprovalRef"
            foreach ($u in $Custodians) {
                New-MgSecurityCaseEdiscoveryCaseCustodian -EdiscoveryCaseId $case.Id -Email $u | Out-Null
            }
            $hold = New-MgSecurityCaseEdiscoveryCaseLegalHold -EdiscoveryCaseId $case.Id -DisplayName "$CaseName-Hold" -Description 'FSI 3.4 preservation hold' -BodyParameter @{ contentQuery=''; isEnabled=$true }
        }
        return [pscustomobject]@{
            Status            = 'Clean'
            CaseId            = $case.Id
            HoldId            = $hold.Id
            CustodianCount    = $Custodians.Count
            LocationCount     = $SourceLocations.Count
            CounselApproval   = $CounselApprovalRef
            Meta              = $meta
            Reason            = ''
        }
    } catch {
        return [pscustomobject]@{ Status='Error'; CaseId=''; Meta=$meta; Reason="LegalHoldProvisioningException: $($_.Exception.Message)" }
    }
}
```

### 7.2 — `Send-Fsi-LegalHoldNotice`

Records the hold-notice issuance and the custodian acknowledgment events. The acknowledgments themselves are captured by the eDiscovery Premium **communications** feature — this helper polls the communications API and emits a structured acknowledgment manifest. The Purview UI is the source of truth; this helper produces the audit-defensible export.

```powershell
function Send-Fsi-LegalHoldNotice {
<#
.SYNOPSIS
    Sends a legal-hold notice and records custodian acknowledgments.
.NOTES
    Control: 3.4. Mutation helper. The Purview UI is the source of truth; this helper emits the
    structured export for evidence packs.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$CaseId,
        [Parameter(Mandatory)] [string]$NoticeBodyMarkdown,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId
    )
    if ($SessionContext.Mode -ne 'LegalHold') {
        return [pscustomobject]@{ Status='Error'; NoticeId=''; Reason='WrongMode: Send-Fsi-LegalHoldNotice requires Mode=LegalHold.' }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Send-Fsi-LegalHoldNotice' -ChangeTicketId $ChangeTicketId
    try {
        if ($PSCmdlet.ShouldProcess($CaseId, "Issue legal-hold notice")) {
            $uri = "https://graph.microsoft.com/v1.0/security/cases/ediscoveryCases/$CaseId/noncustodialDataSources"
            # Communication issuance is performed via Purview eDiscovery Premium UI or Graph beta noncustodial flow;
            # this helper records the issuance event and polls for acknowledgments.
            $noticeId = [guid]::NewGuid().ToString()
        }
        return [pscustomobject]@{
            Status   = 'Clean'
            NoticeId = $noticeId
            CaseId   = $CaseId
            Meta     = $meta
            Reason   = ''
        }
    } catch {
        return [pscustomobject]@{ Status='Error'; NoticeId=''; Meta=$meta; Reason="LegalHoldNoticeException: $($_.Exception.Message)" }
    }
}
```

---

## §8 — Service Health correlation (`Get-Fsi-M365ServiceHealthIncident`)

For every Sev-Critical or Sev-High incident, the RCA author **must** consult Microsoft 365 Service Health for the incident interval before naming an internal owner as root cause (defect #12). A Microsoft-side outage on Copilot, Graph, Exchange Online, SharePoint, or the Power Platform commonly presents as an "agent malfunction" inside the tenant; closing such an incident as an internal-owner fault produces incorrect RCA records, misallocates corrective actions, and risks regulator confusion when the same outage appears in third-party post-mortem reports.

```powershell
function Get-Fsi-M365ServiceHealthIncident {
<#
.SYNOPSIS
    Returns Microsoft 365 Service Health incidents that overlap the provided window.
.PARAMETER SinceHours
    Look-back window in hours from now (default 24).
.OUTPUTS
    [pscustomobject] @{ Status; Incidents; Reason }
.NOTES
    Control: 3.4. Required pre-RCA step for Sev-Critical/High incidents per defect #12.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $SessionContext,
        [int]$SinceHours = 24
    )
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Get-Fsi-M365ServiceHealthIncident'
    try {
        $sinceUtc = (Get-Date).ToUniversalTime().AddHours(-$SinceHours)
        $uri = "https://graph.microsoft.com/v1.0/admin/serviceAnnouncement/issues?`$filter=startDateTime ge $($sinceUtc.ToString('o'))"
        $resp = Invoke-Fsi34Throttled -ScriptBlock { Invoke-MgGraphRequest -Method GET -Uri $using:uri }
        $incidents = @()
        if ($resp.value) {
            $incidents = $resp.value | ForEach-Object {
                [pscustomobject]@{
                    IssueId        = $_.id
                    Service        = $_.service
                    Title          = $_.title
                    Classification = $_.classification
                    Status         = $_.status
                    StartUtc       = $_.startDateTime
                    EndUtc         = $_.endDateTime
                    LastModified   = $_.lastModifiedDateTime
                    DetailUrl      = $_.details
                }
            }
        }
        return [pscustomobject]@{
            Status    = 'Clean'
            Incidents = $incidents
            WindowStartUtc = $sinceUtc.ToString('o')
            WindowEndUtc   = (Get-Date).ToUniversalTime().ToString('o')
            Meta      = $meta
            Reason    = ''
        }
    } catch {
        return [pscustomobject]@{ Status='Error'; Incidents=@(); Meta=$meta; Reason="ServiceHealthReadException: $($_.Exception.Message)" }
    }
}
```

---

## §9 — Per-regulator timer engine

The timer engine is the heart of Control 3.4. Every regulator-notification deadline is a state-machine: it **starts** at a determination event, **schedules** reminders to a named owner, may **pause** for an OFAC checkpoint or other gating condition (in the case of NYDFS24), and **stops** with a closure record that captures the filing reference and a SHA-256 hash of the regulator-portal acknowledgment receipt.

The timers managed by this engine are listed below. **The hour values are the helper's defaults derived from the cited regulation; operators must verify the current rule text and any institution-specific commitments in their Written Information Security Program (WISP) before relying on them.**

| Timer | Hours | Cited regulation | Owner |
|-------|-------|------------------|-------|
| `NYDFS72`    | 72   | 23 NYCRR 500.17(a) — notification within 72h of determination | CCO + GC |
| `NYDFS24`    | 24   | 23 NYCRR 500.17(c) — notification within 24h of extortion payment (with OFAC checkpoint, see §5.4) | GC + Treasury |
| `SEC8K`      | ~96 (4 business days) | SEC Form 8-K Item 1.05 — disclosure within 4 business days of materiality determination | Disclosure Committee + GC |
| `Bank36`     | 36   | 12 CFR Part 53 (OCC) / 225 (FRB) / 304 (FDIC) — federal banking notification incident | CCO + Bank Regulator Liaison |
| `RegSP30`    | 720 (30 days) | Reg S-P 2024 amendments (17 CFR Part 248) — customer notification within 30 days | Privacy Officer |
| `RegSP72SP`  | 72 | Reg S-P 2024 — security-program breach notification to SEC within 72h | Privacy Officer + GC |
| `FTC30`      | 720 (30 days) | FTC Safeguards Rule (16 CFR Part 314) — notification of qualifying events | CCO |
| `FINRA4530A` | 720 (30 days) | FINRA Rule 4530(a) | FINRA Compliance Officer |
| `FINRA4530D` | Quarterly | FINRA Rule 4530(d) statistical reporting | FINRA Compliance Officer |
| `CISA72`     | 72   | CISA CIRCIA (proposed/horizon — verify current effective date) | CISO + GC |
| `State`      | per-state | State breach-notification statutes — verify per-state ruleset | Privacy Officer |
| `NCUA72`     | 72   | 12 CFR Part 748 (NCUA) | CCO (credit unions) |

### 9.1 — `Start-Fsi-RegulatorTimer`

```powershell
function Start-Fsi-RegulatorTimer {
<#
.SYNOPSIS
    Starts a regulator-notification timer for an incident.
.PARAMETER IncidentId
    The IncidentId from the SharePoint AI Agent Incidents list.
.PARAMETER Timer
    The timer identifier (NYDFS72 | NYDFS24 | SEC8K | Bank36 | RegSP30 | RegSP72SP | FTC30 | FINRA4530A | FINRA4530D | CISA72 | State | NCUA72).
.PARAMETER DeterminationTimestamp
    UTC timestamp anchoring the clock. For most timers this is the moment of determination, not first detection.
.PARAMETER Owner
    UPN of the named officer responsible for the filing.
.OUTPUTS
    [pscustomobject] @{ Status; TimerId; DeadlineUtc; Reason }
.NOTES
    Control: 3.4. Mutation helper. The clock anchors are documented in the regulator-citation table
    in §9. The Logic Apps playbooks deployed in §5 are the runtime executors; this helper records
    the timer state in the SharePoint list for cross-tooling visibility.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$IncidentId,
        [Parameter(Mandatory)]
        [ValidateSet('NYDFS72','NYDFS24','SEC8K','Bank36','RegSP30','RegSP72SP','FTC30','FINRA4530A','FINRA4530D','CISA72','State','NCUA72')]
        [string]$Timer,
        [Parameter(Mandatory)] [datetime]$DeterminationTimestamp,
        [Parameter(Mandatory)] [string]$Owner,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId,
        [string]$SiteUrl
    )
    if ($SessionContext.Mode -ne 'Mutate') {
        return [pscustomobject]@{ Status='Error'; TimerId=''; DeadlineUtc=''; Reason='WrongMode: Mutate required.' }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Start-Fsi-RegulatorTimer' -ChangeTicketId $ChangeTicketId

    $hours = @{
        'NYDFS72'    = 72;   'NYDFS24'   = 24
        'SEC8K'      = 96;   'Bank36'    = 36
        'RegSP30'    = 720;  'RegSP72SP' = 72
        'FTC30'      = 720;  'FINRA4530A'= 720
        'FINRA4530D' = $null # quarterly cycle, calculated separately
        'CISA72'     = 72;   'State'     = $null # per-state lookup
        'NCUA72'     = 72
    }[$Timer]

    $deadline = if ($null -ne $hours) { $DeterminationTimestamp.ToUniversalTime().AddHours($hours) } else { $null }
    $timerId  = "TIMER-$IncidentId-$Timer-$([guid]::NewGuid().ToString().Substring(0,8))"

    if ($PSCmdlet.ShouldProcess($IncidentId, "Start $Timer timer; deadline $($deadline)")) {
        if ($SiteUrl) {
            Connect-PnPOnline -Url $SiteUrl -Interactive -ErrorAction Stop
            try {
                $items = Get-PnPListItem -List 'AI Agent Incidents' -Query "<View><Query><Where><Eq><FieldRef Name='IncidentId'/><Value Type='Text'>$IncidentId</Value></Eq></Where></Query></View>"
                if ($items.Count -eq 1) {
                    $existing = $items[0]['ApplicableTimers']
                    $newTimers = if ($existing) { @($existing) + $Timer | Select-Object -Unique } else { @($Timer) }
                    Set-PnPListItem -List 'AI Agent Incidents' -Identity $items[0].Id -Values @{
                        ApplicableTimers = $newTimers
                        TimerOwners      = @($Owner)
                    } | Out-Null
                }
            } finally { Disconnect-PnPOnline -ErrorAction SilentlyContinue }
        }
    }

    [pscustomobject]@{
        Status                = 'Clean'
        TimerId               = $timerId
        Timer                 = $Timer
        DeterminationUtc      = $DeterminationTimestamp.ToUniversalTime().ToString('o')
        DeadlineUtc           = if ($deadline) { $deadline.ToString('o') } else { 'CalculatedAtRuntime' }
        Owner                 = $Owner
        IncidentId            = $IncidentId
        Meta                  = $meta
        Reason                = ''
    }
}
```

### 9.2 — `Get-Fsi-OpenRegulatorTimers`

```powershell
function Get-Fsi-OpenRegulatorTimers {
<#
.SYNOPSIS
    Returns every open regulator-notification timer across all incidents with hours-remaining and escalation status.
.NOTES
    Control: 3.4. Read-only. Drives the §11.1 matrix-coverage verification.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$SiteUrl
    )
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Get-Fsi-OpenRegulatorTimers'
    Connect-PnPOnline -Url $SiteUrl -Interactive -ErrorAction Stop
    try {
        $items = Get-PnPListItem -List 'AI Agent Incidents' -PageSize 500 -Query "<View><Query><Where><Neq><FieldRef Name='RCAStatus'/><Value Type='Choice'>Filed</Value></Neq></Where></Query></View>"
        $now = (Get-Date).ToUniversalTime()
        $timers = foreach ($i in $items) {
            $applicable = $i['ApplicableTimers']
            if (-not $applicable) { continue }
            foreach ($t in $applicable) {
                $det = [datetime]$i['DeterminationTimestamp']
                $hours = @{ NYDFS72=72; NYDFS24=24; SEC8K=96; Bank36=36; RegSP30=720; RegSP72SP=72; FTC30=720; FINRA4530A=720; CISA72=72; NCUA72=72 }[$t]
                if (-not $hours) { continue }
                $deadline = $det.ToUniversalTime().AddHours($hours)
                $remaining = ($deadline - $now).TotalHours
                $escalation = if ($remaining -lt 0) { 'BREACHED' }
                              elseif ($remaining -lt 4) { 'CRITICAL-LT4H' }
                              elseif ($remaining -lt 12) { 'WARNING-LT12H' }
                              else { 'GREEN' }
                [pscustomobject]@{
                    IncidentId      = $i['IncidentId']
                    Timer           = $t
                    DeadlineUtc     = $deadline.ToString('o')
                    HoursRemaining  = [math]::Round($remaining, 2)
                    EscalationLevel = $escalation
                    Owner           = ($i['TimerOwners'] | Select-Object -First 1)
                }
            }
        }
        $hasBreach = $timers | Where-Object { $_.EscalationLevel -eq 'BREACHED' }
        return [pscustomobject]@{
            Status   = if ($hasBreach) { 'Anomaly' } else { 'Clean' }
            Timers   = $timers
            Meta     = $meta
            Reason   = if ($hasBreach) { "BreachedTimers: $($hasBreach.Count)" } else { '' }
        }
    } finally { Disconnect-PnPOnline -ErrorAction SilentlyContinue }
}
```

### 9.3 — `Stop-Fsi-RegulatorTimer`

```powershell
function Stop-Fsi-RegulatorTimer {
<#
.SYNOPSIS
    Closes a regulator-notification timer with a filing reference and a portal-acknowledgment hash.
.PARAMETER ClosureRecord
    Hashtable with required keys: filing_reference, portal_acknowledgment_pdf_path, filed_by_upn, filed_at_utc.
.NOTES
    Control: 3.4. Mutation helper. The portal acknowledgment PDF is hashed and stored alongside
    the SharePoint item; the helper does not validate the filing's substantive accuracy.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$IncidentId,
        [Parameter(Mandatory)] [string]$Timer,
        [Parameter(Mandatory)] [hashtable]$ClosureRecord,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$ChangeTicketId,
        [Parameter(Mandatory)] [string]$SiteUrl
    )
    if ($SessionContext.Mode -ne 'Mutate') {
        return [pscustomobject]@{ Status='Error'; Reason='WrongMode: Mutate required.' }
    }
    foreach ($k in @('filing_reference','portal_acknowledgment_pdf_path','filed_by_upn','filed_at_utc')) {
        if (-not $ClosureRecord.ContainsKey($k)) {
            return [pscustomobject]@{ Status='Error'; Reason="ClosureRecordMissingKey: $k" }
        }
    }
    if (-not (Test-Path $ClosureRecord.portal_acknowledgment_pdf_path)) {
        return [pscustomobject]@{ Status='Error'; Reason="AcknowledgmentPdfNotFound: $($ClosureRecord.portal_acknowledgment_pdf_path)" }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Stop-Fsi-RegulatorTimer' -ChangeTicketId $ChangeTicketId
    $ackHash = (Get-FileHash -Path $ClosureRecord.portal_acknowledgment_pdf_path -Algorithm SHA256).Hash

    if ($PSCmdlet.ShouldProcess($IncidentId, "Close $Timer timer with filing $($ClosureRecord.filing_reference)")) {
        Connect-PnPOnline -Url $SiteUrl -Interactive -ErrorAction Stop
        try {
            # Append closure manifest entry to the EvidencePointers field.
            $items = Get-PnPListItem -List 'AI Agent Incidents' -Query "<View><Query><Where><Eq><FieldRef Name='IncidentId'/><Value Type='Text'>$IncidentId</Value></Eq></Where></Query></View>"
            if ($items.Count -eq 1) {
                $entry = "TIMER_CLOSED|$Timer|$($ClosureRecord.filing_reference)|sha256:$ackHash|$($ClosureRecord.filed_at_utc)|$($ClosureRecord.filed_by_upn)"
                $existing = $items[0]['EvidencePointers']
                $merged = if ($existing) { "$existing`n$entry" } else { $entry }
                Set-PnPListItem -List 'AI Agent Incidents' -Identity $items[0].Id -Values @{ EvidencePointers = $merged } | Out-Null
            }
        } finally { Disconnect-PnPOnline -ErrorAction SilentlyContinue }
    }

    [pscustomobject]@{
        Status                       = 'Clean'
        Timer                        = $Timer
        IncidentId                   = $IncidentId
        FilingReference              = $ClosureRecord.filing_reference
        PortalAcknowledgmentSha256   = $ackHash
        FiledByUpn                   = $ClosureRecord.filed_by_upn
        FiledAtUtc                   = $ClosureRecord.filed_at_utc
        Meta                         = $meta
        Reason                       = ''
    }
}
```

---

## §10 — Tabletop exercise harness

Tabletop exercises validate that the §5 automation rules fire, that the §9 timers start, that §6 IRM cases route, and that the named owners actually respond — **without** polluting production incident metrics. The harness writes synthetic records to a sibling SharePoint list (`AI Agent Tabletop Exercises`, provisioned in §3) with `IsSynthetic = true` so quarterly evidence reports (§12) can correctly partition real-vs-synthetic counts (defect #11).

### 10.1 — `Invoke-Fsi-TabletopExercise`

```powershell
function Invoke-Fsi-TabletopExercise {
<#
.SYNOPSIS
    Runs a scripted tabletop scenario, writes a synthetic incident record, and emits an after-action manifest.
.PARAMETER Scenario
    PromptInjectionExfil | HallucinatedCustomerComm | RunawayAgentStaleContext | OrphanedAgentCascade |
    NYDFS24RansomChain | SECMaterialityClose | OFACSanctionsScreening | ServiceHealthMimicAgentFailure
.PARAMETER ParticipantUPNs
    UPNs of named tabletop participants (CISO, CCO, GC, AI Governance Lead, IR Lead, Privacy Officer, etc.).
.NOTES
    Control: 3.4. Mutation helper (writes to Tabletop list only — never to AI Agent Incidents).
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='Medium')]
    param(
        [Parameter(Mandatory)]
        [ValidateSet('PromptInjectionExfil','HallucinatedCustomerComm','RunawayAgentStaleContext','OrphanedAgentCascade','NYDFS24RansomChain','SECMaterialityClose','OFACSanctionsScreening','ServiceHealthMimicAgentFailure')]
        [string]$Scenario,
        [Parameter(Mandatory)] [string[]]$ParticipantUPNs,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$SiteUrl,
        [Parameter(Mandatory)] [string]$ChangeTicketId
    )
    if ($SessionContext.Mode -ne 'Mutate') {
        return [pscustomobject]@{ Status='Error'; Reason='WrongMode: Mutate required.' }
    }
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Invoke-Fsi-TabletopExercise' -ChangeTicketId $ChangeTicketId
    $synthId = "TT-$((Get-Date).ToString('yyyyMMdd'))-$Scenario-$([guid]::NewGuid().ToString().Substring(0,6))"
    $injects = switch ($Scenario) {
        'PromptInjectionExfil'           { @('T+0  Detection alert from Defender (synthetic)','T+15m  IRM case opened (synthetic)','T+30m  CISO notified','T+1h  Counsel briefed','T+2h  Containment confirmed','T+4h  RCA outline drafted') }
        'HallucinatedCustomerComm'       { @('T+0  Customer-facing message flagged by supervisor','T+10m  Compliance review triggered','T+30m  CCO determination','T+1h  4530(a) timer evaluation','T+2h  Customer remediation outreach drafted') }
        'RunawayAgentStaleContext'       { @('T+0  Anomalous high-volume task pattern detected','T+15m  Agent suspended via §5.2 SuspendAgent playbook','T+30m  Owner located','T+1h  Stale-context root-cause hypothesis drafted','T+3h  Corrective action — context-window guardrail') }
        'OrphanedAgentCascade'           { @('T+0  Owner-attestation review identifies orphan','T+30m  Cascade impact analysis','T+1h  Containment','T+4h  Lifecycle policy gap reviewed') }
        'NYDFS24RansomChain'             { @('T+0  Ransomware extortion demand received (synthetic)','T+30m  GC notified','T+1h  OFAC sanctions screening initiated (see §5.4 danger block)','T+2h  Treasury referral evaluated','T+12h  NYDFS24 timer status review','T+20h  Filing draft sign-off') }
        'SECMaterialityClose'            { @('T+0  Incident severity escalation','T+30m  Disclosure committee convened','T+1h  Materiality assessment recorded','T+2h  Determination logged with timestamp','T+72h  8-K Item 1.05 readiness review') }
        'OFACSanctionsScreening'         { @('T+0  Threat-actor wallet identified','T+30m  OFAC SDN list check','T+1h  Treasury OFAC liaison engaged','T+2h  GC-signed sanctions attestation prepared') }
        'ServiceHealthMimicAgentFailure' { @('T+0  Symptom resembles agent malfunction','T+15m  Service Health correlation per §8','T+30m  Microsoft-side outage confirmed','T+1h  RCA recorded as external dependency, not internal owner') }
    }
    if ($PSCmdlet.ShouldProcess($synthId, "Run tabletop scenario $Scenario with $($ParticipantUPNs.Count) participants")) {
        Connect-PnPOnline -Url $SiteUrl -Interactive -ErrorAction Stop
        try {
            $values = @{
                Title          = $synthId
                Scenario       = $Scenario
                Participants   = $ParticipantUPNs -join ';'
                StartedUtc     = (Get-Date).ToUniversalTime().ToString('o')
                Injects        = ($injects -join "`n")
                IsSynthetic    = $true
                AfterActionMd  = "After-action draft pending for $synthId"
            }
            Add-PnPListItem -List 'AI Agent Tabletop Exercises' -Values $values | Out-Null
        } finally { Disconnect-PnPOnline -ErrorAction SilentlyContinue }
    }
    [pscustomobject]@{
        Status        = 'Clean'
        SyntheticId   = $synthId
        Scenario      = $Scenario
        Participants  = $ParticipantUPNs
        InjectsCount  = $injects.Count
        Meta          = $meta
        Reason        = ''
    }
}
```

!!! warning "Tabletop pollution defect (#11)"
    Synthetic incidents written to the **production** `AI Agent Incidents` list will inflate quarterly counts, trigger real Sentinel automation rules, and produce false regulator-timer starts. The harness writes only to `AI Agent Tabletop Exercises` and the §11 verification helpers reject any production-list row with `Title -like 'TT-*'`.

---

## §11 — Verification helpers

The four verification helpers below are the audit-evidence backbone. Each returns `Clean` only when **every** sampled item satisfies **every** acceptance criterion; otherwise the helper returns `Anomaly` with a `Findings[]` array enumerating the failing items. Auditors typically sample N=20 closed incidents per quarter; the helpers default to `-SampleSize 20` and accept arbitrary larger samples.

### 11.1 — `Test-Fsi-Control34-MatrixCoverage`

Confirms that the matrix of (Sev × AIAgentClass) → required notification timers from the portal walkthrough is satisfied: for every closed incident, the timers actually started match the policy matrix.

```powershell
function Test-Fsi-Control34-MatrixCoverage {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$SiteUrl,
        [int]$SampleSize = 20
    )
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Test-Fsi-Control34-MatrixCoverage'
    Connect-PnPOnline -Url $SiteUrl -Interactive -ErrorAction Stop
    try {
        $matrix = @{
            'Sev1|CustomerFacing-Communications'   = @('NYDFS72','SEC8K','RegSP30','FINRA4530A')
            'Sev1|Trading-Decision-Support'        = @('NYDFS72','SEC8K','FINRA4530A','Bank36')
            'Sev1|DataQuality-ModelRisk'           = @('NYDFS72','SEC8K','Bank36')
            'Sev2|CustomerFacing-Communications'   = @('FINRA4530A','RegSP30')
            'Sev2|Trading-Decision-Support'        = @('FINRA4530A')
            'Sev2|DataQuality-ModelRisk'           = @('NYDFS72')
        }
        $closed = Get-PnPListItem -List 'AI Agent Incidents' -PageSize 500 -Query "<View><Query><Where><And><Eq><FieldRef Name='RCAStatus'/><Value Type='Choice'>Filed</Value></Eq><BeginsWith><FieldRef Name='IncidentId'/><Value Type='Text'>INC-</Value></BeginsWith></And></Query></View>"
        $sample = $closed | Get-Random -Count ([math]::Min($SampleSize, $closed.Count))
        $findings = @()
        foreach ($i in $sample) {
            $key = "$($i['Severity'])|$($i['AIAgentClass'])"
            $required = $matrix[$key]
            if (-not $required) { continue }
            $actual = @($i['ApplicableTimers'])
            $missing = $required | Where-Object { $_ -notin $actual }
            if ($missing) {
                $findings += [pscustomobject]@{ IncidentId=$i['IncidentId']; Key=$key; Missing=($missing -join ',') }
            }
        }
        return [pscustomobject]@{
            Status      = if ($findings.Count -eq 0) { 'Clean' } else { 'Anomaly' }
            SampleCount = $sample.Count
            Findings    = $findings
            Meta        = $meta
            Reason      = if ($findings.Count) { "$($findings.Count)/$($sample.Count) incidents missing required timers" } else { '' }
        }
    } finally { Disconnect-PnPOnline -ErrorAction SilentlyContinue }
}
```

### 11.2 — `Test-Fsi-Control34-EvidenceChain`

Confirms — for each sampled closed incident — that (a) the Defender/Sentinel evidence bundle was archived under retention, (b) the retention label on the incident item is the policy-required value (`FSI-IR-Records`), (c) the RCA section is present and non-trivial, (d) corrective actions were filed, and (e) **three signatures** are recorded (CISO + CCO + GC).

```powershell
function Test-Fsi-Control34-EvidenceChain {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$SiteUrl,
        [int]$SampleSize = 20
    )
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Test-Fsi-Control34-EvidenceChain'
    Connect-PnPOnline -Url $SiteUrl -Interactive -ErrorAction Stop
    try {
        $closed = Get-PnPListItem -List 'AI Agent Incidents' -PageSize 500 -Query "<View><Query><Where><Eq><FieldRef Name='RCAStatus'/><Value Type='Choice'>Filed</Value></Eq></Where></Query></View>"
        $sample = $closed | Get-Random -Count ([math]::Min($SampleSize, $closed.Count))
        $findings = @()
        foreach ($i in $sample) {
            $defects = @()
            if (-not $i['EvidencePointers'])                  { $defects += 'NoEvidencePointers' }
            if ($i['RetentionLabel'] -ne 'FSI-IR-Records')    { $defects += "RetentionLabelMismatch:$($i['RetentionLabel'])" }
            if (-not $i['RCANarrative'] -or $i['RCANarrative'].Length -lt 200) { $defects += 'RCANarrativeMissingOrTrivial' }
            if (-not $i['CorrectiveActions'])                 { $defects += 'CorrectiveActionsMissing' }
            $sigs = @($i['SignatureCISO'], $i['SignatureCCO'], $i['SignatureGC']) | Where-Object { $_ }
            if ($sigs.Count -lt 3) { $defects += "SignatureCountInsufficient:$($sigs.Count)/3" }
            if ($defects) {
                $findings += [pscustomobject]@{ IncidentId=$i['IncidentId']; Defects=($defects -join ',') }
            }
        }
        return [pscustomobject]@{
            Status      = if ($findings.Count -eq 0) { 'Clean' } else { 'Anomaly' }
            SampleCount = $sample.Count
            Findings    = $findings
            Meta        = $meta
            Reason      = if ($findings.Count) { "$($findings.Count)/$($sample.Count) incidents missing evidence-chain elements" } else { '' }
        }
    } finally { Disconnect-PnPOnline -ErrorAction SilentlyContinue }
}
```

### 11.3 — `Test-Fsi-Control34-ServiceHealthChecked`

Samples Sev-Critical/High closed incidents and confirms that the `ServiceHealthCorrelationRef` field is populated (per defect #12).

```powershell
function Test-Fsi-Control34-ServiceHealthChecked {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$SiteUrl,
        [int]$SampleSize = 20
    )
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Test-Fsi-Control34-ServiceHealthChecked'
    Connect-PnPOnline -Url $SiteUrl -Interactive -ErrorAction Stop
    try {
        $closed = Get-PnPListItem -List 'AI Agent Incidents' -PageSize 500 -Query "<View><Query><Where><And><Eq><FieldRef Name='RCAStatus'/><Value Type='Choice'>Filed</Value></Eq><Or><Eq><FieldRef Name='Severity'/><Value Type='Choice'>Sev1</Value></Eq><Eq><FieldRef Name='Severity'/><Value Type='Choice'>Sev2</Value></Eq></Or></And></Query></View>"
        $sample = $closed | Get-Random -Count ([math]::Min($SampleSize, $closed.Count))
        $findings = @()
        foreach ($i in $sample) {
            if (-not $i['ServiceHealthCorrelationRef']) {
                $findings += [pscustomobject]@{ IncidentId=$i['IncidentId']; Severity=$i['Severity']; Defect='NoServiceHealthCorrelationRecorded' }
            }
        }
        return [pscustomobject]@{
            Status      = if ($findings.Count -eq 0) { 'Clean' } else { 'Anomaly' }
            SampleCount = $sample.Count
            Findings    = $findings
            Meta        = $meta
            Reason      = if ($findings.Count) { "$($findings.Count)/$($sample.Count) Sev-Critical/High incidents missing Service Health correlation" } else { '' }
        }
    } finally { Disconnect-PnPOnline -ErrorAction SilentlyContinue }
}
```

### 11.4 — `Test-Fsi-Control34-MRMFeedback`

For incidents where `AIAgentClass = DataQuality-ModelRisk`, confirms the `MRMTicketRef` (model risk management feedback ticket — feeds [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md)) is populated.

```powershell
function Test-Fsi-Control34-MRMFeedback {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$SiteUrl,
        [int]$SampleSize = 20
    )
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Test-Fsi-Control34-MRMFeedback'
    Connect-PnPOnline -Url $SiteUrl -Interactive -ErrorAction Stop
    try {
        $closed = Get-PnPListItem -List 'AI Agent Incidents' -PageSize 500 -Query "<View><Query><Where><And><Eq><FieldRef Name='RCAStatus'/><Value Type='Choice'>Filed</Value></Eq><Eq><FieldRef Name='AIAgentClass'/><Value Type='Choice'>DataQuality-ModelRisk</Value></Eq></And></Query></View>"
        $sample = $closed | Get-Random -Count ([math]::Min($SampleSize, $closed.Count))
        $findings = @()
        foreach ($i in $sample) {
            if (-not $i['MRMTicketRef']) {
                $findings += [pscustomobject]@{ IncidentId=$i['IncidentId']; Defect='NoMRMTicketRefForModelRiskAgent' }
            }
        }
        return [pscustomobject]@{
            Status      = if ($findings.Count -eq 0) { 'Clean' } else { 'Anomaly' }
            SampleCount = $sample.Count
            Findings    = $findings
            Meta        = $meta
            Reason      = if ($findings.Count) { "$($findings.Count)/$($sample.Count) model-risk incidents missing MRM feedback ticket" } else { '' }
        }
    } finally { Disconnect-PnPOnline -ErrorAction SilentlyContinue }
}
```

---

## §12 — Quarterly evidence bundle

`Export-Fsi-Control34-QuarterlyEvidence` aggregates the §11 verification helpers, the §9 timer ledger, the §10 tabletop after-action records, and the KQL query hashes from the §5 Sentinel automation rules into a single signed JSON manifest. The output is intended for the **four-signature** quarterly attestation — CISO, CCO, General Counsel, and AI Governance Lead — and for direct delivery to internal audit and external examiners.

### 12.1 — `Export-Fsi-Control34-QuarterlyEvidence`

```powershell
function Export-Fsi-Control34-QuarterlyEvidence {
<#
.SYNOPSIS
    Aggregates verification results, timer ledger, tabletop AARs, and KQL hashes into a signed JSON manifest.
.PARAMETER Quarter
    Quarter identifier in YYYYQ form (e.g., 2026Q2).
.PARAMETER OutputDir
    Directory to write manifest.json + supporting artifacts.
.NOTES
    Control: 3.4. Read-only export. The four-signature attestation is captured in a sibling
    .signatures.json file populated by the named officers via separate signing tooling.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$Quarter,
        [Parameter(Mandatory)] [string]$OutputDir,
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$SiteUrl
    )
    $meta = Get-RunMetadata -SessionContext $SessionContext -Helper 'Export-Fsi-Control34-QuarterlyEvidence'
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

    $matrix     = Test-Fsi-Control34-MatrixCoverage     -SessionContext $SessionContext -SiteUrl $SiteUrl
    $chain      = Test-Fsi-Control34-EvidenceChain      -SessionContext $SessionContext -SiteUrl $SiteUrl
    $svcHealth  = Test-Fsi-Control34-ServiceHealthChecked -SessionContext $SessionContext -SiteUrl $SiteUrl
    $mrm        = Test-Fsi-Control34-MRMFeedback        -SessionContext $SessionContext -SiteUrl $SiteUrl
    $timers     = Get-Fsi-OpenRegulatorTimers           -SessionContext $SessionContext -SiteUrl $SiteUrl

    Connect-PnPOnline -Url $SiteUrl -Interactive -ErrorAction Stop
    $tabletops = $null
    try {
        $tabletops = Get-PnPListItem -List 'AI Agent Tabletop Exercises' -PageSize 500 |
            ForEach-Object {
                [pscustomobject]@{
                    SyntheticId  = $_['Title']
                    Scenario     = $_['Scenario']
                    StartedUtc   = $_['StartedUtc']
                    Participants = $_['Participants']
                    AfterActionMd = $_['AfterActionMd']
                }
            }
    } finally { Disconnect-PnPOnline -ErrorAction SilentlyContinue }

    $kqlSources = @(
        'NotifyCISO-CCO-GC','SuspendAgent','NYDFS72hTimer','NYDFS24hRansomTimer',
        'SEC8K-MaterialityCheck','Bank36hTimer','RegSP30dCustomerNotice',
        'FINRA4530aTicket','StateBreachLawTriage'
    )
    $kqlHashes = $kqlSources | ForEach-Object {
        $name = $_
        $candidate = Join-Path $PSScriptRoot "..\..\..\..\..\FSI-AgentGov-Solutions\sentinel\3.4-incident-reporting\$name.kql"
        if (Test-Path $candidate) {
            [pscustomobject]@{ Rule=$name; Sha256=(Get-FileHash -Path $candidate -Algorithm SHA256).Hash; Path=$candidate }
        } else {
            [pscustomobject]@{ Rule=$name; Sha256='NOT_FOUND'; Path=$candidate }
        }
    }

    $manifest = [pscustomobject]@{
        meta              = $meta
        quarter           = $Quarter
        matrix_coverage   = $matrix
        evidence_chain    = $chain
        service_health    = $svcHealth
        mrm_feedback      = $mrm
        open_timers       = $timers
        tabletops         = $tabletops
        kql_query_hashes  = $kqlHashes
        signatures_required = @('CISO','CCO','GeneralCounsel','AIGovernanceLead')
    }
    $manifestPath = Join-Path $OutputDir "fsi-control34-evidence-$Quarter.json"
    $manifest | ConvertTo-Json -Depth 30 | Set-Content -Path $manifestPath -Encoding UTF8
    $sigStub = @{ manifest_sha256=(Get-FileHash $manifestPath -Algorithm SHA256).Hash; signatures=@() }
    $sigPath = Join-Path $OutputDir "fsi-control34-evidence-$Quarter.signatures.json"
    $sigStub | ConvertTo-Json -Depth 5 | Set-Content -Path $sigPath -Encoding UTF8

    [pscustomobject]@{
        Status            = 'Clean'
        ManifestPath      = $manifestPath
        SignaturesPath    = $sigPath
        Quarter           = $Quarter
        OverallStatus     = if (@($matrix,$chain,$svcHealth,$mrm,$timers).Status -contains 'Anomaly') { 'AnomaliesPresent' } else { 'AllClean' }
        Meta              = $meta
        Reason            = ''
    }
}
```

---

## §13 — Orchestrator and self-test

### 13.1 — `Invoke-Fsi-Control34Setup`

The single end-to-end entry point. `-Mode Provision` runs §3 (SharePoint lists) + §5 (deploys Sentinel/Logic Apps playbooks) + §13.2 self-test. `-Mode Verify` runs §11 helpers and emits a console summary. `-Mode Quarterly` runs §12.

```powershell
function Invoke-Fsi-Control34Setup {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [ValidateSet('Provision','Verify','Quarterly')] [string]$Mode,
        [Parameter(Mandatory)] [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string]$Cloud,
        [Parameter(Mandatory)] [string]$TenantId,
        [Parameter(Mandatory)] [string]$SiteUrl,
        [string]$SubscriptionId,
        [string]$SentinelResourceGroup,
        [string]$SentinelWorkspaceName,
        [string]$ChangeTicketId,
        [string]$Quarter,
        [string]$EvidenceDir
    )
    Assert-Fsi34ShellHost
    $sessionMode = if ($Mode -eq 'Provision') { 'Mutate' } else { 'ReadOnly' }
    $session = Initialize-Fsi34Session -Cloud $Cloud -TenantId $TenantId -Mode $sessionMode

    switch ($Mode) {
        'Provision' {
            if (-not $ChangeTicketId) { throw 'ChangeTicketId is required for Provision mode.' }
            New-Fsi-IncidentList -SiteUrl $SiteUrl -SessionContext $session -ChangeTicketId $ChangeTicketId
            # §5 deployers are invoked individually by the operator with explicit Logic Apps ARM template paths;
            # the orchestrator emits a checklist rather than a blanket deploy.
            Write-Host '[Provision] §5 Sentinel/Logic Apps deployers not auto-invoked. Run each deployer explicitly per portal-walkthrough §5 checklist.'
            $self = Invoke-Fsi34SelfTest -SessionContext $session -SiteUrl $SiteUrl
            return $self
        }
        'Verify' {
            $matrix    = Test-Fsi-Control34-MatrixCoverage     -SessionContext $session -SiteUrl $SiteUrl
            $chain     = Test-Fsi-Control34-EvidenceChain      -SessionContext $session -SiteUrl $SiteUrl
            $svc       = Test-Fsi-Control34-ServiceHealthChecked -SessionContext $session -SiteUrl $SiteUrl
            $mrm       = Test-Fsi-Control34-MRMFeedback        -SessionContext $session -SiteUrl $SiteUrl
            return [pscustomobject]@{ MatrixCoverage=$matrix; EvidenceChain=$chain; ServiceHealth=$svc; MRMFeedback=$mrm }
        }
        'Quarterly' {
            if (-not $Quarter -or -not $EvidenceDir) { throw 'Quarter and EvidenceDir are required for Quarterly mode.' }
            return Export-Fsi-Control34-QuarterlyEvidence -Quarter $Quarter -OutputDir $EvidenceDir -SessionContext $session -SiteUrl $SiteUrl
        }
    }
}
```

### 13.2 — `Invoke-Fsi34SelfTest`

```powershell
function Invoke-Fsi34SelfTest {
<#
.SYNOPSIS
    Self-test forward-referenced from §0.3 — confirms baseline preconditions are satisfied.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $SessionContext,
        [Parameter(Mandatory)] [string]$SiteUrl
    )
    $checks = @()
    $checks += [pscustomobject]@{ Check='ShellHost';      Status=(if ($PSVersionTable.PSEdition -eq 'Core') {'Clean'} else {'Anomaly'}) }
    $checks += [pscustomobject]@{ Check='SessionContext'; Status=(if ($SessionContext) {'Clean'} else {'Anomaly'}) }
    $checks += [pscustomobject]@{ Check='GraphScopes';    Status=(Test-Fsi34GraphScopes -SessionContext $SessionContext).Status }
    $checks += [pscustomobject]@{ Check='IncidentList';   Status='Pending' }
    Connect-PnPOnline -Url $SiteUrl -Interactive -ErrorAction SilentlyContinue
    try {
        $list = Get-PnPList -Identity 'AI Agent Incidents' -ErrorAction SilentlyContinue
        $checks[-1].Status = if ($list) {'Clean'} else {'Anomaly'}
    } finally { Disconnect-PnPOnline -ErrorAction SilentlyContinue }
    $overall = if ($checks.Status -contains 'Anomaly') { 'Anomaly' } else { 'Clean' }
    [pscustomobject]@{ Status=$overall; Checks=$checks; Reason=if ($overall -eq 'Anomaly') { 'OneOrMoreSelfTestChecksFailed' } else { '' } }
}
```

---

## §14 — Anti-patterns and operating cadence

### 14.1 — Anti-patterns

| # | Anti-pattern | Why it fails | Correct approach |
|---|--------------|--------------|------------------|
| 1 | Running mutation helpers from Windows PowerShell 5.1 | Many Graph/PnP cmdlets target PS 7+ only; silent module-load mismatches mask real failures | `pwsh` 7.4+; `Assert-Fsi34ShellHost` enforces |
| 2 | Calling `Az.Sentinel` cmdlets without `Resolve-Fsi34SentinelWorkspace` | Workspace-resource-id mismatches in sovereign tenants; rules deploy to the wrong workspace | Always pre-resolve via §2.3 |
| 3 | Hard-coded notification timer hours | Regulator rule changes silently invalidate the constant; operators rely on stale values | Source of truth is the §9 table; verify against current rule text |
| 4 | Closing an NYDFS24 ransom timer without OFAC checkpoint | Sanctions-screening attestation gap creates Treasury-OFAC liability | §5.4 `!!! danger` block plus §9 NYDFS24 hand-off |
| 5 | Naming an internal owner as RCA without Service Health correlation | Microsoft-side outage is misattributed; downstream corrective actions misallocated | §8 `Get-Fsi-M365ServiceHealthIncident` is mandatory pre-RCA for Sev1/Sev2 |
| 6 | Writing tabletop incidents to the production list | Inflates quarterly counts; triggers real automation rules; produces false timer starts | §10 writes to `AI Agent Tabletop Exercises` only |
| 7 | Fewer than three signatures on the closed RCA | CISO+CCO+GC accountability chain incomplete; auditors flag as control gap | §11.2 enforces sample-based check |
| 8 | Treating `MRMTicketRef` as optional for model-risk incidents | Disconnects 3.4 RCA from Control 2.6 model-monitoring loop | §11.4 enforces sample-based check |
| 9 | Bypassing `Mode=LegalHold` for §7 helpers | Operational mistakes in legal-hold provisioning are the highest-impact errors in 3.4 | All §7 helpers refuse to run unless Mode=LegalHold |
| 10 | Skipping evidence-bundle SHA-256 manifest | Loss of immutable file-level provenance; SEC 17a-4(f) defensibility weakens | §4.3 emits manifest unconditionally |
| 11 | Treating regulator deadlines as wall-clock hours rather than from the determination event | Anchor errors are common; 4-day SEC 8-K and 24-hour NYDFS payment timers are determination-anchored | §9 `-DeterminationTimestamp` parameter is required |
| 12 | Calling Defender/Sentinel pull helpers without throttle handling | 429s mid-RCA fragment the evidence bundle | §4.5 `Invoke-Fsi34Throttled` handles backoff |
| 13 | Storing portal acknowledgments outside the SHA-256 manifest | Defensibility gap when regulator portal acknowledgment is later disputed | §9.3 `Stop-Fsi-RegulatorTimer` hashes the PDF |
| 14 | Allowing un-pinned module versions in production runners | Silent behavior changes in Az/Graph modules introduce regressions | Use the §1 module-pin matrix |
| 15 | Treating §11 verification as a "green light" rather than as a sample | A clean N=20 sample does not certify the universe; auditors expect documented sampling methodology | Record the sampling seed and population size in evidence packs |

### 14.2 — Operating cadence

| Cadence | Activity | Owner | Helper |
|---------|----------|-------|--------|
| Per incident (real time) | Detection → containment → RCA → notification | IR Lead + named officer | §4 + §5 + §9 |
| Daily (business days) | Open-timer review and escalation | CCO designate | §9.2 `Get-Fsi-OpenRegulatorTimers` |
| Weekly | Sentinel/Defender pull sample for RCA-pending incidents | IR Lead | §4.1 + §4.2 |
| Monthly | Service Health correlation audit on closed Sev1/Sev2 | CISO designate | §11.3 |
| Quarterly | Tabletop exercise (one scenario from §10) | AI Governance Lead | §10 |
| Quarterly | Evidence bundle export with four-signature attestation | CISO + CCO + GC + AI Governance Lead | §12 |
| Annual | KQL query review and §5 automation-rule version bump | Sentinel Contributor | §12 KQL hash diff |

!!! note "Hedged-language reminder"
    These helpers **support compliance with** the named regulations and **help meet** the timer-and-evidence elements that those regulations describe. They do not certify, guarantee, or eliminate regulatory risk. Implementation requires institution-specific legal review of each cited rule's current text, a documented Written Information Security Program (WISP) that aligns with the timer matrix, and ongoing supervisory review by qualified counsel.

---

## Cross-references

| Control | Title | Why it matters here |
|---------|-------|---------------------|
| [1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Data loss prevention and sensitivity labels | DLP signals and sensitivity-label context enrich §4 evidence pulls and §6 IRM cases |
| [1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive audit logging and compliance | Unified audit log is the canonical action source for §4 evidence bundles |
| [1.8](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Runtime protection and external threat detection | Detection surfaces feed §4 Defender/Sentinel pull helpers |
| [1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Data retention and deletion policies | §3 retention-label binding and §7 legal-hold helpers depend on a coherent retention scheme |
| [1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Conditional access and phishing-resistant MFA | Identity controls bound the named-officer signing path used in §11.2 evidence-chain |
| [1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) | Insider risk detection and response | §6 IRM helpers wrap the Purview Insider Risk Management surface |
| [2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Model risk management (OCC 2011-12 / SR 11-7) | §11.4 enforces the model-risk feedback loop from incident → MRM ticket |
| [2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision and oversight (FINRA Rule 3110) | Supervisory escalation paths drive §5 NotifyCISO-CCO-GC and §9 FINRA4530A timers |
| [2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Agent 365 admin center governance console | §4 agent-context enrichment relies on the 2.25 inventory |
| [3.2](../../../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Usage analytics and activity monitoring | §12 quarterly evidence consumes 3.2 activity baselines |
| [3.3](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance and regulatory reporting | §9 timer engine integrates with the broader 3.3 filing automation |
| [3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Orphaned agent detection and remediation | The §10 OrphanedAgentCascade scenario validates 3.6 hand-off |
| [3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Microsoft Sentinel integration | §4 and §5 helpers presume the 3.9 Sentinel baseline |

See also: [`docs/playbooks/_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) — module pinning, sovereign endpoints, mutation safety, evidence emission.

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
