# Microsoft Learn Documentation Changes

**Run Date:** 2026-06-24
**Run Time:** 2026-06-24T09:32:54.216017+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 5 |
| MEDIUM Changes | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | whats-new | HIGH | 2.25, 2.5, 2.10 | Review and update |
| 2 | ...management-settings-policy-indicators | HIGH | 1.12 | Update portal-walkthrough |
| 3 | endpoint-dlp-learn-about | HIGH | 1.17 | Review and update |
| 4 | dlp-configure-endpoint-settings | HIGH | 1.17 | Review and update |
| 5 | agent-id-governance-overview | HIGH | 3.6, 2.26, 1.11 | Review and update |
| 6 | alerts-overview | HIGH | 2.9 | Review and update |
| 7 | whats-new | CRITICAL | None | Monitor |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Insider Risk Indicators

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:54392d5c29b9faff326ff9da57adb987ccf1bff323f75979c32ab4fda665ff03

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -145,7 +145,7 @@ Gather data of interest (for example, downloading Power BI reports).
 Obfuscate the data gathered or change protection (for example, downgrading or removing sensitivity labels of Power BI or Lakehouse assets).
 Exfiltrate the data (for example, sharing Lakehouse data with people outside the organization).
-Generative AI apps indicators (preview)
+Generative AI apps indicators
 These indicators include policy indicators for numerous generative AI applications. Use these indicators in policies to analyze interactions (prompts and responses) entered into these applications and help detect inappropriate or risky interactions or sharing of confidential information. These indicators include the following generative AI applications:
 Microsoft Copilot experiences
 : Support for user interactions in
@@ -192,6 +192,35 @@ Important
 When you select this indicator, you create a Communication Compliance policy. If you modify this policy in Communication Compliance, you might need to pay for
 pay-as-you-go billing
+.
+For Microsoft Copilot experiences and Enterprise AI apps, you can select which specific generative AI apps you want to monitor. By default, all available apps are selected. You can deselect apps that aren't relevant to your organization to reduce alert noise and avoid unnecessary pay-as-you-go billing charges. When an app is deselected, signals from that app aren't processed and no cost is incurred.
+Select generative AI apps to monitor
+Note
+For
+Microsoft Copilot experiences
+and
+Enterprise AI apps
+only, you can review and deselect apps to optimize costs and reduce alert noise.
+In the Microsoft Purview portal, go to
+Insider Risk Management
+>
+Settings
+>
+Policy indicators
+.
+Expand
+Generative AI apps indicators
+.
+For
+Microsoft Copilot experiences
+and
+Enterprise AI apps
+, select
+Choose apps to monitor
+.
+From the side panel, you can select or clear the checkbox for each app to include or exclude it from monitoring.
+Sel
```

---

## HIGH: Control Review Recommended

### 1. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:d98cde44bb12faf881de80448c9c2e2075731f0d67da3c11525fa6ab25678967

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -35,6 +35,19 @@ Releases roll out over several days. New or updated functionality might not appear immediately.
 Notable changes
 The following sections list features released in the past months, with links to related information.
+June 2026
+(Production-ready preview) Use the
+new agent experience
+in Copilot Studio to build agents. The new experience uses an enhanced orchestration runtime for improved response quality and reasoning, available alongside the classic experience.
+Use
+Microsoft IQ
+in the new agent experience to connect your agent to organizational data, giving it access to emails, calendar events, files, Teams messages, and people information.
+Build and reuse
+skills
+in the new agent experience to extend your agent's capabilities with modular, self-contained sets of instructions. Create a skill once, add it to multiple agents, and export it as a Markdown file or package to share with others.
+Turn on
+memory
+in the new agent experience to give your agent persistent context across interactions. It captures user preferences and patterns, stores them per user, and applies them to deliver more relevant and personalized responses over time.
 May 2026
 (General availability)
 Computer use

```

---

### 2. Endpoint DLP

**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:d1a10bb22bf7543abba0140d5fe896cff906035557aa88137c009a233b03fd82

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -42,13 +42,7 @@ Note
 Endpoint DLP cannot detect the sensitivity label from another tenant on a document.
 Endpoint DLP Windows 10/11 and macOS support
-Endpoint DLP allows you to onboard devices running the following versions of Windows Server:
-Windows Server 2019 (
-November 14, 2023âKB5032196 (OS Build 17763.5122) - Microsoft Support
-)
-Windows Server 2022 (
-November 14, 2023 Security update (KB5032198) - Microsoft Support
-)
+Endpoint DLP allows you to onboard devices running Windows Server 2019 and later versions.
 Note
 Installing the supported Windows Server KBs disables the
 Classification
@@ -59,7 +53,7 @@ Once properly configured, the same data loss protection policies can be automatically applied to both Windows PCs and Windows servers.
 Setting
 Subsetting
-Windows 10, 1809 and later, Windows 11, Windows Server 2019, Windows Server 2022 (21H2 onwards) for Endpoints (X64)
+Windows 10, 1809 and later, Windows 11, Windows Server 2019 and later versions for Endpoints (X64)
 macOS (three latest released versions)
 Notes
 Advanced classification scanning and protection
@@ -168,7 +162,7 @@ Other settings
 Setting
 Windows 10/11, Windows 10, 1809 and later, Windows 11
-Windows Server 2019, Windows Server 2022 (21H2 onwards) for Endpoints (X64)
+Windows Server 2019 and later versions for Endpoints (X64)
 macOS (three latest released versions)
 Archive file
 Supported
@@ -188,7 +182,7 @@ Endpoint DLP enables you to audit and manage the following types of activities users take on sensitive items that are physically stored Windows 10, Windows 11, or macOS devices.
 Activity
 Description
-Windows 10 (21H2, 22H2), Windows 11 (21H2, 22H2), Windows Server 2019, Server 2022 (21H2 onwards) for Endpoints (X64)
+Windows 10 (21H2, 22H2), Windows 11 (21H2, 22H2), Windows Server 2019 and later versions for Endpoints (X64)
 Windows 11 (21H2, 22H2) for Endpoints (ARM64)
 macOS three latest released versions
 Auditable/
@@ -582,9 +576,6 @@ Just-in-time protection 
```

---

### 3. Configure Settings

**URL:** https://learn.microsoft.com/en-us/purview/dlp-configure-endpoint-settings
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:3a68f59f8958dacb4d4f036695f269642861784d427ed1372517a913f5fe63ca

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -1054,13 +1054,7 @@ Always-on diagnostics for endpoint DLP
 .
 Enable Endpoint DLP for Windows Servers
-Endpoint DLP supports the following versions of Windows Server:
-Windows Server 2019 (
-November 14, 2023âKB5032196 (OS Build 17763.5122) - Microsoft Support
-)
-Windows Server 2022 (
-November 14, 2023 Security update (KB5032198) - Microsoft Support
-)
+Endpoint DLP supports Windows Server 2019 and later versions.
 After you
 onboard a Windows Server
 , turn on Endpoint DLP support to apply endpoint protection.

```

---

### 4. Governing Agent Identities

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:768b0983ff28c1ea15b541c91f792a523bfa3631188135b20ce84188de0c51e6

**Affected Controls:**
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 2.26: Control 2.26: Entra Agent ID — Identity Governance for Agents
  - File: `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`

**What Changed:**
```diff
--- +++ @@ -25,31 +25,19 @@ Microsoft Entra allows you to ensure that the right people have the right access to the right apps and services at the right time. With the addition of the Microsoft agent identity platform, managing the access rights of agents in the same way is just as important in the governance lifecycle of your organization's identities. The Microsoft agent identity platform introduces the concept of Agent Identities (IDs). Agent identities are accounts within Microsoft Entra ID that provide unique identification and authentication capabilities for AI agents.
 This allows agent identities to be governed with Microsoft Entra features in the same style as you would govern human identities. With Agent identities, you can govern and manage the identity and access lifecycle of agents, ensuring the agents have a responsible person providing oversight throughout the agent lifecycle and agent's access does not persist longer than it is needed. This article provides an overview of how Microsoft Entra can be utilized to govern agent identities.
 License requirements
-Microsoft Entra Agent ID is a product within Microsoft Entra that provides the platform for creating and managing agent identities and agent identity blueprints. Agent ID is available for all Microsoft Entra customers.
+Using
+Microsoft Entra ID Governance
+for agent identities requires one of the following license plans:
+Microsoft 365 E7
+, which includes Agent 365 and Microsoft Entra Suite, to provide governance of user and agent identities.
 Microsoft Agent 365
-enables agents to operate across Microsoft 365 services and enterprise workflows, which requires a
+license paired with at least Microsoft Entra P1 or Microsoft 365 E3.
+For more information, see
+Microsoft Agent 365 plans and pricing
+. For the full list of agent-specific capabilities, refer to the
 Microsoft Agent 365
-license for each user. For pricing details, see
-Microsoft Agent 365 plans and pricing
-.
-Extending Microsoft Entra
```

---

### 5. Azure Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-overview
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:b4c42aee7f79c078456233cffccd860d4e0824217d3a2d414739832a958cf354

**Affected Controls:**
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/alerting-configuration.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -35,6 +35,11 @@ An
 alert
 is triggered if the conditions of the alert rule are met. The alert initiates the associated action group and updates the state of the alert. If you're monitoring more than one resource, the alert rule condition is evaluated separately for each of the resources, and alerts are fired for each resource separately.
+Where supported, a fired alert can also become the starting point for investigation workflows in Azure Monitor, including the
+Azure Copilot Observability Agent
+and
+Azure Monitor issues
+.
 Alerts are stored for 30 days and are deleted after the 30-day retention period. You can see all alert instances for all of your Azure resources on the
 Alerts page
 in the Azure portal.

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Purview What's New
**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:d0fe02a0aae9e8e1f5c66a6c2e485a79a1fa460998df5f2a34df66edfa229884

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*