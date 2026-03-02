# Control 3.10: Hallucination Feedback Loop - Screenshot Specifications

## Required Screenshots

### Screenshot 1: Customer Satisfaction Settings
**Portal Path:** Copilot Studio → Agents → [Agent] → Settings → Customer Satisfaction
**What to capture:**
- Thumbs up/down feedback mechanism enabled
- CSAT survey configuration
- Feedback collection toggle status

### Screenshot 2: Copilot Studio Analytics - Customer Satisfaction
**Portal Path:** Copilot Studio → Agents → [Agent] → Analytics → Customer Satisfaction
**What to capture:**
- CSAT score trends over time
- Thumbs down volume and patterns
- Session-level feedback breakdown

### Screenshot 3: Hallucination Tracking List
**Portal Path:** SharePoint → [Governance Site] → Hallucination Tracking List (or ServiceNow/Jira integration)
**What to capture:**
- Tracking list with hallucination taxonomy categories (Factual Error, Fabrication, Outdated, Misattribution, Calculation Error, Conflation, Overconfidence, Misleading)
- Severity classification and SLA assignment (Critical: 4hrs, High: 24hrs, Medium: 72hrs)
- Remediation status workflow stages

### Screenshot 4: Remediation Workflow
**Portal Path:** Power Automate → Flows → Hallucination Remediation Workflow
**What to capture:**
- Automated routing and escalation flow triggered by feedback
- Severity-based SLA assignment logic
- Notification configuration for stakeholders

### Screenshot 5: Trend Reporting Dashboard
**Portal Path:** Power BI → Hallucination Trend Dashboard
**What to capture:**
- Hallucination rate metrics over time
- Mean time to resolution (MTTR) by severity
- Category distribution charts
- Agent-level quality comparison

### Screenshot 6: Application Insights Conversation Analysis
**Portal Path:** Azure Portal → Application Insights → [Resource] → Custom events
**What to capture:**
- Custom telemetry events for flagged conversations
- Conversation transcript details for root cause analysis
- Response confidence data (if available)

---

## Notes for Verification
- No automated hallucination detection exists in Copilot Studio; all identification relies on manual user feedback
- Capture from pre-production environment when possible
- Ensure conversation content is representative but not sensitive
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates

---

[Back to Control 3.10](../../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md)
