#Requires -Version 7.0

<#
.SYNOPSIS
    Syncs solution assessment records to the Compliance Dashboard for 6 solutions.

.DESCRIPTION
    Queries each solution's Dataverse tables and upserts assessment records to the
    Compliance Dashboard (fsi_controlassessments). Supports all 6 Tier 2 solutions:

    - ACV  (Agent Configuration Validator)  -> Control 1.7
    - SSC  (SharePoint Security Checker)    -> Controls 1.23, 1.11
    - AAM  (Agent Activity Monitor)         -> Control 3.8
    - CMM  (Copilot Metrics Monitor)        -> Control 1.8
    - FUS  (Feature Usage Scanner)          -> Control 1.14
    - DEC  (Deny Event Correlation Report)  -> Controls 1.5, 1.7, 3.4

    DEC uses alert-severity-based status derivation (no direct pass/fail column).
    Control 1.7 is mapped by both ACV and DEC; a post-processing step resolves
    to worst-case (most severe) status when multiple solutions report.

    Status values:
        1 = Compliant
        2 = Partially Compliant
        3 = Non-Compliant
        4 = Not Assessed

.PARAMETER DataverseUrl
    Dataverse environment URL (e.g., https://org.crm.dynamics.com).

.PARAMETER TenantId
    Entra ID tenant ID for authentication.

.PARAMETER ClientId
    Entra ID application (client) ID.

.PARAMETER KeyVaultName
    Azure Key Vault name containing authentication secrets.

.PARAMETER CertificateThumbprint
    Certificate thumbprint for certificate-based service principal authentication.

.PARAMETER Solutions
    Array of solution identifiers to process. Defaults to all 6 solutions.
    Valid values: ACV, SSC, AAM, CMM, FUS, DEC.

.PARAMETER DryRun
    When specified, outputs per-solution and per-zone status summaries without
    writing to Dataverse.

.EXAMPLE
    Sync-SolutionAssessments -DataverseUrl "https://org.crm.dynamics.com" `
        -TenantId "00000000-0000-0000-0000-000000000000" `
        -ClientId "11111111-1111-1111-1111-111111111111" `
        -CertificateThumbprint "ABC123"

    Syncs all 6 solutions to the Compliance Dashboard.

.EXAMPLE
    Sync-SolutionAssessments -DataverseUrl "https://org.crm.dynamics.com" `
        -TenantId "00000000-0000-0000-0000-000000000000" `
        -ClientId "11111111-1111-1111-1111-111111111111" `
        -CertificateThumbprint "ABC123" `
        -Solutions @('DEC') -DryRun

    Previews DEC assessment records without writing to Dataverse.

.NOTES
    Version:        1.0.0
    Framework:      FSI Agent Governance Framework v1.2.38
    Pattern source: v9 cross-solution integration infrastructure
    Solutions:      ACV, SSC, AAM, CMM, FUS, DEC (6 total)
    Requirement:    EVI-05 — Sync-SolutionAssessments queries fsi_denycorrelation
                    and translates to Compliance Dashboard assessment records
    Overlap:        Control 1.7 is mapped by ACV and DEC; worst-case status wins
#>

# ===================================================================
# Import IntegrationConfig module from same directory
# ===================================================================
$configModulePath = Join-Path -Path $PSScriptRoot -ChildPath 'IntegrationConfig.psm1'
if (-not (Test-Path $configModulePath)) {
    Write-Error "IntegrationConfig.psm1 not found at '$configModulePath'. This module is required."
    return
}
Import-Module $configModulePath -Force


# ===================================================================
# Private Helper: Invoke-DataverseQuery
# ===================================================================
function Invoke-DataverseQuery {
    <#
    .SYNOPSIS
        Executes an OData query against Dataverse with pagination support.
    .DESCRIPTION
        Sends GET requests to the Dataverse Web API and handles automatic
        pagination via @odata.nextLink. Returns the complete data array.
    #>
    [CmdletBinding()]
    [OutputType([System.Collections.Generic.List[PSObject]])]
    param(
        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$Url,

        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$Token,

        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$EntitySet,

        [string]$Filter,

        [string]$Select,

        [string]$OrderBy,

        [int]$Top = 0
    )

    $results = [System.Collections.Generic.List[PSObject]]::new()

    # Build OData query URL
    $queryUrl = "$($Url.TrimEnd('/'))/api/data/v9.2/$EntitySet"
    $queryParams = @()

    if ($Filter)  { $queryParams += "`$filter=$Filter" }
    if ($Select)  { $queryParams += "`$select=$Select" }
    if ($OrderBy) { $queryParams += "`$orderby=$OrderBy" }
    if ($Top -gt 0) { $queryParams += "`$top=$Top" }

    if ($queryParams.Count -gt 0) {
        $queryUrl += '?' + ($queryParams -join '&')
    }

    $headers = @{
        'Authorization' = "Bearer $Token"
        'Accept'        = 'application/json'
        'OData-MaxVersion' = '4.0'
        'OData-Version'    = '4.0'
        'Prefer'           = 'odata.include-annotations="*"'
    }

    # Paginate through results
    $currentUrl = $queryUrl
    do {
        Write-Verbose "Querying: $currentUrl"

        try {
            $response = Invoke-RestMethod -Uri $currentUrl -Headers $headers -Method Get -ErrorAction Stop
        }
        catch {
            Write-Error "Dataverse query failed: $_"
            return $results
        }

        if ($response.value) {
            foreach ($record in $response.value) {
                $results.Add($record)
            }
        }

        # Follow pagination link if present
        $currentUrl = $response.'@odata.nextLink'

    } while ($currentUrl)

    Write-Verbose "Query returned $($results.Count) records from $EntitySet."
    return $results
}


# ===================================================================
# Private Helper: Invoke-AssessmentUpsert
# ===================================================================
function Invoke-AssessmentUpsert {
    <#
    .SYNOPSIS
        Upserts an assessment record to fsi_controlassessments.
    .DESCRIPTION
        Checks for an existing same-day assessment record for the given
        control/zone combination. If found, PATCHes the existing record.
        If not found, POSTs a new record.
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$DataverseUrl,

        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$Token,

        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$ControlId,

        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$Zone,

        [Parameter(Mandatory)]
        [ValidateRange(1, 4)]
        [int]$Status,

        [string]$Notes = '',

        [Parameter(Mandatory)]
        [datetime]$AssessmentDate
    )

    $baseUrl = "$($DataverseUrl.TrimEnd('/'))/api/data/v9.2"
    $entitySet = 'fsi_controlassessments'
    $dateStr = $AssessmentDate.ToString('yyyy-MM-dd')

    $headers = @{
        'Authorization'    = "Bearer $Token"
        'Accept'           = 'application/json'
        'OData-MaxVersion' = '4.0'
        'OData-Version'    = '4.0'
        'Content-Type'     = 'application/json'
    }

    # Check for existing same-day assessment
    $existingFilter = "fsi_controlid eq '$ControlId' and fsi_zone eq '$Zone' and fsi_assessmentdate eq $dateStr"
    $existingUrl = "$baseUrl/$entitySet?`$filter=$existingFilter&`$top=1"

    try {
        $existingResponse = Invoke-RestMethod -Uri $existingUrl -Headers $headers -Method Get -ErrorAction Stop
    }
    catch {
        Write-Error "Failed to query existing assessment for Control $ControlId, Zone $Zone : $_"
        return [PSCustomObject]@{
            ControlId = $ControlId
            Zone      = $Zone
            Action    = 'Error'
            Success   = $false
            Error     = $_.Exception.Message
        }
    }

    $body = @{
        fsi_controlid      = $ControlId
        fsi_zone           = $Zone
        fsi_status         = $Status
        fsi_assessmentdate = $dateStr
        fsi_notes          = $Notes
    } | ConvertTo-Json -Depth 5

    $action = 'POST'

    try {
        if ($existingResponse.value -and $existingResponse.value.Count -gt 0) {
            # PATCH existing record
            $recordId = $existingResponse.value[0].fsi_controlassessmentid
            $patchUrl = "$baseUrl/$entitySet($recordId)"
            Invoke-RestMethod -Uri $patchUrl -Headers $headers -Method Patch -Body $body -ErrorAction Stop | Out-Null
            $action = 'PATCH'
            Write-Verbose "Updated existing assessment: Control $ControlId, Zone $Zone, Status $Status"
        }
        else {
            # POST new record
            $postUrl = "$baseUrl/$entitySet"
            Invoke-RestMethod -Uri $postUrl -Headers $headers -Method Post -Body $body -ErrorAction Stop | Out-Null
            Write-Verbose "Created new assessment: Control $ControlId, Zone $Zone, Status $Status"
        }
    }
    catch {
        Write-Error "Failed to upsert assessment for Control $ControlId, Zone $Zone : $_"
        return [PSCustomObject]@{
            ControlId = $ControlId
            Zone      = $Zone
            Action    = 'Error'
            Success   = $false
            Error     = $_.Exception.Message
        }
    }

    [PSCustomObject]@{
        ControlId = $ControlId
        Zone      = $Zone
        Action    = $action
        Success   = $true
        Error     = $null
    }
}


# ===================================================================
# Private Helper: Resolve-SeverityName
# ===================================================================
function Resolve-SeverityName {
    <#
    .SYNOPSIS
        Maps Dataverse option set values and string severity names to canonical names.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        $Value
    )

    switch ($Value) {
        864340000  { 'Critical' }
        864340001  { 'High' }
        864340002  { 'Warning' }
        864340003  { 'Info' }
        'Critical' { 'Critical' }
        'High'     { 'High' }
        'Warning'  { 'Warning' }
        'Info'     { 'Info' }
        default    { 'Info' }
    }
}


# ===================================================================
# Main Function: Sync-SolutionAssessments
# ===================================================================
function Sync-SolutionAssessments {
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$DataverseUrl,

        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$TenantId,

        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$ClientId,

        [string]$KeyVaultName,

        [string]$CertificateThumbprint,

        [ValidateSet('ACV', 'SSC', 'AAM', 'CMM', 'FUS', 'DEC')]
        [string[]]$Solutions = @('ACV', 'SSC', 'AAM', 'CMM', 'FUS', 'DEC'),

        [switch]$DryRun
    )

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $today = (Get-Date).Date
    $dateStr = $today.ToString('yyyy-MM-dd')
    $dateTimeStr = $today.ToString('yyyy-MM-ddT00:00:00Z')

    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "  Compliance Dashboard Sync — $dateStr" -ForegroundColor Cyan
    Write-Host "  Solutions: $($Solutions -join ', ')" -ForegroundColor Cyan
    if ($DryRun) {
        Write-Host "  MODE: DRY RUN (no writes to Dataverse)" -ForegroundColor Yellow
    }
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host ""

    # ===================================================================
    # Step 1: Authenticate to Dataverse
    # ===================================================================
    Write-Verbose "Authenticating to Dataverse..."

    $token = $null
    try {
        if ($CertificateThumbprint) {
            $authResult = Get-MsalToken -TenantId $TenantId -ClientId $ClientId `
                -ClientCertificate (Get-Item "Cert:\CurrentUser\My\$CertificateThumbprint") `
                -Scopes "$($DataverseUrl.TrimEnd('/'))/.default"
            $token = $authResult.AccessToken
        }
        elseif ($KeyVaultName) {
            # Retrieve secret from Key Vault for client credential flow
            $secret = Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name 'SyncClientSecret' -AsPlainText
            $secureSecret = ConvertTo-SecureString $secret -AsPlainText -Force
            $authResult = Get-MsalToken -TenantId $TenantId -ClientId $ClientId `
                -ClientSecret $secureSecret `
                -Scopes "$($DataverseUrl.TrimEnd('/'))/.default"
            $token = $authResult.AccessToken
        }
        else {
            Write-Error "Authentication requires either -CertificateThumbprint or -KeyVaultName."
            return
        }
    }
    catch {
        Write-Error "Authentication failed: $_"
        return
    }

    Write-Verbose "Authentication successful."

    # ===================================================================
    # Step 2: Load integration configuration
    # ===================================================================
    $controlMappings  = Get-SolutionControlMapping
    $allZones         = @('1', '2', '3')

    # Track all upserted assessments for overlap resolution
    $assessmentLog = [System.Collections.Generic.List[PSCustomObject]]::new()

    # Track per-solution summaries for DryRun output
    $solutionSummaries = [System.Collections.Generic.List[PSCustomObject]]::new()

    # ===================================================================
    # Step 3: Per-solution processing loop
    # ===================================================================
    foreach ($solution in $Solutions) {
        Write-Host "Processing $solution..." -ForegroundColor White

        $tableConfig = (Get-SolutionTableConfig)[$solution]
        $solutionControls = $controlMappings[$solution]

        if (-not $solutionControls) {
            Write-Warning "No control mappings found for solution '$solution'. Skipping."
            continue
        }

        if (-not $tableConfig) {
            Write-Warning "No table configuration found for solution '$solution'. Skipping."
            continue
        }

        # =============================================================
        # DEC-specific processing: alert-severity-based status
        # =============================================================
        if ($solution -eq 'DEC') {
            Write-Verbose "DEC: Using alert-severity-based status derivation."

            # Query today's correlation summaries
            $correlationFilter = "fsi_correlation_date ge $dateStr"
            $correlations = Invoke-DataverseQuery -Url $DataverseUrl -Token $token `
                -EntitySet $tableConfig.PrimaryTable `
                -Filter $correlationFilter `
                -OrderBy 'fsi_correlation_date desc'

            # Query today's alerts for severity distribution
            $alertFilter = "fsi_alert_timestamp ge $dateTimeStr"
            $alerts = Invoke-DataverseQuery -Url $DataverseUrl -Token $token `
                -EntitySet $tableConfig.AlertTable `
                -Filter $alertFilter `
                -OrderBy 'fsi_alert_timestamp desc'

            Write-Verbose "DEC: $($correlations.Count) correlations, $($alerts.Count) alerts."

            # Group correlations by zone
            $zoneGroups = $correlations | Group-Object -Property fsi_zone

            # Track assessed zones for gap fill
            $assessedZones = [System.Collections.Generic.List[string]]::new()

            foreach ($zoneGroup in $zoneGroups) {
                $zone = Get-CanonicalZoneValue -Value $zoneGroup.Name
                $assessedZones.Add($zone)

                # Filter alerts to this zone
                $zoneAlerts = $alerts | Where-Object {
                    (Get-CanonicalZoneValue -Value $_.fsi_zone) -eq $zone
                }

                # Build severity distribution hashtable
                $severityDist = @{
                    Critical = 0
                    High     = 0
                    Warning  = 0
                    Info     = 0
                }

                foreach ($alert in $zoneAlerts) {
                    $sevName = Resolve-SeverityName -Value $alert.fsi_severity
                    if ($severityDist.ContainsKey($sevName)) {
                        $severityDist[$sevName]++
                    }
                }

                # Derive status via IntegrationConfig
                $status = ConvertTo-DashboardStatus -SolutionId 'DEC' -InputStatus $severityDist

                $eventCount = ($zoneGroup.Group | Measure-Object -Property fsi_event_count -Sum).Sum
                $alertCount = ($zoneAlerts | Measure-Object).Count

                # Upsert assessment for each mapped control
                foreach ($controlId in $solutionControls) {
                    $notes = "Automated: DenyEventCorrelation — $eventCount events, $alertCount alerts " +
                             "(Critical:$($severityDist.Critical) High:$($severityDist.High) " +
                             "Warning:$($severityDist.Warning) Info:$($severityDist.Info))"

                    if (-not $DryRun) {
                        $result = Invoke-AssessmentUpsert -DataverseUrl $DataverseUrl -Token $token `
                            -ControlId $controlId -Zone $zone -Status $status `
                            -Notes $notes -AssessmentDate $today
                    }

                    $assessmentLog.Add([PSCustomObject]@{
                        Solution  = 'DEC'
                        ControlId = $controlId
                        Zone      = $zone
                        Status    = $status
                        Notes     = $notes
                        Action    = if ($DryRun) { 'DryRun' } else { $result.Action }
                    })
                }
            }

            # Handle zones with no correlations today -> Status 4 (Not Assessed)
            $unassessedZones = $allZones | Where-Object { $_ -notin $assessedZones }
            foreach ($zone in $unassessedZones) {
                foreach ($controlId in $solutionControls) {
                    $notes = "Automated: DenyEventCorrelation — No correlations for today"

                    if (-not $DryRun) {
                        $result = Invoke-AssessmentUpsert -DataverseUrl $DataverseUrl -Token $token `
                            -ControlId $controlId -Zone $zone -Status 4 `
                            -Notes $notes -AssessmentDate $today
                    }

                    $assessmentLog.Add([PSCustomObject]@{
                        Solution  = 'DEC'
                        ControlId = $controlId
                        Zone      = $zone
                        Status    = 4
                        Notes     = $notes
                        Action    = if ($DryRun) { 'DryRun' } else { $result.Action }
                    })
                }
            }

            $solutionSummaries.Add([PSCustomObject]@{
                Solution        = 'DEC'
                CorrelationCount = $correlations.Count
                AlertCount      = $alerts.Count
                ZonesAssessed   = $assessedZones.Count
                ZonesGapFilled  = $unassessedZones.Count
                Controls        = $solutionControls -join ', '
                StatusDerivation = 'AlertBased'
            })

        }
        # =============================================================
        # Standard solution processing: direct status column
        # =============================================================
        else {
            # Query primary table with today's date filter
            $primaryFilter = switch ($solution) {
                'ACV' { "fsi_validation_date ge $dateStr" }
                'SSC' { "fsi_scan_date ge $dateStr" }
                'AAM' { "fsi_assessment_date ge $dateStr" }
                'CMM' { "fsi_metric_date ge $dateStr" }
                'FUS' { "fsi_scan_date ge $dateStr" }
            }

            $records = Invoke-DataverseQuery -Url $DataverseUrl -Token $token `
                -EntitySet $tableConfig.PrimaryTable `
                -Filter $primaryFilter

            Write-Verbose "$solution : $($records.Count) records."

            # Group by zone
            $zoneGroups = $records | Group-Object -Property fsi_zone
            $assessedZones = [System.Collections.Generic.List[string]]::new()

            foreach ($zoneGroup in $zoneGroups) {
                $zone = Get-CanonicalZoneValue -Value $zoneGroup.Name
                $assessedZones.Add($zone)

                # Derive status from status column
                $statusColumn = $tableConfig.StatusColumn
                $latestRecord = $zoneGroup.Group |
                    Sort-Object -Property $statusColumn -Descending |
                    Select-Object -First 1

                $status = ConvertTo-DashboardStatus -SolutionId $solution -InputStatus $latestRecord.$statusColumn
                $recordCount = $zoneGroup.Group.Count

                foreach ($controlId in $solutionControls) {
                    $notes = "Automated: $solution — $recordCount records processed"

                    if (-not $DryRun) {
                        $result = Invoke-AssessmentUpsert -DataverseUrl $DataverseUrl -Token $token `
                            -ControlId $controlId -Zone $zone -Status $status `
                            -Notes $notes -AssessmentDate $today
                    }

                    $assessmentLog.Add([PSCustomObject]@{
                        Solution  = $solution
                        ControlId = $controlId
                        Zone      = $zone
                        Status    = $status
                        Notes     = $notes
                        Action    = if ($DryRun) { 'DryRun' } else { $result.Action }
                    })
                }
            }

            # Handle zones with no records -> Status 4 (Not Assessed)
            $unassessedZones = $allZones | Where-Object { $_ -notin $assessedZones }
            foreach ($zone in $unassessedZones) {
                foreach ($controlId in $solutionControls) {
                    $notes = "Automated: $solution — No records for today"

                    if (-not $DryRun) {
                        $result = Invoke-AssessmentUpsert -DataverseUrl $DataverseUrl -Token $token `
                            -ControlId $controlId -Zone $zone -Status 4 `
                            -Notes $notes -AssessmentDate $today
                    }

                    $assessmentLog.Add([PSCustomObject]@{
                        Solution  = $solution
                        ControlId = $controlId
                        Zone      = $zone
                        Status    = 4
                        Notes     = $notes
                        Action    = if ($DryRun) { 'DryRun' } else { $result.Action }
                    })
                }
            }

            $solutionSummaries.Add([PSCustomObject]@{
                Solution        = $solution
                CorrelationCount = 0
                AlertCount      = 0
                ZonesAssessed   = $assessedZones.Count
                ZonesGapFilled  = $unassessedZones.Count
                Controls        = $solutionControls -join ', '
                StatusDerivation = 'Direct'
            })
        }

        Write-Host "  $solution complete." -ForegroundColor Green
    }

    # ===================================================================
    # Step 4: Post-processing — Multi-solution overlap resolution
    # ===================================================================
    Write-Host ""
    Write-Host "Resolving multi-solution control overlaps..." -ForegroundColor White

    # Detect overlapping controls: controls mapped by more than one solution
    $controlToSolutions = @{}
    foreach ($sol in $Solutions) {
        $solControls = $controlMappings[$sol]
        if (-not $solControls) { continue }
        foreach ($ctrl in $solControls) {
            if (-not $controlToSolutions.ContainsKey($ctrl)) {
                $controlToSolutions[$ctrl] = [System.Collections.Generic.List[string]]::new()
            }
            $controlToSolutions[$ctrl].Add($sol)
        }
    }

    $overlappingControls = $controlToSolutions.GetEnumerator() |
        Where-Object { $_.Value.Count -gt 1 }

    if ($overlappingControls) {
        foreach ($overlap in $overlappingControls) {
            $controlId = $overlap.Key
            $sourceSolutions = $overlap.Value -join ', '

            Write-Host "  Control $controlId mapped by: $sourceSolutions" -ForegroundColor Yellow

            foreach ($zone in $allZones) {
                # Get all assessments for this control/zone from the log
                $zoneAssessments = $assessmentLog | Where-Object {
                    $_.ControlId -eq $controlId -and $_.Zone -eq $zone
                }

                if ($zoneAssessments.Count -le 1) { continue }

                # Resolve to worst-case status
                # Status 4 (Not Assessed) is neutral — does not override real assessments
                $realStatuses = $zoneAssessments | Where-Object { $_.Status -ne 4 } |
                    Select-Object -ExpandProperty Status

                if ($realStatuses.Count -eq 0) {
                    # All solutions reported Not Assessed — keep Status 4
                    $resolvedStatus = 4
                }
                elseif ($realStatuses.Count -eq 1) {
                    # Only one real assessment — use it
                    $resolvedStatus = $realStatuses[0]
                }
                else {
                    # Multiple real assessments — worst-case (highest numeric) wins
                    $resolvedStatus = ($realStatuses | Measure-Object -Maximum).Maximum
                }

                # Build combined notes referencing all source solutions
                $sourceNotes = ($zoneAssessments | ForEach-Object {
                    "$($_.Solution):Status=$($_.Status)"
                }) -join '; '
                $combinedNotes = "Automated: Multi-solution overlap resolved for Control $controlId " +
                                 "Zone $zone — Worst-case status from [$sourceSolutions]. Sources: $sourceNotes"

                Write-Verbose "Control $controlId Zone $zone : Resolved to status $resolvedStatus (from $sourceSolutions)."

                if (-not $DryRun) {
                    Invoke-AssessmentUpsert -DataverseUrl $DataverseUrl -Token $token `
                        -ControlId $controlId -Zone $zone -Status $resolvedStatus `
                        -Notes $combinedNotes -AssessmentDate $today | Out-Null
                }

                # Update the log entries to reflect resolved status
                foreach ($entry in $zoneAssessments) {
                    $entry.Status = $resolvedStatus
                    $entry.Notes  = $combinedNotes
                }
            }
        }

        Write-Host "  Overlap resolution complete." -ForegroundColor Green
    }
    else {
        Write-Host "  No overlapping controls detected." -ForegroundColor DarkGray
    }

    # ===================================================================
    # Step 5: DryRun output
    # ===================================================================
    if ($DryRun) {
        Write-Host ""
        Write-Host "========================================================" -ForegroundColor Yellow
        Write-Host "  DRY RUN SUMMARY" -ForegroundColor Yellow
        Write-Host "========================================================" -ForegroundColor Yellow
        Write-Host ""

        # Per-solution summary
        Write-Host "--- Solution Summaries ---" -ForegroundColor Cyan
        foreach ($summary in $solutionSummaries) {
            Write-Host ""
            Write-Host "  Solution:          $($summary.Solution)" -ForegroundColor White
            Write-Host "  Controls:          $($summary.Controls)"
            Write-Host "  Status Derivation: $($summary.StatusDerivation)"
            Write-Host "  Zones Assessed:    $($summary.ZonesAssessed)"
            Write-Host "  Zones Gap-Filled:  $($summary.ZonesGapFilled)"
            if ($summary.Solution -eq 'DEC') {
                Write-Host "  Correlations:      $($summary.CorrelationCount)"
                Write-Host "  Alerts:            $($summary.AlertCount)"
            }
        }

        # Per-zone status for each control
        Write-Host ""
        Write-Host "--- Assessment Records (would be written) ---" -ForegroundColor Cyan
        Write-Host ""
        Write-Host ("{0,-10} {1,-12} {2,-6} {3,-8} {4}" -f 'Solution', 'Control', 'Zone', 'Status', 'Notes')
        Write-Host ("{0,-10} {1,-12} {2,-6} {3,-8} {4}" -f '--------', '-------', '----', '------', '-----')

        foreach ($entry in $assessmentLog | Sort-Object Solution, ControlId, Zone) {
            $statusLabel = switch ($entry.Status) {
                1 { 'OK' }
                2 { 'Partial' }
                3 { 'Non-Comp' }
                4 { 'N/A' }
            }
            $truncNotes = if ($entry.Notes.Length -gt 60) {
                $entry.Notes.Substring(0, 57) + '...'
            } else { $entry.Notes }
            Write-Host ("{0,-10} {1,-12} {2,-6} {3,-8} {4}" -f $entry.Solution, $entry.ControlId, $entry.Zone, $statusLabel, $truncNotes)
        }

        # Flag overlapping controls
        if ($overlappingControls) {
            Write-Host ""
            Write-Host "--- Control Overlaps ---" -ForegroundColor Cyan
            foreach ($overlap in $overlappingControls) {
                $sources = $overlap.Value -join ' + '
                Write-Host "  Control $($overlap.Key): $sources -> Worst-case status applied" -ForegroundColor Yellow
            }
        }

        Write-Host ""
        Write-Host "DryRun complete. No records were written to Dataverse." -ForegroundColor Yellow
    }

    # ===================================================================
    # Step 6: Return results
    # ===================================================================
    $stopwatch.Stop()

    $totalAssessments = $assessmentLog.Count
    $successCount = ($assessmentLog | Where-Object { $_.Action -ne 'Error' }).Count
    $errorCount   = ($assessmentLog | Where-Object { $_.Action -eq 'Error' }).Count

    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "  Sync Complete — $totalAssessments assessment records" -ForegroundColor Cyan
    Write-Host "  Duration: $($stopwatch.Elapsed.ToString())" -ForegroundColor Cyan
    if ($errorCount -gt 0) {
        Write-Host "  Errors: $errorCount" -ForegroundColor Red
    }
    Write-Host "========================================================" -ForegroundColor Cyan

    [PSCustomObject]@{
        SyncDate         = $dateStr
        SolutionsProcessed = $Solutions
        TotalAssessments = $totalAssessments
        SuccessCount     = $successCount
        ErrorCount       = $errorCount
        OverlapsResolved = if ($overlappingControls) { @($overlappingControls).Count } else { 0 }
        DryRun           = $DryRun.IsPresent
        Duration         = $stopwatch.Elapsed.ToString()
        AssessmentLog    = $assessmentLog
        SolutionSummaries = $solutionSummaries
    }
}
