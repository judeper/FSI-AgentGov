# Verification & Testing: Control 1.1 - Restrict Agent Publishing by Authorization

**Last Updated:** February 2026

## Manual Verification Steps

### Test 1: Verify Non-Authorized Maker Access

1. Sign in as a user **NOT** in the authorized security group
2. Navigate to [Copilot Studio](https://copilotstudio.microsoft.com)
3. Attempt to create a new agent
4. **EXPECTED:** Access is blocked or limited - cannot create or publish agents

### Test 2: Verify Authorized Maker Access

1. Sign in as a user **IN** the authorized security group
2. Navigate to [Copilot Studio](https://copilotstudio.microsoft.com)
3. Create a test agent in the appropriate environment
4. Verify publishing succeeds
5. **EXPECTED:** Can create and publish agents

### Test 3: Verify Release Gate Enforcement (PROD)

1. Sign in as a user in `FSI-Agent-Makers-*` but **NOT** in `FSI-Agent-Publishers-Prod`
2. Access the PROD environment (if they have Basic User access)
3. Attempt to create/edit/publish agents in PROD
4. **EXPECTED:** No ability to publish in PROD

### Test 4: Verify Audit Logging

1. Navigate to [Microsoft Purview portal](https://purview.microsoft.com) > Audit
2. Search for `Published bot` events
3. Verify all publishing attempts are logged with:
   - User identity
   - Timestamp
   - Agent details
4. **EXPECTED:** All attempts logged with full details

### Test 5: Correlate Publish Events to Approvals

For a production publish:

1. Locate the audit log entry for the publish event
2. Find the corresponding approval record/change ticket ID
3. Verify the publisher is a member of `FSI-Agent-Publishers-Prod`
4. Validate timestamps: approval must pre-date publish
5. **EXPECTED:** Every production publish maps to an approval + authorized publisher

### Test 6: Verify Sharing Restrictions

1. As an authorized maker, create an agent
2. Try to share the agent with "Everyone" or an unauthorized group
3. **EXPECTED:** Sharing blocked per Managed Environment settings

### Test 7: Verify Teams/M365 Distribution Restrictions

If Teams/M365 distribution is used:

1. Attempt to make an agent broadly available using a non-admin/non-publisher account
2. **EXPECTED:** Unable to complete org-wide distribution; restricted by role membership and PROD access

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.1-01 | Non-authorized user attempts to create agent | Access denied or blocked | |
| TC-1.1-02 | Authorized user creates agent in DEV | Agent created successfully | |
| TC-1.1-03 | Non-publisher attempts PROD publish | Cannot publish to production | |
| TC-1.1-04 | Publisher publishes to PROD with approval | Publish succeeds, logged | |
| TC-1.1-05 | Audit log captures publish events | Event logged with user/time/details | |
| TC-1.1-06 | Share to "Everyone" attempted | Sharing blocked | |
| TC-1.1-07 | Publish event correlates to approval | Matching ticket/approval found | |

---

## Evidence to Retain

Collect and store the following artifacts for audit readiness:

### Identity & Authorization

- [ ] Screenshot/export of `FSI-Agent-Makers-*` group membership (with timestamp)
- [ ] Screenshot/export of `FSI-Agent-Publishers-Prod` group membership (with timestamp)
- [ ] Periodic access review attestations for the above groups

### Environment Configuration (PPAC)

- [ ] Screenshot of environment **Security roles** showing Environment Maker/Dataverse System Admin assignments
- [ ] Screenshot of Copilot Studio restriction: "Who can create and edit Copilots: Only specific security groups"
- [ ] Screenshot of Managed Environments "Limit sharing" configuration
- [ ] Screenshot of environment region confirmation showing US region

### Approvals & Release Gates

- [ ] Approval record for each production publish (SharePoint list or ticket)
- [ ] Design/data review documentation
- [ ] DLP/connector policy confirmation
- [ ] UAT sign-off documentation
- [ ] Release authorization record

### Audit Logs & Correlation

- [ ] Microsoft Purview Audit search export showing publish events
- [ ] Correlation table mapping: agent name/version → publish event → approval/ticket ID → approver(s)

### Attestation Statement

- [ ] Signed statement from control owner confirming:
  - Production publishing is restricted to `FSI-Agent-Publishers-Prod`
  - All production publishes require documented approval
  - Evidence is retained per policy in US-only repositories

---

## Automated Validation Script

```powershell
# Run validation checks for Control 1.1
Write-Host "=== Control 1.1 Validation ===" -ForegroundColor Cyan

# Check 1: Verify no "All Users" Environment Maker
$envPermissions = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName
$allUsersEM = $envPermissions | Where-Object {
    $_.PrincipalType -eq "Tenant" -and $_.RoleType -eq "EnvironmentMaker"
}

if ($allUsersEM) {
    Write-Host "[FAIL] All Users has Environment Maker role" -ForegroundColor Red
} else {
    Write-Host "[PASS] All Users does not have Environment Maker role" -ForegroundColor Green
}

# Check 2: Verify authorized group has Environment Maker
$authorizedEM = $envPermissions | Where-Object {
    $_.PrincipalObjectId -eq $SecurityGroupId -and $_.RoleType -eq "EnvironmentMaker"
}

if ($authorizedEM) {
    Write-Host "[PASS] Authorized security group has Environment Maker role" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Authorized security group missing Environment Maker role" -ForegroundColor Red
}

# Check 3: Verify Share with Everyone is disabled
$settings = Get-TenantSettings
if ($settings.powerPlatform.powerApps.disableShareWithEveryone -eq $true) {
    Write-Host "[PASS] Share with Everyone is disabled" -ForegroundColor Green
} else {
    Write-Host "[WARN] Share with Everyone is NOT disabled" -ForegroundColor Yellow
}
```

---

## SSPM Configuration Verification

!!! abstract "Security Posture Assessment Test Cases"

    The following test cases validate configuration points flagged by security posture assessments. Each test maps to a specific setting in the [Configuration Hardening Baseline](../../advanced-implementations/configuration-hardening-baseline/index.md).

| Test ID | Configuration Point | Expected Result | Portal Path | Evidence |
|---------|-------------------|-----------------|-------------|----------|
| SSPM-1.1-01 | Agent authentication mode | Not set to "No Authentication" | Copilot Studio > Settings > Security > Authentication | Screenshot |
| SSPM-1.1-02 | Manual auth sign-in requirement | "Require users to sign in" enabled | Copilot Studio > Settings > Security > Authentication | Screenshot |
| SSPM-1.1-03 | Authentication enforcement | Set to "Always" | Copilot Studio > Settings > Security > Authentication | Screenshot |
| SSPM-1.1-04 | Sharing scope | Not set to "Anyone with the link" | Copilot Studio > Settings > Security > Authentication | Screenshot |
| SSPM-1.1-05 | AI feature publishing | "Publish bots with AI features" disabled | PPAC > Manage > Tenant Settings | Screenshot |
| SSPM-1.1-06 | Unapproved agent blocking | Unapproved agents blocked from Teams channels | Teams Admin Center > Manage Apps | Screenshot |

### Test Procedures

**SSPM-1.1-01: Agent Authentication Mode**

1. Navigate to **Copilot Studio** > select agent > **Settings** > **Security** > **Authentication**
2. Verify authentication mode is NOT set to "No Authentication"
3. **Pass criteria:** Authentication is set to "Authenticate with Microsoft" or "Authenticate manually"
4. **Evidence:** Screenshot showing authentication configuration panel

**SSPM-1.1-02: Manual Auth Sign-In Requirement**

1. Navigate to **Copilot Studio** > select agent > **Settings** > **Security** > **Authentication**
2. For agents using manual authentication, verify "Require users to sign in" is enabled
3. **Pass criteria:** Sign-in toggle is enabled for all manually-authenticated agents
4. **Evidence:** Screenshot showing sign-in requirement toggle

**SSPM-1.1-03: Authentication Enforcement**

1. Navigate to **Copilot Studio** > select agent > **Settings** > **Security** > **Authentication**
2. Verify authentication enforcement is set to "Always"
3. **Pass criteria:** Enforcement is "Always" — not "Optional" or "None"
4. **Evidence:** Screenshot showing enforcement setting

**SSPM-1.1-04: Sharing Scope**

1. Navigate to **Copilot Studio** > select agent > **Settings** > **Security** > **Authentication**
2. Verify sharing scope is NOT set to "Anyone with the link"
3. **Pass criteria:** Sharing is restricted to specific users or security groups
4. **Evidence:** Screenshot showing sharing scope configuration

**SSPM-1.1-05: AI Feature Publishing**

1. Navigate to **PPAC** > **Manage** > **Tenant Settings**
2. Locate "Publish bots with AI features" toggle
3. Verify toggle is set to **Off** (disabled)
4. **Pass criteria:** AI feature publishing is disabled at tenant level
5. **Evidence:** Screenshot showing Features page with toggle state

**SSPM-1.1-06: Unapproved Agent Blocking**

1. Navigate to **Teams Admin Center** > **Manage Apps**
2. Search for any unapproved Copilot Studio agents
3. Verify unapproved agents are blocked from Teams channels
4. **Pass criteria:** Only approved agents are available in Teams; unapproved agents show "Blocked" status
5. **Evidence:** Screenshot showing app management page with agent status

---

*Updated: February 2026 | Version: v1.3 | Classification: Verification Testing*

[Back to Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
