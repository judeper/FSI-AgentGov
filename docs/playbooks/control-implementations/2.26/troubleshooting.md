# Playbook: Troubleshooting — Control 2.26

**Control:** 2.26 — Entra Agent ID: Identity Governance for Agents
**Playbook Type:** Troubleshooting
**Scope:** Common implementation issues, configuration failures, and diagnostic procedures for Entra Agent ID identity governance

---

!!! info "Preview Feature — Microsoft Entra Agent ID"
    Because Entra Agent ID is in **PREVIEW** via the Frontier program, some behaviors described in this playbook may change as the feature evolves toward general availability. If a troubleshooting step produces unexpected results or the UI has changed, consult the [Microsoft Entra Agent ID documentation on Microsoft Learn](https://learn.microsoft.com/entra/identity/agent-id) for the most current guidance.

    When filing support cases for issues with this feature, reference the **Frontier program** and **Entra Agent ID Preview** in your support ticket so the case is routed to the correct team.

!!! note "Before Troubleshooting — Quick Checklist"
    Before investigating any specific issue, confirm these prerequisites are met:
    - [ ] Frontier enrollment is confirmed active (M365 Admin Center > Copilot > Settings > Frontier shows "Enrolled")
    - [ ] Your account has the required Entra roles: at minimum Identity Governance Administrator and Application Administrator
    - [ ] Required licenses are assigned: Entra ID Governance (P2 or add-on) and Microsoft 365 E3/E5 with Frontier
    - [ ] Browser cache has been cleared (many Frontier preview UI issues resolve after a hard refresh or private browsing session)

---

## Issue 1: Agent Identities Not Visible in Entra Admin Center

### Symptom
After enrolling in Frontier, the **Agent identities** blade does not appear under **Applications** in the Entra admin center. Administrators navigating to Applications see only Enterprise applications, App registrations, and Application proxy — no Agent identities entry.

### Cause 1A: Frontier Enrollment Still Propagating

**Diagnosis:**
1. Navigate to **M365 Admin Center > Copilot > Settings > Frontier**.
2. Check the enrollment status timestamp.
3. If enrollment completed less than one hour ago, this is expected propagation delay.

**Resolution:**
Wait up to one hour after Frontier enrollment completes. Clear browser cache and reload the Entra admin center in a private/incognito window before attempting again.

```powershell
# Verify Frontier enrollment status via PowerShell
# (No direct Graph API for Frontier status; use admin center UI)
# Instead, verify Graph API beta access which indicates Frontier is active:
Connect-MgGraph -Scopes "Application.Read.All"
try {
    $testQuery = Invoke-MgGraphRequest -Method GET `
        -Uri "https://graph.microsoft.com/beta/servicePrincipals?`$filter=servicePrincipalType eq 'Agent'&`$top=1"
    Write-Host "Agent identity API endpoint accessible. Frontier is active." -ForegroundColor Green
} catch {
    Write-Warning "Agent identity API not accessible: $($_.Exception.Message)"
    Write-Warning "Frontier enrollment may not be complete or may require additional propagation time."
}
```

---

### Cause 1B: Frontier Enrollment Did Not Complete

**Diagnosis:**
1. Navigate to **M365 Admin Center > Copilot > Settings > Frontier**.
2. If the status shows **Not Enrolled**, **Pending**, or if the Frontier section is absent, enrollment was not completed or failed.

**Resolution:**
1. Re-attempt Frontier enrollment: M365 Admin Center > Copilot > Settings > Frontier > Enroll.
2. Ensure you are completing the enrollment as a **Global Administrator** — other admin roles cannot complete Frontier enrollment.
3. If the Frontier option is not visible in the Copilot settings panel, verify that your Microsoft 365 subscription includes a plan that supports Frontier (generally M365 E3 or E5 with Copilot add-on, or M365 Copilot license).

---

### Cause 1C: User Role Missing Agent Identity Read Permission

**Diagnosis:**
1. Verify the administrator's Entra role assignments: Entra admin center > Users > [User] > Assigned roles.
2. Confirm the user has one of: Global Administrator, Application Administrator, or Identity Governance Administrator.

**Resolution:**
Assign the appropriate Entra role to the user. For least-privilege access to agent identities only, use Identity Governance Administrator combined with Application Administrator.

---

### Cause 1D: No Agents Deployed Yet

**Diagnosis:**
The Agent identities blade may be present but display an empty state ("No agents found") if no Copilot Studio agents have been deployed in the tenant.

**Resolution:**
This is not an error condition. Deploy a test Copilot Studio agent from Copilot Studio ([https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)) and allow up to 15 minutes for the agent identity to appear in the Entra Agent identities blade. Then re-verify.

---

## Issue 2: Lifecycle Workflow Not Triggering

### Symptom
The sponsor departure lifecycle workflow was created and enabled, but when a test sponsor's account is deactivated, the workflow does not appear in the workflow execution history, the notification is not sent, and the agent identity is not disabled.

### Cause 2A: HR Connector Not Connected — Trigger Relies on Manual Signal

**Diagnosis:**
Entra lifecycle workflows use HR connector signals (Workday, SAP SuccessFactors, or similar) to detect leavers accurately and promptly. Without an HR connector, the only trigger available is manual account deactivation in Entra, and there may be a processing delay.

1. Navigate to **Entra admin center > Identity Governance > Lifecycle workflows**.
2. Select the sponsor departure workflow.
3. Select **Trigger details**.
4. Verify whether an HR connector is configured as the trigger source.

**Resolution:**
If an HR connector is not yet configured:

- **Short-term workaround:** Disable the sponsor's account in Entra manually when a departure occurs, then wait for the workflow to process (up to 2 hours after account deactivation).
- **Long-term fix:** Configure the Entra HR inbound provisioning connector for your HR system (Workday, SAP SuccessFactors, or BambooHR). Refer to: [Microsoft Learn — HR inbound provisioning](https://learn.microsoft.com/entra/identity/app-provisioning/plan-cloud-hr-provision). Once configured, leaver events will trigger automatically when the HR system marks the user as inactive.

---

### Cause 2B: Workflow Trigger Conditions Not Met

**Diagnosis:**
Lifecycle workflow triggers have specific conditions that must be met precisely. For a leaver trigger, the user must be marked as a leaver in the way the trigger condition expects.

1. Navigate to **Identity Governance > Lifecycle workflows > [Sponsor Departure Workflow]**.
2. Select **Trigger configuration**.
3. Review the exact trigger condition defined (e.g., "employeeLeaveDateTime is in the past X days," or "accountEnabled equals false").

**Resolution:**
Ensure the trigger condition matches the actual mechanism used to signal departure in your environment. Common mismatches:

| Configured Trigger | Actual Signal | Fix |
|---|---|---|
| `employeeLeaveDateTime` based | HR connector not providing this attribute | Switch trigger to `accountEnabled eq false` as interim fix |
| `accountEnabled eq false` | Account disabled but in a guest state, not a member | Confirm the sponsor account type is "Member" not "Guest" |
| `department` attribute change | HR connector uses a different attribute name | Check the exact attribute name in your HR connector mapping |

```powershell
# Check if a test user has the expected leaver attribute populated
$testSponsorId = "test-sponsor-object-id-here"
$userDetail = Get-MgUser -UserId $testSponsorId `
    -Property "id,displayName,accountEnabled,employeeLeaveDateTime,department"

$userDetail | Select-Object DisplayName, AccountEnabled, EmployeeLeaveDateTime, Department
```

---

### Cause 2C: Workflow Is Disabled

**Diagnosis:**
1. Navigate to **Identity Governance > Lifecycle workflows**.
2. Locate the sponsor departure workflow.
3. Check the **Is Enabled** column. If it shows "No" or "Disabled," the workflow will not trigger.

**Resolution:**
1. Select the workflow.
2. Select **Enable workflow**.
3. Confirm the workflow is now listed as enabled.

---

### Cause 2D: Workflow Processing Delay (Normal Behavior)

**Diagnosis:**
Lifecycle workflows do not trigger instantaneously. Microsoft's SLA for lifecycle workflow processing is typically within 2 hours of the trigger condition being met.

**Resolution:**
Wait at least 2 hours after triggering the test departure condition before concluding the workflow has failed. Check the workflow execution history after the wait period.

```powershell
# Check workflow execution history to see if a run was queued or completed
$workflowId = "your-workflow-id-here"
$runs = Get-MgIdentityGovernanceLifecycleWorkflowRun -WorkflowId $workflowId -All |
        Sort-Object StartedDateTime -Descending | Select-Object -First 5

$runs | Select-Object Id, RunStatus, StartedDateTime, CompletedDateTime, ProcessedCount, FailedCount |
    Format-Table -AutoSize

# If a run appears but shows Failed tasks, check individual task details:
if ($runs.Count -gt 0) {
    $latestRun = $runs[0]
    $tasks = Get-MgIdentityGovernanceLifecycleWorkflowRunTaskReport `
        -WorkflowId $workflowId -RunId $latestRun.Id -All

    $tasks | Select-Object DisplayName, Status, FailureReason | Format-Table -AutoSize
}
```

---

## Issue 3: Access Package Assignment Not Working for Agent Identity

### Symptom
When attempting to assign an agent identity to an access package (either via the Entra portal or PowerShell), the assignment fails with an error, or the agent identity does not appear in the user/principal search when creating an assignment.

### Cause 3A: Agent Identity Type Not Supported in Entitlement Management (Preview Limitation)

**Diagnosis:**
During Frontier preview, not all agent identity types may be supported as valid targets for entitlement management access package assignments. Service principals with a `servicePrincipalType` of "Agent" must be explicitly supported by the entitlement management engine.

**Resolution:**
1. Verify the agent's service principal type via PowerShell:

    ```powershell
    $agentId = "your-agent-sp-id-here"
    $sp = Get-MgBetaServicePrincipal -ServicePrincipalId $agentId `
        -Property "id,displayName,servicePrincipalType,tags"
    Write-Host "Service Principal Type: $($sp.ServicePrincipalType)"
    Write-Host "Tags: $($sp.Tags -join ', ')"
    ```

2. If `ServicePrincipalType` is not "Agent" (e.g., if it shows "Application"), the agent may not yet have been classified by Frontier as an agent identity. In this case, check whether the agent was deployed after Frontier enrollment was activated. Agents deployed before Frontier activation may not have the agent identity classification applied.

3. If the issue persists, this may be a Frontier preview limitation. Document the limitation and implement a compensating control: manually document the access package intent in the agent's Properties/description field in Entra, and enforce the access governance policy through manual review until the assignment mechanism is supported for the agent's identity type.

---

### Cause 3B: Catalog Does Not Include the Required Resource

**Diagnosis:**
The access package is configured correctly, but the resource the agent needs to access (e.g., a specific SharePoint site) has not been added to the **AI Agent Resources** catalog.

**Resolution:**
1. Navigate to **Identity Governance > Entitlement management > Catalogs > AI Agent Resources > Resources**.
2. Confirm the target resource is listed.
3. If not, select **Add resources** and add the required resource to the catalog.
4. Rebuild the access package to include the newly added resource.

---

### Cause 3C: Access Package Policy Does Not Allow Service Principal Assignments

**Diagnosis:**
The access package's request policy may be configured to allow only "users" or "members" to request access, which excludes service principals (including agent identities).

**Resolution:**
1. Navigate to the access package > **Policies** > select the policy > **Edit**.
2. In the **Users who can request access** section, confirm that the policy allows service principals or non-user principals, or that the assignment is being made directly by an administrator (not through a self-service request).
3. For administrative assignments (where an admin is assigning the access package to an agent, not the agent requesting it), use the **Assignments > Add assignment** pathway rather than the request pathway.

---

## Issue 4: Sponsor Reassignment Notification Not Sent

### Symptom
The lifecycle workflow ran and completed, the agent was disabled correctly, but the AI Governance Lead or department head did not receive the notification email about the sponsor departure.

### Cause 4A: Notification Task Target Is Misconfigured

**Diagnosis:**
1. Navigate to **Identity Governance > Lifecycle workflows > [Sponsor Departure Workflow] > Tasks**.
2. Locate the notification task (Task 1).
3. Confirm the recipient is set to the correct role or user (AI Governance Lead or equivalent).
4. Check whether the recipient is a distribution group — some lifecycle workflow notification tasks require individual user accounts, not distribution groups.

**Resolution:**
Update the notification task to target a specific named user account (the AI Governance Lead), or ensure the distribution group is configured to receive external/automated messages. If using a shared mailbox as the governance lead inbox, confirm the mailbox is not blocking automated messages.

---

### Cause 4B: Email Deliverability — Message Blocked by Anti-Spam

**Diagnosis:**
The notification was generated by the workflow (workflow shows task success) but the email was quarantined or blocked by the recipient's spam filter or organization's email security gateway.

**Resolution:**
1. Check the AI Governance Lead's spam/quarantine folder.
2. If the organization uses Microsoft Defender for Office 365, check the message trace:
    - M365 Admin Center > Exchange > Mail flow > Message trace
    - Search for messages from the Entra service (sender will be an Entra notification address) to the AI Governance Lead.
3. Add the Entra notification sender address to the allow list if messages are being quarantined.

---

### Cause 4C: Workflow Task Shows Failed Status

**Diagnosis:**
```powershell
# Check specific task failure reason in the latest workflow run
$workflowId = "your-workflow-id-here"
$latestRun = Get-MgIdentityGovernanceLifecycleWorkflowRun -WorkflowId $workflowId -All |
             Sort-Object StartedDateTime -Descending | Select-Object -First 1

$tasks = Get-MgIdentityGovernanceLifecycleWorkflowRunTaskReport `
    -WorkflowId $workflowId -RunId $latestRun.Id -All

$failedTasks = $tasks | Where-Object { $_.Status -ne "Completed" }
$failedTasks | Select-Object DisplayName, Status, FailureReason | Format-Table -AutoSize
```

**Resolution:**
Review the `FailureReason` field for each failed task. Common reasons and resolutions:

| Failure Reason | Resolution |
|---|---|
| `Target user not found` | The recipient user account has been deleted or deactivated; update the task target to an active account |
| `Insufficient permissions` | The lifecycle workflow service principal lacks permissions to send email; review the workflow's service principal role assignments |
| `Message size limit exceeded` | The notification template is too large; simplify the email template in the task configuration |
| `Throttled` | The Graph API was throttled; re-run the workflow or wait and verify the next scheduled execution |

---

## Issue 5: Access Certification Review Not Appearing for Zone 3 Agents

### Symptom
A quarterly access certification campaign was created, but when the review period opens, some Zone 3 agents are not included in the certifier's review queue.

### Cause 5A: Agent Not in Review Scope

**Diagnosis:**
The access review scope may be too narrow and may not include all Zone 3 agents.

1. Navigate to **Identity Governance > Access reviews > [Zone 3 Quarterly Review] > Review definition**.
2. Check the **Scope** configuration: what principals are included?
3. If the scope is defined by group membership, confirm all Zone 3 agents are members of the relevant group.
4. If the scope is defined by access package assignment, confirm all Zone 3 agents have active access package assignments (agents with no current assignment will not appear in a scope filtered to assigned principals).

**Resolution:**
Update the review scope to include all Zone 3 agent identities, or ensure all Zone 3 agents have active access package assignments before the review period opens.

---

### Cause 5B: Certifier Has Not Received Notification

**Diagnosis:**
The review has started but the certifier (sponsor or Compliance Officer) has not received the review notification email and is therefore unaware the review requires action.

**Resolution:**
1. Navigate to the active access review.
2. Select **Send reminders** to manually trigger a reminder notification to all pending certifiers.
3. Ensure certifiers know to check their **MyAccess portal** ([https://myaccess.microsoft.com](https://myaccess.microsoft.com)) as an alternative to email-based review.
4. For future cycles, configure review reminders in the access review settings: periodic reminders at 7 days and 3 days before the review deadline.

---

## General Diagnostic Commands

```powershell
# Full diagnostic snapshot for Control 2.26 troubleshooting

Write-Host "=== Control 2.26 Diagnostic Snapshot ===" -ForegroundColor Cyan
Write-Host "Run at: $(Get-Date -Format 'o')" -ForegroundColor Gray

# 1. Check Graph API connectivity
Write-Host "`n[1] Graph API Connectivity:" -ForegroundColor Yellow
try {
    $context = Get-MgContext
    Write-Host "  Connected as: $($context.Account)" -ForegroundColor Green
    Write-Host "  Tenant: $($context.TenantId)" -ForegroundColor Green
    Write-Host "  Scopes: $($context.Scopes -join ', ')" -ForegroundColor Green
} catch {
    Write-Warning "  Not connected to Microsoft Graph. Run Connect-MgGraph first."
}

# 2. Test agent identity API access (Frontier indicator)
Write-Host "`n[2] Agent Identity API Access (Frontier):" -ForegroundColor Yellow
try {
    $agentTest = Invoke-MgGraphRequest -Method GET `
        -Uri "https://graph.microsoft.com/beta/servicePrincipals?`$filter=servicePrincipalType eq 'Agent'&`$top=1"
    $count = $agentTest.value.Count
    Write-Host "  API accessible. Sample agent count in response: $count" -ForegroundColor Green
} catch {
    Write-Warning "  Agent identity API not accessible: $($_.Exception.Message)"
}

# 3. Entitlement management catalog check
Write-Host "`n[3] Entitlement Management Catalog:" -ForegroundColor Yellow
try {
    $catalog = Get-MgEntitlementManagementAccessPackageCatalog `
        -Filter "displayName eq 'AI Agent Resources'"
    if ($catalog) {
        Write-Host "  'AI Agent Resources' catalog found (ID: $($catalog.Id))" -ForegroundColor Green
    } else {
        Write-Warning "  'AI Agent Resources' catalog NOT found. Create it via Portal Walkthrough — Section 3."
    }
} catch {
    Write-Warning "  Error querying catalogs: $($_.Exception.Message)"
}

# 4. Lifecycle workflow status
Write-Host "`n[4] Lifecycle Workflows:" -ForegroundColor Yellow
try {
    $workflows = Get-MgIdentityGovernanceLifecycleWorkflow -All
    if ($workflows.Count -gt 0) {
        $workflows | ForEach-Object {
            $status = if ($_.IsEnabled) { "ENABLED" } else { "DISABLED" }
            $color  = if ($_.IsEnabled) { "Green" } else { "Red" }
            Write-Host "  $($_.DisplayName): $status" -ForegroundColor $color
        }
    } else {
        Write-Warning "  No lifecycle workflows found. Create the sponsor departure workflow via Portal Walkthrough — Section 5."
    }
} catch {
    Write-Warning "  Error querying lifecycle workflows: $($_.Exception.Message)"
}

# 5. Access reviews status
Write-Host "`n[5] Access Review Campaigns:" -ForegroundColor Yellow
try {
    $reviews = Get-MgIdentityGovernanceAccessReviewScheduleDefinition -All
    if ($reviews.Count -gt 0) {
        $reviews | ForEach-Object {
            Write-Host "  $($_.DisplayName): $($_.Status)" -ForegroundColor Gray
        }
    } else {
        Write-Warning "  No access review campaigns found. Create the Zone 3 quarterly review via Portal Walkthrough — Section 6."
    }
} catch {
    Write-Warning "  Error querying access reviews: $($_.Exception.Message)"
}

Write-Host "`n=== Diagnostic Complete ===" -ForegroundColor Cyan
```

---

## Escalation Path

If issues cannot be resolved using this playbook:

1. **Internal escalation:** AI Governance Lead > Information Security > M365 Administrator
2. **Microsoft Support:** File a support case via the M365 Admin Center > Support > New service request. Reference: "Frontier program," "Entra Agent ID Preview," and the specific symptom.
3. **Microsoft Frontier Feedback:** Use the Frontier feedback mechanism in the M365 Admin Center to report preview-specific bugs. Include the exact error message, tenant ID, and reproduction steps.
4. **Microsoft Learn documentation:** [https://learn.microsoft.com/entra/identity/agent-id](https://learn.microsoft.com/entra/identity/agent-id) — check for updated guidance as this feature evolves.

---

[Back to Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

*Updated: March 2026 | Version: v1.3*
