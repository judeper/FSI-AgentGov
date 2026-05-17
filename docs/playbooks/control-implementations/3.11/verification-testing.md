# Verification & Testing: Control 3.11 - Centralized Agent Inventory Enforcement

**Last Updated:** April 2026
**Testing Level:** Control Validation
**Estimated Time:** 45-60 minutes

---

## Test Environment Setup

Before beginning verification testing, prepare a test environment:

- [ ] Zone 1 (Personal) test environment with 3-5 test agents
- [ ] Zone 2 (Team) test environment with 3-5 test agents
- [ ] Zone 3 (Enterprise) test environment with 3-5 test agents
- [ ] Test agents with varying metadata completeness (complete, incomplete, missing owner)
- [ ] Test agent with departed owner (simulated by deleting test user from Entra ID)
- [ ] Test agent that is stale (manually set last modified date >12 months ago if possible)
- [ ] Access to PPAC Agent Inventory, Power Automate, and PowerShell execution environment

---

## Test Case 1: Power Platform Inventory Data Refresh

**Objective:** Verify that Power Platform Inventory in PPAC discovers all agents within the platform-managed refresh window (~15 minutes).

### Test Steps

1. Navigate to PPAC → Manage → Inventory → Agents
2. Note the current agent count and **Last refreshed** timestamp
3. Create a new test agent in Copilot Studio (any test environment)
4. Wait approximately 15-30 minutes for the platform-managed refresh
5. Refresh the Inventory page in the browser
6. Verify the new test agent appears in the inventory list

### Expected Results

- [ ] Inventory page displays a "Last refreshed" timestamp
- [ ] After the platform refresh window, the new test agent appears in the list
- [ ] Agent metadata (name, owner, environment, creation date) is populated correctly
- [ ] No manual or per-environment refresh schedule is required (platform-managed at ~15-minute intervals)

### Evidence Collection

- Screenshot: Inventory before test agent creation (showing agent count and timestamp)
- Screenshot: Inventory after refresh (showing new agent in list)
- Note the elapsed time between agent creation and appearance in inventory

---

## Test Case 2: Mandatory Metadata Enforcement (Pre-Publication Checklist)

**Objective:** Verify that agents without complete metadata cannot be published to Zone 3 environments.

### Test Steps

1. Create a new test agent in a Zone 3 environment
2. Complete agent configuration but intentionally leave mandatory fields blank:
   - Leave Description empty
   - Do not assign Risk Rating
   - Do not link to documentation
3. Attempt to publish or share the agent to organizational catalog
4. Verify that approval workflow blocks publication due to incomplete metadata

### Expected Results

- [ ] Agent cannot be published until pre-publication checklist is complete
- [ ] Approval workflow rejects the request with message: "Complete mandatory metadata before publication"
- [ ] Missing fields are clearly identified in rejection notice
- [ ] Agent remains in draft or private status until metadata is complete

### Evidence Collection

- Screenshot: Agent approval request form with missing fields highlighted
- Screenshot: Approval rejection message citing incomplete metadata
- Copy of pre-publication checklist with unchecked items

### Alternate Test (if approval workflow not yet implemented)

If automated enforcement is not configured, manually review test agent against pre-publication checklist and document gaps. This demonstrates the manual validation process until automation is implemented.

---

## Test Case 3: Ownership Validation and Orphaned Agent Detection

**Objective:** Verify that orphaned agents (with departed owners) are detected and flagged for remediation.

### Test Steps

1. Create a test agent in a Zone 2 environment and assign a test user as owner
2. Delete or disable the test user in Entra ID (simulating user departure)
3. Run PowerShell script: `Detect-OrphanedAgents.ps1 -InventoryReportPath [path] -OutputPath [path]`
4. Review the Orphaned Agents Report CSV
5. Verify the test agent appears in the report with reason: "Owner status: Departed"

### Expected Results

- [ ] PowerShell script executes without errors
- [ ] Orphaned Agents Report is generated with timestamp
- [ ] Test agent with departed owner appears in report
- [ ] Agent is marked as "High Priority" for remediation
- [ ] Recommended action is "Transfer ownership or decommission"

### Evidence Collection

- Screenshot: PowerShell script execution output showing orphaned agent count
- CSV export: OrphanedAgentsReport showing test agent with departed owner
- Screenshot: Entra ID showing deleted test user (to confirm simulation)

---

## Test Case 4: Incomplete Metadata Detection and Alerting

**Objective:** Verify that Power Automate flow detects agents with incomplete metadata and sends Teams notifications.

### Test Steps

1. Create a test agent with incomplete metadata:
   - Agent Name: "Test Agent - Incomplete Metadata"
   - Owner: Assign valid owner
   - Zone: Leave blank (or set to "Unknown")
   - Risk Rating: Leave blank
2. Wait for Power Automate flow `Agent Inventory Completeness Monitor` to run (or trigger manually)
3. Check Teams channel "Agent Governance Alerts" for notification
4. Verify notification includes the incomplete test agent

### Expected Results

- [ ] Power Automate flow runs on schedule (daily at 3:00 AM)
- [ ] Flow successfully retrieves Agent Inventory data
- [ ] Flow identifies test agent as having incomplete metadata
- [ ] Teams notification is posted to governance channel within 5 minutes of flow execution
- [ ] Notification lists agent name, environment, and missing fields (Zone, Risk Rating)

### Evidence Collection

- Screenshot: Power Automate flow run history showing successful execution
- Screenshot: Teams notification showing incomplete agent alert
- Screenshot: Agent record in Agent Inventory showing missing fields

---

## Test Case 5: Inventory Completeness Validation

**Objective:** Verify that `Test-InventoryCompleteness.ps1` accurately validates agents against mandatory metadata requirements.

### Test Steps

1. Prepare test inventory with mix of compliant and non-compliant agents:
   - Zone 1: 2 compliant agents, 1 with missing owner
   - Zone 2: 2 compliant agents, 1 with missing risk rating
   - Zone 3: 2 compliant agents, 1 with missing approval date
2. Run PowerShell script: `Test-InventoryCompleteness.ps1 -InventoryReportPath [path] -OutputPath [path]`
3. Review Inventory Completeness Report CSV
4. Calculate expected vs. actual compliance rates

### Expected Results

- [ ] Script executes without errors
- [ ] Compliance report correctly identifies all non-compliant agents
- [ ] Missing fields are accurately listed for each non-compliant agent
- [ ] Compliance rate calculation is correct (compliant / total * 100)
- [ ] Zone-specific compliance rates are calculated and displayed
- [ ] Warning is displayed if compliance rate is below target (95%)

### Expected Compliance Calculation

- Zone 1: 2/3 = 66.67%
- Zone 2: 2/3 = 66.67%
- Zone 3: 2/3 = 66.67%
- Overall: 6/9 = 66.67%

### Evidence Collection

- CSV export: InventoryComplianceReport showing all test agents
- Screenshot: PowerShell output showing compliance summary and zone breakdown
- Screenshot: Warning message displayed for sub-target compliance rate

---

## Test Case 6: Stale Agent Detection (12+ Months Without Modification)

**Objective:** Verify that agents not modified in >12 months are flagged as orphaned for review.

### Test Steps

1. Identify or create a test agent that has not been modified in >365 days
   - If not possible to age an agent, manually simulate by using an old agent or adjusting test data
2. Run `Detect-OrphanedAgents.ps1 -StalenessThresholdDays 365`
3. Review Orphaned Agents Report
4. Verify the stale test agent appears with reason: "Stale (not modified in X days)"

### Expected Results

- [ ] Script correctly calculates days since last modification
- [ ] Agents exceeding staleness threshold are flagged
- [ ] Stale agents are marked as "Medium Priority" (unless also have departed owner)
- [ ] Recommended action is "Verify usage and decommission if unused"

### Evidence Collection

- CSV export: OrphanedAgentsReport showing stale agent
- Screenshot: Agent metadata showing last modified date >365 days ago

---

## Test Case 7: Agent Decommissioning Workflow

**Objective:** Verify that agent decommissioning process correctly archives metadata and disables the agent.

### Test Steps

1. Select a test agent for decommissioning (orphaned or stale agent from previous tests)
2. Follow decommissioning workflow:
   - Export agent metadata from Agent Inventory
   - Create change request for decommissioning (include agent name, owner, environment, reason)
   - Obtain required approvals (Power Platform Admin, AI Governance Lead if Zone 2/3)
   - Archive metadata to SharePoint or governance repository
   - Disable agent sharing (set to "Private" or "Only me")
   - Update Agent Inventory status to "Decommissioned"
3. Verify agent is no longer accessible to users
4. Confirm metadata is archived and retained

### Expected Results

- [ ] Agent metadata is successfully exported before decommissioning
- [ ] Change request is created and approved per governance workflow
- [ ] Agent metadata is archived in designated location (SharePoint, compliance repository)
- [ ] Agent sharing is disabled and agent is no longer visible in organizational catalog
- [ ] Agent Inventory status is updated to "Decommissioned" with date and reason
- [ ] Archived metadata is accessible for audit purposes (7-year retention for FSI)

### Evidence Collection

- Exported agent metadata (CSV or JSON)
- Change request ticket showing approval chain
- Screenshot: Agent in Copilot Studio showing sharing disabled
- Screenshot: Agent Inventory showing "Decommissioned" status
- Screenshot: Archived metadata in SharePoint/repository

---

## Test Case 8: Zone-Specific Remediation SLAs

**Objective:** Verify that remediation SLAs are tracked and alerts are generated for overdue items.

### Test Steps

1. Create three orphaned agents (one in each zone):
   - Zone 1 agent: Discovered 61 days ago (exceeds 60-day SLA)
   - Zone 2 agent: Discovered 31 days ago (exceeds 30-day SLA)
   - Zone 3 agent: Discovered 15 days ago (exceeds 14-day SLA)
2. Run `Detect-OrphanedAgents.ps1` with SLA tracking enabled (feature may need custom script enhancement)
3. Review report for SLA breach indicators

### Expected Results

- [ ] Report identifies agents exceeding zone-specific SLA timeframes
- [ ] Zone 1 SLA: 60 days
- [ ] Zone 2 SLA: 30 days
- [ ] Zone 3 SLA: 14 days
- [ ] Overdue agents are flagged with "SLA Breach" indicator
- [ ] Escalation notification is sent to AI Governance Lead for overdue Zone 3 agents

### Evidence Collection

- CSV export: OrphanedAgentsReport with SLA breach indicators
- Screenshot: Email or Teams notification for SLA breach escalation

### Note

If SLA tracking is not yet implemented in the PowerShell script, this test serves as a requirements validation for future enhancement. Document the expected SLA thresholds and recommended automation approach.

---

## Test Case 9: Quarterly Inventory Audit

**Objective:** Verify that quarterly inventory audit process identifies all compliance gaps and generates audit report.

### Test Steps

1. Generate current Agent Inventory Report: `Get-AgentInventoryReport.ps1 -OutputPath [path]`
2. Run completeness validation: `Test-InventoryCompleteness.ps1 -InventoryReportPath [path]`
3. Compare current completeness metrics against baseline (from initial implementation)
4. Identify agents that remain non-compliant since last audit
5. Document audit findings in formal audit report template
6. Present findings to AI Governance Lead and Compliance Officer (simulated review meeting)

### Expected Results

- [ ] Inventory report is complete and includes all active agents
- [ ] Completeness metrics show improvement since baseline (or justify why no improvement)
- [ ] Non-compliant agents from previous audit are remediated or have documented exceptions
- [ ] Audit report documents: Total agents, compliance rate, zone breakdown, outstanding remediation items, trends
- [ ] Recommendations for improving enforcement effectiveness are included in audit report

### Evidence Collection

- CSV export: Current AgentInventoryReport
- CSV export: Current InventoryComplianceReport
- Formal audit report document (Word or PDF) with findings and recommendations
- Meeting notes or email showing presentation to governance leadership

---

## Test Case 10: End-to-End Enforcement Suite Execution

**Objective:** Verify that master orchestration script `Invoke-InventoryEnforcementSuite.ps1` executes all enforcement scripts in sequence without errors.

### Test Steps

1. Run master script: `Invoke-InventoryEnforcementSuite.ps1 -OutputPath [path] -ZoneMappingFile [path] -TeamsWebhookUrl [url]`
2. Monitor script execution and verify each step completes:
   - Step 1: Generate agent inventory report
   - Step 2: Detect orphaned agents
   - Step 3: Validate inventory completeness
3. Verify all reports are generated in output directory
4. Check Teams channel for consolidated notification (if webhook provided)

### Expected Results

- [ ] Master script executes all three sub-scripts without errors
- [ ] All three reports are generated with current timestamp:
  - AgentInventoryReport_YYYYMMDD-HHMMSS.csv
  - OrphanedAgentsReport_YYYYMMDD-HHMMSS.csv
  - InventoryComplianceReport_YYYYMMDD-HHMMSS.csv
- [ ] Console output displays summary statistics from each step
- [ ] Teams notification is sent with consolidated findings (if webhook configured)
- [ ] Total execution time is logged and reasonable (<10 minutes for typical tenant)

### Evidence Collection

- Screenshot: PowerShell console showing master script execution output
- Screenshot: Output directory showing all three generated reports
- Screenshot: Teams notification with consolidated enforcement findings

---

## Integration Testing

### Test Case 11: Change Management Integration

**Objective:** Verify that agent registration and ownership changes are tracked in change management system.

1. Create change request for new agent registration (Zone 3 agent)
2. Complete pre-publication checklist in change request form
3. Submit for approval and obtain required approvals
4. Deploy agent after approval
5. Verify agent appears in Agent Inventory with all metadata populated
6. Cross-reference Agent Inventory against change management system (all production agents have approved change tickets)

### Expected Results

- [ ] Change request template includes all pre-publication checklist items
- [ ] Approval workflow routes request to appropriate approvers based on zone
- [ ] Agent is not deployed until change request is approved
- [ ] Agent metadata in inventory references change ticket number
- [ ] Monthly audit can reconcile inventory against change tickets (100% match for Zone 3)

---

## Performance Testing

### Test Case 12: Large-Scale Inventory Processing

**Objective:** Verify that enforcement scripts can handle large agent inventories (100+ agents) efficiently.

1. Simulate large inventory (or test in tenant with 100+ agents)
2. Run `Get-AgentInventoryReport.ps1` and measure execution time
3. Run `Detect-OrphanedAgents.ps1` and measure execution time
4. Verify reports are generated without memory errors or timeouts

### Expected Results

- [ ] Script handles 100+ agents without errors
- [ ] Execution time is acceptable (<5 minutes for inventory report, <2 minutes for orphaned detection)
- [ ] PowerShell memory usage remains reasonable (<500MB)
- [ ] CSV reports are well-formatted and loadable in Excel without corruption

### Evidence Collection

- PowerShell execution time measurements
- PowerShell memory usage (Get-Process -Name pwsh | Select-Object WorkingSet)
- CSV reports successfully opened in Excel

---

## Negative Testing

### Test Case 13: Missing Permissions

**Objective:** Verify graceful error handling when user lacks required permissions.

1. Execute `Get-AgentInventoryReport.ps1` as a user without Power Platform Admin role
2. Observe error messages
3. Verify script does not crash but provides clear error guidance

### Expected Results

- [ ] Script displays error message: "Insufficient permissions. Power Platform Admin role required."
- [ ] Script suggests remediation: "Request Power Platform Admin role or contact your administrator."
- [ ] Script exits gracefully without stack trace or crash

---

## Validation Checklist

After completing all test cases, confirm:

- [ ] Power Platform Inventory discovers new agents within the platform-managed refresh window (~15 minutes)
- [ ] Mandatory metadata enforcement prevents publication of incomplete agents
- [ ] Orphaned agents (departed owners, stale agents) are detected correctly
- [ ] Incomplete metadata triggers automated Teams alerts
- [ ] Inventory completeness validation accurately calculates compliance rates
- [ ] Decommissioning workflow archives metadata and disables agents
- [ ] Zone-specific remediation SLAs are tracked (or requirements documented for future implementation)
- [ ] Quarterly audit process is documented and executable
- [ ] Master orchestration script executes all enforcement scripts successfully
- [ ] Change management integration tracks all agent registrations
- [ ] Scripts handle large inventories efficiently
- [ ] Error handling provides clear guidance for missing permissions

---

## Compliance Evidence Package

For regulatory examination, compile the following evidence:

1. **Baseline Inventory Report:** Pre-enforcement agent inventory export (demonstrates before state)
2. **Post-Enforcement Inventory Report:** Current agent inventory export (demonstrates after state)
3. **Orphaned Agents Report:** List of agents with departed owners or staleness, showing remediation actions
4. **Completeness Report:** Compliance rate by zone, showing improvement trend
5. **Audit Trail:** Log of all ownership changes, decommissioning actions, and metadata updates (from change management system or Dataverse audit table)
6. **Enforcement Scripts:** PowerShell scripts with version control history (demonstrates automated enforcement)
7. **Pre-Publication Checklist:** Documented checklist with approval workflow (demonstrates preventive control)
8. **Quarterly Audit Reports:** Series of audit reports showing continuous monitoring and improvement
9. **Screenshots:** Portal and Teams notification screenshots demonstrating real-time alerting
10. **Test Results:** This verification testing document with completed test cases and evidence

Package these items in a compliance folder for regulatory examination or internal audit.

---

## Continuous Validation

Implement continuous validation by:

1. **Scheduling the enforcement suite daily:** Use Windows Task Scheduler or Azure Automation to run `Invoke-InventoryEnforcementSuite.ps1` daily at 4:00 AM
2. **Monitoring Teams alerts:** Assign governance team members to review and triage Teams notifications daily
3. **Quarterly audits:** Add recurring calendar event for quarterly inventory audit and compliance review
4. **Annual control testing:** Repeat full verification testing suite annually to confirm control effectiveness

---

[Back to Control 3.11](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
