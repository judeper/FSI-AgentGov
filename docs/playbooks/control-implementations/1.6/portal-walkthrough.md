# Control 1.6 — Portal Walkthrough: Microsoft Purview DSPM for AI

**Control:** [1.6 Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)
**Audience:** M365 administrator (US financial services)
**Last UI Verified:** May 2026
**Cloud coverage:** Commercial · GCC · GCC High · DoD (see sovereign cloud table below)

---

## Sovereign cloud URLs and feature parity

| Cloud | Portal URL | DSPM for AI (classic) | Unified DSPM | IRM-backed templates | Adaptive Protection |
|---|---|---|---|---|---|
| Commercial | `https://purview.microsoft.com` | GA | GA (May 2026, MC1191257) | GA | GA |
| GCC | `https://purview.microsoft.com` | GA | GA (May 2026, commercial-first) | GA | GA |
| GCC High | `https://purview.microsoft.us` | GA (May 2025) | Not announced as of May 2026 | Limited (verify per workload) | Not at parity |
| DoD | `https://purview.microsoft.us` (DoD instance) | GA (May 2025) | Not announced as of May 2026 | Limited (verify per workload) | Not at parity |

> Verify your tenant's cloud before relying on the new unified DSPM. Insider Risk Management is not at parity in US Government clouds — IRM-backed one-click templates may be unavailable. Partner solutions for non-Microsoft data sources and the Data Security Posture Agent remain in preview even in Commercial / GCC.

---

## Prerequisites & licensing matrix

| Capability | Required entitlement / configuration |
|---|---|
| Visibility of M365 Copilot interactions | **Microsoft 365 Copilot** per-user license; Microsoft 365 E5 / E5 Compliance / Microsoft Purview Suite per monitored user |
| Coverage of non-Microsoft AI apps (ChatGPT Enterprise, Gemini, Foundry, Other) | **Purview pay-as-you-go (PAYG) billing** linked to an Azure subscription |
| Long-term `CopilotInteraction` retention (>180 days) | **Audit (Premium)** + retention policy — see Control 1.7 |
| Endpoint AI signals | **Defender for Endpoint** *or* **standalone Purview device onboarding** |
| Edge AI/DLP signal capture | **Microsoft Edge configuration policy** (NOT browser extension) |
| Third-party AI (Chrome/Firefox, Windows-only) | **Microsoft Purview browser extension** |
| Entra-registered AI apps / Foundry | **Microsoft Purview SDK** integration |

## Roles required per Get Started step

| Get Started step | Role group(s) that can complete |
|---|---|
| Activate Audit | Microsoft Exchange Organization Management *or* Exchange Compliance Management *or* Records Management — **NOT** Purview Compliance Admin alone |
| Install browser extension / configure Edge | Endpoint admin (Intune) + Compliance Admin |
| Onboard devices | Defender for Endpoint admin + Compliance Admin |
| Extend your insights | **Insider Risk Management** role group (for IRM-backed templates) + Compliance Admin |
| Create one-click policies (DSPM Policies pane) | Per-template — see control doc Roles & Responsibilities table |

> **Least privilege:** Avoid Global Admin where the workflow is achievable with Compliance Admin or a workload-specific role group. Tenant-restricted (administrative-unit-scoped) admins **cannot** create DSPM/DLP/IRM one-click policies as of April 2026.

---

## Step-by-step walkthrough

### Step 1 — Open DSPM for AI (classic)

1. Sign in to your tenant cloud's Purview URL (see sovereign cloud table)
2. **Solutions** > **DSPM for AI (classic)**
3. Confirm the **Overview** page loads (this gates further role-related troubleshooting)

### Step 2 — Complete Get Started · Activate Audit

> Audit ingestion has been **on by default** in all new tenants since 2023. Detect first; only mutate if disabled. Verify state from **Exchange Online PowerShell** (`Get-AdminAuditLogConfig.UnifiedAuditLogIngestionEnabled`) — the value from Security & Compliance PowerShell (IPPS) is unreliable.

1. Open Get Started > Step 1 (Activate Audit)
2. If marked complete, capture screenshot for evidence and continue
3. If incomplete, hand off to a holder of an Exchange role group (see table above)
4. Cross-reference Control 1.7 portal walkthrough for the audit baseline

### Step 3 — Get Started · Install browser support

- **Edge:** push the **Edge configuration policy** via Intune (NOT the browser extension). Document policy ID + scope.
- **Chrome / Firefox (Windows only):** push the **Microsoft Purview browser extension** via Intune
- Capture per-device coverage report; sites or users without coverage will silently miss third-party AI events (silent-zero-row trap)

### Step 4 — Get Started · Onboard devices

- Confirm Defender for Endpoint or standalone onboarding state for in-scope devices
- Export device inventory; reconcile to monitored-user list

### Step 5 — Get Started · Extend your insights

- Requires **Insider Risk Management** role group
- Enables IRM-backed signals (Adaptive Protection, Risky AI usage)
- Not available at parity in GCC High / DoD — record the exception in your Zone-3 register

### Step 6 — Inventory & enable one-click policy templates

In **DSPM for AI > Policies**, the templates surfaced are *named workflows*, not generic solution categories. Pick by name from the list and confirm the underlying solution and role.

| Template (portal label) | Underlying solution | Role to create | Default scope |
|---|---|---|---|
| Detect risky AI usage in apps | Insider Risk Management | IRM role group | All users |
| Detect risky interactions in AI apps | Insider Risk Management (`Risky AI usage`) | IRM role group | All users |
| Detect sensitive info shared with AI via network | Endpoint DLP | DLP Compliance Admin | All managed devices |
| Secure interactions for Microsoft Copilot experiences | Collection / DLP for Copilot location | DLP Compliance Admin | M365 Copilot users |
| Capture interactions for Copilot experiences | Collection policy (content capture) | Compliance Admin | M365 Copilot users |
| Capture interactions for enterprise AI apps | Collection policy (content capture) | Compliance Admin | PAYG-billed AI apps |
| Discover and govern interactions with ChatGPT Enterprise AI | Collection + extended insights | Compliance Admin | ChatGPT Enterprise tenant |
| Secure data in Azure AI apps and agents | DLP / Purview SDK | DLP Compliance Admin | Azure AI / Foundry apps |

> **Content capture must be explicitly enabled** for any "Capture …" template — otherwise Activity Explorer rows appear but prompt/response content is not stored.

For each enabled template, record: name, mode (Enable / TestWithNotifications / TestWithoutNotifications / Disable / PendingDeletion), scope, exclusions, content-capture state, role used to create.

### Step 7 — Reports

In **DSPM for AI > Reports**, capture timestamped exports for:

- AI interactions over time (filter to in-scope user populations)
- Sensitive info detected in prompts and responses
- App / agent inventory

> Allow up to **24 hours** for new policies to surface in reports; allow up to **3 days** for initial analytics.

### Step 8 — Activity Explorer / AI activities (deterministic interaction test)

> Do **not** treat "table renders" as PASS. Generate a known interaction and assert the row exists.

1. Pick a named user with M365 Copilot license
2. At a recorded UTC timestamp, have them issue a known prompt (e.g., reference a labeled document)
3. Wait the documented window (24 h baseline)
4. Open **DSPM for AI > Activity explorer** or, in unified DSPM, **Discover > Activity explorer > AI activities**; then filter by user + activity type + UTC window
5. Assert event count ≥ 1 with matching user / app / activity
6. To view prompt/response content, the reviewer must hold **Purview Data Security AI Content Viewer**

### Step 9 — Data risk assessments

1. Confirm the **Default Weekly Assessment** is running (top 100 SharePoint sites by usage)
2. For Zone 3 sites outside the top 100, queue **Custom Site Assessments** in a CAB-tracked register
3. Initial results display: allow up to 4 days; refresh after a run: allow at least 48 hours
4. Walk the four tabs: Overview · Identify · Protect · Monitor
5. Capture Protect-tab oversharing list with site, sharing scope, sensitivity-label coverage, and remediation owner

### Step 10 — Apps and agents inventory

In **Apps and agents**, export the inventory and reconcile to your CMDB / agent register (Control 1.4 / Control 2.16). Untagged or unknown apps are an N3.4 default-exclusion symptom — investigate before signing off.

---

## Unified DSPM — generally available callout

The new unified **DSPM** experience consolidating DSPM and DSPM for AI reached general availability in May 2026 (Commercial / GCC) per **MC1191257**. Specific UI affordances continue to evolve; verify against current Microsoft Learn (`data-security-posture-management-learn-about`) at each portal session, and **do not commit to specific widget names, dashboard digest schedules, or "Enhanced CSV" semantics** in your evidence binder until they appear on Learn. Partner solutions for non-Microsoft data sources and the Data Security Posture Agent remain in preview.

---

## Evidence pack

Use a consistent file naming convention:

```
Control-1.6_{TenantId}_{Cloud}_{ArtifactType}_{YYYYMMDD-HHmm-UTC}.{ext}
Control-1.6_{TenantId}_{Cloud}_{ArtifactType}_{YYYYMMDD-HHmm-UTC}.{ext}.sha256
```

| Artifact | Source | Format | Frequency |
|---|---|---|---|
| Get Started step status screenshots | DSPM for AI > Get Started | PNG | On change |
| Roles-by-step record | Internal tracker | JSON | On change |
| One-click policy inventory (template, mode, scope, exclusions, content capture, owner) | DSPM > Policies + Compliance portal | JSON + CSV | Weekly |
| Activity Explorer deterministic test result (user, prompt, UTC, event count) | Activity Explorer + tester log | CSV + log | Weekly (Zone 3) / Monthly (Zone 2) |
| Weekly Risk Assessment summary | Data risk assessments > export | PDF + CSV | Weekly |
| Custom assessment register (Zone 3 sites > top 100) | Internal tracker | CSV | Quarterly review |
| Adaptive Protection threshold + IRM policy snapshot | Insider Risk Management | JSON | On change |
| Tenant cloud + license entitlement snapshot | Graph `Get-MgSubscribedSku` + per-user `Get-MgUserLicenseDetail` | JSON | Monthly |

Store in immutable storage (Purview retention label, SharePoint hold, or WORM blob) aligned to Control 1.7 retention.

---

## Cross-references

- [Control 1.6 PowerShell Setup](powershell-setup.md)
- [Control 1.6 Verification & Testing](verification-testing.md)
- [Control 1.6 Troubleshooting](troubleshooting.md)
- [Control 1.7 Audit Logging](../1.7/portal-walkthrough.md) — durable evidence backbone for `CopilotInteraction`
- [Control 1.5 DLP and Sensitivity Labels](../1.5/portal-walkthrough.md) — labels feeding DSPM
- [Control 1.10 Communication Compliance](../1.10/portal-walkthrough.md) — overlap for unethical-behavior templates
- [Control 1.12 Insider Risk Detection](../1.12/portal-walkthrough.md) — IRM dependency for Adaptive Protection

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current (commercial); GCC High / DoD verified per cloud-availability table*
