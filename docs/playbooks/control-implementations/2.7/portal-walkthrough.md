# Control 2.7: Vendor and Third-Party Risk Management - Portal Walkthrough

> This playbook provides portal-based configuration guidance for [Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md).

---

## Overview

This walkthrough guides you through inventorying third-party connectors, assessing vendor security, configuring connector policies, and establishing ongoing monitoring.

---

## Part 1: Inventory Third-Party Connectors

**Portal Path:** Power Platform Admin Center > Analytics > Power Automate/Power Apps

### Steps

1. Sign in to **Power Platform Admin Center**
2. Navigate to **Analytics** > **Power Automate** or **Power Apps**
3. Review connector usage reports across all environments
4. Export the list of connectors in use
5. Categorize connectors by:
   - Publisher type (Microsoft, certified, independent, custom)
   - Data sensitivity (what data flows through the connector)
   - Business criticality (impact if connector fails)
   - Environment placement (Zone 1, 2, or 3)

### Document for Each Connector

| Field | Description |
|-------|-------------|
| Connector Name | Official connector name |
| Publisher | Microsoft, verified publisher, or custom |
| Environments | List of environments where used |
| Data Types | What data flows through the connector |
| Business Owner | Internal owner responsible |
| Risk Classification | Low, Medium, High, Critical |

---

## Part 2: Connector Categories and Risk Levels

| Category | Examples | Risk Level | Assessment Frequency |
|----------|----------|------------|---------------------|
| **Microsoft First-Party** | Dataverse, SharePoint, Teams | Low | Annual |
| **Certified Third-Party** | Salesforce, SAP, ServiceNow | Medium | Semi-annual |
| **Independent Publisher** | Community-created connectors | High | Quarterly |
| **Custom Connectors** | Organization-built APIs | Medium-High | Quarterly |
| **External AI Services** | OpenAI, third-party LLMs | High | Quarterly |

---

## Part 3: Configure Connector Policies

**Portal Path:** Power Platform Admin Center > Policies > Data policies

### Policy Configuration by Risk Level

| Risk Level | DLP Classification | Approval Required | Monitoring |
|------------|-------------------|-------------------|------------|
| Low | Business | No | Standard |
| Medium | Business (with restrictions) | Manager | Enhanced |
| High | Non-business (blocked by default) | Security + Compliance | Continuous |
| Critical | Blocked | Exception process only | Real-time alerts |

### High-Risk Connector Exceptions

For high-risk connectors requiring exceptions:

1. Document business justification
2. Obtain security team approval
3. Implement compensating controls
4. Set review expiration date

---

## Part 4: Assess Vendor Security

### Security Documentation Required

For each third-party vendor (non-Microsoft connectors), request:

- SOC 2 Type II report (or equivalent)
- Security policies and procedures
- Data processing agreements
- Incident response procedures
- Business continuity plans

### Security Questionnaire Topics

- Data encryption (transit and rest)
- Access controls and authentication
- Audit logging capabilities
- Compliance certifications (SOC 2, ISO 27001, FedRAMP)
- Data residency and sovereignty
- Subprocessor management
- Incident notification procedures

---

## Part 5: AI-Specific Vendor Assessment

### AI Vendor Risk Categories

| Risk Category | Description | Assessment Focus |
|--------------|-------------|------------------|
| **Model Supply Chain** | Risks from underlying AI models | Model provenance, update processes |
| **Training Data** | Risks from data used to train models | Data sources, bias, consent |
| **Output Quality** | Risks from AI-generated content | Accuracy, hallucination, consistency |
| **Operational** | Risks from AI service operations | Availability, performance, support |
| **Regulatory** | Risks from evolving AI regulations | Compliance posture, audit support |

### AI-Specific Contract Clauses

| Clause Category | Requirement |
|-----------------|-------------|
| **Model Change Notification** | 30 days advance notice of material model changes |
| **Training Data Disclosure** | Transparency on training data sources |
| **No Training on Customer Data** | Prohibition without consent |
| **Audit Rights for AI** | Review of AI governance practices |
| **AI Incident Notification** | 24-hour notification of AI-related incidents |
| **Explainability Requirements** | Documentation of AI decision-making |

---

## Part 6: Dynamic Tool and Plugin Governance

### OWASP Agentic AI Top 10 Consideration

Dynamic tool loading creates unique risks:

- Runtime tool discovery
- Automatic capability updates
- Community plugins
- Transitive data exposure

### Dynamic Tool Governance Policy

| Setting | Recommended Value |
|---------|------------------|
| Default behavior | Deny by default |
| Allowlist required | Yes |
| Runtime discovery allowed | No |
| Auto-update allowed | No (for third-party) |

### Plugin Categories and Approval

| Category | Approval Required | Auto-Update | Review Frequency |
|----------|------------------|-------------|------------------|
| Microsoft First-Party | Standard | Yes | Annual |
| Verified Publisher | Security Review | No | Semi-annual |
| Community Plugins | Full Security + Legal | No | Quarterly |
| Custom Internal | Internal Security | No | Quarterly |

---

## Part 7: Establish Monitoring

### Connector Usage Monitoring

- Enable audit logging in Microsoft Purview
- Create alerts for unusual connector activity
- Monitor for new connector deployments

### Review Cadence

| Review Type | Frequency | Participants |
|-------------|-----------|--------------|
| Connector Usage | Monthly | IT Governance |
| Vendor Performance | Quarterly | IT + Business Owners |
| Security Assessments | Annual (minimum) | Security + Compliance |
| Contract Reviews | 90 days before renewal | Procurement + Legal |
| Board Reporting | Quarterly | Executive + Compliance |

---

## Related Playbooks

- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Assessment procedures
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

---

*Updated: January 2026 | Version: v1.1*
