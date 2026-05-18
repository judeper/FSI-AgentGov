# Troubleshooting: Control 2.19 — Customer AI Disclosure and Transparency

**Last Updated:** April 2026

---

## Common Issues at a Glance

| Issue | Likely Cause | First Action |
|-------|--------------|--------------|
| Disclosure not appearing on first turn | Conversation Start topic missing or disclosure node not first | Open the Conversation Start topic; ensure the disclosure Send-message node is the first node |
| Disclosure appears in Web but not in Teams | Custom welcome message is overriding the Conversation Start topic in the Teams channel | Disable the channel-level welcome message and let the topic fire |
| `Transfer conversation` node greyed out | Engagement hub not configured at the agent level | Configure handoff in Settings → Customer engagement (Dynamics 365 / generic hub) before adding the node |
| Handoff fires but no live agent receives | Queue routing rules / unified-routing workstream not bound | Verify the workstream + queue exist and that the bot user is added to the queue |
| Periodic reminder never fires | Threshold variable not initialised; condition uses wrong namespace | Set `System.Conversation.LastReminderTime` on Conversation Start; re-check condition expression |
| Disclosure event not logged | `LogAiDisclosureEvent` flow disabled or connection broken | Power Automate → check flow run history; reauthorize the Dataverse connection |
| Wrong disclosure level surfaces | Agent's zone classification incorrect in Agent Card | Reconcile with Control 3.1 inventory and reapply the right copy version |
| Jurisdiction overlay missing | Jurisdiction signal not flowing into the agent | Verify the upstream variable (e.g., session token claim or CRM lookup) is populated before the disclosure node |

---

## Detailed Troubleshooting

### Issue 1 — Disclosure Not Appearing

**Symptoms:** Users can interact without seeing AI disclosure.

**Diagnostic steps:**

1. Confirm the disclosure lives in the **Conversation Start** topic (not the legacy Greeting topic) and is the first node
2. In Microsoft Copilot Studio, open the **Test bot** pane and start a new conversation — does the disclosure appear here?
3. Reproduce in each customer channel (Web Chat, Teams, Omnichannel, Direct Line)
4. For Teams: open Teams Admin Center → Manage apps → your agent → confirm no custom welcome message is set on the Teams channel that would suppress the topic
5. For Direct Line / custom client: ensure the client sends an `event` activity of type `conversationUpdate` to fire the Conversation Start topic

**Resolution:**

- Move the disclosure Send-message node to position 1 in the Conversation Start topic
- Remove any condition node before it that might short-circuit it
- Republish the agent and clear channel caches
- For custom Direct Line clients, verify the welcome event handshake

---

### Issue 2 — Human Handoff Not Triggering

**Symptoms:** User asks for a human; the bot keeps responding as AI.

**Diagnostic steps:**

1. Open system topic **Escalate** → confirm trigger phrases include common synonyms (`human`, `person`, `representative`, `advisor`, `agent`, `complaint`)
2. Confirm a **Transfer conversation** node exists at the end of the topic (not just a Send-message that says "transferring…")
3. In the node properties, confirm the **engagement hub** dropdown is set (not "None") and the queue/workstream is selected
4. For Dynamics 365 Customer Service: confirm the bot's application user is added as a queue member and the unified-routing workstream is published
5. Check the most recent topic-execution trace in Copilot Studio for the Escalate topic

**Resolution:**

- Add missing trigger phrases (re-train the topic if necessary)
- Configure the engagement hub at the agent level (Settings → Customer engagement)
- Add the bot user to the target queue
- See [Microsoft Learn: hand off to a live agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-hand-off) and [Configure handoff to Dynamics 365 Customer Service](https://learn.microsoft.com/en-us/microsoft-copilot-studio/configuration-hand-off-omnichannel)

---

### Issue 3 — Disclosure Events Not Being Logged

**Symptoms:** Compliance cannot find disclosure rows in `fsi_aidisclosurelog`.

**Diagnostic steps:**

1. In Power Automate, open the `LogAiDisclosureEvent` flow → 28-day run history → look for failed runs
2. If runs fail with auth errors, the Dataverse connection has expired or the connection owner left the org
3. If runs succeed but no row appears, check `Create record` action input — column names may have drifted (`fsi_eventtype` vs `fsi_event_type`, etc.)
4. Confirm the flow is invoked from each disclosure-related node in the topic

**Resolution:**

- Reauthorize the Dataverse connection under a service account / managed identity
- Re-bind action inputs to the correct logical column names
- Add the flow call to any topic node that surfaces disclosure but currently skips logging

---

### Issue 4 — Periodic Reminder Not Appearing

**Symptoms:** Long sessions never see a reminder.

**Diagnostic steps:**

1. Open the `AI Reminder` topic → check the trigger condition syntax against current Power Fx grammar
2. Confirm `System.Conversation.LastReminderTime` is initialised on Conversation Start (otherwise the `now() - blank` comparison fails silently)
3. Check whether the reminder is competing with a higher-priority topic that always fires first

**Resolution:**

- Initialise the variable in Conversation Start
- Adjust topic priority so the reminder is reachable
- Lower the threshold in non-prod to validate the path before restoring production threshold

---

### Issue 5 — Wrong Disclosure Level

**Symptoms:** A Zone 3 agent shows the basic disclosure, or vice versa.

**Diagnostic steps:**

1. Open the Agent Card (Control 3.1) and confirm the recorded zone classification
2. Open the Conversation Start topic and confirm the message variant matches the zone
3. Inspect the disclosure-version global variable for staleness

**Resolution:**

- Update the Agent Card and re-publish the matching disclosure variant
- If the zone genuinely changed, run the Control 2.3 zone-promotion review before changing copy

---

## How to Confirm Configuration is Active

### Disclosure delivery
1. Start a fresh conversation in each customer channel
2. Confirm the disclosure renders first
3. Confirm `DisclosureDelivered` row in the log within 1 minute

### Human handoff
1. Use a trigger phrase
2. Confirm the live agent (or your test queue) receives the conversation with full context
3. Confirm `EscalationOffered` and `EscalationAccepted` rows in the log

### Logging integrity
1. Run `Validate-Control-2.19.ps1` (read-only)
2. All three checks should return `PASS`

---

## Escalation Path

| Tier | Owner | When to Engage |
|------|-------|----------------|
| 1 | Copilot Studio Agent Author | Topic content, node configuration, copy fixes |
| 2 | Power Platform Admin | Environment, connectors, engagement-hub binding, DLP impact |
| 3 | AI Administrator | Tenant-level Copilot settings affecting disclosure surfaces |
| 4 | Compliance Officer | Disclosure copy approval, regulatory interpretation |
| 5 | Legal Counsel | State-law (CA/UT/CO) edge cases, UDAAP exposure |
| 6 | Microsoft Support | Platform behavior (handoff failures, channel regressions) — open ticket via Power Platform Admin Center |

---

## Known Limitations (April 2026)

| Limitation | Impact | Workaround |
|------------|--------|------------|
| No native, tenant-wide "AI disclosure" toggle in Copilot Studio | Each agent must implement disclosure individually | Use a shared solution / template agent and clone for new agents |
| Topic content is not exposed by an admin API | Disclosure copy cannot be mutated via PowerShell | Use Copilot Studio portal or solution import; gate via Control 2.4 ALM |
| Some custom Direct Line clients suppress the conversation-start event | Disclosure may not render | Implement a client-side disclosure render OR require a starter intent that fires the topic |
| Forced acknowledgement of disclosure is not a built-in capability | Cannot block conversation until user clicks `[I understand]` natively | Use an Adaptive Card with required input + Question node that loops until acknowledged |
| Generic engagement-hub adapters require custom development | Non-Microsoft hubs need an adapter | Follow [Configure handoff to a generic engagement hub](https://learn.microsoft.com/en-us/microsoft-copilot-studio/configure-generic-handoff) and the [contact-center skill-handoff sample](https://github.com/microsoft/CopilotStudioSamples/tree/main/contact-center/skill-handoff) |

---

[Back to Control 2.19](../../../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
