# Portal Walkthrough: Control 3.10 - Hallucination Feedback Loop

**Last Updated:** April 2026
**Portal:** Microsoft Copilot Studio, SharePoint Online, Power Automate, Power BI
**Estimated Time:** 90-120 minutes

> This playbook provides step-by-step portal configuration guidance for [Control 3.10](../../../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md). It covers the full feedback loop: capture, triage, remediation, and trend reporting.

!!! warning "Detection Limitations (April 2026)"
    Microsoft Copilot Studio does not natively detect hallucinations. Every step in this playbook depends on **human-submitted feedback** (thumbs down, flag, or out-of-band escalation) and **manual or workflow-driven review**. Configure the controls below as a structured intake — not as an automated detector — and pair them with the proactive mitigations described in the parent control.

---

## Prerequisites

- [ ] **Power Platform Admin** role (for environment-level Copilot Studio settings)
- [ ] **Copilot Studio Agent Author** access to each agent in scope (per-agent feedback toggle)
- [ ] **SharePoint Site Owner** on the AI Governance site (to create the tracking list)
- [ ] **Power Automate** premium license for the agent owner mailbox or service account that runs intake flows
- [ ] **Power BI Pro** license for the AI Governance Lead (trend reporting)
- [ ] Hallucination taxonomy and severity matrix approved by Compliance (see Step 2)
- [ ] Service account or shared mailbox for SLA timer notifications (recommended for FINRA 3110 evidence integrity)
- [ ] Decision recorded on integration with Control 3.4 (Incident Reporting) — direct flow vs. manual escalation

---

## Step-by-Step Configuration

### Part 1: Enable Feedback Capture in Copilot Studio

#### Step 1: Enable Customer Satisfaction (CSAT) on Each Agent

**Portal Path:** [Copilot Studio](https://copilotstudio.microsoft.com) → *select agent* → **Settings** → **Customer satisfaction**

1. Open [Copilot Studio](https://copilotstudio.microsoft.com) and sign in with **Copilot Studio Agent Author** credentials
2. Select the target agent from the agent list
3. In the left navigation, expand **Settings** and choose **Customer satisfaction**
4. Toggle **Allow users to provide feedback** to **On**
5. Configure the survey:
   - **Survey type:** *CSAT survey after each conversation* (recommended for Zone 2/3) or *Thumbs only* (acceptable for Zone 1)
   - **Comment box:** Enable to capture free-text rationale (required for Zone 3 to meet SEC 17a-4 evidence quality)
   - **Trigger:** *After end-of-conversation* and *After each response* (Zone 3 only — captures per-turn signal)
6. Click **Save**
7. **Publish** the agent so the configuration takes effect in deployed channels

> **Zone 3 Requirement:** CSAT must be enabled with comment box on every published agent. Document the agent inventory and CSAT status as part of your supervisory procedures (FINRA Rule 3110 / Notice 25-07).

#### Step 2: Add an "Escalate to Human Review" Topic (Recommended)

**Portal Path:** Copilot Studio → *agent* → **Topics** → **+ Add a topic** → **From blank**

1. Create a new topic named `Report Inaccurate Response`
2. Trigger phrases: `report a hallucination`, `that's wrong`, `incorrect answer`, `flag this response`, `escalate to human`
3. Add a **Question** node: *"Help us improve. What category best describes the issue?"* with multiple choice options matching the taxonomy in Step 4 of Part 2
4. Add a **Question** node: *"What would the correct answer have been?"* (text input — store as variable `CorrectAnswer`)
5. Add a **Power Automate** action node that calls the intake flow built in Part 3
6. End with a **Message** node: *"Thank you. Your report has been logged for review by our governance team."*
7. **Save** and **Publish**

> Capturing the **conversation ID** and **timestamp** in the Power Automate call is essential — without these, you cannot reconstruct the conversation transcript from Dataverse for SEC 17a-4 evidence.

---

### Part 2: Define the Hallucination Taxonomy

This taxonomy must be approved by Compliance before configuring tracking. Modifying categories later invalidates trend data.

| Category | Definition | Default Severity | FSI Example |
|----------|------------|------------------|-------------|
| **Factual Error** | Verifiable fact stated incorrectly | High | Stated wrong APY for a product |
| **Fabrication** | Information that does not exist in any source | Critical | Cited a non-existent SEC rule |
| **Outdated Information** | Was correct at one time, now stale | Medium | Quoted last quarter's rates |
| **Misattribution** | Cited the wrong source document | Medium | Linked to wrong policy PDF |
| **Calculation Error** | Arithmetic or formula mistake | High | Wrong fee or interest calculation |
| **Conflation** | Combined details of two distinct items | Medium | Mixed product features |
| **Overconfidence** | Asserted certainty on uncertain matter | Medium | "Definitely" instead of "may" |
| **Misleading Framing** | Technically true, materially misleading | High | Cherry-picked disclosures |

**Severity to SLA mapping (target — adjust per your firm's risk appetite):**

| Severity | Definition | Triage SLA | Remediation SLA |
|----------|------------|------------|-----------------|
| Critical | Customer harm, regulatory exposure, or supervisory escalation | 1 hour | 4 hours |
| High | Material misinformation that could influence decisions | 4 hours | 24 hours |
| Medium | Minor inaccuracy, low decision impact | 1 business day | 72 hours |
| Low | Cosmetic, stylistic, or de minimis | 2 business days | 1 week |

> SLA targets are firm-defined. Document the chosen values in your Written Supervisory Procedures (WSPs) so supervisors can demonstrate consistent oversight under FINRA Rule 3110.

---

### Part 3: Create the Hallucination Tracking List in SharePoint

**Portal Path:** SharePoint AI Governance site (`https://<tenant>.sharepoint.com/sites/AI-Governance`) → **+ New** → **List** → **Blank list**

#### Step 1: Create the List

1. From the AI Governance site home, click **+ New** → **List** → **Blank list**
2. Name: `Hallucination Tracking`
3. Description: `Intake and remediation log for AI agent hallucinations. Retain per SEC 17a-4 (6 years).`
4. Show in site navigation: **Yes**
5. Click **Create**

#### Step 2: Add Required Columns

Add these columns via **+ Add column** in list view. Match types exactly — Power BI and Power Automate flows depend on the schema.

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| Title | Single line of text | Yes | Auto: `<AgentName> - <Category>` |
| IssueID | Single line of text | Yes | Format `HAL-YYYYMMDD-NNN` (set by intake flow) |
| ReportDate | Date and time | Yes | Default: Today |
| AgentName | Single line of text | Yes | Pulled from conversation context |
| AgentEnvironment | Single line of text | Yes | Power Platform environment ID |
| Zone | Choice (1, 2, 3) | Yes | Auto-populated from environment metadata |
| Category | Choice | Yes | All 8 taxonomy values from Part 2 |
| Severity | Choice (Critical, High, Medium, Low) | Yes | Reporter-suggested; reviewer-confirmed |
| ConfirmedSeverity | Choice | No | Set by triage reviewer |
| UserQuery | Multiple lines of text | Yes | Plain text |
| AgentResponse | Multiple lines of text | Yes | Plain text |
| CorrectInformation | Multiple lines of text | No | Captured at remediation |
| SourceOfTruth | Hyperlink | No | Authoritative reference |
| ConversationId | Single line of text | Yes | For Dataverse transcript lookup |
| ReportedBy | Person or group | Yes | |
| AssignedTo | Person or group | No | Set by triage |
| Status | Choice (New, Triaged, In Remediation, In Validation, Closed, Won't Fix) | Yes | Default: New |
| RootCause | Choice (Knowledge Gap, Prompt Issue, Source Conflict, Model Limitation, Configuration, Unknown) | No | Set at root cause analysis |
| RemediationActions | Multiple lines of text | No | Free-text summary |
| ResolutionDate | Date and time | No | Set when Status → Closed |
| TriageSLAMet | Yes/No | No | Calculated by flow |
| RemediationSLAMet | Yes/No | No | Calculated by flow |
| RelatedIncidentId | Single line of text | No | Link to Control 3.4 incident |

#### Step 3: Configure Retention

1. Open **List settings** → **Library settings** → **Information management policy settings** (or use a Purview retention label)
2. Apply a **Purview retention label** with **6 years** retention from the **ReportDate** column (SEC 17a-4)
3. Set the **Disposition review** to require approval by **Purview Records Manager** before deletion
4. Verify the label applies by adding a test item and inspecting **Compliance details**

> If your firm uses Records Management for broker-dealer evidence, apply the same retention label your existing surveillance records use. Do not rely on SharePoint's built-in retention as a stand-alone control for SEC 17a-4 evidence.

---

### Part 4: Configure Power Automate Intake and SLA Flows

**Portal Path:** [Power Automate](https://make.powerautomate.com) → **+ Create**

#### Flow 1: Hallucination Intake (HTTP-Triggered)

**Type:** *Instant cloud flow* with **When an HTTP request is received** trigger

1. Create new flow `HFL-Intake-3.10`
2. Trigger: **When an HTTP request is received** with JSON schema:
   ```json
   {
     "type": "object",
     "properties": {
       "agentName": {"type": "string"},
       "agentEnvironment": {"type": "string"},
       "conversationId": {"type": "string"},
       "userQuery": {"type": "string"},
       "agentResponse": {"type": "string"},
       "category": {"type": "string"},
       "severity": {"type": "string"},
       "reportedBy": {"type": "string"}
     }
   }
   ```
3. Action: **Compose** → generate `IssueID` = `HAL-` + `formatDateTime(utcNow(),'yyyyMMdd')` + `-` + `rand(100,999)`
4. Action: **Compose** → derive `Zone` from environment lookup (call your environment registry)
5. Action: **Get user profile (V2)** for `reportedBy` to resolve to person field
6. Action: **Create item** in `Hallucination Tracking` with mapped fields, `Status = New`
7. Action: **Condition** — if `severity == Critical`:
   - **HTTP** call to Control 3.4 incident intake flow (or **Create item** in Incident Tracking list)
   - **Post message** in Teams *AI Governance — Critical* channel tagging the **AI Governance Lead** and **Compliance Officer**
   - **Send email** to agent owner and **AI Administrator**
8. Action: **Send email** acknowledgment to `reportedBy` with the `IssueID`
9. **Save** and copy the trigger URL into the Copilot Studio topic from Part 1, Step 2

#### Flow 2: SLA Monitor (Scheduled)

**Type:** *Scheduled cloud flow* — every 1 hour

1. Trigger: **Recurrence** — every 1 hour
2. Action: **Get items** from `Hallucination Tracking` filtered by `Status ne 'Closed' and Status ne 'Won''t Fix'`
3. Action: **Apply to each** item:
   - Compute elapsed hours since `ReportDate`
   - Compare against SLA matrix for `ConfirmedSeverity` (fall back to `Severity` if not yet triaged)
   - If breached and `TriageSLAMet` or `RemediationSLAMet` is empty/false:
     - **Update item** to set the appropriate SLA field to `No`
     - **Post adaptive card** in Teams to `AssignedTo` with escalation prompt
     - For Critical/High breaches, also notify the **AI Governance Lead**

#### Flow 3: Trend Detection (Scheduled Daily)

**Type:** *Scheduled cloud flow* — daily at 06:00 local

1. Trigger: **Recurrence** — daily, 06:00
2. Action: **Get items** from last 24 hours grouped by `AgentName`
3. Action: For each agent, calculate hallucination rate using a separate query against your conversation count source (Application Insights, Copilot Studio Analytics export, or Dataverse session count)
4. Action: **Condition** — if rate > firm-defined threshold (e.g., 2% for Zone 3):
   - **Post message** in Teams *AI Governance — Trends* channel
   - **Create item** in `Trend Alerts` list (separate list, similar schema)

---

### Part 5: Build the Power BI Trend Dashboard

**Portal Path:** [Power BI Service](https://app.powerbi.com) → **+ New** → **Dataset** → **SharePoint Online list**

1. Sign in with the AI Governance Lead account
2. Create a new dataset connected to the `Hallucination Tracking` list
3. (Optional) Add a second source for the **Copilot Studio Analytics export** (CSV) or **Dataverse conversation transcripts** to compute hallucination rate
4. Build the report with these visuals:

| Visual | Field(s) | Purpose |
|--------|----------|---------|
| KPI: Total reports (30d) | Count of `IssueID` | Volume signal |
| KPI: Critical (30d) | Count where `ConfirmedSeverity = Critical` | Risk signal |
| KPI: MTTR (30d) | Avg(`ResolutionDate` - `ReportDate`) | Remediation velocity |
| KPI: SLA compliance % | Count(`TriageSLAMet = Yes`) / Total | Process health |
| Stacked column: Reports by category over time | `ReportDate` × `Category` | Pattern detection |
| Bar: Reports by agent | `AgentName` × Count | Identify problem agents |
| Donut: Root cause distribution | `RootCause` | Inform mitigation strategy |
| Table: Open critical issues | Filtered to `Status != Closed` and `ConfirmedSeverity = Critical` | Operational worklist |

5. **Publish** to a workspace named `AI Governance — Pillar 3 Reporting`
6. **Schedule refresh** every 4 hours (Zone 3) or daily (Zone 2)
7. Share the workspace with **AI Governance Lead**, **Compliance Officer**, and **AI Administrator**

---

### Part 6: Document the Process

Create a one-page run-sheet stored alongside the SharePoint list, referencing:

- The taxonomy and severity definitions from Part 2
- The intake URL and flow ownership from Part 4
- The dashboard URL from Part 5
- Escalation contacts (AI Governance Lead, Compliance Officer, agent owners)
- Pointer to the parent control and to Control 3.4 (incident escalation)

> The run-sheet itself becomes evidence under FINRA Rule 4511 (books and records of supervisory procedures).

---

## Validation

After completing the configuration, verify:

1. [ ] CSAT is enabled and published on every agent in scope (capture screenshot per agent)
2. [ ] `Report Inaccurate Response` topic is published and reachable from the agent
3. [ ] Hallucination Tracking list exists with all schema columns and the Purview retention label applied
4. [ ] Intake flow (`HFL-Intake-3.10`) succeeds end-to-end with a synthetic test report
5. [ ] SLA monitor flow runs hourly and updates `TriageSLAMet` / `RemediationSLAMet` correctly
6. [ ] Trend detection flow runs daily and posts to Teams when the threshold is exceeded
7. [ ] Power BI dashboard loads with non-empty data after the synthetic test
8. [ ] Critical-severity test triggers the Control 3.4 incident path

**Expected Result:** A user-submitted thumbs-down or `report a hallucination` utterance creates a tracked item within 60 seconds, applies the correct SLA, and (for Critical) escalates to incident response within the same workflow.

---

## Sovereign Cloud Considerations

For **GCC**, **GCC High**, or **DoD** tenants:

- Substitute the regional Copilot Studio, SharePoint, Power Automate, and Power BI URLs (`*.gov.us`, `*.us`, etc.)
- Verify CSAT is available in your sovereign cloud — feature parity has historically lagged commercial; check the Copilot Studio release notes for your cloud
- Power Automate connectors for Teams notifications must use the sovereign-cloud connector variant
- Confirm the Purview retention label is published to the sovereign tenant before applying it

---

## Next Steps

- [PowerShell Setup](./powershell-setup.md) — Automate list provisioning, intake, and metrics
- [Verification & Testing](./verification-testing.md) — Test cases and audit evidence
- [Troubleshooting](./troubleshooting.md) — Common issues and resolutions

---

[Back to Control 3.10](../../../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md)

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*
