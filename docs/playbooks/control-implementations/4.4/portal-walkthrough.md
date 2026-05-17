# Control 4.4: Guest and External User Access Controls — Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 4.4](../../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md). It is written for M365 administrators in US financial services organizations and assumes the framework's three-zone model (Personal / Team / Enterprise).

!!! warning "Sequence matters"
    Tenant-level sharing always sets the **upper bound** for site-level sharing. A site cannot be configured more permissively than the tenant. Always inventory current state, then configure tenant defaults, then tighten individual sites.

---

## Prerequisites

Before starting, confirm:

- **Role:** **SharePoint Admin** (canonical name) for tenant and site sharing settings. **Entra Global Admin** is required only for Conditional Access changes that target external users — coordinate with [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md).
- **License:** Microsoft 365 E3 or E5 (Data Access Governance reports require E5 or a SharePoint Advanced Management add-on; verify against your tenant license inventory).
- **Inventory:** A current site inventory tagged by zone (1/2/3) and a documented list of regulated sites used by AI agents as knowledge sources.
- **Change control:** A signed change ticket if your organization is subject to SOX 404 / OCC Bulletin 2026-13 (formerly OCC 2011-12). Sharing-policy changes are tenant-affecting and should follow your standard CAB process.

---

## Step 1 — Inventory current external sharing state

Capture a baseline snapshot before any change. This snapshot is the rollback record and the audit-evidence anchor for the change.

1. Open the [SharePoint Admin Center](https://admin.sharepoint.com).
2. Navigate to **Reports** > **Data access governance**.
3. Open **Sharing links** and **Sites shared with everyone** (or "Anyone links" depending on your tenant report names).
4. Export each report and save with a timestamp under your evidence path (e.g., `evidence/4.4/baseline-YYYYMMDD/`).
5. Cross-reference exported sites against your zone classification list. Any site flagged as **Zone 3 (Enterprise Managed)** that currently shows external sharing must appear on your remediation list.

---

## Step 2 — Configure organization-level sharing defaults

Tenant defaults define the maximum permissive sharing level any site can use. Set defaults to the most restrictive level acceptable for your overall posture, then relax per-site only where business need is documented.

1. Navigate to **Policies** > **Sharing**.
2. Set **External sharing** for SharePoint to one of:
   - **Existing guests** — recommended baseline for tenants with established partner relationships.
   - **Only people in your organization** — recommended for tenants where regulated content dominates and external collaboration uses a separate tenant or B2B Direct Connect.
3. Set **OneDrive external sharing** to a level equal to or more restrictive than SharePoint.
4. Under **File and folder links**, set the default sharing link type:
   - **Specific people** is the audit-friendly default; it requires named recipients and produces per-recipient audit events.
   - **Only people in your organization** is acceptable where external sharing is fully disabled.
5. Set the default link permission to **View** (not **Edit**) for regulated tenants.
6. Save and capture a screenshot to evidence storage.

---

## Step 3 — Enable guest access expiration

Automatic expiration is the primary backstop against orphaned guest access — a recurring finding in FSI audits.

1. Still under **Policies** > **Sharing**, locate **Guest access to a site or OneDrive will expire automatically after this many days**.
2. Enable the toggle and set the value per zone:

| Zone | Expiration | Rationale |
|------|-----------|-----------|
| Zone 1 (Personal) | 90 days | Lower-risk content; balances control with usability |
| Zone 2 (Team) | 30 days | Shared agents amplify exposure; tighter expiration limits dwell time |
| Zone 3 (Enterprise) | External sharing disabled | Expiration not applicable; sharing is blocked at the site |

3. Set **Anyone link** expiration to **30 days maximum** if Anyone links are permitted anywhere in the tenant. For most regulated FSI tenants, Anyone links should be disabled outright.
4. Save and screenshot.

!!! note "Expiration applies to new and renewed grants"
    Enabling expiration does not retroactively add an expiry to guests who already have access. Existing guests must be re-invited (or accept a new sharing event) for the expiration to take effect. Use the PowerShell playbook to enumerate and remediate pre-existing grants.

---

## Step 4 — Configure domain restrictions (optional, recommended for Zone 2/3)

Domain allow-lists or block-lists narrow the population of external recipients to approved partners. This supports FINRA 3110 supervisory review of external communications.

1. Under **Policies** > **Sharing** > **More external sharing settings**, expand **Limit external sharing by domain**.
2. Choose:
   - **Allow only specific domains** — preferred for Zone 2 and Zone 3. Add approved partner, regulator, and auditor domains.
   - **Block specific domains** — use only as a complement to allow-listing or for known high-risk domains.
3. Document the domain list in your sharing-policy procedure with a business owner per domain and a planned review cadence (annual minimum, quarterly recommended).
4. Save and screenshot.

---

## Step 5 — Configure site-level sharing per zone

After tenant defaults are set, tighten individual sites that store AI agent knowledge sources or regulated content.

### Zone 3 — Enterprise Managed (regulated content)

1. Navigate to **Sites** > **Active sites**.
2. Filter or search for sites flagged Zone 3 in your inventory.
3. Select a site, open the **Settings** tab on the right panel, and set **External sharing** to **Only people in your organization**.
4. Repeat for every Zone 3 site. Use the PowerShell bulk script for tenants with more than ~25 Zone 3 sites.

### Zone 2 — Team Collaboration

1. Set **External sharing** to **Existing guests** (no new external invitations from the site).
2. Confirm the site has an assigned business owner and a documented approval trail for any current guest.

### Zone 1 — Personal Productivity

1. Default tenant setting typically suffices.
2. If a Zone 1 site is later reclassified to Zone 2 or 3, re-run this walkthrough for that site.

---

## Step 6 — Coordinate with Conditional Access for external users

Sharing settings control **whether** an external user can be granted access. Conditional Access controls the **conditions** under which they can use that access (MFA, device compliance, location, session lifetime).

1. Navigate to **Microsoft Entra admin center** > **Protection** > **Conditional Access** > **Policies**.
2. Confirm at least one policy targets **Guest or external users** with these controls (see [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) for full guidance):
   - **Require multifactor authentication**
   - **Require compliant device** (where the guest's home tenant supports cross-tenant device compliance) or **block legacy authentication**
   - **Sign-in frequency** capped at a defensible interval (commonly 8–24 hours for regulated tenants)
3. Document the policy ID and screenshot the policy summary view.

---

## Step 7 — Establish ongoing monitoring

Configuration alone is not evidence. FINRA 4511 and SEC 17a-4 require demonstrable, ongoing supervision.

1. Under **Reports** > **Data access governance**, schedule weekly review of:
   - **Sharing links** (volume and trend)
   - **Sites shared with everyone**
   - **Sites with sensitivity labels applied** (cross-check that labeled sites match your Zone 3 inventory)
2. Route findings into your existing supervisory review workflow (e.g., a Microsoft Teams channel monitored by Compliance, or a ServiceNow queue).
3. Quarterly: run an access certification review (see [Control 4.2](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md)) covering all guests on Zone 2 and Zone 3 sites.

---

## Governance Level Configuration Summary

### Baseline (Level 1)

| Setting | Value |
|---------|-------|
| Organization sharing | Existing guests or more restrictive |
| Sensitive sites | External sharing disabled |
| Default link type | Specific people |
| Monitoring | Monthly sharing report review |

### Recommended (Level 2–3)

| Setting | Value |
|---------|-------|
| Guest expiration | 30 days |
| Anyone link expiration | 30 days maximum (or Anyone links disabled) |
| Default link type | Specific people, View permission |
| Domain restrictions | Allow-list of approved partners |
| Monitoring | Weekly sharing report review |

### Regulated (Level 4)

| Setting | Value |
|---------|-------|
| Organization sharing | Existing guests only (or Only people in your organization) |
| Regulated sites | External sharing disabled, no exceptions |
| Conditional Access | MFA + compliant device + sign-in frequency for guests |
| Guest access reviews | Quarterly certification with documented sign-off |
| Evidence retention | WORM-stored snapshots for SEC 17a-4(f) |

---

## Validation Checklist

After completing the walkthrough, confirm:

- [ ] Baseline export captured and stored under evidence path
- [ ] Organization-level sharing set to **Existing guests** or more restrictive
- [ ] Default link type set to **Specific people** with **View** permission
- [ ] Guest access expiration enabled with zone-appropriate values
- [ ] Anyone link expiration configured (or Anyone links disabled)
- [ ] Domain allow-list configured (Zone 2/3 tenants)
- [ ] All Zone 3 sites set to **Only people in your organization**
- [ ] All Zone 2 sites set to **Existing guests**
- [ ] Conditional Access policy targets external users with MFA + device compliance
- [ ] Data Access Governance reports accessible and scheduled for weekly review
- [ ] Test sharing attempt on a Zone 3 site is blocked (capture screenshot for evidence)

**Expected outcome:** External sharing is restricted in proportion to site classification, guest access expires automatically, and sharing activity is visible in supervisory reporting.

---

[Back to Control 4.4](../../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
