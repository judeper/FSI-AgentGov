# Troubleshooting: Control 2.19 - Customer AI Disclosure and Transparency

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Disclosure not showing | Greeting topic misconfigured | Verify greeting topic has disclosure as first message |
| Escalation not working | Trigger phrases not recognized | Check escalation trigger configuration |
| Disclosure not logged | Logging action missing | Add logging step to conversation flow |
| Periodic reminder not appearing | Threshold not tracked | Implement message count/time tracking |
| Wrong disclosure level | Zone classification incorrect | Verify agent zone classification |

---

## Detailed Troubleshooting

### Issue: Disclosure Not Appearing

**Symptoms:** Users can interact without seeing AI disclosure

**Diagnostic Steps:**

1. Check greeting topic configuration:
   ```
   Copilot Studio > Agent > Topics > Greeting
   Verify disclosure is first message node
   ```

2. Check topic trigger:
   - Greeting should trigger on conversation start
   - Verify no conditions blocking disclosure

3. Test in different channels (web, Teams, etc.)

**Resolution:**

- Add disclosure as first message in greeting topic
- Remove any conditions that bypass disclosure
- Ensure topic triggers on all channels

---

### Issue: Human Escalation Not Triggering

**Symptoms:** Users ask for human but stay with AI

**Diagnostic Steps:**

1. Test escalation trigger phrases:
   - "human"
   - "representative"
   - "speak to someone"
   - etc.

2. Check escalation topic configuration:
   ```
   Copilot Studio > Agent > Topics > Escalation topic
   ```

3. Verify escalation action (transfer, ticket, callback)

**Resolution:**

- Add missing trigger phrases
- Verify escalation topic is published
- Check transfer queue/action is valid
- Test end-to-end escalation flow

---

### Issue: Disclosure Not Being Logged

**Symptoms:** Compliance cannot find disclosure records

**Diagnostic Steps:**

1. Check logging action in conversation flow:
   - Should occur after disclosure is sent
   - Should capture required fields

2. Verify Dataverse/logging connection:
   - Connection is valid
   - Table exists with correct schema

3. Check for errors in flow execution

**Resolution:**

- Add logging action if missing
- Fix connection credentials
- Create logging table if missing
- Correct field mapping errors

---

### Issue: Periodic Reminder Not Appearing

**Symptoms:** Long conversations don't get reminder

**Diagnostic Steps:**

1. Check reminder tracking:
   - Message count variable
   - Session time tracking

2. Verify reminder topic trigger:
   - Condition: count > threshold OR time > threshold
   - Topic exists and is published

3. Test with extended conversation

**Resolution:**

- Implement message/time tracking
- Create and publish reminder topic
- Adjust threshold if too high
- Test trigger conditions

---

## How to Confirm Configuration is Active

### Disclosure Delivery

1. Start a new conversation
2. Verify disclosure appears first
3. Check disclosure content is complete

### Human Escalation

1. Say "human" or "representative"
2. Verify escalation offers appear
3. Test actual transfer if possible

### Logging

1. Complete a test conversation
2. Query disclosure log
3. Verify record exists with correct data

---

## Escalation Path

If issues persist after troubleshooting:

1. **Copilot Studio Admin** - Agent configuration
2. **Compliance** - Disclosure content requirements
3. **Legal** - Regulatory language questions
4. **Microsoft Support** - Platform issues

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| No native disclosure feature | Must implement manually | Use greeting topic |
| Escalation limited by channel | Some channels don't support transfer | Offer callback option |
| Session time tracking complex | Hard to implement | Use message count instead |
| Disclosure acknowledgment not native | Cannot force user confirmation | Log delivery; consider approval step |

---

[Back to Control 2.19](../../../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
