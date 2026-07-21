# PowerShell Setup: Control 1.4 — Advanced Connector Policies (ACP)

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

> Automation guide for [Control 1.4 — Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md). ACP is managed in the portal or programmatically through the **Power Platform API `governance/ruleBasedPolicies` operations** (`https://api.powerplatform.com`, api-version `2024-10-01`), where a policy carries a rule set with the ID `ConnectorManagement` that holds the connector allowlist. The `Microsoft.PowerApps.Administration.PowerShell` and `Microsoft.PowerApps.PowerShell` modules cover the **prerequisite** Managed Environment, environment group, and classic DLP surface plus **evidence-collection** read paths; the ACP policy body itself is created, assigned, and read through the governance API (or the C#/Python Admin SDKs). This split means two auth contexts — see Section 2.

---

## 1. Modules

```powershell
# REQUIRED: pin to versions approved by your CAB. See the FSI PowerShell baseline §1.
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name Microsoft.PowerApps.PowerShell `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense

# For the ACP governance API calls (Sections 4–7): acquire tokens with MSAL.PS.
Install-Module -Name MSAL.PS `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
```

The two `Microsoft.PowerApps.*` modules are **Windows PowerShell 5.1 (Desktop) only**. Add the edition guard from baseline §2 to every script that calls their cmdlets:

```powershell
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop edition). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}
```

---

## 2. Authenticate

ACP automation uses **two separate auth contexts**:

- **Prerequisite / evidence cmdlets** (Section 3, Section 6) run against the Power Apps admin modules via `Add-PowerAppsAccount`.
- **ACP governance API calls** (Sections 4, 5, 7) run against `https://api.powerplatform.com` and need a token for that resource, obtained from an [app registration configured for the Power Platform API](https://learn.microsoft.com/power-platform/admin/programmability-authentication-v2). The signing identity must hold an RBAC role that can write governance policies — **Power Platform contributor** or **Power Platform owner** (see [Assign roles to service principals](https://learn.microsoft.com/power-platform/admin/programmability-tutorial-rbac-role-assignment)). `Add-PowerAppsAccount` alone does not authorize the governance API; a caller with only that session receives `401/403`, not `404`.

```powershell
# --- Context 1: Power Apps admin modules (prerequisite + evidence cmdlets) ---
# Interactive (recommended for change windows under PIM elevation)
Add-PowerAppsAccount

# Unattended (service principal). Store secret in Key Vault, never in source.
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId

# --- Context 2: Power Platform governance API (ACP policy CRUD) ---
# These session variables are reused by Sections 4, 5, and 7.
Import-Module MSAL.PS
$clientId   = '<application (client) ID of your Power Platform API app registration>'
$apiBaseUrl = 'https://api.powerplatform.com'
$apiVersion = '2024-10-01'   # single source of truth for the ACP api-version

# Interactive sign-in for a token scoped to the Power Platform API.
$auth    = Get-MsalToken -ClientId $clientId -Scope "$apiBaseUrl/.default" -Interactive
$headers = @{}
$headers['Authorization'] = 'Bearer {0}' -f $auth.AccessToken
# Unattended: Get-MsalToken -ClientId $clientId -ClientSecret $secret -TenantId $tenantId `
#     -Scope "$apiBaseUrl/.default"  (confidential-client flow; store secret in Key Vault)
```


---

## 3. Verify Prerequisites Before Authoring ACP

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$EnvironmentId,
    [Parameter(Mandatory)] [string]$EnvironmentGroupId
)
$ErrorActionPreference = 'Stop'

# 3a. Confirm environment exists and is Managed
$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId
if (-not $env) { throw "Environment $EnvironmentId not found (or wrong cloud endpoint)." }

$isManaged = $env.Internal.properties.governanceConfiguration.protectionLevel -eq 'Standard'
if (-not $isManaged) {
    Write-Warning ("Environment '$($env.DisplayName)' is not a Managed Environment. " +
        "ACP is supported but nonblockable connectors (Dataverse, Office 365 Users, etc.) " +
        "cannot be blocked. To block nonblockable connectors, enable Managed Environments " +
        "per Control 2.1. Continuing evidence collection for certified connectors only.")
}

# 3b. Confirm region is United States
if ($env.Location -notmatch '^unitedstates') {
    Write-Warning "Environment region '$($env.Location)' is not US. Confirm zone classification before proceeding."
}

# 3c. Confirm classic DLP policy exists (mixed-mode coverage for custom + HTTP connectors)
$dlp = Get-DlpPolicy
if (-not $dlp) {
    Write-Warning "No classic DLP policies found. ACP does not cover custom or HTTP connectors — at least one classic DLP policy is required for FSI mixed mode."
}
```

---

## 4. Create and Assign the ACP Policy via the Power Platform Governance API

> ACP is authored through the `governance/ruleBasedPolicies` operations on `https://api.powerplatform.com`. Applying a policy is a two-part operation — **create** the policy (a body containing the `ConnectorManagement` rule set), then **assign** it to the environment group. **Assignment is the apply**: every environment in the group inherits the policy and stays in sync. There is no separate publish API call — "Publish rules" is a Power Platform admin center action, described in the [Portal Walkthrough](portal-walkthrough.md). To modify an already-assigned policy, edit it in place: read it back (Section 5), change the `ConnectorManagement` rule set, and `PATCH .../ruleBasedPolicies/{policyId}` (patch updates the rule set by ID and leaves other rule sets intact). Re-running the create call below produces a **new** policy, so track the returned policy id.

The allowlist body in `$PolicyBodyJsonPath` follows the verified ACP policy shape. A connector absent from `AllowedConnectorList` is blocked (default-deny); `AllAllowed` permits every action, while `SomeAllowed` restricts the connector to the operation IDs in `AllowedActions`. Preserve the rule set `version` read from an existing policy.

```json
{
  "name": "FSI ACP baseline",
  "ruleSets": [
    {
      "id": "ConnectorManagement",
      "version": "1.0",
      "inputs": {
        "AllowedConnectorList": [
          {
            "AllowedConnector": "/providers/Microsoft.PowerApps/apis/shared_office365",
            "AllowedActionsMode": "AllAllowed",
            "AllowedConnectionTypesMode": "AllAllowed"
          },
          {
            "AllowedConnector": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
            "AllowedActionsMode": "SomeAllowed",
            "AllowedActions": ["GetItem", "CreateRecord"],
            "AllowedConnectionTypesMode": "AllAllowed"
          }
        ]
      }
    }
  ]
}
```

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string]$EnvironmentGroupId,
    [Parameter(Mandatory)] [string]$PolicyBodyJsonPath,   # ConnectorManagement policy body in source control
    [string]$EvidencePath = ".\evidence\1.4"
)
$ErrorActionPreference = 'Stop'
# Reuses the Section 2 governance-API session variables: $apiBaseUrl, $apiVersion, $headers.
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
Start-Transcript -Path "$EvidencePath\acp-apply-$ts.log" -IncludeInvocationHeader

if (-not (Test-Path $PolicyBodyJsonPath)) { throw "Policy body file not found: $PolicyBodyJsonPath" }
$body = Get-Content -Raw -Path $PolicyBodyJsonPath

# 4a. Snapshot the policy currently assigned to the group (BEFORE) for rollback evidence
try {
    $beforeAssign = Invoke-RestMethod -Method Get `
        -Uri "$apiBaseUrl/governance/ruleBasedPolicies/environmentGroups/$EnvironmentGroupId/assignments?api-version=$apiVersion" `
        -Headers $headers
    if ($beforeAssign.value) {
        $before = Invoke-RestMethod -Method Get `
            -Uri "$apiBaseUrl/governance/ruleBasedPolicies/$($beforeAssign.value[0].policyId)?api-version=$apiVersion" `
            -Headers $headers
        $before | ConvertTo-Json -Depth 30 | Set-Content "$EvidencePath\acp-before-$ts.json" -Encoding UTF8
    }
} catch {
    Write-Warning "No existing ACP policy on group $EnvironmentGroupId (first assignment): $($_.Exception.Message)"
}

# 4b. Create the policy (contains the ConnectorManagement rule set)
if ($PSCmdlet.ShouldProcess($EnvironmentGroupId, "Create ACP policy and assign to environment group")) {
    $policy = Invoke-RestMethod -Method Post `
        -Uri "$apiBaseUrl/governance/ruleBasedPolicies?api-version=$apiVersion" `
        -Headers $headers -ContentType 'application/json' -Body $body
    $policy | ConvertTo-Json -Depth 30 | Set-Content "$EvidencePath\acp-policy-$ts.json" -Encoding UTF8

    # 4c. Assignment IS the apply. Empty body ({}) targets the whole group; members inherit and stay in sync.
    $assignment = Invoke-RestMethod -Method Post `
        -Uri "$apiBaseUrl/governance/ruleBasedPolicies/$($policy.id)/environmentGroups/$EnvironmentGroupId/assignments?api-version=$apiVersion" `
        -Headers $headers -ContentType 'application/json' -Body '{}'
    $assignment | ConvertTo-Json -Depth 30 | Set-Content "$EvidencePath\acp-assignment-$ts.json" -Encoding UTF8
    Write-Host "[APPLIED] Policy $($policy.id) assigned to group $EnvironmentGroupId" -ForegroundColor Green
}

Stop-Transcript
```

> **Single-environment scope:** to target one high-risk or pilot environment instead of a group, assign the policy to the environment: `POST $apiBaseUrl/governance/ruleBasedPolicies/{policyId}/environments/{environmentId}/assignments`. Each environment supports one effective ACP policy.

> **API version:** all ACP calls use the single `$apiVersion` variable (`2024-10-01`) set in Section 2. The ACP API and Admin SDKs ship monthly — confirm the current version against the [ACP programmability tutorial](https://learn.microsoft.com/power-platform/admin/programmability-tutorial-manage-advanced-connector-policies) and the [governance rule-based-policies REST reference](https://learn.microsoft.com/rest/api/power-platform/governance/rule-based-policies) before each change window.

---

## 5. Verify the Policy and Assignment (Read-Back)

Verification reads the assignment and the policy back from the governance API. There is no `properties.status = 'Applied'` field in the API response — `Status: Applied` is a Power Platform admin center display state (see the [Portal Walkthrough](portal-walkthrough.md) and [Verification & Testing](verification-testing.md) checklist). Programmatically, an assignment present on the group plus a readable `ConnectorManagement` allowlist confirms enforcement.

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$EnvironmentGroupId
)
$ErrorActionPreference = 'Stop'
# Reuses the Section 2 governance-API session variables: $apiBaseUrl, $apiVersion, $headers.

# 5a. Confirm a policy is assigned to the group (assignment present == applied)
$assignments = Invoke-RestMethod -Method Get `
    -Uri "$apiBaseUrl/governance/ruleBasedPolicies/environmentGroups/$EnvironmentGroupId/assignments?api-version=$apiVersion" `
    -Headers $headers
if (-not $assignments.value) {
    Write-Error "No ACP policy assigned to group $EnvironmentGroupId. Assign a policy (Section 4) before verifying. If this is a 401/403, confirm the RBAC role from Section 2."
    return
}
$policyId = $assignments.value[0].policyId

# 5b. Read the policy back and confirm the ConnectorManagement allowlist
$policy  = Invoke-RestMethod -Method Get `
    -Uri "$apiBaseUrl/governance/ruleBasedPolicies/$($policyId)?api-version=$apiVersion" `
    -Headers $headers
$ruleSet   = $policy.ruleSets | Where-Object { $_.id -eq 'ConnectorManagement' }
$allowlist = $ruleSet.inputs.AllowedConnectorList

if ($ruleSet -and $allowlist) {
    Write-Host "[PASS] Group $EnvironmentGroupId -> policy $policyId with $($allowlist.Count) allowlisted connector(s)." -ForegroundColor Green
} else {
    Write-Error "Policy $policyId has no ConnectorManagement rule set / AllowedConnectorList. Investigate the assignment via PPAC environment History ('Update Managed Environment Settings' lifecycle event)."
}
```

---

## 6. Evidence Collection (Read-Only Inventory)

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$EnvironmentGroupId,
    [string]$EvidencePath = ".\evidence\1.4"
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'

# Helper: emit JSON + SHA-256 + manifest entry (see baseline §4)
function Write-FsiEvidence {
    param([Parameter(Mandatory)] $Object, [Parameter(Mandatory)] [string]$Name, [Parameter(Mandatory)] [string]$EvidencePath)
    $stamp = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $jsonPath = Join-Path $EvidencePath "$Name-$stamp.json"
    $Object | ConvertTo-Json -Depth 30 | Set-Content -Path $jsonPath -Encoding UTF8
    $hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
    $manifestPath = Join-Path $EvidencePath "manifest.json"
    $manifest = @()
    if (Test-Path $manifestPath) { $manifest = @(Get-Content $manifestPath | ConvertFrom-Json) }
    $manifest += [PSCustomObject]@{
        file = (Split-Path $jsonPath -Leaf); sha256 = $hash; bytes = (Get-Item $jsonPath).Length; generated_utc = $stamp; control = '1.4'
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
    return $jsonPath
}

# 6a. ACP policy assigned to the group (current allowlist) — via the governance API.
# Reuses the Section 2 governance-API session variables: $apiBaseUrl, $apiVersion, $headers.
$acpAssignments = Invoke-RestMethod -Method Get `
    -Uri "$apiBaseUrl/governance/ruleBasedPolicies/environmentGroups/$EnvironmentGroupId/assignments?api-version=$apiVersion" `
    -Headers $headers
if ($acpAssignments.value) {
    $acpPolicy = Invoke-RestMethod -Method Get `
        -Uri "$apiBaseUrl/governance/ruleBasedPolicies/$($acpAssignments.value[0].policyId)?api-version=$apiVersion" `
        -Headers $headers
    Write-FsiEvidence -Object $acpPolicy -Name 'acp-ruleset' -EvidencePath $EvidencePath
} else {
    Write-Warning "No ACP policy assigned to group $EnvironmentGroupId — nothing to snapshot for 6a."
}

# 6b. Environment group membership
$envs = Get-AdminPowerAppEnvironment | Where-Object { $_.Internal.properties.parentEnvironmentGroup.id -match $EnvironmentGroupId }
Write-FsiEvidence -Object ($envs | Select-Object DisplayName, EnvironmentName, Location, EnvironmentType) -Name 'envgroup-members' -EvidencePath $EvidencePath

# 6c. Classic DLP policies (for mixed-mode coverage proof)
$dlpPolicies = Get-DlpPolicy
Write-FsiEvidence -Object $dlpPolicies -Name 'classic-dlp-policies' -EvidencePath $EvidencePath

# 6d. Connection inventory per member environment (proof allowlist matches reality)
foreach ($e in $envs) {
    $conns = Get-AdminPowerAppConnection -EnvironmentName $e.EnvironmentName
    Write-FsiEvidence -Object ($conns | Select-Object DisplayName, ConnectorName, CreatedBy, CreatedTime) `
        -Name "connections-$($e.EnvironmentName)" -EvidencePath $EvidencePath
}

Write-Host "[DONE] Evidence written to $EvidencePath with manifest.json" -ForegroundColor Green
```

> **WORM landing:** copy `$EvidencePath` to a Microsoft Purview Data Lifecycle retention-locked location (or Azure Storage immutability container) to satisfy SEC 17a-4(f) preservation expectations. See baseline §4.

---

## 7. Rollback (Restore the Previous ACP Body)

Rollback restores the `ConnectorManagement` rule set captured in Section 4a (`acp-before-*.json`) onto the **currently assigned** policy with a `PATCH`. Patch updates the rule set by ID and leaves the policy's other rule sets intact; the assignment already in place re-syncs member environments, so no publish step is required. Read the current policy id from the group's assignment (Section 5) and pass it as `$PolicyId`.

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string]$PolicyId,        # currently assigned policy (from Section 5)
    [Parameter(Mandatory)] [string]$BeforeJsonPath   # acp-before-*.json snapshot from Section 4a
)
$ErrorActionPreference = 'Stop'
# Reuses the Section 2 governance-API session variables: $apiBaseUrl, $apiVersion, $headers.

$before      = Get-Content -Raw -Path $BeforeJsonPath | ConvertFrom-Json
$restoreBody = @{ name = $before.name; ruleSets = $before.ruleSets } | ConvertTo-Json -Depth 30

if ($PSCmdlet.ShouldProcess($PolicyId, "PATCH ACP policy back to $BeforeJsonPath")) {
    Invoke-RestMethod -Method Patch `
        -Uri "$apiBaseUrl/governance/ruleBasedPolicies/$($PolicyId)?api-version=$apiVersion" `
        -Headers $headers -ContentType 'application/json' -Body $restoreBody
}
```

Always invoke first with `-WhatIf`. To turn ACP off entirely rather than restore a prior body, use the `removeRule` operation (`PATCH .../ruleBasedPolicies/{policyId}/removeRule`) on the group's policy and then on each member environment's policy — see the [ACP programmability tutorial](https://learn.microsoft.com/power-platform/admin/programmability-tutorial-manage-advanced-connector-policies).

---

## 8. What This Script Does **Not** Do

- **Custom connectors / HTTP connectors:** not yet in ACP scope; govern via classic DLP groups and `Set-PowerAppDlpPolicyConnectorConfigurations` for endpoint filtering.
- **Microsoft Copilot Studio virtual connectors:** not in ACP scope and not planned. Continue using classic DLP data policies.
- **MCP server tool-level blocking:** ACP supports server-level only. Tool-level toggles are configured in Copilot Studio per agent.
- **Service-principal-bypass safety net:** classic DLP scoped at the **environment level** (not security-group level) is required to cover SP-authenticated connections — see the warning in the control doc.

---

[Back to Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: July 2026 | Version: v1.6.2 | UI Verification Status: Current*
