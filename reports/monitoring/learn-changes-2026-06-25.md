# Microsoft Learn Documentation Changes

**Run Date:** 2026-06-25
**Run Time:** 2026-06-25T09:24:49.473164+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 5 |
| HIGH Changes | 5 |
| MEDIUM Changes | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | managed-environment-enable | HIGH | 2.1, 1.4 | Review and update |
| 2 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Review and update |
| 3 | backup-restore-environments | CRITICAL | 2.4 | Update portal-walkthrough |
| 4 | knowledge-copilot-studio | MEDIUM | 2.16, 4.8, 1.14 | Update portal-walkthrough |
| 5 | audit-log-retention-policies | HIGH | 3.14, 4.5, 1.7 | Update portal-walkthrough |
| 6 | audit-search | HIGH | 3.2, 3.12, 1.7 | Update portal-walkthrough |
| 7 | restricted-content-discovery | HIGH | 4.7, 4.1, 4.6, 1.3, 1.14 | Review and update |
| 8 | monitor-your-data | HIGH | 3.9 | Review and update |
| 9 | investigate-cases | HIGH | None | Review and update |
| 10 | ai-agent-inventory | HIGH | 3.7, 1.8 | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Backup and Restore

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/backup-restore-environments
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:e427b05d2b276ebaa57ef34a7ae848415f76148d14eff5db93eaacb9e21a205b

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -22,11 +22,11 @@ Back up and restore environments
 Feedback
 Summarize this article for me
-It's important to protect your data on Microsoft Power Platform and in Dataverse and to provide continuous availability of service through system or manual backups.
-System backups are automatically created for environments that have a database. By default, backups of all production and nonproduction environments are retained for seven days. However, for production
-Managed Environments
-, the retention period can be extended up to 28 days through the Power Platform admin center or PowerShell.
-Manual backups are backups that the user initiates. It's recommended that you create manual backups before performing major customizations, applying a version update, or making significant changes to the environment. You can create these backups for production and sandbox environments, but not for the default environment. By default, manual backups are kept for seven days. For production Managed Environments, the retention period can be extended up to 28 days.
+Protect your data on Microsoft Power Platform and in Dataverse by providing continuous availability of service through system or manual backups.
+The system automatically creates backups for environments that have a database. By default, the system retains backups of all production and nonproduction environments for seven days. However, for production
+managed environments
+, you can extend the retention period up to 28 days through the Power Platform admin center or PowerShell.
+Manual backups are backups that you initiate. Create manual backups before major customizations, applying a version update, or making significant changes to the environment. You can create these backups for production and sandbox environments, but not for the default environment. By default, manual backups are kept for seven days. For production managed environments, you can extend the retention period up to 28 days.
 Supported retention peri
```

---

### 2. Knowledge Sources

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:915ae281137faeb62c732488c82ca9965c766d4b7ebb9402a5e72772abf06e64

**Affected Controls:**
- Control 2.16: Control 2.16: RAG Source Integrity Validation
  - File: `controls/pillar-2-management/2.16-rag-source-integrity-validation.md`
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.8/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -29,23 +29,6 @@ generative answers node
 in an agent topic.
 You can incorporate knowledge sources into agents during their initial creation, add them after the agent is created, or add them to a generative answers topic node.
-Add and manage knowledge for generative answers
-Generative answers allow your agent to find and present information from multiple sources, internal or external, without having to create specific topics. Use generative answers as primary information sources or as a fallback source when authored topics can't answer a user's query. As a result, you can quickly create and deploy a functional agent. Makers don't need to manually author multiple topics, which might not address all customer questions.
-By default, when you create an agent, Copilot Studio automatically creates the
-Conversational boosting
-system topic. This topic contains a generative answers node, which you can use to begin utilizing knowledge sources immediately. All knowledge sources that you add at the agent level are added to generative answers node in the
-Conversational boosting
-system topic.
-For prerequisites and information on limitations, see
-Generative answers
-.
-For information on analytic metrics on a per knowledge source basis, see:
-Generated answer rate and quality
-for conversational agents.
-Knowledge source use
-for autonomous agents.
-Drill down on a theme
-for knowledge source metrics in the context of themes.
 Supported knowledge sources
 Name
 Source
@@ -101,6 +84,15 @@ Limits and limitations
 .
 Currently, citations returned from a knowledge source can't be used as inputs to other tools or actions.
+Source authentication
+If you're using SharePoint, Dataverse, or enterprise data with Microsoft Copilot connectors, you need to incorporate authentication. For more information, see
+Configure user authentication in Copilot Studio
+. For individual generative answers nodes, see
+Authentication
+.
+In addition, you might need to account for
+URL con
```

---

### 3. Audit Log Retention

**URL:** https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:01a1cd275fb1be44b7e25873137809997d888a5e1643888853cdc686f120dff6

**Affected Controls:**
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/advanced-implementations/microsoft-audit-reporting-tools.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -52,7 +52,7 @@ Your organization can have up to 50 audit log retention policies.
 To retain an audit log for longer than 180 days (and up to 1 year), the user who generates the audit log (by performing an audited activity) must have an Office 365 E5 or Microsoft 365 E5 license or a Microsoft Purview Suite (formerly known as Microsoft 365 E5 Compliance) or E5 eDiscovery and Audit add-on license. To retain audit logs for 10 years, the user who generates the audit log must also have a 10-year audit log retention add-on license in addition to an E5 license.
 Note
-If the user generating the audit log doesn't meet these licensing requirements, data is retained according to the highest priority retention policy. This retention might be either the default retention policy for the user's license or the highest priority policy that matches the user and its record type.
+If the user generating the audit log doesn't have the licenses required for the selected retention duration, data is retained according to the highest priority retention policy. This retention might be either the default retention policy for the user's license or the highest priority policy that matches the user and its record type.
 All custom audit log retention policies (created by your organization) take priority over the default retention policy. For example, if you create an audit log retention policy for Exchange mailbox activity that has a retention period that's shorter than one year, audit records for Exchange mailbox activities are retained for the shorter duration specified by the custom policy.
 The audit item lifetime for data is determined when you add it to the auditing pipeline and is based on the licensing defaults or applicable retention policies. Any changes to licensing or applicable retention policies change the expiration time of the audit data after updating. These changes don't update any previously committed items.
 Create an audit log retention policy
@@ -142,7 +142,7 @@ 
```

---

### 4. Search the Audit Log

**URL:** https://learn.microsoft.com/en-us/purview/audit-search
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:3ffe948aef4e525e4013444c1b73cbd802c9d3dbc67162d3014f6a916cd69de5

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.12: Control 3.12: Agent Governance Exception and Override Management
  - File: `controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.23/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/microsoft-audit-reporting-tools.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-0-governance-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -28,7 +28,7 @@ Each admin Audit account user can have up to 10 search jobs running at the same time, with a limit of one unfiltered search job.
 Before you search the audit log
 Review the following items before you start searching the audit log.
-Audit log search is turned on by default for Microsoft 365 and Office 365 enterprise organizations. To verify that audit log search is turned on, run the following command in
+Audit log search is turned on by default for Microsoft 365 and Office 365 enterprise organizations. Verify the current unified audit log ingestion setting for your organization by running the following command in
 Exchange Online PowerShell
 :
 Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled
@@ -79,9 +79,9 @@ Even when mailbox auditing on by default is turned on, you might notice that mailbox audit events for some users aren't found in audit log searches in the Microsoft Purview portal or via the Office 365 Management Activity API. For more information, see
 Mailbox audit logging
 .
-To turn off audit log search for your organization, run the following command in Exchange Online PowerShell:
+To turn off audit log search for your organization, use the following command to disable unified audit log ingestion in Exchange Online PowerShell:
 Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $false
-To turn on audit search again, run the following command in Exchange Online PowerShell:
+To turn unified audit log ingestion back on for your organization, run the following command in Exchange Online PowerShell:
 Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true
 For more information, see
 Turn off audit log search
@@ -95,8 +95,8 @@ .
 For information about exporting the search results returned by the
 Search-UnifiedAuditLog
-cmdlet to a CSV file, see the "Tips for exporting and viewing the audit log" section in
-Export, configure, and view audit log records
+cmdlet to a CSV file, see
+Tips for exporting an
```

---

### 5. Defender for Cloud Apps - AI Inventory

**URL:** https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-inventory
**Section:** Microsoft Defender
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:3f1de85f1a5ec4a06979b0b52263b37bedf164b2e4b5695db84acc2ae55ee8b4

**Affected Controls:**
- Control 3.7: Control 3.7: PPAC Security Posture Assessment
  - File: `controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/3.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/3.7/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -33,9 +33,9 @@ Opt in to the
 Microsoft Defender for Cloud apps and Defender XDR preview features
 Enable discovery of Copilot Studio AI agents
-After you enable Security for AI, Microsoft Defender automatically discovers all Copilot Studio custom AI agents in your tenant. After discovery, you can view your agents in the
+After you turn on the Security for AI setting in the Microsoft Defender portal, Microsoft Defender automatically discovers all Copilot Studio custom AI agents in your tenant. You can then view your agents in the
 AI agent inventory
-and use
+. Use
 advanced hunting
 to investigate potential threats and misconfigurations.
 Note
@@ -66,7 +66,7 @@ .
 When Copilot Studio AI Agents are connected, a green indicator appears in the
 AI Agents Inventory
-section in the Microsoft Defender system settings. It can take up to 30 minutes for the initial connection status to update. Depending on the size and complexity of your environment, it might take longer to see the full deployment of the AI agent inventory.
+section in the Microsoft Defender system settings. The initial connection status can take up to 30 minutes to update. Depending on the size and complexity of your environment, it might take longer to see the full deployment of the AI agent inventory.
 Related articles
 Protect your Copilot Studio custom AI Agents (Preview)
 Enable real-time protection for Microsoft Copilot Studio Agents

```

---

## HIGH: Control Review Recommended

### 1. Enable Managed Environments

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-enable
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:a8817f7f35d206dd80f2cc89a9a837b8b1acc440cd117f923781b3d7cc1265c3

**Affected Controls:**
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.8/verification-testing.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-0-governance-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -19,20 +19,20 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Enable Managed Environments
+Enable managed environments
 Feedback
 Summarize this article for me
-Admins enable, disable, and edit Managed Environments in the Power Platform admin center. Admins can also use PowerShell to disable Managed Environments. This article explains the permissions you need to manage environments and the steps to get started in the Microsoft Power Platform admin center or with PowerShell.
+Admins enable, disable, and edit managed environments in the Power Platform admin center. Admins can also use PowerShell to disable managed environments. This article explains the permissions you need to manage environments and the steps to get started in the Microsoft Power Platform admin center or with PowerShell.
 Permissions
-To enable or edit Managed Environments, you need the Power Platform Administrator or Dynamics 365 Administrator role in Microsoft Entra ID. You can learn more about these roles in
+To enable or edit managed environments, you need the Power Platform Administrator or Dynamics 365 Administrator role in Microsoft Entra ID. You can learn more about these roles in
 Use service admin roles to manage your tenant
 .
-Any user with permission to view environment details can see the Managed Environments property for an environment.
-Users with the Delegated Admin role or the Environment Admin security role can't change the Managed Environments property in an environment.
+Any user with permission to view environment details can see the managed environments property for an environment.
+Users with the Delegated Admin role or the Environment Admin security role can't change the managed environments property in an environment.
 Important
-The Managed Environments property must be the same in the source and destination before you can start to copy and restore environment lifecycle operations.
-Dataverse is required to use Managed Environ
```

---

### 2. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:504c3465c1ae2979570b52b34fc4f7cc04b066a59294b1d3f269d52e81a4af67

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -340,6 +340,8 @@ By: Microsoft
 Azure Log Analytics Data Collector
 By: Microsoft
+Azure Maps
+By: Microsoft
 Azure Monitor Logs
 By: Microsoft
 Azure OpenAI
@@ -716,8 +718,6 @@ By: Agendium Ltd
 CyberProof
 By: CyberProof Inc.
-D&B Optimizer [DEPRECATED]
-By: Dun & Bradstreet
 d.velop
 By: d.velop AG
 D365 Contact Center Admin MCP
@@ -886,6 +886,8 @@ By: Draup
 Dropbox
 By: Microsoft
+Dun and Bradstreet MCP Server
+By: Dun & Bradstreet, Inc.
 Duration Calculator (Independent Publisher)
 By: Troy Taylor
 DVLA Vehicle Enquiry Service (Independent Publisher)
@@ -1012,6 +1014,8 @@ By: Encodian
 Encodian - Word
 By: Encodian
+Encodian [DEPRECATED]
+By: Encodian
 Engagement Cloud
 By: dotdigital
 Enlyft Insights
@@ -1156,6 +1160,8 @@ By: Formstack LLC
 Formstack Forms
 By: Formstack LLC
+Foxit eSign
+By: Foxit Software Inc.
 FraudLabs Pro (Independent Publisher)
 By: Troy Taylor
 FreeAgent (Independent Publisher)
@@ -1412,8 +1418,6 @@ By: iLovePDF
 iLoveSign
 By: iLoveSign
-iLoveSign [DEPRECATED]
-By: i Love PDF
 iManage AI
 By: iManage Power Platform Connector
 iManage Data Marts
@@ -1512,6 +1516,8 @@ By: ITautomate LTD
 ITGlue (Independent Publisher)
 By: Nirmal Kumar
+Jamie AI
+By: Jamie AI
 Jasper (Independent Publisher)
 By: Troy Taylor
 JBHunt
@@ -2138,6 +2144,8 @@ By: Peakboard GmbH
 Peltarion AI
 By: Peltarion
+Penneo Sign Sandbox
+By: Penneo Integration
 Perfect Wiki
 By: OOO RD17
 Perplexity AI (Independent Publisher)
@@ -2536,6 +2544,8 @@ By: Showcase Software Ltd
 Showpad eOS
 By: Showpad
+Showpad MCP
+By: Showpad
 SHRTCODE (Independent Publisher)
 By: Chandra Sekhar Malla
 Sigma Conso CR
@@ -2590,6 +2600,8 @@ By: Tensis Group
 Smartsheet
 By: Microsoft
+Smartsheet EU
+By: Smartsheet Inc
 Smartsheet US
 By: Smartsheet Inc
 SmileBack
@@ -2740,6 +2752,8 @@ By: TeleSign Corporation
 Templafy
 By: Templafy
+TemplioniX
+By: TemplioniX
 Tendocs Documents
 By: Deepdale BV

```

---

### 3. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:c8e40dad1636a127c048358b08c1b00089e429b3d80b9c4c5174fa109466bab1

**Affected Controls:**
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -22,108 +22,162 @@ Restrict discovery of SharePoint sites and content
 Feedback
 Summarize this article for me
-For organizations onboarding to Microsoft 365 Copilot, maintaining strong data governance controls for SharePoint content is critical to deploying Copilot in a safe manner. Sites identified with the highest risk of oversharing can use Restricted Content Discovery to protect content while taking time to ensure that permissions are accurate and well-managed.
-With Restricted Content Discovery, organizations can limit the ability of end users to search for files from specific SharePoint sites. Enabling Restricted Content Discovery for each site prevents the sites from surfacing in organization-wide search and Microsoft 365 Copilot Business Chat, unless a user had a recent interaction.
-Restricted Content Discovery is a site-level setting that needs to be propagated to the search index, a large number of transactions could lead to a long queue in the ingestion pipeline and higher update latency times.
-While child content is hidden by default, users in your organization can still discover files they own or recently interacted with. End users can still find relevant content they need for their day-to-day tasks, even if Restricted Content Discovery is applied to the parent site.
-Restricted Content Discovery doesn't affect searches originating from a site context or other intelligent features such as Microsoft 365 Feed and Recommendations.
+Organizations preparing for Microsoft 365 Copilot often need time to review SharePoint sites, validate permissions, and implement governance controls before making content broadly discoverable. Restricted Content Discovery (RCD) helps you limit discovery of content from specific SharePoint sites while those reviews are taking place.
+When you enable Restricted Content Discovery for a site, content from that site doesn't appear in organization-wide search and Microsoft 365 Copilot experiences unless a user recently 
```

---

### 4. Workbooks

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/monitor-your-data
**Section:** Azure Services
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:4b799834f827576d6d5a8d1bd80fa9f8c1fed3684764717f980ed03923f23663

**Affected Controls:**
- Control 3.9: Control 3.9: Microsoft Sentinel Integration
  - File: `controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md`

**What Changed:**
```diff
--- +++ @@ -36,6 +36,7 @@ unified security operations experience offered by Microsoft Defender
 .
 Prerequisites
+Before you create or use workbooks, make sure you meet the following prerequisites:
 You must have at least
 Workbook reader
 or
@@ -98,7 +99,7 @@ For more information, see:
 Create interactive reports with Azure Monitor Workbooks
 Tutorial: Visual data in Log Analytics
-Create new workbook
+Create a new workbook
 Create a workbook from scratch in Microsoft Sentinel.
 In Microsoft Sentinel, select
 Threat management > Workbooks
@@ -168,13 +169,15 @@ You can delete both saved templates and customized workbooks from the
 My workbooks
 tab. Templates themselves can't be deleted.
+Warning
+Deleting a workbook permanently removes the workbook resource and any customizations you made to the template. This action can't be undone. The original template remains available.
 To delete a workbook, select the workbook in the
 My workbooks
 tab, and then select
 Delete
-. This action removes the workbook resource and any changes you made to the template. The original template remains available.
+.
 Workbook recommendations
-This section reviews basic recommendations we have for using workbooks with Microsoft Sentinel.
+The following recommendations help you use Microsoft Sentinel workbooks effectively.
 Add Microsoft Entra ID workbooks
 If you use Microsoft Entra ID with Microsoft Sentinel, we recommend that you install the Microsoft Entra solution for Microsoft Sentinel and use the following workbooks:
 Microsoft Entra sign-ins
@@ -198,13 +201,15 @@ or
 CommonSecurityLog
 table, on any other firewall.
+The query compares daily security event counts between the current week and the previous week, so you can quickly spot unusual changes in event volume.
 // week over week query
 SecurityEvent
 | where TimeGenerated > ago(14d)
 | summarize count() by bin(TimeGenerated, 1d)
 | extend Week = iff(TimeGenerated>ago(7d), "This Week", "Last Week"), TimeGenerated = iff(TimeGen
```

---

### 5. Investigate Incidents

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/investigate-cases
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:bb34f56cedceaac70d7a05780245085bd2f62129ed06e2044078131f96739029

**What Changed:**
```diff
--- +++ @@ -22,9 +22,9 @@ Investigate incidents with Microsoft Sentinel (legacy)
 Feedback
 Summarize this article for me
-This article helps you use Microsoft Sentinel's legacy incident investigation experience. If you're using the newer version of the interface, use the newer set of instructions to match. For more information, see
+This article helps you use Microsoft Sentinel's legacy incident investigation experience. If you're using the newer version of the interface, see
 Navigate and investigate incidents in Microsoft Sentinel
-.
+for instructions that match that experience.
 After connecting your data sources to Microsoft Sentinel, you want to be notified when something suspicious happens. To enable you to do this, Microsoft Sentinel lets you create advanced analytics rules that generate incidents that you can assign and investigate.
 An incident can include multiple alerts. It's an aggregation of all the relevant evidence for a specific investigation. An incident is created based on analytics rules that you created in the
 Analytics
@@ -34,11 +34,13 @@ Azure Preview Supplemental Terms
 include additional legal terms that apply to Azure features that are in beta, preview, or otherwise not yet released into general availability.
 Prerequisites
+Before you investigate or assign incidents, make sure the following prerequisites are met:
 You'll only be able to investigate the incident if you used the entity mapping fields when you set up your analytics rule. The investigation graph requires that your original incident includes entities.
 If you have a guest user that needs to assign incidents, the user must be assigned the
 Directory Reader
 role in your Microsoft Entra tenant. Regular (nonguest) users have this role assigned by default.
 How to investigate incidents
+Perform the following steps to review and investigate incidents:
 Select
 Incidents
 . The
@@ -59,8 +61,8 @@ tab, review the timeline of alerts and bookmarks in the incident, which can help you rec
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Knowledge Sources
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:915ae281137faeb62c732488c82ca9965c766d4b7ebb9402a5e72772abf06e64

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*