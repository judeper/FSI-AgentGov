# Control 4.3: Site and Document Retention Management - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 4.3](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md).

---

## Prerequisites

Before starting, ensure you have:

- **SharePoint Admin** role assigned (for site lifecycle policies and OneDrive retention)
- **Purview Compliance Admin** or **Purview Records Manager** role (for retention labels and policies)
- Microsoft 365 E3/E5, Office 365 E3/E5, or **SharePoint Advanced Management (SAM)** add-on for site lifecycle policies
- Retention requirements documented per regulation, content type, and zone
- Coordination with Legal and the eDiscovery owner (Control 1.19) before publishing or modifying any retention policy

!!! warning "Validate before publishing"
    Retention policies that include **delete** actions are difficult to reverse. Pilot every policy in a non-production scope (a single test site or OneDrive) before broad publication. SOX 404 / FINRA 3110 supervisory procedures should require change-ticket evidence for any production retention change.

---

## Step 1: Document Retention Requirements

Identify retention requirements for your organization:

- Regulatory requirements (FINRA, SEC, SOX, GLBA)
- Business and litigation-readiness requirements
- Legal hold scope coordinated with the eDiscovery owner
- Agent knowledge-source retention needs (per Control 4.1)

**Retention Periods by Regulation:**

| Regulation | Retention Period | Content Type |
|------------|-----------------|--------------|
| FINRA Rule 4511 | 6 years | Books and records (general) |
| SEC Rule 17a-4(b)(4) | 3 years (first 2 readily accessible) | Communications, including agent prompts/responses where they constitute a business communication |
| SEC Rule 17a-4(a) | 6 years (first 2 readily accessible) | Financial / accounting records |
| SOX Section 802 / SEC Reg S-X Rule 2-06 | 7 years | Audit workpapers and supporting records |
| GLBA Section 501(b) | Not specified by statute | Customer information; align with internal records-retention schedule (commonly 5–7 years in practice) |
| FINRA Notice 25-07 (AI supervision) | Aligns with underlying record type | Supervisory artifacts for AI/agent activities |

> **Note:** GLBA does not prescribe a specific retention period. The 5–7-year range reflects common industry practice; verify your organization's obligations independently.

---

## Step 2: Configure Inactive Site Policies (SharePoint Admin Center)

Inactive site lifecycle policies are managed in the **SharePoint Admin Center**, not in Microsoft Purview.

1. Navigate to <https://admin.microsoft.com> and open the **SharePoint Admin Center** (or go directly to `https://<tenant>-admin.sharepoint.com`).
2. In the left navigation, expand **Policies** > **Site lifecycle management**.
3. Open **Inactive site policies** and click **Create a policy**.
4. Configure:
    - **Site scope:** All sites, or filter by template (Teams-connected, Communication, Classic, etc.) and/or sensitivity label
    - **Inactivity threshold:** 1, 2, 3, or 6 months (90 days is the common starting baseline; align with your records schedule)
    - **Notifications:** Email site owners and a designated SharePoint admin distribution list
    - **Enforcement actions:** Notify only → mark **Read-only** → **Archive** (graduated escalation is recommended over immediate deletion)
5. Save and **enable** the policy. Review the daily report on first run before broadening scope.

!!! info "Licensing"
    Inactive site policies require SharePoint Advanced Management, M365 E3/E5/A5, Office 365 E3/E5/A5, or at least one Copilot license active in the tenant. Confirm in **SharePoint Admin Center > Settings > SharePoint Advanced Management** before authoring.

---

## Step 3: Configure Site Ownership Policies

Site ownership policies sit alongside inactive site policies in the same SAM page.

1. In **SharePoint Admin Center > Policies > Site lifecycle management**, open **Site ownership policies**.
2. Click **Create a policy** and configure detection of orphaned or under-owned sites (sites with fewer than two active owners).
3. Configure notifications to the SharePoint Admin distribution list and site members eligible to become owners.
4. Set the enforcement action (notify-only is recommended at first; tighten to read-only after pilot).

---

## Step 4: Set Organization Retention Defaults

1. In **SharePoint Admin Center**, go to **Settings**.
2. Open **OneDrive retention** and set retention to **at least 365 days** for regulated organizations.
3. Review **Version history limits** under **Settings**; for regulated content, configure automatic version trimming aligned to your records schedule rather than indefinite versions.

---

## Step 5: Create and Publish Retention Labels (Microsoft Purview)

Document-level retention is managed in Microsoft Purview.

1. Navigate to <https://purview.microsoft.com>.
2. Go to **Solutions > Data Lifecycle Management** (or **Records Management** if labels need to declare records).
3. Under **Labels**, click **Create a label** and create one per retention class. Recommended starter set:

    | Label Name | Retention | Action | Use Case |
    |---|---|---|---|
    | FSI-Communications-3Y | 3 years from creation | Retain then delete | SEC 17a-4(b)(4) communications, including agent prompts/responses recorded as communications |
    | FSI-Financial-Records-6Y | 6 years from last modified | Retain then delete | SEC 17a-4(a), FINRA 4511 records |
    | FSI-Audit-Workpapers-7Y | 7 years from creation | Retain then delete | SOX 802 / SEC Reg S-X Rule 2-06 |
    | FSI-Regulatory-Record-7Y-Locked | 7 years from creation | Retain only (Record) | Immutable record where modification must be blocked |

4. For records that must be preserved unchanged, mark the label as a **Record** (or **Regulatory record** where supported and reviewed by Legal). Regulatory records cannot be removed by users or admins prior to expiry.
5. Click **Publish labels** to make them available in SharePoint, OneDrive, Exchange, and Teams locations.
6. For high-confidence content classes, use **auto-apply label policies** with sensitivity, KQL query, or trainable classifier conditions; review the policy daily for the first 30 days to detect false positives.

---

## Step 6: Apply Preservation Lock to Regulatory Retention Policies

For policies covering content within SEC 17a-4(f) WORM scope, applying **Preservation Lock** prevents disabling or shortening of the policy.

1. In Microsoft Purview, open **Data Lifecycle Management > Policies**.
2. Open the regulatory retention policy.
3. Use `Set-RetentionCompliancePolicy -Identity "<name>" -RestrictiveRetention $true` (Security & Compliance PowerShell — there is no portal toggle for this).
4. Capture the irreversible-confirmation prompt as evidence; preservation lock is one-way.

!!! warning "Preservation Lock is irreversible"
    Once enabled, preservation lock cannot be removed. The policy can be **extended** in scope/duration, but locations cannot be removed and the policy cannot be deleted. Pilot the policy for at least one full review cycle before locking.

---

## Step 7: Coordinate with eDiscovery and Legal Holds

1. Confirm with the eDiscovery owner (per Control 1.19) that legal-hold scope is documented and that holds are placed via Microsoft Purview eDiscovery (Premium where available).
2. Verify behavior: when a hold is in place, retention policies that delete content are overridden — content remains in **Preservation Hold Library** until the hold is released.
3. Document the override behavior in your retention runbook so disposition reviewers do not attempt manual cleanup of held content.

---

## Governance Level Configurations

### Baseline (Level 1)

| Setting | Value |
|---------|-------|
| Inactive site policy | Identify sites inactive for 90+ days (notify only) |
| Version history | Enabled with sensible limits |
| OneDrive retention | Default tenant value (deleted-user OneDrive retained 30 days minimum) |

### Recommended (Level 2-3)

| Setting | Value |
|---------|-------|
| Inactive site policy | Notify → read-only after 30 days → archive after 180 days |
| Site ownership policy | Identify and remediate orphaned sites |
| OneDrive retention | 365 days minimum |
| Retention by content type | Labels published and auto-applied to regulated content classes |
| Disposition review | Enabled for retention labels with delete actions |

### Regulated (Level 4)

| Setting | Value |
|---------|-------|
| Policy-driven retention | All Zone 3 sites covered by a documented retention policy |
| Records labels | Applied to regulatory content; manual deletion blocked |
| Preservation lock | Applied to SEC 17a-4(f) scope policies |
| Disposition logs | Captured in audit log; exported to immutable storage |
| Legal hold integration | Coordinated with eDiscovery; tested annually |

---

## Validation

After completing the configuration, verify:

1. [ ] Inactive site policy enabled with 90+ day threshold in **SharePoint Admin Center > Policies > Site lifecycle management**
2. [ ] Site ownership policy configured to identify and remediate orphaned sites
3. [ ] OneDrive retention set to 365 days minimum in **SharePoint Admin Center > Settings > OneDrive retention**
4. [ ] Retention labels published in Microsoft Purview for FINRA-aligned (6-year), SEC communications (3-year), SEC financial (6-year), and SOX (7-year) content classes
5. [ ] Preservation lock applied (where required) to regulatory retention policies
6. [ ] Legal hold override behavior tested with the eDiscovery owner

**Expected Result:** Inactive sites are identified and managed, orphaned sites have a remediation workflow, regulated content is governed by published labels with appropriate immutability, and legal holds correctly override retention deletion.

---

[Back to Control 4.3](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4.0*
