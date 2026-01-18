# Troubleshooting: Control 1.23 - Step-Up Authentication

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Step-up not triggering | Context not assigned to action | Map action to auth context |
| User can't complete step-up | No phishing-resistant method | Enroll FIDO2 or Windows Hello |
| Excessive step-up prompts | Session frequency too short | Adjust based on risk |
| Service principal bypass | SP not subject to step-up | Implement compensating control |

---

## Detailed Troubleshooting

### Issue: Step-Up Not Triggering

**Symptoms:** Sensitive action proceeds without re-authentication

**Resolution:**

1. Verify action is mapped to authentication context
2. Check CA policy targets the context
3. Verify CA policy is enabled (not report-only)
4. Check for policy conflicts or exceptions

---

### Issue: User Cannot Complete Step-Up

**Symptoms:** User denied even with MFA

**Resolution:**

1. Verify user has enrolled phishing-resistant method
2. Check authentication strength requirements
3. Verify user's device meets CA requirements
4. Help user register FIDO2 key or Windows Hello

---

## Escalation Path

1. **Security Administrator** - CA policy configuration
2. **Entra Admin** - Authentication methods
3. **Help Desk** - User enrollment assistance
4. **Microsoft Support** - Platform issues

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Service principals exempt | SPs don't authenticate interactively | Use approval workflow |
| Not all apps support contexts | Limited integration | Use app-level controls |
| User experience friction | More prompts | Balance security with usability |
| FIDO2 hardware dependency | Requires physical key | Also allow Windows Hello |

---

[Back to Control 1.23](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
