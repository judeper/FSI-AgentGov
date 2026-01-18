# Control 3.4: Incident Reporting and Root Cause Analysis - Portal Walkthrough

> This playbook provides step-by-step portal configuration guidance for [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).

---

## Prerequisites

- Entra Security Admin or Compliance Administrator role
- SharePoint Site Owner permissions for incident tracking
- Power Automate license for workflow automation
- Microsoft Sentinel workspace (for Level 4 implementations)

---

## Step 1: Define Incident Classification Taxonomy

**Incident Categories:**

| Category | Description | Examples | Severity Range |
|----------|-------------|----------|----------------|
| **Security** | Unauthorized access, data breach | Credential theft, DLP violation | Critical - High |
| **Compliance** | Regulatory violation, policy breach | Unapproved data access, missing audit | Critical - Medium |
| **Availability** | Service outage, performance degradation | Agent down, slow response | High - Low |
| **Data Quality** | Incorrect outputs, hallucinations | Wrong financial advice, calculation error | Critical - Low |
| **Privacy** | PII exposure, consent violation | Customer data leak, GLBA breach | Critical - High |
| **Bias/Fairness** | Discriminatory outcomes | Loan denial bias, unfair treatment | Critical - High |

**Severity Levels:**

| Severity | Response SLA | Escalation | Example |
|----------|--------------|------------|---------|
| **Critical (P1)** | 15 minutes | Immediate - CISO/CCO | Data breach, regulatory filing required |
| **High (P2)** | 1 hour | 4 hours - Director | DLP violation, agent producing incorrect advice |
| **Medium (P3)** | 4 hours | 24 hours - Manager | Policy violation, performance degradation |
| **Low (P4)** | 24 hours | 48 hours - Team Lead | Minor UI issues, feature requests |

---

## Step 2: Create SharePoint Incident Tracking System

**Portal Path:** SharePoint Admin Center > Sites > Create Site

Create SharePoint list with the following columns:

| Column Name | Type | Required | Values/Format |
|-------------|------|----------|---------------|
| Incident ID | Auto-generated | Yes | INC-YYYY-MMDD-### |
| Title | Single line | Yes | Brief description |
| Category | Choice | Yes | Security, Compliance, Availability, etc. |
| Severity | Choice | Yes | Critical, High, Medium, Low |
| Agent Name | Lookup | Yes | Link to Agent Inventory |
| Reported By | Person | Yes | User |
| Reported Date | Date/Time | Yes | Auto-populated |
| Status | Choice | Yes | New, Investigating, Pending RCA, Remediation, Closed |
| Assigned To | Person | Yes | Investigator |
| Description | Multi-line | Yes | Full incident details |
| Root Cause | Multi-line | No | RCA findings |
| Corrective Actions | Multi-line | No | Remediation steps |
| Resolution Date | Date/Time | No | When closed |
| Time to Resolution | Calculated | Auto | Resolution Date - Reported Date |
| Regulatory Impact | Yes/No | Yes | FINRA/SEC notification required |
| Evidence Links | Multiple links | No | Audit logs, screenshots |

---

## Step 3: Configure Incident Reporting Form

**Portal Path:** SharePoint Site > New > List Form > Customize with Power Apps

Create user-friendly intake form with:

- Required fields validation
- Auto-population of reporter and date
- Category-based severity suggestions
- File attachment for evidence
- Email confirmation to reporter

---

## Step 4: Set Up Automated Workflows

**Portal Path:** Power Automate > Create > Automated cloud flow

**Workflow 1: New Incident Notification**

```plaintext
Trigger: When item created in Incidents list
Conditions:
├── If Severity = Critical → Immediate escalation
│   └── Email CISO, CCO, CEO
│   └── Teams notification to Security-Ops
│   └── Create Sentinel incident
├── If Severity = High
│   └── Email Security Team Lead
│   └── Teams notification to AI-Ops
└── All incidents
    └── Assign to on-call investigator
    └── Start SLA timer
    └── Log to incident dashboard
```

**Workflow 2: SLA Breach Alert**

```plaintext
Trigger: Scheduled - Every 15 minutes
Conditions:
├── Find incidents past SLA
├── For each overdue incident:
│   └── Email escalation chain
│   └── Update status to "Escalated"
│   └── Notify manager
```

**Workflow 3: Incident Closure**

```plaintext
Trigger: When Status changed to "Closed"
Actions:
├── Validate required fields (Root Cause, Corrective Actions)
├── Calculate Time to Resolution
├── Archive evidence to permanent storage
├── Update metrics dashboard
├── If Regulatory Impact = Yes
│   └── Queue for regulatory filing review
└── Send closure notification
```

---

## Step 5: Configure Root Cause Analysis Template

**RCA Document Structure:**

```plaintext
INCIDENT ROOT CAUSE ANALYSIS
============================
Incident ID: [Auto-populated]
Analysis Date: [Date]
Analyst: [Name]

1. INCIDENT SUMMARY
   - What happened
   - When discovered
   - Impact scope

2. TIMELINE
   [Time] - Event 1
   [Time] - Event 2

3. ROOT CAUSE ANALYSIS
   Primary Cause: [Description]
   Contributing Factors:
   - Factor 1
   - Factor 2

   Analysis Method: 5 Whys / Fishbone / Fault Tree

4. IMPACT ASSESSMENT
   - Customers affected: [Number]
   - Data exposed: [Yes/No - Details]
   - Financial impact: [$Amount]
   - Regulatory implications: [Description]

5. CORRECTIVE ACTIONS
   | Action | Owner | Due Date | Status |

6. PREVENTIVE MEASURES
   - Short-term: [Description]
   - Long-term: [Description]

7. APPROVALS
   Analyst: _______ Date: _______
   Manager: _______ Date: _______
   Compliance: _______ Date: _______
```

---

## Step 6: Integrate with Microsoft Sentinel

**Portal Path:** Azure Portal > Microsoft Sentinel > Analytics

Create analytics rules for agent-related incidents:

| Rule Name | Data Source | Trigger | Severity |
|-----------|-------------|---------|----------|
| Agent DLP Violation | M365 Defender | DLP policy match | High |
| Unauthorized Agent Access | Entra ID | Failed access after hours | Medium |
| Agent Connector Failure | Power Platform | Error rate >5% | High |
| Unusual Data Volume | Audit Log | >3σ from baseline | Medium |
| Agent Response Anomaly | App Insights | Latency spike | Low |

---

## Step 7: Establish Weekly Incident Review Process

**Meeting Structure:**

| Item | Duration | Participants |
|------|----------|--------------|
| Open Incidents Review | 15 min | Ops Team |
| Critical Incident Deep Dive | 20 min | All stakeholders |
| RCA Presentations | 15 min | Analysts |
| Trend Analysis | 5 min | Manager |
| Action Item Review | 5 min | All |

---

## Next Steps

- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.1*
