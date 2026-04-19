# Portal Walkthrough: Control 3.3 - Compliance and Regulatory Reporting

**Last Updated:** April 2026

> Step-by-step portal configuration guidance for [Control 3.3](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md). Audience: Microsoft 365 administrators in US financial services subject to FINRA, SEC, SOX, GLBA, OCC, and Federal Reserve oversight.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **Purview Compliance Admin** role | Primary owner role for Compliance Manager assessments and report templates |
| **Compliance Manager Admin** role | Required to create/modify assessment templates and improvement actions |
| **SharePoint Site Owner** on archive site | Required to configure retention labels and library structure |
| **Power Platform Admin** | Required for Power Automate report flows and connection management |
| **Power BI Pro or Premium Per User** | Required for compliance dashboard authoring; viewers need at minimum Pro |
| **Premium assessment template entitlement** | A5/E5/G5 customers receive 3 premium templates free; verify entitlement in Compliance Manager before enabling EU AI Act / NIST AI RMF / ISO 42001 templates |

> **FSI note:** Assign roles via [Entra Privileged Identity Management (PIM)](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure) with just-in-time elevation and approval. Document role assignments in your Written Supervisory Procedures (FINRA Rule 3110).

---

## Step 1: Configure Microsoft Compliance Manager Assessments

**Portal Path:** [Microsoft Purview](https://purview.microsoft.com) > **Compliance Manager** > **Assessments**

1. Sign in as **Purview Compliance Admin**.
2. Select **Compliance Manager** in the left navigation.
3. Click **Assessments** > **+ Add assessment**.
4. Select **Choose from templates**.
5. Create assessments for each in-scope regulation. Recommended starting set for US FSI:

   | Assessment Name | Source Template | Scope (Group) | License Tier |
   |---|---|---|---|
   | FSI – FINRA Books & Records | Custom (built from FINRA 4511 / 17a-4 controls) | Broker-Dealer Operations | Custom (free) |
   | FSI – SEC 17a-4 Records Preservation | Search "17a-4" in templates; if no exact match exists, create a custom template referencing 17 CFR 240.17a-4 | Broker-Dealer Operations | Custom (free) |
   | FSI – SOX 404 IT General Controls | SOX 2002 (Microsoft baseline) | Enterprise IT | Premium |
   | FSI – GLBA 501(b) Safeguards | GLBA Safeguards Rule | Customer Data Systems | Premium |
   | FSI – NIST AI RMF | NIST AI RMF 1.0 | AI Agent Governance | Premium (counts toward 3-template free allowance) |
   | FSI – ISO/IEC 42001 AI Management | ISO/IEC 42001:2023 | AI Agent Governance | Premium |

   > **Hedged language:** Compliance Manager templates are mappings — they do **not** by themselves attest to compliance. Treat assessment scores as workflow indicators, not regulator-ready attestations.

6. For each assessment, on **Assessment grouping**, place AI agent assessments under a single group (e.g., `AI-Agent-Governance`) so reporting can roll them up.
7. Open each assessment > **Improvement actions** tab > map FSI-AgentGov controls to relevant actions:
   - Use the **Notes** field on each action to record the FSI control ID (e.g., "Implemented via FSI-AgentGov 1.7, 2.13, 3.1").
   - Attach evidence files (policy PDFs, configuration screenshots) directly to actions.

---

## Step 2: Configure SharePoint Records Library for Report Archive

**Portal Path:** [SharePoint Admin Center](https://admin.microsoft.com/sharepoint) > **Active sites** > **+ Create**

1. Sign in as **SharePoint Admin** (creation) or delegate to **SharePoint Site Owner** (configuration).
2. Create a new **Communication site** named `AI-Compliance-Reports` with privacy set to **Private**.
3. Configure the document library structure (use **Site contents > New > Document library** for each top-level folder if you prefer libraries over folders):

   ```text
   AI-Compliance-Reports/
   ├── Weekly Reports/
   ├── Monthly Reports/
   ├── Quarterly Reports/
   ├── Annual Reports/
   ├── Examination Packages/
   │   ├── FINRA/
   │   ├── SEC/
   │   ├── OCC/
   │   ├── State Regulators/
   │   └── Internal Audit/
   └── Archive/{YYYY}/
   ```

4. **Apply retention labels** ([Microsoft Purview](https://purview.microsoft.com) > **Records management** > **Retention labels**):

   | Label | Retention | Behavior | Apply To |
   |---|---|---|---|
   | `FSI-Reg-Records-7Year` | 7 years from last activity | Mark as **regulatory record** (immutable) | Examination Packages, Annual Reports |
   | `FSI-Compliance-Reports-3Year` | 3 years from creation | Mark as **record** | Weekly/Monthly/Quarterly Reports |

   > **SEC 17a-4 note:** Marking a label as a **regulatory record** in Purview Records Management invokes immutability that helps support 17a-4(f) non-rewriteable, non-erasable storage requirements. Confirm your tenant uses Purview-managed retention (not legacy in-place holds) before relying on this for examinations.

5. Publish a **retention label policy** scoped to the `AI-Compliance-Reports` site.
6. On each library, set the **default retention label** so new uploads inherit the correct policy.

---

## Step 3: Build Power Automate Report Flows

**Portal Path:** [Power Automate](https://make.powerautomate.com) > **+ Create** > **Scheduled cloud flow**

Create the following flows in a **Managed Environment** owned by the Power Platform Admin (see Control 2.1):

| Flow | Recurrence | Trigger Time | Outputs |
|---|---|---|---|
| Weekly Control Status | Weekly, Monday | 06:00 local | HTML/PDF report → SharePoint `Weekly Reports/` + email to Compliance Team distribution list |
| Monthly Regulatory Alignment | Monthly, day 1 | 06:00 local | PDF report → `Monthly Reports/` + approval request to CCO |
| Quarterly Audit Evidence Bundle | Monthly, day 1 of month 1, 4, 7, 10 | 06:00 local | ZIP bundle → `Quarterly Reports/` + approval request to CAO |
| Annual Safeguards Review | Yearly, January 15 | 06:00 local | PDF report → `Annual Reports/` + GLBA 501(b) attestation request |

**Each flow should:**

1. Query Compliance Manager scores via the [Microsoft Graph compliance APIs](https://learn.microsoft.com/en-us/graph/api/resources/security-api-overview) (where available) or via PowerShell action calling the script in [PowerShell Setup](powershell-setup.md).
2. Aggregate FSI-AgentGov control status from your control tracking source (Dataverse table, SharePoint list, or Power BI dataset).
3. Generate the report file (HTML → PDF via **Convert file** action, or **Word for Business** template render).
4. Save to SharePoint with metadata: `ReportType`, `PeriodStart`, `PeriodEnd`, `GeneratedBy`, `EvidenceHash` (SHA-256 of source data — see PowerShell Setup §6).
5. Send approval request via **Approvals** connector for Monthly+ reports.
6. Log a row to a Dataverse `ReportRunLog` table for audit trail.

> **Mutation safety:** All flows that write to SharePoint should use a service account with only the minimum library permissions; do **not** use a Global Admin or human admin account as the flow connection.

---

## Step 4: Build the Power BI Compliance Dashboard

**Portal Path:** [Power BI](https://app.powerbi.com) > **+ New** > **Report**

1. Connect to data sources:
   - Dataverse `ReportRunLog` table (flow run history)
   - SharePoint `AI-Compliance-Reports` library metadata
   - Compliance Manager scores (via [Microsoft Graph](https://learn.microsoft.com/en-us/graph/) or scheduled CSV export)
   - FSI-AgentGov control status (your source of truth)
2. Build the following pages:

   | Page | Visuals | Audience |
   |---|---|---|
   | **Executive Summary** | Overall compliance score (KPI card), score by pillar (bar), trend (line, 12 months) | CCO, CAO, CIO |
   | **Pillar Detail** | Drill-through to control-level status with red/amber/green | Compliance Team |
   | **Regulatory Coverage** | Heatmap: regulations × pillars | Audit Team |
   | **Action Items** | Overdue improvement actions, owners, due dates | Control Owners |
   | **Examination Readiness** | Days since last refresh, missing evidence count, pending approvals | CCO, CAO |

3. Publish to a **Power BI workspace** with row-level security enforcing zone-based visibility (Zone 1 owners see only their agents; Zone 3 owners see enterprise rollups).
4. Configure scheduled refresh (recommended: hourly during business hours, then daily overnight).

---

## Step 5: Configure Distribution and Approval Matrix

| Report | Primary Recipients | CC | Approver | Approval SLA |
|---|---|---|---|---|
| Weekly Control Status | Compliance Team, IT Security Operations | — | None (informational) | n/a |
| Monthly Regulatory Alignment | CCO, CIO, CISO | Business Unit Heads | CCO | 5 business days |
| Quarterly Audit Evidence Bundle | CAO, External Auditors | CCO, CEO | CAO + CCO | 10 business days |
| Annual Safeguards Review | Board Risk Committee | CCO, CIO | CCO + CISO | 15 business days |
| Examination Package (on-demand) | Exam Coordinator, Outside Counsel | CCO, Legal | CCO + General Counsel | 24 hours |

Use the [Approvals connector](https://learn.microsoft.com/en-us/power-automate/get-started-approvals) in each Power Automate flow. Capture approval comments — they become part of the audit trail and help support SOX 302 sub-certification evidence.

---

## Step 6: Regulatory Examination Calendar

**Portal Path:** [Microsoft 365 Calendar](https://outlook.office.com/calendar) (shared mailbox: `compliance-calendar@yourdomain.com`)

Create a shared calendar tracking:

| Event Type | Source | Lead Time |
|---|---|---|
| FINRA cycle exam | FINRA notification | 90 days before |
| SEC OCIE/EXAMS exam | SEC notification | 90 days before |
| OCC supervisory cycle | OCC schedule | 180 days before |
| State regulator exams | State filings | Per state |
| SOX 302 quarterly sub-certification | Internal | 30 days before quarter end |
| SOX 404 annual attestation | Internal | 90 days before fiscal year end |
| GLBA 501(b) annual safeguards review | Internal | 30 days before due |
| Reg S-P customer notification readiness drill | Internal | Quarterly |

Subscribe the calendar in Power BI for the **Examination Readiness** page.

---

## Verification

After completing all six steps:

- [ ] All assessments listed in Step 1 appear in Compliance Manager with at least one mapped improvement action each
- [ ] SharePoint site `AI-Compliance-Reports` is accessible to the Compliance Team and applies retention labels by default
- [ ] All four scheduled Power Automate flows show **Succeeded** status on at least one test run
- [ ] Power BI dashboard renders all five pages with no data-refresh errors
- [ ] Approval matrix is documented and linked from your Written Supervisory Procedures

Proceed to [Verification & Testing](verification-testing.md) for detailed test cases and evidence collection.

---

[Back to Control 3.3](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
