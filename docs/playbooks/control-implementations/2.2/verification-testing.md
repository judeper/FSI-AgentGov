# Verification & Testing: Control 2.2 - Environment Groups and Tier Classification

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Environment Groups Exist

1. Sign in to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Manage** > **Environment groups**
3. Verify groups exist for each governance tier (Tier 1/2/3)
4. **EXPECTED:** Groups listed with environment counts

### Test 2: Verify Group Membership

1. Select an environment group
2. Click **Environments** tab
3. Verify environments are assigned to the correct tier group
4. **EXPECTED:** Environments listed with appropriate tier classification

### Test 3: Verify Rules Published

1. Select an environment group
2. Click **Rules** tab
3. Check the status column shows "Published" with date
4. **EXPECTED:** All configured rules show Published status

### Test 4: Test Rule Inheritance

1. Add a new Managed Environment to a Tier 3 group
2. Navigate to the environment's settings
3. Verify the environment inherits group rules (e.g., solution checker = Block)
4. **EXPECTED:** New environment automatically inherits group rules

### Test 5: Test Agent Sharing Restriction (Tier 1)

1. In a Tier 1 environment, create a test agent
2. Attempt to share the agent with another user
3. **EXPECTED:** Sharing is blocked per Tier 1 rules (Editor/Viewer permissions disabled)

### Test 6: Test Solution Checker Enforcement (Tier 3)

1. Create a solution with known checker issues
2. Attempt to import into a Tier 3 environment
3. **EXPECTED:** Import is blocked if solution checker is set to Block

### Test 7: Test External Models Restriction

1. In a Tier 2/3 environment, attempt to configure external AI model
2. **EXPECTED:** External models option is unavailable/blocked

### Test 8: Test Computer Use Restriction

1. Verify Computer Use rule is disabled for all groups
2. Attempt to access CUA features in any environment
3. **EXPECTED:** CUA features are not available

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-2.2-01 | Verify environment groups exist | Groups for Tier 1/2/3 present | |
| TC-2.2-02 | Check environments assigned to correct groups | Environments match tier classification | |
| TC-2.2-03 | Verify rules are published | Status shows "Published" | |
| TC-2.2-04 | Add new environment to group | Inherits rules automatically | |
| TC-2.2-05 | Test Tier 1 sharing restrictions | Agent sharing blocked | |
| TC-2.2-06 | Test Tier 3 solution checker | Non-compliant imports blocked | |
| TC-2.2-07 | Test external models restriction | External models unavailable in Tier 2/3 | |
| TC-2.2-08 | Verify CUA disabled all zones | Computer Use feature unavailable | |
| TC-2.2-09 | Test authentication requirement (Tier 2/3) | Agents require authentication | |
| TC-2.2-10 | Verify unmanaged customizations blocked (Tier 3) | Unmanaged changes rejected | |

---

## Evidence Collection Checklist

### Environment Group Documentation

- [ ] Screenshot: Environment groups list showing all groups with counts
- [ ] Screenshot: Each group's properties (name, description, tier classification)
- [ ] Export: Environment group inventory CSV with IDs and descriptions

### Group Membership

- [ ] Screenshot: Each group's Environments tab showing membership
- [ ] Export: Environment-to-group mapping CSV

### Rule Configuration

- [ ] Screenshot: Rules tab for each group showing configured values
- [ ] Screenshot: Published status with timestamp for each group
- [ ] Note: Document any rules that differ from FSI recommendations with justification

### Testing Evidence

- [ ] Screenshot: Sharing attempt blocked in Tier 1 environment
- [ ] Screenshot: Solution import blocked in Tier 3 environment (if applicable)
- [ ] Screenshot: External models unavailable in restricted environment

### Change Management

- [ ] Change record: Ticket/approval for initial group creation
- [ ] Change record: Approval for rule configurations
- [ ] Change log: Any rule changes during review period

---

## Evidence Artifact Naming Convention

Use consistent naming for audit evidence:

```
Control-2.2_[GroupName]_[ArtifactType]_[YYYYMMDD].[ext]

Examples:
- Control-2.2_FSI-Enterprise-Production_GroupProperties_20260115.png
- Control-2.2_FSI-Team-Collaboration_RulesTab_20260115.png
- Control-2.2_EnvironmentGroupInventory_20260115.csv
- Control-2.2_EnvironmentGroupMapping_20260115.csv
```

---

## Automated Validation Script

```powershell
# Run validation checks for Control 2.2
param(
    [string]$GroupId
)

Write-Host "=== Control 2.2 Validation ===" -ForegroundColor Cyan

# Connect to Power Platform (interactive authentication)
Add-PowerAppsAccount

# For automated/unattended scenarios, use service principal authentication:
# $appId = "<Application-Client-ID>"
# $secret = "<Client-Secret>"
# $tenantId = "<Tenant-ID>"
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId

# Check 1: Verify environment groups exist
$groups = Get-AdminPowerAppEnvironmentGroup
if ($groups) {
    Write-Host "[PASS] $(($groups | Measure-Object).Count) environment groups found" -ForegroundColor Green
} else {
    Write-Host "[FAIL] No environment groups found" -ForegroundColor Red
}

# Check 2: Verify production environments are in groups
$environments = Get-AdminPowerAppEnvironment
$prodEnvs = $environments | Where-Object { $_.EnvironmentType -eq 'Production' }
$ungroupedProd = $prodEnvs | Where-Object { -not $_.EnvironmentGroupId }

if ($ungroupedProd) {
    Write-Host "[WARN] Production environments not in groups:" -ForegroundColor Yellow
    $ungroupedProd | Select-Object DisplayName | Format-Table
} else {
    Write-Host "[PASS] All production environments are in groups" -ForegroundColor Green
}

# Check 3: Verify grouped environments are Managed
$groupedEnvs = $environments | Where-Object { $_.EnvironmentGroupId }
$unmanagedGrouped = $groupedEnvs | Where-Object {
    $_.Properties.governanceConfiguration.protectionLevel -eq 'Standard'
}

if ($unmanagedGrouped) {
    Write-Host "[FAIL] Grouped environments that are NOT Managed:" -ForegroundColor Red
    $unmanagedGrouped | Select-Object DisplayName, EnvironmentGroupId | Format-Table
} else {
    Write-Host "[PASS] All grouped environments are Managed Environments" -ForegroundColor Green
}

# Check 4: Summary by group
Write-Host "`n=== Group Membership Summary ===" -ForegroundColor Cyan
$environments | Group-Object EnvironmentGroupId | ForEach-Object {
    $groupName = if ($_.Name) {
        ($groups | Where-Object { $_.EnvironmentGroupId -eq $_.Name }).DisplayName
    } else {
        "(Ungrouped)"
    }
    Write-Host "$groupName : $($_.Count) environments"
}
```

---

## Attestation Statement Template

```markdown
## Control 2.2 Attestation - Environment Groups and Tier Classification

**Review Period:** [Start Date] to [End Date]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Environment groups have been created for each governance tier:
   - Tier 1 (Personal Productivity): [Group Name]
   - Tier 2 (Team Collaboration): [Group Name]
   - Tier 3 (Enterprise Managed): [Group Name]

2. All production environments are assigned to appropriate tier groups

3. Rules are configured per FSI governance requirements:
   - Tier 1: Sharing disabled, external models disabled, CUA disabled
   - Tier 2: Authentication required, solution checker warn, CUA disabled
   - Tier 3: All security rules enabled, solution checker block, CUA disabled

4. Computer-Using Agents (CUA) is disabled for all environment groups

5. External AI models are disabled for Tier 2 and Tier 3 groups

6. All rule changes during the review period are documented with approvals

7. Evidence artifacts are retained per policy in US-only repositories

**Signature:** _______________________
**Date:** _______________________
```

---

## Evidence Pack Contents

For each audit/review period, retain:

| Artifact | Description | Retention |
|----------|-------------|-----------|
| Groups.csv | Environment group inventory | Per retention policy |
| Environments.csv | Environment-to-group mapping | Per retention policy |
| Rules screenshots | Rule configuration for each group | Per retention policy |
| Change tickets | Approvals for group/rule changes | Per retention policy |
| Test evidence | Screenshots of rule enforcement tests | Per retention policy |
| Attestation | Signed attestation statement | Per retention policy |

---

[Back to Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
