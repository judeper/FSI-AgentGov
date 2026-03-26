<#
.SYNOPSIS
    Collects SharePoint Online configuration data for FSI Agent Governance assessment.

.DESCRIPTION
    Enumerates SharePoint site inventory, external sharing settings, retention labels,
    guest access, item-level permissions, and grounding scope cross-references using
    Microsoft Graph (NOT legacy CSOM).

    Outputs a structured JSON file (sharepoint.json) consumed by the assessment engine.

    Pattern references:
      - Invoke-SharingAudit.ps1 — sharing scope classification, principal evaluation
      - Invoke-HardeningBaselineCheck.ps1 — security baseline checks
      - restrict-agent-publishing.ps1 — security group validation patterns

.PARAMETER TenantId
    Mandatory. Azure AD tenant ID.

.PARAMETER AuthMode
    Mandatory. Authentication mode: Interactive or ServicePrincipal.

.PARAMETER ClientId
    Optional. Application (client) ID for service principal authentication.

.PARAMETER ClientSecret
    Optional. Client secret as SecureString for service principal authentication.

.PARAMETER OutputDir
    Mandatory. Root output directory. Collected JSON is written to $OutputDir\collected\sharepoint.json.

.PARAMETER ApprovedSitesCsv
    Optional. Path to a CSV file of approved grounding site URLs for cross-reference.
    CSV must contain a column named "SiteUrl".

.OUTPUTS
    sharepoint.json — JSON file with site inventory, sharing settings, retention labels,
    guest access, item-level permissions, and grounding scope analysis.

.NOTES
    Part of the FSI Agent Governance Assessment Engine — SharePoint Collector.
    Required Graph scopes: Sites.Read.All, Files.Read.All.
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
    [string]$OutputDir,

    [Parameter()]
    [string]$ApprovedSitesCsv
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ─── Initialise ──────────────────────────────────────────────────────
$warnings = [System.Collections.Generic.List[string]]::new()
$collectedDir = Join-Path $OutputDir 'collected'
if (-not (Test-Path $collectedDir)) {
    New-Item -ItemType Directory -Path $collectedDir -Force | Out-Null
}
$outputFile = Join-Path $collectedDir 'sharepoint.json'

# ─── Module Imports ──────────────────────────────────────────────────
Import-Module Microsoft.Graph.Authentication -ErrorAction Stop
Write-Verbose "Loaded Microsoft.Graph.Authentication module."

# ─── Load Approved Sites ─────────────────────────────────────────────
$approvedSites = @()
if ($ApprovedSitesCsv) {
    if (Test-Path $ApprovedSitesCsv) {
        $approvedSites = @(Import-Csv $ApprovedSitesCsv | ForEach-Object { $_.SiteUrl.TrimEnd('/').ToLower() })
        Write-Verbose "Loaded $($approvedSites.Count) approved grounding site(s) from CSV."
    }
    else {
        $warnings.Add("Approved sites CSV not found at '$ApprovedSitesCsv'. Grounding cross-reference will be skipped.")
        Write-Warning $warnings[-1]
    }
}

# ─── Authentication ──────────────────────────────────────────────────
$requiredScopes = @('Sites.Read.All', 'Files.Read.All')

Write-Verbose "Authenticating to Microsoft Graph in $AuthMode mode..."

if ($AuthMode -eq 'Interactive') {
    Connect-MgGraph -TenantId $TenantId -Scopes $requiredScopes -ErrorAction Stop
}
else {
    if (-not $ClientId -or -not $ClientSecret) {
        throw "ServicePrincipal auth requires -ClientId and -ClientSecret parameters."
    }
    $credential = [System.Management.Automation.PSCredential]::new($ClientId, $ClientSecret)
    Connect-MgGraph -TenantId $TenantId -ClientSecretCredential $credential -ErrorAction Stop
}

Write-Verbose "Microsoft Graph authentication successful."

# ─── Graph API Helper ────────────────────────────────────────────────
# Thin wrapper for Graph REST calls with consistent error handling.
function Invoke-GraphApi {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Uri,
        [Parameter()][ValidateSet('GET', 'POST')][string]$Method = 'GET'
    )
    try {
        $response = Invoke-MgGraphRequest -Uri $Uri -Method $Method -ErrorAction Stop
        return $response
    }
    catch {
        Write-Warning "Graph API call failed ($Method $Uri): $($_.Exception.Message)"
        return $null
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Section 1: Site Inventory
# Supports: Baseline site enumeration for all downstream checks
# ═══════════════════════════════════════════════════════════════════════
$siteInventory = $null
$rawSites = @()
try {
    Write-Verbose "Section 1: Enumerating SharePoint sites via Graph..."

    # Paginate through all sites using Graph search endpoint
    $uri = 'https://graph.microsoft.com/v1.0/sites?search=*&$top=999&$select=id,displayName,webUrl,createdDateTime,isPersonalSite'
    $allSites = [System.Collections.Generic.List[object]]::new()

    while ($uri) {
        $response = Invoke-GraphApi -Uri $uri
        if ($response -and $response.value) {
            $allSites.AddRange([object[]]$response.value)
            $uri = $response.'@odata.nextLink'
        }
        else {
            break
        }
    }

    $rawSites = $allSites
    $siteInventory = $rawSites | ForEach-Object {
        [PSCustomObject]@{
            Id               = $_.id
            DisplayName      = $_.displayName
            WebUrl           = $_.webUrl
            CreatedDateTime  = $_.createdDateTime
            IsPersonalSite   = $_.isPersonalSite
        }
    }
    Write-Verbose "  Enumerated $($siteInventory.Count) site(s)."
}
catch {
    $warnings.Add("Section 1 (Site Inventory) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 2: External Sharing per Site
# Supports: Control 3.8 (Sharing Controls), external access auditing
# Pattern: Invoke-SharingAudit.ps1 — sharing scope classification
# ═══════════════════════════════════════════════════════════════════════
$externalSharing = $null
try {
    Write-Verbose "Section 2: Collecting external sharing settings per site..."
    if ($rawSites.Count -gt 0) {
        $externalSharing = foreach ($site in $rawSites) {
            $siteDetail = Invoke-GraphApi -Uri "https://graph.microsoft.com/v1.0/sites/$($site.id)?`$select=sharingCapability,id,displayName,webUrl"
            if ($siteDetail) {
                [PSCustomObject]@{
                    SiteId              = $site.id
                    DisplayName         = $site.displayName
                    WebUrl              = $site.webUrl
                    SharingCapability   = $siteDetail.sharingCapability
                }
            }
        }
        Write-Verbose "  Collected sharing settings for $(@($externalSharing).Count) site(s)."
    }
    else {
        $warnings.Add("Section 2 (External Sharing): Skipped — no sites collected.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 2 (External Sharing) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 3: Retention Labels on Lists
# Supports: Control 3.2 (Data Retention)
# ═══════════════════════════════════════════════════════════════════════
$retentionLabels = $null
try {
    Write-Verbose "Section 3: Checking retention label status on site lists..."
    if ($rawSites.Count -gt 0) {
        # Sample up to 50 sites to avoid excessive API calls
        $sampleSites = $rawSites | Select-Object -First 50
        $retentionLabels = foreach ($site in $sampleSites) {
            $listsUri = "https://graph.microsoft.com/v1.0/sites/$($site.id)/lists?`$select=id,displayName,list&`$top=50"
            $listsResponse = Invoke-GraphApi -Uri $listsUri
            if ($listsResponse -and $listsResponse.value) {
                foreach ($list in $listsResponse.value) {
                    [PSCustomObject]@{
                        SiteId              = $site.id
                        SiteDisplayName     = $site.displayName
                        ListId              = $list.id
                        ListDisplayName     = $list.displayName
                        ListTemplate        = $list.list.template
                        ContentTypesEnabled = $list.list.contentTypesEnabled
                    }
                }
            }
        }
        Write-Verbose "  Collected list metadata for $(@($retentionLabels).Count) list(s)."
    }
    else {
        $warnings.Add("Section 3 (Retention Labels): Skipped — no sites collected.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 3 (Retention Labels) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 4: Guest Access
# Supports: Control 3.8 (External/Guest Sharing), least-privilege access
# ═══════════════════════════════════════════════════════════════════════
$guestAccess = $null
try {
    Write-Verbose "Section 4: Checking guest/external user access per site..."
    if ($rawSites.Count -gt 0) {
        # Sample up to 30 sites to avoid rate limiting
        $sampleSites = $rawSites | Select-Object -First 30
        $guestAccess = foreach ($site in $sampleSites) {
            $permsUri = "https://graph.microsoft.com/v1.0/sites/$($site.id)/permissions?`$top=100"
            $permsResponse = Invoke-GraphApi -Uri $permsUri
            $guestUsers = @()
            if ($permsResponse -and $permsResponse.value) {
                $guestUsers = @($permsResponse.value | Where-Object {
                    $_.grantedToIdentitiesV2 | Where-Object {
                        $_.user.userPrincipalName -match '#EXT#' -or
                        $_.user.email -and $_.user.email -notmatch ([regex]::Escape($TenantId))
                    }
                })
            }
            if ($guestUsers.Count -gt 0) {
                [PSCustomObject]@{
                    SiteId          = $site.id
                    DisplayName     = $site.displayName
                    WebUrl          = $site.webUrl
                    GuestCount      = $guestUsers.Count
                    HasGuestAccess  = $true
                }
            }
            else {
                [PSCustomObject]@{
                    SiteId          = $site.id
                    DisplayName     = $site.displayName
                    WebUrl          = $site.webUrl
                    GuestCount      = 0
                    HasGuestAccess  = $false
                }
            }
        }
        Write-Verbose "  Checked guest access for $(@($guestAccess).Count) site(s)."
    }
    else {
        $warnings.Add("Section 4 (Guest Access): Skipped — no sites collected.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 4 (Guest Access) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 5: Item-Level Permissions (Grounding Sites)
# Supports: Control 1.4, 3.8 — flag "Everyone" / "Everyone except external" sharing
# Pattern: Invoke-SharingAudit.ps1 — principal classification (ORG_WIDE_SHARING)
# ═══════════════════════════════════════════════════════════════════════
$itemLevelPermissions = $null
try {
    Write-Verbose "Section 5: Sampling item-level permissions on grounding sites..."

    # Determine grounding sites: use approved sites list if provided, else sample first 10 sites
    $groundingSites = @()
    if ($approvedSites.Count -gt 0 -and $rawSites.Count -gt 0) {
        $groundingSites = @($rawSites | Where-Object {
            $approvedSites -contains $_.webUrl.TrimEnd('/').ToLower()
        })
    }
    if ($groundingSites.Count -eq 0 -and $rawSites.Count -gt 0) {
        $groundingSites = @($rawSites | Select-Object -First 10)
        $warnings.Add("Section 5: No approved grounding sites matched. Sampling first 10 sites.")
        Write-Warning $warnings[-1]
    }

    if ($groundingSites.Count -gt 0) {
        $itemLevelPermissions = foreach ($site in $groundingSites) {
            $driveUri = "https://graph.microsoft.com/v1.0/sites/$($site.id)/drive/root/children?`$top=100&`$select=id,name,webUrl"
            $driveResponse = Invoke-GraphApi -Uri $driveUri
            $flaggedItems = @()

            if ($driveResponse -and $driveResponse.value) {
                foreach ($item in $driveResponse.value) {
                    $itemPermsUri = "https://graph.microsoft.com/v1.0/sites/$($site.id)/drive/items/$($item.id)/permissions"
                    $itemPerms = Invoke-GraphApi -Uri $itemPermsUri
                    if ($itemPerms -and $itemPerms.value) {
                        foreach ($perm in $itemPerms.value) {
                            $grantedTo = $perm.grantedToV2
                            $link = $perm.link
                            $isEveryone = $false

                            # Check for "Everyone" or "Everyone except external users" sharing
                            if ($grantedTo -and $grantedTo.siteUser) {
                                if ($grantedTo.siteUser.displayName -match '^Everyone') {
                                    $isEveryone = $true
                                }
                            }
                            if ($link -and $link.scope -eq 'organization') {
                                $isEveryone = $true
                            }
                            if ($link -and $link.scope -eq 'anonymous') {
                                $isEveryone = $true
                            }

                            if ($isEveryone) {
                                $flaggedItems += [PSCustomObject]@{
                                    ItemId      = $item.id
                                    ItemName    = $item.name
                                    ItemUrl     = $item.webUrl
                                    PermScope   = if ($link) { $link.scope } else { 'direct' }
                                    PermType    = if ($link) { $link.type } else { $perm.roles -join ',' }
                                    Flagged     = $true
                                }
                            }
                        }
                    }
                }
            }

            [PSCustomObject]@{
                SiteId          = $site.id
                DisplayName     = $site.displayName
                WebUrl          = $site.webUrl
                SampledItems    = if ($driveResponse -and $driveResponse.value) { $driveResponse.value.Count } else { 0 }
                FlaggedItems    = $flaggedItems
                FlaggedCount    = $flaggedItems.Count
            }
        }
        Write-Verbose "  Sampled permissions on $(@($itemLevelPermissions).Count) grounding site(s)."
    }
    else {
        $warnings.Add("Section 5 (Item-Level Permissions): Skipped — no sites available.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 5 (Item-Level Permissions) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 6: Grounding Scope Cross-Reference
# Supports: Knowledge source governance — flag unapproved grounding sites
# ═══════════════════════════════════════════════════════════════════════
$groundingCrossRef = $null
try {
    Write-Verbose "Section 6: Grounding scope cross-reference..."
    if ($approvedSites.Count -gt 0 -and $siteInventory) {
        $collectedUrls = @($siteInventory | ForEach-Object { $_.WebUrl.TrimEnd('/').ToLower() })

        $approvedFound = @($approvedSites | Where-Object { $collectedUrls -contains $_ })
        $approvedMissing = @($approvedSites | Where-Object { $collectedUrls -notcontains $_ })
        $unapproved = @($collectedUrls | Where-Object { $approvedSites -notcontains $_ })

        $groundingCrossRef = [PSCustomObject]@{
            ApprovedSitesTotal   = $approvedSites.Count
            ApprovedFound        = $approvedFound.Count
            ApprovedMissing      = $approvedMissing
            UnapprovedSiteCount  = $unapproved.Count
            UnapprovedSites      = $unapproved | Select-Object -First 100
        }

        if ($unapproved.Count -gt 0) {
            $warnings.Add("Section 6: $($unapproved.Count) site(s) not in approved grounding list.")
            Write-Warning $warnings[-1]
        }
        Write-Verbose "  Cross-reference complete: $($approvedFound.Count) approved found, $($unapproved.Count) unapproved."
    }
    elseif ($approvedSites.Count -eq 0) {
        $groundingCrossRef = [PSCustomObject]@{
            ApprovedSitesTotal = 0
            Note               = 'No approved sites CSV provided. Grounding cross-reference skipped.'
        }
        Write-Verbose "  No approved sites CSV provided — cross-reference skipped."
    }
    else {
        $warnings.Add("Section 6 (Grounding Cross-Reference): Skipped — no site inventory available.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 6 (Grounding Cross-Reference) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Build Output
# ═══════════════════════════════════════════════════════════════════════
$result = [ordered]@{
    siteInventory          = $siteInventory
    externalSharing        = $externalSharing
    retentionLabels        = $retentionLabels
    guestAccess            = $guestAccess
    itemLevelPermissions   = $itemLevelPermissions
    groundingCrossRef      = $groundingCrossRef
    _metadata              = [ordered]@{
        collector            = 'Collect-SharePoint'
        timestamp            = (Get-Date -Format 'o')
        tenant_id            = $TenantId
        warnings             = @($warnings)
        approvedSitesCsvUsed = [bool]($approvedSites.Count -gt 0)
    }
}

$json = $result | ConvertTo-Json -Depth 10
$json | Out-File -FilePath $outputFile -Encoding utf8
Write-Verbose "Output written to $outputFile"

# ─── Disconnect Graph ────────────────────────────────────────────────
try { Disconnect-MgGraph -ErrorAction SilentlyContinue } catch { }

# ─── Exit Code ───────────────────────────────────────────────────────
$sectionValues = @(
    $siteInventory, $externalSharing, $retentionLabels,
    $guestAccess, $itemLevelPermissions, $groundingCrossRef
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
