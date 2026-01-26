# Control 4.6: Grounding Scope Governance - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md).

---

## Prerequisites

Before starting, ensure you have:

- SharePoint Administrator role assigned
- SharePoint Advanced Management license
- Site inventory completed with content classification
- Sensitivity labels deployed (if using label-based exclusion)

---

## Step 1: Inventory Current Grounding Scope

### Categorize Sites by Content Type

| Category | Description | Default Index Status | Recommendation |
|----------|-------------|---------------------|----------------|
| **Production Knowledge** | Finalized, approved content | Include | Keep indexed |
| **Draft/WIP** | Work in progress documents | Include (by default) | Exclude |
| **Archive** | Historical, outdated content | Include (by default) | Exclude |
| **Personal** | Individual user files | Include (by default) | Exclude |
| **Regulatory Hold** | Content under legal hold | Include (by default) | Review |
| **Highly Confidential** | Top-secret business data | Include (by default) | Exclude or restrict |

---

## Step 2: Configure Site Exclusion from Semantic Index

### Option A: Restricted Content Discovery (RCD) via Portal

1. Navigate to [SharePoint Admin Center](https://admin.sharepoint.com)
2. Go to **Sites** > **Active sites**
3. Select site to exclude
4. Click **Settings** (gear icon)
5. Under **Microsoft 365 Copilot**, configure access:
   - **Standard:** Content indexed and available to Copilot
   - **Restricted:** Content not included in Copilot results
6. Click **Save**

### Sites to Exclude

Apply Restricted Content Discovery to:

- All sites with "Draft" in the name
- Archive sites
- Legal hold sites
- Executive communications
- HR confidential sites
- M&A / deal rooms

---

## Step 3: Implement CopilotReady Metadata Approach

For positive governance (explicit approval for indexing):

1. Create a governance register of approved sites
2. Document each site with:
   - Site URL
   - CopilotReady status (Yes/No)
   - Approved by
   - Approval date
   - Review due date
3. Use site property bags or a SharePoint list to track approvals

---

## Step 4: Establish Monitoring

### Monitoring Cadence

| Activity | Frequency | Responsible Role |
|----------|-----------|------------------|
| Review new sites for grounding scope | Weekly | SharePoint Admin |
| Audit excluded sites | Monthly | AI Governance Lead |
| CopilotReady certification | Quarterly | Content Owners |
| Comprehensive scope review | Annually | Governance Committee |

---

## Governance Level Configurations

### Baseline (Level 1)

| Setting | Value |
|---------|-------|
| Site awareness | Document which sites agents access |
| Manual exclusion | Exclude known sensitive sites |
| Monitoring | Quarterly review of indexed content |

### Recommended (Level 2-3)

| Setting | Value |
|---------|-------|
| Systematic exclusion | Policy-based site exclusion |
| Content type filtering | Exclude Draft, Archived, Personal |
| Metadata approach | CopilotReady tag for approved content |
| Review frequency | Monthly |

### Regulated (Level 4)

| Setting | Value |
|---------|-------|
| Comprehensive governance | All content explicitly approved for indexing |
| Label integration | Sensitivity labels control index inclusion |
| Real-time monitoring | Continuous audit of indexed content |
| Change control | Formal approval for grounding scope changes |

---

*Updated: January 2026 | Version: v1.2*
