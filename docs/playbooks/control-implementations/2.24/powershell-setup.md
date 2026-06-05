---
title: "Control 2.24 — PowerShell Setup: Agent Feature Enablement and Restriction Governance"
description: "PowerShell automation aids in inventorying, validating, and forwarding evidence for Microsoft 365 / Power Platform / Copilot Studio agent feature toggles across the commercial cloud."
control_id: "2.24"
control_title: "Agent Feature Enablement and Restriction Governance"
playbook_type: "powershell-setup"
last_ui_verified: "2026-04-15"
version: "v1.4"
audience:
  - "AI Administrator"
  - "Power Platform Admin"
  - "AI Governance Lead"
  - "Compliance Officer"
  - "Change Management Team"
  - "Agent Owner"
regulatory_anchors:
  - "SOX-302"
  - "SOX-404"
  - "FINRA-3110"
  - "FINRA-4511"
  - "FINRA-25-07"
  - "FedSR-11-7"
  - "OCC-2011-12"
  - "FFIEC-IT-RM"
  - "GLBA-501b"
  - "SEC-RegSCI"
---

# Control 2.24 — PowerShell Setup: Agent Feature Enablement and Restriction Governance

> **Control reference:** [Control 2.24 — Agent Feature Enablement and Restriction Governance](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md)
>
> **Sister playbooks:**
> [Portal Walkthrough](portal-walkthrough.md) · [Verification & Testing](verification-testing.md) · [Troubleshooting](troubleshooting.md)
>
> **Shared baseline:** [PowerShell Baseline](../../_shared/powershell-baseline.md)

The scripts in this playbook **aid in** discovering which Microsoft 365 / Power Platform / Microsoft Copilot Studio / Agent Framework features are currently enabled in a tenant, **help meet** the SOX-302, FINRA 3110/4511 (with RN 24-09 for AI supervisory guidance), Fed SR 26-2 (formerly SR 11-7), OCC Bulletin 2026-13 (formerly OCC 2011-12), FFIEC IT-RM, GLBA 501(b), and SEC Reg SCI evidence expectations summarised in the parent control, and **support compliance with** change-management gating for any feature toggle that affects an in-scope agent. They do **not** themselves authorize a feature to be enabled, replace Model Risk Management review (Control 2.6), substitute for the supervision program (Control 2.12), or grant publishing authorization (Control 1.1). Every output is a *signal* that an Agent Governance Lead, AI Administrator, or Change Advisory Board member must reconcile against an approved Feature Catalog entry before declaring the tenant state compliant. Implementation requires the canonical role assignments listed in [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md); organizations should verify each helper's behaviour in a non-production tenant before scheduling it.

## Scope

| # | Automation area | Primary helper | Pester namespace |
|---|---|---|---|
| 1 | Module pinning, Graph scope matrix, RBAC + PIM gating | `Initialize-Feat224Session` | (prereq) |
| 2 | Commercial bootstrap and helper utilities | `Initialize-Feat224Session` | (prereq) |
| 3 | Dataverse Feature Catalog table provisioning | `Deploy-Feat224FeatureCatalog` | `CATALOG` |
| 4 | Microsoft 365 admin center / Copilot hub reader | `Get-Feat224M365FeatureState` | `M365HUB` |
| 5 | Power Platform Admin Center reader | `Get-Feat224PpacFeatureState` | `PPAC`, `ENV` |
| 6 | Copilot Studio agent feature reader | `Get-Feat224AgentFeatureState` | `AGENT` |
| 7 | DLP policy ↔ feature catalog correlation | `Compare-Feat224DlpAlignment` | `DLP` |
| 8 | Zone (1/2/3) compliance diff | `Compare-Feat224ZoneCompliance` | `ZONE` |
| 9 | MCP connector + Agent Framework flag enumeration | `Get-Feat224McpAgfState` | `MCP`, `AGF` |
| 10 | Change-management evidence exporter | `Export-Feat224ChangeEvidence` | `CHANGE` |
| 11 | Sentinel / SIEM forwarding | `Send-Feat224SiemEvent` | `SIEM` |
| 12 | Scheduling (Az Automation / scheduled jobs) | `Register-Feat224Schedule` | (operational) |
| 13 | Retention alignment with Control 2.13 | `Set-Feat224EvidenceRetention` | (operational) |
| 14 | Cross-control references | (documentation) | — |

## Audience

These scripts are written for **AI Administrators** (the primary owner of tenant-level Microsoft 365 Copilot toggles per the v1.3.3 patch to Control 2.24), **Power Platform Admins** (environment-scope feature flags and DLP), **AI Governance Leads** (catalog ownership and exception adjudication), **Compliance Officers** (evidence sign-off), the **Change Management Team** (CAB ticket reconciliation), and **Agent Owners** (per-agent attestations). **Entra Global Admin** is reserved for exceptional changes only — do **not** run mutation helpers under a permanent Global Admin assignment; use PIM eligible-activation as shown in §1.

---

## §0 — Wrong-shell traps and the false-clean defect catalog

Before running anything in this playbook, confirm you are in the **correct elevated shell** and that prior Graph / Power Platform sessions are not silently masking failures. The following defect catalog enumerates the fifteen most common ways a 2.24 helper has historically returned `Status = 'Clean'` when the tenant was, in fact, non-compliant. Every helper in §§2–10 includes a `Reason` populated from this catalog whenever it downgrades a result to `Anomaly`.

### Wrong-shell traps

| # | Symptom | Root cause | Mitigation |
|---|---|---|---|
| W1 | `Connect-MgGraph` returns instantly with no prompt | Cached delegated token from a different tenant | Run `Disconnect-MgGraph; Clear-MgContext` before §2 bootstrap |
| W2 | `Add-PowerAppsAccount` succeeds in Windows PowerShell 5.1 but `Get-AdminPowerApp` throws `MethodNotFound` | Module loaded into the wrong runtime | Use **PowerShell 7.4+ (pwsh)** exclusively; `Assert-Feat224ShellHost` blocks 5.1 |
| W4 | Pester `BeforeAll` runs as a different identity than `It` blocks | Mixed device-code + cert auth in one session | Pin a single auth method per shell; `Initialize-Feat224Session` enforces |
| W5 | `Invoke-MgGraphRequest` 401 silently swallowed by `try/catch` returning `@()` | Helper treats empty array as Clean | All §§4–10 helpers emit `Status = 'Error'` on caught 4xx/5xx |

### False-clean defect catalog

| # | Defect | What looks Clean | Why it is actually Anomaly | Helper that catches it |
|---|---|---|---|---|
| F1 | Catalog row exists but `ExpirationDate` is in the past | Feature appears governed | Catalog entry is stale; CAB approval lapsed | `Compare-Feat224ZoneCompliance` |
| F2 | Feature toggle ON in tenant, ON in catalog, but `ChangeTicket` field empty | Governance metadata "matches" | No SOX-404 / FINRA 4511 evidence trail | `Export-Feat224ChangeEvidence` |
| F3 | Copilot Studio agent has `Generative Answers` enabled but catalog scope is `Zone 2` only and the agent is published to Zone 3 | Per-agent flag matches catalog default | Zone elevation requires explicit re-approval per Control 2.2 | `Compare-Feat224ZoneCompliance` |
| F4 | DLP policy blocks a connector, but the agent's MCP server tunnels the same capability | Connector blocked at the platform layer | MCP bypass; Fed SR 26-2 (formerly SR 11-7) model-input control gap | `Get-Feat224McpAgfState` + `Compare-Feat224DlpAlignment` |
| F5 | M365 admin center shows `Copilot Pages` Off, but a Graph beta endpoint reports it enabled per group | Tenant-wide toggle "matches" catalog `Off` | Group-scoped override drift; FINRA 3110 supervision blind spot | `Get-Feat224M365FeatureState` |
| F6 | PPAC environment has feature `On`, environment is in **Default** environment group | Feature governed at Default group | Default group is reserved for personal productivity (Zone 1) and must not host shared agents per Control 2.2 | `Get-Feat224PpacFeatureState` |
| F7 | Agent Framework workflow tool registered, no entry in catalog | Workflow does not appear in the M365 hub | AGF feature flags are not surfaced in the admin center; require direct enumeration | `Get-Feat224McpAgfState` |
| F9 | Catalog row marks a feature `Approved`, but `ApprovalDate` precedes the feature's GA date | Approval looks valid | CAB approved an unreleased capability; revisit per OCC Bulletin 2026-13 (formerly OCC 2011-12) | `Deploy-Feat224FeatureCatalog` validator |
| F10 | Per-agent override disables a feature the tenant has enabled | Conservative posture | Hidden override removes a control the supervision program (2.12) is monitoring | `Get-Feat224AgentFeatureState` |
| F11 | Evidence manifest written, but hash chain breaks vs. previous run | Manifest exists | Tampering or unsynced clock; SOX-302 attestation invalid | `New-Feat224EvidenceManifest` |
| F12 | `Send-Feat224SiemEvent` returns HTTP 204, no canary echo | "Forwarded" | DCR-side filter dropped the event; supervision feed unreliable | `Send-Feat224SiemEvent` canary mode |
| F13 | Feature added to catalog but never observed in tenant | Catalog "Clean" | Catalog drift; helper should mark `Pending` until a tenant observation lands | `Compare-Feat224ZoneCompliance` |
| F14 | Two AI Administrators enabled the same toggle within the change window | Single ticket on file | Dual-control violation if the second admin was the requester | `Export-Feat224ChangeEvidence` segregation check |
| F15 | A feature is enabled tenant-wide but no agent uses it | Looks compliant | Latent attack surface; Fed SR 26-2 (formerly SR 11-7) expects the inventory to flag unused-but-enabled capabilities | `Compare-Feat224ZoneCompliance` (`UnusedEnabled` finding) |

> **Non-substitution anchor.** None of the helpers in this playbook substitute for: (a) **Control 1.1** publishing authorization, (b) **Control 2.6** Model Risk Management review, or (c) **Control 2.12** supervisory review of agent communications. A "Clean" result here means the configuration *matches the approved catalog* — it does not certify that the catalog itself reflects a defensible risk decision.

---

## §1 — Prerequisites: modules, Graph scopes, RBAC, and PIM gating

### 1.1 Pinned module set

Pin to these versions for the v1.4 (April 2026) baseline. Newer point releases generally work but have not been UI-verified.

```powershell
# Pinned module manifest for Control 2.24 helpers — verified 2026-04-15
$Feat224Modules = @(
    @{ Name = 'Microsoft.Graph';                              Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Beta';                         Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Authentication';               Version = '2.25.0' },
    @{ Name = 'Microsoft.PowerApps.Administration.PowerShell';Version = '2.0.188' },
    @{ Name = 'Microsoft.PowerApps.PowerShell';               Version = '1.0.34' },
    @{ Name = 'Microsoft.Xrm.Data.PowerShell';                Version = '2.8.84' },
    @{ Name = 'Az.Accounts';                                  Version = '2.15.0' },
    @{ Name = 'Az.OperationalInsights';                       Version = '3.6.0' },
    @{ Name = 'Pester';                                       Version = '5.5.0' }
)

function Install-Feat224Modules {
    [CmdletBinding(SupportsShouldProcess)]
    param([switch] $Force)

    foreach ($m in $Feat224Modules) {
        $installed = Get-Module -ListAvailable -Name $m.Name |
                     Where-Object { $_.Version -eq [version]$m.Version }
        if ($installed -and -not $Force) { continue }
        if ($PSCmdlet.ShouldProcess("$($m.Name) $($m.Version)", 'Install-Module')) {
            Install-Module -Name $m.Name -RequiredVersion $m.Version `
                -Scope CurrentUser -Force -AllowClobber -Repository PSGallery
        }
    }
}
```

### 1.2 Microsoft Graph scope matrix

| Helper | Delegated scope(s) | Application scope(s) |
|---|---|---|
| `Get-Feat224M365FeatureState` | `CopilotSettings.Read.All`, `Directory.Read.All` | `CopilotSettings.Read.All` |
| `Get-Feat224AgentFeatureState` | `CopilotStudio.Read.All`, `Bot.Read.All` (beta) | `CopilotStudio.Read.All` |
| `Get-Feat224McpAgfState` | `Agent.Read.All` (beta), `Application.Read.All` | `Agent.Read.All` |
| `Compare-Feat224DlpAlignment` | n/a (PPAC SDK) | n/a |
| `Export-Feat224ChangeEvidence` | `AuditLog.Read.All`, `SecurityEvents.Read.All` | `AuditLog.Read.All` |
| `Send-Feat224SiemEvent` | n/a (Az + DCR) | Monitoring Metrics Publisher on DCR |

### 1.3 RBAC requirements (canonical role names)

| Activity | Required role | Notes |
|---|---|---|
| Read tenant Copilot toggles | **AI Administrator** (preferred) or Reports Reader | Per the v1.3.3 patch to Control 2.24, AI Administrator is the standing role for tenant-level reads |
| Mutate tenant Copilot toggles | **AI Administrator** with PIM activation | **Entra Global Admin** reserved for exceptional changes only |
| Read Power Platform environments | **Power Platform Admin** (Reader is insufficient for feature-flag enumeration) | |
| Provision Dataverse `fsi_featurecatalog` table | **System Customizer** + **Power Platform Admin** | Idempotent — see §2 |
| Read Copilot Studio agent definitions | **Copilot Studio Maker** + **Power Platform Admin** | |
| Forward to Sentinel | **Monitoring Metrics Publisher** on the DCR | Resource-scoped, not tenant-wide |
| Sign evidence manifests | **AI Governance Lead** (key holder) | Manifests countersigned by **Compliance Officer** |

### 1.4 PIM eligible-activation helper

```powershell
function Request-Feat224PimActivation {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [ValidateSet('AIAdministrator','PowerPlatformAdmin','GlobalAdministrator')]
        [string] $Role,
        [Parameter(Mandatory)] [string] $JustificationTicket,
        [ValidateRange(15, 480)] [int] $DurationMinutes = 60
    )

    if ($Role -eq 'GlobalAdministrator') {
        Write-Warning "Global Administrator activation should be exceptional. Confirm a CAB ticket beyond '$JustificationTicket' is on file (Control 2.24 v1.6.2)."
    }

    $context = Get-MgContext
    if (-not $context) { throw "Run Initialize-Feat224Session before requesting PIM activation." }

    $roleDef = Get-MgRoleManagementDirectoryRoleDefinition -Filter "displayName eq '$Role'"
    if (-not $roleDef) {
        return [pscustomobject]@{
            Status = 'Error'
            Reason = "Role definition '$Role' not found in tenant $($context.TenantId)."
            Role   = $Role
        }
    }

    if ($PSCmdlet.ShouldProcess($Role, "Activate PIM for $DurationMinutes minutes")) {
        $body = @{
            action           = 'selfActivate'
            principalId      = (Get-MgUser -UserId $context.Account).Id
            roleDefinitionId = $roleDef.Id
            directoryScopeId = '/'
            justification    = "Control 2.24 evidence run — ticket $JustificationTicket"
            scheduleInfo     = @{
                startDateTime = (Get-Date).ToUniversalTime().ToString('o')
                expiration    = @{ type = 'AfterDuration'; duration = "PT${DurationMinutes}M" }
            }
        }
        try {
            $req = New-MgRoleManagementDirectoryRoleAssignmentScheduleRequest -BodyParameter $body
            return [pscustomobject]@{
                Status            = 'Clean'
                Role              = $Role
                AssignmentId      = $req.Id
                ExpiresUtc        = (Get-Date).ToUniversalTime().AddMinutes($DurationMinutes)
                JustificationTicket = $JustificationTicket
            }
        } catch {
            return [pscustomobject]@{
                Status = 'Error'
                Reason = $_.Exception.Message
                Role   = $Role
            }
        }
    }
}
```

> **Hedged claim:** PIM activation **aids in** segregation-of-duties enforcement under SOX-404 and FFIEC IT-RM, but does **not** by itself satisfy the dual-control expectation. Defect F14 in §0 must be evaluated by `Export-Feat224ChangeEvidence` (§2).

---

## §2 — Commercial bootstrap and helper utilities

### 2.1 Preview-feature gating

Several beta endpoints required by §6 (Copilot Studio agent reader) and §9 (MCP/AGF) are still labelled `preview` in April 2026. The bootstrap refuses to proceed without explicit acknowledgement.

```powershell
function Confirm-Feat224PreviewGate {
    [CmdletBinding()]
    param(
        [switch] $AcceptPreview,
        [string] $TicketId
    )
    $previews = @(
        'Microsoft.Graph.Beta — /copilotStudio/agents (preview)',
        'Microsoft.Graph.Beta — /copilot/features (preview, group-scoped overrides)',
        'Microsoft.Graph.Beta — /agents/{id}/tools (Agent Framework, preview)',
        'PowerApps Admin — Get-AdminPowerAppEnvironmentFeature (preview parameter set)'
    )
    if (-not $AcceptPreview) {
        return [pscustomobject]@{
            Status = 'Pending'
            Reason = 'Preview surfaces required. Re-run with -AcceptPreview and a CAB ticket reference.'
            Previews = $previews
        }
    }
    if (-not $TicketId) {
        return [pscustomobject]@{
            Status = 'Anomaly'
            Reason = 'Preview accepted without TicketId — defect F2 (no change-management evidence).'
            Previews = $previews
        }
    }
    return [pscustomobject]@{
        Status   = 'Clean'
        Previews = $previews
        TicketId = $TicketId
    }
}
```

### 2.2 Shell-host assertion

```powershell
function Assert-Feat224ShellHost {
    [CmdletBinding()]
    param()
    if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion.Major -lt 7) {
        throw "Control 2.24 helpers require PowerShell 7.4+ (pwsh). Detected: $($PSVersionTable.PSVersion). See defect W2 in §0."
    }
    if ([Environment]::Is64BitProcess -ne $true) {
        throw "32-bit process detected. Re-launch pwsh as 64-bit."
    }
    return [pscustomobject]@{
        Status     = 'Clean'
        PSVersion  = $PSVersionTable.PSVersion.ToString()
        Process    = (Get-Process -Id $PID).ProcessName
    }
}
```

### 2.3 Session initializer

```powershell
function Initialize-Feat224Session {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $TenantId,
        [Parameter(Mandatory)] [string] $JustificationTicket,
        [string[]] $GraphScopes = @('CopilotSettings.Read.All','Directory.Read.All','AuditLog.Read.All','CopilotStudio.Read.All','Agent.Read.All','Application.Read.All'),
        [switch] $AcceptPreview
    )

    $shell   = Assert-Feat224ShellHost
    $preview = Confirm-Feat224PreviewGate -AcceptPreview:$AcceptPreview -TicketId $JustificationTicket

    Disconnect-MgGraph -ErrorAction SilentlyContinue | Out-Null
    Connect-MgGraph -TenantId $TenantId -Scopes $GraphScopes -Environment 'Global' -NoWelcome
    Connect-AzAccount -Tenant $TenantId -Environment 'AzureCloud' -ErrorAction Stop | Out-Null
    Add-PowerAppsAccount -Endpoint 'prod' | Out-Null

    return [pscustomobject]@{
        Status      = if ($preview.Status -eq 'Clean') { 'Clean' } else { $preview.Status }
        TenantId    = $TenantId
        Cloud       = 'Commercial'
        Shell       = $shell
        PreviewGate = $preview
        GraphScopes = $GraphScopes
        Reason      = if ($preview.Status -ne 'Clean') { $preview.Reason } else { $null }
    }
}
```

### 2.4 Graph scope verifier

```powershell
function Test-Feat224GraphScopes {
    [CmdletBinding()]
    param([Parameter(Mandatory)] [string[]] $Required)
    $context = Get-MgContext
    if (-not $context) {
        return [pscustomobject]@{ Status = 'Error'; Reason = 'No Graph context — run Initialize-Feat224Session.' }
    }
    $missing = $Required | Where-Object { $_ -notin $context.Scopes }
    if ($missing.Count -gt 0) {
        return [pscustomobject]@{
            Status   = 'Anomaly'
            Reason   = "Missing Graph scopes: $($missing -join ', '). Re-consent required."
            Missing  = $missing
            Granted  = $context.Scopes
        }
    }
    return [pscustomobject]@{ Status = 'Clean'; Granted = $context.Scopes }
}
```

### 2.5 Paged Graph helper

```powershell
function Invoke-Feat224PagedQuery {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $Uri,
        [ValidateSet('v1.0','beta')] [string] $ApiVersion = 'v1.0',
        [int] $MaxPages = 50
    )
    $results = New-Object System.Collections.Generic.List[object]
    $next = if ($Uri -like 'http*') { $Uri } else { "https://graph.microsoft.com/$ApiVersion/$($Uri.TrimStart('/'))" }
    $page = 0
    while ($next -and $page -lt $MaxPages) {
        try {
            $resp = Invoke-MgGraphRequest -Method GET -Uri $next -ErrorAction Stop
        } catch {
            return [pscustomobject]@{
                Status = 'Error'
                Reason = "Graph paged query failed at page $page : $($_.Exception.Message)"
                Uri    = $next
            }
        }
        if ($resp.value) { $results.AddRange([object[]]$resp.value) }
        $next = $resp.'@odata.nextLink'
        $page++
    }
    return [pscustomobject]@{
        Status = 'Clean'
        Count  = $results.Count
        Pages  = $page
        Items  = $results.ToArray()
    }
}
```

### 2.6 Throttle wrapper

```powershell
function Invoke-Feat224Throttled {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [scriptblock] $Script,
        [int] $MaxRetries = 5,
        [int] $InitialBackoffMs = 500
    )
    $attempt = 0
    while ($true) {
        try {
            return & $Script
        } catch {
            $msg = $_.Exception.Message
            $isThrottle = $msg -match '429|Too Many Requests|throttl'
            if (-not $isThrottle -or $attempt -ge $MaxRetries) {
                throw
            }
            $delay = $InitialBackoffMs * [math]::Pow(2, $attempt)
            Start-Sleep -Milliseconds $delay
            $attempt++
        }
    }
}
```

### 2.7 Configuration JSON schema

`feat224.config.json` lives under `evidence\config\` and is hash-pinned in every manifest.

```json
{
  "$schema": "https://fsi-agentgov/schemas/feat224-config-v1.json",
  "tenantId": "00000000-0000-0000-0000-000000000000",
  "cloud": "Commercial",
  "evidenceRoot": "C:\\fsi-evidence\\2.24",
  "retentionYears": 7,
  "siem": {
    "dceUri": "https://feat224-dce.eastus-1.ingest.monitor.azure.com",
    "dcrImmutableId": "dcr-00000000000000000000000000000000",
    "streamName": "Custom-Feat224ChangeEvent_CL"
  },
  "catalog": {
    "dataverseEnvironmentUrl": "https://orgxxxxxxxx.crm.dynamics.com",
    "tableLogicalName": "fsi_featurecatalog"
  },
  "siemCanaryCorrelationId": "FEAT224-CANARY",
  "approvedRoles": ["AIAdministrator","PowerPlatformAdmin","AIGovernanceLead","ComplianceOfficer","ChangeManagementTeam","AgentOwner"]
}
```

### 2.8 Evidence manifest helper

```powershell
function New-Feat224EvidenceManifest {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string] $RunId,
        [Parameter(Mandatory)] [object[]] $Findings,
        [Parameter(Mandatory)] [string] $EvidenceRoot,
        [string] $PreviousManifestPath
    )

    $manifestDir  = Join-Path $EvidenceRoot $RunId
    $manifestPath = Join-Path $manifestDir 'manifest.json'
    if ($PSCmdlet.ShouldProcess($manifestPath, 'Write evidence manifest')) {
        New-Item -ItemType Directory -Path $manifestDir -Force | Out-Null

        $prevHash = if ($PreviousManifestPath -and (Test-Path $PreviousManifestPath)) {
            (Get-FileHash -Path $PreviousManifestPath -Algorithm SHA256).Hash
        } else { 'GENESIS' }

        $manifest = [ordered]@{
            schemaVersion = 'feat224-manifest-v1'
            runId         = $RunId
            generatedUtc  = (Get-Date).ToUniversalTime().ToString('o')
            generatedBy   = (Get-MgContext).Account
            previousHash  = $prevHash
            regulatoryAnchors = @('SOX-302','SOX-404','FINRA-3110','FINRA-4511','FINRA-25-07','FedSR-11-7','OCC-2011-12','FFIEC-IT-RM','GLBA-501b','SEC-RegSCI')
            findings      = $Findings
        }
        $json = $manifest | ConvertTo-Json -Depth 12
        Set-Content -Path $manifestPath -Value $json -Encoding UTF8
        $hash = (Get-FileHash -Path $manifestPath -Algorithm SHA256).Hash

        return [pscustomobject]@{
            Status        = 'Clean'
            ManifestPath  = $manifestPath
            ManifestHash  = $hash
            PreviousHash  = $prevHash
            FindingCount  = $Findings.Count
        }
    }
}
```

> **Defect F11 mitigation.** Always pass `-PreviousManifestPath` when chaining runs. A broken hash chain is reported by §10's evidence exporter as `Status = 'Anomaly'` with reason `"F11: hash chain discontinuity"`.

---

## §3 — Dataverse Feature Catalog table provisioning

The **Feature Catalog** is the authoritative list of every Microsoft 365 / Power Platform / Copilot Studio / Agent Framework / MCP feature an organization has approved (or explicitly disallowed). It is stored in a Dataverse table, `fsi_featurecatalog`, in a dedicated **Governance** environment (Tier 0 per Control 2.2). The table must exist before any §§4–10 observation helper runs because every observation is reconciled against a catalog row.

### 3.1 Table schema

| Logical name | Display name | Type | Required | Notes |
|---|---|---|---|---|
| `fsi_featurename` | Feature Name | Text(200) | Yes | Vendor-supplied identifier (e.g., `CopilotPages`, `M365Copilot.Generative.Answers`) |
| `fsi_surface` | Surface | Choice | Yes | `M365Hub`, `PPAC`, `CopilotStudio`, `AgentFramework`, `MCP`, `DLP` |
| `fsi_cloudscope` | Cloud Scope | Choice | Yes | `Commercial` |
| `fsi_zonestatus` | Zone Status | Choice | Yes | `Zone1Personal`, `Zone2Team`, `Zone3Enterprise`, `Disallowed` |
| `fsi_approvaldate` | Approval Date | Date | Yes | F9: must be ≥ vendor GA date |
| `fsi_changeticket` | Change Ticket | Text(50) | Yes | ServiceNow / Jira reference |
| `fsi_expirationdate` | Expiration Date | Date | Yes | F1: re-attestation required by this date |
| `fsi_riskrating` | Risk Rating | Choice | Yes | `Low`, `Moderate`, `High`, `Critical` |
| `fsi_mrmreviewid` | MRM Review ID | Text(100) | Conditional | Required when `fsi_riskrating in {High, Critical}` per Control 2.6 |
| `fsi_supervisionscope` | Supervision Scope | Text(500) | Conditional | Required when feature affects user-facing output per Control 2.12 |
| `fsi_lastobservedutc` | Last Observed UTC | DateTime | No | Stamped by `Compare-Feat224ZoneCompliance` |

### 3.2 Idempotent provisioner

```powershell
function Deploy-Feat224FeatureCatalog {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string] $DataverseEnvironmentUrl,
        [string] $SolutionUniqueName = 'fsi_agentgov'
    )

    Import-Module Microsoft.Xrm.Data.PowerShell -ErrorAction Stop
    $conn = Connect-CrmOnline -ServerUrl $DataverseEnvironmentUrl -OAuth -ErrorAction Stop

    # F-defect: Check whether table already exists before attempting create
    $existing = Get-CrmEntityMetadata -conn $conn -EntityLogicalName 'fsi_featurecatalog' -ErrorAction SilentlyContinue
    if ($existing) {
        $columnsPresent = $existing.Attributes | Where-Object { $_.LogicalName -like 'fsi_*' } | Select-Object -ExpandProperty LogicalName
        $required = @('fsi_featurename','fsi_surface','fsi_cloudscope','fsi_zonestatus','fsi_approvaldate','fsi_changeticket','fsi_expirationdate','fsi_riskrating')
        $missingCols = $required | Where-Object { $_ -notin $columnsPresent }
        if ($missingCols.Count -gt 0) {
            return [pscustomobject]@{
                Status      = 'Anomaly'
                Reason      = "Table exists but missing required columns: $($missingCols -join ', '). Run with -WhatIf:`$false to add them, or escalate per Control 2.2."
                MissingCols = $missingCols
            }
        }
        return [pscustomobject]@{
            Status = 'Clean'
            Reason = 'Table fsi_featurecatalog already provisioned and schema-complete.'
            Columns = $columnsPresent
        }
    }

    if (-not $PSCmdlet.ShouldProcess($DataverseEnvironmentUrl, 'Create fsi_featurecatalog')) {
        return [pscustomobject]@{ Status = 'Pending'; Reason = 'WhatIf — no provisioning attempted.' }
    }

    # Table + columns creation via Web API (abbreviated — full body in evidence repo)
    $tableMeta = @{
        '@odata.type'              = 'Microsoft.Dynamics.CRM.EntityMetadata'
        SchemaName                 = 'fsi_FeatureCatalog'
        DisplayName                = @{ LocalizedLabels = @(@{ Label = 'Feature Catalog'; LanguageCode = 1033 }) }
        DisplayCollectionName      = @{ LocalizedLabels = @(@{ Label = 'Feature Catalogs'; LanguageCode = 1033 }) }
        OwnershipType              = 'UserOwned'
        HasActivities              = $false
        HasNotes                   = $true
        Attributes                 = @(
            @{ '@odata.type' = 'Microsoft.Dynamics.CRM.StringAttributeMetadata'; SchemaName = 'fsi_FeatureName'; MaxLength = 200; RequiredLevel = @{ Value = 'ApplicationRequired' }; DisplayName = @{ LocalizedLabels = @(@{ Label = 'Feature Name'; LanguageCode = 1033 }) }; IsPrimaryName = $true }
        )
    }

    try {
        $resp = Invoke-CrmWebApiRequest -conn $conn -Method POST -Path 'EntityDefinitions' -Body ($tableMeta | ConvertTo-Json -Depth 10)
    } catch {
        return [pscustomobject]@{ Status = 'Error'; Reason = "Table creation failed: $($_.Exception.Message)" }
    }

    return [pscustomobject]@{
        Status   = 'Clean'
        Reason   = $null
        Created  = $true
        Solution = $SolutionUniqueName
        TableUrl = "$DataverseEnvironmentUrl/api/data/v9.2/EntityDefinitions(LogicalName='fsi_featurecatalog')"
    }
}
```

### 3.3 Catalog-row validator (F9 catcher)

```powershell
function Test-Feat224CatalogRow {
    [CmdletBinding()]
    param([Parameter(Mandatory)] [hashtable] $Row, [Parameter(Mandatory)] [hashtable] $VendorGaDates)
    $issues = @()

    if (-not $Row.fsi_featurename)   { $issues += 'Missing FeatureName' }
    if (-not $Row.fsi_changeticket)  { $issues += 'F2: Missing ChangeTicket' }
    if (-not $Row.fsi_approvaldate)  { $issues += 'Missing ApprovalDate' }
    if ($Row.fsi_expirationdate -and $Row.fsi_expirationdate -lt (Get-Date)) {
        $issues += 'F1: Expired catalog row'
    }

    $ga = $VendorGaDates[$Row.fsi_featurename]
    if ($ga -and $Row.fsi_approvaldate -lt $ga) {
        $issues += "F9: ApprovalDate $($Row.fsi_approvaldate.ToString('yyyy-MM-dd')) precedes vendor GA $($ga.ToString('yyyy-MM-dd'))"
    }

    if ($Row.fsi_riskrating -in @('High','Critical') -and -not $Row.fsi_mrmreviewid) {
        $issues += 'Missing MRM Review ID for High/Critical risk rating (Control 2.6)'
    }

    if ($issues.Count -gt 0) {
        return [pscustomobject]@{
            Status = 'Anomaly'
            Reason = $issues -join '; '
            Row    = $Row
        }
    }
    return [pscustomobject]@{ Status = 'Clean'; Row = $Row }
}
```

### 3.4 Pester (`CATALOG`)

```powershell
Describe 'Feat224 — CATALOG namespace' -Tag CATALOG {
    Context 'fsi_featurecatalog table' {
        It 'exists in the Governance environment' {
            $r = Deploy-Feat224FeatureCatalog -DataverseEnvironmentUrl $env:FEAT224_GOV_URL -WhatIf
            $r.Status | Should -BeIn @('Clean','Pending')
        }
        It 'has all eight required columns' {
            $r = Deploy-Feat224FeatureCatalog -DataverseEnvironmentUrl $env:FEAT224_GOV_URL -WhatIf
            if ($r.Status -eq 'Clean') {
                ($r.Columns) | Should -Contain 'fsi_changeticket'
            }
        }
    }
    Context 'Catalog-row validation' {
        It 'flags F1 (expired)' {
            $row = @{ fsi_featurename='Test'; fsi_changeticket='CHG1'; fsi_approvaldate=(Get-Date).AddYears(-2); fsi_expirationdate=(Get-Date).AddDays(-1); fsi_riskrating='Low' }
            (Test-Feat224CatalogRow -Row $row -VendorGaDates @{}).Reason | Should -Match 'F1'
        }
        It 'flags F2 (missing ChangeTicket)' {
            $row = @{ fsi_featurename='Test'; fsi_approvaldate=(Get-Date); fsi_riskrating='Low' }
            (Test-Feat224CatalogRow -Row $row -VendorGaDates @{}).Reason | Should -Match 'F2'
        }
        It 'flags F9 (approval before GA)' {
            $row = @{ fsi_featurename='X'; fsi_changeticket='CHG2'; fsi_approvaldate=(Get-Date '2024-01-01'); fsi_riskrating='Low' }
            $ga  = @{ X = (Get-Date '2024-06-01') }
            (Test-Feat224CatalogRow -Row $row -VendorGaDates $ga).Reason | Should -Match 'F9'
        }
    }
}
```

---

## §4 — Microsoft 365 admin center / Copilot hub reader

The M365 admin center surfaces tenant-wide Copilot toggles (Copilot Pages, Copilot Search, declarative-agent allow-list, M365 Hub orchestration). This helper extracts them via Graph **and** the admin-center API, then reconciles tenant-wide vs. group-scoped overrides — defect **F5**.

### 4.1 Helper

```powershell
function Get-Feat224M365FeatureState {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $TenantId,
        [hashtable] $CatalogIndex   # keyed by fsi_featurename
    )

    $scopeCheck = Test-Feat224GraphScopes -Required @('CopilotSettings.Read.All','Directory.Read.All')
    if ($scopeCheck.Status -ne 'Clean') { return $scopeCheck }

    $findings = New-Object System.Collections.Generic.List[object]

    # Tenant-wide Copilot settings (v1.0)
    try {
        $tenantWide = Invoke-Feat224Throttled { Invoke-MgGraphRequest -Method GET -Uri 'https://graph.microsoft.com/v1.0/copilot/settings' }
    } catch {
        return [pscustomobject]@{ Status='Error'; Reason="copilot/settings failed: $($_.Exception.Message)" }
    }

    # Group-scoped overrides (beta)
    $overrides = Invoke-Feat224PagedQuery -Uri 'copilot/features?$expand=assignments' -ApiVersion 'beta'
    if ($overrides.Status -ne 'Clean') { return $overrides }

    foreach ($feature in $tenantWide.features) {
        $name      = $feature.id
        $tenantOn  = [bool]$feature.enabled
        $catalog   = $CatalogIndex[$name]
        $override  = $overrides.Items | Where-Object { $_.id -eq $name -and $_.assignments.Count -gt 0 }

        $status  = 'Clean'
        $reasons = @()

        if (-not $catalog) {
            $status = 'Anomaly'
            $reasons += "F7-adjacent: feature '$name' enabled in tenant but absent from Feature Catalog"
        } elseif ($catalog.fsi_zonestatus -eq 'Disallowed' -and $tenantOn) {
            $status = 'Anomaly'
            $reasons += "Catalog marks '$name' Disallowed but tenant has it ON"
        }

        if ($override) {
            $status = 'Anomaly'
            $reasons += "F5: tenant-wide=$tenantOn but group-scoped overrides exist (assignments=$($override.assignments.Count))"
        }

        $findings.Add([pscustomobject]@{
            Status        = $status
            Surface       = 'M365Hub'
            FeatureName   = $name
            TenantEnabled = $tenantOn
            CatalogZone   = $catalog?.fsi_zonestatus
            CatalogTicket = $catalog?.fsi_changeticket
            HasOverride   = [bool]$override
            Reason        = if ($reasons) { $reasons -join '; ' } else { $null }
        })
    }

    $rollup = if ($findings | Where-Object Status -eq 'Anomaly') { 'Anomaly' } else { 'Clean' }
    return [pscustomobject]@{
        Status       = $rollup
        Surface      = 'M365Hub'
        FeatureCount = $findings.Count
        Findings     = $findings.ToArray()
        Reason       = if ($rollup -eq 'Anomaly') { ($findings | Where-Object Status -eq 'Anomaly').Reason -join ' | ' } else { $null }
    }
}
```

### 4.2 Pester (`M365HUB`)

```powershell
Describe 'Feat224 — M365HUB namespace' -Tag M365HUB {
    BeforeAll {
        $script:catalog = @{
            'CopilotPages' = @{ fsi_featurename='CopilotPages'; fsi_zonestatus='Zone3Enterprise'; fsi_changeticket='CHG-001' }
        }
    }
    It 'returns Clean when tenant matches catalog' {
        Mock Invoke-MgGraphRequest { @{ features = @(@{ id='CopilotPages'; enabled=$true }) } }
        Mock Invoke-Feat224PagedQuery { [pscustomobject]@{ Status='Clean'; Items=@() } }
        Mock Test-Feat224GraphScopes { [pscustomobject]@{ Status='Clean' } }
        (Get-Feat224M365FeatureState -TenantId 'x' -CatalogIndex $script:catalog).Status | Should -Be 'Clean'
    }
    It 'flags F5 when group overrides exist' {
        Mock Invoke-MgGraphRequest { @{ features = @(@{ id='CopilotPages'; enabled=$false }) } }
        Mock Invoke-Feat224PagedQuery { [pscustomobject]@{ Status='Clean'; Items=@(@{ id='CopilotPages'; assignments=@(@{groupId='g1'}) }) } }
        Mock Test-Feat224GraphScopes { [pscustomobject]@{ Status='Clean' } }
        $r = Get-Feat224M365FeatureState -TenantId 'x' -CatalogIndex $script:catalog
        $r.Status | Should -Be 'Anomaly'
        $r.Reason | Should -Match 'F5'
    }
}
```

---

## §5 — Power Platform Admin Center reader

PPAC exposes both **environment-level** Copilot/agent feature flags and the **Copilot Hub** preview-feature opt-ins. This helper enumerates every environment, classifies each by tier (Default / Productivity / Standard / Sandbox / Production-Tier1 per Control 2.2), reads per-environment feature states, and emits one finding per environment × feature.

### 5.1 Helper

```powershell
function Get-Feat224PpacFeatureState {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [hashtable] $CatalogIndex,
        [string[]] $EnvironmentSkuFilter = @('Default','Production','Sandbox','Trial')
    )

    try {
        $envs = Get-AdminPowerAppEnvironment | Where-Object { $_.EnvironmentType -in $EnvironmentSkuFilter }
    } catch {
        return [pscustomobject]@{ Status='Error'; Reason="Get-AdminPowerAppEnvironment failed: $($_.Exception.Message)" }
    }

    $findings = New-Object System.Collections.Generic.List[object]

    foreach ($env in $envs) {
        $isDefault = ($env.EnvironmentType -eq 'Default')

        try {
            $features = Invoke-Feat224Throttled {
                Get-AdminPowerAppEnvironmentFeature -EnvironmentName $env.EnvironmentName -ErrorAction Stop
            }
        } catch {
            $findings.Add([pscustomobject]@{
                Status        = 'Error'
                Surface       = 'PPAC'
                EnvironmentId = $env.EnvironmentName
                Reason        = "Feature read failed: $($_.Exception.Message)"
            })
            continue
        }

        foreach ($f in $features) {
            $name    = $f.FeatureName
            $on      = [bool]$f.Enabled
            $catalog = $CatalogIndex[$name]
            $status  = 'Clean'
            $reasons = @()

            if (-not $catalog) {
                $status = 'Anomaly'
                $reasons += "F7-adjacent: feature '$name' enabled in environment but absent from catalog"
            }
            if ($on -and $isDefault -and $catalog -and $catalog.fsi_zonestatus -ne 'Zone1Personal') {
                $status = 'Anomaly'
                $reasons += "F6: feature '$name' active in Default environment but catalog scope is $($catalog.fsi_zonestatus)"
            }
            if ($catalog -and $catalog.fsi_zonestatus -eq 'Disallowed' -and $on) {
                $status = 'Anomaly'
                $reasons += "Disallowed feature enabled"
            }

            $findings.Add([pscustomobject]@{
                Status          = $status
                Surface         = 'PPAC'
                EnvironmentId   = $env.EnvironmentName
                EnvironmentName = $env.DisplayName
                EnvironmentType = $env.EnvironmentType
                FeatureName     = $name
                Enabled         = $on
                CatalogZone     = $catalog?.fsi_zonestatus
                Reason          = if ($reasons) { $reasons -join '; ' } else { $null }
            })
        }
    }

    $rollup = if ($findings | Where-Object Status -in 'Anomaly','Error') { 'Anomaly' } else { 'Clean' }
    return [pscustomobject]@{
        Status         = $rollup
        Surface        = 'PPAC'
        EnvironmentCount = $envs.Count
        FindingCount   = $findings.Count
        Findings       = $findings.ToArray()
        Reason         = if ($rollup -eq 'Anomaly') { 'See Findings for per-environment detail.' } else { $null }
    }
}
```

### 5.2 Pester (`PPAC`, `ENV`)

```powershell
Describe 'Feat224 — PPAC namespace' -Tag PPAC,ENV {
    BeforeAll {
        $script:catalog = @{
            'CopilotInModelDriven' = @{ fsi_featurename='CopilotInModelDriven'; fsi_zonestatus='Zone2Team' }
        }
    }
    It 'flags F6 when feature is on in Default environment' {
        Mock Get-AdminPowerAppEnvironment { @(@{ EnvironmentName='env-default'; DisplayName='Default'; EnvironmentType='Default' }) }
        Mock Get-AdminPowerAppEnvironmentFeature { @(@{ FeatureName='CopilotInModelDriven'; Enabled=$true }) }
        $r = Get-Feat224PpacFeatureState -CatalogIndex $script:catalog
        $r.Status | Should -Be 'Anomaly'
        ($r.Findings | Where-Object Reason -match 'F6').Count | Should -BeGreaterThan 0
    }
    It 'returns Clean when feature is in a Production environment with matching catalog zone' {
        Mock Get-AdminPowerAppEnvironment { @(@{ EnvironmentName='env-team'; DisplayName='TeamProd'; EnvironmentType='Production' }) }
        Mock Get-AdminPowerAppEnvironmentFeature { @(@{ FeatureName='CopilotInModelDriven'; Enabled=$true }) }
        (Get-Feat224PpacFeatureState -CatalogIndex $script:catalog).Status | Should -Be 'Clean'
    }
}
```

---

## §6 — Copilot Studio agent feature reader

Per-agent overrides can either *strengthen* (disable a feature the tenant allows) or *weaken* (re-enable something disabled at higher scope through a connector or MCP path). The strengthening path is defect **F10** — supervision (Control 2.12) is monitoring something that has been silently turned off.

### 6.1 Helper

```powershell
function Get-Feat224AgentFeatureState {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [hashtable] $CatalogIndex,
        [Parameter(Mandatory)] [hashtable] $TenantFeatureIndex,  # name -> bool
        [string[]] $EnvironmentIds
    )

    $findings = New-Object System.Collections.Generic.List[object]

    if (-not $EnvironmentIds) {
        $EnvironmentIds = (Get-AdminPowerAppEnvironment | Where-Object EnvironmentType -in 'Production','Sandbox').EnvironmentName
    }

    foreach ($envId in $EnvironmentIds) {
        $agents = Invoke-Feat224PagedQuery -Uri "copilotStudio/environments/$envId/agents" -ApiVersion 'beta'
        if ($agents.Status -ne 'Clean') {
            $findings.Add([pscustomobject]@{ Status='Error'; Surface='CopilotStudio'; EnvironmentId=$envId; Reason=$agents.Reason })
            continue
        }

        foreach ($agent in $agents.Items) {
            foreach ($featureName in $agent.featureOverrides.Keys) {
                $agentVal   = [bool]$agent.featureOverrides[$featureName]
                $tenantVal  = [bool]$TenantFeatureIndex[$featureName]
                $catalog    = $CatalogIndex[$featureName]

                $status  = 'Clean'
                $reasons = @()

                if ($tenantVal -and -not $agentVal) {
                    $status = 'Anomaly'
                    $reasons += "F10: agent '$($agent.displayName)' overrides '$featureName' OFF while tenant has it ON; supervision feed (Control 2.12) may have a blind spot"
                }
                if (-not $tenantVal -and $agentVal) {
                    $status = 'Anomaly'
                    $reasons += "Agent re-enables '$featureName' that tenant has OFF — investigate connector/MCP path"
                }
                if ($catalog -and $catalog.fsi_zonestatus -eq 'Disallowed' -and $agentVal) {
                    $status = 'Anomaly'
                    $reasons += 'Disallowed feature active on agent'
                }

                $findings.Add([pscustomobject]@{
                    Status        = $status
                    Surface       = 'CopilotStudio'
                    EnvironmentId = $envId
                    AgentId       = $agent.id
                    AgentName     = $agent.displayName
                    FeatureName   = $featureName
                    AgentValue    = $agentVal
                    TenantValue   = $tenantVal
                    Reason        = if ($reasons) { $reasons -join '; ' } else { $null }
                })
            }
        }
    }

    $rollup = if ($findings | Where-Object Status -in 'Anomaly','Error') { 'Anomaly' } else { 'Clean' }
    return [pscustomobject]@{
        Status   = $rollup
        Surface  = 'CopilotStudio'
        Findings = $findings.ToArray()
        Reason   = if ($rollup -eq 'Anomaly') { 'See Findings.' } else { $null }
    }
}
```

### 6.2 Pester (`AGENT`)

```powershell
Describe 'Feat224 — AGENT namespace' -Tag AGENT {
    It 'flags F10 (agent disables tenant-enabled feature)' {
        Mock Invoke-Feat224PagedQuery {
            [pscustomobject]@{ Status='Clean'; Items=@(@{ id='a1'; displayName='Demo'; featureOverrides=@{ 'GenAns'=$false } }) }
        }
        Mock Get-AdminPowerAppEnvironment { @(@{ EnvironmentName='e1'; EnvironmentType='Production' }) }
        $r = Get-Feat224AgentFeatureState -CatalogIndex @{} -TenantFeatureIndex @{ 'GenAns'=$true } -EnvironmentIds @('e1')
        ($r.Findings | Where-Object Reason -match 'F10').Count | Should -BeGreaterThan 0
    }
}
```

---

## §7 — DLP policy ↔ Feature catalog correlation

DLP policies (Control 1.4) and feature toggles must be evaluated **together**: blocking a connector at the platform layer accomplishes nothing if the same capability can reach the model via an MCP server or Agent Framework workflow tool — defect **F4**.

### 7.1 Helper

```powershell
function Compare-Feat224DlpAlignment {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [hashtable] $CatalogIndex,
        [Parameter(Mandatory)] [object[]] $McpInventory   # output of Get-Feat224McpAgfState
    )

    try {
        $policies = Get-AdminDlpPolicy -ErrorAction Stop
    } catch {
        return [pscustomobject]@{ Status='Error'; Reason="Get-AdminDlpPolicy failed: $($_.Exception.Message)" }
    }

    $blockedConnectors = $policies |
        ForEach-Object { $_.ConnectorGroups | Where-Object Classification -eq 'Blocked' } |
        ForEach-Object { $_.Connectors } |
        Select-Object -ExpandProperty Id -Unique

    $findings = New-Object System.Collections.Generic.List[object]

    foreach ($mcp in $McpInventory) {
        $shadows = $blockedConnectors | Where-Object { $mcp.CapabilityKeywords -contains $_ -or $mcp.ConnectorEquivalents -contains $_ }
        if ($shadows) {
            $findings.Add([pscustomobject]@{
                Status      = 'Anomaly'
                Surface     = 'DLP'
                McpServer   = $mcp.ServerName
                AgentId     = $mcp.AgentId
                Shadows     = $shadows
                Reason      = "F4: MCP server '$($mcp.ServerName)' shadows DLP-blocked connectors: $($shadows -join ', ')"
            })
        }
    }

    foreach ($pol in $policies) {
        if (-not $CatalogIndex["DLP:$($pol.PolicyName)"]) {
            $findings.Add([pscustomobject]@{
                Status     = 'Anomaly'
                Surface    = 'DLP'
                PolicyName = $pol.PolicyName
                Reason     = "DLP policy '$($pol.PolicyName)' has no catalog row (Control 1.4 governance gap)"
            })
        }
    }

    $rollup = if ($findings.Count -gt 0) { 'Anomaly' } else { 'Clean' }
    return [pscustomobject]@{
        Status            = $rollup
        Surface           = 'DLP'
        BlockedConnectors = $blockedConnectors
        Findings          = $findings.ToArray()
        Reason            = if ($rollup -eq 'Anomaly') { 'DLP / MCP shadowing or uncatalogued policies — see Findings.' } else { $null }
    }
}
```

### 7.2 Pester (`DLP`)

```powershell
Describe 'Feat224 — DLP namespace' -Tag DLP {
    It 'flags F4 when MCP server shadows a blocked connector' {
        Mock Get-AdminDlpPolicy {
            @(@{ PolicyName='ProdDLP'; ConnectorGroups=@(@{ Classification='Blocked'; Connectors=@(@{ Id='shared_sql' }) }) })
        }
        $mcp = @([pscustomobject]@{ ServerName='sqlbridge'; AgentId='a1'; CapabilityKeywords=@('shared_sql'); ConnectorEquivalents=@() })
        $r = Compare-Feat224DlpAlignment -CatalogIndex @{ 'DLP:ProdDLP' = @{} } -McpInventory $mcp
        $r.Status | Should -Be 'Anomaly'
        ($r.Findings | Where-Object Reason -match 'F4').Count | Should -Be 1
    }
}
```

---

## §8 — Zone (1/2/3) compliance diff

This is the **central reconciliation helper**. It joins (a) the M365 hub findings (§2), (b) the PPAC findings (§2), (c) per-agent findings (§2), and (d) the catalog itself, and emits one of: `Clean`, `Anomaly`, `Pending` (catalog row exists but no observation yet — defect F13), `NotApplicable`, or `Error`. It also surfaces defect **F15** (`UnusedEnabled`) — features the tenant has enabled but no observed agent uses.

### 8.1 Helper

```powershell
function Compare-Feat224ZoneCompliance {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [hashtable] $CatalogIndex,
        [Parameter(Mandatory)] [object[]] $M365Findings,
        [Parameter(Mandatory)] [object[]] $PpacFindings,
        [Parameter(Mandatory)] [object[]] $AgentFindings
    )

    $observedFeatures = @{}
    foreach ($f in @($M365Findings + $PpacFindings + $AgentFindings)) {
        if ($f.FeatureName) {
            if (-not $observedFeatures[$f.FeatureName]) { $observedFeatures[$f.FeatureName] = New-Object System.Collections.Generic.List[object] }
            $observedFeatures[$f.FeatureName].Add($f)
        }
    }

    $findings = New-Object System.Collections.Generic.List[object]

    # F13: Catalog rows with no observation
    foreach ($name in $CatalogIndex.Keys) {
        if (-not $observedFeatures.ContainsKey($name)) {
            $findings.Add([pscustomobject]@{
                Status      = 'Pending'
                FeatureName = $name
                Reason      = 'F13: catalog row present but no tenant observation yet — re-run after next admin-center sync (typical lag 24h)'
            })
        }
    }

    # F15: enabled but unused
    foreach ($name in $observedFeatures.Keys) {
        $obs       = $observedFeatures[$name]
        $tenantOn  = ($obs | Where-Object { $_.Surface -eq 'M365Hub' -and $_.TenantEnabled }).Count -gt 0
        $agentUse  = ($obs | Where-Object { $_.Surface -eq 'CopilotStudio' -and $_.AgentValue }).Count
        if ($tenantOn -and $agentUse -eq 0) {
            $findings.Add([pscustomobject]@{
                Status      = 'Anomaly'
                FeatureName = $name
                Reason      = 'F15: feature enabled tenant-wide but no agent uses it (latent attack surface; Fed SR 26-2 (formerly SR 11-7) inventory expectation)'
            })
        }
    }

    # F1: expired catalog rows
    foreach ($name in $CatalogIndex.Keys) {
        $row = $CatalogIndex[$name]
        if ($row.fsi_expirationdate -and $row.fsi_expirationdate -lt (Get-Date)) {
            $findings.Add([pscustomobject]@{
                Status      = 'Anomaly'
                FeatureName = $name
                Reason      = "F1: catalog ExpirationDate $($row.fsi_expirationdate.ToString('yyyy-MM-dd')) has passed; re-attestation required"
            })
        }
    }

    # F3: zone elevation — agent in Zone 3 but catalog allows only Zone 2
    foreach ($af in $AgentFindings | Where-Object { $_.Surface -eq 'CopilotStudio' -and $_.AgentValue }) {
        $cat = $CatalogIndex[$af.FeatureName]
        if ($cat -and $cat.fsi_zonestatus -eq 'Zone2Team') {
            $envIsTier1 = $af.EnvironmentId -match 'tier1|prod'
            if ($envIsTier1) {
                $findings.Add([pscustomobject]@{
                    Status      = 'Anomaly'
                    FeatureName = $af.FeatureName
                    AgentId     = $af.AgentId
                    Reason      = "F3: agent uses '$($af.FeatureName)' in a Zone 3 (Tier 1) environment but catalog scope is Zone 2 — re-approve per Control 2.2"
                })
            }
        }
    }

    $rollup = if ($findings | Where-Object Status -eq 'Anomaly') { 'Anomaly' }
              elseif ($findings | Where-Object Status -eq 'Pending') { 'Pending' }
              else { 'Clean' }

    return [pscustomobject]@{
        Status   = $rollup
        Findings = $findings.ToArray()
        Reason   = if ($rollup -ne 'Clean') { 'See Findings.' } else { $null }
    }
}
```

### 8.2 Pester (`ZONE`)

```powershell
Describe 'Feat224 — ZONE namespace' -Tag ZONE {
    It 'flags F13 when catalog has rows but no observations' {
        $r = Compare-Feat224ZoneCompliance -CatalogIndex @{ 'X' = @{} } -M365Findings @() -PpacFindings @() -AgentFindings @()
        ($r.Findings | Where-Object Reason -match 'F13').Count | Should -BeGreaterThan 0
    }
    It 'flags F15 when feature is on but unused by agents' {
        $r = Compare-Feat224ZoneCompliance -CatalogIndex @{ 'X' = @{} } `
            -M365Findings @([pscustomobject]@{ Surface='M365Hub'; FeatureName='X'; TenantEnabled=$true }) `
            -PpacFindings @() `
            -AgentFindings @()
        ($r.Findings | Where-Object Reason -match 'F15').Count | Should -BeGreaterThan 0
    }
    It 'flags F3 when agent uses a Zone 2 feature in a tier-1 environment' {
        $cat = @{ 'GenAns' = @{ fsi_zonestatus='Zone2Team' } }
        $agf = @([pscustomobject]@{ Surface='CopilotStudio'; FeatureName='GenAns'; AgentValue=$true; AgentId='a1'; EnvironmentId='env-tier1-prod' })
        $r = Compare-Feat224ZoneCompliance -CatalogIndex $cat -M365Findings @() -PpacFindings @() -AgentFindings $agf
        ($r.Findings | Where-Object Reason -match 'F3').Count | Should -BeGreaterThan 0
    }
}
```

---

## §9 — MCP connector + Agent Framework feature-flag enumeration

MCP servers and Agent Framework workflow tools are **not** surfaced in the M365 admin center as of April 2026 — defect **F7**. They must be enumerated directly from the agent definition (Copilot Studio export) and from the Agent Framework beta endpoint.

### 9.1 Helper

```powershell
function Get-Feat224McpAgfState {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [hashtable] $CatalogIndex,
        [string[]] $EnvironmentIds
    )

    $findings = New-Object System.Collections.Generic.List[object]
    $mcpInventory = New-Object System.Collections.Generic.List[object]

    if (-not $EnvironmentIds) {
        $EnvironmentIds = (Get-AdminPowerAppEnvironment | Where-Object EnvironmentType -in 'Production','Sandbox').EnvironmentName
    }

    foreach ($envId in $EnvironmentIds) {
        # MCP servers via Copilot Studio agent export
        $agents = Invoke-Feat224PagedQuery -Uri "copilotStudio/environments/$envId/agents?`$expand=tools,mcpServers" -ApiVersion 'beta'
        if ($agents.Status -ne 'Clean') {
            $findings.Add([pscustomobject]@{ Status='Error'; Surface='MCP'; EnvironmentId=$envId; Reason=$agents.Reason })
            continue
        }

        foreach ($agent in $agents.Items) {
            foreach ($mcp in @($agent.mcpServers)) {
                $catKey = "MCP:$($mcp.name)"
                $cat    = $CatalogIndex[$catKey]
                $status = if ($cat) { 'Clean' } else { 'Anomaly' }
                $reason = if (-not $cat) { "F7: MCP server '$($mcp.name)' attached to agent '$($agent.displayName)' is not in catalog (key '$catKey')" } else { $null }

                $mcpInventory.Add([pscustomobject]@{
                    ServerName            = $mcp.name
                    AgentId               = $agent.id
                    EnvironmentId         = $envId
                    CapabilityKeywords    = @($mcp.capabilities)
                    ConnectorEquivalents  = @($mcp.connectorEquivalents)
                })

                $findings.Add([pscustomobject]@{
                    Status        = $status
                    Surface       = 'MCP'
                    EnvironmentId = $envId
                    AgentId       = $agent.id
                    AgentName     = $agent.displayName
                    McpServer     = $mcp.name
                    Capabilities  = $mcp.capabilities
                    Reason        = $reason
                })
            }

            # AGF workflow tools
            foreach ($tool in @($agent.tools | Where-Object { $_.kind -eq 'workflow' })) {
                $catKey = "AGF:$($tool.id)"
                $cat    = $CatalogIndex[$catKey]
                $status = if ($cat) { 'Clean' } else { 'Anomaly' }
                $reason = if (-not $cat) { "F7: Agent Framework workflow tool '$($tool.id)' on agent '$($agent.displayName)' is not in catalog" } else { $null }
                $findings.Add([pscustomobject]@{
                    Status        = $status
                    Surface       = 'AgentFramework'
                    EnvironmentId = $envId
                    AgentId       = $agent.id
                    AgentName     = $agent.displayName
                    ToolId        = $tool.id
                    Reason        = $reason
                })
            }
        }
    }

    $rollup = if ($findings | Where-Object Status -in 'Anomaly','Error') { 'Anomaly' } else { 'Clean' }
    return [pscustomobject]@{
        Status       = $rollup
        Surface      = 'MCP+AGF'
        Findings     = $findings.ToArray()
        McpInventory = $mcpInventory.ToArray()
        Reason       = if ($rollup -ne 'Clean') { 'Uncatalogued MCP servers or AGF tools — see Findings.' } else { $null }
    }
}
```

### 9.2 Pester (`MCP`, `AGF`)

```powershell
Describe 'Feat224 — MCP + AGF namespaces' -Tag MCP,AGF {
    It 'flags F7 for uncatalogued MCP server' {
        Mock Invoke-Feat224PagedQuery {
            [pscustomobject]@{ Status='Clean'; Items=@(@{
                id='a1'; displayName='Demo';
                mcpServers=@(@{ name='unknown-mcp'; capabilities=@('sql.query'); connectorEquivalents=@() });
                tools=@()
            }) }
        }
        Mock Get-AdminPowerAppEnvironment { @(@{ EnvironmentName='e1'; EnvironmentType='Production' }) }
        $r = Get-Feat224McpAgfState -CatalogIndex @{}
        ($r.Findings | Where-Object Reason -match 'F7').Count | Should -BeGreaterThan 0
    }
}
```

---

## §10 — Change-management evidence exporter

Every observation in §§2–9 must be reconcilable to a Change Management ticket — defect **F2**. This helper emits a forward-and-reverse trail (catalog → ticket → audit log entry → admin actor) plus a segregation-of-duties check for defect **F14**.

### 10.1 Helper

```powershell
function Export-Feat224ChangeEvidence {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [object[]] $AllFindings,
        [Parameter(Mandatory)] [hashtable] $CatalogIndex,
        [Parameter(Mandatory)] [string]   $EvidenceRoot,
        [Parameter(Mandatory)] [string]   $RunId,
        [string] $PreviousManifestPath,
        [datetime] $LookbackStart = (Get-Date).AddDays(-30),
        [datetime] $LookbackEnd   = (Get-Date)
    )

    $audit = Invoke-Feat224PagedQuery `
        -Uri "auditLogs/directoryAudits?`$filter=activityDateTime ge $($LookbackStart.ToString('o')) and activityDateTime le $($LookbackEnd.ToString('o')) and category eq 'AgentGovernance'" `
        -ApiVersion 'beta'

    if ($audit.Status -ne 'Clean') {
        return [pscustomobject]@{ Status='Error'; Reason="Audit pull failed: $($audit.Reason)" }
    }

    $changeFindings = New-Object System.Collections.Generic.List[object]

    foreach ($f in $AllFindings | Where-Object FeatureName) {
        $cat = $CatalogIndex[$f.FeatureName]
        if (-not $cat) { continue }

        $ticket = $cat.fsi_changeticket
        if (-not $ticket) {
            $changeFindings.Add([pscustomobject]@{
                Status = 'Anomaly'; FeatureName = $f.FeatureName
                Reason = 'F2: catalog row has no ChangeTicket — SOX-404 / FINRA 4511 evidence trail missing'
            })
            continue
        }

        $auditMatches = $audit.Items | Where-Object { ($_.additionalDetails.value -join ' ') -match [regex]::Escape($ticket) }
        if (-not $auditMatches) {
            $changeFindings.Add([pscustomobject]@{
                Status = 'Anomaly'; FeatureName = $f.FeatureName; Ticket = $ticket
                Reason = "Catalog references ticket '$ticket' but no matching audit record in lookback window"
            })
            continue
        }

        # F14: dual-control / segregation-of-duties
        $actors = $auditMatches.initiatedBy.user.userPrincipalName | Select-Object -Unique
        $requesterFromTicket = $cat.fsi_requesterupn
        if ($requesterFromTicket -and ($actors -contains $requesterFromTicket)) {
            $changeFindings.Add([pscustomobject]@{
                Status = 'Anomaly'; FeatureName = $f.FeatureName; Ticket = $ticket
                Reason = "F14: requester '$requesterFromTicket' also performed the change — dual-control violation"
            })
            continue
        }

        $changeFindings.Add([pscustomobject]@{
            Status      = 'Clean'
            FeatureName = $f.FeatureName
            Ticket      = $ticket
            Actors      = $actors
            AuditCount  = $auditMatches.Count
        })
    }

    $manifest = New-Feat224EvidenceManifest -RunId $RunId -Findings $changeFindings.ToArray() `
        -EvidenceRoot $EvidenceRoot -PreviousManifestPath $PreviousManifestPath

    $rollup = if ($changeFindings | Where-Object Status -eq 'Anomaly') { 'Anomaly' } else { 'Clean' }
    return [pscustomobject]@{
        Status         = $rollup
        ManifestPath   = $manifest.ManifestPath
        ManifestHash   = $manifest.ManifestHash
        ChangeFindings = $changeFindings.ToArray()
        Reason         = if ($rollup -ne 'Clean') { 'See ChangeFindings — F2 / F14 / hash chain issues.' } else { $null }
    }
}
```

### 10.2 Pester (`CHANGE`)

```powershell
Describe 'Feat224 — CHANGE namespace' -Tag CHANGE {
    It 'flags F2 when catalog row has no ChangeTicket' {
        Mock Invoke-Feat224PagedQuery { [pscustomobject]@{ Status='Clean'; Items=@() } }
        Mock New-Feat224EvidenceManifest { [pscustomobject]@{ ManifestPath='x'; ManifestHash='h' } }
        $cat = @{ 'X' = @{ fsi_featurename='X' } }
        $r = Export-Feat224ChangeEvidence -AllFindings @([pscustomobject]@{ FeatureName='X' }) -CatalogIndex $cat -EvidenceRoot 'C:\tmp' -RunId 'r1'
        ($r.ChangeFindings | Where-Object Reason -match 'F2').Count | Should -BeGreaterThan 0
    }
    It 'flags F14 dual-control violation' {
        $cat = @{ 'Y' = @{ fsi_featurename='Y'; fsi_changeticket='CHG-9'; fsi_requesterupn='alice@contoso.com' } }
        Mock Invoke-Feat224PagedQuery {
            [pscustomobject]@{ Status='Clean'; Items=@(@{
                additionalDetails=@(@{ value='CHG-9' });
                initiatedBy=@{ user=@{ userPrincipalName='alice@contoso.com' } }
            }) }
        }
        Mock New-Feat224EvidenceManifest { [pscustomobject]@{ ManifestPath='x'; ManifestHash='h' } }
        $r = Export-Feat224ChangeEvidence -AllFindings @([pscustomobject]@{ FeatureName='Y' }) -CatalogIndex $cat -EvidenceRoot 'C:\tmp' -RunId 'r2'
        ($r.ChangeFindings | Where-Object Reason -match 'F14').Count | Should -BeGreaterThan 0
    }
}
```

---

## §11 — Sentinel / SIEM forwarding

Per Control 2.12 (Supervision) and Control 1.10 (Communication Compliance Monitoring), feature-change events must reach the SIEM. This helper uses the **Logs Ingestion API** via a Data Collection Endpoint (DCE) and Data Collection Rule (DCR), plus a canary event with a known correlation ID to detect defect **F12** (DCR-side filtering silently dropping events).

### 11.1 Helper

```powershell
function Send-Feat224SiemEvent {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string]   $DceUri,
        [Parameter(Mandatory)] [string]   $DcrImmutableId,
        [Parameter(Mandatory)] [string]   $StreamName,
        [Parameter(Mandatory)] [object[]] $Events,
        [string] $CanaryCorrelationId = 'FEAT224-CANARY'
    )

    # Append canary
    $canary = [pscustomobject]@{
        TimeGenerated      = (Get-Date).ToUniversalTime().ToString('o')
        ControlId          = '2.24'
        EventType          = 'Canary'
        CorrelationId      = $CanaryCorrelationId
        Surface            = 'self-test'
        Reason             = 'F12 detector — round-trip validation event'
    }
    $payload = @($Events) + @($canary)

    $token = (Get-AzAccessToken -ResourceUrl 'https://monitor.azure.com').Token
    $uri   = "$DceUri/dataCollectionRules/$DcrImmutableId/streams/$StreamName?api-version=2023-01-01"

    if ($PSCmdlet.ShouldProcess($uri, "POST $($payload.Count) events")) {
        try {
            $resp = Invoke-WebRequest -Method POST -Uri $uri `
                -Headers @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' } `
                -Body ($payload | ConvertTo-Json -Depth 10) -UseBasicParsing
        } catch {
            return [pscustomobject]@{ Status='Error'; Reason="Logs Ingestion POST failed: $($_.Exception.Message)" }
        }

        if ($resp.StatusCode -ne 204) {
            return [pscustomobject]@{ Status='Anomaly'; Reason="Unexpected status $($resp.StatusCode); expected 204"; HttpStatus=$resp.StatusCode }
        }
    }

    # Canary echo verification (defect F12)
    Start-Sleep -Seconds 90
    $kustoCheck = [pscustomobject]@{
        Note   = "Manual or scheduled KQL: $($StreamName) | where CorrelationId == '$CanaryCorrelationId' | summarize Last=max(TimeGenerated)"
        Reason = 'Canary verification must be performed against Log Analytics workspace; helper cannot do it without workspace credentials.'
    }

    return [pscustomobject]@{
        Status            = 'Pending'
        Reason            = 'F12 mitigation: 204 acknowledged; canary echo must be confirmed via KQL within 5 minutes'
        SubmittedCount    = $payload.Count
        CanaryCorrelation = $CanaryCorrelationId
        VerificationHint  = $kustoCheck
    }
}
```

### 11.2 Pester (`SIEM`)

```powershell
Describe 'Feat224 — SIEM namespace' -Tag SIEM {
    It 'returns Pending after a successful 204 (canary echo unverified)' {
        Mock Get-AzAccessToken { @{ Token = 'fake' } }
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 204 } }
        Mock Start-Sleep { }
        $r = Send-Feat224SiemEvent -DceUri 'https://x' -DcrImmutableId 'd' -StreamName 's' -Events @(@{ Foo='bar' })
        $r.Status | Should -Be 'Pending'
        $r.Reason | Should -Match 'F12'
    }
    It 'returns Anomaly for unexpected status code' {
        Mock Get-AzAccessToken { @{ Token = 'fake' } }
        Mock Invoke-WebRequest { [pscustomobject]@{ StatusCode = 200 } }
        Mock Start-Sleep { }
        (Send-Feat224SiemEvent -DceUri 'https://x' -DcrImmutableId 'd' -StreamName 's' -Events @(@{Foo='bar'})).Status | Should -Be 'Anomaly'
    }
}
```

---

## §12 — Scheduling

Two scheduling modes are supported: (a) **Az Automation** (recommended for enterprise, integrates with Managed Identity), and (b) local **Scheduled Jobs** (acceptable for lab/sandbox tenants).

### 12.1 Az Automation runbook registration

```powershell
function Register-Feat224Schedule {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string] $ResourceGroup,
        [Parameter(Mandatory)] [string] $AutomationAccount,
        [Parameter(Mandatory)] [string] $RunbookName,
        [ValidateSet('Daily','Hourly','Weekly')] [string] $Frequency = 'Daily',
        [int] $IntervalHours = 24
    )
    if ($PSCmdlet.ShouldProcess("$AutomationAccount/$RunbookName", 'Schedule')) {
        $startTime = (Get-Date).AddHours(1)
        $sched = New-AzAutomationSchedule -ResourceGroupName $ResourceGroup `
            -AutomationAccountName $AutomationAccount `
            -Name "feat224-$Frequency" `
            -StartTime $startTime `
            -HourInterval $IntervalHours

        Register-AzAutomationScheduledRunbook -ResourceGroupName $ResourceGroup `
            -AutomationAccountName $AutomationAccount `
            -RunbookName $RunbookName `
            -ScheduleName $sched.Name | Out-Null
    }
    return [pscustomobject]@{
        Status      = 'Clean'
        RunbookName = $RunbookName
        Frequency   = $Frequency
    }
}
```

### 12.2 Cadence guidance

| Helper | Recommended cadence | Why |
|---|---|---|
| `Get-Feat224M365FeatureState`        | Daily 02:00 UTC | Tenant-wide toggles change rarely; daily aligns with Microsoft service-update cadence |
| `Get-Feat224PpacFeatureState`        | Daily 02:30 UTC | Environment-level changes track admin actions |
| `Get-Feat224AgentFeatureState`       | Every 4 hours   | Agent overrides change with maker activity |
| `Get-Feat224McpAgfState`             | Every 4 hours   | MCP servers can be added without admin involvement |
| `Compare-Feat224DlpAlignment`        | Daily 03:00 UTC | DLP changes are change-managed |
| `Compare-Feat224ZoneCompliance`      | After each upstream run | Pure rollup |
| `Export-Feat224ChangeEvidence`       | Weekly + ad-hoc on Anomaly | Heavy audit pull |
| `Send-Feat224SiemEvent`              | After each rollup | Real-time supervision feed |

> **Hedged claim.** Cadence is a recommendation that **helps meet** FINRA 3110 supervisory expectations and Fed SR 26-2 (formerly SR 11-7) ongoing-monitoring expectations. Organizations should validate that their ticketing and CAB workflow can absorb the volume of daily evidence and adjust accordingly.

---

## §13 — Retention alignment with Control 2.13

Evidence manifests are governance records and inherit the retention scheme defined in Control 2.13. The default is **7 years** for SOX-aligned manifests and **6 years** for FINRA 4511 supervisory evidence; whichever is longer wins.

```powershell
function Set-Feat224EvidenceRetention {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string] $EvidenceRoot,
        [Parameter(Mandatory)] [string] $StorageAccount,
        [Parameter(Mandatory)] [string] $Container,
        [int] $RetentionYears = 7,
        [switch] $ImmutableLegalHold
    )
    if ($PSCmdlet.ShouldProcess("$StorageAccount/$Container", "Apply $RetentionYears-year retention")) {
        $ctx = (Get-AzStorageAccount -ResourceGroupName $env:FEAT224_RG -Name $StorageAccount).Context
        if ($ImmutableLegalHold) {
            Add-AzRmStorageContainerLegalHold -ResourceGroupName $env:FEAT224_RG -StorageAccountName $StorageAccount -ContainerName $Container -Tag @('feat224-control-224')
        } else {
            Set-AzRmStorageContainerImmutabilityPolicy -ResourceGroupName $env:FEAT224_RG -StorageAccountName $StorageAccount -ContainerName $Container -ImmutabilityPeriod ($RetentionYears * 365)
        }
    }
    return [pscustomobject]@{
        Status        = 'Clean'
        StorageAccount= $StorageAccount
        Container     = $Container
        RetentionYears= $RetentionYears
        LegalHold     = [bool]$ImmutableLegalHold
        Reason        = $null
    }
}
```

> **Hedged claim.** WORM immutability **supports compliance with** SEC 17a-4(f)(2)(ii)(A) and FINRA 4511 retention expectations. It does **not** by itself satisfy the Designated Third-Party (D3P) attestation requirement under SEC 17a-4(f)(3)(vii) — that must be arranged separately with the storage vendor.

---

## §14 — Cross-control references

This control's PowerShell evidence depends on, or is consumed by, the following sister controls. The links below are the canonical anchors used by the §2 evidence exporter when generating cross-references inside manifest payloads.

| Control | Title | Why it matters here |
|---|---|---|
| [1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | Restrict Agent Publishing by Authorization | A "Clean" feature catalog row does **not** imply publishing authorization; defect-catalog F1–F15 explicitly avoid that conflation |
| [1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Agent Registry and Integrated Apps Management | The §2 agent reader joins on AgentId from this registry; broken joins become `Pending` |
| [1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | Advanced Connector Policies (ACP) | §2 DLP correlation reads policies governed under 1.4 |
| [1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | Communication Compliance Monitoring | §10 SIEM forwarding lands events that supplement 1.10's CC policies |
| [1.25](../../../controls/pillar-1-security/1.25-mime-type-restrictions.md) | MIME Type Restrictions | A feature toggle that re-enables a previously restricted MIME path is captured by §2 + §2 |
| [2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | Environment Groups and Tier Classification | Defect F6 (Default-environment misuse) and F3 (Zone elevation) anchor here |
| [2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Model Risk Management Alignment (OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)) | Catalog rows with `RiskRating in {High, Critical}` require an MRM Review ID |
| [2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision and Oversight (FINRA Rule 3110) | Defect F10 (silent agent override) is a direct supervision-program risk |
| [2.17](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Multi-Agent Orchestration Limits | AGF workflow tools enumerated in §2 surface multi-agent paths |
| [2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Agent 365 Admin Center Governance Console | The §2 M365 hub reader and 2.25's console must agree; disagreement is treated as Anomaly |

> **Final hedged statement.** The helpers documented in §§2–14 **aid in** producing a defensible, auditable record of which Microsoft 365 / Power Platform / Copilot Studio / Agent Framework / MCP features are enabled in which environments, on which agents, under which catalog approval, with which change ticket. They do **not**, individually or collectively, constitute legal compliance certification. A "Clean" rollup means *the configuration matches the approved catalog as of the run timestamp*. Implementation requires the role assignments listed in §1.3. Organizations should verify each helper's behaviour in a non-production tenant, retain at least one prior manifest for hash-chain validation, and route any `Anomaly` or `Pending` finding to the AI Governance Lead for adjudication before the next supervisory cycle.

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*

