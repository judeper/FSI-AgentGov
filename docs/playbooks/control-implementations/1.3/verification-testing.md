# Verification & Testing: Control 1.3 - SharePoint Content Governance and Permissions

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Confirm Tenant Sharing Settings

1. Navigate to SharePoint Admin Center > Policies > Sharing
2. Verify external sharing is restricted per FSI requirements
3. **EXPECTED:** External sharing set to "Only people in your organization" or more restrictive

### Test 2: Verify Site-Level Permissions

1. Navigate to agent knowledge source site
2. Go to Site settings > Site permissions
3. Review all permission grants
4. **EXPECTED:** Only approved groups/users; no "Everyone" groups

### Test 3: Test Agent Access Boundaries

1. Configure an agent with access to specific SharePoint sites
2. Ask the agent to retrieve content from an excluded site
3. **EXPECTED:** Agent cannot access or returns "no information found"

### Test 4: Validate Sensitivity Labels

1. Navigate to agent knowledge source document library
2. Check Information panel for documents
3. **EXPECTED:** All documents have appropriate sensitivity labels applied

### Test 5: Confirm External Sharing Blocked

1. Navigate to an enterprise-managed agent knowledge site
2. Attempt to share a document externally
3. **EXPECTED:** Sharing blocked with appropriate message

### Test 6: Test Access Review Notification

1. Verify access review is configured in Entra Admin Center
2. Check that review notifications are being sent
3. **EXPECTED:** Reviewers receive notification per schedule

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.3-01 | Tenant sharing settings check | External sharing restricted | |
| TC-1.3-02 | Site permissions audit | No broad "Everyone" groups | |
| TC-1.3-03 | Agent access boundary test | Cannot access excluded sites | |
| TC-1.3-04 | Sensitivity label validation | Labels applied to documents | |
| TC-1.3-05 | External sharing attempt | Sharing blocked | |
| TC-1.3-06 | Access review notification | Notifications sent on schedule | |
| TC-1.3-07 | IAG restriction test | Restricted content not discoverable | |

---

## Evidence to Retain

Collect and store the following artifacts for audit readiness:

### Tenant Configuration

- [ ] Screenshot: Tenant-level sharing settings
- [ ] Export: Site inventory with sharing settings (CSV)

### Site Permissions

- [ ] Screenshot: Agent knowledge site permissions
- [ ] Export: Permission audit for all agent data sources
- [ ] Documentation: Justification for each permission grant

### Sensitivity Labels

- [ ] Screenshot: Sensitivity labels applied to libraries
- [ ] Export: Label deployment report

### Access Reviews

- [ ] Documentation: Access review schedule and configuration
- [ ] Export: Access review results (completed reviews)

### Attestation Statement

- [ ] Signed statement from control owner confirming:
  - Agent knowledge sites have least-privilege permissions
  - "Everyone" groups have been removed
  - Sensitivity labels are applied per policy
  - Access reviews are conducted on schedule

---

## Automated Validation Script

```powershell
# Run validation checks for Control 1.3
Write-Host "=== Control 1.3 Validation ===" -ForegroundColor Cyan

# Connect to SharePoint
$AdminUrl = "https://contoso-admin.sharepoint.com"
Connect-SPOService -Url $AdminUrl

# Check 1: Verify tenant sharing settings
$TenantSettings = Get-SPOTenant
Write-Host "`nTenant Sharing Settings:" -ForegroundColor Cyan
Write-Host "  Sharing Capability: $($TenantSettings.SharingCapability)"

if ($TenantSettings.SharingCapability -eq "Disabled" -or
    $TenantSettings.SharingCapability -eq "ExistingExternalUserSharingOnly") {
    Write-Host "[PASS] Tenant sharing is appropriately restricted" -ForegroundColor Green
} else {
    Write-Host "[WARN] Tenant sharing may be too permissive" -ForegroundColor Yellow
}

# Check 2: Verify agent sites don't have "Everyone" permissions
$AgentSites = @(
    "https://contoso.sharepoint.com/sites/Agent-CustomerService"
)

Write-Host "`nChecking agent site permissions..." -ForegroundColor Cyan
foreach ($SiteUrl in $AgentSites) {
    try {
        $Users = Get-SPOUser -Site $SiteUrl -Limit All
        $HasEveryone = $Users | Where-Object { $_.LoginName -match "everyone|spo-grid-all-users" }

        if ($HasEveryone) {
            Write-Host "[FAIL] $SiteUrl has 'Everyone' permissions" -ForegroundColor Red
        } else {
            Write-Host "[PASS] $SiteUrl has no 'Everyone' permissions" -ForegroundColor Green
        }
    } catch {
        Write-Host "[ERROR] Cannot check $SiteUrl - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Check 3: Verify sharing is disabled on enterprise agent sites
Write-Host "`nChecking site sharing settings..." -ForegroundColor Cyan
foreach ($SiteUrl in $AgentSites) {
    $Site = Get-SPOSite -Identity $SiteUrl

    if ($Site.SharingCapability -eq "Disabled") {
        Write-Host "[PASS] $SiteUrl - Sharing disabled" -ForegroundColor Green
    } else {
        Write-Host "[WARN] $SiteUrl - Sharing: $($Site.SharingCapability)" -ForegroundColor Yellow
    }
}
```

---

## Zone-Specific Verification

### Zone 1 (Personal Productivity)

| Check | Frequency | Method |
|-------|-----------|--------|
| Site count audit | Quarterly | PowerShell discovery |
| Sharing settings | Annual | Spot check |
| Permissions review | Annual | Site owner self-service |

### Zone 2 (Team Collaboration)

| Check | Frequency | Method |
|-------|-----------|--------|
| Sharing settings | Monthly | Automated check |
| Permissions audit | Semi-annual | PowerShell report |
| Sensitivity labels | Monthly | Purview reports |
| Access reviews | Semi-annual | Entra access reviews |

### Zone 3 (Enterprise Managed)

| Check | Frequency | Method |
|-------|-----------|--------|
| Full permissions audit | Weekly | Automated PowerShell |
| Sharing validation | Weekly | Automated check |
| Sensitivity labels | Weekly | Purview monitoring |
| Access reviews | Quarterly | Entra access reviews |
| IAG configuration | Monthly | Admin center review |

---

[Back to Control 1.3](../../../controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
