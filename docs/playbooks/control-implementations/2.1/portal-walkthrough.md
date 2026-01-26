# Portal Walkthrough: Control 2.1 - Managed Environments

**Last Updated:** January 2026
**Portal:** Power Platform Admin Center
**Estimated Time:** 30-45 minutes per environment

## Prerequisites

- [ ] Power Platform Admin role assigned
- [ ] Access to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
- [ ] Target environment(s) identified
- [ ] Governance tier classification determined
- [ ] Environment region is United States (US-only requirement)
- [ ] DLP policies created and ready to apply
- [ ] Maker welcome content drafted

---

## Step-by-Step Configuration

### Step 1: Navigate to Environment

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select **Environments** in left navigation
3. Click on the target environment name

### Step 2: Access Managed Environment Settings

1. Locate the **Managed environments** card on the environment page
2. Click **Edit managed environments** link
   - Or use toolbar button: **Edit managed environments**
3. In the panel, set **Managed environment** to **On** (enabled)
4. Leave the panel open to configure the settings below before saving

### Step 3: Configure Sharing Limits

In the "Manage sharing" section, configure limits for each resource type:

#### Power Apps
- Expand **Power Apps** section
- Select: "Don't set limits" OR configure sharing restrictions

#### Power Automate
- Expand **Power Automate** section
- Configure flow sharing limits

#### Copilot Studio

Expand **Copilot Studio** section to configure agent sharing:

**Editors:**

- Check/uncheck "Let people grant Editor permissions when agents are shared"

**Viewers:**

- Check/uncheck "Let people grant Viewer permissions when agents are shared"
- "Only share with individuals (no security groups)" - Prevents sharing with security groups
- "Limit the number of viewers who can access each agent" - Set numeric limit

**Governance Tier Recommendations:**

| Tier | Editors | Viewers | Individuals Only | Viewer Limit |
|------|---------|---------|------------------|--------------|
| Tier 1 | Disabled | Disabled | N/A | N/A |
| Tier 2 | Enabled | Enabled | No | No limit |
| Tier 3 | Disabled | Enabled | No | Consider limit |

> **Note:** Sharing limits do not apply when agent authentication is set to "No authentication". Always enable authentication for shared/enterprise agents.

See [Sharing limits](https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-sharing-limits) for details.

### Step 4: Configure Solution Checker

1. Locate **Solution checker enforcement** section
2. Set enforcement level using slider:
   - **None:** No enforcement (personal productivity)
   - **Warn:** Email notifications on issues (team collaboration)
   - **Block:** Prevent import of solutions with issues (enterprise managed)
3. Optionally configure excluded rules
4. Enable email notifications: "Send emails only when a solution is blocked"

**FSI Recommendation:** Set to **Block** for enterprise-managed production environments to prevent deployment of solutions with security vulnerabilities.

**Prerequisite note:** Solution Checker enforcement requires a Dataverse-backed environment and solution import scenarios. If the environment does not use Dataverse/solutions, document "Not applicable" and rely on other governance controls (DLP, sharing limits, and change management).

### Step 5: Enable Usage Insights

1. Locate **Usage insights** section
2. Check **Include insights for this environment in the weekly email digest**
3. Check **Add additional recipients for the weekly digest** and add:
   - Compliance Officer email
   - Security Team distribution list

See [Usage insights](https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-usage-insights) for details.

### Step 6: Configure Maker Welcome Content

1. Locate **Maker welcome content** section
2. Enter governance guidance in Markdown or plain text (1500 character limit)
3. Add **Learn more link** to full policy documentation
4. Click **See preview** to verify formatting

**Example content for a team collaboration environment:**
```markdown
## Welcome to [Environment Name]

This is a **team collaboration environment**. Before creating agents:

- Review the Agent Governance Policy
- Complete required training
- All agents require manager approval before sharing

Contact governance@company.com for questions.
```

### Step 7: Configure AI Features (Optional)

1. Locate **Enable AI-generated app descriptions (preview)** section
2. Enable/disable based on organization policy
3. Review warning about potential inaccuracies

### Step 8: Review Data Policies

1. Locate **Data policies** section
2. Select **See active data policies for this environment**
3. Verify the expected DLP policy/policies are applied to this environment (record policy name(s))
4. If policies are missing, assign them:
   - PPAC > **Data policies** > open the policy > **Environments** > add/select the target environment > **Save**
5. Capture evidence:
   - Screenshot of the environment's **Data policies** showing the active policy list
   - Screenshot of the DLP policy **Environments** tab showing the environment assigned

### Step 9: Save Configuration

1. Review all settings
2. Click **Save** to apply changes
3. Verify settings are active by reopening the panel

### Step 10: Environment Routing Tie-in (Recommended)

Managed Environments complement **Environment Groups** and **Environment Routing** to ensure makers are routed into governed environments by default.

1. PPAC > **Environments** > **Environment groups**
2. Create or open the target environment group (US-only scope)
3. Add the managed environment(s) to the group
4. Enable/configure environment routing per your standard in Control 2.15: Environment Routing
5. Capture evidence:
   - Screenshot of the environment group membership showing the managed environment included
   - Screenshot of the environment routing configuration/rules used for routing makers

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|--------------------|
| **Managed Environment** | Enabled for non-personal | Enabled for all non-personal | **Mandatory** |
| **Sharing Limits - Apps** | Unlimited | 50 users | Security groups only |
| **Sharing Limits - Flows** | Unlimited | 25 users | Security groups only |
| **Sharing Limits - Agents** | Unlimited | 25 users | Security groups only |
| **Solution Checker** | None | Warn | **Block** |
| **Usage Insights** | Optional | Enabled | Enabled + Compliance CC |
| **Maker Welcome** | Optional | Recommended | **Required with acknowledgment** |

---

## Cross-Tenant Restrictions Configuration

Cross-tenant restrictions control whether connectors and data flows can interact with resources in other Microsoft Entra tenants. For FSI organizations, this is critical to prevent data leakage to unauthorized external tenants.

**Configuration:**

1. In Power Platform Admin Center, navigate to **Environments** > select target environment
2. Go to **Settings** > **Product** > **Privacy + Security**
3. Configure **Cross-tenant inbound** and **Cross-tenant outbound** settings:
   - **Disabled**: Block all cross-tenant connector access (recommended for Zone 3)
   - **Enabled with restrictions**: Allow only approved tenants via allowlist
   - **Enabled**: Allow cross-tenant access (not recommended for regulated environments)

**FSI Recommendations:**

| Zone | Inbound | Outbound |
|------|---------|----------|
| Zone 1 | Disabled | Disabled |
| Zone 2 | Disabled | Disabled or approved tenants only |
| Zone 3 | Disabled | Disabled |

See [Cross-tenant restrictions](https://learn.microsoft.com/en-us/power-platform/admin/cross-tenant-restrictions) for detailed configuration guidance.

---

## FSI Example Configuration

```yaml
Organization: Regional Investment Management Firm
Environment: FSI-Client-Services-Prod

Managed Environment Configuration:
  Status: Enabled

  Sharing Controls:
    Power Apps: Security groups only
    Power Automate: Security groups only
    Copilot Studio: Security groups only
    Approved Groups:
      - sg-client-services-users
      - sg-compliance-reviewers

  Solution Checker:
    Enforcement: Block
    Validation: Critical and High severity items block import
    Exceptions: Documented exception process required

  Usage Insights:
    Enabled: Yes
    Recipients:
      - it-governance@firm.com
      - compliance@firm.com
    Frequency: Weekly

  Maker Welcome Content:
    Title: "Enterprise Managed Production Environment - Regulated"
    Content: |
      This is an enterprise-managed regulated environment.
      All solutions require governance approval.
      Client data is subject to SEC and FINRA regulations.
      Contact compliance@firm.com before publishing.
    Acknowledgment: Required

  Data Policies:
    Active Policies:
      - FSI-Block-Consumer-Connectors
      - FSI-Customer-Data-Protection
```

---

## Validation

After completing these steps, verify:

- [ ] Managed Environment card shows enabled status
- [ ] Sharing limits configured per governance tier
- [ ] Solution checker set to appropriate enforcement level
- [ ] Usage insights enabled with correct recipients
- [ ] Maker welcome content displays correctly (use preview)
- [ ] Data policies are applied and visible
- [ ] Cross-tenant restrictions configured appropriately

---

[Back to Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
