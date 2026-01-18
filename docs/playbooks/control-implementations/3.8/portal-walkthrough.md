# Control 3.8: Copilot Hub and Governance Dashboard - Portal Walkthrough

> This playbook provides step-by-step portal configuration guidance for [Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md).

---

## Prerequisites

- Global Administrator or Microsoft 365 Administrator role
- Power Platform Administrator role
- Microsoft 365 Copilot licenses assigned

---

## Part 1: M365 Admin Center - Copilot Section

### Step 1: Access Copilot Management

**Portal Path:** Microsoft 365 Admin Center > Copilot

1. Navigate to [M365 Admin Center](https://admin.microsoft.com)
2. Select **Copilot** in left navigation
3. Review the five navigation sections

---

### Step 2: Review Copilot Navigation Structure

| Section | Path | Purpose |
|---------|------|---------|
| **Overview** | Copilot > Overview | Copilot Control System dashboard |
| **Connectors** | Copilot > Connectors | External data connections |
| **Search** | Copilot > Search | Bookmarks and acronyms |
| **Billing & usage** | Copilot > Billing & usage | Pay-as-you-go policies |
| **Settings** | Copilot > Settings | Comprehensive configuration |

---

### Step 3: Configure Copilot Settings

**Portal Path:** M365 Admin Center > Copilot > Settings

Navigate through the four settings tabs:

**User Access Tab:**

| Setting | FSI Recommendation |
|---------|-------------------|
| Self-service purchases | Disable |
| Copilot in Edge | Managed users only |
| Consumer Copilot access | Disable |

**Data Access Tab:**

| Setting | FSI Recommendation |
|---------|-------------------|
| Web search for M365 Copilot | Disable for compliance |
| External AI providers | Block |
| Third-party LLM access | Block |
| Agents | Approval required |

**Copilot Actions Tab:**

| Setting | FSI Recommendation |
|---------|-------------------|
| Image generation | Disable |
| Video generation | Disable |
| Teams meeting Copilot | Enable with retention |

---

## Part 2: M365 Admin Center - Agents Section

### Step 4: Access Agents Management

**Portal Path:** M365 Admin Center > Agents

1. Navigate to **Agents** in left navigation
2. Review the four navigation sections

---

### Step 5: Review Agents Overview Dashboard

**Portal Path:** M365 Admin Center > Agents > Overview

Key metrics to monitor:

| Metric | Description | Action |
|--------|-------------|--------|
| Agent registry count | Total agents | Track growth |
| Active users | Users interacting with agents | Monitor adoption |
| Pending requests | Agents awaiting approval | Review/approve |
| Ownerless agents | Agents without owner | Assign immediately |

---

### Step 6: Configure Agent Registry

**Portal Path:** M365 Admin Center > Agents > All agents > Registry

Review and filter agents by:

| Filter | Options |
|--------|---------|
| Publisher | Microsoft, External, Your organization |
| Availability | All users, Some users |
| Channel | Copilot, Teams, Outlook, M365 |
| Platform | M365 Copilot, Agent Builder, Other |

---

### Step 7: Manage MCP Servers (Tools)

**Portal Path:** M365 Admin Center > Agents > Tools

Review MCP Server availability:

| Action | When to Use |
|--------|-------------|
| Block server | Prevent specific data access |
| Allow server | Enable capabilities |

---

### Step 8: Configure Agent Settings

**Portal Path:** M365 Admin Center > Agents > Settings

| Setting | Description | FSI Action |
|---------|-------------|------------|
| Allowed agent types | Control agent sources | Restrict to approved |
| Sharing | Manage sharing scope | Limit appropriately |
| Templates | Pre-set governance policies | Create FSI templates |
| User access | Control agent interactions | Define by role |

---

## Part 3: PPAC Copilot Section

### Step 9: Access PPAC Copilot

**Portal Path:** Power Platform Admin Center > Copilot

1. Navigate to [PPAC](https://admin.powerplatform.microsoft.com)
2. Select **Copilot** in left navigation

---

### Step 10: Configure PPAC Copilot Settings

**Portal Path:** PPAC > Copilot > Settings

**Power Platform Settings:**

| Setting | FSI Recommendation |
|---------|-------------------|
| Copilot feedback | Review before sending |
| Generative AI | Enable with monitoring |
| Preview AI models | Disable in production |

**Copilot Studio Settings:**

| Setting | FSI Recommendation |
|---------|-------------------|
| Computer Use | Disable |
| Code generation | Controlled approval |
| External Models | Disable |
| Channel access | Internal only |

---

## Next Steps

- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.1*
