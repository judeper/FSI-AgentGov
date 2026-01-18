# Portal Walkthrough: Control 3.2 - Usage Analytics and Activity Monitoring

**Last Updated:** January 2026
**Portal:** Power Platform Admin Center
**Estimated Time:** 1-2 hours

## Prerequisites

- [ ] Power Platform Administrator role assigned
- [ ] Access to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
- [ ] [Control 2.1: Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md) enabled for target environments
- [ ] [Control 1.7: Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) configured
- [ ] Alert notification recipients identified
- [ ] Monitoring review schedule established

---

## Step-by-Step Configuration

### Step 1: Access the Monitor Section

1. Sign in to **Power Platform Admin Center** ([https://admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com))
2. Navigate to **Monitor** in the left navigation
3. Review the available sub-sections:
   - **Overview** - Platform health summary
   - **Alerts (Preview)** - Alert rules and notifications
   - **Logs** - Activity and error logs
   - **Copilot Studio** - Agent-specific metrics

### Step 2: Review Monitor Overview

1. Click **Overview** to see the platform health summary
2. Review the summary cards showing key metrics
3. Note any custom alerts that have been configured
4. Use product links to drill down into specific areas

### Step 3: Configure Pre-Built Alert Rules

1. Navigate to **Monitor** > **Alerts**
2. Review the pre-built Microsoft alert rules:

| Alert Rule | Description | FSI Relevance |
|------------|-------------|---------------|
| High-use agents have success rate under 90% | Monitors heavily used agents | Critical for customer-facing agents |
| Environment capacity alerts | Warns on capacity limits | Capacity planning |
| Security-related alerts | Detects security concerns | Compliance monitoring |

3. Enable each relevant pre-built rule by clicking the rule and toggling **Enabled**
4. Configure notification recipients for each rule

### Step 4: Create Custom Alert Rules

1. In the Alerts section, click **+ New alert rule**
2. Configure the alert for FSI requirements:
   - **Name:** `Tier 3 Agent Success Rate Below 95%`
   - **Condition:** Agent success rate drops below 95%
   - **Scope:** Enterprise managed agents only
   - **Severity:** Critical
3. Set notification recipients:
   - Operations team email
   - Teams channel (if configured)
   - SMS for critical alerts
4. Configure response SLA expectations
5. Click **Save** to create the rule

**Recommended FSI Custom Alerts:**

| Alert Name | Condition | Severity | Response SLA |
|------------|-----------|----------|--------------|
| Tier 3 Success Rate Below 95% | Success rate < 95% for enterprise agents | Critical | 1 hour |
| Customer Data Access Anomaly | Data access > 3x average | Critical | Immediate |
| After-Hours Activity | Activity outside business hours | Medium | Next business day |
| High Error Rate | Error rate > 5% | High | 4 hours |

### Step 5: Access Copilot Studio Dashboard

1. Navigate to **Monitor** > **Copilot Studio**
2. Review agent health metrics:

| Metric | Description | Target |
|--------|-------------|--------|
| Agent session success rate | Percentage of successful sessions | >95% for Tier 3 |
| Recent sessions | List of recent interactions | Real-time monitoring |
| Environment | Environment hosting the agent | Location tracking |
| Managed status | Whether environment is managed | Governance status |

3. Filter by environment to focus on specific zones
4. Note any agents with success rates below targets

### Step 6: Configure Usage Insights for Managed Environments

1. Navigate to **Manage** > **Environments**
2. Select a Managed Environment
3. Click **Edit Managed Environments**
4. Configure usage insights:
   - Check **Include insights for this environment in the weekly email digest**
   - Add compliance team to additional recipients
5. Click **Save**

### Step 7: Review Activity Logs

1. Navigate to **Monitor** > **Logs**
2. Review available log types:

| Log Type | Description | Retention |
|----------|-------------|-----------|
| Activity logs | User and admin actions | Per retention policy |
| Error logs | System and application errors | Per retention policy |
| Audit logs | Security-relevant events | Per compliance requirements |

3. Apply filters to focus on specific environments or time periods
4. Export logs for compliance documentation

---

## Configuration by Governance Level

| Setting | Baseline (Level 1) | Recommended (Level 2-3) | Regulated (Level 4) |
|---------|-------------------|------------------------|---------------------|
| **Dashboard review** | Monthly | Weekly | Daily |
| **Pre-built alerts** | Optional | Enabled | All enabled |
| **Custom alerts** | None | Tier-specific | Comprehensive |
| **Success rate target** | >80% | >90% | >95% |
| **Response SLA** | Next business day | 4 hours | 1 hour |
| **Audit log retention** | 90 days | 1 year | 7 years |

---

## Key Performance Indicators

| KPI | Tier 1 Target | Tier 2 Target | Tier 3 Target |
|-----|---------------|---------------|---------------|
| Success rate | >80% | >90% | >95% |
| Response time | <10s | <5s | <3s |
| Availability | 95% | 99% | 99.9% |

---

## Integration with Other Monitoring

| System | Integration Method | Purpose |
|--------|-------------------|---------|
| Microsoft 365 Audit | Unified audit log | Comprehensive activity history |
| Azure Monitor | Log forwarding | Custom dashboards |
| SIEM systems | CEF/Syslog export | Security monitoring |
| GRC tools | API integration | Regulatory evidence |

---

## Validation

After completing these steps, verify:

- [ ] Monitor section is accessible
- [ ] Pre-built alert rules are enabled
- [ ] Custom alerts are configured for Tier 2+ agents
- [ ] Copilot Studio dashboard shows agent metrics
- [ ] Usage insights configured for Managed Environments
- [ ] Notification recipients receive test alerts

---

[Back to Control 3.2](../../../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
