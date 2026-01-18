# Control 1.11: Conditional Access and Phishing-Resistant MFA - Verification & Testing

> This playbook provides verification and testing guidance for [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md).

---

## Verification Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Conditional Access | Overview dashboard displayed |
| 2 | Check Policy Summary | Agent Identities card shows count |
| 3 | Review Policies list | Policies visible with states |
| 4 | Navigate to Authentication methods | Method policies displayed |
| 5 | Navigate to Agent ID (Preview) | Agent overview with metrics |
| 6 | Check All agent identities | Agent list with status |
| 7 | Review Agent collections | Global and Quarantined visible |
| 8 | Check Sign-in logs (Is Agent: Yes) | Agent sign-ins logged |
| 9 | Open recent maker sign-in | Applied CA Policies shows policy and result |
| 10 | Validate Tier 3 auth details | FIDO2 or Certificate-based shown |
| 11 | Review CA audit logs | Policy create/modify events logged |
| 12 | Run What if for break-glass | No CA policies apply |
| 13 | Export Tier 3 sign-in record | JSON includes CA and auth details |

---

## Test Cases

### Test 1: MFA Enforcement

1. Sign in as test user in baseline policy scope
2. Attempt to access cloud app
3. **Expected:** MFA challenge presented
4. Complete MFA
5. **Expected:** Access granted

### Test 2: Phishing-Resistant MFA

1. Sign in as Tier 3 agent creator
2. Attempt to access Power Platform
3. **Expected:** FIDO2/Certificate auth required
4. Complete phishing-resistant auth
5. **Expected:** Access granted

### Test 3: Break-Glass Exclusion

1. Run What if for break-glass account
2. Select all cloud apps
3. **Expected:** No CA policies apply
4. Test actual sign-in (controlled window)
5. **Expected:** Access without CA enforcement

### Test 4: Risk-Based Response

1. Simulate high-risk sign-in
2. **Expected:** Additional authentication required
3. **Expected:** Password change prompted if user risk high

### Test 5: Agent Sign-In Logging

1. Trigger agent authentication
2. Navigate to Agent ID > Sign-in logs
3. Filter for agent sign-ins
4. **Expected:** Agent sign-in event logged with details

---

## Evidence Artifacts

- [ ] CA policy export (JSON) with assignments and controls
- [ ] Authentication methods configuration screenshots
- [ ] Authentication strengths configuration
- [ ] Sign-in log samples for agent makers/admins
- [ ] Agent-related sign-ins with CA status
- [ ] Audit log entries for policy changes
- [ ] Break-glass account documentation and exclusions
- [ ] What if output for break-glass verification
- [ ] Quarterly break-glass test evidence

---

## Zone-Specific Testing

### Zone 1 (Personal Productivity)

- Baseline MFA applies tenant-wide
- No additional CA requirements
- Document any exceptions

### Zone 2 (Team Collaboration)

- Strong auth for admin/maker roles
- Risk-aware access policies
- Retain policy export + sign-in samples

### Zone 3 (Enterprise Managed)

- Phishing-resistant MFA enforced
- Changes require change ticket
- Retain policy export + sign-in samples

---

## Authentication Methods by Tier

| Method | Tier 1 | Tier 2 | Tier 3 |
|--------|--------|--------|--------|
| SMS/Voice | Allowed | Not recommended | Blocked |
| Authenticator App | Allowed | Allowed | Limited |
| FIDO2 Security Key | Allowed | Recommended | **Required** |
| Certificate-based | Allowed | Recommended | **Required** |

---

## Confirmation Checklist

- [ ] CA policies created for all governance tiers
- [ ] Break-glass accounts excluded and verified
- [ ] Named locations configured
- [ ] Authentication methods configured per tier
- [ ] Authentication strengths defined
- [ ] Agent ID dashboard reviewed
- [ ] Agent sponsors assigned (Zone 2/3)
- [ ] Sign-in monitoring configured
- [ ] Evidence artifacts collected

---

*Updated: January 2026 | Version: v1.1*
