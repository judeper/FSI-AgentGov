# Application Insights Telemetry Schema Reference

[Playbooks](../../index.md) > Advanced Implementations > [Agent Usage & Performance Workbook](index.md) > Telemetry Schema Reference

**Scope:** Copilot Studio agents connected to Azure Application Insights
**Last Updated:** February 2026 | **Version:** v1.4.0

---

## Overview

When a Copilot Studio agent is connected to an Azure Application Insights resource, the platform emits structured telemetry covering conversation events, topic execution, action invocations, and generative AI usage. This telemetry provides the data foundation for usage monitoring, performance analysis, and governance reporting within financial services environments.

For FSI organizations, this telemetry supports compliance with conversation recordkeeping requirements (FINRA Rule 4511), aids in meeting record retention obligations (SEC Rules 17a-3/17a-4), and helps satisfy internal control monitoring expectations (SOX Section 404). Organizations should verify that their telemetry configuration meets their specific regulatory obligations.

!!! warning "Implementation Caveat"
    Application Insights telemetry is **not a substitute** for official compliance archiving solutions. Organizations should evaluate whether this telemetry, combined with Purview Audit and other retention mechanisms, satisfies their regulatory requirements.

---

## Application Insights Tables

Copilot Studio writes telemetry to a subset of the standard Application Insights tables. Understanding which tables receive data — and which do not — is essential for building accurate KQL queries.

### Tables That Receive Copilot Studio Data

| Table | What Copilot Studio Sends | Key Fields |
|-------|---------------------------|------------|
| `customEvents` | Conversation events, topic triggers, user/agent messages, action executions, generative AI responses | `name`, `timestamp`, `customDimensions.*` |
| `exceptions` | Runtime exceptions, connector failures, action errors | `type`, `message`, `outerMessage` |
| `dependencies` | External API calls (Power Automate flows, HTTP connectors, knowledge source queries) | `name`, `target`, `duration`, `success`, `resultCode` |
| `pageViews` | Web channel conversation starts (webchat and DirectLine channels) | `name`, `url`, `timestamp` |

### Tables That Do NOT Receive Copilot Studio Data

| Table | Status | Notes |
|-------|--------|-------|
| `requests` | Not natively populated | Copilot Studio does not emit server-side request telemetry to this table |
| `traces` | Not natively populated | Only populated by custom Agent 365 SDK implementations; not emitted by standard Copilot Studio agents |

---

## customEvents Schema

The `customEvents` table is the primary telemetry source for agent usage and governance monitoring. Each row represents a discrete event in an agent conversation.

### Event Types

| Event Name | Description | When Fired |
|------------|-------------|------------|
| `BotMessageReceived` | A user sent a message to the agent | Each inbound user message |
| `BotMessageSend` | The agent sent a response to the user | Each outbound agent response |
| `TopicStart` | A topic was triggered | Topic activation (including system topics) |
| `TopicEnd` | A topic completed execution | Topic completion or abandonment |
| `Action` | An action node executed (Power Automate flow, HTTP request, connector call, etc.) | Each action node execution |
| `GenerativeAnswers` | Generative AI was used to formulate a response (generative answers, generative orchestration) | Each generative AI response |

### customDimensions Properties

All `customEvents` rows include a `customDimensions` JSON object with the following properties:

| Field | Type | Description | Always Present |
|-------|------|-------------|----------------|
| `type` | string | Event type (e.g., `"message"`) | Yes |
| `channelId` | string | Delivery channel identifier: `msteams`, `directline`, `webchat`, `sharepoint`, `telephony` | Yes |
| `fromId` | string | User identifier (GUID format) | Yes |
| `fromName` | string | User display name | Only when **Log sensitive activity properties** is enabled |
| `recipientId` | string | Agent/bot identifier (GUID format) | Yes |
| `recipientName` | string | Agent display name | Yes |
| `text` | string | Message content (user input or agent response) | Only when **Log sensitive activity properties** is enabled |
| `designMode` | string | `"True"` when conversation occurs in the test canvas; `"False"` for production conversations | Yes |
| `TopicName` | string | Name of the triggered topic | Only on `TopicStart` and `TopicEnd` events |
| `Kind` | string | Event kind classifier | Yes |
| `locale` | string | User locale (e.g., `"en-us"`) | Yes |
| `session_Id` | string | Session identifier for grouping messages within a single conversation | Yes |

!!! tip "Filtering Test Traffic"
    Always filter on `customDimensions.designMode == "False"` in production queries to exclude test canvas conversations from governance reports.

---

## Channel Identifiers

The `channelId` property in `customDimensions` identifies the platform through which the conversation occurred. FSI organizations typically prioritize Teams and SharePoint channels for governance monitoring.

| Channel ID | Platform | Deployment Method | FSI Relevance |
|------------|----------|-------------------|---------------|
| `msteams` | Microsoft Teams | Published to Teams via Copilot Studio | **Primary** — Most common enterprise deployment channel; subject to Teams compliance policies and Purview retention |
| `directline` | Web Chat / Custom App | DirectLine API integration | **Common** — Used for customer-facing web applications; requires separate content archiving consideration |
| `webchat` | Embedded Web Chat | iframe or Web Chat component | **Common** — Similar to DirectLine; often used for external-facing portals |
| `sharepoint` | SharePoint | Published to SharePoint site | **Primary** — Internal knowledge agents; inherits SharePoint governance and access controls |
| `telephony` | Voice / IVR | Telephony channel connector | **Specialized** — Voice interactions; may have additional recording requirements under FINRA 3110 |

!!! note "Channel Coverage"
    Not all channels may be in use within a given organization. Query `customDimensions.channelId` to identify which channels are active before building channel-specific reports.

---

## Session and Conversation Tracking

The `session_Id` property in `customDimensions` is the primary mechanism for grouping telemetry events into conversations.

### Session Identification

- **Session start:** Inferred from the first `BotMessageReceived` event for a given `session_Id`
- **Session end:** Inferred from the last event (any type) for a given `session_Id`
- **Session duration:** Calculated as `max(timestamp) - min(timestamp)` within a `session_Id` group

### Conversation Metrics

| Metric | Inference Method |
|--------|-----------------|
| **Unique users** | Count distinct `customDimensions.fromId` values (filtered to `designMode == "False"`) |
| **Total conversations** | Count distinct `session_Id` values |
| **Messages per conversation** | Count `BotMessageReceived` events per `session_Id` |
| **Resolution inference** | A conversation is considered resolved if a `TopicEnd` event occurs for a non-system topic without a subsequent escalation topic trigger |
| **Escalation inference** | A conversation is considered escalated if `TopicStart` fires for the `Escalate` system topic |

### Limitations of Session Tracking

- Session boundaries are determined by the Copilot Studio platform; there is no explicit "session close" event
- Long idle periods within a session may indicate abandonment but cannot be confirmed from telemetry alone
- Multi-turn conversations that span extended time periods may appear as a single session or multiple sessions depending on platform timeout behavior

---

## Sensitive Properties and Privacy Settings

Copilot Studio telemetry detail is controlled by a combination of agent-level and tenant-level settings. FSI organizations must carefully evaluate which settings to enable based on their regulatory obligations and data privacy requirements.

### Settings Matrix

| Setting | Configuration Location | What It Enables | Privacy Impact |
|---------|----------------------|-----------------|----------------|
| **Log activities** | Copilot Studio > Agent > Settings > Advanced > Application Insights | Basic telemetry — event types, timestamps, channel, session IDs. Message content is **not** included. | Low — No PII or conversation content in telemetry |
| **Log sensitive activity properties** | Copilot Studio > Agent > Settings > Advanced > Application Insights | Full telemetry — adds `fromName`, `text` (message content), detailed node execution data to `customDimensions` | **High** — Conversation content and user names flow to Application Insights; requires appropriate data handling and retention policies |
| **Allow conversation transcripts** | Power Platform Admin Center > Environment > Settings > Product > Features | Tenant-level prerequisite that permits conversation data storage. Required for sensitive properties to function. | **High** — Enables conversation data storage at the environment level |

### FSI Considerations

- **FINRA Rule 4511 / SEC 17a-3/4:** Organizations subject to conversation recordkeeping requirements may need sensitive properties enabled to capture conversation content for compliance purposes
- **GLBA Section 501(b):** Enabling sensitive properties introduces PII into Application Insights; organizations should apply appropriate access controls, data retention policies, and encryption at rest
- **Minimum viable configuration:** Enable **Log activities** (without sensitive properties) for governance monitoring. Enable sensitive properties only when regulatory obligations require conversation content retention through this channel.

!!! warning "Data Residency"
    Application Insights data is stored in the Azure region of the Application Insights resource. FSI organizations should verify that the resource region aligns with their data residency requirements.

---

## Telemetry Limitations

The following metrics and capabilities are **not available** through native Copilot Studio Application Insights telemetry. Organizations should be aware of these gaps when designing governance dashboards.

| Metric | Availability | Workaround |
|--------|-------------|------------|
| **Token / cost per conversation** | Not available | Cannot be measured from Copilot Studio telemetry; no token usage data is emitted |
| **CSAT score** | Available in Copilot Studio Analytics tab only; **not** sent to Application Insights | Implement a custom survey topic that logs satisfaction scores to Application Insights via a custom event |
| **Hallucination detection** | Not native | Requires Azure AI Evaluation SDK or custom implementation outside of Application Insights |
| **Grounding accuracy** | Not native | Requires custom citation validation logic against knowledge source content |
| **RAI content filter details** | Limited | `GenerativeAnswers` events may indicate content filtering occurred, but detailed filter reasons require Purview Audit log analysis |
| **Response latency (precise)** | Not directly available in `customEvents` | Estimate from timestamp delta between paired `BotMessageReceived` and `BotMessageSend` events within the same `session_Id` |

---

## Prerequisites Checklist

The following configuration is required for Copilot Studio telemetry to flow to Application Insights. This checklist is intended for M365 administrators and Power Platform administrators.

### Required Configuration

- [ ] **Azure Application Insights resource** — Create or identify an existing Application Insights resource in the appropriate Azure subscription and region
- [ ] **Connection string** — Copy the Application Insights connection string from the Azure portal (Resource > Overview > Connection String)
- [ ] **Agent-level configuration** — In Copilot Studio, navigate to Agent > Settings > Advanced > Application Insights and paste the connection string
- [ ] **Enable Log activities** — In the same settings pane, enable the "Log activities" toggle to begin emitting basic telemetry
- [ ] **Tenant-level transcript setting** (if sensitive properties are needed) — In Power Platform Admin Center > Environment > Settings > Product > Features, enable "Allow conversation transcripts"
- [ ] **Enable Log sensitive activity properties** (optional) — In Copilot Studio agent settings, enable this toggle to include message content and user names in telemetry

### Verification

After completing configuration, send a test message to the agent and verify that events appear in the Application Insights `customEvents` table within 5–10 minutes. Use the following KQL query to confirm:

```kql
customEvents
| where timestamp > ago(1h)
| where customDimensions.designMode == "False"
| project timestamp, name, customDimensions
| order by timestamp desc
| take 10
```

---

## Regulatory Context

This telemetry schema supports FSI governance reporting across several regulatory frameworks. The table below maps telemetry capabilities to regulatory requirements.

| Regulation | Requirement | How Telemetry Helps |
|-----------|-------------|---------------------|
| **FINRA Rule 4511** | Recordkeeping — firms must make and preserve records | Agent conversation telemetry (with sensitive properties enabled) aids in meeting recordkeeping requirements by capturing conversation events and content in a queryable store |
| **SEC Rules 17a-3 / 17a-4** | Record creation and retention — broker-dealers must create and retain specified records | Application Insights retention policies (up to 730 days) can be configured to help support retention period requirements; organizations should verify alignment with their specific retention obligations |
| **SOX Section 404** | Internal controls over financial reporting — management must assess effectiveness of internal controls | Agent usage telemetry provides evidence of AI agent activity, exception rates, and escalation patterns that can support internal control monitoring and assessment |
| **FINRA Rule 3110** | Supervision — firms must establish supervisory procedures | Channel-level usage data and escalation tracking help support supervisory review of AI agent interactions |
| **OCC Bulletin 2011-12** | Model risk management — sound practices for model risk management | Performance telemetry (error rates, exception patterns, dependency failures) aids in ongoing model monitoring as recommended by supervisory guidance |

!!! note "Regulatory Disclaimer"
    This telemetry schema reference is provided for informational purposes. Each organization must evaluate whether the captured telemetry, combined with other compliance mechanisms, satisfies their specific regulatory obligations. This framework does not constitute legal or compliance advice.

---

*Updated: February 2026 | Version: v1.4.0 | Framework: FSI Agent Governance*
