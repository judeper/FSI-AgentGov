# Portal Walkthrough: Control 1.6 - Microsoft Purview DSPM for AI

**Last Updated:** March 2026
**Portal:** Microsoft Purview
**Estimated Time:** 2-3 hours

> This playbook provides portal configuration guidance for [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md).

---

## Prerequisites

Before starting, confirm:

- E5 or E5 Compliance licenses active
- Purview portal access verified
- Unified audit logging enabled
- Microsoft 365 Copilot deployed to users
- Purview Compliance Admin role assigned
- Agent inventory available (from Control 3.1)

---

## Accessing DSPM for AI

1. Open [Microsoft Purview](https://purview.microsoft.com)
2. In the left navigation, locate **Solutions** (or expand the nav if collapsed)
3. Select **DSPM for AI**
4. Use the DSPM sub-pages: **Overview**, **Recommendations**, **Reports**, **Policies**, **Activity explorer**, **Data risk assessments**

---

## Get Started Setup (4 Steps)

The Overview page provides four required setup steps:

| Step | Task | Description | Time |
|------|------|-------------|------|
| 1 | **Activate Microsoft Purview Audit** | Get insights into user interactions with Microsoft 365 Copilot | 7 min |
| 2 | **Install Microsoft Purview browser extension** | Detect risky activity and get insights into other AI apps | 1 hour |
| 3 | **Onboard devices to Microsoft Purview** | Prevent sensitive data from leaking to other AI apps | 1 hour |
| 4 | **Extend your insights for data discovery** | Discover sensitive data in interactions with other AI apps | 10 min |

---

## Step 1: Activate Microsoft Purview Audit (Required)

1. In **Purview > DSPM for AI > Overview**, open the **Get started** card
2. Select **Activate Microsoft Purview Audit** and complete the guided workflow
3. In **Purview > Audit**, confirm audit is enabled and recent events are present

**Verification artifacts:**

- Screenshot: DSPM Get started shows Step 1 completed
- Screenshot: Purview Audit page indicates logging is enabled
- Export: Small sample of audit results demonstrating recent activity

---

## Steps 2-4: Extend Visibility (Recommended)

Steps 2-4 expand coverage to other AI apps. Complete as appropriate for your scope:

- **Step 2**: Deploy Purview browser extension via Intune/Endpoint Manager
- **Step 3**: Onboard devices to Purview for endpoint protection
- **Step 4**: Enable extended data discovery for third-party AI apps

---

## Overview Dashboard Configuration

### View Options

| View | Coverage |
|------|----------|
| **All AI apps** | Microsoft 365 Copilot, Copilot Studio, third-party AI |
| **Microsoft 365 Copilot** | M365 Copilot interactions only |

### Dashboard Sections

- **Recommendations**: Data protection actions, AI regulation guidance
- **Reports**: Total interactions, sensitive interactions per AI app
- **Metrics**: Interactions with sensitive data (last 30 days)

---

## Recommendations Configuration

### Status Tracking

| Status | Description |
|--------|-------------|
| **Not Started** | Actions pending implementation |
| **Dismissed** | Actions marked as not applicable |
| **Completed** | Actions successfully implemented |

### Key Recommendations for FSI

| Recommendation | Priority | FSI Impact |
|----------------|----------|------------|
| Protect sensitive data in Copilot responses | High | Customer data protection |
| Detect risky interactions in AI apps | High | Insider threat detection |
| Protect items with sensitivity labels | High | Classification enforcement |
| Secure interactions from enterprise AI apps | Medium | Third-party AI governance |

---

## Reports Configuration

### Report Filters

| Filter | Options |
|--------|---------|
| **Copilot experiences & agents** | Microsoft 365 Copilot, Copilot Studio agents |
| **Enterprise AI apps** | ChatGPT Enterprise, other corporate AI |
| **Other AI apps** | Consumer AI applications |

### FSI Evidence Collection

1. Go to **DSPM for AI > Reports**
2. Select a timeframe (e.g., last 7/30 days)
3. Capture views for evidence pack:
   - Total interactions trend
   - Sensitive interactions summary (by AI app and sensitive info type)

---

## Policies Configuration

### Policy Types Available

| Solution | Purpose |
|----------|---------|
| **Data Loss Prevention** | Prevent sensitive data exposure |
| **DSPM for AI** | AI-specific protections |
| **Insider Risk Management** | Risky behavior detection |
| **Communication Compliance** | Content monitoring |

### Policy Management

1. Navigate to **DSPM for AI > Policies**
2. View policies grouped by solution type
3. Check status (On/Off) for each policy
4. Review last modified date and owner

---

## Activity Explorer Configuration

### Available Filters

| Filter | Purpose |
|--------|---------|
| **Timestamp** | Date range selection |
| **Activity type** | AI Interaction, Sensitive info types |
| **AI app category** | Copilot experiences & agents, Enterprise AI, Other |
| **Agent name** | Specific agent identifier |
| **User participant** | User who performed the interaction |
| **Sensitive info type** | Types of sensitive data detected |

### Evidence Collection

1. Go to **DSPM for AI > Activity explorer**
2. Filter **AI app category** to **Copilot experiences & agents**
3. Filter **Activity type** to **AI Interaction**
4. Optionally filter by **Agent name** for enterprise agents
5. Use **Export** to produce CSV for evidence repository

---

## Data Risk Assessments

### Three-Step Process

| Step | Action | Description |
|------|--------|-------------|
| **1. Identify** | Review assessments | Weekly results from default or custom assessments |
| **2. Protect** | Apply controls | Limit Copilot access, apply labels and retention |
| **3. Monitor** | Ongoing review | SharePoint site and access reviews |

### Weekly Assessment Configuration

DSPM for AI automatically runs weekly risk assessments for the top 100 SharePoint sites based on usage. To configure and monitor these assessments:

1. Navigate to **Microsoft Purview > DSPM for AI**
2. Complete Get Started wizard (if not already done)
3. Go to **Data risk assessments** in the left navigation
4. View default weekly assessment status — confirm top 100 sites being scanned
5. Navigate through dashboard tabs to review risk insights:
   - **Overview** — Summary insights per site/workspace (sites scanned, sensitive items, risk score)
   - **Identify** — Data scanned vs. not scanned for SITs (coverage percentage, unscanned volumes)
   - **Protect** — Oversharing remediation options (org-wide sharing, external sharing)
   - **Monitor** — Sharing breakdown by access type (specific people, external, organization-wide)

**Timing Guidance:**

- **Initial assessment results** appear after approximately 4 days
- **Subsequent weekly results** refresh within 48 hours of assessment completion
- **Custom assessments** for specific sites produce results within 4 days

**FSI-Specific Portal Configuration:**

For regulated environments, prioritize remediation of sites showing "Organization-wide" or "External" sharing classifications in the Monitor tab. Establish monitoring workflows aligned with zone-specific remediation SLAs:

- **Zone 1:** 30-day remediation SLA — review monthly
- **Zone 2:** 14-day remediation SLA — review weekly
- **Zone 3:** 7-day remediation SLA — review daily

### Running Oversharing Assessments

1. Navigate to **DSPM for AI > Data risk assessments**
2. Run the default assessment for defined scope
3. Wait for completion (4 days for initial results, 48 hours for refresh)
4. Review results and record:
   - Assessment name
   - Scope (sites/users/data sources)
   - Run timestamp and completion timestamp
   - Overshared items count and severity

### Custom Assessments

For high-priority sites not in the top 100, create custom assessments:

1. Click **+ Create custom assessment**
2. Define data sources and users to assess
3. Wait for assessment completion (approximately 4 days)
4. Review results for overshared items
5. Take remediation actions based on zone-specific SLAs

---

## Enhanced DSPM AI Observability (Preview)

!!! warning "Preview Feature — UI may change at GA"
    The unified DSPM experience consolidating DSPM and DSPM for AI is in preview. GA rollout was expected June 2026 at time of writing (per MC1191257); check Message Center for the latest timeline. Portal navigation and feature availability may change before general availability.

The unified DSPM experience provides a single interface for monitoring data security posture across all data types, including AI-specific interactions. This section covers configuring enhanced DSPM AI Observability capabilities that help FSI organizations meet comprehensive agent supervision requirements.

### Accessing Unified DSPM Experience

!!! info "Preview Ring Enrollment Required"
    The unified DSPM experience is gradually rolling out to tenants. If your tenant is not yet in the preview ring, these features will not be visible. Monitor Message Center for MC1191257 availability notifications.

1. Navigate to **Microsoft Purview** (https://purview.microsoft.com)
2. In the left navigation, select **Solutions** > **Data Security Posture Management**
   - For preview-enabled tenants: Single unified DSPM dashboard appears
   - For classic tenants: Separate "DSPM for AI" navigation remains (legacy experience)
3. Verify unified experience by checking for integrated AI and non-AI data security metrics on a single dashboard

### Agent Risk Observability Dashboard

The unified DSPM experience includes agent risk observability dashboards that provide per-agent risk scoring based on data sensitivity, access patterns, and policy violations:

1. From **Purview > Data Security Posture Management**, select **AI Risk Dashboard** (or equivalent unified dashboard tab)
2. Review agent risk scores:
   - **High Risk (Red):** Agents with policy violations, excessive data access, or sensitive data exposure
   - **Medium Risk (Yellow):** Agents with elevated data sensitivity interactions or access pattern anomalies
   - **Low Risk (Green):** Agents with normal data access patterns and no policy violations
3. Click on a high-risk agent to view contributing factors:
   - Data sensitivity level accessed (Highly Confidential, Confidential, General)
   - Access pattern analysis (sites/files accessed beyond normal baseline)
   - Policy violation details (DLP policy blocks, sensitivity label mismatches)
   - Oversharing assessment findings (broad permission sites accessed by agent)
4. Export agent risk summary for compliance reporting: Click **Export** to generate CSV

### Enhanced Activity Explorer

The unified DSPM experience includes improved Activity Explorer with advanced filtering and search capabilities:

1. Navigate to **Purview > Data Security Posture Management > Activity explorer**
2. Use enhanced filters:
   - **Multi-Agent Selection:** Filter by multiple agents simultaneously (shift-click agent names)
   - **Data Classification Filter:** Filter events by sensitivity label or sensitive info type
   - **Access Pattern Filter:** Show events where agent accessed data outside normal scope
   - **Policy Violation Filter:** Show only events triggering DLP or IRM policy alerts
3. Use advanced search:
   - Enter keywords in search box to filter across all event fields (user, agent, site, file)
   - Use operators: `AND`, `OR`, `NOT` for complex queries
   - Example: `Agent:"Expense Approver" AND SensitivityLabel:"Highly Confidential"`
4. Export filtered results:
   - Select date range (up to 90 days for standard export, 6 years for compliance export)
   - Click **Export** > **Enhanced CSV** (includes additional metadata fields vs. classic export)
   - Verify export includes: Event timestamp, User, Agent, Activity type, Data source, Sensitivity label, Policy actions

### Unified Dashboard Configuration

The unified dashboard consolidates data security posture metrics across AI and non-AI data:

1. Navigate to **Purview > Data Security Posture Management > Overview**
2. Review integrated dashboard sections:
   - **Overall Data Security Posture:** Combined risk score across all data types
   - **AI-Specific Risks:** Agent risk scores, sensitive AI interactions, policy violations
   - **Data Classification Coverage:** Labeled vs. unlabeled content across AI-accessible locations
   - **Oversharing Summary:** Sites with broad permissions accessible by agents
3. Configure dashboard widgets:
   - Click **Customize dashboard** to add/remove widgets
   - Recommended for Zone 3: Add "High-Risk Agent Summary" and "Daily AI Policy Violations" widgets
4. Set up dashboard email notifications:
   - Click **Configure alerts** > **Dashboard digest email**
   - Schedule: Daily for Zone 3, Weekly for Zone 2, Monthly for Zone 1
   - Recipients: Compliance Officer, AI Governance Lead, CISO (Zone 3 only)

### Data Classification Insights

Enhanced DSPM AI Observability provides real-time insights into how agents interact with classified data:

1. Navigate to **Purview > Data Security Posture Management > Classification insights**
2. Review agent classification metrics:
   - **Labeled Data Access:** Percentage of agent interactions with sensitivity-labeled content
   - **Unlabeled Data Exposure:** Volume of unlabeled content accessed by agents (potential classification gap)
   - **Label Mismatch Events:** Instances where agent received higher sensitivity data than declared scope
3. Configure classification alerts:
   - Set threshold for unlabeled data access (e.g., alert if >10% of agent interactions involve unlabeled content)
   - Enable "Label Mismatch" alert for Zone 3 agents (requires immediate investigation)
4. Export classification report for compliance evidence

### Zone-Specific Configuration Guidance

**Zone 1 (Personal Productivity):**
- Monthly unified dashboard review sufficient
- No agent risk alerts required
- Export quarterly classification insights for trend analysis

**Zone 2 (Team Collaboration):**
- Weekly unified dashboard review
- Enable agent risk email digest (weekly)
- Configure Activity Explorer saved searches for team agents
- Export monthly classification insights and agent risk summaries

**Zone 3 (Enterprise Managed):**
- Daily unified dashboard review required
- Enable real-time agent risk alerts (high-risk agents trigger immediate notification)
- Configure Activity Explorer advanced filters for all Zone 3 agents
- Daily export of enhanced Activity Explorer data for compliance repository
- Weekly agent risk observability report to Compliance Officer and CISO

---

## MIP Labels for Agents (Preview)

### Configuration Path

1. Navigate to **Microsoft Purview > Information protection**
2. Select **Auto-labeling > Create policy**
3. Choose **AI interactions** as the scope
4. Configure label conditions for agent responses
5. Set actions (apply label, block response, notify compliance)

### Zone-Specific Configuration

| Zone | MIP Configuration | Blocked Labels |
|------|------------------|----------------|
| **Zone 1** | No label enforcement | N/A |
| **Zone 2** | Label inheritance; warn on Confidential | Highly Confidential |
| **Zone 3** | Strict enforcement; block restricted | Highly Confidential, Restricted, MNPI |

---

[Back to Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
