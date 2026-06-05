# Portal Walkthrough — Control 1.11: Entra Conditional Access and Phishing-Resistant MFA for AI Agents

**Control:** [1.11 — Conditional Access and Phishing-Resistant MFA](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md)
**Pillar:** 1 — Security
**Last UI Verified:** May 2026 (Microsoft Entra admin center, Microsoft Defender portal, Power Platform admin center, Microsoft Copilot Studio)
**Estimated Time:** 14–22 hours of admin effort across 5–7 calendar days (includes the mandatory 7-day Report-only soak window)
**Governance Levels:** Baseline / Recommended / Regulated
**Audience:** Entra Global Admin, Entra Security Admin, Authentication Policy Admin, Power Platform Admin, AI Administrator, Sentinel Admin, Purview Compliance Admin, CISO, Compliance Officer, Agent Owner, Agent Maker
**Companion playbooks:** [`./powershell-setup.md`](./powershell-setup.md) · [`./verification-testing.md`](./verification-testing.md) · [`./troubleshooting.md`](./troubleshooting.md) · [`./conditional-access-agent-templates.md`](./conditional-access-agent-templates.md)

---

!!! warning "Scope Limit — what this control IS and IS NOT"
    Control 1.11 is an **identity-plane access control**. It governs **who (or what) can sign in to surfaces that produce, host, administer, or invoke Microsoft 365 AI agents** and **how strongly that sign-in is authenticated**. It is **preventive** — it blocks an unauthorized session at the front door.

    It is **not** an evidentiary, supervisory, content-quality, or model-risk control. Specifically, this playbook does **not** replace:

    | Adjacent concern | Owning control |
    
    | Supervisory review of agent outputs (FINRA Rule 3110, registered principal sign-off) | [Control 2.12 — Supervision and Oversight under FINRA Rule 3110](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |
    | DLP policies, environment strategy, connector classification for Power Platform / Copilot Studio | [Control 2.2 — Environment Groups and Tier Classification](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) |
    | Model risk management framework (OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) alignment) | [Control 2.6 — Model Risk Management Alignment with OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) |
    | Agent publishing authorization, maker entitlement gating | [Control 1.1 — Restrict Agent Publishing by Authorization](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) |
    | Lifecycle for ownerless agents and orphan remediation | [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |
    | Agent inventory, governance dashboards, admin-gated approvals | [Control 2.25 — Microsoft Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) |
    | SIEM ingestion, KQL analytics, sign-in correlation rules | [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) |

    A configured Conditional Access (CA) policy that blocks an unauthorized session does **not** generate the supervisory record that FINRA Rule 3110 requires for the *content* of an agent interaction; that record is produced by the controls listed above. Treat 1.11 as a necessary but not sufficient layer.

!!! info "Human vs Agent identity — two distinct MFA boundaries"
    Two identity types touch agent surfaces, and they must be governed by **different mechanisms**:

    | Identity type | Examples | How MFA works | Conditional Access path |
    
    | **Human (interactive) identity** | Agent maker, agent owner, Power Platform Admin, AI Administrator, end-user invoking a Copilot agent in Teams | Interactive MFA prompt — passkey, FIDO2 security key, Windows Hello for Business, Microsoft Authenticator (push + number match) | Standard CA policy targeting `Users and groups` |
    | **Agent / workload identity** | Service principal that runs a Copilot Studio agent, managed identity for an autonomous agent, Entra Agent ID registration, third-party connector app | **Cannot perform interactive MFA** (no human at the keyboard). Governed by certificate-based auth, managed identity, secret rotation, and **Conditional Access for Workload Identities** (CA-WID) which evaluates **location, sign-in risk, and named locations** instead of MFA strength | CA policy with `Users and workload identities → Workload identities` selected (requires the **Microsoft Entra Workload Identities Premium P1 add-on** licensed per service principal in scope) |

    "MFA the agent" is a category error. Strong agent-identity governance means **(a)** issuing the agent a non-shared credential (managed identity preferred, then certificate, then secret with mandatory ≤90-day rotation), **(b)** scoping it via CA-WID to permitted IP ranges and risk thresholds, and **(c)** monitoring its sign-ins separately from human sign-ins. See §7 for the workload-identity path.

!!! warning "Hedged-Language Reminder"
    The procedures here **support compliance with** and **help meet** the following expectations; they do **not** by themselves satisfy any obligation, and configuration is necessary but not sufficient:

    - **FFIEC** — *Authentication and Access to Financial Institution Services and Systems* (June 2021 update to the 2005 *Authentication in an Internet Banking Environment* guidance) — risk-based, layered authentication for high-risk transactions and administrative access
    - **NYDFS 23 NYCRR Part 500 §500.12** — Multi-Factor Authentication; the Second Amendment (effective Nov 1, 2024 / Nov 1, 2025) requires MFA for **any individual** accessing the covered entity's information systems, with Class A companies expected to adopt **phishing-resistant** authentication for privileged accounts
    - **SEC Regulation S-P** — Safeguards Rule and Disposal Rule (May 2024 amendments) — written policies and procedures reasonably designed to safeguard customer information, with 30-day customer-notification timeline on unauthorized access
    - **FINRA Regulatory Notice 21-18** — Cybersecurity practices, supervision of access control changes
    - **NIST SP 800-63B** — Authenticator Assurance Levels; AAL2 (multi-factor) and AAL3 (hardware-bound, verifier-impersonation-resistant) — phishing-resistant authenticators (FIDO2, passkeys, Windows Hello for Business, smart cards) map to AAL3
    - **CISA Zero Trust Maturity Model v2.0** — Identity pillar Optimal stage (continuous, phishing-resistant authentication; centralized identity store; just-in-time access)
    - **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7)** — Model risk management; the supervisory expectation that monitoring of model performance and access extends to AI agents that materially influence customer or financial outcomes
    - **CFTC Rule 1.31 / 17 CFR §1.31** — recordkeeping; sign-in logs and CA policy-change records must be retained in a non-rewritable, non-erasable form

    Implementation requires validated change-control procedures, a periodic access review (Control 2.5), and independent testing. Organizations should verify all configurations against examiner workpapers and counsel.

!!! info "Surface inventory — portals you will touch in this playbook"
    | # | Surface | URL | Owner role |
    
    | 1 | Microsoft Entra admin center | `https://entra.microsoft.com` | Authentication Policy Admin, Entra Security Admin |
    | 2 | Microsoft Defender portal (Sentinel + Identity) | `https://security.microsoft.com` | Sentinel Admin |
    | 3 | Power Platform admin center | `https://admin.powerplatform.microsoft.com` | Power Platform Admin |
    | 4 | Copilot Studio | `https://copilotstudio.microsoft.com` | Agent Maker, AI Administrator |
    | 5 | Microsoft 365 admin center (license validation) | `https://admin.microsoft.com` | Entra Global Admin |
    | 6 | Microsoft Agent 365 Admin Center (governance console) | `https://admin.microsoft.com` → Agent 365 | AI Administrator (cross-ref [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)) |

---

## Document Map

| § | Section | Outcome |

| 0 | [Pre-flight prerequisites and license validation](#0-pre-flight-prerequisites-and-license-validation) | Confirm SKUs, roles, network position, and break-glass posture before any change |
| 1 | [Migrate Security Defaults to a Conditional Access baseline](#1-migrate-security-defaults-to-a-conditional-access-baseline) | Tenant has CA-driven baseline, not Security Defaults |
| 2 | [Authentication Methods policy — passwordless-first baseline](#2-authentication-methods-policy-passwordless-first-baseline) | FIDO2, WHfB, Passkeys enabled; SMS/voice deprecated for privileged roles |
| 3 | [Authentication Strengths — create the "Phishing-Resistant MFA" strength](#3-authentication-strengths-create-the-phishing-resistant-mfa-strength) | Reusable strength object bound to CA policies |
| 4 | [Named Locations — corporate IP ranges and country allow-list](#4-named-locations-corporate-ip-ranges-and-country-allow-list) | Trusted IP envelopes for human and workload policies |
| 5 | [Policy A — Phishing-resistant MFA for all privileged roles](#5-policy-a-phishing-resistant-mfa-for-all-privileged-roles) | Privileged role activations require AAL3-class authenticator |
| 6 | [Policy B — Agent makers require compliant device + phishing-resistant MFA](#6-policy-b-agent-makers-require-compliant-device-phishing-resistant-mfa) | Copilot Studio / Power Platform maker access fenced to compliant devices |
| 7 | [Policy C — Conditional Access for Workload Identities (agents and SPs)](#7-policy-c-conditional-access-for-workload-identities-agents-and-sps) | Agent identities scoped to named locations and risk thresholds |
| 8 | [Policy D — Session controls: CAE, sign-in frequency, Token Protection](#8-policy-d-session-controls-cae-sign-in-frequency-token-protection) | Continuous evaluation, 4-hour reauth in Z3, token binding pilot |
| 9 | [Entra Agent ID — locating agent identities and assigning them to CA](#9-entra-agent-id-locating-agent-identities-and-assigning-them-to-ca) | Agent identities discoverable in Workload identities blade and bound to Policy C |
| 10 | [Privileged Identity Management — activation-time MFA for AI / privileged roles](#10-privileged-identity-management-activation-time-mfa-for-ai-privileged-roles) | PIM eligibility with on-activation phishing-resistant MFA |
| 11 | [Sentinel Conditional Access Insights workbook](#11-sentinel-conditional-access-insights-workbook) | Daily / weekly impact dashboard wired to the Control 3.9 workspace |
| 12 | [Break-glass / emergency access accounts](#12-break-glass-emergency-access-accounts) | Two cloud-only accounts excluded from CA, monitored by analytic rule |
| 13 | [Report-only to Enforce rollout — the 7-day soak](#13-report-only-to-enforce-rollout-the-7-day-soak) | Documented rollout with sign-in log review |
| 15 | [Evidence pack and verification cross-references](#15-evidence-pack-and-verification-cross-references) | Examiner-ready artifact list |

---

## 0. Pre-flight prerequisites and license validation

Before changing anything in production, complete every gate below. Skipping a gate is the most common cause of a CA rollout that locks administrators out of the tenant.

### 0.1 Confirm administrative roles assigned via PIM (eligible, not active)

Sign in to `https://entra.microsoft.com` with an account that already holds **Entra Global Admin** in the tenant. Browse to **Identity governance → Privileged Identity Management → Microsoft Entra roles → Assignments**. Filter to **Eligible assignments**.

Confirm the roles below are present and assigned only to named individuals (not shared service accounts). Use the **canonical role names** from `docs/reference/role-catalog.md` — if your tenant displays the legacy long-form name, that is the same role.

| Canonical role | Required for | Minimum count |

| **Entra Global Admin** | Migrating Security Defaults, creating tenant-wide CA policies | 2 (plus 2 break-glass — see §12) |
| **Authentication Policy Admin** | Authentication Methods policy, Authentication Strengths | 2 |
| **Conditional Access Admin** *(Microsoft built-in role)* | Creating and editing CA policies | 2 |
| **Entra Security Admin** | Reviewing risky users, managing Identity Protection | 2 |
| **Power Platform Admin** | Validating that Policy B does not break Copilot Studio | 1+ |
| **AI Administrator** | Reviewing agent identities (Entra Agent ID, GA April 2026) and Agent 365 console | 1+ |
| **Sentinel Admin** | Wiring the CA Insights workbook in §11 | 1 |

!!! danger "Do not use 'Administrator' as a role name"
    The canonical short name is **Authentication Policy Admin**, not "Authentication Policy Administrator". The Entra portal still displays the long form; the role is identical. The same applies to Power Platform Admin (not "Power Apps Admin"), Exchange Online Admin (not "Exchange Administrator"), and Purview Compliance Admin (not "Compliance Administrator"). Use the short forms in all internal documentation, change tickets, and WSPs to avoid drift.

### 0.2 Validate license entitlements

Open `https://admin.microsoft.com → Billing → Licenses`. Confirm the SKUs below before promoting any policy past Report-only.

| SKU | Required for | Minimum count |

| **Microsoft Entra ID P1** | Conditional Access for human users; Authentication Strengths | All licensed users in any CA policy scope |
| **Microsoft Entra ID P2** | Identity Protection risk policies, PIM, risky-user CA conditions | All privileged-role holders |
| **Microsoft Entra Workload Identities Premium (P1 add-on)** | Conditional Access for Workload Identities (CA-WID) | One per service principal, managed identity, or Entra Agent ID identity in CA-WID scope |
| **Microsoft 365 E5** *or* **Microsoft 365 E3 + Entra ID P2** | Token Protection (Preview), Continuous Access Evaluation | Privileged users, Z3 environment users |
| **Microsoft Defender for Cloud Apps** *(optional)* | Session controls beyond CAE (cloud app reverse proxy) | As scoped |
| **Microsoft Sentinel** | §11 workbook and analytic rules | Tenant-level |

!!! warning "CA-WID without the P1 add-on fails open"
    A Conditional Access policy that targets a **workload identity** without a **Microsoft Entra Workload Identities Premium** license assigned to that identity will **not enforce** — the policy simply does not evaluate. There is **no** in-portal warning for this. The only safe verification is to (a) attempt a deliberate denial scenario (block by named location) from outside the trusted IP range and (b) inspect the Sign-in logs (Service principal sign-ins tab) for the `conditionalAccessStatus` field. A `notApplied` status with the policy in scope is the symptom. See [`./troubleshooting.md`](./troubleshooting.md) issue T-07.


### 0.4 Confirm break-glass accounts already exist

Two cloud-only `*.onmicrosoft.com` emergency-access accounts must exist **before** any CA policy is enabled. If they do not, complete §12 first, then return here. The single most common source of tenant lockout is enabling a CA policy that targets "All users" without confirming the break-glass accounts are excluded.

### 0.5 Document the change in your CAB record

Open the change ticket and reference (a) this playbook revision, (b) the target Authentication Strength name, (c) the four CA policy names you will create, (d) the 7-day Report-only window dates, and (e) the planned cutover date. Attach the empty Evidence Pack folder structure from §15.

---

## 1. Migrate Security Defaults to a Conditional Access baseline

If your tenant still has **Security Defaults** turned on, you cannot create granular CA policies. Security Defaults is an all-or-nothing tenant-wide MFA enforcement that conflicts with policy-based access control. The migration path is well documented and one-way.

### 1.1 Determine current state

1. Browse to `https://entra.microsoft.com → Identity → Overview → Properties` (the **Properties** tab on the tenant overview blade).
2. Scroll to **Security defaults**. Note whether it reads **Enabled** or **Disabled**.

### 1.2 If Security Defaults is enabled — disable only after CA baseline is staged

Do **not** disable Security Defaults until you have at least one CA policy in **Report-only** that requires MFA for privileged roles (the policy you will create in §5). The recommended order is:

1. Stage Policy A from §5 in **Report-only**.
2. Confirm break-glass accounts exist and are excluded (§12).
3. Return to **Properties → Security defaults** and click **Manage security defaults**.
4. Toggle **Security defaults** to **Disabled**.
5. Select **My organization is using Conditional Access** as the reason.
6. Click **Save**.

7. Within 5 minutes, enable Policy A by switching it from **Report-only** to **On** (after the soak period defined in §13). Until that switch, the tenant is in a **temporary reduced-MFA state** — schedule the cutover to occur during a maintenance window with monitoring eyes-on.

!!! warning "Migration is not reversible without re-enabling Security Defaults"
    Once disabled, your tenant relies entirely on the CA policies you have authored. There is no automatic re-application of the Microsoft baseline if you delete all your CA policies. Microsoft Managed Policies (the `Source = Microsoft` baseline templates) provide some safety net, but they do **not** replicate Security Defaults coverage. Treat this as a one-way door.

---

## 2. Authentication Methods policy — passwordless-first baseline

The Authentication Methods policy controls **what authenticators users may register and use**. It is distinct from Conditional Access (which decides **whether** an authentication is acceptable for a given resource). You must enable the strong methods here **before** you can require them in a CA policy.

### 2.1 Navigate to the Authentication Methods policy

1. `https://entra.microsoft.com → Protection → Authentication methods → Policies`.

The blade lists every method (FIDO2, Microsoft Authenticator, Passkey (FIDO2), Windows Hello for Business, Certificate-based authentication, OATH tokens, SMS, Voice call, Email OTP, Temporary Access Pass, Hardware OATH tokens, QR Code (Preview), Third-party software OATH tokens). Each row shows **Enabled**, **Target**, and **Last modified**.

### 2.2 Enable FIDO2 security keys

1. Click **FIDO2 security key** in the methods list.
2. Toggle **Enable** to **On**.
3. Under **Target**, select **All users** (or a pilot group during phased rollout — see §13).
4. Expand **Configure** and set:
   - **Allow self-service set up:** Yes
   - **Enforce attestation:** Yes (rejects keys that cannot prove their cryptographic provenance)
   - **Enforce key restrictions:** Yes
   - **Restrict specific keys:** **Allow** — populate with the AAGUIDs of approved enterprise keys (YubiKey 5 series, Feitian ePass, Token2 PIN+ — get the AAGUIDs from the vendor)
5. Click **Save**.

!!! info "AAGUID allow-list is mandatory for FSI"
    Allowing any FIDO2 key (no allow-list) accepts consumer-grade keys that may not meet your firm's HSM or attestation expectations. The AAGUID allow-list is the only gate between your tenant and a $20 unattested key bought online. Maintain the list in a versioned configuration repo and review it quarterly.

### 2.3 Enable Passkeys (Microsoft Authenticator)

A **passkey** stored in the Microsoft Authenticator app is a phishing-resistant authenticator that satisfies the same CA requirement as a hardware FIDO2 key. It is appropriate for end-users and lower-risk admin scenarios; **device-bound hardware FIDO2 keys remain the recommendation for top-tier privileged roles** (Entra Global Admin, Authentication Policy Admin).

1. In the methods list, click **Passkey (FIDO2)**.
2. Toggle **Enable** to **On**.
3. Under **Target**, select **All users**.
4. Under **Configure**:
   - **Allow self-service set up:** Yes
   - **Enforce attestation:** Yes
   - **Enforce key restrictions:** Yes — include the Microsoft Authenticator passkey AAGUID (`90a3ccdf-635c-4729-a248-9b709135078f` for iOS Authenticator; `de1e552d-db1d-4423-a619-566b625cdc84` for Android Authenticator — verify current AAGUIDs in Microsoft Learn before deployment).
5. Click **Save**.

### 2.4 Enable Windows Hello for Business

1. Click **Windows Hello for Business**.
2. Toggle **Enable** to **On**.
3. Target: **All users** (the Authentication Methods policy enables registration; the deployment of Windows Hello on the endpoint is governed by Intune / Group Policy and is out of scope for this playbook).
4. Click **Save**.

### 2.5 Configure Microsoft Authenticator (push + number match)

1. Click **Microsoft Authenticator**.
2. Toggle **Enable** to **On**.
3. Under **Configure**:
   - **Authentication mode:** **Any** (allows both push and passwordless sign-in)
   - **Require number matching for push notifications:** **Enabled** for **All users**
   - **Show application name in push and passwordless notifications:** **Enabled**
   - **Show geographic location in push and passwordless notifications:** **Enabled**
4. Click **Save**.

!!! info "Number matching has been mandatory since February 27, 2023"
    Microsoft made number matching the default for all Authenticator push notifications in February 2023. The toggle in this blade lets you confirm enforcement and lock additional context (app name, location). It does not need to be re-enabled, but the setting should be auditable.

### 2.6 Deprecate SMS and voice for privileged roles

SMS and voice-call OTP are **not phishing-resistant**. They satisfy NIST AAL2 only when no out-of-band restricted channel (RESTRICTED_USE) condition applies, and they are explicitly disrecommended for privileged accounts under CISA, NIST SP 800-63B-4 (Initial Public Draft, August 2024 / second draft 2025), and NYDFS Class A guidance.

The recommended Entra pattern is **not** to disable SMS / voice tenant-wide (which would lock out users still mid-migration), but to **exclude privileged-role groups from SMS / voice targets** while leaving them available for general user fallback.

1. In the methods list, click **SMS**.
2. Toggle **Enable** to **On** (or leave on if already enabled).
3. Under **Target**, click **Add groups**, select **All users**, then click **Exclude** and add the group **`Privileged-Role-Holders`** (a security group that contains every PIM-eligible privileged-role holder; create this group in `Identity → Groups → All groups → New group` if it does not exist).
4. Repeat for **Voice call**.

!!! warning "Group membership must stay synchronized with PIM eligibility"
    The `Privileged-Role-Holders` group is the linchpin of this exclusion. If a new user is granted Entra Global Admin eligibility but is not added to the group, they retain SMS as a valid authenticator and the phishing-resistance posture is silently broken. Automate group membership via the PowerShell job in [`./powershell-setup.md`](./powershell-setup.md) section "Sync PIM eligibility to security group" and run it on a 1-hour schedule. The verification test is in [`./verification-testing.md`](./verification-testing.md) test case VT-04.

### 2.7 Configure the registration campaign

The registration campaign nudges users with weaker authenticators to register a stronger one (specifically Microsoft Authenticator) at sign-in.

1. `https://entra.microsoft.com → Protection → Authentication methods → Registration campaign`.
2. Set **State** to **Microsoft managed** (recommended) or **Enabled**.
3. Set **Days allowed to snooze** to **0** for the privileged-role group (forced registration) and **14** for general users.
4. Click **Save**.

### 2.8 Propagation note

Authentication Methods policy changes can take **up to 24 hours** to fully propagate across all Microsoft authentication endpoints. Document the change time in the CAB ticket and do **not** rely on a strong method in a CA policy until the soak window described in §13 has elapsed.

---

## 3. Authentication Strengths — create the "Phishing-Resistant MFA" strength

An **Authentication Strength** is a named, reusable bundle of accepted authentication method combinations that you reference from a CA grant control. Microsoft ships three built-in strengths (`Multifactor authentication`, `Passwordless MFA`, `Phishing-resistant MFA`). Most FSI organizations define a **custom** strength in addition, to express their AAGUID allow-list and to forbid combinations that the built-in strength permits but that the firm's WSP does not.

### 3.1 Inspect the built-in strengths

1. `https://entra.microsoft.com → Protection → Conditional Access → Authentication strengths`.
2. The default tab **Built-in** lists the three Microsoft strengths. Click **Phishing-resistant MFA** and review the accepted combinations:
   - Windows Hello for Business
   - Passkey (FIDO2)
   - FIDO2 security key
   - Certificate-based authentication (multi-factor)

The built-in **Phishing-resistant MFA** strength is acceptable for most uses. Skip §3.2 and §3.3 if your firm has no AAGUID-restriction or method-exclusion requirement.

### 3.2 Create a custom "FSI Phishing-Resistant MFA" strength

1. On the Authentication strengths blade, click the **Custom authentication strengths** tab → **+ New authentication strength**.
2. **Name:** `FSI Phishing-Resistant MFA`
3. **Description:** `AAL3-class authenticator. AAGUID-restricted to enterprise-issued FIDO2 keys (YubiKey 5, Feitian ePass) and Authenticator passkeys. Required for privileged roles, agent makers in Z3, and Agent 365 Admin Center access. Owner: CISO. Cross-ref: Control 1.11.`
4. **Authentication method combinations:** check
   - **FIDO2 security key**
   - **Passkey (FIDO2)** (Microsoft Authenticator)
   - **Windows Hello for Business**
5. Click **Next**.
6. On the **FIDO2 security key** advanced settings page, select **Allow specific keys** and paste the AAGUIDs from §2.2.
7. On the **Passkey (FIDO2)** advanced settings page, select **Allow specific keys** and paste the Authenticator passkey AAGUIDs from §2.3.
8. Click **Review + Create**, then **Create**.

### 3.3 Confirm the strength is selectable from a CA policy

1. `https://entra.microsoft.com → Protection → Conditional Access → Policies → + New policy`.
2. Under **Grant**, click **Grant access** and check **Require authentication strength**.
3. Confirm the **`FSI Phishing-Resistant MFA`** entry appears in the dropdown next to the three built-in strengths.
4. Click **Cancel** (do not save the empty test policy).

---

## 4. Named Locations — corporate IP ranges and country allow-list

Named locations are reusable IP and country expressions referenced from CA conditions. You will need at least three:

| Named location | Type | Purpose |

| `Corporate IP Ranges - Trusted` | IPv4/IPv6 CIDR, **Mark as trusted** | Office egress IPs; backbone for Policy B |
| `Permitted Countries - Operations` | Country | Country allow-list for human users (US, plus contracted offshore countries) |
| `Workload Identity Permitted IPs` | IPv4/IPv6 CIDR, **Do not** mark as trusted | Egress IPs from your Azure / on-prem services that host agents; backbone for Policy C |

### 4.1 Create the trusted corporate IP location

1. `https://entra.microsoft.com → Protection → Conditional Access → Named locations → + IP ranges location`.
2. **Name:** `Corporate IP Ranges - Trusted`
3. Add each office egress CIDR (`/32` for single IPs is acceptable; `/24` or wider preferred for branch ranges).
4. Check **Mark as trusted location**.
5. Click **Create**.

### 4.2 Create the permitted countries location

1. **+ Countries location**.
2. **Name:** `Permitted Countries - Operations`
3. **Determine location by:** **IP address** (the default; **Authenticator GPS** is available but should only be used for high-assurance scenarios because it relies on the user having Authenticator with location enabled).
4. Select the country list. Most US FSI organizations include **United States** plus a small number of explicitly contracted offshore-development countries (India, Philippines, Ireland, etc.).
5. Click **Create**.

### 4.3 Create the workload identity permitted IPs location

1. **+ IP ranges location**.
2. **Name:** `Workload Identity Permitted IPs`
3. Add the egress IPs of (a) your Azure subscriptions hosting Copilot Studio bot endpoints and connected services, (b) your on-premises ExpressRoute / hybrid services that host agent code, and (c) any approved third-party SaaS that calls Microsoft Graph or Dataverse on behalf of an agent.
4. **Do not** check Mark as trusted (workload identities should not benefit from "trusted" location bypasses that may be added to other policies).
5. Click **Create**.

!!! info "IPv6 considered"
    Microsoft Graph and Dataverse increasingly accept IPv6 client connections. If your egress is dual-stack, include IPv6 CIDRs alongside IPv4. Missing IPv6 ranges produces intermittent CA-WID denials that are very hard to diagnose. See [`./troubleshooting.md`](./troubleshooting.md) issue T-12.

---

## 5. Policy A — Phishing-resistant MFA for all privileged roles

This policy forces **AAL3-class authentication** at every sign-in (and at PIM activation) for any user holding a privileged Entra role, and for any user activating a PIM-eligible role. It is the foundation of NYDFS Class A §500.12 alignment for FSI.

### 5.1 Create Policy A in Report-only

1. `https://entra.microsoft.com → Protection → Conditional Access → Policies → + New policy`.
2. **Name:** `CA-001 — All users — require phishing-resistant MFA for privileged roles`
3. **Assignments → Users**:
   - **Include:** **Directory roles** — select every privileged role:
     - Entra Global Admin
     - Privileged Role Admin
     - Privileged Authentication Admin
     - Conditional Access Admin
     - Authentication Policy Admin
     - Authentication Admin
     - Security Admin
     - Exchange Admin
     - SharePoint Admin
     - Teams Admin
     - Power Platform Admin
     - Application Admin
     - Cloud Application Admin
     - User Admin
     - Helpdesk Admin
     - Compliance Admin
     - Compliance Data Admin
     - Information Protection Admin
     - **AI Administrator** (Microsoft built-in role added 2025)
     - Intune Admin
     - Hybrid Identity Admin
   - **Exclude:** the **`Break-Glass-Accounts`** group (you create this in §12) and any **service account** group that is governed under Policy C instead.
4. **Target resources → Cloud apps**: **All cloud apps**.
5. **Conditions**: leave at default (no client app, device platform, or location filters — the policy must apply everywhere).
6. **Grant → Grant access**:
   - Check **Require authentication strength** → select **`FSI Phishing-Resistant MFA`** (or built-in **Phishing-resistant MFA** if you skipped §3.2).
   - Check **Require device to be marked as compliant** *(optional — enable only if your privileged-role holders all have managed devices; for mixed BYOD environments, omit and lean on §6)*.
   - **For multiple controls:** **Require all the selected controls**.
7. **Session**: leave default (CAE handled in Policy D).
8. **Enable policy:** **Report-only**.
9. Click **Create**.

### 5.2 Validate Report-only impact

After 24–48 hours of Report-only operation, browse to `Identity → Monitoring & health → Sign-in logs → Conditional Access` tab. Filter by `Conditional Access policy = CA-001` and `Result = Report-only: Failure`. Each failure represents a sign-in that **would have been blocked** if the policy were live. Investigate every failure:

- Was it a privileged-role holder using a non-phishing-resistant authenticator? Their account needs a passkey or hardware key registered (route them through §2.3 self-service setup).
- Was it a service account that should have been excluded? Add to the exclusion group.
- Was it a break-glass account that was accidentally not excluded? **Stop the rollout immediately** and fix the exclusion.

The decision criterion to flip Policy A from Report-only to On is documented in §13.

---

## 6. Policy B — Agent makers require compliant device + phishing-resistant MFA

This policy fences **Copilot Studio**, **Power Platform**, and **Microsoft 365 Copilot agent-authoring surfaces** to **(a)** users on **Intune-compliant devices** **(b)** authenticating with a **phishing-resistant** strength. It is the human-side complement to the workload-identity policy in §7.

### 6.1 Identify the cloud app targets

The relevant cloud apps as enumerated in the Entra cloud-app picker are:

| Cloud app (display name in Entra) | App ID | Role in agent authoring |

| **Power Apps** | `475226c6-020e-4fb2-8a90-7a972cbfc1d4` | Power Apps maker portal |
| **Power Automate** | `7df0a125-d3be-4c96-aa54-591f83ff541c` | Flow authoring |
| **Microsoft Power Platform** | `1c75d0a8-3cd3-4a38-a5b8-e1c8b9e3ae3f` *(verify in your tenant)* | PPAC and consolidated Power Platform admin actions |
| **Copilot Studio** | `38e57f90-7c72-44e9-95a1-04f2f2a3a1f9` *(verify in your tenant — Copilot Studio app ID has shifted as the product was renamed from Power Virtual Agents)* | Copilot Studio maker portal |
| **Common Data Service** *(Dataverse)* | `00000007-0000-0000-c000-000000000000` | Dataverse data plane that agents read/write |

!!! info "Verify app IDs in your tenant before saving the policy"
    The **friendly names** in the Entra cloud-app picker are stable; the **GUIDs** above may differ slightly between tenants depending on whether the app is enterprise-app-installed or first-party. To confirm a GUID, browse to `Identity → Applications → Enterprise applications → All applications`, search by name, and read the **Application ID** column. Copy the friendly names from the picker rather than typing GUIDs into the CA policy form.

### 6.2 Create Policy B in Report-only

1. **+ New policy**.
2. **Name:** `CA-002 — Agent makers — compliant device + phishing-resistant MFA for Copilot Studio / Power Platform`
3. **Assignments → Users**:
   - **Include:** the security group **`Agent-Makers-All`** (a group containing every user with maker entitlement; populate from the source-of-truth defined in [Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md)).
   - **Exclude:** **`Break-Glass-Accounts`**, plus any developer who has a documented exception for a legacy ALM workflow (review quarterly).
4. **Target resources → Cloud apps → Include → Select apps**: select the apps from the table in §6.1.
5. **Conditions**:
   - **Device platforms → Include → Any device** (default).
   - **Locations** — leave at default to apply globally (the goal is to fence makers regardless of network position; do not exempt Trusted IPs, because a maker on a kiosk in the trusted office is still a maker).
6. **Grant → Grant access**:
   - **Require authentication strength** → **`FSI Phishing-Resistant MFA`**.
   - **Require device to be marked as compliant**.
   - **For multiple controls:** **Require all the selected controls**.
7. **Session**: leave default (Policy D will add session controls).
8. **Enable policy:** **Report-only**.
9. Click **Create**.

### 6.3 Add Microsoft Agent 365 Admin Center to the same fence

The Agent 365 Admin Center governance console — see [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — is reached through `https://admin.microsoft.com → Agent 365`. Access is gated by the **Microsoft 365 admin center** cloud app. To extend Policy B to cover this surface, **clone** Policy B as `CA-002b` and change the **Users** scope to:

- **Include:** **`AI-Administrators`** group (members of the AI Administrator role) and **`Agent-365-Approvers`** group.
- **Cloud apps:** **Microsoft 365 admin center** + **Microsoft Graph** *(do not target "All cloud apps" because that would impact every M365 admin sign-in unrelated to Agent 365)*.

This gives you two narrowly-scoped policies (`CA-002` for makers, `CA-002b` for governance-console operators) instead of one broad policy that is hard to roll back.

---

## 7. Policy C — Conditional Access for Workload Identities (agents and SPs)

This policy is the **agent-identity** boundary. It targets **service principals** (including the synthetic service principals that back Entra Agent ID registrations) and applies **location and risk** conditions. **There is no MFA grant control for workload identities** — workload identities cannot present a second factor to a human-style challenge. The grant control is **block** based on context.

### 7.1 Confirm the Workload Identities Premium SKU

Before creating the policy, §0.2: each service principal you intend to scope must have a **Microsoft Entra Workload Identities Premium** license. To check assignments:

1. `https://entra.microsoft.com → Identity → Applications → Enterprise applications → All applications`.
2. Locate the service principal (filter by application type **Application** and search by name).
3. Open the SP, go to **Properties**, and look for **Workload Identities Premium licensed: Yes/No**.

If the field reads **No**, the policy will not enforce against this SP. Acquire the license SKU through `https://admin.microsoft.com → Billing → Purchase services` before continuing.

### 7.2 Create Policy C in Report-only

1. `https://entra.microsoft.com → Protection → Conditional Access → Policies → + New policy`.
2. **Name:** `CA-003 — Workload identities — block agent SPs from non-permitted IPs and high risk`
3. **Assignments → Users and workload identities**:
   - Switch the **Users and workload identities** dropdown to **Workload identities**.
   - **Include → Select service principals**: add **(a)** every service principal that backs a Copilot Studio agent published to Z3, **(b)** every Entra Agent ID registration in Z3 (see §9), **(c)** any third-party application that has Graph or Dataverse permissions consented at admin level and is invoked on behalf of an agent.
   - **Exclude:** Microsoft-first-party service principals required for tenant operations (do not include service principals owned by `Microsoft Services` or with publisher domain `microsoft.com` unless you have a specific reason).

4. **Target resources → Cloud apps → Include → All cloud apps**.
5. **Conditions**:
   - **Service principal risk (Preview)** — **Configure: Yes** — **Include risk levels**: **High**, **Medium** (review weekly; tune based on Identity Protection signal quality).
   - **Locations** — **Configure: Yes** — **Include: Any location**, **Exclude: `Workload Identity Permitted IPs`** (the named location from §4.3). The pattern is "block when **not** in the permitted IP set", expressed as include-all-locations-minus-exclude-permitted.
6. **Grant**: **Block access**. Workload identities receive a `Block` grant (no MFA option exists for SPs).
7. **Session**: not applicable for workload identities.
8. **Enable policy:** **Report-only**.
9. Click **Create**.

### 7.3 Validate Report-only impact for SPs

The Sign-in logs blade has a **separate tab** for service principal sign-ins.

1. `Identity → Monitoring & health → Sign-in logs`.
2. Click the **Service principal sign-ins** tab (next to **User sign-ins**).
3. Filter `Conditional Access = Report-only: Failure` and `Conditional Access policy = CA-003`.
4. Each row is a service principal sign-in that would have been blocked. For each, confirm:
   - Is the source IP one that **should** be in the permitted set? Add it to `Workload Identity Permitted IPs` (§4.3).
   - Is this an unexpected service principal (compromised credential, shadow integration)? Disable the SP and open an incident — see [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) for the analytic rule.

!!! warning "Don't apply CA-WID to managed identities you cannot test"
    A managed identity used by an Azure Function that posts to Microsoft Graph from a public Azure egress IP that you have not enumerated in §4.3 will be **blocked** the moment Policy C goes from Report-only to On. The 7-day soak window in §13 exists for exactly this reason. Plan to add IP ranges as you discover them and to extend the soak by another week if the Report-only failure rate has not stabilized.

---

## 8. Policy D — Session controls: CAE, sign-in frequency, Token Protection

The fourth policy adds **session-layer** controls. Unlike Policies A–C, Policy D does not block; it **shortens session lifetimes** and **subscribes the token to revocation events** so that if a credential or device posture changes mid-session, the session ends.

### 8.1 Continuous Access Evaluation (CAE)

CAE is **enabled by default** at tenant level for all CAE-aware Microsoft services (Exchange Online, SharePoint Online, Teams, Microsoft Graph). You verify it is on; you do not need to enable it per policy.

1. `https://entra.microsoft.com → Protection → Conditional Access → Policies → + New policy`.
2. **Name:** `CA-004 — Session controls — CAE, sign-in frequency, Token Protection (Z3 environments)`
3. **Assignments → Users**: include **`Agent-Makers-Z3`** (makers in Zone 3 environments) and **`Privileged-Role-Holders`**; exclude **`Break-Glass-Accounts`**.
4. **Target resources → Cloud apps → All cloud apps**.
5. **Session**:
   - Check **Customize continuous access evaluation** → **Strict enforcement** *(the strict mode revokes tokens within ~5 minutes of a critical event such as account disable, password change, or risky-user elevation; default mode allows up to 60 minutes)*.

### 8.2 Sign-in frequency — 4-hour reauth in Z3

Sign-in frequency forces an interactive reauthentication after the configured interval. For Z3 (Enterprise / regulated) environments, **4 hours** is the recommended FSI baseline; for Z2 (Team), **8 hours**; Z1 (Personal) inherits tenant default (typically 90 days for non-privileged users).

1. In the same Policy D form, under **Session**:
   - Check **Sign-in frequency** → **Periodic reauthentication** → **4 Hours**.

### 8.3 Persistent browser — Never persistent for makers

1. Check **Persistent browser session** → **Never persistent**.

This blocks "Stay signed in?" prompts in browser sessions on shared / unmanaged endpoints, ensuring the 4-hour reauth actually bites.

### 8.4 Token Protection (Preview) — Windows pilot

**Token Protection** binds a sign-in token to a specific Windows device's TPM, defeating token-replay attacks. It is in **Preview** as of April 2026, supports **Windows 10 / 11** (no macOS, no Linux, limited mobile), and applies only to **Exchange Online** and **SharePoint Online** at preview.

For a pilot, create a **separate** policy `CA-005` rather than co-mingling with Policy D, because the Token Protection scope is narrower than CA-004.

1. **+ New policy** → **Name:** `CA-005 — Token Protection (Preview) — Windows pilot for privileged users`.
2. **Users → Include:** `Privileged-Role-Holders-Pilot` (a 5–20 user pilot subgroup); **Exclude:** `Break-Glass-Accounts`.
3. **Cloud apps → Include:** **Office 365 Exchange Online** and **Office 365 SharePoint Online** *(only the apps Token Protection currently supports)*.
4. **Conditions → Device platforms → Include:** **Windows** only.
5. **Session → Require token protection for sign-in sessions (Preview):** **Enabled**.
6. **Enable policy:** **Report-only**.
7. Click **Create**.

!!! warning "Token Protection breaks unsupported clients silently"
    A user signing in from an unsupported platform (macOS, mobile, Linux) under a Token Protection-required policy will be **blocked**. Scope tightly during preview. Microsoft is expanding platform coverage; check Microsoft Learn before each promotion from pilot to general rollout.

---

## 9. Entra Agent ID — locating agent identities and assigning them to CA

**Entra Agent ID** is the directory-level identity for AI agents. The platform reached **General Availability in April 2026**; the licensing bundle that ships it as part of **Microsoft Agent 365** and **Microsoft 365 E7** became GA on **May 1, 2026**. Agent identities appear in **two** places in the Entra portal — and you need to know both.

### 9.1 Where agent identities appear

| Surface | What you see | When to use |

| `Identity → Applications → Enterprise applications → All applications` | Each agent appears as a service principal with **Application type = Agent** (a value introduced when Entra Agent ID first shipped) | When binding an agent to a CA-WID policy (§7), you select its SP from this list |
| `Identity → Identity governance → Agent ID` *(Frontier-gated; may not appear in your tenant)* | The agent registry — sponsor (human owner of record), custom security attributes (zone classification, risk tier), agent collection membership | When governing the **lifecycle** of agent identities — provisioning, sponsor handoff, deprovisioning. This surface is owned by [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) at the governance-console level and by Control 2.26 (where present) at the directory level |

### 9.2 Filter the Enterprise applications blade to agent identities

1. `Identity → Applications → Enterprise applications → All applications`.
2. Add a filter: **Application type** equals **Agent** (if the value does not appear in your filter dropdown, your tenant is not yet on the Agent ID rollout ring; Policy C still applies to ordinary service principals).
3. Optionally add **Created on or after [date]** to scope to recent agents.

### 9.3 Bind agent identities to Policy C

1. Open Policy C (`CA-003`) from §7.
2. Under **Assignments → Users and workload identities → Workload identities → Include → Select service principals**, add each agent identity from §9.2 that operates in **Zone 3**.
3. Confirm each added SP has the **Workload Identities Premium** license (§7.1) — the field is on the SP's Properties page.
4. Save the policy *(it remains in Report-only; promotion is governed by §13)*.

### 9.4 Cross-reference to the Agent 365 Admin Center

Once an agent identity is in scope of Policy C, the **Agent 365 Admin Center** governance dashboard will display the CA enforcement state for that agent. Cross-reference [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) for the operational read-out — Agent Registry → `[agent]` → **Identity & Access** tab shows linked CA policies, last successful sign-in, and last blocked sign-in.

!!! info "Entra Agent ID surfaces are still evolving post-GA"
    Although Entra Agent ID reached GA in April 2026, schema, attribute names, and blade locations continue to evolve as Microsoft expands the surface (especially the `Identity governance → Agent ID` registry view, which remains Frontier-gated in some tenants). Document the **portal version** you verified against (header **Last UI Verified** date) and after each Microsoft Wave release. Prefer the portal-level **Enterprise applications** view as the durable enforcement plane; treat undocumented Agent ID endpoints as preview surfaces and avoid scripting against them in production.

---

## 10. Privileged Identity Management — activation-time MFA for AI / privileged roles

PIM converts standing privileged-role assignments into **eligible** assignments that the user must **activate** for a time-bound window. By requiring **MFA on activation** with the **`FSI Phishing-Resistant MFA`** strength, every privileged action is gated by AAL3-class authentication at the moment of use, not just at sign-in.

### 10.1 Configure PIM role settings

For each role in the table below, configure **activation requires MFA** with the phishing-resistant strength.

| Role | Maximum activation duration | Requires MFA on activation | Justification required | Approval required | Notification recipients |

| Entra Global Admin | 2 hours | Yes — `FSI Phishing-Resistant MFA` | Yes (ticket #) | Yes — 2 approvers from `GA-Approvers` group | CISO, Compliance Officer |
| Power Platform Admin | 4 hours | Yes — `FSI Phishing-Resistant MFA` | Yes | Yes — 1 approver | AI Administrator, Compliance Officer |
| Authentication Policy Admin | 2 hours | Yes — `FSI Phishing-Resistant MFA` | Yes | Yes — 1 approver | CISO |
| Compliance Admin | 4 hours | Yes — `FSI Phishing-Resistant MFA` | Yes | No | Purview Compliance Admin lead |
| **AI Administrator** | 4 hours | Yes — `FSI Phishing-Resistant MFA` | Yes | Yes — 1 approver | AI Administrator lead, Compliance Officer |

Note the canonical short name is **AI Administrator** (Microsoft built-in role added in 2025), not "AI Admin" or "AI Governance Administrator".

### 10.2 Per-role configuration steps

For each row in the table:

1. `https://entra.microsoft.com → Identity governance → Privileged Identity Management → Microsoft Entra roles → Roles`.
2. Click the role name (e.g., **Entra Global Admin**).
3. Click **Settings** in the left rail.
4. Click **Edit**.
5. **Activation** tab:
   - **Activation maximum duration (hours):** as per table.
   - Check **On activation, require multifactor authentication**.
   - **Required authentication context:** if available in your tenant, select **`FSI Phishing-Resistant MFA`**. If your tenant only exposes the boolean MFA-required toggle (older PIM UI), enable it and rely on Policy A to enforce the strength at the underlying sign-in.
   - Check **Require justification on activation**.
   - Check **Require ticket information on activation**.
6. **Assignment** tab:
   - **Allow permanent eligible assignment:** Yes (eligibility is long-lived).
   - **Allow permanent active assignment:** **No** (force time-bound activation).
   - **Require multifactor authentication on active assignment:** Yes.
7. **Notification** tab: configure recipients per the table.
8. Click **Update**.

### 10.3 Move standing assignments to eligible

For each role, review **Assignments → Active assignments**. Any user with a permanent active assignment should be **converted** to **Eligible**:

1. Tick the user → **Make eligible**.
2. Set the eligibility to **Permanent eligible**.
3. The user must now activate via PIM each time they need the role.

!!! warning "Two-admin pattern for CA mutation"
    Conditional Access Admin should be configured with **approval required** (one approver from a separate group). This implements a two-admin / four-eyes pattern for any change to a CA policy — preventing an attacker who has compromised a single admin from creating an exclusion rule. Document this in the [Control 2.5 — Privileged Access Lifecycle](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) review cadence.

---

## 11. Sentinel Conditional Access Insights workbook

The Conditional Access Insights workbook visualizes policy impact, Report-only failures, and bypass patterns. Wire it to the Log Analytics workspace established in [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

### 11.1 Confirm SigninLogs are flowing to Log Analytics

1. `https://entra.microsoft.com → Identity → Monitoring & health → Diagnostic settings`.
2. Confirm a diagnostic setting exists that ships **SignInLogs**, **NonInteractiveUserSignInLogs**, **ServicePrincipalSignInLogs**, **ManagedIdentitySignInLogs**, and **AuditLogs** to the Log Analytics workspace defined in Control 3.9.
3. If absent, click **+ Add diagnostic setting** and configure all five log categories.

### 11.2 Open the Conditional Access Insights workbook

1. `https://security.microsoft.com → Microsoft Sentinel → Workbooks` *(if the Sentinel UI is not yet integrated into Defender in your tenant, navigate via `https://portal.azure.com → Microsoft Sentinel → [workspace] → Workbooks`)*.
2. Click the **Templates** tab.
3. Search for **Conditional Access Insights and Reporting**.
4. Click **Save** to instantiate, choosing the Control 3.9 workspace.
5. Click **View saved workbook**.

### 11.3 Pin daily / weekly cards to your governance dashboard

The workbook's most useful tiles for ongoing operations:

- **Sign-ins by Conditional Access Result** — daily trend; investigate any spike in `Failure` immediately.
- **Top Conditional Access Failures by User** — feeds the FINRA Notice 21-18 supervision narrative.
- **Workload Identity Sign-ins by Result** — separate from human sign-ins; pin alongside Control 3.6's orphaned-agent dashboard.
- **Report-only Mode Impact** — primary input to the §13 promotion decision.

### 11.4 Companion analytic rules

Sentinel ships several built-in analytic-rule templates that sit alongside this workbook. Enable at minimum:

- **Sign-in from unfamiliar location for Privileged Account**.
- **Service Principal sign-in failure spike**.
- **Conditional Access policy change** *(detects edits to CA policies — pair with the two-admin PIM pattern from §10.3)*.
- **Break-Glass account sign-in** *(see §12.4 for the bespoke rule).*

The analytic-rule configuration steps live in [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

---

## 12. Break-glass / emergency access accounts

Two cloud-only emergency accounts are required by the Microsoft baseline and by every FSI examiner-friendly architecture. They are the only safety net if a CA policy locks every named admin out of the tenant.

### 12.1 Create the two accounts

1. `https://entra.microsoft.com → Identity → Users → All users → + New user → Create new user`.
2. Account 1:
   - **User principal name:** `breakglass-01@<tenant>.onmicrosoft.com` (use the `.onmicrosoft.com` domain, **not** a federated custom domain — the federation IdP is itself a single point of failure).
   - **Display name:** `Break-Glass Account 01 — DO NOT USE`.
   - **Password:** Auto-generated; record in two physically separated safes (see §12.3).
   - **Usage location:** US (or your primary jurisdiction).
3. After creation, assign **Entra Global Admin** as a **permanent active** assignment (PIM activation must not be on the critical path for emergency use).
4. Repeat for `breakglass-02@<tenant>.onmicrosoft.com`.

### 12.2 Exclude break-glass accounts from every CA policy

1. Create a security group **`Break-Glass-Accounts`** containing both accounts (`Identity → Groups → All groups → + New group`).
2. For **every** CA policy you author (Policies A, B, C, D, plus any future ones), under **Assignments → Users → Exclude → Users and groups**, add the **`Break-Glass-Accounts`** group.
3. The Microsoft Managed Policy `Require multifactor authentication for admins` likewise needs the exclusion — open it (filter by `Source = Microsoft`) and confirm the exclusion.

### 12.3 Physical storage and split knowledge

- **Account 1 password** sealed in tamper-evident envelope, stored in CISO's office safe.
- **Account 2 password** sealed in tamper-evident envelope, stored in a second physically separated safe (corporate secondary office or Iron Mountain vault).
- Each FIDO2 hardware key (one per account) registered as the only authenticator and stored in the **opposite** safe from the password (so no single safe access yields a complete credential).
- Quarterly verification (calendar reminder) that the envelopes are intact; tamper triggers a full break-glass credential rotation.

### 12.4 Sentinel analytic rule for any sign-in

A Sentinel analytic rule must alert on **any** sign-in (success or failure) by a break-glass account. The KQL is established in [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md); summary form:

```kql
SigninLogs
| where UserPrincipalName in~ ("breakglass-01@<tenant>.onmicrosoft.com",
                                "breakglass-02@<tenant>.onmicrosoft.com")
| project TimeGenerated, UserPrincipalName, IPAddress, ResultType, AppDisplayName
```

The alert should page the CISO and at least one secondary on-call. A break-glass sign-in that is not pre-coordinated is a high-severity incident.

!!! warning "Break-glass is the only path back from a CA misconfiguration"
    Test the break-glass procedure **at least quarterly**. Sign in from a clean workstation, document the result, rotate the password, return it to the safe. An untested break-glass account is no break-glass account.

---

## 13. Report-only to Enforce rollout — the 7-day soak

Every policy authored in §§5–8 starts in **Report-only**. Promotion to **On** follows a documented soak period with explicit go/no-go criteria.

### 13.1 The 7-day window

| Day | Activity | Owner |

| 0 | Policy created in Report-only; CAB ticket updated | Conditional Access Admin |
| 1 | Verify Sign-in logs show the policy evaluating (`Conditional Access` tab populated) | Entra Security Admin |
| 2–6 | Daily review of `Report-only: Failure` and `Report-only: Success but interrupted` results in the Sign-in logs and the §11 workbook | Entra Security Admin |
| 7 | Go/no-go meeting with CISO, Compliance Officer, AI Administrator | CISO chairs |

### 13.2 Go criteria

Promote from Report-only to On **only if**:

1. Report-only failure rate over the prior 24 hours is **stable** (not increasing day-over-day).
2. Every Report-only failure has been triaged to one of three root causes:
   - **Legitimate user / SP needs to register a stronger authenticator or be added to a permitted IP** — fix forward, not exclude.
   - **Service account that should be governed by Policy C, not Policy A/B** — refactor scope.
   - **Stale / disabled identity that should not be signing in** — investigate as potential incident.
3. Break-glass accounts have been verified excluded (re-test by reading the policy JSON via `https://entra.microsoft.com → Conditional Access → Policy → JSON view` and grepping for the `Break-Glass-Accounts` group ID under `excludeGroups`).
4. CAB has approved the cutover date and time.

### 13.3 No-go criteria — extend the soak

Extend by another 7 days (no shortcut) if any of:

- Report-only failure rate is rising.
- A Report-only failure cannot be attributed to a root cause.
- A planned excluded SP is missing from the policy.
- A new agent or maker has been onboarded mid-soak (their sign-ins need at least 48 h of observation).

### 13.4 The flip

1. `https://entra.microsoft.com → Protection → Conditional Access → Policies → [policy name]`.
2. At the bottom, change **Enable policy** from **Report-only** to **On**.
3. Click **Save**.

4. Within 5 minutes, perform a **smoke test**:
   - From a test account in scope, sign in to a covered cloud app and confirm the expected behavior (MFA challenge, block, or grant as appropriate).
   - From a break-glass account on a clean workstation, sign in to confirm exclusion still functions (then sign out and rotate the credential).
   - Inspect the §11 workbook for the new "Sign-ins by Conditional Access Result" tile and confirm `Success` and `Failure` populate as expected (not `Report-only`).

5. Update the CAB ticket with go-live timestamp, evidence-pack screenshots, and the §15 evidence checklist.

---


## 15. Evidence pack and verification cross-references

Every promotion in §13 must produce evidence artifacts to the firm's compliance archive. The folder structure below mirrors the §13 cutover ticket.

### 15.1 Evidence pack folder structure

```
/compliance-archive/control-1.11/<YYYY-MM-DD-cutover>/
├── 00-cab-ticket.pdf
├── 01-pre-flight-license-validation.png             (§0.2)
├── 02-pim-eligible-assignments.csv                  (§0.1, exported via Get-AzureADMSPrivilegedRoleAssignment one-liner)
├── 03-auth-methods-policy-export.json               (§2 — exported from `https://entra.microsoft.com → Auth methods → ... → Export`)
├── 04-authentication-strength-FSI.json              (§3.2)
├── 05-named-locations.json                          (§4)
├── 06-policy-A-config.json                          (§5)
├── 07-policy-B-config.json                          (§6)
├── 08-policy-C-config.json                          (§7)
├── 09-policy-D-config.json                          (§8)
├── 10-pim-role-settings.csv                         (§10)
├── 11-sentinel-workbook-screenshot.png              (§11)
├── 12-breakglass-attestation-quarterly.pdf          (§12)
├── 13-reportonly-failure-triage-log.xlsx            (§13)
└── 99-cisco-sign-off.pdf
```

### 15.2 Verification cross-references

The portal walkthrough produces the **configuration** evidence. The companion playbooks produce the **operational** evidence:

- [`./powershell-setup.md`](./powershell-setup.md) — same configuration via Microsoft Graph PowerShell SDK; preferred for repeatable rebuild and DR scenarios. Covers the `Sync PIM eligibility to security group` automation referenced in §2.6.
- [`./verification-testing.md`](./verification-testing.md) — test cases VT-01 through VT-22 covering the Verification Criteria in the [Control 1.11 spec](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md). Run quarterly and after every CA policy change.
- [`./troubleshooting.md`](./troubleshooting.md) — issue catalog T-01 through T-25 keyed to the symptoms an admin sees in the Sign-in logs and CA Insights workbook.
- [`./conditional-access-agent-templates.md`](./conditional-access-agent-templates.md) — copy-paste-ready JSON templates for Policies A, B, C, D and the FSI Authentication Strength.

### 15.3 Cross-control evidence joins

The 1.11 evidence pack does not stand alone. For an examiner-ready posture, join it to:

| Joined control | Evidence joined |

| [Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | Maker-entitlement source-of-truth that populates `Agent-Makers-All` |
| [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | MRM register entry showing the agent identity and its MRM tier — drives whether Policy C applies |
| [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervisory review of CA policy changes (FINRA Rule 3110 supervision of WSP changes) |
| [Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | Environment classification (Z1/Z2/Z3) that drives Policy B and Policy C scoping |
| [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Agent 365 dashboard view of per-agent CA enforcement state |
| [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Orphaned-agent SP cleanup that maintains the cleanliness of Policy C's scope |
| [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Log Analytics workspace + analytic rules + the KQL queries in §11 and §12 |

---

## Anti-pattern catalog (top 10)

The patterns below have caused real outages in FSI tenants. Avoid them.

| # | Anti-pattern | Why it fails | Correct pattern |

| AP-01 | Targeting "All cloud apps" with `Require compliant device` for all users | Mobile device sign-ins to Outlook on personal phones are blocked tenant-wide | Scope by group (`Agent-Makers-All`) and cloud app (Power Platform suite) — Policy B |
| AP-02 | Disabling SMS / voice tenant-wide before users have registered alternatives | Locks out users mid-migration | Exclude `Privileged-Role-Holders` from SMS targets; leave SMS available as fallback for general users until passkey rollout completes — §2.6 |
| AP-03 | Skipping Report-only and going straight to On | First incident is always tenant-wide | Mandatory 7-day Report-only soak — §13 |
| AP-04 | Forgetting to exclude break-glass accounts | First tenant lockout produces an "open Microsoft support ticket" stress event | Always exclude `Break-Glass-Accounts` group on every policy — §12 |
| AP-05 | Applying CA-WID to a service principal without the Workload Identities Premium SKU | Policy fails open silently; no enforcement | Verify SKU before promotion — §0.2, §7.1 |
| AP-06 | Using "Block access" with no `Require MFA` fallback for human users | Block is final; user has no path forward | Use `Grant access → Require authentication strength` for humans; `Block access` is correct only for workload identities |
| AP-07 | Combining Token Protection requirement with macOS / mobile users in scope | Unsupported platform → blocked | Scope Token Protection to Windows-only via Device Platform condition — §8.4 |
| AP-08 | Standing Entra Global Admin assignments | Compromise → tenant takeover | PIM eligible-only with phishing-resistant MFA on activation — §10 |
| AP-09 | Allowing any FIDO2 key (no AAGUID restriction) | Consumer-grade key with weak attestation accepted | AAGUID allow-list — §2.2 |
| AP-10 | Documenting product capability gaps as "policy exceptions" instead of "product unavailability" | Examiner reads exception register as firm-internal deviation | Document as product unavailability with Microsoft Learn link |

---

## Summary

You have configured the four foundational Conditional Access policies for AI agents in an FSI Microsoft 365 tenant: **Policy A** for privileged-role phishing-resistant MFA, **Policy B** for agent-maker compliant-device + phishing-resistant MFA, **Policy C** for workload-identity location and risk fencing, and **Policy D** (plus pilot **Policy E** / `CA-005`) for session-layer controls including CAE, sign-in frequency, and Token Protection. You have promoted them through a 7-day Report-only soak, wired the Sentinel CA Insights workbook to the Control 3.9 workspace, and confirmed the break-glass posture.

These configurations **support compliance with** NYDFS §500.12, FFIEC authentication guidance, SEC Reg S-P, FINRA Notice 21-18, NIST SP 800-63B AAL3, and CISA Zero Trust identity-pillar expectations. They do **not** by themselves satisfy any obligation; the joined controls in §15.3 carry the rest of the load.

Continue with [`./verification-testing.md`](./verification-testing.md) to run the Verification Criteria checklist, [`./powershell-setup.md`](./powershell-setup.md) to produce the same configuration via code for DR rebuild, and [`./troubleshooting.md`](./troubleshooting.md) when sign-in failures need triage.

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
