# Control 4.3: Site and Document Retention Management - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 4.3](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md).

---

## Prerequisites

Before starting, ensure you have:

- SharePoint Administrator role assigned
- Microsoft 365 E5 or E5 Compliance license
- SharePoint Advanced Management enabled for tenant
- Retention requirements documented by regulation and content type

---

## Step 1: Document Retention Requirements

Identify retention requirements for your organization:

- Regulatory requirements (FINRA, SEC, SOX, GLBA)
- Business requirements
- Legal hold requirements
- Agent knowledge source retention needs

**Retention Periods by Regulation:**

| Regulation | Retention Period | Content Type |
|------------|-----------------|--------------|
| FINRA 4511 | 6 years | Books and records |
| SEC 17a-3/4 | 6 years | Communications, records |
| SOX 404 | 7 years | Financial records |
| GLBA | 5-7 years | Customer information |

---

## Step 2: Configure Inactive Site Policies

Create policy to manage inactive sites:

1. Navigate to [SharePoint Admin Center](https://admin.sharepoint.com)
2. Go to **Policies** > **Site lifecycle management**
3. Click **Open** under "Inactive site policies"
4. Click **Create policy**
5. Configure:
   - **Scope:** All sites or specific site templates
   - **Inactivity period:** 90 days (adjust per requirements)
   - **Notification:** Email to site owners and admins
   - **Action:** Notify > Mark read-only > Archive
6. Enable the policy

---

## Step 3: Configure Site Ownership Policies

Ensure sites have active owners:

1. Navigate to **Policies** > **Site lifecycle management**
2. Click **Open** under "Site ownership policies"
3. Create policy to identify orphaned sites
4. Configure notification to SharePoint admins
5. Set action for unresolved ownership issues:
   - Notify admins to assign new owners
   - Mark read-only after 30 days if no owner assigned

---

## Step 4: Set Organization Retention Defaults

Configure organization-wide settings:

1. Navigate to **Settings** in SharePoint Admin Center
2. Review "OneDrive Retention" setting
3. Set to 365 days minimum for regulated organizations
4. Review "Version history limits" settings

---

## Step 5: Integrate with Microsoft Purview

For comprehensive document-level retention:

1. Navigate to [Microsoft Purview Compliance Portal](https://compliance.microsoft.com)
2. Go to **Data lifecycle management** > **Microsoft 365**
3. Create retention labels for document-level retention
4. Apply retention labels to sensitivity-labeled content
5. Configure retention policies for regulated content types
6. Coordinate with eDiscovery for legal holds

---

## Governance Level Configurations

### Baseline (Level 1)

| Setting | Value |
|---------|-------|
| Inactive site policy | Identify sites inactive for 90+ days |
| Policy action | Notify only |
| Version history | Enabled for document recovery |

### Recommended (Level 2-3)

| Setting | Value |
|---------|-------|
| Site ownership policy | Identify and remediate orphaned sites |
| Inactive site action | Archive after 180 days |
| OneDrive retention | 365 days minimum |
| Retention by content type | Apply labels to regulated content |

### Regulated (Level 4)

| Setting | Value |
|---------|-------|
| Policy-driven retention | All Zone 3 sites have documented retention |
| Manual deletion | Disabled for regulated content |
| Deletion logs | Immutable and non-editable |
| Legal hold integration | Coordinated with eDiscovery |

---

*Updated: January 2026 | Version: v1.2*
