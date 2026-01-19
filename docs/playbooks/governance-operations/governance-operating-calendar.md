# Governance Operating Calendar

## Overview

This template provides a consolidated operational calendar for AI agent governance tasks. Control tasks from the FSI Agent Governance Framework are organized by cadence (weekly, monthly, quarterly, annually) to ensure consistent execution and regulatory compliance.

---

## Purpose

The Governance Operating Calendar:

- **Consolidates** tasks from 60 controls into a single operational view
- **Prevents gaps** by scheduling recurring governance activities
- **Supports audit** by documenting when tasks should be performed
- **Enables planning** for resource allocation and scheduling
- **Aligns with regulatory** examination expectations

---

## How to Use This Template

1. **Customize** the calendar to your organization's structure
2. **Assign owners** to each task category
3. **Configure reminders** in your calendar system
4. **Track completion** using the verification checklists
5. **Review quarterly** to adjust timing as needed

---

## Weekly Tasks

### Security Operations (Every Week)

| Task | Control Reference | Owner | Day | Duration |
|------|-------------------|-------|-----|----------|
| Shadow agent sweep | [1.1](../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md), [3.6](../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Platform Admin | Monday | 1 hour |
| DLP incident triage | [1.5](../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Security Analyst | Daily | 30 min |
| High-risk prompt review | [1.10](../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | Compliance | Wednesday | 2 hours |
| Adversarial input log review | [1.21](../../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Security Analyst | Friday | 1 hour |
| Step-up auth failure review | [1.23](../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | Security Admin | Daily | 30 min |

### Monitoring Tasks (Every Week)

| Task | Control Reference | Owner | Day | Duration |
|------|-------------------|-------|-----|----------|
| Agent performance dashboard review | [2.9](../../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | AI Governance Lead | Monday | 30 min |
| Copilot usage analytics review | [4.7](../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md), [3.2](../../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | M365 Admin | Wednesday | 30 min |
| Incident queue triage | [3.4](../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | AI Governance Lead | Daily | 30 min |
| Hallucination feedback review | [3.10](../../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | QA Lead | Friday | 1 hour |

### Weekly Verification Checklist

```markdown
# Weekly Governance Checklist - Week of [Date]

## Security Operations
- [ ] Shadow agent sweep completed
- [ ] DLP incidents triaged (count: ____)
- [ ] High-risk prompts reviewed (count: ____)
- [ ] Adversarial inputs analyzed (count: ____)
- [ ] Step-up auth failures investigated (count: ____)

## Monitoring
- [ ] Agent performance reviewed
- [ ] Usage analytics reviewed
- [ ] Incident queue current
- [ ] Hallucination feedback processed

## Notes/Issues
[Document any issues requiring escalation]

Completed by: _________________ Date: _________
```

---

## Monthly Tasks

### Access and Permission Reviews

| Task | Control Reference | Owner | Week | Duration |
|------|-------------------|-------|------|----------|
| Plugin permission audit | [1.4](../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | Platform Admin | Week 1 | 2 hours |
| Sensitivity label drift review | [1.5](../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Compliance | Week 1 | 2 hours |
| Service principal access review | [1.18](../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | Security Admin | Week 2 | 2 hours |
| Environment security group audit | [2.1](../../controls/pillar-2-management/2.1-managed-environments.md) | Platform Admin | Week 2 | 1 hour |
| SharePoint site permission scan | [1.3](../../controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md), [4.2](../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | SharePoint Admin | Week 3 | 3 hours |

### Compliance Activities

| Task | Control Reference | Owner | Week | Duration |
|------|-------------------|-------|------|----------|
| Audit log retention verification | [1.7](../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Compliance | Week 1 | 1 hour |
| Agent inventory reconciliation | [3.1](../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | AI Governance Lead | Week 2 | 2 hours |
| Training completion tracking | [2.14](../../controls/pillar-2-management/2.14-training-and-awareness-program.md) | HR/Training | Week 3 | 1 hour |
| Documentation currency check | [2.13](../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | AI Governance Lead | Week 4 | 2 hours |

### Technical Maintenance

| Task | Control Reference | Owner | Week | Duration |
|------|-------------------|-------|------|----------|
| DLP policy effectiveness review | [1.5](../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Security Analyst | Week 1 | 2 hours |
| Conditional Access policy review | [1.11](../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Security Admin | Week 2 | 2 hours |
| Agent versioning audit | [2.6](../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | AI Governance Lead | Week 3 | 2 hours |
| Connector policy validation | [1.4](../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | Platform Admin | Week 4 | 2 hours |

### Monthly Verification Checklist

```markdown
# Monthly Governance Checklist - [Month Year]

## Access Reviews
- [ ] Plugin permissions audited
- [ ] Sensitivity label drift addressed
- [ ] Service principal access reviewed
- [ ] Environment security groups validated
- [ ] SharePoint site permissions scanned

## Compliance
- [ ] Audit log retention verified
- [ ] Agent inventory reconciled (total: ____)
- [ ] Training completion tracked (% compliant: ____)
- [ ] Documentation currency verified

## Technical
- [ ] DLP policy effectiveness reviewed
- [ ] Conditional Access policies reviewed
- [ ] Agent versions audited
- [ ] Connector policies validated

## Metrics Summary
| Metric | This Month | Last Month | Trend |
|--------|------------|------------|-------|
| Active agents | | | |
| DLP incidents | | | |
| Step-up auth events | | | |
| Hallucination reports | | | |

## Issues Requiring Escalation
[Document issues for governance committee]

Completed by: _________________ Date: _________
AI Governance Lead approval: _________________ Date: _________
```

---

## Quarterly Tasks

### Governance Reviews

| Task | Control Reference | Owner | Duration |
|------|-------------------|-------|----------|
| Full agent inventory audit | [3.1](../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | AI Governance Lead | 4 hours |
| Zone classification validation | [Zones Guide](../../framework/zones-and-tiers.md) | AI Governance Lead | 2 hours |
| Orphaned agent cleanup | [3.6](../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Platform Admin | 3 hours |
| Governance maturity assessment | [Lifecycle](../../framework/agent-lifecycle.md) | AI Governance Lead | 4 hours |

### Risk and Compliance

| Task | Control Reference | Owner | Duration |
|------|-------------------|-------|----------|
| Bias/fairness regression testing | [2.11](../../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | QA/Compliance | 6 hours |
| Model risk review (Zone 3 agents) | [2.6](../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Risk | 4 hours |
| Adversarial red team exercise | [2.20](../../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Security | 8 hours |
| Information barrier validation | [1.22](../../controls/pillar-1-security/1.22-information-barriers.md) | Compliance | 2 hours |

### Access Reviews

| Task | Control Reference | Owner | Duration |
|------|-------------------|-------|----------|
| PIM role review | [1.18](../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | Security Admin | 3 hours |
| RBAC role assignment review | [1.18](../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | Platform Admin | 4 hours |
| Site access certification | [4.2](../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | SharePoint Admin | 4 hours |
| External user access review | [4.4](../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md) | SharePoint Admin | 2 hours |

### Testing and Validation

| Task | Control Reference | Owner | Duration |
|------|-------------------|-------|----------|
| 17a-4 sample restore test | [1.9](../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Compliance | 3 hours |
| DR/BC tabletop exercise | [2.4](../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) | Platform Admin | 4 hours |
| Incident response drill | [3.4](../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | AI Governance Lead | 2 hours |
| eDiscovery search test | [1.19](../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | Legal/Compliance | 2 hours |

### Quarterly Verification Checklist

```markdown
# Quarterly Governance Review - Q[X] [Year]

## Governance Reviews
- [ ] Agent inventory audit completed (total agents: ____)
- [ ] Zone classifications validated (changes: ____)
- [ ] Orphaned agents remediated (count: ____)
- [ ] Maturity assessment completed (score: ____/5)

## Risk and Compliance
- [ ] Bias testing completed for Zone 3 agents
  - Agents tested: ____
  - Issues found: ____
  - Issues remediated: ____
- [ ] Model risk review completed
- [ ] Red team exercise conducted
  - Critical findings: ____
  - High findings: ____
  - Remediation status: ____
- [ ] Information barriers validated

## Access Reviews
- [ ] PIM roles reviewed
- [ ] RBAC assignments reviewed
- [ ] Site access certified
- [ ] External users reviewed

## Testing
- [ ] 17a-4 restore test successful
- [ ] DR/BC exercise completed
- [ ] Incident response drill completed
- [ ] eDiscovery search test successful

## Quarterly Metrics Dashboard
| Metric | Q[X-1] | Q[X] | Target | Status |
|--------|--------|------|--------|--------|
| Agent count | | | | |
| Zone 3 agents | | | | |
| Security incidents | | | <5 | |
| DLP violations | | | Decreasing | |
| Bias test pass rate | | | >95% | |
| Training compliance | | | >90% | |

## Executive Summary
[Summary for governance committee/board]

## Action Items
| Item | Owner | Due Date | Status |
|------|-------|----------|--------|
| | | | |

Completed by: _________________ Date: _________
Compliance Officer: _________________ Date: _________
AI Governance Lead: _________________ Date: _________
```

---

## Annual Tasks

### Comprehensive Reviews

| Task | Control Reference | Owner | Duration |
|------|-------------------|-------|----------|
| Full control effectiveness assessment | All controls | AI Governance Lead | 2 days |
| Third-party model validation (Zone 3) | [2.6](../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | External Validator | 3-5 days |
| Independent red team assessment | [2.20](../../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | External Security | 2-3 days |
| Regulatory mapping update | [Regulatory Mappings](../../framework/regulatory-framework.md) | Compliance | 1 day |
| Framework version update review | All controls | AI Governance Lead | 1 day |

### Policy and Training

| Task | Control Reference | Owner | Duration |
|------|-------------------|-------|----------|
| Governance policy refresh | [RACI](raci-governance-template.md) | AI Governance Lead | 2 days |
| Training program update | [2.14](../../controls/pillar-2-management/2.14-training-and-awareness-program.md) | HR/Training | 1 day |
| Acceptable use policy update | [4.7](../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | Legal/Compliance | 1 day |
| Incident response playbook refresh | [3.4](../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | AI Governance Lead | 1 day |

### Vendor and Third-Party

| Task | Control Reference | Owner | Duration |
|------|-------------------|-------|----------|
| Vendor risk reassessment | [2.7](../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Risk | 2 days |
| Microsoft service review | All controls | Platform Admin | 1 day |
| Third-party attestation review | [2.6 Step 8a](../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md#third-party-attestation) | Compliance | 1 day |
| Connector security review | [1.4](../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | Security | 1 day |

### Annual Verification Checklist

```markdown
# Annual Governance Review - [Year]

## Comprehensive Reviews
- [ ] Full control effectiveness assessed
  - Controls tested: 60
  - Effective: ____
  - Partially effective: ____
  - Not effective: ____
- [ ] Third-party model validation completed (Zone 3)
- [ ] Independent red team assessment completed
- [ ] Regulatory mappings updated
- [ ] Framework version review completed

## Policy and Training
- [ ] Governance policy refreshed
- [ ] Training program updated
- [ ] Acceptable use policy updated
- [ ] Incident response playbook refreshed

## Vendor and Third-Party
- [ ] Vendor risk assessments current
- [ ] Microsoft service review completed
- [ ] Third-party attestations reviewed
- [ ] Connector security review completed

## Annual Metrics Summary
| Metric | [Year-1] | [Year] | Trend |
|--------|----------|--------|-------|
| Total agents | | | |
| Zone 3 agents | | | |
| Security incidents | | | |
| Regulatory findings | | | |
| Audit findings | | | |
| Training completion | | | |
| Control effectiveness | | | |

## Board/Executive Report Items
[Key points for board reporting]

## Next Year Priorities
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

## Approval

Completed by: _________________ Date: _________
AI Governance Lead: _________________ Date: _________
Compliance Officer: _________________ Date: _________
CISO: _________________ Date: _________
Executive Sponsor: _________________ Date: _________
```

---

## Calendar Integration

### Microsoft Outlook/Teams Calendar

Create recurring calendar events for each task category:

```
Weekly Tasks:
- "AI Governance - Weekly Security Review" (Monday 9:00 AM, 2 hours)
- "AI Governance - Weekly Monitoring" (Wednesday 10:00 AM, 1 hour)
- "AI Governance - Weekly Triage" (Friday 2:00 PM, 1 hour)

Monthly Tasks:
- "AI Governance - Monthly Access Review" (1st Wednesday, 4 hours)
- "AI Governance - Monthly Compliance" (2nd Wednesday, 3 hours)
- "AI Governance - Monthly Technical" (3rd Wednesday, 3 hours)

Quarterly Tasks:
- "AI Governance - Quarterly Review" (Last week of quarter, full day)

Annual Tasks:
- "AI Governance - Annual Assessment" (Q4, multiple days)
```

### Microsoft Planner/Project Integration

Create a Planner board with buckets for each cadence:

| Bucket | Task Type | Example Tasks |
|--------|-----------|---------------|
| Weekly Sprint | Recurring weekly tasks | Shadow sweep, DLP triage |
| Monthly Cycle | Monthly reviews | Access reviews, audits |
| Quarterly Checkpoint | Major reviews | Red team, bias testing |
| Annual Planning | Strategic reviews | Third-party validation |

---

## Customization Guide

### Step 1: Adjust for Organization Size

| Organization Size | Weekly | Monthly | Quarterly |
|------------------|--------|---------|-----------|
| Small (<500 users) | Combine tasks | Reduce frequency | Extend timeline |
| Medium (500-5000) | Use as-is | Use as-is | Use as-is |
| Large (>5000) | Add resources | Parallel tracks | Multiple reviewers |

### Step 2: Adjust for Zone Distribution

| Zone Profile | Focus Areas |
|--------------|-------------|
| Mostly Zone 1 | Reduce frequency; focus on adoption |
| Mixed Zone 1-2 | Standard calendar; team collaboration focus |
| Zone 3 Heavy | Increase frequency; compliance emphasis |

### Step 3: Regulatory Considerations

| Regulatory Environment | Adjustments |
|-----------------------|-------------|
| Broker-Dealer | Add FINRA-specific reviews |
| Bank/Thrift | Add OCC examination prep |
| Investment Advisor | Add SEC/fiduciary reviews |
| Insurance | Add state regulatory reviews |

---

## Related Documents

- [Governance Review Cadence](../../framework/governance-cadence.md) - Review framework
- [RACI Governance Template](raci-governance-template.md) - Role assignments
- [Lifecycle Governance](../../framework/agent-lifecycle.md) - Agent lifecycle
- [Control Index](../../controls/index.md) - Complete control list

---

*FSI Agent Governance Framework v1.1 - January 2026*
