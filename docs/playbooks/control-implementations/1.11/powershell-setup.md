# PowerShell Setup — Control 1.11: Conditional Access and Phishing-Resistant MFA

**Control ID:** 1.11
**Pillar:** 1 — Identity & Access
**Last UI Verified:** April 2026
**Governance Levels:** Zone 1 (Personal), Zone 2 (Team), Zone 3 (Enterprise)

> **Scope.** This playbook automates Conditional Access (CA), phishing-resistant authentication strengths, named locations, CA for Workload Identities (WID), Entra Agent ID (Public Preview), Privileged Identity Management (PIM) eligibility, sign-in audit collection, evidence emission, and validation for Microsoft 365 AI agents in US financial services tenants.
>
> **Hedged language.** Scripts, settings, and verification steps in this playbook **support compliance with** FINRA Rules 3110/3120/4511, SEC Rule 17a-4(f), SEC Reg S-P (17 CFR §248.30), SOX §404, GLBA Safeguards Rule (16 CFR §314.4(c)(5)), OCC Bulletin 2013-29, Federal Reserve SR 11-7, NIST SP 800-63B AAL3, and NYDFS 23 NYCRR §500.12. They do **not** by themselves guarantee compliance — your control owners must validate scope, evidence retention, and exception handling against your firm's written supervisory procedures.
>
> **Preview features.** Entra Agent ID is **Public Preview** as of April 2026 and is subject to change. CA for Workload Identities is **GA** but **requires the Workload Identities Premium add-on SKU** (per service principal, per month). Token Protection for sign-in tokens is **Public Preview**. Continuous Access Evaluation (CAE) is **GA**.

---

## §0 — Wrong-shell trap and pre-flight defects

PowerShell 5.1 silently degrades several Microsoft Graph operations needed by this control. Run the following guard **before** any other code in this playbook. Five recurring "false-clean" defects observed in FSI tenants when scripts run on Windows PowerShell 5.1 instead of PowerShell 7.4 Core:

| # | False-clean defect under PS 5.1 | Real impact |
|---|----------------------------------|-------------|
| 1 | `Get-MgIdentityConditionalAccessPolicy` returns `null` for `sessionControls.signInFrequency` even when set | Operator believes SIF is unset and re-applies it, generating audit churn |
| 2 | `Invoke-MgGraphRequest` against `/beta/agents` deserialises numeric IDs as `[Int32]`, truncating Agent IDs > 2^31 | Agent governance evidence references the wrong agent |
| 3 | TLS 1.0/1.1 negotiated by default → Graph returns 400 from federal cloud endpoints | Operator concludes "GCC High not supported" |
| 4 | `New-MgPolicyAuthenticationStrengthPolicy` accepts but silently drops `deviceBoundPasskey` from the `allowedCombinations` array | Policy appears authored; users still register synced passkeys |
| 5 | PIM cmdlets in `Microsoft.Graph.Identity.Governance` 2.x require `PSEdition Core` — under 5.1 they throw `MethodInvocationException` and the script's `try/catch` masks the failure | Eligible assignments never created; admins remain permanent |

```powershell
#Requires -Version 7.4 -PSEdition Core

if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion.Major -lt 7) {
    throw "Control 1.11 automation requires PowerShell 7.4+ Core. Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}

# Force TLS 1.2+ for all sovereign Graph endpoints
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13

# Execution policy guard — RemoteSigned or stricter
$ep = Get-ExecutionPolicy -Scope Process
if ($ep -in @('Unrestricted','Bypass')) {
    Write-Warning "Process ExecutionPolicy is $ep. Set to RemoteSigned for production runs."
}

# Auth Methods Policy migration check — Microsoft retired the legacy MFA/SSPR policy surface in September 2025.
# Tenants still on the legacy policy will see CA grant controls evaluate against an empty methods set.
try {
    $amp = Invoke-MgGraphRequest -Method GET -Uri 'https://graph.microsoft.com/v1.0/policies/authenticationMethodsPolicy' -ErrorAction Stop
    if ($amp.policyMigrationState -ne 'migrationComplete') {
        Write-Warning "Authentication Methods Policy migration state: $($amp.policyMigrationState). Complete migration before enforcing phishing-resistant CA grants."
    }
} catch {
    Write-Warning "Could not read authenticationMethodsPolicy — verify Policy.Read.All scope."
}
```

---

## §1 — Module installation and version pinning

Pin the following modules. Floating versions cause non-reproducible evidence and are a documented audit finding.

| Module | Pinned version | Purpose |
|--------|----------------|---------|
| `Microsoft.Graph` | `2.20.0` | Meta-module; pulls v1.0 sub-modules |
| `Microsoft.Graph.Beta.Identity.SignIns` | `2.20.0` | Authentication strengths, CA policies (beta surfaces) |
| `Microsoft.Graph.Beta.Identity.DirectoryManagement` | `2.20.0` | Custom security attributes for Agent ID |
| `Microsoft.Graph.Beta.Reports` | `2.20.0` | Sign-in logs with `appliedConditionalAccessPolicies` |
| `Microsoft.Graph.Identity.Governance` | `2.20.0` | PIM eligibility/assignment requests |
| `Microsoft.Graph.Identity.SignIns` | `2.20.0` | v1.0 CA policy CRUD |
| `Microsoft.Graph.Authentication` | `2.20.0` | `Connect-MgGraph`, `Invoke-MgGraphRequest` |
| `Microsoft.Graph.Applications` | `2.20.0` | Service principal lookup for CA WID |

```powershell
$modules = @(
    @{ Name='Microsoft.Graph';                                  Version='2.20.0' }
    @{ Name='Microsoft.Graph.Beta.Identity.SignIns';            Version='2.20.0' }
    @{ Name='Microsoft.Graph.Beta.Identity.DirectoryManagement';Version='2.20.0' }
    @{ Name='Microsoft.Graph.Beta.Reports';                     Version='2.20.0' }
    @{ Name='Microsoft.Graph.Identity.Governance';              Version='2.20.0' }
    @{ Name='Microsoft.Graph.Identity.SignIns';                 Version='2.20.0' }
    @{ Name='Microsoft.Graph.Authentication';                   Version='2.20.0' }
    @{ Name='Microsoft.Graph.Applications';                     Version='2.20.0' }
)
foreach ($m in $modules) {
    if (-not (Get-Module -ListAvailable -Name $m.Name | Where-Object Version -eq $m.Version)) {
        Install-Module -Name $m.Name -RequiredVersion $m.Version -Scope CurrentUser -Force -AllowClobber
    }
    Import-Module -Name $m.Name -RequiredVersion $m.Version -Force
}
```

### Cmdlet status table (April 2026)

| Cmdlet | Surface | Status | Notes |
|--------|---------|--------|-------|
| `New-MgPolicyAuthenticationStrengthPolicy` | v1.0 | GA | `deviceBoundPasskey`, `fido2`, `windowsHelloForBusiness`, `x509CertificateMultiFactor` |
| `New-MgIdentityConditionalAccessPolicy` | v1.0 | GA | Use beta module for `tokenProtectionEnforcementPolicy` |
| `New-MgBetaIdentityConditionalAccessPolicy` | beta | GA-equivalent | Required for token protection + CAE strict enforcement |
| `New-MgIdentityConditionalAccessNamedLocation` | v1.0 | GA | `ipNamedLocation`, `countryNamedLocation` |
| `Invoke-MgGraphRequest -Uri /beta/agents` | beta REST | Public Preview | No typed cmdlet; call REST directly |
| `New-MgRoleManagementDirectoryRoleEligibilityScheduleRequest` | v1.0 | GA | PIM eligibility creation |
| `Get-MgBetaAuditLogSignIn -All` | beta | GA | **Always** use `-All` or follow `@odata.nextLink` |
| `New-MgDirectoryCustomSecurityAttributeDefinition` | v1.0 | GA | `AgentZone`, `AgentSponsor`, `AgentRiskTier` |

### Required Graph delegated scopes

```powershell
$scopes = @(
    'Policy.ReadWrite.ConditionalAccess'
    'Policy.ReadWrite.AuthenticationMethod'
    'Policy.Read.All'
    'Application.Read.All'
    'CustomSecAttributeDefinition.ReadWrite.All'
    'CustomSecAttributeAssignment.ReadWrite.All'
    'RoleManagement.ReadWrite.Directory'
    'RoleEligibilitySchedule.ReadWrite.Directory'
    'AuditLog.Read.All'
    'Directory.Read.All'
    'Agent.ReadWrite.All'   # Preview scope for Entra Agent ID
)
```

### Operator role pre-flight

The operator must hold one or more of the following Entra roles, activated via PIM (per Control 1.11 baseline):

- **Conditional Access Administrator** — CA policies, named locations
- **Authentication Administrator** — auth strengths, methods policy
- **Privileged Authentication Administrator** — break-glass account changes
- **Cloud Application Administrator** — service principal CA WID assignment
- **Entra Security Admin** — Agent ID custom security attributes
- **Power Platform Admin** — agent-tier policy alignment (read-only here)

## §2 — Sovereign-aware bootstrap: `Initialize-Agt111Session`

`Initialize-Agt111Session` is the single entry point for every script in this playbook. It maps the firm's deployed Microsoft 365 cloud to the correct Graph environment, validates operator UPN against the tenant, performs a role pre-flight, prepares an evidence root, and returns a typed context object that all downstream functions consume. **Never** call `Connect-MgGraph` directly elsewhere — it bypasses the cloud-to-environment mapping, which is the single most common cause of "GCC High runs that silently hit Commercial Graph."

```powershell
function Initialize-Agt111Session {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
        [string] $Cloud,

        [Parameter(Mandatory)] [ValidatePattern('^[^@\s]+@[^@\s]+\.[^@\s]+$')]
        [string] $OperatorUpn,

        [Parameter(Mandatory)] [string] $TenantId,

        [string] $EvidenceRoot = (Join-Path $env:LOCALAPPDATA 'FSI-AgentGov\1.11')
    )

    # Sovereign cloud → Graph environment map (verified against Microsoft Learn, April 2026)
    $cloudMap = @{
        'Commercial' = @{ GraphEnv='Global';     Endpoint='https://graph.microsoft.com'      }
        'GCC'        = @{ GraphEnv='USGov';      Endpoint='https://graph.microsoft.us'       }
        'GCCHigh'    = @{ GraphEnv='USGovDoD';   Endpoint='https://dod-graph.microsoft.us'   }
        'DoD'        = @{ GraphEnv='USGovDoD';   Endpoint='https://dod-graph.microsoft.us'   }
    }
    $env = $cloudMap[$Cloud]

    Connect-MgGraph -TenantId $TenantId -Environment $env.GraphEnv -Scopes $script:scopes -NoWelcome -ErrorAction Stop

    $ctx = Get-MgContext
    if (-not $ctx -or $ctx.Account -ne $OperatorUpn) {
        throw "Operator UPN mismatch. Expected '$OperatorUpn', got '$($ctx.Account)'."
    }

    # Role pre-flight — operator must hold at least one CA-capable role, activated via PIM
    $requiredRoles = @(
        'Conditional Access Administrator'
        'Security Administrator'
        'Global Administrator'   # last resort; should be PIM eligible only
    )
    $me = Get-MgUser -UserId $OperatorUpn -ErrorAction Stop
    $assignments = Get-MgRoleManagementDirectoryRoleAssignment -Filter "principalId eq '$($me.Id)'" -ErrorAction SilentlyContinue
    $heldRoleIds = $assignments | Select-Object -ExpandProperty RoleDefinitionId -Unique
    $heldRoleNames = $heldRoleIds | ForEach-Object {
        (Get-MgRoleManagementDirectoryRoleDefinition -UnifiedRoleDefinitionId $_).DisplayName
    }
    $intersect = $heldRoleNames | Where-Object { $_ -in $requiredRoles }
    if (-not $intersect) {
        Write-Warning "Operator $OperatorUpn does not hold any of: $($requiredRoles -join ', '). Activate via PIM before mutating policies."
    }

    if (-not (Test-Path $EvidenceRoot)) { New-Item -ItemType Directory -Path $EvidenceRoot -Force | Out-Null }
    $runId = [Guid]::NewGuid().ToString()
    $runDir = Join-Path $EvidenceRoot "run-$(Get-Date -Format 'yyyyMMdd-HHmmss')-$runId"
    New-Item -ItemType Directory -Path $runDir -Force | Out-Null

    [pscustomobject]@{
        RunId          = $runId
        StartedUtc     = (Get-Date).ToUniversalTime()
        Cloud          = $Cloud
        GraphEnv       = $env.GraphEnv
        Endpoint       = $env.Endpoint
        TenantId       = $TenantId
        OperatorUpn    = $OperatorUpn
        EvidenceDir    = $runDir
        ModuleVersions = ($modules | ForEach-Object { "$($_.Name)@$($_.Version)" })
        HeldRoles      = $heldRoleNames
    }
}
```

**Caveats.** `Get-MgContext.Account` returns the UPN only for delegated sign-in flows; for managed identity or workload identity bootstraps the comparison must be skipped. Organizations should verify the cloud-to-Graph-environment mapping above against current Microsoft Learn documentation before each release — Microsoft has historically renamed `USGovDoD` and consolidated GCC High and DoD endpoints.

---

## §3 — Phishing-resistant authentication strengths

Author a custom authentication strength that **only** permits NIST SP 800-63B AAL3 combinations. FINRA retired SMS and voice MFA from acceptable Reg Notice 24-XX guidance in July 2025; NYDFS §500.12 (fully effective November 1, 2025) requires phishing-resistant MFA for privileged accounts.

```powershell
function New-Agt111PhishResistantStrength {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Context,
        [string] $DisplayName = 'FSI Phishing-Resistant AAL3'
    )

    $body = @{
        displayName        = $DisplayName
        description        = 'Device-bound passkeys, FIDO2, WHfB cloud Kerberos trust, and x509 multi-factor only. Synced passkeys excluded — they do not meet AAL3.'
        policyType         = 'custom'
        requirementsSatisfied = 'mfa'
        allowedCombinations = @(
            'fido2'
            'windowsHelloForBusiness'
            'x509CertificateMultiFactor'
            'deviceBoundPasskey'
        )
    }

    if ($PSCmdlet.ShouldProcess($DisplayName, 'Create authentication strength policy')) {
        $existing = Get-MgPolicyAuthenticationStrengthPolicy -Filter "displayName eq '$DisplayName'" -ErrorAction SilentlyContinue
        if ($existing) {
            Write-Verbose "Policy '$DisplayName' already exists; updating allowedCombinations."
            Update-MgPolicyAuthenticationStrengthPolicy -AuthenticationStrengthPolicyId $existing.Id -BodyParameter $body
            return $existing
        }
        return New-MgPolicyAuthenticationStrengthPolicy -BodyParameter $body
    }
}
```

> **Why `deviceBoundPasskey` and not `passkey`?** Synced passkeys (iCloud Keychain, Google Password Manager) replicate private keys across devices and **do not meet AAL3**. Microsoft surfaces both as `passkey` in some UI strings; the Graph value `deviceBoundPasskey` is the only AAL3-aligned combination. Verify by inspecting the policy via `Get-MgPolicyAuthenticationStrengthPolicy` after authoring — under PowerShell 5.1 the `deviceBoundPasskey` element is silently dropped (see §0 defect #4).

## §4 — Named Locations

Named locations underpin the location-based exclusions in your CA grant logic and the regulator-required "approved jurisdictions" list. Two types: `ipNamedLocation` (CIDR ranges; supports `isTrusted=true` to bypass MFA from the corporate egress) and `countryNamedLocation` (ISO 3166 alpha-2 country codes; OFAC-aligned exclusions for sanctioned jurisdictions).

```powershell
function Set-Agt111NamedLocations {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Context,
        [string[]] $TrustedCidrs,
        [string[]] $BlockedCountries = @('CU','IR','KP','RU','SY','BY')
    )

    if ($TrustedCidrs -and $PSCmdlet.ShouldProcess('Trusted Corporate Egress','Create ipNamedLocation')) {
        $ipBody = @{
            '@odata.type' = '#microsoft.graph.ipNamedLocation'
            displayName   = 'FSI Trusted Corporate Egress'
            isTrusted     = $true
            ipRanges      = $TrustedCidrs | ForEach-Object {
                @{ '@odata.type' = '#microsoft.graph.iPv4CidrRange'; cidrAddress = $_ }
            }
        }
        New-MgIdentityConditionalAccessNamedLocation -BodyParameter $ipBody
    }

    if ($PSCmdlet.ShouldProcess('OFAC Blocked Jurisdictions','Create countryNamedLocation')) {
        $countryBody = @{
            '@odata.type'                     = '#microsoft.graph.countryNamedLocation'
            displayName                       = 'FSI OFAC-Blocked Jurisdictions'
            countriesAndRegions               = $BlockedCountries
            includeUnknownCountriesAndRegions = $true
            countryLookupMethod               = 'clientIpAddress'
        }
        New-MgIdentityConditionalAccessNamedLocation -BodyParameter $countryBody
    }
}

# Stale-location detector — flag named locations not referenced by any CA policy in >90 days
function Find-Agt111StaleNamedLocations {
    [CmdletBinding()] param([Parameter(Mandatory)] [pscustomobject] $Context)

    $locations = Get-MgIdentityConditionalAccessNamedLocation -All
    $policies  = Get-MgIdentityConditionalAccessPolicy -All
    $referenced = $policies.Conditions.Locations.IncludeLocations + $policies.Conditions.Locations.ExcludeLocations | Sort-Object -Unique

    $locations | Where-Object {
        $_.Id -notin $referenced -and ($_.ModifiedDateTime ?? $_.CreatedDateTime) -lt (Get-Date).AddDays(-90)
    } | Select-Object Id, DisplayName, ModifiedDateTime
}
```

---

## §5 — Conditional Access policies (ring-deployed, report-only first)

Author CA policies for AI agent users and admins using a **ring-deployed** model: every policy lands in `enabledForReportingButNotEnforced` mode, soaks for at least the org-defined report-only window, and is promoted to `enabled` only after a documented sign-in-log review. Production tenants must additionally guard against **break-glass collisions** — every CA policy must exclude the break-glass group.

```powershell
function New-Agt111CaPolicy {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Context,
        [Parameter(Mandatory)] [string]   $DisplayName,
        [Parameter(Mandatory)] [string[]] $IncludeUserGroupIds,
        [Parameter(Mandatory)] [string]   $AuthStrengthId,
        [string] $BreakGlassGroupId,
        [ValidateSet('enabledForReportingButNotEnforced','enabled','disabled')]
        [string] $State = 'enabledForReportingButNotEnforced'
    )

    # Break-glass guard — hard-fail if missing or under-staffed
    if (-not $BreakGlassGroupId) { throw "BreakGlassGroupId is mandatory. Refusing to author CA policy without break-glass exclusion." }
    $bg = Get-MgGroup -GroupId $BreakGlassGroupId -ErrorAction Stop
    $bgMembers = Get-MgGroupMember -GroupId $BreakGlassGroupId -All
    if ($bgMembers.Count -lt 2) {
        throw "Break-glass group '$($bg.DisplayName)' has $($bgMembers.Count) members. FSI baseline requires >= 2 break-glass accounts (Control 1.11)."
    }
    # Factor-collision check — break-glass accounts must NOT be enrolled in the same auth method this policy enforces
    foreach ($m in $bgMembers) {
        $methods = Get-MgUserAuthenticationMethod -UserId $m.Id
        if ($methods.AdditionalProperties.'@odata.type' -contains '#microsoft.graph.fido2AuthenticationMethod') {
            Write-Warning "Break-glass account $($m.AdditionalProperties.userPrincipalName) is FIDO2-enrolled. Verify hardware token custody and storage."
        }
    }

    $body = @{
        displayName = $DisplayName
        state       = $State
        conditions  = @{
            users = @{
                includeGroups = $IncludeUserGroupIds
                excludeGroups = @($BreakGlassGroupId)
            }
            applications  = @{ includeApplications = @('All') }
            signInRiskLevels = @('high','medium')
            clientAppTypes   = @('all')
        }
        grantControls = @{
            operator                    = 'AND'
            authenticationStrength      = @{ id = $AuthStrengthId }
            builtInControls             = @('compliantDevice')
        }
        sessionControls = @{
            signInFrequency = @{
                isEnabled       = $true
                type            = 'hours'
                value           = 4
                authenticationType = 'primaryAndSecondaryAuthentication'
            }
            continuousAccessEvaluation = @{ mode = 'strictEnforcement' }
            tokenProtectionEnforcementPolicy = @{ isEnabled = $true }   # Public Preview
        }
    }

    if ($PSCmdlet.ShouldProcess($DisplayName, "Create CA policy ($State)")) {
        New-MgBetaIdentityConditionalAccessPolicy -BodyParameter $body
    }
}

# Promotion gate — refuses to flip to 'enabled' unless report-only soak shows zero unintended blocks
function Enable-Agt111CaPolicy {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Context,
        [Parameter(Mandatory)] [string] $PolicyId,
        [int] $SoakDays = 7
    )
    $policy = Get-MgIdentityConditionalAccessPolicy -ConditionalAccessPolicyId $PolicyId
    if ($policy.State -ne 'enabledForReportingButNotEnforced') {
        throw "Policy '$($policy.DisplayName)' is not in report-only state. Refusing to enable."
    }
    if ($policy.ModifiedDateTime -gt (Get-Date).AddDays(-$SoakDays)) {
        throw "Policy '$($policy.DisplayName)' modified within last $SoakDays days. Soak period not met."
    }
    if ($PSCmdlet.ShouldProcess($policy.DisplayName, 'Promote to enabled')) {
        Update-MgIdentityConditionalAccessPolicy -ConditionalAccessPolicyId $PolicyId -State 'enabled'
    }
}
```

## §6 — Conditional Access for Workload Identities (service principals)

CA for Workload Identities (WID) is **GA**, but it requires the **Workload Identities Premium** add-on SKU (per service principal, per month). Without the SKU, policies appear authored in the portal and via Graph but **fail open** at evaluation time — a documented audit-blind failure mode. Always perform the SKU pre-flight before authoring any WID policy.

```powershell
function Test-Agt111WorkloadIdentitiesSku {
    [CmdletBinding()] param([Parameter(Mandatory)] [pscustomobject] $Context)

    $skus = Get-MgSubscribedSku -All
    $widSku = $skus | Where-Object { $_.SkuPartNumber -match 'WORKLOAD_IDENTITIES' }
    if (-not $widSku) {
        return [pscustomobject]@{ Present=$false; Consumed=0; Enabled=0; Note='Workload Identities Premium SKU not present in tenant.' }
    }
    [pscustomobject]@{
        Present  = $true
        Consumed = $widSku.ConsumedUnits
        Enabled  = $widSku.PrepaidUnits.Enabled
        SkuId    = $widSku.SkuId
    }
}

function New-Agt111CaWorkloadIdentityPolicy {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Context,
        [Parameter(Mandatory)] [string]   $DisplayName,
        [Parameter(Mandatory)] [string[]] $ServicePrincipalIds,
        [Parameter(Mandatory)] [string[]] $TrustedNamedLocationIds
    )

    $sku = Test-Agt111WorkloadIdentitiesSku -Context $Context
    if (-not $sku.Present) {
        Write-Warning "Workload Identities Premium SKU absent. Skipping CA WID authoring — policies would silently fail open."
        return
    }
    if ($sku.Consumed -ge $sku.Enabled) {
        Write-Warning "Workload Identities Premium consumed ($($sku.Consumed)) >= enabled ($($sku.Enabled)). New SP assignments may not protect."
    }

    $body = @{
        displayName = $DisplayName
        state       = 'enabledForReportingButNotEnforced'
        conditions  = @{
            clientApplications = @{
                includeServicePrincipals = $ServicePrincipalIds
            }
            applications = @{ includeApplications = @('All') }
            locations    = @{
                includeLocations = @('All')
                excludeLocations = $TrustedNamedLocationIds
            }
        }
        grantControls = @{
            operator        = 'OR'
            builtInControls = @('block')
        }
    }

    if ($PSCmdlet.ShouldProcess($DisplayName, 'Create CA policy for workload identities')) {
        New-MgBetaIdentityConditionalAccessPolicy -BodyParameter $body
    }
}
```

> **Caveat.** As of April 2026, CA WID supports `block` and `grantControls` for tokens issued under the client_credentials flow only. On-behalf-of and authorization-code flows for service principals are not yet covered. Verify scope against current Microsoft Learn before authoring.

---

## §7 — Entra Agent ID (Public Preview) and custom security attributes

Entra Agent ID is a Public Preview directory object representing autonomous AI agents (Microsoft 365 Copilot agents, Copilot Studio agents, Azure AI Foundry agents). There is **no typed PowerShell cmdlet** as of April 2026 — call the beta REST API via `Invoke-MgGraphRequest`. Tag every agent with the three custom security attributes: `AgentZone` (1/2/3), `AgentSponsor` (UPN), `AgentRiskTier` (low/medium/high).

```powershell
function Initialize-Agt111CustomSecurityAttributes {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param([Parameter(Mandatory)] [pscustomobject] $Context)

    $setName = 'AgentGovernance'
    $set = Get-MgDirectoryAttributeSet -AttributeSetId $setName -ErrorAction SilentlyContinue
    if (-not $set -and $PSCmdlet.ShouldProcess($setName, 'Create attribute set')) {
        New-MgDirectoryAttributeSet -BodyParameter @{
            id = $setName; description = 'FSI AI Agent Governance attributes'; maxAttributesPerSet = 25
        }
    }

    $defs = @(
        @{ name='AgentZone';     type='String'; allowed=@('Zone1','Zone2','Zone3'); multi=$false }
        @{ name='AgentSponsor';  type='String'; allowed=@();                         multi=$false }
        @{ name='AgentRiskTier'; type='String'; allowed=@('Low','Medium','High');    multi=$false }
    )
    foreach ($d in $defs) {
        $defId = "${setName}_$($d.name)"
        $existing = Get-MgDirectoryCustomSecurityAttributeDefinition -CustomSecurityAttributeDefinitionId $defId -ErrorAction SilentlyContinue
        if (-not $existing -and $PSCmdlet.ShouldProcess($defId, 'Create custom security attribute definition')) {
            $body = @{
                attributeSet         = $setName
                name                 = $d.name
                description          = "Agent governance — $($d.name)"
                type                 = $d.type
                status               = 'Available'
                isCollection         = $d.multi
                isSearchable         = $true
                usePreDefinedValuesOnly = ($d.allowed.Count -gt 0)
            }
            $created = New-MgDirectoryCustomSecurityAttributeDefinition -BodyParameter $body
            foreach ($v in $d.allowed) {
                Invoke-MgGraphRequest -Method POST `
                    -Uri "https://graph.microsoft.com/v1.0/directory/customSecurityAttributeDefinitions/$($created.Id)/allowedValues" `
                    -Body (@{ id=$v; isActive=$true } | ConvertTo-Json)
            }
        }
    }
}

function Get-Agt111Agents {
    [CmdletBinding()] param([Parameter(Mandatory)] [pscustomobject] $Context)

    # Beta REST — no typed cmdlet for /beta/agents as of April 2026
    $uri = "$($Context.Endpoint)/beta/agents"
    $all = @()
    do {
        $resp = Invoke-MgGraphRequest -Method GET -Uri $uri -ErrorAction Stop
        $all += $resp.value
        $uri  = $resp.'@odata.nextLink'
    } while ($uri)
    $all
}

function Get-Agt111ManagedPolicies {
    [CmdletBinding()] param([Parameter(Mandatory)] [pscustomobject] $Context)

    # Microsoft Managed CA Policies — filter by Source = Microsoft (no separate menu in portal)
    Get-MgBetaIdentityConditionalAccessPolicy -All |
        Where-Object { $_.AdditionalProperties.source -eq 'Microsoft' } |
        Select-Object Id, DisplayName, State, CreatedDateTime, ModifiedDateTime
}
```

> **Caveat.** The `/beta/agents` endpoint surface, response schema, and required scope (`Agent.ReadWrite.All`) are all Public Preview and may change without notice. Pin your runtime to a specific Graph beta build via the `Microsoft.Graph.Beta.*` module versions in §1, and re-verify after every Graph release wave.

## §8 — PIM eligibility for CA-capable roles

Permanent assignments of Conditional Access Administrator, Authentication Administrator, and Privileged Authentication Administrator are an FSI audit finding. Use PIM eligibility with **MFA-on-activation** (via authentication context) and bounded activation windows: 4 hours for Authentication-class roles, 8 hours for Conditional Access-class roles.

```powershell
function New-Agt111PimEligibility {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Context,
        [Parameter(Mandatory)] [string] $PrincipalId,
        [Parameter(Mandatory)] [ValidateSet('Conditional Access Administrator','Authentication Administrator','Privileged Authentication Administrator','Cloud Application Administrator')]
        [string] $RoleName,
        [ValidateSet('PT4H','PT8H')] [string] $Duration = 'PT8H',
        [string] $Justification = 'Control 1.11 baseline — eligible assignment for CA operator'
    )

    $role = Get-MgRoleManagementDirectoryRoleDefinition -Filter "displayName eq '$RoleName'"
    if (-not $role) { throw "Role '$RoleName' not found." }

    $body = @{
        action            = 'adminAssign'
        justification     = $Justification
        roleDefinitionId  = $role.Id
        directoryScopeId  = '/'
        principalId       = $PrincipalId
        scheduleInfo      = @{
            startDateTime = (Get-Date).ToUniversalTime().ToString('o')
            expiration    = @{
                type     = 'afterDuration'
                duration = $Duration
            }
        }
    }

    if ($PSCmdlet.ShouldProcess("$PrincipalId as eligible $RoleName", 'Create PIM eligibility')) {
        New-MgRoleManagementDirectoryRoleEligibilityScheduleRequest -BodyParameter $body
    }
}
```

> **MFA-on-activation.** Configure the role's PIM activation policy (via portal or `Update-MgPolicyRoleManagementPolicyRule`) to require an authentication context that maps to your phishing-resistant strength from §3. Cmdlet-only configuration of PIM activation rules is fragile; the verification step (§11) confirms the activation policy is in place.

---

## §9 — Sign-in audit pull with proper paging

The Graph sign-in logs endpoint returns at most 1,000 records per page. The single most common evidence-collection defect for this control is using `-Top 100` and assuming the result is exhaustive. **Always** use `-All` (which transparently follows `@odata.nextLink`) or implement the paging loop yourself.

```powershell
function Get-Agt111CaEnforcementResults {
    [CmdletBinding()] param(
        [Parameter(Mandatory)] [pscustomobject] $Context,
        [datetime] $Since = (Get-Date).AddDays(-30),
        [string] $UserUpnFilter
    )

    $filter = "createdDateTime ge $($Since.ToUniversalTime().ToString('o'))"
    if ($UserUpnFilter) { $filter += " and userPrincipalName eq '$UserUpnFilter'" }

    # CRITICAL: -All performs the @odata.nextLink walk. Never -Top 100.
    $signins = Get-MgBetaAuditLogSignIn -Filter $filter -All

    $signins | ForEach-Object {
        foreach ($appliedCa in ($_.AppliedConditionalAccessPolicies)) {
            [pscustomobject]@{
                CorrelationId        = $_.CorrelationId
                CreatedDateTime      = $_.CreatedDateTime
                UserPrincipalName    = $_.UserPrincipalName
                AppDisplayName       = $_.AppDisplayName
                IpAddress            = $_.IpAddress
                ConditionalAccessStatus = $_.ConditionalAccessStatus
                CaPolicyId           = $appliedCa.Id
                CaPolicyName         = $appliedCa.DisplayName
                CaResult             = $appliedCa.Result      # success / failure / notApplied / reportOnlySuccess / reportOnlyFailure
                EnforcedGrantControls= ($appliedCa.EnforcedGrantControls -join ',')
                AuthMethod           = $_.AuthenticationDetails.AuthenticationMethod -join ','
            }
        }
    }
}

function Test-Agt111BreakGlassUsage {
    [CmdletBinding()] param(
        [Parameter(Mandatory)] [pscustomobject] $Context,
        [Parameter(Mandatory)] [string[]] $BreakGlassUpns,
        [datetime] $Since = (Get-Date).AddDays(-90)
    )

    $usage = foreach ($upn in $BreakGlassUpns) {
        Get-MgBetaAuditLogSignIn -Filter "userPrincipalName eq '$upn' and createdDateTime ge $($Since.ToUniversalTime().ToString('o'))" -All
    }
    if (-not $usage) {
        Write-Warning "No break-glass sign-ins observed in last $((Get-Date) - $Since | Select-Object -ExpandProperty Days) days. FSI baseline requires quarterly alternating test."
    }
    $usage | Select-Object CreatedDateTime, UserPrincipalName, IpAddress, AppDisplayName, ConditionalAccessStatus
}
```

## §10 — SHA-256 evidence manifest: `Write-Agt111Evidence`

Every artefact emitted by this playbook (CA policy JSON, auth strength JSON, sign-in CSV, validation report) must be hashed and recorded in a chain-of-custody manifest. SEC Rule 17a-4(f) and FINRA Rule 4511 require WORM-equivalent retention of supervisory evidence; SHA-256 over UTF-8 content is the firm-side integrity check before write to immutable storage.

```powershell
function Write-Agt111Evidence {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Context,
        [Parameter(Mandatory)] [string] $ArtefactName,
        [Parameter(Mandatory)] $Content,
        [ValidateSet('json','csv','txt')] [string] $Format = 'json'
    )

    $path = Join-Path $Context.EvidenceDir "$ArtefactName.$Format"
    $serialised = switch ($Format) {
        'json' { $Content | ConvertTo-Json -Depth 12 }
        'csv'  { $Content | ConvertTo-Csv -NoTypeInformation | Out-String }
        'txt'  { $Content | Out-String }
    }

    if ($PSCmdlet.ShouldProcess($path, 'Write evidence artefact')) {
        # UTF-8 NO BOM — required for hash reproducibility across platforms
        $utf8 = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($path, $serialised, $utf8)
    }

    $hash = (Get-FileHash -Path $path -Algorithm SHA256).Hash

    # Append to manifest
    $manifestPath = Join-Path $Context.EvidenceDir 'manifest.jsonl'
    $entry = [pscustomobject]@{
        RunId          = $Context.RunId
        TenantId       = $Context.TenantId
        Cloud          = $Context.Cloud
        OperatorUpn    = $Context.OperatorUpn
        ArtefactName   = $ArtefactName
        Path           = $path
        SizeBytes      = (Get-Item $path).Length
        Sha256         = $hash
        ModuleVersions = $Context.ModuleVersions
        WrittenUtc     = (Get-Date).ToUniversalTime().ToString('o')
    }
    Add-Content -Path $manifestPath -Value ($entry | ConvertTo-Json -Compress -Depth 6) -Encoding utf8

    # Manifest hash-of-hashes — chain-of-custody anchor
    $manifestHash = (Get-FileHash -Path $manifestPath -Algorithm SHA256).Hash
    Set-Content -Path (Join-Path $Context.EvidenceDir 'manifest.sha256') -Value $manifestHash -Encoding ascii

    [pscustomobject]@{ Path=$path; Sha256=$hash; ManifestSha256=$manifestHash }
}
```

---

## §11 — Validation: `Test-Agt111Implementation`

Returns one row per check. Exit code 0 = all pass, 1 = warnings, 2 = blockers.

```powershell
function Test-Agt111Implementation {
    [CmdletBinding()]
    param([Parameter(Mandatory)] [pscustomobject] $Context)

    $results = @()

    # 1. Phishing-resistant strength exists and contains AAL3 combinations only
    $strength = Get-MgPolicyAuthenticationStrengthPolicy -All | Where-Object DisplayName -like 'FSI Phishing-Resistant*'
    $aal3Set = @('fido2','windowsHelloForBusiness','x509CertificateMultiFactor','deviceBoundPasskey')
    $bad = $strength.AllowedCombinations | Where-Object { $_ -notin $aal3Set }
    $results += [pscustomobject]@{
        Check='Phishing-resistant auth strength is AAL3-only'; Pass=($strength -and -not $bad)
        Details="Combinations: $($strength.AllowedCombinations -join ',')"; Severity='Blocker'
    }

    # 2. Every CA policy excludes the break-glass group
    $policies = Get-MgIdentityConditionalAccessPolicy -All | Where-Object State -ne 'disabled'
    $bgMissing = $policies | Where-Object { $_.Conditions.Users.ExcludeGroups.Count -eq 0 }
    $results += [pscustomobject]@{
        Check='All enabled CA policies exclude break-glass group'; Pass=($bgMissing.Count -eq 0)
        Details="Missing exclusion: $(($bgMissing.DisplayName) -join ', ')"; Severity='Blocker'
    }

    # 3. No CA policy stuck in report-only > 30 days (operator must promote or retire)
    $stale = $policies | Where-Object {
        $_.State -eq 'enabledForReportingButNotEnforced' -and $_.ModifiedDateTime -lt (Get-Date).AddDays(-30)
    }
    $results += [pscustomobject]@{
        Check='No CA policy stuck in report-only >30d'; Pass=($stale.Count -eq 0)
        Details="Stale: $(($stale.DisplayName) -join ', ')"; Severity='Warning'
    }

    # 4. Workload Identities Premium SKU present (warn-only — some tenants deliberately defer)
    $sku = Test-Agt111WorkloadIdentitiesSku -Context $Context
    $results += [pscustomobject]@{
        Check='Workload Identities Premium SKU present'; Pass=$sku.Present
        Details="Consumed=$($sku.Consumed) of $($sku.Enabled)"; Severity='Warning'
    }

    # 5. Custom security attribute set 'AgentGovernance' exists with all 3 definitions
    $set = Get-MgDirectoryAttributeSet -AttributeSetId 'AgentGovernance' -ErrorAction SilentlyContinue
    $defs = if ($set) { Get-MgDirectoryCustomSecurityAttributeDefinition -All | Where-Object AttributeSet -eq 'AgentGovernance' } else { @() }
    $needed = @('AgentZone','AgentSponsor','AgentRiskTier')
    $missing = $needed | Where-Object { $_ -notin $defs.Name }
    $results += [pscustomobject]@{
        Check='AgentGovernance custom security attributes defined'; Pass=($missing.Count -eq 0)
        Details="Missing: $($missing -join ',')"; Severity='Blocker'
    }

    # 6. Auth Methods Policy migration complete
    $amp = Invoke-MgGraphRequest -Method GET -Uri "$($Context.Endpoint)/v1.0/policies/authenticationMethodsPolicy" -ErrorAction SilentlyContinue
    $results += [pscustomobject]@{
        Check='Authentication Methods Policy migration complete'; Pass=($amp.policyMigrationState -eq 'migrationComplete')
        Details="State=$($amp.policyMigrationState)"; Severity='Blocker'
    }

    # 7. Evidence directory has a manifest with at least one entry
    $manifest = Join-Path $Context.EvidenceDir 'manifest.jsonl'
    $hasManifest = (Test-Path $manifest) -and ((Get-Item $manifest).Length -gt 0)
    $results += [pscustomobject]@{
        Check='Evidence manifest emitted for this run'; Pass=$hasManifest
        Details="Path=$manifest"; Severity='Warning'
    }

    Write-Agt111Evidence -Context $Context -ArtefactName 'validation-report' -Content $results -Format json | Out-Null

    $blockers = $results | Where-Object { -not $_.Pass -and $_.Severity -eq 'Blocker' }
    $warnings = $results | Where-Object { -not $_.Pass -and $_.Severity -eq 'Warning' }
    $exit = if ($blockers) { 2 } elseif ($warnings) { 1 } else { 0 }
    $results | Format-Table -AutoSize
    Write-Host ""
    Write-Host "Validation exit code: $exit (0=clean, 1=warnings, 2=blockers)"
    return $exit
}
```

## §12 — Sovereign cloud variants

| Cloud | `Connect-MgGraph -Environment` | Graph endpoint | Notes |
|-------|--------------------------------|----------------|-------|
| Commercial | `Global` | `https://graph.microsoft.com` | Default for non-federal tenants |
| GCC | `USGov` | `https://graph.microsoft.us` | M365 GCC (commercial-side compliance) |
| GCC High | `USGovDoD` | `https://dod-graph.microsoft.us` | Verify per Microsoft Learn — historically Microsoft has used both `USGov` and `USGovDoD` for GCC High; current April 2026 guidance is `USGovDoD` |
| DoD | `USGovDoD` | `https://dod-graph.microsoft.us` | DoD IL5 tenants |

**Cmdlet parity caveats (April 2026):**

- **GCC High / DoD:** `Get-MgBetaAuditLogSignIn` returns sign-ins, but the `appliedConditionalAccessPolicies.authenticationStrength` sub-property may be omitted. Validate by sampling one known-good sign-in before relying on it for evidence.
- **GCC High / DoD:** Entra Agent ID (`/beta/agents`) is **not yet available** in federal clouds as of April 2026. Skip §7 agent enumeration; the custom security attribute definitions still apply.
- **GCC:** Token Protection (Public Preview) lights up with the same `tokenProtectionEnforcementPolicy` body but enforcement engine roll-out lags Commercial by ~one release wave.
- **All federal clouds:** `Microsoft.Graph.Beta.*` modules ship with the same code paths but feature flags differ. Pin to module version 2.20.0+ which contains the federal endpoint table.

Organizations should verify the cloud-to-environment mapping against current [Microsoft Graph national cloud deployments](https://learn.microsoft.com/graph/deployments) before each release.

---

## §13 — Anti-patterns and false-clean defects

The following 25 anti-patterns are documented audit findings or operator missteps. Each row lists the wrong approach, why it produces a false-clean, and the corrective control.

| # | Anti-pattern | Why it false-cleans | Corrective control |
|---|--------------|---------------------|--------------------|
| 1 | Running this playbook under PowerShell 5.1 | Several Graph cmdlets silently drop properties (see §0 table) | §0 wrong-shell guard |
| 2 | Floating module versions (`Install-Module Microsoft.Graph` without `-RequiredVersion`) | Evidence is non-reproducible; Graph behaviour drifts release-to-release | §1 pinned-version installer |
| 3 | Calling `Connect-MgGraph` without `-Environment` on a GCC High tenant | Defaults to Commercial Graph; tenant data is not retrieved, but cmdlets return empty success | §2 `Initialize-Agt111Session` cloud map |
| 4 | Using `passkey` instead of `deviceBoundPasskey` in auth strength | Synced (cloud-replicated) passkeys do not meet AAL3 | §3 `New-Agt111PhishResistantStrength` |
| 5 | Authoring CA policy in `enabled` state without report-only soak | Production sign-in disruption; rollback churn | §5 `enabledForReportingButNotEnforced` default + §5 promotion gate |
| 6 | CA policy without break-glass exclusion | Single auth-method failure locks out all admins; documented FSI lock-out incident | §5 break-glass guard with hard-fail |
| 7 | Break-glass group with <2 members | No alternating quarterly test possible; single-key dependency | §5 member-count check |
| 8 | Break-glass account enrolled in the same FIDO2 token model the CA policy enforces | Token vendor outage = total lock-out (factor collision) | §5 factor-collision check |
| 9 | Authoring CA WID policy without Workload Identities Premium SKU | Policies appear authored; evaluation engine fails open | §6 `Test-Agt111WorkloadIdentitiesSku` pre-flight |
| 10 | Using `-Top 100` on `Get-MgBetaAuditLogSignIn` | Truncated evidence; missed CA failures beyond the first page | §9 `-All` paging |
| 11 | Treating Entra Agent ID GA in evidence narratives | Agent ID is Public Preview; schema is unstable | §7 explicit Preview caveat in evidence |
| 12 | Searching for "Microsoft Managed Policies" as a separate menu | They live in the standard CA list with `Source = Microsoft` | §7 `Get-Agt111ManagedPolicies` filter |
| 13 | Permanent assignment of Conditional Access Administrator | Audit finding; violates least-privilege baseline | §8 PIM eligibility |
| 14 | PIM eligibility without MFA-on-activation | Compromised refresh token can self-elevate without re-auth | §8 authentication-context-bound activation |
| 15 | Activation duration > 8 hours | Exceeds FSI baseline; extended privileged session | §8 `PT4H`/`PT8H` enum |
| 16 | Trusting `$_.AppliedConditionalAccessPolicies` count alone for "did CA fire?" | Some sign-ins record `notApplied` for all policies (no targeted user/app match) | §9 inspect `Result` per policy, not count |
| 17 | Using ASCII-with-BOM or UTF-16 for evidence files | Hash differs across hosts; chain-of-custody breaks | §10 explicit UTF-8 NO BOM |
| 18 | Hashing only the per-artefact files but not the manifest | Manifest tampering undetectable | §10 `manifest.sha256` hash-of-hashes |
| 19 | Not recording module versions in the evidence context | Cannot reproduce evidence after a Graph SDK update | §10 `ModuleVersions` field |
| 20 | Promoting CA policy from report-only without sign-in-log review | Unintended block events surface in production | §5 `Enable-Agt111CaPolicy` soak gate |
| 21 | Allowing `policyMigrationState != migrationComplete` | Legacy MFA/SSPR surface ignores CA grant logic | §0 + §11 check #6 |
| 22 | Hard-coding tenant or CIDR ranges in scripts | Drift between dev/prod; secret leakage in commits | Parameterise via `$Context` and external config |
| 23 | Using `Update-MgIdentityConditionalAccessPolicy -State enabled` directly without checking soak duration | Bypasses §5 promotion gate | §5 `Enable-Agt111CaPolicy` |
| 24 | Skipping the operator UPN check in `Initialize-Agt111Session` | Wrong account silently authors policies under shared workstation | §2 UPN equality check |
| 25 | No quarterly break-glass usage test recorded in evidence | Audit finding under FFIEC IT Handbook; cannot prove operability | §9 `Test-Agt111BreakGlassUsage` and quarterly run cadence |

---

## End-to-end runner

```powershell
$ctx = Initialize-Agt111Session -Cloud 'Commercial' -OperatorUpn 'admin@contoso.com' -TenantId '00000000-0000-0000-0000-000000000000'

Initialize-Agt111CustomSecurityAttributes -Context $ctx
$strength = New-Agt111PhishResistantStrength -Context $ctx
Set-Agt111NamedLocations -Context $ctx -TrustedCidrs @('203.0.113.0/24')
$pol = New-Agt111CaPolicy -Context $ctx -DisplayName 'FSI Agent Operators — AAL3' `
    -IncludeUserGroupIds @('<group-id>') -AuthStrengthId $strength.Id -BreakGlassGroupId '<bg-group-id>'
New-Agt111CaWorkloadIdentityPolicy -Context $ctx -DisplayName 'FSI Agent SPNs — Block Untrusted' `
    -ServicePrincipalIds @('<sp-id>') -TrustedNamedLocationIds @('<loc-id>')
$signins = Get-Agt111CaEnforcementResults -Context $ctx -Since (Get-Date).AddDays(-7)
Write-Agt111Evidence -Context $ctx -ArtefactName 'signins-7d' -Content $signins -Format csv | Out-Null

$exit = Test-Agt111Implementation -Context $ctx
exit $exit
```

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
