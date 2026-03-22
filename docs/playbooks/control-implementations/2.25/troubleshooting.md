# Control 2.25: Microsoft Agent 365 — Admin Center Governance Console — Troubleshooting

This playbook documents common issues encountered when configuring and operating the Agent 365 Admin Center Governance Console, with step-by-step resolutions, root cause analysis, and regulatory impact guidance. All issues are presented with escalation paths appropriate for financial services environments where governance gaps carry regulatory consequences.

!!! info "Frontier Preview — Known Limitations"
    Many issues in this playbook are specific to the Frontier Preview release (current as of March 2026). Some of these issues may be resolved at General Availability (May 1, 2026) as the product matures. Annotate your troubleshooting logs with the date of issue occurrence so you can identify whether the issue persists post-GA and requires a support case.

## Issue Index

| Issue | Severity | Section |
|---|---|---|
| Frontier / Agents section not visible in admin center | High | [Issue 1](#issue-1-frontier-agents-section-not-visible-in-admin-center) |
| Access denied error after enabling Frontier | High | [Issue 2](#issue-2-access-denied-error-after-enabling-frontier) |
| Governance template not applying at publish time | Critical | [Issue 3](#issue-3-governance-template-not-applying-at-publish-time) |
| Agents not showing metrics on Overview dashboard | Medium | [Issue 4](#issue-4-agents-not-showing-metrics-on-overview-dashboard) |
| Pending Requests card shows no requests despite known submissions | High | [Issue 5](#issue-5-pending-requests-card-shows-no-requests-despite-known-submissions) |
| Ownerless Agents card not updating after owner assignment | Medium | [Issue 6](#issue-6-ownerless-agents-card-not-updating-after-owner-assignment) |
| Inventory export produces empty or incomplete file | High | [Issue 7](#issue-7-inventory-export-produces-empty-or-incomplete-file) |
| Researcher Computer Use tab not visible | Medium | [Issue 8](#issue-8-researcher-computer-use-tab-not-visible) |
| Graph API calls returning 403 Forbidden for Agent 365 endpoints | High | [Issue 9](#issue-9-graph-api-calls-returning-403-forbidden-for-agent-365-endpoints) |
| Agent 365 Frontier licenses not appearing in Billing after enrollment | High | [Issue 10](#issue-10-agent-365-frontier-licenses-not-appearing-in-billing-after-enrollment) |

---

## Issue 1: Frontier / Agents Section Not Visible in Admin Center

**Severity:** High
**Regulatory Impact:** All Agent 365 governance controls are blocked until this is resolved. This constitutes a technology risk management control failure under OCC 2011-12 if the intended governance timeline is missed.

**Symptoms:**
- The left navigation in the M365 Admin Center does not show an "Agents" section
- Navigating directly to `https://admin.microsoft.com/#/agents` returns a 404 or redirects to the home page
- Copilot Frontier option is not visible under Copilot > Settings > User Access

**Root Causes:**

| Root Cause | Probability | Check |
|---|---|---|
| No Microsoft 365 Copilot license in tenant | High | Billing > Licenses — check for any M365 Copilot SKU |
| Frontier enrollment not completed | High | Copilot > Settings > User Access — is Frontier toggle present? |
| Admin account lacks required roles | Medium | Entra ID > Roles — requires Global Admin or Copilot Admin role |
| Tenant region not yet supported | Low | Check Microsoft 365 Roadmap for regional GA dates |
| Provisioning still in progress | Medium | Wait 60 minutes after enrolling |

**Resolution Steps:**

1. **Verify Microsoft 365 Copilot license:**
   Navigate to **Billing > Licenses**. Confirm a Microsoft 365 Copilot license (any SKU) is present and has at least one assigned unit. If not present, this license must be procured before Frontier can be enabled. Contact your Microsoft account team.

2. **Verify Frontier enrollment:**
   Navigate to **Copilot > Settings**. If the User Access tab is not visible, your account may lack the required admin role (see step 3). If the tab is visible, check whether the Copilot Frontier toggle is present and its state.

3. **Verify admin role assignment:**
   Navigate to **Entra ID > Roles and Administrators** and confirm your account has one of the following roles: Global Administrator, Copilot Administrator, or a custom role with M365 admin center agent management permissions.

4. **Complete Frontier enrollment:**
   If the toggle is present but set to Disabled, toggle it to Enabled and wait 15–60 minutes. Refresh the admin center browser tab (Ctrl+F5 / Cmd+Shift+R for a hard refresh).

5. **If still not visible after 60 minutes:**
   Toggle Frontier **off**, wait 5 minutes, then toggle it back **on**. This forces a re-provisioning cycle. Wait an additional 60 minutes.

6. **If still not visible after re-provisioning:**
   Open a Microsoft support case via **Admin Center > Support > New Service Request**, referencing SKU name and enrollment date. Provide the support case number to your Technology Risk Manager as documentation that remediation is actively in progress.

**Documentation:** Log all troubleshooting steps with timestamps in your governance activity log. If this issue delays Agent 365 governance implementation beyond your planned timeline, document the delay and its cause in your OCC 2011-12 technology risk register with a revised target date.

---

## Issue 2: Access Denied Error After Enabling Frontier

**Severity:** High
**Regulatory Impact:** Inability to access the governance console after enrollment creates a gap between the intended and actual control state. Document under change management.

**Symptoms:**
- Frontier toggle is Enabled
- Agents section appears in navigation
- Clicking into Agents shows an "Access Denied" or "You don't have permission" error
- Error may appear immediately or after a browser refresh

**Root Causes:**

| Root Cause | Probability | Check |
|---|---|---|
| Provisioning not yet complete (most common) | Very High | Wait up to 60 minutes post-enrollment |
| Session token not refreshed after enrollment | High | Sign out and sign back in |
| Admin consent not yet granted for Agent 365 service | Medium | Entra ID > Enterprise Applications — check Agent 365 |
| Role assignment propagation delay | Low | Entra ID role assignments can take 5–15 minutes to propagate |

**Resolution Steps:**

1. **Wait for provisioning to complete:**
   After enabling Frontier, the Agent 365 backend service provisions your tenant. This takes up to 60 minutes. Do not attempt to access the Agents section during this window.

2. **Sign out and sign back in:**
   After waiting 60 minutes, sign out of the M365 Admin Center completely (not just refresh), then sign back in. This forces a new session token that reflects the updated permissions.

3. **Toggle Frontier off and on:**
   If sign-in refresh does not resolve the issue, navigate back to **Copilot > Settings > User Access > Copilot Frontier**, toggle Frontier **off**, wait 5 minutes, toggle it back **on**, and wait another 60 minutes before retrying.

4. **Verify admin consent for Agent 365:**
   Navigate to **Entra ID > Enterprise Applications**, search for "Agent 365", and confirm the application is present with admin consent granted for the required permissions. If consent is not granted, click **Grant admin consent for [tenant name]**.

5. **Clear browser cache:**
   Try accessing the admin center in an InPrivate/Incognito window to rule out browser cache issues. If InPrivate access works, clear your browser cache and cookies for microsoft.com domains.

6. **If unresolved after all steps:**
   Open a Microsoft support case. Include: tenant ID, admin account UPN, enrollment date/time, error message text, and steps already taken.

---

## Issue 3: Governance Template Not Applying at Publish Time

**Severity:** Critical
**Regulatory Impact:** An agent published without a governance template is operating outside the required policy framework. This is a direct control failure affecting OCC 2011-12 layered security and SOX 404 IT general controls. Block the agent immediately using the Block lifecycle action until the template is applied via re-publication.

**Symptoms:**
- Publishing wizard completes but agent detail view shows "No Template" or blank Governance Template field
- Policies from the Default Template (Purview Audit, SharePoint Site Access Control, etc.) are not active for the published agent
- Admin consent prompt during template application was dismissed or failed silently

**Root Causes:**

| Root Cause | Probability | Check |
|---|---|---|
| Admin consent not granted for template policies | Very High | Template application requires admin consent; if dismissed, template silently fails to apply |
| Template application step skipped in wizard | High | Wizard allows proceeding without selecting a template |
| Custom template has configuration errors | Medium | Template picker may show template but policies may be misconfigured |
| Permissions missing on governance template service | Low | Service principal / admin account may lack policy application permissions |

**Resolution Steps:**

1. **Immediately block the affected agent:**
   Navigate to **Agents > All Agents > Registry**, locate the affected agent, and click **Block**. This prevents users from interacting with the agent until the governance gap is remediated. Document this action in your change management system as an emergency remediation.

2. **Grant admin consent for template policies:**
   Navigate to **Entra ID > Enterprise Applications** and search for each policy service in the Default Template (e.g., "Agent Identity Protection", "Purview AI Compliance"). For each service, confirm admin consent is granted. If consent is missing, click **Grant admin consent for [tenant name]** and accept.

   Alternatively, navigate to the governance template settings page and use the **Grant Consent for All Template Policies** bulk action if available in your build.

3. **Re-publish the agent with template applied:**
   Open a change management ticket for the re-publication. Navigate to the blocked agent's detail view and initiate a new publish action. In the publishing wizard, explicitly select the correct governance template at the Apply Template step. Do not click Next until the template is shown as selected and all policies show a green consent status.

4. **Verify template application post-publish:**
   After re-publishing, open the agent detail view and confirm the Governance Template field shows the correct template name. Perform TC-2.25-03 test case verification steps to confirm Purview Audit and other policies are active.

5. **Document as a control deficiency:**
   Log the initial publication without a template as a control deficiency in your SOX 404 testing workpapers. Document: agent name, publication date, date gap discovered, remediation date, and root cause. Assess whether the gap was material based on the agent's data access and user scope.

!!! danger "Do Not Leave an Untemplatted Agent Active"
    An agent operating in Zone 2 or Zone 3 without a governance template applied is not governed. Do not unblock the agent until you have confirmed the template is applied and the policy bundle is active. There is no grace period for governance template compliance in regulated financial services environments.

---

## Issue 4: Agents Not Showing Metrics on Overview Dashboard

**Severity:** Medium
**Regulatory Impact:** Monitoring gaps reduce the effectiveness of the supervisory system (FINRA 3110) and may prevent timely detection of anomalous behavior (OCC 2011-12). Document coverage limitations in your monitoring runbook.

**Symptoms:**
- Hero metrics show zero or unexpectedly low values
- Specific agents are not contributing to Active Users, Total Sessions, or Exception Rate metrics
- Analytics charts (Agents by Publishers, Active Users Over Time) appear blank or incomplete

**Root Causes:**

| Root Cause | Probability | Check |
|---|---|---|
| Agents built on unsupported platforms | Very High | Only Copilot Agent Builder, SharePoint, M365 Agents Toolkit, and Observability SDK agents generate metrics |
| Agent has had zero usage in the last 30 days | High | Metrics are usage-based; inactive agents show zeros |
| Observability SDK not instrumented | Medium | Custom agents require SDK integration to generate metrics |
| Data pipeline delay | Low | Metrics may have a 2–4 hour ingestion lag |

**Resolution Steps:**

1. **Identify agent platform:**
   For each agent showing no metrics, check the Platform field in the agent detail view. If the platform is not one of: Copilot Agent Builder, SharePoint, M365 Agents Toolkit, or a platform with Observability SDK integration, this is expected behavior — not a bug.

2. **Document the coverage gap:**
   In your monitoring runbook, list all agents that do not generate metrics and the reason. For these agents, implement alternative monitoring (e.g., Purview Audit log queries, SharePoint access logs, Azure Monitor for Azure AI Foundry agents).

3. **Instrument custom agents with Observability SDK:**
   For custom-built agents on Azure AI Foundry or partner platforms, work with the development team to integrate the Microsoft Observability SDK. This enables metric reporting to the Agent 365 dashboard. Reference Microsoft Learn documentation for the Observability SDK integration guide.

4. **For legitimate zero-usage scenarios:**
   If an agent has not been used in 30 days, the metric values will be zero. This is correct. Review whether the agent should be deactivated or removed if it has had no usage for an extended period — inactive agents in the registry without usage represent unnecessary attack surface.

5. **For data pipeline delays:**
   If you expect metrics to appear for a recently active agent and they are not showing, wait 4 hours and refresh the Overview page. If metrics still do not appear after 24 hours of confirmed agent usage, open a Microsoft support case.

---

## Issue 5: Pending Requests Card Shows No Requests Despite Known Submissions

**Severity:** High
**Regulatory Impact:** If pending requests are not surfacing, the governance review queue is silently broken. Agents may be publishing without the admin approval that satisfies FINRA 3110 supervision requirements.

**Symptoms:**
- A developer confirms they submitted an agent for approval
- The Pending Requests governance card shows zero requests
- The Requests tab in the Registry is empty

**Resolution Steps:**

1. **Verify the submission completed:**
   Ask the submitting user to confirm the submission workflow completed with a confirmation message (not abandoned mid-wizard). Check whether the agent appears in the All Agents registry in any status (e.g., Draft, Pending, Active). If the agent is already Active, it published without admin approval — treat as a critical issue per Issue 3 response.

2. **Check filters on the Requests tab:**
   Navigate to **Agents > All Agents > Registry > Requests tab**. Confirm no filters are applied that may be hiding requests (e.g., filter by platform or date range). Clear all filters and refresh.

3. **Verify the admin account has request visibility permissions:**
   The signed-in admin must have the Agents management permission. Switch to a Global Administrator account and check whether requests appear.

4. **Wait for request propagation:**
   Newly submitted requests may take up to 15 minutes to appear in the governance card. If the submission was recent, wait 15 minutes and hard-refresh the Overview page.

5. **If requests are genuinely missing:**
   Open a Microsoft support case with the submission timestamps and submitting user UPN. Until resolved, implement a manual confirmation process: require all developers to notify the governance administrator directly upon submission, and use Script 3 (PowerShell) to query pending requests independently of the portal UI.

---

## Issue 6: Ownerless Agents Card Not Updating After Owner Assignment

**Severity:** Medium
**Regulatory Impact:** If the card does not reflect owner assignments, the governance administrator cannot confirm remediation, creating an audit documentation gap.

**Symptoms:**
- Owner assigned via the inline Assign Owner button or Script 4
- Agent still appears on the Ownerless Agents card after assignment
- Agent detail view shows the new owner correctly

**Resolution Steps:**

1. **Wait for card refresh:**
   The governance cards may have a refresh cycle of up to 15–30 minutes. If the agent detail view shows the correct owner, the assignment was successful. Wait 30 minutes and hard-refresh the Overview page before escalating.

2. **Force a page refresh:**
   Navigate away from the Overview page and return, or perform a hard refresh (Ctrl+F5). The card should reflect the updated state.

3. **Use Script 3 for authoritative ownerless agent count:**
   The PowerShell governance queue script queries the API directly and is not subject to portal cache delays. If Script 3 returns `OwnerlessAgentsTotal: 0`, the assignment is confirmed. Use the Script 3 output as your audit evidence if the portal card is lagging.

4. **If owner assignment did not persist:**
   If Script 3 still shows the agent as ownerless after the assignment attempt, the assignment may have failed silently. Re-run Script 4 with the `-WhatIf` flag removed, confirm the Graph API call returns HTTP 200, and re-verify via Script 3.

---

## Issue 7: Inventory Export Produces Empty or Incomplete File

**Severity:** High
**Regulatory Impact:** An incomplete inventory export does not satisfy SEC 17a-4 recordkeeping obligations for the period. Do not substitute an incomplete export as examination evidence.

**Symptoms:**
- Downloaded export CSV contains only headers with no data rows
- Export file contains fewer agents than the Registry shows
- Export file is missing expected fields (e.g., Governance Template, Owner)

**Resolution Steps:**

1. **Check for active filters:**
   Before exporting, navigate to **Agents > All Agents** and confirm all filters are cleared. The export respects any active filters — if a status or platform filter is applied, only filtered agents export.

2. **Verify admin permissions:**
   Export may be restricted to accounts with full Agents management permissions. Confirm you are signed in as Global Administrator or a role with Agents export rights.

3. **Retry the export:**
   Close the admin center tab, re-open, navigate to Agents > All Agents, and retry the export. Portal export operations can occasionally timeout for large inventories.

4. **Use PowerShell Script 2 as authoritative export:**
   If the portal export fails or produces incomplete data, Script 2 (Export-AgentInventory) queries the Graph API directly and is not subject to portal export limitations. The Script 2 output is equally valid as examination evidence — include the script version and execution timestamp in your export log.

5. **For missing fields (Governance Template, Owner):**
   These fields may not populate for agents that were published before governance templates were introduced (early Frontier preview builds). Document this known limitation in your examination evidence package with a note explaining the historical gap and the date from which all new agents include complete fields.

---

## Issue 8: Researcher Computer Use Tab Not Visible

**Severity:** Medium
**Regulatory Impact:** If Computer Use cannot be configured, document the access restriction as a known limitation and re-verify at GA (May 1, 2026).

**Symptoms:**
- Agents > Researcher section is present but has no Computer Use tab
- Researcher section itself is not visible in the Agents sub-navigation

**Root Causes:**

| Root Cause | Probability | Check |
|---|---|---|
| Frontier not enrolled (Researcher with Computer Use is Frontier-only) | High | Verify Frontier enrollment |
| Feature not yet rolled out to tenant's region/ring | Medium | Check Microsoft 365 Roadmap |
| Admin account lacks required permissions | Low | Try Global Administrator account |

**Resolution Steps:**

1. **Verify Frontier enrollment is complete** per Issue 1 resolution steps. Researcher with Computer Use is exclusively a Frontier feature and will not appear without enrollment.

2. **Check feature rollout status:**
   Navigate to **Admin Center > Message Center** and search for "Researcher Computer Use" or "Agent 365 Computer Use" to check whether a feature rollout message has been posted for your tenant. Some Frontier features roll out in rings.

3. **Try with Global Administrator account:**
   Some sub-features within the Agents section may require elevated permissions during the preview period.

4. **Document and defer:**
   If the tab is genuinely unavailable, document this in your governance log with the date of check and a note that configuration will be completed when the feature becomes available. Set a calendar reminder to re-check after GA (May 1, 2026). In the interim, treat Computer Use as implicitly set to No Users and document this in your AI governance policy as a known limitation under OCC 2011-12.

---

## Issue 9: Graph API Calls Returning 403 Forbidden for Agent 365 Endpoints

**Severity:** High
**Regulatory Impact:** Automation failures mean governance operations (inventory export, queue monitoring, owner assignment) must revert to manual processes, increasing human error risk and SLA pressure.

**Symptoms:**
- PowerShell scripts return HTTP 403 Forbidden
- Error message: "Authorization_RequestDenied" or "Insufficient privileges to complete the operation"
- Occurs on `/beta/admin/agentApps` or related endpoints

**Resolution Steps:**

1. **Verify service principal permissions:**
   Navigate to **Entra ID > App Registrations > [your service principal] > API Permissions**. Confirm the following permissions are present and have **admin consent granted** (shown with a green checkmark):
   - `AgentApp.Read.All` (for read operations)
   - `AgentApp.ReadWrite.All` (for write operations — owner assignment, blocking)
   - `Directory.Read.All` (for user/owner validation)
   - `Reports.Read.All` (for analytics data)

2. **Grant missing admin consent:**
   If any permission shows "Not granted" status, click **Grant admin consent for [tenant name]** and confirm. Admin consent must be granted by a Global Administrator — delegated permissions (requiring user sign-in) will not work for service principal automation.

3. **Verify Frontier enrollment is complete:**
   The Agent 365 Graph API endpoints may return 403 if the tenant is not enrolled in Frontier or if the service has not finished provisioning. Confirm enrollment per Issue 1 before re-testing API access.

4. **Check for Conditional Access blocking the service principal:**
   Navigate to **Entra ID > Sign-in Logs**, filter for the service principal's client ID, and check for CA policy-blocked sign-ins. If the service principal is being blocked by a CA policy, work with your Identity team to add the service principal to an appropriate exclusion or CA policy that permits API access.

5. **Verify the API endpoint URL:**
   Confirm the script is using `https://graph.microsoft.com/beta/` (not `/v1.0/` — these endpoints are beta-only). Mismatched endpoint versions return 404 or 403 depending on the operation.

---

## Issue 10: Agent 365 Frontier Licenses Not Appearing in Billing After Enrollment

**Severity:** High
**Regulatory Impact:** Without confirmed license provisioning, governance template auto-assignment will fail and agents cannot be properly activated. Document as a change management tracking item.

**Symptoms:**
- Frontier enrollment toggle shows Enabled
- Billing > Licenses does not show Agent 365 Frontier SKU
- Agent 365 Frontier license count remains at zero

**Resolution Steps:**

1. **Wait for billing propagation:**
   License provisioning after Frontier enrollment can take up to 2 hours to appear in the Billing portal. Wait the full 2 hours before concluding that licenses are missing.

2. **Hard refresh the Billing page:**
   Navigate away from Billing > Licenses and return, or force a hard browser refresh. License counts are sometimes cached in the portal UI.

3. **Verify via PowerShell:**
   Run Script 1 (Frontier Enrollment Check) and review the raw SKU output. The Graph API may reflect the license state faster than the portal UI. If Script 1 returns `Agent365LicenseCount: 25`, the licenses are provisioned even if the portal UI has not caught up.

   ```powershell
   # Quick SKU check
   Connect-MgGraph -Scopes "Organization.Read.All"
   Get-MgSubscribedSku -All | Where-Object { $_.SkuPartNumber -like "*AGENT*" } |
       Select-Object SkuPartNumber, CapabilityStatus, @{N='Total';E={$_.PrepaidUnits.Enabled}}, ConsumedUnits
   ```

4. **Toggle Frontier off and on:**
   Navigate to **Copilot > Settings > User Access > Copilot Frontier**, disable Frontier, wait 5 minutes, re-enable. This re-triggers the provisioning workflow and often resolves license allocation issues.

5. **Open a Microsoft support case:**
   If licenses do not appear within 4 hours of enrollment and the toggle cycle did not resolve the issue, open a support case referencing your tenant ID, enrollment timestamp, and Copilot license SKU. Request confirmation that the Agent 365 Frontier license bundle is correctly tied to your tenant's Copilot subscription.

---

## Escalation Matrix

When issues cannot be resolved using this playbook, escalate according to the following matrix:

| Issue Severity | Initial Escalation | Secondary Escalation | Regulatory Notification |
|---|---|---|---|
| Critical (control failure) | AI Governance Administrator → CISO (same business day) | CISO → Compliance Officer → Technology Risk Committee (next business day) | Assess whether regulatory self-disclosure is required per your incident response policy |
| High (governance gap) | AI Governance Administrator → M365 Global Administrator (same business day) | Open Microsoft support case; escalate to Technology Risk Manager if unresolved in 48 hours | Document in OCC 2011-12 risk register if unresolved beyond planned remediation date |
| Medium (monitoring/reporting gap) | AI Governance Administrator → Microsoft support case (within 2 business days) | Technology Risk Manager notification if unresolved in 5 business days | Document limitation in monitoring runbook for examination transparency |

---

[Back to Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

*Updated: March 2026 | Version: v1.3*
