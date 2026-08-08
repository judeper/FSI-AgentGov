# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-08
**Run Time:** 2026-08-08T06:54:59.825001+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| MEDIUM Changes | 1 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | security-and-governance | HIGH | 1.3, 1.4, 1.8, 1.28, 1.1, 1.5, 2.8 | Update portal-walkthrough |
| 2 | plan-designer | MEDIUM | None | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Security and Governance

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:fcba00c2ca2b078403a490514dcd8eda3e76635a7c1839f32e9592ee060fbcda

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)

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
@@ -24,16 +24,18 @@ Summarize this article for me
 Copilot Studio follows a number of security and governance controls and processes, including geographic data residency, data loss prevention (DLP), multiple standards certifications, regulatory compliance,
 environment routing
-, and regional customization. For more information and details on how Copilot Studio agent handle data, see
+, and regional customization. For details on data residency and handling practices for Copilot Studio agents, see
 Geographic data residency in Copilot Studio
 .
 This article provides an overview of the security practices followed by Copilot Studio, a list of security and governance controls and features, and examples and suggestions for employing safety and security within Copilot Studio for your agent makers and users.
+Microsoft Agent 365
+serves as a central control plane to observe, govern, and secure Copilot Studio agents. For organizations that onboard Agent 365, Copilot Studio agents can be represented as identities in Microsoft Entra. These identities can be governed with controls such as Conditional Access, role-based and attribute-based access controls, and access governance workflows. Admins can use Agent 365 for centralized observability and policy enforcement across Copilot Studio agents, in addition to existing Power Platform and Microsoft 365 governance mechanisms.
 Security and governance controls
 Control
 Core scenario
 Related content
 Agent runtime protection status
-Makers can see the security status of their agents from the Agents page.
+Makers can see the security status of their agents from the Agents page. For organizations that onboard Agent 365, this status is complemented by centralized agent inventory and ownership telemetry in Agent 365 experiences.
 Agent runtime protection status
 Data policy controls
 Admins can use data policies in t
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Testing Guidance
**URL:** https://learn.microsoft.com/en-us/power-apps/maker/plan-designer/plan-designer
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8a6b41a4f64b4752d77a28a57e3ef98e2a49449df4667816b3c435223ab9997d

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*