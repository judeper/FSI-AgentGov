# Verification & Testing: Control 3.2 - Usage Analytics and Activity Monitoring

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Monitor Section Access

1. Sign in to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Monitor** in the left navigation
3. Verify the Monitor section loads
4. **EXPECTED:** Monitor overview page displays with summary cards

### Test 2: Verify Alert Rules Configuration

1. Navigate to **Monitor** > **Alerts**
2. Review the list of alert rules
3. Verify pre-built Microsoft rules are visible
4. Check that custom rules are configured for your organization
5. **EXPECTED:** Alert rules are listed and enabled appropriately

### Test 3: Verify Copilot Studio Dashboard

1. Navigate to **Monitor** > **Copilot Studio**
2. Review agent health metrics
3. Verify success rate metrics are displayed
4. Check recent sessions list
5. **EXPECTED:** Dashboard shows agent metrics with current success rates

### Test 4: Verify Alert Notifications

1. Create or identify a test alert rule
2. Manually trigger the alert condition (or wait for natural trigger)
3. Verify notification is received by configured recipients
4. **EXPECTED:** Email/Teams notification received within configured timeframe

### Test 5: Verify Usage Insights Email

1. Confirm Managed Environments have usage insights enabled
2. Wait for weekly digest email (or check recent emails)
3. Verify compliance team is included in recipients
4. **EXPECTED:** Weekly digest email received with environment insights

### Test 6: Verify Audit Log Access

1. Navigate to [Microsoft Purview](https://compliance.microsoft.com) > Audit
2. Search for Power Platform activities
3. Filter by date range (last 7 days)
4. **EXPECTED:** Audit log entries for agent activities are visible

### Test 7: Verify Log Export Functionality

1. In Monitor > Logs, apply filters for your target environment
2. Click Export to download log data
3. Open the export file and verify data completeness
4. **EXPECTED:** CSV/JSON export downloads with complete log entries

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-3.2-01 | Access Monitor section | Overview page loads | |
| TC-3.2-02 | View pre-built alert rules | Microsoft rules listed | |
| TC-3.2-03 | Enable pre-built alert | Alert activates | |
| TC-3.2-04 | Create custom alert rule | Rule saves and activates | |
| TC-3.2-05 | Access Copilot Studio dashboard | Agent metrics displayed | |
| TC-3.2-06 | View success rate metric | Current rate shown | |
| TC-3.2-07 | Test alert notification | Notification received | |
| TC-3.2-08 | Export activity logs | CSV downloads | |
| TC-3.2-09 | Search audit logs | Entries found | |
| TC-3.2-10 | Verify weekly digest | Email received | |

---

## Evidence to Retain

Collect and store the following artifacts for audit readiness:

### Dashboard Screenshots

- [ ] Screenshot of Monitor Overview page
- [ ] Screenshot of Alerts configuration page
- [ ] Screenshot of Copilot Studio dashboard with metrics
- [ ] Screenshot of enabled alert rules list

### Alert Configuration Evidence

- [ ] Export of all configured alert rules
- [ ] List of notification recipients per alert
- [ ] Documentation of alert response procedures
- [ ] Alert history showing triggered alerts

### Usage Reports

- [ ] Weekly usage digest emails (archived)
- [ ] Monthly executive summary reports
- [ ] Trend analysis documentation
- [ ] Capacity planning reports

### Audit Log Evidence

- [ ] Audit log exports for compliance period
- [ ] Activity log exports by environment
- [ ] Error log analysis documentation

### Attestation Statement

- [ ] Signed statement from control owner confirming:
  - Monitoring is actively configured
  - Alerts are reviewed and responded to per SLA
  - Usage reports are generated on schedule
  - Evidence is retained per policy

---

## Automated Validation Script

```powershell
# Run validation checks for Control 3.2
Write-Host "=== Control 3.2 Validation ===" -ForegroundColor Cyan

# Check 1: Verify environment access
$environments = Get-AdminPowerAppEnvironment
if ($environments.Count -gt 0) {
    Write-Host "[PASS] Environment access: $($environments.Count) environments" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Cannot access environments" -ForegroundColor Red
}

# Check 2: Verify managed environments
$managedCount = ($environments | Where-Object { $_.Properties.isManaged -eq $true }).Count
if ($managedCount -gt 0) {
    Write-Host "[PASS] Managed environments: $managedCount (usage insights available)" -ForegroundColor Green
} else {
    Write-Host "[WARN] No managed environments - usage insights unavailable" -ForegroundColor Yellow
}

# Check 3: Verify app visibility for monitoring
$allApps = Get-AdminPowerApp
if ($allApps -ne $null -and $allApps.Count -gt 0) {
    Write-Host "[PASS] App visibility: $($allApps.Count) apps monitored" -ForegroundColor Green
} else {
    Write-Host "[WARN] No apps visible for monitoring" -ForegroundColor Yellow
}

# Check 4: Verify audit log connectivity
try {
    $testAudit = Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-1) -EndDate (Get-Date) -RecordType PowerApps -ResultSize 1 -ErrorAction Stop
    Write-Host "[PASS] Audit log access verified" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Audit log access issue - may need Exchange Online connection" -ForegroundColor Yellow
}

# Check 5: Verify recent exports exist
$exportPath = "C:\Governance\UsageAnalytics"
if (Test-Path $exportPath) {
    $recentExports = Get-ChildItem $exportPath -Filter "*.csv" |
        Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }
    if ($recentExports.Count -gt 0) {
        Write-Host "[PASS] Recent exports found: $($recentExports.Count)" -ForegroundColor Green
    } else {
        Write-Host "[WARN] No exports in last 7 days" -ForegroundColor Yellow
    }
} else {
    Write-Host "[INFO] Export directory not found - create during first export" -ForegroundColor Yellow
}

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

## Governance Tier-Specific Testing

### Level 1 - Baseline Testing

- [ ] Monitor section is accessible
- [ ] Monthly dashboard review documented
- [ ] Basic metrics (success rate) visible

### Level 2-3 - Recommended Testing

- [ ] Pre-built alert rules enabled
- [ ] Custom alerts configured for Tier 2+ agents
- [ ] Weekly dashboard reviews documented
- [ ] Usage insights enabled for managed environments
- [ ] Trend analysis reports generated

### Level 4 - Regulated Testing

- [ ] Daily dashboard reviews documented
- [ ] All pre-built + custom alerts active
- [ ] Success rate targets monitored (>95%)
- [ ] Response SLA tracking implemented
- [ ] GRC integration configured
- [ ] 7-year audit log retention verified

---

## KPI Verification

| KPI | Tier 1 Target | Tier 2 Target | Tier 3 Target | Actual | Status |
|-----|---------------|---------------|---------------|--------|--------|
| Success rate | >80% | >90% | >95% | | |
| Response time | <10s | <5s | <3s | | |
| Availability | 95% | 99% | 99.9% | | |
| Alert response SLA | Next day | 4 hours | 1 hour | | |

---

[Back to Control 3.2](../../../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
