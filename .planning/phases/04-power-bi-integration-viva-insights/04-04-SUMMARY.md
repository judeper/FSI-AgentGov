---
phase: 04
plan: 04
subsystem: agent-observability
tags: [viva-insights, reconciliation, documentation, power-bi, scope-limitations]
requires:
  - "Application Insights telemetry pipeline"
  - "Power BI semantic model structure"
  - "Agent type taxonomy (Copilot Studio, Agent Builder, Agent 365 SDK)"
provides:
  - "Viva Insights scope and limitations documentation"
  - "Cross-system reconciliation workflow"
  - "Gap analysis matrix: Viva Insights vs Application Insights"
  - "Common discrepancy patterns catalog"
affects:
  - "Executive reporting decisions (when to use Viva vs Power BI)"
  - "Compliance evidence planning (Application Insights is authoritative)"
  - "Adoption metrics interpretation (understanding coverage gaps)"
tech-stack:
  added: []
  patterns:
    - "Dual-platform reconciliation (Viva Insights + Application Insights)"
    - "Expected discrepancy modeling (agent type coverage)"
key-files:
  created:
    - agent-observability-foundation/power-bi/docs/viva-insights-scope.md
    - agent-observability-foundation/power-bi/docs/viva-insights-reconciliation.md
  modified: []
decisions:
  - id: VIVA-SCOPE-WARNING
    decision: "Place prominent warning box at top of scope doc before any other content"
    rationale: "Executives need immediate clarity that Viva only covers Copilot Studio Production agents"
    impact: "Prevents misinterpretation of metric discrepancies"
  - id: VIVA-10PCT-THRESHOLD
    decision: "Use 10% variance threshold as investigation trigger"
    rationale: "Balances sensitivity (catches real issues) with tolerance (normal sampling/timing variance)"
    impact: "Weekly reconciliation process triggered only when meaningful discrepancies occur"
  - id: VIVA-APP-INSIGHTS-AUTHORITATIVE
    decision: "Application Insights is authoritative source for all agent types"
    rationale: "Only App Insights covers Agent Builder, Agent 365 SDK, dev/test environments, and compliance evidence"
    impact: "Viva Insights positioned as supplementary adoption view, not primary observability platform"
metrics:
  duration: "3 minutes"
  completed: "2026-02-05"
---

# Phase 04 Plan 04: Viva Insights Scope and Reconciliation Summary

**One-liner:** Documentation clarifying Viva Insights covers only Copilot Studio Production agents, with 7-step reconciliation workflow to explain metric discrepancies vs Application Insights.

## What Was Built

Created two documentation files to prevent executive confusion about Viva Insights limitations and metric discrepancies:

1. **viva-insights-scope.md** — Comprehensive scope and limitations guide
   - Prominent warning box: Copilot Studio Production agents only
   - Preview disclaimer: March 2026 GA expectation
   - Excluded agent types table: Agent Builder, Agent 365 SDK, dev/test environments
   - Excluded metrics table: Performance, compliance, zone governance, cost data
   - Gap analysis matrix: 9 capabilities comparing Viva Insights vs Application Insights
   - Appropriate vs inappropriate use cases
   - Cross-references to reconciliation workflow and Power BI guide

2. **viva-insights-reconciliation.md** — Step-by-step reconciliation workflow
   - 7-step process: Export Viva metrics → Query App Insights → Identify agent types → Calculate expected discrepancy → Compare → Investigate → Document
   - Copy-paste KQL queries for agent type breakdown
   - 10% variance threshold for investigation trigger
   - 5 common discrepancy patterns with resolutions
   - Recommended reconciliation schedule (weekly/monthly/quarterly by audience)
   - Complete example reconciliation scenario with real numbers

## Task Commits

| Task | Name | Commit | Files | Status |
|------|------|--------|-------|--------|
| 1 | Create Viva Insights Scope and Limitations Document | 12df501 | viva-insights-scope.md | ✓ |
| 2 | Create Viva Insights Reconciliation Workflow | 53fcbfe | viva-insights-reconciliation.md | ✓ |

## Decisions Made

### 1. Prominent Warning Box (VIVA-SCOPE-WARNING)
**Decision:** Place warning box at top of scope doc before any other content.
**Why:** Executives scanning the doc need immediate clarity that Viva only covers Copilot Studio Production agents.
**Impact:** Prevents misinterpretation of metric discrepancies ("Why do we have 15 agents in Viva but 28 in App Insights?").

### 2. 10% Variance Threshold (VIVA-10PCT-THRESHOLD)
**Decision:** Use 10% variance as investigation trigger.
**Why:** Balances sensitivity (catches real issues like misconfigured telemetry) with tolerance (normal sampling/timing variance).
**Impact:** Weekly reconciliation process triggered only when meaningful discrepancies occur, not noise.

### 3. Application Insights is Authoritative (VIVA-APP-INSIGHTS-AUTHORITATIVE)
**Decision:** Application Insights is the authoritative data source for all agent types.
**Why:** Only App Insights covers Agent Builder, Agent 365 SDK, dev/test environments, performance metrics, and compliance evidence (FINRA 3110, SEC 17a-4).
**Impact:** Viva Insights positioned as supplementary adoption view for quick executive briefings, not primary observability platform.

## Next Phase Readiness

### Blockers
None.

### Concerns
- **Viva Insights preview state:** March 2026 GA expected — documentation will need refresh if metrics/features change at GA
- **Agent type detection logic:** KQL query in reconciliation workflow assumes custom dimensions exist (`copilotStudioAgent`, `agent365Sdk`) — requires Application Insights custom telemetry from Phase 1

### Prerequisites for Next Plans
- Power BI dashboard must exist for cross-reference links to work (created in plan 04-01)
- Agent usage analytics KQL query must exist for reconciliation workflow (created in Phase 1)

## Deviations from Plan

None — plan executed exactly as written.

## Key Technical Details

### Viva Insights Coverage Scope
| Coverage Area | Viva Insights | Application Insights |
|--------------|:---:|:---:|
| Copilot Studio (Production) | YES | YES |
| Copilot Studio (Dev/Test) | NO | YES |
| Agent Builder | NO | YES |
| Agent 365 SDK | NO | YES |
| Performance metrics | NO | YES |
| Compliance evidence | NO | YES |
| Zone governance | NO | YES |
| Real-time monitoring | NO | YES |
| Historical depth | 28-day initial | 730-day retention |

### Reconciliation Formula
```
Expected Viva Total = Copilot Studio Production agents (from App Insights)
Expected Discrepancy = App Insights Total - Expected Viva Total
Variance = Viva Actual - Expected Viva Total
Investigation Trigger = Variance > 10% of Expected Viva Total
```

### KQL Query Pattern
```kql
// Agent type breakdown
customEvents
| where timestamp between (datetime(start) .. datetime(end))
| where name in ("BotMessageReceived", "BotMessageSend")
| where tostring(customDimensions['DesignMode']) == "False"
| extend
    AgentType = case(
        isnotempty(tostring(customDimensions["copilotStudioAgent"])), "CopilotStudio",
        isnotempty(tostring(customDimensions["agent365Sdk"])), "Agent365SDK",
        "AgentBuilder"
    ),
    IsProduction = tostring(customDimensions["environment"]) == "Production"
| summarize Agents = dcount(AgentId) by AgentType, IsProduction
```

## Integration Points

### Inbound Dependencies
- **Phase 1 (Application Insights):** Requires custom dimensions for agent type detection
- **Plan 04-01 (Power BI Dashboard):** Cross-referenced for comprehensive reporting alternative

### Outbound Usage
- **Executive briefings:** Quick adoption view from Viva Insights, detailed analysis from Power BI
- **Compliance audits:** Application Insights is source of truth (FINRA 3110, SEC 17a-4 evidence)
- **Operations reviews:** Weekly reconciliation catches configuration drift

## Validation Results

All verification checks passed:
- ✓ viva-insights-scope.md has prominent warning box (Copilot Studio agents only)
- ✓ Preview disclaimer with March 2026 GA date present
- ✓ Gap analysis matrix covers 9 capabilities (Agent Inventory, Adoption, Performance, Compliance, Satisfaction, Executive Reporting, Historical Depth, Real-Time Monitoring, Zone Governance)
- ✓ Reconciliation workflow has 7 numbered steps
- ✓ KQL queries are copy-paste ready (2 queries included)
- ✓ 5 common discrepancy patterns with cause/resolution documented
- ✓ 10% variance threshold explicitly documented
- ✓ No prohibited regulatory guarantee language ("ensures compliance", "guarantees", "will prevent", "eliminates risk")

## Lessons Learned

### What Went Well
- **Prominent warning box:** Placing the "Copilot Studio only" warning at the very top (before even the preview disclaimer) ensures executives can't miss it
- **Gap analysis matrix:** The 9-capability comparison table makes it crystal clear where Viva falls short and why App Insights is necessary
- **Example reconciliation:** The worked example with real numbers (15 vs 28 agents) demonstrates the workflow concretely

### What Could Be Improved
- **Agent type detection:** The KQL query assumes custom dimensions exist — should cross-reference Phase 1 telemetry setup docs more explicitly
- **Anonymization threshold:** Viva's 10-person minimum is mentioned but could have more detail on impact for small organizations

### For Future Phases
- **Viva Insights GA refresh:** When Viva goes GA in March 2026, revisit this doc to update preview disclaimers and confirm metrics haven't changed
- **Power BI dashboard screenshots:** Consider adding screenshots of Viva dashboard vs Power BI dashboard side-by-side in the scope doc

## Self-Check: PASSED

✓ Created files exist:
- agent-observability-foundation/power-bi/docs/viva-insights-scope.md
- agent-observability-foundation/power-bi/docs/viva-insights-reconciliation.md

✓ Commits exist:
- 12df501 (Task 1 - Viva Insights scope and limitations)
- 53fcbfe (Task 2 - Viva Insights reconciliation workflow)
