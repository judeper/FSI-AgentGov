# Portal Walkthrough: Control 1.28 - Policy-Based Agent Publishing Restrictions

**Last Updated:** February 2026
**Portal:** Power Platform Admin Center + Copilot Studio
**Estimated Time:** 30-45 minutes

## Prerequisites

- [ ] Power Platform Admin or Entra Global Admin role
- [ ] Access to Power Platform Admin Center
- [ ] Access to Copilot Studio environment
- [ ] Knowledge of agent governance zone classifications
- [ ] Approved DLP policy design (Zone 2+ environments)

---

## Step-by-Step Configuration

### Step 1: Configure Tenant-Level DLP Policies

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Click **Policies** in the left navigation
3. Click **Data policies** to view existing DLP policies
4. Click **+ New Policy** to create a zone-specific DLP policy
5. Enter policy details:
   - **Policy Name:** Zone 3 Enterprise - Restricted DLP Policy
   - **Description:** Enforces connector restrictions for Zone 3 customer-facing agents
   - **Scope:** Select specific environments (or environment groups)
6. Click **Next** to configure connector classification

> **Note:** DLP policies are the primary enforcement mechanism for publishing restrictions. Agents with DLP violations cannot be published, and published agents are blocked from updates until violations are resolved (enforced since February 2025).

### Step 2: Classify Connectors by Zone

1. On the **Assign Connectors** page, review the three connector categories:
   - **Business:** Connectors allowed for business data (e.g., SharePoint, Dataverse)
   - **Non-Business:** Connectors allowed for non-business data (e.g., Twitter, RSS)
   - **Blocked:** Connectors prohibited in this environment
2. Configure connector classification by zone:

   **Zone 1 (Personal) Policy:**
   - Business: SharePoint, Dataverse, Office 365, Microsoft Teams
   - Non-Business: Twitter, RSS, HTTP, Weather
   - Blocked: Public websites connector, Telegram, Facebook

   **Zone 2 (Team) Policy:**
   - Business: SharePoint, Dataverse, Office 365, Microsoft Teams, SQL Server
   - Non-Business: (empty)
   - Blocked: Twitter, HTTP, Public websites, Telegram, Facebook, RSS

   **Zone 3 (Enterprise) Policy:**
   - Business: SharePoint (read-only), Dataverse (approved tables only), Microsoft 365 Groups (read-only)
   - Non-Business: (empty)
   - Blocked: All external connectors, HTTP, premium connectors without approval

3. Search for specific connectors using the search bar
4. Drag connectors between categories to reclassify
5. Click **Next** to configure custom connector patterns

> **Zone 3 Critical Restriction:** Block public channels (public websites, Telegram, Facebook) in Zone 3 DLP policies to prevent customer-facing agents from being published to insecure channels.

### Step 3: Configure Custom Connector Restrictions (Optional)

1. On the **Custom connector patterns** page, configure URL patterns for HTTP connector restrictions
2. Define allowed domains for Zone 2+ environments:
   - **Allowed domain pattern:** `*.yourcompany.com`, `*.microsoft.com`
   - **Blocked domain pattern:** `*` (block all others)
3. Click **Next** to review policy scope

> **Optional:** Custom connector patterns provide granular control over HTTP and custom connector usage. Use this feature in Zone 3 to whitelist only approved external APIs.

### Step 4: Assign DLP Policy to Environments

1. On the **Define scope** page, select how to apply the policy:
   - **Add multiple environments:** Select specific environments by name
   - **Add all environments:** Apply policy tenant-wide (not recommended for Zone 1)
   - **Exclude certain environments:** Apply policy to all except selected environments
2. For zone-based deployment, select **Add multiple environments**
3. Check the boxes for environments classified as Zone 3 (e.g., "Production", "Customer-Facing")
4. Click **Next** to review policy summary
5. Review all settings on the **Review and create policy** page
6. Click **Create policy** to enforce the DLP policy

> **Environment Assignment Strategy:** Create separate DLP policies for each zone (Zone 1, Zone 2, Zone 3) with escalating restrictions. Assign each policy to the appropriate environments based on zone classification.

### Step 5: Enable Security Scans for Agent Publishing

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select the target agent from the agent list
3. Click **Publish** in the top-right corner
4. Observe the **Security scan** indicator before publishing:
   - **Green checkmark:** No security issues detected
   - **Yellow warning:** Warnings detected (Zone 1 can proceed)
   - **Red error:** Blocking issues detected (Zone 2+ cannot proceed)
5. Click **View details** to see security scan findings

> **Note:** Security scans are triggered automatically before publishing. Scans check for blocked channels, insecure connectors, DLP violations, and configuration vulnerabilities.

### Step 6: Review and Resolve Security Scan Findings

1. In the **Security scan results** panel, review detected issues:
   - **DLP violations:** Agent uses connectors not allowed by DLP policy
   - **Blocked channels:** Agent is configured to publish to prohibited channels (e.g., public website)
   - **Insecure configuration:** Agent has settings that pose security risks
2. For each finding, click **Details** to view remediation guidance
3. Resolve DLP violations:
   - Remove or replace blocked connectors from agent topics
   - Request DLP policy exemption (Zone 1 only)
   - Reconfigure agent to use approved connectors
4. Resolve blocked channel violations:
   - Navigate to agent **Settings** → **Channels**
   - Disable or remove prohibited channels (e.g., uncheck "Facebook", "Telegram")
   - Save changes
5. Return to the **Publish** screen and re-run the security scan
6. Verify all issues are resolved before proceeding

> **Zone 2+ Requirement:** Security scans must pass before publishing is allowed. Yellow warnings are acceptable in Zone 1 but require resolution in Zone 2+.

### Step 7: Configure Approval Workflow for Agent Publishing (Zone 2+ Only)

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Environments**
3. Select the target environment (Zone 2 or Zone 3)
4. Click **Settings** at the top
5. Expand **Product** section
6. Click **Features**
7. Scroll to **Copilot and Power Apps** section
8. Enable **Require approval for new chatbots**
9. Optionally enable **Require approval for chatbot updates**
10. Click **Save**

> **Approval Workflow Enablement:** This setting requires agent authors to submit a publishing request that must be approved by a Power Platform Admin before the agent is published or updated.

### Step 8: Submit Agent for Approval (Agent Author Perspective)

1. In Copilot Studio, open the agent to be published
2. Click **Publish** in the top-right corner
3. Verify security scan passes (or warnings are acknowledged in Zone 1)
4. On the **Publish agent** screen, provide:
   - **Publishing justification:** Brief description of why the agent is being published
   - **Expected impact:** Who will use the agent and for what purpose
   - **Testing evidence:** Reference to test results or validation documentation
5. Click **Submit for approval** (if approval is required) or **Publish** (if no approval required)
6. Wait for approval notification from Power Platform Admin

> **Documentation Requirement:** Zone 3 environments require formal publishing documentation including test results, security review sign-off, and business justification before approval.

### Step 9: Approve or Reject Publishing Request (Admin Perspective)

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Pending approvals** or check email for approval notification
3. Click the pending agent publishing request
4. Review submission details:
   - Agent name and environment
   - Publishing justification from agent author
   - Security scan results
   - DLP compliance status
5. Verify the agent meets zone-specific requirements:
   - Zone 2: Documented approval, passing security scan, DLP compliance
   - Zone 3: Multi-level approval, security review sign-off, formal documentation
6. Click **Approve** to allow publishing, or **Reject** with feedback
7. Provide approval comments for audit trail

> **Multi-Level Approval (Zone 3):** For Zone 3 customer-facing agents, require approval from both Power Platform Admin and Compliance Officer before publishing. Configure multi-stage approval workflows using Power Automate.

### Step 10: Verify Environment Promotion Pipeline (Zone 3 Only)

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Environments**
3. Verify separate environments exist:
   - **Development environment:** For agent authoring and initial testing
   - **Test environment:** For pre-production validation and UAT
   - **Production environment:** For live customer-facing deployments
4. Configure environment groups to link dev/test/prod environments:
   - Navigate to **Environment groups**
   - Click **+ New group**
   - Add development, test, and production environments to the group
5. Enforce promotion pipeline:
   - Agents published in development environment must be promoted to test
   - Agents published in test environment must be promoted to production
   - Each promotion requires re-approval at the destination environment level

> **Zone 3 Requirement:** Environment promotion pipelines prevent agents from being published directly to production without undergoing testing and validation in lower environments.

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|---------------------|
| **DLP policy assignment** | Basic restrictions | Moderate restrictions | Strict whitelist only |
| **Security scan enforcement** | Warning only | Must pass | Must pass + review |
| **Approval workflow** | Not required | Single approver | Multi-level approval |
| **Channel restrictions** | Recommended | Enforced (block public) | Whitelist only |
| **Environment separation** | Single environment | Dev + Prod recommended | Dev + Test + Prod required |
| **Publishing documentation** | Recommended | Required | Required with sign-off |
| **Approval SLA** | N/A | 48 hours | 24 hours |

---

## Validation

After completing these steps, verify:

- [ ] DLP policies are configured and assigned to environments by zone
- [ ] Connector classification aligns with zone requirements (Business/Non-Business/Blocked)
- [ ] Security scans are enabled and triggered automatically before publishing
- [ ] Approval workflows are configured for Zone 2+ environments
- [ ] Channel restrictions are enforced (public channels blocked in Zone 2+)
- [ ] Environment separation is implemented for Zone 3 (dev/test/prod)
- [ ] Test publishing an agent to verify DLP enforcement and approval workflow
- [ ] Publishing audit logs are captured in Microsoft Purview

---

## Visual Reference

Expected portal locations:
- **DLP policies:** Power Platform Admin Center → Policies → Data policies
- **Environment settings:** Power Platform Admin Center → Environments → [Environment] → Settings
- **Approval enablement:** Power Platform Admin Center → Environments → [Environment] → Settings → Features → Require approval for new chatbots
- **Security scan results:** Copilot Studio → [Agent] → Publish → Security scan details
- **Channel configuration:** Copilot Studio → [Agent] → Settings → Channels

> **UI Note:** The DLP enforcement change (removal of "Soft-Enabled" exemption) became effective in February 2025. All published agents now require DLP compliance—agents with violations are blocked from updates until violations are resolved.

---

[Back to Control 1.28](../../../controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
