# Control 2.17: Multi-Agent Orchestration Limits - Screenshot Specifications

## Required Screenshots

### Screenshot 1: Copilot Studio Agent Orchestration Configuration
**Portal Path:** Microsoft Copilot Studio → Agents → [Agent] → Topics → Plugin actions
**What to capture:**
- Agent-to-agent delegation configuration (plugin actions calling other agents)
- Orchestration topology showing which agents can invoke others
- Action configuration for delegated tasks

### Screenshot 2: Application Insights Custom Telemetry
**Portal Path:** Azure Portal → Application Insights → [Resource] → Transaction search → Custom events
**What to capture:**
- Custom telemetry events tracking multi-agent interactions
- Delegation depth logging (agent chain depth per invocation)
- Circuit breaker trigger events (consecutive failure counts)

### Screenshot 3: Power Platform Admin Center Environment Monitoring
**Portal Path:** Power Platform Admin Center → Environments → [Environment] → Analytics
**What to capture:**
- Agent activity metrics for environments with orchestrated agents
- Error rates and failure patterns in multi-agent scenarios
- Environment-level usage analytics

### Screenshot 4: Combined Agent Card Documentation
**What to capture:**
- Agent Card documenting multi-agent orchestration topology
- Delegation depth limits per zone (Zone 1: 1, Zone 2: 2, Zone 3: 3)
- Circuit breaker thresholds and HITL trigger conditions
- Financial stop-loss control parameters

---

## Notes for Verification
- This control is based on governance design patterns, not built-in platform constraints
- Screenshots should demonstrate custom implementation of orchestration controls
- Capture from pre-production environment when possible
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates
