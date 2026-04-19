# Control 4.1: SharePoint Information Access Governance (IAG) — Portal Walkthrough

> Step-by-step portal configuration for [Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md). Covers Restricted Content Discovery (RCD), Restricted SharePoint Search (RSS), Restricted Access Control (RAC), and Data Access Governance (DAG) reports across the SharePoint admin center and Microsoft Purview portal.

---

## Prerequisites

- [ ] **Roles:** SharePoint Admin (canonical role from `docs/reference/role-catalog.md`); Purview Compliance Admin for audit-log verification
- [ ] **Licensing:** At least one Microsoft 365 Copilot license assigned in the tenant (hard prerequisite for RCD as of the April 2026 Microsoft Learn update). SAM features ship with Copilot; Restricted Site Creation still requires the standalone SAM add-on
- [ ] **Inventory:** Governance-tier classification completed for SharePoint sites; Zone 2 / Zone 3 sensitive site list documented
- [ ] **Audit:** Unified Audit Log enabled in Microsoft Purview (verify in *Audit > Audit search > Settings*)
- [ ] **Browser session:** Sign in to [https://admin.sharepoint.com](https://admin.sharepoint.com) (modern admin center) and [https://purview.microsoft.com](https://purview.microsoft.com)

---

## Portal Surface Map (April 2026)

| Capability | Portal | Path |
|---|---|---|
| Data Access Governance reports | SharePoint admin center | **Reports → Data access governance** |
| Per-site RCD toggle | SharePoint admin center | **Sites → Active sites → {site} → Settings → Restrict content from Microsoft 365 Copilot** |
| Tenant-wide RSS allow-list | SharePoint admin center | **Settings → Search → Restricted SharePoint Search** |
| Per-site RAC | SharePoint admin center | **Sites → Active sites → {site} → Settings → Restricted access control** |
| Audit search for IAG events | Microsoft Purview | **Audit → New search** (operations: `SiteRestrictedFromOrgSearch`, `RestrictedAccessControlPolicyUpdated`) |

---

## Step 1 — Identify Oversharing with Data Access Governance Reports

1. SharePoint admin center → **Reports → Data access governance**.
2. Open **Sites shared with "Everyone except external users"** and **Sites with sharing links**. Export each report.
3. Cross-reference flagged sites with your Zone 2 / Zone 3 inventory. Sites that appear here and contain NPI, MNPI, SOX-scoped, or regulatory-examination data are candidates for RCD.
4. Save the exports to your evidence store (see [verification-testing.md](verification-testing.md) for retention guidance).

---

## Step 2 — Enable Restricted Content Discovery (RCD) per Site

For each site identified in Step 1:

1. SharePoint admin center → **Sites → Active sites**.
2. Select the site. In the right pane, choose the **Settings** tab.
3. Locate **Restrict content from Microsoft 365 Copilot** and toggle it **On**.
4. Capture a screenshot of the toggle in the **On** state. Record: site URL, business owner, justification, change ticket ID, and review date in your governance system.

!!! warning "Reindex latency"
    Enabling RCD triggers a Semantic Index reindex of the site. For libraries with thousands of items, propagation may take **several hours up to ~72 hours**. Plan rollouts during maintenance windows and re-test Copilot behaviour after reindex completes.

!!! info "Site-admin delegation (GA, January 2026)"
    Site collection administrators can toggle RCD on their own sites and must supply a justification, which is captured to the audit log. Tenant SharePoint Admins remain responsible for tenant-level visibility via DAG reports.

---

## Step 3 — (Optional) Configure Restricted SharePoint Search (RSS) Allow-List

!!! warning "Short-term posture only"
    RSS is a short-term, allow-list posture intended to buy time while permissions are remediated. It is not recommended as a long-term governance model — transition to RCD + Purview-based controls.

1. SharePoint admin center → **Settings → Search → Restricted SharePoint Search**.
2. Toggle **Restricted SharePoint Search** to **On**.
3. Click **Add sites** and supply the approved site URLs (current documented limit: **100 sites** — verify on Microsoft Learn before relying on this number).
4. Save. Allow up to 24 hours for propagation.

---

## Step 4 — Configure Restricted Access Control (RAC) for Ethical Walls

For information-barrier scenarios (M&A deal rooms, trading-desk separation, IB/research walls, regulatory examination sites):

1. SharePoint admin center → **Sites → Active sites → {site} → Settings**.
2. Open **Restricted access control** → **Edit**.
3. Enable the policy and add up to **10 Microsoft Entra security groups** authorised to access the site.
4. Save and capture a screenshot of the policy state plus the listed groups.
5. If your tenant uses delegated RAC management, the site admin will be prompted for a justification — record it for the change file.

!!! info "Tenant-level RAC delegation"
    Delegation is configured tenant-wide via PowerShell (`Set-SPOTenant -DelegateRestrictedAccessControlManagement $true`). See [powershell-setup.md](powershell-setup.md).

---

## Step 5 — Verify Audit Capture in Microsoft Purview

1. Microsoft Purview portal → **Audit → New search**.
2. Date range: covering your changes. Activities: `SiteRestrictedFromOrgSearch`, `RestrictedAccessControlPolicyUpdated`.
3. Confirm each change you made appears with user UPN, site URL, timestamp, and (where applicable) the justification text.
4. Export the result to CSV and store with your change records — required for FINRA 4511 / SEC 17a-4 evidence.

---

## Step 6 — Document and Schedule Reviews

| Cadence | Action | Owner |
|---|---|---|
| On change | Capture screenshot, audit-log export, justification | SharePoint Admin / site owner |
| Quarterly (Zone 3) | Re-attest restricted site list; reconfirm RAC group membership | Compliance Officer |
| Semi-annual (Zone 2) | Review owner approvals for shared agent knowledge sources | AI Governance Lead |
| On agent deployment | Verify knowledge sources do not include RCD-protected sites | AI Governance Lead |
| On regulatory change | Reassess RCD/RAC scope | Compliance Officer |

---

## Configuration by Governance Level

| Setting | Baseline | Recommended | Regulated |
|---|---|---|---|
| RCD on sensitive sites | Case-by-case | All Zone 2 sensitive sites | All Zone 3 sites |
| RAC for ethical walls | Not required | Recommended for MNPI/M&A | Required |
| DAG report review | Annual | Semi-annual | Quarterly |
| Change approval | Self-service | Owner approval | Governance committee |

---

## RCD vs RSS — Choosing the Approach

| Approach | Model | Use when |
|---|---|---|
| **RCD** | Block-list (exclude specific sites) | Mature deployment with reasonable permission hygiene |
| **RSS** | Allow-list (include only approved sites) | Initial Copilot rollout while permissions remediation is in flight (short-term) |
| **Hybrid** | RSS now, transition to RCD | Phased rollout; track exit criteria from RSS |

---

## Validation Checklist

- [ ] RCD enabled for every Zone 3 site and confirmed via the toggle UI
- [ ] RSS enabled (only if pursuing the short-term allow-list approach) with documented exit plan
- [ ] RAC configured for all ethical-wall sites with the correct Entra groups
- [ ] DAG oversharing report reviewed and exported for evidence
- [ ] Audit-log search in Purview returns all expected `SiteRestrictedFromOrgSearch` events
- [ ] Governance system updated with site, owner, justification, and review date

---

[Back to Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.3.3*
