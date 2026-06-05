# Portal Walkthrough: Control 2.17 — Multi-Agent Orchestration Limits

**Last Updated:** April 2026
**Portals:** Microsoft Copilot Studio, Power Automate, Power Platform Admin Center (PPAC), Application Insights
**Estimated Time:** 2–4 hours per orchestration pattern (initial); ~30 minutes per quarterly review
**Audience:** AI Governance Lead, Power Platform Admin, Copilot Studio Agent Author

!!! warning "Design patterns, not platform-enforced controls"
    Copilot Studio does **not** natively enforce delegation depth limits, circuit breakers, financial stop-loss caps, or HITL checkpoints. The portal steps below configure the *building blocks* (topics, variables, Power Automate flows, telemetry); the *limits themselves* are enforced by the orchestration logic you author. Treat this playbook as a design and configuration aid — not as a one-click compliance switch.

---

## Prerequisites

- [ ] **Roles:**
    - *Power Platform Admin* (PPAC tenant settings, environment governance)
    - *Environment Admin* on each environment hosting orchestrating agents
    - *Copilot Studio Agent Author* on each agent in the delegation chain
    - *AI Governance Lead* sign-off on the proposed delegation graph and limits
- [ ] **Inventory artifacts:**
    - Agent inventory (Control 2.1) listing every agent in the proposed orchestration
    - Zone classification per agent (Control 2.2)
    - Combined Model Risk Card if any agent in the chain is in Zone 3 (Control 2.6)
- [ ] **Approved limits documented in writing** (delegation depth, circuit-breaker thresholds, financial stop-loss caps, HITL trigger conditions) — these are governance decisions, not defaults
- [ ] **Application Insights (or equivalent SIEM) workspace** provisioned and connected to the environment for custom telemetry
- [ ] **Power Automate premium licensing** for any flow that calls non-Microsoft endpoints (HTTP connector) or Dataverse-backed circuit-breaker state

---

## Step 1: Document the Orchestration Graph (Before Any Configuration)

Configuration without a documented graph creates audit gaps. Produce a *named* delegation graph for each orchestration pattern:

1. List every agent that may invoke another agent (**parent → child**).
2. For each edge, record: invocation mechanism (A2A, MCP, Power Automate flow, direct tool call), expected payload class (PII / MNPI / public), and zone of each agent.
3. Compute the **maximum potential depth** of the graph and confirm it does not exceed the per-zone limit recorded in the control:

    | Zone | Max delegation depth | Notes |
    |------|----------------------|-------|
    | Zone 1 (Personal) | 0 | Single-agent only; delegation is a design violation |
    | Zone 2 (Team) | 2 | Circuit breaker required; interactions logged |
    | Zone 3 (Enterprise) | 3 | Full telemetry, HITL on customer-impacting steps, financial stop-loss |

4. Store the graph as evidence (PNG / Mermaid / Visio) under your control evidence folder using the naming convention in *Verification & Testing*.

!!! tip "Use Microsoft Foundry agent diagrams"
    For agents authored in Microsoft Foundry, the *Workflow* designer surfaces a built-in graph view that exports to PNG. This is preferable to hand-drawn diagrams because it stays in sync with the deployed agent.

---

## Step 2: Configure Per-Agent Tool and Connector Inventory

Each Copilot Studio agent supports up to **128 tools** (connectors, plugins, MCP tools, child agents). Plan multi-agent architectures with this constraint in mind.

1. Open [Copilot Studio](https://copilotstudio.microsoft.com).
2. Select the orchestrating agent → **Tools** (or **Actions** in older tenants).
3. Record the current tool count and remaining headroom for each agent in the chain.
4. Where tools are reused across multiple agents, package them into a **Component Collection** (GA) so updates propagate consistently and audit evidence references a single artifact.
5. For child agents invoked via **Agent-to-Agent (A2A)** or **Microsoft Foundry**: list the child agent under the parent agent's tools and record the child's environment, zone, and owner.

---

## Step 3: Implement Delegation Depth Tracking

Depth tracking is the foundation of every other control in this playbook. Without it, circuit breakers, stop-loss, and HITL cannot reliably scope to a single orchestration chain.

**Pattern A — Conversation-scoped depth (single-environment chains):**

1. In the *root* agent, create a topic-level variable `Topic.OrchestrationDepth` (Number) initialized to `0`.
2. Before any delegation node (Tool call, child agent, A2A handoff), add a **Set variable** node: `Topic.OrchestrationDepth = Topic.OrchestrationDepth + 1`.
3. Add a **Condition** node: if `Topic.OrchestrationDepth > <max-for-zone>`, route to a **Send a message** node returning a structured error and exit the topic. Log the violation (Step 6).
4. Pass `Topic.OrchestrationDepth` as an input parameter on every child invocation so the child can continue tracking.

**Pattern B — Correlation-ID-scoped depth (cross-environment chains):**

1. Generate a `correlationId` (GUID) at the root agent on first invocation.
2. Persist `{correlationId, currentDepth, startedUtc}` in a Dataverse table (`fsi_OrchestrationState`) accessible to every environment in the chain.
3. Each agent reads the row, increments depth, and writes back atomically (use a Power Automate flow with the *Update a row* action and the `If-Match` ETag header to detect concurrent updates).
4. Add a row-level retention policy aligned to your audit-log retention (typically 6–7 years for FSI).

!!! warning "Cross-environment chains add operational risk"
    Pattern B introduces a Dataverse dependency on the critical orchestration path. Document the failure mode (Dataverse outage → orchestration blocks) in your incident-response playbook and validate the behavior in pre-production.

---

## Step 4: Implement Circuit Breaker (Power Automate)

Copilot Studio has no native circuit breaker. Implement one as a Power Automate flow invoked before each delegation:

1. Create a solution-aware flow `fsi-CircuitBreaker-Check` in the orchestration environment.
2. Inputs: `targetAgentId`, `correlationId`.
3. Steps:
    - **Get rows** from a `fsi_CircuitBreakerState` Dataverse table filtered by `targetAgentId`.
    - If `state == 'Open'` and `(utcNow() - openedUtc) < resetTimeoutSeconds`, return `{allow: false, reason: 'circuit-open'}`.
    - If `state == 'Open'` and timeout elapsed, set `state = 'HalfOpen'` and return `{allow: true, mode: 'probe'}`.
    - Else return `{allow: true, mode: 'normal'}`.
4. Create a companion flow `fsi-CircuitBreaker-Record` invoked **after** every delegation:
    - Input: `targetAgentId`, `success` (bool).
    - On failure, increment `consecutiveFailures`. If it reaches the threshold (default `3`), set `state = 'Open'` and `openedUtc = utcNow()`.
    - On success in `HalfOpen` mode, reset `state = 'Closed'`, `consecutiveFailures = 0`.
5. In each orchestrating agent topic, call `fsi-CircuitBreaker-Check` immediately before delegation; gate the delegation on `allow == true`.

**Recommended thresholds (organization may tune):**

| Setting | Zone 2 | Zone 3 |
|---------|--------|--------|
| Per-call timeout | 30s | 30s |
| Total chain timeout | 120s | 90s |
| Consecutive-failure threshold | 5 | 3 |
| Reset timeout | 120s | 60s |
| Half-open probe attempts | 1 | 1 |

---

## Step 5: Configure Human-in-the-Loop (HITL) Checkpoints

For Zone 3 chains and any chain that touches customer-impacting actions, regulated data, or material financial decisions:

1. Identify the **specific orchestration boundaries** that require human approval (do not approve the *whole chain* — approve at the boundary closest to the action).
2. In the agent topic, add an **Adaptive Card** (Teams or in-channel) with `Approve` / `Reject` actions. The card must include:
    - `correlationId` (so the approver can trace the full chain)
    - Summary of the action requiring approval (max 200 chars; do not embed customer PII in the card body)
    - Reviewer attestation field
3. Use **Power Automate's *Wait for an approval*** action with a configured timeout (recommend 4 business hours for customer-impacting actions; 24 hours for non-urgent reviews).
4. On timeout: route to escalation (secondary approver group) — never silently proceed.
5. Persist the approval decision (`approverUpn`, `decision`, `decisionUtc`, `correlationId`) to the same Dataverse table used for orchestration state, retained per Control 1.7.

!!! tip "Microsoft Agent Framework HITL primitives"
    Microsoft Agent Framework (preview as of April 2026) documents `RequestPort` / `request_info()` / response-handler routing for HITL. If your orchestration is built on Agent Framework rather than Copilot Studio topics, prefer those primitives over hand-rolled adaptive cards — they integrate with checkpoint persistence and event streaming for chain-of-custody evidence.

---

## Step 6: Configure Orchestration Telemetry

1. In each orchestrating agent, enable **Application Insights** under *Settings → Advanced → Analytics*.
2. Add custom event emission at four points using the *Send a custom event* action (or via Power Automate calling the Application Insights ingestion endpoint):

    | Event name | Emit when | Required custom dimensions |
    |------------|-----------|---------------------------|
    | `Orchestration.DelegationStart` | Before child invocation | `correlationId`, `parentAgentId`, `childAgentId`, `depth`, `zone` |
    | `Orchestration.DelegationEnd` | After child returns | `correlationId`, `childAgentId`, `success`, `durationMs` |
    | `Orchestration.CircuitBreakerOpen` | When state transitions to Open | `correlationId`, `targetAgentId`, `consecutiveFailures` |
    | `Orchestration.HitlDecision` | After HITL checkpoint resolves | `correlationId`, `approverUpn`, `decision`, `waitDurationMs` |
    | `Orchestration.MCP.ToolInvocation` | Each MCP tool call | `correlationId`, `mcpServer`, `toolName`, `dataClassification` |

3. Configure Application Insights → *Alerts* for: depth-limit violations, circuit-breaker opens, HITL timeouts, and MCP invocations on **unapproved servers** (cross-reference your approved MCP registry — see Control 2.17 § MCP Server Governance).
4. Forward Application Insights events to Microsoft Sentinel (or your SIEM) for correlation with Copilot audit log events from Control 1.7.

---

## Step 7: Configure MCP Server Allow-list (If Applicable)

If your orchestration uses MCP servers (Microsoft-built or custom):

1. Maintain an **approved MCP server registry** (recommended: SharePoint list with columns `mcpServerId`, `vendor`, `dataClassification`, `approvedZones`, `approverUpn`, `approvedUtc`, `nextReviewUtc`).
2. In Copilot Studio → agent → **Tools → Add tool → Model Context Protocol**, register only servers from the approved list.
3. Capture the *server URL*, *authentication method* (OAuth 2.0 minimum; OAuth 2.0 + certificate pinning for Zone 3), and *tool surface* (specific tools enabled vs. wildcard).
4. Add a Power Platform DLP policy (Control 2.14) blocking the MCP HTTP connector from being combined with non-business connectors in Zone 2/3 environments.

!!! warning "Custom MCP servers — preview status"
    Microsoft documents custom MCP servers in the 2026 Wave 1 release plan with public preview in March 2026 and GA targeted for April 2026. Confirm current GA status on Microsoft Learn before promoting custom MCP servers to production. For Zone 3, do not use preview features in customer-impacting orchestrations.

---

## Configuration by Governance Level

| Setting | Zone 1 (Baseline) | Zone 2 (Recommended) | Zone 3 (Regulated) |
|---------|------------------|----------------------|--------------------|
| Max delegation depth | 0 | 2 | 3 |
| Depth tracking pattern | N/A | Pattern A | Pattern A or B |
| Circuit breaker | Not required | Required | Required |
| Per-call timeout | N/A | 30s | 30s |
| Total chain timeout | N/A | 120s | 90s |
| Failure threshold | N/A | 5 | 3 |
| HITL checkpoints | None | Optional | Required for customer-impacting / financial / regulated-data steps |
| Telemetry | Basic Copilot audit log | Custom events to App Insights | App Insights → Sentinel with real-time alerts |
| Combined model risk card | Not required | Not required | Required (Control 2.6) |
| MCP server registry | N/A | Required if MCP used | Required + monthly review |
| Quarterly orchestration review | Optional | Required | Required + approver attestation |

---

## Validation Checklist

After completing the steps above, confirm the following before declaring the control implemented:

- [ ] Delegation graph documented and stored as evidence
- [ ] Depth tracking variable / Dataverse row exists in every orchestrating agent
- [ ] Circuit breaker flows deployed and invoked in topic flows
- [ ] HITL checkpoints configured at the **action boundary**, not chain entry
- [ ] All five custom events emit with required dimensions
- [ ] Sentinel / SIEM alerts wired for depth violations, circuit opens, HITL timeouts, unapproved MCP invocations
- [ ] MCP server registry exists and is referenced by the DLP policy
- [ ] Combined Model Risk Card written for Zone 3 chains (Control 2.6)
- [ ] Quarterly review scheduled in your governance cadence (Control 2.12)

Run the *Verification & Testing* playbook against this configuration before promoting to production.

---

[Back to Control 2.17](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
