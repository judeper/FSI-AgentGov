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
- Risk-based policies for Zone 3-4 environments
- Session controls limit token lifetime
