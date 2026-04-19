# Verification & Testing: Control 3.10 - Hallucination Feedback Loop

**Last Updated:** April 2026
**Testing Level:** Control Validation
**Estimated Time:** 60-90 minutes

> This playbook provides verification and testing procedures for [Control 3.10](../../../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md). Use it after the [Portal Walkthrough](./portal-walkthrough.md) or [PowerShell Setup](./powershell-setup.md), and re-run quarterly as part of the supervisory cadence required by FINRA Rule 3110.

---

## Test Environment Setup

Before beginning verification testing, prepare:

- [ ] At least one Zone 2 and one Zone 3 test agent in Copilot Studio
- [ ] Copilot Studio CSAT enabled and `Report Inaccurate Response` topic published on each test agent
- [ ] SharePoint `Hallucination Tracking` list provisioned with Purview retention label applied
- [ ] Power Automate flows (`HFL-Intake-3.10`, SLA monitor, trend detector) enabled
- [ ] Test users with **Reporter** role (regular user) and **Triager** role (AI Governance Lead delegate)
- [ ] Access to Power BI workspace `AI Governance — Pillar 3 Reporting`
- [ ] Test incident response queue (Control 3.4) wired to the Critical escalation path

> Avoid running these tests in production agents that handle live customer queries — synthetic load can skew CSAT analytics and inflate hallucination rate metrics.

---

## Test Case 1: End-to-End Feedback Capture (CSAT Path)

**Objective:** Verify a user thumbs-down + comment lands in `Hallucination Tracking` within SLA.

**Regulatory Anchor:** FINRA Rule 3110 (supervisory review), SEC 17a-4 (record creation)

### Test Steps

1. As the Reporter user, open the published Zone 2 test agent in its deployed channel (Teams, web, or Copilot Studio test pane)
2. Send a query that the agent will answer (e.g., `What is the current Reg D limit?`)
3. Select **thumbs down** on the response
4. Submit a comment of the form `[Hallucination][Factual Error][High] Stated $X but actual is $Y`
5. Wait up to 60 seconds for the intake flow to run
6. As the Triager, open the SharePoint `Hallucination Tracking` list

### Expected Results

- [ ] A new list item appears with `IssueID` matching the format `HAL-YYYYMMDD-NNN`
- [ ] `AgentName`, `AgentEnvironment`, `Zone`, `ConversationId`, `UserQuery`, `AgentResponse`, `ReportedBy` are all populated
- [ ] `Category = Factual Error`, `Severity = High`, `Status = New`
- [ ] An acknowledgment email arrives at the Reporter mailbox citing the `IssueID`

### Evidence Collection

- Screenshot: agent thumbs-down + comment box with submitted text
- Screenshot: SharePoint list item showing all populated fields
- Email export (`.eml`) of the acknowledgment

---

## Test Case 2: Critical Severity Escalation

**Objective:** Verify Critical reports trigger Control 3.4 incident creation and Compliance notification within 1 hour.

**Regulatory Anchor:** FINRA Notice 25-07 (real-time supervision), SOX 302 (material misstatement escalation)

### Test Steps

1. As the Reporter, invoke the `Report Inaccurate Response` topic on the Zone 3 test agent
2. Choose `Fabrication` as the category and `Critical` as the suggested severity
3. Provide a synthetic correct-answer string clearly marked `[TEST DATA]`
4. Submit and start a stopwatch
5. Monitor the *AI Governance — Critical* Teams channel and the incident queue (Control 3.4)

### Expected Results

- [ ] Teams adaptive card posts in *AI Governance — Critical* within 5 minutes, tagging AI Governance Lead and Compliance Officer
- [ ] Incident record appears in the Control 3.4 queue with `RelatedIssueId` matching the hallucination `IssueID`
- [ ] The hallucination list item shows `RelatedIncidentId` populated
- [ ] Email arrives at the agent owner and AI Administrator mailboxes
- [ ] Within 1 hour: a Triager updates `Status = Triaged` and `AssignedTo` is populated

### Evidence Collection

- Screenshot: Teams adaptive card with timestamp
- Screenshot: incident record cross-referencing the hallucination IssueID
- Run history export from the intake flow showing the Condition branch executed

---

## Test Case 3: SLA Timer Accuracy

**Objective:** Verify the SLA monitor correctly flags breaches and only flags genuine breaches.

### Test Steps

1. Create three test items via the intake flow with `Severity = Medium` (72-hour remediation SLA)
2. Backdate `ReportDate` on item A to 73 hours ago (using a System Account or via PowerShell)
3. Leave item B with current `ReportDate`
4. On item C, set `Status = Closed` and `ResolutionDate` to 71 hours after `ReportDate`
5. Wait for the next hourly SLA monitor flow run (or trigger manually)

### Expected Results

- [ ] Item A: `RemediationSLAMet = No`, escalation card posted
- [ ] Item B: `RemediationSLAMet` empty (not yet due)
- [ ] Item C: `RemediationSLAMet = Yes` (closed within SLA)
- [ ] No false positives on items with `Status = Closed` or `Won't Fix`

### Evidence Collection

- Flow run history showing the three items processed
- SharePoint list view filtered to `RemediationSLAMet = No`

---

## Test Case 4: Trend Detection Threshold

**Objective:** Verify the daily trend detector posts an alert when an agent exceeds the configured rate.

### Test Steps

1. Submit 10 hallucination reports for the same Zone 3 test agent over a 24-hour synthetic window
2. Ensure the test agent's recorded conversation count for the same window is 100 (10% rate, well above any reasonable threshold)
3. Wait for the next 06:00 trend detector run (or trigger manually)

### Expected Results

- [ ] Teams message posts in *AI Governance — Trends* citing the agent and rate
- [ ] A `Trend Alerts` list item is created
- [ ] No alert is generated for unrelated agents

### Evidence Collection

- Screenshot: Teams trend alert with rate and agent name
- Flow run history

---

## Test Case 5: Power BI Dashboard Refresh and Accuracy

**Objective:** Confirm dashboard reflects current data within scheduled refresh window.

### Test Steps

1. Note the current Total Reports KPI value
2. Submit 3 new test reports across different categories
3. Trigger an on-demand dataset refresh in Power BI
4. Reload the report

### Expected Results

- [ ] Total Reports KPI increases by exactly 3
- [ ] Category distribution chart reflects the new categories
- [ ] No data quality warnings on the dataset

### Evidence Collection

- Before/after screenshots of the KPI tile
- Refresh history export from the dataset settings

---

## Test Case 6: Retention Label Enforcement

**Objective:** Verify the Purview retention label cannot be removed by a non-records-manager and that disposition requires review.

**Regulatory Anchor:** SEC Rule 17a-4(f) (non-rewriteable, non-erasable record retention)

### Test Steps

1. As a regular site member, attempt to delete a closed list item older than 30 days
2. As the **Purview Records Manager**, attempt to remove the retention label

### Expected Results

- [ ] Regular user cannot delete the item (or the deletion is intercepted by retention)
- [ ] Records Manager sees a disposition review prompt rather than immediate deletion
- [ ] Audit log captures both attempts with actor, action, and timestamp

### Evidence Collection

- Screenshot: deletion attempt error or retention notice
- Purview audit log export filtered to the test items

---

## Test Case 7: Reporter Acknowledgment and Closure Notification

**Objective:** Verify communication loop closes with the original reporter.

### Test Steps

1. Submit a test report
2. Triage and remediate to `Status = Closed` with a populated `RemediationActions` field

### Expected Results

- [ ] Reporter receives an acknowledgment at intake (Test Case 1)
- [ ] Reporter receives a closure notification with the remediation summary
- [ ] Closure email contains a link back to the SharePoint item

### Evidence Collection

- Email exports of both notifications

---

## Quarterly Compliance Checklist

Run this checklist as part of the supervisory cadence and store the completed copy in your WSP evidence archive.

| Item | Required For | Status |
|------|--------------|--------|
| CSAT enabled on all in-scope published agents | Quality management — FINRA 3110 | |
| Hallucination taxonomy reviewed and approved by Compliance | Consistent categorization — FINRA 25-07 | |
| Tracking list operational with current schema | FINRA 3110 supervisory review | |
| Purview retention label applied (6 years) | SEC 17a-4 record retention | |
| Intake, SLA, and trend flows all enabled (no failed runs > 5%) | Process integrity | |
| MTTR within firm target | Operational metric | |
| SLA compliance ≥ firm target (e.g., 95%) | Operational metric | |
| Power BI dashboard refreshed in last 7 days | Reporting integrity | |
| At least one tabletop exercise of Critical escalation in the quarter | FINRA 3110 supervisor training | |
| Quarterly trend report delivered to AI Governance Council | Governance cadence | |

---

## Evidence Collection for Audit

For FINRA, SEC, or internal audit reviews, prepare an evidence pack containing:

| Evidence Item | Source | Retention |
|---------------|--------|-----------|
| CSAT configuration screenshot per agent | Copilot Studio | 6 years (SEC 17a-4) |
| Hallucination Tracking list export (CSV or JSON) | SharePoint | 6 years |
| Conversation transcripts for sampled items | Dataverse / Application Insights | 6 years |
| Intake flow run history (sampled) | Power Automate | Per Power Platform retention + export |
| SLA compliance metrics report | Power BI export | 6 years |
| Quarterly trend reports | Power BI export | 6 years |
| Remediation evidence (knowledge source updates per Control 2.16, prompt changes) | Source control + change tickets | 6 years |
| Purview retention label policy and audit log | Purview portal | Per Purview policy |

> Wherever possible, exports should include cryptographic hashes (SHA-256) generated at export time. The PowerShell setup playbook includes helper functions that emit hashes alongside CSV exports.

---

## Negative Test Cases

Equally important — verify the system does **not** misbehave:

| Negative Test | Expected Behavior |
|---------------|-------------------|
| Submit thumbs-up | No item created, no flow triggered |
| Submit malformed JSON to intake URL | Flow returns 400, no list item created, error captured in run history |
| Disable CSAT on an agent | New conversations on that agent produce no items; existing items remain intact |
| Delete a triaged item as a regular user | Action denied or intercepted by retention label |
| Run intake flow with same `ConversationId` twice | Both items created (deduplication is intentionally manual at triage to avoid losing distinct turns) |

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) — Initial configuration
- [PowerShell Setup](./powershell-setup.md) — Automation scripts
- [Troubleshooting](./troubleshooting.md) — Common issues

---

[Back to Control 3.10](../../../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md)

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
