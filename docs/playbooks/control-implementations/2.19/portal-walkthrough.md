# Portal Walkthrough: Control 2.19 — Customer AI Disclosure and Transparency

**Last Updated:** April 2026
**Portals Used:** Microsoft Copilot Studio, Power Automate, Dynamics 365 Customer Service (or generic engagement hub), Power Platform Admin Center
**Estimated Time:** 3–5 hours initial setup; 30 minutes per ongoing copy update
**Primary Owner:** Copilot Studio Agent Author (with Compliance Officer as approver)
**Supporting Roles:** AI Administrator, Power Platform Admin, AI Governance Lead

---

## Prerequisites

- [ ] Disclosure templates drafted by Compliance/Legal and approved (Initial, Periodic Reminder, Pre-Transaction, Post-Handoff)
- [ ] Customer-facing channels enumerated (web, Teams, Omnichannel, Direct Line clients)
- [ ] Engagement hub identified for human handoff (Dynamics 365 Customer Service, Teams voice queue, or generic hub via custom adapter — see [Microsoft Learn: hand off to a live agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-hand-off))
- [ ] Disclosure-event log target chosen (Dataverse table, Application Insights, or Log Analytics workspace) and retention configured for ≥ 6 years (SEC 17a-4 / FINRA 4511)
- [ ] Jurisdiction matrix prepared (which customers see CA / UT / CO copy variations)
- [ ] Agent registered in Agent Inventory (Control 3.1) before disclosure language is published

!!! warning "Hedging is mandatory"
    These steps **support compliance with** SEC Reg BI, CFPB UDAAP, FINRA Rule 2210 / Notice 24-09, and applicable state AI laws — they do not, on their own, guarantee compliance. The firm remains accountable for content correctness, supervision (Control 2.12), and recordkeeping (Control 2.13).

---

## Step 1: Define Disclosure Requirements by Zone

| Zone | Disclosure Level | Initial Timing | Reinforcement | Human Escalation |
|------|------------------|----------------|----------------|------------------|
| Zone 1 (Personal) | Basic AI ID (only if shared externally) | First interaction | None | On request |
| Zone 2 (Team) | Standard | First interaction of each session | Status text persists | Readily available; one-tap "Talk to a representative" |
| Zone 3 (Enterprise) | Comprehensive | First interaction + at session resume | Periodic reminder + pre-transaction reconfirmation | Proactive offer; on request always honored |

---

## Step 2: Author Disclosure Message Templates

All copy below is **illustrative** — your Compliance and Legal teams should approve final wording.

**Basic Disclosure (Zone 1 / external sharing only):**

> You're chatting with an AI assistant. For complex questions, ask to speak with a representative.

**Standard Disclosure (Zone 2):**

> You're interacting with an AI-powered assistant designed to help with **\[purpose]**. Information here is general; please verify important details with a licensed representative. Would you like to speak with a person?

**Comprehensive Disclosure (Zone 3 — regulated, customer-facing):**

> **Important:** You're communicating with an AI assistant, not a human representative. This AI:
>
> - Provides general information only and does not provide personalized investment, tax, or legal advice
> - May not have access to your complete account picture
> - Cannot replace the judgment of a licensed professional
>
> For account-specific questions, recommendations, or complaints, please ask to be transferred to a representative at any time.

**Jurisdiction overlays (Zone 3, append where applicable):**

| Jurisdiction | Required Overlay (illustrative) |
|--------------|----------------------------------|
| California (SB 1001) | Single-line "I am a bot" statement before any commercial-transaction prompt |
| California (SB 243, minor users) | Periodic AI reminder; surface "You're chatting with an AI" every 3 hours of continuous interaction |
| Utah (AI Policy Act / SB 149) | Clear AI disclosure at the start of any meaningful interaction in regulated sectors (finance, insurance, etc.) |
| Colorado (CO AI Act, effective Feb 1 2026) | Up-front AI disclosure, on-request human escalation, plain-language explanation of any automated decision affecting the consumer |

---

## Step 3: Configure the Conversation-Start (Greeting) Disclosure

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select the target agent → **Topics** → System topic **Conversation Start** (create if missing)
3. As the **first node**, add a **Send a message** node with the approved disclosure copy for the relevant zone
4. Add a **Set a variable** node `Global.DisclosureShown = true` (used by the logging step in Step 6)
5. Add an **Adaptive Card** with two buttons: `[I understand]` and `[Talk to a representative]` — the second routes to the Escalate topic (Step 4)
6. **Test in the channel test pane** — the disclosure should appear before any other agent reply

!!! tip "Channel coverage"
    The Conversation Start topic fires for each new conversation in Web Chat, Teams, and Omnichannel. Verify it also fires correctly in any embedded Direct Line clients — some custom clients suppress system events.

---

## Step 4: Configure Human Handoff via the Escalate Topic + Transfer Conversation Node

This is the canonical Microsoft Copilot Studio pattern (the older "Transfer to Agent" wording is deprecated).

1. **Topics** → System topic **Escalate** → open
2. Confirm trigger phrases include: `talk to a person`, `talk to a human`, `representative`, `agent`, `advisor`, `human`, `complaint`
3. Add or confirm a **Send a message** node summarizing what the AI has captured so far (passed to the live agent as context)
4. Add a **Transfer conversation** node (Add node → Topic management → **Transfer conversation**)
5. In the node properties:
    - **Engagement hub:** select your configured target (Dynamics 365 Customer Service / Microsoft 365 / Generic)
    - **Context variables:** pass `User.AccountId` (if available), `Global.SessionId`, `Global.DisclosureShown`, and a redacted conversation summary
6. Publish the agent
7. For Dynamics 365 Customer Service handoff, also complete the steps in [Microsoft Learn: Configure handoff to Dynamics 365 Customer Service](https://learn.microsoft.com/en-us/microsoft-copilot-studio/configuration-hand-off-omnichannel)

---

## Step 5: Configure Reinforcement (Reminders + Pre-Transaction Reconfirm)

For Zone 3 agents:

1. Create a **topic** named `AI Reminder`
2. Trigger: condition node evaluating `System.Conversation.MessageCount > 10` **OR** `(System.Conversation.LastReminderTime is blank) OR (now() - System.Conversation.LastReminderTime > Time(0,5,0))`
3. Body: short reminder ("Reminder: you're chatting with an AI. Ask anytime to speak with a representative.")
4. Set `System.Conversation.LastReminderTime = utcNow()`

For pre-transaction confirmation:

1. In any topic that initiates an account action (transfer, trade, dispute), insert a **Question** node before the action with two options: `Continue with AI` / `Connect me with a representative`
2. The "Connect" option routes to the Escalate topic from Step 4

For California SB 243 minor-protection scenarios, set a 3-hour reminder cadence (also raise to Compliance whether the agent is in scope of SB 243 at all).

---

## Step 6: Configure Disclosure-Event Logging

Capture an immutable log entry every time disclosure is delivered or escalation is offered/taken. This evidence supports Control 3.4 (audit-log readiness) and Control 2.13 (recordkeeping).

**Recommended fields (Dataverse table or Log Analytics custom log):**

| Field | Type | Notes |
|-------|------|-------|
| `SessionId` | GUID | From `System.Conversation.Id` |
| `Timestamp` | DateTime (UTC) | Event time |
| `EventType` | Choice | `DisclosureDelivered` / `ReminderDelivered` / `EscalationOffered` / `EscalationAccepted` / `EscalationCompleted` |
| `DisclosureType` | Choice | `Basic` / `Standard` / `Comprehensive` |
| `DisclosureVersion` | String | Pulled from a global variable set by Compliance |
| `Jurisdiction` | String | CA / UT / CO / Other |
| `Channel` | String | Web / Teams / Omnichannel / DirectLine |
| `UserPseudoId` | String | One-way hash of user identifier (do **not** store raw PII unless retention/PII rules permit) |

**Implementation pattern:**

1. From each disclosure-related node, call a **Power Automate** flow named `LogAiDisclosureEvent`
2. The flow performs a `Create record` against the chosen log target
3. Apply Dataverse column-level security and DLP per Pillar 1 (Control 1.6) so PII is not exposed to non-compliance roles

---

## Configuration Matrix by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|--------------------|
| Initial Disclosure | Basic | Standard | **Comprehensive + jurisdiction overlay** |
| Periodic Reminder | None | Optional | **Required (≥ every 10 messages or 5 minutes)** |
| Pre-Transaction Reconfirm | None | Optional | **Required for any account-impacting action** |
| Human Escalation | On request | Readily available (1 tap) | **Proactively offered + always on request** |
| Disclosure Logging | Optional | Recommended | **Required, ≥ 6-year retention** |
| Disclosure Versioning | Recommended | Required | **Required with named approver + change ticket** |
| State Overlay (CA/UT/CO) | N/A | If user location indicates | **Required** |

---

## Illustrative FSI Configuration (Wealth Advisory Bot)

```yaml
# ILLUSTRATIVE — adapt to your tenant. Final wording requires Compliance + Legal sign-off.
agent: Client Advisory Bot
environment: FSI-Wealth-Prod
zone: 3 (Enterprise Managed)

disclosures:
  initial:
    type: Comprehensive
    version: "2026.04-rev1"
    approved_by: "Compliance Officer (J. Doe)"
    effective_date: "2026-04-15"
    message: |
      Important: You're communicating with an AI assistant. This AI provides general
      information only and does not provide personalized investment advice. For specific
      recommendations regarding your portfolio, please ask to speak with your advisor.

  periodic_reminder:
    trigger: "MessageCount > 10 OR ElapsedMinutes > 5"
    message: "Reminder: you're chatting with an AI assistant. Want to speak with your advisor?"

  pre_transaction:
    trigger: "Topic in (PlaceTrade, Withdraw, Transfer)"
    require_acknowledgement: true
    options: ["I understand — continue with AI", "Connect me with my advisor"]

handoff:
  copilot_studio_topic: "Escalate (system)"
  node: "Transfer conversation"
  engagement_hub: "Dynamics 365 Customer Service"
  queue: "Wealth Advisory Queue"
  triggers:
    - "user keyword: human, advisor, representative, complaint"
    - "topic: investment recommendation"
    - "transaction value > 10000"
    - "agent confidence < 0.7"
  fallback: "Create callback request in Dynamics 365"

logging:
  target: "Dataverse table: fsi_aidisclosurelog"
  retention_years: 7
  fields:
    - SessionId
    - Timestamp
    - EventType
    - DisclosureType
    - DisclosureVersion
    - Jurisdiction
    - Channel
    - UserPseudoId
```

---

## Validation

After completing these steps, confirm:

- [ ] Disclosure renders as the **first** message in every channel (Web, Teams, Omnichannel)
- [ ] The `[Talk to a representative]` button routes through the Escalate topic and reaches the live engagement hub in a test session
- [ ] Periodic reminder fires at the configured threshold during a long test session
- [ ] Pre-transaction reconfirm appears before any account-impacting action
- [ ] Each event creates a row in the disclosure log with the expected fields
- [ ] Disclosure copy version, approver, and effective date are recorded in the Agent Card (Control 3.1)

---

[Back to Control 2.19](../../../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
