# Semantic Index Governance Queries

**Status:** January 2026 - FSI-AgentGov v1.1
**Related Controls:** 4.6 (Grounding Scope), 4.1 (IAG/RCD), 1.7 (Audit Logging)

---

## Purpose

This template provides PowerShell and KQL queries for auditing and monitoring content indexed by Microsoft 365's Semantic Index for AI agent grounding. Use these queries to ensure governance compliance and identify potential oversharing risks.

---

## PowerShell Queries

!!! note "Parameter Status"
    `RestrictContentOrgWideSearch` is the current GA parameter for site-level search/Copilot
    restrictions. Copilot-specific parameters are in preview and subject to change.

### Query 1: Audit Site Copilot Restrictions

```powershell
# ============================================================
# Audit SharePoint Sites - Copilot Restriction Status
# ============================================================

function Get-CopilotRestrictionAudit {
    param(
        [string]$AdminUrl = "https://tenant-admin.sharepoint.com",
        [string]$OutputPath = ".\Copilot-Restriction-Audit-$(Get-Date -Format 'yyyyMMdd').csv"
    )

    Connect-SPOService -Url $AdminUrl

    Write-Host "Auditing Copilot restriction status for all sites..." -ForegroundColor Cyan

    $sites = Get-SPOSite -Limit All | Where-Object {
        $_.Template -notlike "*SPSPERS*"  # Exclude OneDrive
    }

    $results = $sites | ForEach-Object {
        [PSCustomObject]@{
            Url = $_.Url
            Title = $_.Title
            Template = $_.Template
            Owner = $_.Owner
            RestrictedFromCopilot = $_.RestrictContentOrgWideSearch
            SensitivityLabel = $_.SensitivityLabel
            SharingCapability = $_.SharingCapability
            StorageUsedGB = [math]::Round($_.StorageUsageCurrent / 1024, 2)
            LastContentModified = $_.LastContentModifiedDate
            AuditDate = Get-Date
        }
    }

    $results | Export-Csv -Path $OutputPath -NoTypeInformation
    Write-Host "Exported $($results.Count) sites to: $OutputPath" -ForegroundColor Green

    # Summary
    $restricted = ($results | Where-Object RestrictedFromCopilot).Count
    $unrestricted = ($results | Where-Object { -not $_.RestrictedFromCopilot }).Count

    Write-Host "`nSummary:" -ForegroundColor Yellow
    Write-Host "  Total Sites: $($results.Count)"
    Write-Host "  Restricted from Copilot: $restricted"
    Write-Host "  Available to Copilot: $unrestricted"

    return $results
}

# Run audit
# $audit = Get-CopilotRestrictionAudit
```

### Query 2: Identify High-Risk Indexed Content

```powershell
# ============================================================
# Identify High-Risk Content Available to Copilot
# ============================================================

function Get-HighRiskIndexedContent {
    param(
        [string]$AdminUrl = "https://tenant-admin.sharepoint.com"
    )

    Connect-SPOService -Url $AdminUrl

    Write-Host "Identifying high-risk content available to Copilot..." -ForegroundColor Cyan

    $sites = Get-SPOSite -Limit All | Where-Object {
        $_.Template -notlike "*SPSPERS*" -and
        -not $_.RestrictContentOrgWideSearch
    }

    $highRisk = @()

    foreach ($site in $sites) {
        $riskFactors = @()

        # Check for risky patterns in URL
        if ($site.Url -match "draft|archive|test|sandbox|personal|confidential|restricted") {
            $riskFactors += "URL pattern suggests non-production content"
        }

        # Check for broad sharing
        if ($site.SharingCapability -eq "ExternalUserAndGuestSharing") {
            $riskFactors += "External sharing enabled"
        }

        # Check for large storage (potential data accumulation)
        $storageGB = $site.StorageUsageCurrent / 1024
        if ($storageGB -gt 50) {
            $riskFactors += "Large storage ($([math]::Round($storageGB, 1)) GB)"
        }

        # Check for stale content
        if ($site.LastContentModifiedDate -lt (Get-Date).AddDays(-180)) {
            $riskFactors += "Content not modified in 180+ days"
        }

        # Check for missing sensitivity label
        if ([string]::IsNullOrEmpty($site.SensitivityLabel)) {
            $riskFactors += "No sensitivity label applied"
        }

        if ($riskFactors.Count -gt 0) {
            $highRisk += [PSCustomObject]@{
                Url = $site.Url
                Title = $site.Title
                RiskFactors = ($riskFactors -join "; ")
                RiskScore = $riskFactors.Count
                SensitivityLabel = $site.SensitivityLabel
                LastModified = $site.LastContentModifiedDate
            }
        }
    }

    $highRisk = $highRisk | Sort-Object RiskScore -Descending

    Write-Host "`nHigh-Risk Sites Available to Copilot:" -ForegroundColor Red
    $highRisk | Select-Object -First 20 | Format-Table Url, RiskScore, RiskFactors -Wrap

    return $highRisk
}

# Run analysis
# $risks = Get-HighRiskIndexedContent
```

### Query 3: Monitor Copilot Restriction Changes

```powershell
# ============================================================
# Monitor Changes to Copilot Restriction Settings
# ============================================================

function Get-CopilotRestrictionChanges {
    param(
        [int]$DaysBack = 30,
        [string]$OutputPath = ".\Copilot-Restriction-Changes-$(Get-Date -Format 'yyyyMMdd').csv"
    )

    Write-Host "Searching for Copilot restriction changes in last $DaysBack days..." -ForegroundColor Cyan

    # Connect to Security & Compliance
    Connect-IPPSSession

    $startDate = (Get-Date).AddDays(-$DaysBack)
    $endDate = Get-Date

    # Search for site setting changes
    $changes = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
        -Operations "SiteCollectionSettingsChanged" -ResultSize 1000

    $restrictionChanges = @()

    foreach ($change in $changes) {
        $data = $change.AuditData | ConvertFrom-Json

        # Filter for Copilot-related changes
        if ($data.ModifiedProperty -like "*RestrictContentOrgWideSearch*" -or
            $data.ModifiedProperty -like "*Copilot*") {

            $restrictionChanges += [PSCustomObject]@{
                Timestamp = $change.CreationDate
                User = $change.UserIds
                SiteUrl = $data.SiteUrl
                Operation = $change.Operations
                ModifiedProperty = $data.ModifiedProperty
                OldValue = $data.OldValue
                NewValue = $data.NewValue
            }
        }
    }

    if ($restrictionChanges.Count -gt 0) {
        $restrictionChanges | Export-Csv -Path $OutputPath -NoTypeInformation
        Write-Host "Found $($restrictionChanges.Count) Copilot restriction changes" -ForegroundColor Yellow
        Write-Host "Exported to: $OutputPath"

        # Alert on unrestricted changes (sites made available to Copilot)
        $unrestricted = $restrictionChanges | Where-Object {
            $_.NewValue -eq "False" -or $_.NewValue -eq $false
        }
        if ($unrestricted.Count -gt 0) {
            Write-Host "`nALERT: $($unrestricted.Count) sites were UNRESTRICTED (made available to Copilot):" -ForegroundColor Red
            $unrestricted | Format-Table Timestamp, User, SiteUrl
        }
    }
    else {
        Write-Host "No Copilot restriction changes found" -ForegroundColor Green
    }

    return $restrictionChanges
}

# Run monitoring
# $changes = Get-CopilotRestrictionChanges -DaysBack 30
```

### Query 4: Validate Agent Knowledge Source Alignment

```powershell
# ============================================================
# Validate Agent Knowledge Sources Against Grounding Scope Policy
# ============================================================

function Test-AgentGroundingScopeCompliance {
    param(
        [string]$AgentInventoryPath,  # CSV with AgentId, KnowledgeSourceUrl columns
        [string]$AdminUrl = "https://tenant-admin.sharepoint.com"
    )

    Connect-SPOService -Url $AdminUrl

    Write-Host "Validating agent knowledge sources against grounding scope policy..." -ForegroundColor Cyan

    # Load agent inventory
    $agents = Import-Csv -Path $AgentInventoryPath

    $validationResults = @()

    foreach ($agent in $agents) {
        $sourceUrl = $agent.KnowledgeSourceUrl

        try {
            $site = Get-SPOSite -Identity $sourceUrl -ErrorAction Stop

            $compliant = $true
            $issues = @()

            # Check if site is restricted (should NOT be if agent needs access)
            if ($site.RestrictContentOrgWideSearch) {
                $compliant = $false
                $issues += "Site is restricted from Copilot but agent uses it"
            }

            # Check sensitivity label alignment
            if ($agent.Zone -eq "3" -and [string]::IsNullOrEmpty($site.SensitivityLabel)) {
                $compliant = $false
                $issues += "Zone 3 agent source lacks sensitivity label"
            }

            $validationResults += [PSCustomObject]@{
                AgentId = $agent.AgentId
                AgentName = $agent.AgentName
                Zone = $agent.Zone
                KnowledgeSourceUrl = $sourceUrl
                Compliant = $compliant
                Issues = ($issues -join "; ")
                SiteRestricted = $site.RestrictContentOrgWideSearch
                SensitivityLabel = $site.SensitivityLabel
            }
        }
        catch {
            $validationResults += [PSCustomObject]@{
                AgentId = $agent.AgentId
                AgentName = $agent.AgentName
                Zone = $agent.Zone
                KnowledgeSourceUrl = $sourceUrl
                Compliant = $false
                Issues = "Site not found or access denied"
                SiteRestricted = "Unknown"
                SensitivityLabel = "Unknown"
            }
        }
    }

    # Summary
    $compliantCount = ($validationResults | Where-Object Compliant).Count
    $nonCompliantCount = ($validationResults | Where-Object { -not $_.Compliant }).Count

    Write-Host "`nValidation Summary:" -ForegroundColor Yellow
    Write-Host "  Total Agents: $($validationResults.Count)"
    Write-Host "  Compliant: $compliantCount" -ForegroundColor Green
    Write-Host "  Non-Compliant: $nonCompliantCount" -ForegroundColor Red

    if ($nonCompliantCount -gt 0) {
        Write-Host "`nNon-Compliant Agents:" -ForegroundColor Red
        $validationResults | Where-Object { -not $_.Compliant } |
            Format-Table AgentId, KnowledgeSourceUrl, Issues -Wrap
    }

    return $validationResults
}

# Run validation
# $validation = Test-AgentGroundingScopeCompliance -AgentInventoryPath ".\agent-inventory.csv"
```

---

## KQL Queries (for Microsoft Sentinel / Log Analytics)

!!! warning "Data Source Limitations"
    KQL queries in Log Analytics use the **OfficeActivity** table for Microsoft 365 audit data.
    Tables like `CopilotInteraction`, `SharePointAuditLogs`, `SharePointSiteProperties`, and
    `SharePointFileProperties` do not exist in Log Analytics. For site/file property data,
    use PowerShell (`Get-SPOSite`) or Microsoft Graph API, then optionally ingest results
    into a custom Log Analytics table for correlation.

### Query 1: Track Copilot Content Access Patterns

```kql
// Track Copilot interactions with SharePoint sources
// Uses OfficeActivity table with CopilotInteraction RecordType
OfficeActivity
| where TimeGenerated > ago(30d)
| where RecordType == "CopilotInteraction"
| extend SourceSiteUrl = tostring(parse_json(tostring(AdditionalInfo)).SourceSiteUrl)
| where isnotempty(SourceSiteUrl)
| summarize
    AccessCount = count(),
    UniqueUsers = dcount(UserId),
    LastAccess = max(TimeGenerated)
    by SourceSiteUrl
| order by AccessCount desc
| take 50
```

### Query 2: Detect Copilot Access to Sensitive Sites

```kql
// Detect Copilot interactions with sites containing sensitive keywords
// Note: Site restriction status requires PowerShell lookup (Get-SPOSite)
OfficeActivity
| where TimeGenerated > ago(7d)
| where RecordType == "CopilotInteraction" or Operation has "Copilot"
| extend SiteUrl = tostring(parse_json(tostring(AdditionalInfo)).SiteUrl)
| where SiteUrl has_any ("confidential", "restricted", "pii", "financial")
| project TimeGenerated, UserId, SiteUrl, Operation
| order by TimeGenerated desc
```

### Query 3: Monitor Site Setting Changes (Copilot Restrictions)

```kql
// Alert on changes to site collection settings affecting Copilot access
OfficeActivity
| where TimeGenerated > ago(24h)
| where Operation == "SiteCollectionSettingsChanged"
| extend AuditData = parse_json(tostring(AdditionalInfo))
| extend ModifiedProperty = tostring(AuditData.ModifiedProperty)
| where ModifiedProperty has_any ("RestrictContentOrgWideSearch", "Copilot", "Search")
| extend
    OldValue = tostring(AuditData.OldValue),
    NewValue = tostring(AuditData.NewValue),
    ChangeDirection = case(
        tostring(AuditData.NewValue) == "True", "Restricted (removed from search/Copilot)",
        tostring(AuditData.NewValue) == "False", "Unrestricted (added to search/Copilot)",
        "Unknown"
    )
| project TimeGenerated, UserId, Site_Url, ChangeDirection, ModifiedProperty, OldValue, NewValue
| order by TimeGenerated desc
```

### Query 4: Copilot Usage by Application

```kql
// Analyze Copilot usage patterns by application
OfficeActivity
| where TimeGenerated > ago(30d)
| where RecordType == "CopilotInteraction" or RecordType == "CopilotForM365Interaction"
| extend AppName = tostring(parse_json(tostring(AdditionalInfo)).AppName)
| summarize
    InteractionCount = count(),
    UniqueUsers = dcount(UserId),
    FirstSeen = min(TimeGenerated),
    LastSeen = max(TimeGenerated)
    by AppName
| order by InteractionCount desc
```

### Query 5: Detect Unusual Copilot Activity Patterns

```kql
// Identify users with unusually high Copilot activity
let baseline = OfficeActivity
| where TimeGenerated > ago(30d) and TimeGenerated < ago(1d)
| where RecordType has "Copilot"
| summarize AvgDaily = count() / 30.0 by UserId;
OfficeActivity
| where TimeGenerated > ago(1d)
| where RecordType has "Copilot"
| summarize TodayCount = count() by UserId
| join kind=inner baseline on UserId
| where TodayCount > AvgDaily * 3
| project UserId, TodayCount, BaselineAvg = round(AvgDaily, 1), Deviation = round(TodayCount / AvgDaily, 1)
| order by Deviation desc
```

### Query 6: Copilot Activity Summary Dashboard

```kql
// Dashboard query for Copilot activity overview
// Note: Site restriction counts require PowerShell (Get-SPOSite) - this shows activity metrics only
let TotalInteractions = OfficeActivity
| where TimeGenerated > ago(7d)
| where RecordType has "Copilot"
| summarize InteractionCount = count();

let UniqueUsers = OfficeActivity
| where TimeGenerated > ago(7d)
| where RecordType has "Copilot"
| summarize UserCount = dcount(UserId);

let SettingChanges = OfficeActivity
| where TimeGenerated > ago(7d)
| where Operation == "SiteCollectionSettingsChanged"
| summarize ChangeCount = count();

let SensitiveSiteAccess = OfficeActivity
| where TimeGenerated > ago(7d)
| where RecordType has "Copilot"
| extend SiteUrl = tostring(parse_json(tostring(AdditionalInfo)).SiteUrl)
| where SiteUrl has_any ("confidential", "restricted", "pii")
| summarize SensitiveCount = count();

union
    (TotalInteractions | extend Metric = "Copilot Interactions (7 days)", Value = InteractionCount),
    (UniqueUsers | extend Metric = "Unique Users", Value = UserCount),
    (SettingChanges | extend Metric = "Site Setting Changes", Value = ChangeCount),
    (SensitiveSiteAccess | extend Metric = "Sensitive Site Interactions", Value = SensitiveCount)
| project Metric, Value
```

---

## Scheduled Monitoring

### Weekly Audit Script

```powershell
# ============================================================
# Weekly Semantic Index Governance Audit
# Schedule via Task Scheduler or Azure Automation
# ============================================================

param(
    [string]$OutputPath = "\\governance\reports\semantic-index",
    [string[]]$AlertRecipients = @("ai-governance@company.com")
)

$timestamp = Get-Date -Format "yyyyMMdd"
$reportPath = "$OutputPath\Weekly-Audit-$timestamp"

New-Item -ItemType Directory -Path $reportPath -Force | Out-Null

Write-Host "Running Weekly Semantic Index Governance Audit..." -ForegroundColor Cyan

# Run all audits
$siteAudit = Get-CopilotRestrictionAudit -OutputPath "$reportPath\Site-Audit.csv"
$highRisk = Get-HighRiskIndexedContent
$changes = Get-CopilotRestrictionChanges -DaysBack 7

# Generate summary
$summary = @{
    AuditDate = Get-Date
    TotalSites = $siteAudit.Count
    RestrictedSites = ($siteAudit | Where-Object RestrictedFromCopilot).Count
    UnrestrictedSites = ($siteAudit | Where-Object { -not $_.RestrictedFromCopilot }).Count
    HighRiskSites = $highRisk.Count
    RecentChanges = $changes.Count
    UnrestrictedChanges = ($changes | Where-Object { $_.NewValue -eq "False" }).Count
}

# Alert if issues found
$alertConditions = @()
if ($highRisk.Count -gt 10) {
    $alertConditions += "High number of high-risk sites indexed: $($highRisk.Count)"
}
if ($summary.UnrestrictedChanges -gt 0) {
    $alertConditions += "Sites unrestricted this week: $($summary.UnrestrictedChanges)"
}

if ($alertConditions.Count -gt 0) {
    Write-Host "ALERT CONDITIONS MET:" -ForegroundColor Red
    $alertConditions | ForEach-Object { Write-Host "  - $_" }

    # Send alert email (implement your notification method)
    # Send-MailMessage -To $AlertRecipients -Subject "Semantic Index Governance Alert" -Body ($alertConditions -join "`n")
}

Write-Host "`nAudit complete. Reports saved to: $reportPath" -ForegroundColor Green
```

---

## Integration with Controls

| Query/Script | Related Control | Purpose |
|--------------|-----------------|---------|
| Get-CopilotRestrictionAudit | [4.6 Grounding Scope](../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Site inventory |
| Get-HighRiskIndexedContent | [4.6 Grounding Scope](../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Risk identification |
| Get-CopilotRestrictionChanges | [1.7 Audit Logging](../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Change monitoring |
| Citation Analysis (KQL) | [2.16 RAG Source Integrity](../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | Source tracking |

---

*FSI Agent Governance Framework v1.1 - January 2026*
