# Control 3.6: Orphaned Agent Detection and Remediation - Portal Walkthrough

> This playbook provides step-by-step portal configuration guidance for [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).

---

## Prerequisites

- Power Platform Admin role
- SharePoint Admin role (for SharePoint agents)
- M365 Admin role (for Integrated Apps)
- Power Automate license for automated workflows

---

## Step 1: Define Orphan Criteria

**Orphan Categories:**

| Category | Definition | Risk Level |
|----------|------------|------------|
| **Owner Departed** | Business owner no longer with organization | High |
| **Environment Deleted** | Agent's environment removed | Critical |
| **No Activity** | Zero interactions for 90+ days | Medium |
| **License Expired** | Required licenses no longer assigned | High |
| **Maker Inactive** | Creator account disabled/deleted | High |
| **Connector Broken** | Key data connections failed | Medium |

---

## Step 2: Configure PPAC Agent Inventory Export

**Portal Path:** Power Platform Admin Center > Resources > Power Apps/Copilot Studio

1. Navigate to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Go to **Resources** > **Power Apps** or **Copilot Studio**
3. Export agent list with owner information
4. Compare against Entra ID active users

---

## Step 3: Set Up M365 Admin Center Agent Review

**Portal Path:** M365 Admin Center > Agents > All agents > Registry

1. Navigate to [M365 Admin Center](https://admin.microsoft.com)
2. Go to **Agents** > **All agents** > **Registry tab**
3. Review "Missing an owner" metric on the summary bar
4. Filter for agents without owner assignment

---

## Step 4: Create SharePoint Orphan Tracking List

Create a SharePoint list to track orphaned agents:

| Column | Type | Purpose |
|--------|------|---------|
| Agent ID | Text | Unique identifier |
| Agent Name | Text | Display name |
| Orphan Category | Choice | Classification |
| Discovery Date | Date | When identified |
| Last Owner | Person | Previous owner |
| Assigned Reviewer | Person | Current reviewer |
| Action | Choice | Reassign/Archive/Delete |
| Action Date | Date | When resolved |
| Justification | Multi-line | Reasoning |

---

## Step 5: Configure Automated Detection Flow

**Portal Path:** Power Automate > Create > Scheduled cloud flow

Create flow to detect orphaned agents weekly:

```plaintext
Trigger: Recurrence (Weekly - Sunday 2 AM)

Actions:
├── Get all agents from PPAC
├── Get all active users from Entra ID
├── For each agent:
│   ├── Check if owner exists in active users
│   ├── Check last activity date
│   ├── If orphan criteria met:
│   │   ├── Add to Orphan Tracking List
│   │   ├── Notify AI Governance Lead
│   │   └── Start remediation timer
└── Generate weekly orphan report
```

---

## Step 6: Establish Remediation Workflow

**Remediation Options:**

| Action | When to Use | Process |
|--------|-------------|---------|
| **Reassign** | Agent still valuable | Transfer to new owner; update metadata |
| **Archive** | Uncertain value | Disable agent; retain 90 days |
| **Delete** | No business need | Backup config; permanent removal |
| **Consolidate** | Duplicate functionality | Merge with another agent |

**Approval Requirements:**

| Action | Zone 1 | Zone 2 | Zone 3 |
|--------|--------|--------|--------|
| Reassign | Team Lead | Manager | Director + Compliance |
| Archive | Team Lead | Manager | Director |
| Delete | Manager | Director | VP + Legal |

---

## Step 7: Configure Remediation SLAs

| Orphan Category | Review SLA | Remediation SLA |
|-----------------|------------|-----------------|
| Owner Departed | 5 days | 14 days |
| Environment Deleted | Immediate | 3 days |
| No Activity (90d) | 14 days | 30 days |
| License Expired | 5 days | 7 days |
| Maker Inactive | 5 days | 14 days |
| Connector Broken | 7 days | 14 days |

---

## Next Steps

- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.1*
