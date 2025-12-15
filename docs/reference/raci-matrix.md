# RACI Matrix: Roles and Responsibilities

Define who is Responsible, Accountable, Consulted, and Informed for each governance activity.

---

## RACI Definitions

- **R (Responsible):** Does the work
- **A (Accountable):** Final approval authority
- **C (Consulted):** Provides input and expertise
- **I (Informed):** Kept updated on status

---

## Agent Governance Activities

### Zone 1: Personal Agent Deployment

| Activity | AI Lead | Compliance | CISO | PP Admin | Requester | Board |
|----------|---------|-----------|------|----------|-----------|-------|
| Create personal agent | C | I | I | I | R | I |
| Document purpose | R/A | I | I | I | I | I |
| Deploy to personal env | I | I | I | R | A | I |
| Record in inventory | I | R | I | I | I | I |

**Summary:** Personal agent, minimal governance, creator owns documentation.

---

### Zone 2: Team Agent Deployment

| Activity | AI Lead | Compliance | CISO | PP Admin | Manager | Board |
|----------|---------|-----------|------|----------|---------|-------|
| Business case review | A | C | C | I | R | I |
| Risk assessment | R | C | C | I | C | I |
| Approval workflow | C | R/A | C | I | C | I |
| Security review | C | C | R/A | C | I | I |
| Deploy to team env | I | I | I | R/A | I | I |
| Document in registry | I | R | I | I | C | I |
| Train team | C | I | I | I | R/A | I |
| Quarterly review | R | A | I | I | C | I |

**Summary:** Team agent, formal approval, manager sign-off, quarterly reviews.

---

### Zone 3: Enterprise Agent Deployment

| Activity | AI Lead | Compliance | CISO | Legal | CRO | Board | External Auditor |
|----------|---------|-----------|------|-------|-----|-------|-----------------|
| Strategic planning | R/A | C | C | I | C | C | I |
| Business case | R | C | C | C | R | C | I |
| Risk assessment | R | C | C | C | C | A | C |
| Regulatory review | C | R/A | C | C | C | A | C |
| Security testing | C | C | R/A | C | I | I | C |
| Model risk assess | R | C | C | I | A | A | C |
| Bias/fairness testing | R/A | C | C | I | C | C | C |
| Legal review | C | C | I | R/A | I | C | C |
| Governance committee | R | A | A | A | A | A | I |
| Change control | I | C | R | C | C | I | I |
| Deploy to production | I | I | I | I | I | R/A | I |
| Document in registry | I | R | I | I | I | I | I |
| Train operators | C | I | I | I | I | I | I |
| Monthly monitoring | R/A | A | C | I | C | I | C |
| Quarterly review | R | A | C | C | A | A | I |
| Annual validation | R | C | C | I | A | A | A |

**Summary:** Enterprise agent, comprehensive governance, board-level oversight, multiple approvals.

---

## Core Governance Roles

### 1. Chief Information Security Officer (CISO)
**Accountability:** Information security program and risk management

**Responsibilities:**
- Oversee agent security requirements
- Approve security testing procedures
- Incident response and escalation
- Define encryption standards
- MFA and conditional access policies
- Runtime threat detection
- Reporting to board/audit committee

**Zone Focus:** Zones 2 & 3 security

---

### 2. Chief Compliance Officer / Compliance Officer
**Accountability:** Regulatory compliance and governance effectiveness

**Responsibilities:**
- Define governance policies and procedures
- Oversee compliance assessments
- Regulatory relationship management
- Audit coordination
- Incident investigation and reporting
- Compliance training
- Executive reporting on compliance status

**Zone Focus:** Zones 2 & 3 compliance

---

### 3. AI Governance Lead
**Accountability:** Agent governance framework and implementation

**Responsibilities:**
- Framework administration
- Agent classification to zones
- Governance committee chair (Zone 3)
- Model risk management oversight
- Change control coordination
- Compliance dashboard
- Governance team leadership

**Zone Focus:** All zones

---

### 4. Power Platform Administrator
**Accountability:** Technical implementation and platform governance

**Responsibilities:**
- Environment setup and management
- Connector policies and restrictions
- DLP policy configuration and testing
- Audit logging setup and retention
- ALM pipeline configuration
- Performance monitoring
- Technical troubleshooting

**Zone Focus:** Technical setup for all zones

---

### 5. Compliance Administrator
**Accountability:** Compliance monitoring and audit support

**Responsibilities:**
- Audit log management
- Compliance reporting
- Data retention policies
- eDiscovery coordination
- Policy violation investigation
- Audit evidence compilation
- Compliance training administration

**Zone Focus:** Zones 2 & 3 monitoring

---

### 6. Security Administrator
**Accountability:** Identity and access security

**Responsibilities:**
- MFA and Conditional Access setup
- User provisioning and deprovisioning
- Threat investigation
- Insider risk monitoring
- Access review coordination
- Incident response

**Zone Focus:** Authentication and access control

---

### 7. SharePoint Administrator
**Accountability:** SharePoint governance for agents

**Responsibilities:**
- Site permissions and access control
- RCD (Restricted Content Discovery) setup
- Retention policies
- Guest access controls
- Information access governance
- Site-level compliance monitoring

**Zone Focus:** SharePoint-specific controls (Pillar 4)

---

### 8. Legal/General Counsel
**Accountability:** Legal risk and regulatory obligations

**Responsibilities:**
- AI vendor agreements
- Customer disclosure requirements
- Regulatory filing/disclosure
- Model validation oversight
- Fair lending compliance
- Breach notification procedures

**Zone Focus:** Zone 3 legal review

---

### 9. Chief Risk Officer (CRO)
**Accountability:** Enterprise risk oversight

**Responsibilities:**
- Model risk governance (OCC SR 11-7)
- Fair lending oversight
- Third-party risk management
- Risk committee reporting
- Model validation supervision
- Bias/fairness testing oversight

**Zone Focus:** Model risk for Zones 2 & 3

---

### 10. Internal Audit
**Accountability:** Independent control testing and assessment

**Responsibilities:**
- Annual control testing
- Governance procedure testing
- Compliance monitoring
- Model validation reviews
- Audit reporting to board
- Finding follow-up
- SOX 404 assessment

**Zone Focus:** All zones monitoring

---

## Agent Lifecycle Responsibilities

### Agent Creation Phase

| Role | Responsibility | Timing |
|------|-----------------|--------|
| Requester | Submit business case | Day 1 |
| AI Lead | Initial classification | Day 2 |
| Manager (Zone 2+) | Approve request | Day 3 |
| Compliance | Review for regulatory fit | Day 4 |
| CISO | Security assessment | Day 5 |
| Governance Committee (Zone 3) | Final approval | Day 10 |

---

### Implementation Phase

| Role | Responsibility | Timing |
|------|-----------------|--------|
| PP Admin | Setup environment | Day 1-2 |
| Developer | Build and test | Day 3-5 |
| QA | Test procedures | Day 6-7 |
| CISO | Security testing | Day 8-10 |
| Compliance | Compliance verification | Day 11 |
| AI Lead | Final sign-off | Day 12 |

---

### Operations Phase

| Role | Responsibility | Frequency |
|------|-----------------|-----------|
| Requester/Owner | Daily monitoring | Daily |
| PP Admin | Availability monitoring | Daily |
| Compliance | Compliance checks | Weekly |
| AI Lead | Zone 2+ oversight | Weekly |
| Compliance Officer | Monthly compliance review | Monthly |
| Internal Audit | Quarterly testing | Quarterly |
| Governance Committee (Zone 3) | Monthly oversight | Monthly |
| CISO | Security monitoring | Continuous |

---

### Incident Response Phase

| Role | Responsibility | Timing |
|------|-----------------|--------|
| Observer | Report incident | Immediately |
| PP Admin | Initial containment | <1 hour |
| CISO | Security assessment | <4 hours |
| Compliance Officer | Investigate root cause | <24 hours |
| AI Lead | Notify governance committee | <24 hours |
| Board (if material) | Escalation and approval | <48 hours |

---

## Approval Authority by Zone

### Zone 1: Personal Productivity
- **Approver:** Self-service (creator)
- **Escalation:** N/A

### Zone 2: Team Collaboration
- **Approver:** Manager or Department Head
- **Escalation:** AI Governance Lead or Compliance Officer

### Zone 3: Enterprise Managed
- **Approvers:** 
  - Compliance Officer
  - CISO
  - General Counsel (if customer-facing)
  - CRO (if credit-related)
- **Final Authority:** Governance Committee
- **Escalation:** CEO or Board for material issues

---

## Governance Committee (Zone 3)

### Composition
- Chair: AI Governance Lead
- Members:
  - Compliance Officer
  - CISO
  - General Counsel
  - Chief Risk Officer (if OCC/CRO regulated)
  - Business Owner (agent requester)
  - Internal Audit (observer)

### Meeting Frequency
- Monthly for Zone 3 oversight
- Special meetings for incidents or urgent items

### Key Responsibilities
1. Approve Zone 3 agent deployments
2. Monitor ongoing compliance
3. Approve model changes
4. Escalate issues to senior management
5. Report to board quarterly

---

## Training Requirements

| Role | Training Topic | Frequency |
|------|---|---|
| **All Staff** | AI governance basics | Annual |
| **Agent Creators** | Development best practices | Annual |
| **Agent Managers** | Oversight and approval | Annual |
| **Compliance** | Detailed framework | Annual + as-needed |
| **CISO** | Security controls | Annual + as-needed |
| **Board/Exec** | AI governance overview | Annual |

---

## Escalation Procedures

**Level 1 (Compliance Officer):**
- Policy violations
- Non-compliance findings
- Performance issues

**Level 2 (CISO/Compliance):**
- Security incidents
- Potential data breaches
- Regulatory concerns

**Level 3 (Board/CEO):**
- Material security breaches
- Regulatory violations
- Customer impact incidents
- Significant compliance failures

---

*FSI Agent Governance Framework Beta - December 2025*
