---
phase: 03-azure-monitor-workbooks-alert-rules
plan: 02
subsystem: alerts
tags: [azure-monitor, action-groups, logic-apps, teams-notifications, arm-templates]

# Dependency graph
requires:
  - phase: 02-kql-query-library-governance-mapping
    provides: KQL query library with workbook parameter syntax
  - phase: 01-telemetry-infrastructure-solution-docs
    provides: Application Insights and Log Analytics Workspace infrastructure
provides:
  - Zone-specific action groups (3) routing alerts to appropriate Teams channels
  - Logic App for Teams schema transformation (common alert schema parsing)
  - Shared parameter files (dev/prod) for alert deployments
  - Foundation for alert rule templates in subsequent plans
affects: [03-03-alert-rules, alert-deployment, teams-integration]

# Tech tracking
tech-stack:
  added: [Microsoft.Insights/actionGroups, Microsoft.Logic/workflows, Teams API connection]
  patterns: [Zone-based notification routing, Common alert schema, Logic App intermediary pattern]

key-files:
  created:
    - agent-observability-foundation/alerts/action-groups/logic-app-teams-notification.json
    - agent-observability-foundation/alerts/action-groups/action-group-zone1.json
    - agent-observability-foundation/alerts/action-groups/action-group-zone2.json
    - agent-observability-foundation/alerts/action-groups/action-group-zone3.json
    - agent-observability-foundation/alerts/shared-parameters.dev.json
    - agent-observability-foundation/alerts/shared-parameters.prod.json
  modified: []

key-decisions:
  - "Logic App intermediary required for Teams (direct webhooks produce malformed messages)"
  - "Zone-based routing: Zone 1→general ops, Zone 2→team ops, Zone 3→enterprise ops"
  - "Both email (audit trail) and Teams (real-time) notifications per user decision"
  - "Common alert schema enabled across all receivers for consistent payload structure"
  - "Severity color coding: Sev0=red, Sev1=orange, Sev2=yellow"

patterns-established:
  - "ARM template structure: parameters → resources → outputs with metadata"
  - "Shared parameter files enable environment-specific configuration"
  - "Custom properties in alerts: RunbookUrl, Zone, ControlReference"

# Metrics
duration: 2min 11s
completed: 2026-02-05
---

# Phase 03 Plan 02: Action Groups and Teams Notification Summary

**Zone-specific Action Groups with Logic App Teams integration providing risk-based alert routing per FSI governance zones**

## Performance

- **Duration:** 2 min 11 sec
- **Started:** 2026-02-05T23:50:08Z
- **Completed:** 2026-02-05T23:52:19Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Logic App ARM template for Teams schema transformation with severity color coding (Sev0=red, Sev1=orange, Sev2=yellow)
- Three zone-specific Action Groups routing alerts per FSI governance model (Zone 1→general, Zone 2→team ops, Zone 3→enterprise ops)
- Shared parameter files (dev/prod) enabling environment-specific alert deployments
- Common alert schema enabled across all receivers (email and Logic App) for consistent payload structure
- Custom properties support: RunbookUrl, Zone, ControlReference

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Logic App and Zone Action Group ARM Templates** - `a5ffbbb` (feat)
   - Logic App: Microsoft.Logic/workflows with HTTP trigger and Teams API connection
   - Zone 1 Action Group: Microsoft.Insights/actionGroups with general ops routing
   - Zone 2 Action Group: Microsoft.Insights/actionGroups with team ops routing
   - Zone 3 Action Group: Microsoft.Insights/actionGroups with enterprise ops routing

2. **Task 2: Create Shared Parameter Files** - `2ab14bc` (feat)
   - Dev environment parameters: 8 parameters including Application Insights, Log Analytics, email, Teams Logic App, 3 zone action groups
   - Prod environment parameters: Same structure with prod-specific resource IDs and email addresses

## Files Created/Modified

- `agent-observability-foundation/alerts/action-groups/logic-app-teams-notification.json` - Logic App (Consumption tier) for Teams schema transformation with common alert schema parsing
- `agent-observability-foundation/alerts/action-groups/action-group-zone1.json` - Zone 1 (Personal Productivity) Action Group with general ops channel routing
- `agent-observability-foundation/alerts/action-groups/action-group-zone2.json` - Zone 2 (Team Collaboration) Action Group with team ops channel routing
- `agent-observability-foundation/alerts/action-groups/action-group-zone3.json` - Zone 3 (Enterprise Managed) Action Group with enterprise ops channel routing
- `agent-observability-foundation/alerts/shared-parameters.dev.json` - Dev environment shared parameters (8 parameters)
- `agent-observability-foundation/alerts/shared-parameters.prod.json` - Prod environment shared parameters (8 parameters)

## Decisions Made

1. **Logic App intermediary pattern**: Direct Teams webhooks produce malformed messages; Logic App provides schema transformation layer
2. **Zone-based routing**: Zone 1→general ops channel, Zone 2→team ops channel, Zone 3→enterprise ops channel (matches FSI risk-based governance model)
3. **Dual notification channels**: Email (audit trail for SEC 17a-4 compliance) + Teams (real-time alerting) per user decision during planning
4. **Common alert schema**: Enabled across all receivers (emailReceivers, logicAppReceivers) for consistent payload structure
5. **Severity color coding**: Sev0=red (#ff0000), Sev1=orange (#ff8c00), Sev2=yellow (#ffd700) for visual priority signaling
6. **Custom properties structure**: RunbookUrl (remediation link), Zone (governance zone), ControlReference (framework control ID)
7. **Shared parameters approach**: Environment-specific parameter files (dev/prod) enable consistent deployments across environments
8. **API version selection**: actionGroups 2023-01-01, Logic Apps 2019-05-01 (stable versions for production)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all ARM templates validated successfully, parameter files passed schema checks.

## User Setup Required

**Post-deployment configuration required.** After deploying these templates, users must:

1. **Deploy Logic App first** to obtain callback URL:
   ```bash
   az deployment group create \
     --resource-group rg-agent-observability-dev \
     --template-file logic-app-teams-notification.json \
     --parameters logicAppName=fsi-agent-alert-teams-notification-dev
   ```

2. **Capture Logic App callback URL** from deployment outputs:
   ```bash
   az deployment group show \
     --resource-group rg-agent-observability-dev \
     --name logic-app-teams-notification \
     --query properties.outputs.logicAppCallbackUrl.value
   ```

3. **Update shared parameter files** with actual callback URL (replace placeholder in `teamsLogicAppCallbackUrl`)

4. **Configure Teams API connection** in Azure portal:
   - Navigate to Logic App → API connections
   - Authorize Teams connection
   - Replace `TEAM_ID` and `CHANNEL_ID` placeholders in Logic App definition with actual Teams IDs

5. **Deploy Action Groups** referencing the Logic App:
   ```bash
   az deployment group create \
     --resource-group rg-agent-observability-dev \
     --template-file action-group-zone1.json \
     --parameters @shared-parameters.dev.json
   ```

6. **Verify notification flow**:
   - Test alert → Action Group triggers Logic App → Teams message appears
   - Verify email received with common alert schema payload

## Next Phase Readiness

**Ready for 03-03 (Alert Rules).** Action Groups are the notification foundation that alert rules will reference.

**Provides:**
- Zone 1 Action Group ID for Personal Productivity agent alerts
- Zone 2 Action Group ID for Team Collaboration agent alerts
- Zone 3 Action Group ID for Enterprise Managed agent alerts
- Logic App callback URL for direct Logic App receivers (if needed)
- Shared parameter pattern for alert rule deployments

**Dependencies satisfied:**
- Application Insights and Log Analytics Workspace from Phase 1 (01-telemetry-infrastructure)
- KQL queries from Phase 2 (02-kql-query-library) will be referenced in scheduled query rules

**Blockers/Concerns:**
- None - Action Groups are stateless infrastructure, no runtime dependencies

## Self-Check: PASSED

All created files verified:
- agent-observability-foundation/alerts/action-groups/logic-app-teams-notification.json ✓
- agent-observability-foundation/alerts/action-groups/action-group-zone1.json ✓
- agent-observability-foundation/alerts/action-groups/action-group-zone2.json ✓
- agent-observability-foundation/alerts/action-groups/action-group-zone3.json ✓
- agent-observability-foundation/alerts/shared-parameters.dev.json ✓
- agent-observability-foundation/alerts/shared-parameters.prod.json ✓

All commits verified:
- a5ffbbb (Task 1: Logic App and Action Groups) ✓
- 2ab14bc (Task 2: Shared parameter files) ✓

---
*Phase: 03-azure-monitor-workbooks-alert-rules*
*Completed: 2026-02-05*
