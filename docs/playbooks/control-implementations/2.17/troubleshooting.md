# Troubleshooting: Control 2.17 - Multi-Agent Orchestration Limits

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Depth limit not enforcing | Tracking variable not implemented | Verify depth tracking in agent topics |
| Circuit breaker stuck open | Reset timeout too long or failures continue | Check downstream agent health; adjust reset timeout |
| Cascade failures occurring | Circuit breaker not configured | Implement circuit breaker pattern |
| HITL timeouts causing abandonment | Timeout too short or approvers unavailable | Adjust timeout; ensure approver coverage |
| Orchestration too slow | Multiple sequential calls | Consider parallel calls where safe |

---

## Detailed Troubleshooting

### Issue: Delegation Depth Limit Not Enforcing

**Symptoms:** Agents can chain beyond configured depth limits

**Diagnostic Steps:**

1. Verify depth tracking variable exists:
   ```
   Copilot Studio > Agent > Topics > Check for orchestration_depth variable
   ```

2. Check depth increment logic:
   - Variable should increment before each delegation
   - Should be passed to delegated agent

3. Verify depth check condition:
   - Condition should compare against max_depth
   - Should block or error if exceeded

**Resolution:**

- Implement depth tracking if missing
- Fix increment logic (ensure it increments BEFORE delegation)
- Add proper condition check before delegation calls
- Consider using Power Automate for complex orchestration with better control

---

### Issue: Circuit Breaker Stuck Open

**Symptoms:** Delegated agent calls permanently blocked even after issue resolved

**Diagnostic Steps:**

1. Check circuit breaker state in your monitoring system

2. Verify the downstream agent is actually healthy:
   - Test direct calls to the agent
   - Check agent health metrics

3. Check reset timeout configuration:
   - Timeout may be longer than expected
   - Half-open test may be failing

**Resolution:**

- Manually reset circuit breaker if available
- Fix downstream agent issues
- Adjust reset timeout to appropriate duration
- Verify half-open test is configured correctly

---

### Issue: Cascade Failures in Orchestration

**Symptoms:** One agent failure causes entire chain to fail

**Diagnostic Steps:**

1. Check if circuit breakers are implemented

2. Review error handling in orchestrating agents:
   - Are failures being caught?
   - Is there fallback behavior?

3. Check timeout configuration:
   - Timeouts should be shorter than total allowed time
   - Cascading timeouts should not exceed total

**Resolution:**

- Implement circuit breakers on all agent-to-agent calls
- Add proper error handling with fallbacks
- Configure appropriate timeouts at each level
- Consider bulkhead pattern for isolation

---

### Issue: HITL Causing User Abandonment

**Symptoms:** Users leave before HITL approval completes

**Diagnostic Steps:**

1. Check HITL timeout configuration:
   - Is timeout appropriate for the approval process?
   - Are approvers available during business hours?

2. Review approval routing:
   - Are requests going to available approvers?
   - Is there a backup approver chain?

3. Check user communication:
   - Are users informed of the wait?
   - Is there a way to check status?

**Resolution:**

- Adjust timeout based on actual approval times
- Implement backup approver chain
- Provide status updates to waiting users
- Consider async patterns where appropriate

---

## How to Confirm Configuration is Active

### Depth Limiting

1. Create a test scenario that would exceed depth
2. Verify the request is blocked
3. Check logs for depth violation event

### Circuit Breaker

1. Simulate failures in a test environment
2. Verify circuit opens after threshold
3. Wait for reset and verify it closes

### HITL Checkpoints

1. Trigger a HITL-required operation
2. Verify approval request is generated
3. Test approval and denial paths

---

## Escalation Path

If issues persist after troubleshooting:

1. **Copilot Studio Admin** - Agent configuration issues
2. **Power Automate Admin** - Flow-based orchestration issues
3. **AI Governance Lead** - Policy and limit questions
4. **Microsoft Support** - Platform limitations

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| No native depth tracking | Must implement manually | Use conversation variables; document pattern |
| Circuit breaker not built-in | Requires custom implementation | Use Power Automate with error handling |
| Limited visibility into chains | Hard to trace multi-agent flows | Implement correlation IDs; use Application Insights |
| HITL requires polling | No native webhook support | Use Power Automate adaptive cards |
| Cross-environment orchestration complex | Multi-env chains hard to manage | Keep orchestration within single environment |

---

[Back to Control 2.17](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
