# Governance Review Cadence

## Overview

This guide establishes a structured review schedule to ensure AI agent governance remains current, effective, and aligned with regulatory requirements. Regular reviews prevent governance drift and support examination readiness.

---

## Review Schedule Summary

| Cadence | Focus Areas | Primary Owner | Participants |
|---------|-------------|---------------|--------------|
| **Quarterly** | Operational controls, policies | Power Platform Admin | IT, Compliance |
| **Semi-Annual** | Governance structure, processes | AI Governance Lead | All stakeholders |
| **Annual** | Full governance refresh | Governance Committee | Executive sponsors |

---

## Quarterly Reviews

**Timing:** End of each calendar quarter (March, June, September, December)

**Duration:** 2-4 hours

### Review Checklist

| Area | Review Items | Owner |
|------|--------------|-------|
| **Connector Policies** | DLP policy effectiveness, blocked connector violations, new connector requests | Power Platform Admin |
| **Environment Rules** | Environment group configurations, sharing rules, channel access settings | Power Platform Admin |
| **AI Feature Enablement** | Generative AI settings, preview features, external model access | AI Governance Lead |
| **Agent Inventory** | New agents deployed, agents requiring reclassification, inactive agents | AI Governance Lead |
| **Incident Review** | Security incidents, policy violations, near-misses | Security Team |
| **Access Reviews** | User permissions, admin role assignments, service accounts | Identity Admin |

### Quarterly Review Template

```
QUARTERLY GOVERNANCE REVIEW
Period: Q[X] [YYYY]
Date: [Review Date]
Attendees: [Names and Roles]

1. CONNECTOR POLICY REVIEW
   - DLP violations this quarter: [Count]
   - New connectors requested: [List]
   - Policy changes implemented: [List]
   - Recommendations: [Notes]

2. ENVIRONMENT RULES REVIEW
   - Environment groups reviewed: [List]
   - Rule changes implemented: [List]
   - Issues identified: [Notes]

3. AI FEATURE SETTINGS
   - Generative AI status: [Enabled/Disabled by zone]
   - Preview features active: [List]
   - External models approved: [List]

4. AGENT INVENTORY STATUS
   - Total active agents: [Count by zone]
   - New agents this quarter: [Count]
   - Agents decommissioned: [Count]
   - Reclassification needed: [List]

5. INCIDENT SUMMARY
   - Security incidents: [Count and summary]
   - Policy violations: [Count and summary]
   - Remediation status: [Complete/In Progress]

6. ACTION ITEMS
   | Action | Owner | Due Date |
   |--------|-------|----------|
   | [Action] | [Name] | [Date] |

Reviewed By: _________________ Date: _________
AI Governance Lead

Reviewed By: _________________ Date: _________
Compliance Officer
```

---

## Semi-Annual Reviews

**Timing:** Mid-year (June) and Year-end (December)

**Duration:** Half-day session

### Review Checklist

| Area | Review Items | Owner |
|------|--------------|-------|
| **Zone Definitions** | Zone criteria appropriateness, zone boundary clarity, promotion/demotion criteria | AI Governance Lead |
| **ALM Processes** | Pipeline effectiveness, deployment success rates, rollback incidents | Platform Team |
| **Delegated Admin Roles** | Role assignments, privilege creep, role consolidation opportunities | Identity Admin |
| **Testing Procedures** | Test coverage adequacy, bias testing results, security testing gaps | QA Lead |
| **Training Program** | Training completion rates, content currency, new training needs | Training Lead |
| **Vendor/Third-Party** | External service reviews, contract renewals, SLA compliance | Procurement |

### Semi-Annual Review Template

```
SEMI-ANNUAL GOVERNANCE REVIEW
Period: [H1/H2] [YYYY]
Date: [Review Date]
Attendees: [Names and Roles]

1. ZONE GOVERNANCE REVIEW
   Zone 1 (Personal):
   - Agent count: [X]
   - Issues identified: [Notes]
   - Criteria changes needed: [Yes/No - Details]

   Zone 2 (Team):
   - Agent count: [X]
   - Issues identified: [Notes]
   - Criteria changes needed: [Yes/No - Details]

   Zone 3 (Enterprise):
   - Agent count: [X]
   - Issues identified: [Notes]
   - Criteria changes needed: [Yes/No - Details]

2. ALM PROCESS REVIEW
   - Deployments this period: [Count]
   - Successful deployments: [%]
   - Rollbacks required: [Count]
   - Pipeline improvements needed: [Notes]

3. ROLE AND ACCESS REVIEW
   - Admin roles reviewed: [List]
   - Privilege changes made: [List]
   - Segregation of duties confirmed: [Yes/No]

4. TESTING PROGRAM REVIEW
   - Agents tested: [Count]
   - Bias testing pass rate: [%]
   - Security testing pass rate: [%]
   - Testing gaps identified: [Notes]

5. TRAINING STATUS
   - Users trained: [Count]
   - Training completion rate: [%]
   - New training developed: [List]
   - Training gaps: [Notes]

6. RECOMMENDATIONS FOR NEXT PERIOD
   [List prioritized recommendations]

Approved By: _________________ Date: _________
AI Governance Lead

Approved By: _________________ Date: _________
Compliance Officer
```

---

## Annual Reviews

**Timing:** End of fiscal/calendar year (typically Q4)

**Duration:** Full-day session with executive participation

### Review Checklist

| Area | Review Items | Owner |
|------|--------------|-------|
| **Full Governance Model** | Framework effectiveness, control adequacy, gap analysis | AI Governance Lead |
| **Regulatory Alignment** | New regulations, guidance updates, examination findings | Compliance Officer |
| **Risk Assessment** | Enterprise AI risk posture, emerging risks, risk appetite alignment | Risk Management |
| **Technology Roadmap** | Platform updates, new capabilities, deprecations | Platform Team |
| **Budget and Resources** | Governance program funding, staffing adequacy, tool investments | Finance/HR |
| **Metrics and KPIs** | Program performance, trend analysis, benchmark comparison | AI Governance Lead |

### Regulatory Update Review

| Regulation | Review Focus | Action Required |
|------------|--------------|-----------------|
| **FINRA 25-07** | AI supervision guidance updates | Update supervision procedures |
| **SEC AI Priorities** | Examination focus areas | Align documentation |
| **OCC 2011-12 / SR 11-7** | Model risk guidance | Review validation procedures |
| **State Regulations** | NYDFS, state-specific requirements | Verify compliance |
| **Industry Standards** | NIST AI RMF, ISO updates | Gap assessment |

### Annual Review Template

```
ANNUAL GOVERNANCE REVIEW
Year: [YYYY]
Date: [Review Date]
Attendees: [Names and Roles including Executive Sponsors]

EXECUTIVE SUMMARY
- Overall program health: [Green/Yellow/Red]
- Key achievements: [List]
- Key challenges: [List]
- Budget status: [On track/Over/Under]

1. GOVERNANCE MODEL ASSESSMENT
   Framework Version: [Current version]
   Controls Implemented: [X of Y]
   Control Effectiveness: [Assessment]
   Gaps Identified: [List with remediation plans]

2. REGULATORY ALIGNMENT
   | Regulation | Status | Gaps | Remediation |
   |------------|--------|------|-------------|
   | FINRA 25-07 | [Status] | [Gaps] | [Plan] |
   | SEC 17a-3/4 | [Status] | [Gaps] | [Plan] |
   | OCC 2011-12 | [Status] | [Gaps] | [Plan] |
   | SOX 302/404 | [Status] | [Gaps] | [Plan] |

3. ENTERPRISE RISK ASSESSMENT
   AI Risk Category: [High/Medium/Low]
   Risk Trend: [Increasing/Stable/Decreasing]
   Top Risks:
   1. [Risk and mitigation]
   2. [Risk and mitigation]
   3. [Risk and mitigation]

4. PROGRAM METRICS
   | Metric | Target | Actual | Trend |
   |--------|--------|--------|-------|
   | Agent compliance rate | [%] | [%] | [↑↓→] |
   | Incident count | [#] | [#] | [↑↓→] |
   | Training completion | [%] | [%] | [↑↓→] |
   | Audit findings | [#] | [#] | [↑↓→] |

5. TECHNOLOGY ROADMAP ALIGNMENT
   Upcoming platform changes: [List]
   Impact on governance: [Assessment]
   Required updates: [List]

6. BUDGET AND RESOURCES
   Current year spend: [$]
   Next year request: [$]
   Staffing assessment: [Adequate/Gap]
   Tool investments needed: [List]

7. NEXT YEAR PRIORITIES
   1. [Priority with rationale]
   2. [Priority with rationale]
   3. [Priority with rationale]

8. GOVERNANCE FRAMEWORK UPDATES
   Proposed changes for next version: [List]
   Effective date: [Date]

APPROVALS

Executive Sponsor: _________________ Date: _________

AI Governance Lead: _________________ Date: _________

Chief Compliance Officer: _________________ Date: _________

Chief Information Security Officer: _________________ Date: _________
```

---

## Review Calendar Template

| Month | Q1 | Q2 | Q3 | Q4 |
|-------|----|----|----|----|
| **January** | | | | |
| **February** | | | | |
| **March** | Quarterly Review | | | |
| **June** | | Quarterly + Semi-Annual | | |
| **September** | | | Quarterly Review | |
| **December** | | | | Quarterly + Semi-Annual + Annual |

---

## Examination Readiness

Maintain these artifacts for regulatory examination:

| Artifact | Retention | Location |
|----------|-----------|----------|
| Quarterly review minutes | 7 years | SharePoint Compliance Library |
| Semi-annual review reports | 7 years | SharePoint Compliance Library |
| Annual governance assessment | 10 years | SharePoint Compliance Library |
| Remediation tracking | 7 years | Compliance tracking system |
| Policy change history | 10 years | Version control system |

---

## Related Documents

- [Zones Overview](./zones.md) - Governance zone definitions
- [Agent Lifecycle](./lifecycle.md) - Lifecycle governance requirements
- [Control 2.5 - Testing & Validation](../reference/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) - Testing procedures
- [Control 3.1 - Agent Inventory](../reference/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) - Inventory management

---

*FSI Agent Governance Framework v1.0 - January 2026*
