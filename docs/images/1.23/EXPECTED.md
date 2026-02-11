# Control 1.23: Step-Up Authentication for AI Agent Operations - Screenshot Specifications

## Required Screenshots

### Screenshot 1: Authentication Contexts Configuration
**Portal Path:** Microsoft Entra Admin Center → Protection → Authentication contexts
**What to capture:**
- Authentication contexts c1 through c5 defined (Financial Transaction, Data Export, External API, Config Change, Sensitive Query)
- Context IDs and display names
- Published status for each context

### Screenshot 2: Conditional Access Policy for Step-Up Authentication
**Portal Path:** Microsoft Entra Admin Center → Protection → Conditional Access → Policies
**What to capture:**
- CA policies configured for each authentication context (c1-c5)
- Policy targeting authentication context as cloud app assignment
- Grant controls requiring phishing-resistant MFA (FIDO2/Windows Hello)

### Screenshot 3: Authentication Strength Configuration
**Portal Path:** Microsoft Entra Admin Center → Protection → Authentication methods → Authentication strengths
**What to capture:**
- Phishing-resistant MFA strength definition
- Allowed authentication methods (FIDO2, Windows Hello for Business)
- Association with step-up CA policies

### Screenshot 4: Sign-In Frequency Session Controls
**Portal Path:** Microsoft Entra Admin Center → Protection → Conditional Access → [Policy] → Session
**What to capture:**
- Sign-in frequency settings (15 min for c1, 30 min for c2-c4, 1 hour for c5)
- Persistent browser session disabled
- Compliant device requirement

### Screenshot 5: PIM Role Activation for Agent Operations
**Portal Path:** Microsoft Entra Admin Center → Identity Governance → Privileged Identity Management → Roles
**What to capture:**
- PIM-eligible roles for agent administrative operations (Power Platform Admin, Environment Admin, Purview Admin)
- Activation requirements (approval workflow, justification required)
- Step-up authentication context applied upon activation

### Screenshot 6: Report-Only Mode Verification
**Portal Path:** Microsoft Entra Admin Center → Protection → Conditional Access → Policies
**What to capture:**
- Policies in Report-only mode during initial deployment
- Sign-in log showing report-only evaluation results
- Policy impact assessment before enforcement

---

## Notes for Verification
- Capture from pre-production environment when possible
- Ensure authentication context names and policy names are representative
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates
