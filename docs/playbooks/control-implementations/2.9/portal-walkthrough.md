# Portal Walkthrough: Control 2.9 - Agent Performance Monitoring and Optimization

**Last Updated:** January 2026
**Portal:** Power Platform Admin Center, Copilot Studio, Power BI
**Estimated Time:** 3-4 hours

## Prerequisites

- [ ] Power Platform Admin role
- [ ] Power BI Pro license (for dashboards)
- [ ] Copilot Studio access
- [ ] KPIs defined for each governance tier

---

## Step-by-Step Configuration

### Step 1: Enable Copilot Studio Analytics

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Navigate to **Analytics** > **Copilot Studio**
3. Verify analytics is enabled (default: enabled)
4. Review available metrics:
   - Sessions and conversations
   - Resolution rate
   - Escalation rate
   - Customer satisfaction (CSAT)
   - Average handling time

### Step 2: Configure Data Export to Azure

1. In Power Platform Admin Center, go to **Data integration** > **Data export**
2. Click **+ New export**
3. Configure export:
   - **Name:** Agent-Analytics-Export
   - **Destination:** Azure Data Lake Storage Gen2
   - **Tables:** Select analytics tables
   - **Frequency:** Daily
4. Save and enable the export

### Step 3: Create Power BI Performance Dashboard

1. Open [Power BI](https://app.powerbi.com)
2. Create new workspace: **Agent-Performance-Analytics**
3. Connect to exported data or Power Platform dataflows
4. Create dashboard with:
   - KPI cards (response time, error rate, CSAT)
   - Trend charts (7-day, 30-day, 90-day)
   - Agent comparison matrix
   - SLA compliance gauge

### Step 4: Configure Alerting

1. Open [Power Automate](https://make.powerautomate.com)
2. Create flow: **Agent Performance Alert**
3. Trigger: Scheduled (hourly or daily)
4. Action: Query analytics for threshold violations
5. Configure conditions by tier:

| Zone | Error Rate Threshold | Response Time Threshold |
|------|---------------------|------------------------|
| Zone 1 | > 5% | > 30 seconds |
| Zone 2 | > 2% | > 15 seconds |
| Zone 3 | > 1% | > 5 seconds |

6. Send Teams notification or email when exceeded

### Step 5: Enable Anomaly Detection (Zone 3)

1. Open [Azure Portal](https://portal.azure.com)
2. Navigate to Azure Monitor > Alerts
3. Create alert rule with smart detection:
   - **Scope:** Application Insights resource
   - **Condition:** Smart detection - anomaly
   - **Actions:** Email AI Governance Lead, Teams channel
4. Configure for Zone 3 agent telemetry

### Step 6: Establish Review Cadence

Document and schedule performance reviews:

| Review Type | Frequency | Attendees | Focus |
|-------------|-----------|-----------|-------|
| Operational | Weekly | Ops team, Agent owners | Issues, incidents |
| Business | Monthly | AI Governance Lead, Stakeholders | KPI trends, optimization |
| Executive | Quarterly | Leadership, Compliance | Strategic metrics, compliance |

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|-------------------|
| **Analytics** | Basic | Standard | Full + anomaly detection |
| **Alerting** | Error rate only | Error + response time | All metrics |
| **Dashboard** | Summary view | Detailed per-agent | Real-time + drill-down |
| **Review** | Monthly | Weekly | Daily + real-time |
| **Data Retention** | 30 days | 90 days | 1 year |

---

## FSI Example Configuration

```yaml
Performance Monitoring: Agent Analytics Configuration

Analytics:
  Copilot Studio: Enabled
  Data Export: Azure Data Lake (daily)
  Retention: 365 days

KPIs by Zone:
  Zone 1 (Personal Productivity):
    Error Rate: < 5%
    Response Time: < 30s
    Resolution Rate: > 70%

  Zone 2 (Team Collaboration):
    Error Rate: < 2%
    Response Time: < 15s
    Resolution Rate: > 85%
    CSAT: > 3.5/5

  Zone 3 (Enterprise Managed):
    Error Rate: < 1%
    Response Time: < 5s
    Resolution Rate: > 95%
    CSAT: > 4.0/5

Alerting:
  Channels: Teams + Email
  Recipients: ai-governance@example.com
  Escalation: CISO (SLA breach)

Dashboards:
  Workspace: Agent-Performance-Analytics
  Refresh: Hourly
  Access: AI Governance Team + Agent Owners
```

---

## Validation

After completing these steps, verify:

- [ ] Copilot Studio analytics shows data
- [ ] Data export running to Azure
- [ ] Power BI dashboard displays current metrics
- [ ] Alert flow triggers on test threshold breach
- [ ] Review meetings scheduled in calendar

---

[Back to Control 2.9](../../../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
