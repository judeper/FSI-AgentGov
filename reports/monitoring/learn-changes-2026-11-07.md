# Microsoft Learn Documentation Changes

**Run Date:** 2026-11-07
**Run Time:** 2026-11-07T12:36:41.989927+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 6 |
| HIGH Changes | 3 |
| MEDIUM Changes | 7 |
| Redirects | 16 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | power-platform-inventory | HIGH | 3.11 | Review and update |
| 2 | alerts | HIGH | None | Review and update |
| 3 | ...ower-platform/release-plan/2025wave2/ | MEDIUM | 1.27 | Review and update |
| 4 | ...ower-platform/release-plan/2026wave1/ | MEDIUM | 2.10, 2.3, 2.8, 1.18, 3.8 | Review optional |
| 5 | ...ilot-security-enhanced-admin-controls | MEDIUM | 2.3, 2.8, 1.18 | Review optional |
| 6 | admin-deployment-hub | CRITICAL | 2.3, 2.1 | Update portal-walkthrough |
| 7 | ...-governance-agentic-center-enablement | MEDIUM | None | Review optional |
| 8 | whats-new | MEDIUM | None | Review optional |
| 9 | plan-agent-model-lifecycle | MEDIUM | 2.6 | Update portal-walkthrough |
| 10 | ...rosoft.com/en-us/microsoft-agent-365/ | HIGH | 2.12, 2.5, 2.6, 2.25, 1.11, 1.7, 1.2, 3.8, 3.6, 3.2, 3.14, 3.13, 3.1 | Update portal-walkthrough |
| 11 | agent-id-governance-overview | HIGH | 2.26, 1.11, 3.6 | Update portal-walkthrough |
| 12 | overview | MEDIUM | 1.27, 1.8 | Update portal-walkthrough |
| 13 | microsoft-purview-service-description | HIGH | None | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Admin Deployment Hub

**URL:** https://learn.microsoft.com/en-us/power-platform/alm/admin-deployment-hub
**Section:** Power Platform ALM
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:74a8e4548a693e09653d3569dda5b234cde9d97c2128e2ba42a8577747ebdd4c

**Affected Controls:**
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.3/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -76,32 +76,6 @@ is the name of the artifact and the
 Version
 deployed to the target environment.
-Important
-All target environments used in a pipeline must be enabled as
-managed environments
-.
-Tenant admins can enable automatic conversion of pipelines environments to
-managed environments
-.
-Manage deployment settings
-Admins can manage these
-Settings
-within the selected pipelines host (settings are managed separately for each host):
-Enable automatic conversion of pipelines environments to
-managed environments
-. This ensures pipelines environments meet Microsoft compliance standards automatically. When makers deploy to this environment, it gets automatically converted to a managed environment.
-Solution deployments across regions
-: Admins can opt in to allow deployments between environments in different geographic locations. For example, when the host and production environments are in North America but the development environment is in India.
-Important
-This setting enables data to be shared across geographical regions within your tenant.
-Allow makers to import shared solution deployments
-: Deployed solution backups are stored in the pipelines host. This setting allows nonadmins to import solutions that were shared with them, in addition to the ability to import solutions that they deployed.
-Use a custom pipelines host
-: Allows you to set one default host for the entire tenant. This replaces
-personal pipelines
-- meaning admins control who can access pipelines and makers can no longer create personal pipelines in the platform host. It's also useful when a central team manages deployments for the entire tenant. This setting is only visible when the
-Platform host
-is selected in the host picker.
 Review and approve deployment requests
 On the deployment page, admins approve or reject deployment requests assigned to them. Youâll first need to
 setup delegated deployments
@@ -117,32 +91,122 @@ in the details panel if the operation was
 D
```

---

### 2. Manage the AI model lifecycle for Copilot Studio agents

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/plan-agent-model-lifecycle
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:fad4e5077cca33f3deb1f4b77e70649a9193430013561c86786dbd44c47eb91c

**Affected Controls:**
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.6/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.6/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -57,7 +57,7 @@ Copilot Studio identifies models by release and availability classifications. These classifications help determine how to govern a model and where to use it. Model names, release stages, regional availability, and retirement status change over time. Always check
 model availability by region
 for current information instead of relying on a static model list.
-An agent that uses the default model moves to a new model whenever the default is upgraded, whether or not you planned for it. For high-risk and high-volume agents, select a specific model rather than tracking the default, so that every model change goes through your migration process.
+An agent that uses the default model moves to a new model whenever the default is upgraded, whether or not you planned for it. For high-risk and high-volume agents, select a specific model rather than tracking the default. Selecting a specific model reduces, but doesn't eliminate, the risk of behavior changes. Named models can still receive updates that affect tool calling or orchestration. Continue to monitor production results and run regression tests for agents that use a specific model.
 Warning
 Experimental and preview models can have limited availability, variable response quality, different latency or message consumption, timeouts, and regional data-processing considerations. Copilot Studio doesn't recommend them for production agents. If you publish an agent that uses a preview or experimental model and users interact with it, that use is still billed at the established rates.
 Match the model use category to the agent's purpose

```

---

### 3. Agent 365 Documentation Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:dab6ea8a8cc16a101b23cfd4e4cd7bfd482d512c3cd0c4e97e174204bde522fd

**Affected Controls:**
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 1.2: Control 1.2: Agent Registry and Integrated Apps Management
  - File: `controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.2/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.25/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.25/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/index.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/opentelemetry-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -1,28 +1,51 @@ Microsoft Agent 365 documentation
-Agent 365 is the control plane for IT and security leaders to observe, secure, and govern agents across the organization.
-Why does an enterprise need Agent 365?
+Microsoft Agent 365 is the observability platform for AI. Manage every agent from one place, wherever it was built. Give each agent a clear owner and the right permissions, understand AI risk and keep agents protected, and turn your AI investment into business value.
 Explore Microsoft Agent 365
-Microsoft Agent 365 allows you to manage all your organizationâs agents at scale, regardless of where they originate.
-Meet Microsoft Agent 365
-Transform fragmented, high-risk experimentation into trusted, enterprise-wide AI operations with a unified control plane that makes agents visible, governed, and secure.
-Learn more
-Govern without slowing innovation
-Establish lightweight guardrails for observability and acccountability to gain control and trust while still allowing teams to move quickly.
-Learn more
-How can I extend my agent to be Microsoft Agent 365 compatible?
-Use Microsoft Agent 365 SDK to extend agents built using any agent SDK or platform, with enterpriseâgrade identity, observability, notifications, security, and governed access to Microsoft 365 data.
-Learn more
-Get started with Microsoft Agent 365
-Observe, secure, and govern every agent across your organization with Microsoft Agent 365.
-Observe
-Gain visibility into agents in your environment, understand how theyâre used, and act quickly on performance, behavior, and risk signals before they impact the business.
-Learn more
-Govern
-Establish guardrails for agents and people, onboard agents with IT oversight, and govern agent access to resources and data. Be audit ready with built-in compliance and data retention.
-Learn more
-Secure
-Secure agent identities, control access to resources, prevent data oversharing and leaks, and defend against threats and vulnerabilities with 
```

---

### 4. Governing Agent Identities

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:33849e214b5d04792649550f717643485cdf963c6be2be57963c860fceacd51a

**Affected Controls:**
- Control 2.26: Control 2.26: Entra Agent ID — Identity Governance for Agents
  - File: `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.26/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -44,7 +44,7 @@ Microsoft Entra Agent ID
 introduces support for identities for the agents themselves, with four new types of object: agent identity blueprint, agent identity blueprint principal, agent identity, and agent user. Through the
 agent identity blueprint
-, the agent can create one or more agent identities, and optionally an agent user for each agent identity. Each agent identity and agent user can have distinct access rights.
+, the agent can create one or more agent identities, and optionally an agent user for each agent identity, which it can use for authentication to Microsoft, third party and line of business applications. Each agent identity and agent user can have distinct access rights.
 For a multitenant-capable agent, an agent identity blueprint principal can be brought into the tenant with resources so it can create agent identities in that tenant, similar to how a multitenant application can have a service principal in each tenant.
 The agent identity and the agent user allow AI agents to take on digital identities within Microsoft Entra. Once agent identities are created, these agent identities are able to be governed using lifecycle and access features. Sponsors can be assigned to agent identities after creation. Sponsors of agent identities are human users accountable for making decisions about its lifecycle and access. For more information about the role of a sponsor of agent identities, see:
 Administrative relationships for agent IDs
@@ -63,6 +63,8 @@ Microsoft Copilot Studio
 can be configured to automatically be assigned to an agent identity. When an agent identity is first created in a Power Platform environment after enabling this setting, a Microsoft Copilot Studio agent identity blueprint, and an agent identity blueprint principal, are automatically created. For more information, see
 Microsoft Entra Agent IDs for Copilot Studio agents
+and
+Agent identities and authentication for Copilot Studio
 .
 For agents in the
 Mic
```

---

### 5. AI Content Safety

**URL:** https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview
**Section:** Azure Services
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:eee230d75b0e3aff638feb91a266ff3b74e28ededcd632a3a7c228fcb43de1cf

**Affected Controls:**
- Control 1.27: Control 1.27: AI Agent Content Moderation Enforcement
  - File: `controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.27/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -218,6 +218,8 @@ Custom categories
 (standard) (preview)
 Multimodal
+Content provenance
+detection
 F0
 5 RPS
 5 RPS
@@ -226,6 +228,7 @@ 5 RPS
 5 RPS
 5 RPS
+1 RP10S
 S0
 1000 RP10S
 1000 RP10S
@@ -234,6 +237,12 @@ 1000 RP10S
 5 RPS
 10 RPS
+1 RP10S
+The content provenance detection limit applies to requests that submit content to the
+Detect API
+(
+POST /contentsafety/provenance:detect
+). Polling for the result has a higher limit: 5 RPS on F0 and 200 RP10S on S0.
 If you need a faster rate,
 contact us
 to request it.

```

---

### 6. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:c45074b75656ed59f6cb6323636373f9b0cf1633c008228e78610a643c5d8231

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.10/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.10/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.13/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.5/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -664,9 +664,15 @@ (formerly named Double Key Encryption for Microsoft 365) lets you protect your highly sensitive data to meet specialized requirements and maintain full control of your encryption key. Double Key Encryption uses two keys to protect your data, with one key in your control and the second key stored securely by Microsoft Azure. To view the data, you must have access to both keys. Since Microsoft can access only one key, your key and also your data are unavailable to Microsoft, ensuring that you have full control over the privacy and security of your data.
 Users benefit from Double Key Encryption by being able to migrate their encrypted data to the cloud, which prevents third-party access as long as the key remains in control of the users. Users can protect and consume Double Key Encrypted content similar to any other sensitivity label protected content.
 Feature
-Microsoft 365 E5/A5/G5, Microsoft Purview Suite/EDU/GOV/FLW and Microsoft Defender + Purview Suite FLW, Microsoft 365 E5/A5/F5/G5 Information Protection and Governance
-EMS E5
+Microsoft 365 E5/A5/G5
+Microsoft 365 E5/A5/F5/G5 Information Protection and Governance
+Microsoft Purview Suite/EDU/GOV/FLW
+Microsoft Defender + Purview Suite FLW
+Azure Information Protection Premium P2, including EMS E5
 Double Key Encryption
+Yes
+Yes
+Yes
 Yes
 Yes
 To assign encryption keys to data within an Office 365 and/or Microsoft 365 organization for licensed users, follow the Double Key Encryption deployment instructions

```

---

## HIGH: Control Review Recommended

### 1. Power Platform Inventory

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:8bd75b6d01a37ead50dd5eac04e171cae24a70114f2a674f8788cad5c2b3d58f

**Affected Controls:**
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`

**What Changed:**
```diff
--- +++ @@ -22,7 +22,7 @@ Power Platform inventory
 Feedback
 Summarize this article for me
-Power Platform inventory gives tenant administrators a unified view of all agents, apps, and flows built on Power Platform across their organization. Administrators can discover, search, filter, and sort these resources to streamline common administrative tasks.
+Power Platform inventory gives tenant administrators a unified view of all agents, apps, flows, and sites built on Power Platform across their organization. Administrators can discover, search, filter, and sort these resources to streamline common administrative tasks.
 By using Power Platform inventory, you can easily complete the following tasks:
 Map connector usage
 : Find which apps, flows, and agents use a given connector or operation. Use this information to scope DLP, audit Premium connector adoption, and plan ahead of deprecations, security issues, or licensing changes.
@@ -32,7 +32,7 @@ : Effortlessly detect resources created in nonapproved regions to maintain adherence to organizational policies.
 Focus your governance
 : Rank environments by resource count to focus security, governance, and compliance efforts where they matter most.
-Prevent orphaned agents
+Prevent orphaned resources
 : Proactively find resources owned by departing users to allow seamless ownership transfers and ensure business continuity.
 Accelerate support
 : Instantly pinpoint that
@@ -48,6 +48,8 @@ , and all apps you create in Microsoft 365 Copilot's App Builder agent.
 Flows
 : All agent flows you create in Copilot Studio, all cloud flows you create in Power Automate, and all workflows you create in Microsoft 365 Copilot's Workflows agent.
+Power Pages sites (preview)
+: Power Pages websites across your tenant.
 Connectors
 : All connectors available in your tenant, including the operations each connector exposes and its publisher and tier.
 Environments
@@ -96,7 +98,7 @@ Environments
 and
 environment groups
-Canvas apps, model-d
```

---

### 2. Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/alerts
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:3a27e65123b16710a65763716b1237f74df334677bc0b27d3e589cad3484deab

**What Changed:**
```diff
--- +++ @@ -28,9 +28,15 @@ Monitor
 area of the Power Platform admin center.
 Keep the following principles in mind:
-Alerts are evaluated after new metrics are produced. Currently, all metrics are 24-hour aggregates, which means an alert rule in the
-Monitor
-area is evaluated every 24 hours after the newest 24-hour aggregates are produced. An alert rule does an on-demand evaluation upon its creation.
+Alerts are evaluated after new metrics are produced. By default, all metrics are 24-hour aggregates, which means an alert rule with a 24 hour
+Data review period
+in the
+Monitor
+area is evaluated every 24 hours after the newest 24-hour aggregates are produced. However, you can also create an alert rule with a 1 hour
+Data review period
+. This enables an hourly aggregation on the resource's metric the alert rule is configured with. Alert rules with a 24 hour
+Data review period
+do an on-demand evaluation upon their creation.
 Alert rules are alerts that admins create to monitor their resources. You can edit, delete, and turn an alert rule on or off. You can place alert rules on an environment and a specific resource.
 A
 triggered alert
@@ -213,9 +219,9 @@ After you create your alert, the system runs an on-demand evaluation and scans all the applicable resources under its scope.
 Monitor critical resources with low-latency alerts (preview)
 Use low-latency alerts to evaluate supported resource metrics every hour instead of waiting for the daily evaluation. These alerts can help you detect issues sooner on mission-critical applications and other resources.
-For example, you can create a low-latency alert for a production canvas app to check whether its
-App open success rate
-falls below 95%. The rule evaluates each hour after new hourly metrics are produced and can fire when the condition is met, rather than waiting for the next daily evaluation.
+For example, you can create a low-latency alert for a production cloud flow to check whether its
+Success rate
+falls 
```

---

### 3. Release Plans (2025 Wave 2)

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:7c7f50d0ce3d31d06770a882b764548d4b7132341f29ac7a59a2fbe3d40078e2

**Affected Controls:**
- Control 1.27: Control 1.27: AI Agent Content Moderation Enforcement
  - File: `controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.27/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -7,7 +7,6 @@ Read in English
 Add
 Add to Plans
-Edit
 Copy Markdown
 Print
 Note
@@ -100,14 +99,4 @@ Let us know your thoughts. Share your feedback in the
 Microsoft Power Platform community forum
 . We'll use your feedback to make improvements.
-Feedback
-Was this page helpful?
-Yes
-No
-No
-Need help with this topic?
-Want to try using Ask Learn to clarify or guide you through this topic?
-Ask Learn
-Ask Learn
-Suggest a fix?
 Additional resources
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Release Plans (2025 Wave 2)
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:7c7f50d0ce3d31d06770a882b764548d4b7132341f29ac7a59a2fbe3d40078e2

---

### 2. Release Plans (2026 Wave 1)
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a2063cfdfb14c437bb2e2678a9611bd7fa78211131e73fc11df86b2301b7522a

---

### 3. Enhanced Admin Controls [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8ab5ce99b5a0deb0091abc3ed7a3217859446497af79ce1747d15ab258d84ccf

---

### 4. Agentic Center of Enablement [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/automate-governance-agentic-center-enablement
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:4a768e06409d00ce54fe534d9afb8e57d38e20173acc041666fd24978545a5e7

---

### 5. Copilot Studio guidance hub — What's new
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:18441039934811fa06847a198d9476f16811e3a01c59b7a03f6272e8ad289087

---

### 6. Manage the AI model lifecycle for Copilot Studio agents
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/plan-agent-model-lifecycle
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:fad4e5077cca33f3deb1f4b77e70649a9193430013561c86786dbd44c47eb91c

---

### 7. AI Content Safety
**URL:** https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:eee230d75b0e3aff638feb91a266ff3b74e28ededcd632a3a7c228fcb43de1cf

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2025wave2/ |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio | https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/automate-governance-agentic-center-enablement | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/automate-governance-agentic-center-enablement |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-overview | https://learn.microsoft.com/en-us/copilot/plan/copilot-overview |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy | https://learn.microsoft.com/en-us/copilot/plan/microsoft-365-copilot-privacy |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/enable-users | https://learn.microsoft.com/en-us/copilot/adopt/enable-users |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-overview | https://learn.microsoft.com/en-us/copilot/implement/copilot-controls-overview |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-security-governance | https://learn.microsoft.com/en-us/copilot/implement/copilot-controls-security-governance |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-management | https://learn.microsoft.com/en-us/copilot/implement/copilot-controls-management |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/security/operations/incident-response-planning | https://learn.microsoft.com/en-us/security/zero-trust/security-operations-incident-response-readiness |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*