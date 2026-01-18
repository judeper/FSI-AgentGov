# Portal Walkthrough: Control 2.17 - Multi-Agent Orchestration Limits

**Last Updated:** January 2026
**Portal:** Copilot Studio, Power Automate
**Estimated Time:** 1-2 hours per orchestration pattern

## Prerequisites

- [ ] Copilot Studio Environment Admin or Maker role
- [ ] Power Automate license (for flow-based orchestration)
- [ ] Multi-agent architecture documented
- [ ] Delegation depth limits defined per zone
- [ ] Circuit breaker thresholds established

---

## Step-by-Step Configuration

### Step 1: Document Agent Orchestration Architecture

Before configuring limits, document your multi-agent patterns:

1. Identify all agents that can invoke other agents
2. Map delegation chains (Agent A → Agent B → Agent C)
3. Determine maximum acceptable depth per zone:

| Zone | Max Delegation Depth | Rationale |
|------|---------------------|-----------|
| Zone 1 | 0 (no delegation) | Personal productivity, no chaining |
| Zone 2 | 2 levels | Team collaboration, limited chaining |
| Zone 3 | 3 levels | Enterprise, controlled orchestration |

### Step 2: Configure Agent-to-Agent Delegation

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select the orchestrating agent
3. Navigate to **Actions** or **Plugins**
4. If using agent-to-agent calls:
   - Document which agents can be called
   - Implement depth tracking in conversation context

### Step 3: Implement Depth Tracking

For each orchestrating agent, implement depth tracking:

```
Conversation Variable: orchestration_depth
Initial Value: 0
Increment on each agent call
Check against max_depth before delegating
```

**In Copilot Studio Topic:**

1. Create a topic for delegation handling
2. Add condition node checking depth:
   - If `orchestration_depth < max_allowed_depth`: proceed
   - Else: return error or escalate to human

### Step 4: Configure Circuit Breakers

Implement circuit breakers to prevent cascade failures:

1. **Timeout Configuration:**
   - Set maximum response time for delegated calls
   - Default: 30 seconds per agent call
   - Total chain timeout: 90 seconds

2. **Retry Limits:**
   - Maximum retries per failed call: 2
   - Backoff strategy: exponential

3. **Failure Threshold:**
   - After N failures, stop delegating
   - Default: 3 consecutive failures

### Step 5: Configure HITL Checkpoints

For Zone 3 orchestrations, add human-in-the-loop checkpoints:

1. Identify decision points requiring human review
2. Configure approval topics:
   - Topic triggers on sensitive delegations
   - Pauses for human approval
   - Timeout with escalation

### Step 6: Set Up Monitoring

1. Enable audit logging (Control 1.7)
2. Create alerts for:
   - Delegation depth exceeded attempts
   - Circuit breaker activations
   - HITL timeout escalations

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|--------------------|
| **Max Delegation Depth** | 0 (none) | 2 levels | 3 levels |
| **Circuit Breaker** | Optional | Recommended | **Required** |
| **Timeout per Call** | 60s | 30s | 30s |
| **Total Chain Timeout** | N/A | 120s | 90s |
| **HITL Checkpoints** | None | Optional | **Required for sensitive** |
| **Monitoring** | Basic | Enhanced | **Real-time alerting** |

---

## FSI Example Configuration

```yaml
Orchestration Pattern: Client Service Request Handler

Primary Agent: Client-Service-Bot
Environment: FSI-Client-Services-Prod
Zone: 3 (Enterprise Managed)

Delegation Chain:
  Level 1: Client-Service-Bot
    → Delegates to: Account-Lookup-Agent
    → Delegates to: Transaction-History-Agent

  Level 2: Account-Lookup-Agent
    → Delegates to: KYC-Verification-Agent

  Level 3: KYC-Verification-Agent
    → No further delegation (leaf node)

Configuration:
  Max Depth: 3
  Total Timeout: 90 seconds
  Per-Call Timeout: 30 seconds

  Circuit Breaker:
    Failure Threshold: 3
    Reset Timeout: 60 seconds
    Half-Open Attempts: 1

  HITL Checkpoints:
    - Before KYC verification (customer data)
    - Before transaction execution (financial)
    - On confidence < 0.8

Monitoring:
  Alerts:
    - Depth exceeded: Immediate
    - Circuit open: Warning
    - HITL timeout: Escalation
```

---

## Validation

After completing these steps, verify:

- [ ] Delegation depth limits are enforced
- [ ] Circuit breakers activate on failures
- [ ] Timeouts are enforced correctly
- [ ] HITL checkpoints pause for approval
- [ ] Monitoring alerts are functioning
- [ ] Audit logs capture orchestration events

---

[Back to Control 2.17](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
