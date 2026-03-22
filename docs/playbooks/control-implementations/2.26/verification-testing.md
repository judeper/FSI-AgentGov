# Playbook: Verification Testing — Control 2.26

**Control:** 2.26 — Entra Agent ID: Identity Governance for Agents
**Playbook Type:** Verification Testing
**Estimated Time:** 2–3 hours (full test suite); 45 minutes (smoke test for individual criteria)
**Prerequisites:** Portal Walkthrough playbook completed; a non-production or designated test agent identity available; Frontier enrollment active; test user accounts available to simulate sponsor departure

---

!!! info "Preview Feature — Microsoft Entra Agent ID"
    All verification tests in this playbook depend on **Microsoft Entra Agent ID being active via Frontier enrollment**. If Frontier is not enrolled or the Agent identities blade is not visible, begin with Test 1.1 (Frontier Enrollment Verification) and resolve that prerequisite before proceeding to other tests.

!!! note "Test Environment Recommendation"
    Where possible, execute verification tests against a **designated test agent identity** rather than production agents. The sponsor departure simulation test (Test 4) in particular involves disabling a user account; this must be performed against test accounts only. Create a test agent and test sponsor account for use in this playbook.

---

## Test Matrix Overview

| Test ID | Test Name | Control Criteria Verified | Zone Applicability | Exam Evidence? |
|---|---|---|---|---|
| 1.1 | Frontier Enrollment Verification | Criterion 1 | All Zones | Yes |
| 1.2 | Agent Identities Blade Visibility | Criterion 1 | All Zones | Yes |
| 2.1 | Sponsor Assignment Confirmation | Criterion 2 | Zone 2, Zone 3 | Yes |
| 2.2 | Zero-Sponsor Gap Scan | Criterion 2 | Zone 2, Zone 3 | Yes |
| 3.1 | Access Package Assignment Verification | Criterion 3 | Zone 3 (required), Zone 2 (recommended) | Yes |
| 3.2 | Access Package Expiration Verification | Criterion 4 | Zone 2, Zone 3 | Yes |
| 3.3 | No Perpetual Access Verification | Criterion 4 | Zone 3 | Yes |
| 4.1 | Lifecycle Workflow Existence Verification | Criterion 5 | Zone 2, Zone 3 | Yes |
| 4.2 | Sponsor Departure Simulation | Criterion 5 | Zone 2, Zone 3 | Yes |
| 5.1 | Access Certification Campaign Verification | Criterion 6 | Zone 3 | Yes |
| 5.2 | Certification Completion Evidence Export | Criterion 6 | Zone 3 | Yes |
| 6.1 | Expired Access Active-Agent Scan | Criterion 7 | Zone 2, Zone 3 | Yes |
| 7.1 | SIEM Log Forwarding Confirmation | Criterion 8 | Zone 3 | Yes |

---

## Test 1: Frontier Enrollment and Entra Agent ID Availability

### Test 1.1: Frontier Enrollment Verification

**Purpose:** Confirm that the Microsoft 365 Frontier program is actively enrolled, which is a prerequisite for all Entra Agent ID functionality.

**Procedure:**

1. Navigate to the **Microsoft 365 Admin Center**: [https://admin.microsoft.com](https://admin.microsoft.com)
2. Select **Copilot** > **Settings**.
3. Locate the **Frontier** section.
4. Verify that the enrollment status shows **Enrolled** (not "Not enrolled" or "Pending").

**Pass Criteria:** Frontier enrollment status displays as "Enrolled" with an active enrollment date.

**Fail Criteria:** Status shows not enrolled, pending, or the Frontier section is absent.

**Evidence to Capture:** Screenshot of Frontier enrollment status page showing "Enrolled" status and enrollment date.

**If Failing:** Enroll in Frontier per the Portal Walkthrough playbook — Section 1. Allow up to one hour for propagation before re-running this test.

---

### Test 1.2: Agent Identities Blade Visibility

**Purpose:** Confirm that the Entra Agent ID blade is accessible, indicating Frontier enrollment has fully propagated.

**Procedure:**

1. Navigate to the **Microsoft Entra admin center**: [https://entra.microsoft.com](https://entra.microsoft.com)
2. In the left navigation, expand **Applications**.
3. Confirm the presence of **Agent identities** in the submenu.
4. Select **Agent identities**.
5. Verify that the blade loads and displays agent identity records (or an empty state with "No agents found" if no agents have been deployed yet).

**Pass Criteria:** The Agent identities blade is visible and loads without errors.

**Fail Criteria:** The Agent identities blade is absent from the Applications menu, or the blade returns an error.

**Evidence to Capture:** Screenshot of the Entra admin center Applications menu showing Agent identities, and a screenshot of the Agent identities blade contents.

---

## Test 2: Sponsor Assignment

### Test 2.1: Sponsor Assignment Confirmation for Test Agent

**Purpose:** Confirm that a known test agent has a correctly assigned sponsor reflected in Entra.

**Procedure:**

1. Navigate to **Entra admin center > Applications > Agent identities**.
2. Select the designated test agent identity.
3. Select **Properties**.
4. Locate the **Sponsor** field.
5. Verify that the Sponsor field contains the name of the expected test sponsor user (not empty, not a group, not a service account).

**Pass Criteria:** Sponsor field displays a named individual user account matching the expected sponsor.

**Fail Criteria:** Sponsor field is empty, displays a group, or displays a service account.

**Evidence to Capture:** Screenshot of the test agent's Properties panel showing the Sponsor field with the assigned individual.

---

### Test 2.2: Zero-Sponsor Gap Scan (Zone 2 and Zone 3)

**Purpose:** Confirm that no production Zone 2 or Zone 3 agents have a null sponsor field. This is a production-scope test using the PowerShell gap report.

**Procedure:**

1. Open PowerShell and connect to Microsoft Graph (read permissions as defined in PowerShell Setup playbook — Section 1.1).
2. Run the governance gap report from the PowerShell Setup playbook — Section 2.2:

    ```powershell
    $allAgents = Get-AllAgentIdentities
    $sponsorGaps = Get-AgentsWithoutSponsors -Agents $allAgents
    Write-Host "Agents without sponsors: $($sponsorGaps.Count)"
    ```

3. Filter to Zone 2 and Zone 3 agents only.
4. Verify the count of Zone 2/3 agents without sponsors is **zero**.

**Pass Criteria:** Zero Zone 2 or Zone 3 agents without an assigned sponsor.

**Fail Criteria:** One or more Zone 2 or Zone 3 agents have no sponsor assigned.

**Evidence to Capture:** Export of the governance gap report CSV showing zero records (or the filtered Zone 2/3 count = 0). Include the report timestamp.

**If Failing:** Assign sponsors to all identified agents per the PowerShell Setup playbook — Section 3 (Bulk Sponsor Assignment) or Portal Walkthrough — Section 2.

---

## Test 3: Access Package Configuration and Expiration

### Test 3.1: Access Package Assignment Verification for Test Agent

**Purpose:** Confirm that the test agent has an active access package assignment and that the assignment is the correct package for the agent's zone.

**Procedure:**

1. Navigate to **Entra admin center > Identity Governance > Entitlement management > Catalogs > AI Agent Resources > Access packages**.
2. Locate the access package appropriate for the test agent's zone.
3. Select the access package and navigate to **Assignments**.
4. Locate the test agent's assignment in the list.
5. Verify:
    - Assignment state is **Delivered** (active).
    - The assigned principal is the test agent identity (not a user account).
    - An expiration date is present.

**Pass Criteria:** Test agent has an active, delivered access package assignment with a future expiration date.

**Fail Criteria:** No assignment found, assignment is expired, or no expiration date is configured.

**Evidence to Capture:** Screenshot of the Assignments tab showing the test agent's assignment with state and expiration date visible.

---

### Test 3.2: Access Package Expiration Date Verification

**Purpose:** Confirm that the maximum access duration policy is correctly applied. Zone 2 and Zone 3 access packages must not exceed 365 days, and Zone 3 access packages must have expiration enforced (no perpetual access).

**Procedure:**

1. Navigate to each Zone 2 and Zone 3 access package in the **AI Agent Resources** catalog.
2. For each package, select **Lifecycle** settings.
3. Verify:
    - Maximum duration is set to **365 days** (or fewer).
    - "Never expires" or "No end date" is **not** selected.

**Pass Criteria:** All Zone 2 and Zone 3 access packages have a maximum duration of 365 days or fewer with expiration enforced.

**Fail Criteria:** Any Zone 2 or Zone 3 access package has no expiration configured or has a duration exceeding 365 days.

**Evidence to Capture:** Screenshot of each access package's Lifecycle settings panel showing the expiration configuration.

---

### Test 3.3: No Perpetual Access — Zone 3 Agent Direct Permission Check

**Purpose:** Confirm that Zone 3 agents have no resource access outside of entitlement management access packages. Direct SharePoint site permissions or direct Graph API delegated permissions assigned outside the access package framework constitute a compliance violation for Zone 3.

**Procedure:**

1. Open PowerShell and run the following query to check for direct application role assignments on Zone 3 agents:

    ```powershell
    # For each Zone 3 agent, check for direct app role assignments
    # (assignments that are NOT traceable to an access package)
    $zone3Agents = $allAgents | Where-Object {
        (Get-MgBetaServicePrincipal -ServicePrincipalId $_.Id).AdditionalData["governanceZone"] -eq "Zone3"
    }

    foreach ($agent in $zone3Agents) {
        $directRoles = Get-MgServicePrincipalAppRoleAssignment `
            -ServicePrincipalId $agent.Id -All

        if ($directRoles.Count -gt 0) {
            Write-Warning "Zone 3 agent '$($agent.DisplayName)' has $($directRoles.Count) direct role assignments outside access packages."
            $directRoles | Select-Object PrincipalDisplayName, ResourceDisplayName, AppRoleId
        } else {
            Write-Host "[OK] $($agent.DisplayName) — no direct role assignments." -ForegroundColor Green
        }
    }
    ```

2. Verify that no Zone 3 agents have direct role assignments outside entitlement management.

**Pass Criteria:** Zero Zone 3 agents have direct application role assignments outside the access package framework.

**Fail Criteria:** One or more Zone 3 agents have direct role assignments not governed by an access package.

**Evidence to Capture:** PowerShell output showing "[OK]" for all Zone 3 agents, or the remediation actions taken to remove direct assignments.

---

## Test 4: Lifecycle Workflow — Sponsor Departure Simulation

!!! danger "Test Environment Only — Do Not Run Against Production Sponsors"
    This test involves simulating the deactivation of a user account to trigger the leaver lifecycle workflow. This MUST be performed using a **designated test sponsor account** — never a production user's account. Ensure the test agent and test sponsor are clearly labeled as test objects and are not used for any production workloads.

### Test 4.1: Lifecycle Workflow Existence Verification

**Purpose:** Confirm that at least one active lifecycle workflow is configured with a sponsor-departure trigger.

**Procedure:**

1. Navigate to **Entra admin center > Identity Governance > Lifecycle workflows**.
2. Verify at least one workflow is listed.
3. Select the sponsor departure workflow created in the Portal Walkthrough.
4. Verify:
    - Workflow is **Enabled**.
    - Trigger category is **Leaver**.
    - At least three tasks are configured: notification, disable agent, create review task.

**Pass Criteria:** At least one enabled lifecycle workflow with leaver trigger and the required task sequence is present.

**Fail Criteria:** No lifecycle workflows present, or the workflow is disabled, or required tasks are missing.

**Evidence to Capture:** Screenshot of the lifecycle workflow detail view showing enabled status, trigger, and tasks.

---

### Test 4.2: Sponsor Departure Simulation Test

**Purpose:** Confirm that when a sponsor's account is deactivated, the lifecycle workflow fires correctly, sends the expected notification, disables the associated agent identity, and creates an access review task.

**Procedure:**

1. **Assign the test sponsor to the test agent:** Ensure the test agent's Sponsor field in Entra is set to the test sponsor account.

2. **Note the test agent's current state:** Confirm the test agent is currently enabled.

3. **Trigger the departure event:** In Entra admin center (or via PowerShell), deactivate the test sponsor's user account:

    ```powershell
    # Disable test sponsor account to simulate departure
    # REPLACE with actual test sponsor object ID — never use a production account
    $testSponsorId = "test-sponsor-object-id-here"
    Update-MgUser -UserId $testSponsorId -AccountEnabled:$false
    Write-Host "Test sponsor account disabled at $(Get-Date -Format 'o')"
    ```

4. **Wait for workflow processing:** Lifecycle workflows may take up to 15–30 minutes to trigger after the leaver condition is detected. Do not proceed until the wait period has elapsed.

5. **Check workflow execution history:**
    - Navigate to **Identity Governance > Lifecycle workflows > [Sponsor Departure Workflow] > Workflow history**.
    - Locate the run triggered by the test sponsor's departure.
    - Verify all tasks completed successfully (green checkmarks).

6. **Verify notification was sent:** Check the AI Governance Lead's inbox for the notification email generated by Task 1 of the workflow. Confirm the email references the correct agent and sponsor names.

7. **Verify agent identity was disabled:**
    - Navigate to **Agent identities > [Test Agent]**.
    - Confirm **AccountEnabled** is now **False**.

8. **Verify access review task was created:**
    - Navigate to **Identity Governance > Access reviews**.
    - Confirm an ad-hoc access review was created for the test agent.

9. **Re-enable test accounts after test completion:**

    ```powershell
    # Re-enable test sponsor after test
    Update-MgUser -UserId $testSponsorId -AccountEnabled:$true

    # Re-enable test agent (assign new test sponsor before re-enabling in production)
    Update-MgBetaServicePrincipal -ServicePrincipalId "test-agent-id-here" `
        -AccountEnabled:$true
    Write-Host "Test accounts restored at $(Get-Date -Format 'o')"
    ```

**Pass Criteria:** All of the following are confirmed:
- Workflow execution appears in history with successful completion status
- Notification email received by AI Governance Lead with correct agent and sponsor names
- Test agent AccountEnabled = False after workflow execution
- Ad-hoc access review task created for the test agent

**Fail Criteria:** Workflow did not fire within 30 minutes; any task failed; notification not received; agent was not disabled; access review task was not created.

**Evidence to Capture:**
- Screenshot of workflow execution history showing successful run
- Screenshot of notification email received
- Screenshot of test agent Properties showing AccountEnabled = False
- Screenshot of ad-hoc access review task created

**If Failing:** See [Troubleshooting playbook](troubleshooting.md) — Section 2: Lifecycle Workflow Not Triggering.

---

## Test 5: Access Certification Campaign Verification

### Test 5.1: Access Certification Campaign Existence

**Purpose:** Confirm that a recurring quarterly access certification campaign is active for Zone 3 agents.

**Procedure:**

1. Navigate to **Entra admin center > Identity Governance > Access reviews**.
2. Look for the Zone 3 quarterly access certification review created in the Portal Walkthrough — Section 6.
3. Verify:
    - Review name matches: "Zone 3 Agent Access Certification — Quarterly"
    - Status: **Active** or **In Progress**
    - Recurrence: **Quarterly**
    - Reviewers: Sponsor (primary) + Compliance Officer (secondary)
    - On failure to review: **Remove access**

**Pass Criteria:** Quarterly access certification review is active with correct configuration.

**Fail Criteria:** No review found, review is not recurring, reviewers are incorrect, or "on failure" action is not set to remove access.

**Evidence to Capture:** Screenshot of the access review configuration showing all required settings.

---

### Test 5.2: Certification Completion Evidence Export

**Purpose:** Confirm that at least one completed quarterly certification cycle has evidence available for export. This is the primary examination evidence for FINRA 3110 supervisory attestation.

**Procedure:**

This test applies when the first quarterly cycle has completed. If no cycle has completed yet (control was recently implemented), document the current review's active status as preliminary evidence and re-run this test at the close of the first review period.

1. Navigate to the completed access review instance (if one exists).
2. Select **Download results**.
3. Verify the exported CSV contains the following columns with populated data:
    - Agent / principal name
    - Resource accessed
    - Certifier (reviewer) name and UPN
    - Decision (Approve / Deny)
    - Justification text (for approve decisions: business need statement; for deny: reason for removal)
    - Decision date and time

4. Verify all Zone 3 agents appear in the certification output (no agents missing from the review scope).
5. Archive the CSV to the governance evidence repository per retention policy.

**Pass Criteria:** Completed certification export exists with all required fields populated; all Zone 3 agents are represented; evidence is archived with correct retention applied.

**Fail Criteria:** No completed certification exists (if more than 90 days since control implementation); agents are missing from the scope; justification fields are empty (decisions made without documented rationale); evidence is not archived.

**Evidence to Capture:** The exported CSV file and its archival confirmation (file hash, archival timestamp, retention system confirmation).

---

## Test 6: Zero Expired Access Verification

### Test 6.1: Expired Access Active-Agent Scan

**Purpose:** Confirm that no agents with expired access package assignments remain in an active (enabled) state. This is a zero-tolerance criterion — an active agent with expired access represents both a security gap and a compliance violation.

**Procedure:**

1. Open PowerShell and run the expired access scan from the PowerShell Setup playbook — Section 2.3:

    ```powershell
    $accessPackageReport = Get-AgentAccessPackageAssignments

    $expiredActiveAgents = $accessPackageReport | Where-Object {
        $_.ExpiryStatus -like "EXPIRED*" -and $_.AssignmentState -eq "Delivered"
    }

    if ($expiredActiveAgents.Count -eq 0) {
        Write-Host "PASS: Zero agents with expired active access package assignments." -ForegroundColor Green
    } else {
        Write-Warning "FAIL: $($expiredActiveAgents.Count) agents have expired access still in delivered state."
        $expiredActiveAgents | Format-Table AccessPackageName, AssignedToId, ExpirationDateTime -AutoSize
    }
    ```

2. Verify the count of expired active assignments is **zero**.

**Pass Criteria:** Zero agents have expired access package assignments in a delivered/active state.

**Fail Criteria:** One or more agents have expired access package assignments that have not been removed.

**Evidence to Capture:** PowerShell output showing "PASS: Zero agents with expired active access package assignments." Include the timestamp of the scan.

**If Failing:** Manually remove the expired assignments via Entra admin center > Entitlement management > Access packages > [Package] > Assignments > [Assignment] > Remove, or use the access review process to certify removal. Document the remediation actions with timestamps.

---

## Test 7: SIEM Log Forwarding Verification

### Test 7.1: Entra Lifecycle Event Log Forwarding Confirmation

**Purpose:** Confirm that Entra audit log events for agent identity lifecycle actions are being forwarded to the SIEM and are queryable within the SIEM platform.

**Procedure:**

1. **Verify Entra Diagnostic Settings are configured:**
    - Navigate to **Entra admin center > Monitoring & health > Diagnostic settings**.
    - Confirm a diagnostic setting exists targeting the organization's Log Analytics workspace or Event Hub.
    - Confirm **AuditLogs** is checked in the log categories.

2. **Generate a known test event:** In the Entra admin center, make a minor, reversible change to the test agent identity (e.g., update the description field). This generates an AuditLog entry.

3. **Query the SIEM for the test event:** In the organization's SIEM (e.g., Microsoft Sentinel), run a query to confirm the event was received:

    ```kql
    // Example KQL query for Microsoft Sentinel
    AuditLogs
    | where TimeGenerated > ago(15m)
    | where Category == "ApplicationManagement"
    | where TargetResources has "test-agent-display-name"
    | project TimeGenerated, OperationName, InitiatedBy, TargetResources, Result
    ```

4. Verify the test event appears in the SIEM query results within 15 minutes of the change.

5. **Verify retention policy:**
    - Navigate to the Log Analytics workspace (or SIEM retention settings).
    - Confirm the retention period for the agent identity log stream is set to **minimum 6 years (2190 days)**.

**Pass Criteria:** Test event appears in SIEM query within 15 minutes; retention policy is confirmed at 6 years minimum.

**Fail Criteria:** Test event does not appear in SIEM query within 15 minutes; retention policy is less than 6 years; diagnostic setting is absent.

**Evidence to Capture:** Screenshot of the SIEM query results showing the test event; screenshot of the retention policy setting.

---

## Verification Summary Report Template

Use this template to document test results for the quarterly governance report and examination evidence file:

```
CONTROL 2.26 VERIFICATION SUMMARY
Test Date: [DATE]
Tested By: [NAME, TITLE]
Reviewed By: [NAME, TITLE — AI Governance Lead or Compliance Officer]

---
TEST RESULTS

Test 1.1 — Frontier Enrollment:          [ PASS / FAIL ]
Test 1.2 — Agent Identities Blade:        [ PASS / FAIL ]
Test 2.1 — Sponsor Assignment (Test):     [ PASS / FAIL ]
Test 2.2 — Zero-Sponsor Gap Scan:         [ PASS / FAIL ]
Test 3.1 — Access Package Assignment:     [ PASS / FAIL ]
Test 3.2 — Expiration Date Config:        [ PASS / FAIL ]
Test 3.3 — No Perpetual Access (Zone 3):  [ PASS / FAIL ]
Test 4.1 — Workflow Existence:            [ PASS / FAIL ]
Test 4.2 — Sponsor Departure Simulation:  [ PASS / FAIL ]
Test 5.1 — Certification Campaign:        [ PASS / FAIL ]
Test 5.2 — Certification Evidence Export: [ PASS / FAIL ]
Test 6.1 — Zero Expired Access:           [ PASS / FAIL ]
Test 7.1 — SIEM Log Forwarding:           [ PASS / FAIL ]

---
OVERALL RESULT: [ PASS / FAIL — N tests failed ]

OPEN ITEMS / REMEDIATION ACTIONS:
[List any failing tests with assigned owner and due date]

EVIDENCE FILES ARCHIVED:
[List all evidence files, their locations, and archive timestamps]
```

---

[Back to Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

*Updated: March 2026 | Version: v1.3*
