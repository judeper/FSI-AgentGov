# Verification & Testing: Control 3.1 - Agent Inventory and Metadata Management

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Power Platform Inventory Access

1. Sign in to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Manage** > **Inventory**
3. Verify the inventory view loads
4. **EXPECTED:** Power Platform inventory displays with item count

### Test 2: Verify Agent Filtering

1. In Power Platform inventory, click the **Item type** filter
2. Select **Agent** to filter the view
3. Review the filtered results
4. **EXPECTED:** Only agents displayed (apps and flows filtered out)

### Test 3: Verify All Environments Visible

1. Review the **Environment** column values
2. Compare against known environment list
3. Verify all production, sandbox, and developer environments appear
4. **EXPECTED:** All environments with agents are visible

### Test 4: Verify Owner Information

1. Review the **Owner** column for each agent
2. Verify owners are valid users (not system accounts or deleted users)
3. Cross-reference against Entra ID for validity
4. **EXPECTED:** All agents have valid, identifiable owners

### Test 5: Verify Export Functionality

1. Click the **Export** button in the inventory toolbar
2. Select CSV format
3. Download the export file
4. Open and verify all columns are populated
5. **EXPECTED:** CSV export completes with all inventory data

### Test 6: Verify M365 Agent Registry Access

1. Sign in to [Microsoft 365 Admin Center](https://admin.microsoft.com)
2. Navigate to **Settings** > **Integrated apps** > **Agents** tab
3. Review declarative agents and extensions
4. **EXPECTED:** M365 Agent Registry displays organizational agents

### Test 7: Verify Inventory Reconciliation

1. Export Power Platform inventory
2. Export M365 Agent Registry list
3. Compare agent counts
4. Identify any discrepancies
5. **EXPECTED:** Documented understanding of agents in both systems

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-3.1-01 | Access Power Platform inventory | Inventory view loads with items | |
| TC-3.1-02 | Filter by Item type = Agent | Only agents displayed | |
| TC-3.1-03 | View all environments | All known environments visible | |
| TC-3.1-04 | Check owner column | All agents have valid owners | |
| TC-3.1-05 | Export to CSV | Export downloads successfully | |
| TC-3.1-06 | Access M365 Agent Registry | Registry displays agents | |
| TC-3.1-07 | Reconcile both inventories | Discrepancies documented | |
| TC-3.1-08 | Identify orphaned agents | Orphans flagged for remediation | |
| TC-3.1-09 | PowerShell inventory export | Script completes with hash | |
| TC-3.1-10 | Verify NYDFS fields (if applicable) | RTO/RPO fields populated | |

---

## Evidence to Retain

Collect and store the following artifacts for audit readiness:

### Inventory Exports

- [ ] Power Platform inventory CSV export (dated)
- [ ] M365 Agent Registry export (dated)
- [ ] Reconciliation report showing both sources
- [ ] SHA-256 hash of each export file

### Configuration Evidence

- [ ] Screenshot of Power Platform inventory view
- [ ] Screenshot of M365 Admin Center Agents tab
- [ ] Screenshot of inventory filter settings

### Orphaned Agent Documentation

- [ ] List of orphaned agents identified
- [ ] Remediation assignments for each orphan
- [ ] Status tracking for orphan resolution

### System of Record

- [ ] SharePoint list or GRC tool configuration
- [ ] Field definitions and required metadata
- [ ] Version history settings confirmation

### NYDFS Part 500 (if applicable)

- [ ] RTO/RPO values for each agent
- [ ] Criticality tier assignments
- [ ] Backup compliance status
- [ ] Support expiration dates

### Attestation Statement

- [ ] Signed statement from control owner confirming:
  - Inventory is current and complete
  - Both discovery sources are monitored
  - Orphaned agents are tracked for remediation
  - Evidence is retained per policy

---

## Automated Validation Script

```powershell
# Run validation checks for Control 3.1
Write-Host "=== Control 3.1 Validation ===" -ForegroundColor Cyan

# Check 1: Verify environment access
$environments = Get-AdminPowerAppEnvironment
if ($environments.Count -gt 0) {
    Write-Host "[PASS] Environment access verified: $($environments.Count) environments" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Cannot access environments" -ForegroundColor Red
}

# Check 2: Verify app inventory access
$allApps = Get-AdminPowerApp
if ($allApps -ne $null) {
    Write-Host "[PASS] App inventory access verified: $($allApps.Count) apps" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Cannot access app inventory" -ForegroundColor Red
}

# Check 3: Check for orphaned agents
$orphanCount = 0
foreach ($app in $allApps) {
    if ([string]::IsNullOrEmpty($app.Owner.email) -or
        $app.Owner.email -like "*system*" -or
        $app.Owner.email -like "*deleted*") {
        $orphanCount++
    }
}

if ($orphanCount -eq 0) {
    Write-Host "[PASS] No orphaned agents detected" -ForegroundColor Green
} else {
    Write-Host "[WARN] $orphanCount orphaned agents require remediation" -ForegroundColor Yellow
}

# Check 4: Verify export directory exists
$exportPath = "C:\Governance\AgentInventory"
if (Test-Path $exportPath) {
    $recentExports = Get-ChildItem $exportPath -Filter "AgentInventory_*.csv" |
        Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }
    if ($recentExports.Count -gt 0) {
        Write-Host "[PASS] Recent inventory exports found: $($recentExports.Count)" -ForegroundColor Green
    } else {
        Write-Host "[WARN] No inventory exports in last 7 days" -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARN] Export directory not found - create and configure" -ForegroundColor Yellow
}

# Check 5: Verify hash file exists
$hashFile = "$exportPath\AgentInventory_Hashes.csv"
if (Test-Path $hashFile) {
    Write-Host "[PASS] Hash verification file exists" -ForegroundColor Green
} else {
    Write-Host "[WARN] Hash verification file not found - integrity tracking not configured" -ForegroundColor Yellow
}

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

## Governance Tier-Specific Testing

### Level 1 - Baseline Testing

- [ ] Monthly inventory review completed
- [ ] Basic metadata (owner, environment, dates) captured
- [ ] Orphaned agents identified

### Level 2-3 - Recommended Testing

- [ ] Weekly inventory exports automated
- [ ] Extended metadata captured (purpose, data sources, approvals)
- [ ] Dashboard reporting configured
- [ ] GRC tool integration verified
- [ ] Hash verification implemented

### Level 4 - Regulated Testing

- [ ] Daily inventory reviews completed
- [ ] Real-time drift detection configured
- [ ] Executive reporting generated monthly
- [ ] NYDFS Part 500 fields populated
- [ ] Comprehensive metadata validated
- [ ] Audit trail snapshots retained

---

[Back to Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
