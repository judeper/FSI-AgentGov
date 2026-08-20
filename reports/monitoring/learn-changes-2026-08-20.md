# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-20
**Run Time:** 2026-08-20T06:47:12.741975+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| MEDIUM Changes | 1 |
| Redirects | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...rosoft.com/en-us/microsoft-agent-365/ | MEDIUM | 3.13, 3.2, 3.6, 3.1, 3.14, 2.25, 2.12, 2.5, 2.6, 1.7 | Update portal-walkthrough |
| 2 | overview | HIGH | 3.13, 3.1, 2.25, 2.12, 2.6 | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Agent 365 Documentation Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:36939cbe3a6b317d232c1a8d69fc88e42e2af8dcd72dde9299b1174b8b1b3d7f

**Affected Controls:**
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.25/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/index.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/opentelemetry-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -1,9 +1,9 @@ Microsoft Agent 365 documentation
 Agent 365 is the control plane for IT and security leaders to observe, secure, and govern agents across the organization.
-Get Microsoft Agent 365 for IT admins
+Why does an enterprise need Agent 365?
 Explore Microsoft Agent 365
 Microsoft Agent 365 allows you to manage all your organizationâs agents at scale, regardless of where they originate.
-Why does an enterprise need Agent 365?
+Meet Microsoft Agent 365
 Transform fragmented, high-risk experimentation into trusted, enterprise-wide AI operations with a unified control plane that makes agents visible, governed, and secure.
 Learn more
 Govern without slowing innovation
@@ -25,4 +25,4 @@ Learn more
 Learn more about Microsoft Agent 365
 Agent 365 extends the existing infrastructure that you use for managing people to agents. It equips your agents with the same apps and protections, tailored to agent needs, saving IT time and effort on integrating agents into business processes.
-Get started+Prepare and learn
```

---

### 2. Agent 365 Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/overview
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:3424165830dd8ee85d166cf43f9c319f3e0c2b9e79a61fcec05f7dfb0506d0bb

**Affected Controls:**
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.25/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -33,25 +33,23 @@ Microsoft Agent 365 gives organizations real-time visibility into their agentic environment, helping admins understand how agents are used, identify performance or risk signals early, and take action before issues impact the business. Admins can now view all their agents in a single, centralized registry providing a unified view of agent adoption, activity, and agent health. These insights help leaders and AI admins stay in control, operate efficiently, and maximize the value of their agent investments from a centralized AI admin experience. Role-specific oversight extends this visibility to security and business leaders, ensuring the right stakeholders have the tailored insights they need to manage risk and measure agent value within their domains. Learn more:
 Agent registry
 ,
-Registry sync
-,
-Agent Map
+Agent map
 .
 Govern
 Establish consistent guardrails for AI agents by centralizing lifecycle management, access control, and compliance across the enterprise. Through the Agent 365 registry in the Microsoft 365 admin center, Microsoft Entra, and Microsoft Purview, admins can intentionally manage the lifecycle of their organizationâs agents while ensuring the right permissions, policies, and reviews are in place. Together, these controls help organizations reduce risk, stay audit-ready, and ensure agents remain aligned with organizational policies and business needs. Learn more:
 Agent management overview
 .
 Secure
-Microsoft Agent 365 delivers endâtoâend protection for every agent by extending Microsoftâs enterpriseâgrade identity, data, and threatâdefense capabilities across your AI ecosystem. Microsoft Entra enforces consistent, riskâbased access controls for users and agents acting on their behalf, while MicrosoftPurview provides deep visibility into data risks with information protection, DLP, and risk sa
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Agent 365 Documentation Hub
**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:36939cbe3a6b317d232c1a8d69fc88e42e2af8dcd72dde9299b1174b8b1b3d7f

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-messages-capacity | https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-copilot-credits-capacity |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*