# Portal Walkthrough: Control 1.16 — Information Rights Management (IRM)

**Last Updated:** May 2026
**Portals:** Microsoft 365 Admin Center, Microsoft Purview, SharePoint Admin Center, individual SharePoint site
**Estimated Time:** 2–4 hours (initial activation + first label + first library); add ~15 min per additional library

---

## Prerequisites

- [ ] Entra Global Admin (one-time, for Azure RMS activation only — elevate via Privileged Identity Management).
- [ ] Purview Info Protection Admin (label creation and policy publication).
- [ ] SharePoint Admin (library IRM activation at tenant level and per site).
- [ ] Licensing that includes Azure Rights Management — Microsoft 365 E3/E5, Office 365 E3/E5, Microsoft 365 Business Premium, or a standalone Microsoft Purview Information Protection P1/P2 SKU. Verify before activation.
- [ ] Inventory of SharePoint document libraries used as agent knowledge sources (from [Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) inventory).
- [ ] Approved naming convention for sensitivity labels (e.g., `FSI-Confidential-IRM`, `FSI-Client-NPI-IRM`, `FSI-MNPI-IRM`).
- [ ] Compliance super-user group provisioned in Entra ID (recommended: mail-enabled security group, e.g., `SG-Compliance-RMS-SuperUsers`).

---

## Step 1 — Activate Azure Rights Management Service

1. Sign in to the [Microsoft 365 Admin Center](https://admin.microsoft.com).
2. Navigate to **Settings** → **Org settings** → **Services** tab.
3. Select **Microsoft Azure Information Protection**.
4. Confirm status reads **Protection is activated**. If it reads "Not activated", select **Activate**.
5. Wait 15–30 minutes for tenant propagation before configuring labels or library IRM.

> **Note:** Newer tenants have Azure RMS activated by default. Existing tenants migrated from legacy Azure Information Protection may show as activated already — verify rather than re-activate.

---

## Step 2 — Create an IRM-Enabled Sensitivity Label

1. Open the [Microsoft Purview portal](https://purview.microsoft.com).
2. Navigate to **Solutions** → **Information Protection** → **Labels**.
3. Select **Create a label** and provide:
    - **Display name:** `FSI Confidential — IRM` (or per your taxonomy)
    - **Description for users:** "Confidential firm content. Do not redistribute. Access is logged."
    - **Description for admins:** Reference Control 1.16 and the Zone tier this label supports.
4. **Scope:** Select **Items** → **Files**, **Emails**, and **Meetings** as appropriate.
5. **Encryption:** Select **Configure encryption settings**:
    - **Assign permissions now or let users decide:** **Assign permissions now**.
    - **User access to content expires:** Per Zone (Zone 2: 180 days; Zone 3: 90 days; Zone 1: Never).
    - **Allow offline access:** Per Zone (Zone 2: 14 days; Zone 3: 7 days; Zone 1: 30 days).
    - **Assign permissions:** Add the user / group / agent identity entries below.
6. **Permission entries (least privilege):**

    | Principal | Recommended permission level |
    |---|---|
    | Compliance group (e.g., `SG-Compliance-RMS-SuperUsers`) | Co-Owner |
    | Authoring team (e.g., `SG-Advisory-Authors`) | Co-Author |
    | Reviewing audience (e.g., `SG-Advisory-Reviewers`) | Reviewer |
    | Agent service identity (Microsoft Copilot Studio app registration or M365 Copilot identity) | **Viewer** |

7. **Content marking:** Enable header, footer, and watermark as required by Zone:
    - Header (Zone 2/3): `CONFIDENTIAL — FSI INTERNAL USE`
    - Footer (Zone 3): `Do not distribute. Access is logged. © [Org]`
    - Watermark (Zone 3): `${Item.Label} — ${User.PrincipalName}` (dynamic with viewer email)
8. Complete the wizard and **Save**.
9. Navigate to **Label policies** → **Publish labels**. Add the new label to a policy targeted at the user populations that author or consume agent content. Do **not** scope the publishing policy to the agent's service identity itself.

---

## Step 3 — Enable IRM for SharePoint at the Tenant Level

1. Open the [SharePoint Admin Center](https://admin.microsoft.com/sharepoint).
2. Navigate to **Policies** → **Access control** → **Information Rights Management (IRM)**.
3. Select **Use the IRM service specified in your configuration** and **Save**.
4. Wait up to 1 hour for tenant propagation before enabling IRM on individual libraries.

---

## Step 4 — Enable IRM on a SharePoint Document Library

Repeat for each library in the agent knowledge-source inventory.

1. Navigate to the SharePoint site that hosts the library.
2. Open the library, then select **Settings (gear)** → **Library settings** → **More library settings**.
3. Under **Permissions and Management**, select **Information Rights Management**. (If the link does not appear, Step 3 has not propagated yet.)
4. Check **Restrict permissions on this library on download**.
5. **Permission policy title:** `1.16 — Agent KB IRM Policy ([Zone N])`.
6. **Permission policy description:** `Documents downloaded from this library are protected per FSI Control 1.16. Discuss only with authorized firm personnel.`
7. Select **Show options** and configure per Zone:

    | Setting | Zone 1 | Zone 2 | Zone 3 |
    |---|---|---|---|
    | Allow viewers to print | Yes | No | No |
    | Allow viewers to run script and screen reader on downloaded documents | No | No | No |
    | After download, document access rights expire after (days) | (Unset) | 180 | 90 |
    | Do not allow users to upload documents that do not support IRM | No | Yes | Yes |
    | Stop restricting access to the library at | (Unset) | (Unset) | (Unset) |
    | Users must verify their credentials using this interval (days) | 30 | 14 | 7 |
    | Allow group protection | Yes (per advisory team) | Yes (per advisory team) | Yes (per advisory team) |

8. **Save**.
9. Confirm the library card now shows the IRM badge in the library settings header.

---

## Step 5 — Configure Document Tracking and the Super-User Feature

1. In Microsoft Purview, navigate to **Information Protection** → **Settings** → **Track and revoke documents** and confirm tracking is enabled tenant-wide.
2. Provision the super-user group (one-time) — see [PowerShell Setup](powershell-setup.md) Step "Configure super-user group".
3. Communicate the super-user group identity and revocation procedure to the compliance team. Limit super-user membership to the minimum number of named individuals.

---

## Step 6 — Configure Auto-Labeling (Recommended for Zone 2 and Required for Zone 3)

1. In Microsoft Purview, navigate to **Information Protection** → **Auto-labeling**.
2. Create a new auto-labeling policy:
    - **Sensitive info types:** U.S. Social Security Number, Credit Card Number, U.S. Bank Account Number, plus organization-defined types for client identifiers and MNPI keywords.
    - **Locations:** SharePoint sites hosting agent knowledge libraries; OneDrive accounts of authoring users.
    - **Label to apply:** the `FSI Confidential — IRM` label from Step 2.
    - **Run in simulation mode** for at least 7 days before turning on.
3. Review simulation results, tune sensitive info type confidence levels, then turn the policy on.

---

## Validation Summary

After completing all steps, confirm:

- [ ] `Get-AipService` returns `Enabled` and the admin center shows "Protection is activated".
- [ ] At least one IRM-enabled label is published in an active label policy.
- [ ] Tenant-level SharePoint IRM is enabled in the SharePoint Admin Center.
- [ ] Each library in the agent knowledge-source inventory shows the IRM settings configured per its Zone.
- [ ] Super-user group exists and is documented in the compliance runbook.
- [ ] Auto-labeling policy is published (simulation or active) for Zone 2/3 content scopes.

See [Verification & Testing](verification-testing.md) for end-to-end test cases and evidence collection.

---

[Back to Control 1.16](../../../controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
