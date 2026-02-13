# Portal Walkthrough: Control 2.24 - Agent Feature Enablement and Restriction Governance

**Last Updated:** February 2026
**Portal:** Power Platform Admin Center (PPAC), Copilot Studio
**Estimated Time:** 35-45 minutes

## Prerequisites

- [ ] Power Platform Admin role (for PPAC configuration)
- [ ] Entra Global Admin role (for tenant-wide feature decisions)
- [ ] Access to Power Platform Admin Center and Copilot Studio
- [ ] Knowledge of environment tier classifications (Control 2.2)
- [ ] List of governance zones and their corresponding environments
- [ ] Draft feature governance policy document
- [ ] Change management process for feature enablement

---

## Step-by-Step Configuration

### Part 1: PPAC Copilot Governance Dashboard Configuration

#### Step 1: Navigate to Copilot Governance Page

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Sign in with Power Platform Admin credentials
3. In the left navigation, click **Copilot** (may be under a "Features" or "Governance" section)
4. Click **Governance** to open the Copilot governance dashboard
5. Review the governance page layout:
   - Tenant-wide feature toggles (top section)
   - Environment-specific feature controls (middle section)
   - Agent sharing and distribution settings (bottom section)

> **Note:** The Copilot governance page provides centralized control over Copilot Studio features across all environments. This is the primary configuration surface for Control 2.24. If you do not see this page, verify your role has Power Platform Admin permissions and check Message Center for feature availability announcements.

#### Step 2: Review Tenant-Wide Feature Toggles

1. In the Copilot governance dashboard, locate the **Tenant settings** or **Global features** section
2. Review available tenant-wide feature toggles:
   - **Copilot Studio enabled:** Master toggle for Copilot Studio availability (should be On)
   - **Generative AI features:** Toggle for AI Builder generative actions across all environments
   - **Preview features:** Toggle for access to preview/experimental capabilities
   - **Agent sharing:** Controls for how agents can be shared and distributed
   - **Multi-agent orchestration:** Enablement of agent-to-agent communication
3. Document the current state of each tenant-wide toggle (take screenshots for baseline documentation)
4. Do not make changes yet — first assess impact on existing agents and environments

> **Zone 3 Consideration:** For organizations with Zone 3 (Enterprise) environments, tenant-wide toggles should be set conservatively (generative AI and preview features disabled unless explicit exception process is in place). Use environment-specific overrides to enable features in Zone 1/2.

#### Step 3: Configure Environment-Specific Feature Controls

1. In the Copilot governance dashboard, scroll to the **Environment settings** section
2. Review the list of environments displayed:
   - Each environment should show: Environment name, Type (Production/Sandbox), Features enabled count
3. Click on a **Zone 3 (Enterprise)** environment to open its feature configuration panel
4. Review environment-specific feature toggles:
   - **Generative actions:** Disable (unless specific actions are approved)
   - **Preview features:** Ensure this is Disabled/Off
   - **Web search tool:** Disable or restrict to explicit allowlist
   - **Code interpreter:** Ensure this is Disabled
   - **Custom plugins:** Restrict to approved plugin list
   - **Multi-agent orchestration:** Disable or set to "Requires approval"
5. Click **Save** to apply Zone 3 environment restrictions
6. Repeat for all Zone 3 environments in your tenant

> **Best Practice:** Start with Zone 3 (most restrictive), then configure Zone 2 and Zone 1. This ensures your highest-risk environments are secured first, and you can progressively enable features for lower-risk zones.

#### Step 4: Configure Zone 2 (Team) Environment Features

1. In the environment settings section, click on a **Zone 2 (Team)** environment
2. Configure Zone 2 feature toggles:
   - **Generative actions:** Enable (with documented approval process for specific actions)
   - **Preview features:** Disable (unless temporary enablement is approved via change management)
   - **Web search tool:** Enable with restrictions (approved agents only)
   - **Code interpreter:** Disable (high-risk feature)
   - **Custom plugins:** Enable with plugin allowlist
   - **Multi-agent orchestration:** Enable with depth limit (max 2 levels)
3. Document which features are enabled and the rationale for each decision
4. Click **Save** to apply Zone 2 environment configuration
5. Repeat for all Zone 2 environments

> **Zone 2 Requirement:** Generative AI features are allowed in Zone 2, but each specific generative action used by agents must have documented approval. Maintain a feature approval log (created in Part 3) tracking: Feature name, Agent name, Approval date, Approver, Change ticket.

#### Step 5: Configure Zone 1 (Personal) Environment Features

1. In the environment settings section, click on a **Zone 1 (Personal)** environment
2. Configure Zone 1 feature toggles:
   - **Generative actions:** Enable (Microsoft default)
   - **Preview features:** Enable (for testing and innovation)
   - **Web search tool:** Enable
   - **Code interpreter:** Enable (personal productivity only)
   - **Custom plugins:** Enable (user-installed plugins allowed)
   - **Multi-agent orchestration:** Enable with monitoring
3. Zone 1 allows most features for personal productivity and testing
4. Implement periodic review process (quarterly) to assess feature usage and risk
5. Click **Save** to apply Zone 1 environment configuration

> **Zone 1 Testing:** Personal productivity environments serve as testing grounds for new features before promotion to Zone 2/3. Require summary reports of preview feature usage and lessons learned before enabling features in higher zones.

---

### Part 2: Feature-Specific Configuration (DLP Integration)

#### Step 6: Configure DLP Policies for Feature Restrictions

1. In PPAC, navigate to **Data policies** (left navigation under "Policies")
2. Select or create a DLP policy for **Zone 3 environments**
3. Review the policy's environment scope:
   - Ensure all Zone 3 environments are included
   - Exclude Zone 1/2 environments (they will have separate policies)
4. Configure connector restrictions that enforce feature limits:
   - **AI Builder connector:** Move to "Blocked" group if generative actions are prohibited
   - **HTTP connector:** Block to prevent custom API calls that bypass controls
   - **Custom connectors:** Block unless explicitly approved and added to allowlist
   - **Premium connectors:** Review and block high-risk connectors (e.g., Code Interpreter, unapproved data sources)
5. Click **Save** to apply the DLP policy

> **Integration Note:** DLP policies (Control 1.4) enforce feature restrictions at runtime by blocking prohibited connectors. This is a critical enforcement layer for Control 2.24. Even if a feature toggle is on, DLP policies can prevent agents from using specific capabilities.

#### Step 7: Configure Connector Allowlist for Approved Features

1. In the Zone 3 DLP policy, review the "Business" connector group
2. Add connectors for explicitly approved features:
   - **SharePoint:** Allowed for document retrieval (if approved)
   - **Dataverse:** Allowed for internal data access (if approved)
   - **Microsoft 365 Users:** Allowed for user lookup (if approved)
3. Document each allowed connector with:
   - **Connector name**
   - **Approval date and change ticket reference**
   - **Use case justification**
   - **Risk rating (Low/Medium/High)**
4. For Zone 2 and Zone 1, repeat the process with progressively more permissive connector lists
5. Save each DLP policy and test connector restrictions by attempting to add a blocked connector in Copilot Studio

> **Testing DLP Restrictions:** After configuring DLP policies, test in Copilot Studio by attempting to add a blocked connector to an agent in a Zone 3 environment. The connector should not appear in the connector list, or an error message should display: "This connector is blocked by your organization's data policy."

---

### Part 3: Feature Catalog Deployment

#### Step 8: Create Feature Catalog in Dataverse or SharePoint

Option A: **Dataverse Table** (Recommended for programmatic access)

1. Open [Power Apps](https://make.powerapps.com) and select a **default environment** (not Zone 3)
2. Navigate to **Tables** in the left navigation
3. Click **+ New table** → **Start from blank**
4. Name the table: `fsi_featurecatalog`
5. Add the following columns (fields):
   - **fsi_featurename** (Single line of text) — Feature name (e.g., "Generative Actions", "Web Search")
   - **fsi_featurecategory** (Choice) — Options: Generative Actions, Preview Feature, Tool, Plugin, Orchestration, Other
   - **fsi_zone1status** (Choice) — Options: Allowed, Restricted, Prohibited
   - **fsi_zone2status** (Choice) — Options: Allowed, Restricted, Prohibited
   - **fsi_zone3status** (Choice) — Options: Allowed, Restricted, Prohibited
   - **fsi_approvalrequired** (Yes/No) — Whether documented approval is needed
   - **fsi_approvaldate** (Date) — Date feature was approved for use
   - **fsi_changeticket** (Single line of text) — Change management ticket reference
   - **fsi_expirationdate** (Date) — For time-bound exceptions
   - **fsi_riskrating** (Choice) — Options: High, Medium, Low
   - **fsi_justification** (Multiple lines of text) — Business justification for feature enablement
6. Click **Create** to deploy the table
7. Navigate to **Data** tab and add initial feature records (see Step 9)

Option B: **SharePoint List** (Simpler for non-technical teams)

1. Open your governance SharePoint site
2. Create a new list named "Feature Catalog"
3. Add the same columns as the Dataverse table above (using SharePoint column types: Single line of text, Choice, Date, Yes/No)
4. Configure list permissions: Read access for all agent authors, Edit access for Power Platform Admins and Governance Team
5. Add initial feature records (see Step 9)

#### Step 9: Populate Feature Catalog with Initial Data

Add feature records for common Copilot Studio capabilities:

| Feature Name | Category | Zone 1 | Zone 2 | Zone 3 | Approval Required | Risk Rating |
|--------------|----------|--------|--------|--------|-------------------|-------------|
| Generative Actions (AI Builder) | Generative Actions | Allowed | Restricted | Prohibited | Yes (Zone 2/3) | High |
| Web Search Tool | Tool | Allowed | Restricted | Prohibited | Yes (Zone 2/3) | Medium |
| Code Interpreter | Tool | Allowed | Prohibited | Prohibited | Yes (Zone 1 only) | High |
| Custom Plugins | Plugin | Allowed | Restricted | Restricted | Yes (Zone 2/3) | Medium |
| Multi-Agent Orchestration | Orchestration | Allowed | Restricted | Prohibited | Yes (Zone 2/3) | Medium |
| Preview Features (General) | Preview Feature | Allowed | Prohibited | Prohibited | Yes (Zone 2/3 exceptions) | High |
| SharePoint Connector | Connector | Allowed | Allowed | Restricted | Yes (Zone 3) | Low |
| Dataverse Connector | Connector | Allowed | Allowed | Restricted | Yes (Zone 3) | Low |
| HTTP Connector | Connector | Allowed | Restricted | Prohibited | Yes (Zone 2/3) | High |

1. For each feature, create a record in the Dataverse table or SharePoint list
2. Fill in all required fields based on your organization's feature governance policy
3. For "Restricted" features, add justification text explaining under what conditions the feature is allowed
4. For "Prohibited" features, document compensating controls if the feature must be enabled due to business requirements

> **Maintenance Note:** Update the feature catalog quarterly or when Microsoft releases new Copilot Studio features. Monitor Message Center for announcements of new capabilities and add them to the catalog with appropriate zone status.

---

### Part 4: Change Management Integration

#### Step 10: Create Feature Enablement Change Request Template

1. In your change management system (ServiceNow, Jira, SharePoint, etc.), create a new change request template: "Copilot Studio Feature Enablement"
2. Include the following fields in the template:
   - **Feature Name:** Name of the Copilot Studio feature to be enabled
   - **Environment(s):** Target environment(s) where feature will be enabled
   - **Governance Zone:** Zone 1, Zone 2, or Zone 3
   - **Requestor:** Agent author or business owner requesting feature access
   - **Business Justification:** Why the feature is needed and expected benefits
   - **Risk Assessment:** Security and compliance risks introduced by the feature
   - **Compensating Controls:** Controls to mitigate identified risks
   - **Approval Required From:** Power Platform Admin, Compliance Officer (Zone 2/3), AI Governance Lead (Zone 3)
   - **Implementation Date:** Planned date for feature enablement
   - **Expiration Date:** For time-bound exceptions, date when feature access expires
   - **Rollback Plan:** How to disable the feature if issues arise
3. Configure approval workflow:
   - **Zone 1 requests:** Power Platform Admin approval only
   - **Zone 2 requests:** Power Platform Admin + AI Governance Lead approval
   - **Zone 3 requests:** Power Platform Admin + Compliance Officer + AI Governance Lead approval
4. Test the workflow by submitting a test feature enablement request

> **Best Practice:** For Zone 3 feature requests, require a formal risk assessment document (1-2 pages) analyzing: (1) security implications, (2) regulatory impact, (3) compensating controls, (4) alternative solutions considered. This documentation supports regulatory examination and demonstrates due diligence.

#### Step 11: Process a Sample Feature Enablement Request

Walk through a feature enablement scenario to test the change management process:

**Scenario:** A Zone 2 agent author requests enabling the Web Search tool for a customer support agent.

1. **Requester submits change request:**
   - Feature Name: Web Search Tool
   - Environment: Zone 2 Production (Customer Support environment)
   - Governance Zone: Zone 2
   - Business Justification: "Customer support agents need to search for current product information and troubleshooting articles to answer customer inquiries in real-time."
   - Risk Assessment: "Web search introduces potential for retrieval of inaccurate or outdated information. Risk: Medium."
   - Compensating Controls: "Web search limited to approved domains only; agent responses reviewed by human before sending to customer; search queries logged for audit."
2. **Power Platform Admin reviews:**
   - Verify feature is "Restricted" (not "Prohibited") in Zone 2 feature catalog
   - Confirm business justification is reasonable
   - Check that compensating controls are adequate
   - Approve or request additional information
3. **AI Governance Lead reviews (Zone 2 requirement):**
   - Assess whether compensating controls meet governance standards
   - Verify no regulatory concerns with web search usage
   - Approve or escalate to Compliance Officer
4. **Implementation:**
   - Power Platform Admin enables Web Search tool in Zone 2 environment (Copilot governance page)
   - Update feature catalog with approval date and change ticket reference
   - Configure DLP policy to allow required connectors (if needed)
   - Notify requester that feature is available
5. **Documentation:**
   - Record approval in change management system
   - Update feature catalog: Approval Date, Change Ticket, Justification
   - Add to agent registry that this agent uses Web Search tool

> **Audit Trail:** All feature enablement changes for Zone 2/3 must have: (1) change ticket in change management system, (2) approval record from required stakeholders, (3) feature catalog entry, (4) notification to affected users. This audit trail is critical for regulatory examination.

---

### Part 5: Verification and Testing

#### Step 12: Test Feature Restrictions by Zone

Test that feature restrictions are enforced in each governance zone:

**Test 1: Zone 3 — Attempt to Enable Prohibited Feature**

1. Open [Copilot Studio](https://copilotstudio.microsoft.com) and select a **Zone 3 environment**
2. Create a new test agent or open an existing Zone 3 agent
3. In the agent authoring canvas, attempt to add a **generative action** (if prohibited in Zone 3):
   - Click **+ Add action** → **Create generative action**
   - Expected result: Either the option is not available, or an error displays: "Generative actions are not enabled in this environment"
4. Attempt to enable **Code Interpreter** tool:
   - Navigate to agent settings → Tools
   - Try to toggle Code Interpreter on
   - Expected result: Toggle is disabled or error message displays
5. Document test results with screenshots

**Test 2: Zone 2 — Verify Restricted Features Require Approval**

1. Switch to a **Zone 2 environment** in Copilot Studio
2. Attempt to add **Web Search** tool to an agent:
   - If Web Search is in "Restricted" status, verify that it appears in the tool list but has a warning icon or tooltip: "This tool requires approval for use in this environment"
   - If approval process is implemented via DLP, verify the connector is available after approval but blocked before approval
3. Test with an approved feature (one with a change ticket in the feature catalog):
   - Verify the feature is available and functional
   - Confirm no error messages or warnings
4. Document test results

**Test 3: Zone 1 — Verify All Default Features Are Available**

1. Switch to a **Zone 1 environment** in Copilot Studio
2. Verify that all Microsoft default features are available:
   - Generative actions: Available and functional
   - Web Search: Available
   - Code Interpreter: Available (if personal environment)
   - Custom plugins: Available for installation
   - Preview features: Visible in Settings → Preview features
3. Test enabling a preview feature:
   - Navigate to Settings → Preview features
   - Toggle a preview feature on
   - Expected result: Feature is enabled without approval workflow (Zone 1 allows testing)
4. Document test results and feature usage for quarterly review

#### Step 13: Validate DLP Policy Enforcement

1. In a **Zone 3 environment**, attempt to add a connector that is blocked by DLP policy:
   - Open an agent in Copilot Studio
   - Click **Add an action** → **Call an action from a connector**
   - Search for a prohibited connector (e.g., HTTP connector if blocked)
   - Expected result: Connector does not appear in the search results, or displays with a "Blocked" badge
2. Attempt to save an agent that uses a blocked connector:
   - If an agent already has a blocked connector (e.g., from before DLP was applied), try to edit and save the agent
   - Expected result: Error message: "This agent uses connectors that are blocked by your organization's data policy and cannot be saved. Remove the [Connector Name] action to continue."
3. Test the same connector in a **Zone 1 environment** where it should be allowed:
   - Verify the connector is available and functional
   - Confirm no blocking error

> **Expected Behavior:** DLP policies provide runtime enforcement of feature restrictions. Even if a feature toggle is on in PPAC, DLP can block specific connectors and actions. This layered approach provides defense in depth.

---

### Part 6: Ongoing Maintenance

#### Step 14: Schedule Quarterly Feature Risk Assessment

1. Add a recurring task (quarterly) to your governance calendar: "Copilot Studio Feature Risk Assessment"
2. For each quarterly review, perform the following:
   - **Review feature catalog:** Identify new features released by Microsoft since last review
   - **Assess risk:** For each new feature, conduct risk assessment: security implications, regulatory impact, potential misuse scenarios
   - **Update zone status:** Assign each new feature to Allowed/Restricted/Prohibited for Zone 1/2/3
   - **Test new features:** In Zone 1 environment, enable and test preview features to understand behavior before allowing in Zone 2/3
   - **Update policies:** Adjust PPAC feature toggles and DLP policies based on risk assessment findings
   - **Communicate changes:** Notify agent authors of newly available or newly restricted features
3. Document each quarterly review with:
   - Date of review
   - Features assessed (new features since last review)
   - Risk ratings assigned
   - Zone status updates
   - Policy changes implemented
   - Approvers and reviewers
4. Store review documentation in governance SharePoint site for audit trail

> **Microsoft Roadmap Monitoring:** Subscribe to Microsoft 365 Roadmap updates for Copilot Studio and Power Platform. New features are announced months in advance. Use this lead time to conduct risk assessments and plan for feature enablement/restriction before features reach General Availability.

#### Step 15: Monitor and Report on Feature Usage

1. Implement monitoring for feature usage across all environments:
   - Use Power Platform Analytics to track agent creation, connector usage, and generative action invocations
   - Query Dataverse audit logs for feature configuration changes
   - Use PowerShell scripts (see PowerShell Setup playbook) to generate feature usage reports
2. Create monthly feature usage report:
   - **Agents by Zone:** Count of agents in each governance zone
   - **Feature Adoption:** Which features are most commonly used in each zone
   - **Exception Tracking:** Time-bound feature exceptions and their expiration status
   - **Compliance Status:** Percentage of agents compliant with zone-specific feature restrictions
   - **Incidents:** Any incidents of unauthorized feature usage or policy violations
3. Review report with AI Governance Lead and Compliance Officer
4. Use report findings to adjust feature restrictions and approval processes

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|---------------------|
| **Generative AI features (PPAC toggle)** | Enabled | Enabled with approval | Disabled (explicit allowlist) |
| **Preview/experimental features** | Enabled for testing | Disabled (exceptions with approval) | Prohibited |
| **Web Search tool** | Enabled | Restricted (approved agents) | Prohibited or explicit allowlist |
| **Code Interpreter** | Enabled | Prohibited | Prohibited |
| **Custom plugins** | Enabled | Approved plugins only | Explicit allowlist |
| **Multi-agent orchestration** | Enabled with monitoring | Depth limit (max 2 levels) | Prohibited or approval required |
| **DLP policy enforcement** | Basic (default connectors) | Moderate (approved connectors) | Strict (explicit allowlist) |
| **Feature catalog maintenance** | Quarterly review | Monthly update | Monthly update + risk assessment |
| **Change management for feature changes** | Recommended | Required (Power Platform Admin + AI Governance Lead) | Required (+ Compliance Officer) |
| **Feature usage reporting** | Quarterly | Monthly | Monthly + incident tracking |

---

## Validation

After completing these steps, verify:

- [ ] PPAC Copilot governance page is configured with environment-specific feature restrictions for all Zone 1/2/3 environments
- [ ] Zone 3 environments have preview/experimental features disabled (or documented exceptions)
- [ ] Generative AI features are disabled in Zone 3 (or explicit allowlist is maintained)
- [ ] DLP policies enforce feature restrictions by blocking prohibited connectors in Zone 2/3
- [ ] Feature catalog (Dataverse or SharePoint) is deployed with initial feature records
- [ ] Change management template for feature enablement is created and tested
- [ ] Feature restriction testing confirms prohibited features are blocked in appropriate zones
- [ ] Quarterly feature risk assessment is scheduled in governance calendar
- [ ] Feature usage monitoring and reporting is operational
- [ ] All Zone 2/3 feature enablements have corresponding entries in feature catalog with approval date and change ticket

---

## Visual Reference

Expected portal locations:
- **PPAC Copilot Governance:** Power Platform Admin Center → Copilot → Governance
- **Environment-specific features:** PPAC → Copilot → Governance → Environment settings → [Select environment]
- **DLP policies:** PPAC → Data policies → [Select policy] → Connector groups (Business/Non-business/Blocked)
- **Feature catalog (Dataverse):** Power Apps (make.powerapps.com) → Tables → fsi_featurecatalog → Data
- **Feature catalog (SharePoint):** Governance SharePoint site → Feature Catalog list
- **Copilot Studio tools:** Copilot Studio → [Agent] → Settings → Tools (Web Search, Code Interpreter toggles)
- **Preview features:** Copilot Studio → Settings → Preview features

> **UI Note:** The PPAC Copilot governance page provides centralized feature management across environments. If specific feature toggles are not available in your tenant, they may be controlled by Microsoft support only (document as compensating control gap). Contact Microsoft support for assistance with disabling GA features that lack self-service toggles.

---

[Back to Control 2.24](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
