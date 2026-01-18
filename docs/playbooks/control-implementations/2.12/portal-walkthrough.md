# Portal Walkthrough: Control 2.12 - Supervision and Oversight (FINRA Rule 3110)

**Last Updated:** January 2026
**Portal:** Copilot Studio, Power Automate
**Estimated Time:** 4-6 hours

## Prerequisites

- [ ] Written Supervisory Procedures (WSP) addendum drafted
- [ ] Designated principals identified (Series 24 for BD)
- [ ] Copilot Studio Maker access
- [ ] Power Automate license

---

## Step-by-Step Configuration

### Step 1: Document WSP Addendum

Create Written Supervisory Procedures addendum for AI agents:

1. Define scope of AI agent supervision
2. Document supervisory responsibilities
3. Specify review frequencies and sampling rates
4. Define escalation procedures
5. Document record retention requirements

### Step 2: Configure Human-in-the-Loop (HITL)

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select agent > **Settings**
3. Configure generative answers:
   - For Zone 3: Enable review before sending
4. Configure topics requiring human approval

### Step 3: Set Up Sampling Protocol

Define sampling rates by zone:

| Zone | Sampling Rate | Review Frequency |
|------|---------------|------------------|
| Zone 1 | 1% spot check | Monthly |
| Zone 2 | 10% statistical | Weekly |
| Zone 3 | 100% high-risk, 10% routine | Real-time/Daily |

### Step 4: Create Review Queue Workflow

1. Open [Power Automate](https://make.powerautomate.com)
2. Create flow for supervision queue:
   - Trigger: Agent response flagged
   - Action: Create review item in SharePoint
   - Action: Notify designated principal
   - Action: Wait for approval/rejection
   - Action: Log decision

### Step 5: Configure Exception Escalation

1. Define escalation triggers:
   - Investment recommendations
   - Account-specific advice
   - Regulatory disclosures
   - Customer complaints
2. Route to appropriate supervisor
3. Document escalation decisions

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **WSP Coverage** | Awareness | Documented procedures | Full addendum |
| **HITL** | None | High-risk topics | All generative answers |
| **Sampling** | Annual spot check | 10% statistical | 100% high-risk |
| **Supervision** | Self-service | Owner review | Principal required |
| **Documentation** | Basic | Tracked | Full evidence trail |

---

## FSI Example Configuration

```yaml
Supervision: Investment Advisory Bot

WSP Addendum: FSI-AI-Supervision-2026-v1
Effective Date: January 1, 2026
Designated Principal: [Series 24 Name]

HITL Configuration:
  - Investment recommendations: Review required
  - Account-specific advice: Review required
  - General information: Pass-through

Sampling Protocol:
  High-Risk: 100% (investment recommendations)
  Medium-Risk: 25% (account inquiries)
  Low-Risk: 5% (general information)

Review Queue:
  Platform: SharePoint + Power Automate
  SLA: 15 minutes for high-risk
  Escalation: CISO if SLA breached

Evidence Retention:
  Duration: 6 years
  Location: SharePoint with retention label
```

---

## Validation

After completing these steps, verify:

- [ ] WSP addendum documented and approved
- [ ] HITL configured for Zone 3 agents
- [ ] Sampling protocol implemented
- [ ] Review queue functional
- [ ] Supervision evidence retained

---

[Back to Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
