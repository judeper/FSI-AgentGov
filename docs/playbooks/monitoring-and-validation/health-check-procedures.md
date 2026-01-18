# Health Check Procedures

Regular validation checks to ensure AI agent governance controls are operating effectively.

---

## Overview

Health checks provide ongoing assurance that governance controls are functioning as designed. These procedures should be run at scheduled intervals and after significant changes.

---

## Health Check Schedule

| Check Type | Frequency | Owner | Duration |
|------------|-----------|-------|----------|
| Daily automated checks | Daily | Automated | N/A |
| Weekly operational review | Weekly | Power Platform Admin | 1-2 hours |
| Monthly governance review | Monthly | AI Governance Lead | 2-4 hours |
| Quarterly deep dive | Quarterly | Governance Committee | Half day |

---

## Daily Automated Checks

Configure these checks to run automatically and alert on failures.

### Agent Availability

- [ ] All Zone 3 agents responding
- [ ] Response times within SLA
- [ ] Error rates below threshold

### Security Monitoring

- [ ] Audit logging active
- [ ] DLP policies enforcing
- [ ] No unauthorized connector usage
- [ ] No security alerts unacknowledged

### Data Flow

- [ ] Backup jobs completing
- [ ] Replication healthy (if applicable)
- [ ] Storage utilization within limits

---

## Weekly Operational Review

### Agent Health

| Check | Control | Procedure | Expected Result |
|-------|---------|-----------|-----------------|
| Agent inventory accuracy | 3.1 | Compare PPAC agent list to inventory | 100% match |
| DLP violations | 1.5 | Review Purview DLP reports | Violations addressed |
| Orphaned agents | 3.6 | Run orphan detection query | Zero new orphans |
| Usage anomalies | 3.2 | Review usage analytics | No unexplained spikes |

### Environment Health

| Check | Control | Procedure | Expected Result |
|-------|---------|-----------|-----------------|
| Managed Environment status | 2.1 | Verify all Zone 2-3 environments enabled | All enabled |
| Environment group rules | 2.2 | Verify rules unchanged | No unauthorized changes |
| Connector policies | 1.4 | Review connector policy violations | Zero violations |
| Sharing settings | 1.1 | Verify sharing restrictions in place | Settings correct |

### Access Health

| Check | Control | Procedure | Expected Result |
|-------|---------|-----------|-----------------|
| Admin role assignments | 1.18 | Review admin role holders | Expected list |
| Service account status | 2.8 | Verify service accounts active/inactive | Expected state |
| Conditional access | 1.11 | Verify policies active | All policies active |

---

## Monthly Governance Review

### Inventory Reconciliation

1. Export current agent inventory from PPAC
2. Compare to governance registry
3. Investigate discrepancies:
   - Agents in PPAC not in registry
   - Agents in registry not in PPAC
   - Metadata mismatches
4. Update records as needed

### Policy Effectiveness

| Policy Type | Review Procedure | Success Criteria |
|-------------|------------------|------------------|
| DLP policies | Review violation trends | Decreasing or stable |
| Sharing policies | Review sharing events | Only authorized sharing |
| Channel policies | Review channel usage | Only approved channels |

### Compliance Verification

- [ ] Audit logs accessible for required period
- [ ] Retention policies enforced
- [ ] Access reviews completed on schedule
- [ ] Training completion current

### Change Review

- [ ] All changes followed change management process
- [ ] No unauthorized changes detected
- [ ] Rollbacks documented and analyzed
- [ ] Post-implementation reviews completed

---

## Quarterly Deep Dive

### Comprehensive Control Testing

Test each critical control end-to-end:

#### Control 1.1: Publishing Restrictions

1. Attempt to publish agent without authorization
2. Verify rejection
3. Document test result

#### Control 1.5: DLP Policies

1. Attempt to send restricted data via agent
2. Verify DLP blocks transmission
3. Verify audit event created
4. Document test result

#### Control 1.7: Audit Logging

1. Perform test action (e.g., agent access)
2. Search for event in Purview Audit
3. Verify event details correct
4. Document test result

#### Control 2.1: Managed Environments

1. Verify all Zone 2-3 environments enabled
2. Test that environment features work
3. Document test result

#### Control 2.8: Segregation of Duties

1. Review admin role assignments
2. Verify no single person has conflicting roles
3. Document test result

### Bias and Fairness Review (Zone 3)

- [ ] Review bias testing results from past quarter
- [ ] Identify any concerning patterns
- [ ] Document remediation actions taken
- [ ] Plan next bias testing cycle

### Incident Review

- [ ] Review all incidents from past quarter
- [ ] Verify root cause analyses completed
- [ ] Verify remediation actions implemented
- [ ] Identify trends or patterns
- [ ] Update procedures as needed

---

## Health Check Report Template

```
GOVERNANCE HEALTH CHECK REPORT
Period: [Date Range]
Completed By: [Name]
Date: [Date]

EXECUTIVE SUMMARY
Overall Health: [Green/Yellow/Red]
Critical Issues: [Count]
Open Remediation Items: [Count]

AGENT HEALTH
Total Agents: [Count by zone]
Availability: [%]
Performance: [Within SLA/Below SLA]
Orphaned Agents: [Count]

CONTROL EFFECTIVENESS
| Control | Status | Notes |
|---------|--------|-------|
| 1.1 Publishing | [Pass/Fail] | [Notes] |
| 1.5 DLP | [Pass/Fail] | [Notes] |
| [Continue for all tested controls] |

INCIDENTS
Incidents This Period: [Count]
Resolved: [Count]
Open: [Count]

COMPLIANCE STATUS
Audit Log Retention: [Compliant/Non-compliant]
Access Reviews: [On schedule/Behind]
Training: [% complete]

ISSUES AND REMEDIATION
| Issue | Priority | Owner | Due Date |
|-------|----------|-------|----------|
| [Issue] | [High/Medium/Low] | [Name] | [Date] |

RECOMMENDATIONS
1. [Recommendation]
2. [Recommendation]

Reviewed By: _________________ Date: _________
AI Governance Lead
```

---

## Remediation Tracking

### Issue Severity Levels

| Severity | Definition | Remediation Timeline |
|----------|------------|---------------------|
| Critical | Control failure affecting production or customer data | 24 hours |
| High | Control weakness with potential impact | 7 days |
| Medium | Control gap with limited impact | 30 days |
| Low | Minor improvement opportunity | 90 days |

### Remediation Workflow

1. Document issue and assign severity
2. Assign remediation owner
3. Define remediation plan
4. Track progress
5. Verify remediation complete
6. Close issue with evidence

---

## Related Playbooks

- [Real-time Compliance Dashboard](real-time-compliance-dashboard.md)
- [Scope Creep Detection](scope-creep-detection.md)
- [Purview Audit Query Pack](purview-audit-query-pack.md)

---

*Last Updated: January 2026*
*FSI Agent Governance Framework v1.1*
