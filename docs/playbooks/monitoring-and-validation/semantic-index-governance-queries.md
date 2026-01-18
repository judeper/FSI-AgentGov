# Semantic Index Governance Queries

**Status:** January 2026 - FSI-AgentGov v1.0
**Related Controls:** 4.6 (Grounding Scope), 4.1 (IAG/RCD), 1.7 (Audit Logging)

---

## Purpose

This template provides PowerShell and KQL queries for auditing and monitoring content indexed by Microsoft 365's Semantic Index for AI agent grounding. Use these queries to ensure governance compliance and identify potential oversharing risks.

---

## PowerShell Queries

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
            RestrictedFromCopilot = $_.RestrictContentOrgWideSearchAndCopilot
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
        -not $_.RestrictContentOrgWideSearchAndCopilot
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
        if ($data.ModifiedProperty -like "*RestrictContentOrgWideSearchAndCopilot*" -or
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
            if ($site.RestrictContentOrgWideSearchAndCopilot) {
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
                SiteRestricted = $site.RestrictContentOrgWideSearchAndCopilot
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

### Query 1: Track Copilot Content Access Patterns

```kql
// Track which SharePoint sites Copilot is accessing most frequently
CopilotInteraction
| where TimeGenerated > ago(30d)
| where SourceType == "SharePoint"
| summarize
    AccessCount = count(),
    UniqueUsers = dcount(UserId),
    LastAccess = max(TimeGenerated)
    by SourceSiteUrl
| order by AccessCount desc
| take 50
```

### Query 2: Detect Unauthorized Source Access Attempts

```kql
// Detect Copilot attempts to access restricted content
SharePointAuditLogs
| where TimeGenerated > ago(7d)
| where Operation == "SearchQueryPerformed"
| where AdditionalInfo contains "Copilot"
| join kind=inner (
    // Sites that should be restricted
    SharePointSiteProperties
    | where RestrictedFromCopilot == true
) on SiteUrl
| project TimeGenerated, UserId, SiteUrl, Query
| order by TimeGenerated desc
```

### Query 3: Monitor Index Scope Changes

```kql
// Alert on changes to Copilot restriction settings
SharePointAuditLogs
| where TimeGenerated > ago(24h)
| where Operation == "SiteCollectionSettingsChanged"
| where ModifiedProperty contains "RestrictContentOrgWideSearchAndCopilot"
| extend
    ChangeDirection = case(
        NewValue == "True", "Restricted (removed from Copilot)",
        NewValue == "False", "Unrestricted (added to Copilot)",
        "Unknown"
    )
| project TimeGenerated, UserId, SiteUrl, ChangeDirection, OldValue, NewValue
| order by TimeGenerated desc
```

### Query 4: Copilot Citation Source Analysis

```kql
// Analyze which sources Copilot cites most frequently
CopilotInteraction
| where TimeGenerated > ago(30d)
| extend Citations = parse_json(ResponseMetadata).Citations
| mv-expand Citation = Citations
| summarize
    CitationCount = count(),
    AvgConfidence = avg(todouble(Citation.Confidence)),
    UniqueQueries = dcount(UserQuery)
    by SourceUrl = tostring(Citation.SourceUrl)
| order by CitationCount desc
| take 50
```

### Query 5: Detect Stale Content Being Cited

```kql
// Identify stale content being actively cited by Copilot
CopilotInteraction
| where TimeGenerated > ago(7d)
| extend Citations = parse_json(ResponseMetadata).Citations
| mv-expand Citation = Citations
| summarize CitationCount = count() by SourceUrl = tostring(Citation.SourceUrl)
| join kind=inner (
    SharePointFileProperties
    | where LastModified < ago(180d)
    | project SourceUrl = Url, LastModified, DaysSinceModified = datetime_diff('day', now(), LastModified)
) on SourceUrl
| project SourceUrl, CitationCount, LastModified, DaysSinceModified
| order by CitationCount desc
```

### Query 6: Grounding Scope Compliance Dashboard

```kql
// Dashboard query for grounding scope compliance overview
let IndexedSites = SharePointSiteProperties
| where RestrictedFromCopilot == false
| summarize IndexedCount = count();

let RestrictedSites = SharePointSiteProperties
| where RestrictedFromCopilot == true
| summarize RestrictedCount = count();

let HighRiskIndexed = SharePointSiteProperties
| where RestrictedFromCopilot == false
| where Url contains "draft" or Url contains "archive" or Url contains "test"
| summarize HighRiskCount = count();

let RecentChanges = SharePointAuditLogs
| where TimeGenerated > ago(7d)
| where Operation == "SiteCollectionSettingsChanged"
| where ModifiedProperty contains "RestrictContentOrgWideSearchAndCopilot"
| summarize ChangeCount = count();

union
    (IndexedSites | extend Metric = "Sites Available to Copilot", Value = IndexedCount),
    (RestrictedSites | extend Metric = "Sites Restricted from Copilot", Value = RestrictedCount),
    (HighRiskIndexed | extend Metric = "High-Risk Sites Indexed", Value = HighRiskCount),
    (RecentChanges | extend Metric = "Scope Changes (7 days)", Value = ChangeCount)
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

*FSI Agent Governance Framework v1.0 - January 2026*
