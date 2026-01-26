# RACI Governance Template

## Overview

This template provides a Responsible-Accountable-Consulted-Informed (RACI) matrix for AI agent governance tasks in financial services organizations. Customize roles and assignments based on your organizational structure.

---

## RACI Legend

| Code | Meaning | Description |
|------|---------|-------------|
| **R** | Responsible | Does the work to complete the task |
| **A** | Accountable | Ultimately answerable for completion (only one per task) |
| **C** | Consulted | Provides input before decisions are made |
| **I** | Informed | Kept updated on progress and outcomes |

---

## Role Definitions

Adapt these roles to your organization's structure:

| Role | Typical Title(s) | Responsibility |
|------|------------------|----------------|
| **AI Gov Lead** | AI Governance Lead, AI Program Manager | Day-to-day governance program management |
| **Compliance** | Compliance Officer, CCO | Regulatory compliance oversight |
| **Risk** | Risk Manager, CRO | Enterprise risk assessment |
| **Security** | CISO, Security Architect | Security controls and monitoring |
| **Platform** | Power Platform Admin, M365 Admin | Technical platform administration |
| **Business** | Business Owner, Product Owner | Business requirements and UAT |
| **Legal** | General Counsel, Legal Counsel | Legal review and contracts |
| **Audit** | Internal Audit, External Audit | Independent assurance |
| **Exec Sponsor** | CIO, CDO, COO | Executive oversight and funding |

---

## Agent Lifecycle RACI

### Agent Creation and Deployment

| Task | AI Gov Lead | Compliance | Risk | Security | Platform | Business | Legal |
|------|-------------|------------|------|----------|----------|----------|-------|
| Zone classification | A | C | C | C | I | R | I |
| Business justification | C | I | I | I | I | A/R | I |
| Data source approval | C | A | C | C | R | R | I |
| Security assessment | C | I | C | A/R | C | I | I |
| Bias testing (Zone 2-3) | A | C | C | I | I | R | I |
| UAT sign-off | I | I | I | I | I | A/R | I |
| Production approval (Zone 2) | A | C | I | C | R | R | I |
| Production approval (Zone 3) | R | A | C | C | R | R | C |

### Agent Operations

| Task | AI Gov Lead | Compliance | Risk | Security | Platform | Business | Legal |
|------|-------------|------------|------|----------|----------|----------|-------|
| Performance monitoring | A | I | I | I | R | I | I |
| Incident response | C | I | C | A/R | R | I | C |
| Change management | A | C | I | C | R | R | I |
| Access reviews | C | A | I | C | R | I | I |
| Audit log review | C | A | I | C | R | I | I |
| Compliance testing | C | A/R | C | I | I | I | I |

### Agent Decommissioning

| Task | AI Gov Lead | Compliance | Risk | Security | Platform | Business | Legal |
|------|-------------|------------|------|----------|----------|----------|-------|
| Decommission request | I | I | I | I | I | A/R | I |
| Data retention verification | C | A | I | I | R | I | C |
| Access removal | I | I | I | C | A/R | I | I |
| Audit trail preservation | C | A | I | I | R | I | I |
| Decommission sign-off | A | C | I | C | R | R | I |

---

## Governance Program RACI

### Policy and Standards

| Task | AI Gov Lead | Compliance | Risk | Security | Platform | Legal | Exec Sponsor |
|------|-------------|------------|------|----------|----------|-------|--------------|
| Governance framework updates | A/R | C | C | C | C | C | I |
| DLP policy changes | C | C | I | C | A/R | I | I |
| Zone criteria updates | A | C | C | C | C | I | C |
| Connector policy updates | C | C | I | C | A/R | I | I |
| Training program development | A/R | C | I | C | C | I | I |

### Reviews and Assessments

| Task | AI Gov Lead | Compliance | Risk | Security | Platform | Audit | Exec Sponsor |
|------|-------------|------------|------|----------|----------|-------|--------------|
| Quarterly governance review | A/R | R | C | C | R | I | I |
| Semi-annual governance review | A/R | R | C | C | R | C | I |
| Annual governance assessment | A/R | R | R | R | R | C | A |
| Model risk validation | C | C | A/R | C | I | C | I |
| Regulatory examination prep | R | A | C | C | R | R | I |

### Incident and Exception Management

| Task | AI Gov Lead | Compliance | Risk | Security | Platform | Legal | Exec Sponsor |
|------|-------------|------------|------|----------|----------|-------|--------------|
| Security incident escalation | C | I | C | A/R | R | C | I |
| Policy exception request | A | C | C | C | I | I | C |
| Policy exception approval | R | A | C | C | I | C | C |
| Regulatory breach response | C | A | C | C | I | R | I |
| Board/executive reporting | R | C | C | C | I | I | A |

---

## Zone-Specific RACI Variations

### Zone 1 (Personal Productivity)

| Task | AI Gov Lead | Platform | Business |
|------|-------------|----------|----------|
| Agent creation | I | I | A/R |
| Self-service deployment | I | I | A/R |
| Basic compliance check | A | I | R |

### Zone 2 (Team Collaboration)

| Task | AI Gov Lead | Compliance | Platform | Business | Manager |
|------|-------------|------------|----------|----------|---------|
| Agent creation | C | I | I | R | A |
| Deployment approval | C | I | R | R | A |
| Quarterly review | A | C | R | I | R |

### Zone 3 (Enterprise Managed)

| Task | AI Gov Lead | Compliance | Risk | Security | Platform | Business | Legal | Exec Sponsor |
|------|-------------|------------|------|----------|----------|----------|-------|--------------|
| Agent creation | A | C | C | C | R | R | I | I |
| Security assessment | C | I | C | A/R | C | I | I | I |
| Bias testing | A | C | C | I | I | R | I | I |
| Deployment approval | R | A | C | C | R | R | C | I |
| Monthly review | A/R | R | C | C | R | I | I | I |
| Incident response | C | I | C | A/R | R | I | C | I |

---

## Customization Guide

### Step 1: Map Roles to Your Organization

| Template Role | Your Organization's Role | Name/Team |
|---------------|-------------------------|-----------|
| AI Gov Lead | | |
| Compliance | | |
| Risk | | |
| Security | | |
| Platform | | |
| Business | | |
| Legal | | |
| Audit | | |
| Exec Sponsor | | |

### Step 2: Validate Assignments

- [ ] Each task has exactly one "A" (Accountable)
- [ ] "R" (Responsible) assigned to roles with capacity
- [ ] "C" (Consulted) limited to essential input providers
- [ ] "I" (Informed) includes all stakeholders needing awareness
- [ ] No role is overloaded with responsibilities

### Step 3: Document Exceptions

| Task | Standard RACI | Your RACI | Rationale |
|------|---------------|-----------|-----------|
| | | | |

---

## RACI Review Schedule

| Review Type | Frequency | Participants |
|-------------|-----------|--------------|
| Role assignment validation | Quarterly | AI Gov Lead, HR |
| RACI matrix update | Semi-annually | All role owners |
| Full RACI refresh | Annually | Governance Committee |

---

## Related Documents

- [Governance Review Cadence](../../framework/governance-cadence.md) - Review schedules
- [Zones Guide](../../framework/zones-and-tiers.md) - Zone definitions
- [Agent Lifecycle](../../framework/agent-lifecycle.md) - Lifecycle phases

---

*FSI Agent Governance Framework v1.2 - January 2026*
