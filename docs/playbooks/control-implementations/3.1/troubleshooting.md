# Troubleshooting: Control 3.1 - Agent Inventory and Metadata Management

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| PPAC Inventory shows 0 items | Preview feature not enabled or data not synced | Wait 24-48 hours for initial sync; verify feature is enabled |
| Missing agents from inventory | Agents in environments without proper access | Verify Power Platform Admin role |
| Owner shows as "System Account" | Agent created by deleted user or service principal | Follow orphaned agent remediation process |
| Cannot export inventory to CSV | Browser permissions or popup blocker | Disable popup blocker for PPAC; try different browser |
| PowerShell commands timeout | Large number of environments or items | Process environments in batches; increase timeout values |
| Inventory count mismatch | Sync latency between portals | Allow 24 hours for sync; filter by item type for comparison |

---

## Detailed Troubleshooting

### Issue: PPAC Inventory Shows 0 Items

**Symptoms:** Power Platform inventory page loads but shows no items.

**Diagnostic Steps:**

1. Verify the feature is in Preview and enabled for your tenant
2. Check if data synchronization has completed (initial sync can take 24-48 hours)
3. Verify your role:
   ```
   Entra Admin Center > Identity > Users > [Your user] > Assigned roles
   ```
4. Confirm you have Power Platform Admin role

**Resolution:**
- Wait 24-48 hours for initial sync
- Contact Microsoft support if sync does not complete
- Verify tenant settings allow inventory feature

---

### Issue: Missing Agents from Inventory

**Symptoms:** Known agents do not appear in the Power Platform inventory.

**Diagnostic Steps:**

1. Verify the agent's environment is accessible:
   ```powershell
   Get-AdminPowerAppEnvironment | Select-Object DisplayName, EnvironmentName
   ```

2. Check your access to the specific environment:
   ```powershell
   Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName "environment-id" |
       Where-Object { $_.PrincipalDisplayName -eq "YourName" }
   ```

3. Verify the agent exists in the environment:
   ```powershell
   Get-AdminPowerApp -EnvironmentName "environment-id"
   ```

4. Check environment security settings that may restrict visibility

**Resolution:**
- Request appropriate role assignment for hidden environments
- Verify environment has not been deleted or disabled
- Check if agent was created recently (sync delay)

---

### Issue: Owner Shows as "System Account"

**Symptoms:** Agent owner displays as "System Account" or deleted user reference.

**Diagnostic Steps:**

1. Check Entra ID for the original owner's status:
   ```
   Entra Admin Center > Identity > Users > Deleted users
   ```

2. Review the agent's creation history if available

3. Check if a service principal created the agent:
   ```powershell
   Get-AdminPowerApp -EnvironmentName "env-id" |
       Where-Object { $_.DisplayName -eq "AgentName" } |
       Select-Object Owner
   ```

**Resolution:**
- Follow orphaned agent remediation process (see [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md))
- Assign new owner from appropriate business unit
- Document ownership transfer in governance records

---

### Issue: Inventory Count Differs from Copilot Studio

**Symptoms:** PPAC inventory shows different count than Copilot Studio agent list.

**Diagnostic Steps:**

1. PPAC Inventory includes all item types (apps, flows, agents)
2. Filter PPAC Inventory by "Item type = Agent" for accurate comparison
3. Check environment filter in Copilot Studio
4. Allow 24 hours for sync between portals

**Resolution:**
- Use consistent filtering across both portals
- Document the source of each count
- Reconcile differences during inventory review

---

### Issue: Cannot Export Inventory to CSV

**Symptoms:** Export button does not respond or file does not download.

**Diagnostic Steps:**

1. Check browser popup blocker settings
2. Try a different browser (Edge recommended for M365)
3. Clear browser cache and cookies
4. Verify you have download permissions

**Resolution:**
- Disable popup blocker for admin.powerplatform.microsoft.com
- Use PowerShell export as alternative
- Contact IT support for browser configuration

---

### Issue: PowerShell Commands Timeout

**Symptoms:** Get-AdminPowerApp or Get-AdminFlow commands timeout with large environments.

**Diagnostic Steps:**

1. Check the number of environments:
   ```powershell
   (Get-AdminPowerAppEnvironment).Count
   ```

2. Test individual environment access:
   ```powershell
   Get-AdminPowerApp -EnvironmentName "specific-env-id" -Top 10
   ```

**Resolution:**
- Process environments in batches
- Use the -Top parameter to limit results
- Implement pagination in scripts:
  ```powershell
  # Process in batches
  $environments = Get-AdminPowerAppEnvironment
  foreach ($env in $environments) {
      $apps = Get-AdminPowerApp -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue
      # Process apps...
      Start-Sleep -Seconds 2  # Rate limiting
  }
  ```

---

### Issue: Cannot See Specific Environment in Inventory

**Symptoms:** A known environment does not appear in the inventory view.

**Diagnostic Steps:**

1. Verify environment has not been deleted:
   ```powershell
   Get-AdminPowerAppEnvironment -EnvironmentName "env-id"
   ```

2. Check your role assignment for that environment

3. Confirm environment region matches your admin center access

4. Verify environment is not in a restricted security group

**Resolution:**
- Request environment access from Environment Admin
- Contact Entra Global Admin for visibility issues
- Check if environment requires special permissions

---

## How to Confirm Configuration is Active

### Via Portal (PPAC)

1. Navigate to **Manage** > **Inventory**
2. Verify item count is displayed
3. Apply "Item type = Agent" filter
4. Confirm expected agents are visible

### Via Portal (M365 Admin Center)

1. Navigate to **Settings** > **Integrated apps** > **Agents**
2. Verify declarative agents are listed
3. Check deployment status for each

### Via PowerShell

```powershell
# Quick validation check
Write-Host "Checking Control 3.1 Configuration..." -ForegroundColor Cyan

# Check environment access
$envCount = (Get-AdminPowerAppEnvironment).Count
Write-Host "Accessible environments: $envCount" -ForegroundColor Green

# Check app access
$appCount = (Get-AdminPowerApp).Count
Write-Host "Visible Power Apps: $appCount" -ForegroundColor Green

# Check for recent exports
$exportPath = "C:\Governance\AgentInventory"
if (Test-Path $exportPath) {
    $latestExport = Get-ChildItem $exportPath -Filter "*.csv" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($latestExport) {
        Write-Host "Latest export: $($latestExport.Name) ($($latestExport.LastWriteTime))" -ForegroundColor Green
    }
}
```

---

## Escalation Path

If issues persist after troubleshooting:

1. **Power Platform Admin Team** - For inventory access and environment issues
2. **Entra ID Admin Team** - For role assignment and permission issues
3. **Microsoft Support** - For platform bugs or feature availability
4. **AI Governance Lead** - For policy and process questions
5. **Compliance Officer** - For regulatory implications of inventory gaps

---

[Back to Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
