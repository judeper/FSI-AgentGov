# Adoption Roadmap

Phased implementation guidance for deploying the FSI Agent Governance Framework.

---

## Overview

This roadmap provides a structured approach to implementing AI agent governance. Organizations should adapt timelines and priorities based on their specific regulatory obligations, existing infrastructure, and agent deployment plans.

---

## Implementation Phases

| Phase | Timeline | Focus | Key Outcomes |
|-------|----------|-------|--------------|
| **Phase 0** | 0-60 days | Foundation | Governance structure, core controls, Zone 1-2 enabled |
| **Phase 1** | 2-6 months | Production Readiness | SoD, reporting, Zone 3 governance, first agents |
| **Phase 2** | 6-12 months | Advanced Governance | Runtime protection, adversarial testing, steady-state |

---

## Phase 0: Foundation (0-60 days)

### Objectives

- Establish governance structure and accountability
- Deploy minimum viable controls for initial agent usage
- Enable Zone 1 and Zone 2 environments
- Complete baseline training for key stakeholders

### Core Controls to Implement

| Control | Name | Priority | Owner |
|---------|------|----------|-------|
| 1.1 | Restrict Agent Publishing by Authorization | Critical | Power Platform Admin |
| 1.5 | Data Loss Prevention (DLP) and Sensitivity Labels | Critical | Purview Admin |
| 2.1 | Managed Environments | Critical | Power Platform Admin |
| 2.3 | Change Management and Release Planning | High | AI Governance Lead |
| 3.1 | Agent Inventory and Metadata Management | Critical | AI Governance Lead |
| 4.1 | SharePoint IAG and Restricted Content Discovery | High | SharePoint Admin |

### Week-by-Week Activities

**Weeks 1-2: Governance Structure**

- [ ] Identify AI Governance Lead and assign accountability
- [ ] Draft governance committee charter (Zone 3 preparation)
- [ ] Review existing IT policies for AI agent implications
- [ ] Conduct initial regulatory mapping review
- [ ] Identify Power Platform Admin and SharePoint Admin leads

**Weeks 3-4: Core Technical Controls**

- [ ] Configure Managed Environments for Zone 2 (Control 2.1)
- [ ] Implement baseline DLP policies (Control 1.5)
- [ ] Enable default environment routing (Control 2.15)
- [ ] Restrict agent publishing to authorized users (Control 1.1)
- [ ] Configure audit logging baseline (Control 1.7)

**Weeks 5-6: Environment Setup**

- [ ] Create Zone 1 personal developer environment group
- [ ] Create Zone 2 team collaboration environment group
- [ ] Configure environment group rules for sharing
- [ ] Enable sensitivity labels for agent content
- [ ] Document environment architecture

**Weeks 7-8: Operational Readiness**

- [ ] Establish agent inventory process (Control 3.1)
- [ ] Create change management workflow (Control 2.3)
- [ ] Document SharePoint sites approved for agent grounding (Control 4.1)
- [ ] Complete baseline training for Power Platform Admin
- [ ] Conduct first governance review meeting

### Phase 0 Success Criteria

- [ ] AI Governance Lead appointed with clear accountability
- [ ] Zone 1 and Zone 2 environments configured with DLP policies
- [ ] Agent publishing restricted to authorized users
- [ ] Agent inventory process documented and operational
- [ ] Baseline audit logging enabled
- [ ] Key stakeholders trained on governance requirements

### Phase 0 Deliverables

| Deliverable | Owner | Due |
|-------------|-------|-----|
| Governance committee charter | AI Governance Lead | Week 2 |
| Environment architecture document | Power Platform Admin | Week 4 |
| DLP policy documentation | Purview Admin | Week 4 |
| Agent inventory process | AI Governance Lead | Week 6 |
| Training completion records | Training Lead | Week 8 |

---

## Phase 1: Production Readiness (2-6 months)

### Objectives

- Implement segregation of duties and access controls
- Enable comprehensive reporting and monitoring
- Establish Zone 3 governance structure
- Deploy first production agents with full governance

### Controls to Implement

| Control | Name | Priority | Owner |
|---------|------|----------|-------|
| 1.7 | Comprehensive Audit Logging and Compliance | Critical | Purview Admin |
| 1.9 | Data Retention and Deletion Policies | Critical | Purview Admin |
| 1.11 | Conditional Access and Phishing-Resistant MFA | High | Entra Admin |
| 2.5 | Testing Validation and Quality Assurance | High | QA Lead |
| 2.8 | Access Control and Segregation of Duties | Critical | AI Governance Lead |
| 2.12 | Supervision and Oversight (FINRA 3110) | Critical | Compliance Officer |
| 3.2 | Usage Analytics and Activity Monitoring | High | AI Governance Lead |
| 3.3 | Compliance and Regulatory Reporting | High | Compliance Officer |
| 3.7 | PPAC Security Posture Assessment | High | Power Platform Admin |
| 4.2 | Site Access Reviews and Certification | High | SharePoint Admin |

### Month-by-Month Activities

**Month 2: Access and Segregation**

- [ ] Implement segregation of duties controls (Control 2.8)
- [ ] Configure role-based access for PPAC (Control 1.18)
- [ ] Enable conditional access policies for Zone 3 (Control 1.11)
- [ ] Document approval workflows for Zone 2-3 agents
- [ ] Conduct access review for existing admin roles

**Month 3: Reporting and Monitoring**

- [ ] Configure usage analytics dashboard (Control 3.2)
- [ ] Implement compliance reporting process (Control 3.3)
- [ ] Enable PPAC security posture monitoring (Control 3.7)
- [ ] Set up orphaned agent detection (Control 3.6)
- [ ] Create executive reporting templates

**Month 4: Zone 3 Governance**

- [ ] Establish governance committee with regular meetings
- [ ] Document Zone 3 approval workflow
- [ ] Configure 10-year retention for Zone 3 environments (Control 1.9)
- [ ] Implement supervision controls (Control 2.12)
- [ ] Create Zone 3 agent deployment checklist

**Month 5: Testing and Validation**

- [ ] Implement testing procedures (Control 2.5)
- [ ] Create test environment for Zone 3 agents
- [ ] Document bias testing requirements (Control 2.11)
- [ ] Conduct first model risk assessment (Control 2.6)
- [ ] Validate DLP policy effectiveness

**Month 6: First Production Agents**

- [ ] Deploy first Zone 3 agent with full governance
- [ ] Conduct governance committee review
- [ ] Document lessons learned
- [ ] Update procedures based on experience
- [ ] Conduct first quarterly governance review

### Phase 1 Success Criteria

- [ ] Segregation of duties implemented for agent lifecycle
- [ ] Comprehensive audit logging with appropriate retention
- [ ] Governance committee operational with documented procedures
- [ ] At least one Zone 3 agent deployed with full governance
- [ ] Quarterly compliance reporting process established
- [ ] First quarterly governance review completed

### Phase 1 Deliverables

| Deliverable | Owner | Due |
|-------------|-------|-----|
| Access control matrix | AI Governance Lead | Month 2 |
| Compliance reporting templates | Compliance Officer | Month 3 |
| Zone 3 approval workflow | AI Governance Lead | Month 4 |
| Testing procedures | QA Lead | Month 5 |
| First quarterly governance review | AI Governance Lead | Month 6 |

---

## Phase 2: Advanced Governance (6-12 months)

### Objectives

- Implement advanced security controls
- Enable adversarial testing program
- Integrate with Sentinel for advanced monitoring
- Achieve steady-state governance operations

### Controls to Implement

| Control | Name | Priority | Owner |
|---------|------|----------|-------|
| 1.6 | Microsoft Purview DSPM for AI | High | Purview Admin |
| 1.8 | Runtime Protection and External Threat Detection | High | Security Team |
| 1.19 | eDiscovery for Agent Interactions | High | Purview Admin |
| 1.22 | Information Barriers for AI Agents | Medium | Compliance Officer |
| 2.6 | Model Risk Management (OCC 2011-12) | Critical | CRO/Risk |
| 2.11 | Bias Testing and Fairness Assessment | High | AI Governance Lead |
| 2.16 | RAG Source Integrity Validation | High | AI Governance Lead |
| 2.20 | Adversarial Testing and Red Team Framework | High | Security Team |
| 3.9 | Microsoft Sentinel Integration | High | Security Team |
| 3.10 | Hallucination Feedback Loop | Medium | AI Governance Lead |

### Quarterly Activities

**Quarter 3 (Months 7-9): Advanced Security**

- [ ] Deploy runtime protection for Zone 3 agents (Control 1.8)
- [ ] Configure DSPM for AI monitoring (Control 1.6)
- [ ] Implement eDiscovery procedures (Control 1.19)
- [ ] Enable information barriers if required (Control 1.22)
- [ ] Conduct security assessment of agent infrastructure

**Quarter 4 (Months 10-12): Advanced Monitoring and Testing**

- [ ] Integrate with Microsoft Sentinel (Control 3.9)
- [ ] Implement adversarial testing program (Control 2.20)
- [ ] Establish hallucination feedback loop (Control 3.10)
- [ ] Conduct comprehensive bias testing (Control 2.11)
- [ ] Complete annual governance review
- [ ] Document steady-state operations procedures

### Phase 2 Success Criteria

- [ ] Runtime protection deployed for all Zone 3 agents
- [ ] Sentinel integration operational with analytics rules
- [ ] Adversarial testing program established
- [ ] Model risk management framework aligned with SR 11-7
- [ ] All 61 controls assessed and appropriately implemented
- [ ] Steady-state governance operations documented

### Phase 2 Deliverables

| Deliverable | Owner | Due |
|-------------|-------|-----|
| Runtime protection deployment | Security Team | Month 9 |
| Sentinel analytics rules | SOC Team | Month 10 |
| Adversarial testing program | Security Team | Month 11 |
| Annual governance assessment | AI Governance Lead | Month 12 |
| Steady-state operations guide | AI Governance Lead | Month 12 |

---

## Control Implementation Priority Matrix

### Critical Path Controls

These controls should be implemented first as they enable other governance capabilities:

| Priority | Control | Dependency | Enables |
|----------|---------|------------|---------|
| 1 | 2.1 Managed Environments | None | All Zone 2-3 controls |
| 2 | 1.1 Restrict Publishing | 2.1 | Controlled agent deployment |
| 3 | 1.5 DLP and Labels | None | Data protection |
| 4 | 3.1 Agent Inventory | 1.1 | Monitoring, reporting |
| 5 | 1.7 Audit Logging | 2.1 | Compliance, eDiscovery |
| 6 | 2.8 Access Control | None | Segregation of duties |

### Regulatory Priority by Institution Type

**Broker-Dealers (FINRA/SEC):**

1. Control 2.12 (Supervision) — FINRA 3110
2. Control 1.7 (Audit Logging) — FINRA 4511, SEC 17a-4
3. Control 2.11 (Bias Testing) — FINRA 25-07
4. Control 3.3 (Compliance Reporting) — Examination readiness

**Banks (OCC/Fed):**

1. Control 2.6 (Model Risk Management) — OCC 2011-12, SR 11-7
2. Control 2.11 (Bias Testing) — Fair lending
3. Control 1.7 (Audit Logging) — Records requirements
4. Control 1.5 (DLP) — GLBA 501(b)

**Investment Advisers (SEC):**

1. Control 2.12 (Supervision) — Reg BI
2. Control 2.19 (AI Disclosure) — Client communication
3. Control 1.7 (Audit Logging) — SEC 17a-4
4. Control 3.1 (Agent Inventory) — Examination readiness

---

## Resource Planning

### Estimated Effort by Phase

| Phase | Power Platform Admin | Compliance | Security | AI Governance Lead |
|-------|---------------------|------------|----------|-------------------|
| Phase 0 | 40-60 hours | 20-30 hours | 10-20 hours | 60-80 hours |
| Phase 1 | 60-80 hours | 40-60 hours | 30-40 hours | 80-100 hours |
| Phase 2 | 40-60 hours | 30-40 hours | 60-80 hours | 60-80 hours |

### Ongoing Operations (Post-Implementation)

| Activity | Frequency | Estimated Effort |
|----------|-----------|------------------|
| Agent inventory review | Weekly | 2-4 hours |
| Compliance monitoring | Weekly | 4-8 hours |
| Governance committee | Monthly | 4-6 hours |
| Quarterly review | Quarterly | 8-16 hours |
| Annual assessment | Annual | 40-60 hours |

---

## Risk Factors and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Insufficient executive sponsorship | Delayed implementation | Obtain board-level commitment before Phase 0 |
| Resource constraints | Extended timeline | Prioritize critical path controls |
| Rapid agent proliferation | Governance gaps | Implement publishing controls early (1.1) |
| Microsoft platform changes | Playbook updates required | Monitor Microsoft announcements, budget for updates |
| Regulatory examination | Compliance gaps exposed | Prioritize controls for your regulatory profile |

---

## Governance Review Checkpoints

| Checkpoint | Timing | Focus | Participants |
|------------|--------|-------|--------------|
| Phase 0 Review | Week 8 | Foundation readiness | AI Gov Lead, PP Admin, Compliance |
| Phase 1 Midpoint | Month 4 | Zone 3 readiness | Governance Committee |
| Phase 1 Review | Month 6 | Production readiness | Governance Committee, Executive Sponsor |
| Phase 2 Midpoint | Month 9 | Advanced controls | Governance Committee |
| Annual Review | Month 12 | Full assessment | Governance Committee, Board |

---

## Next Steps

1. **Assess Current State** — Inventory existing agents and governance capabilities
2. **Assign Accountability** — Identify AI Governance Lead and key stakeholders
3. **Customize Timeline** — Adapt phases based on your organization's priorities
4. **Secure Resources** — Obtain budget and staffing commitments
5. **Begin Phase 0** — Start with governance structure and core controls

---

*FSI Agent Governance Framework v1.1 - January 2026*
