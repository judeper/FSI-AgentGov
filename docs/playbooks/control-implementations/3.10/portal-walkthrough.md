# Control 3.10: Hallucination Feedback Loop - Portal Walkthrough

> This playbook provides step-by-step portal configuration guidance for [Control 3.10](../../../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md).

---

## Prerequisites

- Copilot Studio access for agent configuration
- Power Automate license for feedback workflows
- SharePoint site for tracking list
- Power BI Pro for trend reporting

---

## Step 1: Enable User Feedback Collection

**Portal Path:** Copilot Studio > Agent > Settings > Customer satisfaction

1. Open your agent in **Copilot Studio**
2. Navigate to **Settings** > **Customer satisfaction**
3. Enable **Allow users to provide feedback**
4. Configure feedback options:

| Option | Recommendation |
|--------|----------------|
| Thumbs up/down | Always enable |
| Comment box | Enable for detailed feedback |
| Flag for review | Enable for escalation |

---

## Step 2: Define Hallucination Taxonomy

**Hallucination Categories:**

| Category | Description | Severity | Example |
|----------|-------------|----------|---------|
| **Factual Error** | Incorrect facts | High | Wrong interest rate |
| **Fabrication** | Made up information | Critical | Non-existent product |
| **Outdated** | No longer current | Medium | Discontinued service |
| **Misattribution** | Wrong source cited | Medium | Incorrect document |
| **Calculation Error** | Math mistakes | High | Wrong fee calculation |
| **Conflation** | Mixing items | Medium | Different products confused |
| **Overconfidence** | Certainty about uncertain | Medium | "Definitely" vs "likely" |
| **Misleading** | Technically true but deceptive | High | Selective information |

**Severity Classification:**

| Severity | Impact | Response SLA |
|----------|--------|--------------|
| Critical | Customer harm, regulatory risk | 4 hours |
| High | Significant misinformation | 24 hours |
| Medium | Minor inaccuracy | 72 hours |
| Low | Cosmetic/minor | 1 week |

---

## Step 3: Create Hallucination Tracking List

**Portal Path:** SharePoint Site > New > List

Create SharePoint list with columns:

| Column | Type | Required |
|--------|------|----------|
| Issue ID | Auto-number | Yes |
| Report Date | Date/Time | Yes |
| Agent Name | Lookup | Yes |
| Category | Choice | Yes |
| Severity | Choice | Yes |
| User Query | Multi-line | Yes |
| Agent Response | Multi-line | Yes |
| Correct Information | Multi-line | No |
| Source of Truth | Hyperlink | No |
| Status | Choice | Yes |
| Assigned To | Person | Yes |
| Root Cause | Choice | No |
| Remediation Actions | Multi-line | No |
| Resolution Date | Date/Time | No |

---

## Step 4: Configure Automated Workflows

**Portal Path:** Power Automate > Create > Automated cloud flow

**Workflow 1: New Hallucination Report**

```plaintext
Trigger: When feedback marked as hallucination
Actions:
├── Create item in Hallucination Tracking list
├── Capture conversation context
├── Auto-assign based on agent owner
├── If Severity = Critical:
│   ├── Create incident (Control 3.4)
│   ├── Notify Compliance Officer
│   └── Consider temporary suspension
├── Send acknowledgment to reporter
└── Start SLA timer
```

**Workflow 2: Trend Alert**

```plaintext
Trigger: Scheduled (daily)
Actions:
├── Query last 24 hours of reports
├── Calculate hallucination rate per agent
├── If rate > 5%:
│   ├── Alert AI Governance Lead
│   └── Flag agent for review
└── Update trend dashboard
```

---

## Step 5: Establish Remediation Process

**Remediation by Root Cause:**

| Root Cause | Remediation | Owner |
|------------|-------------|-------|
| Knowledge Gap | Update knowledge source | Content Owner |
| Prompt Issue | Modify system prompt | Prompt Engineer |
| Training Data | Flag for retraining | AI Governance |
| Source Conflict | Resolve conflicting sources | Content Owner |
| Configuration | Adjust agent settings | Platform Admin |

---

## Step 6: Configure Trend Reporting

**Power BI Dashboard Metrics:**

| Metric | Calculation | Target |
|--------|-------------|--------|
| Hallucination Rate | Reports / Total Interactions | <2% |
| Critical Hallucinations | Critical / Total Issues | <5% |
| MTTR | Avg resolution time | <72 hours |
| Repeat Rate | Recurrence rate | <5% |
| Open Issues | Unresolved count | <10 |

---

## Step 7: Quality Scoring Framework

**Confidence-Based Actions:**

| Score Range | Quality | Action |
|-------------|---------|--------|
| 0.95 - 1.00 | High | Deliver immediately |
| 0.85 - 0.94 | Medium | Deliver with logging |
| 0.70 - 0.84 | Low | Flag for review |
| Below 0.70 | Very Low | Hold for human review |

---

## Next Steps

- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.2*
