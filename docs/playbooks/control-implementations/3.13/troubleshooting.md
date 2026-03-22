# Playbook 3.11-D: Troubleshooting — Resolving Common Analytics and Export Issues

**Playbook ID:** 3.11-D
**Control:** 3.11 — Agent 365 Admin Center Analytics and Reporting
**Pillar:** Reporting
**Last Verified:** March 2026

---

!!! info "Preview-Period Caveat"
    Many issues during the Frontier Preview period result from feature changes, endpoint modifications, or tenant-specific configuration states that may differ from documented behavior. Always verify current Microsoft Learn documentation and check the Microsoft 365 Message Center for service announcements before escalating to Microsoft Support.

---

## Overview

This playbook documents the most common issues encountered when implementing and operating Control 3.13 and provides structured remediation steps. Issues are organized by symptom category. For each issue, the playbook provides: probable cause, diagnostic steps, resolution steps, and escalation path if self-service resolution is not possible.

---

## Issue Category 1: Cannot Access Agent 365 Overview Page

### Issue 1.1: "Agents" option not visible in M365 Admin Center navigation

**Symptom**: The "Agents" item does not appear in the M365 Admin Center left navigation, even after selecting "Show all."

**Probable Causes**:
- The signed-in account does not have the Global Administrator or Microsoft 365 Copilot Admin role
- The tenant does not have an active Microsoft 365 Copilot license
- A browser caching issue is presenting a stale navigation state

**Diagnostic Steps**:
1. Verify the signed-in account's roles: Entra Admin Center > Users > [your account] > Assigned roles. Confirm "Global Administrator" or "Microsoft 365 Copilot Administrator" is listed.
2. Verify Copilot licensing: M365 Admin Center > Billing > Licenses. Confirm Microsoft 365 Copilot licenses are present and assigned.
3. Check the M365 Message Center for any active service advisories affecting the Admin Center navigation.

**Resolution**:
1. If the account lacks the required role: have a current Global Admin assign the Microsoft 365 Copilot Admin role via Entra Admin Center > Roles and administrators.
2. If the tenant lacks Copilot licenses: the Agent 365 features require Copilot licensing. Work with your Microsoft account team to acquire appropriate licenses.
3. If a caching issue is suspected: clear browser cache and cookies, open a new private browsing window, and navigate to `https://admin.microsoft.com` again.
4. Try the direct navigation URL: `https://admin.microsoft.com/Adminportal/Home#/agents`

**Escalation**: If the above steps do not resolve the issue and the account has confirmed licensing and role assignments, open a Microsoft 365 Admin support ticket via Admin Center > Support > New service request.

---

### Issue 1.2: Agent 365 Overview page loads but shows no data

**Symptom**: The Overview page loads but the Agent Registry count shows zero or displays a "no data available" placeholder despite known agent deployments.

**Probable Causes**:
- No agents have been formally registered in the Agent Registry
- A data refresh delay (metrics may take up to 48 hours to populate after initial agent deployment)
- The tenant is in a new state and telemetry has not yet been generated

**Diagnostic Steps**:
1. Navigate to Agents > All Agents. Confirm whether any agents are listed in the full inventory view.
2. If agents are listed in All Agents but not reflected in the Overview count, a data sync issue is present — note the discrepancy and time.
3. If All Agents is also empty, agents may not be registered. Review Control 3.1 (Agent Inventory) to confirm agents are registered.

**Resolution**:
1. Allow 24–48 hours after agent registration or first use for the Overview metrics to populate.
2. If agents are in All Agents but Overview shows zero after 48 hours, perform a browser hard refresh (Ctrl+Shift+R) on the Overview page.
3. If the issue persists beyond 48 hours, open a Microsoft 365 Admin support ticket with the details of the discrepancy.

---

## Issue Category 2: Hero Metrics Not Visible [Frontier Preview]

### Issue 2.1: Hero metric cards show placeholder or are absent from the page

**Symptom**: The Overview page displays the Agent Registry count but the four hero metric cards (Active Users, Total Sessions, Exception Rate, Agent Runtime) are not visible, or display a "Frontier Preview required" message.

**Probable Causes**:
- Tenant is not enrolled in the Microsoft 365 Frontier program
- Frontier enrollment is pending and not yet fully provisioned

**Diagnostic Steps**:
1. Navigate to M365 Admin Center > Settings > Org settings > Microsoft 365 Insider program (or equivalent Frontier enrollment page). Confirm enrollment status.
2. Check the M365 Message Center for any Frontier-specific announcements about feature availability in your region.

**Resolution**:
1. Enroll in the Frontier program: M365 Admin Center > Settings > Org settings > Microsoft 365 Insider (or Frontier) > Enroll.
2. Allow 24–72 hours for enrollment to propagate and Frontier features to activate.
3. After enrollment confirmation, revisit the Overview page. Hero metrics should appear.
4. Document the Frontier enrollment date and store it in the IT governance register.

**Escalation**: If enrollment is confirmed but hero metrics are still absent after 72 hours, contact Microsoft Support via your FastTrack contact or admin support ticket.

---

### Issue 2.2: Exception Rate metric shows 0% or 100% unexpectedly

**Symptom**: The Exception Rate hero metric displays an anomalous value — either 0% (no sessions completing successfully) or exactly 100% (implying perfect completion) — which appears inconsistent with known agent activity.

**Probable Causes**:
- Custom agents are not instrumented with the Agent 365 Observability SDK, causing exception data to be absent from the calculation
- A telemetry ingestion issue is affecting the exception rate denominator
- All measured sessions have in fact completed without error (100% is possible in low-volume environments)

**Diagnostic Steps**:
1. Check Total Sessions count. If Total Sessions = 0, exception rate of 100% is mathematically indeterminate and should be treated as "no data."
2. Review Control 3.14 implementation status: confirm custom agents have the Observability SDK implemented and ENABLE_A365_OBSERVABILITY_EXPORTER=true is set.
3. If exception rate = 0%, check Microsoft Defender for agent-related incident alerts that may indicate a widespread failure event.

**Resolution**:
1. If the root cause is missing SDK instrumentation: implement the Agent 365 Observability SDK per Control 3.14 and Playbook 3.12-B.
2. If Total Sessions = 0 despite known agent usage: see Issue 2.3 below.
3. If exception rate = 0% and Defender shows active incidents: initiate incident response procedures; do not attempt Admin Center resolution until the agent failure is understood.

---

## Issue Category 3: Governance Card Issues

### Issue 3.1: Pending Requests count does not match Requests tab count

**Symptom**: The Pending Requests governance card shows a different count than the actual number of requests visible in the Agent Registry > Requests tab.

**Probable Causes**:
- The governance card reflects a 30-day rolling window while the Requests tab may show all-time unresolved requests
- A display caching issue is causing the card to show stale data
- Requests were dispositioned in the Requests tab but the card has not yet refreshed

**Resolution**:
1. Refresh the Overview page (F5 or browser refresh). Governance cards typically refresh on page load.
2. If the discrepancy persists after refresh, treat the Requests tab count as authoritative for disposition purposes — it shows the actual queue.
3. Document the discrepancy in the review log and note the date/time. If it persists across multiple review sessions, raise a Microsoft Support ticket.

---

### Issue 3.2: "Assign Owner" button navigates to unfiltered agent list

**Symptom**: Selecting "Assign Owner" from the Ownerless Agents card does not apply the Ownerless Agents filter and instead shows the full All Agents list.

**Probable Causes**:
- A UI bug in the current Admin Center version
- Browser extension interfering with URL parameter passing

**Resolution**:
1. Clear browser extensions, or use a private browsing window without extensions.
2. As a workaround, navigate manually: Agents > All Agents > Filter by Owner = "None" or "Unassigned" (exact filter label may vary).
3. Assign owners manually using the filter. Document that the governance card navigation was non-functional and the date.
4. Check the M365 Message Center for known issues with the Admin Center navigation and report the issue via Admin Center > Support if no known issue exists.

---

## Issue Category 4: Inventory Export Issues

### Issue 4.1: Export button produces a file with fewer rows than agents shown in All Agents list

**Symptom**: The downloaded CSV contains fewer agent entries than the count displayed in the All Agents list.

**Probable Causes**:
- The All Agents list paginates (e.g., 50 agents per page) and the display count reflects the current page, not the full list
- Some agents are in a state (e.g., "Disabled" or "Draft") that excludes them from the export
- A mid-export agent status change caused a record to be missed

**Resolution**:
1. Navigate to All Agents and look for a total count indicator (e.g., "Showing 1–50 of 247") in the page header. Use this total as the expected export row count, not the visible page count.
2. Check whether the All Agents list has any active filters applied (filter pills visible in the list header). Clear all filters before exporting to ensure a full unfiltered export.
3. If filtered and unfiltered counts match and still differ from the export: open a Microsoft Support ticket with the specific count discrepancy and export date.

---

### Issue 4.2: Automated PowerShell export script returns a 404 error on the Graph API endpoint

**Symptom**: The Export-AgentInventory.ps1 script fails with an HTTP 404 (Not Found) error when calling the Graph API endpoint.

**Probable Causes**:
- The Graph API endpoint path for Agent 365 data has changed during the Preview period (this is expected behavior for Preview APIs)
- The Entra app registration lacks the required API permissions

**Diagnostic Steps**:
1. Check the current Microsoft Graph API changelog: `https://learn.microsoft.com/en-us/graph/changelog`
2. Search for "agents" or "agent 365" in the changelog for recent endpoint path changes.
3. Verify the Entra app registration API permissions in Entra Admin Center: App registrations > [your app] > API permissions. Confirm `Reports.Read.All` and `Directory.Read.All` are granted with admin consent.

**Resolution**:
1. Update the `$AgentInventoryUri` variable in Export-AgentInventory.ps1 to the current endpoint path per the Microsoft Graph changelog.
2. If permissions are missing: add the required permissions in Entra and re-grant admin consent.
3. Test with the updated endpoint using the interactive Graph Explorer (`https://developer.microsoft.com/en-us/graph/graph-explorer`) before updating the production script.

!!! warning "Preview API Instability"
    Preview Graph API endpoints can change without a deprecation notice. Build your automation scripts to handle 404 and 410 errors gracefully, log the failure, and send an alert to the IT operations team rather than silently failing. The compliance officer must be notified if an automated export fails, as this creates a gap in the examination artifact record.

---

### Issue 4.3: Azure Blob Storage upload fails with authorization error

**Symptom**: The PowerShell export script successfully generates the CSV but fails during the Azure Blob Storage upload step with an authorization error.

**Probable Causes**:
- The automation service account or managed identity lacks the Storage Blob Data Contributor role on the target storage account
- The storage account has network access restrictions that block the automation host

**Resolution**:
1. Assign the Storage Blob Data Contributor role: Azure Portal > Storage Account > Access Control (IAM) > Add role assignment > Storage Blob Data Contributor > assign to the service account or managed identity.
2. If using network restrictions: add the automation host's IP address or VNet to the storage account's allowed networks. Azure Portal > Storage Account > Networking > Firewalls and virtual networks.
3. Test upload with a simple PowerShell test after role assignment:

```powershell
$Context = (Get-AzStorageAccount -ResourceGroupName $rg -Name $sa).Context
Set-AzStorageBlobContent -File "C:\test.txt" -Container "agent-inventory-exports" `
    -Blob "test.txt" -Context $Context
```

---

## Issue Category 5: Alert Workflow Issues

### Issue 5.1: Power Automate flow is not sending alert emails

**Symptom**: Threshold conditions appear to be met (e.g., pending requests exceed the threshold) but no alert email is received.

**Probable Causes**:
- The flow is paused or turned off
- The Office 365 Outlook connector in Power Automate has expired credentials
- The alert threshold condition logic contains an error
- Alert emails are being delivered to the spam/junk folder

**Diagnostic Steps**:
1. Navigate to Power Automate > My flows > `FSI-AgentGov-3.11-ComplianceAlerts`.
2. Check flow status: must be "On."
3. Review flow run history: expand recent runs and check for error states in individual actions.
4. If the flow is running but emails are not received: check the recipient's spam/junk folder.

**Resolution**:
1. If flow is off: turn it on and document why it was turned off.
2. If the Outlook connector shows credential errors: re-authenticate the connection under Power Automate > Connections.
3. If condition logic is failing: test the condition values manually using the Power Automate "Test" function with a manually entered payload.
4. If emails are going to spam: add the Power Automate sender address to the firm's email safe-sender list via Exchange admin.

---

### Issue 5.2: Graph API call in Power Automate returns authentication error

**Symptom**: The HTTP action in the Power Automate flow that calls the Graph API returns a 401 Unauthorized error.

**Resolution**:
1. Verify the OAuth 2.0 connection configuration in Power Automate: the client ID, client secret, and tenant ID must be correct.
2. Confirm the Entra app registration has admin consent for the required permissions and the consent has not expired or been revoked.
3. Regenerate the client secret in Entra (Certificates & secrets > New client secret) and update the secret value in the Power Automate connection and/or Azure Key Vault.

---

## Issue Category 6: Supervisory Review Log Gaps

### Issue 6.1: Review log entries are missing for one or more required review dates

**Symptom**: Internal Audit identifies gaps in the supervisory review log — dates where a review was required by the Zone designation but no log entry exists.

**Regulatory Risk**: Missing review log entries are evidence of a supervisory control failure under FINRA Rule 3110. This is a material finding that must be escalated to the CCO and documented in the firm's compliance deficiency log.

**Resolution**:
1. Identify all gaps in the review log by comparing actual entry dates to the required cadence schedule.
2. For each gap, determine whether a review actually occurred but was not logged (recoverable with a retroactive entry noting the lateness) or whether no review occurred (non-recoverable gap requiring a formal deficiency notice).
3. If a review occurred but was not logged: create a retroactive log entry clearly marked as "retroactively logged on [date] by [reviewer]" with the reason for the delay. Include this entry in the deficiency log.
4. If no review occurred: log a formal deficiency entry. Initiate root cause analysis. Implement corrective controls (e.g., calendar reminders, GRC task auto-creation) to prevent recurrence.
5. Report the deficiency to the CCO. Determine whether the gap requires disclosure in any pending regulatory filing or examination response.

!!! danger "FINRA 3110 Deficiency"
    A supervisory review log gap is not a technical issue — it is a regulatory compliance failure. Do not attempt to create falsified log entries. Retroactive entries are permissible when clearly labeled, but they do not cure the underlying supervisory gap. Escalate immediately to Legal and Compliance for guidance on appropriate disclosure.

---

## Escalation Matrix

| Severity | Issue Type | First Escalation | Second Escalation | Timeline |
|---|---|---|---|---|
| P1 — Critical | Exception rate drop > 20 percentage points; widespread agent failure | CISO + CCO immediate notification | Microsoft Support P1 ticket | Within 1 hour |
| P2 — High | Export automation failure; agent inventory data missing from Admin Center | IT Operations Lead | Microsoft Support standard ticket | Within 4 hours |
| P3 — Medium | Hero metrics not populating; governance card discrepancy | IT Governance Lead | Microsoft Support standard ticket | Within 1 business day |
| P4 — Low | Navigation issues; minor UI discrepancies | IT Help Desk | IT Governance Lead | Within 3 business days |
| Compliance | Review log gaps; ownerless agent SLA breach | CCO | Legal / External Counsel | Per firm incident response policy |

---

## Microsoft Support Resources

- **M365 Admin Support**: M365 Admin Center > Support > New service request
- **Microsoft 365 Message Center**: M365 Admin Center > Health > Message center (check for known issues before opening tickets)
- **Microsoft Tech Community — M365 Admin**: `https://techcommunity.microsoft.com/t5/microsoft-365-admin/bd-p/Microsoft365Admin`
- **Microsoft 365 Status Page**: `https://status.office.com` (check for active service incidents)
- **FastTrack for Microsoft 365**: Contact your FastTrack Success Architect for Frontier Preview issues

---

[Back to Control 3.13](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

*Updated: March 2026 | Version: v1.3*
