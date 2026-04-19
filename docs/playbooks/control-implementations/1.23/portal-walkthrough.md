# Portal Walkthrough: Control 1.23 — Step-Up Authentication for AI Agent Operations

**Last Updated:** April 2026
**Portals:** Microsoft Entra Admin Center, Microsoft Entra Privileged Identity Management, Microsoft Defender XDR
**Estimated Time:** 4–6 hours (initial deployment); allow an additional 72-hour bake window in report-only mode before enforcement

---

## Prerequisites

- [ ] Entra Security Admin or Conditional Access Administrator role (for CA policies and authentication contexts)
- [ ] Authentication Policy Administrator role (for Authentication Strengths)
- [ ] Entra Privileged Role Admin role (for PIM role settings)
- [ ] Baseline Conditional Access posture from [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) deployed and enforcing
- [ ] At least one phishing-resistant authentication method enrolled per pilot user (FIDO2 security key, Windows Hello for Business, passkey in Microsoft Authenticator, or certificate-based authentication)
- [ ] Two break-glass accounts excluded from all step-up policies and stored per [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) break-glass guidance
- [ ] Microsoft Entra ID P2 licensing for users in scope (required for sign-in risk policies, user risk policies, and Privileged Identity Management)

!!! warning "Test in report-only mode first"
    All Conditional Access changes in this playbook must be created with **State = Report-only** and held in that state for a minimum of 72 hours. Promote to **On** only after reviewing sign-in diagnostics and confirming zero unintended block events.

---

## Step 1 — Create Authentication Contexts (`c1`–`c5`)

1. Open the [Microsoft Entra admin center](https://entra.microsoft.com).
2. Navigate to **Protection → Conditional Access → Authentication contexts**.
3. Select **+ New authentication context** and create the following five entries. **Publish to apps** must be checked or downstream services (Copilot Studio flows, Graph, SharePoint, Purview) cannot request the context.

| ID  | Display name             | Description                                | Publish to apps |
|-----|--------------------------|--------------------------------------------|-----------------|
| c1  | Financial Transaction    | Critical — 15-minute fresh auth required   | ✅              |
| c2  | Data Export              | High — 30-minute fresh auth required       | ✅              |
| c3  | External API Call        | High — 30-minute fresh auth required       | ✅              |
| c4  | Configuration Change     | High — 30-minute fresh auth required       | ✅              |
| c5  | Sensitive Query          | Medium — 60-minute fresh auth required     | ✅              |

> **Note:** Authentication context IDs are immutable once created. Reserve `c6`–`c25` for future use (for example, `c6` = Customer PII Read, `c7` = Trade Approval).

---

## Step 2 — Create the Phishing-Resistant Authentication Strength

1. Navigate to **Protection → Authentication methods → Authentication strengths**.
2. Confirm the built-in **Phishing-resistant MFA** strength exists (it includes FIDO2, Windows Hello for Business, and certificate-based authentication).
3. For Zone 3 critical operations, optionally create a custom strength named `FSI-Critical-Operations` that includes only:
    - FIDO2 security key
    - Windows Hello for Business
    - Certificate-based authentication (multi-factor)
    - Passkey (device-bound) in Microsoft Authenticator

   Use this custom strength on the `c1` (Financial Transaction) policy.

---

## Step 3 — Create One Conditional Access Policy per Context

For each authentication context, create a Conditional Access policy. Use the table below for the per-context settings.

1. Navigate to **Protection → Conditional Access → Policies → + New policy**.
2. Repeat once per row in the table:

| Policy name                       | Auth context | Authentication Strength            | Sign-in frequency | Device requirement (Zone 3)       |
|-----------------------------------|--------------|------------------------------------|-------------------|------------------------------------|
| `FSI-StepUp-c1-FinancialTxn`      | c1           | `FSI-Critical-Operations` (or built-in Phishing-resistant MFA) | 15 minutes        | Require compliant or hybrid-joined |
| `FSI-StepUp-c2-DataExport`        | c2           | Phishing-resistant MFA             | 30 minutes        | Require compliant or hybrid-joined |
| `FSI-StepUp-c3-ExternalAPI`       | c3           | Phishing-resistant MFA             | 30 minutes        | Require compliant or hybrid-joined |
| `FSI-StepUp-c4-ConfigChange`      | c4           | Phishing-resistant MFA             | 30 minutes        | Require compliant or hybrid-joined |
| `FSI-StepUp-c5-SensitiveQuery`    | c5           | Phishing-resistant MFA             | 60 minutes        | Require compliant or hybrid-joined |

For each policy:

1. **Users**: Include the production users in scope; **Exclude** the two break-glass accounts and any service-account exception group documented for this control.
2. **Target resources**: Switch the dropdown from *Cloud apps* to **Authentication context**, and select the matching context.
3. **Grant**: Select **Require authentication strength** and choose the strength from the table.
4. **Session**: Toggle **Sign-in frequency** to **Periodic reauthentication** with the value from the table. Set **Persistent browser session = Never persistent** for Zone 3.
5. **Enable policy**: Set to **Report-only** for the initial bake window.
6. Select **Create**.

---

## Step 4 — Stack Sign-in Risk and User Risk Policies

These policies fire even when no authentication context is invoked, providing defense-in-depth against compromised sessions used to drive an agent.

1. Navigate to **Protection → Conditional Access → Policies → + New policy**.
2. Create `FSI-StepUp-SignInRisk-Medium`:
    - **Conditions → Sign-in risk** = *Medium and above*
    - **Grant** = Require authentication strength → **Phishing-resistant MFA**
    - **Session → Sign-in frequency** = 1 hour
    - **Enable policy** = Report-only (then On after bake)
3. Create `FSI-StepUp-UserRisk-High`:
    - **Conditions → User risk** = *High*
    - **Grant** = Require authentication strength → **Phishing-resistant MFA** **and** Require password change
    - **Enable policy** = Report-only (then On after bake)

---

## Step 5 — Configure PIM for Agent Administrative Roles

For each role in the agent governance scope, tighten PIM activation settings so administrative actions on agents inherit a step-up posture.

1. Navigate to **Identity governance → Privileged Identity Management → Microsoft Entra roles → Roles**.
2. For each role in the table below, select the role → **Role settings → Edit**:

| Role (canonical name)                  | Approval required | Justification | MFA on activation                         | Max activation |
|----------------------------------------|-------------------|---------------|-------------------------------------------|----------------|
| Power Platform Admin                   | ✅                | ✅            | Authentication context **c4**             | 4 hours        |
| Environment Admin                      | ✅                | ✅            | Authentication context **c4**             | 4 hours        |
| AI Administrator                       | ✅                | ✅            | Authentication context **c4**             | 4 hours        |
| Purview Data Security AI Admin         | ✅                | ✅            | Authentication context **c4**             | 2 hours        |
| Entra Security Admin                   | ✅                | ✅            | Authentication context **c4**             | 2 hours        |

> **Note:** Select **On activation, require Conditional Access authentication context** and choose the context from the table. Do not skip approval for the Zone 3 agent governance roles.

---

## Step 6 — Map Sensitive Agent Actions to Authentication Contexts

Authentication contexts only enforce when an action requests them. Work with Power Platform Admins and AI Administrators to wire the contexts into downstream services.

| Surface                          | Where to configure                                                                 | Recommended context |
|----------------------------------|------------------------------------------------------------------------------------|---------------------|
| SharePoint Online sensitive sites| SharePoint admin center → Sites → Site → Authentication context (per-site mapping) | c2 or c5            |
| Purview sensitivity labels       | Purview portal → Information Protection → Labels → Auto-labeling settings          | c2                  |
| Copilot Studio sensitive flows   | Topic action → Run a Power Automate flow → flow requires CAE-aware connector       | c1, c2, c3 as appropriate |
| Custom connectors                | Connector definition → security → enforce auth context via Graph                   | c3                  |
| Power Automate cloud flows       | Trigger or action → Conditional Access enforcement (preview features)              | c1, c4              |

---

## Step 7 — Configure Monitoring and Alerts

1. Navigate to **Microsoft Entra → Monitoring → Diagnostic settings** and confirm sign-in logs (interactive, non-interactive, service principal) are streamed to Log Analytics or Sentinel.
2. In Sentinel or Defender XDR, create the following analytics rules (see [PowerShell Setup](powershell-setup.md) for KQL):
    - **Step-up failure spike** — `>5` failures within 10 minutes for the same user
    - **Conditional Access policy disabled** — alerts on any of the `FSI-StepUp-*` policies transitioning to `Off` or `Report-only` after enforcement
    - **PIM activation without step-up** — activation events where the requested authentication context was not satisfied

---

## Step 8 — Promote Policies from Report-Only to On

After the 72-hour bake window:

1. Open **Sign-in logs → Conditional Access → Report-only results** and confirm zero unintended *Failure* outcomes for in-scope users.
2. Edit each `FSI-StepUp-*` policy → **Enable policy = On → Save**.
3. Notify the help desk and capture the change in the change advisory record per [Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md).

---

## Configuration by Governance Level

| Setting                | Baseline (Zone 1)            | Recommended (Zone 2)                       | Regulated (Zone 3)                                     |
|------------------------|------------------------------|--------------------------------------------|--------------------------------------------------------|
| Step-up required       | Not required                 | Data export, external API, config change   | All sensitive actions (`c1`–`c5`)                      |
| Baseline session       | 8 hours                      | 4 hours                                    | 1 hour                                                 |
| Fresh auth (`c1`)      | n/a                          | 30 minutes                                 | 15 minutes                                             |
| Authentication Strength| Standard MFA                 | Phishing-resistant MFA (preferred)         | Phishing-resistant MFA required                        |
| Device                 | Any                          | Compliant preferred                        | Compliant or hybrid-joined required                    |
| PIM                    | Optional                     | Recommended for Power Platform Admin       | Required for all agent governance roles                |
| Risk policies          | Sign-in risk: medium → MFA   | Sign-in risk + user risk policies enabled  | Sign-in risk + user risk policies enabled              |

---

## Validation

After completing these steps, verify:

- [ ] All five authentication contexts exist and show **Published to apps = Yes**
- [ ] All five `FSI-StepUp-*` Conditional Access policies are in **On** state
- [ ] `FSI-StepUp-SignInRisk-Medium` and `FSI-StepUp-UserRisk-High` are in **On** state
- [ ] PIM role settings for the five agent governance roles require approval, justification, MFA, and bind to context `c4`
- [ ] Sign-in logs show authentication context being requested by at least one downstream service
- [ ] Two break-glass accounts are excluded from every `FSI-StepUp-*` policy and from sign-in risk and user risk policies
- [ ] Sentinel or Defender XDR analytics rules for step-up failure and CA policy state changes are enabled

---

[Back to Control 1.23](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
