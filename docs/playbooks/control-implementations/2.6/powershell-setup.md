# Control 2.6 — PowerShell Setup: MRM Evidence Inventories and Reports (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)

!!! danger "Non-Substitution — This PowerShell Produces Evidence; Validation Judgments Remain with People"
    The helpers in this playbook are **inventory, change-detection, and evidence-export** utilities. They do **not** perform model validation, **do not** assign model tiers, **do not** issue effective challenge, and **do not** approve, reject, or retire any AI agent. Those judgments are reserved — under OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) and Federal Reserve SR 26-2 §V (formerly SR 11-7 §V) — to:

    - The firm's **Model Risk Management Committee** (model-tiering, validation acceptance, model retirement).
    - The firm's **independent model validation function** — personnel **organizationally and functionally separate** from model owners and developers. "Independent" is the SR 26-2 §V (formerly SR 11-7 §V) test; third-party engagement is one way to achieve it but is not required and is not equivalent.
    - The firm's **effective challenge** process — qualified personnel not involved in model development conducting critical, objective review.
    - **Three lines of defense** — first line (model owner / developer), second line (independent MRM / validation / compliance), third line (Internal Audit).
    - **Registered-principal supervisory review** under FINRA Rule 3110 (see [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)).

    The Microsoft Purview DSPM for AI inventory, Azure AI Foundry evaluation harness, Microsoft Copilot Studio analytics, Agent 365 Admin Center, and Microsoft Entra Agent ID surfaces this playbook reads from are **evidence-collection surfaces**. They do not constitute, and must not be presented in your firm's MRM policy, WSPs, or examiner submissions as, a substitute for the human governance above. Treat every artifact this playbook emits as **input to** an MRM Committee or independent validation review — never as the conclusion of one.

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety, Dataverse compatibility, and SHA-256 evidence emission.

> **Scope.** This playbook automates **read-only evidence inventories** for [Control 2.6 — Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md). Outputs feed your existing MRM program; they do not replace it.
>
> **Namespace.** All functions use the `FsiMRM` prefix to prevent collision with peer-control automation (`Agt36`, `Agt225`, `Agt226`).
>
> **Hedged-language reminder.** The artifacts produced here **support compliance with** OCC Bulletin 2026-13 (formerly OCC 2011-12), SR 26-2 (formerly SR 11-7), FDIC FIL-22-2017, FFIEC IT Handbook, FINRA 3110/4511, SEC 17a-3/17a-4, SOX §§302/404, GLBA 501(b), and NYDFS 23 NYCRR 500. They do not — and cannot — *ensure*, *guarantee*, *prevent*, or *eliminate* anything on their own.

---

## §1 — Pre-flight: Modules, licenses, roles, and connection verification

### 1.1 — Module version matrix

Pin to versions approved by your Change Advisory Board. Floating versions break reproducibility and weaken SOX 404 / OCC 2023-17 evidence.

```powershell
# PowerShell 7.2+ required for Microsoft.Graph; Power Apps Administration cmdlets
# require Windows PowerShell 5.1 (Desktop). See baseline §2 for the wrong-shell guard
# pattern. Run inventory and change-feed steps from PS 7; run Power Apps maker/env
# enumeration from a PS 5.1 session that imports the produced JSON.

$FsiMRMModuleMatrix = @(
    @{ Name = 'Microsoft.Graph.Authentication';            Min = '2.19.0' },
    @{ Name = 'Microsoft.Graph.Identity.Governance';       Min = '2.19.0' },
    @{ Name = 'Microsoft.Graph.Applications';              Min = '2.19.0' },
    @{ Name = 'Microsoft.Graph.Users';                     Min = '2.19.0' },
    @{ Name = 'ExchangeOnlineManagement';                  Min = '3.4.0'  },  # Purview / unified audit log
    @{ Name = 'Microsoft.PowerApps.Administration.PowerShell'; Min = '2.0.175' },
    @{ Name = 'Az.Accounts';                               Min = '2.15.0' },  # Foundry workspace access
    @{ Name = 'Az.MachineLearningServices';                Min = '1.0.0'  }   # Foundry evaluator runs (TODO: verify exact module surface for Foundry GA)
)

function Test-FsiMRMModuleMatrix {
    [CmdletBinding()]
    param([switch]$InstallMissing)
    $results = foreach ($m in $FsiMRMModuleMatrix) {
        $installed = Get-Module -ListAvailable -Name $m.Name |
            Sort-Object Version -Descending | Select-Object -First 1
        $status = if (-not $installed) { 'Anomaly' }
                  elseif ($installed.Version -lt [version]$m.Min) { 'Anomaly' }
                  else { 'Clean' }
        if ($status -eq 'Anomaly' -and $InstallMissing) {
            try {
                Install-Module $m.Name -MinimumVersion $m.Min -Scope CurrentUser -AllowClobber -Force
                $status = 'Pending'   # re-import required
            } catch { $status = 'Error' }
        }
        [pscustomobject]@{
            Module    = $m.Name
            Required  = $m.Min
            Installed = $installed.Version
            Status    = $status
        }
    }
    $results
}
```

### 1.2 — Licenses and role prerequisites

| Capability | Minimum license / SKU | Canonical role(s) |
|---|---|---|
| Power Platform CoE inventory | Power Apps per-user OR per-app for the CoE owner; CoE Starter Kit installed | **Power Platform Admin** |
| DSPM for AI inventory of Copilot / Copilot Studio / Foundry / Entra-registered AI apps | Microsoft Purview (E5 Compliance or equivalent add-on); DSPM for AI enabled | **Purview Data Security AI Admin** + **Purview Compliance Admin** |
| Agent 365 Admin Center inventory | Agent 365 GA SKU in the tenant region (verify per Microsoft Learn) | **AI Administrator** |
| Entra Agent ID enumeration | Entra ID P1 minimum; P2 recommended for Identity Governance lifecycle workflows | **Entra Global Reader** (read-only); **Entra Identity Governance Admin** for lifecycle exports |
| Purview Unified Audit Log queries | E5 Compliance; audit log search enabled | **Purview Audit Admin** |
| Azure AI Foundry evaluator-run export | Contributor on the Foundry workspace; Storage Blob Data Reader on the linked storage | **AI Administrator** + Foundry-workspace RBAC |
| Evidence label application & WORM routing | Purview retention labels published; Records Management feature enabled | **Purview Records Manager** |

All role activations for evidence collection should be performed via **PIM with a `ChangeTicketId`** in the activation justification — see [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) for retention routing and [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for audit-log / 17a-4(f) handoff.

### 1.3 — Connection verification (commercial cloud)

```powershell
function Test-FsiMRMConnection {
    [CmdletBinding()]
    param()

    $tgt = @{ Graph='Global'; PP='prod'; Az='AzureCloud' }
    $checks = @()

    # Graph
    try {
        $ctx = Get-MgContext
        $checks += [pscustomobject]@{
            Surface = 'MicrosoftGraph'
            Expected = $tgt.Graph
            Actual   = $ctx.Environment
            Status   = if ($ctx.Environment -eq $tgt.Graph) { 'Clean' } else { 'Anomaly' }
            Note     = if (-not $ctx) { 'Not connected — call Connect-MgGraph -Environment Global' } else { '' }
        }
    } catch { $checks += [pscustomobject]@{ Surface='MicrosoftGraph'; Status='Error'; Note=$_.Exception.Message } }

    # Power Platform — no native session-introspection cmdlet; probe via env list
    try {
        $envs = Get-AdminPowerAppEnvironment -ErrorAction Stop
        $checks += [pscustomobject]@{
            Surface = 'PowerPlatform'
            Expected = $tgt.PP
            Actual   = "$($envs.Count) environment(s) returned"
            Status   = if ($envs.Count -gt 0) { 'Clean' } else { 'Anomaly' }
            Note     = if ($envs.Count -eq 0) { 'Empty list — verify Power Platform permissions and tenant access' } else { '' }
        }
    } catch { $checks += [pscustomobject]@{ Surface='PowerPlatform'; Status='Error'; Note=$_.Exception.Message } }

    # Azure (Foundry)
    try {
        $azCtx = Get-AzContext
        $checks += [pscustomobject]@{
            Surface = 'Azure'
            Expected = $tgt.Az
            Actual   = $azCtx.Environment.Name
            Status   = if ($azCtx.Environment.Name -eq $tgt.Az) { 'Clean' } else { 'Anomaly' }
            Note     = if (-not $azCtx) { "Run Connect-AzAccount -Environment $($tgt.Az)" } else { '' }
        }
    } catch { $checks += [pscustomobject]@{ Surface='Azure'; Status='Error'; Note=$_.Exception.Message } }

    # Exchange / Purview
    try {
        $eo = Get-ConnectionInformation -ErrorAction Stop | Where-Object { $_.State -eq 'Connected' }
        $uriProp = 'Connection' + 'Uri'
        $checks += [pscustomobject]@{
            Surface = 'ExchangeOnline'
            Expected = 'Commercial'
            Actual   = $eo.$uriProp
            Status   = if ($eo) { 'Clean' } else { 'Anomaly' }
            Note     = if (-not $eo) { 'Run Connect-ExchangeOnline and verify the session is connected' } else { '' }
        }
    } catch { $checks += [pscustomobject]@{ Surface='ExchangeOnline'; Status='Error'; Note=$_.Exception.Message } }

    [pscustomobject]@{
        Cloud  = 'Commercial'
        RunUtc = (Get-Date).ToUniversalTime()
        Status = if ($checks.Status -contains 'Error')   { 'Error' }
                 elseif ($checks.Status -contains 'Anomaly') { 'Anomaly' }
                 else { 'Clean' }
        Checks = $checks
    }
}
```

---


## §2 — Helper definitions

All four helpers below return `[pscustomobject]` with a top-level `Status` ∈ `{Clean, Anomaly, Pending, NotApplicable, Error}` and a `Findings` collection. Errors are **caught and reported**, never thrown to the caller — a thrown exception in a scheduled MRM job produces no evidence at all, which is worse than an `Error` artifact for an examiner.

### 2.1 — `Get-FsiAgentInventoryForMRM`

```powershell
function Get-FsiAgentInventoryForMRM {
<#
.SYNOPSIS
    Produces a unified AI-agent inventory for MRM Committee review by joining
    Power Platform CoE (Copilot Studio agents), Purview DSPM for AI (Copilot,
    Foundry, Entra-registered AI apps), and the Agent 365 Admin Center.

.DESCRIPTION
    Read-only. Does NOT classify model tier — Tier is populated from the firm's
    1.2 agent registry if supplied, otherwise emitted as 'Unassigned' with
    Status='Pending' so the MRM Committee assigns it.

    Each row is a [pscustomobject] with:
      AgentId, DisplayName, Owner, Environment, UnderlyingModel, ModelVersion,
      KnowledgeSources, LastValidationDate, NextValidationDate, Tier,
      Source ∈ {PowerPlatformCoE, DSPMforAI, Agent365}, Status

    Status values:
      Clean         — all required MRM fields populated, validation in-window
      Anomaly       — validation overdue, missing model card, or untiered with
                      production usage signals
      Pending       — newly discovered agent awaiting MRM Committee tiering
      Error         — surface call failed; row preserved for audit


.PARAMETER RegistryPath
    Optional path to the firm's 1.2 AI agent registry (CSV or JSON) used to
    enrich rows with Tier, LastValidationDate, NextValidationDate.

.PARAMETER ValidationWindowDays
    Days inside which a validation is considered current. Default 365 per
    common MRM annual-revalidation cycles; Tier-1 agents may require shorter.

.OUTPUTS
    [pscustomobject] { RunUtc, Status, Findings[] }
#>
    [CmdletBinding()]
    param(
        [string]$RegistryPath,
        [ValidateRange(30,1095)][int]$ValidationWindowDays = 365
    )

    $registry = @{}
    if ($RegistryPath -and (Test-Path $RegistryPath)) {
        try {
            $entries = if ($RegistryPath -match '\.json$') { Get-Content $RegistryPath -Raw | ConvertFrom-Json }
                       else { Import-Csv $RegistryPath }
            foreach ($e in $entries) { $registry[$e.AgentId] = $e }
        } catch {
            Write-Warning "Registry load failed: $($_.Exception.Message). Tier/validation fields will be Unassigned."
        }
    }

    $findings = @()

    # --- Source 1: Power Platform CoE (Copilot Studio agents) -------------
    try {
        $envs = Get-AdminPowerAppEnvironment -ErrorAction Stop
        foreach ($env in $envs) {
            # Copilot Studio agents surface as bots within the environment;
            # use Get-AdminPowerAppEnvironment + Dataverse query in production.
            # TODO: confirm the GA cmdlet name for Copilot Studio bot enumeration
            # (currently Get-AdminBot in the BAP API; verify against your pinned
            # Microsoft.PowerApps.Administration.PowerShell version).
            try {
                $bots = Get-AdminBot -EnvironmentName $env.EnvironmentName -ErrorAction Stop
            } catch { $bots = @() }

            foreach ($b in $bots) {
                $reg = $registry[$b.BotName]
                $row = [pscustomobject]@{
                    AgentId            = $b.BotName
                    DisplayName        = $b.DisplayName
                    Owner              = $b.Owner.userPrincipalName
                    Environment        = $env.DisplayName
                    UnderlyingModel    = $reg.UnderlyingModel    # CoE does not always expose model assignment
                    ModelVersion       = $reg.ModelVersion
                    KnowledgeSources   = $reg.KnowledgeSources
                    LastValidationDate = $reg.LastValidationDate
                    NextValidationDate = $reg.NextValidationDate
                    Tier               = if ($reg.Tier) { $reg.Tier } else { 'Unassigned' }
                    Source             = 'PowerPlatformCoE'
                    Status             = 'Pending'   # set below
                }
                $findings += (Resolve-FsiMRMRowStatus -Row $row -ValidationWindowDays $ValidationWindowDays)
            }
        }
    } catch {
        $findings += [pscustomobject]@{
            AgentId='(power-platform-error)'; Source='PowerPlatformCoE';
            Status='Error'; DisplayName=$_.Exception.Message
        }
    }

    # --- Source 2: Purview DSPM for AI ------------------------------------
    try {
            # DSPM for AI inventory is exposed via Microsoft Graph
            # /security/dataSecurityAndGovernance/* surface (preview at time of writing).
            # TODO: verify the GA endpoint path before production scheduling.
            $dspmAgents = Invoke-MgGraphRequest -Method GET `
                -Uri '/v1.0/security/dataSecurityAndGovernance/aiInteractionHistory?$top=999' `
                -ErrorAction Stop
            foreach ($a in $dspmAgents.value) {
                $reg = $registry[$a.appId]
                $row = [pscustomobject]@{
                    AgentId            = $a.appId
                    DisplayName        = $a.appDisplayName
                    Owner              = $a.ownerUpn
                    Environment        = $a.platform   # Copilot | CopilotStudio | Foundry | EntraRegistered
                    UnderlyingModel    = $a.modelId
                    ModelVersion       = $a.modelVersion
                    KnowledgeSources   = ($a.dataSources -join ';')
                    LastValidationDate = $reg.LastValidationDate
                    NextValidationDate = $reg.NextValidationDate
                    Tier               = if ($reg.Tier) { $reg.Tier } else { 'Unassigned' }
                    Source             = 'DSPMforAI'
                    Status             = 'Pending'
                }
                $findings += (Resolve-FsiMRMRowStatus -Row $row -ValidationWindowDays $ValidationWindowDays)
            }
        } catch {
            $findings += [pscustomobject]@{
                AgentId='(dspm-error)'; Source='DSPMforAI';
                Status='Error'; DisplayName=$_.Exception.Message
            }
    }

    # --- Source 3: Agent 365 Admin Center ---------------------------------
    try {
            # Agent 365 inventory is exposed via Graph /agents (preview).
            # TODO: pin to GA endpoint when announced.
            $a365 = Invoke-MgGraphRequest -Method GET -Uri '/beta/agents?$top=999' -ErrorAction Stop
            foreach ($a in $a365.value) {
                $reg = $registry[$a.id]
                $row = [pscustomobject]@{
                    AgentId            = $a.id
                    DisplayName        = $a.displayName
                    Owner              = $a.owner.userPrincipalName
                    Environment        = 'Agent365'
                    UnderlyingModel    = $a.modelBinding.modelId
                    ModelVersion       = $a.modelBinding.modelVersion
                    KnowledgeSources   = ($a.knowledge.sources -join ';')
                    LastValidationDate = $reg.LastValidationDate
                    NextValidationDate = $reg.NextValidationDate
                    Tier               = if ($reg.Tier) { $reg.Tier } else { 'Unassigned' }
                    Source             = 'Agent365'
                    Status             = 'Pending'
                }
                $findings += (Resolve-FsiMRMRowStatus -Row $row -ValidationWindowDays $ValidationWindowDays)
            }
        } catch {
            $findings += [pscustomobject]@{
                AgentId='(agent365-error)'; Source='Agent365';
                Status='Error'; DisplayName=$_.Exception.Message
            }
    }

    $aggregate = if ($findings.Status -contains 'Error') { 'Error' }
                 elseif ($findings.Status -contains 'Anomaly') { 'Anomaly' }
                 elseif ($findings.Status -contains 'Pending') { 'Pending' }
                 elseif ($findings.Status -contains 'NotApplicable') { 'NotApplicable' }
                 else { 'Clean' }

    [pscustomobject]@{
        RunUtc   = (Get-Date).ToUniversalTime()
        Source   = 'Get-FsiAgentInventoryForMRM'
        Status   = $aggregate
        Findings = $findings
    }
}

function Resolve-FsiMRMRowStatus {
    param($Row, [int]$ValidationWindowDays)
    $now = Get-Date
    if ($Row.Tier -eq 'Unassigned') { $Row.Status = 'Pending'; return $Row }
    if (-not $Row.LastValidationDate) { $Row.Status = 'Anomaly'; return $Row }
    try {
        $last = [datetime]$Row.LastValidationDate
        if (($now - $last).TotalDays -gt $ValidationWindowDays) { $Row.Status = 'Anomaly' }
        else { $Row.Status = 'Clean' }
    } catch { $Row.Status = 'Anomaly' }
    $Row
}
```

### 2.2 — `Get-FsiAgentModelChangeFeed`

Per **SR 26-2 §V (formerly SR 11-7 §V) (vendor-model governance)**, the firm must monitor and disposition vendor-driven changes to underlying models — including default-model migrations in Copilot Studio and model deprecations in Azure AI Foundry. This helper aggregates two signal sources into a disposition-ready feed.

```powershell
function Get-FsiAgentModelChangeFeed {
<#
.SYNOPSIS
    Surfaces vendor-driven model-change signals (Power Platform release plan
    items + M365 Message Center notices) the MRM Committee must disposition
    under SR 26-2 §V (formerly SR 11-7 §V) vendor-model governance.

.DESCRIPTION
    Read-only. Pulls candidate change events from:
      1. Microsoft Graph /admin/serviceAnnouncement/messages (Message Center)
         filtered to Copilot / Copilot Studio / Foundry / Azure OpenAI services.
      2. Power Platform Release Plan public RSS feed.

    Each row is dispositioned as:
      Anomaly       — pending default-model migration or Foundry deprecation
                      affecting an in-scope agent
      Pending       — change announced but not yet effective; MRM tracking only
      Clean         — informational notice (e.g. UI changes) not affecting model
      Error         — feed call failed


.PARAMETER LookbackDays
    Days of message history to pull. Default 90.

.PARAMETER InventoryFindings
    Optional output of Get-FsiAgentInventoryForMRM .Findings to enrich change
    rows with affected-agent counts.
#>
    [CmdletBinding()]
    param(
        [ValidateRange(7,365)][int]$LookbackDays = 90,
        [object[]]$InventoryFindings
    )

    $cutoff = (Get-Date).AddDays(-$LookbackDays).ToUniversalTime()
    $rows = @()

    # --- Signal 1: Message Center via Graph -------------------------------
    try {
        $msgs = Invoke-MgGraphRequest -Method GET `
            -Uri "/v1.0/admin/serviceAnnouncement/messages?`$top=200" `
            -ErrorAction Stop
        foreach ($m in $msgs.value) {
            $title = "$($m.title)"
            $body  = "$($m.body.content)"
            $isModelChange = $title -match '(?i)copilot|foundry|azure openai|gpt|claude|model.*deprecat|default model'
            if (-not $isModelChange) { continue }
            $effective = if ($m.actionRequiredByDateTime) { [datetime]$m.actionRequiredByDateTime } else { $null }
            $affected  = if ($InventoryFindings) {
                @($InventoryFindings | Where-Object { $body -match [regex]::Escape("$($_.UnderlyingModel)") }).Count
            } else { 0 }
            $status = if ($effective -and $effective -gt (Get-Date) -and $affected -gt 0) { 'Anomaly' }
                      elseif ($affected -gt 0) { 'Pending' }
                      else { 'Clean' }
            $rows += [pscustomobject]@{
                Source           = 'MessageCenter'
                Id               = $m.id
                Title            = $title
                Category         = $m.category
                EffectiveUtc     = $effective
                PublishedUtc     = $m.startDateTime
                AffectedAgentCount = $affected
                DispositionDue   = if ($effective) { $effective.AddDays(-30) } else { $null }
                Status           = $status
            }
        }
    } catch {
        $rows += [pscustomobject]@{
            Source='MessageCenter'; Status='Error'; Title=$_.Exception.Message
        }
    }

    # --- Signal 2: Power Platform Release Plan ----------------------------
    try {
            # Public release plan RSS — verify the canonical URL with Microsoft Learn
            # before scheduling. TODO: confirm endpoint stability.
            $rss = Invoke-RestMethod -Uri 'https://learn.microsoft.com/en-us/power-platform/release-plan/feed' -ErrorAction Stop
            foreach ($item in $rss) {
                if ([datetime]$item.pubDate -lt $cutoff) { continue }
                $isModel = "$($item.title) $($item.description)" -match '(?i)copilot studio.*model|default.*model|foundry'
                if (-not $isModel) { continue }
                $rows += [pscustomobject]@{
                    Source           = 'PowerPlatformReleasePlan'
                    Id               = $item.guid
                    Title            = $item.title
                    Category         = 'ReleasePlan'
                    EffectiveUtc     = [datetime]$item.pubDate
                    PublishedUtc     = [datetime]$item.pubDate
                    AffectedAgentCount = 0
                    DispositionDue   = ([datetime]$item.pubDate).AddDays(30)
                    Status           = 'Pending'
                }
            }
        } catch {
            $rows += [pscustomobject]@{ Source='PowerPlatformReleasePlan'; Status='Error'; Title=$_.Exception.Message }
    }

    $aggregate = if ($rows.Status -contains 'Error') { 'Error' }
                 elseif ($rows.Status -contains 'Anomaly') { 'Anomaly' }
                 elseif ($rows.Status -contains 'Pending') { 'Pending' }
                 else { 'Clean' }

    [pscustomobject]@{
        RunUtc   = (Get-Date).ToUniversalTime()
        Source   = 'Get-FsiAgentModelChangeFeed'
        Status   = $aggregate
        Findings = $rows
    }
}
```

### 2.3 — `Export-FsiMRMEvidencePackage`

Bundles the inventory, change feed, and (optionally) Foundry evaluator runs into a structured folder ready for MRM Committee review and 17a-4(f)-vendor ingestion. **Mutation safety is not required** — this helper writes only to the local evidence path supplied by the caller; downstream WORM routing is performed by [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) retention labels and the 17a-4(f) vendor pipeline.

```powershell
function Export-FsiMRMEvidencePackage {
<#
.SYNOPSIS
    Exports an MRM Committee evidence package: inventory snapshot, vendor-model
    change feed, optional Foundry evaluator-run index, and a SHA-256 manifest.

.DESCRIPTION
    Writes a folder structured as:
      <EvidencePath>\mrm-<yyyyMMddTHHmmssZ>\
        ├─ inventory.json
        ├─ inventory-summary.csv
        ├─ change-feed.json
        ├─ foundry-evaluator-runs.json   (only if -FoundryWorkspaceId supplied)
        ├─ manifest.json                 (SHA-256 per artifact + script version)
        └─ README.md                     (human-readable cover for committee)

    Each artifact in manifest.json carries Status ∈ {Clean, Anomaly, Pending,
    NotApplicable, Error} so the MRM Committee chair can triage at a glance.


.PARAMETER EvidencePath
    Local folder to write into. Should be Purview-labeled (see Control 1.7) or
    pre-mounted to your 17a-4(f) vendor staging area (see Control 1.9).

.PARAMETER RegistryPath
    Optional 1.2 agent registry CSV/JSON; passed through to the inventory helper.

.PARAMETER FoundryWorkspaceId
    Optional Azure AI Foundry workspace resource ID. When supplied, the helper
    enumerates evaluator runs and includes a structured index. Omit if Foundry
    is not in scope for this MRM cycle.

.PARAMETER ScriptVersion
    Tag used in the manifest. Default 'v1.4'.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$EvidencePath,
        [string]$RegistryPath,
        [string]$FoundryWorkspaceId,
        [string]$ScriptVersion = 'v1.4'
    )

    $ts        = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $pkgRoot   = Join-Path $EvidencePath "mrm-$ts"
    New-Item -ItemType Directory -Force -Path $pkgRoot | Out-Null

    $artifacts = @()

    function _emit {
        param($Name, $Object)
        $path = Join-Path $pkgRoot $Name
        try {
            $Object | ConvertTo-Json -Depth 25 | Set-Content -Path $path -Encoding UTF8
            $hash = (Get-FileHash -Path $path -Algorithm SHA256).Hash
            $artifacts += [pscustomobject]@{
                File          = $Name
                Sha256        = $hash
                Bytes         = (Get-Item $path).Length
                GeneratedUtc  = $ts
                ScriptVersion = $ScriptVersion
                Status        = $Object.Status
            }
        } catch {
            $artifacts += [pscustomobject]@{
                File=$Name; Status='Error'; ScriptVersion=$ScriptVersion;
                GeneratedUtc=$ts; Note=$_.Exception.Message
            }
        }
        # Return the updated artifacts collection back to the parent scope.
        Set-Variable -Scope 1 -Name artifacts -Value $artifacts
    }

    # 1) Inventory
    $inv = Get-FsiAgentInventoryForMRM -RegistryPath $RegistryPath
    _emit -Name 'inventory.json' -Object $inv
    try {
        $invCsv = $inv.Findings | Select-Object AgentId,DisplayName,Owner,Environment,UnderlyingModel,ModelVersion,Tier,LastValidationDate,NextValidationDate,Source,Status
        $csvPath = Join-Path $pkgRoot 'inventory-summary.csv'
        $invCsv | Export-Csv -NoTypeInformation -Path $csvPath -Encoding UTF8
        $artifacts += [pscustomobject]@{
            File='inventory-summary.csv'
            Sha256=(Get-FileHash $csvPath -Algorithm SHA256).Hash
            Bytes=(Get-Item $csvPath).Length; GeneratedUtc=$ts; ScriptVersion=$ScriptVersion
            Status=$inv.Status
        }
    } catch {
        $artifacts += [pscustomobject]@{
            File='inventory-summary.csv'; Status='Error'
            ScriptVersion=$ScriptVersion; GeneratedUtc=$ts; Note=$_.Exception.Message
        }
    }

    # 2) Change feed
    $feed = Get-FsiAgentModelChangeFeed -InventoryFindings $inv.Findings
    _emit -Name 'change-feed.json' -Object $feed

    # 3) Foundry evaluator runs (optional — caller provides workspace ID)
    if ($FoundryWorkspaceId) {
        try {
            # TODO: confirm the GA cmdlet for Foundry evaluator-run enumeration
            # in your pinned Az.MachineLearningServices version. The Foundry
            # surface is moving; in the absence of a stable cmdlet, fall back
            # to the REST API at /providers/Microsoft.MachineLearningServices/workspaces/{ws}/jobs.
            $runs = Get-AzMLWorkspaceJob -ResourceId $FoundryWorkspaceId -ErrorAction Stop |
                Where-Object { $_.Properties.jobType -eq 'evaluation' }
            $runIndex = [pscustomobject]@{
                RunUtc   = (Get-Date).ToUniversalTime()
                WorkspaceId = $FoundryWorkspaceId
                Status   = if ($runs.Count -eq 0) { 'Pending' } else { 'Clean' }
                Findings = @($runs | Select-Object Id, Name, Status, CreatedAt, ModelVersion, EvaluatorIds)
            }
            _emit -Name 'foundry-evaluator-runs.json' -Object $runIndex
        } catch {
            _emit -Name 'foundry-evaluator-runs.json' -Object ([pscustomobject]@{
                RunUtc=(Get-Date).ToUniversalTime(); WorkspaceId=$FoundryWorkspaceId
                Status='Error'; Findings=@(); Note=$_.Exception.Message
            })
        }
    }

    # 4) Manifest + README
    $manifest = [pscustomobject]@{
        PackageId     = "mrm-$ts"
        Cloud         = 'Commercial'
        ScriptVersion = $ScriptVersion
        GeneratedUtc  = $ts
        Status        = if ($artifacts.Status -contains 'Error') { 'Error' }
                        elseif ($artifacts.Status -contains 'Anomaly') { 'Anomaly' }
                        elseif ($artifacts.Status -contains 'Pending') { 'Pending' }
                        elseif ($artifacts.Status -contains 'NotApplicable') { 'NotApplicable' }
                        else { 'Clean' }
        Artifacts     = $artifacts
    }
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -Path (Join-Path $pkgRoot 'manifest.json') -Encoding UTF8

    $readme = @"
# MRM Evidence Package $($manifest.PackageId)

**Generated (UTC):** $ts
**Script version:** $ScriptVersion
**Aggregate Status:** $($manifest.Status)

This package is **input to** an MRM Committee or independent validation review.
It is not a validation, a tier assignment, or an effective-challenge record. All
MRM judgments under OCC Bulletin 2026-13 / SR 26-2 (formerly OCC 2011-12 / SR 11-7) §V remain with the firm's MRM
Committee and independent validators.

## Contents
$($artifacts | ForEach-Object { "- ``$($_.File)`` — Status: $($_.Status)" } | Out-String)

## Next steps
1. Apply Purview retention label per Control 1.9 (Data Retention and Deletion Policies).
2. Route to 17a-4(f) audit/vendor staging per Control 1.7 (Comprehensive Audit Logging and Compliance).
3. Add to the next MRM Committee agenda; assign disposition owners for any
   row with Status = Anomaly or Pending.
"@
    $readme | Set-Content -Path (Join-Path $pkgRoot 'README.md') -Encoding UTF8

    [pscustomobject]@{
        RunUtc        = (Get-Date).ToUniversalTime()
        PackagePath   = $pkgRoot
        Status        = $manifest.Status
        ArtifactCount = $artifacts.Count
        Manifest      = $manifest
    }
}
```

---

## §3 — Reporting recipes

### 3.1 — Quarterly inventory snapshot for MRM Committee

```powershell
$pkg = Export-FsiMRMEvidencePackage `
    -EvidencePath 'D:\evidence\mrm\Q2-2026' `
    -RegistryPath 'D:\registry\agent-registry-1.2.json' `
    -FoundryWorkspaceId '/subscriptions/.../workspaces/mrm-foundry-prod'

$pkg | Format-List PackagePath, Status, ArtifactCount
# Hand PackagePath to MRM Committee chair via Purview-labeled email or
# SharePoint location with retention label applied (see Control 1.7).
```

### 3.2 — Validation-due-soon list (next 30 / 60 / 90 days)

```powershell
$inv = Get-FsiAgentInventoryForMRM -RegistryPath '.\registry.json'
$now = Get-Date

$dueSoon = $inv.Findings | Where-Object {
    $_.NextValidationDate -and ([datetime]$_.NextValidationDate - $now).TotalDays -le 90
} | Select-Object AgentId, DisplayName, Tier, NextValidationDate,
    @{n='DaysUntilDue';e={[int]([datetime]$_.NextValidationDate - $now).TotalDays}},
    @{n='Bucket';e={
        $d = ([datetime]$_.NextValidationDate - $now).TotalDays
        if ($d -le 30) {'30-day'} elseif ($d -le 60) {'60-day'} else {'90-day'}
    }} | Sort-Object DaysUntilDue

$dueSoon | Export-Csv -Path '.\validation-due-soon.csv' -NoTypeInformation
$dueSoon | Group-Object Bucket | Format-Table Name, Count
```

### 3.3 — Vendor-model-change disposition log

```powershell
$inv  = Get-FsiAgentInventoryForMRM -RegistryPath '.\registry.json'
$feed = Get-FsiAgentModelChangeFeed -InventoryFindings $inv.Findings -LookbackDays 180

$dispositionLog = $feed.Findings | Where-Object Status -in @('Anomaly','Pending') |
    Select-Object Source, Id, Title, EffectiveUtc, AffectedAgentCount, DispositionDue, Status,
        @{n='OwnerToAssign';e={'MRM Committee chair'}},
        @{n='DispositionDecision';e={''}},
        @{n='DecisionDateUtc';e={''}}

$dispositionLog | Export-Csv -Path '.\sr26-2-vendor-model-disposition.csv' -NoTypeInformation
# DispositionDecision and DecisionDateUtc are filled in by the MRM Committee,
# NOT by this script. The script produces the queue; people produce the decisions.
```

### 3.4 — Outcomes-analysis evidence index

Outcomes analysis (SR 26-2 §V (formerly SR 11-7 §V)) requires that model output be compared against actual outcomes on an ongoing basis. This recipe indexes the evidence inputs the MRM analyst will join — it does not perform the analysis.

```powershell
$pkg = Export-FsiMRMEvidencePackage `
    -EvidencePath 'D:\evidence\mrm\outcomes-Q2-2026' `
    -RegistryPath '.\registry.json' `
    -FoundryWorkspaceId '/subscriptions/.../workspaces/mrm-foundry-prod'

$index = [pscustomobject]@{
    PackagePath       = $pkg.PackagePath
    InventoryArtifact = 'inventory.json'
    EvaluatorArtifact = 'foundry-evaluator-runs.json'
    ChangeFeedArtifact= 'change-feed.json'
    Status            = $pkg.Status
    AnalystAction     = 'Join evaluator run output to production telemetry from the firm''s downstream business systems; perform outcomes analysis per SR 26-2 §V (formerly SR 11-7 §V); record conclusion in MRM Committee minutes.'
}
$index | ConvertTo-Json -Depth 5 |
    Set-Content -Path (Join-Path $pkg.PackagePath 'outcomes-analysis-index.json')
```

---

## §4 — Scheduling and retention

### 4.1 — Azure Automation pattern

Run the quarterly snapshot as an Azure Automation runbook with a managed identity granted the read-only roles in §1.2. **Do not** grant remediation roles to the runbook identity — this control's automation is read-only.

```powershell
# Runbook entry point (PowerShell 7.2 Runbook, hybrid worker recommended for
# Power Platform cmdlet support which still requires Windows PowerShell 5.1).
Connect-AzAccount -Identity -Environment AzureCloud | Out-Null
Connect-MgGraph -Identity -Environment Global -NoWelcome
# Power Platform cmdlets cannot use managed identity directly; use a CAB-approved
# certificate-based service principal stored in Automation credentials.
$pp = Get-AutomationPSCredential -Name 'pp-coe-readonly-spn'
Add-PowerAppsAccount -ApplicationId $pp.UserName -ClientSecret $pp.GetNetworkCredential().Password -TenantID $env:AZURE_TENANT_ID

$evidencePath = Join-Path $env:TEMP "mrm-$(Get-Date -Format yyyyMMdd)"
$pkg = Export-FsiMRMEvidencePackage -EvidencePath $evidencePath `
    -RegistryPath $env:MRM_REGISTRY_BLOB_LOCAL_PATH

# Upload to Purview-labeled SharePoint or to 17a-4(f) vendor staging blob
Set-AzStorageBlobContent -Container 'mrm-evidence' `
    -File (Join-Path $pkg.PackagePath 'manifest.json') `
    -Blob "$($pkg.Manifest.PackageId)/manifest.json" `
    -Context (New-AzStorageContext -StorageAccountName $env:WORM_STORAGE_ACCOUNT -UseConnectedAccount)
# Apply Purview retention label downstream — see Control 1.9.
```

### 4.2 — On-premises scheduled task pattern

Where Automation is not approved, use a Windows Task Scheduler job on a hardened admin workstation. The task must:

- Run under a least-privilege managed service account.
- Write artifacts to a folder that is **inside** a Purview retention scope OR mounted to your 17a-4(f) vendor's secure ingestion share.
- Produce `Start-Transcript` / `Stop-Transcript` logs for the audit trail (see baseline §3).

### 4.3 — Retention routing

| Artifact | Retention requirement | Routing |
|---|---|---|
| Inventory snapshot (CSV + JSON) | 7 years (SOX 802) minimum; 6 years (SEC 17a-4) for broker-dealer scope | Purview retention label (Control 1.7) → 17a-4(f) vendor (Control 1.9) |
| Vendor-model-change disposition log | Life of model + 7 years (MRM policy norm) | Same as above |
| Foundry evaluator-run index | 7 years; underlying run artifacts retained per Foundry workspace policy | Same as above |
| MRM Committee minutes referencing the package | Permanent (MRM policy) | Records Management retention label |
| `manifest.json` (SHA-256 integrity) | Permanent — integrity proof must outlive the artifact | Records Management retention label |

Cross-link: [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md), [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---

## §5 — Verification checks

Run these after every scheduled execution. Each check returns a `[pscustomobject]` with the canonical `Status` enum so a downstream SIEM / Sentinel rule can alert on `Anomaly` or `Error` without parsing free text.

```powershell
function Test-FsiMRMPackageIntegrity {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$PackagePath)

    $checks = @()
    $manifestPath = Join-Path $PackagePath 'manifest.json'

    # Check 1: package exists
    $checks += [pscustomobject]@{
        Check  = 'PackageExists'
        Status = if (Test-Path $PackagePath) { 'Clean' } else { 'Error' }
        Note   = $PackagePath
    }

    # Check 2: manifest exists
    $checks += [pscustomobject]@{
        Check  = 'ManifestExists'
        Status = if (Test-Path $manifestPath) { 'Clean' } else { 'Error' }
        Note   = $manifestPath
    }
    if (-not (Test-Path $manifestPath)) {
        return [pscustomobject]@{ Status='Error'; Checks=$checks }
    }

    $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json

    # Check 3: every artifact in manifest exists on disk
    foreach ($a in $manifest.Artifacts) {
        $p = Join-Path $PackagePath $a.File
        $checks += [pscustomobject]@{
            Check  = "ArtifactPresent:$($a.File)"
            Status = if (Test-Path $p) { 'Clean' } else { 'Anomaly' }
            Note   = $p
        }
    }

    # Check 4: SHA-256 matches recorded hash
    foreach ($a in $manifest.Artifacts) {
        $p = Join-Path $PackagePath $a.File
        if (-not (Test-Path $p)) { continue }
        $live = (Get-FileHash -Path $p -Algorithm SHA256).Hash
        $checks += [pscustomobject]@{
            Check  = "ShaMatch:$($a.File)"
            Status = if ($live -eq $a.Sha256) { 'Clean' } else { 'Anomaly' }
            Note   = "expected=$($a.Sha256) actual=$live"
        }
    }

    # Check 5: package age (alert if > 100 days for quarterly cadence)
    $ageDays = ((Get-Date).ToUniversalTime() - [datetime]::ParseExact($manifest.GeneratedUtc,'yyyyMMddTHHmmssZ',$null)).TotalDays
    $checks += [pscustomobject]@{
        Check  = 'PackageFreshness'
        Status = if ($ageDays -le 100) { 'Clean' } elseif ($ageDays -le 130) { 'Anomaly' } else { 'Error' }
        Note   = "$([int]$ageDays) days old"
    }

    # Check 6: inventory contains at least one row (else likely auth failure)
    $invPath = Join-Path $PackagePath 'inventory.json'
    if (Test-Path $invPath) {
        $inv = Get-Content $invPath -Raw | ConvertFrom-Json
        $checks += [pscustomobject]@{
            Check  = 'InventoryNonEmpty'
            Status = if ($inv.Findings.Count -gt 0) { 'Clean' } else { 'Anomaly' }
            Note   = "$($inv.Findings.Count) row(s)"
        }
    }

    [pscustomobject]@{
        PackagePath = $PackagePath
        RunUtc      = (Get-Date).ToUniversalTime()
        Status      = if ($checks.Status -contains 'Error') { 'Error' }
                      elseif ($checks.Status -contains 'Anomaly') { 'Anomaly' }
                      else { 'Clean' }
        Checks      = $checks
    }
}
```

---

## §6 — Troubleshooting hooks

| Symptom | Likely cause | First check | Cross-link |
|---|---|---|---|
| `Get-FsiAgentInventoryForMRM` returns 0 rows from DSPM for AI | DSPM for AI not provisioned, or Purview Data Security AI Admin role not active | Verify role activation in PIM and confirm DSPM for AI onboarding | [Troubleshooting playbook](./troubleshooting.md) |
| `Get-FsiAgentInventoryForMRM` returns 0 rows from Agent 365 Admin Center | Agent 365 not GA in your region, or licensing not enabled | Confirm Agent 365 SKU per Microsoft Learn and verify the Agent 365 Admin Center inventory surface | [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) |
| `Export-FsiMRMEvidencePackage` writes Foundry artifact with `Status='Error'` and `Note=ResourceNotFound` | Foundry workspace ID malformed or RBAC missing | Validate full `/subscriptions/.../resourceGroups/.../providers/Microsoft.MachineLearningServices/workspaces/<name>` path; verify Contributor + Storage Blob Data Reader | [Troubleshooting playbook](./troubleshooting.md) |
| Graph throttling (HTTP 429) on `aiInteractionHistory` or `messages` | DSPM for AI / Message Center pages aggressively at tenant scale | Implement `Retry-After` honoring; reduce `$top`; split runs by week | [Troubleshooting playbook](./troubleshooting.md) |
| `Test-FsiMRMPackageIntegrity` reports `ShaMatch:Anomaly` | Artifact mutated after manifest write (possible WORM violation) | Treat as **incident**; preserve package and the divergent artifact; notify Purview Records Manager and Internal Audit | [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) |
| `Get-AdminBot` cmdlet not found | Module surface for Copilot Studio bot enumeration changed; module pinning drifted | Check pinned `Microsoft.PowerApps.Administration.PowerShell` version; review module release notes; substitute Dataverse query or BAP REST call as fallback | Baseline §1 |

For full diagnostic flows, see the companion [Troubleshooting playbook](./troubleshooting.md).

---

## Cross-references

- **Framework controls**
    - [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — 17a-4(f) audit-log retention and vendor handoff
    - [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — Purview retention label routing
    - [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) — registered-principal supervisory review
    - [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — Agent 365 inventory surface
    - [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) — Entra Agent ID inventory surface
    - [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — adjacent inventory reconciliation worksheet patterns
- **Companion playbooks for Control 2.6**
    - [Portal walkthrough](./portal-walkthrough.md)
    - [Verification testing](./verification-testing.md)
    - [Troubleshooting](./troubleshooting.md)
- **Authoring references**
    - [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
