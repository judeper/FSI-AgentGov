# Power Platform SSPM Control Mapping

**Last Updated:** May 2026
**Version:** v1.6.2

---

!!! note "Point-in-Time Reference"
    This mapping was prepared in May 2026 based on FSI-AgentGov v1.6.2 and a representative Power Platform SSPM security assessment. Control coverage may change as the framework evolves.

## Overview

SaaS Security Posture Management (SSPM) tools evaluate Power Platform environments against security baselines. This page maps common Power Platform SSPM assessment controls to their FSI-AgentGov equivalents, helping organizations cross-reference SSPM findings with framework controls.

---

## How to Use This Document

If you are reviewing FSI-AgentGov coverage against a Power Platform SSPM assessment (such as FalconShield, Adaptive Shield, or similar):

1. Find your SSPM control ID in the mapping tables below
2. Follow the FSI-AgentGov control link(s) for full implementation details
3. Controls marked "Out of Scope" are intentionally excluded — see [Governance Fundamentals](../framework/governance-fundamentals.md#what-this-framework-does-not-cover) for scope rationale
4. Controls marked "Platform-Inherited" are handled by Entra ID tenant configuration
5. The [Configuration Hardening Baseline](../playbooks/advanced-implementations/configuration-hardening-baseline/index.md) provides a consolidated checklist for SSPM-detectable settings

---

## Coverage Summary

| Coverage Level | Count | % of Included | Notes |
|---|---|---|---|
| Full Coverage | 32 | 84% | FSI-AgentGov control fully addresses SSPM requirement |
| Partial Coverage | 1 | 3% | RBAC covers core requirement; Dataverse-specific review is a future candidate |
| Out of Scope | 5 | 13% | Outside FSI-AgentGov scope (Power Pages, Dynamics 365 email) |
| Excluded | 4 | N/A | Excluded (Operational/UX) |
| Platform-Inherited | 8 | N/A | Handled by Microsoft 365 / Entra ID platform |

---

## Mapping by Category

### Authentication & Access Control

| SSPM Control | FSI-AgentGov Control(s) | Coverage | Notes |
|---|---|---|---|
| SSPM-4: User Authentication Required| [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md), [1.23](../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md), [2.8](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Full | Comprehensive authentication with MFA and step-up auth |
| SSPM-5: Require Users to Sign In | [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Full | Phishing-resistant authentication mandated |
| SSPM-6: Auth Bypass Prevention | [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md), [1.23](../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | Full | No bypass scenarios allowed |
| SSPM-2: Prevent Unauthorized Actions | [1.18](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md), [2.8](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Full | RBAC + agent tool consent ("Ask the user before running this tool") |
| SSPM-23: Unrestricted Access to AI Agents | [1.1](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md), [1.2](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md), [2.2](../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | Full | Zone-based access with security groups |
| SSPM-32: Configure Security Groups | [2.2](../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md), [1.18](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | Full | Managed Environments with RBAC |
| SSPM-38: Set PPAC/Environment Admins | [2.8](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Full | Least privilege admin roles |

### Data Protection & DLP

| SSPM Control | FSI-AgentGov Control(s) | Coverage | Notes |
|---|---|---|---|
| SSPM-7: Blocked Attachments| [1.5](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [1.17](../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | Full | DLP policies enforce file extension blocking |
| SSPM-10: MIME Type Restriction | [1.25](../controls/pillar-1-security/1.25-mime-type-restrictions.md) | Full | Added in v1.2.49; comprehensive MIME/extension blocking with zone-tiered enforcement |
| SSPM-30: Tenant Isolation | [1.20](../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md), [1.4](../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | Full | ACP + network isolation |
| SSPM-33: Block Agent Publishing via DLP | [1.4](../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md), [1.1](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | Full | Connector-level DLP |
| SSPM-39: Set DLP in PPAC | [1.4](../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md), [1.5](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Full | Comprehensive DLP guidance |
| SSPM-34: Block Shared Agents | [1.2](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md), [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Full | Agent registry + M365 Admin Center blocking |

### Monitoring, Logging & Audit

| SSPM Control | FSI-AgentGov Control(s) | Coverage | Notes |
|---|---|---|---|
| SSPM-9: Audit Logging Enabled| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [3.9](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Full | Comprehensive logging + Sentinel SIEM |
| SSPM-11: Audit Log Retention (≥180 days) | [1.9](../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md), [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Full | 10-year retention for Zone 3 (exceeds 180-day minimum) |
| SSPM-31: Dataverse Auditing Policy | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [2.1](../controls/pillar-2-management/2.1-managed-environments.md) | Full | Managed Environments enforce Dataverse auditing |
| SSPM-36: Conversational Transcript Access | [1.19](../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md), [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Full | eDiscovery + RBAC controls |

### Session & Email Security

| SSPM Control | FSI-AgentGov Control(s) | Coverage | Notes |
|---|---|---|---|
| SSPM-8: Inactivity Timeout (≤120 min)| [2.22](../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md) | Full | Zone 2 ≤120 min, Zone 3 ≤60 min (added v1.2.46) |
| SSPM-12: Session Expiration (≤1440 min) | [2.22](../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md), [3.7](../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md) | Full | Session expiration documented in 3.7 hardening baseline; cross-referenced from 2.22 |
| SSPM-22: Mailbox Access in Dynamics| [1.18](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | Partial | RBAC covers access control; Dataverse-specific mailbox review is a candidate for future Pillar 2 control |

### AI-Specific Features & Safety

| SSPM Control | FSI-AgentGov Control(s) | Coverage | Notes |
|---|---|---|---|
| SSPM-18: AI Prompts Access| [1.14](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md), [2.16](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | Full | Scope control + RAG validation |
| SSPM-24: Generative Actions Enabled | [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md), [2.20](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Full | Orchestration limits + adversarial testing |
| SSPM-25: File Analysis Enabled | [1.6](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md), [1.14](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Full | DSPM + scope controls |
| SSPM-26: Model Knowledge | [1.14](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md), [2.16](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | Full | Scope + RAG validation |
| SSPM-27: Semantic Search | [4.6](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md), [4.1](../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | Full | IAG (RCD/RSS) + grounding scope |
| SSPM-28: Content Moderation | [1.10](../controls/pillar-1-security/1.10-communication-compliance-monitoring.md), [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Full | Compliance monitoring + bias testing |
| SSPM-37: Block Generative AI Features | [1.4](../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md), [2.1](../controls/pillar-2-management/2.1-managed-environments.md) | Full | ACP + Managed Environments |
| SSPM-42: Connected Agent Access | [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md), [1.22](../controls/pillar-1-security/1.22-information-barriers.md) | Full | Orchestration limits + information barriers |

### Environment & Lifecycle Management

| SSPM Control | FSI-AgentGov Control(s) | Coverage | Notes |
|---|---|---|---|
| SSPM-29: Block Bot Publishing via AI| [1.1](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md), [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Full | Publishing restrictions + change control |
| SSPM-35: Restrict Environment Creation | [2.2](../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md), [2.15](../controls/pillar-2-management/2.15-environment-routing.md) | Full | Tenant-level provisioning controls |
| SSPM-40: Environment Routing | [2.15](../controls/pillar-2-management/2.15-environment-routing.md) | Full | Regional routing |
| SSPM-41: Managed Environments | [2.1](../controls/pillar-2-management/2.1-managed-environments.md) | Full | Core governance control |
| SSPM-19: CSP Enforcement | [3.7](../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md) | Full | CSP enforcement documented in PPAC security posture hardening baseline |

---

## Controls Not Mapped

The following SSPM controls have no FSI-AgentGov equivalent by design:

### Out of Scope (Power Pages)

| SSPM Control | Reason |
|---|---|
| SSPM-1: Power Pages Table Permissions | Power Pages portal security is outside FSI-AgentGov scope (focused on Copilot Studio/Agent Builder) |
| SSPM-17: Old Pending Invitations (Portal) | Power Pages invitation lifecycle management is outside scope |

### Out of Scope (Dynamics 365 Email)

| SSPM Control | Reason |
|---|---|
| SSPM-13: Email Message Content Restriction | Dynamics 365 server-side sync setting; Copilot Studio uses MCP-based email channels |
| SSPM-15: Process Emails - Approved Queues | Dynamics 365 server-side sync feature, not applicable to AI agent governance |
| SSPM-16: Process Emails - Approved Users | Same as SSPM-15 |

### Excluded (Operational)

| SSPM Control | Reason |
|---|---|
| SSPM-3: User-Defined Action Messages | UX governance, not a security control |
| SSPM-14: Emails with Unresolved Recipients | Data quality, not security |
| SSPM-20: Email Notifications | Operational alerting |
| SSPM-21: Activities Visibility | UI feature |

### Platform-Inherited (Entra ID)

| SSPM Control | Reason |
|---|---|
| SSPM-ORG-1 through SSPM-ORG-8: Organization SSO/Auth Standards | Handled by the organization's Entra ID SSO integration; no additional FSI-AgentGov controls needed |

---

## User Consent Coverage Note

SSPM control SSPM-2 (Prevent Unauthorized Agent Actions) maps to two complementary FSI-AgentGov controls:

- **[Control 1.18](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md)** — Agent tool consent: "Ask the user before running this tool" for all agent tools in Zone 2/3
- **[Control 2.23](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md)** — AI disclosure consent: User acknowledgment of AI interaction with 90-day re-acknowledgment cycle

---

*Updated: May 2026 | Version: v1.6.2 | Source: Power Platform SSPM Assessment*
