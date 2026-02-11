# Phase 1 Research: Telemetry Research & KQL Query Library

**Project:** Agent Usage & Performance Workbook (v15)
**Phase:** 1 — Telemetry Research & KQL Query Library
**Researched:** 2026-02-11
**Overall Confidence:** HIGH

---

## Research Source

Phase 1 research is fully covered by prior v13 research, which remains applicable:

| Artifact | Location | Sections |
|----------|----------|----------|
| v13 Phase 1 Research | `.planning/phases/01-workbook-template-kql/01-RESEARCH.md` | 665 lines: telemetry schema, KQL patterns, tab designs, visualization specs, risks, file locations |

**Key findings reused from v13 research:**

### Telemetry Schema (Section 4)
- **Primary table:** `customEvents` (NOT `traces` — that's Agent 365 SDK only)
- **Event types:** BotMessageReceived, BotMessageSend, TopicStart, TopicEnd, Action, GenerativeAnswers
- **customDimensions fields:** type, channelId, fromId, fromName, recipientId, recipientName, text, designMode, TopicName, Kind, locale, session_Id
- **Supporting tables:** `exceptions` (runtime errors), `dependencies` (connector calls), `pageViews` (web channel starts)
- **Sensitive properties:** Required for text content and user IDs; without it, session counts and topic triggers still work

### KQL Design Principles (Section 3.3)
- Time filters first, exclude designMode=="True", project only needed columns
- Parameterize with {TimeRange}, {AgentFilter}, {ChannelFilter} workbook parameters
- Include regulatory reference comments (FINRA 4511, SEC 17a-3)

### Tab Designs (Section 7)
- Tab 1: 8 visualizations (session volume, DAU/MAU, channel breakdown, topics, resolution, messages/session, assisted hours, business value)
- Tab 2: 8 visualizations (latency P50/P95/P99, error rate, error types, connector success, gen AI usage, topic completion, RAI filtering, fallback/escalation)
- Tab 3: 7 visualizations (session anomaly, availability, exception spikes, gen answers quality, dependency health, DLP events, agent health summary)

### Known Limitations (Sections 4.7, 6.1)
- Latency is estimated from timestamp deltas (not precise)
- Resolution rate inferred from TopicEnd presence (no explicit field)
- Token/cost data unavailable from Copilot Studio
- CSAT not sent to App Insights (stays in PPAC Analytics)
- RAI content filter details require Purview Audit, not App Insights

### File Locations (Section 5)
- Workbook JSON: `src/agent-usage-workbook.json`
- KQL query library: research artifacts in `.planning/` (queries embedded in workbook JSON for deployment)
- Schema reference: `docs/playbooks/advanced-implementations/agent-usage-workbook/` (new)

---

**No additional research required.** v13 research is comprehensive and current. Proceed to planning.

*Research referenced: 2026-02-11*
*Source: .planning/phases/01-workbook-template-kql/01-RESEARCH.md (v13)*
