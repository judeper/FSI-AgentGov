# Control 1.11 — Conditional Access and Phishing-Resistant MFA: Verification & Testing Playbook

**Control:** 1.11 — Conditional Access and Phishing-Resistant MFA
**Pillar:** 1 — Security
**Audience:** Entra Security Admin, Authentication Administrator, Entra Identity Governance Admin, Entra Agent ID Admin, AI Governance Lead, Compliance Officer, CISO delegate, Incident Response Lead, FSI Internal Audit
**Sovereign clouds:** Commercial, GCC, GCC High, DoD (per-cloud feature parity tracked in §5; 21Vianet treated as out-of-scope — see PRE-06)
**Cross-links:** 1.5 (DLP & sensitivity labels), 1.7 (Tenant restrictions / cross-tenant access), 1.12 (Insider Risk / Identity Protection), 1.14 (Data minimization & policy-aware DLP), 1.19 (eDiscovery & evidence preservation), 1.21 (Adversarial sign-in correlation), 2.5 (PIM lifecycle & access reviews), 2.8 (Service principal consent & permissions), 2.22 (Inactivity timeout enforcement), 2.26 (Entra Agent ID identity governance), 3.8 (Copilot Hub & governance dashboard), 4.6 (SharePoint sensitive site protection), AI Incident Response Playbook

> **Regulatory hedging notice.** This playbook describes verification procedures intended to **support compliance with** SEC Rule 17a-4(f) (audit-trail-alternative recordkeeping), FINRA Rule 4511 (books and records), FINRA Rule 3110 (supervision), FINRA Regulatory Notice 25-07 (AI supervision), SOX Section 404 (internal control over financial reporting — applied to identity boundary integrity), GLBA Section 501(b) (Safeguards Rule — access controls), the FFIEC IT Examination Handbook (Information Security and Authentication booklets), NIST SP 800-63B (Authenticator Assurance Level 3 — phishing-resistant authenticators), NYDFS 23 NYCRR 500.12 (multi-factor authentication), OCC Bulletin 2011-12 / Federal Reserve SR 11-7 (model risk management — applied to AI agent identities as model-bearing principals), and CFTC Regulation 1.31 (recordkeeping). Implementation **does not guarantee** legal compliance. Organizations should verify applicability with qualified counsel and re-confirm tenant-specific behaviour against current Microsoft Learn documentation at the cycle's `lastVerifiedUtc` date.

---

## What this playbook catches

This playbook proves that an FSI Microsoft 365 tenant operates a **fail-closed, evidence-pinned, examiner-defensible** Conditional Access (CA) and phishing-resistant MFA posture for Microsoft 365 Copilot makers, Copilot Studio agent authors, Power Platform makers, AI administrators, and **Entra Agent ID** principals (the framework's first first-class non-human AI identity). Specifically, it verifies:

1. **License & feature posture** — Entra ID P1/P2 covers in-scope users; **Workload Identities Premium** covers every service principal, managed identity, and Agent ID enrolled in a CA workload-identity policy; Microsoft Authenticator FedRAMP authorization is current in sovereign clouds; preview-state features (Agent ID, Token Protection on macOS, risk-based CA for workload identities) are reconciled to a per-cloud parity matrix rather than assumed-equivalent across clouds.
2. **CA policy integrity** — production CA policies match a CA-as-code source of truth with zero unexplained drift; exclusions appear in an approved register and are reviewed within the cycle's grace window; Report-only staging policies have not been silently promoted; named locations reconcile to the corporate egress IP register.
3. **Authentication Strength binding** — phishing-resistant Authentication Strengths (FIDO2 / Windows Hello for Business / device-bound passkeys / certificate-based authentication) are bound to every CA policy gating Zone 3 makers and high-privilege roles; SMS, voice, and OTP do not satisfy a Z3 grant; **synced (multi-device) passkeys are excluded from the AAL3 strength** because they break the device-binding assumption that makes a passkey phishing-resistant.
4. **Device compliance and Token Protection** — Z3 maker access requires `compliantDevice` AND a `signinFrequency` boundary AND `signInTokenProtection`; non-compliant devices are blocked or challenged per policy intent; mobile maker access is gated by an App Protection (MAM) policy; Token Protection is rolled out via the Microsoft-recommended report-only / pilot / enforce ladder rather than enforced cold.
5. **Continuous Access Evaluation (CAE)** — sign-in logs for Microsoft 365 Copilot and Copilot Studio resource calls show `Continuous access evaluation = True`; revocation latency for a disabled canary user is measured, recorded into the tenant baseline (PRE-07), and compared cycle-over-cycle rather than against an invented Microsoft SLA.
6. **PIM eligibility for AI administrative roles** — every role listed in the parent control's PIM table (`Entra Agent ID Admin`, `AI Administrator`, `Entra Security Admin`, `Authentication Administrator`, `Entra Identity Governance Admin`) is **PIM-eligible only** with no permanent active assignments; activation requires MFA via a CA Authentication Context (NOT session-token reuse), justification, ticket reference, and time-bound activation that does not exceed the parent control's per-role ceiling.
7. **Entra Agent ID lifecycle** — every in-scope agent is enrolled in Agent ID; each carries a non-null `sponsor` reviewed within the cycle window; the custom security attribute `AgentZone` is populated for every Z2/Z3 agent so scale-based CA policies can target them deterministically; the Microsoft Managed `Block high-risk agents` baseline is ON; a tenant-defined CA policy scoped to `AgentZone=3` is enforced.
8. **Service principal coverage** — service principals enrolled in a CA workload-identity policy actually carry the **Workload Identities Premium** SKU consumption; service principals are **never** present in user-targeted CA security groups (the parent control's `!!! warning` anti-pattern); SP sign-ins fire a Sentinel detection rule whose last-fired timestamp is within the review window.
9. **Break-glass posture** — at least two cloud-only (non-federated) emergency accounts exist; both are bound to **hardware FIDO2 keys held in a physical safe** with no SMS, voice, OTP, or Authenticator factors; both are excluded from every enabled CA policy AND **NOT** excluded from the phishing-resistant Authentication Strength requirement (the most commonly mis-implemented exception); a Sentinel analytic rule fires within the tenant baseline on any break-glass sign-in; the quarterly recoverability test record exists and is signed.
10. **Negative / deny-by-default controls** — the What-If tool, given a synthetic high-risk user, produces a deterministic block; an SP without Workload Identities Premium cannot be silently bound to a workload-identity CA policy (or the binding is detected as fail-open and surfaced as a finding); the canary CA policy disable triggers a Sentinel alert within the tenant baseline; expired or disabled production policies do not fail open against the residual baseline grant.
11. **Sovereign-cloud parity & incident readiness** — Commercial / GCC / GCC High / DoD parity for CA, Authentication Strengths, CAE, Token Protection, Agent ID, and Identity Protection (workload identities) is re-verified each cycle; gaps are recorded as compensating controls, not silent passes; an annual risky-sign-in tabletop and an account-compromise tabletop tied to FINRA 4530 and NYDFS 500.17(a) 72-hour notification timelines are exercised and signed.

> **What this playbook does NOT claim.** It does **not** assert any single numeric Microsoft SLA for CA propagation, CAE token-revocation latency, PIM activation latency, or Identity Protection risk-evaluation latency — Microsoft Learn explicitly states these are eventually-consistent and that latency varies by client, app, signal type, and cloud; the operative threshold for any cycle is the per-tenant baseline measured in PRE-07. It does **not** claim that Entra Agent ID itself "blocks" prompt-injection, jailbreak, or content-class abuse — those belong to Controls 1.13, 1.21, and 4.6; Agent ID's role here is to give the agent an enforceable identity boundary so CA, Identity Protection, and PIM can act on it. It does **not** treat the Microsoft Managed `Block high-risk agents` policy as a substitute for tenant-authored agent scoping; the managed policy is a baseline floor, not the ceiling. It does **not** assert that a passing cycle eliminates account-compromise risk; the cycle proves the **control surface** is intact and evidenced, not that no control has ever been bypassed by a sufficiently determined adversary. It does **not** apply to Microsoft 365 operated by 21Vianet (China), which has materially different CA, Identity Protection, and Agent ID feature availability and requires a separate validator (out of scope here).

---
## 1. Cadence Matrix (12 families × 3 zones)

Each verification family has a defined cadence per zone. **Grace windows:** weekly = 10 days, monthly = 35 days, quarterly = 100 days, semi-annual = 200 days, annual = 400 days from the previous successful cycle's `cycleCompletedUtc`. A cycle that exceeds its grace window without an `acceptedRiskUntilUtc` exception (signed by AI Governance Lead AND Compliance Officer) is reported as a finding to FSI Internal Audit and the assessment engine (`assessment/engine/score.py`) downgrades the control's confidence from `high` to `medium`.

| Family | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise / Regulated) | Owner (Run) | Reviewer (Sign-off) | Grace |
|---|---|---|---|---|---|---|
| **LIC** — License & feature posture | Quarterly | Monthly | Monthly | Entra Identity Admin | AI Governance Lead | 5 business days |
| **CA** — Conditional Access policy integrity | Quarterly | Monthly | **Weekly** | Entra Security Admin | Compliance Officer | 2 business days |
| **AUTHSTRENGTH** — Authentication Strength binding | Quarterly | Monthly | **Weekly** | Authentication Administrator | Entra Security Admin | 2 business days |
| **DEVICE** — Device compliance + Token Protection | Quarterly | Monthly | Monthly | Endpoint Admin (Intune) | Entra Security Admin | 5 business days |
| **CAE** — Continuous Access Evaluation | N/A | Quarterly | Monthly | Entra Security Admin | AI Governance Lead | 5 business days |
| **PIM** — Just-in-time for AI admin roles | Quarterly | Monthly | Monthly | Entra Identity Governance Admin | Compliance Officer | 5 business days |
| **AGENTID** — Entra Agent ID lifecycle | N/A (Z1 not in scope) | Monthly | **Weekly** | AI Governance Lead | Compliance Officer | 2 business days |
| **SP** — Service Principal CA coverage | Quarterly | Monthly | Monthly | Entra Security Admin | Power Platform Admin | 5 business days |
| **BREAKGLASS** — Emergency access | Quarterly | Quarterly | **Monthly** | Entra Global Admin | CISO delegate | 2 business days |
| **NEG** — Deny-by-default / negative controls | Quarterly | Quarterly | Quarterly | Entra Security Admin | Compliance Officer | 5 business days |
| **SOV** — Sovereign-cloud parity re-check | Annual | Semi-annual | Quarterly | Entra Identity Admin | Compliance Officer | 10 business days |
| **IR** — Risky-sign-in / compromise tabletop | Annual | Semi-annual | **Quarterly** | Incident Response Lead | CISO delegate + Compliance Officer | 10 business days |

> **Drift escalation rule.** If any test in the CA, AUTHSTRENGTH, AGENTID, BREAKGLASS, or NEG family fails twice in two consecutive cycles, the next cycle's cadence for that family **escalates one tier** (quarterly → monthly → weekly) and remains escalated until two consecutive clean cycles, after which it returns to the matrix default. Escalation events are recorded in `manifest.cadenceEscalations[]`.

> **Hedged framing requirement.** Owner and reviewer columns use canonical role names from `docs/reference/role-catalog.md`. Frequencies are operational defaults; tenants may run more often. They may **not** run less often without a signed `acceptedRiskUntilUtc` exception.

---

## 2. Pre-flight Gates (Fail-Closed)

PRE gates run **before** any test in §4. If any PRE gate returns FAIL, the validator (§7) exits with code **2**, no §4 test results are written to the evidence pack, and the cycle is halted and surfaced to the AI Governance Lead. Do not patch around a failed PRE gate by editing the validator.

### PRE-01 — Operator role separation and PIM activation

- **Objective.** Confirm the operator running the cycle did not hold `Entra Security Admin`, `Authentication Administrator`, `Entra Identity Governance Admin`, `Entra Agent ID Admin`, or `Entra Global Admin` as a permanent active assignment for the cycle, and that the three CA-relevant roles are held by **distinct identities** rather than concentrated in one super-admin.
- **How to verify.** Query Microsoft Graph `roleManagement/directory/roleAssignmentScheduleInstances` filtered by `principalId` of the operator and the role definitions for the five roles; assert `assignmentType eq 'Activated'` AND `endDateTime` ≤ the parent control's per-role activation ceiling. Separately, enumerate **all** active and eligible holders of the three CA-relevant roles (`Entra Security Admin`, `Authentication Administrator`, `Entra Identity Governance Admin`); assert that no single principal holds all three (active OR eligible).
- **Evidence.** `pre-01-pim-and-separation.json` containing the activation record IDs, role definition IDs, justification text, ticket references, and the 3-role intersection table.
- **Pass.** Every privileged role exercised in this cycle is backed by a time-bound PIM activation with a ticket reference; zero permanent active assignments on the five privileged roles; the 3-role intersection on `Entra Security Admin` × `Authentication Administrator` × `Entra Identity Governance Admin` is empty.
- **Audit assertion.** "No standing privileged identity-control access; all elevation is just-in-time and ticketed; CA-relevant administrative authority is split across at least three distinct principals (supports SOX 404 segregation of duties and FFIEC Authentication §III.A)."

### PRE-02 — License & SKU floor (incl. Workload Identities Premium)

- **Objective.** Confirm the tenant carries the SKUs required for the CA features, Authentication Strengths, Identity Protection, and **workload-identity CA** that the cycle exercises.
- **How to verify.** Use Graph `subscribedSkus` and `assignedPlans`. Required:
  1. **Entra ID P1** assigned to every in-scope user identity (Z2 floor) and **Entra ID P2** assigned to every Z3 maker, agent author, and PIM-eligible identity (P2 enables Identity Protection risk policies and PIM).
  2. **Workload Identities Premium (WIDP)** present at tenant scope with `ConsumedUnits ≥ count(SP/MI/Agent ID enrolled in any workload-identity CA policy)`.
  3. **Microsoft 365 E5** (or E3 + Defender for Identity standalone) for Identity Protection and Defender for Identity attestation.
- **Evidence.** `pre-02-licensing.json` with SKU IDs, service plan IDs, and per-identity assignment counts; cross-join showing every workload-identity CA policy target carries WIDP consumption.
- **Pass.** All three license families present AND every identity targeted by a workload-identity CA policy carries WIDP consumption; identities **not** carrying WIDP are absent from workload-identity CA policy targets (LIC-02 verifies this directly).
- **Audit assertion.** "Tenant carries the entitlements that Microsoft documents as required for the CA, Identity Protection, and workload-identity features exercised in §4 of this cycle; no policy is silently inert because of a missing SKU."

### PRE-03 — Break-glass attestation

- **Objective.** Confirm break-glass posture meets the framework's irreducible minimum **before** any §4 test executes (because BG-01..03 themselves rely on the BG accounts existing and being recoverable).
- **How to verify.** (a) Enumerate all members of the `Entra Global Admin` role; identify ≥ 2 cloud-only (non-federated, non-synced) emergency accounts whose UPN matches the tenant's documented BG naming convention; (b) for each, inspect `authentication/methods` and confirm the only registered method is a **hardware FIDO2 key** (vendor + AAGUID recorded against the firm's approved-key register); (c) for each, run the CA What-If tool against every enabled CA policy and record the outcome; (d) confirm a Sentinel analytic rule scoped to the BG account UPNs exists and is enabled with severity High; (e) confirm a quarterly recoverability test record exists for the prior quarter.
- **Evidence.** `pre-03-breakglass.json` containing roster, method audit, per-policy What-If JSON, Sentinel rule export, and the prior quarter's signed recoverability test record.
- **Pass.** Count ≥ 2 cloud-only AND hardware-FIDO2-only AND What-If returns "Not applied" for every enabled CA policy AND Sentinel rule enabled AND prior-quarter recoverability test signed.
- **Audit assertion.** "Break-glass posture is verifiable independently of the CA control plane; recovery does not require the same control plane the cycle is testing."

### PRE-04 — Microsoft Authenticator FedRAMP attestation (sovereign clouds)

- **Objective.** In sovereign clouds, confirm Microsoft Authenticator carries the cloud-appropriate FedRAMP authorization and that non-FedRAMP authentication factors are blocked at the tenant Authentication Methods Policy.
- **How to verify.** If `cloud ∈ {GCC, GCC-High, DoD}`: capture the Microsoft FedRAMP attestation reference for Microsoft Authenticator at `lastVerifiedUtc` (URL + retrieval timestamp + responsible-party text); inspect the tenant Authentication Methods Policy and confirm that any factor without a current FedRAMP authorization in the cloud is `state: disabled`; in Commercial cloud the gate returns `n/a` rather than PASS.
- **Evidence.** `pre-04-fedramp.json` with cloud classification, attestation reference, retrieval timestamp, and Authentication Methods Policy export.
- **Pass.** (Sovereign) Attestation current AND non-FedRAMP factors disabled. (Commercial) Marked `n/a` with cloud declared.
- **Audit assertion.** "Authentication factors permitted in this sovereign cloud carry the FedRAMP authorization Microsoft asserts at `lastVerifiedUtc` (supports FedRAMP High continuous monitoring obligations and DoD CC SRG IL5 where applicable)."

### PRE-05 — Canary CA policy + canary user

- **Objective.** Confirm a dedicated canary CA policy in `enabledForReportingButNotEnforced` state, scoped to a synthetic canary user, exists and is monitored — so silent CA-control-plane disable events are detected within the tenant baseline rather than at the next quarterly review.
- **How to verify.** Locate the canary CA policy by its documented `displayName` (e.g., `FSI-CANARY-DO-NOT-DISABLE`); confirm `state == 'enabledForReportingButNotEnforced'`, `users.includeUsers` is the synthetic canary UPN only, and `applications.includeApplications == 'All'`. Confirm a Sentinel analytic rule fires on `Update conditional access policy` events targeting this policy ID with severity High. Confirm the canary user UPN matches the regex `^fsi-canary-[a-z0-9]{4,}@…$` AND does NOT appear in HR's authoritative employee directory.
- **Evidence.** `pre-05-canary.json` with the canary policy export, the Sentinel rule export, and the HR-directory cross-check result.
- **Pass.** Canary policy present with correct state AND Sentinel rule enabled AND canary UPN is synthetic.
- **Audit assertion.** "A canary CA policy and synthetic canary user provide near-real-time detection of unauthorized CA-control-plane changes; no real PII is exercised in the cycle."

### PRE-06 — Cloud-environment guard and module-version pinning

- **Objective.** Refuse to run if the operator targets an unsupported cloud (21Vianet) or if module versions cannot be pinned and hashed.
- **How to verify.** (a) Query `Get-MgEnvironment` and the connection's authority URL; classify the cloud; HALT if the endpoint resolves to `partner.microsoftonline.cn` or if classification is ambiguous; (b) for each required module (`Microsoft.Graph` ≥ pinned minimum, `Microsoft.Graph.Identity.SignIns`, `Microsoft.Graph.Identity.Governance`, `Microsoft.Graph.Beta.Identity.SignIns` for Agent ID preview surfaces, `MSCommerce` for SKU enumeration), run `Get-Module -ListAvailable`, capture `Name`, `Version`, `Path`, and SHA-256 of the resolved `.psd1`.
- **Evidence.** `pre-06-environment.json` with classified cloud, endpoint URI, tenant region, and module manifest with hashes.
- **Pass.** Cloud is one of {Commercial, GCC, GCC High, DoD} AND matches the cloud declared in the cycle's `manifest.tenant.cloud` AND all required modules ≥ pinned minimum AND module signatures trusted (`Get-AuthenticodeSignature` Status = Valid for the primary `.psm1`).
- **Audit assertion.** "Cycle executed against the declared sovereign cloud with version-pinned operator tooling; no cross-cloud contamination; cmdlet behaviour matches the playbook's documented expectations at this revision."

### PRE-07 — Tenant baseline (CA propagation, CAE revocation, PIM activation, IDP risk lag)

- **Objective.** Establish a per-tenant, per-cycle baseline for the four eventually-consistent latency properties this control depends on, **rather than** asserting a Microsoft SLA for any of them.
- **How to verify.** Generate four synthetic measurements with a unique cycle marker (`fsi-cycle-{cycleId}`):
  1. **CA propagation.** Modify a no-op attribute on the canary CA policy at T0; poll the Graph `policies/conditionalAccessPolicies/{id}` and Sentinel ingestion until the change appears in a fresh canary sign-in's `appliedConditionalAccessPolicies`. Record T0 → T_observed for the canary user.
  2. **CAE revocation.** Disable the canary user at T0; from a CAE-aware client (Outlook desktop or Teams desktop) signed in as the canary, repeatedly request resource access; record T0 → T_denied.
  3. **PIM activation.** From a PIM-eligible operator, request activation of `Entra Security Admin` at T0; record T0 → T_token_includes_role.
  4. **Identity Protection risk evaluation.** Trigger a documented risky sign-in from a synthetic test identity (e.g., Tor exit-node sign-in attempt against a non-canary disabled test user); poll Identity Protection report for the corresponding risk detection until it appears.
- **Evidence.** `pre-07-baseline.json` with the four measurement series and computed P50/P95 per series.
- **Pass.** All four measurements complete within the cycle's measurement budget (default 4 hours each); P95 ≤ tenant's prior 4-cycle rolling P95 + 50% drift allowance.
- **Audit assertion.** "Tenant CA propagation, CAE revocation, PIM activation, and Identity Protection risk-evaluation latencies are within rolling baseline; cycle's freshness threshold for CA, CAE, PIM, and risk-related tests is the measured P95, not an asserted Microsoft SLA."

> **PRE-07 supersedes any numeric SLA stated elsewhere in this playbook.** Tests that reference a window must reference the baseline value from PRE-07, not an absolute number.

---

## 3. Documented Processing Windows (Microsoft Learn–cited only)

The table below captures **only** Microsoft-documented behaviours. Where Microsoft Learn does not publish a numeric SLA, the column reads "no documented numeric SLA — use tenant baseline from PRE-07". **Do not invent SLAs.**

| Mechanism | Documented behaviour (Microsoft Learn, qualitative) | Operative threshold for this cycle |
|---|---|---|
| Conditional Access policy propagation | Typically takes effect on the next sign-in attempt; can be delayed under load and during global service events | No documented numeric SLA — use tenant baseline `pre-07-baseline.caPropagationP95` |
| Continuous Access Evaluation token revocation | Described as near real-time for CAE-aware clients; Microsoft documents that propagation of an event such as user disable to an enforcing resource can take several minutes; IP-location enforcement is described as immediate | No documented numeric SLA — use tenant baseline `pre-07-baseline.caeRevocationP95` |
| Authentication Strength evaluation | Evaluated at sign-in once the policy applies; existing tokens are not revoked retroactively unless `signinFrequency` or CAE forces a fresh sign-in | Authentication Strength applies only to **new** sign-ins; verify by triggering a fresh sign-in, not by reading an existing token |
| PIM activation | Effective after MFA / approval / justification completes; the new role assignment must propagate into a fresh token before exercise | No documented numeric SLA — use tenant baseline `pre-07-baseline.pimActivationP95` |
| Identity Protection risk evaluation | Combines real-time signals at sign-in with offline batch detections that surface later; some risk types (e.g., leaked credentials) only surface offline | No documented numeric SLA — use tenant baseline `pre-07-baseline.idpRiskP95`; offline risk types must be re-checked after a documented offline-batch window |
| Token Protection rollout | Microsoft recommends pilot group → report-only analysis → enforcement; no documented numeric SLA for global rollout | Verify the rollout ladder is followed, not a calendar date |
| Entra Agent ID (Preview) availability | Documented as Preview in Commercial cloud; sovereign-cloud availability is "Confirm at `lastVerifiedUtc`" | SOV-01 verifies availability per cloud each cycle; gaps are scoped, not ignored |
| Microsoft Managed `Block high-risk agents` policy | Microsoft documents this as a baseline managed policy applicable to Agent ID where available | AID-04 verifies enabled state; the managed policy is a floor, not a ceiling |

> **Citation discipline.** Every row above is testable against a Microsoft Learn page reachable at the cycle's `lastVerifiedUtc`. Any behaviour not on this table that affects cycle outcome must be added in the cycle's `manifest.deviations[]` with a Learn URL and a verification timestamp; an undocumented behaviour without a deviation entry is a finding.

---
## 4. Test Catalog (32 tests across 12 namespaces)

Test ID format: `1.11-{NAMESPACE}-NN`. Each test uses a 7-field structure: **Objective / Preconditions / Steps / Expected / Pass criteria / Audit assertion / Evidence**. The validator (§7) emits one record per test against the JSON Schema in §6.

> Symbols: ⛔ = blocking failure (cycle FAIL); ⚠ = non-blocking finding (cycle PASS WITH NOTE if no other failure); ✅ = informational green path.

### 4.1 Namespace `LIC` — License & feature posture (3 tests)

#### 1.11-LIC-01 — Workload Identities Premium covers every workload-identity CA target ⛔

- **Objective.** Prove every service principal, managed identity, and Agent ID enrolled in any workload-identity CA policy carries WIDP consumption — closing the silent fail-open path where a CA policy targets an identity the SKU does not cover.
- **Preconditions.** PRE-02 PASS; the cycle's CA-as-code repo enumerates which CA policies are workload-identity policies (`conditions.clientApplications.servicePrincipals` populated).
- **Steps.** (1) Enumerate workload-identity CA policies via `Get-MgIdentityConditionalAccessPolicy` filtered to those with `conditions.clientApplications.servicePrincipals.includeServicePrincipals` non-empty or referencing a service-principal group. (2) Resolve each target SP/MI/Agent ID's `appId`. (3) Cross-join against `MSCommerce` WIDP consumption records. (4) Compute the set difference: `targets \ widpConsumers`.
- **Expected.** The set difference is empty.
- **Pass.** `count(targets \ widpConsumers) == 0`.
- **Audit assertion.** "Every non-human identity bound to a workload-identity CA policy carries the SKU Microsoft documents as required for that policy to evaluate; no policy is silently inert (supports SOX 404 control-design integrity)."
- **Evidence.** `tests/lic-01-widp-coverage.json` containing the policy list, target list, consumer list, and the (empty) difference set.

#### 1.11-LIC-02 — Entra ID P1/P2 covers in-scope users by zone ⛔

- **Objective.** Confirm Z2 users carry P1 and Z3 users carry P2 (P2 enables Identity Protection sign-in / user risk policies and PIM).
- **Preconditions.** PRE-02 PASS; HR's authoritative directory tags each user with `extensionAttribute1 ∈ {Z1,Z2,Z3}` per the parent control's zone tag convention.
- **Steps.** Enumerate user SKU assignments; cross-join against zone tag; flag any Z2 user without P1 OR P2 service-plan and any Z3 user without P2 service-plan.
- **Expected.** Zero Z2 users without P1/P2; zero Z3 users without P2.
- **Pass.** Both counts == 0.
- **Audit assertion.** "License floor matches zone classification; PIM and Identity Protection are licensable for the populations they target."
- **Evidence.** `tests/lic-02-userlicense.json`.

#### 1.11-LIC-03 — Microsoft Authenticator FedRAMP attestation current (sovereign only) ⚠

- **Objective.** In sovereign clouds, the Microsoft FedRAMP attestation reference for Authenticator is current relative to the cycle's `lastVerifiedUtc`; in Commercial, the test is `n/a`.
- **Preconditions.** PRE-04 PASS or `n/a`.
- **Steps.** Re-fetch the FedRAMP attestation reference recorded in PRE-04; compute age in days vs. `lastVerifiedUtc`.
- **Expected.** Attestation age ≤ 90 days OR re-confirmed by the responsible party in the cycle window.
- **Pass.** Sovereign + age ≤ 90d, OR Commercial (`n/a`).
- **Audit assertion.** "FedRAMP authorization for the authenticator app is current at cycle close (supports FedRAMP continuous-monitoring obligations)."
- **Evidence.** `tests/lic-03-fedramp.json`.

### 4.2 Namespace `CA` — Conditional Access policy integrity (4 tests)

#### 1.11-CA-01 — Phishing-resistant Authentication Strength bound to every Z3-maker CA grant ⛔

- **Objective.** Verify every CA policy gating a Zone 3 maker, Copilot Studio agent author, AI Administrator, or PIM-eligible role binds the **phishing-resistant MFA** Authentication Strength (or a tenant-defined Auth Strength that is a subset of phishing-resistant).
- **Preconditions.** Z3 maker group resolvable via Graph; AuthStrength catalog enumerable.
- **Steps.** For each enabled CA policy whose `users.includeUsers/Groups/Roles` intersects the Z3 maker set OR any role in `[AI Administrator, Entra Agent ID Admin, Authentication Administrator, Entra Security Admin, Entra Identity Governance Admin]`: read `grantControls.authenticationStrength.id`; resolve the strength definition; assert `allowedCombinations` ⊆ phishing-resistant combinations (FIDO2, WHfB, deviceBoundPasskey, x509CertificateMultiFactor).
- **Expected.** Every such policy resolves to a phishing-resistant strength.
- **Pass.** `count(z3PoliciesWithoutPhishResistant) == 0` AND `count(z3PoliciesWithSmsOrVoiceOrOtp) == 0`.
- **Audit assertion.** "Phishing-resistant MFA per NIST SP 800-63B AAL3 is bound to every Z3 maker access path (supports FFIEC Authentication §III.B and NYDFS 500.12 phishing-resistant guidance)."
- **Evidence.** `tests/ca-01-authstrength-binding.json`.

#### 1.11-CA-02 — Drift vs. CA-as-code source of truth ⛔

- **Objective.** Production CA matches the signed CA-as-code repo HEAD; no out-of-band edits.
- **Preconditions.** CA-as-code repo with signed commits and the prior cycle's HEAD SHA recorded in `manifest.caAsCodeBaselineSha`.
- **Steps.** Export every enabled CA policy via Graph; render to the canonical CA-as-code JSON shape; diff against the repo's exported set; flag adds, deletes, attribute changes.
- **Expected.** Zero unexplained drift; any drift entry has a corresponding signed pull request merged into the repo within the cycle window.
- **Pass.** `count(driftEntriesWithoutPR) == 0`.
- **Audit assertion.** "CA control plane changes only via reviewed, signed change-control (supports SOX 404 ITGC change-management)."
- **Evidence.** `tests/ca-02-drift.json`.

#### 1.11-CA-03 — Exclusions appear in approved register and are within freshness window ⚠

- **Objective.** Every user, group, role, application, and IP excluded from a CA policy appears in the firm's approved exclusion register with a stated business justification, owner, expiry, and last-review date inside the cycle's grace window.
- **Preconditions.** Approved exclusion register exists at a known repo path.
- **Steps.** Enumerate all `*.excludeUsers/Groups/Roles/Applications/Locations` across enabled policies; cross-join the register; flag exclusions absent from the register OR with `lastReviewUtc` older than (cycle start − cadence grace).
- **Expected.** Every exclusion is registered and reviewed.
- **Pass.** `count(unregisteredExclusions) == 0` AND `count(staleExclusions) == 0`.
- **Audit assertion.** "Every CA exception is named, owned, justified, time-bound, and recently reviewed (supports FFIEC IS Booklet exception management)."
- **Evidence.** `tests/ca-03-exclusions.json`.

#### 1.11-CA-04 — Report-only ring not silently promoted; named-locations fresh ⚠

- **Objective.** A report-only policy older than the documented pilot window has either been promoted with a signed approval or retired; named-locations IP ranges match the corporate-egress IP register.
- **Preconditions.** Pilot ladder window documented (e.g., 30 days report-only).
- **Steps.** (a) For each `state == 'enabledForReportingButNotEnforced'` policy: compare `modifiedDateTime` against pilot window; flag stale report-only policies absent a signed extension. (b) Enumerate `namedLocations`; diff IP ranges against the corporate-egress IP register; flag mismatches.
- **Expected.** No stale report-only without extension; no IP-range drift.
- **Pass.** Both counts == 0.
- **Audit assertion.** "Pilot-state policies are time-bound and reviewed; named-locations reflect the firm's actual egress posture."
- **Evidence.** `tests/ca-04-reportonly-namedlocations.json`.

### 4.3 Namespace `AUTHSTRENGTH` — Authentication Strength catalog (3 tests)

#### 1.11-AUTHSTRENGTH-01 — Synced (multi-device) passkeys excluded from AAL3 strength ⛔ (negative test)

- **Objective.** The phishing-resistant Authentication Strength used for AAL3 grants does **not** permit synced passkeys (which break the device-binding assumption that makes a passkey AAL3-grade).
- **Preconditions.** Tenant-defined or built-in Authentication Strength used for AAL3 grants is identifiable in the schema.
- **Steps.** Resolve the AAL3 strength definition; enumerate `allowedCombinations`; assert that no combination resolves to a synced-passkey AAGUID; assert `deviceBoundPasskey` is the operative passkey combination if passkeys are permitted at all.
- **Expected.** Synced-passkey AAGUIDs absent from AAL3 strength.
- **Pass.** `count(syncedPasskeyAAGUIDsInAAL3) == 0`.
- **Audit assertion.** "AAL3 grants permit only device-bound authenticators; synced/multi-device passkeys are not silently treated as phishing-resistant (supports NIST SP 800-63B AAL3 device-binding requirement)."
- **Evidence.** `tests/authstrength-01-synced-passkey-excluded.json`.

#### 1.11-AUTHSTRENGTH-02 — FIDO2-only enforcement on Z3 makers ⛔

- **Objective.** Z3 makers can complete a sign-in **only** with FIDO2/WHfB/CBA — not with Authenticator number-match, OTP, SMS, or voice.
- **Preconditions.** AUTHSTRENGTH-01 PASS; canary Z3 user available.
- **Steps.** Triggered via the operator workstation: simulate a sign-in for the canary Z3 user using each non-FIDO2 method registered for the canary; capture sign-in log `authenticationDetails` and `appliedConditionalAccessPolicies`; assert non-FIDO2 attempts are denied with the AAL3 CA policy as the deny reason.
- **Expected.** Non-FIDO2 methods denied; FIDO2 / WHfB / CBA succeed.
- **Pass.** Zero non-FIDO2 success records for the canary Z3 user.
- **Audit assertion.** "Z3 maker sign-ins cannot fall back to weaker factors; phishing-resistant MFA is operationally enforced, not merely policy-configured."
- **Evidence.** `tests/authstrength-02-fido2-only.json`.

#### 1.11-AUTHSTRENGTH-03 — Certificate-based authentication (CBA) chain validity for x509 grants ⚠

- **Objective.** Where x509 CBA is permitted in the AAL3 strength, the trusted CA chain configured at the tenant matches the firm's PKI's current intermediate set; revoked or expired intermediates are not trusted.
- **Preconditions.** Tenant CBA configuration exported.
- **Steps.** Export the tenant CBA configuration; cross-check each trusted CA against the firm's current PKI roster; flag mismatches and expired/revoked entries.
- **Expected.** Tenant CBA trust set ≡ firm PKI roster intersected with non-expired non-revoked intermediates.
- **Pass.** `count(trustedCaMismatches) == 0`.
- **Audit assertion.** "x509 trust at the identity edge matches firm PKI; no orphaned-trust path."
- **Evidence.** `tests/authstrength-03-cba-chain.json`.

### 4.4 Namespace `DEVICE` — Device compliance + Token Protection (3 tests)

#### 1.11-DEVICE-01 — Z3 access requires compliantDevice + Token Protection + signinFrequency ⛔

- **Objective.** Every CA policy gating Z3 maker resource access carries `grantControls.builtInControls` containing `compliantDevice` AND `sessionControls.signInFrequency` set AND `sessionControls.signInTokenProtection.isEnabled == true`.
- **Preconditions.** CA-01 PASS.
- **Steps.** Enumerate Z3 grant policies; for each, assert the three session/grant controls above are present and enabled.
- **Expected.** All three present on every Z3 grant.
- **Pass.** Zero Z3 policies missing any of the three.
- **Audit assertion.** "Z3 access requires a managed device, a periodic re-authentication, and Token Protection — closing token-replay paths from non-compliant endpoints."
- **Evidence.** `tests/device-01-compliantdevice-tokenprot-sif.json`.

#### 1.11-DEVICE-02 — Hybrid-join / Entra-join enforcement on Z3 endpoints ⚠

- **Objective.** Devices used by Z3 makers are Entra-joined or Hybrid-joined; workgroup or Azure-AD-registered-only endpoints cannot satisfy `compliantDevice`.
- **Preconditions.** Intune device inventory accessible.
- **Steps.** Cross-join Z3 user roster against Intune `managedDevices`; flag Z3 users whose primary device is `azureAdRegistered` only or absent.
- **Expected.** Every Z3 user has at least one `azureAdJoined` or `hybridAzureAdJoined` compliant device.
- **Pass.** Count of non-compliant Z3 users == 0.
- **Audit assertion.** "Z3 makers operate on devices that fall under tenant-managed posture; BYOD that is merely registered is not silently treated as managed."
- **Evidence.** `tests/device-02-join-state.json`.

#### 1.11-DEVICE-03 — Mobile maker access gated by App Protection (MAM) policy ⚠

- **Objective.** When Z2/Z3 makers use mobile clients, an Intune App Protection policy is enforced on the Microsoft 365 / Copilot mobile app.
- **Preconditions.** Intune App Protection policies enumerable.
- **Steps.** Enumerate App Protection policies; assert at least one policy is assigned to the maker group AND scoped to the Microsoft 365 Copilot mobile app bundle IDs.
- **Expected.** Policy present and assigned.
- **Pass.** Policy present and assigned.
- **Audit assertion.** "Mobile maker access enforces a MAM boundary; corporate data on personal mobile is policy-bound."
- **Evidence.** `tests/device-03-mam.json`.

### 4.5 Namespace `CAE` — Continuous Access Evaluation (2 tests)

#### 1.11-CAE-01 — Microsoft 365 Copilot and Copilot Studio sign-ins show CAE = True ⛔

- **Objective.** Sign-in logs for Microsoft 365 Copilot resource calls (`Microsoft.AzureAdvancedThreatProtection`-adjacent app IDs and the documented Copilot resource app IDs) show `Continuous access evaluation = True` on the resource leg of the call chain.
- **Preconditions.** Sign-in log retention covers the cycle window.
- **Steps.** Query sign-in logs for the cycle window filtered to Copilot / Copilot Studio resource app IDs; aggregate by client app and CAE flag.
- **Expected.** Every interactive Copilot resource sign-in chain shows CAE evaluation in scope.
- **Pass.** Zero Copilot resource sign-in records show `Continuous access evaluation = False` for a CAE-aware client.
- **Audit assertion.** "Copilot resource access participates in CAE; revocation events propagate via the CAE channel rather than waiting for token expiry."
- **Evidence.** `tests/cae-01-copilot-cae-true.json`.

#### 1.11-CAE-02 — CAE revocation latency within tenant baseline ⚠

- **Objective.** PRE-07's CAE revocation P95 is within the rolling 4-cycle baseline.
- **Preconditions.** PRE-07 PASS.
- **Steps.** Read `pre-07-baseline.caeRevocationP95`; compare to the rolling 4-cycle P95 stored in `manifest.rollingBaselines.caeRevocationP95`; flag if current > rolling × 1.5.
- **Expected.** Within 1.5× rolling P95.
- **Pass.** Within threshold.
- **Audit assertion.** "Tenant-measured CAE revocation latency is within rolling baseline; no Microsoft SLA is asserted (supports defensible operational metric reporting)."
- **Evidence.** `tests/cae-02-revocation-baseline.json`.

### 4.6 Namespace `PIM` — Just-in-time for AI admin roles (3 tests)

#### 1.11-PIM-01 — MFA on activation via CA Authentication Context (NOT session-token reuse) ⛔

- **Objective.** PIM activation for the five privileged roles requires fresh phishing-resistant MFA bound through a CA Authentication Context, not satisfaction by a previously-issued token in the operator's current session.
- **Preconditions.** PIM role settings exportable; CA Authentication Context references resolvable.
- **Steps.** For each role in `[Entra Agent ID Admin, AI Administrator, Authentication Administrator, Entra Security Admin, Entra Identity Governance Admin]`: read `roleManagementPolicy` activation rules; assert `Enablement_EndUser_Assignment` requires `MultiFactorAuthentication` AND a CA Authentication Context reference; assert the referenced Authentication Context is bound to a CA policy whose grant is the AAL3 phishing-resistant Authentication Strength; assert no rule sets `claimValue` mode that would accept a pre-existing MFA claim older than the CA policy's `signInFrequency` value.
- **Expected.** All five roles require fresh MFA-via-CA-Auth-Context bound to AAL3.
- **Pass.** Zero roles fail any sub-assertion.
- **Audit assertion.** "PIM activation cannot be satisfied by token reuse; every elevation re-presents a phishing-resistant factor (supports SOX 404 and FFIEC Authentication §III)."
- **Evidence.** `tests/pim-01-mfa-on-activation.json`.

#### 1.11-PIM-02 — Eligibility-only (zero permanent active assignments on the five roles) ⛔

- **Objective.** No principal holds any of the five privileged roles as a permanent `Active` assignment outside the break-glass exception.
- **Preconditions.** Break-glass roster from PRE-03.
- **Steps.** Enumerate `roleManagement/directory/roleAssignmentScheduleInstances` filtered to the five role definitions and `assignmentType eq 'Assigned'` (permanent); subtract the BG roster.
- **Expected.** Empty set.
- **Pass.** `count(permanentNonBgAssignments) == 0`.
- **Audit assertion.** "Standing privilege on identity-control roles is limited to documented break-glass; all routine elevation is just-in-time."
- **Evidence.** `tests/pim-02-eligibility-only.json`.

#### 1.11-PIM-03 — Activation duration ≤ per-role ceiling, justification + ticket required ⚠

- **Objective.** Activation duration ceilings, mandatory justification, and mandatory ticket reference per the parent control's PIM table.
- **Preconditions.** Parent control PIM table version pinned in `manifest.parentControlVersion`.
- **Steps.** Read `roleManagementPolicy` for each role; assert `Expiration_EndUser_Assignment.maximumDuration` ≤ ceiling; assert `Enablement_EndUser_Assignment.enabledRules` contains `Justification` AND `Ticketing`.
- **Expected.** All sub-assertions pass.
- **Pass.** Zero rule violations.
- **Audit assertion.** "Activation duration, justification, and ticket reference are policy-enforced (supports change-management and audit-trail evidence)."
- **Evidence.** `tests/pim-03-duration-justification-ticket.json`.

### 4.7 Namespace `AGENTID` — Entra Agent ID lifecycle (4 tests)

#### 1.11-AGENTID-01 — Every in-scope agent enrolled in Agent ID with `sponsor` populated ⛔

- **Objective.** Every Z2/Z3 Copilot Studio agent in scope is enrolled as an Entra Agent ID with a non-null `sponsor` attribute referencing a current employee.
- **Preconditions.** Z2/Z3 Copilot Studio agent inventory enumerable from Power Platform admin; Agent ID list enumerable via Graph beta (Preview).
- **Steps.** Cross-join the agent inventory against the Agent ID roster; flag agents present in Power Platform inventory but missing from Agent ID OR present in Agent ID but with null/orphan `sponsor`.
- **Expected.** Empty difference set; sponsor populated and resolvable to an active employee.
- **Pass.** `count(unenrolledAgents) == 0` AND `count(orphanSponsorAgents) == 0`.
- **Audit assertion.** "Every in-scope agent has an enforceable identity boundary and a named human sponsor (supports OCC 2011-12 / SR 11-7 model identity accountability and FINRA 3110 supervision applied to AI agents)."
- **Evidence.** `tests/agentid-01-enrollment-sponsor.json`.

#### 1.11-AGENTID-02 — Sponsor review within cycle window ⚠

- **Objective.** Each enrolled agent's sponsor signed a review attestation within the cycle's grace window.
- **Preconditions.** Sponsor-review record store accessible (Lifecycle Workflows or Access Reviews export).
- **Steps.** Enumerate sponsor-review records by agent ID; flag agents whose most recent signed review is older than (cycle start − cadence grace).
- **Expected.** Every agent has a fresh sponsor review.
- **Pass.** `count(staleSponsorReviews) == 0`.
- **Audit assertion.** "Agent sponsorship is actively maintained; orphan agents are surfaced for retirement (supports identity governance lifecycle)."
- **Evidence.** `tests/agentid-02-sponsor-review.json`.

#### 1.11-AGENTID-03 — Custom security attribute `AgentZone` populated for every Z2/Z3 agent ⛔

- **Objective.** The custom security attribute `AgentZone ∈ {2,3}` is populated for every Z2/Z3 agent so scale-based CA policies can target them deterministically.
- **Preconditions.** Custom security attribute set `Agent` with attribute `AgentZone` defined at tenant scope (one-time setup; deletion is irreversible per Microsoft Learn).
- **Steps.** Enumerate Agent ID principals; read the `customSecurityAttributes.Agent.AgentZone` attribute; assert non-null AND value matches the agent's classified zone.
- **Expected.** Every agent's attribute matches its classification.
- **Pass.** `count(agentZoneMissingOrMismatched) == 0`.
- **Audit assertion.** "Agent zone classification is encoded in a tamper-evident, deletion-irreversible custom security attribute consumable by CA filters; agent-targeted CA policies are deterministic, not name-pattern guesses."
- **Evidence.** `tests/agentid-03-agentzone.json`.

#### 1.11-AGENTID-04 — Microsoft Managed `Block high-risk agents` baseline enabled + tenant Z3-agent CA policy enforced ⛔

- **Objective.** Both the Microsoft Managed baseline AND a tenant-authored CA policy targeting `AgentZone == 3` are enabled and enforcing.
- **Preconditions.** AGENTID-03 PASS.
- **Steps.** Locate the Microsoft Managed `Block high-risk agents` policy via Graph; assert `state == 'enabled'`. Locate the tenant policy targeting `customSecurityAttributes.Agent.AgentZone eq '3'` (filter syntax pinned in CA-as-code repo); assert `state == 'enabled'` AND grant is the phishing-resistant AAL3 strength.
- **Expected.** Both policies enabled and enforcing.
- **Pass.** Both states `enabled`; tenant policy grant matches AAL3 strength.
- **Audit assertion.** "Microsoft baseline floor and tenant ceiling for agent CA both enforce; the floor is not used as a substitute for tenant scoping."
- **Evidence.** `tests/agentid-04-managed-and-tenant-policies.json`.

### 4.8 Namespace `SP` — Service principal CA coverage (3 tests)

#### 1.11-SP-01 — Service principal CA policies exist and resolve to phishing-resistant or workload-identity equivalent grant ⛔

- **Objective.** Workload-identity CA policies for SPs in scope (Power Platform, Logic Apps, custom connectors used by AI agents) exist and apply a grant of `block`, `requireRiskAssessment`, or an Authentication Context the SP must satisfy via certificate-based credential.
- **Preconditions.** PRE-02 PASS; LIC-01 PASS.
- **Steps.** Enumerate workload-identity CA policies; cross-join against the in-scope SP roster from `manifest.scope.servicePrincipals[]`; flag in-scope SPs without a workload-identity CA policy.
- **Expected.** Every in-scope SP is bound to at least one workload-identity CA policy.
- **Pass.** `count(unboundInScopeSps) == 0`.
- **Audit assertion.** "Non-human identities operating against Microsoft 365 / Copilot resources are governed by CA at parity with human identities; no silent SP path bypasses the CA control plane."
- **Evidence.** `tests/sp-01-sp-ca-coverage.json`.

#### 1.11-SP-02 — Service principals NOT present in any user-targeted CA security group ⛔ (anti-pattern guard)

- **Objective.** No SP is a member of any group that appears in `users.includeGroups` of a CA policy intended for human identities — the parent control's flagged anti-pattern.
- **Preconditions.** Group membership enumerable.
- **Steps.** Enumerate every group referenced in `users.includeGroups` across enabled CA policies; resolve full membership; flag any member with `objectType == 'ServicePrincipal'`.
- **Expected.** Empty set.
- **Pass.** `count(spsInUserCaGroups) == 0`.
- **Audit assertion.** "Anti-pattern of mixing human and non-human identities in user-CA groups is verifiably absent (supports SOX ITGC and FFIEC IS Booklet)."
- **Evidence.** `tests/sp-02-no-sps-in-user-ca-groups.json`.

#### 1.11-SP-03 — Sentinel SP-sign-in detection rule fired or test-fired within review window ⚠

- **Objective.** The Sentinel analytic rule scoped to anomalous SP sign-ins (e.g., new IP, new resource, dormant-SP wake-up) is enabled and has a recent fired-or-test-fired record.
- **Preconditions.** Sentinel rule export accessible.
- **Steps.** Locate the rule by its documented `displayName`; assert `enabled == true`; query rule incident history; assert at least one `incidentCreated` OR signed manual test-fire record exists in the cycle window.
- **Expected.** Rule enabled and exercised within window.
- **Pass.** Both conditions true.
- **Audit assertion.** "Detective control over SP sign-in anomalies is operational, not merely configured."
- **Evidence.** `tests/sp-03-sentinel-spdetection.json`.

### 4.9 Namespace `BREAKGLASS` — Emergency access (3 tests)

#### 1.11-BREAKGLASS-01 — Two cloud-only hardware-FIDO2 BG accounts, quarterly recoverability test signed ⛔

- **Objective.** Re-prove the BG posture asserted in PRE-03 at test time (defence in depth — PRE-03 happens at cycle start, BG-01 happens during §4 to detect mid-cycle drift).
- **Preconditions.** PRE-03 PASS.
- **Steps.** Re-enumerate Global Admin role members; recompute the BG-cloud-only-hardware-FIDO2 set; assert ≥ 2; re-confirm the prior-quarter recoverability test record's signature is valid.
- **Expected.** Set size ≥ 2; signature valid.
- **Pass.** Both conditions true.
- **Audit assertion.** "Emergency access remains posture-pure mid-cycle; recoverability is exercised quarterly and signed."
- **Evidence.** `tests/breakglass-01-recoverability.json`.

#### 1.11-BREAKGLASS-02 — BG accounts NOT excluded from phishing-resistant Authentication Strength ⛔ (most-mis-implemented exception)

- **Objective.** BG accounts are excluded from CA policies that would lock them out (correct), but **not** excluded from the phishing-resistant Authentication Strength requirement that protects them from credential-only attack (correct framing — many tenants get this backwards).
- **Preconditions.** BG roster from PRE-03.
- **Steps.** For each enabled CA policy: confirm BG accounts appear in `users.excludeUsers` (PASS direction); separately, assert there is **no** policy whose grant **removes** the AAL3 phishing-resistant requirement specifically for BG accounts (FAIL direction).
- **Expected.** BG excluded from lockout-risk policies; BG NOT excluded from phishing-resistant grant.
- **Pass.** Both directional checks pass.
- **Audit assertion.** "BG exclusion model excludes only what locks them out; it does not silently downgrade their authenticator strength (supports the parent control's `!!! warning` anti-pattern)."
- **Evidence.** `tests/breakglass-02-not-excluded-from-phishresistant.json`.

#### 1.11-BREAKGLASS-03 — Sentinel alert on BG sign-in fires within tenant baseline ⚠

- **Objective.** The Sentinel analytic rule scoped to the BG account UPNs fires within `pre-07-baseline.sentinelIngestionP95` of a synthetic test sign-in.
- **Preconditions.** PRE-03 PASS; PRE-07 PASS.
- **Steps.** Trigger a no-impact test event (e.g., a benign Graph read that the rule's KQL captures) using a non-BG synthetic account that the rule treats as a BG match for test purposes (preferred over actually exercising a BG account); measure T0 → alert-created.
- **Expected.** Latency within baseline.
- **Pass.** Within `pre-07-baseline.sentinelIngestionP95 × 1.5`.
- **Audit assertion.** "BG sign-in detection is exercised, not assumed (supports IR readiness and FINRA 4530 30-day reporting)."
- **Evidence.** `tests/breakglass-03-sentinel-bg-alert-latency.json`.

### 4.10 Namespace `NEG` — Deny-by-default / negative tests (3 tests)

#### 1.11-NEG-01 — What-If with synthetic high-risk user → blocked ⛔

- **Objective.** The CA What-If tool, given a synthetic high-risk Z3 user (sign-in risk = high, location = unknown, device = non-compliant, app = Microsoft 365 Copilot), returns a deterministic block from the AAL3 + risk policy stack.
- **Preconditions.** What-If invokable via Graph.
- **Steps.** Construct the What-If request with the documented synthetic profile; capture `appliedPolicies` and `notAppliedPolicies` with reason codes; assert at least one applied policy with `grantControls.builtInControls` containing `block` OR a non-satisfiable strength.
- **Expected.** Synthetic high-risk Z3 sign-in resolves to block.
- **Pass.** Block resolved; reason codes captured.
- **Audit assertion.** "Deny-by-default is verifiable via deterministic What-If (supports control-design test evidence)."
- **Evidence.** `tests/neg-01-whatif-block.json`.

#### 1.11-NEG-02 — SP without WIDP cannot be silently bound to workload-identity CA policy ⛔

- **Objective.** Attempting to add an SP that does **not** carry WIDP consumption to a workload-identity CA policy either fails the bind OR is detected as a fail-open and surfaces as a finding within the cycle window.
- **Preconditions.** Sandbox SP without WIDP available; sandbox CA policy in test slot.
- **Steps.** In a non-production tenant slot or via a `-WhatIf` Graph call against production: attempt the bind; capture the response; if the bind succeeds despite missing WIDP, assert that LIC-01 surfaces this as a difference and that a Sentinel rule fires on the policy modification.
- **Expected.** Either the bind is rejected at policy save, or LIC-01 catches it AND Sentinel fires.
- **Pass.** One of the two safe outcomes.
- **Audit assertion.** "There is no silent fail-open path where a workload-identity CA policy targets an unlicensed SP; the failure mode is either rejection or detection."
- **Evidence.** `tests/neg-02-sp-without-widp.json`.

#### 1.11-NEG-03 — Canary CA policy disable fires Sentinel alert within baseline ⛔

- **Objective.** Disabling the canary CA policy from PRE-05 fires a Sentinel alert within `pre-07-baseline.sentinelIngestionP95`.
- **Preconditions.** PRE-05 PASS; PRE-07 PASS.
- **Steps.** Toggle the canary policy `state` from `enabledForReportingButNotEnforced` to `disabled` at T0; measure T0 → alert-created; restore the canary policy state; record both timestamps.
- **Expected.** Alert within baseline; canary state restored.
- **Pass.** Both conditions true.
- **Audit assertion.** "Canary detection over the CA control plane is operational; unauthorized CA disable is detected near-real-time relative to the tenant's measured ingestion baseline."
- **Evidence.** `tests/neg-03-canary-disable-alert.json`.

### 4.11 Namespace `SOV` — Sovereign-cloud parity (1 test)

#### 1.11-SOV-01 — Per-cloud feature parity matrix re-verified at `lastVerifiedUtc` ⛔

- **Objective.** Re-verify that the §5 sovereign-cloud parity matrix (CA features, Authentication Strengths, CAE, Token Protection, Agent ID, Identity Protection workload-identities) reflects current Microsoft Learn for the cycle's `lastVerifiedUtc`; gaps are recorded as compensating controls in `manifest.compensatingControls[]`.
- **Preconditions.** Operator can reach Microsoft Learn for each declared cloud's documentation.
- **Steps.** For each cloud `c ∈ {Commercial, GCC, GCC-High, DoD}`: open the relevant Learn page; record availability for each feature listed in §5; compare to the matrix in this playbook; record drift in `manifest.deviations[]`.
- **Expected.** Either no drift OR drift recorded with compensating control.
- **Pass.** Drift entries (if any) all have a non-null `compensatingControlId`.
- **Audit assertion.** "Sovereign-cloud parity gaps are surfaced and compensated, not silently passed (supports defensible regulatory posture across clouds)."
- **Evidence.** `tests/sov-01-parity-recheck.json`.

### 4.12 Namespace `IR` — Incident response readiness (2 tests)

#### 1.11-IR-01 — Risky-sign-in tabletop exercised within cycle window ⛔

- **Objective.** A tabletop covering a high-risk sign-in on a Z3 maker (e.g., impossible-travel + atypical-token-claim + Copilot Studio agent author) was exercised; the runbook executed end-to-end and the after-action report is signed.
- **Preconditions.** AI Incident Response Playbook current; IR roster current.
- **Steps.** Reference the cycle-window tabletop record; assert all required steps executed (detection → triage → containment via CAE revoke → forensics via sign-in logs + Audit logs + Defender for Identity → eradication via credential reset + session revoke → recovery → lessons learned); assert sign-off by Incident Response Lead AND CISO delegate.
- **Expected.** Tabletop record present, executed, signed.
- **Pass.** All conditions true.
- **Audit assertion.** "IR muscle memory for risky-sign-in scenarios on AI maker identities is exercised at least at cycle cadence (supports FINRA 4530 timely reporting and NYDFS 500.16 incident response)."
- **Evidence.** `tests/ir-01-risky-signin-tabletop.json`.

#### 1.11-IR-02 — Account-compromise tabletop tied to FINRA 4530 / NYDFS 72-hour notification timelines ⛔

- **Objective.** A second tabletop covering full account compromise of a Z3 maker exercised the FINRA 4530 30-calendar-day external reporting decision tree AND the NYDFS 23 NYCRR 500.17(a) 72-hour superintendent notification decision tree.
- **Preconditions.** Compliance Officer participated; legal counsel review available on request.
- **Steps.** Reference the cycle-window tabletop record; assert decision-tree branches were exercised with timestamps; assert Compliance Officer sign-off captured.
- **Expected.** Tabletop record present, executed, signed; both decision trees exercised.
- **Pass.** All conditions true.
- **Audit assertion.** "Regulatory notification decision trees for account compromise are pre-exercised; the firm does not first encounter the 72-hour clock during a real incident (supports NYDFS 500.17(a) and FINRA 4530)."
- **Evidence.** `tests/ir-02-compromise-tabletop.json`.

---
## 5. Sovereign-Cloud Parity Matrix

The matrix below is **re-verified each cycle by SOV-01**. Symbols: ✅ GA, 🟡 Preview, ⚠ partial / cloud-specific limits, ❌ not available, ❓ confirm at `lastVerifiedUtc`. **Treat any cell as authoritative only at the cycle's `lastVerifiedUtc`** — Microsoft revises sovereign-cloud feature matrices on its own cadence.

| Capability | Commercial | GCC | GCC High | DoD | Cycle action if a cell is ❌ or ❓ |
|---|---|---|---|---|---|
| Conditional Access (user policies) | ✅ | ✅ | ✅ | ✅ | n/a |
| CA Workload-Identities (workload-identity policies) | ✅ | ✅ | ❓ | ❓ | If ❓: SOV-01 records gap; LIC-01 still runs; SP-01 marks affected SPs as scope-excluded with compensating control |
| Authentication Strengths (built-in phishing-resistant) | ✅ | ✅ | ✅ | ✅ | n/a |
| Tenant-defined Authentication Strengths | ✅ | ✅ | ❓ | ❓ | If ❓: AUTHSTRENGTH-* uses built-in phishing-resistant strength; record deviation |
| Continuous Access Evaluation (CAE) | ✅ | ✅ | ⚠ | ⚠ | If ⚠: CAE-01 scoped to documented client/resource pairs only; CAE-02 still runs against measured baseline |
| Token Protection (sign-in token binding) | ✅ Windows; 🟡 macOS | ✅ Windows; 🟡 macOS | ❓ | ❓ | If ❓: DEVICE-01 marks Token Protection sub-assertion as scope-excluded with compensating control (e.g., shorter `signInFrequency`) |
| Identity Protection — user / sign-in risk | ✅ | ✅ | ⚠ | ⚠ | n/a |
| Identity Protection — workload identities | 🟡 | ❓ | ❓ | ❓ | If 🟡 or ❓: AGENTID-04 / SP-* may not have Identity-Protection-driven CA available; record as compensating-control gap |
| Privileged Identity Management (PIM) | ✅ | ✅ | ✅ | ✅ | n/a |
| Entra Agent ID | 🟡 | ❓ | ❓ | ❓ | If ❓: AGENTID-* tests scope to enrollable agents only; un-enrollable agents tracked under the parent control's "agent identity blueprint" alternative |
| Microsoft Authenticator (FedRAMP authorization) | n/a | ✅ | ✅ | ✅ | PRE-04 enforces |
| Defender for Identity (sensors on AD DS for federated paths) | ✅ | ✅ | ✅ | ✅ | n/a |
| Microsoft Sentinel (SIEM ingestion of sign-in logs + audit logs) | ✅ | ✅ | ✅ | ✅ | n/a |

> **Compensating-control discipline.** Every ❓ or ❌ cell that affects a §4 test outcome MUST appear in `manifest.compensatingControls[]` with `gap`, `compensatingControl`, `owner`, `acceptedRiskUntilUtc`, and `signedBy`. A gap without a compensating control is a finding.

---

## 6. JSON Schema, PowerShell Validator, Manifest Builder

### 6.1 Evidence JSON Schema (excerpt)

The full schema lives at `schemas/1.11/evidence.schema.json` in the repo. The validator (§6.2) refuses to emit an evidence pack that does not validate against this schema.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://fsi-agentgov/schemas/1.11/evidence.schema.json",
  "title": "FSI Agent Governance — Control 1.11 Evidence Pack",
  "type": "object",
  "required": ["envelope", "preflight", "tests", "manifest", "attestations"],
  "properties": {
    "envelope": {
      "type": "object",
      "required": ["controlId", "version", "cycleId", "cloud", "tenantId", "cycleStartedUtc", "cycleCompletedUtc", "lastVerifiedUtc", "previousCycleAttestationSha256"],
      "properties": {
        "controlId": { "const": "1.11" },
        "version": { "const": "v1.4" },
        "cycleId": { "type": "string", "pattern": "^[0-9]{4}-(Q[1-4]|M(0[1-9]|1[0-2])|W[0-5][0-9])$" },
        "cloud": { "enum": ["Commercial", "GCC", "GCC-High", "DoD"] },
        "tenantId": { "type": "string", "format": "uuid" },
        "cycleStartedUtc": { "type": "string", "format": "date-time" },
        "cycleCompletedUtc": { "type": "string", "format": "date-time" },
        "lastVerifiedUtc": { "type": "string", "format": "date-time" },
        "previousCycleAttestationSha256": {
          "oneOf": [
            { "type": "string", "pattern": "^[a-f0-9]{64}$" },
            { "type": "null", "description": "null only for genesis cycle" }
          ]
        }
      }
    },
    "preflight": {
      "type": "object",
      "required": ["PRE-01", "PRE-02", "PRE-03", "PRE-04", "PRE-05", "PRE-06", "PRE-07"],
      "additionalProperties": false,
      "patternProperties": {
        "^PRE-0[1-7]$": {
          "type": "object",
          "required": ["status", "evidenceFile"],
          "properties": {
            "status": { "enum": ["PASS", "FAIL", "N/A"] },
            "evidenceFile": { "type": "string" },
            "notes": { "type": "string" }
          }
        }
      }
    },
    "tests": {
      "type": "array",
      "minItems": 32,
      "items": {
        "type": "object",
        "required": ["testId", "namespace", "status", "evidenceFile", "executedUtc"],
        "properties": {
          "testId": { "type": "string", "pattern": "^1\\.11-[A-Z]+-[0-9]{2}$" },
          "namespace": { "enum": ["LIC", "CA", "AUTHSTRENGTH", "DEVICE", "CAE", "PIM", "AGENTID", "SP", "BREAKGLASS", "NEG", "SOV", "IR"] },
          "status": { "enum": ["PASS", "FAIL", "PASS_WITH_NOTE", "N/A", "SKIPPED_BY_PREGATE"] },
          "evidenceFile": { "type": "string" },
          "executedUtc": { "type": "string", "format": "date-time" },
          "auditAssertion": { "type": "string" }
        }
      }
    },
    "manifest": {
      "type": "object",
      "required": ["files", "manifestSha256", "validatorScriptSha256", "modules", "tenant", "cadenceEscalations", "deviations", "compensatingControls", "rollingBaselines"],
      "properties": {
        "files": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["path", "sha256", "sizeBytes"],
            "properties": {
              "path": { "type": "string" },
              "sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
              "sizeBytes": { "type": "integer", "minimum": 0 }
            }
          }
        },
        "manifestSha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "validatorScriptSha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "modules": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name", "version", "psd1Sha256"],
            "properties": {
              "name": { "type": "string" },
              "version": { "type": "string" },
              "psd1Sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" }
            }
          }
        },
        "tenant": {
          "type": "object",
          "required": ["tenantId", "cloud", "region"],
          "properties": {
            "tenantId": { "type": "string", "format": "uuid" },
            "cloud": { "enum": ["Commercial", "GCC", "GCC-High", "DoD"] },
            "region": { "type": "string" }
          }
        },
        "cadenceEscalations": { "type": "array" },
        "deviations": { "type": "array" },
        "compensatingControls": { "type": "array" },
        "rollingBaselines": {
          "type": "object",
          "properties": {
            "caPropagationP95": { "type": "string" },
            "caeRevocationP95": { "type": "string" },
            "pimActivationP95": { "type": "string" },
            "idpRiskP95": { "type": "string" },
            "sentinelIngestionP95": { "type": "string" }
          }
        }
      }
    },
    "attestations": {
      "type": "array",
      "minItems": 3,
      "items": {
        "type": "object",
        "required": ["signerRole", "signerUpn", "signedUtc", "manifestSha256AtSign", "priorCycleSha256", "signatureBase64"],
        "properties": {
          "signerRole": { "enum": ["AI Governance Lead", "Compliance Officer", "CISO delegate"] },
          "signerUpn": { "type": "string", "format": "email" },
          "signedUtc": { "type": "string", "format": "date-time" },
          "manifestSha256AtSign": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
          "priorCycleSha256": {
            "oneOf": [
              { "type": "string", "pattern": "^[a-f0-9]{64}$" },
              { "type": "null" }
            ]
          },
          "signatureBase64": { "type": "string" }
        }
      }
    }
  }
}
```

### 6.2 PowerShell Validator (skeleton)

The full script lives at `scripts/1.11/Invoke-Verification.ps1`. The skeleton below shows the **fail-closed contract**: PRE gate failure → exit 2; test failure → exit 1; clean cycle → exit 0; self-integrity failure (validator hash mismatch) → exit 2.

```powershell
#Requires -Version 7.4
#Requires -Modules @{ModuleName='Microsoft.Graph';ModuleVersion='2.20.0'}
#Requires -Modules @{ModuleName='Microsoft.Graph.Identity.SignIns';ModuleVersion='2.20.0'}
#Requires -Modules @{ModuleName='Microsoft.Graph.Identity.Governance';ModuleVersion='2.20.0'}
#Requires -Modules @{ModuleName='MSCommerce';ModuleVersion='2.0'}
[CmdletBinding()]
param(
  [Parameter(Mandatory)] [string] $TenantId,
  [Parameter(Mandatory)] [ValidateSet('Commercial','GCC','GCC-High','DoD')] [string] $Cloud,
  [Parameter(Mandatory)] [string] $CycleId,
  [Parameter(Mandatory)] [string] $EvidenceRoot,
  [string] $PriorCycleAttestationSha256
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 3

# --- Self-integrity gate (fail-closed) ---
$selfPath  = $PSCommandPath
$expected  = Get-Content "$PSScriptRoot/Invoke-Verification.ps1.sha256" -Raw -ErrorAction Stop
$actual    = (Get-FileHash -Path $selfPath -Algorithm SHA256).Hash.ToLower()
if ($actual -ne $expected.Trim().ToLower()) {
  Write-Error "Validator self-hash mismatch (expected=$expected actual=$actual). Refusing to run."
  exit 2
}

# --- Helpers ---
$global:PreResults  = @{}
$global:TestResults = [System.Collections.Generic.List[object]]::new()

function Invoke-Gate {
  param([string]$Id, [scriptblock]$Block)
  Write-Host "[PRE] $Id starting"
  try {
    $r = & $Block
    if ($r.Status -notin 'PASS','N/A') { throw "Gate $Id returned $($r.Status)" }
    $global:PreResults[$Id] = $r
    Write-Host "[PRE] $Id $($r.Status)"
  } catch {
    $global:PreResults[$Id] = [pscustomobject]@{ Status='FAIL'; Notes=$_.Exception.Message; EvidenceFile="preflight/$Id-FAIL.json" }
    Write-Error "[PRE] $Id FAIL: $_"
    Write-EvidencePack
    exit 2  # fail-closed — no §4 test results emitted
  }
}

function Invoke-Test {
  param([string]$Id, [string]$Namespace, [scriptblock]$Block)
  Write-Host "[TEST] $Id starting"
  try {
    $r = & $Block
    $global:TestResults.Add([pscustomobject]@{
      testId         = $Id
      namespace      = $Namespace
      status         = $r.Status
      evidenceFile   = $r.EvidenceFile
      executedUtc    = (Get-Date).ToUniversalTime().ToString('o')
      auditAssertion = $r.AuditAssertion
    })
  } catch {
    $global:TestResults.Add([pscustomobject]@{
      testId='1.11-' + $Namespace + '-' + ($Id -replace '.*-',''); namespace=$Namespace; status='FAIL';
      evidenceFile="tests/$Id-EXCEPTION.json"; executedUtc=(Get-Date).ToUniversalTime().ToString('o');
      auditAssertion="Exception: $($_.Exception.Message)"
    })
  }
}

# --- PRE gates (fail any → exit 2) ---
Invoke-Gate 'PRE-01' { Test-OperatorPimAndSeparation }
Invoke-Gate 'PRE-02' { Test-LicensingFloor }
Invoke-Gate 'PRE-03' { Test-BreakGlassPosture }
Invoke-Gate 'PRE-04' { Test-AuthenticatorFedRamp -Cloud $Cloud }
Invoke-Gate 'PRE-05' { Test-CanaryPolicyAndUser }
Invoke-Gate 'PRE-06' { Test-EnvironmentAndModules -Cloud $Cloud }
Invoke-Gate 'PRE-07' { Measure-TenantBaselines }

# --- §4 Tests ---
Invoke-Test '1.11-LIC-01'          'LIC'          { Test-WidpCoverage }
Invoke-Test '1.11-LIC-02'          'LIC'          { Test-UserLicenseByZone }
Invoke-Test '1.11-LIC-03'          'LIC'          { Test-FedRampAttestationFreshness -Cloud $Cloud }
Invoke-Test '1.11-CA-01'           'CA'           { Test-AuthStrengthBoundToZ3 }
Invoke-Test '1.11-CA-02'           'CA'           { Test-CaAsCodeDrift }
Invoke-Test '1.11-CA-03'           'CA'           { Test-ExclusionsRegistered }
Invoke-Test '1.11-CA-04'           'CA'           { Test-ReportOnlyAndNamedLocations }
Invoke-Test '1.11-AUTHSTRENGTH-01' 'AUTHSTRENGTH' { Test-SyncedPasskeyExcluded }
Invoke-Test '1.11-AUTHSTRENGTH-02' 'AUTHSTRENGTH' { Test-Fido2OnlyOnZ3 }
Invoke-Test '1.11-AUTHSTRENGTH-03' 'AUTHSTRENGTH' { Test-CbaChainValidity }
Invoke-Test '1.11-DEVICE-01'       'DEVICE'       { Test-CompliantDeviceTokenProtSif }
Invoke-Test '1.11-DEVICE-02'       'DEVICE'       { Test-JoinStateOnZ3 }
Invoke-Test '1.11-DEVICE-03'       'DEVICE'       { Test-MamOnMobileMakers }
Invoke-Test '1.11-CAE-01'          'CAE'          { Test-CaeTrueOnCopilot }
Invoke-Test '1.11-CAE-02'          'CAE'          { Test-CaeRevocationBaseline }
Invoke-Test '1.11-PIM-01'          'PIM'          { Test-MfaOnPimActivation }
Invoke-Test '1.11-PIM-02'          'PIM'          { Test-EligibilityOnly }
Invoke-Test '1.11-PIM-03'          'PIM'          { Test-DurationJustificationTicket }
Invoke-Test '1.11-AGENTID-01'      'AGENTID'      { Test-AgentEnrollmentSponsor }
Invoke-Test '1.11-AGENTID-02'      'AGENTID'      { Test-SponsorReviewFreshness }
Invoke-Test '1.11-AGENTID-03'      'AGENTID'      { Test-AgentZoneAttribute }
Invoke-Test '1.11-AGENTID-04'      'AGENTID'      { Test-ManagedAndTenantAgentPolicies }
Invoke-Test '1.11-SP-01'           'SP'           { Test-SpCaCoverage }
Invoke-Test '1.11-SP-02'           'SP'           { Test-NoSpsInUserCaGroups }
Invoke-Test '1.11-SP-03'           'SP'           { Test-SentinelSpDetection }
Invoke-Test '1.11-BREAKGLASS-01'   'BREAKGLASS'   { Test-BgRecoverability }
Invoke-Test '1.11-BREAKGLASS-02'   'BREAKGLASS'   { Test-BgNotExcludedFromPhishResistant }
Invoke-Test '1.11-BREAKGLASS-03'   'BREAKGLASS'   { Test-BgSentinelLatency }
Invoke-Test '1.11-NEG-01'          'NEG'          { Test-WhatIfBlock }
Invoke-Test '1.11-NEG-02'          'NEG'          { Test-SpWithoutWidp }
Invoke-Test '1.11-NEG-03'          'NEG'          { Test-CanaryDisableAlertLatency }
Invoke-Test '1.11-SOV-01'          'SOV'          { Test-SovereignParityRecheck -Cloud $Cloud }
Invoke-Test '1.11-IR-01'           'IR'           { Test-RiskySigninTabletop }
Invoke-Test '1.11-IR-02'           'IR'           { Test-CompromiseTabletop }

# --- Build manifest, write evidence pack, return exit code ---
$failed = $global:TestResults | Where-Object { $_.status -eq 'FAIL' }
Write-EvidencePack
if ($failed.Count -gt 0) { exit 1 }
exit 0
```

### 6.3 Manifest Builder Contract

`Write-EvidencePack` (above) MUST:

1. Compute SHA-256 over every file under `$EvidenceRoot/preflight` and `$EvidenceRoot/tests`.
2. Build `manifest.json` with `files[]`, `tenant`, `modules` (from PRE-06), `cadenceEscalations[]` (from prior cycle), `deviations[]`, `compensatingControls[]`, `rollingBaselines` (computed from current + prior 3 cycles).
3. Compute `manifestSha256` over the canonical JSON serialization of `manifest.json` **excluding** the `manifestSha256` and `validatorScriptSha256` properties themselves (the post-fill canonicalization rule).
4. Set `validatorScriptSha256` to the validator's measured self-hash.
5. Write `evidence.json` (envelope + preflight + tests + manifest + attestations).
6. Validate `evidence.json` against `schemas/1.11/evidence.schema.json`; refuse to write a non-validating pack (raise and exit 2).

---

## 7. Hash-Chain Attestation (3 signatures, prior-cycle chain)

Each cycle's `evidence.json` requires **three** independent signatures:

| # | Role | Signs what | Why |
|---|---|---|---|
| 1 | **AI Governance Lead** | `manifestSha256AtSign` | Owns AI agent governance posture across the framework |
| 2 | **Compliance Officer** | `manifestSha256AtSign` | Owns regulatory mapping (FINRA, SEC, SOX, GLBA, NYDFS, FFIEC, OCC, Fed SR) |
| 3 | **CISO delegate** | `manifestSha256AtSign` | Owns identity-control plane and incident-response posture |

Each signer's record carries `priorCycleSha256` set to the prior cycle's `manifestSha256`. The **first** (genesis) cycle uses `null` and a documented genesis attestation note. A cycle whose `priorCycleSha256` cannot be matched to an extant prior cycle is treated as a **chain break** by the assessment engine and the control's confidence is set to `low` until an investigator-signed reconciliation note resolves the gap.

> **Integrity properties.** (a) Tamper-evidence — any post-sign edit to the evidence pack changes `manifestSha256AtSign` and invalidates all three signatures. (b) Non-repudiation — three roles, three signers, three independent reporting lines. (c) Append-only history — `priorCycleSha256` chain makes silent deletion of a prior cycle detectable.

---

## 8. Anti-Patterns (paired one-to-one with detecting tests)

| # | Anti-pattern | Detected by |
|---|---|---|
| AP-01 | Service principal placed in a user-targeted CA group | `1.11-SP-02` |
| AP-02 | Synced (multi-device) passkey accepted as AAL3 | `1.11-AUTHSTRENGTH-01` |
| AP-03 | Break-glass excluded from the phishing-resistant Authentication Strength | `1.11-BREAKGLASS-02` |
| AP-04 | Break-glass with SMS / voice / OTP / Authenticator factor registered | `PRE-03` and `1.11-BREAKGLASS-01` |
| AP-05 | Permanent active assignment on `Entra Security Admin` / `Authentication Administrator` / `Entra Identity Governance Admin` | `1.11-PIM-02` |
| AP-06 | PIM activation accepts a session-token-reuse MFA claim instead of fresh CA-Auth-Context MFA | `1.11-PIM-01` |
| AP-07 | Z3 maker CA grant lacks `compliantDevice` OR `signInTokenProtection` OR `signInFrequency` | `1.11-DEVICE-01` |
| AP-08 | Z3 maker permitted to authenticate with non-FIDO2 / non-WHfB / non-CBA factor | `1.11-AUTHSTRENGTH-02` |
| AP-09 | Out-of-band CA edit not reflected in CA-as-code repo | `1.11-CA-02` |
| AP-10 | Stale CA exclusion (no review within grace window) or unregistered exclusion | `1.11-CA-03` |
| AP-11 | Stale Report-only policy silently retained past the documented pilot window | `1.11-CA-04` |
| AP-12 | Workload-identity CA policy targeting an SP without WIDP consumption (silent fail-open) | `1.11-LIC-01` and `1.11-NEG-02` |
| AP-13 | SP-targeted CA policy without Workload Identities Premium for the cloud | `1.11-NEG-02` |
| AP-14 | Agent enrolled in Power Platform but not in Entra Agent ID OR with null sponsor | `1.11-AGENTID-01` |
| AP-15 | Custom security attribute `AgentZone` missing on a Z2/Z3 agent (CA filter cannot target deterministically) | `1.11-AGENTID-03` |
| AP-16 | Microsoft Managed `Block high-risk agents` policy disabled OR tenant Z3-agent CA policy missing | `1.11-AGENTID-04` |
| AP-17 | Real PII or production user used as the canary user | `PRE-05` |
| AP-18 | Numeric CA / CAE / PIM / IDP latency SLA asserted without Microsoft Learn citation | Schema $id check + `pre-07` discipline; cycle reviewer rejects narrative claims that cite no Learn URL |

---

## 9. Cross-Linked Controls (12)

| Linked control | Why it matters here |
|---|---|
| **1.5** Sensitivity labels & DLP | Z3 maker access + Token Protection complement label-bound access; CA enforces who, labels enforce what |
| **1.7** Tenant restrictions / cross-tenant access | TR v2 governs which external tenants can be reached; CA governs the local identity that initiates the call |
| **1.12** Identity Protection / Insider Risk Management | Risk-based CA grants in §4 depend on IRM/IDP risk signals being current and tenant-baselined |
| **1.14** Data minimization & policy-aware DLP | Phishing-resistant MFA reduces account-compromise paths into data assets that DLP also guards |
| **1.19** eDiscovery & evidence preservation | The hash-chain attestation pattern in §7 mirrors 1.19's evidentiary chain; cross-cycle integrity is inherited |
| **1.21** Adversarial sign-in correlation & threat hunting | NEG-01 What-If and IR-01 / IR-02 tabletops feed 1.21's detection content |
| **2.5** PIM lifecycle & access reviews | PIM-01..03 in §4 are the day-to-day enforcement of 2.5's lifecycle policy |
| **2.8** Service principal consent & permissions | SP-01..03 in §4 enforce 2.8's consent posture at the CA layer |
| **2.22** Inactivity timeout enforcement | `signInFrequency` in DEVICE-01 is the CA half of 2.22's session-lifetime control |
| **2.26** Entra Agent ID identity governance | AGENTID-01..04 in §4 are the CA-side enforcement of 2.26's agent-lifecycle governance |
| **3.8** Copilot Hub & governance dashboard | Cycle outcome (and `manifest.compensatingControls[]`) feed the dashboard's residual-risk view |
| **AI Incident Response Playbook** | IR-01 / IR-02 tabletops execute against the playbook's runbooks; cycle records sign-off |

---

## 10. Cycle-Close Checklist

- [ ] All 7 PRE gates returned PASS or N/A (no FAIL).
- [ ] All 32 §4 tests have a status; none are `SKIPPED_BY_PREGATE` for a PRE gate that itself returned PASS.
- [ ] `evidence.json` validates against `schemas/1.11/evidence.schema.json` (validator exited 0 or 1, never 2).
- [ ] `manifest.json` `manifestSha256` recomputed and stable.
- [ ] `validatorScriptSha256` matches the pinned `Invoke-Verification.ps1.sha256`.
- [ ] All required modules (PRE-06) hash-pinned; signatures Valid.
- [ ] Three signatures present; each signer's role is one of {AI Governance Lead, Compliance Officer, CISO delegate}; UPNs distinct.
- [ ] `priorCycleSha256` matches the prior cycle's `manifestSha256` (or is `null` for genesis with documented note).
- [ ] Every `compensatingControl` has `acceptedRiskUntilUtc` not in the past.
- [ ] Cadence escalation events (if any) recorded in `manifest.cadenceEscalations[]`.
- [ ] Drift entries reconciled (CA-as-code PRs merged, exclusion register updated, named-locations updated).
- [ ] Tabletop after-action reports archived and signed.
- [ ] Evidence pack uploaded to long-term retention store with SEC 17a-4(f) WORM policy applied (where applicable).
- [ ] Assessment engine notified; `docs/assessment/state.json` updated; Copilot Hub dashboard refreshed.
- [ ] If any §4 test returned FAIL, an issue is filed in the governance repo with the test ID, owner, due date, and (if appropriate) `acceptedRiskUntilUtc`.

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
