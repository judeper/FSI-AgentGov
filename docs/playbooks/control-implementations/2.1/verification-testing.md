# Verification & Testing: Control 2.1 - Managed Environments

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Verify Managed Environment Status

1. Sign in to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Environments** > select target environment
3. Locate the **Managed environments** card
4. **EXPECTED:** Card shows "Managed environment: Yes" or enabled status

### Test 2: Verify Sharing Limits Enforcement

1. Sign in as a non-admin maker in the managed environment
2. Create a test app or agent
3. Attempt to share the app with more users than the configured limit
4. **EXPECTED:** Sharing is blocked or constrained per configured limits

### Test 3: Verify Solution Checker Enforcement (If Configured to Block)

1. Create or obtain a test solution with known checker findings
2. Attempt to import the solution into the managed environment
3. **EXPECTED:** Import is blocked; solution checker results displayed

### Test 4: Verify Usage Insights Delivery

1. Wait for the weekly digest cycle (sent on Mondays)
2. Check inboxes of configured recipients
3. **EXPECTED:** Weekly usage digest email received with environment activity summary

### Test 5: Verify Maker Welcome Content

1. Sign in as a new maker (first-time access to environment)
2. Navigate to [Power Apps](https://make.powerapps.com) or [Copilot Studio](https://copilotstudio.microsoft.com)
3. Select the managed environment
4. **EXPECTED:** Welcome content dialog displays with configured governance guidance

### Test 6: Verify Data Policies Applied

1. In PPAC, navigate to **Environments** > select target environment
2. Open **Edit managed environments** panel
3. Click **See active data policies for this environment**
4. **EXPECTED:** Expected DLP policies are listed as active

### Test 7: Verify Cross-Tenant Restrictions

1. In a test app, attempt to use a connector that accesses an external tenant
2. **EXPECTED:** Connection blocked per cross-tenant restriction settings

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-2.1-01 | Check Managed Environment status in PPAC | Status shows enabled | |
| TC-2.1-02 | Non-admin attempts to share beyond limit | Sharing blocked | |
| TC-2.1-03 | Import solution with checker findings (Block mode) | Import blocked | |
| TC-2.1-04 | Weekly usage digest delivery | Email received by recipients | |
| TC-2.1-05 | New maker sees welcome content | Welcome dialog displays | |
| TC-2.1-06 | Verify DLP policies applied | Policies listed in panel | |
| TC-2.1-07 | Cross-tenant connector access | Blocked per configuration | |
| TC-2.1-08 | Environment Admin bypasses sharing limits | Admin can share (expected) | |

---

## Evidence Collection Checklist

Retain an evidence pack per environment. Minimum recommended artifacts:

### Environment Configuration

- [ ] Screenshot: PPAC > Environment details showing **Managed Environment = Yes**
- [ ] Screenshot: **Edit managed environments** panel showing configured settings:
  - Sharing limits configuration
  - Solution checker level
  - Usage insights recipients
  - Maker welcome content
- [ ] Screenshot: Environment region showing US location

### Data Policies

- [ ] Screenshot: Environment **Data policies** showing active DLP policy list
- [ ] Screenshot: DLP policy **Environments** tab showing the environment assigned

### Usage Insights

- [ ] Email evidence: Weekly Usage Insights digest received by intended recipients
- [ ] Save email with message header and body

### Solution Checker (If Applicable)

- [ ] Screenshot: Solution checker enforcement setting
- [ ] Screenshot: Test import blocked (if Block mode enabled)

### Cross-Tenant Restrictions

- [ ] Screenshot: Privacy + Security settings showing cross-tenant configuration

### PowerShell Exports

- [ ] Export: PowerShell environment config JSON snapshot
- [ ] Export: CSV inventory report of all environments

---

## Automated Validation Script

```powershell
# Run validation checks for Control 2.1
param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentName
)

Write-Host "=== Control 2.1 Validation ===" -ForegroundColor Cyan

# Connect to Power Platform (interactive authentication)
Add-PowerAppsAccount

# For automated/unattended scenarios, use service principal authentication:
# $appId = "<Application-Client-ID>"
# $secret = "<Client-Secret>"
# $tenantId = "<Tenant-ID>"
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId

# Check 1: Verify environment exists and get details
$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName

if (-not $env) {
    Write-Host "[FAIL] Environment not found: $EnvironmentName" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Environment: $($env.DisplayName)" -ForegroundColor Cyan

# Check 2: Verify Managed Environment status
$protectionLevel = $env.Properties.protectionLevel
if ($protectionLevel -ne "Standard") {
    Write-Host "[PASS] Managed Environment is enabled" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Managed Environment is NOT enabled" -ForegroundColor Red
}

# Check 3: Verify US region
$region = $env.Location
if ($region -match "unitedstates|US") {
    Write-Host "[PASS] Environment is in US region: $region" -ForegroundColor Green
} else {
    Write-Host "[WARN] Verify region is US-compliant: $region" -ForegroundColor Yellow
}

# Check 4: Verify environment type for production
if ($env.EnvironmentType -eq "Production") {
    Write-Host "[INFO] Production environment - verify Block mode for solution checker" -ForegroundColor Cyan
}

# Check 5: Verify Dataverse status
if ($env.Properties.linkedEnvironmentMetadata) {
    Write-Host "[INFO] Dataverse is provisioned - solution checker is applicable" -ForegroundColor Cyan
} else {
    Write-Host "[INFO] No Dataverse - solution checker N/A, document accordingly" -ForegroundColor Cyan
}

# Summary
Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
Write-Host "Environment: $($env.DisplayName)"
Write-Host "Type: $($env.EnvironmentType)"
Write-Host "Region: $region"
Write-Host "Managed: $(if ($protectionLevel -ne 'Standard') { 'Yes' } else { 'No' })"
Write-Host "Dataverse: $(if ($env.Properties.linkedEnvironmentMetadata) { 'Yes' } else { 'No' })"
```

---

## Evidence Artifact Naming Convention

Use consistent naming for audit evidence:

```
Control-2.1_[EnvironmentName]_[ArtifactType]_[YYYYMMDD].[ext]

Examples:
- Control-2.1_FSI-Production_ManagedEnvPanel_20260115.png
- Control-2.1_FSI-Production_SharingLimits_20260115.png
- Control-2.1_FSI-Production_UsageDigest_20260120.eml
- Control-2.1_FSI-Production_EnvConfig_20260115.json
```

---

## Attestation Statement Template

Prepare signed attestation for control owner:

```markdown
## Control 2.1 Attestation - Managed Environments

**Environment:** [Environment Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. The environment [Environment Name] is configured as a Managed Environment
2. Sharing limits are configured per governance zone [Zone 1/2/3]
3. Solution checker enforcement is set to [None/Warn/Block]
4. Usage insights are enabled with recipients: [List recipients]
5. Maker welcome content includes governance policy information
6. Data policies are applied and enforced
7. Evidence artifacts are retained per policy in US-only repositories

**Signature:** _______________________
**Date:** _______________________
```

---

## SSPM Configuration Verification

!!! abstract "Security Posture Assessment Test Cases"

    The following test cases validate configuration points flagged by security posture assessments. Each test maps to a specific setting in the [Configuration Hardening Baseline](../../advanced-implementations/configuration-hardening-baseline/index.md).

| Test ID | Configuration Point | Expected Result | Portal Path | Evidence |
|---------|-------------------|-----------------|-------------|----------|
| SSPM-2.1-01 | Environment creation restriction | Set to "Only specific admins" | PPAC > Settings > Environment creation | Screenshot |
| SSPM-2.1-02 | Environment routing | Routing rules configured for new environments | PPAC > Settings > Environment routing | Screenshot |
| SSPM-2.1-03 | Tenant isolation | Tenant isolation enabled | PPAC > Settings > Tenant isolation | Screenshot |
| SSPM-2.1-04 | Security groups | Security groups assigned to Zone 2/3 environments | PPAC > Environments > {env} > Settings > Security groups | Screenshot |

### Test Procedures

**SSPM-2.1-01: Environment Creation Restriction**

1. Navigate to **PPAC** > **Settings** > **Environment creation**
2. Verify "Who can create production and sandbox environments" is set to **Only specific admins**
3. **Pass criteria:** Environment creation is restricted — not set to "Everyone" or "All licensed users"
4. **Evidence:** Screenshot showing environment creation restriction setting

**SSPM-2.1-02: Environment Routing**

1. Navigate to **PPAC** > **Settings** > **Environment routing**
2. Verify routing rules are configured to direct new maker environments to managed environments
3. **Pass criteria:** Routing rules are active and directing new environments per governance policy
4. **Evidence:** Screenshot showing environment routing configuration with active rules

**SSPM-2.1-03: Tenant Isolation**

1. Navigate to **PPAC** > **Settings** > **Tenant isolation**
2. Verify tenant isolation is **Enabled**
3. Review any configured exceptions (allowlisted tenants)
4. **Pass criteria:** Tenant isolation is enabled; any exceptions are documented and approved
5. **Evidence:** Screenshot showing tenant isolation toggle and exception list

**SSPM-2.1-04: Security Groups**

1. Navigate to **PPAC** > **Environments** > select a Zone 2 or Zone 3 environment
2. Open **Settings** > **Security groups** (or check the environment details panel)
3. Verify a security group is assigned to restrict access
4. Repeat for each Zone 2/3 environment
5. **Pass criteria:** All Zone 2 and Zone 3 environments have a security group assigned — not "Open to all"
6. **Evidence:** Screenshot showing security group assignment for each Zone 2/3 environment

---

*Updated: February 2026 | Version: v1.3 | Classification: Verification Testing*

[Back to Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
