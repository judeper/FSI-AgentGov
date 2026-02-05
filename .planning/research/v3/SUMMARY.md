# V3 Milestone Research Summary

**Project:** Agent Observability Foundation + Documentation Gap Closure
**Domain:** AI Agent Governance for Microsoft 365 / Azure in Financial Services
**Researched:** February 5, 2026
**Confidence:** HIGH

## Executive Summary

The v3 milestone combines two tracks: **Agent Observability Foundation** (new capability) and **Documentation Gap Closure** (framework updates for 2025-2026 Microsoft releases). This dual-track approach addresses both operational excellence and strategic alignment with Microsoft's governance evolution.

**Agent Observability Foundation** delivers FSI-compliant monitoring for Copilot Studio and Agent 365 SDK agents using Azure-native telemetry (Application Insights, Azure Monitor Workbooks, Power BI). Research validates that Microsoft provides foundational integration but FSI-specific features (regulatory audit formatting, cost allocation by zone, separation of duties enforcement) require custom implementation. Critical finding from Perplexity research: **token/cost tracking is NOT available natively** in Copilot Studio—only Azure AI Foundry agents expose token metrics via OpenTelemetry. This eliminates a planned differentiator and shifts focus to credit consumption tracking via Copilot Studio Billing API.

**Documentation Gap Closure** addresses 18 governance features Microsoft released between November 2025 and January 2026, centered on three pillars: Microsoft Agent 365 (unified control plane), Entra Agent ID (agent identity), and enhanced Defender for Cloud Apps capabilities. The framework has excellent coverage of GA features (95%+) but needs architectural updates to align with Microsoft's strategic shift from per-platform governance to unified Agent 365 governance.

**Key risks:** (1) PII/sensitive data leakage via custom telemetry requiring pre-production compliance review, (2) SEC 17a-4 retention violations if Application Insights default 90-day retention not configured to 730 days + immutable storage export, (3) FINRA 4511 audit trail gaps if source attribution and prompt versioning not logged, (4) Cost explosion from high-cardinality events requiring sampling strategy, (5) Technical debt from not aligning with Agent 365 architecture as Microsoft consolidates governance.

## Key Findings

### Recommended Stack (Agent Observability)

Azure-native observability stack leveraging existing M365/Azure ecosystem with minimal third-party dependencies. All components are native Microsoft services within FSI compliance boundaries.

**Core technologies:**
- **Azure Application Insights** — Central telemetry repository for Copilot Studio and Agent 365 SDK agents. Native integration, 730-day retention configurable, KQL query engine. OpenTelemetry-based for future extensibility.
- **Azure Monitor Workbooks** — Real-time operational dashboards with parameterization and ARM template deployment. No pre-built Copilot Studio templates exist (validated via Perplexity)—our solution fills this gap.
- **Power BI Premium** — Executive dashboards and compliance reporting via DirectQuery (Premium) or Azure Data Explorer connector (Pro). Log Analytics connector in preview; ADX connector more mature.
- **Viva Insights Agent Dashboard** — Adoption metrics for Copilot Studio agents (GA March 2026). **Limitations confirmed**: Does NOT support declarative agents, Agent Builder, autonomous agents, or generative orchestration agents.
- **Microsoft Purview Audit Logs** — Regulatory audit trail with automatic logging of Copilot Studio activities. Includes FINRA-relevant fields: AgentId, AgentVersion, AccessedResources, XPIADetected, SensitivityLabelId, ModelTransparencyDetails.

**Critical correction from Perplexity research:**
- **Continuous Export is deprecated** for workspace-based Application Insights. Use **Diagnostic Settings** instead for long-term compliance retention.
- **Token tracking NOT available** in Copilot Studio. Must track Copilot Credit consumption via Billing API (aggregate cost, not per-call tokens).
- **Azure Monitor Workbook templates** do NOT exist for Copilot Studio—our workbooks are genuinely novel contribution.

### Expected Features (Agent Observability)

**Table stakes features (must have):**
- Session volume and user adoption metrics (Viva Insights provides pre-built dashboard)
- Completion vs abandonment rate (native Copilot Studio metric with 60-minute inactivity threshold)
- Error categorization by type (Connector/Knowledge/Orchestration failures via KQL aggregation)
- Copilot Credit cost tracking (Billing API with zone-based allocation via Power BI DAX)
- Response time latency percentiles (P50/P95/P99 via KQL queries)
- Conversation transcript export (Dataverse ConversationTranscript table for FINRA 3110/SEC 17a-4)
- Regulatory audit trail (timestamp, user, agent, input, output, sources, decision rationale)
- Executive KPI dashboard (cost, usage, ROI, risk incidents via Power BI)
- Data residency indicators (DORA/CCPA compliance tracking)
- Flow failure correlation (link Power Automate failures to agent conversations via correlation IDs)

**Differentiators (competitive advantage):**
- Zone-based cost allocation (Copilot Credits by governance zone with chargeback models)
- Agent-to-control mapping (link agents to 62 framework controls for compliance gap reports)
- Knowledge source drift detection (alert when agent accesses SharePoint beyond declared scope—integrates with Scope Drift Monitor solution)
- Adversarial input detection (flag jailbreaks, PII extraction attempts, bias testing patterns)
- Hallucination feedback aggregation (structured user reporting with pattern analysis—integrates with Hallucination Tracker solution)
- Multi-agent orchestration tracing (trace Agent A → Agent B handoffs with latency waterfall)
- SR 11-7 Model Risk Report generator (auto-generate Federal Reserve compliance reports)
- Conditional Access failure correlation (link CA policy blocks to agent access attempts)
- RAG source validation status (real-time integrity checks—integrates with RAG Source Validator solution)
- Conflict of interest alert dashboard (surface COI test failures—integrates with COI Testing Framework solution)

**Anti-features (explicitly NOT build):**
- Real-time streaming dashboards (batch refresh sufficient for FSI compliance reporting)
- Custom ML anomaly detection (percentile thresholds more explainable to auditors than black-box models)
- Unified observability platform (accept Microsoft's multi-portal reality; link via correlation IDs)
- User-level performance profiling (GDPR privacy concerns; aggregate by department/zone)
- Predictive capacity planning (token forecasting unreliable; report historical trends)
- Custom token usage APIs (**validated by Perplexity**: not available in Copilot Studio)
- Real-time compliance scoring (compliance is point-in-time quarterly assessment, not continuous)
- Agent performance benchmarking (no industry standards; focus on time-series trends)
- Log data warehousing beyond retention (use archival storage; operational logs rarely accessed)
- Blockchain audit trails (Azure Immutable Storage achieves WORM at lower complexity)

### Architecture Approach (Agent Observability)

Layered observability architecture with **separation of duties** between operational monitoring (real-time, mutable, Operations Team) and compliance audit (historical, immutable, Compliance Team).

**Data flow:**
```
Copilot Studio Agents → Application Insights (telemetry hub)
    ↓                                    ↓
Operational Path                   Compliance Path
    ↓                                    ↓
KQL Queries → Workbooks            Diagnostic Settings → ADLS Gen2 (immutable)
    ↓                                    ↓
Alert Rules → Teams/Email          Power BI Import → Compliance Dashboard
```

**Major components:**
1. **Application Insights** — Central telemetry storage with 90-day default retention (configurable to 730 days). Copilot Studio integration via connection string; Agent 365 SDK via OpenTelemetry.
2. **KQL Query Library** — Reusable parameterized queries organized as Log Analytics workspace functions. Base queries (success rate, latency), compliance queries (deny events, zone 3 audit), anomaly detection, cross-workspace.
3. **Azure Monitor Workbooks** — Interactive operational dashboards deployed via ARM templates. Zone-specific workbooks (Zone 3 Operations, Zone 2 Team Agents, Compliance Audit, Executive Summary, TSG).
4. **Azure Monitor Alerts** — Log search alerts (5-min evaluation) with dynamic thresholds. Action groups for email/SMS/Teams/ServiceNow/Azure Functions. Zone-specific severity and frequency.
5. **Power BI Semantic Model** — Star schema (FactConversations, DimAgent, DimTopic, DimDate) with DAX measures for compliance scoring. DirectQuery for real-time operational, Import for compliance historical.
6. **Compliance Dashboard Integration** — Application Insights metrics flow to Dataverse `fsi_compliancescore` table via Power Automate (daily aggregation). Control 3.2 compliance evidence stored in `fsi_complianceevidence`.
7. **ADLS Gen2 Export** — Diagnostic Settings export telemetry to immutable blob storage (WORM policies) for 3-6 year SEC 17a-4 retention.

**Integration with existing FSI-AgentGov solutions:**
- Environment Lifecycle Management — provisions Application Insights with zone-tagged retention
- Deny Event Correlation Report — shares KQL queries for RAI content filtering events
- Compliance Dashboard — receives observability metrics via Power Automate
- Scope Drift Monitor — shares SharePoint audit log correlation patterns
- Message Center Monitor, FINRA Supervision Workflow — share Dataverse schemas and authentication patterns

**SoD boundaries:**
- Operations Team: Reader on Application Insights, Workbooks, Alert Action Groups
- Compliance Team: Reader on ADLS Gen2 compliance export, NO access to operational alerts
- External Auditors: Time-limited Reader on ADLS Gen2 (90-day PIM assignments)
- Platform Admins: Contributor on all resources

### Documentation Gap Closure (from earlier research)

**18 governance features** identified from Microsoft's November 2025 - January 2026 releases:

**High priority gaps (document in v3):**
1. **Microsoft Entra Agent ID** (preview) — Agent identity architecture with sponsorship model (FINRA 3110 alignment)
2. **Microsoft Agent 365 Control Plane** (preview) — Unified governance replacing per-platform approaches
3. **M365 Admin Center Agent Settings** (preview → GA Q1 2026) — Centralized agent governance controls

**Medium priority gaps (document in v3):**
4. **Virtual Connectors for Copilot Studio** — DLP-based feature toggles (GA)
5. **Enhanced DSPM AI Observability** — Weekly risk assessments, agent insights (GA)
6. **Copilot Hub AI Feature Access Control** — User-level feature restrictions (GA in Managed Environments)

**Low priority gaps (monitor for release):**
7. **SharePoint Restricted Search** (announced 2026) — Emergency brake for Copilot indexing
8. **AI Administrator Role** — New Entra role for delegation

**Coverage validation:**
- Defender for Cloud Apps capabilities: 100% documented (Controls 1.8, 1.24 comprehensive)
- GA features (Nov 2025 - Jan 2026): 95% documented
- Preview features: 40% documented (6 of 15 features need documentation)

### Critical Pitfalls (Top 5)

1. **PII/Sensitive Data in Custom Telemetry** — Custom telemetry calls inadvertently log PII, violating GDPR/GLBA. **Prevention:** Pre-production compliance review, data classification headers, sanitization functions, Application Insights Transformations. **Phase addressed:** Phase 2 (Data Classification & Schema Design).

2. **Incomplete Audit Trail for FINRA 4511/Rule 3110** — Telemetry captures outputs but not decision chain (model version, data sources, confidence, approvals). FINRA 2026 Oversight Report: "Outputs alone insufficient." **Prevention:** Structured schema with AgentID, BlueprintID, UserUPN, Action, DataSourcesQueried, PromptVersion, HumanApprovalRequired. **Phase addressed:** Phase 2 (Schema Design), Phase 4 (Compliance Dashboard).

3. **SEC 17a-4 Retention Violations** — Application Insights default 90-day retention violates 3-year communications / 6-year financial records requirements. **Prevention:** Configure 730-day retention + Diagnostic Settings export to ADLS Gen2 with immutable blob policies. **Phase addressed:** Phase 1 (Infrastructure Setup).

4. **Uncontrolled Cost Explosion** — High-cardinality custom events (per-user, per-message) spike costs from $200/month to $20,000/month. **Prevention:** Adaptive sampling (5-10 events/sec), GetMetric for metrics (not custom events), Basic Logs for verbose diagnostics ($0.50/GB vs $2.30/GB), cost alerts at 50%/75%/90% thresholds. **Phase addressed:** Phase 1 (Infrastructure Setup), Phase 3 (Cost Management).

5. **GDPR Article 22 Automated Decision Violations** — AI agent makes autonomous decisions (credit recommendations, account restrictions) without human oversight or explanation logging. **Prevention:** Track HumanApprovalRequired, SupervisorUPN, ApprovalTimestamp, explanation text, GDPRAutomatedDecision flag. **Phase addressed:** Phase 2 (Schema Design), Phase 4 (Compliance Dashboard).

**Additional moderate pitfalls:**
- KQL query performance anti-patterns (early filtering, projection before aggregation, shuffle for joins)
- Azure Monitor Workbooks parameter binding mistakes (time range inconsistencies, cross-subscription failures)
- Alert fatigue from poor threshold tuning (dynamic thresholds over static, historical baseline P90 + 20%)
- Power BI data model complexity (star schema, Import over DirectQuery, incremental refresh)
- Separation of duties RBAC violations (custom roles, resource-scoped assignments, separate workspaces)

## Scope Adjustments Based on Research

**Features to REMOVE from original scope:**

1. **Token Usage by Orchestration Type** (differentiator)
   - **Research finding:** Copilot Studio does NOT expose per-call token consumption (confirmed via Perplexity). Only Azure AI Foundry agents get token metrics via OpenTelemetry.
   - **Alternative:** Track Copilot Credit consumption via Billing API (aggregate cost trend, not granular token breakdown).
   - **Impact:** Removes a planned differentiator but preserves cost governance capability via credits.

2. **Real-Time Compliance Scoring** (anti-feature)
   - **Research finding:** Compliance assessments are point-in-time (quarterly control reviews). Real-time scoring implies false precision.
   - **Alternative:** Generate compliance reports on-demand or scheduled (weekly/monthly).

3. **Custom Token Usage APIs** (anti-feature)
   - **Research finding:** Microsoft owns token metering; attempting to replicate introduces billing discrepancies.
   - **Alternative:** Trust Copilot Studio Billing API; validate with monthly invoices.

**Features to ADD based on research:**

1. **Diagnostic Settings Export Architecture**
   - **Research finding:** Continuous Export deprecated for workspace-based Application Insights (confirmed via Perplexity).
   - **Replacement:** Use Diagnostic Settings to export to ADLS Gen2 for long-term compliance retention.
   - **Impact:** Architecture change from legacy Continuous Export to modern Diagnostic Settings.

2. **Azure Data Explorer Connector for Power BI Pro**
   - **Research finding:** Log Analytics connector requires Power BI Premium. ADX connector supports DirectQuery in both Pro and Premium.
   - **Addition:** Provide ADX connector pattern for Pro customers as alternative to Premium-only Log Analytics connector.

3. **Viva Insights Limitations Documentation**
   - **Research finding:** Viva Insights Agent Dashboard does NOT support declarative agents, Agent Builder, autonomous agents, generative orchestration (confirmed via Perplexity).
   - **Addition:** Document limitations and position as "Copilot Studio adoption metrics only."

## Documentation Gaps Track (from Earlier Research)

**Summary of documentation updates from v2 milestone research:**

| Gap | Priority | Effort | Target Control |
|-----|----------|--------|----------------|
| Microsoft Entra Agent ID architecture | High | 2-3 days | Control 1.2 enhancement or new Control 1.25 |
| Microsoft Agent 365 control plane | High | 3-4 days | New framework doc: `agent-365-architecture.md` |
| M365 Admin Center agent settings | Medium | 1 day | Control 1.2 enhancement (wait for Q1 2026 GA) |
| Virtual connectors for Copilot Studio | Medium | 0.5 days | Control 1.5 (DLP) enhancement |
| Enhanced DSPM AI observability | Medium | 0.5 days | Control 1.6 enhancement |
| Copilot Hub AI feature access control | Medium | 0.5 days | Control 3.8 enhancement |
| SharePoint Restricted Search | Low | 0.5 days | Control 4.6/4.7 enhancement (wait for release) |
| AI Administrator role | Low | 0.25 days | Update `role-catalog.md` |

**Integration with observability track:**
- Agent 365 documentation informs how observability aligns with unified governance
- Entra Agent ID architecture shows how agents authenticate to Application Insights
- Virtual connectors documentation shows how DLP controls Copilot Studio features being monitored
- DSPM enhancements show how observability complements proactive data governance

## Implications for Roadmap

Based on combined research from both tracks, suggested dual-path phase structure:

### Track 1: Agent Observability Foundation (10 phases)

#### Phase 1: Core Telemetry Infrastructure (Foundation)
**Rationale:** Must establish data pipeline before building dashboards/alerts. SEC 17a-4 retention configured at deployment to avoid compliance gap.

**Delivers:**
- Application Insights resource with 730-day retention
- Log Analytics workspace with zone-specific retention policies
- RBAC role assignments (operations vs compliance separation)
- Diagnostic Settings export to ADLS Gen2 (immutable blob storage)
- Basic KQL query library (5-10 core queries)

**Addresses:** SEC 17a-4 retention pitfall, cost explosion prevention via sampling configuration

**Stack elements:** Azure Application Insights, Log Analytics workspace, ADLS Gen2

**Validation:** Copilot Studio agent configured with connection string, telemetry flowing to `customEvents` table

**Research flag:** Standard pattern deployment, unlikely to need phase-level research

---

#### Phase 2: Telemetry Schema & Data Classification
**Rationale:** Must define compliant schema before custom telemetry logging begins. Prevents PII leakage and FINRA audit trail gaps.

**Delivers:**
- Structured telemetry schema with required fields (AgentID, UserUPN, DataSourcesQueried, PromptVersion, HumanApprovalRequired)
- Data classification taxonomy (Public/Internal/Confidential/Restricted)
- PII sanitization functions
- Copilot Studio custom event taxonomy (`AgentRecommendationGenerated`, `AgentApprovalRequested`, `AgentErrorOccurred`)
- GDPR Article 22 fields (HumanApprovalRequired, SupervisorUPN, ExplanationText)

**Addresses:** PII leakage pitfall, FINRA 4511 audit trail pitfall, GDPR Article 22 pitfall

**Uses:** Copilot Studio "Track Event" actions, Application Insights custom dimensions

**Validation:** Compliance review of schema, query for PII patterns returns zero results

**Research flag:** May need legal/compliance review for GDPR Article 22 interpretation in US FSI context

---

#### Phase 3: KQL Query Library Development
**Rationale:** Reusable queries enable consistent metrics across workbooks, alerts, Power BI. Performance optimization prevents dashboard timeouts.

**Delivers:**
- KQL functions deployed to workspace (`GetAgentSuccessRate`, `GetAgentLatencyP95`, `DetectAnomalies`)
- Base queries (session volume, error categorization, latency percentiles)
- Compliance queries (deny events, zone 3 audit trail, RAG source access)
- Anomaly detection queries (latency spike, error rate, volume anomaly)
- Query performance testing (all queries <10 seconds)

**Addresses:** KQL performance pitfall (early filtering, projection before aggregation)

**Implements:** Query library structure from ARCHITECTURE.md

**Validation:** Performance Analyzer shows all queries <10 seconds, 100K event dataset test

**Research flag:** Standard KQL patterns, unlikely to need phase-level research

---

#### Phase 4: Operational Monitoring Dashboards
**Rationale:** Operations team needs real-time visibility before scaling production agents. Alert rules depend on validated KQL queries.

**Delivers:**
- Azure Monitor Workbooks (Zone 3 Operations, Zone 2 Team Agents, Troubleshooting Guide)
- Workbook parameterization (time range, agent selector, environment filter)
- ARM templates for repeatable deployment
- Zone-specific visualizations (success rate, latency, error trends)

**Addresses:** Workbook parameter binding pitfall (time range consistency, cross-subscription support)

**Uses:** KQL Query Library from Phase 3

**Validation:** Operations team can troubleshoot agent failures without compliance team access

**Research flag:** Standard workbook patterns, unlikely to need phase-level research

---

#### Phase 5: Alert Rules & Action Groups
**Rationale:** Proactive incident response requires alerts. Threshold tuning needs 2-week baseline from Phase 4 production data.

**Delivers:**
- Log search alert rules (success rate, latency, exception rate, RAI content filtered)
- Dynamic thresholds based on 7-day rolling baseline (P90 + 20%)
- Action groups (email, SMS, Teams, ServiceNow integration)
- Alert severity classification (Zone 3: 0-1, Zone 2: 1-2, Zone 1: 2-3)
- Alert processing rules (suppress non-business-hours for non-critical)

**Addresses:** Alert fatigue pitfall (dynamic thresholds, historical baseline, actionable alerts only)

**Implements:** Alert architecture from ARCHITECTURE.md

**Validation:** Test alert fires and resolves without flicker, Teams notification received

**Research flag:** Standard alerting patterns, unlikely to need phase-level research

---

#### Phase 6: Compliance Dashboard Integration
**Rationale:** Compliance reporting requires separate data path from operations (SoD). Integrates with existing Compliance Dashboard solution.

**Delivers:**
- Power Automate flow: Application Insights → Dataverse `fsi_compliancescore` (daily)
- Control 3.2 compliance scoring (>95% success rate = Compliant)
- Evidence storage in `fsi_complianceevidence` (workbook screenshots, KQL results)
- RBAC enforcement (compliance team access to ADLS, NOT Application Insights)
- SoD validation (operations team cannot access compliance export)

**Addresses:** FINRA 4511 audit trail pitfall, SoD RBAC violations pitfall

**Uses:** Existing Compliance Dashboard solution (Dataverse schema)

**Validation:** Compliance team can generate Control 3.2 evidence without operations team assistance

**Research flag:** Integration with existing solution, may need schema alignment research

---

#### Phase 7: Executive Reporting (Power BI)
**Rationale:** Executive visibility requires polished dashboards. DirectQuery for real-time operational, Import for compliance historical.

**Delivers:**
- Power BI semantic model (star schema with FactConversations, DimAgent, DimTopic, DimDate)
- DAX measures (success rate, P95 latency, zone compliance score, daily conversation volume)
- DirectQuery connection for operational dashboard (Premium) OR ADX connector (Pro)
- Import connection for compliance dashboard (daily refresh)
- Row-level security (RLS) by zone
- Executive Summary dashboard (cost, usage, ROI, compliance posture)

**Addresses:** Power BI data model complexity pitfall (star schema, incremental refresh)

**Uses:** Application Insights (DirectQuery), ADLS Gen2 (Import for historical)

**Validation:** Operational dashboard refreshes in <5 seconds, RLS enforces zone access

**Research flag:** Standard Power BI patterns, unlikely to need phase-level research

---

#### Phase 8: Viva Insights Adoption Metrics
**Rationale:** Pre-built adoption dashboard reduces custom development. Complements Application Insights technical metrics.

**Delivers:**
- Viva Insights Agent Dashboard access (requires 50+ Copilot licenses)
- Adoption metrics (active agents, active users, responses, retention trends, credit usage)
- Limitations documentation (does NOT support declarative agents, Agent Builder, autonomous agents)
- Export automation (CSV/Excel for offline analysis)

**Addresses:** Table stakes adoption metrics feature

**Uses:** Viva Insights (GA March 2026)

**Validation:** Dashboard shows Copilot Studio agent adoption, 28-day rolling window data

**Research flag:** Feature GA in March 2026, may delay if not released on schedule

---

#### Phase 9: Advanced Features (Differentiators)
**Rationale:** Once foundation stable, layer advanced FSI-specific capabilities. Requires mature observability baseline.

**Delivers:**
- Zone-based cost allocation (Copilot Credits by governance zone via Power BI DAX)
- Agent-to-control mapping (link agents to 62 framework controls)
- Knowledge source drift detection (integration with Scope Drift Monitor solution)
- Adversarial input detection (pattern library for jailbreaks, PII extraction)
- Hallucination feedback aggregation (integration with Hallucination Tracker solution)
- Multi-agent orchestration tracing (correlation ID propagation)

**Addresses:** Differentiator features from FEATURES.md

**Uses:** Existing FSI-AgentGov-Solutions (Scope Drift Monitor, Hallucination Tracker)

**Validation:** Zone cost allocation matches environment groups, drift detection alerts on out-of-scope access

**Research flag:** Complex integrations, may need deeper research on multi-agent tracing architecture

---

#### Phase 10: Automation & Optimization
**Rationale:** Final phase optimizes costs and adds automated remediation. Requires 30 days historical data for ML training.

**Delivers:**
- Azure Functions for auto-remediation (disable failing agents, create tickets)
- Dynamic alert thresholds (ML-based anomaly detection)
- Cost optimization (sampling, Basic Logs, aggregation tables)
- Cross-environment correlation (multi-workspace queries)
- Anomaly detection queries (ML-enhanced KQL)

**Addresses:** Cost explosion pitfall, alert fatigue pitfall

**Uses:** Azure Functions, Application Insights ML-based smart detection

**Validation:** Auto-remediation triggers on alert, cost reduced 30% via optimization

**Research flag:** Auto-remediation patterns may need research on FSI-safe remediation workflows

---

### Track 2: Documentation Gap Closure (3 phases)

#### Phase 11: Agent 365 Foundation (Strategic Architecture)
**Rationale:** Microsoft's strategic shift to unified governance requires framework alignment. Frontier program participants need guidance now.

**Delivers:**
- `docs/framework/agent-365-architecture.md` (unified registry, comparison with current governance, FSI migration roadmap)
- Microsoft Entra Agent ID documentation (Control 1.2 enhancement or new Control 1.25)
- M365 Admin Center Agent Settings (Control 1.2 enhancement—wait for Q1 2026 GA)

**Addresses:** Agent 365 Control Plane (preview), Entra Agent ID (preview), M365 Admin Center (preview → GA Q1 2026)

**Avoids:** Technical debt from not aligning with Microsoft's strategic direction

**Validation:** Early adopters can implement Agent 365 concepts using framework guidance

**Research flag:** Likely needs deeper research on Agent 365 vs. current architecture tradeoffs

---

#### Phase 12: Enhance Existing Controls (Incremental Updates)
**Rationale:** GA features available now, can update immediately. Enhancements to existing controls, lower risk.

**Delivers:**
- Control 1.5 (DLP) enhancement: Virtual connectors table
- Control 1.6 (DSPM) enhancement: Weekly risk assessments, AI observability
- Control 3.8 (Copilot Hub) enhancement: AI feature access control
- Update `role-catalog.md`: AI Administrator role, Defender XDR Administrator role

**Addresses:** Virtual connectors, enhanced DSPM, AI feature access control, new roles

**Avoids:** Framework becoming outdated on granular governance controls

**Validation:** Controls reflect GA capabilities as of Q1 2026

**Research flag:** Standard pattern updates, unlikely to need additional research

---

#### Phase 13: SharePoint Restricted Search (Monitor for Release)
**Rationale:** Feature announced for 2026 but not yet released. Low priority until GA confirmed.

**Delivers:**
- Control 4.6 or 4.7 enhancement: SharePoint Restricted Search (flag sites to exclude from Copilot index)
- SharePoint governance checklist update

**Addresses:** SharePoint Restricted Search (announced 2026)

**Avoids:** Missing critical SharePoint governance control for FSI

**Validation:** Once GA, control documents emergency brake for Copilot indexing

**Research flag:** Wait-and-see until feature GA date confirmed

---

### Phase Ordering Rationale

**Track 1 (Observability) sequencing:**
1. **Infrastructure first** (Phase 1) — Must establish telemetry pipeline before anything else. SEC 17a-4 retention configured immediately to avoid compliance gap.
2. **Schema before logging** (Phase 2) — Prevents PII leakage and FINRA audit trail gaps. Cannot fix bad schema after production deployment.
3. **Queries before dashboards** (Phase 3) — Workbooks and alerts depend on validated KQL queries. Performance optimization prevents downstream issues.
4. **Operations before compliance** (Phases 4-5 before Phase 6) — Operations team needs working dashboards to validate telemetry completeness before compliance integration.
5. **Foundation before advanced** (Phases 1-7 before Phases 8-10) — Advanced features (zone cost allocation, drift detection) require mature observability baseline.
6. **Optimization last** (Phase 10) — Requires 30 days historical data for ML-based dynamic thresholds and anomaly detection.

**Track 2 (Documentation) sequencing:**
1. **Agent 365 first** (Phase 11) — Foundational architecture change that informs all other updates. Early adopters in Frontier program need guidance now.
2. **Enhancements second** (Phase 12) — GA features can be documented immediately without waiting for releases.
3. **Future features third** (Phase 13) — Wait for GA before investing effort.

**Cross-track dependencies:**
- Phase 11 (Agent 365) informs Phase 2 (telemetry schema) — Entra Agent ID shows how agents authenticate
- Phase 12 (virtual connectors) informs Phase 3 (KQL queries) — DLP controls affect which features generate telemetry
- Phase 12 (DSPM enhancements) complements Phases 4-6 (monitoring) — Proactive governance + reactive monitoring

**Parallelization opportunities:**
- Phase 3 (KQL) can overlap with Phase 2 (schema definition)
- Phase 12 (control enhancements) can run parallel to Phases 1-5 (observability foundation)
- Phase 8 (Viva Insights) is independent, can be done any time after Phase 1

**Critical path:**
- Track 1: Phase 1 → Phase 2 → Phase 3 → Phase 6 (for compliance dashboards)
- Track 2: Phase 11 → Phase 12 (for strategic alignment)

### Research Flags

**Phases needing deeper research:**
- **Phase 2 (Schema Design):** May need legal/compliance review for GDPR Article 22 interpretation in US FSI context. Schema design is high-stakes (cannot easily change after production).
- **Phase 6 (Compliance Integration):** Integration with existing Compliance Dashboard solution may need schema alignment research. Dataverse table structure must match existing patterns.
- **Phase 9 (Advanced Features):** Multi-agent orchestration tracing requires distributed tracing architecture research. Knowledge source drift detection needs Scope Drift Monitor integration patterns.
- **Phase 10 (Auto-Remediation):** Auto-remediation workflows need research on FSI-safe remediation (what can be automated vs. requires human approval).
- **Phase 11 (Agent 365):** Likely needs deeper research on Agent 365 vs. current architecture tradeoffs. Preview feature with incomplete documentation.

**Phases with standard patterns (skip phase-level research):**
- **Phase 1 (Infrastructure):** Standard Azure deployment (Application Insights, ADLS Gen2)
- **Phase 3 (KQL Queries):** Standard KQL patterns, well-documented
- **Phase 4 (Workbooks):** Standard workbook development, ARM templates
- **Phase 5 (Alerts):** Standard alerting patterns, action groups
- **Phase 7 (Power BI):** Standard semantic model design
- **Phase 12 (Control Enhancements):** Incremental updates to existing controls

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack (Observability) | **HIGH** | All components verified via official Microsoft documentation. Perplexity research corrected 3 assumptions (Continuous Export deprecated, token tracking unavailable, workbook templates don't exist). |
| Features (Observability) | **MEDIUM-HIGH** | Table stakes features validated with HIGH confidence. Differentiators have MEDIUM confidence (multi-agent tracing theoretical, SR 11-7 report generator needs template validation). |
| Architecture (Observability) | **HIGH** | Integration patterns verified via official docs and existing FSI-AgentGov solutions. SoD boundaries align with SOX 404 requirements. |
| Pitfalls (Observability) | **HIGH** | PII leakage, retention violations, cost explosion, audit trail gaps validated via FSI compliance sources and community war stories. |
| Documentation Gaps | **HIGH** | 40+ official Microsoft sources. All claims verified with Microsoft Learn or TechCommunity. Defender capabilities 100% validated against Controls 1.8/1.24. |
| Agent 365 Architecture | **MEDIUM** | Preview feature with incomplete documentation. Strategic direction clear but implementation details evolving. |

**Overall confidence:** **HIGH** for observability foundation, **MEDIUM-HIGH** for documentation gaps track (Agent 365 in preview)

### Gaps to Address During Planning/Execution

**Observability track:**

1. **GDPR Article 22 applicability to US FSI firms** — Research shows Article 22 applies to EU customers/employees. Need legal review: Which US FSI firms have EU exposure requiring Article 22 telemetry fields? Recommendation: Include fields by default (defensive compliance), make configurable.

2. **Multi-agent orchestration tracing implementation** — Research confirms correlation IDs enable tracing but implementation patterns not documented. Gap: How to propagate correlation IDs across Copilot Studio → Agent 365 SDK handoffs? Needs technical validation during Phase 9.

3. **SR 11-7 Model Risk Report template** — Research validates Federal Reserve SR 11-7 requirements (conceptual soundness, ongoing monitoring, outcomes analysis). Gap: Specific report template format acceptable to regulators. Needs model risk management team engagement during Phase 9.

4. **Token-level cost attribution** — Perplexity research confirms token tracking NOT available in Copilot Studio. Validated alternative: Copilot Credit Billing API. Gap: Granularity sufficient for FSI cost governance? Monitor Azure AI Foundry agents (have token metrics) for migration path.

5. **Viva Insights Agent Dashboard GA timeline** — Microsoft announced March 2026 GA. Gap: If delayed, Phase 8 blocked. Mitigation: Phase 8 is independent, can defer without blocking critical path.

**Documentation gaps track:**

6. **Agent 365 migration timeline** — Microsoft consolidating to unified governance but timeline unclear. Gap: When will per-platform governance be deprecated? Recommendation: Document both patterns (current + Agent 365 target state) with migration guidance.

7. **M365 Admin Center Agent Settings GA date** — Preview announced, GA expected Q1 2026. Gap: Exact GA date unclear. Mitigation: Phase 11 can document preview with "GA Q1 2026" flag, update when released.

8. **SharePoint Restricted Search release date** — Announced for 2026 but no specific date. Gap: Cannot document until released. Mitigation: Phase 13 monitors for release, updates when GA.

## Sources

### Primary (HIGH confidence)

**Agent Observability Foundation:**
- Microsoft Learn: Application Insights integration with Copilot Studio (https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-bot-framework-composer-capture-telemetry)
- Microsoft Learn: Power Platform Application Insights overview (https://learn.microsoft.com/en-us/power-platform/admin/overview-integration-application-insights)
- Microsoft Learn: Azure Monitor Workbooks (https://learn.microsoft.com/en-us/azure/azure-monitor/visualize/workbooks-overview)
- Microsoft Learn: Azure Monitor Alerts (https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-overview)
- Microsoft Learn: Viva Insights Copilot Dashboard (https://learn.microsoft.com/en-us/viva/insights/org-team-insights/copilot-dashboard)
- Microsoft Learn: Purview Audit Logs for Copilot (https://learn.microsoft.com/en-us/purview/audit-copilot)
- Microsoft Learn: Power BI Log Analytics integration (https://learn.microsoft.com/en-us/power-bi/transform-model/log-analytics/desktop-log-analytics-overview)
- Perplexity Deep Research: Copilot Studio telemetry schema, Viva Insights limitations, token tracking unavailability, Continuous Export deprecation (February 2026)

**Documentation Gap Closure:**
- 17 Microsoft Learn documentation pages (Agent 365, Entra Agent ID, Defender for Cloud Apps, DSPM, virtual connectors, AI feature access control)
- 12 Microsoft TechCommunity blog posts (November 2025 - January 2026 releases)
- 8 Microsoft official blogs (Agent 365 announcements, Entra Agent ID preview)
- FSI-AgentGov v1.2.37 CHANGELOG and control files (coverage validation)

### Secondary (MEDIUM confidence)

**Agent Observability Foundation:**
- Dynamics 365 Guidance: Copilot Studio Application Insights telemetry (https://learn.microsoft.com/en-us/dynamics365/guidance/resources/copilot-studio-appinsights)
- Community blog: Power BI DirectQuery with Application Insights (https://whitepages.bifocal.show/2020/06/connect-to-application-insights-and-log-analytics-with-direct-query-in-power-bi/)
- Holger Imbery blog: Azure Application Insights with Copilot Studio (https://holgerimbery.blog/analytics-with-azure-insights)

**Financial Services Compliance:**
- FINRA 2026 Regulatory Oversight Report (autonomous AI supervision requirements)
- Shumaker law firm: GenAI compliance playbook for 2026
- AdvisorEngine: AI compliance risk framework for financial services 2026
- ValidMind: SR 11-7 Model Risk Management compliance
- ICO (UK): GDPR Article 22 automated decision-making guidance

### Tertiary (LOW confidence, needs validation)

**Cost Management:**
- Community war stories: Azure Application Insights cost overruns (Medium.com blog posts)
- CloudEagle.ai: SOX 302 vs 404 compliance guide
- Screenata: SOX ITGC evidence automation best practices 2026

---

## Ready for Roadmap

Research is **complete and comprehensive**. Key deliverables:

**Track 1 (Agent Observability Foundation):**
1. ✅ **STACK.md** — Azure-native stack validated with HIGH confidence; Perplexity research corrected 3 key assumptions
2. ✅ **FEATURES.md** — Table stakes, differentiators, anti-features identified; token tracking scope adjustment
3. ✅ **ARCHITECTURE.md** — Layered observability architecture with SoD boundaries; integration with existing solutions
4. ✅ **PITFALLS.md** — 15 pitfalls identified (5 critical, 5 moderate, 5 minor) with phase-specific prevention
5. ✅ **PERPLEXITY-FINDINGS.md** — Real-time web research correcting agent assumptions

**Track 2 (Documentation Gap Closure):**
6. ✅ **Earlier research SUMMARY.md** — 18 governance features from Nov 2025 - Jan 2026; 8 gaps with effort estimates

**High-confidence findings:**
- Azure Application Insights is production-ready for Copilot Studio telemetry with 730-day retention + ADLS export for SEC 17a-4 compliance
- Token tracking NOT available in Copilot Studio (use Copilot Credit Billing API instead)
- Continuous Export deprecated (use Diagnostic Settings)
- No pre-built Azure Monitor Workbook templates for Copilot Studio (our solution fills gap)
- Viva Insights Agent Dashboard limited to Copilot Studio agents (does NOT support Agent Builder, declarative, autonomous)
- Microsoft Agent 365 and Entra Agent ID are strategic shifts requiring framework architectural updates
- FSI-AgentGov v1.2.37 has excellent GA feature coverage but 6 high/medium priority gaps for preview features

**Next steps:**
1. Create detailed requirements for Phase 1 (Core Telemetry Infrastructure)
2. Create detailed requirements for Phase 2 (Telemetry Schema & Data Classification)
3. Create detailed requirements for Phase 11 (Agent 365 Foundation)
4. Legal/compliance review for GDPR Article 22 applicability
5. Monitor Viva Insights Agent Dashboard GA (March 2026), M365 Admin Center Agent Settings GA (Q1 2026)

---

*Research completed: February 5, 2026*
*Research quality: HIGH (dual-track synthesis with Perplexity validation)*
*Ready for roadmap: YES*
