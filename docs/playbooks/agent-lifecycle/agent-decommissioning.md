# Agent Decommissioning

Procedures for securely retiring AI agents while maintaining compliance and audit trail.

---

## Overview

When an agent is no longer needed, it must be decommissioned following a controlled process that ensures data retention requirements are met and all stakeholders are notified.

---

## Decommissioning Triggers

| Trigger | Action |
|---------|--------|
| Business decision | Standard decommissioning |
| Replaced by new agent | Migration then decommissioning |
| Compliance violation | Immediate suspension, then decommissioning |
| Security incident | Emergency suspension, investigation, then decommissioning |
| Owner departure | Ownership transfer or decommissioning |
| Inactivity (>90 days) | Review for decommissioning |

---

## Decommissioning by Zone

### Zone 1 Decommissioning

**Approver:** Creator (self-service)

**Retention Requirements:** 30 days minimum (if any logs exist)

**Process:**

1. [ ] Document reason for retirement
2. [ ] Disable agent access
3. [ ] Wait 30 days for log retention
4. [ ] Delete agent from environment
5. [ ] Remove from inventory (if tracked)

---

### Zone 2 Decommissioning

**Approver:** Manager + Environment Owner

**Retention Requirements:** 1 year minimum

**Process:**

1. [ ] Document business justification for retirement
2. [ ] Obtain manager approval
3. [ ] Notify team members and users (2-week notice recommended)
4. [ ] Disable agent (do not delete yet)
5. [ ] Export conversation history (if required)
6. [ ] Verify audit logs are retained (1-year minimum)
7. [ ] Remove user access
8. [ ] Wait retention period
9. [ ] Delete agent from environment
10. [ ] Update inventory to show decommissioned status
11. [ ] Archive documentation

---

### Zone 3 Decommissioning

**Approver:** Governance Committee

**Retention Requirements:** 7-10 years (per regulatory requirements)

**Process:**

1. [ ] Document detailed business justification
2. [ ] Present to governance committee
3. [ ] Obtain committee approval:
   - [ ] AI Governance Lead
   - [ ] Compliance Officer
   - [ ] CISO
   - [ ] Business Owner
4. [ ] Notify all stakeholders (minimum 30-day notice)
5. [ ] Create transition plan (if replacing with new agent)
6. [ ] Disable agent in production
7. [ ] Complete data exports:
   - [ ] Full conversation history
   - [ ] Audit logs (entire retention period)
   - [ ] Configuration backup
   - [ ] Model/knowledge source documentation
8. [ ] Transfer data to long-term retention storage
9. [ ] Verify retention meets regulatory requirements
10. [ ] Remove user and system access
11. [ ] Preserve agent for retention period (disabled state)
12. [ ] Update inventory to show decommissioned
13. [ ] Archive all governance documentation
14. [ ] Schedule deletion after retention period expires

---

## Data Retention Requirements

| Data Type | Zone 1 | Zone 2 | Zone 3 |
|-----------|--------|--------|--------|
| Conversation logs | N/A | 1 year | 7-10 years |
| Audit trail | 30 days | 1 year | 7-10 years |
| Configuration | N/A | 1 year | 7 years |
| Approval records | N/A | 3 years | 7 years |
| Incident records | N/A | 3 years | 7 years |

### Regulatory Retention Guidelines

| Regulation | Requirement | Applies To |
|------------|-------------|------------|
| FINRA 4511 | 6 years + 1 year accessible | Broker-dealers |
| SEC 17a-4 | 6 years + 3 years accessible | SEC registrants |
| SOX 802 | 7 years | Public companies |
| GLBA | Per institution policy | All FSI |

---

## Stakeholder Notification Template

```
Subject: [Agent Name] Decommissioning Notice

Dear [Stakeholder],

This notice informs you that [Agent Name] will be decommissioned on [Date].

REASON: [Brief explanation]

TIMELINE:
- [Date]: Agent disabled (read-only)
- [Date]: User access removed
- [Date]: Agent deleted

IMPACT:
- [Description of impact on users/workflows]

ALTERNATIVES:
- [Replacement agent, if applicable]
- [Alternative processes]

QUESTIONS:
Contact [Name] at [Email] for questions.

[AI Governance Lead]
[Date]
```

---

## Emergency Decommissioning

For security incidents or compliance violations requiring immediate action:

1. **Immediate Actions (within 1 hour):**
   - [ ] Disable agent access
   - [ ] Notify CISO and Compliance Officer
   - [ ] Preserve all logs and evidence
   - [ ] Document reason for emergency action

2. **Within 24 Hours:**
   - [ ] Notify AI Governance Lead
   - [ ] Brief governance committee
   - [ ] Complete incident report
   - [ ] Assess data exposure (if any)

3. **Within 7 Days:**
   - [ ] Complete root cause analysis
   - [ ] Document lessons learned
   - [ ] Update governance procedures (if needed)
   - [ ] Decide on permanent decommissioning vs. remediation

---

## Decommissioning Checklist Summary

### Pre-Decommissioning

- [ ] Business justification documented
- [ ] Approvals obtained (per zone requirements)
- [ ] Stakeholders notified
- [ ] Transition plan created (if applicable)

### Decommissioning Execution

- [ ] Agent disabled
- [ ] Data exported and preserved
- [ ] User access removed
- [ ] Systems integrations disconnected

### Post-Decommissioning

- [ ] Inventory updated
- [ ] Documentation archived
- [ ] Retention compliance verified
- [ ] Final review completed

---

## Related Playbooks

- [Agent Inventory Entry](agent-inventory-entry.md)
- [Agent Promotion Checklist](agent-promotion-checklist.md)
- [AI Incident Response Playbook](../incident-and-risk/ai-incident-response-playbook.md)

---

*Last Updated: January 2026*
*FSI Agent Governance Framework v1.2*
