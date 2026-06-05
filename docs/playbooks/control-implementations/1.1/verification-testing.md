# Verification & Testing: Control 1.1 - Restrict Agent Publishing by Authorization

**Last Updated:** May 2026

!!! warning "Audit-log methodology prerequisites"
    Before running Test 4 / Test 5 / SSPM-1.1-05–06, verify the following — otherwise a second admin will get "no results" and incorrectly conclude the control is broken:

    - **Power Platform environment auditing** is enabled on each environment under inspection (PPAC > Environments > [env] > Settings > Audit and logs > Audit settings).
    - **Microsoft Purview Audit** is enabled tenant-wide. Audit (Standard) gives 180-day retention; Audit (Premium) gives 1 year by default; longer retention requires an **Audit Retention Policy** in Purview.
    - **All time inputs/outputs are UTC.** Audit search operates in UTC; FSI policy retention windows are typically in local time. Convert explicitly.
    - **Audit ingestion delay:** new events typically appear in Purview within **60–90 minutes** for core services; Microsoft does **not** publish a hard SLA. If an event is absent after several hours, escalate per Troubleshooting.

## Testing Cadence

| Test ID | Trigger | Frequency |
|---|---|---|
| TC-1.1-01, -02 | Per-event (after any group / role change) | + monthly sample |
| TC-1.1-03, -04 | Per-event (after any release-gate change) | + monthly sample |
| TC-1.1-05, -06 | Continuous via SSPM / weekly spot-check | + monthly sample |
| TC-1.1-07 | **Annual full re-attestation** + monthly sample of 5 publishes | required |
| Full re-execution of all tests | After any tenant-level Power Platform / Microsoft Copilot Studio rollout note (MC update) affecting agent governance | required |

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

### Test 3: Verify Server-Side Publish-Authorization Enforcement (PROD)

> **Why this rewrite matters:** A greyed-out UI button is a UX hint, not enforcement evidence. An auditor needs proof that the *server* rejects an unauthorized publish, not that the client hides a button.

1. Sign in as a user in `FSI-Agent-Makers-*` but **NOT** in `FSI-Agent-Publishers-Prod`. Capture UPN, UTC timestamp.
2. Attempt a publish to PROD via a **non-UI surface** — at least one of:
   - **Power Platform CLI:** `pac auth create -t <tenant> -u <upn>`; then `pac copilot publish --environment <prod-env-id> --bot-id <agent-id>`
   - **Power Platform Web API:** call the publish endpoint with the test user's bearer token
   - **Microsoft 365 Agents Toolkit / SDK** equivalent for M365 Agent Builder agents
3. Capture the **server response payload** in full — HTTP status, response body (typically a 401/403 with a Microsoft `code`/`message`), and the `x-ms-correlation-id` / `request-id` header.
4. Within ~60–90 minutes, confirm the rejection appears in Purview Audit (Search-UnifiedAuditLog with `Operations BotUpdateOperation-BotPublish` and `ResultStatus -ne Success`).
5. **EXPECTED ARTIFACTS for an examiner:**
   - Tester UPN, environment ID, agent ID
   - UTC request timestamp
   - HTTP status + raw response body
   - Correlation/request ID
   - Purview audit row showing the rejected operation tied to the same correlation ID
   - SHA-256 hash of the captured artifacts

### Test 4: Verify Audit Logging

1. Navigate to [Microsoft Purview portal](https://purview.microsoft.com) > Audit
2. Search for Copilot Studio activities. The correct operation label is `BotUpdateOperation-BotPublish` (verified against `learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio`)
3. Verify all publishing attempts are logged with:
   - User identity (`UserKey`)
   - Timestamp (`CreationTime`, UTC)
   - Agent details (`BotId`, `BotSchemaName`)
   - `ResultStatus`
4. Export results as CSV; preserve the `Date` column header; compute SHA-256 of the export
5. **EXPECTED:** All attempts logged with full details; no events missing within the search window (allowing for ~60–90 min ingestion delay)

### Test 5: Correlate Publish Events to Approvals

1. Define the approval **system of record** (SharePoint list, ServiceNow, ITSM tool) and the **join key** between approval records and Purview audit rows (typically a change ticket ID or correlation ID embedded in the publish request)
2. Choose a temporal window (e.g., the most recent 30 days)
3. Export approval records and Purview publish events for that window
4. Join on the agreed key; identify any publish events without a matching approval AND any approvals without a corresponding publish
5. Document the **exception path** — every gap must have a documented reason (e.g., approval rejected, publish rolled back, break-glass with retroactive approval)
6. **EXPECTED:** 100% of production publishes mapped to a pre-dated approval; 100% of approvals either consumed or expired

### Test 6: Verify Sharing Restrictions

1. As an authorized maker, create an agent
2. Try to share the agent with "Everyone" or an unauthorized group
3. **EXPECTED:** Sharing blocked per Managed Environment agent-sharing settings (allow up to ~1 hour for setting propagation; existing shares are not retroactively removed)

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

> **Audit-grade evidence requires more than screenshots.** SEC Rule 17a-4(f) and FINRA 4511(b) expect immutable, query-able, hashed records with chain of custody. Use this list as the working artifact set; preserve all exported evidence through the Control 1.7 architecture: Azure immutable blob storage with a locked time-based policy, a 17a-4-attested archive vendor, or the documented audit-trail alternative with DEO/DTP documentation and an independent records-management assessment. Do not treat SharePoint record labels alone as the preservation layer for this evidence set.

### Identity & Authorization

- [ ] **Microsoft Graph JSON export** of `FSI-Agent-Makers-*` group membership (with UTC timestamp). `GET https://graph.microsoft.com/v1.0/groups/{id}/members?$select=id,userPrincipalName,displayName`
- [ ] **Microsoft Graph JSON export** of `FSI-Agent-Publishers-Prod` group membership
- [ ] SHA-256 hashes of the above JSON files; record hashes in the evidence index
- [ ] Periodic access-review attestations (Entra Access Reviews export) for both groups

### Environment Configuration (PPAC)

- [ ] Screenshot of environment **Security roles** showing Environment Maker / Dataverse System Admin assignments (annotate with UTC timestamp; cross-reference to a JSON export from the Dataverse Web API)
- [ ] **JSON export** from `Get-TenantSettings` showing `disableShareWithEveryone = true` and AI / generative-AI publishing setting state
- [ ] PPAC export of Managed Environment agent-sharing limits (screenshot + URL + UTC timestamp)
- [ ] Environment region confirmation (US region) — JSON export from `Get-AdminPowerAppEnvironment`

### Approvals & Release Gates

- [ ] Approval record for each production publish (SharePoint list export with item version history retained, or ITSM ticket export)
- [ ] Design / data review documentation
- [ ] DLP / connector policy confirmation (JSON from `Get-DlpPolicy`)
- [ ] UAT sign-off documentation
- [ ] Release authorization record (with UTC timestamps and approver UPN)

### Audit Logs & Correlation

- [ ] **Microsoft Purview Audit search export (CSV)** showing `BotUpdateOperation-BotPublish` events for the period under examination — preserve the `Date` column header; do not re-format dates
- [ ] **Correlation table** mapping: agent name + version → publish event (audit row ID + `x-ms-correlation-id`) → approval / ticket ID → approver UPN → publisher UPN → membership-at-time-of-publish snapshot
- [ ] SHA-256 hashes of every exported file; store in a single `evidence-index.csv` with file name, hash, capture UTC timestamp, operator UPN

### Storage & Chain of Custody

- [ ] Storage location follows the preservation path documented in [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md): Azure immutable blob storage with a locked time-based policy, a 17a-4-attested archive vendor, or the documented audit-trail alternative with DEO/DTP documentation and an independent records-management assessment. Do not store authoritative evidence in user OneDrive or treat SharePoint record labels alone as the preservation layer.
- [ ] Storage region is US per data-residency requirements
- [ ] Access to evidence container is logged and least-privileged

### Attestation Statement

- [ ] Signed statement from control owner confirming:
  - Production publishing is restricted to `FSI-Agent-Publishers-Prod`
  - All production publishes require documented approval
  - Evidence is retained per policy through the preservation path documented in [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
  - The retention period applied matches the firm's record schedule and the record-type model in Control 1.7 (3 years for communications, 6 years for financial/accounting or governance records, 5 years for CFTC records, and longer only where a specific rule or firm schedule requires it)

---

## Automated Validation Script

> **Use the production-grade script.** The parent control's `restrict-agent-publishing.ps1` (referenced from Control 1.1) is the maintained validator. The snippet below is illustrative only — for change-window runs use `restrict-agent-publishing.ps1` and `Test-AgentAuthConfiguration.ps1`.

```powershell
# Illustrative validation - see restrict-agent-publishing.ps1 for production version
param(
    [Parameter(Mandatory=$true)][string]$EnvironmentName,
    [Parameter(Mandatory=$true)][string]$SecurityGroupId,
    )

if ($PSVersionTable.PSEdition -ne 'Desktop') { throw "Run in Windows PowerShell 5.1." }
Add-PowerAppsAccount

Write-Host "=== Control 1.1 Validation ===" -ForegroundColor Cyan
$failures = 0

# Detect Dataverse - cmdlets below do not apply to Dataverse environments
$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName
if ($env.CommonDataServiceDatabaseProvisioningState -eq 'Succeeded') {
    Write-Host "[INFO] Dataverse-backed environment detected." -ForegroundColor Yellow
    Write-Host "[INFO] Validate role assignments via PPAC > Settings > Users + permissions > Security roles." -ForegroundColor Yellow
    Write-Host "[INFO] An empty Get-AdminPowerAppEnvironmentRoleAssignment result here is NOT proof of compliance." -ForegroundColor Yellow
    exit 3   # documented partial-validation exit code
}

# Check 1: No Tenant principal with Environment Maker
$envPermissions = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName
$allUsersEM = $envPermissions | Where-Object {
    $_.PrincipalType -eq "Tenant" -and $_.RoleName -eq "Environment Maker"   # NOTE: 'RoleName' with space, not 'RoleType'
}
if ($allUsersEM) {
    Write-Host "[FAIL] Tenant principal has Environment Maker role" -ForegroundColor Red
    $failures++
} else {
    Write-Host "[PASS] Tenant principal does not have Environment Maker role" -ForegroundColor Green
}

# Check 2: Authorized group has Environment Maker
$authorizedEM = $envPermissions | Where-Object {
    $_.PrincipalObjectId -eq $SecurityGroupId -and $_.RoleName -eq "Environment Maker"
}
if ($authorizedEM) {
    Write-Host "[PASS] Authorized security group has Environment Maker role" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Authorized security group missing Environment Maker role" -ForegroundColor Red
    $failures++
}

# Check 3: Tenant disableShareWithEveryone (CORRECT path - root level)
$settings = Get-TenantSettings
if ($settings.disableShareWithEveryone -eq $true) {
    Write-Host "[PASS] Share with Everyone (canvas apps) is disabled" -ForegroundColor Green
} else {
    Write-Host "[WARN] Share with Everyone (canvas apps) is NOT disabled (supplementary hygiene; not the primary 1.1 control)" -ForegroundColor Yellow
}

if ($failures -gt 0) { exit 1 } else { exit 0 }
```

> **Filter property fix:** The cmdlet returns `RoleName` (with **spaces**, e.g., `"Environment Maker"`). Filtering on `RoleType -eq "EnvironmentMaker"` (the prior version of this script) returns `$null` and produces a false-clean PASS. Always validate the field name on your installed module version with `Get-AdminPowerAppEnvironmentRoleAssignment ... | Get-Member`.

> **Tenant setting path fix:** The setting is at the root of the response, `$settings.disableShareWithEveryone` — not `$settings.powerPlatform.powerApps.disableShareWithEveryone`. Always inspect with `$settings | Get-Member` after a module update.

---

## SSPM Configuration Verification

!!! abstract "Security Posture Assessment Test Cases"

    The following test cases validate configuration points flagged by security posture assessments. Each test maps to a specific setting in the [Configuration Hardening Baseline](../../advanced-implementations/configuration-hardening-baseline/index.md).

| Test ID | Configuration Point | Expected Result | Portal Path | Evidence |
|---------|-------------------|-----------------|-------------|----------|
| SSPM-1.1-01 | Agent authentication mode | Not set to "No Authentication" | Copilot Studio > Settings > Security > Authentication | Screenshot |
| SSPM-1.1-02 | Manual auth sign-in requirement | "Require users to sign in" enabled | Copilot Studio > Settings > Security > Authentication | Screenshot |
| SSPM-1.1-03 | Authentication enforcement | Set to "Always" | Copilot Studio > Settings > Security > Authentication | Screenshot |
| SSPM-1.1-04 | Sharing scope | Not set to "Anyone with the link" | Copilot Studio > Agent > **…** > **Share** | Screenshot |
| SSPM-1.1-05 | Generative AI publishing | AI / generative-AI publishing setting is **Off** (or restricted to specific environments) at tenant level; exception documented if On | PPAC > Manage > Tenant settings > AI features (label may vary by rollout) | JSON export of `Get-TenantSettings` with the AI-feature flag captured + SHA-256 |
| SSPM-1.1-06 | Unapproved agent blocking | Unapproved Copilot Studio agents are blocked at the **instance level** in M365 Admin Center per Portal Walkthrough Step 9. The Teams Admin Center blocking surface is **distinct** from M365 Admin Center agent block — capture whichever applies to the agent's distribution surface. | M365 Admin Center > Copilot > Agents & connectors > Agents > [agent] > Overview > Instance availability **AND/OR** Teams Admin Center > Manage Apps for Teams-distributed agents | Screenshot of Block status per instance + agent ID + UTC timestamp |

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

1. Navigate to **Copilot Studio** > select agent > **…** > **Share**
2. Verify the agent is NOT shared with "Anyone with the link" or unrestricted access
3. **Pass criteria:** Sharing is restricted to specific users or security groups
4. **Evidence:** Screenshot showing sharing scope configuration

**SSPM-1.1-05: Generative AI Publishing**

1. Navigate to **PPAC** > **Manage** > **Tenant Settings**
2. Locate the tenant-level setting for publishing agents that use generative AI features
3. Verify the setting is **Off** (disabled)
4. **Pass criteria:** Generative AI agent publishing is disabled at tenant level
5. **Evidence:** Screenshot showing tenant settings page with toggle state

**SSPM-1.1-06: Unapproved Agent Blocking**

1. Navigate to **Teams Admin Center** > **Manage Apps**
2. Search for any unapproved Copilot Studio agents
3. Verify unapproved agents are blocked from Teams channels
4. **Pass criteria:** Only approved agents are available in Teams; unapproved agents show "Blocked" status
5. **Evidence:** Screenshot showing app management page with agent status

---

[Back to Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
