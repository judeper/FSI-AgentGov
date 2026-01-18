# Control 1.6: Microsoft Purview DSPM for AI - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md).

---

## Prerequisites

Before starting, confirm:

- E5 or E5 Compliance licenses active
- Purview portal access verified
- Unified audit logging enabled
- Microsoft 365 Copilot deployed to users
- Compliance Administrator role assigned
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

### Running Oversharing Assessments

1. Navigate to **DSPM for AI > Data risk assessments**
2. Run the default assessment for defined scope
3. Wait for completion
4. Review results and record:
   - Assessment name
   - Scope (sites/users/data sources)
   - Run timestamp and completion timestamp
   - Overshared items count and severity

### Custom Assessments

1. Click **+ Create custom assessment**
2. Define data sources and users to assess
3. Review results for overshared items
4. Take remediation actions

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

*Updated: January 2026 | Version: v1.1*
