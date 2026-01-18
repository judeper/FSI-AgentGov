# Verification & Testing: Control 4.1 - SharePoint Information Access Governance (IAG)

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify RCD Settings in Admin Portal

1. Navigate to **SharePoint Admin Center** > **Sites** > **Active sites**
2. Select a regulated/enterprise-managed site
3. Open **Settings** panel
4. Confirm "Restrict content from Microsoft 365 Copilot" is visible
5. Verify setting is **On** for regulated sites
6. **EXPECTED:** Settings panel shows restriction toggle, set to On

### Test 2: Verify Copilot Cannot Access Restricted Content

1. Sign in as a user with access to the restricted site
2. Open Microsoft 365 Copilot (in Teams or Microsoft365.com)
3. Ask Copilot a question that would require content from the restricted site
4. **EXPECTED:** Copilot does NOT return content from the restricted site

### Test 3: Verify Copilot CAN Access Non-Restricted Content

1. Sign in as a user with access to an unrestricted site
2. Open Microsoft 365 Copilot
3. Ask Copilot a question about content from the unrestricted site
4. **EXPECTED:** Copilot returns relevant content (if user has permission)

### Test 4: Verify Restricted Access Control (RAC)

1. Sign in as a user NOT in the authorized security group
2. Attempt to access a RAC-protected site
3. **EXPECTED:** Access denied regardless of previous sharing permissions

### Test 5: Verify Audit Logging

1. Navigate to **Microsoft Purview** > **Audit**
2. Search for "SiteRestrictedFromOrgSearch" operations
3. Filter by date range covering your configuration changes
4. **EXPECTED:** All IAG setting changes are logged with user, timestamp, and site details

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-4.1-01 | RCD enabled for regulated site | Setting shows "On" in portal | |
| TC-4.1-02 | Copilot query against restricted site | Content not returned | |
| TC-4.1-03 | Copilot query against unrestricted site | Content returned (per user permissions) | |
| TC-4.1-04 | User outside RAC group accesses protected site | Access denied | |
| TC-4.1-05 | User in RAC group accesses protected site | Access granted | |
| TC-4.1-06 | RSS allow-list configured | Only listed sites accessible to Copilot | |
| TC-4.1-07 | Audit log captures RCD changes | Events logged with full details | |

---

## Evidence to Retain

Collect and store the following artifacts for audit readiness:

### Configuration Evidence

- [ ] Screenshot of SharePoint Admin Center showing RCD setting for each regulated site
- [ ] Export of all sites with their RCD status (PowerShell report)
- [ ] Screenshot of RSS configuration (if using allow-list approach)
- [ ] Screenshot of RAC configuration for information barrier sites

### Testing Evidence

- [ ] Screenshot of Copilot response showing no restricted content returned
- [ ] Screenshot of successful Copilot response for unrestricted content
- [ ] Screenshot of access denied for non-RAC group user

### Audit Evidence

- [ ] Microsoft Purview Audit search export for "SiteRestrictedFromOrgSearch" events
- [ ] Change documentation with business justification for each restriction

---

## Automated Validation Script

```powershell
# Run validation checks for Control 4.1
Write-Host "=== Control 4.1 Validation ===" -ForegroundColor Cyan

# Connect to SharePoint
$AdminUrl = "https://yourtenant-admin.sharepoint.com"
Connect-SPOService -Url $AdminUrl

# Define expected restricted sites (from your governance inventory)
$ExpectedRestrictedSites = @(
    "https://yourtenant.sharepoint.com/sites/TradingData",
    "https://yourtenant.sharepoint.com/sites/CustomerPII",
    "https://yourtenant.sharepoint.com/sites/RegulatoryFilings"
)

$PassCount = 0
$FailCount = 0

# Check 1: Verify expected sites are restricted
Write-Host "`n[Check 1] Verifying expected sites are restricted..." -ForegroundColor Yellow
foreach ($SiteUrl in $ExpectedRestrictedSites) {
    $Site = Get-SPOSite -Identity $SiteUrl
    if ($Site.RestrictContentOrgWideSearch -eq $true) {
        Write-Host "[PASS] $SiteUrl - Restricted" -ForegroundColor Green
        $PassCount++
    }
    else {
        Write-Host "[FAIL] $SiteUrl - NOT Restricted" -ForegroundColor Red
        $FailCount++
    }
}

# Check 2: Verify SharePoint Advanced Management features available
Write-Host "`n[Check 2] Verifying SharePoint Advanced Management..." -ForegroundColor Yellow
$TenantSettings = Get-SPOTenant
if ($TenantSettings) {
    Write-Host "[PASS] SharePoint tenant settings accessible" -ForegroundColor Green
    $PassCount++
}
else {
    Write-Host "[FAIL] Cannot access SharePoint tenant settings" -ForegroundColor Red
    $FailCount++
}

# Check 3: Verify no sensitive sites are unrestricted
Write-Host "`n[Check 3] Scanning for potentially sensitive unrestricted sites..." -ForegroundColor Yellow
$SensitivePatterns = @("*confidential*", "*pii*", "*customer*", "*trading*", "*regulatory*")
$AllSites = Get-SPOSite -Limit All

$PotentialIssues = @()
foreach ($Site in $AllSites) {
    foreach ($Pattern in $SensitivePatterns) {
        if ($Site.Url -like $Pattern -and $Site.RestrictContentOrgWideSearch -ne $true) {
            $PotentialIssues += $Site.Url
        }
    }
}

if ($PotentialIssues.Count -eq 0) {
    Write-Host "[PASS] No sensitive sites found without restrictions" -ForegroundColor Green
    $PassCount++
}
else {
    Write-Host "[WARN] Found $($PotentialIssues.Count) potentially sensitive sites without restrictions:" -ForegroundColor Yellow
    $PotentialIssues | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
}

# Summary
Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
Write-Host "Passed: $PassCount" -ForegroundColor Green
Write-Host "Failed: $FailCount" -ForegroundColor $(if ($FailCount -gt 0) { "Red" } else { "Green" })

if ($FailCount -gt 0) {
    Write-Host "`nAction Required: Review and remediate failed checks" -ForegroundColor Red
}
else {
    Write-Host "`nControl 4.1 validation passed!" -ForegroundColor Green
}
```

---

## Verification Evidence Template

| Evidence Type | Location | Retention |
|---------------|----------|-----------|
| Configuration screenshot | Site Settings panel | 1 year |
| Restricted sites list | Governance documentation | 6 years |
| Setting change audit | Unified Audit Log | Per retention policy |
| Test results | Compliance records | 1 year |

---

[Back to Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
