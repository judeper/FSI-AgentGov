# Control 1.8: Runtime Protection and External Threat Detection - Verification & Testing

> This playbook provides verification and testing guidance for [Control 1.8](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md).

---

## Verification Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Confirm Managed Environment | Environment shows as Managed |
| 2 | Test prompt injection detection | Blocked with log entry |
| 3 | Validate egress controls | Blocked connector/tool invocation logged |
| 4 | Verify alert configuration | FSI alerts created and enabled |
| 5 | Test content moderation | Appropriate moderation response |
| 6 | Validate SIEM integration (Tier 3) | Events streaming within SLA |
| 7 | Verify external threat detection | Webhook receives requests (if enabled) |

---

## Test Cases

### Test 1: Prompt Injection Detection

1. Submit test prompt with injection pattern (e.g., "ignore previous instructions")
2. **Expected:** Blocked with log entry
3. Verify event appears in audit log

### Test 2: Egress Controls

1. Attempt to invoke a blocked/high-risk connector from the agent
2. Attempt to reach a non-approved destination
3. **Expected:** Invocation blocked; audit log captured with policy reason

### Test 3: Content Moderation

1. Submit content that should be blocked (e.g., harmful content)
2. **Expected:** Appropriate moderation response
3. Verify moderation event logged

### Test 4: Alert Generation

1. Generate test security event (e.g., prompt injection attempt)
2. **Expected:** Alert generated and delivered to configured recipients
3. Verify alert appears in Purview

### Test 5: SIEM Integration

1. Generate test security event
2. **Expected:** Event appears in SIEM within SLA
3. Verify event correlation is working

---

## Evidence Artifacts

- [ ] Screenshot: Managed environment confirmation
- [ ] Screenshot: Runtime protection settings
- [ ] Export: Alert policy configurations
- [ ] Log: Prompt injection detection test
- [ ] Export/screenshot: DLP policy and connector restrictions
- [ ] Log: Egress/tool blocking test
- [ ] Documentation: Incident response playbook
- [ ] SIEM: Power Platform connector status
- [ ] Screenshot: External threat detection configuration (if enabled)
- [ ] Documentation: Vendor risk assessment (if using third-party webhook)

---

## Zone-Specific Testing

### Zone 1 (Personal Productivity)

- Runtime protection: Optional
- Prompt injection: Log only
- Response SLA: Best effort

### Zone 2 (Team Collaboration)

- Runtime protection: Required
- Prompt injection: Block and log
- Response SLA: 4 hours

### Zone 3 (Enterprise Managed)

- Runtime protection: Required - Maximum
- Prompt injection: Block, log, and investigate
- Response SLA: 15 minutes
- Incident playbook: Required

---

## Confirmation Checklist

- [ ] Managed Environment is enabled
- [ ] Runtime protection settings are configured
- [ ] Prompt injection detection is active
- [ ] Content moderation is enabled
- [ ] Egress controls are in place
- [ ] Alert policies are created and enabled
- [ ] SIEM integration is functional (Tier 2-3)
- [ ] Incident response playbook is documented
- [ ] Evidence artifacts collected and stored

---

*Updated: January 2026 | Version: v1.2*
