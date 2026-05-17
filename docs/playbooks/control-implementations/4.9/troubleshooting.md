# Control 4.9 — Troubleshooting: Embedded File Content Governance

**Playbook Type:** Troubleshooting
**Control:** [4.9 — Embedded File Content Governance](../../../controls/pillar-4-sharepoint/4.9-embedded-file-content-governance.md)
**Audience:** M365 Administrators, SharePoint Admins, Compliance Officers
**Estimated Time:** Variable (see individual issue resolution time estimates)
**Last UI Verified:** April 2026

!!! info "Before Troubleshooting Any Issue"
    For every issue in this playbook, determine whether the problem involves a Zone 3 agent serving users across IB-segregated segments. If it does, regardless of the technical issue, escalate to the Compliance team before taking any technical action. The IB bypass limitation (see Control 4.9) means the compliance posture must be assessed before restoring or modifying any embedded file agent serving a cross-IB user population.

## Issue Index

| # | Issue | Severity | Resolution Time |
|---|---|---|---|
| 1 | Agent not appearing in the embedded files filter | Medium | 15–30 minutes |
| 2 | Sensitivity label not appearing on agent Overview tab | High | 30 minutes – 24 hours |
| 3 | Agent is broken — embedded files not loading | Critical | 30 minutes – 4 hours |
| 4 | Container accidentally deleted — agent broken | Critical | 30 minutes – 4 hours (if within recycle bin window) |
| 5 | User can access IB-restricted content via agent | Critical (by design) | Compliance process: 1–5 business days |
| 6 | File upload rejected — size or format error | Low | 15 minutes |
| 7 | Sensitivity label blocking legitimate users from the agent | Medium | 30 minutes – 2 hours |
| 8 | PowerShell container enumeration returns no results | Medium | 30–60 minutes |

---

## Issue 1: Agent Not Appearing in the Embedded Files Filter

**Symptom:** An agent that uses embedded file knowledge sources does not appear when the "Embedded files" filter is applied in M365 Admin Center › Copilot › Agents › All Agents.

**Estimated Resolution Time:** 15–30 minutes

### Cause A — Agent Was Built in Copilot Studio, Not Agent Builder

The embedded files filter applies only to agents created via **Agent Builder** in M365 Copilot. Agents created in **Microsoft Copilot Studio** use a different knowledge source configuration path and are not represented in this filter.

**Resolution:**
1. Verify where the agent was built. Navigate to the agent detail view and review the creation metadata or ask the agent owner.
2. If the agent was built in Copilot Studio and uses file knowledge sources, governance of those files falls under Copilot Studio governance controls (see the applicable governance controls across Pillars 1-3), not Control 4.9.
3. Update the agent inventory (Control 3.1) to correctly record the agent type and applicable control reference.

### Cause B — Agent Uses SharePoint Site Knowledge, Not Uploaded Files

Agents can also be configured to access SharePoint sites as knowledge sources (site-based grounding). This is distinct from uploading files directly into the agent's embedded container. Site-based knowledge sources are governed by SharePoint site access controls, not by Control 4.9.

**Resolution:**
1. Open the agent detail view and review the **Data & tools** tab.
2. If the knowledge source shows a SharePoint site URL rather than individual file names, the agent uses site-based grounding — it correctly does not appear in the embedded files filter.
3. Verify the agent is governed under the appropriate SharePoint site access control (Control 4.3).

### Cause C — Agent Has No Files Currently Uploaded

If the agent was created with the intent to use embedded files but files have not yet been uploaded, the agent may not appear in the filter.

**Resolution:**
1. Open the agent in Agent Builder.
2. Verify whether files have been uploaded to the knowledge source configuration.
3. If files are intended to be uploaded, complete the IB assessment (Portal Walkthrough Section 4) before uploading.

### Cause D — Filter Is Not Applying Correctly (UI Issue)

Occasionally the M365 Admin Center filter may not apply as expected due to UI delays or browser caching.

**Resolution:**
1. Clear browser cache and reload the All Agents page.
2. Try applying the filter again.
3. If the filter still does not show the expected agent after a hard reload, use the PowerShell container enumeration (PowerShell Setup playbook Section 2) to confirm whether the container exists. If the container exists but the agent is not visible in the portal, raise a support case with Microsoft.

---

## Issue 2: Sensitivity Label Not Appearing on Agent Overview Tab

**Symptom:** The Sensitivity label field on the agent's Overview tab shows blank, null, or "None" even though files have been uploaded.

**Estimated Resolution Time:** 30 minutes to 24 hours (depending on label policy propagation)

**Compliance Impact:** HIGH — An unlabeled agent container has no sensitivity-based access restriction and may fail Control 4.9 verification.

### Cause A — Uploaded Files Have No Sensitivity Label

If the files uploaded to the agent are unlabeled, and no default label policy is configured, the container receives no label.

**Resolution:**
1. Identify whether a default sensitivity label policy is configured (Portal Walkthrough Section 6 / PowerShell Setup Section 6).
2. If a default policy is configured, wait up to 24 hours for propagation — then recheck the Overview tab.
3. If no default policy is configured, configure one immediately.
4. Additionally, apply sensitivity labels directly to the source files before uploading them:
   - Open each file in the appropriate Office application (Word, Excel, PowerPoint) or in the browser.
   - Apply the appropriate sensitivity label via the label picker (Home tab › Sensitivity in Office apps, or the Sensitivity button in the browser editor).
   - Re-upload the labeled files to the agent, replacing the unlabeled versions.
5. After re-upload, verify the Overview tab now shows the expected label.

### Cause B — Label Policy Has Not Propagated Yet

Sensitivity label policy changes can take up to 24 hours to fully propagate across the tenant.

**Resolution:**
1. Verify the label policy is configured correctly in Microsoft Purview.
2. Wait 24 hours.
3. Recheck the agent Overview tab.
4. If the label still does not appear after 24 hours, proceed to Cause C.

### Cause C — Label Not Scoped to the Agent Author or Service Account

If the sensitivity label policy does not include the user or service account that performed the file upload, the label may not apply to the uploaded content.

**Resolution:**
1. Review the label policy scope in Microsoft Purview › Information Protection › Label policies.
2. Confirm the policy is scoped to include all users who may upload files to agents (consider using an "All users" scope for the default document label policy if appropriate for your classification taxonomy).
3. After updating the policy scope, wait for propagation and retest.

### Cause D — Agent Was Not Created via Agent Builder (Copilot Studio Agents)

Sensitivity label auto-assignment applies only to agents created via Agent Builder that include embedded files. Copilot Studio agents are not subject to this automatic labeling behavior.

**Resolution:** Verify the agent creation method (see Issue 1 Cause A). If this is a Copilot Studio agent, apply sensitivity labels to the underlying data sources per the Copilot Studio governance controls.

---

## Issue 3: Agent Is Broken — Embedded Files Not Loading

**Symptom:** An agent that previously functioned correctly now shows an error in the Data & tools tab, returns no grounded responses, or shows a missing or empty file list where files were previously present.

**Estimated Resolution Time:** 30 minutes to 4 hours

**Severity:** CRITICAL — Agent is non-functional; content may be inaccessible.

### Cause A — SharePoint Embedded Container Was Deleted

The most common cause of a broken agent is direct deletion of the SharePoint Embedded container outside of the proper agent deletion workflow.

**Diagnosis:**
1. Note the Container ID from the agent inventory or the last successful review of the Data & tools tab.
2. Navigate to SharePoint Admin Center and search for the container by ID.
3. If the container is not found in the active list, check the SharePoint recycle bin.

**Resolution — If Container Is in the Recycle Bin (Within 93 Days of Deletion):**
1. Navigate to SharePoint Admin Center.
2. Access the recycle bin for deleted containers.
3. Restore the container associated with the agent.
4. After restoration, verify the agent's Data & tools tab shows the files correctly.
5. Test the agent with a sample query to confirm grounding is restored.
6. Document the incident: who deleted the container, when, how it was restored, and what process controls help avoid recurrence.
7. Escalate to the relevant team lead for the person who performed the deletion — add "do not delete Declarative Agent containers" to operator training.

**Resolution — If Container Is NOT in the Recycle Bin (Beyond 93 Days or Permanently Deleted):**
1. The container and its files cannot be recovered.
2. The agent must be rebuilt. Retrieve the original source files from their origin locations (document management system, SharePoint sites, local storage).
3. Repeat the IB assessment and file upload process per Portal Walkthrough Section 4.
4. Update the agent inventory (Control 3.1) with the new Container ID.
5. Investigate the permanent deletion event via the Microsoft Purview audit log and raise a support case with Microsoft if the deletion cannot be explained.

### Cause B — Agent Has Exceeded the 20-File Limit

If an administrator or user attempts to add more than 20 files to an agent, additional files may not be accepted, which could manifest as an incomplete or broken file listing.

**Resolution:**
1. Review the current file count in the Data & tools tab.
2. If the count is at or near 20, remove less critical files to stay within the limit.
3. Consider restructuring the agent's knowledge approach: consolidate content into fewer files, or split the agent into multiple agents each covering a smaller file set.

### Cause C — File Format or Size Changed Retrospectively

Files that were previously valid may become invalid if they are updated to exceed size limits or converted to unsupported formats.

**Resolution:**
1. Review each file in the Data & tools tab for error indicators.
2. For any file showing an error, verify it still meets the format and size requirements.
3. Replace oversized or reformatted files with compliant versions.

---

## Issue 4: Container Accidentally Deleted — Agent Broken

**Symptom:** A SharePoint administrator or script has deleted a container associated with an active agent, and the agent is now broken.

**Estimated Resolution Time:** 30 minutes to 4 hours

**Severity:** CRITICAL

This issue is a specific and actionable instance of Issue 3 Cause A. Refer to the resolution steps in Issue 3, then also complete the following process controls:

### Additional Process Controls After Recovery

1. **Incident report:** File an internal IT incident report documenting the unauthorized deletion.
2. **Access review:** Review who has SharePoint Admin access and whether all administrators have been trained on the "do not delete Declarative Agent containers" rule.
3. **Operational runbook update:** Add an explicit warning to your SharePoint Admin operational runbooks: containers with application name "Declarative Agent" must never be deleted directly. Use the M365 Admin Center agent deletion workflow for agent retirement.
4. **PowerShell guard:** Consider adding a guard to any automated SharePoint cleanup scripts that checks for the "Declarative Agent" application name and skips or alerts before any container deletion:

```powershell
# Guard pattern — add to any cleanup script that deletes SharePoint containers
function Remove-ContainerSafely {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ContainerId
    )

    $container = Get-PnPContainer -Identity $ContainerId

    if ($container.ApplicationName -eq "Declarative Agent") {
        Write-Error "BLOCKED: Container $ContainerId is a Declarative Agent container. Do NOT delete directly. Use M365 Admin Center agent deletion workflow. Exiting."
        return
    }

    # Proceed with deletion only for non-agent containers
    Remove-PnPContainer -Identity $ContainerId
}
```

---

## Issue 5: User Can Access IB-Restricted Content via Agent

**Symptom:** A user in an IB-separated business segment has received a response from an agent that is grounded in content that should be restricted by Information Barriers.

**Estimated Resolution Time:** Compliance process: 1–5 business days

**Severity:** CRITICAL (by design — this is the expected behavior of the platform limitation)

!!! danger "This Is Expected Platform Behavior — Not a Misconfiguration"
    Microsoft Purview Information Barriers are NOT enforced on SharePoint Embedded containers. A user receiving IB-restricted content via an agent is the confirmed and documented behavior described in Control 4.9. This is NOT a bug to be fixed at the platform level by your team.

    **Immediate actions upon discovery of an IB bypass incident:**

### Step 5.1 — Contain the Exposure

1. **Immediately restrict access to the agent** for all users outside the IB-permitted segment:
   - Navigate to: M365 Admin Center › Copilot › Agents › All Agents › [Agent]
   - Modify the agent sharing settings to remove access for the IB-separated user(s) or their segment.
2. If the agent is a Zone 3 enterprise agent with broad access, consider **temporarily disabling the agent** until the IB assessment and compliance review is complete.

### Step 5.2 — Assess the Exposure

1. Determine what content was accessed: Review the agent interaction audit logs (Microsoft Purview › Audit) for the date range and user(s) involved.
2. Determine whether the accessed content constitutes MNPI, deal-sensitive information, restricted research, or other IB-regulated content categories.
3. Brief the Chief Compliance Officer and General Counsel.

### Step 5.3 — Determine Whether Regulatory Notification Is Required

1. Work with Legal and Compliance to assess whether the IB breach:
   - Constitutes a violation requiring FINRA or SEC notification under applicable rules
   - Triggers customer notification obligations under GLBA or state privacy laws
   - Requires disclosure in SOX attestations

2. Do not make any regulatory notification decisions without Legal and Compliance sign-off.

### Step 5.4 — Root Cause and Remediation

Determine which governance control failed:

| Root Cause | Remediation |
|---|---|
| Zone 3 agent deployed without IB prohibition in effect | Enforce Zone 3 prohibition immediately. Retire or restrict all Zone 3 agents with embedded files pending compliance review. |
| Zone 2 agent deployed without IB assessment | Complete IB assessment for all Zone 2 agents. Restrict any agent where IB-restricted content is present. |
| Zone 3 exception signed off but scope was incorrectly assessed | Revoke the exception. Reassess the user population scope. Require re-sign-off with corrected scope documentation. |
| Agent was shared with a user outside the originally assessed scope | Audit all agent sharing changes since last IB assessment. Restrict sharing. Update IB assessment. |

### Step 5.5 — Update Examination File

Document the incident in the examination-ready compliance file:
- Date of discovery
- Nature of exposed content
- Users involved
- Immediate containment actions
- Legal/regulatory assessment
- Remediation actions
- Changes to governance controls to prevent recurrence

This documentation is essential if the incident is identified by a FINRA or SEC examiner.

---

## Issue 6: File Upload Rejected — Size or Format Error

**Symptom:** When uploading a file to an agent in Agent Builder, the file is rejected or does not appear in the Data & tools tab.

**Estimated Resolution Time:** 15 minutes

### Cause A — File Exceeds Size Limit

| Format | Limit |
|---|---|
| .docx, .pptx, .pdf | 512 MB |
| .doc, .ppt, .xls, .xlsx, .txt, .csv | 150 MB |

**Resolution:**
1. Check the file size.
2. If it exceeds the limit, reduce the file size by:
   - Compressing images within the document
   - Splitting the document into multiple smaller files (note: maximum 20 files per agent)
   - Removing non-essential content
3. Re-upload the reduced-size file.

### Cause B — Unsupported File Format

Only the following formats are accepted: `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.pdf`, `.txt`, `.csv`

**Resolution:**
1. Convert the file to a supported format. Recommended conversions:
   - `.pages` → `.docx` (via Pages export or Word import)
   - `.odt` → `.docx`
   - `.csv` → `.xlsx`
   - Other formats → `.pdf` (via print-to-PDF)
2. Apply a sensitivity label to the converted file before uploading.
3. Upload the converted file.

### Cause C — Agent Has Reached the 20-File Limit

An agent cannot have more than 20 embedded files.

**Resolution:**
1. Review the current files in the agent's Data & tools tab.
2. Determine whether any existing files can be consolidated or retired.
3. Remove a file before uploading the new one.
4. Consider whether the content scope requires a second agent.

---

## Issue 7: Sensitivity Label Blocking Legitimate Users

**Symptom:** A user who should have access to an agent is being blocked, receiving an access denied message or seeing no response due to the agent's sensitivity label restrictions.

**Estimated Resolution Time:** 30 minutes to 2 hours

### Diagnosis

1. Navigate to: M365 Admin Center › Copilot › Agents › [Agent] › Overview tab
2. Record the sensitivity label applied to the agent.
3. Check the label's protection settings in Microsoft Purview to understand the extract rights requirement.
4. Verify whether the affected user has extract rights for this label.

### Resolution A — User Is Missing the Required License or Group Membership

If the label requires membership in a specific Microsoft Entra ID group (for scoped label policies):
1. Add the user to the appropriate group, or
2. Adjust the label policy scope if the user is a legitimate agent user who was inadvertently excluded.

### Resolution B — Label Is More Restrictive Than Intended

If the agent's files were labeled with a more restrictive label than required:
1. Re-label the files with the appropriate sensitivity label.
2. Re-upload the files.
3. Verify the Overview tab reflects the updated label.

!!! warning "Label Down-Classification Requires Compliance Review"
    Reducing the sensitivity classification of embedded files (down-classifying) requires review by the Information Security or Compliance team. Do not reduce labels to resolve access issues without proper authorization.

### Resolution C — Sensitivity Label Is Correctly Blocking an Unauthorized User

If investigation confirms the user should not have access to the labeled content, the label is functioning as intended. Do not attempt to remove or reduce the label.

1. Review whether the user should have access to this agent at all.
2. If the user legitimately needs the agent's functionality, determine whether a different agent with less restricted content can serve their use case.
3. Document the outcome.

---

## Issue 8: PowerShell Container Enumeration Returns No Results

**Symptom:** `Get-PnPContainer -IncludeAll` returns an empty result set when filtering for "Declarative Agent", even though agents with embedded files are visible in the M365 Admin Center.

**Estimated Resolution Time:** 30–60 minutes

### Cause A — Module Version Is Outdated

SharePoint Embedded container management requires a recent version of PnP.PowerShell.

**Resolution:**
```powershell
# Check current version
Get-Module -ListAvailable PnP.PowerShell | Select-Object Name, Version

# Update to latest version if below 4.x
Update-Module -Name PnP.PowerShell -Force

# Verify update
Get-Module -ListAvailable PnP.PowerShell | Select-Object Name, Version
```

### Cause B — Incorrect Admin URL or Authentication Context

The `Get-PnPContainer` command requires connection to the SharePoint Admin site, not a regular site collection.

**Resolution:**
```powershell
# Verify current connection context
Get-PnPConnection

# Reconnect to the tenant admin URL (not a site URL)
$TenantAdminUrl = "https://YOURTENANT-admin.sharepoint.com"
Connect-PnPOnline -Url $TenantAdminUrl -Interactive

# Retry enumeration
Get-PnPContainer -IncludeAll | Where-Object { $_.ApplicationName -eq "Declarative Agent" }
```

### Cause C — Required API Permissions Not Granted to the Service Principal

If using service principal authentication, the App Registration may be missing required permissions.

**Resolution:**
1. Navigate to: **Azure Portal › Entra ID › App registrations › [Your App] › API permissions**
2. Verify the following permissions are granted with admin consent:
   - `SharePoint: Sites.Read.All` (Application)
   - `SharePoint: TermStore.Read.All` (Application)
3. If permissions are missing, add them and grant admin consent.
4. Wait 5–10 minutes for permission propagation.
5. Re-authenticate and retry the command.

### Cause D — No Declarative Agent Containers Exist in the Tenant

If no agents with embedded files have been created in the tenant, the filter correctly returns no results.

**Resolution:**
1. Verify in M365 Admin Center that at least one agent with embedded files exists (apply the embedded files filter).
2. If no agents exist, no containers should exist — results are correct. No action required.
3. If agents exist but containers are not returned by PowerShell after resolving other causes, open a Microsoft support case.

---

## Escalation Reference

| Issue Type | Primary Escalation | Secondary Escalation |
|---|---|---|
| IB breach incident | Chief Compliance Officer | General Counsel, CISO |
| Container accidentally deleted (unrecoverable) | CISO, Compliance | Microsoft Support |
| Sensitivity label not applying after 24 hours | M365 Tenant Administrator | Microsoft Support (raise ticket) |
| Unexpected IB enforcement on embedded files (anomalous) | Microsoft Support | Compliance (document anomaly) |
| PowerShell enumeration fails after troubleshooting | Microsoft Support — SharePoint Embedded | Internal M365 admin team |

---
[Back to Control 4.9](../../../controls/pillar-4-sharepoint/4.9-embedded-file-content-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
