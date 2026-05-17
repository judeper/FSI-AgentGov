# Control 1.6 — PowerShell Setup: DSPM for AI

**Control:** [1.6 Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)
**Baseline:** [PowerShell baseline (`_shared/powershell-baseline.md`)](../../_shared/powershell-baseline.md)
**Last UI Verified:** April 2026

> **Important:** There is **no dedicated `Microsoft.Purview.DSPM.AI` PowerShell module**. DSPM for AI is configured primarily through the Purview portal. PowerShell coverage is **detection / evidence / cross-control bridging** via:
>
> - `ExchangeOnlineManagement` (`Connect-ExchangeOnline` for `Get-AdminAuditLogConfig`)
> - `ExchangeOnlineManagement` (`Connect-IPPSSession` for DLP / IRM / Retention compliance cmdlets)
> - `Microsoft.Graph` (`Get-MgSubscribedSku`, `Get-MgUserLicenseDetail`, Audit Search Graph API for long-running queries)
> - **Audit Search Graph API** (`auditLogQueries` resource) — the strategic path Microsoft is steering automation customers toward; preferred over `Search-UnifiedAuditLog` for tenants with high event volume
>
> **Reject any cmdlet beginning with `Get-DspmAi*`, `Set-DspmAi*`, `New-DspmAi*` — none exist in Microsoft modules as of April 2026.**

---

## Wrong-shell trap (READ FIRST)

| Cmdlet | Required session | Symptom if used in wrong session |
|---|---|---|
| `Get-AdminAuditLogConfig` | `Connect-ExchangeOnline` | From `Connect-IPPSSession`, `UnifiedAuditLogIngestionEnabled` returns `False` even when audit is on |
| `Set-AdminAuditLogConfig` | `Connect-ExchangeOnline` | From `Connect-IPPSSession`, command-not-found under modern REST modules |
| `Get-DlpCompliancePolicy` / `Get-RetentionCompliancePolicy` | `Connect-IPPSSession` | Not exposed in `Connect-ExchangeOnline` |
| `Get-MgSubscribedSku` | `Connect-MgGraph` | Requires `Organization.Read.All` |

Always assert session state at the top of every script.

---

## Sovereign cloud connection parameters

```powershell
# Commercial
Connect-ExchangeOnline -UserPrincipalName $upn
Connect-IPPSSession -UserPrincipalName $upn

# GCC High
Connect-ExchangeOnline -UserPrincipalName $upn -ExchangeEnvironmentName O365USGovGCCHigh
Connect-IPPSSession -UserPrincipalName $upn `
    -ConnectionUri 'https://ps.compliance.protection.microsoftonline.us/PowerShell-LiveId' `
    -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.us/common'

# DoD
Connect-ExchangeOnline -UserPrincipalName $upn -ExchangeEnvironmentName O365USGovDoD
Connect-IPPSSession -UserPrincipalName $upn `
    -ConnectionUri 'https://l5.ps.compliance.protection.office365.us/PowerShell-LiveId' `
    -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.us/common'

# Graph (sovereign)
Connect-MgGraph -Environment USGov     # GCC / GCC High
Connect-MgGraph -Environment USGovDoD  # DoD
```

---

## Module pinning (mandatory)

```powershell
#Requires -Version 7.2
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Authentication'; RequiredVersion = '2.20.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Identity.DirectoryManagement'; RequiredVersion = '2.20.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Users'; RequiredVersion = '2.20.0' }

[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string] $TenantId,
    [Parameter(Mandatory)] [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string] $Cloud,
    [Parameter(Mandatory)] [string] $UPN,
    [Parameter(Mandatory)] [string] $EvidencePath
)

$transcript = Join-Path $EvidencePath "Control-1.6_${TenantId}_${Cloud}_Transcript_$(Get-Date -Format 'yyyyMMdd-HHmm').log"
Start-Transcript -Path $transcript -IncludeInvocationHeader
```

---

## 1 — License entitlement assertion

```powershell
# Required: Graph Organization.Read.All
$skus = Get-MgSubscribedSku
$required = @('SPE_E5','M365_E5','M365_E5_COMPLIANCE','Microsoft_365_Copilot','Microsoft_Purview_Suite')
$present = $skus | Where-Object { $required -contains $_.SkuPartNumber }
if (-not $present) {
    Write-Error "Tenant lacks required SKU floor for DSPM for AI evidence claims. Aborting."; return
}

# Per-user Copilot entitlement (sample n=20 for evidence)
$users = Get-MgUser -Top 20 -Filter "accountEnabled eq true"
$copilotMissing = foreach ($u in $users) {
    $details = Get-MgUserLicenseDetail -UserId $u.Id -ErrorAction SilentlyContinue
    if ($details.SkuPartNumber -notcontains 'Microsoft_365_Copilot') { $u.UserPrincipalName }
}
$copilotMissing | Out-File (Join-Path $EvidencePath 'copilot-license-gaps.txt')
```

---

## 2 — Audit ingestion (assert-first; do not blindly mutate)

```powershell
Connect-ExchangeOnline -UserPrincipalName $UPN @cloudParams
$cfg = Get-AdminAuditLogConfig
[pscustomobject]@{
    UnifiedAuditLogIngestionEnabled = $cfg.UnifiedAuditLogIngestionEnabled
    Source = 'Exchange Online'
    UTC = (Get-Date).ToUniversalTime().ToString('o')
} | ConvertTo-Json | Out-File (Join-Path $EvidencePath 'audit-state-pre.json')

if (-not $cfg.UnifiedAuditLogIngestionEnabled) {
    if ($PSCmdlet.ShouldProcess('Tenant audit ingestion','Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true')) {
        Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true
    }
} else {
    Write-Information "Audit ingestion already on (default since 2023). No mutation." -InformationAction Continue
}
```

---

## 3 — One-click policy inventory (DLP + Retention + IRM bridging)

```powershell
Connect-IPPSSession -UserPrincipalName $UPN @cloudParams

# DLP — assert Mode AND that the policy targets a Copilot/AI workload
$dlp = Get-DlpCompliancePolicy | ForEach-Object {
    $rules = Get-DlpComplianceRule -Policy $_.Name -ErrorAction SilentlyContinue
    [pscustomobject]@{
        Name      = $_.Name
        Mode      = $_.Mode      # Enable | TestWithNotifications | TestWithoutNotifications | Disable | PendingDeletion
        Workloads = ($_.Workload -split ',') -join '|'
        TouchesCopilot = ($_.Workload -match 'MicrosoftCopilotExperiences|Copilot')
        RuleCount = ($rules | Measure-Object).Count
    }
}
$dlp | Export-Csv (Join-Path $EvidencePath 'dlp-policies.csv') -NoTypeInformation -Encoding UTF8

# Retention — pair policy + rule for accurate RetentionDuration
$ret = Get-RetentionCompliancePolicy | ForEach-Object {
    $rule = Get-RetentionComplianceRule -Policy $_.Name -ErrorAction SilentlyContinue | Select-Object -First 1
    [pscustomobject]@{
        Policy            = $_.Name
        Enabled           = $_.Enabled
        Workload          = $_.Workload
        RetentionDuration = $rule.RetentionDuration
        RetentionAction   = $rule.RetentionAction
    }
}
$ret | Export-Csv (Join-Path $EvidencePath 'retention-policies.csv') -NoTypeInformation -Encoding UTF8
```

---

## 4 — Audit query for `CopilotInteraction` (paginated; not silent-zero-row)

> The correct `RecordType` is **`CopilotInteraction`**. `AIPDiscover`, `AIPHeartBeat`, `AIPSensitivityLabelAction`, etc. are **Azure Information Protection** record types and **return zero Copilot rows** — never use them as DSPM-for-AI evidence.

```powershell
$end   = (Get-Date).ToUniversalTime()
$start = $end.AddDays(-7)
$session = "ctrl16-$(Get-Date -Format 'yyyyMMddHHmmss')"

$all = New-Object System.Collections.Generic.List[object]
do {
    $batch = Search-UnifiedAuditLog `
        -StartDate $start -EndDate $end `
        -RecordType 'CopilotInteraction' `
        -ResultSize 5000 `
        -SessionId $session `
        -SessionCommand ReturnLargeSet
    if ($batch) { $all.AddRange($batch) }
} while ($batch -and $batch.Count -gt 0 -and $all.Count -lt 50000)

if ($all.Count -eq 0) {
    Write-Warning "Zero CopilotInteraction events in last 7 days. Investigate: license, audit ingestion, scope, content capture."
}

# Strategic alternative for high-volume tenants — Audit Search Graph API
# POST https://graph.microsoft.com/v1.0/security/auditLog/queries
# (auditLogQueries resource — preferred per MS guidance Jan 2025+)
```

`AuditData` schema reminder: top-level `CopilotEventData` carries `AppHost`, `Contexts[]`, and `AccessedResources[].SensitivityLabelId`. Do **not** project `RiskScore` / `AccessPattern` — those fields are not in the published `CopilotInteraction` schema and will populate `$null`.

---

## 5 — Evidence emission with SHA-256

```powershell
function Write-FsiEvidence {
    param(
        [Parameter(Mandatory)] $InputObject,
        [Parameter(Mandatory)] [string] $Path,
        [ValidateSet('Json','Csv')] [string] $As = 'Json'
    )
    if ($As -eq 'Json') {
        $InputObject | ConvertTo-Json -Depth 8 | Out-File $Path -Encoding UTF8
    } else {
        $InputObject | Export-Csv $Path -NoTypeInformation -Encoding UTF8
    }
    $hash = (Get-FileHash $Path -Algorithm SHA256).Hash
    [pscustomobject]@{
        File         = (Split-Path $Path -Leaf)
        SHA256       = $hash
        Bytes        = (Get-Item $Path).Length
        GeneratedUtc = (Get-Date).ToUniversalTime().ToString('o')
        ScriptVersion= '1.6-v1.4'
    } | ConvertTo-Json | Out-File "$Path.sha256" -Encoding UTF8
}
```

Apply `Write-FsiEvidence` to every CSV/JSON exported by sections 1–4. Store outputs in immutable storage (Purview retention label / SharePoint hold / WORM blob) aligned to Control 1.7.

---

## 6 — Teardown

```powershell
try {
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
    Disconnect-MgGraph -ErrorAction SilentlyContinue
} finally {
    Stop-Transcript | Out-Null
}
```

---

## Anti-patterns

| Anti-pattern | Why it's wrong |
|---|---|
| Iterating `-RecordType` over `AIPDiscover`, `AIPHeartBeat`, `AIPSensitivityLabelAction` for Copilot evidence | These are AIP record types; return zero Copilot rows (silent-zero-row trap) |
| Calling `Set-AdminAuditLogConfig` after `Connect-IPPSSession` | Wrong shell — command-not-found under modern REST modules |
| Single-shot `Search-UnifiedAuditLog -ResultSize 5000` without `-SessionId` / `-SessionCommand ReturnLargeSet` | Silent truncation past 5,000 rows |
| Filtering `Where-Object { $_.Enabled -eq $true }` on DLP policy | DLP uses `Mode`, not `Enabled`; policy in `Enable` mode without Copilot workload is not a DSPM-for-AI control |
| Using `Send-MailMessage` for alerts | Cmdlet is obsolete per Microsoft; use Graph `sendMail` or OAuth2 SMTP |
| Asserting `RiskScore` / `AccessPattern` fields | Not in published `CopilotInteraction` schema — fabricated |
| Hard-coded `admin@contoso.com` UPN | Must be parameterized for CAB approval |

---

## Cross-references

- [_shared/powershell-baseline.md](../../_shared/powershell-baseline.md)
- [Control 1.6 Verification & Testing](verification-testing.md)
- [Control 1.6 Troubleshooting](troubleshooting.md)
- [Control 1.7 PowerShell Setup](../1.7/powershell-setup.md) — durable Audit Premium retention
- Microsoft Learn — [`CopilotInteraction` schema](https://learn.microsoft.com/en-us/office/office-365-management-api/copilot-schema)
- Microsoft Learn — [Audit Search Graph API (`auditLogQueries`)](https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogquery)
- Microsoft Learn — [Search-UnifiedAuditLog](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog)
- Microsoft Learn — [Connect-IPPSSession](https://learn.microsoft.com/en-us/powershell/module/exchange/connect-ippssession)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
