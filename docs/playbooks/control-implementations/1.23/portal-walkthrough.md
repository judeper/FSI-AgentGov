# Portal Walkthrough: Control 1.23 - Step-Up Authentication for Agent Operations

**Last Updated:** January 2026
**Portal:** Microsoft Entra Admin Center
**Estimated Time:** 3-4 hours

## Prerequisites

- [ ] Entra Security Admin or Conditional Access Admin role
- [ ] Phishing-resistant MFA deployed (FIDO2, Windows Hello)
- [ ] Authentication contexts feature enabled

---

## Step-by-Step Configuration

### Step 1: Create Authentication Contexts

1. Open [Microsoft Entra Admin Center](https://entra.microsoft.com)
2. Navigate to **Protection** > **Conditional Access** > **Authentication context**
3. Create contexts:
   - `c1` - Financial Transaction (Critical)
   - `c2` - Data Export (High)
   - `c3` - External API Call (High)
   - `c4` - Configuration Change (High)
   - `c5` - Sensitive Query (Medium)

### Step 2: Configure Conditional Access Policies

1. Navigate to **Conditional Access** > **Policies**
2. Create policy for each context:

**Financial Transaction (c1):**
- Name: `FSI-StepUp-FinancialTransaction`
- Conditions: Authentication context = c1
- Grant: Require phishing-resistant MFA
- Session: Sign-in frequency = 15 minutes

**Data Export (c2):**
- Name: `FSI-StepUp-DataExport`
- Conditions: Authentication context = c2
- Grant: Require phishing-resistant MFA
- Session: Sign-in frequency = 30 minutes

### Step 3: Configure Authentication Strength

1. Navigate to **Protection** > **Authentication methods** > **Authentication strengths**
2. Create custom strength: `FSI-Critical-Operations`
3. Include only:
   - FIDO2 security key
   - Windows Hello for Business
   - Certificate-based authentication

### Step 4: Integrate with Agent Operations

1. Configure agent actions to require authentication context:
   - Financial transactions → c1
   - Data export → c2
   - External API calls → c3
2. Implement via Copilot Studio flows or connector configuration

### Step 5: Configure Monitoring

1. Enable sign-in log monitoring for step-up events
2. Create alert for step-up failures
3. Track step-up bypass attempts

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **Step-Up Required** | Not required | Data export, API | All sensitive actions |
| **Session Frequency** | 8 hours | 4 hours | 1 hour |
| **Fresh Auth** | Not required | 30 minutes | 15 minutes |
| **MFA Strength** | Standard MFA | Passwordless preferred | Phishing-resistant required |

---

## Validation

After completing these steps, verify:

- [ ] Authentication contexts created
- [ ] CA policies enforce step-up
- [ ] Phishing-resistant MFA required for critical operations
- [ ] Sign-in logs capture step-up events

---

[Back to Control 1.23](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
