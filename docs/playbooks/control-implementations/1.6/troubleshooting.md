# Control 1.6: Microsoft Purview DSPM for AI - Troubleshooting

> This playbook provides troubleshooting guidance for [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md).

---

## Common Issues

### Issue: DSPM Dashboard Shows No AI Interactions

**Symptoms:** Overview displays zero interactions despite active Copilot usage

**Solutions:**

1. Verify unified audit logging is enabled (Get Started step 1)
2. Check that users have Microsoft 365 Copilot licenses assigned
3. Wait 24-48 hours for initial data population
4. Verify date range filter in reports
5. Confirm users are actually using Copilot features

---

### Issue: Browser Extension Not Capturing Third-Party AI

**Symptoms:** ChatGPT, Claude, other AI usage not appearing in reports

**Solutions:**

1. Verify extension deployment via Intune/Endpoint Manager
2. Check extension is enabled in user browsers
3. Confirm AI domains are in the monitored list
4. Verify users are signed in to browser with work account
5. Check extension version is current

---

### Issue: Recommendations Not Updating

**Symptoms:** Completed actions still show as pending in Recommendations

**Solutions:**

1. Manually mark recommendation as complete if action was taken
2. Refresh the browser/dashboard
3. Wait for sync (can take up to 24 hours)
4. Verify the action was fully completed in source system
5. Contact Microsoft support if stuck for >48 hours

---

### Issue: Activity Explorer Missing Expected Events

**Symptoms:** Known AI interactions not appearing in Activity explorer

**Solutions:**

1. Adjust date range filter to include event timeframe
2. Check filter settings (user, app, activity type)
3. Verify audit retention policy hasn't deleted events
4. Confirm user/app is in scope for monitoring
5. Export all data and search manually if needed

---

### Issue: Oversharing Assessment Returns Errors

**Symptoms:** Data risk assessment fails or shows errors

**Solutions:**

1. Verify SharePoint sites are accessible
2. Check permissions to run assessments
3. Ensure sites aren't in a locked/read-only state
4. Reduce scope and retry with smaller site set
5. Check service health for Purview/SharePoint issues

---

### Issue: DSPM for AI Not Visible in Navigation

**Symptoms:** Cannot find DSPM for AI in Purview portal

**Solutions:**

1. Verify E5 or E5 Compliance license is assigned
2. Check Purview Compliance Admin role is assigned
3. Clear browser cache and refresh
4. Try a different browser
5. Verify tenant region supports DSPM for AI

---

### Issue: Policies Not Syncing from Other Solutions

**Symptoms:** DLP or IRM policies not appearing in DSPM Policies view

**Solutions:**

1. Verify policies exist in their native solution
2. Check policy is enabled (not in test mode only)
3. Wait for sync (can take several hours)
4. Refresh the DSPM Policies page
5. Verify permissions to view policies

---

## Enhanced DSPM AI Observability Troubleshooting (Preview)

### Issue: Unified DSPM Experience Not Visible

**Symptoms:** Cannot find "Data Security Posture Management" in Purview navigation; only classic "DSPM for AI" appears

**Solutions:**

1. Verify tenant is in preview ring:
   - Check Message Center for MC1191257 (unified DSPM experience rollout notification)
   - If notification not received, tenant not yet in preview ring
   - GA expected June 2026; unified experience will become available for all tenants at GA
2. Complete DSPM for AI Get Started wizard:
   - Unified experience migration requires all four Get Started steps completed
   - Navigate to **Purview > DSPM for AI > Overview** and complete wizard
3. Check tenant preview ring enrollment:
   - Navigate to **M365 Admin Center > Settings > Org settings > Organization profile**
   - Verify "Targeted release for entire organization" OR "Targeted release for selected users" is enabled
   - Note: Not all targeted release tenants receive preview immediately; gradual rollout
4. Verify licensing:
   - Unified DSPM experience requires E5 Compliance or Microsoft 365 E5
   - Verify license assignment: **M365 Admin Center > Users > Active users > [User] > Licenses**
5. Clear browser cache and retry:
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Try incognito/private browsing window
   - Try different browser (Edge, Chrome)

**Workaround:** Use classic DSPM for AI until unified experience becomes available for your tenant. Core functionality (weekly risk assessments, Activity Explorer, oversharing detection) remains available in classic experience.

---

### Issue: Agent Risk Data Not Populating

**Symptoms:** Agent risk observability dashboard shows "No data available" or agents listed with "Insufficient Data" risk status

**Solutions:**

1. Verify Application Insights integration:
   - Unified DSPM agent risk scoring requires Application Insights telemetry
   - Navigate to **Azure Portal > Application Insights > [Your AI Instance]**
   - Verify "Logs" section shows AI agent telemetry events (search for `customEvents` or `traces` tables)
   - Check data ingestion latency: **Application Insights > Overview > Data ingestion volume**
2. Check Observability SDK configuration (for Agent 365 SDK agents):
   - Agent 365 SDK agents require Observability SDK integration for risk scoring
   - Verify agent code includes: `import { observability } from '@microsoft/agent-sdk'`
   - Check Observability SDK telemetry export: Agent settings should include Application Insights connection string
   - See [Microsoft 365 Agents SDK documentation](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/m365-agents-sdk) for configuration guidance
3. Verify agent activity baseline:
   - Risk scoring requires 7-14 days of agent activity to establish baseline
   - Check agent has generated sufficient events: **Activity Explorer** should show 50+ events for agent
   - New agents deployed <7 days ago may show "Insufficient Data" until baseline established
4. Check data latency:
   - Agent risk scores update weekly (typically Sunday night)
   - Last risk assessment date shown on dashboard; if >7 days old, risk scoring may be delayed
   - Wait 24-48 hours after first agent activity before expecting risk data
5. Verify DSPM for AI Get Started completion:
   - Navigate to **Purview > DSPM for AI > Overview**
   - Confirm all four Get Started steps show "Completed" status
   - Extended Insights (Step 4) required for comprehensive risk scoring

**Workaround:** Use Activity Explorer enhanced filters to manually review agent activity and identify high-risk patterns (excessive data access, policy violations) until automated risk scoring populates.

---

### Issue: Activity Explorer Missing AI Events

**Symptoms:** Activity Explorer shows no AI interaction events despite active Copilot or agent usage

**Solutions:**

1. Verify audit logging enabled:
   - Navigate to **Purview > Audit > Audit** (main page)
   - Confirm "Start recording user and admin activity" banner is NOT present
   - If banner present, click "Start recording" and wait 24 hours for events to populate
   - Verify unified audit log ingestion: PowerShell `Get-AdminAuditLogConfig | Select UnifiedAuditLogIngestionEnabled` should return `True`
2. Check Activity Explorer filters:
   - Ensure date range includes recent activity (last 7-30 days)
   - Clear all filters and verify events appear
   - Try broadening "AI app category" filter to "All AI apps"
3. Verify audit retention policy:
   - Navigate to **Purview > Audit > Audit retention policies**
   - Confirm retention period includes desired date range (minimum 90 days for FSI compliance)
   - If events older than retention period, they are permanently deleted and unrecoverable
4. Check agent activity type:
   - Not all agent interactions generate Activity Explorer events
   - Copilot Studio agents: Interactions logged if DLP or sensitivity label policy applies
   - Agent Builder agents: Interactions logged via Observability SDK telemetry
   - M365 Copilot: Interactions logged if involving sensitive data or policy enforcement
5. Verify user/agent in scope:
   - Check agent is published and active (not in draft mode)
   - Verify users interacting with agent have licenses (M365 Copilot or appropriate agent license)
   - Confirm user is not excluded from audit logging via retention policy

**Workaround:** Export audit log data via PowerShell `Search-UnifiedAuditLog` and filter for AI-related operations manually. See PowerShell Setup playbook for export script.

---

## Escalation Path

If issues persist after troubleshooting:

1. **First tier**: Purview Compliance Admin - verify configuration
2. **Second tier**: Security Operations - check integration issues
3. **Third tier**: Microsoft Support - platform-level issues

---

*Updated: January 2026 | Version: v1.2*
