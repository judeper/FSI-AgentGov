# Verification & Testing: Control 2.19 — Customer AI Disclosure and Transparency

**Last Updated:** April 2026
**Cadence:** Pre-go-live, on every disclosure-copy change, and at least quarterly thereafter
**Primary Owner:** Copilot Studio Agent Author (with Compliance Officer sign-off on test evidence)

---

## Test Environment Requirements

- Non-production Copilot Studio environment with the same disclosure copy and engagement-hub configuration as production (Control 2.3)
- Test user accounts simulating each in-scope channel (Web Chat, Microsoft Teams, Omnichannel, embedded Direct Line)
- Read access to the disclosure-event log (Dataverse `fsi_aidisclosurelog` table or equivalent)
- A test queue in Dynamics 365 Customer Service (or your generic engagement hub) that can confirm receipt of the **Transfer conversation** payload

---

## Manual Verification Steps

### Test 1 — Initial Disclosure Renders First

1. Start a new conversation with the agent in each channel
2. Observe the very first message from the agent
3. **Expected:** approved Zone-appropriate disclosure copy renders before any other content; in Zone 3, the comprehensive disclosure with `[I understand]` and `[Talk to a representative]` choices is shown

### Test 2 — Disclosure Content Completeness

1. Read the rendered disclosure for a Zone 3 agent
2. Confirm presence of: AI identification, capability statement, limitation statement, on-request human escalation, and (where applicable) jurisdiction overlay
3. **Expected:** all four base elements present; CA / UT / CO overlay copy renders for the matching jurisdiction

### Test 3 — Human Handoff via Escalate Topic

1. Send the trigger phrase `talk to a representative`
2. Confirm the system **Escalate** topic fires
3. Confirm the **Transfer conversation** node executes and the conversation appears in the configured engagement hub queue
4. **Expected:** payload includes `SessionId`, `DisclosureShown`, redacted summary, and any account context expected by the live agent

### Test 4 — On-Request Escalation (Colorado AI Act path)

1. Begin a session with the Colorado overlay enabled (test user in CO)
2. Mid-conversation, type `I want to talk to a person`
3. **Expected:** escalation occurs immediately; no friction prompt blocks the request

### Test 5 — Periodic Reminder (Zone 3)

1. Hold a continuous test session of ≥ 11 messages or ≥ 5 minutes
2. **Expected:** reminder topic fires once at the threshold and at the configured cadence thereafter; reminder text identifies the agent as AI and offers handoff

### Test 6 — Pre-Transaction Reconfirmation (Zone 3)

1. Drive the agent into a topic that initiates an account-impacting action (e.g., `place a trade`, `transfer funds`)
2. **Expected:** the Question node renders before the action and offers `Connect me with a representative` as a valid option that routes to the Escalate topic

### Test 7 — Disclosure Logging End-to-End

1. Run Test 1 + Test 3 + Test 5 in sequence
2. Query `fsi_aidisclosurelog` for the test `SessionId`
3. **Expected:** rows for `DisclosureDelivered`, `ReminderDelivered`, `EscalationOffered`, `EscalationAccepted`, `EscalationCompleted` with correct `DisclosureType`, `DisclosureVersion`, `Jurisdiction`, and `Channel`

### Test 8 — Disclosure Versioning Integrity

1. Trigger a disclosure copy update via your change process
2. **Expected:** new `DisclosureVersion` value appears in subsequent log rows; the previous version is retained and queryable; the change ticket and approver are recorded in the Agent Card (Control 3.1)

---

## Test Case Matrix

| Test ID | Scenario | Channel | Zone | Jurisdiction | Expected Result | Pass/Fail |
|---------|----------|---------|------|--------------|-----------------|-----------|
| TC-2.19-01 | Initial disclosure renders first | Web | 3 | Default | Comprehensive disclosure shown before any other content | |
| TC-2.19-02 | Initial disclosure renders first | Teams | 3 | Default | Same as above | |
| TC-2.19-03 | Initial disclosure renders first | Omnichannel | 3 | Default | Same as above | |
| TC-2.19-04 | Disclosure content complete | Web | 3 | Default | All four elements present | |
| TC-2.19-05 | Jurisdiction overlay — CA | Web | 3 | CA | SB 1001 line present | |
| TC-2.19-06 | Jurisdiction overlay — UT | Web | 3 | UT | UT AI Policy Act line present | |
| TC-2.19-07 | Jurisdiction overlay — CO | Web | 3 | CO | CO AI Act line present | |
| TC-2.19-08 | Escalate via keyword | Web | 3 | Default | Transfer conversation fires; payload received in hub | |
| TC-2.19-09 | Escalate via button | Web | 3 | Default | Same as above | |
| TC-2.19-10 | On-request escalation honored | Web | 3 | CO | No friction; escalates immediately | |
| TC-2.19-11 | Periodic reminder fires | Web | 3 | Default | Reminder appears at message ≥ 11 or 5 min | |
| TC-2.19-12 | Pre-transaction reconfirm | Web | 3 | Default | Question node with handoff option renders | |
| TC-2.19-13 | DisclosureDelivered logged | Web | 3 | Default | Row in fsi_aidisclosurelog with correct fields | |
| TC-2.19-14 | EscalationAccepted logged | Web | 3 | Default | Row written and matches SessionId | |
| TC-2.19-15 | DisclosureVersion increments | Web | 3 | Default | New version observed after update | |

---

## Evidence Collection Checklist

### Disclosure Configuration
- [ ] Screenshot — Conversation Start topic showing the disclosure as the first node
- [ ] Screenshot — system **Escalate** topic showing the **Transfer conversation** node and engagement-hub binding
- [ ] PDF — Compliance/Legal-approved disclosure copy register with version, approver, effective date

### Disclosure Delivery
- [ ] Screenshot — disclosure rendered in Web Chat session
- [ ] Screenshot — disclosure rendered in Teams session
- [ ] Screenshot — disclosure rendered in Omnichannel session
- [ ] Screenshot — periodic reminder rendered
- [ ] Screenshot — pre-transaction reconfirm rendered
- [ ] Screenshot — Colorado overlay rendered

### Handoff
- [ ] Screenshot — live agent receiving transferred conversation in Dynamics 365 Customer Service / hub
- [ ] Export — handoff payload captured (with PII redacted)

### Logging and Reporting
- [ ] CSV — `fsi_aidisclosurelog` export for the test period (output of `Get-DisclosureLog.ps1`)
- [ ] JSON — summary file for the same period
- [ ] MD — generated `DisclosureComplianceReport-*.md`
- [ ] TXT — `SHA256SUMS.txt` with hashes of the above artifacts

---

## Evidence Artifact Naming Convention

```
Control-2.19_[ArtifactType]_[YYYYMMDD].[ext]

Examples:
- Control-2.19_DisclosureCopyRegister_20260415.pdf
- Control-2.19_ConversationStartTopic_20260415.png
- Control-2.19_EscalateTopic_TransferConversationNode_20260415.png
- Control-2.19_HandoffPayload_20260415.json
- Control-2.19_DisclosureLog_20260415.csv
- Control-2.19_ComplianceReport_20260415.md
- Control-2.19_SHA256SUMS_20260415.txt
```

---

## Attestation Statement Template

```markdown
## Control 2.19 Attestation — Customer AI Disclosure

**Organization:** [Organization Name]
**Control Owner:** [Name / Role]
**Period Covered:** [YYYY-MM-DD] to [YYYY-MM-DD]
**Date of Attestation:** [YYYY-MM-DD]

I attest that, for the period covered:

1. AI identification was rendered at the start of every customer conversation across all in-scope channels
2. Disclosure copy was reviewed and approved by Compliance/Legal; approver and effective date are recorded in the Agent Card (Control 3.1)
3. The Copilot Studio system Escalate topic includes a working Transfer conversation node and successfully routes test sessions to the configured engagement hub
4. Periodic reminders and pre-transaction reconfirmations are configured for Zone 3 agents and fired during testing
5. Jurisdiction overlays for CA / UT / CO render correctly for the relevant test users
6. Disclosure events are logged to fsi_aidisclosurelog with the required fields and retained per the firm's books-and-records policy (≥ 6 years)
7. Outstanding deviations are tracked in the firm's risk register with target remediation dates

Disclosure delivery rate (period): [X]%
Escalation take rate (period, informational): [X]%
Last Compliance review date: [YYYY-MM-DD]

Signature: _____________________________
Date:      _____________________________
```

---

[Back to Control 2.19](../../../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
