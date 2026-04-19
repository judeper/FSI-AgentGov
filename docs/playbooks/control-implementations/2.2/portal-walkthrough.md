# Portal Walkthrough: Control 2.2 — Environment Groups and Tier Classification

**Last Updated:** April 2026
**Portal:** Power Platform Admin Center (PPAC) — `https://admin.powerplatform.microsoft.com`
**Estimated Time:** 60–90 minutes initial setup; ~15 minutes per quarterly re-baseline

---

## Prerequisites

- [ ] **Power Platform Admin** role assigned (canonical role per `docs/reference/role-catalog.md`)
- [ ] **AI Administrator** sign-off on AI-related rule values (rules 3, 4, 5, 8, 9, 12)
- [ ] **Purview Compliance Admin** sign-off on retention (rule 6) and supervisory rules (1, 21)
- [ ] All target environments are **Managed Environments** ([Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md)). Default and trial environments cannot join groups.
- [ ] Governance zone classifications agreed and documented for each environment in scope
- [ ] DLP policies ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)) reviewed for compatibility with planned sharing rules
- [ ] Change ticket open for Zone 3 group changes

---

## Step 1 — Create environment groups

**Path:** PPAC → **Manage** (left rail) → **Environment groups** → **+ New group**

1. Enter a descriptive name following the FSI convention `FSI-Z{n}-{purpose}`:
    - `FSI-Z1-Personal` (Zone 1)
    - `FSI-Z2-{BU}` (Zone 2 per business unit, e.g. `FSI-Z2-WealthMgmt`)
    - `FSI-Z3-Enterprise-Prod` and `FSI-Z3-Enterprise-NonProd` (Zone 3)
2. Description **must** include: governance zone, allowed data sensitivity, change authority, and review cadence.
3. Click **Save**.

> Repeat for each zone group. Each environment can belong to only one group; groups cannot be nested.

---

## Step 2 — Add Managed Environments to a group

**Path:** PPAC → **Environment groups** → *select group* → **Environments** tab → **Add environments**

1. Filter to Managed Environments only (the picker hides non-managed environments).
2. Select the environments matching the group's zone classification.
3. Click **Add**. Newly added environments inherit any **published** rules within ~15 minutes.

> If an environment is missing from the picker, confirm Managed Environment is enabled in [Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md). Default and developer (personal) environments must first be promoted to Managed.

---

## Step 3 — Configure the 23 group rules

**Path:** PPAC → **Environment groups** → *select group* → **Rules** tab

For each rule listed in the [Control 2.2 zone matrix](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md#environment-group-rules-fsi-zone-matrix-april-2026-baseline), click the rule, set the value, and click **Save**.

### Rule-by-rule notes (high-impact rules)

| # | Rule | Notes for FSI |
|---|------|---------------|
| 1 | Accessing transcripts | Set to **Enable** in every zone — this is the primary capture for FINRA 4511 / SEC 17a-4 evidence of agent conversations. |
| 9 | External models | Set to **Disabled** in every zone unless an explicit model-risk-management approval is recorded under [Control 1.x model governance]. |
| 12 | Preview and experimental AI models | Set to **Disabled** in Zone 2 and Zone 3. Helps keep unvalidated models out of regulated workloads (OCC 2011-12 / SR 11-7). |
| 14, 15 | Sharing agents (Editor / Viewer) | Use the dialog to set **organization-wide cap = 0** for Zone 1 Editor sharing; cap Editor sharing in Zone 3 to force ALM. |
| 16, 17 | Sharing controls (canvas apps / solution flows) | Set to **Specific security groups only** with a small approver-managed group. |
| 19 | Solution checker enforcement | Zone 1 = **None**, Zone 2 = **Warn**, Zone 3 = **Block**. Block prevents import of solutions with known issues. |
| 20 | Unmanaged customizations | Zone 2 and Zone 3 = **Block**. Required for SOX-relevant change control. |

### Step 4 — Publish rules

**Saved ≠ enforced.** A rule only takes effect after publication.

1. After completing all rule edits, click **Publish rules** at the top of the Rules tab.
2. Wait up to 15 minutes for propagation. Each rule's **Status** column changes to **Published** with a timestamp.
3. Open one member environment and confirm the affected setting now shows as **Locked by environment group**.

---

## Step 5 — Document and capture evidence

For each group, capture the following to your evidence pack ([Control 3.x evidence retention]):

- [ ] Screenshot — group list with environment counts.
- [ ] Screenshot — each group's **Environments** tab.
- [ ] Screenshot — each group's **Rules** tab showing **Published** status and timestamp.
- [ ] CSV export — environment-to-group mapping (use the [PowerShell Setup](powershell-setup.md) script).
- [ ] Change ticket reference for Zone 3 changes.

---

## Settings that look like group rules but aren't

The following settings sometimes appear in environment-group conversations but are configured **elsewhere**. Do not assume they are inherited from a group:

| Setting | Where it's configured | Related control |
|---|---|---|
| Computer-Using Agents (CUA) | Copilot Studio admin / Microsoft 365 admin center | [Control 2.24](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) |
| Agent authentication mode | Per agent in Copilot Studio | Copilot Studio agent settings |
| IP firewall / IP cookie binding | Per Managed Environment | [Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md) |
| Customer Managed Key (CMK) | Per Managed Environment | [Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) |
| Cross-tenant inbound/outbound restrictions | PPAC → Environment → Settings → Privacy + Security | [Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md) |
| Channel publishing endpoints | Per agent in Copilot Studio | [Control 2.24](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) |

---

## Quarterly re-baseline checklist

Microsoft adds and graduates group rules periodically. Each quarter:

1. Open the [Microsoft Learn rules list](https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules).
2. Diff against the Control 2.2 zone matrix.
3. For any new rule, decide a Zone 1/2/3 value with AI Administrator + Purview Compliance Admin sign-off.
4. Update the matrix in `docs/controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md` and re-publish in PPAC.
5. Record the re-baseline date in the governance change log.

---

## Validation

Before closing the change ticket, confirm:

- [ ] Every Zone 3 (production) Managed Environment is a member of an `FSI-Z3-*` group.
- [ ] Each group's Rules tab shows **Published** for all 23 rules.
- [ ] Spot-check a member environment's setting (e.g., External models) shows **Locked by environment group**.
- [ ] Evidence pack uploaded with the change ticket.

---

*Updated: April 2026 | Version: v1.3.3*

[Back to Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
