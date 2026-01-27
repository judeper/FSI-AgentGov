# Agent Observability Alerting Configuration

> Part of [Agent 365 Observability Implementation Guide](index.md)

---

## Overview

This guide provides zone-based alerting thresholds and escalation configurations for Agent 365 observability. Alerts are designed to surface operational issues, security events, and compliance concerns based on governance zone requirements.

---

## Alert Categories

| Category | Zone 1 | Zone 2 | Zone 3 |
|----------|--------|--------|--------|
| Performance | Optional | ✓ | ✓ |
| Availability | Optional | ✓ | ✓ |
| Security | - | ✓ | ✓ (Priority) |
| Compliance | - | Optional | ✓ (Priority) |
| Governance | - | ✓ | ✓ |

---

## Performance Alerts

### Alert 1: High Response Latency

**Trigger:** Agent response time exceeds threshold.

| Zone | Warning | Critical | Evaluation Window |
|------|---------|----------|-------------------|
| Zone 2 | P95 > 3s | P95 > 5s | 5 minutes |
| Zone 3 | P95 > 2s | P95 > 3s | 5 minutes |

```json
{
  "name": "Agent High Response Latency",
  "description": "Agent response time exceeds acceptable threshold",
  "severity": 2,
  "enabled": true,
  "scopes": ["/subscriptions/{sub}/resourceGroups/{rg}/providers/microsoft.insights/components/{ai}"],
  "evaluationFrequency": "PT5M",
  "windowSize": "PT5M",
  "criteria": {
    "allOf": [
      {
        "query": "traces | where name == 'agent.interaction' | extend latency = todouble(customDimensions.agent_response_latency_ms) | summarize P95 = percentile(latency, 95) by bin(timestamp, 5m) | where P95 > 3000",
        "timeAggregation": "Count",
        "operator": "GreaterThan",
        "threshold": 0,
        "failingPeriods": {
          "numberOfEvaluationPeriods": 1,
          "minFailingPeriodsToAlert": 1
        }
      }
    ]
  },
  "actions": [
    { "actionGroupId": "/subscriptions/{sub}/resourceGroups/{rg}/providers/microsoft.insights/actionGroups/ag-platform-ops" }
  ]
}
```

### Alert 2: Low Success Rate

**Trigger:** Agent success rate drops below threshold.

| Zone | Warning | Critical | Evaluation Window |
|------|---------|----------|-------------------|
| Zone 2 | < 95% | < 90% | 15 minutes |
| Zone 3 | < 98% | < 95% | 10 minutes |

```json
{
  "name": "Agent Low Success Rate",
  "description": "Agent success rate below acceptable threshold",
  "severity": 1,
  "enabled": true,
  "criteria": {
    "allOf": [
      {
        "query": "traces | where timestamp > ago(15m) | where name == 'agent.interaction' | extend success = customDimensions.agent_response_success == 'true' | summarize SuccessRate = 100.0 * countif(success) / count() | where SuccessRate < 95",
        "timeAggregation": "Count",
        "operator": "GreaterThan",
        "threshold": 0
      }
    ]
  }
}
```

### Alert 3: High Fallback Rate

**Trigger:** Fallback topic triggered excessively.

| Zone | Warning | Critical | Evaluation Window |
|------|---------|----------|-------------------|
| Zone 2 | > 20% | > 30% | 1 hour |
| Zone 3 | > 10% | > 20% | 30 minutes |

```json
{
  "name": "Agent High Fallback Rate",
  "description": "Agent triggering fallback topic too frequently - review topic coverage",
  "severity": 3,
  "criteria": {
    "allOf": [
      {
        "query": "traces | where timestamp > ago(1h) | extend isFallback = name == 'fallback.triggered', isInteraction = name == 'agent.interaction' | summarize FallbackRate = 100.0 * countif(isFallback) / countif(isInteraction) | where FallbackRate > 20"
      }
    ]
  }
}
```

---

## Availability Alerts

### Alert 4: Agent Unavailable

**Trigger:** No interactions received for extended period.

| Zone | Threshold | Evaluation Window |
|------|-----------|-------------------|
| Zone 2 | 0 interactions | 30 minutes |
| Zone 3 | 0 interactions | 15 minutes |

```json
{
  "name": "Agent Unavailable",
  "description": "No agent interactions detected - service may be down",
  "severity": 0,
  "criteria": {
    "allOf": [
      {
        "query": "traces | where timestamp > ago(15m) | where name == 'agent.interaction' | where customDimensions.fsi_zone == 'Zone3' | count",
        "timeAggregation": "Count",
        "operator": "LessThanOrEqual",
        "threshold": 0
      }
    ]
  },
  "actions": [
    { "actionGroupId": "/subscriptions/{sub}/resourceGroups/{rg}/providers/microsoft.insights/actionGroups/ag-critical-oncall" }
  ]
}
```

### Alert 5: Connector Failure

**Trigger:** External connector/tool calls failing.

| Zone | Warning | Critical |
|------|---------|----------|
| Zone 2 | > 10% fail | > 25% fail |
| Zone 3 | > 5% fail | > 15% fail |

```json
{
  "name": "Agent Connector Failures",
  "description": "External connector calls experiencing high failure rate",
  "severity": 2,
  "criteria": {
    "allOf": [
      {
        "query": "traces | where timestamp > ago(15m) | where name == 'tool.invocation' | extend success = customDimensions.tool_success == 'true' | summarize FailRate = 100.0 * countif(not(success)) / count() by tostring(customDimensions.tool_name) | where FailRate > 10"
      }
    ]
  }
}
```

---

## Security Alerts

### Alert 6: RAI Filter Spike (Zone 3 Priority)

**Trigger:** Unusual increase in RAI filter activations.

```json
{
  "name": "RAI Filter Spike - Security",
  "description": "Significant increase in RAI content filter activations - review for potential abuse",
  "severity": 1,
  "criteria": {
    "allOf": [
      {
        "query": "let baseline = traces | where timestamp between (ago(7d) .. ago(1d)) | where name == 'rai.filter' | summarize BaselineAvg = count() / 6; traces | where timestamp > ago(1h) | where name == 'rai.filter' | summarize CurrentCount = count() | extend baseline = toscalar(baseline) | where CurrentCount > baseline * 3"
      }
    ]
  },
  "actions": [
    { "actionGroupId": "/subscriptions/{sub}/resourceGroups/{rg}/providers/microsoft.insights/actionGroups/ag-security-ops" }
  ]
}
```

### Alert 7: DLP Block Event (Zone 3 Priority)

**Trigger:** DLP policy blocks agent content.

```json
{
  "name": "Agent DLP Block",
  "description": "DLP policy blocked agent content - review for data protection",
  "severity": 2,
  "criteria": {
    "allOf": [
      {
        "query": "traces | where timestamp > ago(15m) | where name == 'dlp.block' | where customDimensions.fsi_zone == 'Zone3' | count",
        "operator": "GreaterThan",
        "threshold": 0
      }
    ]
  },
  "actions": [
    { "actionGroupId": "/subscriptions/{sub}/resourceGroups/{rg}/providers/microsoft.insights/actionGroups/ag-compliance" }
  ]
}
```

### Alert 8: Access Denial Spike

**Trigger:** Unusual increase in access denial events.

```json
{
  "name": "Agent Access Denial Spike",
  "description": "Spike in access denial events - potential unauthorized access attempts",
  "severity": 1,
  "criteria": {
    "allOf": [
      {
        "query": "traces | where timestamp > ago(1h) | where name == 'access.denied' | summarize DenialCount = count() | where DenialCount > 10"
      }
    ]
  },
  "actions": [
    { "actionGroupId": "/subscriptions/{sub}/resourceGroups/{rg}/providers/microsoft.insights/actionGroups/ag-security-ops" }
  ]
}
```

### Alert 9: Authentication Failure Pattern

**Trigger:** Multiple authentication failures from same source.

```json
{
  "name": "Agent Auth Failure Pattern",
  "description": "Multiple authentication failures detected - potential credential attack",
  "severity": 1,
  "criteria": {
    "allOf": [
      {
        "query": "traces | where timestamp > ago(30m) | where name == 'auth.failure' | summarize FailCount = count() by tostring(customDimensions.client_ip) | where FailCount > 5"
      }
    ]
  }
}
```

---

## Compliance Alerts

### Alert 10: Sponsor Attestation Overdue (Zone 3)

**Trigger:** Agent sponsor attestation past due date.

```json
{
  "name": "Sponsor Attestation Overdue",
  "description": "Agent sponsor attestation is overdue - compliance risk",
  "severity": 2,
  "criteria": {
    "allOf": [
      {
        "query": "traces | where timestamp > ago(24h) | where name == 'sponsor.attestation.check' | extend overdue = customDimensions.attestation_overdue == 'true' | where overdue | summarize OverdueCount = dcount(customDimensions.agent_id) | where OverdueCount > 0"
      }
    ]
  },
  "actions": [
    { "actionGroupId": "/subscriptions/{sub}/resourceGroups/{rg}/providers/microsoft.insights/actionGroups/ag-compliance" }
  ]
}
```

### Alert 11: Orphaned Agent Detected

**Trigger:** Agent without valid sponsor identified.

```json
{
  "name": "Orphaned Agent Detected",
  "description": "Agent without valid sponsor - immediate attention required",
  "severity": 1,
  "criteria": {
    "allOf": [
      {
        "query": "traces | where timestamp > ago(1h) | where name == 'agent.interaction' | where customDimensions.fsi_zone in ('Zone2', 'Zone3') | where isempty(customDimensions.sponsor_id) or customDimensions.sponsor_status == 'Invalid' | distinct tostring(customDimensions.service_name)"
      }
    ]
  }
}
```

---

## Governance Alerts

### Alert 12: Blueprint Phase Change

**Trigger:** Agent promoted or demoted in Blueprint lifecycle.

```json
{
  "name": "Blueprint Phase Change",
  "description": "Agent Blueprint lifecycle phase changed",
  "severity": 4,
  "criteria": {
    "allOf": [
      {
        "query": "traces | where timestamp > ago(15m) | where name in ('blueprint.promotion', 'blueprint.demotion') | project timestamp, AgentId = customDimensions.agent_id, FromPhase = customDimensions.source_phase, ToPhase = customDimensions.target_phase"
      }
    ]
  }
}
```

### Alert 13: Configuration Change (Zone 3)

**Trigger:** Agent configuration modified.

```json
{
  "name": "Zone 3 Agent Configuration Change",
  "description": "Zone 3 agent configuration was modified - audit required",
  "severity": 3,
  "criteria": {
    "allOf": [
      {
        "query": "traces | where timestamp > ago(15m) | where name == 'config.change' | where customDimensions.fsi_zone == 'Zone3' | project timestamp, AgentId = customDimensions.agent_id, ChangeType = customDimensions.change_type, ModifiedBy = customDimensions.modified_by"
      }
    ]
  },
  "actions": [
    { "actionGroupId": "/subscriptions/{sub}/resourceGroups/{rg}/providers/microsoft.insights/actionGroups/ag-compliance" }
  ]
}
```

---

## Action Groups Configuration

### Platform Operations

```json
{
  "name": "ag-platform-ops",
  "shortName": "PlatformOps",
  "emailReceivers": [
    {
      "name": "Platform-Ops-Email",
      "emailAddress": "platform-ops@contoso.com"
    }
  ],
  "webhookReceivers": [
    {
      "name": "Teams-PlatformOps",
      "serviceUri": "https://contoso.webhook.office.com/webhookb2/..."
    }
  ]
}
```

### Security Operations

```json
{
  "name": "ag-security-ops",
  "shortName": "SecOps",
  "emailReceivers": [
    {
      "name": "SecOps-Email",
      "emailAddress": "secops@contoso.com"
    }
  ],
  "smsReceivers": [
    {
      "name": "SecOps-Oncall",
      "countryCode": "1",
      "phoneNumber": "5551234567"
    }
  ]
}
```

### Compliance Team

```json
{
  "name": "ag-compliance",
  "shortName": "Compliance",
  "emailReceivers": [
    {
      "name": "Compliance-Team",
      "emailAddress": "compliance@contoso.com"
    }
  ]
}
```

### Critical On-Call

```json
{
  "name": "ag-critical-oncall",
  "shortName": "CriticalOC",
  "emailReceivers": [
    {
      "name": "Critical-Escalation",
      "emailAddress": "critical@contoso.com"
    }
  ],
  "smsReceivers": [
    {
      "name": "Oncall-Primary",
      "countryCode": "1",
      "phoneNumber": "5551234567"
    },
    {
      "name": "Oncall-Backup",
      "countryCode": "1",
      "phoneNumber": "5559876543"
    }
  ],
  "voiceReceivers": [
    {
      "name": "Oncall-Voice",
      "countryCode": "1",
      "phoneNumber": "5551234567"
    }
  ]
}
```

---

## Deployment Script

```powershell
# Deploy all alert rules
$alertRules = Get-ChildItem -Path "./alerts/*.json"

foreach ($rule in $alertRules) {
    $alertConfig = Get-Content $rule.FullName | ConvertFrom-Json

    $params = @{
        ResourceGroupName = "rg-agent-governance"
        Name = $alertConfig.name
        Location = "eastus"
        Description = $alertConfig.description
        Severity = $alertConfig.severity
        Enabled = $alertConfig.enabled
        Scope = $alertConfig.scopes
        EvaluationFrequency = $alertConfig.evaluationFrequency
        WindowSize = $alertConfig.windowSize
        Criteria = $alertConfig.criteria
        ActionGroupId = $alertConfig.actions[0].actionGroupId
    }

    New-AzScheduledQueryRule @params
    Write-Host "Created alert: $($alertConfig.name)" -ForegroundColor Green
}
```

---

## Escalation Matrix

| Severity | Initial Response | Escalation (15 min) | Escalation (1 hr) |
|----------|------------------|---------------------|-------------------|
| Sev 0 (Critical) | On-call + Manager | Director | VP/CIO |
| Sev 1 (High) | On-call | Manager | Director |
| Sev 2 (Medium) | Platform Ops | On-call | Manager |
| Sev 3 (Low) | Platform Ops | - | On-call |
| Sev 4 (Info) | Log only | - | - |

---

## Related Resources

- [Overview](index.md) - Observability architecture
- [OpenTelemetry Setup](opentelemetry-setup.md) - Collector configuration
- [Application Insights Workbooks](application-insights-workbooks.md) - Dashboard templates
- [Microsoft Learn: Azure Monitor Alerts](https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-overview)

---

*FSI Agent Governance Framework v1.2.6 - January 2026*
