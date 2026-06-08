# Control 2.13 — Troubleshooting: Documentation and Record Keeping

**Control:** 2.13 — Documentation and Record Keeping
**Pillar:** Pillar 2 — Management
**Audience:** SharePoint Admin, Purview Records Manager, Purview Compliance Admin, Power Platform Admin, Compliance Officer
**Companion playbooks:** [Portal Walkthrough](./portal-walkthrough.md) · [PowerShell Setup](./powershell-setup.md) · [Verification & Testing](./verification-testing.md)
**Last UI verified:** April 2026

---

## Audit Log and Retention Issues

### Missing Audit Logs for Agent Interactions

**Symptom:** Agent interaction events do not appear in Microsoft Purview Audit logs, or audit search returns zero results for `CopilotInteraction` or `PowerPlatformAdministratorActivity` record types.

**Likely Cause:**

- Unified audit logging is disabled at the tenant level
- The user or agent lacks the required license for Audit Premium events
- The audit log search timeframe does not cover the interaction window
- The query uses an invalid `RecordType` value for the tenant's licensing tier

**Diagnostic Steps:**

1. Verify unified audit is enabled:
   ```powershell
   Connect-ExchangeOnline
   Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled
   ```
   Expected: `True`. If `False`, escalate to Entra Global Admin.

2. Verify Copilot audit events are flowing:
   ```powershell
   Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
       -RecordType CopilotInteraction -ResultSize 5
   ```
   If zero results, verify user license assignments.

3. Check license entitlement:
   - Microsoft 365 E5 or E5 Compliance add-on required for Audit Premium
   - E3 tenants receive Audit Standard with 180-day default retention
   - Purview Audit 10-Year Retention add-on required for 10-year retention

**Resolution:**

1. If audit is disabled: `Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true` (requires Entra Global Admin)
2. If license gap: assign E5 or E5 Compliance licenses to users interacting with governed agents
3. If events are delayed: audit events may take 60–90 minutes to appear; wait and retry
4. Review [Control 1.7 — Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for complete audit configuration

**Escalation Path:** Purview Audit Admin → Entra Global Admin → Microsoft Support (if events still not flowing after 24 hours with valid licenses)

---

### Retention Policy Gaps

**Symptom:** Retention labels are not being applied to agent governance records, or records are being deleted before the required retention period expires.

**Likely Cause:**

- Retention label policy is not published to the AI Governance SharePoint site
- Retention label policy is in simulation mode (not enforcing)
- Auto-labeling policy conditions do not match document content
- A deletion policy is overriding the retention policy (policy precedence conflict)

**Diagnostic Steps:**

1. Verify retention label policy status:
   ```powershell
   Connect-IPPSSession -ShowBanner:$false
   Get-RetentionCompliancePolicy | Where-Object { $_.Name -like '*FSI*' -or $_.Name -like '*AI*' } |
       Select-Object Name, Mode, Enabled, SharePointLocation
   ```
   Verify `Enabled = True` and `Mode = Enforce` (not `Simulate`).

2. Verify labels are published and visible:
   - Navigate to a governed library > upload a document > check if FSI-Agent labels appear in the retention label dropdown
   - If labels do not appear: the policy may still be propagating (up to 7 days)

3. Check for conflicting policies:
   ```powershell
   Get-RetentionCompliancePolicy | Select-Object Name, Mode, Enabled, Priority |
       Sort-Object Priority
   ```
   Lower priority numbers take precedence. A deletion-only policy with higher priority may override retention.

**Resolution:**

1. If policy is in simulation mode: edit the policy in Purview and switch to **Enforce** mode
2. If not published to the site: edit the policy and add the AI Governance SharePoint site URL
3. If propagation delay: wait 7 days after publishing; if still not visible, recreate the policy
4. If policy conflict: adjust policy priority or modify the conflicting policy scope to exclude AI Governance libraries

**Escalation Path:** Purview Records Manager → Purview Compliance Admin → Microsoft Support

---

### Retention Conflicts Between Labels

**Symptom:** Multiple retention labels apply conflicting retention periods to the same content, or a user-applied label conflicts with an auto-applied label.

**Likely Cause:**

- Multiple auto-labeling policies target the same content
- A user manually applied a label with a shorter retention period than the auto-labeling policy intended
- The tenant has overlapping retention policies from different governance programs

**Diagnostic Steps:**

1. Check which label is currently applied to the document:
   - Open document properties in SharePoint > **Retention label** column
   - Note the label name and whether it was auto-applied or manually applied

2. Review auto-labeling policies:
   ```powershell
   Get-AutoSensitivityLabelPolicy | Where-Object { $_.Name -like '*FSI*' -or $_.Name -like '*Agent*' } |
       Select-Object Name, ApplySensitivityLabel, Mode
   ```

3. Review retention label precedence rules in [Microsoft Learn: Retention label precedence](https://learn.microsoft.com/en-us/purview/retention#the-principles-of-retention-or-what-takes-precedence)

**Resolution:**

1. Microsoft Purview applies the **retention wins over deletion** principle: if one label retains and another deletes, retention takes precedence
2. For conflicting retention periods: the **longer retention period** takes precedence
3. If a record label has been applied: it cannot be removed or replaced with a non-record label
4. Adjust auto-labeling policy conditions to avoid overlapping targeting

**Escalation Path:** Purview Records Manager → Purview Compliance Admin → Legal/Compliance Officer (for regulatory interpretation)

---

## Document Library and Metadata Issues

### Solution Layer Drift

**Symptom:** Agent configurations in Microsoft Copilot Studio do not match the documented configuration in the governance library, or solution layers show unauthorized changes.

**Likely Cause:**

- Agent was modified directly in the environment without following the change management process (per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md))
- Solution was imported from a different environment with different configurations
- Unmanaged customizations override managed solution layers

**Diagnostic Steps:**

1. In **Power Platform Admin Center** > **Environments** > select environment > **Solutions**:
   - Review solution history for the agent's solution
   - Check for unmanaged layers above the managed solution layer

2. Compare the agent's current configuration against the governance record:
   - Export the current agent definition from Copilot Studio
   - Compare against the last documented version in the `AgentConfigurations` library

3. Check Dataverse audit logs for the environment:
   ```powershell
   # Requires Windows PowerShell 5.1 (Desktop edition)
   Add-PowerAppsAccount
   Get-AdminPowerAppEnvironment -EnvironmentName '<env-id>' |
       Select-Object DisplayName, @{N='AuditEnabled';E={$_.Properties.isAuditEnabled}}
   ```

**Resolution:**

1. If unmanaged layer exists: remove the unmanaged customization and reimport the managed solution
2. If configuration drift detected: document the drift, determine root cause, update the governance record with the current state
3. Implement [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) change management procedures to prevent future drift
4. For Zone 3: flag any undocumented changes as a compliance finding in the next audit

**Escalation Path:** Power Platform Admin → Environment Admin → AI Governance Lead → Compliance Officer (if regulatory impact)

---

### Version History Loss

**Symptom:** SharePoint document version history is missing or truncated, or previous versions of governance documents cannot be recovered.

**Likely Cause:**

- Version history limits were set too low and older versions were automatically purged
- A library administrator disabled versioning after documents were created
- The document library was recreated or migrated without version history preservation
- Site collection storage limits caused version trimming

**Diagnostic Steps:**

1. Check versioning settings:
   - Navigate to the library > **Settings** > **Versioning settings**
   - Verify **Create a version each time you edit a file** = Yes
   - Verify version limit is ≥ 500 major versions

2. Check if version history exists for a specific document:
   - Navigate to the document > **⋮** > **Version history**
   - If versions are missing, check the recycle bin

3. Check storage quotas:
   ```powershell
   Connect-PnPOnline -Url $SiteUrl -Interactive
   Get-PnPSite -Includes Usage | Select-Object -ExpandProperty Usage |
       Select-Object Storage, StoragePercentageUsed
   ```

**Resolution:**

1. If versioning is disabled: re-enable versioning in library settings (this does not restore deleted versions)
2. If version limit is too low: increase to ≥ 500 major versions
3. If versions were purged: check the site collection recycle bin (first-stage and second-stage) for recoverable items
4. If storage limits are the cause: request a storage quota increase from the SharePoint Admin
5. Preventive: configure a scheduled export of critical governance documents to the WORM storage container

**Escalation Path:** SharePoint Admin → SharePoint Site Collection Admin → Microsoft Support (if recycle bin restoration needed)

---

### Metadata Schema Not Applied

**Symptom:** AI Governance site columns do not appear in document libraries, or users cannot populate required metadata fields when uploading documents.

**Likely Cause:**

- Site columns were created but not added to the specific library
- Content types are not enabled on the library
- The site column group was created at the wrong scope (site vs. hub vs. tenant)

**Diagnostic Steps:**

1. Verify site columns exist at the site level:
   ```powershell
   Connect-PnPOnline -Url $SiteUrl -Interactive
   Get-PnPField | Where-Object { $_.Group -eq 'AI Governance' } |
       Select-Object InternalName, Title, TypeDisplayName
   ```

2. Verify columns are added to each library:
   ```powershell
   $libs = @('AgentConfigurations','InteractionLogs','GovernanceDecisions')
   foreach ($lib in $libs) {
       $fields = Get-PnPField -List $lib | Where-Object { $_.Group -eq 'AI Governance' }
       Write-Host "$lib : $($fields.Count) AI Governance columns" -ForegroundColor Cyan
   }
   ```

3. If content types are used, verify they are enabled:
   - Library > **Settings** > **Advanced settings** > **Allow management of content types** = Yes

**Resolution:**

1. If columns exist at site level but not in library: add them via **Library settings** > **Add from existing site columns** > select **AI Governance** group
2. If content types are not enabled: enable content type management in advanced library settings
3. If columns were created at wrong scope: recreate at the site level
4. Verify columns with PowerShell after fix:
   ```powershell
   foreach ($lib in $RequiredLibraries) {
       Add-PnPField -List $lib -Field 'AgentID' -ErrorAction SilentlyContinue
       Add-PnPField -List $lib -Field 'DocCategory' -ErrorAction SilentlyContinue
       Add-PnPField -List $lib -Field 'ClassificationDate' -ErrorAction SilentlyContinue
   }
   ```

**Escalation Path:** SharePoint Admin → SharePoint Site Collection Admin

---

## Export and Evidence Issues

### Export Failures

**Symptom:** PowerShell evidence export scripts fail with errors, CSV files are empty, or the evidence manifest is incomplete.

**Likely Cause:**

- Insufficient permissions for the connected session
- Module version mismatch (PnP.PowerShell v1 vs. v2 breaking changes)
- Session timeout during long-running exports
- Output path does not exist or has insufficient write permissions

**Diagnostic Steps:**

1. Verify the current PowerShell session:
   ```powershell
   Get-PnPConnection | Select-Object Url, ConnectionType
   Get-ConnectionInformation | Where-Object { $_.ConnectionUri -like '*compliance*' }
   ```

2. Verify module version:
   ```powershell
   Get-Module PnP.PowerShell -ListAvailable | Select-Object Name, Version
   Get-Module ExchangeOnlineManagement -ListAvailable | Select-Object Name, Version
   ```

3. Verify output directory exists and is writable:
   ```powershell
   $EvidenceRoot = 'C:\fsi-evidence\2.13'
   Test-Path $EvidenceRoot
   New-Item -Path (Join-Path $EvidenceRoot 'test.txt') -ItemType File -Force |
       Remove-Item -Force
   ```

4. Check for session timeout:
   - If the session has been open for > 60 minutes, the token may have expired
   - Reconnect: `Connect-PnPOnline -Url $SiteUrl -Interactive`

**Resolution:**

1. If permission error: verify the signed-in account has SharePoint Admin + Purview Records Manager roles
2. If PnP v1 → v2 issue: PnP.PowerShell v2 requires Entra app registration with explicit consent; follow the migration guide
3. If session timeout: reconnect before each major export section
4. If output path issue: ensure `C:\fsi-evidence\2.13` exists; create with `New-Item -ItemType Directory -Path $EvidenceRoot -Force`
5. If CSV is empty: verify the pipeline filter matches data (e.g., `Where-Object { $_.Name -like 'FSI-Agent*' }` — check naming convention)

**Escalation Path:** M365 administrator running scripts → SharePoint Admin (permission issues) → Microsoft Support (module bugs)

---

### Evidence Integrity Issues

**Symptom:** SHA-256 hashes in the evidence manifest do not match the current file hashes, indicating potential tampering or unintended modification.

**Likely Cause:**

- Evidence files were opened and modified (even accidentally) after manifest creation
- Anti-virus software modified file metadata
- File was re-exported, overwriting the original
- The manifest was not finalized before files were moved or copied

**Diagnostic Steps:**

1. Run the integrity verification script:
   ```powershell
   $manifest = Import-Csv 'C:\fsi-evidence\2.13\manifest-2.13-{stamp}.csv'
   foreach ($entry in $manifest) {
       if (Test-Path $entry.FullPath) {
           $currentHash = (Get-FileHash -Path $entry.FullPath -Algorithm SHA256).Hash
           $match = $currentHash -eq $entry.SHA256
           Write-Host "[$($entry.File)] Match: $match — Expected: $($entry.SHA256) — Current: $currentHash"
       } else {
           Write-Host "[$($entry.File)] MISSING" -ForegroundColor Red
       }
   }
   ```

2. Check file modification timestamps:
   ```powershell
   Get-ChildItem 'C:\fsi-evidence\2.13' | Select-Object Name, LastWriteTime, Length |
       Sort-Object LastWriteTime -Descending
   ```

3. Compare modification timestamps against the manifest creation timestamp

**Resolution:**

1. If files were accidentally modified: re-run the export scripts to generate fresh evidence and a new manifest
2. If anti-virus modified files: add `C:\fsi-evidence` to the anti-virus exclusion list (with IT Security approval)
3. If the evidence is needed for an active examination: document the integrity discrepancy and provide both the original manifest and the re-generated evidence
4. Preventive: copy evidence files to read-only storage (WORM container) immediately after manifest creation

**Escalation Path:** AI Governance Lead → Compliance Officer → Legal (if evidence integrity is questioned during an examination)

---

## Permission and Access Issues

### Permission Errors

**Symptom:** Users receive "Access Denied" when attempting to upload governance documents, or administrators cannot modify library settings or retention configurations.

**Likely Cause:**

- User is not a member of the AI Governance SharePoint site
- Library has unique permissions that exclude the user
- Retention label prevents modification (record or regulatory record label applied)
- Purview role assignment is missing or expired (PIM time-bound elevation)

**Diagnostic Steps:**

1. Check user's site permissions:
   ```powershell
   Connect-PnPOnline -Url $SiteUrl -Interactive
   Get-PnPUser | Where-Object { $_.Email -like '*user@contoso*' } |
       Select-Object Title, Email, LoginName
   ```

2. Check library-level permissions:
   - Navigate to library > **Settings** > **Permissions for this document library**
   - Check if the library has unique permissions or inherits from the site

3. Check if a record label is blocking modification:
   - If the document has a record label, it cannot be edited or deleted until the retention period expires
   - Check the label: document properties > **Retention label** column

4. Verify Purview role assignments:
   ```powershell
   Connect-MgGraph -Scopes 'RoleManagement.Read.Directory'
   Get-MgRoleManagementDirectoryRoleAssignment -Filter "principalId eq '<user-object-id>'" |
       Select-Object RoleDefinitionId, DirectoryScopeId
   ```

**Resolution:**

1. If site membership issue: add the user to the AI Governance site owners or members group
2. If unique permissions: grant the user appropriate permissions on the specific library
3. If record label blocking edit: this is working as designed — create a new version of the document instead of editing the locked version
4. If PIM elevation expired: re-activate the Purview Records Manager or Purview Compliance Admin role in PIM
5. If Purview role missing: assign via Entra ID > **Roles and administrators** (requires Entra Privileged Role Admin)

**Escalation Path:** SharePoint Admin → Entra Privileged Role Admin → Purview Compliance Admin

---

### Cross-Site Search Failures

**Symptom:** Content Search or eDiscovery does not return expected agent records from the AI Governance site, or search results are incomplete.

**Likely Cause:**

- Search index has not yet crawled the content (indexing delay)
- The search scope does not include the AI Governance site
- Documents are in a format that cannot be indexed (e.g., encrypted, password-protected)
- The user running the search lacks eDiscovery permissions

**Diagnostic Steps:**

1. Verify the content is indexed:
   - Upload a test document with unique text to the AI Governance site
   - Wait 15–30 minutes for indexing
   - Search for the unique text using SharePoint search
   - If not found, force a crawl request (SharePoint Admin)

2. Verify eDiscovery scope:
   - In Purview > **eDiscovery** > create a test search
   - Set location to include the AI Governance site
   - Verify results include content from all governed libraries

3. Check for indexing errors:
   ```powershell
   Connect-PnPOnline -Url $SiteUrl -Interactive
   Get-PnPSiteSearchKeywords  # Check for excluded terms
   ```

**Resolution:**

1. If indexing delay: wait 30 minutes after upload; for bulk uploads, allow up to 24 hours
2. If scope issue: add the AI Governance site URL explicitly to the search or eDiscovery scope
3. If format issue: convert to indexable formats (DOCX, PDF, XLSX) or add metadata to enable discovery
4. If permission issue: assign eDiscovery Manager or eDiscovery Administrator role in Purview per [Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)

**Escalation Path:** SharePoint Admin → Purview eDiscovery Roles → Microsoft Support (if indexing failures persist)

---

## SEC 17a-4 Compliance Issues

### WORM Storage Misconfiguration

**Symptom:** Blobs in the immutable storage container can be deleted or modified, or the time-based retention policy is not locked.

**Likely Cause:**

- The time-based retention policy was created but not locked
- The container was created without immutability configured
- Blob versioning is not enabled, allowing overwrites
- The storage account is using a tier that does not support immutability

**Diagnostic Steps:**

1. In **Azure Portal** > **Storage accounts** > select account > **Containers** > select container:
   - Check **Access policy** > **Immutable blob storage**
   - Verify a time-based retention policy exists
   - Check if the policy is **Locked** (shows a lock icon)

2. Test immutability:
   - Attempt to delete a blob in the container via Azure Portal
   - Expected: deletion blocked with error message

3. Verify blob versioning:
   - **Storage account** > **Data protection** > **Enable versioning for blobs** should be checked

**Resolution:**

1. If policy exists but is unlocked: **carefully consider locking** — this is irreversible. Verify the retention period is correct (≥ 2190 days) before locking. Obtain Compliance Officer approval.
2. If no policy exists: create a time-based retention policy on the container (see Portal Walkthrough Step 11)
3. If blob versioning is disabled: enable it in storage account Data protection settings
4. If wrong storage tier: ensure the account uses Standard or Premium tier with immutability support

!!! danger "Policy locking is irreversible"
    Once a time-based retention policy is locked, it cannot be unlocked, shortened, or deleted. The container cannot be deleted until all blobs in it have expired. Test in a non-production environment first. Organizations should verify this meets their operational and regulatory requirements before proceeding.

**Escalation Path:** Azure Storage Account Owner → Compliance Officer (approval) → Legal (if regulatory interpretation needed)

---

### Audit-Trail Alternative Gaps

**Symptom:** The firm is relying on the SEC 17a-4(f) audit-trail alternative but documentation is incomplete, or the DEO representation / DTP undertaking has lapsed.

**Likely Cause:**

- The Designated Executive Officer (DEO) representation was not filed or has expired
- The Designated Third Party (DTP) undertaking was not executed
- The independent records-management assessment was not conducted
- Serialized indexing is not implemented in the electronic recordkeeping system

**Diagnostic Steps:**

1. Review the firm's WSPs for the audit-trail alternative section
2. Verify the DEO representation or DTP undertaking is current and on file
3. Verify the Cohasset Associates (or equivalent) attestation is current
4. Review the electronic recordkeeping system's serialized indexing capability
5. Confirm the system maintains a complete time-stamped audit trail of all original records and modifications

**Resolution:**

1. If DEO/DTP documentation is missing: engage legal counsel to prepare and file the required representation or undertaking per SEC 17a-4(f)(3)(vii)
2. If attestation has lapsed: engage Cohasset Associates (or equivalent assessor) for a current attestation
3. If serialized indexing is not implemented: work with the recordkeeping system vendor to enable serialized indexing
4. If audit trail is incomplete: implement modification tracking and verifying records capability
5. Document all remediation actions in the firm's compliance register

**Escalation Path:** Purview Records Manager → Compliance Officer → Legal → External assessor (Cohasset or equivalent)

---

## Escalation Matrix

| Issue Category | Level 1 | Level 2 | Level 3 | Level 4 |
|---|---|---|---|---|
| SharePoint site/library | SharePoint Admin | SharePoint Site Collection Admin | Entra Global Admin | Microsoft Support |
| Retention labels/policies | Purview Records Manager | Purview Compliance Admin | Entra Global Admin | Microsoft Support |
| Audit log gaps | Purview Audit Admin | Entra Global Admin | Microsoft Support | — |
| SEC 17a-4 storage | Azure Storage Account Owner | Compliance Officer | Legal | External assessor |
| Permission issues | SharePoint Admin | Entra Privileged Role Admin | Entra Global Admin | — |
| Agent versioning/PPAC | Power Platform Admin | Environment Admin | Microsoft Support | — |
| Regulatory interpretation | AI Governance Lead | Compliance Officer | Legal | External counsel |

---

## Known Limitations

| Limitation | Impact | Workaround |
|---|---|---|
| Auto-labeling processing delay | New documents may take 24–48 hours to receive auto-applied labels | Apply labels manually for time-sensitive records; use simulation mode to test before enforcing |
| WORM policy lock is irreversible | Cannot shorten retention period or delete the container after locking | Test thoroughly in non-production before locking; plan retention period with buffer |
| Retention label publishing delay | Labels may take up to 7 days to appear in SharePoint libraries after policy publishing | Plan a 1-week buffer between policy creation and expected label availability |
| Search indexing delay | Newly uploaded documents are not immediately searchable | Allow 15–30 minutes for indexing; for bulk uploads, allow up to 24 hours |
| Cross-site eDiscovery complexity | Searching across multiple libraries requires eDiscovery cases | Use Purview eDiscovery for comprehensive cross-library search per [Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) |
| PnP.PowerShell v2 requires app registration | v2 breaking change from v1; cannot silently upgrade | Register an Entra app with explicit consent before upgrading; see FSI PowerShell baseline |
| Regulatory record labels are permanent | Cannot remove or replace regulatory record labels once applied | Use regulatory record labels only for content with clear, confirmed regulatory retention requirements |
| Copilot Studio publish history is not exportable via API | No programmatic export of agent publish history | Manual screenshot capture; document version via solution history if agent is in a managed solution |
| PowerApps Administration module requires Desktop edition | Module does not work in PowerShell 7 | Run PPAC-related scripts in Windows PowerShell 5.1; use the PSEdition guard from the baseline |

---

[Back to Control 2.13](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
