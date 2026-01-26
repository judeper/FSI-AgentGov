# Control 1.4: Advanced Connector Policies (ACP) - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md).

---

## Prerequisites

Before starting, confirm:

- Target environments are in a **United States** region
- Environments are enabled as **Managed Environments** ([Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md))
- Environments are members of an **Environment Group** ([Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md))
- Organization has documented **approved connector catalog** (allowlist) and **restricted connector catalog** (denylist)

---

## Step 1: Enable Managed Environments (if not already enabled)

1. Sign in to the **Power Platform Admin Center** ([https://admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com))
2. Navigate to **Manage** > **Environments**
3. Select the ellipsis (**...**) next to your target environment
4. Select **Enable Managed Environments**
5. Configure the settings:
   - **For Financial Sector**: Enable all security features
   - Weekly digest: Enabled (for compliance tracking)
   - Limit sharing: Enabled (prevent unauthorized data exposure)
6. Select **Enable**

---

## Step 2: Create Environment Group

1. In Power Platform Admin Center, select **Manage** > **Environment Groups**
2. Select **New group**
3. Add a **Name**: Example for FSI: `FSI-Production-Agents` or `Regulated-Banking-Environments`
4. Add a **Description**: `Regulated production environments for financial services Copilot Studio agents - SOX and FINRA compliant`
5. Select **Add environments** and choose your managed environments
6. Select **Create**

---

## Step 3: Configure Advanced Connector Policy

1. Select the environment group you created
2. Select the **Rules** tab
3. Select **Advanced connector policies (preview)**
4. Configure allowed connectors and actions:
   - **Default behavior**: Non-blockable connectors (Microsoft Dataverse, Office 365) are pre-loaded
   - Select **Add connectors** to add certified connectors
   - **For Financial Sector**: Use an **explicit allowlist** approach—only add connectors that have documented business justification and a completed security/vendor review
   - To block a connector, select it and choose **Remove connector**

### FSI Recommended Allowlist

- Microsoft Dataverse
- SharePoint
- Microsoft Teams
- Office 365 Users
- Internal custom connectors (verified by security team)

### FSI Recommended Blocklist

- Social media connectors (Twitter, Facebook, LinkedIn)
- Public cloud storage (Dropbox, Box)
- Consumer file sharing services
- Any connector that transmits data outside your tenant

### Action-Level Allowlisting (Recommended for Regulated Environments)

For each allowed connector, set the policy to **allow only the minimum required actions** for agent scenarios. Prefer **read-only** actions by default; require change control for any write/update/delete actions.

**Example action guidance:**

- **Microsoft Dataverse**
  - Allow: read/query (e.g., list/get rows)
  - Restrict: create/update/delete rows unless a regulated business use case exists
- **SharePoint**
  - Allow: read/list/get content needed for retrieval-augmented responses
  - Restrict: create/update/delete files, manage permissions/sharing links
- **Microsoft Teams**
  - Allow: post messages to approved channels for escalation
  - Restrict: create teams/channels, add members, export/tenant-wide search actions
- **Custom connectors (internal APIs)**
  - Allow: specific, documented endpoints only
  - Restrict: wildcard endpoints, admin functions, bulk export endpoints

5. Select **Save**
6. Select **Publish rules** to apply across all environments in the group

---

## Step 3B: Configure DLP Policy Alignment

ACP is not a replacement for DLP. Use DLP to define **data loss prevention boundaries** (Business / Non-Business / Blocked).

1. In Power Platform Admin Center, go to **Policies** > **Data policies**
2. Select an existing policy aligned to your regulated tier, or select **New policy**
3. Configure connector groups:
   - **Business**: enterprise/tenant-approved connectors required by agents
   - **Non-Business**: generally prohibited for regulated agent environments
   - **Blocked**: connectors explicitly disallowed (high-risk, consumer, or external data egress)
4. Scope the DLP policy to the same environments covered by your environment group
5. Select **Save**

---

## Step 4: Verify Policy Application

1. Navigate to **Manage** > **Environments**
2. Select an environment in your group
3. Confirm that the environment shows as part of the group
4. Test by attempting to create a connection using a blocked connector—should be prevented
5. Test action-level restrictions: attempt to add a flow/action that is not allowed—should be blocked

**Evidence note:** Capture a screenshot of the policy in **Published** status and the blocked connector/action error banner shown to a test maker account.

---

## Configuration Matrix by Governance Tier

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|--------------------|
| **Connector approach** | DLP-based blocking | ACP allowlist | Strict ACP allowlist |
| **Social media** | Block via DLP | Block via ACP | Block via ACP |
| **External storage** | Warn | Block | Block |
| **Custom connectors** | No restriction | Security review | Security + legal review |
| **Review frequency** | Annual | Quarterly | Monthly |

---

## Copilot Studio DLP Examples

### Example 1: Block Social Media Connectors

| Connector | Classification | Rationale |
|-----------|---------------|-----------|
| Facebook | Blocked | Customer data exposure risk; not compliant with record retention |
| Twitter/X | Blocked | Public disclosure risk; cannot audit conversations |
| LinkedIn | Blocked | Data sharing with third party; privacy concerns |
| Instagram | Blocked | No business justification for FSI agents |

### Example 2: Restrict HTTP Request Actions

| Setting | Configuration |
|---------|---------------|
| Connector | HTTP / HTTP with Microsoft Entra ID |
| Classification | Business (with action restrictions) |
| Allowed endpoints | `https://api.internal.bank.com/*`, `https://services.internal.bank.com/*` |
| Blocked patterns | All external URLs, public APIs |

### Example 3: Knowledge Source Restrictions

| Knowledge Source Type | Zone 1 | Zone 2 | Zone 3 |
|-----------------------|--------|--------|--------|
| SharePoint (internal sites) | Allowed | Allowed | Allowed (approved sites only) |
| Dataverse (internal tables) | Allowed | Allowed | Allowed (approved tables only) |
| Public websites | Blocked | Blocked | Blocked |
| External file uploads | Blocked | Blocked | Blocked |
| Third-party APIs | Blocked | Require review | Blocked |

### Example 4: Restrict Agent Output Channels

| Channel | Classification | FSI Guidance |
|---------|---------------|--------------|
| Microsoft Teams (internal) | Business | Allowed for internal agents |
| Web chat (authenticated) | Business | Allowed with SSO enforcement |
| Direct Line | Non-Business | Require security review |
| Facebook Messenger | Blocked | Not permitted for FSI |
| WhatsApp | Blocked | Not permitted for FSI |
| Omnichannel | Business | Requires Dynamics 365 integration approval |

---

## Model Context Protocol (MCP) Governance

### What is MCP?

MCP (Model Context Protocol) provides a standardized way for AI agents to connect to external tools and data sources. For financial services, MCP servers must be governed with controls equivalent to Power Platform connectors.

### MCP Server Categories and Risk Levels

| Category | Examples | Risk Level | Approval Process |
|----------|----------|------------|------------------|
| **Internal MCP Servers** | Self-hosted tools, internal APIs | Medium | Security review |
| **Vendor MCP Servers** | Third-party hosted services | High | Full vendor assessment |
| **Community MCP Servers** | Open-source, community-built | Critical | Code review + security audit |
| **Development/Test MCP** | Local development tools | Low | Standard approval for non-prod |

### Zone-Specific MCP Rules

- **Zone 1**: MCP not allowed (personal productivity agents do not use MCP)
- **Zone 2**: Internal MCP servers only with approval
- **Zone 3**: Approved internal + vetted vendor MCP only with full audit logging

---

## "Bring Your Own Agent" (BYOA) Governance

| BYOA Scenario | Risk | Policy |
|---------------|------|--------|
| **Personal AI Assistants** | Data leakage to consumer AI | Blocked in regulated environments |
| **External AI Agents** | Unknown governance, audit gaps | Requires full assessment |
| **Partner AI Systems** | Shared responsibility unclear | Contract required with audit rights |
| **Acquired Company AI** | Unknown technical debt | Integration assessment required |

---

*Updated: January 2026 | Version: v1.2*
