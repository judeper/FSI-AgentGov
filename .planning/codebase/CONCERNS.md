# Codebase Concerns

**Analysis Date:** 2026-02-02

## Tech Debt

**Microsoft Learn Documentation Synchronization:**
- Issue: Microsoft Learn content changes frequently (UI updates, deprecations, date extensions, feature GA/retirement). The current learn-monitor automation detects changes but requires manual review and updates.
- Files: `scripts/learn_monitor.py`, `data/learn-monitor-state.json`, `docs/reference/microsoft-learn-urls.md`, `.github/workflows/learn-monitor.yml`
- Impact: Playbooks may become outdated if Learn content changes between monitoring runs. Portal-walkthrough.md steps can diverge from actual Microsoft UI within days of a release.
- Fix approach: The Learn Monitor AI Enhancement (v1.2.37+) introduces `/review-learn-changes` skill for AI-assisted draft generation. Implement systematic review workflow where PR changes are analyzed by Claude before merging to ensure accuracy.

**Solution Coverage Gaps (45 of 62 controls without deployable automation):**
- Issue: 72.6% of controls lack automated solutions; many rely solely on portal configuration. Pillar 4 (SharePoint) has 0% coverage.
- Files: `docs/reference/solutions-coverage-gaps.md`
- Impact: Organizations must implement 45 controls manually through configuration playbooks. Gap analysis identifies 1.21 (Adversarial Input Logging), 1.3 (SharePoint Content Governance), 2.5 (Testing & Validation), 2.9 (Performance Monitoring), 3.9 (Sentinel Integration) as high-risk gaps requiring custom development.
- Fix approach: Prioritize P0/P1/P2 development backlog per solutions-coverage-gaps.md with phased rollout through Q1-Q3 2026.

**Agent 365 Blueprint SDK in Limited Preview:**
- Issue: Agent 365 SDK and Agent Essentials are in Frontier program limited preview. Controls 2.1 and related lifecycle controls reference these capabilities which may change before GA.
- Files: `docs/controls/pillar-2-management/2.1-managed-environments.md` (line 173-174)
- Impact: Production deployments depending on Agent 365 Blueprints may face breaking changes or extended preview periods affecting control implementation timelines.
- Fix approach: Monitor SDK release status; flag controls as "preview-dependent" until GA; maintain fallback portal configuration paths.

---

## Known Bugs

**Learn Monitor URL Redirect Chain:**
- Symptoms: 25 Microsoft Learn URLs redirect to new paths (Purview consolidation, M365 Copilot path changes, Sentinel paths updated)
- Files: `docs/reference/microsoft-learn-urls.md`
- Trigger: Microsoft reorganizes Learn content structure (November 2025 consolidation wave)
- Workaround: Learn Monitor script automatically detects and reports redirects; v1.2.37 fixed 25 redirect entries manually pending automation of redirect following.

**Learn Monitor Rate Limiting Intermittency:**
- Symptoms: Learn Monitor workflow occasionally hits HTTP 429 rate limiting during bulk URL checks
- Files: `scripts/learn_monitor.py` (lines 178-181)
- Trigger: Monitoring 209+ URLs daily; Microsoft Learn rate limits after ~150 sequential requests
- Workaround: Script implements exponential backoff and Retry-After header parsing; recommend running in off-peak hours (2-5 AM UTC).

---

## Security Considerations

**Information Barriers Enforcement Gap - Channel Agents:**
- Risk: Channel Agents in Teams do NOT inherit Information Barrier policies from invoking users; Chinese wall enforcement fails for channel-based agents.
- Files: `docs/controls/pillar-1-security/1.22-information-barriers.md` (lines 37-57)
- Current mitigation: Control documentation warns: "Do not deploy Channel Agents in Teams channels where barrier-protected segments interact." Recommends Copilot Studio agents (app packages) instead, which DO support IB.
- Recommendations: (1) Audit all deployed Channel Agents; (2) Zone 3 prohibition on Channel Agents in barrier-sensitive channels; (3) Use connector policies (Control 1.4) as compensating control to restrict data access.

**DLP Enforcement Mandatory (No Opt-Out):**
- Risk: Organizations cannot disable DLP enforcement for Copilot Studio agents as of early 2025. Tenants with permissive DLP policies automatically enforce on all agents.
- Files: `docs/controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md` (lines 33-35)
- Current mitigation: Mandatory enforcement triggered by MC973179; organizations must audit existing DLP policies and ensure Copilot-appropriate sensitivity thresholds.
- Recommendations: (1) Audit all DLP policies for Copilot-blocking rules; (2) Configure Copilot Studio-specific policies with FSI-appropriate SITs; (3) Test with pilot agents before enterprise deployment.

**Pay-As-You-Go Does NOT Satisfy Managed Environment Licensing:**
- Risk: Enabling PAYG consumption for a Managed Environment is insufficient to meet licensing requirements; standalone premium licenses still required per user.
- Files: `docs/controls/pillar-2-management/2.1-managed-environments.md` (lines 38-46)
- Current mitigation: Control documentation explicitly warns: "Pay-as-you-go consumption meters do NOT satisfy Managed Environment licensing for active users."
- Recommendations: (1) Audit all Managed Environments for PAYG-only configurations; (2) Verify each active user has standalone premium license; (3) Implement licensing validation in onboarding workflows.

**Append-Only Audit Trails (Not Immutable):**
- Risk: Environment Lifecycle Management playbook documentation previously claimed "immutable" audit trails, but Dataverse ProvisioningLog is append-only with access control limitations.
- Files: `docs/playbooks/advanced-implementations/environment-lifecycle-management/architecture.md` (v1.2.27 corrected)
- Current mitigation: v1.2.27 remediation changed "immutable" to "append-only" and added table of access control limitations. System Administrators retain full Dataverse access.
- Recommendations: (1) Do not position ProvisioningLog as immutable compliance control; (2) Implement separate external audit archive in Azure Immutable Blob Storage (SEC 17a-4 validated WORM); (3) Audit System Admin access quarterly.

**Service Principal Security Group Bypass:**
- Risk: Service principals used in Environment Lifecycle Management bypass environment Security Groups; cannot restrict SP scope to specific segments.
- Files: `docs/playbooks/advanced-implementations/environment-lifecycle-management/` architecture docs
- Current mitigation: Architecture design documentation notes SPs bypass SG enforcement; recommends quarterly audit of SP permissions.
- Recommendations: (1) Limit SPs to read-only provisioning roles where possible; (2) Quarterly audit SP operations in ProvisioningLog; (3) Consider Azure Managed Identity alternatives for reduced privilege.

---

## Performance Bottlenecks

**PPAC Agent Inventory 500-Agent Display Limit:**
- Problem: Power Platform Admin Center agent inventory preview caps display at 500 agents; tenants with 500+ agents cannot view full list in portal
- Files: `docs/reference/faq.md` (line 106)
- Cause: PPAC data refresh design limitation; 24-hour refresh cycle for large tenant inventories
- Improvement path: Use Graph API directly for programmatic inventory; implement custom Power BI dataset for >500 agent scenarios. FSI-AgentGov-Solutions Compliance Dashboard (Control 3.3) addresses this via Dataverse aggregation.

**DEC Solution Power BI Refresh Limits (Pro License):**
- Problem: Deny Event Correlation Report (DEC) with Power BI Pro license refreshes max 8x daily (every 3 hours); real-time compliance monitoring gaps during off-hours
- Files: `docs/reference/solutions-architecture-guide.md` (lines 176-177), `docs/playbooks/control-implementations/1.7/` (DEC integration)
- Cause: Power BI Pro dataset refresh limits; Premium capacity required for sub-hourly refresh
- Improvement path: Upgrade reporting environment to Premium capacity for near-real-time DLP/deny event monitoring. For cost-constrained deployments, implement scheduled hourly exports to Dataverse with alerts.

**Graph API Throttling on Scope Drift Monitor:**
- Problem: Scope Drift Monitor (Control 1.14 solution) may hit Graph API throttling when querying 1000+ connectors across multiple environments
- Files: FSI-AgentGov-Solutions `scope-drift-monitor/` scripts
- Cause: Tight polling loops without backoff; Microsoft Graph throttles to ~2,000 requests per 60 seconds per app
- Improvement path: Implement exponential backoff in polling; batch connector queries; cache results with 1-hour TTL.

---

## Fragile Areas

**Multi-Agent Orchestration (Design Patterns, No Platform Enforcement):**
- Files: `docs/controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md` (lines 30-32)
- Why fragile: Delegation depth limits, circuit breakers, and financial stop-loss controls are governance patterns, NOT built-in platform constraints. Organizations must implement custom logic; Copilot Studio has no native delegation depth enforcement.
- Safe modification: (1) Document all orchestration patterns in deployment runbook; (2) Test agent chains with max-depth scenarios before Zone 3 promotion; (3) Implement timeout and error handling in each agent's error topic; (4) Set up alerts for orphaned/hanging agent calls.
- Test coverage: Integration tests needed for 3+ agent chaining scenarios; manual walkthrough required for financial stop-loss implementations.

**Information Barriers + SharePoint Alignment:**
- Files: `docs/controls/pillar-1-security/1.22-information-barriers.md` (full control)
- Why fragile: IB enforcement depends on concurrent SharePoint permission alignment; drift between barriers and site permissions creates gaps.
- Safe modification: (1) Cannot modify barrier definitions without reviewing all agent data sources; (2) Before changing site permissions, audit all agents referencing that site; (3) Implement quarterly alignment audit comparing Purview barriers to SharePoint site membership.
- Test coverage: Barrier enforcement testing (line 57) requires user in each segment to verify blocked access; test must be manual per user role.

**Learn Monitor State File Corruption:**
- Files: `data/learn-monitor-state.json`
- Why fragile: If state file becomes corrupted or deleted, monitor loses URL hash history and all changes appear as "new"; change detection resets.
- Safe modification: (1) Back up state file before each monitor run; (2) Validate JSON structure before applying changes; (3) Git tracks state file; use git history to recover if corrupted.
- Test coverage: Manual verification required after state file recovery; spot-check 5-10 URLs against actual Learn content.

**Sentinel Integration Path (MI vs. Direct Line):**
- Files: `docs/controls/pillar-3-reporting/3.9-sentinel-integration-and-advanced-analytics.md`
- Why fragile: Multiple Sentinel integration paths exist (Power Platform Admin Activity → LA → Sentinel vs. MCP Server vs. custom connectors). Migration from classic eDiscovery to new paths is ongoing.
- Safe modification: (1) Do NOT mix integration approaches in same tenant; standardize on one path; (2) Test KQL queries on both classic and new Sentinel data sources before rolling out; (3) Maintain fallback reporting path during migration.
- Test coverage: KQL alert queries require tuning per tenant's agent naming conventions; cannot be generalized across orgs.

---

## Scaling Limits

**Managed Environment Licensing at Scale:**
- Current capacity: Managed Environment licensing model requires standalone premium license per user OR Power Platform Premium capacity reservation
- Limit: Organizations with 500+ users face exponential licensing costs; per-user model breaks at enterprise scale
- Scaling path: (1) Migrate to Power Platform Premium capacity pooling for Zone 2-3 environments; (2) Implement environment routing to reduce unlicensed user access to managed environments; (3) Monitor usage via PPAC insights to optimize licensing tier.

**Dataverse Capacity for Compliance Dashboards:**
- Current capacity: Dataverse default 1 GB storage; Compliance Dashboard aggregating 62 controls + 500+ agents requires monitoring
- Limit: Organizations with 10,000+ agents + multi-year audit logs may exceed 10 GB threshold
- Scaling path: (1) Implement archival strategy: move 12+ month old records to Azure Data Lake; (2) Implement Synapse Link for Dataverse → Data Lake pipeline; (3) Monitor storage monthly; request capacity increase at 70% utilization.

**Learn Monitor URL Monitoring at Scale:**
- Current capacity: Monitor currently tracks 209 URLs; daily polling takes ~30-40 minutes with backoff
- Limit: Scaling to 500+ URLs increases risk of timeout/rate limiting; job execution time becomes problematic in CI/CD
- Scaling path: (1) Implement parallel fetching with thread pool (4-8 workers); (2) Move to weekly monitoring for non-critical URLs; (3) Implement caching layer to avoid re-parsing unchanged content.

---

## Dependencies at Risk

**Microsoft Learn Content Instability (Knowledge Base Gap):**
- Risk: Microsoft Learn undergoes structural reorganization every 60-90 days; URLs redirect, sections move, deprecation dates shift
- Impact: 25+ URLs required corrections in v1.2.37 alone; portal walkthrough steps can diverge from Learn within weeks of major releases
- Migration plan: (1) Maintain internal "FSI-canonical" documentation that mirrors Learn concepts but documents FSI-specific zone guidance; (2) Reduce hard dependency on exact Learn paths by linking to "Purview compliance center" vs. specific URLs; (3) Establish SLA for Learn change response (48-hour update window).

**Azure Key Vault API Retirement (February 27, 2027):**
- Risk: Azure Key Vault APIs created before February 1, 2026 will be retired February 27, 2027. ELM and other solutions using pre-2026 APIs will break.
- Impact: Solutions using Access Policy permission model (vs. Azure RBAC) must migrate or lose key access
- Migration plan: (1) Audit all Key Vaults created before Feb 2026; (2) Migrate to Azure RBAC model by January 2027; (3) Update all solution scripts to use RBAC-based authentication; (4) Test credential rotation after migration.

**x-api-key Deprecation for App Insights (March 31, 2026):**
- Risk: App Insights API key (x-api-key) authentication is deprecated March 31, 2026. DEC solution and other monitoring integrations using API keys will fail.
- Impact: Deny Event Correlation Report and any custom App Insights queries via API key will lose access
- Migration plan: (1) Audit all solutions using x-api-key; (2) Migrate to Entra ID authentication (bearer token) before March 31, 2026; (3) DEC v1.1.0+ includes deprecation warnings; validate upgrade applied to all deployments.

**O365 Connectors Deprecation (March 2026) - Webhooks:**
- Risk: O365 Connectors (Incoming Webhooks) deprecated March 2026. Message Center Monitor and custom webhook integrations lose delivery mechanism.
- Impact: Power Automate flows sending webhooks to Teams/Slack will need migration to native connectors
- Migration plan: (1) Inventory all flows using O365 Connectors; (2) Migrate to native Teams Connector or Slack connector before March 2026; (3) Test message delivery in pilot environments first.

**Reporting Webservice API Retirement (April 2026):**
- Risk: Microsoft Power Platform Reporting Webservice API deprecated April 2026. Custom reporting scripts querying this API will fail.
- Impact: Legacy custom inventory or usage reporting scripts will need migration to new Graph endpoints
- Migration plan: (1) Audit custom scripts using Reporting Webservice; (2) Migrate to Graph API endpoints (Admin API, Usage API); (3) Test new endpoints with representative data sets.

---

## Missing Critical Features

**No Native Hallucination Detection in Copilot Studio:**
- Problem: Control 2.9 (Hallucination & Accuracy Monitoring) documents that no automated hallucination detection exists. All detection relies on manual user feedback.
- Blocks: Organizations cannot implement automated guardrails against false information in agent responses
- Workaround: FSI-AgentGov-Solutions Hallucination Tracker (Control 3.10, v1.0.0) implements feedback aggregation pipeline with pattern analysis, but requires manual feedback cycle to work.

**No Built-In Adversarial Input Detection:**
- Problem: Control 1.21 (Adversarial Input Logging) documents that prompt injection and jailbreaking patterns must be detected via custom logic or third-party SIEM integration.
- Blocks: Organizations cannot implement automated real-time detection of prompt injection attacks
- Workaround: Defender CloudAppEvents logs UPIA/XPIA detection flags (v1.2.32+), but organizations must build custom Sentinel rules or Logic Apps to trigger on suspicious patterns.

**No Platform Enforcement of Agent Scope:**
- Problem: Control 1.14 (Data Minimization) documents that agents can access any connectors an admin allows. No platform mechanism restricts individual agents to specific data sources.
- Blocks: Organizations must implement custom connector policies or role-based access controls via shared groups
- Workaround: FSI-AgentGov-Solutions Scope Drift Monitor (v1.0.0) detects when agents access connectors outside declared scope, but detection is post-hoc, not preventative.

---

## Test Coverage Gaps

**Learn Monitor Accuracy Validation (Untested Area):**
- What's not tested: Learn Monitor change classification accuracy. Script categorizes changes as CRITICAL/HIGH/MEDIUM/NOISE, but no baseline validates classification correctness against human review.
- Files: `scripts/learn_monitor.py` (change classification logic ~lines 300-400)
- Risk: Script may misclassify portal-walkthrough-affecting changes as MEDIUM, resulting in delayed control updates
- Priority: Medium - Affects v1.2.38+ Learn Monitor releases. Recommend manual spot-check of 10-15 change classifications per month until confidence threshold reached.

**Information Barriers Channel Agent Scenario:**
- What's not tested: Actual channel agent vs. Copilot Studio agent IB enforcement in Teams with barrier-protected users
- Files: `docs/controls/pillar-1-security/1.22-information-barriers.md` (testing note, line 57)
- Risk: Organizations may deploy Channel Agents in barrier-sensitive channels unaware of lack of enforcement
- Priority: High - Risk impacts FINRA/SEC regulated environments. Recommend formal test plan before Zone 3 Channel Agent deployments.

**Multi-Environment Orchestration Error Handling:**
- What's not tested: Agent chaining across 3+ environments with failure scenarios (timeout, permission denied, upstream agent down)
- Files: `docs/controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`, ELM advanced implementation
- Risk: Production orchestration chains may fail silently or cascade failures across environments
- Priority: High - Affects Tier 1 (critical) agents. Recommend integration test suite with chaos engineering scenarios.

**Scope Drift Monitor at Scale (1000+ Agents):**
- What's not tested: Scope Drift Monitor scalability with 1000+ agents across 50+ environments
- Files: FSI-AgentGov-Solutions `scope-drift-monitor/`
- Risk: Monitor may timeout or miss drift detection on large deployments
- Priority: Medium - Affects enterprise deployments. Recommend load test with 1000-agent simulation.

**DLP Enforcement Interaction with Agent 365 Blueprints:**
- What's not tested: DLP policies applied to Managed Environments with Agent 365 Blueprints in preview
- Files: Control 1.5 (DLP) + Control 2.1 (ME) + Agent 365 SDK integration
- Risk: DLP may not enforce correctly on Blueprint-promoted agents; enforcement gaps during promotion
- Priority: High - Critical for Zone 3 deployments. Recommend functional test when Agent 365 exits preview.

---

## Technical Debt Summary (By Priority)

| Area | Priority | Impact | Effort | Notes |
|------|----------|--------|--------|-------|
| Learn Monitor AI-assisted review workflow adoption | P1 | Reduces manual update burden; improves accuracy | Low | v1.2.37 skill available; needs process integration |
| Solution coverage gaps (45 controls) | P1 | 72.6% of framework lacks automation | High | 7 solutions released v1.2.36; backlog in solutions-coverage-gaps.md |
| DLP enforcement validation with Copilot agents | P1 | Mandatory enforcement needs baseline testing | Medium | Recommend pre-deployment audit of all DLP policies |
| Channel Agent IB limitation communication | P1 | Organizations unaware of Chinese wall gap | Low | Update Zone 3 deployment guidance; add to architecture review checklist |
| February 2026 Managed Environment licensing deadline | P0 | BLOCKER - Automatic enforcement starts Feb 2026 | High | Audit all pipeline targets now; use Pipeline Governance Cleanup solution |
| Key Vault RBAC migration (Feb 2027 deadline) | P1 | Post-2026 APIs will break if not migrated | Medium | Audit access policy KVs; schedule migration for Q1 2027 |
| x-api-key deprecation for App Insights (March 2026) | P1 | DEC solution and monitoring will break | Medium | Migrate DEC and custom APIs to bearer token auth |
| Learn Monitor rate limiting optimization | P2 | Occasional workflow failures during bulk checks | Low | Implement parallel fetching; move to off-peak schedule |
| Append-only audit trail documentation | P2 | Risk of misuse as immutable compliance control | Low | Maintain v1.2.27 corrections; audit quarterly |
| Learn Monitor URL redirect following | P2 | 25+ redirects require manual update | Low | Implement automatic redirect following in future monitor version |

---

*Concerns audit: 2026-02-02*
