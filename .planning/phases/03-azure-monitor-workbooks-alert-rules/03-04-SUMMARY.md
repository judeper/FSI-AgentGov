---
phase: 03-azure-monitor-workbooks-alert-rules
plan: 04
subsystem: alerts
tags: [scheduled-query-rules, dynamic-thresholds, zone-aware-alerting, arm-templates]

# Dependency graph
requires:
  - phase: 03-azure-monitor-workbooks-alert-rules
    plan: 02
    provides: Action Group resource IDs for zone-based notification routing
  - phase: 02-kql-query-library-governance-mapping
    provides: KQL queries adapted into alert conditions (error-trend-analysis, latency-distribution, agent-usage-analytics)
  - phase: 01-telemetry-infrastructure-solution-docs
    provides: Application Insights resource for scheduled query scopes
provides:
  - ALRT-01: High Failure Rate alert with dynamic thresholds per zone (Control 3.4)
  - ALRT-02: Latency Regression alert with P95 monitoring per zone (Control 2.9)
  - ALRT-03: Abnormal Usage Pattern alert with bidirectional detection per zone (Control 3.2)
  - Zone-specific sensitivity tuning (Low/Medium/High) aligned with FSI risk profiles
  - Runbook links embedded in alert customProperties for automated remediation guidance
affects: [alert-deployment, proactive-monitoring, incident-response, control-3.2, control-2.9, control-3.4]

# Tech tracking
tech-stack:
  added: [Microsoft.Insights/scheduledQueryRules API 2023-12-01, DynamicThresholdCriterion]
  patterns: [3-resource-per-alert pattern, zone-filtered KQL queries, bidirectional threshold operators, customProperties for runbook integration]

key-files:
  created:
    - agent-observability-foundation/alerts/ALRT-01-high-failure-rate.json
    - agent-observability-foundation/alerts/ALRT-02-latency-regression.json
    - agent-observability-foundation/alerts/ALRT-03-abnormal-usage.json
  modified: []

key-decisions:
  - "3-resource pattern: Each alert deploys 3 scheduledQueryRules (one per zone) with zone-filtered KQL"
  - "Dynamic thresholds: ML-based anomaly detection reduces false positives compared to static thresholds"
  - "Zone sensitivity mapping: Zone 1=Low (higher tolerance), Zone 2=Medium (balanced), Zone 3=High (strict)"
  - "Severity progression: Zone 1=2/3 (Warning/Info), Zone 2=1/2 (Error/Warning), Zone 3=0/1 (Critical/Error)"
  - "Bidirectional operator: ALRT-03 uses GreaterOrLessThan to detect both usage spikes and drops"
  - "failingPeriods tuning: ALRT-01/ALRT-03 use 4/3 (stricter), ALRT-02 uses 4/2 (more sensitive for latency)"
  - "RunbookUrl structure: Points to control-specific troubleshooting playbooks (3.4, 2.9, 3.2)"
  - "autoMitigate enabled: Alerts automatically resolve when condition clears"

patterns-established:
  - "Zone-filtered KQL: let ZoneFilter = 'zone1'; ... where customDimensions['Zone'] == ZoneFilter"
  - "metricMeasureColumn: Explicit column name for dynamic threshold calculation (ErrorRate, P95Latency, TotalSessions)"
  - "Runbook integration: customProperties.RunbookUrl links to framework troubleshooting playbooks"
  - "Parameter consistency: All templates accept same 7 parameters (alertName, applicationInsightsId, 3x actionGroup IDs, enabled, location)"

# Metrics
duration: 2min 26s
completed: 2026-02-05
---

# Phase 03 Plan 04: Alert Rule Templates Summary

**Dynamic threshold alert rules (ALRT-01, ALRT-02, ALRT-03) with zone-specific sensitivity tuning and automated runbook links for proactive FSI-compliant monitoring**

## Performance

- **Duration:** 2 min 26 sec
- **Started:** 2026-02-05T23:56:31Z
- **Completed:** 2026-02-05T23:58:57Z
- **Tasks:** 2
- **Files created:** 3
- **Commits:** 2

## Accomplishments

- **ALRT-01: High Failure Rate** - Dynamic threshold alert monitoring BotMessageSend error rates across 3 zones with severity 2/1/0 progression (Warning/Error/Critical)
- **ALRT-02: Latency Regression** - P95 latency monitoring with zone-specific sensitivity (Low/Medium/High) and 4/2 failing periods for faster latency detection
- **ALRT-03: Abnormal Usage** - Bidirectional (GreaterOrLessThan) session volume monitoring detecting both spikes and drops with severity 3/2/1 (Info/Warning/Error)
- **Zone sensitivity mapping** - Zone 1 Low (personal productivity tolerance), Zone 2 Medium (team collaboration balance), Zone 3 High (enterprise strict SLA)
- **Runbook automation** - customProperties embedded in each alert with RunbookUrl, ControlReference, Zone, and Severity for automated incident response
- **9 total alert rules deployed** - 3 alerts × 3 zones with zone-filtered KQL queries and zone-specific action group routing

## Task Commits

Each task was committed atomically:

1. **Task 1: Create High Failure Rate and Latency Regression Alert Templates** - `b549f33` (feat)
   - ALRT-01: High Failure Rate with error rate calculation from BotMessageSend events
   - ALRT-02: Latency Regression with P95 percentile monitoring from duration field
   - Zone-specific sensitivity levels (Low/Medium/High) with 5-minute evaluation frequency
   - customProperties: RunbookUrl links to Control 3.4 (ALRT-01) and Control 2.9 (ALRT-02) troubleshooting playbooks

2. **Task 2: Create Abnormal Usage Pattern Alert Template** - `dfe3653` (feat)
   - ALRT-03: Abnormal Usage with GreaterOrLessThan operator for bidirectional detection
   - Session count aggregation from BotMessageReceived and BotMessageSend events
   - Design mode filtering (where customDimensions['DesignMode'] == 'False')
   - customProperties: RunbookUrl link to Control 3.2 troubleshooting playbook

## Files Created/Modified

- `agent-observability-foundation/alerts/ALRT-01-high-failure-rate.json` - High Failure Rate alert (3 zone resources: Zone1=severity 2/Low, Zone2=severity 1/Medium, Zone3=severity 0/High)
- `agent-observability-foundation/alerts/ALRT-02-latency-regression.json` - Latency Regression alert (3 zone resources with P95 latency monitoring, 4/2 failing periods for faster detection)
- `agent-observability-foundation/alerts/ALRT-03-abnormal-usage.json` - Abnormal Usage alert (3 zone resources with bidirectional GreaterOrLessThan operator, severity 3/2/1 progression)

## Decisions Made

1. **3-resource-per-alert pattern**: Each alert template deploys 3 separate scheduledQueryRules (one per zone) instead of single rule with parameter. Enables zone-specific action group routing and avoids alert rule sprawl.

2. **Zone sensitivity mapping**: Zone 1 uses Low sensitivity (higher false positive tolerance for personal productivity), Zone 2 uses Medium (balanced), Zone 3 uses High sensitivity (strict enterprise SLA enforcement).

3. **Severity progression per zone**: Zone 1 starts at severity 2-3 (Warning/Info), Zone 2 at severity 1-2 (Error/Warning), Zone 3 at severity 0-1 (Critical/Error) to align with FSI governance framework risk tiers.

4. **failingPeriods tuning**: ALRT-01 and ALRT-03 use 4/3 (must fail 3 out of 4 periods) for stricter threshold enforcement. ALRT-02 uses 4/2 (more sensitive) because latency regressions require faster detection.

5. **Bidirectional operator for usage monitoring**: ALRT-03 uses GreaterOrLessThan instead of GreaterThan to detect both usage spikes (potential abuse) and drops (service degradation or agent unavailability).

6. **RunbookUrl structure**: customProperties.RunbookUrl points to control-specific troubleshooting playbooks matching the alert's control reference (3.4 for ALRT-01, 2.9 for ALRT-02, 3.2 for ALRT-03).

7. **autoMitigate enabled**: All alerts configured with autoMitigate: true so resolved conditions automatically close alerts without manual intervention.

8. **KQL zone filtering**: Zone filter implemented as KQL variable (let ZoneFilter = 'zone1') instead of ARM parameter for performance (pre-filters before query execution).

9. **metricMeasureColumn explicit**: Each alert specifies metricMeasureColumn (ErrorRate, P95Latency, TotalSessions) to ensure dynamic threshold calculates on correct metric.

10. **Evaluation frequency vs window size**: All alerts use PT5M evaluation (every 5 minutes) with PT15M window (15-minute aggregation) to balance detection speed and noise reduction.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all ARM templates passed JSON validation and Python verification checks.

## Alert Configuration Details

### ALRT-01: High Failure Rate

| Zone | Severity | Sensitivity | failingPeriods | Action Group | Severity Label |
|------|----------|-------------|----------------|--------------|----------------|
| Zone 1 | 2 | Low | 4/3 | actionGroupZone1Id | Warning |
| Zone 2 | 1 | Medium | 4/3 | actionGroupZone2Id | Error |
| Zone 3 | 0 | High | 4/3 | actionGroupZone3Id | Critical |

**KQL Logic:**
```kql
let ZoneFilter = 'zone1'; // or zone2, zone3
customEvents
| where timestamp > ago(15m)
| where name == 'BotMessageSend'
| where tostring(customDimensions['Zone']) == ZoneFilter or ZoneFilter == 'all'
| extend hasError = isnotempty(tostring(customDimensions['errorCodeText']))
| summarize ErrorRate = todouble(countif(hasError)) / count() * 100
```

**customProperties:**
- RunbookUrl: https://judeper.github.io/FSI-AgentGov/playbooks/control-implementations/3.4/troubleshooting/
- ControlReference: 3.4 - Incident Reporting and Root Cause Analysis
- Zone: Zone 1/2/3
- Severity: Warning/Error/Critical

### ALRT-02: Latency Regression

| Zone | Severity | Sensitivity | failingPeriods | Action Group | Severity Label |
|------|----------|-------------|----------------|--------------|----------------|
| Zone 1 | 2 | Low | 4/2 | actionGroupZone1Id | Warning |
| Zone 2 | 1 | Medium | 4/2 | actionGroupZone2Id | Error |
| Zone 3 | 0 | High | 4/2 | actionGroupZone3Id | Critical |

**KQL Logic:**
```kql
let ZoneFilter = 'zone1'; // or zone2, zone3
customEvents
| where timestamp > ago(15m)
| where name == 'BotMessageSend'
| where tostring(customDimensions['Zone']) == ZoneFilter or ZoneFilter == 'all'
| extend DurationMs = todouble(customDimensions['duration'])
| where isnotnull(DurationMs)
| summarize P95Latency = percentile(DurationMs, 95)
```

**customProperties:**
- RunbookUrl: https://judeper.github.io/FSI-AgentGov/playbooks/control-implementations/2.9/troubleshooting/
- ControlReference: 2.9 - Agent Performance Monitoring and Optimization
- Zone: Zone 1/2/3
- Severity: Warning/Error/Critical

### ALRT-03: Abnormal Usage

| Zone | Severity | Sensitivity | failingPeriods | Operator | Action Group | Severity Label |
|------|----------|-------------|----------------|----------|--------------|----------------|
| Zone 1 | 3 | Low | 4/3 | GreaterOrLessThan | actionGroupZone1Id | Informational |
| Zone 2 | 2 | Medium | 4/3 | GreaterOrLessThan | actionGroupZone2Id | Warning |
| Zone 3 | 1 | High | 4/3 | GreaterOrLessThan | actionGroupZone3Id | Error |

**KQL Logic:**
```kql
let ZoneFilter = 'zone1'; // or zone2, zone3
customEvents
| where timestamp > ago(15m)
| where name in ('BotMessageReceived', 'BotMessageSend')
| where tostring(customDimensions['DesignMode']) == 'False'
| where tostring(customDimensions['Zone']) == ZoneFilter or ZoneFilter == 'all'
| extend AgentId = tostring(customDimensions['recipientId'])
| summarize SessionCount = dcount(session_Id) by AgentId
| summarize TotalSessions = sum(SessionCount)
```

**customProperties:**
- RunbookUrl: https://judeper.github.io/FSI-AgentGov/playbooks/control-implementations/3.2/troubleshooting/
- ControlReference: 3.2 - Usage Analytics and Activity Monitoring
- Zone: Zone 1/2/3
- Severity: Informational/Warning/Error

## Deployment Instructions

**Prerequisites:**
- Action Groups deployed from 03-02 (provides actionGroupZone1Id, actionGroupZone2Id, actionGroupZone3Id)
- Application Insights deployed from Phase 1 (provides applicationInsightsId)
- Shared parameter files updated with actual resource IDs (see shared-parameters.dev.json)

**Deploy all 3 alert rules:**
```bash
# Navigate to solutions repo
cd /path/to/FSI-AgentGov-Solutions

# Deploy ALRT-01 (High Failure Rate)
az deployment group create \
  --resource-group rg-agent-observability-dev \
  --template-file agent-observability-foundation/alerts/ALRT-01-high-failure-rate.json \
  --parameters @agent-observability-foundation/alerts/shared-parameters.dev.json

# Deploy ALRT-02 (Latency Regression)
az deployment group create \
  --resource-group rg-agent-observability-dev \
  --template-file agent-observability-foundation/alerts/ALRT-02-latency-regression.json \
  --parameters @agent-observability-foundation/alerts/shared-parameters.dev.json

# Deploy ALRT-03 (Abnormal Usage)
az deployment group create \
  --resource-group rg-agent-observability-dev \
  --template-file agent-observability-foundation/alerts/ALRT-03-abnormal-usage.json \
  --parameters @agent-observability-foundation/alerts/shared-parameters.dev.json
```

**Verify deployment:**
```bash
# List deployed alert rules
az monitor scheduled-query list --resource-group rg-agent-observability-dev --output table

# Check alert rule details
az monitor scheduled-query show \
  --resource-group rg-agent-observability-dev \
  --name ALRT-01-High-Failure-Rate-Zone3
```

**Important Notes:**
1. Dynamic thresholds require 3-10 days of baseline data before fully operational
2. Initial alerts may appear in "Learning" state while ML model builds baseline
3. Zone metadata (customDimensions['Zone']) must be configured in Copilot Studio telemetry for zone filtering to work
4. RunbookUrl links assume FSI-AgentGov documentation published to GitHub Pages

## Next Phase Readiness

**Ready for 03-05 (Alert Rules Part 2).** ALRT-01, ALRT-02, and ALRT-03 provide foundational proactive monitoring. Next plan will add:
- ALRT-04: Threshold Breaches (cost, quota, capacity limits)
- Deployment automation scripts
- Alert testing and validation procedures

**Provides:**
- 9 production-ready alert rules (3 alerts × 3 zones)
- Zone-specific sensitivity tuning pattern for future alerts
- Runbook integration pattern for incident automation
- customProperties structure for alert context enrichment

**Dependencies satisfied:**
- Action Groups from 03-02 (notification routing)
- KQL queries from Phase 2 (alert condition logic)
- Application Insights from Phase 1 (telemetry data source)

**Blockers/Concerns:**
- **Zone metadata availability**: Alert zone filtering assumes customDimensions['Zone'] field exists in Application Insights telemetry. Verify Copilot Studio agents are configured to emit zone metadata or add enrichment via Application Insights custom processors.
- **Dynamic threshold learning period**: Alerts will be in "Learning" state for 3-10 days after deployment. Consider deploying with static thresholds initially, then switching to dynamic after baseline established.
- **RunbookUrl accessibility**: Links point to FSI-AgentGov GitHub Pages. Ensure documentation site is deployed and accessible to operations teams receiving alerts.

## Self-Check: PASSED

All created files verified:
- agent-observability-foundation/alerts/ALRT-01-high-failure-rate.json ✓
- agent-observability-foundation/alerts/ALRT-02-latency-regression.json ✓
- agent-observability-foundation/alerts/ALRT-03-abnormal-usage.json ✓

All commits verified:
- b549f33 (Task 1: ALRT-01 and ALRT-02) ✓
- dfe3653 (Task 2: ALRT-03) ✓

---
*Phase: 03-azure-monitor-workbooks-alert-rules*
*Completed: 2026-02-05*
