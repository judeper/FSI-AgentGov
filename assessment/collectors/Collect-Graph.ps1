<#
.SYNOPSIS
    Collects Microsoft Graph / Entra ID configuration data for FSI Agent Governance assessment.

.DESCRIPTION
    Enumerates Conditional Access policies, FSI-Agent security groups, privileged role
    assignments, Copilot Studio service principals, tenant security settings, and
    AI-leadership job titles via Microsoft Graph.

    Outputs a structured JSON file (graph.json) consumed by the assessment engine.

    Pattern references:
      - restrict-agent-publishing.ps1 — CA policy validation patterns
      - Invoke-HardeningBaselineCheck.ps1 — tenant settings, security group checks
      - Invoke-SharingAudit.ps1 — cross-tenant access pattern for principal classification

.PARAMETER TenantId
    Mandatory. Microsoft Entra tenant ID.

.PARAMETER AuthMode
    Mandatory. Authentication mode: Interactive or ServicePrincipal.

.PARAMETER ClientId
    Optional. Application (client) ID for service principal authentication.

.PARAMETER ClientSecret
    Optional. Client secret as SecureString for service principal authentication.

.PARAMETER OutputDir
    Mandatory. Root output directory. Collected JSON is written to $OutputDir\collected\graph.json.

.OUTPUTS
    graph.json — JSON file with CA policies, security groups, privileged roles,
    service principals, information barriers, tenant settings, and AI-leadership users.

.NOTES
    Part of the FSI Agent Governance Assessment Engine — Graph Collector.
    Required Graph scopes: Policy.Read.All, Group.Read.All, Directory.Read.All,
    AuditLog.Read.All, User.Read.All.
    Exit codes: 0 = success, 1 = partial failure (some sections null), 2 = total failure.
    Version: 1.1.0
#>

#Requires -Version 7.0

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$TenantId,

    [Parameter(Mandatory)]
    [ValidateSet('Interactive', 'ServicePrincipal')]
    [string]$AuthMode,

    [Parameter()]
    [string]$ClientId,

    [Parameter()]
    [securestring]$ClientSecret,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$OutputDir
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ─── Initialise ──────────────────────────────────────────────────────
$warnings = [System.Collections.Generic.List[string]]::new()
$collectedDir = Join-Path $OutputDir 'collected'
if (-not (Test-Path $collectedDir)) {
    New-Item -ItemType Directory -Path $collectedDir -Force | Out-Null
}
$outputFile = Join-Path $collectedDir 'graph.json'

function Invoke-CollectorOperation {
    param(
        [Parameter(Mandatory)][string]$Target,
        [Parameter(Mandatory)][string]$Action,
        [Parameter(Mandatory)][scriptblock]$ScriptBlock
    )

    if (-not $PSCmdlet.ShouldProcess($Target, $Action)) {
        Write-Verbose "Skipping $Action on $Target because -WhatIf was specified."
        return $null
    }

    & $ScriptBlock
}

# ─── Module Imports ──────────────────────────────────────────────────
Import-Module Microsoft.Graph.Authentication    -ErrorAction Stop
Import-Module Microsoft.Graph.Identity.SignIns  -ErrorAction Stop
Import-Module Microsoft.Graph.Groups            -ErrorAction Stop
Write-Verbose "Loaded Microsoft.Graph modules."

# ─── Authentication ──────────────────────────────────────────────────
# Interactive: delegated with scopes. ServicePrincipal: client credential flow.
$requiredScopes = @('Policy.Read.All', 'Group.Read.All', 'Directory.Read.All', 'AuditLog.Read.All')

Write-Verbose "Authenticating to Microsoft Graph in $AuthMode mode..."

if ($AuthMode -eq 'Interactive') {
    Invoke-CollectorOperation -Target "Microsoft Graph tenant $TenantId" -Action 'Connect to Microsoft Graph (interactive)' -ScriptBlock {
        Connect-MgGraph -TenantId $TenantId -Scopes $requiredScopes -ErrorAction Stop
    } | Out-Null
}
else {
    if (-not $ClientId -or -not $ClientSecret) {
        throw "ServicePrincipal auth requires -ClientId and -ClientSecret parameters."
    }
    $credential = [System.Management.Automation.PSCredential]::new($ClientId, $ClientSecret)
    $body = @{
        client_id     = $ClientId
        scope         = 'https://graph.microsoft.com/.default'
        client_secret = ConvertFrom-SecureString $ClientSecret -AsPlainText
        grant_type    = 'client_credentials'
    }
    # Use Connect-MgGraph with client secret credential
    Invoke-CollectorOperation -Target "Microsoft Graph tenant $TenantId" -Action 'Connect to Microsoft Graph (service principal)' -ScriptBlock {
        Connect-MgGraph -TenantId $TenantId -ClientSecretCredential $credential -ErrorAction Stop
    } | Out-Null
}

Write-Verbose "Microsoft Graph authentication stage complete."

# ═══════════════════════════════════════════════════════════════════════
# Section 1: Conditional Access Policies
# Supports: Control 1.11 (Conditional Access and Phishing-Resistant MFA),
#           Control 1.29 (Global Secure Access network policy dependencies)
# Pattern: restrict-agent-publishing.ps1 — CA policy evaluation
# ═══════════════════════════════════════════════════════════════════════
$conditionalAccessPolicies = $null
try {
    Write-Verbose "Section 1: Collecting Conditional Access policies..."
    $rawPolicies = Invoke-CollectorOperation -Target "Microsoft Graph tenant $TenantId" -Action 'List conditional access policies' -ScriptBlock {
        Get-MgIdentityConditionalAccessPolicy -All -ErrorAction Stop
    }
    $conditionalAccessPolicies = $rawPolicies | ForEach-Object {
        [PSCustomObject]@{
            Id                    = $_.Id
            DisplayName           = $_.DisplayName
            State                 = $_.State
            IncludeApplications   = $_.Conditions.Applications.IncludeApplications
            ExcludeApplications   = $_.Conditions.Applications.ExcludeApplications
            IncludeUsers          = $_.Conditions.Users.IncludeUsers
            ExcludeUsers          = $_.Conditions.Users.ExcludeUsers
            IncludeGroups         = $_.Conditions.Users.IncludeGroups
            ExcludeGroups         = $_.Conditions.Users.ExcludeGroups
            BuiltInControls       = $_.GrantControls.BuiltInControls
            Operator              = $_.GrantControls.Operator
            SignInFrequency       = $_.SessionControls.SignInFrequency
            PersistentBrowser     = $_.SessionControls.PersistentBrowser
        }
    }
    Write-Verbose "  Collected $($conditionalAccessPolicies.Count) CA policy/policies."
}
catch {
    $warnings.Add("Section 1 (Conditional Access) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 2: FSI-Agent Security Groups
# Supports: Control 1.1 (Restrict Agent Publishing by Authorization)
# Pattern: Invoke-HardeningBaselineCheck.ps1 Item 17 (Security Groups)
# ═══════════════════════════════════════════════════════════════════════
$fsiSecurityGroups = $null
try {
    Write-Verbose "Section 2: Collecting FSI-Agent-* security groups..."
    $rawGroups = Invoke-CollectorOperation -Target "Microsoft Graph tenant $TenantId" -Action 'List FSI-Agent security groups' -ScriptBlock {
        Get-MgGroup -Filter "startsWith(displayName,'FSI-Agent-')" -ConsistencyLevel eventual -CountVariable fsiSecurityGroupCount -All `
            -Property Id, DisplayName, SecurityEnabled, GroupTypes, MembershipRule -ErrorAction Stop
    }

    $fsiSecurityGroups = foreach ($grp in $rawGroups) {
        # Get member count via a separate call
        $memberCount = 0
        try {
            $members = Invoke-CollectorOperation -Target $grp.Id -Action 'List group members' -ScriptBlock {
                Get-MgGroupMember -GroupId $grp.Id -All -ErrorAction Stop
            }
            $memberCount = @($members).Count
        }
        catch {
            $warnings.Add("Member count for group '$($grp.DisplayName)' failed: $($_.Exception.Message)")
            Write-Warning $warnings[-1]
        }
        [PSCustomObject]@{
            Id               = $grp.Id
            DisplayName      = $grp.DisplayName
            SecurityEnabled  = $grp.SecurityEnabled
            GroupTypes       = $grp.GroupTypes
            MembershipRule   = $grp.MembershipRule
            MemberCount      = $memberCount
        }
    }
    Write-Verbose "  Collected $(@($fsiSecurityGroups).Count) FSI-Agent security group(s)."
}
catch {
    $warnings.Add("Section 2 (FSI-Agent Security Groups) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 3: Information Barrier Policies
# Supports: Data isolation, ethical wall requirements
# Note: Requires Purview/Exchange Online module; attempt Graph fallback.
# ═══════════════════════════════════════════════════════════════════════
$informationBarriers = $null
try {
    Write-Verbose "Section 3: Collecting Information Barrier policies..."
    # Try ExchangeOnlineManagement cmdlet if available
    $ibModule = Get-Module -ListAvailable -Name ExchangeOnlineManagement -ErrorAction SilentlyContinue
    if ($ibModule) {
        Import-Module ExchangeOnlineManagement -ErrorAction Stop
        $rawIb = Invoke-CollectorOperation -Target "Microsoft Graph tenant $TenantId" -Action 'List information barrier policies' -ScriptBlock {
            Get-InformationBarrierPolicy -ErrorAction Stop
        }
        $informationBarriers = $rawIb | ForEach-Object {
            [PSCustomObject]@{
                Identity     = $_.Identity
                DisplayName  = $_.Name
                State        = $_.State
                Segments     = $_.AssignedSegment
            }
        }
        Write-Verbose "  Collected $(@($informationBarriers).Count) IB policy/policies."
    }
    else {
        $informationBarriers = @{ available = $false; reason = 'ExchangeOnlineManagement module not installed — IB policies cannot be collected via Graph alone.' }
        $warnings.Add("Section 3 (Information Barriers): ExchangeOnlineManagement module unavailable; IB data not collected.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 3 (Information Barriers) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 4: Privileged Role Assignments
# Supports: Control 1.18 (Application-Level Authorization and RBAC),
#           Control 2.8 (Access Control and Segregation of Duties)
# ═══════════════════════════════════════════════════════════════════════
$privilegedRoleAssignments = $null
try {
    Write-Verbose "Section 4: Collecting privileged role assignments..."

    # Target roles: Power Platform Admin and Dynamics 365 Admin
    $targetRoleNames = @('Power Platform Administrator', 'Dynamics 365 Administrator')

    # Get all role definitions to map IDs to names
    $roleDefinitions = Invoke-CollectorOperation -Target "Microsoft Graph tenant $TenantId" -Action 'List privileged role definitions' -ScriptBlock {
        Get-MgRoleManagementDirectoryRoleDefinition -All -ErrorAction Stop
    }
    $targetRoles = $roleDefinitions | Where-Object { $targetRoleNames -contains $_.DisplayName }

    $privilegedRoleAssignments = foreach ($role in $targetRoles) {
        $assignments = Invoke-CollectorOperation -Target $role.Id -Action 'List privileged role assignments' -ScriptBlock {
            Get-MgRoleManagementDirectoryRoleAssignment -Filter "roleDefinitionId eq '$($role.Id)'" -All -ErrorAction Stop
        }
        foreach ($assignment in $assignments) {
            [PSCustomObject]@{
                RoleDefinitionId   = $role.Id
                RoleName           = $role.DisplayName
                PrincipalId        = $assignment.PrincipalId
                DirectoryScopeId   = $assignment.DirectoryScopeId
            }
        }
    }
    Write-Verbose "  Collected $(@($privilegedRoleAssignments).Count) privileged role assignment(s)."
}
catch {
    $warnings.Add("Section 4 (Privileged Role Assignments) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 5: M365 Integrated Apps — Copilot Studio Service Principals
# Supports: Control 1.2 (Agent Registry and Integrated Apps Management),
#           Control 3.1 (Agent Inventory and Metadata Management)
# ═══════════════════════════════════════════════════════════════════════
$copilotServicePrincipals = $null
try {
    Write-Verbose "Section 5: Collecting Copilot Studio service principals..."

    # Primary lookup by stable AppIds (Microsoft Copilot Studio current + PVA legacy x2)
    # Display-name lookups miss tenants where the SPs have been rebranded from
    # "Power Virtual Agents" to "Microsoft Copilot Studio". AppIds are stable across
    # the rebrand. Display-name filter retained below as fallback for tenants
    # without any of these AppIds provisioned.
    $copilotAppIds = @(
        '38e57bc7-9498-4bcc-b6b6-37001619bd96',  # Microsoft Copilot Studio (current)
        '96ff4394-9197-43aa-b393-6a41652e21f8',  # Power Virtual Agents (legacy)
        '5bdf5494-2491-4cb6-b4f9-92dbed25ff86',  # Power Virtual Agents Service (legacy)
        '38e15ad7-bb74-4ac3-9aef-f4b720b51c20'   # Power Virtual Agents Service (Copilot Studio runtime; per 1.11 CA templates)
    )
    $appIdFilter = "appId in ('{0}')" -f ($copilotAppIds -join "','")
    try {
        $copilotServicePrincipals = Invoke-CollectorOperation -Target "Microsoft Graph tenant $TenantId" -Action "List Copilot Studio service principals by AppId" -ScriptBlock {
            Get-MgServicePrincipal -Filter $appIdFilter -ConsistencyLevel eventual -CountVariable servicePrincipalCount -All -ErrorAction Stop |
                ForEach-Object {
                    [PSCustomObject]@{
                        AppId          = $_.AppId
                        DisplayName    = $_.DisplayName
                        AccountEnabled = $_.AccountEnabled
                        Id             = $_.Id
                        ServicePrincipalType = $_.ServicePrincipalType
                    }
                }
        }
        $copilotServicePrincipals = @($copilotServicePrincipals)
    }
    catch {
        $warnings.Add("Section 5 AppId lookup failed: $($_.Exception.Message)")
        Write-Warning $warnings[-1]
        $copilotServicePrincipals = @()
    }

    # Fallback: if AppId lookup returns 0 (rare — tenant has neither current nor legacy SP),
    # retry display-name filters and warn that results may miss rebranded SPs.
    if ($copilotServicePrincipals.Count -eq 0) {
        $warnings.Add("Section 5: AppId lookup returned 0 service principals; falling back to display-name lookup (fallback-only — may miss rebranded SPs).")
        Write-Warning $warnings[-1]
        $filterConditions = @(
            "startsWith(displayName,'Copilot Studio')",
            "startsWith(displayName,'Power Virtual Agents')",
            "startsWith(displayName,'Microsoft Copilot Studio')"
        )
        $copilotServicePrincipals = foreach ($filterExpr in $filterConditions) {
            try {
                $sps = Invoke-CollectorOperation -Target "Microsoft Graph tenant $TenantId" -Action "List service principals matching filter $filterExpr" -ScriptBlock {
                    Get-MgServicePrincipal -Filter $filterExpr -ConsistencyLevel eventual -CountVariable servicePrincipalCount -All -ErrorAction Stop
                }
                foreach ($sp in $sps) {
                    [PSCustomObject]@{
                        AppId          = $sp.AppId
                        DisplayName    = $sp.DisplayName
                        AccountEnabled = $sp.AccountEnabled
                        Id             = $sp.Id
                        ServicePrincipalType = $sp.ServicePrincipalType
                    }
                }
            }
            catch {
                $warnings.Add("SP filter '$filterExpr' failed: $($_.Exception.Message)")
                Write-Warning $warnings[-1]
            }
        }
        $copilotServicePrincipals = @($copilotServicePrincipals)
    }
    # Deduplicate by AppId
    $copilotServicePrincipals = @($copilotServicePrincipals | Sort-Object AppId -Unique)
    Write-Verbose "  Collected $($copilotServicePrincipals.Count) Copilot Studio service principal(s)."
}
catch {
    $warnings.Add("Section 5 (Copilot Service Principals) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 6: Tenant TLS / Encryption Settings
# Supports: Baseline security posture, encryption-at-rest / in-transit
# ═══════════════════════════════════════════════════════════════════════
$tenantSecuritySettings = $null
try {
    Write-Verbose "Section 6: Collecting tenant security settings via Get-MgOrganization..."
    $org = Invoke-CollectorOperation -Target "Microsoft Graph tenant $TenantId" -Action 'Get organization settings' -ScriptBlock {
        Get-MgOrganization -ErrorAction Stop | Select-Object -First 1
    }

    if ($org) {
        $tenantSecuritySettings = [PSCustomObject]@{
            DisplayName               = $org.DisplayName
            TenantId                  = $org.Id
            TenantType                = $org.TenantType
            SecurityComplianceNotificationMails = $org.SecurityComplianceNotificationMails
            SecurityComplianceNotificationPhones = $org.SecurityComplianceNotificationPhones
            TechnicalNotificationMails = $org.TechnicalNotificationMails
            VerifiedDomains           = $org.VerifiedDomains | ForEach-Object {
                [PSCustomObject]@{
                    Name       = $_.Name
                    IsDefault  = $_.IsDefault
                    IsInitial  = $_.IsInitial
                    Type       = $_.Type
                }
            }
            CreatedDateTime           = $org.CreatedDateTime
            OnPremisesSyncEnabled     = $org.OnPremisesSyncEnabled
        }
        Write-Verbose "  Tenant security settings collected."
    }
    else {
        Write-Verbose "  Tenant security settings collection skipped."
    }
}
catch {
    $warnings.Add("Section 6 (Tenant Security Settings) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 7: AI Leadership Job Titles
# Supports: Frontier Q01 (ai_initiative_owner_identified) — AI Strategy L100
# Prereq: User.Read.All Graph scope (incremental; Graph auth already required)
# ═══════════════════════════════════════════════════════════════════════
$aiLeadershipUsers = $null
try {
    Write-Verbose "Section 7: Enumerating AI-leadership job titles..."

    # AI-leadership keyword fragments for post-filtering
    $aiKeywords = @(
        'Chief Data Officer', 'Chief Information Officer', 'Chief AI Officer',
        'Chief Digital Officer', 'Chief Analytics Officer',
        'Chief Data and Analytics Officer', 'Chief Technology Officer',
        'Head of AI', 'Head of Data', 'Head of Digital',
        'AI Governance Lead', 'AI Officer',
        'Director of AI', 'VP of AI', 'VP of Data', 'VP of Digital',
        'CDO', 'CIO', 'CTO'
    )
    $selectProps = @('DisplayName', 'UserPrincipalName', 'JobTitle', 'Department')

    # Two narrow server-side filters to limit API response volume
    $rawUsers = @()
    try {
        $chiefUsers = Invoke-CollectorOperation -Target "Microsoft Graph tenant $TenantId" -Action "List users matching job title prefix 'Chief'" -ScriptBlock {
            Get-MgUser -Filter "startswith(jobTitle,'Chief')" -ConsistencyLevel eventual -CountVariable chiefUserCount `
                -Property $selectProps -All -ErrorAction Stop
        }
        if ($chiefUsers) {
            $rawUsers += @($chiefUsers)
        }
    }
    catch {
        $warnings.Add("Section 7 filter 'Chief' failed: $($_.Exception.Message)")
        Write-Warning $warnings[-1]
    }
    try {
        $leadershipUsers = Invoke-CollectorOperation -Target "Microsoft Graph tenant $TenantId" -Action "List users matching AI leadership job title filters" -ScriptBlock {
            Get-MgUser -Filter "startswith(jobTitle,'Head of') or startswith(jobTitle,'VP of') or startswith(jobTitle,'Director of') or startswith(jobTitle,'AI ')" -ConsistencyLevel eventual -CountVariable leadershipUserCount `
                -Property $selectProps -All -ErrorAction Stop
        }
        if ($leadershipUsers) {
            $rawUsers += @($leadershipUsers)
        }
    }
    catch {
        $warnings.Add("Section 7 filter 'Head/VP/Director/AI' failed: $($_.Exception.Message)")
        Write-Warning $warnings[-1]
    }

    # Deduplicate by UserPrincipalName
    $uniqueUsers = @($rawUsers | Sort-Object UserPrincipalName -Unique)

    # Post-filter: match job titles against canonical AI-leadership keywords
    $matchedUsers = @(foreach ($user in $uniqueUsers) {
        if (-not $user.JobTitle) { continue }
        $titleLower = $user.JobTitle.ToLower()
        $matchedKeyword = $null
        foreach ($kw in $aiKeywords) {
            $kwLower = $kw.ToLower()
            # Short acronyms (CDO, CIO, CTO): require word boundary
            if ($kwLower.Length -le 3) {
                if ($titleLower -match "\b$([regex]::Escape($kwLower))\b") {
                    $matchedKeyword = $kw
                    break
                }
            }
            else {
                if ($titleLower.Contains($kwLower)) {
                    $matchedKeyword = $kw
                    break
                }
            }
        }
        if ($matchedKeyword) {
            [PSCustomObject]@{
                DisplayName       = $user.DisplayName
                UserPrincipalName = $user.UserPrincipalName
                JobTitle          = $user.JobTitle
                Department        = $user.Department
                MatchedKeyword    = $matchedKeyword
            }
        }
    })

    $aiLeadershipUsers = $matchedUsers
    Write-Verbose "  Found $($aiLeadershipUsers.Count) user(s) with AI-leadership job titles."
}
catch {
    $warnings.Add("Section 7 (AI Leadership Job Titles) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Build Output
# ═══════════════════════════════════════════════════════════════════════
$result = [ordered]@{
    conditionalAccessPolicies  = $conditionalAccessPolicies
    fsiSecurityGroups          = $fsiSecurityGroups
    informationBarriers        = $informationBarriers
    privilegedRoleAssignments  = $privilegedRoleAssignments
    copilotServicePrincipals   = $copilotServicePrincipals
    tenantSecuritySettings     = $tenantSecuritySettings
    aiLeadershipUsers          = $aiLeadershipUsers
    _metadata                  = [ordered]@{
        collector   = 'Collect-Graph'
        timestamp   = (Get-Date -Format 'o')
        tenant_id   = $TenantId
        warnings    = @($warnings)
    }
}

$json = $result | ConvertTo-Json -Depth 10
$json | Out-File -FilePath $outputFile -Encoding utf8
Write-Verbose "Output written to $outputFile"

# ─── Disconnect Graph ────────────────────────────────────────────────
try { Disconnect-MgGraph -ErrorAction SilentlyContinue } catch { }

# ─── Exit Code ───────────────────────────────────────────────────────
$sectionValues = @(
    $conditionalAccessPolicies, $fsiSecurityGroups, $informationBarriers,
    $privilegedRoleAssignments, $copilotServicePrincipals, $tenantSecuritySettings,
    $aiLeadershipUsers
)
$nullSections = @($sectionValues | Where-Object { $null -eq $_ })

if ($nullSections.Count -eq $sectionValues.Count) {
    Write-Error "All sections failed to collect data. See warnings for details."
    exit 2
}
elseif ($nullSections.Count -gt 0) {
    Write-Warning "Partial collection: $($nullSections.Count)/$($sectionValues.Count) sections returned null."
    exit 1
}
else {
    Write-Verbose "All sections collected successfully."
    exit 0
}
