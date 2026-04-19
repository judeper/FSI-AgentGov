# Verification & Testing: Control 1.23 — Step-Up Authentication for AI Agent Operations

**Last Updated:** April 2026

This playbook provides the test plan, evidence collection checklist, and attestation template needed to demonstrate Control 1.23 effectiveness to internal auditors and FINRA / SEC / NYDFS examiners.

---

## Test Environment Prerequisites

- [ ] At least one pilot user account in scope of the `FSI-StepUp-*` policies (not a break-glass account)
- [ ] Pilot user has at least one phishing-resistant method enrolled (FIDO2 key, Windows Hello, passkey, or certificate)
- [ ] A second pilot user enrolled **only** in SMS / voice MFA, used for negative tests
- [ ] All `FSI-StepUp-*` policies in **On** state (post-bake)
- [ ] Sentinel or Defender XDR analytics rules from [PowerShell Setup](powershell-setup.md) deployed

---

## Functional Test Cases

### TC-1.23-01 — Step-up triggers on a `c1` action after the freshness window

1. Pilot user signs in interactively at `T0`, completes phishing-resistant MFA.
2. Wait until `T0 + 16 minutes`.
3. Initiate a Copilot Studio agent action wired to context `c1` (e.g., test "Submit Trade").
4. **Expected:** Re-authentication prompt presented; the prompt shows the policy display name `FSI-StepUp-c1-FinancialTxn` in the diagnostic tooltip.
5. **Expected:** Action proceeds only after fresh phishing-resistant MFA.

### TC-1.23-02 — Step-up does not trigger inside the freshness window

1. Same pilot user; complete TC-1.23-01.
2. Within 5 minutes, repeat the `c1` action.
3. **Expected:** Action proceeds without an additional prompt.

### TC-1.23-03 — Phishing-resistant strength rejects SMS

1. Sign in as the SMS-only pilot user.
2. Attempt a `c1` action.
3. **Expected:** Sign-in denied with **AADSTS53003** (Conditional Access) and **AADSTS500121** (Authentication failed) classes; the `Authentication strength` tab in the sign-in details lists the unsatisfied requirement.

### TC-1.23-04 — FIDO2 / Windows Hello / passkey accepted

For each method type the organization supports, repeat TC-1.23-01 substituting the method during step-up. **Expected:** Action succeeds.

### TC-1.23-05 — Sign-in log captures the authentication context

1. After TC-1.23-01, open **Entra → Monitoring → Sign-in logs** and locate the pilot user's most recent interactive sign-in.
2. **Expected:** `Authentication Details` tab shows the requested context (`c1`) and the satisfying methods.
3. **Expected:** `Conditional Access` tab shows `FSI-StepUp-c1-FinancialTxn` with result *Success*.

### TC-1.23-06 — Sign-in risk policy forces step-up without context

1. Simulate a *Medium* sign-in risk for the pilot user (e.g., from an anonymous proxy in a non-production tenant).
2. **Expected:** `FSI-StepUp-SignInRisk-Medium` triggers and forces phishing-resistant re-authentication, even though no authentication context was invoked.

### TC-1.23-07 — PIM activation enforces step-up context

1. Pilot user with eligible Power Platform Admin assignment requests PIM activation.
2. **Expected:** Activation flow requires approval from the configured approver, justification text, MFA, and satisfies authentication context `c4`.
3. **Expected:** PIM audit log entry shows the context that gated the activation.

### TC-1.23-08 — Service principal compensating control fires

1. Attempt the sensitive SP operation in scope (e.g., publishing a connector to the allowlist) using a service principal that should be governed.
2. **Expected:** Operation blocked or routed to the approval workflow per [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md). The SP did not silently bypass step-up.

### TC-1.23-09 — Break-glass account bypass works

1. Sign in as a break-glass account (in a controlled, witnessed test).
2. **Expected:** No `FSI-StepUp-*` policy applies; the sign-in succeeds without step-up. Verify the **emergency access** alert defined per [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) fires.

### TC-1.23-10 — Step-up failure spike alert

1. Have the SMS-only pilot user attempt the `c1` action 6 times within 5 minutes.
2. **Expected:** Sentinel / Defender XDR `Step-up failure spike` analytics rule generates an incident within the documented SLA.

---

## Test Result Tracker

| Test ID     | Scenario                                             | Expected Result                              | Pass / Fail | Evidence Reference |
|-------------|------------------------------------------------------|----------------------------------------------|-------------|--------------------|
| TC-1.23-01  | Step-up after freshness window                       | Phishing-resistant MFA prompt                |             |                    |
| TC-1.23-02  | No prompt inside freshness window                    | Silent success                               |             |                    |
| TC-1.23-03  | SMS rejected for `c1`                                | Access denied (AADSTS53003)                  |             |                    |
| TC-1.23-04  | FIDO2 / WHfB / passkey accepted                      | Action succeeds                              |             |                    |
| TC-1.23-05  | Sign-in log captures context                         | Context and policy logged                    |             |                    |
| TC-1.23-06  | Sign-in risk forces step-up                          | Risk policy triggers                         |             |                    |
| TC-1.23-07  | PIM activation enforces context                      | Activation requires approval + MFA + context |             |                    |
| TC-1.23-08  | SP compensating control                              | Operation blocked or approval-routed         |             |                    |
| TC-1.23-09  | Break-glass bypass works                             | Sign-in succeeds; emergency alert fires      |             |                    |
| TC-1.23-10  | Step-up failure spike alert                          | Sentinel / Defender XDR incident created     |             |                    |

---

## Evidence Collection Checklist

- [ ] Screenshot: **Authentication contexts** list showing `c1`–`c5` with `Published = Yes`
- [ ] Screenshot: Each `FSI-StepUp-*` Conditional Access policy in **On** state
- [ ] Screenshot: Authentication Strength assignment on each step-up policy
- [ ] Screenshot: Sign-in frequency on each step-up policy with the documented value
- [ ] Screenshot: PIM role settings for Power Platform Admin, Environment Admin, AI Administrator, Purview Data Security AI Admin showing approval, justification, MFA, and bound authentication context
- [ ] Screenshot: Sign-in log entry for TC-1.23-01 with **Authentication Details** and **Conditional Access** tabs
- [ ] Export: `ca-policies-stepup.json`, `authentication-contexts.json`, `authentication-strengths.json`, `signins-with-authcontext.json`, and `manifest.json` (SHA-256) from [PowerShell Setup Script 4](powershell-setup.md#script-4-export-step-up-evidence-sha-256-hashed)
- [ ] Sentinel / Defender XDR incident export for TC-1.23-10 (step-up failure spike)
- [ ] Change advisory ticket reference for the report-only → enforcement promotion

---

## Attestation Statement Template

```markdown
## Control 1.23 Attestation — Step-Up Authentication for AI Agent Operations

**Organization:** [Organization Name]
**Control Owner:** [Name / Role — e.g., Entra Security Admin]
**Date:** [YYYY-MM-DD]
**Reporting Period:** [YYYY-MM-DD] to [YYYY-MM-DD]

I attest that during the reporting period:

1. The five FSI authentication contexts (`c1`–`c5`) were configured in Microsoft
   Entra Conditional Access and remained available to applications.
2. The five `FSI-StepUp-*` Conditional Access policies were enforced in **On**
   state and required the **Phishing-resistant MFA** Authentication Strength.
3. Sign-in frequency was set to 15 minutes for `c1`, 30 minutes for `c2`–`c4`,
   and 60 minutes for `c5` for users in scope of Zone 3.
4. Privileged Identity Management was configured for Power Platform Admin,
   Environment Admin, AI Administrator, Purview Data Security AI Admin, and
   Entra Security Admin with approval required, justification required, MFA on
   activation, and binding to authentication context `c4`.
5. Sign-in risk and user risk Conditional Access policies were enforced for
   users in scope.
6. Two break-glass accounts were excluded from all `FSI-StepUp-*` policies and
   from the sign-in risk and user risk policies; their use was monitored.
7. Service principal sensitive operations were governed via approval workflow
   or workload identity Conditional Access; no service principal was silently
   exempt from step-up controls.
8. Sign-in logs, Conditional Access policy snapshots, and PIM activation
   history were retained per the FINRA / SEC retention window applicable to
   the workloads in scope.

**Evidence package SHA-256:** [hash from manifest.json]

**Signature:** _______________________
**Date:** _______________________
```

---

[Back to Control 1.23](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
