# Verification & Testing: Control 1.23 - Step-Up Authentication

**Last Updated:** January 2026

## Manual Verification Steps

### Test 1: Test Step-Up Trigger

1. Perform action requiring step-up (e.g., data export)
2. **EXPECTED:** Prompted for fresh authentication

### Test 2: Test Session Timeout

1. Authenticate, wait longer than session frequency
2. Attempt sensitive action
3. **EXPECTED:** Re-authentication required

### Test 3: Test MFA Strength Enforcement

1. Attempt critical action with SMS MFA
2. **EXPECTED:** Denied - phishing-resistant required

### Test 4: Test FIDO2 Acceptance

1. Complete step-up with FIDO2 key
2. **EXPECTED:** Action proceeds after authentication

---

## Test Cases

| Test ID | Scenario | Expected Result | Pass/Fail |
|---------|----------|-----------------|-----------|
| TC-1.23-01 | Step-up triggers on sensitive action | Auth prompt appears | |
| TC-1.23-02 | Session timeout enforced | Re-auth after 15/30/60 min | |
| TC-1.23-03 | SMS MFA rejected for critical | Access denied | |
| TC-1.23-04 | FIDO2 accepted | Action succeeds | |
| TC-1.23-05 | Sign-in log captures event | Context logged | |

---

## Evidence Collection Checklist

- [ ] Screenshot: Authentication contexts
- [ ] Screenshot: CA policy configuration
- [ ] Screenshot: Authentication strength settings
- [ ] Export: Sign-in logs with step-up events

---

## Attestation Statement Template

```markdown
## Control 1.23 Attestation - Step-Up Authentication

**Organization:** [Organization Name]
**Control Owner:** [Name/Role]
**Date:** [Date]

I attest that:

1. Authentication contexts are configured for sensitive operations:
   - c1: Financial Transaction (15 min)
   - c2: Data Export (30 min)
   - c3-c5: Other high-risk actions
2. Conditional Access policies enforce step-up requirements
3. Phishing-resistant MFA is required for Zone 3 critical operations
4. Sign-in logs capture step-up authentication events

**Authentication Contexts:** [Count]
**Step-Up Policies:** [Count]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 1.23](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
