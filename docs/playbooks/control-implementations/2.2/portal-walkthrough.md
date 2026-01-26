# Portal Walkthrough: Control 2.2 - Environment Groups and Tier Classification

**Last Updated:** January 2026
**Portal:** Power Platform Admin Center
**Estimated Time:** 30-60 minutes initial setup, ongoing rule configuration

## Prerequisites

- [ ] Power Platform Admin role assigned
- [ ] Access to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
- [ ] Governance tier definitions documented (Tier 1/2/3)
- [ ] Inventory of existing environments and classifications
- [ ] All target environments are Managed Environments ([Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md))
- [ ] DLP policies reviewed for compatibility
- [ ] Compliance team approval for rule configurations

---

## Step-by-Step Configuration

### Step 1: Create Environment Groups

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Manage** > **Environment groups**
3. Click **+ New group**
4. Enter group name (e.g., "FSI-Team-Collaboration")
5. Add description with tier classification (Tier 1/2/3), business scope, and change authority
6. Click **Save**

**Recommended Group Structure for FSI:**

| Group Name | Governance Tier | Description |
|------------|-----------------|-------------|
| FSI-Personal-Dev | Tier 1 | Personal productivity environments - non-sensitive data only |
| FSI-Team-Collaboration | Tier 2 | Team collaboration environments - internal/confidential data |
| FSI-Enterprise-Production | Tier 3 | Enterprise production - all classifications, maximum governance |
| FSI-Enterprise-NonProd | Tier 3 | UAT/staging - same rules as production for pre-deployment testing |

### Step 2: Add Environments to Groups

1. Select the environment group
2. Click **Environments** tab
3. Click **Add environments**
4. Select environments to include
5. Click **Add**

**Important:** If an environment cannot be added, verify it is a Managed Environment first ([Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md)).

### Step 3: Configure Rules

1. Select the environment group
2. Click **Rules** tab (shows 21+ available rules)
3. Click on a rule name to configure
4. Set the appropriate value/toggle
5. Click **Save** (or **Publish rules** for batch changes)

---

## Rule Configuration by Governance Tier

### Tier 1 - Personal Productivity Rules

**Allowed data:** Non-sensitive only (no regulated customer data). Use synthetic/sample data when possible.

| Rule | Setting | Rationale |
|------|---------|-----------|
| Sharing agents with Editor permissions | **Disabled** | Prevents uncontrolled agent co-authoring |
| Sharing agents with Viewer permissions | **Disabled** | Limits agent distribution |
| Channel access for published agents | **Teams + M365 Copilot only** | Restricts to internal channels |
| Enable External Models | **Disabled** | Prevents external AI model usage |
| Preview and experimental AI models | **Enabled** | Allows learning with low-risk features |
| Computer Use | **Disabled** | High-risk feature - always disabled |

### Tier 2 - Team Collaboration Rules

**Expected ownership:** Named group owner and approval trail for rule changes.

| Rule | Setting | Rationale |
|------|---------|-----------|
| Sharing agents with Editor permissions | **Enabled** | Allows team collaboration |
| Sharing agents with Viewer permissions | **Enabled** | Allows internal distribution |
| Channel access for published agents | **Teams, SharePoint enabled** | Controlled internal channels |
| Authentication for agents | **Required** | Enforces identity for access |
| Solution checker enforcement | **Warn** | Alerts on issues without blocking |
| Maker welcome content | **Team policy configured** | Communicates governance requirements |
| Enable External Models | **Disabled** | Prevents external AI model usage |
| Computer Use | **Disabled** | High-risk feature - always disabled |

### Tier 3 - Enterprise Managed Rules

**Change control:** Treat rule changes as controlled changes (ticket + peer review + recorded testing results).

| Rule | Setting | Rationale |
|------|---------|-----------|
| Sharing agents with Editor permissions | **Disabled** | Use ALM for controlled changes |
| Sharing agents with Viewer permissions | **Enabled** | Allows controlled distribution |
| Channel access for published agents | **All (with approval)** | Requires documented approval |
| Authentication for agents | **Required** | Enforces identity for all access |
| Enable External Models | **Disabled** (unless explicitly approved) | Strict AI governance |
| Solution checker enforcement | **Block** | Prevents non-compliant deployments |
| Unmanaged customizations | **Block** | Enforces ALM practices |
| Default deployment pipeline | **Configured** | Links to deployment automation |
| IP Firewall setting | **Configured** | Network-level access control |
| Enable IP Cookie Binding | **Enabled** | Prevents session hijacking |
| Computer Use | **Disabled** | High-risk feature - always disabled |

### Step 4: Publish Rules

1. After configuring all rules, click **Publish rules**
2. Rules apply to all environments in the group
3. Verify by checking individual environment settings

---

## Computer-Using Agents (CUA) - Critical Configuration

**WARNING:** Computer-Using Agents (CUA) is a high-risk preview feature that allows agents to control desktop applications, navigate UIs, and interact with any visible screen content.

**FSI Recommendation: DISABLED for All Zones**

| Zone | CUA Setting | Rationale |
|------|-------------|-----------|
| Zone 1 | **Disabled** | No use case justifies risk |
| Zone 2 | **Disabled** | Shared data increases blast radius |
| Zone 3 | **Disabled** | Regulatory data exposure risk too high |

**To Disable CUA:**

1. Navigate to **Environment groups** > select group > **Rules**
2. Locate **Computer Use** rule
3. Set to **Disabled**
4. Click **Save** and **Publish rules**

---

## Cross-Tenant Restrictions Configuration

For each environment group, configure cross-tenant restrictions to prevent data leakage:

**Portal Path:** PPAC > Environments > [env] > Settings > Product > Privacy + Security

| Zone | Inbound Setting | Outbound Setting |
|------|-----------------|------------------|
| Zone 1 | Disabled | Disabled |
| Zone 2 | Disabled | Disabled or approved tenants only |
| Zone 3 | Disabled | Disabled |

---

## FSI Example Configuration

```yaml
# FSI Environment Group Configuration
Organization: Contoso Financial Services

environment_groups:
  - name: "FSI-Enterprise-Production"
    description: "Enterprise production environments - maximum governance (Tier 3)"
    tier: "Production"
    governance_tier: "Enterprise Managed"

    rules:
      # Sharing Rules
      sharing_agents_editor: disabled
      sharing_agents_viewer: enabled
      sharing_canvas_apps: "organization_only"
      sharing_solution_flows: "organization_only"

      # Channel Rules
      channel_access_agents: "teams,m365copilot,sharepoint"

      # Security Rules
      authentication_agents: required
      ip_cookie_binding: enabled
      ip_firewall: enabled
      content_security_policy: strict

      # AI Governance
      ai_prompts: enabled
      external_models: disabled
      preview_experimental_ai: disabled
      generative_ai: enabled
      computer_use: disabled

      # Solution Governance
      solution_checker: block_on_error
      unmanaged_customizations: blocked
      default_pipeline: "FSI-Production-Pipeline"

      # Audit & Compliance
      transcript_access: enabled
      usage_insights: enabled
      backup_retention: "28_days"

    environments:
      - "prod-trading-001"
      - "prod-wealth-management"
      - "prod-customer-service"
```

---

## Validation

After completing configuration, verify:

- [ ] Environment groups created with appropriate names and descriptions
- [ ] Environments added to correct groups based on tier classification
- [ ] Rules configured per governance tier requirements
- [ ] Rules published and status shows "Published" with date
- [ ] Computer Use rule disabled for all groups
- [ ] External Models rule disabled for Tier 2/3 groups
- [ ] Test environment inherits rules when added to group

---

## Evidence Collection

Capture the following for audit documentation:

- [ ] Screenshot: Environment groups list with counts
- [ ] Screenshot: Each group's Environments tab showing membership
- [ ] Screenshot: Each group's Rules tab showing configured values
- [ ] Export: Environment group inventory CSV
- [ ] Export: Environment-to-group mapping CSV
- [ ] Change record: Ticket/approval for rule configurations

---

[Back to Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
