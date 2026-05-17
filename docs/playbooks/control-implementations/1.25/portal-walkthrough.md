# Portal Walkthrough: Control 1.25 - MIME Type Restrictions for File Uploads

**Last Updated:** April 2026
**Portals:** Power Platform Admin Center (PPAC), Copilot Studio, Microsoft Defender for Cloud Apps, SharePoint Admin Center
**Estimated Time:** 30-45 minutes (full Zone 3 walkthrough including per-agent and Defender for Cloud Apps configuration)

## Prerequisites

- [ ] **Power Platform Admin** role (canonical role per `docs/reference/role-catalog.md`) — required for PPAC environment settings
- [ ] **AI Administrator** or environment-level Copilot Studio maker role — required for per-agent File Upload toggle and per-agent allowed file types
- [ ] **Entra Security Admin** — required for Defender for Cloud Apps file policy configuration (Zone 3)
- [ ] **SharePoint Admin** — required for tenant-level sync-client file blocking (defense-in-depth complement)
- [ ] Documented governance-zone classification for each target environment
- [ ] Documented per-agent file-type allowlist with business justification (for Zone 2/3 production agents)

> **Scope note:** PPAC settings configured below apply at the **environment** level and govern attachments stored on the Dataverse Organization entity. Per-agent settings in Copilot Studio apply additional constraints **within** those environment bounds. SharePoint and Defender for Cloud Apps controls listed at the end are tenant-level complements, not substitutes.

---

## Step-by-Step Configuration

### Step 1: Navigate to Environment Settings (PPAC)

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select **Environments** from the left navigation
3. Select the target environment (repeat for each environment per zone)
4. Click **Settings** in the top menu bar
5. Expand **Product** → **Privacy + Security**

> **Portal path (April 2026):** *Power Platform Admin Center → Environments → \[Environment\] → Settings → Product → Privacy + Security*. The **Privacy + Security** node now sits under **Product**; older guidance that lists it under **Features** is stale.

### Step 2: Configure Blocked File Extensions

1. Locate the **Set blocked file extensions for attachments** field
2. Enter a semicolon-separated list of file extensions to block
3. The following is a **partial list** of the most critical executable extensions. The complete Zone 1 baseline requires **44 extensions** — use `Set-FsiMimeConfig -ZoneTemplate zone1` from the [PowerShell Setup](powershell-setup.md) for the full list:

    ```
    exe;bat;cmd;com;vbs;js;wsf;scr;pif;msi;dll;reg;inf;hta;cpl;msp;mst
    ```

    !!! warning "Partial List"
        The inline list above covers only 17 of the 44 required Zone 1 extensions. Using this list alone will leave your environment **under-protected**. Apply the complete zone template via PowerShell or copy the full list from `scripts/governance/mime-templates/zone1.json`.

4. Click **Save** to apply changes

> **Note:** Zone 2+ environments should also block `ps1`. Zone 3 adds `cab`, `gadget`, `ps1xml`, `ps2`, `ps2xml`, `psc1`, `psc2`, `isp`, `its`, and `rgs`. The `FsiMimeControl` zone templates at `scripts/governance/mime-templates/` contain the complete lists (44 extensions for Zone 1, 45 for Zone 2, 55 for Zone 3). For full compliance, use `Set-FsiMimeConfig -ZoneTemplate zone1` from the [PowerShell Setup](powershell-setup.md) playbook or copy the complete list from the zone template JSON file.

### Step 3: Configure Blocked MIME Types (Zone 2+)

> **Zone 2 and Zone 3 only.** Skip this step for Zone 1 environments.

1. Locate the **Set blocked mime types for attachments** field
2. Enter a semicolon-separated list of MIME types to block
3. Recommended MIME types to block:

    ```
    application/x-msdownload;application/x-msdos-program;application/x-bat;application/x-cmd;application/x-vbs;application/javascript;application/x-powershell;application/x-msi
    ```

4. Click **Save** to apply changes

> **Note:** The list above covers the most common executable content types. The `FsiMimeControl` zone templates contain extended lists (15 types for Zone 2, 21 for Zone 3) including `text/javascript`, `application/hta`, `application/msaccess`, and others. For full compliance, use `Set-FsiMimeConfig -ZoneTemplate zone2` from the [PowerShell Setup](powershell-setup.md) playbook or copy the complete list from the zone template JSON file.

### Step 4: Configure Allowed MIME Types (Zone 2+)

1. Locate the **Set allowed mime types for attachments** field
2. Enter a semicolon-separated allowlist of MIME types that are permitted
3. Recommended allowlist for regulated environments:

    ```
    application/pdf;image/png;image/jpeg;image/gif;image/tiff;text/plain;text/csv;application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;application/vnd.openxmlformats-officedocument.wordprocessingml.document;application/vnd.openxmlformats-officedocument.presentationml.presentation
    ```

4. Click **Save** to apply changes

> **Important:** When an allowlist is configured, only the listed MIME types are accepted. All other types are rejected regardless of the blocked list. Both Zone 2 and Zone 3 templates include `image/tiff` in the allowlist — see the zone template JSON files for the complete list.

!!! warning "Legacy Office Formats Not Included"
    The zone template allowlists include modern Office formats (`.docx`, `.xlsx`, `.pptx`) but **not** legacy binary formats (`.doc`, `.xls`, `.ppt`). If your organization exchanges legacy Office documents — common in FSI for regulatory correspondence and historical records — add `application/msword`, `application/vnd.ms-excel`, and `application/vnd.ms-powerpoint` to your environment's allowed MIME types list. Alternatively, file an exception request using the [MIME Type Exception Request template](https://github.com/judeper/FSI-AgentGov/blob/main/docs/templates/exception-template.md) (form on GitHub).

### Step 5: Review and Apply Zone Template

1. Review the configuration against the governance level table below
2. Verify the settings match the zone classification for the selected environment
3. Document the applied configuration in your governance records
4. Repeat Steps 1-4 for each environment within the zone

### Step 6: Configure Per-Agent File Upload Settings (Copilot Studio)

> **Required for every file-upload-enabled agent in Zone 2 and Zone 3.** PPAC settings establish the *maximum* allowable file types; per-agent settings apply *additional* least-privilege restrictions.

1. Open [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select the target agent → **Settings** → **Security**
3. Locate the **File Upload** toggle
    - Set to **Off** if the agent has no documented file-handling use case (recommended default for Zone 1 personal agents)
    - Set to **On** only when the agent's documented purpose requires file inputs
4. If File Upload is **On**, configure **Allowed file types** to the minimum set required by the agent's documented purpose (e.g., `.pdf` only for a contract-summary agent — do not inherit the full environment allowlist by default)
5. Capture screenshot evidence of the toggle state and allowed-type list for each production agent (store under `maintainers-local/tenant-evidence/1.25/`)

> **User-input limits to communicate to agent owners (Microsoft Learn, April 2026):** PDFs uploaded by users at runtime are limited to **<40 pages**; TXT/CSV to **<180 KB**; images to **15 MB** (4 MB on Direct Line). Files configured as **knowledge sources** by makers may be up to **512 MB**, with **500 files per agent** for local uploads and **1,000 files per agent** for SharePoint/OneDrive sources (GA August 2025). Executable, audio, and video formats are not supported as knowledge sources and need not appear in the agent allowlist.

### Step 7: Configure Defender for Cloud Apps File Policy (Zone 3 Magic-Byte Inspection)

> **Required for Zone 3.** PPAC and per-agent settings inspect the *declared* file extension and MIME header. A file renamed `invoice.pdf` whose magic bytes are `MZ` (Windows executable) will pass PPAC checks. Defender for Cloud Apps (formerly MCAS) provides the true-content-type inspection layer.

1. Open [Microsoft Defender XDR portal](https://security.microsoft.com) → **Cloud apps** → **Policies** → **Policy management** → **File policy**
2. **Create policy** → **File policy**
3. **Filter** by **App** = SharePoint Online / OneDrive for Business (and any other connected app that hosts agent file inputs)
4. Add filter: **MIME type (true type) does not equal** the approved Zone 3 allowlist (mirrors PPAC `allowedmimetypes`)
5. **Governance actions:** Quarantine + Notify file owner + Notify SOC distribution list
6. **Alert:** Create alert; set severity High; configure SIEM forwarding to Microsoft Sentinel
7. Save policy and confirm it appears as **Enabled** in the policy list

> **Limitation:** Defender for Cloud Apps file policies operate on connected SaaS apps via API connectors, with near-real-time (not synchronous) scanning. Files may be briefly accessible to agents before quarantine completes; pair with PPAC blocking to fail-fast at the environment edge.

### Step 8: Configure SharePoint Tenant Blocked File Types (Defense-in-Depth)

1. Open [SharePoint Admin Center](https://admin.microsoft.com/sharepoint) → **Settings** → **Sync** → **Block upload of specific file types**
2. Add executable/script extensions matching your PPAC blocklist (e.g., `exe, bat, cmd, vbs, js, ps1, dll, msi, scr, hta`)
3. Save

> **Important caveat:** This SharePoint setting blocks the **OneDrive sync client only**. It does **not** block browser uploads to SharePoint, which means files reaching agent SharePoint knowledge sources via the browser are not filtered here. PPAC and Defender for Cloud Apps file policies remain the primary controls; this is a complementary layer for the sync-client vector.

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|---------------------|
| **Blocked File Extensions** | Yes — executable types | Yes — executable types | Yes — executable types |
| **Blocked MIME Types** | Optional | Yes | Yes |
| **Allowed MIME Types (Allowlist)** | Not required | Required | Required |
| **DLP Policy for File Uploads** | Not required | Yes | Yes — with alerts |
| **Sentinel Monitoring** | Not required | Optional | Required |
| **Review Frequency** | Quarterly | Monthly | Weekly |
| **Exception Process** | Informal | Documented | Documented with approval |

---

## Validation

After completing these steps, verify:

- [ ] Blocked file extensions are configured for each environment (Microsoft defaults retained, plus organizational additions)
- [ ] Blocked MIME types are configured for Zone 2 and Zone 3 environments
- [ ] Allowed MIME types allowlist is configured for Zone 2 and Zone 3 environments
- [ ] Per-agent **File Upload** toggle state is documented for every production agent (Zone 2 and Zone 3)
- [ ] Per-agent **Allowed file types** are configured to the minimum set required by each agent's documented purpose (least-privilege)
- [ ] Defender for Cloud Apps file policy with true-MIME (magic-byte) inspection is **Enabled** (Zone 3)
- [ ] SharePoint sync-client blocked file types match the PPAC blocklist (defense-in-depth)
- [ ] Configuration matches the governance level table for each environment zone
- [ ] Screenshot evidence is captured under `maintainers-local/tenant-evidence/1.25/` (gitignored)
- [ ] Changes are documented in governance records and reviewed at zone cadence (Q/M/W)

---

[Back to Control 1.25](../../../controls/pillar-1-security/1.25-mime-type-restrictions.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
