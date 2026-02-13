# Verification & Testing: Control 2.24 - Agent Feature Enablement and Restriction Governance

**Last Updated:** February 2026
**Test Environment:** Pre-production or isolated test tenant recommended
**Estimated Time:** 45-60 minutes

## Test Objectives

Verify that:
1. PPAC Copilot governance page correctly restricts features per zone
2. DLP policies enforce connector restrictions at runtime
3. Feature catalog accurately reflects approved/prohibited features
4. Change management workflow functions for feature requests
5. Prohibited features are inaccessible in restricted zones
6. Feature usage reporting captures compliance metrics

---

## Test Suite 1: PPAC Feature Governance Configuration

### Test 1.1: Verify Zone 3 Environment Has Restrictive Settings

**Objective:** Confirm Zone 3 environments have all high-risk features disabled.

**Prerequisites:**
- Access to PPAC with Power Platform Admin role
- At least one Zone 3 (Enterprise) environment identified

**Steps:**
1. Open Power Platform Admin Center → Copilot → Governance
2. Select a Zone 3 environment from the environment list
3. Review feature toggle states

**Expected Results:**
| Feature | Expected State | Pass/Fail |
|---------|---------------|-----------|
| Generative Actions | Disabled or Explicit Allowlist | ☐ |
| Preview Features | Disabled | ☐ |
| Web Search Tool | Disabled or Explicit Allowlist | ☐ |
| Code Interpreter | Disabled | ☐ |
| Multi-Agent Orchestration | Disabled or Requires Approval | ☐ |

**Pass Criteria:** All high-risk features are disabled or require explicit approval.

**Evidence:** Screenshot of Zone 3 environment feature settings panel in PPAC.

---

### Test 1.2: Verify Zone 2 Environment Has Moderate Restrictions

**Objective:** Confirm Zone 2 environments allow approved features with documented approval.

**Prerequisites:**
- At least one Zone 2 (Team) environment identified

**Steps:**
1. In PPAC Copilot governance page, select a Zone 2 environment
2. Review feature toggle states

**Expected Results:**
| Feature | Expected State | Pass/Fail |
|---------|---------------|-----------|
| Generative Actions | Enabled (with approval process) | ☐ |
| Preview Features | Disabled | ☐ |
| Web Search Tool | Enabled (restricted to approved agents) | ☐ |
| Code Interpreter | Disabled | ☐ |
| Multi-Agent Orchestration | Enabled with depth limit (max 2) | ☐ |

**Pass Criteria:** Zone 2 allows more features than Zone 3, but maintains restrictions on high-risk capabilities.

**Evidence:** Screenshot of Zone 2 environment feature settings.

---

### Test 1.3: Verify Zone 1 Environment Has Permissive Settings

**Objective:** Confirm Zone 1 environments allow Microsoft default features for testing.

**Prerequisites:**
- At least one Zone 1 (Personal) environment identified

**Steps:**
1. In PPAC Copilot governance page, select a Zone 1 environment
2. Review feature toggle states

**Expected Results:**
| Feature | Expected State | Pass/Fail |
|---------|---------------|-----------|
| Generative Actions | Enabled | ☐ |
| Preview Features | Enabled | ☐ |
| Web Search Tool | Enabled | ☐ |
| Code Interpreter | Enabled | ☐ |
| Multi-Agent Orchestration | Enabled | ☐ |

**Pass Criteria:** Zone 1 allows all Microsoft default features without restrictive controls.

**Evidence:** Screenshot of Zone 1 environment feature settings.

---

## Test Suite 2: Runtime Feature Restriction Enforcement

### Test 2.1: Attempt to Enable Prohibited Feature in Zone 3

**Objective:** Verify that prohibited features cannot be enabled in Zone 3 agents.

**Prerequisites:**
- Access to Copilot Studio
- Zone 3 environment with generative actions disabled

**Steps:**
1. Open Copilot Studio and select the Zone 3 test environment
2. Create a new test agent or open an existing agent
3. Attempt to add a generative action:
   - Click **+ Add action** → **Create generative action**
4. If the option is available, attempt to configure and save the generative action
5. Observe the result

**Expected Results:**
- Option A: "Create generative action" is not available in the action menu
- Option B: Attempting to create generative action displays error: "Generative actions are not enabled in this environment"
- Option C: Agent cannot be saved with generative action (validation error)

**Pass Criteria:** Generative action cannot be successfully added to Zone 3 agent.

**Evidence:** Screenshot showing error message or unavailable option.

---

### Test 2.2: Attempt to Enable Code Interpreter in Zone 3

**Objective:** Verify Code Interpreter is disabled in Zone 3.

**Prerequisites:**
- Zone 3 environment with Code Interpreter disabled

**Steps:**
1. In Copilot Studio, open a Zone 3 agent
2. Navigate to **Settings** → **Tools**
3. Locate the **Code Interpreter** toggle
4. Attempt to toggle Code Interpreter on
5. Observe the result

**Expected Results:**
- Option A: Code Interpreter toggle is grayed out (disabled)
- Option B: Toggle appears enabled, but clicking displays error: "This tool is not available in this environment"
- Option C: Tooltip displays: "Code Interpreter is restricted in this environment"

**Pass Criteria:** Code Interpreter cannot be enabled.

**Evidence:** Screenshot of disabled toggle or error message.

---

### Test 2.3: Verify Restricted Feature Works in Zone 2 After Approval

**Objective:** Confirm that a restricted feature (e.g., Web Search) can be enabled in Zone 2 after approval.

**Prerequisites:**
- Zone 2 environment with Web Search in "Restricted" status
- Approval record in feature catalog for Web Search in this environment

**Steps:**
1. Open Copilot Studio and select Zone 2 environment
2. Open an approved agent that should have Web Search access
3. Navigate to **Settings** → **Tools**
4. Toggle **Web Search** on
5. Save the agent
6. Test the agent's web search functionality

**Expected Results:**
- Web Search toggle is enabled and functional
- Agent can perform web searches during conversation
- No error messages or restrictions

**Pass Criteria:** Web Search works correctly after documented approval.

**Evidence:** Screenshot of Web Search enabled + test conversation showing search results.

---

## Test Suite 3: DLP Policy Enforcement

### Test 3.1: Verify Blocked Connector Is Not Available in Zone 3

**Objective:** Confirm DLP policies block prohibited connectors.

**Prerequisites:**
- Zone 3 DLP policy with HTTP connector in "Blocked" group
- Zone 3 environment

**Steps:**
1. In Copilot Studio, open a Zone 3 agent
2. Click **+ Add action** → **Call an action from a connector**
3. In the connector search, search for "HTTP"
4. Observe the search results

**Expected Results:**
- HTTP connector does not appear in search results
- OR HTTP connector appears with "Blocked" badge and cannot be selected
- Attempting to add HTTP action displays error: "This connector is blocked by your organization's data policy"

**Pass Criteria:** HTTP connector is not usable in Zone 3 agent.

**Evidence:** Screenshot showing blocked connector or empty search results.

---

### Test 3.2: Verify Allowed Connector Works in Zone 3

**Objective:** Confirm approved connectors in DLP policy are functional.

**Prerequisites:**
- Zone 3 DLP policy with SharePoint connector in "Business" group
- Zone 3 environment

**Steps:**
1. In Copilot Studio, open a Zone 3 agent
2. Add an action using the SharePoint connector
3. Configure the action (e.g., "Get files from folder")
4. Save the agent
5. Test the SharePoint action in agent conversation

**Expected Results:**
- SharePoint connector is available and selectable
- Action configuration completes without errors
- Agent successfully retrieves data from SharePoint during test

**Pass Criteria:** Approved connector works without restrictions.

**Evidence:** Screenshot of SharePoint action configuration + test conversation showing successful data retrieval.

---

### Test 3.3: Verify DLP Policy Prevents Saving Agent with Blocked Connector

**Objective:** Confirm DLP prevents saving agents that use prohibited connectors.

**Prerequisites:**
- Zone 3 environment
- Agent with a connector that is later moved to "Blocked" group

**Steps:**
1. Create a test agent in Zone 3 with an allowed connector (e.g., HTTP in Zone 1, then move to Zone 3)
2. Update the Zone 3 DLP policy to move HTTP connector to "Blocked" group
3. Attempt to open and edit the agent in Copilot Studio
4. Make any change and attempt to save

**Expected Results:**
- Error message displays: "This agent uses connectors that are blocked by your organization's data policy and cannot be saved"
- Error message lists the blocked connector(s): "Remove the [HTTP] action to continue"
- Save button is disabled or save fails

**Pass Criteria:** Agent cannot be saved with blocked connector.

**Evidence:** Screenshot of error message preventing save.

---

## Test Suite 4: Feature Catalog Validation

### Test 4.1: Verify Feature Catalog Contains All Default Features

**Objective:** Confirm feature catalog is populated with baseline features.

**Prerequisites:**
- Feature catalog deployed to Dataverse (via PowerShell script)

**Steps:**
1. Open Power Apps (make.powerapps.com)
2. Navigate to **Tables** → **fsi_featurecatalog**
3. Click **Data** tab to view records
4. Review the list of features

**Expected Results:**
Feature catalog contains at minimum:
- Generative Actions (AI Builder)
- Web Search Tool
- Code Interpreter
- Custom Plugins
- Multi-Agent Orchestration
- Preview Features (General)
- SharePoint Connector
- Dataverse Connector
- HTTP Connector

**Pass Criteria:** All baseline features are present with correct zone status (Zone 1/2/3).

**Evidence:** Screenshot of feature catalog data view showing 9+ feature records.

---

### Test 4.2: Verify Feature Approval Record Includes Required Fields

**Objective:** Confirm approved features have complete approval metadata.

**Prerequisites:**
- At least one approved feature with a change ticket

**Steps:**
1. In feature catalog table, locate a feature with "Restricted" status in Zone 2 or Zone 3
2. Review the record fields

**Expected Results:**
Record includes:
- ☐ Feature Name (populated)
- ☐ Zone Status (Restricted)
- ☐ Approval Required (Yes)
- ☐ Approval Date (populated)
- ☐ Change Ticket (populated with ticket reference)
- ☐ Risk Rating (High/Medium/Low)
- ☐ Justification (text explaining approval rationale)

**Pass Criteria:** All required fields are populated for approved features.

**Evidence:** Screenshot of complete feature record.

---

### Test 4.3: Verify Time-Bound Exception Has Expiration Date

**Objective:** Confirm time-bound feature exceptions include expiration tracking.

**Prerequisites:**
- At least one temporary feature exception (e.g., preview feature enabled in Zone 2 for 90-day evaluation)

**Steps:**
1. In feature catalog, locate a time-bound exception record
2. Review the Expiration Date field

**Expected Results:**
- Expiration Date field is populated with future date
- Justification field explains this is a temporary exception
- Change Ticket field references the approval with time-bound clause

**Pass Criteria:** Exception includes expiration date and supporting documentation.

**Evidence:** Screenshot of exception record with expiration date.

---

## Test Suite 5: Change Management Workflow

### Test 5.1: Submit Feature Enablement Request for Zone 2

**Objective:** Test change management workflow for Zone 2 feature request.

**Prerequisites:**
- Change management system configured with Copilot Studio Feature Enablement template
- Test user account with agent author permissions

**Steps:**
1. As a test agent author, submit a change request to enable Web Search tool in Zone 2 environment
2. Complete all required fields:
   - Feature Name: Web Search Tool
   - Environment: Zone 2 Production
   - Business Justification: "Customer support agents need real-time product information"
   - Risk Assessment: "Medium risk - potential for inaccurate information retrieval"
   - Compensating Controls: "Human review before sending to customer; domain restrictions"
3. Submit the request
4. As Power Platform Admin, review and approve the request
5. As AI Governance Lead, review and approve the request
6. Verify approval notification is sent to requester

**Expected Results:**
- Change request is submitted successfully
- Approval workflow routes to Power Platform Admin → AI Governance Lead
- Both approvers can review justification and risk assessment
- After final approval, requester receives notification
- Request status changes to "Approved"

**Pass Criteria:** Workflow completes with all approvals and notifications.

**Evidence:** Screenshots of change request at each workflow stage.

---

### Test 5.2: Submit Feature Enablement Request for Zone 3 (Requires Compliance Officer)

**Objective:** Verify Zone 3 requests require additional approval from Compliance Officer.

**Prerequisites:**
- Change management workflow with Zone 3 approval path

**Steps:**
1. Submit a change request to enable a high-risk feature in Zone 3 (e.g., generative actions for specific use case)
2. Include formal risk assessment document (1-2 pages)
3. Verify workflow routes to: Power Platform Admin → AI Governance Lead → Compliance Officer
4. As Compliance Officer, review and approve (or reject if compensating controls are insufficient)

**Expected Results:**
- Workflow requires three approvals for Zone 3
- Compliance Officer receives request with risk assessment attachment
- Request cannot be implemented until Compliance Officer approves
- If rejected, feedback is provided to requester

**Pass Criteria:** Zone 3 workflow enforces Compliance Officer approval.

**Evidence:** Screenshot of workflow showing three approval stages.

---

### Test 5.3: Verify Feature Catalog Is Updated After Approval

**Objective:** Confirm feature catalog is updated when feature is approved.

**Prerequisites:**
- Approved change request from Test 5.1 or 5.2

**Steps:**
1. After change request is approved, check the feature catalog table
2. Locate the feature record (e.g., Web Search Tool)
3. Verify the record is updated with approval details

**Expected Results:**
- Approval Date field is populated with today's date
- Change Ticket field contains the change request ID
- Zone 2 (or Zone 3) Status field reflects the approved status (Restricted or Allowed)
- Justification field includes the approved use case

**Pass Criteria:** Feature catalog reflects the approved change.

**Evidence:** Screenshot of updated feature record showing approval metadata.

---

## Test Suite 6: Compliance Reporting

### Test 6.1: Generate Feature Compliance Report

**Objective:** Verify PowerShell script generates accurate compliance report.

**Prerequisites:**
- Feature catalog populated with test data
- PowerShell script `Get-FeatureComplianceReport.ps1` available

**Steps:**
1. Run the PowerShell script:
   ```powershell
   .\Get-FeatureComplianceReport.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\TestReports"
   ```
2. Review the generated CSV file
3. Check for expiration alerts (if any time-bound exceptions exist)

**Expected Results:**
- CSV file is created with filename: `FeatureComplianceReport_[timestamp].csv`
- Report includes all features from catalog with columns:
  - FeatureName, Category, Zone1Status, Zone2Status, Zone3Status, ApprovalDate, ChangeTicket, ExpirationDate, RiskRating
- If features are expiring within 30 days, a separate alerts file is generated: `FeatureExpirationAlerts_[timestamp].csv`
- Console displays summary statistics: Total Features, High/Medium/Low Risk counts, Zone 3 Prohibited count

**Pass Criteria:** Report is generated successfully with accurate data.

**Evidence:** Screenshot of PowerShell console output + CSV file contents.

---

### Test 6.2: Verify Expiration Alert for Time-Bound Exception

**Objective:** Confirm expiration alerts are generated for features nearing expiration.

**Prerequisites:**
- Feature catalog record with Expiration Date within 30 days (or past date for testing)

**Steps:**
1. Manually create or update a feature record with Expiration Date = 15 days from today
2. Run `Get-FeatureComplianceReport.ps1`
3. Review the expiration alerts file

**Expected Results:**
- Expiration alerts CSV file is generated
- File contains the feature with 15 days to expiration
- ExpirationAlert column shows: "EXPIRES SOON (15 days)"
- Console displays warning message: "⚠ WARNING: 1 feature(s) have expired or expiring exceptions!"

**Pass Criteria:** Alert is triggered and reported correctly.

**Evidence:** Screenshot of alerts file and console warning.

---

### Test 6.3: Validate DLP Enforcement Report

**Objective:** Verify DLP validation script detects non-compliant policies.

**Prerequisites:**
- Zone 3 DLP policy with HTTP connector in Business group (intentionally misconfigured for test)
- PowerShell script `Test-DLPEnforcement.ps1` available

**Steps:**
1. Temporarily move HTTP connector from "Blocked" to "Business" group in Zone 3 DLP policy
2. Run the DLP validation script:
   ```powershell
   .\Test-DLPEnforcement.ps1
   ```
3. Review the output and CSV report

**Expected Results:**
- Script detects HTTP connector in Business group for Zone 3 policy
- Console displays: "✗ shared_http is NOT blocked (should be blocked for high-risk environments)"
- CSV report includes row with Compliance = "NON-COMPLIANT"
- Console summary shows: "⚠ WARNING: 1 non-compliant connector(s) found!"

**Pass Criteria:** Non-compliant configuration is detected and reported.

**Evidence:** Screenshot of console output showing non-compliant connector.

**Cleanup:** Move HTTP connector back to "Blocked" group after test.

---

## Test Suite 7: User Experience Validation

### Test 7.1: Verify Feature Restriction Error Message Is Clear

**Objective:** Ensure users receive helpful error messages when attempting to use restricted features.

**Prerequisites:**
- Zone 3 environment with generative actions disabled

**Steps:**
1. As an agent author (non-admin), attempt to add generative action in Zone 3 agent
2. Read the error message displayed

**Expected Results:**
Error message includes:
- Clear explanation: "Generative actions are not enabled in this environment"
- Guidance: "Contact [Governance Team / Power Platform Admin] for approval"
- Reason (optional): "This environment is classified as Zone 3 (Enterprise) with restricted feature access"

**Pass Criteria:** Error message is informative and includes contact information.

**Evidence:** Screenshot of error message.

---

### Test 7.2: Verify Agent Author Can See Allowed Features in Zone 1

**Objective:** Confirm Zone 1 users have unrestricted access to default features.

**Prerequisites:**
- Zone 1 environment
- Non-admin agent author account

**Steps:**
1. As agent author in Zone 1, open Copilot Studio
2. Create a new agent
3. Explore available features:
   - Add generative action (should work)
   - Enable Web Search tool (should work)
   - Enable preview features in Settings (should work)
4. Save and test the agent

**Expected Results:**
- All features are available without approval
- No error messages or restrictions
- Agent functions correctly with enabled features

**Pass Criteria:** Agent author has full feature access in Zone 1.

**Evidence:** Screenshot of agent with multiple features enabled.

---

## Test Results Summary Template

| Test ID | Test Name | Status | Notes | Evidence |
|---------|-----------|--------|-------|----------|
| 1.1 | Zone 3 Restrictive Settings | ☐ Pass ☐ Fail | | Screenshot: |
| 1.2 | Zone 2 Moderate Restrictions | ☐ Pass ☐ Fail | | Screenshot: |
| 1.3 | Zone 1 Permissive Settings | ☐ Pass ☐ Fail | | Screenshot: |
| 2.1 | Prohibited Feature in Zone 3 | ☐ Pass ☐ Fail | | Screenshot: |
| 2.2 | Code Interpreter Disabled | ☐ Pass ☐ Fail | | Screenshot: |
| 2.3 | Restricted Feature After Approval | ☐ Pass ☐ Fail | | Screenshot: |
| 3.1 | DLP Blocks Connector | ☐ Pass ☐ Fail | | Screenshot: |
| 3.2 | DLP Allows Connector | ☐ Pass ☐ Fail | | Screenshot: |
| 3.3 | DLP Prevents Save | ☐ Pass ☐ Fail | | Screenshot: |
| 4.1 | Feature Catalog Populated | ☐ Pass ☐ Fail | | Screenshot: |
| 4.2 | Approval Record Complete | ☐ Pass ☐ Fail | | Screenshot: |
| 4.3 | Exception Has Expiration | ☐ Pass ☐ Fail | | Screenshot: |
| 5.1 | Zone 2 Change Workflow | ☐ Pass ☐ Fail | | Screenshot: |
| 5.2 | Zone 3 Requires Compliance | ☐ Pass ☐ Fail | | Screenshot: |
| 5.3 | Catalog Updated After Approval | ☐ Pass ☐ Fail | | Screenshot: |
| 6.1 | Compliance Report Generated | ☐ Pass ☐ Fail | | Screenshot: |
| 6.2 | Expiration Alert Triggered | ☐ Pass ☐ Fail | | Screenshot: |
| 6.3 | DLP Validation Detects Issue | ☐ Pass ☐ Fail | | Screenshot: |
| 7.1 | Clear Error Messages | ☐ Pass ☐ Fail | | Screenshot: |
| 7.2 | Zone 1 Feature Access | ☐ Pass ☐ Fail | | Screenshot: |

**Overall Test Results:**
- Total Tests: 19
- Passed: ___
- Failed: ___
- Pass Rate: ___%

**Tested By:** ___________________  
**Date:** ___________________  
**Environment:** ___________________

---

## Acceptance Criteria

Control 2.24 is considered successfully implemented if:

1. ✅ All Zone 3 environments have high-risk features disabled (generative actions, preview features, code interpreter)
2. ✅ Zone 2 environments enforce documented approval for restricted features
3. ✅ Zone 1 environments allow Microsoft default features without restrictions
4. ✅ DLP policies correctly block prohibited connectors in runtime
5. ✅ Feature catalog is deployed with all baseline features and approval tracking
6. ✅ Change management workflow routes Zone 2/3 requests through required approvers
7. ✅ Feature catalog is updated after approvals with change ticket references
8. ✅ Compliance reporting generates accurate feature status and expiration alerts
9. ✅ Users receive clear error messages when attempting to use restricted features
10. ✅ Quarterly feature risk assessment process is documented and scheduled

---

## Continuous Monitoring

After implementation, establish continuous monitoring:

- **Weekly:** Review feature usage logs for unauthorized attempts to use restricted features
- **Monthly:** Generate feature compliance report and review with AI Governance Lead
- **Quarterly:** Conduct feature risk assessment and update zone restrictions
- **On-Demand:** After each Microsoft feature release, assess new capabilities and update catalog

---

[Back to Control 2.24](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
