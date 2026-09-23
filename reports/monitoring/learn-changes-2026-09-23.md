# Microsoft Learn Documentation Changes

**Run Date:** 2026-09-23
**Run Time:** 2026-09-23T10:57:24.515571+00:00
**Total URLs Checked:** 231

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 3 |
| MEDIUM Changes | 2 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Review and update |
| 2 | ...pilot-studio-copilot-credits-capacity | MEDIUM | None | Review optional |
| 3 | planned-features | HIGH | 3.8, 1.4, 2.25, 2.17 | Review and update |
| 4 | restricted-content-discovery | MEDIUM | 4.6, 4.1, 4.7, 1.14, 1.3 | Review and update |

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:c2efa6b0de538e66c4ec178ca2bb53b479fbb5df22110c2b249772d97b0b0fef

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -258,6 +258,8 @@ By: H3 Solutions Inc.
 Autenti E-Signature Workflow
 By: Autenti sp. z o.o.
+AuthBinder
+By: Authbinder
 Autodesk Data Exchange
 By: Autodesk, Inc.
 AutoReview
@@ -322,6 +324,8 @@ By: Databricks Inc.
 Azure DevOps
 By: Microsoft
+Azure DevOps MCP
+By: Microsoft
 Azure Digital Twins
 By: Microsoft Corporation
 Azure Event Grid
@@ -368,6 +372,8 @@ By: Microsoft
 Basecamp 3
 By: Microsoft
+BastionGPT
+By: Bastion Intelligence
 BBC News (Independent Publisher)
 By: krautrocker
 Beauhurst (Independent Publisher)
@@ -694,6 +700,8 @@ By: NovaGL
 Courier (Independent Publisher)
 By: Troy Taylor
+CourtListener (Independent Publisher)
+By: krautrocker
 COVID-19 JHU CSSE (Independent Publisher)
 By: Woong Choi
 CPQSync
@@ -731,6 +739,16 @@ D365 Contact Center Admin MCP
 By: Microsoft
 D365 Customer Insights MCP
+By: Microsoft
+D365 CX Customer Insights MCP
+By: Microsoft
+D365 CX MCP Server
+By: Microsoft
+D365 CX Sales MCP Server
+By: Microsoft
+D365 CX Service MCP Server
+By: Microsoft
+D365 CX WEM MCP Server
 By: Microsoft
 D7Messaging
 By: Signtaper Technologies FZCO
@@ -922,11 +940,11 @@ By: Microsoft
 Dynamics 365 Fraud Protection
 By: Microsoft
+Dynamics 365 MCP Server
+By: Microsoft
 Dynamics 365 Sales Insights
 By: Microsoft
 Dynamics 365 Sales MCP Server
-By: Microsoft
-Dynamics 365 Service MCP
 By: Microsoft
 Dynamics NAV
 By: Microsoft
@@ -1427,7 +1445,7 @@ IFTTT MCP Server Streamable
 By: IFTTT Inc
 iLovePDFv2
-By: iLovePDF
+By: i Love PDF
 iLoveSign
 By: iLoveSign
 iManage AI
@@ -1694,6 +1712,8 @@ By: Microsoft
 Mailform
 By: Mailform, Inc.
+Mailgun
+By: Sinch Sweden AB
 Mailinator
 By: Troy Taylor
 MailJet (Independent Publisher)
@@ -1828,6 +1848,8 @@ By: Microsoft Translator
 Mime Automation (Independent Publisher)
 By: Andreas Cieslik
+MiniPDF (Independent Publisher)
+By: dinhvansh
 MiniSoup HTML Parser (Independent Publisher)
 By: Shogo Shindo
 Mintlify (Independent Publisher)
@@ -1968,7 +1990,7 @@ By: Nodefusion d.o.o
 Nosco
 By: 
```

---

### 2. Planned Features (2026 Wave 1) [Preview]

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:0a34b3dfd4d1e25d05e150c071e1fe785cb66a9a15fa6cc389ea894073a7395f

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/mcp-server-governance/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -43,6 +43,10 @@ Copilot Cowork: Now Available in Frontier
 Introducing multi-model intelligence in Researcher
 View details
+September 14
+September 4
+September 1
+July 24
 July 9
 July 2
 June 24
@@ -55,10 +59,9 @@ May 1
 April 30
 April 27
-April 16-24
-April 7-13
-March 30
-March 9
+September 4
+Available today: OpenAI GPT-6 Astra in Microsoft Copilot
+View details
 July 24
 Available today: Anthropic’s Claude Opus 5 in Microsoft 365 Copilot
 View details
@@ -96,6 +99,15 @@ Generally available
 Now available: Brand Kit and Skills in Copilot in PowerPoint
 Brand Kit and Skills in Copilot for PowerPoint bring approved branding and reusable workflows directly into PowerPoint, helping Copilot create presentations that align with your organization's standards from the start. You can focus on shaping your story instead of formatting slides and repeating review processes, helping you create polished presentations faster.
+Learn more
+Try now
+Rolling out to Copilot Cowork and Copilot Studio
+September 4
+Available today: OpenAI GPT-6 Astra in Microsoft Copilot
+View details
+Rolling out to Copilot Cowork and Copilot Studio
+Available today: OpenAI GPT-6 Astra in Microsoft Copilot
+OpenAI GPT-6 Astra is now available in Copilot Cowork and Copilot Studio, expanding the frontier model options available to customers. GPT-6 Astra helps you delegate larger, more complex work to Copilot, so you can focus on reviewing outcomes, making decisions, and driving work forward.
 Learn more
 Try now
 Rolling out to Copilot in Word, Excel, PowerPoint, Chat, and Copilot Studio
@@ -446,6 +458,10 @@ Get started
 Coming soon
 These features are currently in development.
+Build apps in Copilot Cowork and Copilot Studio
+Turn your ideas into business apps using natural language in Copilot Cowork and Copilot Studio. Describe what you need, then refine your app through conversation and connect it to your organization’s data and systems. When you publish, IT admins have centralized v
```

---

### 3. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:5e08e775d8397c4bc822d11d86af4689d3bbcbb901a6ba61ab06e36d55af7659

**Affected Controls:**
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -29,7 +29,6 @@ When a site has a Restricted Content Discovery policy applied to it, a Restricted tag is visible, as shown in the following screenshot:
 Restricted Content Discovery is designed as a temporary governance control that gives organizations time to review and right-size access while continuing their Copilot deployment.
 Note
-You can apply Restricted Content Discovery to up to 20,000 sites.
 Restricted Content Discovery doesn't change existing permissions. Users who already have access to content can continue to access that content directly.
 You can only apply this feature to SharePoint sites. It's not supported for OneDrive sites.
 Restricted Content Discovery doesn't affect searches that originate from site context or other intelligent experiences such as Microsoft 365 Feed and Recommendations.

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Copilot Studio Message Capacity
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-copilot-credits-capacity
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e86f8ff169249e7632057ac3531a0b61771bf28750dbd357950be5a5261306fa

---

### 2. Restricted Content Discovery
**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:5e08e775d8397c4bc822d11d86af4689d3bbcbb901a6ba61ab06e36d55af7659

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