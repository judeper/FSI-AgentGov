<#
.SYNOPSIS
    Imports approved security groups into Dataverse for UASD validation.

.DESCRIPTION
    Reads approved security group definitions from a CSV or JSON file and
    upserts them into the fsi_ApprovedSecurityGroup Dataverse table. Uses
    fsi_entraid_group_id as the unique key for upsert operations.

    Designed for initial seeding and ongoing maintenance of the approved
    security groups registry used by the Unrestricted Agent Sharing Detector.

    Supports WhatIf mode for previewing changes without writing to Dataverse.

.PARAMETER InputPath
    Path to the CSV or JSON file containing approved security groups.
    CSV must contain columns: GroupId, DisplayName.
    Optional CSV columns: Zone (defaults to DefaultZone parameter), IsActive (defaults to true).
    JSON must be an array of objects with GroupId, DisplayName properties.
    Optional JSON properties: Zone, IsActive.

.PARAMETER InputFormat
    Input file format. Valid values: CSV, JSON.
    Default: auto-detect from file extension.

.PARAMETER DataverseUrl
    Dataverse environment URL (e.g., https://org.crm.dynamics.com).
    Must include the scheme (https://) and trailing slash is optional.

.PARAMETER DefaultZone
    Default governance zone for imported groups when not specified per-record.
    Valid values: Zone1, Zone2, Zone3, All. Default: All.

.EXAMPLE
    .\Import-ApprovedSecurityGroups.ps1 -InputPath .\approved-groups.csv -DataverseUrl https://org.crm.dynamics.com

    Imports approved security groups from a CSV file into Dataverse.

.EXAMPLE
    .\Import-ApprovedSecurityGroups.ps1 -InputPath .\approved-groups.json -DataverseUrl https://org.crm.dynamics.com -WhatIf

    Preview import from JSON without making changes to Dataverse.

.EXAMPLE
    .\Import-ApprovedSecurityGroups.ps1 -InputPath .\approved-groups.csv -DataverseUrl https://org.crm.dynamics.com -DefaultZone Zone3

    Imports groups from CSV, assigning Zone3 to any records without a Zone value.

.OUTPUTS
    PSCustomObject with Metadata, Summary, and Details properties.

.NOTES
    Part of the FSI Agent Governance — Unrestricted Agent Sharing Detector.
    Controls: 1.1, 2.10
    Version: 1.0.0
    Requires: Az.Accounts module for Dataverse authentication
#>

#Requires -Version 7.0
#Requires -Modules Az.Accounts

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$InputPath,

    [Parameter()]
    [ValidateSet('CSV', 'JSON')]
    [string]$InputFormat,

    [Parameter(Mandatory)]
    [string]$DataverseUrl,

    [Parameter()]
    [ValidateSet('Zone1', 'Zone2', 'Zone3', 'All')]
    [string]$DefaultZone = 'All'
)

$ErrorActionPreference = 'Stop'

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  UASD — Import Approved Security Groups                ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ─── Helper Functions ────────────────────────────────────────────────

function Get-DataverseToken {
    <#
    .SYNOPSIS
        Obtains an access token for Dataverse via Az.Accounts.
    .DESCRIPTION
        Uses Get-AzAccessToken to acquire an OAuth token scoped to the
        specified Dataverse environment URL. Requires an active Azure
        session (Connect-AzAccount).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ResourceUrl
    )

    try {
        $tokenResult = Get-AzAccessToken -ResourceUrl $ResourceUrl -ErrorAction Stop
        # Handle both Az.Accounts 2.x (.Token as string) and 3.x+ (.Token as SecureString)
        if ($tokenResult.Token -is [securestring]) {
            return $tokenResult.Token | ConvertFrom-SecureString -AsPlainText
        }
        return $tokenResult.Token
    }
    catch {
        throw "Failed to acquire Dataverse token. Ensure you are signed in via Connect-AzAccount. Error: $($_.Exception.Message)"
    }
}

function Invoke-DataverseApi {
    <#
    .SYNOPSIS
        Invokes a Dataverse Web API endpoint with authorization and error handling.
    .DESCRIPTION
        Wrapper around Invoke-RestMethod that adds the Bearer token header
        and provides consistent error handling for Dataverse API calls.
        Supports GET, POST, and PATCH methods.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Uri,

        [Parameter(Mandatory)]
        [string]$Token,

        [Parameter()]
        [ValidateSet('GET', 'POST', 'PATCH')]
        [string]$Method = 'GET',

        [Parameter()]
        [hashtable]$Body
    )

    $headers = @{
        Authorization    = "Bearer $Token"
        'Content-Type'   = 'application/json'
        'OData-MaxVersion' = '4.0'
        'OData-Version'    = '4.0'
        'Prefer'           = 'return=representation'
    }

    $params = @{
        Uri         = $Uri
        Method      = $Method
        Headers     = $headers
        ErrorAction = 'Stop'
    }

    if ($Body -and ($Method -eq 'POST' -or $Method -eq 'PATCH')) {
        $params['Body'] = ($Body | ConvertTo-Json -Depth 10 -Compress)
    }

    try {
        $response = Invoke-RestMethod @params
        return $response
    }
    catch {
        $statusCode = $null
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }
        throw "Dataverse API call failed ($Method $Uri) [HTTP $statusCode]: $($_.Exception.Message)"
    }
}

function ConvertTo-ZoneValue {
    <#
    .SYNOPSIS
        Converts a zone string to the fsi_acv_zone option set integer value.
    .DESCRIPTION
        Maps governance zone names to their Dataverse option set values
        per the CAA shared fsi_acv_zone option set:
        Unclassified = 0, Zone1 = 1, Zone2 = 2, Zone3 = 3.
        'All' maps to Unclassified (0) to indicate zone-independent scope.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Zone
    )

    switch ($Zone) {
        'Zone1' { return 1 }
        'Zone2' { return 2 }
        'Zone3' { return 3 }
        'All'   { return 0 }  # Unclassified = zone-independent
        default { return 0 }  # Default to Unclassified
    }
}

function Import-GroupsFromCsv {
    <#
    .SYNOPSIS
        Parses a CSV file into standardized group objects.
    .DESCRIPTION
        Reads a CSV file with GroupId, DisplayName, Zone, IsActive columns
        and returns standardized PSCustomObjects for processing.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path,

        [Parameter()]
        [string]$FallbackZone = 'All'
    )

    $records = Import-Csv -Path $Path -ErrorAction Stop
    $groups = [System.Collections.Generic.List[PSCustomObject]]::new()

    foreach ($record in $records) {
        if (-not $record.GroupId -or -not $record.DisplayName) {
            Write-Warning "Skipping CSV row — missing GroupId or DisplayName: $($record | ConvertTo-Json -Compress)"
            continue
        }

        $zone = if ($record.Zone -and $record.Zone -match '^Zone[123]$|^All$') {
            $record.Zone
        } else {
            $FallbackZone
        }

        $isActive = if ($null -ne $record.IsActive -and $record.IsActive -ne '') {
            $val = $record.IsActive.Trim()
            if ($val -match '^(true|yes|1|y)$') { $true }
            elseif ($val -match '^(false|no|0|n)$') { $false }
            else {
                Write-Warning "Unrecognized IsActive value '$val' for group '$($record.GroupId)' — defaulting to true"
                $true
            }
        } else {
            $true
        }

        $groups.Add([PSCustomObject]@{
            GroupId     = $record.GroupId.Trim()
            DisplayName = $record.DisplayName.Trim()
            Zone        = $zone
            IsActive    = $isActive
        })
    }

    return $groups.ToArray()
}

function Import-GroupsFromJson {
    <#
    .SYNOPSIS
        Parses a JSON file into standardized group objects.
    .DESCRIPTION
        Reads a JSON array of objects with GroupId, DisplayName, Zone, IsActive
        properties and returns standardized PSCustomObjects for processing.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path,

        [Parameter()]
        [string]$FallbackZone = 'All'
    )

    $rawContent = Get-Content -Path $Path -Raw -ErrorAction Stop
    $records = $rawContent | ConvertFrom-Json -ErrorAction Stop

    if ($records -isnot [System.Array]) {
        $records = @($records)
    }

    $groups = [System.Collections.Generic.List[PSCustomObject]]::new()

    foreach ($record in $records) {
        if (-not $record.GroupId -or -not $record.DisplayName) {
            Write-Warning "Skipping JSON entry — missing GroupId or DisplayName: $($record | ConvertTo-Json -Compress)"
            continue
        }

        $zone = if ($record.Zone -and $record.Zone -match '^Zone[123]$|^All$') {
            $record.Zone
        } else {
            $FallbackZone
        }

        $isActive = if ($null -ne $record.IsActive) {
            [bool]$record.IsActive
        } else {
            $true
        }

        $groups.Add([PSCustomObject]@{
            GroupId     = $record.GroupId.Trim()
            DisplayName = $record.DisplayName.Trim()
            Zone        = $zone
            IsActive    = $isActive
        })
    }

    return $groups.ToArray()
}

# ─── Validate Input File ─────────────────────────────────────────────
if (-not (Test-Path -Path $InputPath)) {
    throw "Input file not found: $InputPath"
}

$inputFile = Get-Item -Path $InputPath
Write-Verbose "Input file: $($inputFile.FullName) ($($inputFile.Length) bytes)"

# ─── Determine Input Format ──────────────────────────────────────────
if (-not $InputFormat) {
    $extension = $inputFile.Extension.ToLower()
    switch ($extension) {
        '.csv'  { $InputFormat = 'CSV' }
        '.json' { $InputFormat = 'JSON' }
        default {
            throw "Cannot auto-detect format from extension '$extension'. Use -InputFormat to specify CSV or JSON."
        }
    }
    Write-Verbose "Auto-detected input format: $InputFormat"
}

# ─── Parse Input ─────────────────────────────────────────────────────
Write-Host "  Reading $InputFormat input from: $($inputFile.Name)" -ForegroundColor Gray

$groups = switch ($InputFormat) {
    'CSV'  { Import-GroupsFromCsv  -Path $InputPath -FallbackZone $DefaultZone }
    'JSON' { Import-GroupsFromJson -Path $InputPath -FallbackZone $DefaultZone }
}

if (-not $groups -or $groups.Count -eq 0) {
    Write-Warning "No valid group records found in input file."
    return [PSCustomObject]@{
        Metadata = [PSCustomObject]@{
            Timestamp  = (Get-Date -Format 'o')
            InputFile  = $inputFile.Name
            TotalRecords = 0
        }
        Summary = [PSCustomObject]@{
            Created = 0; Updated = 0; Skipped = 0; Errors = 0
        }
        Details = @()
    }
}

Write-Host "  Parsed $($groups.Count) group record(s)" -ForegroundColor Gray

# ─── Normalize Dataverse URL ─────────────────────────────────────────
$DataverseUrl = $DataverseUrl.TrimEnd('/')
$apiBase = "$DataverseUrl/api/data/v9.2"
$entitySetName = 'fsi_approvedsecuritygroups'

# ─── Authenticate ────────────────────────────────────────────────────
Write-Host "  Authenticating to Dataverse..." -ForegroundColor Gray

if (-not $PSCmdlet.ShouldProcess($DataverseUrl, "Authenticate and import $($groups.Count) security group(s)")) {
    Write-Verbose "WhatIf: Would authenticate to $DataverseUrl and upsert $($groups.Count) group(s)"

    # Still show a preview of what would happen
    $previewDetails = foreach ($group in $groups) {
        [PSCustomObject]@{
            GroupId     = $group.GroupId
            DisplayName = $group.DisplayName
            Zone        = $group.Zone
            IsActive    = $group.IsActive
            Action      = 'WhatIf — would query and upsert'
            Status      = 'Skipped'
        }
    }

    Write-Host ""
    Write-Host "  [WhatIf] Would process the following groups:" -ForegroundColor Yellow
    $previewDetails | Format-Table -Property GroupId, DisplayName, Zone, IsActive -AutoSize

    return [PSCustomObject]@{
        Metadata = [PSCustomObject]@{
            Timestamp    = (Get-Date -Format 'o')
            InputFile    = $inputFile.Name
            TotalRecords = $groups.Count
            WhatIf       = $true
        }
        Summary = [PSCustomObject]@{
            Created = 0; Updated = 0; Skipped = $groups.Count; Errors = 0
        }
        Details = $previewDetails
    }
}

$token = Get-DataverseToken -ResourceUrl $DataverseUrl
Write-Verbose "Token acquired for $DataverseUrl"

# ─── Process Groups ──────────────────────────────────────────────────
$startTime = [DateTime]::UtcNow
$createdCount = 0
$updatedCount = 0
$skippedCount = 0
$errorCount   = 0
$details = [System.Collections.Generic.List[PSCustomObject]]::new()

Write-Host "  Processing $($groups.Count) group(s)...`n" -ForegroundColor Gray

foreach ($group in $groups) {
    $groupId = $group.GroupId
    $displayName = $group.DisplayName
    $zoneValue = ConvertTo-ZoneValue -Zone $group.Zone
    $isActive = $group.IsActive

    Write-Verbose "Processing: $displayName ($groupId)"

    try {
        # ─── Query for existing record ────────────────────────────
        $escapedGroupId = $groupId -replace "'", "''"
        $filterUri = "$apiBase/$entitySetName`?`$filter=fsi_entraid_group_id eq '$escapedGroupId'&`$select=fsi_approvedsecuritygroupid,fsi_entraid_group_id,fsi_display_name"
        $queryResult = Invoke-DataverseApi -Uri $filterUri -Token $token -Method GET

        $existingRecord = $null
        if ($queryResult.value -and $queryResult.value.Count -gt 0) {
            $existingRecord = $queryResult.value[0]
        }

        $payload = @{
            fsi_entraid_group_id = $groupId
            fsi_display_name     = $displayName
            fsi_zone             = $zoneValue
            fsi_is_active        = $isActive
            fsi_added_by         = if ($IsWindows -or $null -eq $IsWindows) {
                try { [System.Security.Principal.WindowsIdentity]::GetCurrent().Name }
                catch { $env:USERNAME ?? $env:USER ?? 'unknown' }
            } else { $env:USER ?? 'unknown' }
            fsi_added_at         = (Get-Date -Format 'o')
        }

        if ($existingRecord) {
            # ─── Update existing record ───────────────────────────
            $recordId = $existingRecord.fsi_approvedsecuritygroupid
            $patchUri = "$apiBase/$entitySetName($recordId)"

            Invoke-DataverseApi -Uri $patchUri -Token $token -Method PATCH -Body $payload | Out-Null

            $updatedCount++
            Write-Host "    Updated: $displayName ($groupId)" -ForegroundColor Yellow

            $details.Add([PSCustomObject]@{
                GroupId     = $groupId
                DisplayName = $displayName
                Zone        = $group.Zone
                IsActive    = $isActive
                Action      = 'Updated'
                Status      = 'Success'
                RecordId    = $recordId
            })
        }
        else {
            # ─── Create new record ────────────────────────────────
            $postUri = "$apiBase/$entitySetName"

            $response = Invoke-DataverseApi -Uri $postUri -Token $token -Method POST -Body $payload

            $newRecordId = if ($response.fsi_approvedsecuritygroupid) {
                $response.fsi_approvedsecuritygroupid
            } else {
                'created'
            }

            $createdCount++
            Write-Host "    Created: $displayName ($groupId)" -ForegroundColor Green

            $details.Add([PSCustomObject]@{
                GroupId     = $groupId
                DisplayName = $displayName
                Zone        = $group.Zone
                IsActive    = $isActive
                Action      = 'Created'
                Status      = 'Success'
                RecordId    = $newRecordId
            })
        }
    }
    catch {
        $errorCount++
        Write-Warning "    Error processing $displayName ($groupId): $($_.Exception.Message)"

        $details.Add([PSCustomObject]@{
            GroupId     = $groupId
            DisplayName = $displayName
            Zone        = $group.Zone
            IsActive    = $isActive
            Action      = 'Error'
            Status      = 'Failed'
            RecordId    = $null
            Error       = $_.Exception.Message
        })
    }
}

# ─── Build Results ────────────────────────────────────────────────────
$duration = ([DateTime]::UtcNow - $startTime).TotalSeconds

$results = [PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        Timestamp     = $startTime.ToString('o')
        InputFile     = $inputFile.Name
        InputFormat   = $InputFormat
        TotalRecords  = $groups.Count
        DataverseUrl  = $DataverseUrl
        DefaultZone   = $DefaultZone
        DurationSeconds = [math]::Round($duration, 2)
    }
    Summary = [PSCustomObject]@{
        Created = $createdCount
        Updated = $updatedCount
        Skipped = $skippedCount
        Errors  = $errorCount
    }
    Details = $details.ToArray()
}

# ─── Console Summary Banner ──────────────────────────────────────────
$bannerColor = if ($errorCount -gt 0) { 'Yellow' } elseif ($createdCount + $updatedCount -gt 0) { 'Green' } else { 'Cyan' }

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor $bannerColor
Write-Host   "║  Import Complete                                        ║" -ForegroundColor $bannerColor
Write-Host   "╠══════════════════════════════════════════════════════════╣" -ForegroundColor $bannerColor
$line1 = "  Total: $($groups.Count)   Created: $createdCount   Updated: $updatedCount"
Write-Host   "║$($line1.PadRight(58).Substring(0, 58))║" -ForegroundColor $bannerColor
$line2 = "  Skipped: $skippedCount   Errors: $errorCount"
Write-Host   "║$($line2.PadRight(58).Substring(0, 58))║" -ForegroundColor $bannerColor
Write-Host   "╚══════════════════════════════════════════════════════════╝" -ForegroundColor $bannerColor
Write-Host ""
Write-Host "  Duration: $([math]::Round($duration, 2))s" -ForegroundColor DarkGray
Write-Host ""

# ─── Return Results ──────────────────────────────────────────────────
Write-Output $results
