# Microsoft Learn Documentation Changes

**Run Date:** 2026-07-11
**Run Time:** 2026-07-11T07:57:42.936664+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 3 |
| HIGH Changes | 5 |
| MEDIUM Changes | 6 |
| Redirects | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Review and update |
| 2 | cross-tenant-restrictions | MEDIUM | 2.1 | Review and update |
| 3 | power-platform-inventory | HIGH | 3.11 | Review and update |
| 4 | welcome-content | MEDIUM | None | Review optional |
| 5 | regions-overview | MEDIUM | 2.4 | Update portal-walkthrough |
| 6 | microsoft-365-copilot-overview | MEDIUM | 3.8 | Review optional |
| 7 | microsoft-365-copilot-privacy | HIGH | 2.23, 4.7, 4.6 | Update portal-walkthrough |
| 8 | m365-agents-blueprint | MEDIUM | 2.1, 2.3, 1.11 | Review optional |
| 9 | human-in-the-loop | HIGH | 2.17, 2.12 | Review and update |
| 10 | permissions-reference | CRITICAL | 2.23 | Monitor |
| 11 | restricted-access-control | HIGH | 4.1, 1.3 | Review and update |
| 12 | data-access-governance-reports | HIGH | 4.5, 4.2, 4.1, 4.4, 4.6, 1.3, 1.14 | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Regions Overview

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/regions-overview
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:332e7fc1117c1dc36eb3d0620061228c78bdd0a81821f75d667b56182560ea68

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

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

```

---

### 2. Data, Privacy, and Security

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:15c247eb38a856722fc0225f14a65c5b8c241d07b6505f97b8e98e84fb107d01

**Affected Controls:**
- Control 2.23: Control 2.23: User Consent and AI Disclosure Enforcement
  - File: `controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/4.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/sharepoint-copilot-preflight/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -42,10 +42,11 @@ , and
 blocking prompt injections (jailbreak attacks)
 .
-Anthropic models within Microsoft 365 Copilot experiences are provided under the Microsoft Product Terms and Data Protection Addendum.
-Learn more about Anthropic's safeguards.
-Anthropic models are out of scope for the EU Data Boundary and when available, in-country LLM processing commitments. For more information, see
-Anthropic as a subprocessor for Microsoft Online Services
+For information about models provided by Anthropic as a subprocessor within Microsoft 365 Copilot experiences, see
+Anthropic models in Microsoft Online Services
+.
+For information about models provided by OpenAI as a subprocessor within Microsoft 365 Copilot experiences, see
+OpenAI as a subprocessor in Microsoft Online Services
 .
 The information in this article is intended to help provide answers to the following questions:
 How does Microsoft 365 Copilot use your proprietary organizational data?
@@ -68,7 +69,7 @@ Microsoft 365 Copilot only surfaces organizational data to which individual users have at least view permissions. It's important that you're using the permission models available in Microsoft 365 services, such as SharePoint, to help ensure the right users or groups have the right access to the right content within your organization. This includes permissions you give to users outside your organization through inter-tenant collaboration solutions, such as
 shared channels in Microsoft Teams
 .
-When you enter prompts using Microsoft 365 Copilot, the information contained within your prompts, the data they retrieve, and the generated responses remain within the Microsoft 365 service boundary, in keeping with our current privacy, security, and compliance commitments. Microsoft 365 Copilot uses Azure OpenAI services for processing, not OpenAI's publicly available services. Azure OpenAI doesn't cache customer content and Copilot modified prompts for Microsoft 365 Copilot. For more information, se
```

---

### 3. Data Access Governance Reports

**URL:** https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports
**Section:** SharePoint Administration
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:43e8be52c313c2114bd6b083467d415dddebbf119e50ade29cc4249b513ebfe7

**Affected Controls:**
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.4: Control 4.4: Guest and External User Access Controls
  - File: `controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/4.2/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.4/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/sharepoint-copilot-preflight/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -27,7 +27,7 @@ See
 Prerequisites for SharePoint Advanced Management
 .
-The reports are currently unavailable for Gallatin, even if you have the required licenses.
+The reports are currently unavailable for Microsoft 365 operated by 21Vianet, even if you have the required licenses.
 How to access the Data access governance reports in the SharePoint admin center
 Sign in to the
 SharePoint admin center

```

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:ea2991c7d27b7add041f4ae896c3361892009f6814198916309b31f627953aa0

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -108,8 +108,6 @@ By: Adobe
 Adobe PDF Services
 By: Adobe Acrobat Services
-ADP Employee Self-Service
-By: ADP, Inc.
 Advanced Data Operations
 By: State Solutions
 Advanced Scraper (Independent Publisher)
@@ -126,6 +124,8 @@ By: Africa's Talking
 AfterShip (Independent Publisher)
 By: Taiki Yoshida
+Agent SDK
+By: Microsoft
 AgilePoint NX
 By: AgilePoint Inc
 Agilite
@@ -177,11 +177,11 @@ Amazon Redshift [DEPRECATED]
 By: Microsoft
 Amazon S3
-By: Microsoft
+By:
 Amazon S3 Bucket (Independent Publisher)
 By: Michael Megel
 Amazon SQS
-By: Microsoft
+By:
 Ambee (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 AMEE Open Business (Independent Publisher)
@@ -270,8 +270,6 @@ By: Microsoft
 Azure - Foundry IQ
 By: Microsoft
-Azure AD Identity and Access
-By: Microsoft, Daniel Laskewitz
 Azure AI Content Understanding
 By: Microsoft
 Azure AI Document Intelligence (form recognizer)
@@ -283,7 +281,7 @@ Azure AI Search
 By: Microsoft
 Azure App Service
-By: Microsoft
+By:
 Azure Application Insights [DEPRECATED]
 By: Microsoft
 Azure Automation
@@ -340,6 +338,8 @@ By: Microsoft
 Azure Log Analytics Data Collector
 By: Microsoft
+Azure Maps
+By: Microsoft
 Azure Monitor Logs
 By: Microsoft
 Azure OpenAI
@@ -357,7 +357,7 @@ Azure Text to speech
 By: Microsoft
 Azure VM
-By: Microsoft
+By:
 Badgr (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 Basecamp 2
@@ -548,6 +548,8 @@ By: Cireson
 Cisco Webex Meetings
 By: Cisco
+Cisco Workspaces
+By: Cisco Systems.
 Citymapper (Independent Publisher)
 By: Troy Taylor
 CivicPlus Transform
@@ -626,6 +628,8 @@ By: Roy Paar
 Commercient
 By: Commercient LLC
+CommunitycliQ Agent
+By: Mentorcliq, Inc.
 Companies House (Independent Publisher)
 By: Matt Collins
 Company Connect
@@ -665,7 +669,7 @@ ConvertKit (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 Copilot for Finance
-By: Microsoft
+By:
 Copilot for Sales
 By: Microsoft Corporation
 Copilot for Service extension (preview)
@@ -684,6 +688,8
```

---

### 2. Cross-Tenant Restrictions

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/cross-tenant-restrictions
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:2fcfd22221d118491aef503762b6e563d115f12e18bb057017831a3168b07f9e

**Affected Controls:**
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)

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

```

---

### 3. Power Platform Inventory

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:94ac275aece7f332b5a3c67226f788c6d7189f50e8f5e64e06d5e89284837cbe

**Affected Controls:**
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`

**What Changed:**
```diff
--- +++ @@ -39,7 +39,7 @@ needle in a haystack
 resource referenced in a support ticket to dramatically improve response times.
 Supported resource types
-The Power Platform inventory includes:
+The Power Platform inventory includes the following resource types:
 Agents:
 All agents created in Copilot Studio, and all agents created in Microsoft 365 Copilot Agent Builder.
 Apps:
@@ -51,6 +51,7 @@ Environment groups:
 All environment groups in your tenant.
 Key features
+The Power Platform inventory includes the following key features:
 Unified inventory
 : Centralized view of all resources.
 Fast updates
@@ -66,11 +67,36 @@ Connector visibility (preview)
 : See which connectors and operations each resource uses, directly in the inventory grid.
 Access requirements
-To view the Power Platform inventory, you must have one of the following tenant-wide administrative roles:
+To view the Power Platform inventory, you must hold one of the supported Microsoft Entra roles. What you can see in the Power Platform admin center depends on your role: most roles have full visibility into all resources, while the AI roles are scoped to AI-related resources only.
+Role
+What they can see
+Global administrator
+All inventory resources
 Power Platform administrator
-or
+All inventory resources
 Dynamics 365 administrator
-. If you don't have one of these roles, you can't access the inventory.
+All inventory resources
+Global reader
+All inventory resources
+AI administrator
+Agents, agentic apps, agent flows, environments, and environment groups only
+AI reader
+Agents, agentic apps, agent flows, environments, and environment groups only
+The AI administrator and AI reader roles are scoped to AI-related resources only. They can see:
+Agents
+from Microsoft 365 Copilot and Copilot Studio
+Agentic apps
+, including vibe apps, code apps, and App Builder apps
+Agent flows
+from Copilot Studio and workflow agent flows from Microsoft 365 Copilot
+Environments
+and
+environment groups
+Canva
```

---

### 4. Human-in-the-Loop Workflows

**URL:** https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:764e860ebc80cb5e20f4c3c1ede0defa35648d9a675c891ca15470072833fa21

**Affected Controls:**
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`

**What Changed:**
```diff
--- +++ @@ -144,6 +144,30 @@ and
 response
 parameters.
+Workflows support human-in-the-loop patterns through
+RequestPort
+, which pauses execution and waits for external input.
+approvalPort := workflow.RequestPort{
+ ID: "ApprovalPort",
+ Request: reflect.TypeFor[string](),
+ Response: reflect.TypeFor[bool](),
+}
+
+approval := approvalPort.Bind()
+finalize := workflow.NewExecutor("FinalizeExecutor", func(approved bool) string {
+ if approved {
+ return "Request approved by the human reviewer"
+ }
+ return "Request rejected by the human reviewer"
+}).Bind()
+
+wf, err := workflow.NewBuilder(approval).
+ AddEdge(approval, finalize).
+ WithOutputFrom(finalize).
+ Build()
+A
+RequestPort
+defines a typed request/response channel between the workflow and the outside world. When an executor reaches a request port, the workflow pauses and emits an external request event. The workflow resumes when an external response is provided.
 Handling Requests and Responses
 An
 RequestPort
@@ -215,6 +239,40 @@ See this
 full sample
 for a complete runnable file.
+Listen for
+workflow.RequestInfoEvent
+, create a response from the request, and resume the run with that response:
+run, err := inproc.Default.Run(ctx, wf, "Approve deployment to production?")
+if err != nil {
+ return err
+}
+
+var request *workflow.ExternalRequest
+for evt := range run.NewEvents() {
+ if requestEvent, ok := evt.(workflow.RequestInfoEvent); ok {
+ request = requestEvent.Request
+ break
+ }
+}
+
+response, err := request.CreateResponse(true)
+if err != nil {
+ return err
+}
+
+if _, err := run.Resume(ctx, response); err != nil {
+ return err
+}
+
+for evt := range run.NewEvents() {
+ if output, ok := evt.(workflow.OutputEvent); ok {
+ fmt.Println(output.Output)
+ }
+}
+Tip
+See the
+human-in-the-loop sample
+for a complete runnable file.
 Human-in-the-Loop with Agent Orchestrations
 The
 RequestPort
@@ -231,7 +289,7 @@ RequestPort
 pattern, but the event payload contains a
 ToolApprovalRequestContent
-(
```

---

### 5. Restricted Access Control

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-access-control
**Section:** SharePoint Administration
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:a7702b4671c88258ff57559f88d21d5571643d89a5b29604c98c595d33e1ddc9

**Affected Controls:**
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**What Changed:**
```diff
--- +++ @@ -86,15 +86,15 @@ Add or remove your security groups or Microsoft 365 groups and select
 Save
 .
+Apply site access restriction to a site
 To apply site access restriction to the site, you must add at least one group to the site access restriction policy.
 For a group connected site, the Microsoft 365 group connected to the site is the default Restricted Access Control group. You can choose to keep this group and add more Microsoft 365 or Microsoft Entra Security groups as Restricted Access Control group.
 Note
 There's a tag labeled as
 Default group
 marked against the Microsoft 365 group connected to the site as shown in the previous image.
-To manage site access restriction for a SharePoint site by using PowerShell, use the following commands:
-Action
-PowerShell command
+Manage site access restriction by using PowerShell
+To manage site access restriction for a SharePoint site by using PowerShell, use the PowerShell commands described in this section.
 Enable site access restriction
 Set-SPOSite -Identity <siteurl> -RestrictedAccessControl $true
 Add group
@@ -111,7 +111,7 @@ After you delegate the site access restriction control to site admins, they can configure the site access restriction setting at the
 Site Information
 panel.
-To restrict access to a SharePoint site:
+Restrict access to a SharePoint site
 Limit who can access a site by using Microsoft Entra security groups or Microsoft 365 groups.
 Add the groups that contain the users who should have access.
 Add up to 10 groups for each site.
@@ -141,17 +141,14 @@ As an IT administrator, you can view the following reports to gain more insight about SharePoint sites protected with restricted site access policy:
 Sites protected by restricted site access policy (RACProtectedSites)
 Details of access denials due to restricted site access policy (ActionsBlockedByPolicy)
-Reports are currently unavailable for Gallatin, even if you have the required licenses.
+Reports are currently unavailable for M
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Cross-Tenant Restrictions
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/cross-tenant-restrictions
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:2fcfd22221d118491aef503762b6e563d115f12e18bb057017831a3168b07f9e

---

### 2. Maker Onboarding (Welcome Content)
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/welcome-content
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:2808310cb91c3da3f308533f7a8d4a0c951f75c6176729bcb4a292a58fd8fdf3

---

### 3. Regions Overview
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/regions-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:332e7fc1117c1dc36eb3d0620061228c78bdd0a81821f75d667b56182560ea68

---

### 4. M365 Copilot Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:1846e1ff2b2542244827e02132f3f4ad19153be6c0ecea249d1d3166fc4f8975

---

### 5. Deployment Blueprint
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-blueprint
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:0e6c78ee99ba5f978813ddde987110e3862b22b870f380f3b5f4a4adb9c93699

---

### 6. Admin Roles
**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:ed5f09065720713a04db92d666643843a09f98efa9fa0e09be2904bb2b92eb1e

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-inventory | https://learn.microsoft.com/en-us/defender-xdr/security-for-ai/ai-agent-inventory |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*