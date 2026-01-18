# Portal Walkthrough: Control 2.19 - Customer AI Disclosure and Transparency

**Last Updated:** January 2026
**Portal:** Copilot Studio, Custom Implementation
**Estimated Time:** 2-4 hours initial setup

## Prerequisites

- [ ] Disclosure templates approved by Legal/Compliance
- [ ] Customer communication channels identified
- [ ] Human escalation paths defined
- [ ] Disclosure tracking mechanism established
- [ ] Regulatory requirements mapped (SEC Reg BI, CFPB UDAAP, FINRA)

---

## Step-by-Step Configuration

### Step 1: Define Disclosure Requirements by Zone

| Zone | Disclosure Level | Timing | Human Escalation |
|------|-----------------|--------|------------------|
| Zone 1 | Basic | On first interaction | On request |
| Zone 2 | Standard | On first interaction + periodic | Readily available |
| Zone 3 | Comprehensive | Every session + transaction | Proactive offer |

### Step 2: Create Disclosure Message Templates

**Basic Disclosure (Zone 1):**
```
You are interacting with an AI assistant. For complex questions,
ask to speak with a representative.
```

**Standard Disclosure (Zone 2):**
```
This is an AI-powered assistant designed to help with [purpose].
While I strive to provide accurate information, I recommend verifying
important details with a licensed representative. Would you like to
speak with a human agent?
```

**Comprehensive Disclosure (Zone 3):**
```
IMPORTANT: You are communicating with an AI assistant. This AI:
- Provides general information only, not personalized advice
- May not have access to your complete financial picture
- Cannot replace the judgment of a licensed professional

For financial advice, investment recommendations, or account-specific
questions, please speak with a licensed representative.
[Connect me with a representative]
```

### Step 3: Configure Agent Greeting Topic

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select target agent
3. Navigate to **Topics** > **Greeting** (or create new)
4. Add disclosure message as first response
5. Add human escalation option

**Example Topic Flow:**
```
Trigger: Conversation start
  → Send disclosure message
  → Offer human escalation option
  → Continue to main conversation flow
```

### Step 4: Implement Human Escalation Path

1. In agent topics, add escalation triggers:
   - User requests human
   - Sensitive topic detected
   - Low confidence response
   - Transaction threshold exceeded

2. Configure escalation action:
   - Transfer to Teams queue
   - Create support ticket
   - Provide callback option

### Step 5: Configure Disclosure Tracking

Track that disclosures were delivered:

1. Log disclosure events:
   - Timestamp
   - User identifier (anonymized)
   - Disclosure type
   - Escalation offered/taken

2. Create compliance reports:
   - Disclosure delivery rate
   - Escalation rate
   - User acknowledgment (if required)

### Step 6: Periodic Disclosure Reminders

For Zone 3 agents with extended conversations:

1. Create reminder topic:
   - Triggers after N messages or X minutes
   - Re-states AI nature
   - Offers escalation

2. Configure in conversation flow:
   - Track message count or time
   - Insert reminder at threshold

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|--------------------|
| **Initial Disclosure** | Basic | Standard | **Comprehensive** |
| **Periodic Reminder** | None | Optional | **Required** |
| **Human Escalation** | On request | Readily available | **Proactively offered** |
| **Disclosure Logging** | Optional | Recommended | **Required with retention** |
| **Acknowledgment** | None | Optional | **Consider requiring** |

---

## FSI Example Configuration

```yaml
Agent: Client Advisory Bot
Environment: FSI-Wealth-Prod
Zone: 3 (Enterprise Managed)

Disclosure Configuration:
  Initial:
    Type: Comprehensive
    Message: |
      IMPORTANT DISCLOSURE: You are interacting with an AI-powered
      assistant. This AI provides general information only and does
      not provide personalized investment advice. For specific
      recommendations regarding your portfolio or financial situation,
      please speak with your assigned financial advisor.

      [Connect me with my advisor]

  Periodic:
    Trigger: Every 10 messages OR 5 minutes
    Message: |
      Reminder: You're chatting with an AI assistant.
      Would you like to speak with a human advisor?

  Pre-Transaction:
    Trigger: Before any account action
    Message: |
      Before proceeding, please confirm you understand this is an AI
      assistant. For personalized advice, please speak with an advisor.
      [I understand] [Connect me with an advisor]

Human Escalation:
  Triggers:
    - User says "human", "person", "advisor", "representative"
    - Confidence < 0.7
    - Topic: Investment recommendation
    - Topic: Complaint
    - Transaction > $10,000

  Action: Transfer to Teams "Wealth Advisory Queue"

  Fallback: Create callback request in Dynamics

Tracking:
  Log To: Dataverse - AI Disclosure Log
  Retain: 7 years
  Fields: SessionId, Timestamp, DisclosureType, EscalationOffered, EscalationTaken
```

---

## Validation

After completing these steps, verify:

- [ ] Disclosure appears on first interaction
- [ ] Human escalation option is visible and functional
- [ ] Periodic reminders trigger as configured
- [ ] Disclosure events are logged
- [ ] Escalation transfers to correct queue
- [ ] Compliance can generate disclosure reports

---

[Back to Control 2.19](../../../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
