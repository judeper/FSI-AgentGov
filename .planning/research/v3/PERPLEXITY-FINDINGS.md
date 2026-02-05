# Perplexity Deep Research Findings (February 2026)

Validated via real-time web research — corrections and confirmations for agent research.

## 1. Copilot Studio Telemetry Schema — CONFIRMED

Events: `TopicStart`, `TopicEnd`, `BotMessageReceived`, `BotMessageSend`, `Action`, `GenerativeAnswers`

Custom dimensions: `type`, `channelId`, `fromName`, `TopicName`, `Kind`, `designMode`, `text`, `session_Id`

No formal published schema — documented through KQL examples in Dynamics 365 guidance.

Source: https://learn.microsoft.com/en-us/dynamics365/guidance/resources/copilot-studio-appinsights

## 2. KQL Examples — CONFIRMED

Microsoft publishes KQL examples: session/message counts, distinct users, error analysis, generative answers telemetry, test conversation filtering.

Source: https://learn.microsoft.com/en-us/dynamics365/guidance/resources/copilot-studio-appinsights

## 3. Azure Monitor Workbook Templates — NOT AVAILABLE

No pre-built workbook templates for Copilot Studio as of Feb 2026. Our solution fills this gap.

Community workaround: "Copilot Studio Monitor" CoE Kit (Power BI template, not Azure Workbook).

## 4. Power BI Integration — 4 METHODS

- Export from Log Analytics (M query) — Power BI Desktop
- Export as new Dataset — Power BI Service
- Azure Data Explorer connector — DirectQuery
- Power BI dataflows — ETL with incremental refresh (Premium required)

**BREAKING**: Continuous Export is deprecated for workspace-based App Insights. Use Diagnostic Settings instead.

## 5. Viva Insights — CONFIRMED WITH LIMITATIONS

"Copilot Studio agents report" in public preview. Covers agents built in Copilot Studio deployed across Teams, web, mobile.

**NOT covered**: declarative agents, Agent Builder agents, autonomous agents, generative AI orchestration agents, third-party agents.

Requires: 50+ Copilot licenses, 1+ agent published in Production.

## 6. Token/Cost Tracking — NOT AVAILABLE NATIVELY

Copilot Studio does NOT expose per-call token consumption or cost data. Operates as abstracted service.

Alternatives:
- Azure AI Foundry agents get token metrics via OpenTelemetry
- Custom instrumentation for `llm.prompt_tokens` / `llm.completion_tokens`
- September 2025 "ROI analysis" tracks business value, not token consumption

## 7. Pricing — VALIDATED

| Plan | Price/GB |
|------|----------|
| Analytics Logs | ~$2.30 |
| Basic Logs | ~$0.50 |
| Auxiliary Logs | ~$0.05 |

Retention: 31 days default (Analytics), 90 days free (App Insights tables), up to 730 days interactive, 12 years archive.

Log processing: free if <50% filtered; $0.05/GB above threshold (billing started Oct 2025).
