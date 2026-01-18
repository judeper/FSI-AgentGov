# Control 3.5: Cost Allocation and Budget Tracking - Portal Walkthrough

> This playbook provides step-by-step portal configuration guidance for [Control 3.5](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md).

---

## Prerequisites

- Power Platform Admin role
- Microsoft 365 Admin or Global Admin role (for Copilot billing)
- Azure Subscription Owner role (for Azure-based services)
- Cost Management Reader role

---

## Step 1: Configure Power Platform Usage Tracking

**Portal Path:** Power Platform Admin Center > Analytics > Capacity

1. Navigate to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select **Analytics** > **Capacity**
3. Review Dataverse, AI Builder, and Copilot Studio capacity
4. Note consumption by environment

**Capacity Types to Monitor:**

| Capacity Type | Unit | Typical Allocation |
|---------------|------|-------------------|
| Dataverse Storage | GB | 10 GB base + per user |
| AI Builder Credits | Credits | 1M base for E5, additional purchasable |
| Copilot Studio Messages | Messages | Per license allocation |
| Power Automate Runs | Runs | Per user or per flow |

---

## Step 2: Set Up Cost Allocation by Business Unit

**Portal Path:** Power Platform Admin Center > Environments > [Environment] > Details

Create environment naming convention for chargeback:

```plaintext
Environment Naming: {BU}-{Zone}-{Purpose}

Examples:
- WEALTH-Z3-PRODUCTION
- LENDING-Z2-DEVELOPMENT
- OPS-Z1-SANDBOX
```

**Business Unit Mapping:**

| Environment Prefix | Cost Center | Business Unit | Zone |
|-------------------|-------------|---------------|------|
| WEALTH | CC-1001 | Wealth Management | 2-3 |
| LENDING | CC-1002 | Consumer Lending | 2-3 |
| OPS | CC-1003 | Operations | 1-2 |
| CORP | CC-1004 | Corporate | 1-3 |
| SHARED | CC-1005 | Shared Services | All |

---

## Step 3: Configure Microsoft 365 Copilot Billing

**Portal Path:** Microsoft 365 Admin Center > Copilot > Billing & usage > Billing policies

1. Navigate to [M365 Admin Center](https://admin.microsoft.com)
2. Go to **Copilot** > **Billing & usage** > **Billing policies**
3. Click **+ Add a billing policy**
4. Configure billing policy by department/cost center:

| Policy Name | User Group | Services | Budget |
|-------------|------------|----------|--------|
| Wealth-Copilot | Wealth_Users | M365 Copilot Chat, SharePoint Agents | $5,000/month |
| Lending-Copilot | Lending_Users | M365 Copilot Chat | $3,000/month |
| Ops-Copilot | Ops_Users | M365 Copilot Chat | $2,000/month |

---

## Step 4: Set Up Azure Cost Management (if applicable)

**Portal Path:** Azure Portal > Cost Management + Billing > Cost Management

For Azure-based Copilot Studio components:

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Go to **Cost Management + Billing** > **Cost Management**
3. Create cost views filtered by:
   - Resource group (aligned with business unit)
   - Tags (CostCenter, BusinessUnit, Zone)
   - Service name (Power Platform, Azure AI)

**Tag Requirements:**

| Tag Name | Required | Example Values |
|----------|----------|----------------|
| CostCenter | Yes | CC-1001, CC-1002 |
| BusinessUnit | Yes | Wealth, Lending, Ops |
| Zone | Yes | Zone1, Zone2, Zone3 |
| Owner | Yes | email@company.com |
| Application | Yes | CustomerServiceBot |

---

## Step 5: Build Cost Allocation Dashboard

**Portal Path:** Power BI Service > Create > Report

**Dashboard Components:**

| Section | Metrics | Data Source |
|---------|---------|-------------|
| **Total AI Costs** | Monthly spend, trend | Azure Cost Mgmt + PPAC |
| **By Business Unit** | Cost per BU | Tagged resources |
| **By Agent** | Cost per agent | Usage logs |
| **License Utilization** | Assigned vs. active | M365 Admin |
| **Budget vs. Actual** | Variance | Budget system |

**Sample KPIs:**

| KPI | Calculation | Target |
|-----|-------------|--------|
| Cost per Agent | Total cost / Active agents | <$500/month |
| Cost per Interaction | Total cost / Interactions | <$0.05 |
| License Utilization | Active users / Licensed | >80% |
| Budget Variance | (Actual - Budget) / Budget | <10% |

---

## Step 6: Configure Budget Alerts

**Portal Path:** Azure Portal > Cost Management > Budgets

Create budget alerts for each business unit:

1. Go to **Cost Management** > **Budgets**
2. Click **+ Add**
3. Configure budget:

| Setting | Configuration |
|---------|---------------|
| Scope | Resource group or subscription |
| Budget Amount | Monthly limit |
| Reset Period | Monthly |
| Alert Conditions | 50%, 75%, 90%, 100% |
| Alert Recipients | BU owner, Finance, IT |

---

## Step 7: Set Up Chargeback Reporting

**Monthly Chargeback Process:**

1. Export usage data from PPAC and M365 Admin
2. Map consumption to cost centers
3. Apply rate card for internal pricing
4. Generate chargeback report by BU
5. Route to Finance for billing

**Rate Card Example:**

| Service | Unit | Internal Rate |
|---------|------|---------------|
| Copilot Studio Message | Per message | $0.01 |
| M365 Copilot Chat | Per user/month | $30 |
| AI Builder Credit | Per 1000 credits | $5 |
| Dataverse Storage | Per GB/month | $2 |

---

## Next Steps

- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.1*
