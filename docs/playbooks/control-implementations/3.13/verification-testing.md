# Playbook 3.13-C: Verification Testing — Confirming Analytics Visibility and Export Integrity

**Playbook ID:** 3.13-C
**Control:** 3.13 — Agent 365 Admin Center Analytics and Reporting
**Pillar:** Reporting
**Estimated Duration:** 1–2 hours
**Required Role:** Entra Global Admin or AI Administrator; Internal Audit (for attestation)
**Last Verified:** April 2026

---

!!! info "Purpose of Verification Testing"
    This playbook provides the structured test procedures that Internal Audit, IT Risk, and Compliance teams must execute to confirm that Control 3.13 is operating effectively. Each test produces documented evidence that can be presented to FINRA examiners or SOX auditors as proof that the supervisory analytics program is functioning as designed. Complete this playbook at minimum annually; Zone 3 firms should complete quarterly.

---

## Overview

Verification testing for Control 3.13 confirms that:

1. The Agent 365 Admin Center Analytics dashboard is accessible to authorized roles and displaying accurate data.
2. Hero metrics (if Frontier-enrolled) are populating from real agent telemetry.
3. Governance cards (Pending Requests, Ownerless Agents) are visible and actionable.
4. Inventory exports are complete, correctly formatted, and successfully stored in the designated records repository.
5. Automated alert workflows are functioning and delivering notifications within the expected timeframe.
6. The supervisory review log contains evidence of recurring reviews at the required cadence.

---

## Test 1: Dashboard Accessibility and Role Verification

**Test Objective**: Confirm that users with the correct roles can access the analytics dashboard and that users without appropriate roles are denied access.

**Test Steps**:

**T1.1 — Authorized Access Test**
1. Sign in to the M365 Admin Center with an Entra Global Admin account.
2. Navigate to Agents > Overview.
3. Confirm the page loads and displays the Agent Registry count.
4. Record: page load time, Agent Registry count, and any error messages.

Expected Result: Page loads successfully. Agent Registry count displays a non-zero value if agents are deployed.

**T1.2 — AI Administrator Role Test**
1. Sign in with an account that has only the AI Administrator role (not Entra Global Admin).
2. Navigate to Agents > Overview.
3. Confirm the page loads and displays data.

Expected Result: Page loads successfully. AI Administrator has sufficient privileges for analytics review (per the Agent 365 GA role limitations).

**T1.3 — Unauthorized Access Test**
1. Sign in with a standard Microsoft 365 user account (no admin roles).
2. Attempt to navigate to `https://admin.microsoft.com`.

Expected Result: User is either redirected away from the admin center or cannot navigate to the Agents section. No agent inventory data should be visible.

**Evidence to Record**:
- Screenshots of successful access for authorized roles
- Screenshot or description of access denial for unauthorized user
- Date, time, and tester identity

---

## Test 2: Hero Metrics Population Verification [Requires Agent 365 / E7 licensing]

**Test Objective**: Confirm that hero metrics are displaying real data (not zeros or placeholder values) from agent telemetry.

!!! info "Availability"
    With Agent 365 generally available as of May 1, 2026, hero metrics are available to all tenants with Agent 365 or Microsoft 365 E7 licensing. If neither licensing path applies to the tenant, document this test as N/A and record the planned licensing date.

**Test Steps**:

**T2.1 — Metric Presence**
1. Navigate to Agents > Overview.
2. Confirm all four hero metric cards are visible: Active Users, Total Sessions, Exception Rate, Agent Runtime.
3. Record all four current values.

Expected Result: All four cards visible and displaying numeric values.

**T2.2 — Non-Zero Validation**
1. Confirm Active Users > 0 (at least one user has interacted with an agent in the past 30 days).
2. Confirm Total Sessions > 0.
3. Confirm Exception Rate is between 0% and 100% (a value outside this range indicates a data error).
4. Confirm Agent Runtime > 0.

Expected Result: All metrics show non-zero values in a tenant with deployed, active agents.

**T2.3 — Metric Consistency Check**
1. If Total Sessions = N, Active Users cannot logically exceed N. Verify this relationship holds.
2. Record any metric combinations that appear logically inconsistent (e.g., Active Users > Total Sessions) as anomalies requiring investigation.

**T2.4 — Historical Trend Validation**
1. Review the Active Users Over Time chart.
2. Confirm the chart displays 30 days of daily data points.
3. Confirm the trend line is continuous (no unexpected gaps that might indicate telemetry interruption).

Expected Result: Continuous 30-day trend line with no unexplained gaps.

**Evidence to Record**:
- Screenshot of Overview page showing all four hero metric values
- Screenshot of Active Users Over Time chart
- Record of any anomalies and follow-up actions

---

## Test 3: Governance Cards Functionality Test

**Test Objective**: Confirm that Pending Requests and Ownerless Agents governance cards are accurate and navigation links are functional.

**Test Steps**:

**T3.1 — Pending Requests Card**
1. Note the pending request count displayed on the governance card.
2. Select the "Manage requests" button.
3. Confirm navigation to Agent Registry > Requests tab.
4. Count the requests visible in the Requests tab.
5. Verify count in Requests tab matches (or is consistent with) the governance card count.

Expected Result: Navigation works correctly. Count in Requests tab is consistent with governance card.

**T3.2 — Ownerless Agents Card**
1. Note the ownerless agent count displayed on the governance card.
2. Select the "Assign Owner" button.
3. Confirm navigation to Agent Registry with Ownerless Agents filter applied.
4. Count the agents displayed under the filter.
5. Verify count matches (or is consistent with) the governance card count.

Expected Result: Navigation works correctly. Filtered agent count is consistent with governance card.

**T3.3 — Cross-Reference Validation**
1. Navigate to Agents > All Agents.
2. Sort or filter agents by "Owner" to identify agents with no owner assigned.
3. Confirm the ownerless agents identified in the All Agents view match those shown in the governance card filter.

Expected Result: Agent list and governance card are consistent. Discrepancies should be documented and investigated.

**Evidence to Record**:
- Screenshot of Pending Requests governance card with count
- Screenshot of Requests tab showing matching count
- Screenshot of Ownerless Agents governance card with count
- Screenshot of All Agents filtered view showing ownerless agents
- Documentation of any count discrepancies and resolution

---

## Test 4: Inventory Export Completeness Test

**Test Objective**: Confirm that the exported agent inventory is complete, correctly formatted, and suitable as a FINRA examination artifact.

**Test Steps**:

**T4.1 — Manual Export Generation**
1. Navigate to Agents > All Agents.
2. Note the total agent count displayed in the All Agents list (page header or row count).
3. Select the Export button.
4. Allow the download to complete.
5. Open the downloaded CSV file.

**T4.2 — Row Count Verification**
1. Count the data rows in the exported CSV (excluding the header row).
2. Compare row count to the agent count noted in step T4.1.

Expected Result: Row count in CSV matches the agent count displayed in the All Agents list. A discrepancy of more than 1–2 agents (accounting for any pagination timing differences) should be investigated.

**T4.3 — Field Completeness Verification**
Review the CSV headers and confirm the export includes at minimum:
- [ ] Agent display name
- [ ] Publisher / publisher type (Microsoft / Organization / Partner)
- [ ] Platform (Copilot Studio / Azure AI Foundry / etc.)
- [ ] Agent status (Active / Inactive / etc.)
- [ ] Owner or owner email
- [ ] Creation date or last modified date

Expected Result: All fields are present. Blank values in "Owner" column should correlate to agents identified as ownerless in the governance card.

**T4.4 — Cross-Reference with Known Agents**
1. Select three known agents (one Microsoft-built, one custom/internal, one partner-built if applicable).
2. Confirm each appears in the exported CSV with the correct publisher type.

Expected Result: All three test agents appear in the CSV with correct attributes.

**T4.5 — Storage Repository Confirmation**
1. Navigate to the designated records repository (SharePoint library, Azure Blob Storage container, or document management system).
2. Confirm the most recent dated export file is present with the correct filename convention: `AgentInventory_[TenantName]_[YYYYMMDD].csv`
3. Confirm the file timestamp on the repository matches the expected export date.
4. Confirm the file is accessible and opens correctly.

Expected Result: File is present, correctly named, and readable in the records repository.

**T4.6 — Automated Export Verification (if PowerShell automation is configured)**
1. Review the Azure Blob Storage container for the last three automated export files.
2. Confirm each file is present with the correct date-stamped filename.
3. Confirm the immutability policy status is "Locked" (Zone 3) by running:

```powershell
Get-AzStorageContainerImmutabilityPolicy `
    -ResourceGroupName $ResourceGroupName `
    -StorageAccountName $StorageAccountName `
    -ContainerName "agent-inventory-exports" | Select-Object ImmutabilityPeriodSinceCreationInDays, State
```

Expected Result: Policy State = "Locked"; Immutability period = 2,190 days (6 years).

**Evidence to Record**:
- Screenshot of All Agents page showing total agent count
- Exported CSV file (retain as test evidence artifact)
- Row count comparison results
- Field completeness checklist
- Screenshot of records repository showing dated export files
- PowerShell output showing immutability policy state (Zone 3)

---

## Test 5: Alert Workflow Verification

**Test Objective**: Confirm that automated compliance alert workflows deliver notifications when threshold conditions are met.

**Test Steps**:

**T5.1 — Power Automate Flow Status**
1. Navigate to Power Automate (https://make.powerautomate.com).
2. Locate the `FSI-AgentGov-3.13-ComplianceAlerts` flow.
3. Confirm the flow status is "On."
4. Review the flow run history for the most recent executions.

Expected Result: Flow is active. Run history shows successful executions on the scheduled cadence.

**T5.2 — Alert Trigger Test (Exception Rate)**
1. Temporarily lower the exception rate alert threshold in the flow to a value guaranteed to trigger (e.g., 99%) to simulate an alert condition.
2. Manually trigger the flow using the "Run" button in Power Automate.
3. Confirm the compliance officer email inbox receives the alert email within 15 minutes.
4. Review the email content for accuracy: exception rate value, required action, timestamp.
5. Restore the threshold to the production value (90%) after the test.

Expected Result: Alert email received within 15 minutes. Email content is accurate and actionable.

**T5.3 — Alert Trigger Test (Pending Requests)**
1. Temporarily lower the pending request threshold to 0 to ensure an alert will trigger if any pending requests exist, or manually set the threshold to a value below the current pending request count.
2. Manually trigger the flow.
3. Confirm the compliance officer email inbox receives the alert email.
4. Restore the production threshold value.

Expected Result: Alert email received. Email accurately reports the pending request count.

**Evidence to Record**:
- Screenshot of Power Automate flow status showing "On"
- Screenshot of flow run history
- Copy of alert email received during T5.2 test
- Copy of alert email received during T5.3 test
- Confirmation that production thresholds were restored after testing

---

## Test 6: Supervisory Review Log Verification

**Test Objective**: Confirm that the recurring analytics review process is documented and that review log entries satisfy FINRA 3110 written supervisory procedures requirements.

**Test Steps**:

**T6.1 — Review Log Existence**
1. Navigate to the designated supervisory review log (GRC system, SharePoint document, or equivalent).
2. Confirm a review log exists and contains entries dating back at least 12 months (or since Control 3.13 was implemented, whichever is shorter).

**T6.2 — Review Cadence Verification**
1. Review the dates of all log entries in the past 12 months.
2. Verify the cadence matches the Zone designation:
   - Zone 1: Monthly entries (12 entries in 12 months)
   - Zone 2: Weekly entries (approximately 52 entries in 12 months)
   - Zone 3: Daily business day entries (approximately 260 entries in 12 months)
3. Identify any gaps in the review schedule (dates with no log entry). Document gaps as findings.

Expected Result: Log entries are present at the required cadence. Gaps, if any, are documented with explanations (e.g., holidays, system outages).

**T6.3 — Log Entry Completeness**
1. Select three log entries at random.
2. For each entry, verify it contains:
   - [ ] Date and time of review
   - [ ] Reviewer name and title
   - [ ] Agent Registry count
   - [ ] Pending requests count and disposition actions
   - [ ] Ownerless agents count and remediation actions
   - [ ] Exception rate value (where available)
   - [ ] Export filename and storage location (for review sessions that included an export)
   - [ ] Any anomalies identified and follow-up actions

Expected Result: All three sampled log entries contain the required elements.

**T6.4 — Reviewer Authorization Verification**
1. For each sampled log entry, confirm the listed reviewer holds the Entra Global Admin or AI Administrator role.
2. Verify via Entra admin center: Users > [reviewer name] > Assigned roles.

Expected Result: All reviewers hold an authorized role. Log entries from users without an authorized role should be treated as a control deficiency.

**Evidence to Record**:
- Screenshot or export of supervisory review log showing entry dates
- Cadence analysis (count of entries vs. expected count)
- Copies of three sampled log entries
- Entra role confirmation for sampled reviewers

---

## Test Summary and Attestation

Upon completion of all six tests, complete the following attestation:

| Test | Pass / Fail / N/A | Findings | Remediation Required |
|---|---|---|---|
| Test 1: Dashboard Accessibility | | | |
| Test 2: Hero Metrics Population | | | |
| Test 3: Governance Cards Functionality | | | |
| Test 4: Inventory Export Completeness | | | |
| Test 5: Alert Workflow Verification | | | |
| Test 6: Supervisory Review Log Verification | | | |

**Overall Control Effectiveness Assessment**:
- [ ] Effective — All tests passed; control is operating as designed
- [ ] Partially Effective — One or more tests identified minor findings; remediation plan documented
- [ ] Deficient — One or more tests identified material findings; escalation required

**Tester Name**: ____________________________
**Tester Title**: ____________________________
**Date of Testing**: ____________________________
**Reviewed By (Compliance Officer)**: ____________________________
**Date Reviewed**: ____________________________

Retain this completed attestation form as a business record. For Zone 3 firms, retain for 6 years in the designated records repository.

---

[Back to Control 3.13](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
