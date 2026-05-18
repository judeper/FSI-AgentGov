# Troubleshooting: Control 1.23 — Step-Up Authentication for AI Agent Operations

**Last Updated:** April 2026

This playbook indexes the most common failures observed when deploying step-up authentication for AI agent operations and maps each to the diagnostic surface and resolution. Use it during pilot, after promoting policies from report-only to enforcement, and during incident response.

---

## Quick-Reference Issue Index

| # | Symptom                                                       | Likely cause                                                | Section |
|---|---------------------------------------------------------------|-------------------------------------------------------------|---------|
| 1 | Sensitive action proceeds with no step-up prompt              | Action not requesting the authentication context            | [§1](#1-sensitive-action-proceeds-without-step-up) |
| 2 | User cannot complete step-up                                  | No phishing-resistant method enrolled                       | [§2](#2-user-cannot-complete-step-up) |
| 3 | Excessive step-up prompts during normal work                  | Sign-in frequency too short for action profile              | [§3](#3-excessive-step-up-prompts) |
| 4 | Service principal performs sensitive op with no step-up       | SP not subject to interactive auth; no compensating control | [§4](#4-service-principal-bypass) |
| 5 | Conditional Access policy locks out tenant after promotion    | Break-glass exclusion missing or misconfigured              | [§5](#5-tenant-lockout-after-promotion) |
| 6 | Step-up succeeds but downstream service still rejects action  | Authentication context mapping incomplete on the resource   | [§6](#6-downstream-service-still-rejects) |
| 7 | PIM activation does not satisfy step-up                       | PIM role setting does not require the right context         | [§7](#7-pim-activation-does-not-satisfy-step-up) |
| 8 | Sign-in risk policy never fires                               | Identity Protection licensing or risk evaluation not active | [§8](#8-sign-in-risk-policy-never-fires) |
| 9 | Custom Authentication Strength rejected unexpectedly          | Method enrolled but not allowed by tenant authentication methods policy | [§9](#9-custom-authentication-strength-rejected) |

---

## 1. Sensitive action proceeds without step-up

**Diagnostics:**

- **Entra → Monitoring → Sign-in logs** for the user — open the relevant entry, **Authentication Details** tab. Check whether `Authentication context` is populated.
- **Conditional Access → Policies → `FSI-StepUp-c<N>-*` → Policy details** — confirm **State = On**, not Report-only.
- **Conditional Access → What If** — replay the user, app, and authentication context.

**Resolution:**

1. Confirm the downstream service (Microsoft Copilot Studio flow, custom connector, SharePoint site) is wired to request the context — see [Portal Walkthrough Step 6](portal-walkthrough.md#step-6-map-sensitive-agent-actions-to-authentication-contexts).
2. Confirm the policy is not in report-only mode.
3. Confirm the user is not in any exclusion group other than the documented break-glass group.
4. Confirm no other CA policy with a less restrictive grant (`Require MFA` only) is shadowing the step-up policy; CA evaluates all matching policies and the most restrictive grant wins, but a `Block` in another policy can short-circuit evaluation.

---

## 2. User cannot complete step-up

**Diagnostics:**

- Sign-in log entry with `ResultType = 53003` (Conditional Access blocked) and the **Authentication Strength** tab listing the unsatisfied methods.
- **Entra → Users → [user] → Authentication methods** — confirm enrolled methods.

**Resolution:**

1. Help the user enroll an allowed phishing-resistant method (FIDO2 security key, Windows Hello for Business, passkey in Microsoft Authenticator, certificate-based authentication). See [Microsoft Learn: passwordless options](https://learn.microsoft.com/entra/identity/authentication/concept-authentication-passwordless).
2. Confirm the tenant authentication methods policy permits the chosen method.
3. If the user is on an unmanaged personal device for a Zone 3 action, the device requirement (`Compliant or hybrid-joined`) will block them — direct them to a compliant device.

---

## 3. Excessive step-up prompts

**Diagnostics:**

- Count step-up prompts per user per day from sign-in logs.
- Review which contexts are being invoked most often and whether the action is correctly classified.

**Resolution:**

1. Re-classify low-risk actions out of `c1`/`c2` if they are firing during routine work.
2. Increase **Sign-in frequency** for `c5` (Sensitive Query) up to 4 hours when business justifies it; do not relax `c1`.
3. Confirm token caching at the client is not bypassed (e.g., InPrivate browsing forces re-authentication every session).

---

## 4. Service principal bypass

**Symptoms:** A service principal performs a sensitive operation (`c1`–`c4`) without any step-up evidence.

**Why it happens:** Service principals authenticate non-interactively. Conditional Access **for users** never applies to them.

**Resolution:**

1. Identify the SP and the operation.
2. Apply a **Conditional Access for workload identities** policy targeting the SP and requiring a managed location and / or a token-protection certificate. See [Microsoft Learn: workload identity CA](https://learn.microsoft.com/entra/identity/conditional-access/workload-identity).
3. For SP operations that touch the agent governance scope, route the operation through an approval workflow per [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md).
4. Replace long-lived client secrets with **federated credentials** or **managed identities** wherever possible.

---

## 5. Tenant lockout after promotion

**Symptoms:** After flipping a step-up policy from Report-only to On, large numbers of users (or all users) cannot complete sensitive actions.

**Resolution:**

1. **Use a break-glass account** to sign in. Do not attempt remediation with a regular admin account that may itself be locked.
2. Set the offending `FSI-StepUp-*` policy back to **Report-only** while you investigate.
3. Open **Sign-in logs → Conditional Access → Report-only results** for the prior 72 hours and confirm whether failures were present that should have blocked promotion.
4. Confirm the break-glass exclusion group is still attached to the policy and contains the break-glass accounts.
5. Re-bake for at least 72 hours before re-attempting promotion.

---

## 6. Downstream service still rejects

**Symptoms:** User completes step-up, sign-in log shows context satisfied, but the action still fails at the service.

**Diagnostics:**

- Inspect the downstream service's audit log (SharePoint, Purview, custom connector).
- Confirm the service's authentication context mapping was applied successfully.

**Resolution:**

1. SharePoint sites: re-apply the authentication context under **SharePoint admin center → Sites → [Site] → Authentication context**. The mapping can take up to 30 minutes to propagate.
2. Custom connectors: confirm the connector definition uses a Continuous Access Evaluation (CAE)-aware authentication library.
3. Power Automate flows: confirm the connector inside the flow honours the requested context.

---

## 7. PIM activation does not satisfy step-up

**Symptoms:** A user activates a PIM-eligible role and the activation succeeds, but the next administrative action triggers an unexpected step-up prompt.

**Resolution:**

1. Open **PIM → Microsoft Entra roles → Roles → [role] → Role settings** and confirm **On activation, require Conditional Access authentication context** is set to `c4` (Configuration Change).
2. Confirm the same context is targeted by an active `FSI-StepUp-c4-ConfigChange` policy.
3. Activation tokens are re-issued with the satisfied context — if the user is using a stale token (e.g., long-running PowerShell session), they must re-acquire a token after activation.

---

## 8. Sign-in risk policy never fires

**Diagnostics:**

- **Entra → Identity Protection → Risky sign-ins** — confirm the user appears with a non-zero risk level.
- Confirm the user has Entra ID P2 licensing.

**Resolution:**

1. Confirm Identity Protection is enabled and risk evaluation is active for the tenant.
2. Confirm `FSI-StepUp-SignInRisk-Medium` is in **On** state and includes the user.
3. Confirm no other CA policy is granting access at a higher precedence (e.g., a "trusted location" exception that suppresses risk evaluation).

---

## 9. Custom Authentication Strength rejected

**Symptoms:** A user enrolled in FIDO2 still receives an "authentication strength requirement not met" error when the custom `FSI-Critical-Operations` strength is required.

**Resolution:**

1. **Entra → Protection → Authentication methods → Policies** — confirm the FIDO2 method is enabled and the user is in the included scope.
2. Re-open the custom strength definition and confirm FIDO2 is selected with the correct AAGUID restrictions if any are configured.
3. If the strength requires certificate-based authentication, confirm the certificate authority is registered under **Entra → Protection → Authentication methods → Certificate-based authentication**.

---

## Escalation Path

1. **Entra Security Admin** — Conditional Access policy configuration and Authentication Strengths
2. **Authentication Administrator** — assist non-admin users with method enrollment
3. **Entra Privileged Role Admin** — PIM role setting changes
4. **Entra Global Admin** — break-glass operations and tenant authentication methods policy
5. **AI Administrator** / **Power Platform Admin** — downstream service mapping (Copilot Studio, Power Automate, custom connectors)
6. **Microsoft Support** — platform-side bugs (open ticket from the Entra admin center; reference the sign-in log Correlation ID)

---

## Known Limitations

| Limitation                                                            | Impact                                                                         | Workaround / Mitigation                                                  |
|-----------------------------------------------------------------------|--------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| Service principals are not subject to user Conditional Access         | SPs can perform sensitive ops without step-up                                  | Workload identity CA + approval workflow + managed identities            |
| Not every downstream service supports authentication contexts         | Some sensitive actions cannot be context-gated                                 | Use app-level controls and connector governance ([1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md)) |
| Continuous Access Evaluation (CAE) is library-dependent               | Some clients honour token revocation slower than expected                      | Pair short sign-in frequency with CAE-aware client libraries              |
| FIDO2 hardware dependency                                             | Some users do not have a security key                                          | Permit Windows Hello for Business and passkey in the strength definition  |
| Authentication context IDs are immutable                              | Cannot rename `c1`–`c25` once published                                        | Reserve ID space and document the catalog before publishing               |
| Identity Protection requires Entra ID P2                              | Sign-in risk and user risk policies do not function on lower SKUs              | License users in scope of Zone 3 with Entra ID P2                         |

---

[Back to Control 1.23](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
