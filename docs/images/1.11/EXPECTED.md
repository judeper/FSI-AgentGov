# Control 1.11: Conditional Access and Phishing-Resistant MFA

## Expected Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-entra-ca-policies.png` | Entra | Protection → Conditional Access → Policies | CA policies list |
| `02-entra-ca-create.png` | Entra | Policies → New policy | Policy creation panel |
| `03-entra-ca-assignments.png` | Entra | Policy → Assignments | Users/groups and apps assignment |
| `04-entra-ca-conditions.png` | Entra | Policy → Conditions | Risk, device, location conditions |
| `05-entra-ca-grant.png` | Entra | Policy → Grant | Grant controls (MFA, compliant device) |
| `06-entra-ca-session.png` | Entra | Policy → Session | Session controls |
| `07-entra-auth-methods.png` | Entra | Protection → Authentication methods | Authentication methods policies |
| `08-entra-phishing-resistant.png` | Entra | Authentication methods → Policies | FIDO2/Passkey configuration |
| `09-entra-auth-strengths.png` | Entra | Protection → Authentication strengths | Authentication strength definitions |

## Verification Focus

- CA policies target Power Platform and Copilot apps
- Phishing-resistant MFA required for privileged access
- Risk-based policies for Zone 3 environments
- Session controls limit token lifetime
- Capture from pre-production environment when possible
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates

---

## Screenshot Organization

Organize screenshots in this directory as:
- `1.11-01-entra-ca-policies.png` — CA policies list
- `1.11-02-entra-ca-create.png` — Policy creation panel
- `1.11-03-entra-ca-assignments.png` — Users/groups and apps assignment
- `1.11-04-entra-ca-conditions.png` — Risk, device, location conditions
- `1.11-05-entra-ca-grant.png` — Grant controls (MFA, compliant device)
- `1.11-06-entra-ca-session.png` — Session controls
- `1.11-07-entra-auth-methods.png` — Authentication methods policies
- `1.11-08-entra-phishing-resistant.png` — FIDO2/Passkey configuration
- `1.11-09-entra-auth-strengths.png` — Authentication strength definitions
