# Phase 1: Minimal Viable Controls

Production readiness phase for enabling Zone 3 governance (2-6 months).

---

## Overview

Phase 1 implements the controls needed to support production agents in Zone 3, including comprehensive audit, access controls, supervision, and reporting.

**Timeline:** 2-6 months (after Phase 0)
**Outcome:** Zone 3 governance operational, first production agents deployed

---

## Month 2: Access and Segregation

### Control 2.8: Segregation of Duties

**Purpose:** Prevent single individuals from having conflicting roles

**Steps:**

1. Document required separation between roles:
   - Agent developer vs. production deployer
   - Compliance reviewer vs. agent owner
   - Admin vs. auditor
2. Review current role assignments
3. Remediate any conflicts
4. Configure role-based access in PPAC

**Verification:**

- [ ] Role matrix documented
- [ ] No conflicting assignments
- [ ] Access restrictions enforced

### Control 1.18: Application-Level RBAC

**Purpose:** Implement role-based access control for administrative functions

**Steps:**

1. Review PPAC admin roles
2. Assign minimum necessary permissions
3. Document role assignments
4. Configure access reviews

**Verification:**

- [ ] Admin roles documented
- [ ] Principle of least privilege applied

### Control 1.11: Conditional Access

**Purpose:** Enforce strong authentication for Zone 3 access

**Steps:**

1. Navigate to Microsoft Entra admin center
2. Create Conditional Access policy for Zone 3 environments
3. Configure:
   - Require phishing-resistant MFA
   - Block legacy authentication
   - Require compliant devices (optional)
4. Apply to Zone 3 admin groups

**Verification:**

- [ ] Policy active
- [ ] Test access requires MFA

---

## Month 3: Reporting and Monitoring

### Control 3.2: Usage Analytics

**Purpose:** Monitor agent usage patterns

**Steps:**

1. Access Power Platform analytics
2. Configure usage reports
3. Create monitoring dashboard
4. Set up anomaly alerts

**Verification:**

- [ ] Dashboard accessible
- [ ] Reports generating

### Control 3.3: Compliance Reporting

**Purpose:** Generate regular compliance reports

**Steps:**

1. Define reporting requirements
2. Create report templates
3. Assign report owners
4. Schedule report generation

**Verification:**

- [ ] Report template created
- [ ] First report generated

### Control 3.7: PPAC Security Posture

**Purpose:** Monitor and improve security posture

**Steps:**

1. Navigate to PPAC > Security
2. Review security recommendations
3. Create remediation plan for gaps
4. Track improvements

**Verification:**

- [ ] Security score reviewed
- [ ] Improvement plan documented

### Control 3.6: Orphaned Agent Detection

**Purpose:** Identify agents without active owners

**Steps:**

1. Create detection query/process
2. Document remediation workflow
3. Schedule regular detection runs
4. Assign ownership for remediation

**Verification:**

- [ ] Detection process running
- [ ] Orphans identified and remediated

---

## Month 4: Zone 3 Governance

### Governance Committee

**Purpose:** Establish formal approval body for Zone 3 agents

**Steps:**

1. Finalize committee charter
2. Appoint committee members:
   - AI Governance Lead (Chair)
   - Compliance Officer
   - CISO
   - General Counsel
   - CRO (if applicable)
3. Schedule monthly meetings
4. Create meeting templates

**Verification:**

- [ ] Charter approved
- [ ] Members appointed
- [ ] First meeting scheduled

### Zone 3 Approval Workflow

**Purpose:** Document formal approval process

**Steps:**

1. Document approval requirements
2. Create approval request template
3. Define routing rules
4. Configure workflow (Power Automate or manual)

**Verification:**

- [ ] Process documented
- [ ] Template available

### Control 1.9: 10-Year Retention

**Purpose:** Configure retention for Zone 3 regulatory requirements

**Steps:**

1. Navigate to Microsoft Purview
2. Create retention policy for Zone 3
3. Configure 10-year retention
4. Apply to Zone 3 environments

**Verification:**

- [ ] Policy created
- [ ] Applied to Zone 3

### Control 2.12: Supervision Controls

**Purpose:** Document supervisory procedures per FINRA 3110

**Steps:**

1. Document supervision requirements
2. Assign supervisory responsibilities
3. Create supervision checklist
4. Schedule supervision activities

**Verification:**

- [ ] Procedures documented
- [ ] Responsibilities assigned

---

## Month 5: Testing and Validation

### Control 2.5: Testing Procedures

**Purpose:** Establish testing requirements for Zone 3 agents

**Steps:**

1. Document testing requirements by zone
2. Create test plan template
3. Define security testing requirements
4. Establish bias testing process

**Verification:**

- [ ] Test plan template created
- [ ] Requirements documented

### Control 2.11: Bias Testing

**Purpose:** Establish fairness assessment process

**Steps:**

1. Document bias testing approach
2. Define testing scenarios
3. Create documentation template
4. Schedule quarterly testing

**Verification:**

- [ ] Process documented
- [ ] First test scheduled

### Control 2.6: Model Risk Assessment

**Purpose:** Align with OCC 2011-12 / SR 11-7 guidance

**Steps:**

1. Document model risk framework
2. Create risk assessment template
3. Define validation requirements
4. Assign risk management responsibilities

**Verification:**

- [ ] Framework documented
- [ ] Template available

---

## Month 6: First Production Agents

### Deploy First Zone 3 Agent

**Steps:**

1. Identify candidate agent for Zone 3
2. Complete risk assessment
3. Present to governance committee
4. Obtain all required approvals
5. Deploy following change management
6. Enable monitoring

### Post-Deployment Review

After 30 days, conduct review:

- [ ] Agent performing as expected
- [ ] No incidents or issues
- [ ] Monitoring effective
- [ ] Lessons learned documented

### First Quarterly Governance Review

Conduct comprehensive review:

- [ ] All Phase 1 controls implemented
- [ ] Issues identified and tracked
- [ ] Phase 2 priorities defined
- [ ] Governance committee briefed

---

## Phase 1 Completion Checklist

### Access and Segregation

- [ ] Segregation of duties implemented
- [ ] RBAC configured
- [ ] Conditional Access policies active

### Reporting and Monitoring

- [ ] Usage analytics operational
- [ ] Compliance reporting established
- [ ] Security posture monitored
- [ ] Orphaned agent detection running

### Zone 3 Governance

- [ ] Governance committee operational
- [ ] Approval workflow documented
- [ ] 10-year retention configured
- [ ] Supervision procedures documented

### Testing and Validation

- [ ] Testing procedures established
- [ ] Bias testing process defined
- [ ] Model risk framework documented

### Production Readiness

- [ ] At least one Zone 3 agent deployed
- [ ] Post-deployment review completed
- [ ] Quarterly governance review conducted

---

## Success Criteria

Phase 1 is complete when:

1. Governance committee is operational with documented procedures
2. At least one Zone 3 agent is deployed with full governance
3. Comprehensive audit logging with 10-year retention is active
4. Compliance reporting process is established
5. First quarterly governance review is completed

---

## Next Phase

Proceed to [Phase 2: Hardening](phase-2-hardening.md) to implement advanced security and monitoring capabilities.

---

*Last Updated: January 2026*
*FSI Agent Governance Framework v1.1*
