<#
.SYNOPSIS
    Validates hardening baseline items via Power Platform Admin APIs.

.DESCRIPTION
    Checks 18 items (6 via cross-reference + 12 direct) from the 32-item Configuration Hardening Baseline:
    - Items 1-6: Agent publishing restrictions (env maker role, security groups, sharing, DLP, managed env limits, approval workflow) — validated by restrict-agent-publishing.ps1
    - Items 7-9: Audit logging (environment-level auditing, retention period, tenant-level auditing)
    - Items 14-17: Environment provisioning (creation restriction, routing, tenant isolation, security groups)
    - Items 28-32: Environment security settings (blocked attachments, MIME types, inactivity timeout, session expiration, CSP)

    Uses Get-TenantSettings (items 14-16), Get-AdminPowerAppEnvironment (item 17),
    and Dataverse Organization entity REST API (items 7-9, 28-32) to query current configuration.

    Supports zone-specific thresholds for audit retention (item 8) and security group
    requirements (item 17) via the -ZoneMapping parameter.

.PARAMETER OutputFormat
    Output format for results. Valid values: Table, JSON, Object. Default: Table.

.PARAMETER OutputPath
    Optional file path to export JSON results. When omitted, results display to console only.

.PARAMETER EnvironmentFilter
    Optional array of environment names or display names to limit scope.
    When omitted, all environments are checked.

.PARAMETER ZoneMapping
    Optional hashtable mapping environment names to zone numbers (1, 2, or 3).
    Used for zone-specific thresholds on items 8 and 17.
    Example: @{ 'prod-env-1' = 3; 'dev-env-1' = 1 }

.PARAMETER IncludeEvidence
    When specified, computes SHA-256 integrity hash over results for evidence packaging.

.EXAMPLE
    .\Invoke-HardeningBaselineCheck.ps1

    Runs all 7 checks with default settings and displays results in table format.

.EXAMPLE
    .\Invoke-HardeningBaselineCheck.ps1 -OutputFormat JSON -OutputPath .\evidence\baseline.json -IncludeEvidence

    Runs checks, exports JSON with SHA-256 integrity hash to the specified path.

.EXAMPLE
    .\Invoke-HardeningBaselineCheck.ps1 -EnvironmentFilter 'prod-env-1','prod-env-2' -ZoneMapping @{ 'prod-env-1' = 3; 'prod-env-2' = 2 }

    Checks only the specified environments with zone-specific thresholds applied.

.OUTPUTS
    PSCustomObject with Metadata, Summary, Checks, and Gaps properties.

.NOTES
    Part of the FSI Agent Governance — Configuration Hardening Baseline.
    Controls: 1.7, 2.1, 3.7
    Version: 1.2.0
    Requires: Microsoft.PowerApps.Administration.PowerShell (2.0.0+)
#>

#Requires -Version 7.0
#Requires -Modules @{ ModuleName = 'Microsoft.PowerApps.Administration.PowerShell'; ModuleVersion = '2.0.0' }

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter()]
    [ValidateSet('Table', 'JSON', 'Object')]
    [string]$OutputFormat = 'Table',

    [Parameter()]
    [string]$OutputPath,

    [Parameter()]
    [string[]]$EnvironmentFilter,

    [Parameter()]
    [hashtable]$ZoneMapping,

    [Parameter()]
    [switch]$IncludeEvidence
)

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — Hardening Baseline Checker      ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ─── WhatIf Preview ──────────────────────────────────────────────────
if (-not $PSCmdlet.ShouldProcess("Power Platform tenant", "Run hardening baseline checks (items 1-9, 14-17, 28-32)")) {
    Write-Verbose "WhatIf: Would check hardening baseline items 1-6 (agent publishing restrictions), 7-9 (audit logging), 14-17 (environment provisioning), and 28-32 (environment security settings)"
    return
}

# ─── Helper Functions ────────────────────────────────────────────────

function Get-EnvironmentZone {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$EnvironmentName,
        [Parameter()]
        [hashtable]$Mapping
    )
    if ($Mapping -and $Mapping.ContainsKey($EnvironmentName)) {
        return $Mapping[$EnvironmentName]
    }
    return 1  # Default to Zone 1 (least restrictive)
}

function New-CheckResult {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][int]$ItemNumber,
        [Parameter(Mandatory)][string]$Setting,
        [Parameter(Mandatory)][string]$CheckGroup,
        [Parameter(Mandatory)][ValidateSet('Pass', 'Fail', 'Skip', 'Warning')][string]$Status,
        [Parameter()][string]$Expected,
        [Parameter()][string]$Actual,
        [Parameter()][string]$Environment,
        [Parameter()][string]$Message
    )
    [PSCustomObject]@{
        ItemNumber  = $ItemNumber
        Setting     = $Setting
        CheckGroup  = $CheckGroup
        Status      = $Status
        Expected    = $Expected
        Actual      = $Actual
        Environment = $Environment
        Message     = $Message
    }
}

# ─── Initialize Results ──────────────────────────────────────────────
$allChecks = [System.Collections.Generic.List[PSCustomObject]]::new()
$gaps = [System.Collections.Generic.List[string]]::new()
$startTime = [DateTime]::UtcNow

# ═══════════════════════════════════════════════════════════════════════
# Check Group 0: Agent Publishing Restrictions (Items 1-6)
# Validated by: restrict-agent-publishing.ps1
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Check Group 0: Agent Publishing Restrictions (Items 1-6) — cross-reference..."

$publishingScriptPath = Join-Path $PSScriptRoot 'restrict-agent-publishing.ps1'
$publishingScriptExists = Test-Path $publishingScriptPath

$publishingItems = @(
    @{ Number = 1; Setting = 'Environment Maker role removal';      AutoLevel = 'Automated' }
    @{ Number = 2; Setting = 'Authorized security groups';          AutoLevel = 'Semi-Automated' }
    @{ Number = 3; Setting = 'Share with Everyone disabled';        AutoLevel = 'Automated' }
    @{ Number = 4; Setting = 'DLP connector blocking';              AutoLevel = 'Semi-Automated' }
    @{ Number = 5; Setting = 'Managed Environment sharing limits';  AutoLevel = 'Automated' }
    @{ Number = 6; Setting = 'Approval workflow active (Zone 2/3)'; AutoLevel = 'Semi-Automated' }
)

foreach ($item in $publishingItems) {
    if ($publishingScriptExists) {
        $allChecks.Add((New-CheckResult -ItemNumber $item.Number `
            -Setting $item.Setting -CheckGroup 'AgentPublishing' `
            -Status 'Skip' `
            -Message "Run restrict-agent-publishing.ps1 to validate ($($item.AutoLevel))"))
    } else {
        $allChecks.Add((New-CheckResult -ItemNumber $item.Number `
            -Setting $item.Setting -CheckGroup 'AgentPublishing' `
            -Status 'Skip' `
            -Message "Manual attestation required — restrict-agent-publishing.ps1 not found"))
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Check Group 1: Tenant Settings (Items 14-16)
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Check Group 1: Tenant Settings (Items 14-16)..."

try {
    $tenantSettings = Get-TenantSettings

    # Item 14 — Environment Creation Restriction
    $devRestriction = $tenantSettings.powerPlatform.environments.disableNonAdminDeveloperEnvironmentCreation
    $prodRestriction = $tenantSettings.powerPlatform.environments.disableNonAdminProductionEnvironmentCreation
    $trialRestriction = $tenantSettings.powerPlatform.environments.disableNonAdminTrialEnvironmentCreation

    $item14AllRestricted = ($devRestriction -eq $true) -and ($prodRestriction -eq $true) -and ($trialRestriction -eq $true)
    $item14Status = if ($item14AllRestricted) { 'Pass' } else { 'Fail' }
    $item14Actual = "Dev=$devRestriction, Prod=$prodRestriction, Trial=$trialRestriction"

    $allChecks.Add((New-CheckResult -ItemNumber 14 -Setting 'Environment creation restriction' `
        -CheckGroup 'TenantSettings' -Status $item14Status `
        -Expected 'All environment types restricted to admins' -Actual $item14Actual))

    if ($item14Status -eq 'Fail') {
        $gaps.Add("Item 14: Environment creation not fully restricted — $item14Actual")
    }

    # Item 15 — Environment Routing
    $routingEnabled = $tenantSettings.powerPlatform.environments.environmentRoutingEnabled
    $item15Status = if ($routingEnabled -eq $true) { 'Pass' } else { 'Fail' }

    $allChecks.Add((New-CheckResult -ItemNumber 15 -Setting 'Environment routing' `
        -CheckGroup 'TenantSettings' -Status $item15Status `
        -Expected 'Routing enabled/configured' -Actual "RoutingEnabled=$routingEnabled"))

    if ($item15Status -eq 'Fail') {
        $gaps.Add("Item 15: Environment routing not enabled")
    }

    # Item 16 — Tenant Isolation
    $isolationEnabled = $tenantSettings.powerPlatform.tenantIsolation.enabled
    $item16Status = if ($isolationEnabled -eq $true) { 'Pass' } else { 'Fail' }

    $allChecks.Add((New-CheckResult -ItemNumber 16 -Setting 'Tenant isolation' `
        -CheckGroup 'TenantSettings' -Status $item16Status `
        -Expected 'Cross-tenant connections restricted' -Actual "IsolationEnabled=$isolationEnabled"))

    if ($item16Status -eq 'Fail') {
        $gaps.Add("Item 16: Tenant isolation not enabled — cross-tenant connections permitted")
    }
}
catch {
    Write-Warning "Check Group 1 (Tenant Settings) failed: $($_.Exception.Message)"
    $allChecks.Add((New-CheckResult -ItemNumber 14 -Setting 'Environment creation restriction' `
        -CheckGroup 'TenantSettings' -Status 'Skip' -Message "Error: $($_.Exception.Message)"))
    $allChecks.Add((New-CheckResult -ItemNumber 15 -Setting 'Environment routing' `
        -CheckGroup 'TenantSettings' -Status 'Skip' -Message "Error: $($_.Exception.Message)"))
    $allChecks.Add((New-CheckResult -ItemNumber 16 -Setting 'Tenant isolation' `
        -CheckGroup 'TenantSettings' -Status 'Skip' -Message "Error: $($_.Exception.Message)"))
}

# ═══════════════════════════════════════════════════════════════════════
# Check Group 2: Environment Settings (Items 7-8, 17)
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Check Group 2: Environment Settings (Items 7-8, 17)..."

# Pre-initialize $environments so downstream check groups have a safe default
$environments = @()

try {
    $environments = Get-AdminPowerAppEnvironment
    if ($EnvironmentFilter) {
        $environments = $environments | Where-Object {
            $EnvironmentFilter -contains $_.EnvironmentName -or
            $EnvironmentFilter -contains $_.DisplayName
        }
    }

    Write-Verbose "Scanning $($environments.Count) environment(s)..."

    foreach ($env in $environments) {
        $envName = $env.DisplayName
        $envId = $env.EnvironmentName
        $zone = Get-EnvironmentZone -EnvironmentName $envId -Mapping $ZoneMapping

        # Check for linked Dataverse instance
        $dataverseUrl = $env.Internal.properties.linkedEnvironmentMetadata.instanceUrl

        # Item 7 — Environment-Level Auditing
        if ($dataverseUrl) {
            $dataverseUrl = $dataverseUrl.TrimEnd('/') + '/'
            $resourceUrl = $dataverseUrl.TrimEnd('/')  # Az.Accounts rejects trailing slash
            try {
                $orgResponse = Invoke-RestMethod -Uri "${dataverseUrl}api/data/v9.2/organizations?`$select=isauditenabled" `
                    -Headers @{ Authorization = "Bearer $((Get-AzAccessToken -ResourceUrl $resourceUrl).Token)" } `
                    -Method Get -ErrorAction Stop

                # isauditenabled is a BooleanManagedProperty — extract .Value
                $auditProp = $orgResponse.value[0].isauditenabled
                $isAuditEnabled = if ($auditProp -is [bool]) { $auditProp } else { $auditProp.Value -eq $true }
                $item7Status = if ($isAuditEnabled) { 'Pass' } else { 'Fail' }

                $allChecks.Add((New-CheckResult -ItemNumber 7 -Setting 'Environment-level auditing' `
                    -CheckGroup 'EnvironmentSettings' -Status $item7Status `
                    -Expected 'Auditing enabled' -Actual "IsAuditEnabled=$isAuditEnabled" `
                    -Environment $envName))

                if ($item7Status -eq 'Fail') {
                    $gaps.Add("Item 7: Auditing not enabled in environment '$envName'")
                }
            }
            catch {
                Write-Warning "  Item 7: Could not query Dataverse for '$envName': $($_.Exception.Message)"
                $allChecks.Add((New-CheckResult -ItemNumber 7 -Setting 'Environment-level auditing' `
                    -CheckGroup 'EnvironmentSettings' -Status 'Skip' `
                    -Environment $envName -Message "API error: $($_.Exception.Message)"))
            }

            # Item 8 — Audit Log Retention Period
            try {
                $retResponse = Invoke-RestMethod -Uri "${dataverseUrl}api/data/v9.2/organizations?`$select=auditretentionperiodv2" `
                    -Headers @{ Authorization = "Bearer $((Get-AzAccessToken -ResourceUrl $resourceUrl).Token)" } `
                    -Method Get -ErrorAction Stop

                $retentionDays = $retResponse.value[0].auditretentionperiodv2
                $requiredDays = switch ($zone) {
                    1 { 180 }
                    2 { 365 }
                    3 { 730 }
                    default { 180 }
                }
                $item8Status = if ($retentionDays -ge $requiredDays) { 'Pass' } else { 'Fail' }

                $allChecks.Add((New-CheckResult -ItemNumber 8 -Setting 'Audit log retention period' `
                    -CheckGroup 'EnvironmentSettings' -Status $item8Status `
                    -Expected ">= $requiredDays days (Zone $zone)" -Actual "$retentionDays days" `
                    -Environment $envName))

                if ($item8Status -eq 'Fail') {
                    $gaps.Add("Item 8: Audit retention in '$envName' is $retentionDays days (Zone $zone requires >= $requiredDays)")
                }
            }
            catch {
                Write-Warning "  Item 8: Could not query retention for '$envName': $($_.Exception.Message)"
                $allChecks.Add((New-CheckResult -ItemNumber 8 -Setting 'Audit log retention period' `
                    -CheckGroup 'EnvironmentSettings' -Status 'Skip' `
                    -Environment $envName -Message "API error: $($_.Exception.Message)"))
            }
        }
        else {
            Write-Warning "  Environment '$envName' has no linked Dataverse instance — skipping items 7-8"
            $allChecks.Add((New-CheckResult -ItemNumber 7 -Setting 'Environment-level auditing' `
                -CheckGroup 'EnvironmentSettings' -Status 'Skip' `
                -Environment $envName -Message 'No Dataverse instance linked'))
            $allChecks.Add((New-CheckResult -ItemNumber 8 -Setting 'Audit log retention period' `
                -CheckGroup 'EnvironmentSettings' -Status 'Skip' `
                -Environment $envName -Message 'No Dataverse instance linked'))
        }

        # Item 17 — Environment Security Groups
        $securityGroupId = $env.Internal.properties.securityGroupId
        $hasSecurityGroup = -not [string]::IsNullOrWhiteSpace($securityGroupId)

        if ($zone -ge 2) {
            $item17Status = if ($hasSecurityGroup) { 'Pass' } else { 'Fail' }
            $item17Message = $null
        }
        else {
            # Zone 1: pass with advisory if no security group
            $item17Status = 'Pass'
            $item17Message = if (-not $hasSecurityGroup) { 'Advisory: No security group assigned (acceptable for Zone 1)' } else { $null }
        }

        $allChecks.Add((New-CheckResult -ItemNumber 17 -Setting 'Environment security groups' `
            -CheckGroup 'EnvironmentSettings' -Status $item17Status `
            -Expected "Security group assigned (Zone $zone)" `
            -Actual $(if ($hasSecurityGroup) { "GroupId=$securityGroupId" } else { 'None' }) `
            -Environment $envName -Message $item17Message))

        if ($item17Status -eq 'Fail') {
            $gaps.Add("Item 17: No security group assigned to Zone $zone environment '$envName'")
        }
    }
}
catch {
    Write-Warning "Check Group 2 (Environment Settings) failed: $($_.Exception.Message)"
    $allChecks.Add((New-CheckResult -ItemNumber 7 -Setting 'Environment-level auditing' `
        -CheckGroup 'EnvironmentSettings' -Status 'Skip' -Message "Error: $($_.Exception.Message)"))
    $allChecks.Add((New-CheckResult -ItemNumber 8 -Setting 'Audit log retention period' `
        -CheckGroup 'EnvironmentSettings' -Status 'Skip' -Message "Error: $($_.Exception.Message)"))
    $allChecks.Add((New-CheckResult -ItemNumber 17 -Setting 'Environment security groups' `
        -CheckGroup 'EnvironmentSettings' -Status 'Skip' -Message "Error: $($_.Exception.Message)"))
}

# ═══════════════════════════════════════════════════════════════════════
# Check Group 3: Tenant-Level Auditing (Item 9)
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Check Group 3: Tenant-Level Auditing (Item 9)..."

try {
    # Use the default environment to check tenant-level audit settings
    $defaultEnv = $environments | Where-Object { $_.Internal.properties.environmentSku -eq 'Default' } | Select-Object -First 1
    if (-not $defaultEnv) {
        $defaultEnv = $environments | Select-Object -First 1
    }

    if ($defaultEnv) {
        $defaultDataverseUrl = $defaultEnv.Internal.properties.linkedEnvironmentMetadata.instanceUrl
        if ($defaultDataverseUrl) {
            $defaultDataverseUrl = $defaultDataverseUrl.TrimEnd('/') + '/'
            $defaultResourceUrl = $defaultDataverseUrl.TrimEnd('/')  # Az.Accounts rejects trailing slash
            $orgResponse = Invoke-RestMethod -Uri "${defaultDataverseUrl}api/data/v9.2/organizations?`$select=isauditenabled" `
                -Headers @{ Authorization = "Bearer $((Get-AzAccessToken -ResourceUrl $defaultResourceUrl).Token)" } `
                -Method Get -ErrorAction Stop

            # isauditenabled is a BooleanManagedProperty — extract .Value
            $auditProp = $orgResponse.value[0].isauditenabled
            $tenantAuditEnabled = if ($auditProp -is [bool]) { $auditProp } else { $auditProp.Value -eq $true }
            $item9Status = if ($tenantAuditEnabled) { 'Pass' } else { 'Fail' }

            $allChecks.Add((New-CheckResult -ItemNumber 9 -Setting 'Tenant-level Dataverse auditing' `
                -CheckGroup 'TenantAuditing' -Status $item9Status `
                -Expected 'Auditing enabled at tenant level' -Actual "IsAuditEnabled=$tenantAuditEnabled" `
                -Environment $defaultEnv.DisplayName))

            if ($item9Status -eq 'Fail') {
                $gaps.Add("Item 9: Tenant-level Dataverse auditing not enabled")
            }
        }
        else {
            Write-Warning "Default environment has no Dataverse instance — cannot check tenant-level auditing"
            $allChecks.Add((New-CheckResult -ItemNumber 9 -Setting 'Tenant-level Dataverse auditing' `
                -CheckGroup 'TenantAuditing' -Status 'Skip' `
                -Message 'Default environment has no Dataverse instance'))
        }
    }
    else {
        Write-Warning "No environments found — cannot check tenant-level auditing"
        $allChecks.Add((New-CheckResult -ItemNumber 9 -Setting 'Tenant-level Dataverse auditing' `
            -CheckGroup 'TenantAuditing' -Status 'Skip' -Message 'No environments available'))
    }
}
catch {
    Write-Warning "Check Group 3 (Tenant-Level Auditing) failed: $($_.Exception.Message)"
    $allChecks.Add((New-CheckResult -ItemNumber 9 -Setting 'Tenant-level Dataverse auditing' `
        -CheckGroup 'TenantAuditing' -Status 'Skip' -Message "Error: $($_.Exception.Message)"))
}

# ═══════════════════════════════════════════════════════════════════════# Check Group 4: Environment Security Settings (Items 28-32)
# ═════════════════════════════════════════════════════════════════════
Write-Verbose "Check Group 4: Environment Security Settings (Items 28-32)..."

# Critical file extensions that should be blocked
$requiredBlockedExtensions = @('ade','adp','app','asa','asp','bat','cdx','cmd','com','cpl','crt','csh',
    'dll','exe','hta','inf','ins','jar','js','jse','lnk','mda','mdb','mde','msc','msi','msp','mst',
    'pcd','pif','reg','scr','sct','shb','shs','tmp','url','vb','vbe','vbs','ws','wsc','wsf','wsh')

# Critical MIME types that should be blocked
$requiredBlockedMimeTypes = @('application/x-msdownload','application/x-msdos-program',
    'application/x-bat','application/x-cmd','application/x-vbs',
    'application/javascript','application/x-javascript','text/javascript',
    'application/x-powershell','application/x-msi',
    'application/hta','application/msaccess','text/scriptlet','application/xml','application/prg')

foreach ($env in $environments) {
    $envName = $env.DisplayName
    $dataverseUrl = $env.Internal.properties.linkedEnvironmentMetadata.instanceUrl

    if (-not $dataverseUrl) {
        Write-Warning "  Environment '$envName' has no linked Dataverse instance — skipping items 28-32"
        28..32 | ForEach-Object {
            $settingName = switch ($_) {
                28 { 'Blocked attachment extensions' }
                29 { 'Blocked MIME types' }
                30 { 'Inactivity timeout' }
                31 { 'Session expiration' }
                32 { 'Content Security Policy (CSP)' }
            }
            $allChecks.Add((New-CheckResult -ItemNumber $_ -Setting $settingName `
                -CheckGroup 'EnvironmentSecuritySettings' -Status 'Skip' `
                -Environment $envName -Message 'No Dataverse instance linked'))
        }
        continue
    }

    # Normalize URL to ensure trailing slash for API path construction
    $dataverseUrl = $dataverseUrl.TrimEnd('/') + '/'
    $resourceUrl = $dataverseUrl.TrimEnd('/')  # Az.Accounts rejects trailing slash

    try {
        $securityFields = 'blockedattachments,blockedmimetypes,inactivitytimeoutinmins,' +
            'sessiontimeoutenabled,sessiontimeoutinmins,isaborttimeenabled,' +
            'iscontentsecuritypolicyenabled,contentsecuritypolicyoptions'
        $orgResponse = Invoke-RestMethod `
            -Uri "${dataverseUrl}api/data/v9.2/organizations?`$select=$securityFields" `
            -Headers @{ Authorization = "Bearer $((Get-AzAccessToken -ResourceUrl $resourceUrl).Token)" } `
            -Method Get -ErrorAction Stop

        $org = $orgResponse.value[0]

        # Item 28 — Blocked Attachment Extensions
        $blockedAttachments = $org.blockedattachments
        if ($blockedAttachments) {
            $configuredExtensions = ($blockedAttachments -split '[;,]') | ForEach-Object { $_.Trim().ToLower() } | Where-Object { $_ }
            $missingExtensions = $requiredBlockedExtensions | Where-Object { $_ -notin $configuredExtensions }
            $item28Status = if ($missingExtensions.Count -eq 0) { 'Pass' } else { 'Fail' }
            $item28Actual = "$($configuredExtensions.Count) extensions configured; $($missingExtensions.Count) critical missing"
        }
        else {
            $item28Status = 'Fail'
            $item28Actual = 'No blocked extensions configured'
            $missingExtensions = $requiredBlockedExtensions
        }

        $allChecks.Add((New-CheckResult -ItemNumber 28 -Setting 'Blocked attachment extensions' `
            -CheckGroup 'EnvironmentSecuritySettings' -Status $item28Status `
            -Expected 'Critical file extensions blocked' -Actual $item28Actual `
            -Environment $envName))

        if ($item28Status -eq 'Fail') {
            $gaps.Add("Item 28: Blocked attachments in '$envName' — missing: $($missingExtensions -join ', ')")
        }

        # Item 29 — Blocked MIME Types
        $blockedMimes = $org.blockedmimetypes
        if ($blockedMimes) {
            $configuredMimes = ($blockedMimes -split '[;,]') | ForEach-Object { $_.Trim().ToLower() } | Where-Object { $_ }
            $missingMimes = $requiredBlockedMimeTypes | Where-Object { $_ -notin $configuredMimes }
            $item29Status = if ($missingMimes.Count -eq 0) { 'Pass' } else { 'Fail' }
            $item29Actual = "$($configuredMimes.Count) MIME types blocked; $($missingMimes.Count) critical missing"
        }
        else {
            $item29Status = 'Fail'
            $item29Actual = 'No MIME type restrictions configured'
            $missingMimes = $requiredBlockedMimeTypes
        }

        $allChecks.Add((New-CheckResult -ItemNumber 29 -Setting 'Blocked MIME types' `
            -CheckGroup 'EnvironmentSecuritySettings' -Status $item29Status `
            -Expected 'High-risk MIME types blocked' -Actual $item29Actual `
            -Environment $envName))

        if ($item29Status -eq 'Fail') {
            $gaps.Add("Item 29: Blocked MIME types in '$envName' — missing: $($missingMimes -join ', ')")
        }

        # Item 30 — Inactivity Timeout
        $inactivityEnabled = $org.isaborttimeenabled -eq $true
        $inactivityMinutes = $org.inactivitytimeoutinmins

        if ($inactivityEnabled -and $inactivityMinutes -and $inactivityMinutes -le 120) {
            $item30Status = 'Pass'
        }
        elseif (-not $inactivityEnabled) {
            $item30Status = 'Fail'
        }
        else {
            $item30Status = 'Fail'
        }
        $item30Actual = "Enabled=$inactivityEnabled; Duration=$($inactivityMinutes ?? 'N/A') minutes"

        $allChecks.Add((New-CheckResult -ItemNumber 30 -Setting 'Inactivity timeout' `
            -CheckGroup 'EnvironmentSecuritySettings' -Status $item30Status `
            -Expected 'Enabled; <= 120 minutes' -Actual $item30Actual `
            -Environment $envName))

        if ($item30Status -eq 'Fail') {
            $gaps.Add("Item 30: Inactivity timeout in '$envName' — $item30Actual")
        }

        # Item 31 — Session Expiration
        $sessionEnabled = $org.sessiontimeoutenabled -eq $true
        $sessionMinutes = $org.sessiontimeoutinmins

        if ($sessionEnabled -and $sessionMinutes -and $sessionMinutes -le 1440) {
            $item31Status = 'Pass'
        }
        elseif (-not $sessionEnabled) {
            $item31Status = 'Fail'
        }
        else {
            $item31Status = 'Fail'
        }
        $item31Actual = "Enabled=$sessionEnabled; MaxLength=$($sessionMinutes ?? 'N/A') minutes"

        $allChecks.Add((New-CheckResult -ItemNumber 31 -Setting 'Session expiration' `
            -CheckGroup 'EnvironmentSecuritySettings' -Status $item31Status `
            -Expected 'Custom timeout enabled; <= 1440 minutes' -Actual $item31Actual `
            -Environment $envName))

        if ($item31Status -eq 'Fail') {
            $gaps.Add("Item 31: Session expiration in '$envName' — $item31Actual")
        }

        # Item 32 — Content Security Policy (CSP) Enforcement
        $cspEnabled = $org.iscontentsecuritypolicyenabled -eq $true
        $item32Status = if ($cspEnabled) { 'Pass' } else { 'Fail' }
        $item32Actual = "CSPEnforced=$cspEnabled"

        $allChecks.Add((New-CheckResult -ItemNumber 32 -Setting 'Content Security Policy (CSP)' `
            -CheckGroup 'EnvironmentSecuritySettings' -Status $item32Status `
            -Expected 'CSP enforcement enabled for model-driven apps' -Actual $item32Actual `
            -Environment $envName))

        if ($item32Status -eq 'Fail') {
            $gaps.Add("Item 32: Content Security Policy not enforced in environment '$envName'")
        }
    }
    catch {
        Write-Warning "  Check Group 4: Could not query environment security settings for '$envName': $($_.Exception.Message)"
        28..32 | ForEach-Object {
            $settingName = switch ($_) {
                28 { 'Blocked attachment extensions' }
                29 { 'Blocked MIME types' }
                30 { 'Inactivity timeout' }
                31 { 'Session expiration' }
                32 { 'Content Security Policy (CSP)' }
            }
            $allChecks.Add((New-CheckResult -ItemNumber $_ -Setting $settingName `
                -CheckGroup 'EnvironmentSecuritySettings' -Status 'Skip' `
                -Environment $envName -Message "API error: $($_.Exception.Message)"))
        }
    }
}

# ═════════════════════════════════════════════════════════════════════# Results Aggregation
# ═══════════════════════════════════════════════════════════════════════

$passCount = ($allChecks | Where-Object { $_.Status -eq 'Pass' }).Count
$failCount = ($allChecks | Where-Object { $_.Status -eq 'Fail' }).Count
$skipCount = ($allChecks | Where-Object { $_.Status -eq 'Skip' }).Count
$warnCount = ($allChecks | Where-Object { $_.Status -eq 'Warning' }).Count
$totalChecks = $allChecks.Count
$envCount = if ($environments) { $environments.Count } else { 0 }
$duration = ([DateTime]::UtcNow - $startTime).TotalSeconds

$baselineResults = [PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        CheckedAt           = $startTime
        ScriptVersion       = '1.2.0'
        EnvironmentsScanned = $envCount
        DurationSeconds     = [math]::Round($duration, 2)
        IntegrityHash       = $null
    }
    Summary = [PSCustomObject]@{
        TotalChecks   = $totalChecks
        Passed        = $passCount
        Failed        = $failCount
        Skipped       = $skipCount
        Warnings      = $warnCount
        OverallStatus = if ($failCount -eq 0) { 'Passed' } else { 'GapsFound' }
    }
    Checks = $allChecks.ToArray()
    Gaps   = $gaps.ToArray()
}

# ─── SHA-256 Evidence Hash ────────────────────────────────────────────
if ($IncludeEvidence) {
    $resultsJson = $baselineResults | ConvertTo-Json -Depth 10 -Compress
    $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
        [System.Text.Encoding]::UTF8.GetBytes($resultsJson)
    )
    $baselineResults.Metadata.IntegrityHash = [BitConverter]::ToString($hashBytes) -replace '-'
}

# ─── Console Summary ─────────────────────────────────────────────────
Write-Host "`n── Hardening Baseline Summary ──────────────────────────────" -ForegroundColor Cyan
Write-Host "  Items checked:     $totalChecks"
Write-Host "  Passed:            $passCount" -ForegroundColor $(if ($passCount -eq $totalChecks) { 'Green' } else { 'White' })
Write-Host "  Failed:            $failCount" -ForegroundColor $(if ($failCount -gt 0) { 'Yellow' } else { 'Green' })
Write-Host "  Skipped:           $skipCount" -ForegroundColor $(if ($skipCount -gt 0) { 'DarkYellow' } else { 'White' })
Write-Host "  Environments:      $envCount"
Write-Host "  Duration:          $([math]::Round($duration, 2))s"
if ($IncludeEvidence) {
    Write-Host "  Integrity Hash:    $($baselineResults.Metadata.IntegrityHash)" -ForegroundColor DarkGray
}
Write-Host "────────────────────────────────────────────────────────────`n" -ForegroundColor Cyan

# ─── Output ──────────────────────────────────────────────────────────
switch ($OutputFormat) {
    'JSON' {
        $json = $baselineResults | ConvertTo-Json -Depth 10
        if ($OutputPath) {
            $parentDir = Split-Path -Path $OutputPath -Parent
            if ($parentDir -and -not (Test-Path $parentDir)) {
                New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
            }
            $json | Out-File -FilePath $OutputPath -Encoding utf8
            Write-Verbose "Results exported to $OutputPath"
        }
        else {
            Write-Output $json
        }
    }
    'Table' {
        $allChecks | Format-Table -Property ItemNumber, Setting, Environment, Status, Expected, Actual -AutoSize

        if ($gaps.Count -gt 0) {
            Write-Host "Gaps:" -ForegroundColor Yellow
            $gaps | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
        }

        if ($OutputPath) {
            $parentDir = Split-Path -Path $OutputPath -Parent
            if ($parentDir -and -not (Test-Path $parentDir)) {
                New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
            }
            $baselineResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding utf8
            Write-Verbose "Results exported to $OutputPath"
        }
    }
    'Object' {
        Write-Output $baselineResults
    }
}
