# Control 4.7: Microsoft 365 Copilot Data Governance - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 4.7](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md).

---

## Prerequisites

Before starting, ensure you have:

- Microsoft 365 Admin role assigned
- Microsoft 365 Copilot licenses assigned to target users
- SharePoint site inventory with sensitivity classification
- Sensitivity labels deployed

---

## Step 1: Configure Copilot Settings in M365 Admin Center

1. Navigate to [admin.microsoft.com](https://admin.microsoft.com)
2. Go to **Settings** > **Org settings** > **Copilot**
3. Configure settings based on governance level:

| Setting | Baseline | Recommended | Regulated |
|---------|----------|-------------|-----------|
| **Copilot enabled** | Yes | Yes | Yes |
| **Web search** | Enabled | Review | Disabled |
| **Plugin marketplace** | Enabled | Limited | Disabled |
| **Usage analytics** | Enabled | Enabled | Enabled |

---

## Step 2: Configure Content Exclusions

Exclude sensitive sites from M365 Copilot via Restricted Content Discovery:

1. Navigate to [SharePoint Admin Center](https://admin.sharepoint.com)
2. Go to **Sites** > **Active sites**
3. Select the sensitive site
4. Click **Settings**
5. Under **Microsoft 365 Copilot**, set to **Restricted**

**Categories to Exclude:**

| Content Category | Risk Level | Recommendation |
|-----------------|------------|----------------|
| Executive compensation | High | Exclude |
| M&A / Deal rooms | Critical | Exclude |
| Legal/Compliance investigations | Critical | Exclude |
| HR confidential | High | Exclude |
| Board materials | High | Exclude |
| Draft content | Medium | Consider exclusion |

---

## Step 3: Configure Plugin Governance

1. Navigate to [admin.microsoft.com](https://admin.microsoft.com)
2. Go to **Settings** > **Integrated apps**
3. Review installed plugins
4. Configure plugin approval workflow:
   - Block unapproved plugins
   - Require security review for new plugins
   - Maintain allowlist for approved plugins

**Plugin Risk Assessment:**

| Risk Factor | Low Risk | Medium Risk | High Risk |
|-------------|----------|-------------|-----------|
| Data access | Read-only, public | Read org data | Read/write sensitive |
| Vendor | Microsoft first-party | Established vendor | Unknown vendor |
| Certification | M365 certified | SOC 2 | No certification |

---

## Step 4: Configure Usage Monitoring

1. Navigate to [admin.microsoft.com](https://admin.microsoft.com)
2. Go to **Reports** > **Usage** > **Microsoft 365 Copilot usage**
3. Review key metrics:
   - Active users
   - Feature usage by app
   - Queries per user

**Monitoring Cadence:**

| Metric | Review Frequency |
|--------|------------------|
| Active users | Weekly |
| Feature usage | Monthly |
| Queries per user | Monthly |
| Feedback submitted | Weekly |

---

## Step 5: Establish User Behavior Guardrails

Publish acceptable use policy covering:

- Permitted uses (drafting, summarizing, analysis)
- Prohibited uses (regulatory filings without review, investment recommendations)
- Output review requirements by content type
- Over-reliance prevention guidelines

---

## Governance Level Configurations

### Baseline (Level 1)

| Setting | Value |
|---------|-------|
| License management | Track Copilot assignments |
| Access control | Rely on existing permissions |
| Awareness | User communication |
| Review | Quarterly usage review |

### Recommended (Level 2-3)

| Setting | Value |
|---------|-------|
| Content exclusions | Exclude sensitive sites via RCD |
| Plugin governance | Approval workflow |
| Usage monitoring | Monthly analytics review |
| Training | Mandatory Copilot training |

### Regulated (Level 4)

| Setting | Value |
|---------|-------|
| Comprehensive exclusions | Default-deny for unlabeled content |
| Plugin control | Allowlist-only model |
| Output review | Formal review for external communications |
| Audit trail | Full logging with 6+ year retention |

---

*Updated: January 2026 | Version: v1.1*
