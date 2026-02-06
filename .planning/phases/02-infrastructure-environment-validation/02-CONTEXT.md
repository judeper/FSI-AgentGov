# Phase 2: Infrastructure & Environment Validation - Context

**Gathered:** 2026-02-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Solution infrastructure established with Dataverse schema for status tracking, and per-environment audit validation using Dataverse Web API. Includes solution folder structure in FSI-AgentGov-Solutions, Dataverse table creation, connection references, environment variables, and PowerShell scripts for environment-level audit validation. Phase 3 handles orchestration/alerting; Phase 4 handles evidence export and documentation.

</domain>

<decisions>
## Implementation Decisions

### Dataverse schema design
- Record granularity: Claude's discretion — pick the approach that best fits Dataverse query patterns and evidence export needs
- Separate current-state table vs history-only: Claude's discretion — pick based on Dataverse performance patterns and downstream dashboard needs
- Zone classification: Denormalized — zone stored on each validation record (not a separate lookup table). Simplifies queries; zone changes are captured as new records with updated zone value
- Scope: Store both tenant-level results (from Phase 1 scripts) and per-environment results in the same history table, differentiated by a 'scope' field
- Immutability: History table is organization-owned with no update/delete — append-only for compliance evidence
- Publisher prefix: fsi_ on all tables and fields

### Environment discovery & filtering
- Discovery approach: Dual — API discovery finds all environments, auto-registers new ones in Dataverse registry, then validates the registered set. Alerts on newly-discovered environments
- New environment zone: Unclassified status that triggers an alert. Admin must assign a zone before validation runs against it
- Trial/Dev filtering: Automatic exclusion by environment type from API, with admin override capability to include specific dev/trial environments when needed
- Deprovisioned environments: Mark as Inactive in registry. History records preserved. Environment stops appearing in validation runs

### Validation result structure
- Severity levels: Same as Phase 1 — Passed, Warning, GracePeriod, Failed, Error. Same priority logic for overall status computation
- Remediation hints: Claude's discretion — decide based on what Phase 3 alerting needs and what's maintainable
- Run correlation: Unique GUID run ID links all records (tenant-level + all per-environment) from the same execution
- Raw values: Store actual configuration values checked (e.g., RetentionDays=90, AuditEnabled=true) alongside the pass/fail result. Enables drift detection by comparing stored values rather than re-querying

### Solution packaging conventions
- Solution type: Unmanaged with PowerShell deployment scripts
- Folder structure: Follow the exact same layout as existing solutions in FSI-AgentGov-Solutions (README, CHANGELOG, docs/, scripts/, src/)
- Zone thresholds: Configurable via Dataverse environment variables (fsi_ACV_* convention), not hardcoded
- Deployment paths: Dual-path — (1) PowerShell setup scripts for fast lab/dev testing that create Dataverse tables, seed environment variables, and configure defaults; (2) Unmanaged solution export as alternative deployment path. Both paths produce the same result. Scripts are primary for rapid testing; solution export is the enterprise deployment option
- Connection references: fsi_cr_* naming convention per requirements

### Claude's Discretion
- Record granularity (one row per environment per run vs one row per check)
- Whether to use a separate current-state table or query history directly
- Remediation hint inclusion in validation records
- Exact Dataverse field types and option set values
- Setup script idempotency approach

</decisions>

<specifics>
## Specific Ideas

- "We need scripts to create tables and everything needed so I can test faster in a lab environment, and customers can test in their dev environment"
- Dual deployment: scripts for speed, unmanaged solution export for enterprise deployment
- Follow existing Tier 2 solution pattern exactly (environment-lifecycle-management as reference)
- 24-hour grace period for newly-enabled environments (consistent with Phase 1 tenant-level approach)
- Zone-specific retention enforcement: Zone 1 = 180d, Zone 2 = 365d, Zone 3 = 730d

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-infrastructure-environment-validation*
*Context gathered: 2026-02-06*
