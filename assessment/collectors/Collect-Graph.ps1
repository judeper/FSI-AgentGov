<#
.SYNOPSIS
    Collects Microsoft Graph / Entra ID configuration data for FSI Agent Governance assessment.

.DESCRIPTION
    Enumerates Conditional Access policies, FSI-Agent security groups, privileged role
    assignments, Copilot Studio service principals, and tenant security settings via
    Microsoft Graph.

    Outputs a structured JSON file (graph.json) consumed by the assessment engine.

    Pattern references:
      - restrict-agent-publishing.ps1 — CA policy validation patterns
      - Invoke-HardeningBaselineCheck.ps1 — tenant settings, security group checks
      - Invoke-SharingAudit.ps1 — cross-tenant access pattern for principal classification

.PARAMETER TenantId
    Mandatory. Azure AD tenant ID.

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
    service principals, information barriers, and tenant settings.

.NOTES
    Part of the FSI Agent Governance Assessment Engine — Graph Collector.
    Required Graph scopes: Policy.Read.All, Group.Read.All, Directory.Read.All, AuditLog.Read.All.
    Exit codes: 0 = success, 1 = partial failure (some sections null), 2 = total failure.
    Version: 1.0.0
#>

#Requires -Version 7.0

[CmdletBinding()]
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
    Connect-MgGraph -TenantId $TenantId -Scopes $requiredScopes -ErrorAction Stop
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
    Connect-MgGraph -TenantId $TenantId -ClientSecretCredential $credential -ErrorAction Stop
}

Write-Verbose "Microsoft Graph authentication successful."

# ═══════════════════════════════════════════════════════════════════════
# Section 1: Conditional Access Policies
# Supports: Control 1.1 (Agent Authentication Enforcement), MFA requirements
# Pattern: restrict-agent-publishing.ps1 — CA policy evaluation
# ═══════════════════════════════════════════════════════════════════════
$conditionalAccessPolicies = $null
try {
    Write-Verbose "Section 1: Collecting Conditional Access policies..."
    $rawPolicies = Get-MgIdentityConditionalAccessPolicy -All -ErrorAction Stop
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
# Supports: Control 1.1 (Security Group Governance), 2.1 (Managed Environments)
# Pattern: Invoke-HardeningBaselineCheck.ps1 Item 17 (Security Groups)
# ═══════════════════════════════════════════════════════════════════════
$fsiSecurityGroups = $null
try {
    Write-Verbose "Section 2: Collecting FSI-Agent-* security groups..."
    $rawGroups = Get-MgGroup -Filter "startsWith(displayName,'FSI-Agent-')" -All `
        -Property Id, DisplayName, SecurityEnabled, GroupTypes, MembershipRule -ErrorAction Stop

    $fsiSecurityGroups = foreach ($grp in $rawGroups) {
        # Get member count via a separate call
        $memberCount = 0
        try {
            $members = Get-MgGroupMember -GroupId $grp.Id -All -ErrorAction Stop
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
        $rawIb = Get-InformationBarrierPolicy -ErrorAction Stop
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
# Supports: Control 3.7 (Least-Privilege Access), admin role auditing
# ═══════════════════════════════════════════════════════════════════════
$privilegedRoleAssignments = $null
try {
    Write-Verbose "Section 4: Collecting privileged role assignments..."

    # Target roles: Power Platform Admin and Dynamics 365 Admin
    $targetRoleNames = @('Power Platform Administrator', 'Dynamics 365 Administrator')

    # Get all role definitions to map IDs to names
    $roleDefinitions = Get-MgRoleManagementDirectoryRoleDefinition -All -ErrorAction Stop
    $targetRoles = $roleDefinitions | Where-Object { $targetRoleNames -contains $_.DisplayName }

    $privilegedRoleAssignments = foreach ($role in $targetRoles) {
        $assignments = Get-MgRoleManagementDirectoryRoleAssignment -Filter "roleDefinitionId eq '$($role.Id)'" -All -ErrorAction Stop
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
# Supports: Control 1.1 (Agent Authentication), app registration auditing
# ═══════════════════════════════════════════════════════════════════════
$copilotServicePrincipals = $null
try {
    Write-Verbose "Section 5: Collecting Copilot Studio service principals..."

    # Filter for known Copilot Studio / Power Virtual Agents app names
    $filterConditions = @(
        "startsWith(displayName,'Copilot Studio')",
        "startsWith(displayName,'Power Virtual Agents')",
        "startsWith(displayName,'Microsoft Copilot Studio')"
    )

    $copilotServicePrincipals = foreach ($filterExpr in $filterConditions) {
        try {
            $sps = Get-MgServicePrincipal -Filter $filterExpr -All -ErrorAction Stop
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
    $org = Get-MgOrganization -ErrorAction Stop | Select-Object -First 1

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
catch {
    $warnings.Add("Section 6 (Tenant Security Settings) failed: $($_.Exception.Message)")
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
    $privilegedRoleAssignments, $copilotServicePrincipals, $tenantSecuritySettings
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
