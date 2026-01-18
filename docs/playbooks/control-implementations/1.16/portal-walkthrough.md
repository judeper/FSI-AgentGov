# Portal Walkthrough: Control 1.16 - Information Rights Management (IRM)

**Last Updated:** January 2026
**Portal:** Microsoft Purview, SharePoint Admin Center
**Estimated Time:** 2-4 hours

## Prerequisites

- [ ] Purview Information Protection Admin role
- [ ] SharePoint Admin role
- [ ] Azure RMS activated for tenant

---

## Step-by-Step Configuration

### Step 1: Activate Azure Rights Management

1. Open [Microsoft 365 Admin Center](https://admin.microsoft.com)
2. Navigate to **Settings** > **Org settings** > **Services**
3. Select **Microsoft Azure Information Protection**
4. Verify status shows "Protection is activated"
5. If not activated, click **Activate**

### Step 2: Create IRM-Enabled Sensitivity Labels

1. Open [Microsoft Purview](https://compliance.microsoft.com)
2. Navigate to **Information protection** > **Labels**
3. Create new label:
   - Name: `FSI-Confidential-IRM`
   - Description: Confidential content with IRM protection
4. Configure encryption:
   - Enable **Encryption**
   - Select **Assign permissions now**
   - Add permissions for agent service accounts (Viewer)
5. Configure content marking:
   - Header: "CONFIDENTIAL - FSI Internal Use"
   - Watermark: Enable with user identity
6. Publish label via label policy

### Step 3: Enable IRM on SharePoint Libraries

1. Open [SharePoint Admin Center](https://admin.microsoft.com/sharepoint)
2. Navigate to the site containing agent knowledge sources
3. Go to **Site settings** > **Site permissions**
4. For each document library:
   - Open Library settings > Information Rights Management
   - Enable "Restrict permissions on this library on download"
   - Configure settings:
     - Allow viewers to print: [Based on zone]
     - Allow viewers to run scripts: No
     - Set content expiration: [Based on zone]

### Step 4: Configure Agent Service Account Access

1. In the sensitivity label permissions:
2. Add agent service account with "Viewer" permissions
3. This allows agent to read content but not bypass IRM

### Step 5: Configure Document Tracking

1. In Purview > Information protection > **Track usage**
2. Enable document tracking for IRM-protected content
3. Configure alerts for:
   - Access from unusual locations
   - Multiple failed access attempts
   - Revocation events

---

## Configuration by Governance Level

| Setting | Baseline (Tier 1) | Recommended (Tier 2) | Regulated (Tier 3) |
|---------|-------------------|----------------------|-------------------|
| **IRM Required** | Optional | Required | Mandatory |
| **Print/Copy** | Allowed | Blocked | Blocked |
| **Content Expiration** | None | 180 days | 90 days |
| **Offline Access** | 30 days | 14 days | 7 days |
| **Watermark** | Optional | Header only | Full watermark |
| **Screen Capture Block** | No | No | Yes |

---

## FSI Example Configuration

```yaml
IRM Configuration: Client Advisory Documents

Sensitivity Label: FSI-Client-Confidential
  Encryption: Enabled
  Permissions:
    - Compliance Team: Co-Owner
    - Advisory Team: Co-Author
    - Agent Service Account: Viewer

  Content Marking:
    Header: "CLIENT CONFIDENTIAL - [Client Name]"
    Footer: "Do not distribute without authorization"
    Watermark: Dynamic (viewer email)

  Protection Settings:
    Print: Blocked
    Copy: Blocked
    Forward: Blocked
    Expiration: 90 days
    Offline: 7 days

SharePoint Library: /sites/ClientAdvisory/Documents
  IRM: Enabled
  Download Restriction: Apply label on download
  Offline Viewing: 7 days maximum
```

---

## Validation

After completing these steps, verify:

- [ ] Azure RMS shows "Protection is activated"
- [ ] Sensitivity labels with IRM are published
- [ ] SharePoint library IRM is enabled
- [ ] Agent can read IRM content but not bypass restrictions
- [ ] Document tracking captures access events

---

[Back to Control 1.16](../../../controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
