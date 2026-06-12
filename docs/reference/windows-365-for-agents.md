# Windows 365 for Agents (W365A) Reference

**Last Updated:** June 2026
**Version:** v1.6.2

!!! note "Generally Available (week of June 1, 2026)"
    Windows 365 for Agents became **generally available** the week of June 1, 2026 ([What's new in Windows 365 for Agents](https://learn.microsoft.com/windows-365/agents/whats-new)). Confirm current **region availability** against Microsoft Learn before relying on it in a given geography, and validate licensing, billing-plan, and support terms for your tenant. Cloud PC pools for Copilot Studio computer-use runs remain in preview ([Use a Cloud PC pool for computer use runs (preview)](https://learn.microsoft.com/microsoft-copilot-studio/use-cloud-pc-pool)); complete organizational risk acceptance before treating W365A as a Zone 2/3 enforcement procedure.

---

## Overview

Windows 365 for Agents (W365A) is the Windows 365 execution layer for computer-using agents in Agent 365. Microsoft describes it as a way for Agent 365 agents to obtain Cloud PCs when work requires a full Windows session for desktop applications, browsers, files, or enterprise systems instead of API-only automation ([Windows 365 for Agents in Agent 365](https://learn.microsoft.com/windows-365/agents/w365a-availability-a365)).

Microsoft also describes W365A as a new class of Cloud PCs for agent use, built on the Windows 365 Cloud PC platform. Agents use a check-out/check-in model: an agent checks out a Cloud PC for a task, then checks it back in when the task completes ([What is Windows 365 for Agents?](https://learn.microsoft.com/windows-365/agents/introduction-windows-365-for-agents)). W365A reached general availability the week of June 1, 2026 ([What's new in Windows 365 for Agents](https://learn.microsoft.com/windows-365/agents/whats-new)); confirm current region availability against Microsoft Learn, as the supported regions may differ from the earlier preview footprint.

For FSI governance, W365A should be treated as an agent execution substrate that introduces endpoint, identity, network, audit, and billing evidence streams. It does not replace the framework's existing controls for audit logging, private connectivity, outbound network controls, or Agent 365 administration.

---

## Intune Policy Hooks

Microsoft states that Cloud PCs for Agents are managed through the Microsoft Intune admin center and appear under **Devices** > **All devices** with a `CPCA-` device-name prefix and a **Cloud PC for Agents** device model ([Manage and monitor Cloud PCs for Agents in Microsoft Intune](https://learn.microsoft.com/windows-365/agents/device-management-cloud-pcs-agents)).

Microsoft also states that Intune apps and policies can target Cloud PCs for Agents by using the device name prefix, device model, or enrollment profile in device groups or filters ([Manage and monitor Cloud PCs for Agents in Microsoft Intune](https://learn.microsoft.com/windows-365/agents/device-management-cloud-pcs-agents#assign-apps-and-policies)). A provisioning policy (agents) determines the configuration used to create Cloud PCs for Agents, and Microsoft maps that provisioning policy to a Cloud PC agent pool in Intune ([Create a provisioning policy (agents)](https://learn.microsoft.com/windows-365/agents/create-provisioning-policy-agents)).

| Intune hook | Governance use in this framework | Evidence to retain |
|-------------|----------------------------------|--------------------|
| `CPCA-` device-name prefix and **Cloud PC for Agents** model | Build dynamic groups or filters for W365A Cloud PCs without mixing human-user Cloud PCs into agent policy scope | Screenshot/export of the Intune device filter or dynamic group definition |
| Enrollment profile matching the provisioning policy | Tie a Cloud PC back to the agent pool and business owner recorded in [Control 2.25](../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Provisioning policy name, assigned agent list, and owner approval record |
| Intune app and configuration policy targeting | Apply endpoint hardening baselines, browser policy, extension restrictions, and approved tooling only to W365A Cloud PCs | Policy assignment export and last successful device check-in evidence |
| Compliance policy targeting | Track whether W365A Cloud PCs meet the same endpoint posture expectations as other managed endpoints | Compliance state export with remediation tickets for exceptions |

Implementation caveat: policy targeting depends on accurate naming, model, and enrollment-profile signals. Validate filters in a non-production W365A pool before relying on them for Zone 2 or Zone 3 evidence.

---

## Cloud PC Audit Evidence

W365A introduces two related evidence layers: Windows 365 Cloud PC administrative audit events and agent/session audit context across Agent 365, Microsoft Entra, Microsoft Defender, and Microsoft Purview.

| Evidence layer | Microsoft-documented location | Framework use |
|----------------|-------------------------------|---------------|
| Windows 365 Cloud PC audit logs | Microsoft states that Windows 365 audit logs record Cloud PC create, update, delete, assign, and remote actions, are enabled by default, and can be retrieved through Microsoft Graph beta cmdlets or exported through Intune **Reports** > **Diagnostic settings** by selecting `Windows365AuditLogs` ([Get Windows 365 audit logs](https://learn.microsoft.com/windows-365/enterprise/get-cloud-pc-audit-logs-using-powershell)). | Retain as supplemental evidence for [Control 1.7 — Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), especially when examiners ask how agent execution infrastructure is administered. |
| W365A agent session audit trail | Microsoft describes an end-to-end W365A audit view spanning Agent 365 task execution, Microsoft Entra sign-in logs, Microsoft Defender security events, and Microsoft Purview data access/governance activity ([Identity and security: secure by design](https://learn.microsoft.com/windows-365/agents/identity-security-secure-by-design#end-to-end-audit-trail)). | Correlate agent prompts, agent identity sign-ins, Cloud PC session activity, and Purview records under [Control 1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md). |
| Network path and private dependency evidence | W365A Cloud PCs are Microsoft Entra-joined and Intune-enrolled in the W365A identity/security model ([Identity and security: secure by design](https://learn.microsoft.com/windows-365/agents/identity-security-secure-by-design)). | Evaluate whether agent Cloud PC traffic to regulated dependencies should follow private connectivity patterns in [Control 1.20 — Network Isolation and Private Connectivity](../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md). |
| Outbound web access evidence | Microsoft documents network controls for agents as a Microsoft Entra Internet Access / Global Secure Access licensing area for agent identities ([Agent ID prerequisites](https://learn.microsoft.com/entra/agent-id/migrate-copilot-studio-agents-to-agent-id#prerequisites)). | Evaluate W365A-driven browser or web-application activity against [Control 1.29 — Global Secure Access Network Controls](../controls/pillar-1-security/1.29-global-secure-access-network-controls.md) where agent egress should be filtered or logged. |

Recommended evidence package for Zone 2 and Zone 3 W365A pilots:

1. W365A risk acceptance and approved use-case scope (GA the week of June 1, 2026; confirm regional availability for your tenant).
2. Intune device filter or dynamic group definition for `CPCA-` / **Cloud PC for Agents** devices.
3. Provisioning policy export, assigned agents, region, billing plan, and pool capacity.
4. Windows 365 audit-log export or Azure Monitor diagnostic setting showing `Windows365AuditLogs` routing.
5. Agent 365 / Entra / Purview correlation sample linking the human requester, agent identity, Cloud PC session, and data-access event.
6. Network evidence showing whether the Cloud PC path uses private connectivity, GSA egress filtering, or documented compensating controls.

---

## Mappings to Existing Controls

| W365A touchpoint | Existing framework mapping | Why it matters |
|------------------|----------------------------|----------------|
| Agent Cloud PC execution layer for UI-level or OS-level tasks | [Control 2.25 — Agent 365 Admin Center Governance Console](../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Agent approvals, owners, and governance templates should include whether W365A execution is enabled for the agent use case. |
| Cloud PC provisioning policies and agent pools | [Control 2.25](../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) and [License Requirements](license-requirements.md) | Pool configuration, billing plan, and assigned agents are part of the governance evidence for the agent service. |
| Intune-managed Cloud PCs for Agents | [Control 1.20 — Network Isolation and Private Connectivity](../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | W365A Cloud PCs add managed endpoint posture and network-path evidence that should be reviewed alongside private connectivity choices. |
| Windows 365 Cloud PC audit logs and W365A session audit trail | [Control 1.7 — Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Cloud PC administrative events and session correlation help support supervisory review and recordkeeping evidence. |
| Browser/web-application activity from agent Cloud PCs | [Control 1.29 — Global Secure Access Network Controls](../controls/pillar-1-security/1.29-global-secure-access-network-controls.md) | Agent-driven web access may need outbound filtering, traffic logs, and destination review. |
| Agent ID licensing and identity attribution | [Control 2.26 — Entra Agent ID Identity Governance](../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | Agent identity sponsorship, lifecycle, and Conditional Access should be reviewed before W365A is enabled for regulated tasks. |

---

## License Requirements Summary

For provisioning policies (agents), Microsoft lists these prerequisites: either a Windows 365 or Agent 365 license in the tenant, an active Windows 365 for Agents billing plan, and optional Agent users in Agent 365 that can use W365A ([Create a provisioning policy (agents)](https://learn.microsoft.com/windows-365/agents/create-provisioning-policy-agents#prerequisites)). Microsoft also describes W365A billing as consumption-based pay-as-you-go with an optional monthly always-available Cloud PC charge through an Azure subscription ([Set up billing for Windows 365 for Agents](https://learn.microsoft.com/windows-365/agents/billing-w365a), [Pricing for Windows 365 for Agents](https://learn.microsoft.com/windows-365/agents/pricing-paygo-always-available)).

For Agent ID features, Microsoft states that users need a **Microsoft Agent 365** or **Microsoft 365 E7** license, with additional licensing for Conditional Access, ID Protection, ID Governance, and network controls depending on the feature used ([Agent ID prerequisites](https://learn.microsoft.com/entra/agent-id/migrate-copilot-studio-agents-to-agent-id#prerequisites)).

See the W365A row in [License Requirements](license-requirements.md) for the framework-level interpretation. Validate procurement and availability directly with Microsoft before treating W365A as production-ready in a regulated environment.

---

## Microsoft Learn URLs Verified

- [What's new in Windows 365 for Agents](https://learn.microsoft.com/windows-365/agents/whats-new)
- [Windows 365 for Agents in Agent 365](https://learn.microsoft.com/windows-365/agents/w365a-availability-a365)
- [What is Windows 365 for Agents?](https://learn.microsoft.com/windows-365/agents/introduction-windows-365-for-agents)
- [Manage and monitor Cloud PCs for Agents in Microsoft Intune](https://learn.microsoft.com/windows-365/agents/device-management-cloud-pcs-agents)
- [Create a provisioning policy (agents)](https://learn.microsoft.com/windows-365/agents/create-provisioning-policy-agents)
- [Identity and security: secure by design](https://learn.microsoft.com/windows-365/agents/identity-security-secure-by-design)
- [Get Windows 365 audit logs](https://learn.microsoft.com/windows-365/enterprise/get-cloud-pc-audit-logs-using-powershell)
- [Set up billing for Windows 365 for Agents](https://learn.microsoft.com/windows-365/agents/billing-w365a)
- [Pricing for Windows 365 for Agents](https://learn.microsoft.com/windows-365/agents/pricing-paygo-always-available)
- [Agent ID prerequisites](https://learn.microsoft.com/entra/agent-id/migrate-copilot-studio-agents-to-agent-id#prerequisites)

---

*Updated: June 2026 | Version: v1.6.2 | UI Verification Status: Current*
