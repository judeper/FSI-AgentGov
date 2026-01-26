# Control 3.7: PPAC Security Posture Assessment - Portal Walkthrough

> This playbook provides step-by-step portal configuration guidance for [Control 3.7](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md).

---

## Prerequisites

- Power Platform Admin role
- Entra Security Admin role for Defender integration
- Power BI Pro license for advanced reporting

---

## Step 1: Access Security Dashboard

**Portal Path:** Power Platform Admin Center > Security

1. Navigate to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select **Security** in the left navigation
3. Review the Security dashboard components

---

## Step 2: Review Security Page Overview

The Security page provides four tabs:

| Tab | Purpose | Key Metrics |
|-----|---------|-------------|
| **Overview** | Security recommendations | Top recommendations, linked controls |
| **Health** | Posture recommendations | Recommendations list |
| **Monitor** | Audit logs and sign-ins | Activity monitoring |
| **Controls** | Link to Copilot settings | Configuration access |

---

## Step 3: Review Security Recommendations

**Portal Path:** PPAC > Security > Overview

The Overview tab displays security recommendations:

| Section | Content |
|---------|---------|
| **Top recommendations** | Priority security actions |
| **Linked recommendations** | Related security controls |

Click "See more recommendations in Health" to view full list.

---

## Step 4: Review Health Recommendations

**Portal Path:** PPAC > Security > Health

The Health tab shows all recommendations:

| Column | Description |
|--------|-------------|
| **Recommendation** | Security improvement |
| **Recommendation status** | Not started / In progress / Completed |
| **Risk level** | High / Medium / Low |
| **Category** | Security area |

**Common Recommendations:**

| Recommendation | Category | Risk |
|----------------|----------|------|
| Enable managed environments | Environment | High |
| Configure DLP policies | Data protection | High |
| Enable Copilot Studio security settings | AI governance | Medium |
| Restrict sharing scope | Access control | Medium |

---

## Step 5: Configure Monitor Tab

**Portal Path:** PPAC > Security > Monitor

Monitor tab provides links to:

| Section | Destination |
|---------|-------------|
| **Audit logs** | Unified audit log |
| **Sign-ins** | Entra ID sign-in logs |
| **Activity** | Power Platform activity |

---

## Step 6: Access Controls Configuration

**Portal Path:** PPAC > Security > Controls

The Controls tab links to:

- Copilot Studio settings
- Generative AI configuration
- Security policies

---

## Step 7: Create Posture Assessment Report

Build a periodic assessment report:

| Section | Content |
|---------|---------|
| **Summary Score** | Overall posture rating |
| **Recommendations Status** | Count by status |
| **Risk Distribution** | Count by risk level |
| **Trend** | Score over time |
| **Action Items** | Open recommendations |

---

## Step 8: Integrate with Microsoft Defender

For enhanced security visibility:

1. Navigate to Microsoft Defender portal
2. Configure Power Platform connector
3. Enable threat detection for agents
4. Review security alerts

---

---

[Back to Control 3.7](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
