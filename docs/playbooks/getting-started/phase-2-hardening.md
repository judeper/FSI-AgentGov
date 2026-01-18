# Phase 2: Hardening

Advanced governance phase for mature operations (6-12 months).

---

## Overview

Phase 2 implements advanced security controls, monitoring integration, and adversarial testing to achieve steady-state governance operations.

**Timeline:** 6-12 months (after Phase 1)
**Outcome:** Full control implementation, steady-state operations

---

## Quarter 3 (Months 7-9): Advanced Security

### Control 1.8: Runtime Protection

**Purpose:** Detect and respond to threats in real-time

**Steps:**

1. Enable Microsoft Defender for Cloud Apps
2. Configure Copilot Studio app connector
3. Create alert policies:
   - Unusual usage patterns
   - Data exfiltration attempts
   - Suspicious authentication
4. Configure automated responses

**Verification:**

- [ ] Connector configured
- [ ] Policies active
- [ ] Test alert fires correctly

### Control 1.6: DSPM for AI

**Purpose:** Discover and protect sensitive data in AI contexts

**Steps:**

1. Navigate to Microsoft Purview > Data Security Posture Management
2. Enable DSPM for AI
3. Configure sensitivity scanning
4. Review discovered data exposures
5. Remediate findings

**Verification:**

- [ ] DSPM enabled
- [ ] Scan results reviewed
- [ ] Remediation tracked

### Control 1.19: eDiscovery Configuration

**Purpose:** Enable legal hold and search for agent interactions

**Steps:**

1. Navigate to Microsoft Purview > eDiscovery
2. Create case template for AI agent investigations
3. Test search capabilities
4. Document procedures

**Verification:**

- [ ] Case template created
- [ ] Search finds agent interactions
- [ ] Procedures documented

### Control 1.22: Information Barriers (If Needed)

**Purpose:** Prevent information sharing between specific groups

**Steps:**

1. Identify barrier requirements
2. Configure segments in Entra
3. Create barrier policies
4. Test barrier enforcement

**Verification:**

- [ ] Segments defined
- [ ] Policies active
- [ ] Test confirms barriers work

---

## Quarter 4 (Months 10-12): Advanced Monitoring and Testing

### Control 3.9: Microsoft Sentinel Integration

**Purpose:** Centralized security monitoring and threat detection

**Steps:**

1. Navigate to Microsoft Sentinel workspace
2. Enable Power Platform connector
3. Create analytics rules:
   - Agent configuration changes
   - DLP violations
   - Unusual access patterns
   - High-risk activities
4. Configure workbooks for visualization
5. Set up automated response playbooks

**Verification:**

- [ ] Connector configured
- [ ] Analytics rules active
- [ ] Workbooks displaying data
- [ ] Test playbook executes

### Control 2.20: Adversarial Testing

**Purpose:** Proactively test agent resilience to attacks

**Steps:**

1. Document adversarial testing framework
2. Define test scenarios:
   - Prompt injection attempts
   - Data extraction attempts
   - Jailbreak attempts
   - Social engineering
3. Schedule regular testing (quarterly for Zone 3)
4. Track findings and remediation

**Verification:**

- [ ] Framework documented
- [ ] First test completed
- [ ] Findings tracked

### Control 3.10: Hallucination Feedback Loop

**Purpose:** Monitor and improve output accuracy

**Steps:**

1. Implement user feedback mechanism
2. Create logging for flagged responses
3. Establish review process
4. Track accuracy trends
5. Feed learnings into agent improvement

**Verification:**

- [ ] Feedback mechanism active
- [ ] Review process operational
- [ ] Trends tracked

### Control 2.11: Comprehensive Bias Testing

**Purpose:** Full fairness assessment program

**Steps:**

1. Document comprehensive testing approach
2. Define protected characteristics for testing
3. Create test datasets
4. Conduct quarterly assessments
5. Document and remediate findings

**Verification:**

- [ ] Testing program documented
- [ ] Quarterly schedule established
- [ ] Results tracked

---

## Annual Governance Review

### Full Framework Assessment

Conduct comprehensive review of all 60 controls:

- [ ] Each control assessed for implementation status
- [ ] Gaps identified and documented
- [ ] Remediation plans created
- [ ] Priority controls for next year identified

### Regulatory Alignment Review

- [ ] Review any new regulatory guidance
- [ ] Assess framework alignment
- [ ] Update mappings as needed
- [ ] Brief legal and compliance

### Technology Roadmap Review

- [ ] Review Microsoft platform updates
- [ ] Assess impact on governance
- [ ] Update playbooks for portal changes
- [ ] Plan for new capabilities

### Governance Effectiveness Assessment

- [ ] Review metrics and KPIs
- [ ] Assess control effectiveness
- [ ] Identify improvement opportunities
- [ ] Update governance procedures

---

## Steady-State Operations

### Ongoing Activities

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Agent inventory reconciliation | Weekly | AI Governance Lead |
| DLP policy review | Monthly | Power Platform Admin |
| Security posture review | Monthly | CISO |
| Governance committee meeting | Monthly | AI Governance Lead |
| Bias testing | Quarterly | AI Governance Lead |
| Adversarial testing | Quarterly | Security Team |
| Comprehensive governance review | Quarterly | Governance Committee |
| Annual framework assessment | Annual | Governance Committee |

### Operational Documentation

Create and maintain:

- [ ] Steady-state operations guide
- [ ] Runbooks for common tasks
- [ ] Escalation procedures
- [ ] On-call rotation (if applicable)

---

## Phase 2 Completion Checklist

### Advanced Security

- [ ] Runtime protection enabled
- [ ] DSPM for AI configured
- [ ] eDiscovery procedures documented
- [ ] Information barriers (if needed)

### Advanced Monitoring

- [ ] Sentinel integration complete
- [ ] Analytics rules active
- [ ] Response playbooks configured
- [ ] Hallucination feedback operational

### Advanced Testing

- [ ] Adversarial testing program established
- [ ] Comprehensive bias testing operational
- [ ] Quarterly testing schedule confirmed

### Steady-State Operations

- [ ] All 60 controls assessed
- [ ] Gaps documented with remediation plans
- [ ] Operations guide created
- [ ] Ongoing cadence established

---

## Success Criteria

Phase 2 is complete when:

1. Runtime protection is detecting threats
2. Sentinel integration provides centralized monitoring
3. Adversarial testing program is operational
4. All 60 controls have been assessed
5. Steady-state operations documentation is complete
6. Annual governance review has been conducted

---

## Continuous Improvement

After Phase 2, governance enters steady-state with focus on:

- Continuous monitoring and response
- Regular control testing and validation
- Platform updates and playbook maintenance
- Regulatory change management
- Ongoing training and awareness

---

*Last Updated: January 2026*
*FSI Agent Governance Framework v1.1*
