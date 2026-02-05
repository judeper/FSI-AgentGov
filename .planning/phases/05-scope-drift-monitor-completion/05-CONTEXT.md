# Phase 5: Scope Drift Monitor Completion - Context

**Gathered:** 2026-02-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Move Scope Drift Monitor from WIP (v1.0.0) to production-ready (v1.1.0) with validated detection logic and alert workflow. The solution already has a baseline capture script and documented architecture. This phase implements the missing detection, alerting, and scope expansion components.

**In scope:**
- Baseline capture script validation and documentation
- Access log aggregation from multiple sources
- Drift detection logic (baseline vs actual comparison)
- Alert workflow for violations
- Scope expansion approval workflow
- README deployment documentation
- Version bump v1.0.0 → v1.1.0

**Out of scope:**
- Zone-based detection frequency (deferred)
- Multi-stage approval workflows (deferred)
- Scope expansion recertification (deferred)

</domain>

<decisions>
## Implementation Decisions

### Detection Scope & Data Sources
- Support all 4 data sources: Unified Audit Log, Defender CloudAppEvents, SharePoint Audit, Dataverse Audit
- Graceful degradation: log warning when a source isn't available, continue with available sources
- Fixed detection frequency: 15 minutes (real-time) for all agents regardless of zone
- No blocking on missing sources — detection runs with reduced coverage

### Alert Behavior
- Dual delivery: both Teams Adaptive Card and email for each violation
- Recipients: agent owner + Security team (distribution list)
- Escalation and severity routing: Claude's discretion to design appropriate model

### Baseline Workflow
- Auto-generate baselines from audit history (30-day analysis period)
- New agents with no history: create empty baseline, monitor everything (any access triggers drift alert)
- No approval required: auto-generated baseline goes active immediately
- Existing script (`New-AgentBaseline.ps1`) provides foundation

### Expansion Approval Flow
- Include full workflow in v1.1.0: request, approve, update scope
- Single approver: Security team (simplify from multi-stage)
- Timeout: auto-deny after 7 days if no response
- No expiration: approved scope expansions are permanent

### Claude's Discretion
- Alert escalation timing and model
- Severity thresholds and routing logic
- Teams Adaptive Card design
- Email notification formatting
- Dataverse table schema for violations and expansion requests
- Power Automate flow structure

</decisions>

<specifics>
## Specific Ideas

- Detection should work even if only Unified Audit Log is available (graceful degradation principle)
- Empty baseline for new agents means "monitor everything" — treats any data access as potential drift until scope is defined
- 15-minute detection aligns with Zone 3 real-time requirement from README, applied uniformly
- Security team as single approver simplifies v1.1.0 — can add data owner stage in v1.2.0 if needed

</specifics>

<deferred>
## Deferred Ideas

- **Zone-based detection frequency** — README documents 15min/1hr/daily by zone; v1.1.0 uses fixed 15min for simplicity
- **Multi-stage approval** — Data owner + Security staged approval deferred to v1.2.0
- **Scope expansion recertification** — Annual re-approval of expansions deferred
- **Configurable recipients per agent** — All agents use same alert routing in v1.1.0

</deferred>

---

*Phase: 05-scope-drift-monitor-completion*
*Context gathered: 2026-02-04*
