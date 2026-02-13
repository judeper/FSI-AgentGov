# Verification & Testing: Control 1.28 - Policy-Based Agent Publishing Restrictions

**Last Updated:** February 2026
**Test Environment:** Pre-production/Test
**Estimated Time:** 30-40 minutes

## Overview

This playbook provides test cases and verification procedures to confirm that policy-based publishing restrictions are functioning correctly across all governance zones.

---

## Prerequisites

- [ ] DLP policies configured and assigned to environments
- [ ] Test environments available for each zone (Zone 1, Zone 2, Zone 3)
- [ ] Test agent available for publishing experiments
- [ ] Approval workflows configured (Zone 2+ environments)
- [ ] Test user accounts with Agent Author and Power Platform Admin roles

---

## Test Case 1: DLP Enforcement - Block Publishing with Violations

**Objective:** Verify that agents with DLP violations cannot be published

### Test Steps

1. Open Copilot Studio and navigate to a Zone 3 environment
2. Create a new test agent named "Test Agent - DLP Violation"
3. Add a topic that uses a blocked connector:
   - Create a new topic called "Test HTTP Connector"
   - Add an action node using HTTP connector (blocked in Zone 3)
   - Configure the HTTP action to call an external API
4. Save the agent
5. Attempt to publish the agent by clicking **Publish**
6. Observe the security scan results

### Expected Results

- [ ] Security scan detects DLP violation for HTTP connector
- [ ] Publishing is blocked with red error indicator
- [ ] Error message displays: "This agent cannot be published due to DLP policy violations"
- [ ] Details panel lists HTTP connector as the violation
- [ ] Agent remains in draft status

### Evidence Collection

- Screenshot of security scan showing DLP violation
- Screenshot of blocked publish button
- Export DLP policy assignment showing Zone 3 restrictions

---

## Test Case 2: DLP Enforcement - Allow Publishing with Compliant Configuration

**Objective:** Verify that agents compliant with DLP policies can be published

### Test Steps

1. Open Copilot Studio and navigate to Zone 3 environment
2. Create a new test agent named "Test Agent - DLP Compliant"
3. Add a topic that uses only approved connectors:
   - Create a topic called "Test SharePoint Connector"
   - Add an action node using SharePoint Online connector (allowed in Zone 3)
   - Configure the SharePoint action to read from a document library
4. Save the agent
5. Attempt to publish the agent by clicking **Publish**
6. Observe the security scan results

### Expected Results

- [ ] Security scan passes with green checkmark
- [ ] No DLP violations detected
- [ ] Publishing proceeds to approval workflow (if Zone 2+)
- [ ] Agent enters "Pending Approval" or "Published" status

### Evidence Collection

- Screenshot of security scan showing no violations
- Screenshot of successful publish (or pending approval)
- Purview audit log entry for agent publishing event

---

## Test Case 3: Blocked Channel Detection

**Objective:** Verify that agents configured with prohibited channels are blocked from publishing

### Test Steps

1. Open Copilot Studio and navigate to Zone 2 or Zone 3 environment
2. Create a new test agent named "Test Agent - Blocked Channel"
3. Configure the agent to use a prohibited channel:
   - Navigate to **Settings** → **Channels**
   - Enable "Facebook" or "Telegram" channel
   - Save channel configuration
4. Attempt to publish the agent by clicking **Publish**
5. Observe the security scan results

### Expected Results

- [ ] Security scan detects blocked channel configuration
- [ ] Publishing is blocked with red error indicator
- [ ] Error message displays: "This agent uses prohibited channels"
- [ ] Details panel lists Facebook or Telegram as the violation
- [ ] Agent cannot be published until channel is removed

### Evidence Collection

- Screenshot of channel configuration with Facebook/Telegram enabled
- Screenshot of security scan showing blocked channel violation
- Screenshot of blocked publish button

---

## Test Case 4: Approval Workflow - Single Approver (Zone 2)

**Objective:** Verify that Zone 2 environments require approval before publishing

### Test Steps

1. Open Copilot Studio and navigate to a Zone 2 environment
2. Create a compliant test agent named "Test Agent - Zone 2 Approval"
3. Configure agent with approved connectors only (SharePoint, Teams)
4. Attempt to publish the agent:
   - Click **Publish**
   - Verify security scan passes
   - Provide publishing justification: "Test approval workflow"
   - Click **Submit for approval**
5. As Power Platform Admin, review the pending approval:
   - Open Power Platform Admin Center → Pending Approvals
   - Review agent publishing request
   - Approve the request with comment: "Approved for testing"
6. Verify agent publishing completes

### Expected Results

- [ ] Agent enters "Pending Approval" status after submission
- [ ] Agent author receives notification that approval is required
- [ ] Power Platform Admin receives approval request notification
- [ ] After approval, agent publishing completes successfully
- [ ] Agent enters "Published" status
- [ ] Approval event is logged in Purview audit log

### Evidence Collection

- Screenshot of "Submit for approval" screen with justification
- Screenshot of pending approval in Power Platform Admin Center
- Screenshot of approval action with admin comment
- Purview audit log entry showing approval event

---

## Test Case 5: Approval Workflow - Rejection (Zone 2)

**Objective:** Verify that rejected publishing requests prevent agent deployment

### Test Steps

1. Open Copilot Studio and navigate to Zone 2 environment
2. Create a test agent named "Test Agent - Rejection Test"
3. Submit the agent for publishing approval with justification: "Testing rejection workflow"
4. As Power Platform Admin, reject the publishing request:
   - Open Power Platform Admin Center → Pending Approvals
   - Review agent publishing request
   - Reject the request with comment: "Insufficient testing evidence"
5. Verify agent remains in draft status

### Expected Results

- [ ] Power Platform Admin successfully rejects the request
- [ ] Agent author receives notification that request was rejected
- [ ] Rejection comment is visible to agent author
- [ ] Agent remains in "Draft" status
- [ ] Agent is not deployed to production
- [ ] Rejection event is logged in Purview audit log

### Evidence Collection

- Screenshot of rejection action with admin comment
- Screenshot of rejection notification to agent author
- Purview audit log entry showing rejection event

---

## Test Case 6: Environment Promotion Pipeline (Zone 3)

**Objective:** Verify that Zone 3 agents must be promoted through dev→test→prod pipeline

### Test Steps

1. Verify separate environments exist:
   - Development environment (e.g., "Dev-Zone3")
   - Test environment (e.g., "UAT-Zone3")
   - Production environment (e.g., "Prod-Zone3")
2. Create a test agent in the Development environment
3. Publish the agent in Development (should succeed with approval)
4. Attempt to export/import the agent to Production environment (bypassing Test):
   - Export the agent from Development
   - Import the agent to Production
   - Attempt to publish in Production
5. Observe the promotion enforcement

### Expected Results

- [ ] Agent publishes successfully in Development after approval
- [ ] Agent can be promoted from Development to Test
- [ ] Agent cannot be published in Production without Test environment approval
- [ ] Promotion pipeline enforcement prevents bypassing Test environment
- [ ] Audit logs capture each promotion step

### Evidence Collection

- Screenshot of agent published in Development environment
- Screenshot of agent promoted to Test environment
- Screenshot of blocked direct promotion to Production
- Purview audit log showing environment promotion chain

---

## Test Case 7: DLP Update Blocking for Published Agents

**Objective:** Verify that published agents are blocked from updates if DLP violations are introduced

### Test Steps

1. Publish a compliant agent in Zone 3 environment (e.g., "Test Agent - Update Block")
2. Verify the agent is successfully published and available
3. Modify the DLP policy to block a connector the agent uses:
   - In Power Platform Admin Center, edit the Zone 3 DLP policy
   - Move SharePoint connector from "Business" to "Blocked"
   - Save the DLP policy
4. Attempt to update the published agent:
   - Make a minor change to the agent (e.g., update a topic message)
   - Click **Publish** to update the agent
5. Observe the publishing enforcement

### Expected Results

- [ ] Agent was initially published successfully
- [ ] After DLP policy change, agent is flagged as non-compliant
- [ ] Attempting to update the agent triggers security scan
- [ ] Security scan detects DLP violation (SharePoint connector now blocked)
- [ ] Publishing update is blocked with error message
- [ ] Agent remains in previous published version until violation is resolved

### Evidence Collection

- Screenshot of agent published successfully before DLP change
- Screenshot of DLP policy change (SharePoint moved to Blocked)
- Screenshot of blocked update attempt with DLP violation error
- Screenshot of agent status showing "Published (Non-Compliant)"

---

## Test Case 8: Security Scan Warning Override (Zone 1 Only)

**Objective:** Verify that Zone 1 environments allow publishing with warnings (but not errors)

### Test Steps

1. Open Copilot Studio and navigate to Zone 1 environment
2. Create a test agent that triggers a security warning (not error):
   - Use a connector that generates a warning (e.g., HTTP with untrusted certificate)
   - Configure the agent to use the connector
3. Attempt to publish the agent:
   - Click **Publish**
   - Observe security scan results showing yellow warning
   - Review warning details
4. Acknowledge the warning and proceed with publishing
5. Verify the agent publishes despite the warning

### Expected Results

- [ ] Security scan displays yellow warning indicator
- [ ] Warning details explain the security concern
- [ ] Zone 1 environment allows publishing with acknowledgment
- [ ] Agent author must explicitly acknowledge warning to proceed
- [ ] Agent publishes successfully after acknowledgment
- [ ] Warning is logged in audit trail

### Evidence Collection

- Screenshot of security scan showing yellow warning
- Screenshot of warning acknowledgment dialog
- Screenshot of successful publishing despite warning
- Purview audit log entry showing warning acknowledged

---

## Test Case 9: Audit Log Capture

**Objective:** Verify that all publishing events are captured in Microsoft Purview audit logs

### Test Steps

1. Perform several publishing actions across different zones:
   - Publish an agent in Zone 1 (successful)
   - Submit an agent for approval in Zone 2
   - Reject a publishing request in Zone 2
   - Approve a publishing request in Zone 3
2. Open Microsoft Purview Compliance Portal → Audit
3. Search for publishing-related events:
   - **Keywords:** "Chatbot", "Publish", "Approval"
   - **Activities:** "Create chatbot", "Update chatbot", "Approve request", "Reject request"
   - **Date range:** Last 24 hours
4. Review the audit log results

### Expected Results

- [ ] All publishing events are captured in Purview audit logs
- [ ] Audit entries include timestamp, user, agent name, environment, and action
- [ ] Approval and rejection events include approver comments
- [ ] DLP violation events are logged with connector details
- [ ] Security scan results are logged with pass/fail status
- [ ] Audit logs are retained per regulatory requirements (7 years for FSI)

### Evidence Collection

- Screenshot of Purview audit search results showing publishing events
- Export of audit log entries to CSV for compliance records
- Sample audit log entry showing detailed event metadata

---

## Test Case 10: PowerShell Compliance Report

**Objective:** Verify that PowerShell automation scripts accurately report publishing compliance

### Test Steps

1. Run the PowerShell compliance audit script:
   ```powershell
   .\Audit-AgentPublishingCompliance.ps1
   ```
2. Review the compliance report output:
   - Total agents count
   - Compliant agents count
   - Non-compliant agents count
   - List of non-compliant agents with violations
3. Manually verify several agents in the report:
   - Check DLP status in Power Platform Admin Center
   - Check channel configuration in Copilot Studio
   - Confirm approval status matches report

### Expected Results

- [ ] PowerShell script executes without errors
- [ ] Report displays accurate agent counts
- [ ] Non-compliant agents are correctly identified with violations
- [ ] DLP violations match manual verification
- [ ] Blocked channels match manual verification
- [ ] Report exports to CSV successfully

### Evidence Collection

- Screenshot of PowerShell compliance report output
- CSV export of compliance report
- Manual verification screenshots for sample agents

---

## Compliance Verification Checklist

After completing all test cases, verify the following:

- [ ] DLP policies are configured for all three zones with appropriate connector restrictions
- [ ] DLP violations prevent agent publishing in all zones
- [ ] Published agents are blocked from updates if DLP violations exist (February 2025 enforcement)
- [ ] Security scans detect blocked channels and configuration issues
- [ ] Zone 1 allows publishing with warnings (after acknowledgment)
- [ ] Zone 2+ requires approval before publishing
- [ ] Approval workflow captures approver identity, timestamp, and comments
- [ ] Rejection workflow prevents agent deployment
- [ ] Zone 3 enforces environment promotion pipeline (dev→test→prod)
- [ ] All publishing events are logged in Microsoft Purview
- [ ] Audit logs include DLP violations, approvals, rejections, and security scan results
- [ ] PowerShell automation scripts provide accurate compliance reporting

---

## Evidence Package

Compile the following evidence for compliance documentation:

1. **DLP Policy Configuration:**
   - Export of Zone 1, Zone 2, and Zone 3 DLP policies
   - Connector classification listings (Business/Non-Business/Blocked)
   - Environment assignment records

2. **Security Scan Results:**
   - Screenshots of passed scans (compliant agents)
   - Screenshots of failed scans (DLP violations, blocked channels)
   - Security scan reports for sample agents

3. **Approval Workflow Documentation:**
   - Screenshots of approval requests
   - Screenshots of approved requests with admin comments
   - Screenshots of rejected requests with feedback
   - Approval workflow configuration settings

4. **Audit Logs:**
   - CSV export of publishing events from Purview
   - Sample audit log entries with detailed metadata
   - Audit log retention policy documentation

5. **Compliance Reports:**
   - PowerShell compliance report CSV export
   - Summary of compliant vs. non-compliant agents
   - Remediation plan for non-compliant agents

---

## Ongoing Monitoring

Establish ongoing monitoring for publishing compliance:

- **Weekly:** Run PowerShell compliance audit script; review non-compliant agents
- **Monthly:** Review approval workflow metrics (requests, approvals, rejections, SLA)
- **Quarterly:** Audit DLP policy effectiveness; update connector restrictions as needed
- **Annually:** Review and update publishing governance policies based on regulatory changes

---

[Back to Control 1.28](../../../controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
