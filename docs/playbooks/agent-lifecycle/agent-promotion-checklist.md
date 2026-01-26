# Agent Promotion Checklist

Requirements and procedures for promoting agents between governance zones.

---

## Overview

Agents progress through governance zones as they mature from personal experimentation to enterprise production. This checklist ensures all requirements are met before zone promotion.

---

## Zone 1 to Zone 2 Promotion

### Trigger Conditions

Promotion to Zone 2 is required when:

- Agent will be shared with team members (beyond creator)
- Agent accesses internal business data
- Agent will be used for departmental workflows

### Pre-Promotion Requirements

#### Business Requirements

- [ ] Business justification documented
- [ ] Manager or department head approval obtained
- [ ] Data sources identified and approved
- [ ] User list defined

#### Technical Requirements

- [ ] Agent moved to Zone 2 environment (Managed Environment)
- [ ] Solution created for version control
- [ ] DLP policy compliance verified
- [ ] Authentication configured (Entra ID required)
- [ ] Sharing rules appropriate for Zone 2

#### Testing Requirements

- [ ] Functional testing completed
- [ ] User acceptance testing completed
- [ ] Security review completed (if accessing sensitive data)

#### Documentation Requirements

- [ ] Agent registered in inventory (Control 3.1)
- [ ] Agent metadata complete (owner, purpose, data sources)
- [ ] Incident response procedures documented
- [ ] User training materials prepared

### Approval Workflow

1. Creator completes checklist
2. Manager reviews and approves
3. Power Platform Admin verifies technical requirements
4. Compliance reviews (if applicable)
5. Agent enabled in Zone 2 environment

---

## Zone 2 to Zone 3 Promotion

### Trigger Conditions

Promotion to Zone 3 is required when:

- Agent will be customer-facing
- Agent accesses customer PII or financial data
- Agent makes decisions affecting customers
- Agent used in regulatory contexts

### Pre-Promotion Requirements

#### Business Requirements

- [ ] Detailed business case documented
- [ ] Executive sponsor identified
- [ ] Risk assessment completed (Control 2.6)
- [ ] Legal review completed (if customer-facing)
- [ ] Regulatory alignment confirmed

#### Governance Requirements

- [ ] Governance committee presentation scheduled
- [ ] Committee review materials prepared
- [ ] All committee member approvals obtained:
  - [ ] AI Governance Lead
  - [ ] Compliance Officer
  - [ ] CISO
  - [ ] General Counsel (if customer-facing)
  - [ ] Business Owner

#### Technical Requirements

- [ ] Agent migrated to Zone 3 managed environment
- [ ] 10-year audit retention configured
- [ ] Phishing-resistant MFA enabled (Control 1.11)
- [ ] Runtime protection enabled (Control 1.8)
- [ ] DLP policies at strictest level
- [ ] Sensitivity labels applied
- [ ] Change management process established

#### Testing Requirements

- [ ] Comprehensive functional testing completed
- [ ] Security penetration testing completed
- [ ] Bias and fairness testing completed (Control 2.11)
- [ ] Performance benchmarking completed
- [ ] Fallback scenario testing completed
- [ ] User acceptance testing with production-like data

#### Compliance Requirements

- [ ] Model risk assessment completed (Control 2.6)
- [ ] Supervisory procedures documented (Control 2.12)
- [ ] Disclosure requirements reviewed (Control 2.19)
- [ ] Records retention configured (Control 1.9)

#### Documentation Requirements

- [ ] Complete agent documentation package
- [ ] Incident response playbook
- [ ] Monitoring and alerting configured
- [ ] Training materials for operators
- [ ] User communication plan

### Approval Workflow

1. Business Owner completes requirements
2. AI Governance Lead validates readiness
3. Governance committee reviews package
4. Committee votes on approval
5. Post-approval implementation:
   - [ ] Change control ticket created
   - [ ] Phased deployment scheduled
   - [ ] Monitoring configured
   - [ ] Stakeholders notified

---

## Post-Promotion Activities

### Zone 2 Post-Promotion

- [ ] Update agent inventory with new zone
- [ ] Enable quarterly compliance reviews
- [ ] Configure monitoring dashboards
- [ ] Schedule first governance review

### Zone 3 Post-Promotion

- [ ] Update agent inventory with new zone
- [ ] Enable real-time monitoring
- [ ] Configure executive reporting
- [ ] Schedule monthly governance reviews
- [ ] Brief operations team
- [ ] Conduct post-deployment review (30 days)

---

## Promotion Denial Handling

If promotion is denied:

1. Document specific concerns from reviewers
2. Create remediation plan
3. Assign remediation owner and deadline
4. Re-submit for review when complete
5. Track in governance records

### Common Denial Reasons

| Reason | Typical Remediation |
|--------|---------------------|
| Incomplete testing | Complete required tests |
| Security concerns | Address findings, re-test |
| Documentation gaps | Complete missing documentation |
| Unclear business case | Strengthen justification |
| Data access concerns | Implement additional controls |

---

## Related Playbooks

- [Agent Inventory Entry](agent-inventory-entry.md)
- [Per-Agent Data Policy](per-agent-data-policy.md)
- [Agent Decommissioning](agent-decommissioning.md)

---

*Last Updated: January 2026*
*FSI Agent Governance Framework v1.2*
