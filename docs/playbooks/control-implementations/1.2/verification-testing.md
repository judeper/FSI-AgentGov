# Verification & Testing: Control 1.2 - Agent Registry and Integrated Apps Management

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Confirm Registry is Complete

1. Navigate to SharePoint registry list
2. Compare count with Power Platform discovery
3. **EXPECTED:** All agents in environments appear in registry

### Test 2: Verify Integrated Apps Visibility

1. Navigate to M365 Admin Center > Settings > Integrated Apps
2. Confirm all published Copilot Studio agents appear
3. **EXPECTED:** Complete list with user access details

### Test 3: Test Discovery Automation

1. Create a test agent in sandbox environment
2. Wait for automated scan to run
3. Check for alert notification
4. **EXPECTED:** Unregistered agent flagged within scheduled interval

### Test 4: Validate Metadata Completeness

1. Select 5 random agents from registry
2. Verify all required fields are populated
3. **EXPECTED:** 100% field completion for Tier 2-3 agents

### Test 5: Confirm Approval Workflow

1. Attempt to publish agent without registration
2. **EXPECTED:** Blocked or flagged per approval policy

### Test 6: Verify Review Scheduling

1. Check registry for agents with upcoming review dates
2. Confirm notifications are being sent
3. **EXPECTED:** Reminders sent 30 days before review due

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.2-01 | Registry completeness check | All discovered agents in registry | |
| TC-1.2-02 | Integrated Apps visibility | All agents visible in M365 Admin | |
| TC-1.2-03 | Unregistered agent detection | Alert generated within SLA | |
| TC-1.2-04 | Metadata completeness | All required fields populated | |
| TC-1.2-05 | Approval workflow enforcement | Unpublished agents cannot deploy | |
| TC-1.2-06 | Review notification | Reminders sent on schedule | |
| TC-1.2-07 | Orphaned agent detection | Owner changes flagged | |

---

## Evidence to Retain

Collect and store the following artifacts for audit readiness:

### Registry Configuration

- [ ] Screenshot: SharePoint registry list with sample entries
- [ ] Export: Full agent inventory CSV
- [ ] Documentation: Metadata schema and naming convention

### Integrated Apps

- [ ] Screenshot: Integrated Apps configuration in M365 Admin Center
- [ ] Export: List of all integrated applications

### Approval Workflow

- [ ] Documentation: Approval workflow process
- [ ] Screenshot: Approval settings in Power Platform Admin Center
- [ ] Sample: Completed approval record

### Automation Evidence

- [ ] Screenshot: Power Automate flow configuration
- [ ] Log: Automated discovery scan results
- [ ] Sample: Alert notification for unregistered agent

### Attestation Statement

- [ ] Signed statement from control owner confirming:
  - Registry is current and complete
  - All agents have documented owners
  - Review schedule is being followed
  - Approval workflow is enforced

---

## Automated Validation Script

```powershell
# Run validation checks for Control 1.2
Write-Host "=== Control 1.2 Validation ===" -ForegroundColor Cyan

# Check 1: Verify agent discovery
$AllEnvironments = Get-AdminPowerAppEnvironment
$TotalAgents = 0

foreach ($Env in $AllEnvironments) {
    $Apps = Get-AdminPowerApp -EnvironmentName $Env.EnvironmentName
    $TotalAgents += $Apps.Count
}

Write-Host "[INFO] Total agents discovered: $TotalAgents" -ForegroundColor Cyan

# Check 2: Compare with registry (assumes CSV export exists)
if (Test-Path "C:\Governance\RegisteredAgents.csv") {
    $RegisteredAgents = Import-Csv "C:\Governance\RegisteredAgents.csv"
    $RegisteredCount = $RegisteredAgents.Count

    if ($RegisteredCount -ge $TotalAgents) {
        Write-Host "[PASS] Registry count ($RegisteredCount) >= Discovered count ($TotalAgents)" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Registry may be incomplete: $RegisteredCount registered vs $TotalAgents discovered" -ForegroundColor Yellow
    }
} else {
    Write-Host "[SKIP] No registered agents CSV found for comparison" -ForegroundColor Gray
}

# Check 3: Verify Integrated Apps access
try {
    Connect-MgGraph -Scopes "Application.Read.All" -NoWelcome
    $IntegratedApps = Get-MgServicePrincipal -Filter "tags/any(t:t eq 'WindowsAzureActiveDirectoryIntegratedApp')" -Top 10
    Write-Host "[PASS] Can access Integrated Apps via Graph API" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Cannot access Integrated Apps: $($_.Exception.Message)" -ForegroundColor Red
}

# Check 4: Verify orphaned agents (owners no longer active)
Write-Host "`nChecking for orphaned agents..." -ForegroundColor Cyan
# This would require comparing owner emails against Entra ID user status
# Implementation depends on your specific setup
```

---

## Zone-Specific Verification

### Zone 1 (Personal Productivity)

| Check | Frequency | Method |
|-------|-----------|--------|
| Agent count | Monthly | Automated discovery |
| Owner validation | Quarterly | Manual review |
| Basic metadata | Monthly | Spot check |

### Zone 2 (Team Collaboration)

| Check | Frequency | Method |
|-------|-----------|--------|
| Complete inventory | Weekly | Automated discovery |
| Full metadata validation | Monthly | Automated + manual |
| Approval records | Monthly | SharePoint audit |
| Owner verification | Monthly | Entra ID cross-reference |

### Zone 3 (Enterprise Managed)

| Check | Frequency | Method |
|-------|-----------|--------|
| Real-time inventory | Daily | Automated with alerts |
| Full metadata + audit trail | Weekly | Automated validation |
| Approval + risk assessment | Per change | Workflow enforcement |
| Owner + backup owner | Weekly | Automated check |
| Regulatory readiness | Quarterly | Full audit preparation |

---

[Back to Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
