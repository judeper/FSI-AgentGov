# Troubleshooting: Control 1.1 - Restrict Agent Publishing by Authorization

**Last Updated:** April 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| User can still create agents | Security group not applied; user has Dataverse System Admin (bypasses Maker restriction); user already had a Copilot Studio license at time tenant author-gate was set (license-grandfathering) | Verify group membership; check Dataverse security roles in PPAC; verify license was removed for users not in the approved group |
| Authorized user cannot access | Group sync delay; nested-group not supported by destination control; user signed-in to wrong tenant | Wait up to 60 minutes for Entra sync; have user sign out/in; flatten nested groups if required; check for Conditional Access policy blocking the sign-in |
| Publishing events not in audit | Audit not enabled at tenant or environment level; ingestion delay; wrong operation name | Verify Unified Audit Log is on; verify per-environment auditing is on; **expect ~60–90 min ingestion (no hard SLA per Microsoft); investigate if absent after several hours**. Search on `BotUpdateOperation-BotPublish` |
| Cannot restrict Copilot Studio | Managed Environments not enabled; tenant author-gate setting renamed in your tenant | Enable Managed Environments first ([Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md)); verify the current label of "Copilot Studio authors" in your tenant rollout |
| Sharing still works | Wrong sharing-limit blade configured (canvas-app limits ≠ agent limits); existing shares not retroactively removed | Configure the **agent** sharing rules in Managed Environment (Editor / Viewer / individuals-only / viewer-cap). Note settings are not retroactive; remove existing over-broad shares manually |
| Group membership not reflected | Entra ID sync delay | Wait up to 60 minutes for directory sync |
| Role assignment fails (403) | Trying to use `Set-AdminPowerAppEnvironmentRoleAssignment` on a Dataverse-backed environment (cmdlet does not work there) | Assign the Dataverse "Environment Maker" / "Copilot Author" role via PPAC > Settings > Users + permissions > Security roles, or via the Dataverse Web API |
| `Get-AdminPowerAppEnvironmentRoleAssignment` returns empty | Dataverse-backed environment (cmdlet returns nothing); module version returning a different shape; sovereign-cloud endpoint mismatch | Check `(Get-AdminPowerAppEnvironment -EnvironmentName <id>).CommonDataServiceDatabaseProvisioningState`. If `Succeeded`, use PPAC. Verify module version with `Get-Module Microsoft.PowerApps.Administration.PowerShell`. For sovereign tenants, add `-Endpoint usgov\|usgovhigh\|dod` to every cmdlet |
| Validation script reports PASS but the environment is wide open | Script filtered on the wrong field (`RoleType` vs `RoleName`) or wrong tenant-setting path | See the corrected validation script in `verification-testing.md`. Always verify property names with `... \| Get-Member` after a module update |
| Authentication change not enforced | Authentication settings take effect **only after the next publish** of each agent | Re-publish the agent after changing authentication; verify in test session |

---

## Detailed Troubleshooting

### Issue: User Can Still Create Agents After Restriction

**Symptoms:** A user who should not have access can still create agents in Copilot Studio.

**Diagnostic Steps:**

1. Verify the user is NOT in the authorized security group:
   ```
   Entra Admin Center > Identity > Groups > [FSI-Agent-Makers-*] > Members
   ```

2. Check if the user has Environment Maker role directly assigned (non-Dataverse environments only):
   ```powershell
   Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName |
       Where-Object { $_.PrincipalDisplayName -eq "username" }
   ```
   If the environment is Dataverse-backed, this returns empty regardless. Inspect via PPAC > Settings > Users + permissions > Security roles instead.

3. Verify the tenant-level Copilot Studio author setting (PPAC > Manage > Tenant settings > Copilot Studio authors) restricts authoring to your approved groups.

4. Check if the user retained access via license-grandfathering: users who already held a Copilot Studio license when the tenant gate was set retain authoring access. Remove the license from non-approved users.

5. Check if the user has Dataverse System Admin role (bypasses Maker restriction):
   ```powershell
   Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName |
       Where-Object { $_.RoleName -eq "System Administrator" }
   ```

**Resolution:** Remove direct role assignments; ensure user is not in an authorized group; remove Copilot Studio license from non-approved users; assess whether the user legitimately needs Dataverse System Admin.

---

### Issue: Authorized User Cannot Access Environment

**Symptoms:** A user in the authorized security group cannot create agents.

**Diagnostic Steps:**

1. Verify group membership is current (check timestamp on the membership record)
2. Have user sign out completely and sign back in
3. Check for nested group issues — some Power Platform / Copilot Studio surfaces do not honor nested security-group membership; flatten if required
4. Verify the security group is added to both the tenant Copilot Studio authors gate (PPAC > Manage > Tenant settings) **and** the per-environment Dataverse security roles (PPAC > Settings > Users + permissions > Security roles)
5. Check Conditional Access — a CA policy targeting Power Platform / M365 Copilot may be blocking the sign-in even though authorization is correct

**Resolution:**
- Wait 15-60 minutes for sync
- Ensure group is a Security group (not M365 group, unless the destination control supports M365 groups)
- Flatten nested groups if needed
- **Break-glass (time-boxed direct assignment, regulated tenants):** *Direct individual role assignment is acceptable only as a documented break-glass action.* Required artifacts: written approval from the AI Governance Lead or designated approver; explicit expiry timestamp (≤24h recommended); `BotUpdateOperation-BotShare` / role-assignment audit row captured; post-incident review entry; removal of the direct assignment confirmed in audit on or before expiry. Direct assignment without these artifacts breaks the SoD evidence chain and will be flagged on examination.

---

### Issue: Publishing Events Not Appearing in Audit Log

**Symptoms:** Cannot find publish events in Microsoft Purview Audit.

**Diagnostic Steps:**

1. Verify Unified Audit Log is enabled:
   ```powershell
   # Requires ExchangeOnlineManagement module
   # Install-Module ExchangeOnlineManagement -Scope CurrentUser -RequiredVersion <pinned-version>
   # Connect-ExchangeOnline
   Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled
   ```

2. Verify per-environment audit is enabled (PPAC > Environments > [env] > Settings > Audit and logs > Audit settings).

3. Check ingestion delay: Microsoft Learn states audit events typically appear in **60–90 minutes** for core services and does **not** publish a hard SLA. If absent after several hours, escalate. The previous "wait 24-48 hours" guidance was overly conservative and led to delayed incident response.

4. Verify correct search criteria:
   - Operation: `BotUpdateOperation-BotPublish` (verified against Microsoft Learn `admin-logging-copilot-studio`)
   - Workload: search by record type / workload appropriate to the agent surface (`PowerApps` for Power Platform agents; `MicrosoftCopilotStudio` where surfaced)
   - Time range expressed in **UTC**

5. Check the operator has audit-log search permissions (View-Only Audit Logs or Audit Logs role in Purview).

**Resolution:**
- Enable audit logging if disabled
- Expand search date range; use UTC
- Wait through the typical 60–90 min ingestion window before declaring missing
- If absent after several hours, escalate per the FSI Incident Handling section below

---

## Additional Failure Modes (FSI-Relevant)

Failure modes commonly seen in regulated tenants that do not fit the table above:

| Failure Mode | Symptom | Diagnosis | Mitigation |
|---|---|---|---|
| **DLP misclassifies channel connector** | Authorized publisher cannot publish to a previously-allowed channel | DLP policy has been updated to move the connector from Business → Blocked or to a non-overlapping group | Review DLP policy change history; coordinate with DLP owner; document approved exception |
| **"No Authentication" agent re-emerges** | New agents created with `No Authentication` despite policy | Policy is enforced at validation/publish time, not at agent-create time; or the per-agent enforcement was reverted | Run periodic detection (Test 1 in Verification & Testing); enable SSPM-1.1-01 monitoring; apply Copilot Studio data policy that blocks unauthenticated channels |
| **Generative-AI tenant toggle drift** | AI features setting flipped from Off to On unexpectedly | An admin changed it via PPAC; or a Microsoft default-on rollout (per MC notice) re-enabled it | Subscribe to MC notices; run weekly tenant-settings export and diff; restore + document |
| **Conditional Access blocking authorized publisher** | Publish attempt fails with sign-in error, not a 403 | CA policy on the Power Platform service principal blocks the user's location, device, or risk state | Review Entra Sign-in Logs for the failed sign-in; coordinate CA policy exception with security |
| **Copilot Studio license / trial expiry** | Authorized publisher loses access on a specific date | Trial license expired; per-user license reassigned | Inventory license assignments to `FSI-Agent-Publishers-Prod` members monthly; alert ≥30 days before expiry |
| **Service principal API bypass** | Publish appears in audit log but no human approver record | A service-principal token was used to publish (legitimate automation OR API bypass) | Maintain an inventory of service principals authorized to publish; correlate publish events to that inventory; investigate any SP not on the list |
| **Default-environment publish slipping through** | An agent appears in PROD that no one approved | Maker created the agent in the Default environment which was not part of the governance scope | Apply DLP and sharing limits to the Default environment; route makers to governed environments via Environment Routing |
| **Stale PowerShell module returns different field shapes** | Validation script reports PASS in lab, FAIL in PROD (or vice versa) | Module version drift between operator workstations | Pin `-RequiredVersion` (see PowerShell Setup); bake the pinned module into the operator workstation image |

---

## How to Confirm Configuration is Active

### Via Portal (Entra ID)

1. Navigate to **Identity** > **Groups** > Select FSI-Agent-Makers group
2. Verify correct members are listed
3. Check no unauthorized users have access

### Via Portal (Power Platform)

1. Navigate to **Manage** > **Environments** > Select environment
2. Go to **Settings** > **Users + permissions** > **Security roles**
3. Verify Environment Maker role is assigned only to authorized groups

### Via User Testing

1. Have an unauthorized user attempt to access Copilot Studio
2. Verify they cannot create or publish agents
3. Have an authorized user test full workflow

### Via PowerShell

```powershell
# Quick validation check (non-Dataverse environments only)
$EnvironmentName = "your-environment-id"

$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName
if ($env.CommonDataServiceDatabaseProvisioningState -eq 'Succeeded') {
    Write-Host "Dataverse-backed - validate via PPAC Security Roles, not this script" -ForegroundColor Yellow
    return
}

# Check Environment Maker assignments (NOTE: filter on RoleName WITH SPACE, not RoleType)
Write-Host "Environment Maker Assignments:" -ForegroundColor Cyan
Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName |
    Where-Object { $_.RoleName -eq "Environment Maker" } |
    Format-Table PrincipalDisplayName, PrincipalType

# Check for Tenant principal assignment (should be empty)
$allUsers = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName |
    Where-Object { $_.PrincipalType -eq "Tenant" -and $_.RoleName -eq "Environment Maker" }

if ($allUsers) {
    Write-Host "WARNING: Tenant principal still has Environment Maker role!" -ForegroundColor Red
} else {
    Write-Host "OK: Tenant principal does not have Environment Maker role" -ForegroundColor Green
}
```

---

## FSI Incident Handling

> **Use this section when a Control 1.1 failure is detected in production** — for example, an unauthorized publish reaches PROD, a wide-open share is discovered, or audit evidence is missing during examination prep.

### Reportability Decision Tree (consult Compliance / Legal — this is a working aid, not legal advice)

| Scenario | Possible Reportability Triggers | Owner |
|---|---|---|
| Unauthorized agent reached customers and may have accessed customer NPI | **GLBA Safeguards Rule §314.4(j)** breach-notification (≥500 customers, 30 days); state notification laws | CISO + Privacy + Legal |
| Agent acted on behalf of representatives in regulated communications | **FINRA Rule 4530** internal-conclusions report; **FINRA Rule 2210** retail-comms supervision lapse | Compliance / Supervision |
| Agent altered books-and-records or affected ICFR | **SEC 17a-4(f)** records-integrity assessment; **SOX §404** material-weakness assessment | Internal Audit + CFO |
| Model risk event (gen-AI agent producing material errors) | **Federal Reserve SR 26-2 (formerly SR 11-7)** model-event escalation | Model Risk |
| Customer data exfiltration suspected | State breach laws (NY DFS 23 NYCRR §500 cyber event 72-hour, etc.) | CISO + Legal |

### Evidence Preservation BEFORE Remediation

1. **Snapshot tenant settings** before changing anything:
   ```powershell
   Get-TenantSettings | ConvertTo-Json -Depth 20 |
       Out-File ".\incident-tenant-snapshot-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
   ```
2. **Export the offending agent's full configuration** (Copilot Studio export, Dataverse solution export, or Power Platform CLI `pac copilot export`).
3. **Capture audit log evidence** for the incident time window via `Search-UnifiedAuditLog` and export to CSV — preserve column headers; compute SHA-256.
4. **Snapshot group memberships** at incident time (Microsoft Graph JSON export).
5. **Hash and WORM-store everything** before applying any remediation that may alter state.

### Compensating Controls During Outage

| If you must disable... | Compensating control |
|---|---|
| Tenant Copilot Studio authors gate (Layer A) | Disable Copilot Studio licenses for non-approved users; tighten DLP to block all channel connectors; enable agent-publish notifications to Compliance |
| Managed Environment agent-sharing limits (Step 4) | Run hourly export of Copilot Studio agent shares; alert on any new wide-open share |
| Per-agent authentication (Step 6) | Block the agent from all distribution channels (Step 9) until authentication is restored |

### Chain of Custody

For each evidence artifact: file name, SHA-256, capture UTC timestamp, operator UPN, source system, storage location, retention period. Store the index in WORM-capable storage with the artifacts. Do not modify file contents after capture.

### Incident Report Template (Control 1.1 — stub)

- Incident ID + opening UTC timestamp + closing UTC timestamp
- Detection method (SSPM alert, manual review, customer report, audit pull)
- Affected agents (ID, name, environment, distribution surface)
- Affected users / customers (count, classification of data accessed)
- Root cause (from the Additional Failure Modes table or a new mode)
- Remediation actions (timestamped, with operator UPN)
- Evidence artifacts (filename + SHA-256)
- Reportability assessment (Yes/No per row in the decision tree above; with rationale)
- Lessons learned + control changes proposed

---

## Escalation Path

> **Before opening a Microsoft case, gather the pre-call checklist below.** Microsoft Support response times correlate strongly with the completeness of the initial submission.

### Pre-Call Checklist

- [ ] Tenant ID
- [ ] Affected environment ID(s)
- [ ] Affected agent ID(s) and `BotSchemaName`
- [ ] Operator UPN (your account)
- [ ] All UTC timestamps for the issue window
- [ ] Failed-request correlation ID (`x-ms-correlation-id`) and request ID where available
- [ ] Reproduction steps (numbered, exact clicks / cmdlets / API calls)
- [ ] Expected vs observed behavior
- [ ] Power Platform admin module version (`Get-Module Microsoft.PowerApps.Administration.PowerShell`)
- [ ] Browser + OS + tenant cloud (commercial / GCC / GCC-High / DoD)
- [ ] Audit search export covering the issue window (CSV, with `Date` column intact)
- [ ] Screenshots showing the issue (annotated with UTC timestamps)
- [ ] Any recent MC notices that may be related

### Escalation Severity Matrix

| Severity | Trigger | Internal SLA (suggested — confirm against your firm's policy) | Microsoft Support level |
|---|---|---|---|
| **S1 — Critical** | Unauthorized publish reached PROD; customer-facing impact; suspected data exfiltration | 1-hour ack, 4-hour status, continuous engagement | Severity A |
| **S2 — High** | Validation script failing in PROD; control-evidence gap during audit prep window | 4-hour ack, 24-hour status | Severity B |
| **S3 — Medium** | Validation script failing in DEV/UAT; documentation drift; non-blocking issues | 1-business-day ack, 5-business-day status | Severity C |
| **S4 — Low** | Cosmetic issues; future-improvement requests | Weekly review queue | Severity C / Feedback |

### Escalation Order

1. **Power Platform Admin Team** — environment configuration, DLP, Managed Environment settings
2. **Entra ID Admin Team** — security group, role, and Conditional Access issues
3. **AI Governance Lead** — policy interpretation, governance-tier exceptions, break-glass approvals
4. **Compliance / Legal** — reportability decisions, customer notifications, regulatory submissions
5. **Microsoft Support** — platform bugs, feature defects, audit log completeness questions (use pre-call checklist)
6. **Microsoft FastTrack / Account Team** — pattern-level issues across multiple controls or controls-vs-feature roadmap questions

---

[Back to Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
