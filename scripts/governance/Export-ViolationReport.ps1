<#
.SYNOPSIS
    Exports sharing violation records from Dataverse for compliance reporting.

.DESCRIPTION
    Queries the fsi_SharingViolation Dataverse table and exports violation
    records to CSV or JSON format. Supports filtering by date range, zone,
    violation type, and status.

    Optionally computes a SHA-256 integrity hash over the exported data for
    evidence packaging and regulatory audit trails.

    Optionally joins active exception records from fsi_SharingException
    for comprehensive compliance review.

.PARAMETER DataverseUrl
    Dataverse environment URL (e.g., https://org.crm.dynamics.com).

.PARAMETER OutputFormat
    Output format. Valid values: CSV, JSON, Object. Default: CSV.

.PARAMETER OutputPath
    File path for the exported report. Required for CSV and JSON formats.

.PARAMETER StartDate
    Optional start date filter (inclusive). ISO 8601 format.

.PARAMETER EndDate
    Optional end date filter (inclusive). ISO 8601 format.

.PARAMETER ViolationType
    Optional violation type filter. Valid: ORG_WIDE_SHARING, PUBLIC_INTERNET_LINK,
    UNAPPROVED_GROUP, EXCESSIVE_INDIVIDUAL, CROSS_TENANT_ACCESS.

.PARAMETER Status
    Optional violation status filter. Valid: Open, Remediated, Exception_Granted, False_Positive.

.PARAMETER Zone
    Optional governance zone filter. Valid: Zone1, Zone2, Zone3, Unclassified, All.
    'All' returns violations from all zones (no zone filter applied).

.PARAMETER IncludeEvidence
    When specified, computes SHA-256 integrity hash over results.

.PARAMETER IncludeExceptions
    When specified, joins active exception records for each violation.

.EXAMPLE
    .\Export-ViolationReport.ps1 -DataverseUrl https://org.crm.dynamics.com -OutputPath .\violations.csv

    Exports all violation records to CSV with default settings.

.EXAMPLE
    .\Export-ViolationReport.ps1 -DataverseUrl https://org.crm.dynamics.com -OutputFormat JSON -OutputPath .\evidence\violations.json -IncludeEvidence -StartDate 2026-01-01

    Exports violations since January 2026 to JSON with SHA-256 evidence hash.

.EXAMPLE
    .\Export-ViolationReport.ps1 -DataverseUrl https://org.crm.dynamics.com -ViolationType PUBLIC_INTERNET_LINK -Status Open -OutputFormat Object

    Returns open public internet link violations as PowerShell objects.

.EXAMPLE
    .\Export-ViolationReport.ps1 -DataverseUrl https://org.crm.dynamics.com -Zone Zone1 -IncludeExceptions -OutputPath .\zone1-report.csv

    Exports Zone 1 violations with joined exception data to CSV.

.OUTPUTS
    PSCustomObject with Metadata, Summary, Records, and optional EvidenceHash properties.

.NOTES
    Part of the FSI Agent Governance — Unrestricted Agent Sharing Detector.
    Controls: 1.1, 3.8
    Version: 1.0.0
    Requires: Az.Accounts for Dataverse authentication
#>

#Requires -Version 7.0
#Requires -Modules Az.Accounts

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$DataverseUrl,

    [Parameter()]
    [ValidateSet('CSV', 'JSON', 'Object')]
    [string]$OutputFormat = 'CSV',

    [Parameter()]
    [string]$OutputPath,

    [Parameter()]
    [datetime]$StartDate,

    [Parameter()]
    [datetime]$EndDate,

    [Parameter()]
    [ValidateSet('ORG_WIDE_SHARING', 'PUBLIC_INTERNET_LINK', 'UNAPPROVED_GROUP',
                 'EXCESSIVE_INDIVIDUAL', 'CROSS_TENANT_ACCESS')]
    [string]$ViolationType,

    [Parameter()]
    [ValidateSet('Open', 'Remediated', 'Exception_Granted', 'False_Positive')]
    [string]$Status,

    [Parameter()]
    [ValidateSet('Zone1', 'Zone2', 'Zone3', 'Unclassified', 'All')]
    [string]$Zone,

    [Parameter()]
    [switch]$IncludeEvidence,

    [Parameter()]
    [switch]$IncludeExceptions
)

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — Export Violation Report          ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$ErrorActionPreference = 'Stop'

# ─── Validate Parameters ─────────────────────────────────────────────
if ($OutputFormat -in @('CSV', 'JSON') -and -not $OutputPath) {
    throw "OutputPath is required when OutputFormat is '$OutputFormat'."
}

if ($StartDate -and $EndDate -and $StartDate -gt $EndDate) {
    throw "StartDate ($StartDate) cannot be after EndDate ($EndDate)."
}

# ─── WhatIf Preview ──────────────────────────────────────────────────
if (-not $PSCmdlet.ShouldProcess("Dataverse: $DataverseUrl", "Export violation report")) {
    Write-Verbose "WhatIf: Would query fsi_sharingviolations and export to $OutputFormat"
    return
}

# ─── Option Set Mappings ─────────────────────────────────────────────

$ViolationTypeMap = @{
    0 = 'ORG_WIDE_SHARING'
    1 = 'PUBLIC_INTERNET_LINK'
    2 = 'UNAPPROVED_GROUP'
    3 = 'EXCESSIVE_INDIVIDUAL'
    4 = 'CROSS_TENANT_ACCESS'
}

$ViolationTypeReverseMap = @{
    'ORG_WIDE_SHARING'     = 0
    'PUBLIC_INTERNET_LINK'  = 1
    'UNAPPROVED_GROUP'      = 2
    'EXCESSIVE_INDIVIDUAL'  = 3
    'CROSS_TENANT_ACCESS'   = 4
}

$ViolationStatusMap = @{
    0 = 'Open'
    1 = 'Remediated'
    2 = 'Exception_Granted'
    3 = 'False_Positive'
}

$ViolationStatusReverseMap = @{
    'Open'              = 0
    'Remediated'        = 1
    'Exception_Granted' = 2
    'False_Positive'    = 3
}

$ZoneMap = @{
    0 = 'Unclassified'
    1 = 'Zone1'
    2 = 'Zone2'
    3 = 'Zone3'
}

$ZoneReverseMap = @{
    'Unclassified' = 0
    'Zone1' = 1
    'Zone2' = 2
    'Zone3' = 3
}

$SeverityMap = @{
    0 = 'Critical'
    1 = 'High'
    2 = 'Medium'
    3 = 'Low'
}

$ExceptionStatusMap = @{
    0 = 'Pending'
    1 = 'Approved'
    2 = 'Denied'
    3 = 'Expired'
}

# ═══════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════

function Get-DataverseToken {
    <#
    .SYNOPSIS
        Obtains an access token for the Dataverse API.
    .DESCRIPTION
        Uses Az.Accounts to acquire an OAuth token scoped to the Dataverse
        environment URL. Requires an active Azure session (Connect-AzAccount).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$EnvironmentUrl
    )

    try {
        $resourceUrl = $EnvironmentUrl.TrimEnd('/')
        $tokenResult = Get-AzAccessToken -ResourceUrl $resourceUrl -ErrorAction Stop
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
        Wrapper around Invoke-RestMethod that adds the Bearer token header,
        OData preferences, and provides consistent error handling.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Uri,

        [Parameter(Mandatory)]
        [string]$Token,

        [Parameter()]
        [ValidateSet('GET', 'POST', 'PUT', 'PATCH', 'DELETE')]
        [string]$Method = 'GET'
    )

    try {
        $headers = @{
            Authorization    = "Bearer $Token"
            'Content-Type'   = 'application/json'
            'OData-MaxVersion' = '4.0'
            'OData-Version'    = '4.0'
            'Prefer'           = 'odata.include-annotations="*",odata.maxpagesize=5000'
        }
        $response = Invoke-RestMethod -Uri $Uri -Method $Method -Headers $headers -ErrorAction Stop
        return $response
    }
    catch {
        $statusCode = $null
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }
        Write-Warning "Dataverse API call failed ($Method $Uri) [HTTP $statusCode]: $($_.Exception.Message)"
        return $null
    }
}

function New-ODataFilter {
    <#
    .SYNOPSIS
        Constructs an OData $filter string from the provided parameters.
    .DESCRIPTION
        Builds a filter expression for the fsi_sharingviolations entity set
        based on date range, violation type, status, and zone filters.
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [datetime]$FilterStartDate,

        [Parameter()]
        [datetime]$FilterEndDate,

        [Parameter()]
        [string]$FilterViolationType,

        [Parameter()]
        [string]$FilterStatus,

        [Parameter()]
        [string]$FilterZone
    )

    $filters = [System.Collections.Generic.List[string]]::new()
    $descriptions = [System.Collections.Generic.List[string]]::new()

    if ($FilterStartDate) {
        $isoDate = $FilterStartDate.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        $filters.Add("fsi_detectedat ge $isoDate")
        $descriptions.Add("StartDate >= $($FilterStartDate.ToString('yyyy-MM-dd'))")
    }

    if ($FilterEndDate) {
        $isoDate = $FilterEndDate.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        $filters.Add("fsi_detectedat le $isoDate")
        $descriptions.Add("EndDate <= $($FilterEndDate.ToString('yyyy-MM-dd'))")
    }

    if ($FilterViolationType) {
        $typeValue = $script:ViolationTypeReverseMap[$FilterViolationType]
        $filters.Add("fsi_violationtype eq $typeValue")
        $descriptions.Add("ViolationType = $FilterViolationType")
    }

    if ($FilterStatus) {
        $statusValue = $script:ViolationStatusReverseMap[$FilterStatus]
        $filters.Add("fsi_violationstatus eq $statusValue")
        $descriptions.Add("Status = $FilterStatus")
    }

    if ($FilterZone -and $FilterZone -ne 'All') {
        $zoneValue = $script:ZoneReverseMap[$FilterZone]
        $filters.Add("fsi_zone eq $zoneValue")
        $descriptions.Add("Zone = $FilterZone")
    }
    elseif ($FilterZone -eq 'All') {
        $descriptions.Add("Zone = All (no filter)")
    }

    $filterString = $null
    if ($filters.Count -gt 0) {
        $filterString = $filters -join ' and '
    }

    $filterDescription = if ($descriptions.Count -gt 0) {
        $descriptions -join '; '
    }
    else {
        'None (all records)'
    }

    return @{
        Filter      = $filterString
        Description = $filterDescription
    }
}

function ConvertTo-ViolationRecord {
    <#
    .SYNOPSIS
        Maps a Dataverse fsi_SharingViolation entity to a clean output object.
    .DESCRIPTION
        Translates numeric option set values to readable labels and extracts
        key fields into a standardized PSCustomObject for reporting.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [PSCustomObject]$Entity
    )

    $typeValue = $Entity.fsi_violationtype
    $statusValue = $Entity.fsi_violationstatus
    $zoneValue = $Entity.fsi_zone
    $severityValue = $Entity.fsi_severity

    $typeName = if ($null -ne $typeValue -and $script:ViolationTypeMap.ContainsKey([int]$typeValue)) {
        $script:ViolationTypeMap[[int]$typeValue]
    } else { 'Unknown' }

    $statusName = if ($null -ne $statusValue -and $script:ViolationStatusMap.ContainsKey([int]$statusValue)) {
        $script:ViolationStatusMap[[int]$statusValue]
    } else { 'Unknown' }

    $zoneName = if ($null -ne $zoneValue -and $script:ZoneMap.ContainsKey([int]$zoneValue)) {
        $script:ZoneMap[[int]$zoneValue]
    } else { 'Unspecified' }

    $severityName = if ($null -ne $severityValue -and $script:SeverityMap.ContainsKey([int]$severityValue)) {
        $script:SeverityMap[[int]$severityValue]
    } else { 'Unspecified' }

    [PSCustomObject]@{
        ViolationId     = $Entity.fsi_sharingviolationid
        ViolationName   = $Entity.fsi_violationname
        AgentId         = $Entity.fsi_agentid
        AgentName       = $Entity.fsi_agentname
        EnvironmentId   = $Entity.fsi_environmentid
        EnvironmentName = $Entity.fsi_environmentname
        ViolationType   = $typeName
        Status          = $statusName
        Zone            = $zoneName
        Severity        = $severityName
        Description     = $Entity.fsi_description
        DetectedAt      = if ($Entity.fsi_detectedat) { $Entity.fsi_detectedat } else { $Entity.createdon }
        ModifiedAt      = $Entity.modifiedon
        RemediatedAt    = $Entity.fsi_remediatedon
        RemediatedBy    = $Entity.fsi_remediatedby
        PrincipalCount  = $Entity.fsi_principalcount
        PrincipalDetail = $Entity.fsi_principaldetail
        EvidenceJson    = $Entity.fsi_evidencejson
        EvidenceHash    = $Entity.fsi_evidencehash
    }
}

function Get-EvidenceHash {
    <#
    .SYNOPSIS
        Computes a SHA-256 hash over serialized data for evidence integrity.
    .DESCRIPTION
        Serializes the input object to JSON and computes a SHA-256 hash.
        Used for regulatory audit trail evidence packaging.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Data
    )

    $json = $Data | ConvertTo-Json -Depth 10 -Compress
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha256.ComputeHash(
            [System.Text.Encoding]::UTF8.GetBytes($json)
        )
        return [BitConverter]::ToString($hashBytes) -replace '-'
    }
    finally {
        $sha256.Dispose()
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Main Logic
# ═══════════════════════════════════════════════════════════════════════

$startTime = [DateTime]::UtcNow

# ─── Step 1: Authenticate to Dataverse ────────────────────────────────
Write-Verbose "Step 1: Acquiring Dataverse token..."

try {
    $token = Get-DataverseToken -EnvironmentUrl $DataverseUrl
    Write-Verbose "Dataverse token acquired successfully."
}
catch {
    Write-Error "Cannot proceed without Dataverse token: $($_.Exception.Message)"
    return
}

# ─── Step 2: Build OData Filter ──────────────────────────────────────
Write-Verbose "Step 2: Building OData filter..."

$filterResult = New-ODataFilter `
    -FilterStartDate $StartDate `
    -FilterEndDate $EndDate `
    -FilterViolationType $ViolationType `
    -FilterStatus $Status `
    -FilterZone $Zone

$filterDescription = $filterResult.Description
Write-Verbose "Filter: $filterDescription"

# ─── Step 3: Query Violation Records with Pagination ──────────────────
Write-Verbose "Step 3: Querying fsi_sharingviolations..."

$baseUrl = $DataverseUrl.TrimEnd('/')
$selectColumns = @(
    'fsi_sharingviolationid',
    'fsi_violationname',
    'fsi_agentid',
    'fsi_agentname',
    'fsi_environmentid',
    'fsi_environmentname',
    'fsi_violationtype',
    'fsi_violationstatus',
    'fsi_zone',
    'fsi_severity',
    'fsi_description',
    'fsi_detectedat',
    'createdon',
    'modifiedon',
    'fsi_remediatedon',
    'fsi_remediatedby',
    'fsi_principalcount',
    'fsi_principaldetail',
    'fsi_evidencejson',
    'fsi_evidencehash'
) -join ','

$queryUrl = "$baseUrl/api/data/v9.2/fsi_sharingviolations?`$select=$selectColumns&`$orderby=fsi_detectedat desc"

if ($filterResult.Filter) {
    $queryUrl += "&`$filter=$($filterResult.Filter)"
}

$allRecords = [System.Collections.Generic.List[PSCustomObject]]::new()
$pageCount = 0
$currentUrl = $queryUrl

while ($currentUrl) {
    $pageCount++
    Write-Verbose "  Fetching page $pageCount..."

    $response = Invoke-DataverseApi -Uri $currentUrl -Token $token

    if (-not $response) {
        Write-Warning "Failed to retrieve violation records on page $pageCount."
        break
    }

    if ($response.value) {
        foreach ($record in $response.value) {
            $allRecords.Add($record)
        }
        Write-Verbose "  Page $pageCount returned $($response.value.Count) record(s). Total: $($allRecords.Count)"
    }

    # Handle OData pagination via @odata.nextLink
    $currentUrl = $response.'@odata.nextLink'
}

Write-Verbose "Total records retrieved: $($allRecords.Count)"

# ─── Step 4: Optionally Join Exception Records ───────────────────────
$exceptionLookup = @{}

if ($IncludeExceptions -and $allRecords.Count -gt 0) {
    Write-Verbose "Step 4: Querying fsi_sharingexceptions for joined records..."

    $exceptionUrl = "$baseUrl/api/data/v9.2/fsi_sharingexceptions?`$select=fsi_sharingexceptionid,fsi_violationid,fsi_requestedby,fsi_approvedby,fsi_approvedbysecurity,fsi_approvedbydataowner,fsi_approvedon,fsi_justification,fsi_expireson,fsi_exceptionstatus&`$orderby=createdon desc"

    $exceptionPageUrl = $exceptionUrl
    while ($exceptionPageUrl) {
        $exResponse = Invoke-DataverseApi -Uri $exceptionPageUrl -Token $token

        if (-not $exResponse) {
            Write-Warning "Failed to retrieve exception records."
            break
        }

        if ($exResponse.value) {
            foreach ($ex in $exResponse.value) {
                $violationId = if ($ex.fsi_violationid) { $ex.fsi_violationid.ToString().ToLower() } else { $null }
                if ($violationId -and -not $exceptionLookup.ContainsKey($violationId)) {
                    $exStatusValue = $ex.fsi_exceptionstatus
                    $exStatusName = if ($null -ne $exStatusValue -and $ExceptionStatusMap.ContainsKey([int]$exStatusValue)) {
                        $ExceptionStatusMap[[int]$exStatusValue]
                    } else { 'Unknown' }

                    $exceptionLookup[$violationId] = [PSCustomObject]@{
                        ExceptionId         = $ex.fsi_sharingexceptionid
                        RequestedBy         = $ex.fsi_requestedby
                        ApprovedBy          = $ex.fsi_approvedby
                        ApprovedBySecurity  = $ex.fsi_approvedbysecurity
                        ApprovedByDataOwner = $ex.fsi_approvedbydataowner
                        ApprovedOn          = $ex.fsi_approvedon
                        Justification       = $ex.fsi_justification
                        ExpiresOn           = $ex.fsi_expireson
                        ExceptionStatus     = $exStatusName
                    }
                }
            }
        }

        $exceptionPageUrl = $exResponse.'@odata.nextLink'
    }

    Write-Verbose "Exception records loaded: $($exceptionLookup.Count)"
}
else {
    Write-Verbose "Step 4: Skipping exception join (not requested or no violations)."
}

# ─── Step 5: Map to Clean Violation Records ───────────────────────────
Write-Verbose "Step 5: Mapping records to violation objects..."

$mappedRecords = [System.Collections.Generic.List[PSCustomObject]]::new()

foreach ($raw in $allRecords) {
    $record = ConvertTo-ViolationRecord -Entity $raw

    # Attach exception data if available
    if ($IncludeExceptions -and $record.ViolationId -and $exceptionLookup.ContainsKey($record.ViolationId.ToString().ToLower())) {
        $exception = $exceptionLookup[$record.ViolationId.ToString().ToLower()]
        $record | Add-Member -NotePropertyName 'ExceptionId' -NotePropertyValue $exception.ExceptionId
        $record | Add-Member -NotePropertyName 'ExceptionRequestedBy' -NotePropertyValue $exception.RequestedBy
        $record | Add-Member -NotePropertyName 'ExceptionApprovedBy' -NotePropertyValue $exception.ApprovedBy
        $record | Add-Member -NotePropertyName 'ExceptionApprovedBySecurity' -NotePropertyValue $exception.ApprovedBySecurity
        $record | Add-Member -NotePropertyName 'ExceptionApprovedByDataOwner' -NotePropertyValue $exception.ApprovedByDataOwner
        $record | Add-Member -NotePropertyName 'ExceptionApprovedOn' -NotePropertyValue $exception.ApprovedOn
        $record | Add-Member -NotePropertyName 'ExceptionJustification' -NotePropertyValue $exception.Justification
        $record | Add-Member -NotePropertyName 'ExceptionExpiresOn' -NotePropertyValue $exception.ExpiresOn
        $record | Add-Member -NotePropertyName 'ExceptionStatus' -NotePropertyValue $exception.ExceptionStatus
    }

    $mappedRecords.Add($record)
}

Write-Verbose "Mapped $($mappedRecords.Count) violation record(s)."

# Warn if exceptions were loaded but none matched violations
if ($IncludeExceptions -and $exceptionLookup.Count -gt 0) {
    $matchedCount = @($mappedRecords | Where-Object { $_.PSObject.Properties['ExceptionId'] }).Count
    if ($matchedCount -eq 0) {
        Write-Warning "Exception records found ($($exceptionLookup.Count)) but none matched violation IDs. Check fsi_violationid format in fsi_SharingException records."
    }
}

# ─── Step 6: Compute Summary Statistics ──────────────────────────────
Write-Verbose "Step 6: Computing summary statistics..."

$byType = @{}
foreach ($typeName in $ViolationTypeMap.Values) {
    $byType[$typeName] = @($mappedRecords | Where-Object { $_.ViolationType -eq $typeName }).Count
}

$byStatus = @{}
foreach ($statusName in $ViolationStatusMap.Values) {
    $byStatus[$statusName] = @($mappedRecords | Where-Object { $_.Status -eq $statusName }).Count
}

$byZone = @{}
foreach ($zoneName in $ZoneMap.Values) {
    $byZone[$zoneName] = @($mappedRecords | Where-Object { $_.Zone -eq $zoneName }).Count
}

$bySeverity = @{}
foreach ($sevName in $SeverityMap.Values) {
    $bySeverity[$sevName] = @($mappedRecords | Where-Object { $_.Severity -eq $sevName }).Count
}

# ─── Step 7: Compute Evidence Hash ───────────────────────────────────
$evidenceHash = $null

if ($IncludeEvidence) {
    Write-Verbose "Step 7: Computing SHA-256 evidence hash..."
    $evidenceHash = Get-EvidenceHash -Data $mappedRecords
    Write-Verbose "Evidence hash: $evidenceHash"
}
else {
    Write-Verbose "Step 7: Skipping evidence hash (not requested)."
}

# ─── Step 8: Build Results Object ─────────────────────────────────────
$duration = ([DateTime]::UtcNow - $startTime).TotalSeconds

$results = [PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        ScriptName      = 'Export-ViolationReport.ps1'
        Version         = '1.0.0'
        ExecutedAt      = (Get-Date -Format 'o')
        DataverseUrl    = $DataverseUrl
        FilterApplied   = $filterDescription
        DurationSeconds = [math]::Round($duration, 2)
        PagesRetrieved  = $pageCount
        IncludeExceptions = [bool]$IncludeExceptions
    }
    Summary = [PSCustomObject]@{
        TotalRecords = $mappedRecords.Count
        ByType       = $byType
        ByStatus     = $byStatus
        ByZone       = $byZone
        BySeverity   = $bySeverity
        DateRange    = [PSCustomObject]@{
            Start = if ($StartDate) { $StartDate.ToString('o') } else { $null }
            End   = if ($EndDate) { $EndDate.ToString('o') } else { $null }
        }
    }
    Records      = $mappedRecords.ToArray()
    EvidenceHash = $evidenceHash
}

# ─── Step 9: Export in Requested Format ───────────────────────────────
Write-Verbose "Step 9: Exporting results as $OutputFormat..."

switch ($OutputFormat) {
    'CSV' {
        $parentDir = Split-Path -Path $OutputPath -Parent
        if ($parentDir -and -not (Test-Path $parentDir)) {
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
        }
        $mappedRecords | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding utf8NoBOM
        Write-Host "  Exported $($mappedRecords.Count) record(s) to: $OutputPath" -ForegroundColor Cyan
    }
    'JSON' {
        $parentDir = Split-Path -Path $OutputPath -Parent
        if ($parentDir -and -not (Test-Path $parentDir)) {
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
        }
        $results | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding utf8NoBOM
        Write-Host "  Exported $($mappedRecords.Count) record(s) to: $OutputPath" -ForegroundColor Cyan
    }
    'Object' {
        # Object format — output handled below
    }
}

# ─── Console Summary Banner ──────────────────────────────────────────
$openCount = $byStatus['Open']
$bannerColor = if ($openCount -gt 0) { 'Yellow' } else { 'Green' }

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor $bannerColor
Write-Host   "║  Violation Report Complete                              ║" -ForegroundColor $bannerColor
Write-Host   "╠══════════════════════════════════════════════════════════╣" -ForegroundColor $bannerColor
$line1 = "  Total: $($mappedRecords.Count)   Open: $openCount   Remediated: $($byStatus['Remediated'])"
Write-Host   "║$($line1.PadRight(58).Substring(0, 58))║" -ForegroundColor $bannerColor
$line2 = "  Critical: $($bySeverity['Critical'])   High: $($bySeverity['High'])   Medium: $($bySeverity['Medium'])"
Write-Host   "║$($line2.PadRight(58).Substring(0, 58))║" -ForegroundColor $bannerColor
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor $bannerColor

if ($IncludeEvidence -and $evidenceHash) {
    Write-Host "  Integrity Hash: $evidenceHash" -ForegroundColor DarkGray
}

Write-Host "  Filter: $filterDescription" -ForegroundColor DarkGray
Write-Host "  Duration: $([math]::Round($duration, 2))s" -ForegroundColor DarkGray
Write-Host ""

# ─── Return Results ──────────────────────────────────────────────────
Write-Output $results
