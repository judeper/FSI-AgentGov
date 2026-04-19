# Portal Walkthrough: Control 2.15 — Environment Routing and Auto-Provisioning

**Last Updated:** April 2026
**Portal:** Power Platform Admin Center (PPAC)
**Estimated Time:** 45–90 minutes (excluding security group readiness)

> **What this playbook configures.** Tenant-level **environment routing** so that makers visiting Copilot Studio, Power Apps, or Power Automate are auto-provisioned into a personal Managed developer environment inside an admin-defined environment group. Routing rules live at **Tenant settings → Environment routing**. Policy rules (sharing limits, AI features, ALM) live at **Environment groups → Rules** — these are different surfaces and serve different purposes.

---

## Prerequisites

- [ ] **Power Platform Admin** role assigned to the executing identity
- [ ] Microsoft Entra **security groups** that will scope routing already exist and are populated (e.g., `sg-fsi-wealth-makers`, `sg-fsi-compliance-makers`)
- [ ] Managed Environments licensing in place (routing requires Managed Environments — see Microsoft Learn: [Managed Environments overview](https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview))
- [ ] Default environment cleanup plan in place (Control 2.16) — routing does **not** revoke access to the default environment
- [ ] DLP policies (Control 1.4) attached to the target environment groups before turning routing on
- [ ] Change ticket open with documented routing rule order and approver sign-off

---

## Stage 1 — Create the Target Environment Group(s)

Routing assigns each routed personal dev environment to **one** environment group whose published rules govern it. Create the group(s) **before** turning routing on.

1. Sign in to the [Power Platform Admin Center](https://admin.powerplatform.microsoft.com) as a Power Platform Admin.
2. Select **Manage** → **Environment groups** → **+ New group**.
3. Name and describe the group. Suggested FSI naming:
   - `FSI-Personal-Dev-Default` — catch-all for "Everyone" rule
   - `FSI-Personal-Dev-Wealth` — for the Wealth Management LOB
   - `FSI-Personal-Dev-Compliance` — for the Compliance LOB
4. Open the new group → **Rules** tab → publish rules for each governance area:
   - **Sharing limits** — restrict sharing with security groups; cap individual shares
   - **AI features** — enable/disable Copilot, generative answers, AI Builder per LOB risk appetite
   - **Data retention / ALM** — solution-checker level, backup retention, preview features
5. Repeat for each LOB group. Confirm rules show **Published** (not Draft) — only published rules are inherited.

> **Constraint:** Environment groups can only contain Managed Environments. Newly auto-provisioned personal dev envs are Managed by default; existing envs you wish to add must be Managed first.

---

## Stage 2 — Turn On Environment Routing (Tenant Settings)

1. PPAC → **Manage** → **Tenant settings** → **Environment routing**.
2. In **Turn on environment routing for**, select the maker portals to govern:
   - [x] Power Apps
   - [x] Power Automate (cloud)
   - [x] Power Automate for desktop
   - [x] Copilot Studio

   *(Power Pages is not currently in scope for routing.)*
3. Decide scope:
   - **All makers** (new and existing) — recommended for Zone 2 / Zone 3
   - **New makers only** — acceptable for Zone 1 if existing makers' work in default must be preserved
4. Do **not** save yet — first create the routing rules in Stage 3.

---

## Stage 3 — Create Routing Rules

Each rule maps an audience (**Everyone** or a specific Microsoft Entra security group) to one target **environment group**. Rules are evaluated **top-down**; the first match wins.

1. In the **Environment routing** pane, select **+ New rule**.
2. **Name** — use a stable, descriptive name (e.g., `Route-Wealth-Makers`).
3. **Apply to** — choose:
   - **Everyone** — used only as the final catch-all, or as the sole rule in Zone 1.
   - **Specific security group** — pick the Entra group (e.g., `sg-fsi-wealth-makers`).
4. **Target environment group** — pick the group created in Stage 1.
5. **Save** the rule. It appears in the rule list.
6. Repeat for each LOB. Recommended order:

   | Priority | Audience | Target Group |
   |----------|----------|--------------|
   | 1 | `sg-fsi-wealth-makers` | `FSI-Personal-Dev-Wealth` |
   | 2 | `sg-fsi-compliance-makers` | `FSI-Personal-Dev-Compliance` |
   | 3 (last) | Everyone | `FSI-Personal-Dev-Default` |

7. Use the **arrow icons** beside each rule to reorder. Confirm the **Everyone** rule is last so LOB rules win for their members.
8. Select **Save** at the pane level to publish the rule set.

> **Rule scope is limited.** Microsoft Learn currently documents only **Everyone** and **Specific security group** as routing-rule audiences. There are no built-in domain, geographic, or attribute-based rule types — model any such requirement via security group membership upstream of Entra.

---

## Stage 4 — Validate End-to-End

1. Sign in to [Copilot Studio](https://copilotstudio.microsoft.com) as a member of `sg-fsi-wealth-makers` who has **no** existing developer environment.
2. The portal should auto-provision a new personal dev env inside `FSI-Personal-Dev-Wealth`. Confirm the environment name pattern (`<DisplayName>'s environment` by default).
3. In PPAC, open the new environment → **Settings** → confirm:
   - **Type:** Developer
   - **Managed Environments:** On
   - Sharing limit, AI feature flags, and other rules from the parent group are **applied** and **locked**.
4. Repeat for a Compliance maker and an unaffiliated maker (catch-all path).
5. Capture screenshots into `maintainers-local/tenant-evidence/2.15/` per `docs/images/2.15/EXPECTED.md`.

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|--------------------|
| Routing scope | Power Apps + Copilot Studio | + Power Automate (cloud) | + Power Automate for desktop |
| Maker scope | New makers only | All makers | All makers |
| Routing rules | Single "Everyone" → `Personal-Dev-Default` | Per-LOB security group rules + catch-all | Per-LOB rules + catch-all + formal change control |
| Rule documentation | Optional | Required, version-controlled | Required, supervisory-reviewed (FINRA 3110) |
| Default-env hygiene | Quarterly review | Monthly review + DLP block-list | Continuous; quarantined via DLP and access reviews |

---

## Important Behavior Notes

- **Routing sets the maker's landing environment; it does not restrict access.** Makers can still navigate to the default environment or any other environment they have access to. Pair routing with default-environment cleanup, DLP, and publisher restrictions (Control 1.1).
- **Existing developer environments take precedence.** If a maker already owns one or more developer environments, routing sends them to their existing environment (alphabetically first, if multiple), not a new one in the configured group.
- **No "deny" outcome.** If no rule matches and routing is on, makers are routed to the default environment. There is no "block" or "fail-closed" rule type.
- **Provisioning failures fall back to the default environment.** If the new dev env cannot be created, the maker silently lands in the default — monitor Power Platform admin activity logs for these events.

---

## Validation Checklist

- [ ] Each target environment group exists, is populated, and has its rules **Published** (not Draft)
- [ ] Routing is enabled in PPAC → Tenant settings → Environment routing for the agreed product portals
- [ ] Each LOB security group has a rule above the "Everyone" catch-all
- [ ] A test member of each LOB lands in the expected env group on first portal visit
- [ ] An unaffiliated test maker lands in the catch-all group
- [ ] Evidence (PPAC screenshots + `Get-TenantSettings` JSON + SHA-256 manifest) filed per Control 2.15 evidence convention

---

[Back to Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
