# AI Incident Response Playbook

**Status:** January 2026 - FSI-AgentGov v1.0
**Related Controls:** 3.4 (Incident Reporting), 1.21 (Adversarial Input), 3.10 (Hallucination Feedback)

---

## Purpose

This playbook provides structured response procedures for AI agent-specific incidents in financial services environments. It extends general incident response with AI-specific categories, evidence collection requirements, and regulatory notification triggers.

---

## Incident Categories

### Category 1: Hallucination / Data Quality

**Description:** Agent provides factually incorrect, fabricated, or misleading information.

**Severity Triggers:**

| Severity | Criteria | Example |
|----------|----------|---------|
| Critical | Financial advice error; customer harm likely | Wrong interest rate affecting loan decision |
| High | Significant misinformation; potential customer impact | Incorrect product features |
| Medium | Minor inaccuracy; limited impact | Typo in general information |
| Low | Cosmetic issue | Formatting or style issues |

**Response Procedure:**

```plaintext
T+0:00 - Incident Detected
├── Capture conversation and response
├── Classify severity using criteria above
├── If Critical/High: Notify AI Governance Lead immediately
└── If customer-facing: Consider temporary agent suspension

T+0:15 - Initial Assessment
├── Identify affected users
├── Determine source of incorrect information
├── Check if issue is systemic (multiple users) or isolated
└── Document findings

T+1:00 - Containment
├── If systemic: Disable agent or problematic feature
├── If isolated: Flag user session for follow-up
├── Prepare customer communication (if needed)
└── Notify compliance if regulatory impact

T+4:00 - Investigation
├── Review knowledge sources (per Control 2.16)
├── Check citation logging (per Control 3.4)
├── Analyze prompt configuration
├── Determine root cause

T+24:00 - Remediation
├── Update knowledge source if needed
├── Modify agent configuration
├── Test fix in non-production
├── Deploy fix with change control

T+48:00 - Verification
├── Monitor for recurrence
├── Verify fix effectiveness
├── Close incident with documentation
└── Schedule post-incident review
```

**Evidence to Collect:**

- [ ] Full conversation transcript
- [ ] Agent configuration at time of incident
- [ ] Knowledge sources cited
- [ ] User information (anonymized if needed)
- [ ] Timestamp and session details
- [ ] Screenshots of incorrect output

---

### Category 2: Prompt Injection / Adversarial Attack

**Description:** Attempted or successful manipulation of agent behavior through malicious inputs.

**Severity Triggers:**

| Severity | Criteria | Example |
|----------|----------|---------|
| Critical | Successful jailbreak; safety bypass achieved | Agent disclosed restricted information |
| High | Partial bypass; suspicious behavior observed | Agent acknowledged injection attempt |
| Medium | Detected attempt; no bypass | Blocked injection logged |
| Low | False positive; legitimate use | Business term triggered detection |

**Response Procedure:**

```plaintext
T+0:00 - Detection Alert
├── Review detection details from Control 1.21
├── Classify as successful attack vs. blocked attempt
├── If successful: IMMEDIATELY escalate to Security Operations
└── Preserve all evidence

T+0:05 - Immediate Containment (if successful)
├── Suspend user session (if identifiable)
├── Consider agent suspension for Zone 3
├── Engage Security Operations Center
└── Do NOT delete evidence

T+0:30 - Security Assessment
├── Determine scope of compromise
├── Identify data accessed or disclosed
├── Check for lateral movement indicators
├── Assess regulatory notification requirements

T+1:00 - Notification
├── If data breach: Engage legal and compliance
├── Notify CISO/CCO per escalation matrix
├── Prepare regulatory notification if required
└── Document all notifications

T+24:00 - Forensic Investigation
├── Collect all audit logs
├── Analyze attack pattern
├── Check for similar attempts across agents
├── Determine if attack was targeted

T+48:00+ - Remediation
├── Update detection patterns
├── Strengthen agent guardrails
├── Implement additional controls
├── Conduct red team exercise to validate
```

**Evidence to Collect:**

- [ ] Full attack input/output
- [ ] Audit logs surrounding incident
- [ ] User identity information
- [ ] IP address and session details
- [ ] Detection alert details
- [ ] Agent configuration
- [ ] Any data accessed or disclosed

---

### Category 3: Data Leakage / Privacy Breach

**Description:** Agent disclosed sensitive information inappropriately.

**Severity Triggers:**

| Severity | Criteria | Example |
|----------|----------|---------|
| Critical | Customer PII/NPI exposed to unauthorized party | Another customer's account details shown |
| High | Internal confidential data disclosed | Employee information visible |
| Medium | Potentially sensitive data; limited exposure | Internal URL exposed |
| Low | Minor disclosure; no sensitive data | System metadata visible |

**Response Procedure:**

```plaintext
T+0:00 - Detection
├── Identify what data was exposed
├── Determine who received the data
├── If customer data: CRITICAL - immediate escalation
└── Preserve evidence immediately

T+0:05 - Containment
├── Suspend agent immediately
├── Revoke access to knowledge sources
├── Block additional queries to affected areas
└── Notify Privacy Officer

T+0:30 - Scope Assessment
├── Identify all affected individuals
├── Determine data elements exposed
├── Assess regulatory notification triggers
├── Check for ongoing exposure

T+2:00 - Regulatory Assessment
├── GLBA notification requirements (72 hours)
├── State breach notification laws
├── FINRA/SEC notification if applicable
├── Document assessment and decisions

T+24:00 - Notification Preparation
├── Prepare affected individual notifications
├── Draft regulatory notifications
├── Coordinate with legal counsel
├── Obtain compliance approval

T+72:00 - Notifications (if required)
├── Send customer notifications
├── File regulatory notifications
├── Document all notifications
└── Begin remediation

Ongoing - Remediation
├── Fix root cause
├── Implement additional controls
├── Conduct post-incident review
├── Update procedures as needed
```

**Evidence to Collect:**

- [ ] Exact data elements disclosed
- [ ] Recipient information
- [ ] Full conversation context
- [ ] Knowledge source configuration
- [ ] Access control settings
- [ ] DLP policy configuration at time

---

### Category 4: Bias / Fairness Violation

**Description:** Agent demonstrated discriminatory behavior or unfair recommendations.

**Severity Triggers:**

| Severity | Criteria | Example |
|----------|----------|---------|
| Critical | Clear discriminatory outcome; regulatory violation | Loan denial based on protected class |
| High | Potential bias pattern; investigation needed | Recommendation disparity observed |
| Medium | Isolated concern; may be coincidental | Single user complaint of unfairness |
| Low | Edge case; likely not bias | Unusual recommendation with clear rationale |

**Response Procedure:**

```plaintext
T+0:00 - Report Received
├── Document specific concern
├── Gather relevant interactions
├── Classify initial severity
└── Notify AI Governance Lead

T+4:00 - Statistical Analysis
├── Analyze recommendation patterns
├── Compare outcomes across demographic groups
├── Review conflict of interest test results (Control 2.18)
└── Engage Model Risk Management

T+24:00 - Compliance Assessment
├── Evaluate against fair lending requirements
├── Check for Reg BI compliance
├── Review FINRA 25-07 alignment
└── Document findings

If bias confirmed:
├── T+48:00 - Suspend affected functionality
├── T+72:00 - Conduct comprehensive bias audit
├── T+1 week - Remediate and validate
└── T+2 weeks - Implement ongoing monitoring

If bias not confirmed:
├── Document analysis methodology
├── Archive evidence
├── Consider enhanced monitoring
└── Close incident
```

**Evidence to Collect:**

- [ ] Interactions exhibiting potential bias
- [ ] Statistical analysis of outcomes
- [ ] Agent configuration and prompts
- [ ] Training data characteristics (if applicable)
- [ ] Comparison population data
- [ ] Previous bias test results

---

## Regulatory Notification Requirements

### Notification Triggers

| Regulation | Trigger | Timeline | Recipient |
|------------|---------|----------|-----------|
| **GLBA 501(b)** | Customer NPI breach | 72 hours | Affected customers |
| **State Breach Laws** | PII exposure | Varies (24-72 hours) | State AG, affected individuals |
| **FINRA 4530** | Significant security incident | Prompt | FINRA |
| **SEC Reg S-P** | Customer information breach | Reasonable time | SEC |
| **OCC** | Significant incident (banks) | Prompt | Primary regulator |

### Notification Decision Matrix

```
Is customer data involved?
├── No → Document internally only (unless material)
└── Yes → Was it exposed to unauthorized party?
    ├── No → Document, monitor, no notification required
    └── Yes → Notification likely required
        ├── How many affected?
        │   ├── <500 → State laws only (typically)
        │   └── >=500 → State + federal notification
        └── What data types?
            ├── Financial account info → GLBA applies
            ├── PII only → State breach laws
            └── Both → Most stringent requirements apply
```

---

## Escalation Matrix

| Severity | Initial Response | Escalation Path | SLA |
|----------|-----------------|-----------------|-----|
| **Critical** | SOC + AI Governance | → CISO → CCO → CEO | 15 min |
| **High** | AI Governance Lead | → Director → VP | 1 hour |
| **Medium** | On-call analyst | → Manager → AI Governance | 4 hours |
| **Low** | Standard queue | → Team Lead | 24 hours |

---

## Post-Incident Requirements

### Incident Review Checklist

```markdown
# AI Incident Post-Incident Review

## Incident Summary
- **Incident ID:** [ID]
- **Category:** [Category]
- **Severity:** [Level]
- **Duration:** [Start to Close]
- **Affected Users:** [Count]

## Timeline Review
- Detection time: [How long to detect]
- Response time: [How long to respond]
- Resolution time: [How long to fix]
- Total duration: [End-to-end]

## Root Cause Analysis
- Primary cause: [Description]
- Contributing factors: [List]
- Prevention gaps: [What failed]

## Lessons Learned
1. [Lesson 1]
2. [Lesson 2]

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| [Action] | [Name] | [Date] | [Status] |

## Process Improvements
- [ ] Update playbook
- [ ] Enhance detection
- [ ] Improve training
- [ ] Modify controls

## Sign-off
- Incident Manager: _______ Date: _____
- AI Governance Lead: _______ Date: _____
- Compliance (if regulatory): _______ Date: _____
```

### Documentation Retention

| Document Type | Retention Period | Storage Location |
|---------------|------------------|------------------|
| Incident report | 7 years | Compliance archive |
| Evidence package | 7 years | Secure storage |
| Notification records | 7 years | Legal hold |
| Post-incident review | 7 years | Governance repository |

---

## Integration with Framework Controls

| Control | Integration Point |
|---------|-------------------|
| [1.7 Audit Logging](../../reference/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Evidence source |
| [1.21 Adversarial Input](../../reference/pillar-1-security/1.21-adversarial-input-logging.md) | Attack detection |
| [3.4 Incident Reporting](../../reference/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Workflow integration |
| [3.10 Hallucination Feedback](../../reference/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Quality incident source |

---

*FSI Agent Governance Framework v1.0 - January 2026*
