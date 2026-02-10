# Configuration Hardening Baseline

**Status:** February 2026 - FSI-AgentGov v1.3
**Related Controls:** 1.1, 1.7, 1.8, 1.18, 2.1, 3.7, 3.8

---

## Purpose

This playbook consolidates security-critical configuration settings across Power Platform, Copilot Studio, and M365 Admin Center into a single reviewable hardening baseline. It enables FSI organizations to proactively verify their configuration posture across agent authentication, audit logging, content moderation, RBAC, environment governance, and AI feature access — addressing the settings most commonly flagged by security posture assessments.

**Applies to:** All zones; baseline settings apply organization-wide, with stricter requirements for Zone 2/3 environments.

---

## Problem Statement

Financial services organizations face continuous configuration drift risk across dozens of inter-related settings spanning multiple admin portals. Native PPAC security recommendations cover a subset of these settings, but critical agent-level configurations (authentication mode, content moderation level, AI feature toggles, connected agent access) are not surfaced in native posture scoring and require manual verification.

**Key challenges:**

1. **Settings span multiple portals** — PPAC, Copilot Studio, M365 Admin Center, Entra ID
2. **No native aggregated view** — each setting must be checked individually
3. **Configuration drift between reviews** — settings may change between weekly/monthly review cycles
4. **Audit evidence collection** — manual screenshots and attestation forms for each setting

---

## Master Configuration Hardening Checklist

### Agent Authentication and Access (Control 1.1)

| # | Setting | Portal Path | Expected Value (Zone 2/3) | Severity |
|---|---------|-------------|---------------------------|----------|
| 1 | Agent authentication mode | Copilot Studio > Agent > Settings > Security | Not "No Authentication" | High |
| 2 | Require users to sign in (manual auth) | Copilot Studio > Agent > Settings > Security | Enabled | High |
| 3 | Authentication enforcement timing | Copilot Studio > Agent > Settings > Security | "Always" (not "As Needed") | High |
| 4 | Agent sharing scope | Copilot Studio > Agent > Channels > Share Settings | Copilot Readers or Security Groups (not "Anyone") | High |
| 5 | Publish bots with AI features | PPAC > Tenant Settings | Disabled (until governance review) | High |
| 6 | Unapproved shared agents blocked | M365 Admin > Copilot > Agents & connectors > Agent Inventory | Blocked | High |

### Audit Logging (Control 1.7)

| # | Setting | Portal Path | Expected Value | Severity |
|---|---------|-------------|----------------|----------|
| 7 | Environment-level auditing | PPAC > Environment > Settings > Audit and logs | "Start Auditing" enabled | High |
| 8 | Audit log retention period | PPAC > Environment > Audit settings > "Retain these logs for" | ≥ 180 days (Zone 1), ≥ 365 days (Zone 2), ≥ 730 days (Zone 3) | High |
| 9 | Tenant-level Dataverse auditing | PPAC > Security > Compliance > Auditing | "Turn on Auditing" enabled with User Sign-In and Activity | Medium |

### Content Moderation (Control 1.8)

| # | Setting | Portal Path | Expected Value (Zone 2/3) | Severity |
|---|---------|-------------|---------------------------|----------|
| 10 | Content moderation level | Copilot Studio > Agent > Settings > Generative AI > Content moderation | High | High |

### RBAC and Agent Governance (Control 1.18)

| # | Setting | Portal Path | Expected Value | Severity |
|---|---------|-------------|----------------|----------|
| 11 | Agent action user consent | Copilot Studio > Agent > Actions | "Ask the user before running this action" enabled for all actions | High |
| 12 | Connected agent access | Copilot Studio > Agent > Settings > Connected Agents | Disabled unless explicitly approved | High |
| 13 | Environment admin count | PPAC > Environment > Users + Permissions | < 10 System Administrators per environment | Medium |

### Environment Provisioning (Control 2.1)

| # | Setting | Portal Path | Expected Value | Severity |
|---|---------|-------------|----------------|----------|
| 14 | Environment creation restriction | PPAC > Tenant Settings > Dev/Prod/Trial environment assignments | "Only specific admins" | High |
| 15 | Environment routing | PPAC > Tenant Settings > Environment Routing | Configured for correct region | Medium |
| 16 | Tenant isolation | PPAC > Security > Identity and access > Tenant Isolation | "Restrict Cross-Tenant Connections" enabled | High |
| 17 | Environment security groups | PPAC > Environment details > Security group | Assigned for all Zone 2/3 environments | High |

### AI Feature Access (Control 3.8)

| # | Setting | Portal Path | Expected Value (Zone 2/3) | Severity |
|---|---------|-------------|---------------------------|----------|
| 18 | AI Prompts | PPAC > Environment > Settings > Features | Off (unless approved) | Medium |
| 19 | Generative Actions | Copilot Studio > Agent > Overview > Orchestration | Off (unless approved) | High |
| 20 | File Analysis | Copilot Studio > Agent > Settings > Generative AI > File processing | Off (unless approved) | Medium |
| 21 | Model Knowledge | Copilot Studio > Agent > Settings > Generative AI | Off for sensitive data agents | Medium |
| 22 | Semantic Search | Copilot Studio > Agent > Settings > Generative AI | Off (unless approved) | High |
| 23 | Generative AI features (per-env) | PPAC > Environment > Generative AI features | Restrict by default | Medium |
| 24 | Move Data Across Regions | PPAC > Environment > Generative AI features | Off | High |
| 25 | Bing Search | PPAC > Environment > Generative AI features | Off | Medium |
| 26 | Conversational transcript access | PPAC > Environment > Features > Copilot Studio Agents | Restricted to authorized personnel | Medium |
| 27 | DLP for agent publishing connectors | PPAC > Data policies | Block Copilot Studio for Teams and M365 Copilot channel in restricted environments | High |

---

## Review Frequency

| Zone | Review Cadence | Reviewer | Evidence Requirement |
|------|---------------|----------|---------------------|
| **Zone 1** | Monthly | Power Platform Admin | Checklist completion record |
| **Zone 2** | Bi-weekly | Power Platform Admin + AI Governance Lead | Checklist + screenshot evidence |
| **Zone 3** | Weekly | Power Platform Admin + Compliance Officer | Checklist + screenshot evidence + attestation statement |

---

## Manual Attestation Procedures

For settings that cannot be validated through automated means (tenant-level toggles, approval-based configurations), collect evidence using the following procedures:

### Evidence Collection Template

For each setting in the checklist:

1. **Navigate** to the portal path listed in the checklist
2. **Capture** a screenshot showing the current setting value
3. **Document** in the attestation record:
   - Setting name and portal path
   - Current value observed
   - Expected value per checklist
   - Pass/Fail determination
   - Reviewer name and date
   - Exception documentation (if applicable)
4. **Archive** screenshots and attestation records per your organization's evidence retention policy

### Attestation Record Format

```
Setting: [Name from checklist]
Portal Path: [Path from checklist]
Expected: [Expected value]
Observed: [Actual value]
Status: [Pass / Fail / Exception]
Reviewer: [Name]
Date: [YYYY-MM-DD]
Exception Justification: [If applicable]
Next Review: [Date]
```

---

## Integration with Existing Solutions

This hardening baseline complements existing FSI-AgentGov solutions:

| Solution | Integration Point |
|----------|-------------------|
| **Audit Configuration Validator** | Validates items 7-9 (audit logging settings) automatically |
| **Environment Lifecycle Management** | Validates items 14-17 (environment provisioning) at creation time |
| **Compliance Dashboard** | Aggregate hardening baseline results into compliance posture scoring |

### Planned Solution: Agent Security Configuration Validator

A new solution is planned to automate validation of Copilot Studio agent-level settings (items 1-6, 10-12, 18-22):

- Validates authentication mode, content moderation, connected agent access, and AI feature toggles across all agents in a tenant
- Uses Power Platform Admin Connector + Copilot Studio management API
- Provides daily drift detection with compliance scoring
- Maps to Controls 1.1, 1.8, 1.18, 3.8

---

## Related Resources

- [Control 3.7: PPAC Security Posture Assessment](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md) — Native PPAC posture scoring
- [Control 1.24: Defender AI Security Posture Management](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) — Multi-cloud AI infrastructure posture
- [PPAC Security Best Practices](https://learn.microsoft.com/en-us/power-platform/admin/security/security-overview)

---

*Updated: February 2026 | Version: v1.0*
