# Control 3.3: Compliance and Regulatory Reporting - Portal Walkthrough

> This playbook provides step-by-step portal configuration guidance for [Control 3.3](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md).

---

## Prerequisites

- Purview Compliance Admin role in Microsoft Purview
- SharePoint Site Owner permissions for report archiving
- Power BI Pro or Premium license for dashboards
- Power Automate license for automated workflows

---

## Step 1: Configure Microsoft Compliance Manager

**Portal Path:** Microsoft Purview > Compliance Manager > Assessments

1. Navigate to [Microsoft Purview Compliance Portal](https://compliance.microsoft.com)
2. Select **Compliance Manager** in the left navigation
3. Click **Assessments** > **+ Add assessment**
4. Create assessments for applicable regulations:

| Assessment | Template | Scope |
|------------|----------|-------|
| FINRA Agent Governance | Custom template | AI Agents |
| SEC 17a-4 Records | SEC 17a-4 template | Agent Interactions |
| SOX 404 IT Controls | SOX 404 template | Agent Infrastructure |
| GLBA Safeguards | GLBA 501(b) template | Customer Data Agents |

5. Map FSI-AgentGov controls to assessment actions

---

## Step 2: Create Compliance Reporting Template Library

**Report Types Required:**

| Report Type | Frequency | Audience | Retention |
|-------------|-----------|----------|-----------|
| Control Status Summary | Weekly | IT/Compliance | 3 years |
| Regulatory Alignment Report | Monthly | Compliance/Audit | 7 years |
| Executive Compliance Dashboard | Monthly | C-Suite | 3 years |
| Examination Ready Package | On-demand | Regulators | 7 years |
| Audit Evidence Bundle | Quarterly | Internal/External Audit | 7 years |
| Incident Compliance Summary | As needed | Compliance/Legal | 7 years |

---

## Step 3: Set Up SharePoint Report Archive

**Portal Path:** SharePoint Admin Center > Sites > Create Site

1. Create dedicated SharePoint site: `AI-Compliance-Reports`
2. Configure document libraries:

```plaintext
AI-Compliance-Reports/
├── Weekly Reports/
│   ├── Control Status/
│   └── Metrics Summary/
├── Monthly Reports/
│   ├── Regulatory Alignment/
│   ├── Executive Dashboard/
│   └── Trend Analysis/
├── Quarterly Reports/
│   ├── Audit Evidence/
│   ├── Risk Assessment/
│   └── Control Effectiveness/
├── Examination Packages/
│   ├── FINRA/
│   ├── SEC/
│   ├── OCC/
│   └── State Regulators/
└── Archive/
    └── [Year]/
```

3. Apply retention labels:
   - `Regulatory-7Year` for examination packages
   - `Compliance-3Year` for operational reports

---

## Step 4: Configure Automated Report Generation

**Portal Path:** Power Automate > Create > Scheduled cloud flow

Create automated flows for each report type:

| Flow Name | Trigger | Actions |
|-----------|---------|---------|
| Weekly Control Status | Every Monday 6 AM | Query Compliance Manager > Generate PDF > Email > Archive |
| Monthly Regulatory Report | 1st of month | Aggregate data > Generate report > Route for approval > Archive |
| Quarterly Audit Package | Quarterly | Compile evidence > Generate package > Executive sign-off > Archive |

---

## Step 5: Build Compliance Dashboard in Power BI

**Dashboard Components:**

| Section | Metrics | Data Source |
|---------|---------|-------------|
| **Overall Compliance Score** | % controls compliant | Compliance Manager |
| **Control Status by Pillar** | Red/Yellow/Green by pillar | Control tracking |
| **Regulatory Coverage** | % regulations addressed | Assessment mapping |
| **Trend Analysis** | Score over time | Historical data |
| **Action Items** | Open remediation items | Compliance Manager |
| **Upcoming Reviews** | Scheduled control reviews | Calendar integration |

---

## Step 6: Establish Report Distribution and Approval

**Distribution Matrix:**

| Report | Primary Recipients | CC Recipients | Approval Required |
|--------|-------------------|---------------|-------------------|
| Weekly Status | Compliance Team, IT Ops | - | No |
| Monthly Regulatory | CCO, CIO, CISO | Business Heads | Yes - CCO |
| Quarterly Audit | CAO, External Auditors | CCO, CEO | Yes - CAO, CCO |
| Examination Package | Exam Coordinator | CCO, Legal | Yes - CCO, Legal |

---

## Step 7: Configure Regulatory Calendar Integration

Track examination schedules and filing deadlines:

| Regulator | Typical Schedule | Report Requirements |
|-----------|------------------|---------------------|
| FINRA | Annual cycle exam | Books and records, supervision evidence |
| SEC | Periodic exams | 17a-4 compliance, trading records |
| OCC | 12-18 month cycle | IT risk management, third-party controls |
| State Regulators | Annual | State-specific requirements |
| SOX Auditors | Annual | IT general controls, access management |

---

---

[Back to Control 3.3](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
