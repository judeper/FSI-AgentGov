# PowerShell Setup: Control 1.4 — Advanced Connector Policies (ACP)

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), and SHA-256 evidence emission.

> Automation guide for [Control 1.4 — Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md). ACP is managed through the Power Platform API `governance/ruleBasedPolicies` namespace with API version `2024-10-01`. Policy creation and assignment are separate operations. The Power Platform administration modules do not replace this API surface.

!!! important "No live tenant execution in this repository change"
    This pull request updates documentation only. The examples were not executed against a live tenant. Run them first with `-WhatIf`, then execute and validate them during an approved change window in a representative tenant.

---

## 1. Authentication and Authorization Prerequisites

Register a single-tenant Microsoft Entra application for the **Power Platform API** and request tokens for:

```text
https://api.powerplatform.com/.default
```

For interactive administration, configure the app registration for an interactive browser flow. For unattended automation, use the documented confidential-client flow with a certificate or a secret retrieved at runtime from an approved secret store.

The calling identity must be authorized to manage governance policies:

- **Delegated user:** the signed-in user needs the applicable Power Platform administrative permissions.
- **Service principal:** assign **Power Platform contributor** or **Power Platform owner** through Power Platform RBAC at the narrowest practical scope. The RBAC feature and role-assignment API are documented as preview; validate suitability with your change-management and security teams.

Do not print, transcript, serialize, or persist access tokens. The examples keep the token in process memory and write only policy/assignment responses to the evidence folder.

See:

- [Authentication for Power Platform API](https://learn.microsoft.com/power-platform/admin/programmability-authentication-v2)
- [Assign Power Platform RBAC roles to service principals](https://learn.microsoft.com/power-platform/admin/programmability-tutorial-rbac-role-assignment)

### Module

The interactive example follows Microsoft's documented `MSAL.PS` flow. Pin the module to a CAB-approved version:

```powershell
Install-Module -Name MSAL.PS `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AcceptLicense
```

---

## 2. Approved Allowlist Input

ACP is default-deny. A certified connector omitted from `AllowedConnectorList` is blocked. Use connector resource IDs and operation IDs returned by the [Connector Catalog API](https://learn.microsoft.com/rest/api/power-platform/connectivity/connectors).

Example `approved-connectors.json`:

```json
[
  {
    "AllowedConnector": "/providers/Microsoft.PowerApps/apis/shared_office365",
    "AllowedActionsMode": "AllAllowed",
    "AllowedConnectionTypesMode": "AllAllowed"
  },
  {
    "AllowedConnector": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
    "AllowedActionsMode": "SomeAllowed",
    "AllowedActions": [
      "GetItem",
      "CreateRecord"
    ],
    "AllowedConnectionTypesMode": "AllAllowed"
  }
]
```

- `AllAllowed` permits every action for that connector.
- `SomeAllowed` permits only the operation IDs listed in `AllowedActions`.
- Preserve the `ConnectorManagement` rule-set version returned by the service when updating an existing policy.
- An empty list blocks all certified connectors except platform behavior documented for the target environment. The script requires `-AllowEmptyAllowlist` to make that high-impact intent explicit.

---

## 3. Create or Update and Assign the Group Policy

The script follows these fail-closed branches:

1. Read the environment group's assignments.
2. If one policy is assigned, snapshot it and update its `ConnectorManagement` rule set with `PATCH`.
3. If the successful assignment response is empty, look for one unassigned policy with the exact `PolicyName`. Reuse and patch that orphan before assignment; this recovers safely if a previous run created the policy but failed before assignment.
4. If no matching policy exists, create one with `POST`, then assign it to the group with a separate `POST`.
5. Perform new assignment and policy reads after mutation and compare the returned allowlist with the requested allowlist.

The script does **not** convert authentication, authorization, network, service, JSON, or malformed-response failures into "no policy." `Invoke-RestMethod` failures terminate the run. Only a successful response containing an empty `value` array is treated as no assignment.

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string]$ClientId,
    [Parameter(Mandatory)] [string]$EnvironmentGroupId,
    [Parameter(Mandatory)] [string]$PolicyName,
    [Parameter(Mandatory)] [string]$AllowlistJsonPath,
    [string]$EvidencePath = ".\evidence\1.4",
    [switch]$AllowEmptyAllowlist
)

$ErrorActionPreference = 'Stop'
$apiBaseUrl = 'https://api.powerplatform.com'
$apiVersion = '2024-10-01'

function Assert-ValueArrayResponse {
    param(
        [Parameter(Mandatory)] $Response,
        [Parameter(Mandatory)] [string]$Operation
    )

    if ($null -eq $Response -or $Response.PSObject.Properties.Name -notcontains 'value') {
        throw "$Operation returned a malformed response: required 'value' property is missing."
    }
}

function Write-FsiEvidence {
    param(
        [Parameter(Mandatory)] $Object,
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [string]$EvidencePath
    )

    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ')
    $jsonPath = Join-Path $EvidencePath "$Name-$stamp.json"
    $Object | ConvertTo-Json -Depth 30 | Set-Content -Path $jsonPath -Encoding UTF8

    $entry = [PSCustomObject]@{
        file          = Split-Path $jsonPath -Leaf
        sha256        = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
        bytes         = (Get-Item $jsonPath).Length
        generated_utc = $stamp
        control       = '1.4'
    }

    $manifestPath = Join-Path $EvidencePath 'manifest.json'
    $manifest = @()
    if (Test-Path $manifestPath) {
        $manifest = @(Get-Content -Raw -Path $manifestPath | ConvertFrom-Json)
    }
    $manifest += $entry
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
}

function Get-AllowlistFingerprint {
    param([Parameter(Mandatory)] [AllowEmptyCollection()] [object[]]$Allowlist)

    $normalized = @(
        $Allowlist | ForEach-Object {
            [PSCustomObject][ordered]@{
                AllowedConnector           = [string]$_.AllowedConnector
                AllowedActionsMode         = [string]$_.AllowedActionsMode
                AllowedActions             = @($_.AllowedActions | Sort-Object)
                AllowedConnectionTypesMode = [string]$_.AllowedConnectionTypesMode
                AllowedConnectionTypes     = @($_.AllowedConnectionTypes | Sort-Object)
            }
        } | Sort-Object AllowedConnector
    )
    return $normalized | ConvertTo-Json -Depth 10 -Compress
}

if (-not (Test-Path -LiteralPath $AllowlistJsonPath -PathType Leaf)) {
    throw "Allowlist file not found: $AllowlistJsonPath"
}

$allowlistDocument = Get-Content -Raw -LiteralPath $AllowlistJsonPath | ConvertFrom-Json
if ($allowlistDocument.PSObject.Properties.Name -contains 'AllowedConnectorList') {
    $allowedConnectors = @($allowlistDocument.AllowedConnectorList)
}
else {
    $allowedConnectors = @($allowlistDocument)
}

if ($allowedConnectors.Count -eq 0 -and -not $AllowEmptyAllowlist) {
    throw 'The allowlist is empty. Re-run with -AllowEmptyAllowlist only when blocking all certified connectors is the approved intent.'
}

foreach ($entry in $allowedConnectors) {
    foreach ($requiredProperty in 'AllowedConnector', 'AllowedActionsMode', 'AllowedConnectionTypesMode') {
        if ($entry.PSObject.Properties.Name -notcontains $requiredProperty -or
            [string]::IsNullOrWhiteSpace([string]$entry.$requiredProperty)) {
            throw "Allowlist entry is missing required property '$requiredProperty'."
        }
    }

    if ($entry.AllowedActionsMode -notin 'AllAllowed', 'SomeAllowed') {
        throw "Unsupported AllowedActionsMode '$($entry.AllowedActionsMode)' for $($entry.AllowedConnector)."
    }
}

New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
Import-Module MSAL.PS

# Token remains in memory. Do not output $auth, $headers, or the Authorization value.
$auth = Get-MsalToken `
    -ClientId $ClientId `
    -Scope 'https://api.powerplatform.com/.default' `
    -Interactive

if ($null -eq $auth -or [string]::IsNullOrWhiteSpace([string]$auth.AccessToken)) {
    throw 'Power Platform API token acquisition returned no access token.'
}
$headers = @{ Authorization = "Bearer $($auth.AccessToken)" }

function Invoke-PowerPlatformApi {
    param(
        [Parameter(Mandatory)] [ValidateSet('GET', 'POST', 'PATCH')] [string]$Method,
        [Parameter(Mandatory)] [string]$Uri,
        [string]$Body
    )

    $request = @{
        Method      = $Method
        Uri         = $Uri
        Headers     = $headers
        ErrorAction = 'Stop'
    }
    if ($PSBoundParameters.ContainsKey('Body')) {
        $request.ContentType = 'application/json'
        $request.Body = $Body
    }
    Invoke-RestMethod @request
}

try {
    $assignmentUri = "$apiBaseUrl/governance/ruleBasedPolicies/environmentGroups/$EnvironmentGroupId/assignments?includeRuleSetCounts=true&api-version=$apiVersion"
    $beforeAssignments = Invoke-PowerPlatformApi -Method GET -Uri $assignmentUri
    Assert-ValueArrayResponse -Response $beforeAssignments -Operation 'List environment-group assignments'
    Write-FsiEvidence -Object $beforeAssignments -Name 'acp-assignments-before' -EvidencePath $EvidencePath

    $assignments = @($beforeAssignments.value)
    if ($assignments.Count -gt 1) {
        throw "Group $EnvironmentGroupId returned $($assignments.Count) ACP assignments. Refusing to choose one."
    }

    $policy = $null
    $policyId = $null

    if ($assignments.Count -eq 1) {
        $policyId = [string]$assignments[0].policyId
        if ([string]::IsNullOrWhiteSpace($policyId)) {
            throw 'The assignment response did not contain policyId.'
        }

        $policyUri = "$apiBaseUrl/governance/ruleBasedPolicies/$policyId`?api-version=$apiVersion"
        $policy = Invoke-PowerPlatformApi -Method GET -Uri $policyUri
        Write-FsiEvidence -Object $policy -Name 'acp-policy-before' -EvidencePath $EvidencePath
    }
    else {
        # A successful empty assignment list is the only "no assignment" signal.
        # Recover an unassigned exact-name policy left by an interrupted prior run.
        $policiesUri = "$apiBaseUrl/governance/ruleBasedPolicies?api-version=$apiVersion"
        $policies = Invoke-PowerPlatformApi -Method GET -Uri $policiesUri
        Assert-ValueArrayResponse -Response $policies -Operation 'List rule-based policies'

        $nameMatches = @($policies.value | Where-Object { $_.name -eq $PolicyName })
        if ($nameMatches.Count -gt 1) {
            throw "Found multiple policies named '$PolicyName'. Refusing to create or select another."
        }

        if ($nameMatches.Count -eq 1) {
            $policyId = [string]$nameMatches[0].id
            $candidateAssignmentsUri = "$apiBaseUrl/governance/ruleBasedPolicies/$policyId/assignments?includeRuleSetCounts=true&api-version=$apiVersion"
            $candidateAssignments = Invoke-PowerPlatformApi -Method GET -Uri $candidateAssignmentsUri
            Assert-ValueArrayResponse -Response $candidateAssignments -Operation 'List candidate policy assignments'

            if (@($candidateAssignments.value).Count -ne 0) {
                throw "Policy '$PolicyName' is already assigned to another scope. Refusing to modify or reuse it."
            }

            $policyUri = "$apiBaseUrl/governance/ruleBasedPolicies/$policyId`?api-version=$apiVersion"
            $policy = Invoke-PowerPlatformApi -Method GET -Uri $policyUri
            Write-FsiEvidence -Object $policy -Name 'acp-orphan-policy-before' -EvidencePath $EvidencePath
        }
    }

    $existingConnectorRule = $null
    if ($null -ne $policy) {
        $existingConnectorRule = @($policy.ruleSets | Where-Object { $_.id -eq 'ConnectorManagement' })
        if ($existingConnectorRule.Count -gt 1) {
            throw "Policy $policyId contains multiple ConnectorManagement rule sets."
        }
        $existingConnectorRule = $existingConnectorRule | Select-Object -First 1
    }

    $ruleVersion = if ($null -ne $existingConnectorRule -and
        -not [string]::IsNullOrWhiteSpace([string]$existingConnectorRule.version)) {
        [string]$existingConnectorRule.version
    }
    else {
        '1.0'
    }

    $connectorRule = @{
        id      = 'ConnectorManagement'
        version = $ruleVersion
        inputs  = @{ AllowedConnectorList = $allowedConnectors }
    }

    if ($null -ne $policy) {
        $effectiveName = if ([string]::IsNullOrWhiteSpace([string]$policy.name)) { $PolicyName } else { [string]$policy.name }
        $patchBody = @{ name = $effectiveName; ruleSets = @($connectorRule) } | ConvertTo-Json -Depth 20

        if (-not $PSCmdlet.ShouldProcess("policy $policyId", 'PATCH ConnectorManagement rule set')) {
            return
        }
        $null = Invoke-PowerPlatformApi -Method PATCH `
            -Uri "$apiBaseUrl/governance/ruleBasedPolicies/$policyId`?api-version=$apiVersion" `
            -Body $patchBody
    }
    else {
        $createBody = @{ name = $PolicyName; ruleSets = @($connectorRule) } | ConvertTo-Json -Depth 20

        if (-not $PSCmdlet.ShouldProcess("policy '$PolicyName' and group $EnvironmentGroupId", 'POST policy, then POST assignment')) {
            return
        }
        $createdPolicy = Invoke-PowerPlatformApi -Method POST `
            -Uri "$apiBaseUrl/governance/ruleBasedPolicies?api-version=$apiVersion" `
            -Body $createBody
        $policyId = [string]$createdPolicy.id
        if ([string]::IsNullOrWhiteSpace($policyId)) {
            throw 'Policy creation response did not contain id; assignment was not attempted.'
        }
        Write-FsiEvidence -Object $createdPolicy -Name 'acp-policy-created' -EvidencePath $EvidencePath
    }

    if ($assignments.Count -eq 0) {
        # Assignment is a separate operation. Empty JSON means the whole group.
        $assignmentResult = Invoke-PowerPlatformApi -Method POST `
            -Uri "$apiBaseUrl/governance/ruleBasedPolicies/$policyId/environmentGroups/$EnvironmentGroupId/assignments?api-version=$apiVersion" `
            -Body '{}'
        Write-FsiEvidence -Object $assignmentResult -Name 'acp-assignment-created' -EvidencePath $EvidencePath
    }

    # Independent read-back after mutation: confirm scope and policy content.
    $afterAssignments = Invoke-PowerPlatformApi -Method GET -Uri $assignmentUri
    Assert-ValueArrayResponse -Response $afterAssignments -Operation 'Read back environment-group assignments'
    $afterAssignmentValues = @($afterAssignments.value)
    if ($afterAssignmentValues.Count -ne 1 -or [string]$afterAssignmentValues[0].policyId -ne $policyId) {
        throw "Read-back did not confirm policy $policyId as the sole assignment for group $EnvironmentGroupId."
    }

    $afterPolicy = Invoke-PowerPlatformApi -Method GET `
        -Uri "$apiBaseUrl/governance/ruleBasedPolicies/$policyId`?api-version=$apiVersion"
    $afterConnectorRule = @($afterPolicy.ruleSets | Where-Object { $_.id -eq 'ConnectorManagement' })
    if ($afterConnectorRule.Count -ne 1) {
        throw "Read-back did not return exactly one ConnectorManagement rule set for policy $policyId."
    }

    $expectedFingerprint = Get-AllowlistFingerprint -Allowlist $allowedConnectors
    $actualFingerprint = Get-AllowlistFingerprint -Allowlist @($afterConnectorRule[0].inputs.AllowedConnectorList)
    if ($actualFingerprint -cne $expectedFingerprint) {
        throw "Read-back allowlist differs from the requested allowlist for policy $policyId."
    }

    Write-FsiEvidence -Object $afterAssignments -Name 'acp-assignments-after' -EvidencePath $EvidencePath
    Write-FsiEvidence -Object $afterPolicy -Name 'acp-policy-after' -EvidencePath $EvidencePath

    Write-Host "[PASS] Configuration read-back confirmed policy $policyId on group $EnvironmentGroupId."
    Write-Warning 'This confirms policy content and assignment scope only. It does not prove runtime enforcement. Complete the blocked-connector negative test in the verification playbook.'
}
finally {
    if ($null -ne $headers) { $headers.Clear() }
    $auth = $null
}
```

### Idempotency and concurrency boundary

- An assigned group is updated in place with `PATCH`; reruns do not create a second policy.
- With no assignment, an exact-name, unassigned policy is reused to recover from an interrupted create/assign sequence.
- Multiple assignments, duplicate exact-name policies, or a same-name policy assigned elsewhere cause a hard failure.
- Serialize runs for the same environment group. The API examples don't provide a distributed lock, so concurrent first runs could still race between the read and create operations.

There is no programmatic `publishRules` call in this flow. The API contract separates policy mutation from scope assignment. The PPAC environment-group experience still has its documented **Publish rules** action for portal-authored group rules.

---

## 4. What Read-Back Proves

The API read-back establishes:

- the environment group has one returned policy assignment;
- the assignment references the intended policy ID;
- the policy contains one `ConnectorManagement` rule set;
- the service returned the requested `AllowedConnectorList`.

It does **not** establish that a maker or workload was blocked at design time or runtime. To claim enforcement, complete **Test Scenario A — Blocked Certified Connector Cannot Be Added** in the [verification playbook](verification-testing.md), or capture equivalent operational evidence showing a non-allowlisted connector/action was rejected in the target workload.

---

## 5. Read-Only Evidence Collection

For later evidence runs, repeat the two reads used above and emit both responses with hashes:

```powershell
$assignments = Invoke-RestMethod -Method Get `
    -Uri "https://api.powerplatform.com/governance/ruleBasedPolicies/environmentGroups/$EnvironmentGroupId/assignments?includeRuleSetCounts=true&api-version=2024-10-01" `
    -Headers $headers

if ($null -eq $assignments -or $assignments.PSObject.Properties.Name -notcontains 'value') {
    throw "Malformed assignment response for group $EnvironmentGroupId."
}
if (@($assignments.value).Count -ne 1) {
    throw "Expected exactly one assignment for group $EnvironmentGroupId; found $(@($assignments.value).Count)."
}

$policyId = [string]$assignments.value[0].policyId
$policy = Invoke-RestMethod -Method Get `
    -Uri "https://api.powerplatform.com/governance/ruleBasedPolicies/$policyId`?api-version=2024-10-01" `
    -Headers $headers

Write-FsiEvidence -Object $assignments -Name 'acp-assignments' -EvidencePath $EvidencePath
Write-FsiEvidence -Object $policy -Name 'acp-policy' -EvidencePath $EvidencePath
```

Do not catch request failures and emit an empty inventory. A failed evidence run is incomplete evidence, not evidence that no policy exists.

---

## 6. Rollback

If the group had an assigned policy before the change, restore the **prior `ConnectorManagement` rule set** from the before-state policy evidence by patching that rule set back into the same policy. Do not replace the entire policy, because it can contain unrelated rule sets.

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string]$ClientId,
    [Parameter(Mandatory)] [string]$PolicyId,
    [Parameter(Mandatory)] [string]$BeforePolicyJsonPath
)

$ErrorActionPreference = 'Stop'
$apiVersion = '2024-10-01'
$apiBaseUrl = 'https://api.powerplatform.com'

$beforePolicy = Get-Content -Raw -LiteralPath $BeforePolicyJsonPath | ConvertFrom-Json
$priorConnectorRule = @($beforePolicy.ruleSets | Where-Object { $_.id -eq 'ConnectorManagement' })
if ($priorConnectorRule.Count -ne 1) {
    throw "Before-state evidence must contain exactly one ConnectorManagement rule set; found $($priorConnectorRule.Count)."
}

$auth = Get-MsalToken `
    -ClientId $ClientId `
    -Scope 'https://api.powerplatform.com/.default' `
    -Interactive
if ($null -eq $auth -or [string]::IsNullOrWhiteSpace([string]$auth.AccessToken)) {
    throw 'Power Platform API token acquisition returned no access token.'
}
$headers = @{ Authorization = "Bearer $($auth.AccessToken)" }

try {
    $current = Invoke-RestMethod -Method Get `
        -Uri "$apiBaseUrl/governance/ruleBasedPolicies/$PolicyId`?api-version=$apiVersion" `
        -Headers $headers

    $rollbackBody = @{
        name     = $current.name
        ruleSets = @($priorConnectorRule[0])
    } | ConvertTo-Json -Depth 20

    if ($PSCmdlet.ShouldProcess("policy $PolicyId", 'Restore prior ConnectorManagement rule set with PATCH')) {
        $null = Invoke-RestMethod -Method Patch `
            -Uri "$apiBaseUrl/governance/ruleBasedPolicies/$PolicyId`?api-version=$apiVersion" `
            -Headers $headers `
            -ContentType 'application/json' `
            -Body $rollbackBody

        # Separate rollback read-back.
        $restored = Invoke-RestMethod -Method Get `
            -Uri "$apiBaseUrl/governance/ruleBasedPolicies/$PolicyId`?api-version=$apiVersion" `
            -Headers $headers
        $restoredRule = @($restored.ruleSets | Where-Object { $_.id -eq 'ConnectorManagement' })
        if ($restoredRule.Count -ne 1) {
            throw "Rollback read-back did not return the restored ConnectorManagement rule set."
        }
    }
}
finally {
    if ($null -ne $headers) { $headers.Clear() }
    $auth = $null
}
```

Always invoke rollback with `-WhatIf` first.

### When there was no prior `ConnectorManagement` rule

Use the documented operation:

```http
PATCH https://api.powerplatform.com/governance/ruleBasedPolicies/{policyId}/removeRule?api-version=2024-10-01
```

Send the current policy name and the current `ConnectorManagement` rule set in `ruleSets`. Removing it from the **group policy** stops group management, but environments retain their last-applied ACP configuration. To clear ACP enforcement everywhere, enumerate the environments and call `removeRule` on each environment's assigned policy as well. Group removal and per-environment removal are not equivalent.

---

## 7. Scope and Caveats

- This playbook manages the `ConnectorManagement` rule set only. It doesn't build a first-party live ACP assessment collector.
- Custom connectors and HTTP connectors remain outside ACP and require classic data-policy coverage.
- Portal **Status: Applied**, API assignment, and API content read-back are configuration evidence. Pair them with a blocked-connector/action negative test for enforcement evidence.
- Official reference metadata uses the operation name `Create Enviornment Group Rule Based Assignment` with the misspelling "Enviornment"; the documented URI shown in this playbook is the authoritative route.
- Power Platform RBAC role assignment is documented as preview. Revalidate role availability and production support before unattended use.

---

## Official Sources

- [Manage advanced connector policies programmatically](https://learn.microsoft.com/power-platform/admin/programmability-tutorial-manage-advanced-connector-policies)
- [Rule-based policies REST API](https://learn.microsoft.com/rest/api/power-platform/governance/rule-based-policies)
- [Authentication for Power Platform API](https://learn.microsoft.com/power-platform/admin/programmability-authentication-v2)
- [Assign Power Platform RBAC roles to service principals](https://learn.microsoft.com/power-platform/admin/programmability-tutorial-rbac-role-assignment)

[Back to Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: July 2026 | Version: v1.6.2 | UI Verification Status: Current*
