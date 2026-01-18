# Verification & Testing: Control 4.2 - Site Access Reviews and Certification

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Data Access Governance Reports

1. Navigate to **SharePoint Admin Center** > **Reports** > **Data access governance**
2. Click **Get started** (if first use) or view existing reports
3. Run "Site permissions across your organization" report
4. Verify report shows permission details for all sites
5. **EXPECTED:** Reports accessible and showing current data

### Test 2: Verify Site Attestation Policy Configuration

1. Navigate to **SharePoint Admin Center** > **Policies** > **Site lifecycle management**
2. Click **Open** under "Site attestation policies"
3. Verify attestation policy is configured for regulated sites
4. Check notification settings (30, 14, 7 day reminders)
5. Verify non-compliance action is set (read-only recommended)
6. **EXPECTED:** Attestation policy active with appropriate settings

### Test 3: Verify Access Review in Entra ID

1. Navigate to **Entra Admin Center** > **Identity governance** > **Access reviews**
2. Locate the SharePoint site access review
3. Verify review status and schedule
4. Check reviewer assignments
5. **EXPECTED:** Access review scheduled with correct settings

### Test 4: Test Notification Flow

1. Create a test site requiring attestation
2. Wait for notification cycle (or manually trigger if available)
3. Verify site owner receives attestation request
4. Complete attestation as site owner
5. **EXPECTED:** Notification received and attestation completes successfully

### Test 5: Verify Non-Compliance Action

1. Identify a test site with overdue attestation (or simulate)
2. Let the attestation deadline pass
3. Verify non-compliance action is applied (read-only or archive)
4. **EXPECTED:** Site becomes read-only per policy configuration

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-4.2-01 | Data access governance reports accessible | Reports generate with permission data | |
| TC-4.2-02 | Site attestation policy created | Policy shows in Site lifecycle management | |
| TC-4.2-03 | Attestation notifications sent | Site owners receive email notifications | |
| TC-4.2-04 | Attestation completed by owner | Attestation recorded with timestamp | |
| TC-4.2-05 | Non-compliance action triggered | Site becomes read-only after deadline | |
| TC-4.2-06 | Access review created in Entra ID | Review shows with correct schedule | |
| TC-4.2-07 | Access review decisions exported | CSV export contains all decisions | |

---

## Evidence to Retain

Collect and store the following artifacts for audit readiness:

### Configuration Evidence

- [ ] Screenshot of site attestation policy configuration
- [ ] Screenshot of access review schedule in Entra ID
- [ ] Export of Data access governance "Site permissions" report
- [ ] Documentation of review frequency by governance tier

### Review Evidence

- [ ] Attestation responses for each review cycle
- [ ] Access review decisions export from Entra ID
- [ ] Remediation records for access changes
- [ ] Exception documentation with approvals

### Compliance Evidence

- [ ] Quarterly review completion rates
- [ ] Escalation records for non-responsive sites
- [ ] Audit trail of permission changes
- [ ] Signed attestation statements from site owners

---

## Automated Validation Script

```powershell
# Run validation checks for Control 4.2
Write-Host "=== Control 4.2 Validation ===" -ForegroundColor Cyan

# Connect to services
Connect-MgGraph -Scopes "AccessReview.Read.All"
$adminUrl = "https://yourtenant-admin.sharepoint.com"
Connect-SPOService -Url $adminUrl

$PassCount = 0
$FailCount = 0

# Check 1: Verify access reviews exist
Write-Host "`n[Check 1] Verifying access reviews..." -ForegroundColor Yellow
$reviews = Get-MgIdentityGovernanceAccessReviewDefinition
if ($reviews.Count -gt 0) {
    Write-Host "[PASS] Found $($reviews.Count) access review definition(s)" -ForegroundColor Green
    $PassCount++
}
else {
    Write-Host "[FAIL] No access reviews configured" -ForegroundColor Red
    $FailCount++
}

# Check 2: Verify sites have owners
Write-Host "`n[Check 2] Checking site ownership..." -ForegroundColor Yellow
$sites = Get-SPOSite -Limit All | Where-Object { $_.Template -notlike "*SPSPERS*" }
$orphanedSites = $sites | Where-Object { [string]::IsNullOrEmpty($_.Owner) }

if ($orphanedSites.Count -eq 0) {
    Write-Host "[PASS] All sites have owners assigned" -ForegroundColor Green
    $PassCount++
}
else {
    Write-Host "[WARN] Found $($orphanedSites.Count) sites without owners" -ForegroundColor Yellow
    $orphanedSites | ForEach-Object { Write-Host "  - $($_.Url)" -ForegroundColor Yellow }
}

# Check 3: Verify regulated sites have sensitivity labels
Write-Host "`n[Check 3] Checking sensitivity labels..." -ForegroundColor Yellow
$unlabeledSites = $sites | Where-Object {
    [string]::IsNullOrEmpty($_.SensitivityLabel) -and
    ($_.Url -like "*confidential*" -or $_.Url -like "*regulated*" -or $_.Url -like "*enterprise*")
}

if ($unlabeledSites.Count -eq 0) {
    Write-Host "[PASS] Potentially sensitive sites have labels" -ForegroundColor Green
    $PassCount++
}
else {
    Write-Host "[WARN] Found $($unlabeledSites.Count) potentially sensitive sites without labels" -ForegroundColor Yellow
    $unlabeledSites | Select-Object Url | Format-Table
}

# Summary
Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
Write-Host "Passed: $PassCount" -ForegroundColor Green
Write-Host "Failed: $FailCount" -ForegroundColor $(if ($FailCount -gt 0) { "Red" } else { "Green" })
```

---

## Verification Evidence Template

| Evidence Type | Location | Retention |
|---------------|----------|-----------|
| Permissions report export | Data access governance | 1 year |
| Attestation policy screenshot | Site lifecycle management | 1 year |
| Attestation responses | Site lifecycle management | 6 years |
| Access review decisions | Entra ID exports | 6 years |
| Remediation records | Governance documentation | 6 years |

---

[Back to Control 4.2](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
