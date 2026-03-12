# Troubleshooting: Control 1.26 - Agent File Upload and File Analysis Restrictions

**Last Updated:** February 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| File upload toggle not visible in agent settings | Agent version below v8 or feature not enabled in environment | Verify agent is on Copilot Studio v8+; check environment feature flags |
| Agent accepts uploads despite toggle disabled | Cached session or propagation delay | Clear browser cache; wait 15 minutes for propagation |
| Sensitivity labels not applied to uploaded files | Purview labeling policies not scoped to SPE containers | Verify sensitivity label auto-labeling policies cover SharePoint Embedded |
| DLP policy not triggering on uploaded file content | DLP policy not scoped to Power Platform or wrong connector | Review DLP policy scope in Purview Compliance Portal |
| SPE container access not restricted | Default container permissions too permissive | Configure access controls on the SPE container via PPAC |
| Agent inventory script returns incomplete results | Insufficient permissions or environment filtering | Verify Power Platform Admin role; check environment scope |

---

## Detailed Troubleshooting

### Issue: File Upload Toggle Not Visible in Agent Settings

**Symptoms:** The File Upload security toggle does not appear in the agent's Security settings in Copilot Studio

**Resolution:**

1. Verify the agent is running on Copilot Studio v8 or later:
   - Open the agent in Copilot Studio
   - Check the agent version in Settings → Details
2. Verify file upload features are enabled at the environment level:
   - Navigate to Power Platform Admin Center → Environments → [Environment] → Settings → Features
   - Check that Copilot features are enabled
3. Confirm your role has permissions to view security settings:
   - Agent authors and Power Platform Admins should see the toggle
   - Users with viewer-only access may not see the Security settings panel
4. If the feature is still not visible, check for tenant-level feature flags:
   - Contact your Microsoft account team to verify file upload features are available in your tenant

**Portal Path:**
```
Copilot Studio → [Agent] → Settings → Security → File Upload
```

> **Note:** File upload capabilities are progressively rolling out. If the toggle is not available, the feature may not yet be enabled for your tenant region.

---

### Issue: Agent Accepts Uploads Despite Toggle Disabled

**Symptoms:** Users can upload files to an agent even though the File Upload toggle is set to disabled

**Resolution:**

1. Verify the toggle is saved (not just toggled but unsaved):
   - Open agent Settings → Security
   - Confirm the File Upload toggle shows "Disabled"
   - Click **Save** if there are unsaved changes
2. Clear browser cache and open a new session:
   - Cached agent configurations may persist for up to 15 minutes
3. Verify the agent is published after the toggle change:
   - Changes to agent settings may require republishing the agent
   - Click **Publish** in the Copilot Studio editor
4. Check for environment-level overrides:
   - Some environment configurations may override per-agent settings
   - Navigate to PPAC → Environments → [Environment] → Settings

---

### Issue: Sensitivity Labels Not Applied to Uploaded Files

**Symptoms:** Uploaded files do not display sensitivity labels; agent does not inherit labels from file knowledge sources

**Resolution:**

1. Verify Purview sensitivity labeling is configured for your tenant:
   - Navigate to Microsoft Purview → Information Protection → Labels
   - Confirm labels are published and active
2. Check that auto-labeling policies cover SharePoint Embedded containers:
   - SPE containers used by Copilot Studio may not be included in standard SharePoint labeling policies
   - Create or update auto-labeling policies to include SPE container locations
3. Verify the uploaded file has a label applied at the source:
   - Labels inherited by the agent come from the uploaded files themselves
   - Test with a file that has an explicit label applied before upload
4. Allow up to 24 hours for label propagation after policy changes

**Portal Path:**
```
Microsoft Purview → Information Protection → Labels → [Label Name] → Auto-labeling
```

---

### Issue: DLP Policy Not Triggering on Uploaded File Content

**Symptoms:** DLP alerts are not generated when files with sensitive content are uploaded to agents

**Resolution:**

1. Navigate to Microsoft Purview Compliance Portal → Data Loss Prevention → Policies
2. Verify a DLP policy exists that covers Power Platform connectors
3. Check the policy scope includes the target environment and connector
4. Verify the policy is in **Enforce** mode (not **Test** or **Off**)
5. Confirm the DLP policy includes rules for the sensitive information types present in the test file
6. Allow up to 24 hours for new DLP policies to take effect
7. Check Activity explorer for recent events to rule out display delay

**Portal Path:**
```
Microsoft Purview Compliance Portal → Data Loss Prevention → Policies → [Policy Name]
```

---

### Issue: SPE Container Access Not Restricted

**Symptoms:** Uploaded files in SharePoint Embedded containers are accessible to unauthorized users or lack proper retention policies

**Resolution:**

1. Navigate to Power Platform Admin Center → Environments → [Environment]
2. Locate the SharePoint Embedded container details
3. Review access controls:
   - Verify only authorized users and service accounts have access
   - Remove any overly broad permissions (e.g., "Everyone" or "All Users")
4. Apply retention policies:
   - Navigate to Microsoft Purview → Data Lifecycle Management → Retention Policies
   - Create or update a retention policy that covers SPE container locations
5. Enable auditing on the SPE container to track access events

---

### Issue: Agent Inventory Script Returns Incomplete Results

**Symptoms:** The PowerShell inventory script does not list all agents or environments

**Resolution:**

1. Verify your account has Power Platform Admin or Entra Global Admin role:
   ```powershell
   Get-AdminPowerAppEnvironment | Measure-Object
   ```
2. Check for environments excluded by filtering:
   ```powershell
   Get-AdminPowerAppEnvironment -GetAllEnvironments | Format-Table DisplayName, EnvironmentType
   ```
3. Verify the PowerShell module is current:
   ```powershell
   Get-Module -Name Microsoft.PowerApps.Administration.PowerShell -ListAvailable
   Update-Module -Name Microsoft.PowerApps.Administration.PowerShell
   ```
4. Some environments may require explicit authentication:
   ```powershell
   Add-PowerAppsAccount -Endpoint "prod"
   ```

---

## Escalation Path

1. **Copilot Studio Agent Author** — Per-agent toggle configuration, agent publishing
2. **Power Platform Admin** — Environment settings, SPE container management, feature flags
3. **Purview Compliance Admin** — DLP policy scoping, sensitivity label configuration
4. **Security Operations** — Upload activity monitoring, anomaly investigation
5. **Microsoft Support** — Platform-level issues with file upload features or SPE containers

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| File upload toggle is per-agent (no bulk toggle in UI) | Individual configuration required for each agent | Use PowerShell scripts for bulk operations |
| Maximum 20 files per agent | Agents cannot accept more than 20 files as knowledge sources | Consolidate content into fewer files; use SharePoint sites for larger knowledge bases |
| File size limits are platform-defined | Cannot reduce limits below Microsoft defaults per agent | Apply DLP and content scanning to compensate |
| SPE containers share tenant-level settings | Container-level fine-grained access requires additional configuration | Apply retention and access policies at the container level |
| Sensitivity label inheritance is automatic | Cannot override inherited labels at the agent level | Ensure source files have appropriate labels before upload |
| Toggle changes may require agent republish | Settings may not take effect until the agent is republished | Always republish the agent after modifying security settings |
| Propagation delay up to 15 minutes | Recent toggle changes may not be enforced immediately | Wait 15 minutes before testing after configuration changes |

---

## Diagnostic Commands

### Check Agent File Upload Status

```powershell
Get-AdminPowerAppChatbot -EnvironmentName "your-environment-name" |
    Select-Object @{N='Agent';E={$_.Properties.DisplayName}},
                  @{N='FileUpload';E={$_.Properties.FileUploadEnabled}},
                  @{N='LastModified';E={$_.Properties.LastModifiedTime}} |
    Format-Table -AutoSize
```

### Verify Module Installation

```powershell
Get-Module -Name Microsoft.PowerApps.Administration.PowerShell -ListAvailable |
    Format-Table Name, Version, Path
```

### List All Environments

```powershell
Get-AdminPowerAppEnvironment | Format-Table DisplayName, EnvironmentName, EnvironmentType
```

### Export File Upload Inventory for Audit

```powershell
Get-AdminPowerAppEnvironment | ForEach-Object {
    $envName = $_.EnvironmentName
    $envDisplay = $_.DisplayName
    Get-AdminPowerAppChatbot -EnvironmentName $envName -ErrorAction SilentlyContinue | ForEach-Object {
        [PSCustomObject]@{
            Environment       = $envDisplay
            AgentName         = $_.Properties.DisplayName
            FileUploadEnabled = $_.Properties.FileUploadEnabled
            LastModified      = $_.Properties.LastModifiedTime
        }
    }
} | Export-Csv -Path ".\FileUploadAudit.csv" -NoTypeInformation
```

---

## Related Documentation

- [Microsoft Learn: Copilot Studio file upload configuration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-file-upload)
- [Microsoft Learn: Power Platform Admin Center security settings](https://learn.microsoft.com/en-us/power-platform/admin/security/security-overview)
- [Microsoft Learn: SharePoint Embedded overview](https://learn.microsoft.com/en-us/sharepoint/dev/embedded/overview)
- [Microsoft Learn: Microsoft Purview sensitivity labels](https://learn.microsoft.com/en-us/purview/sensitivity-labels)

---

[Back to Control 1.26](../../../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)
