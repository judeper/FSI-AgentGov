# Troubleshooting: Control 1.26 - Agent File Upload and File Analysis Restrictions

**Last Updated:** May 2026
**Audience:** M365 administrators, Microsoft Copilot Studio agent authors, SOC analysts

This playbook is structured by **Symptom (H2) → Likely Cause and Resolution (H3)**. For each symptom, work through the resolution steps in order; each step is independently safe to skip if it does not apply.

---

## Quick-Reference Symptom Matrix

| Symptom | Likely Causes | Section |
|--------|---------------|---------|
| Runtime File Upload On but files not processed | Agent resides in CMK-enabled environment | [CMK No-Op](#symptom-runtime-file-upload-toggle-is-on-but-agent-doesnt-process-uploaded-files) |
| File Upload toggle not visible in agent settings | Permissions, agent version, regional rollout | [Toggle Not Visible](#symptom-file-upload-toggle-not-visible-in-agent-settings) |
| Agent still accepts uploads after toggle disabled | Unsaved change, stale cache, agent not republished | [Toggle Not Enforced](#symptom-agent-accepts-uploads-after-toggle-disabled) |
| Uploads silently fail when toggle is on | Per-agent allowlist mismatch, file size, environment-level (1.25) block | [Uploads Fail When Enabled](#symptom-uploads-fail-when-toggle-is-on) |
| Sensitivity labels not displayed in agent responses | Auto-labeling policy scope, source file unlabeled, propagation delay | [Labels Not Displayed](#symptom-sensitivity-labels-not-displayed-in-agent-responses-for-uploaded-knowledge-files) |
| DLP not triggering on sensitive content | Policy mode, scope, SIT version, latency | [DLP Not Triggering](#symptom-dlp-policy-not-triggering-on-uploaded-content) |
| Dataverse storage access too permissive | Default permissions, missing retention policy | [Dataverse Storage Hardening](#symptom-dataverse-storage-access-not-restricted-or-retention-missing) |
| Inventory script returns incomplete results | PSEdition, role | [Inventory Incomplete](#symptom-inventory-script-returns-incomplete-or-empty-results) |
| `Set-AdminPowerAppChatbot -FileUploadEnabled` rejected | Module version, schema not present | [API Surface Missing](#symptom-set-adminpowerappchatbot-fileuploadenabled-rejected) |

---

## Symptom: Runtime File Upload Toggle is On But Agent Doesn't Process Uploaded Files

### Cause: Agent resides in a Customer Managed Key (CMK)-enabled environment

This is documented Microsoft platform behaviour, not a configuration error.

1. Confirm the agent's environment has Customer Managed Keys (CMK) enabled: open *Power Platform Admin Center → Environments → \[Environment\] → Settings* and check for the CMK configuration
2. If CMK is enabled, the runtime File Upload toggle reads **On** in Copilot Studio but the agent will not process uploaded files (per [Microsoft Learn: Allow file input from users](https://learn.microsoft.com/en-us/microsoft-copilot-studio/image-input-analysis))
3. This behaviour is not configurable — it is an architectural constraint of CMK-enabled environments
4. **Governance action:** Document this as a compensating control gap in the agent's risk assessment. Zone 3 agents in CMK environments should treat the runtime File Upload capability as unavailable

> **Source:** Microsoft Learn (image-input-analysis): *"If your agent resides in a customer managed key enabled environment, adding files as input is allowed, but the agent doesn't process the files."*

---

## Symptom: File Upload Toggle Not Visible in Agent Settings

### Cause: Insufficient role on the agent or environment

1. Confirm the user holds **AI Administrator**, **Power Platform Admin**, or **Environment Maker + agent ownership**
2. Read-only roles (e.g., **Environment Reader**) see agent settings without the Security panel toggles

### Cause: Agent version below v8 or environment feature flag disabled

1. Open *Copilot Studio → \[Agent\] → Settings → Details* and confirm the agent runtime version
2. Open *PPAC → Environments → \[Environment\] → Settings → Features* and confirm Copilot features are enabled
3. If the toggle is missing across every agent in the environment, check tenant-level feature rollout — the per-agent File Upload toggle has rolled out progressively by region

### Cause: Tenant region pending rollout

1. Open the [Microsoft 365 Admin Center → Health → Message Center](https://admin.microsoft.com) and search for "Copilot Studio file upload"
2. If the feature is pending for your region, document the gap and apply environment-level controls (Control 1.25) as a temporary compensating measure

**Portal path:** *Copilot Studio → \[Agent\] → Settings → Generative AI → File processing capabilities → File uploads*

---

## Symptom: Agent Accepts Uploads After Toggle Disabled

### Cause: Toggle change not saved

1. Reopen *Settings → Generative AI → File processing capabilities* and confirm the toggle reads **Off**
2. If a **Save** button is highlighted, click it and re-test

### Cause: Agent not republished after toggle change

1. Most agent runtime configuration is enforced at publish time
2. Click **Publish** in the Copilot Studio editor and re-test after publish completes

### Cause: Stale browser session or cached configuration

1. Wait up to **15 minutes** for cache expiry
2. Test in a new private/incognito window or with a different test account

### Cause: Environment-level setting overriding per-agent state

1. Open *PPAC → Environments → \[Environment\] → Settings* and review tenant policies that may force file upload behavior
2. If an environment-level allowlist (Control 1.25) is permissive and the agent toggle change has not propagated, file the gap with Microsoft Support

---

## Symptom: Uploads Fail When Toggle is On

### Cause: File type not in the per-agent allowlist

1. Open *Settings → Generative AI → File processing capabilities → Allowed file types* and confirm the file's extension is listed
2. Add the extension if it matches the agent's documented purpose; otherwise the rejection is correct

### Cause: File type blocked at the environment level (Control 1.25)

1. Open *PPAC → Environments → \[Environment\] → Settings → Product → Privacy + Security*
2. Check the **blocked file extensions** and **blocked MIME types** lists
3. Per-agent allowlists cannot override environment-level blocks — this is intentional defense-in-depth

### Cause: File exceeds Microsoft platform limits

1. Confirm the file is within Microsoft Learn limits:
   - User-uploaded file at runtime (individual file size): **15 MB** (per [Allow file input from users](https://learn.microsoft.com/en-us/microsoft-copilot-studio/image-input-analysis))
   - User-uploaded text file at runtime (character limit, without code interpreter): **30,000 characters** per file
   - Maker-uploaded knowledge file: **up to 512 MB** (per [Copilot Studio quotas and limits](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas))
2. Reduce file size or split the document if it exceeds the limit

### Cause: Defender for Cloud Apps quarantined the file (Zone 3)

1. Open [Microsoft Defender XDR](https://security.microsoft.com) → **Cloud apps** → **Files** and search for the file name
2. If quarantined, verify the magic-byte inspection rule is intentional; if a false positive, refine the file policy
3. Restore the file only after verifying it is not a renamed executable

---

## Symptom: Sensitivity Labels Not Displayed in Agent Responses for Uploaded Knowledge Files

### Cause: Auto-labeling policy does not cover the Dataverse location

1. Open *Microsoft Purview → Information Protection → Auto-labeling policies*
2. Confirm a policy is in scope that covers the Dataverse environment where the agent's knowledge files are stored
3. If the Dataverse location is not enumerated, create or update the policy and allow up to **24 hours** for propagation

### Cause: Source file was not labeled before upload

1. Sensitivity label display in responses relies on labels already present on the file at the time of upload
2. Open the source location and confirm the file carries an explicit sensitivity label
3. For runtime-uploaded files, encourage end users to apply labels in the originating application before upload

### Cause: Sensitivity labels not published to relevant users

1. Open *Microsoft Purview → Information Protection → Label policies*
2. Confirm the labels are published to the user(s) uploading the files
3. Users without label policies will upload unlabeled files even when labels exist in the tenant

**Portal path:** *Microsoft Purview → Information Protection → Auto-labeling policies → \[Policy\] → Locations*

> **Note (preview feature):** Sensitivity label display in agent responses is a preview feature per Microsoft Learn. The documented behaviour is a per-response shield displaying the highest label of cited content — not an agent-level inherited property. Verify current GA status at [View sensitivity labels in agent responses](https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio) before relying on this for Regulated-zone attestation.

---

## Symptom: DLP Policy Not Triggering on Uploaded Content

### Cause: DLP policy not in Enforce mode

1. Open *Microsoft Purview → Data Loss Prevention → Policies → \[Policy\]*
2. Confirm the policy is **Enforce** (not **Test** or **Off**)

### Cause: Policy scope excludes the agent's environment

1. Open the policy and confirm the **Power Platform** location is included
2. Confirm the environment is not excluded by environment-group filter

### Cause: Sensitive Information Type (SIT) does not match the test data

1. The test file must contain content matching the SIT's regex and supporting evidence (e.g., US SSN SIT requires keyword proximity)
2. Use a synthetic test file built from the [Microsoft documented test patterns](https://learn.microsoft.com/en-us/purview/sit-defn-us-social-security-number) — never use real PII

### Cause: Reporting latency

1. DLP Activity Explorer can lag by several hours
2. Wait up to **24 hours** before declaring a failure
3. Check Microsoft Sentinel mirror tables (if configured) for faster signal

---

## Symptom: Dataverse Storage Access Not Restricted or Retention Missing

### Cause: Default environment permissions retained

1. Open *PPAC → Environments → \[Environment\] → Settings → Users + permissions → Security roles*
2. Review Dataverse security roles; remove any overly broad role assignments (e.g., "Basic User" with Organization-level read on knowledge tables)
3. Restrict access to required service principals and named admin security roles

### Cause: No Purview retention policy covers the Dataverse location

1. Open *Microsoft Purview → Data Lifecycle Management → Retention policies*
2. Add the Dataverse environment location to a retention policy that meets your record-keeping obligation (FINRA 4511: 6 years; SEC 17a-4(f): typically 6 years with WORM characteristics)
3. Enable **retention lock** if SEC 17a-4(f) WORM equivalence is required

### Cause: Dataverse auditing not enabled

1. Open *PPAC → Environments → \[Environment\] → Settings → Auditing* and confirm auditing is enabled
2. Confirm Microsoft Purview Audit (Standard or Premium) is enabled at the tenant level
3. Test by uploading a knowledge file and querying *Purview → Audit → Search* for the activity within 30 minutes

---

## Symptom: Inventory Script Returns Incomplete or Empty Results


### Cause: Script run on PowerShell 7 (Core) instead of Windows PowerShell 5.1 (Desktop)

1. `Microsoft.PowerApps.Administration.PowerShell` is **Desktop edition only**
2. Re-run from Windows PowerShell 5.1; the baseline guard will throw if Desktop edition is missing

### Cause: Insufficient role

1. Confirm the running account holds **Power Platform Admin** or **AI Administrator** at minimum
2. Run `Get-AdminPowerAppEnvironment | Measure-Object` as a smoke test

### Cause: Module out of date

```powershell
Get-Module -Name Microsoft.PowerApps.Administration.PowerShell -ListAvailable
# If outdated, pin to a CAB-approved version per the PowerShell baseline §1
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
    -RequiredVersion '<cab-approved-version>' -Scope CurrentUser -AllowClobber -AcceptLicense
```

---

## Symptom: `Set-AdminPowerAppChatbot -FileUploadEnabled` Rejected

### Cause: Module version does not expose the parameter

1. Run *Script 0 — Probe Cmdlet Surface* from the [PowerShell Setup](powershell-setup.md) playbook
2. If `FileUploadParamPresent = False`, your module version does not expose the schema this control depends on
3. Resolution paths (in order of preference):
    a. Upgrade the module to a CAB-approved version that includes `-FileUploadEnabled`
    b. Use the [Portal Walkthrough](portal-walkthrough.md) for manual configuration
    c. Open a Microsoft Support case to confirm parameter availability for your tenant tier

### Cause: API call returns 403 Forbidden

1. Confirm the running account holds **AI Administrator** or **Power Platform Admin**
2. Confirm the agent is in an environment the running account can administer
3. Some Dataverse-backed environments require Dataverse-side role assignment in addition to platform role — see [PowerShell Authoring Baseline §5](../../_shared/powershell-baseline.md)

---

## Escalation Path

1. **Copilot Studio Agent Author** — per-agent toggle, allowed-types list, agent publishing
2. **AI Administrator** — per-agent governance policy enforcement, allowlist standards, approval review
3. **Power Platform Admin** — environment settings, Dataverse access, DLP scope, feature flags
4. **Purview Compliance Admin** — DLP policy authoring, retention policy, sensitivity-label policy
5. **Purview Info Protection Admin** — auto-labeling policy scope and label publication
6. **SOC Analyst** — Defender XDR alerts, Sentinel queries, anomalous upload investigation
7. **Microsoft Support** — platform-level issues with file upload features, Dataverse storage, Defender for Cloud Apps file policies

---

## Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Maker-uploaded knowledge files with encryption (sensitivity labels or password protection) are not supported | Files marked Confidential/Highly Confidential or password-protected appear "Ready" but silently fail to serve knowledge responses (per Microsoft Learn) | Apply labels below the encrypted threshold; use unencrypted test files for knowledge upload testing; audit knowledge source files for encrypted content before upload |
| File Upload toggle is per-agent (no bulk UI) | Each agent must be configured individually in the portal | Use the PowerShell mutation script (Script 3) for bulk operations |
| Microsoft platform file size limits cannot be lowered per agent in the portal | Maker-uploaded knowledge files can be up to 512 MB | Enforce reductions via Defender for Cloud Apps file policies (Zone 3) |
| Dataverse environment settings are largely tenant-managed | Environment-level fine-grained access requires Dataverse security role configuration | Apply retention and access policies at the Purview / PPAC tier |
| Sensitivity-label inheritance flows from source files | Cannot apply labels at the agent level after upload | Enforce labeling at source via auto-labeling policies |
| Toggle changes may require agent republish | Settings may not take effect until republish completes | Republish the agent after every Security setting change |
| Propagation delay up to 15 minutes | Recent toggle changes may not be enforced immediately | Wait 15 minutes before declaring a regression |
| Defender for Cloud Apps file policies are near-real-time, not synchronous | Files may be briefly accessible before quarantine completes | Pair with PPAC environment-level blocks (Control 1.25) for fail-fast at the edge |
| Agent activity log column names vary by Sentinel connector version | KQL queries may need column adjustments | Verify schema against the connector version deployed in your tenant |

---

## Diagnostic Commands

### Check Agent File Upload Status (Single Environment)

```powershell
Get-AdminPowerAppChatbot -EnvironmentName "<environment-guid>" |
    Select-Object @{N='Agent';E={$_.Properties.DisplayName}},
                  @{N='FileUpload';E={$_.Properties.FileUploadEnabled}},
                  @{N='LastModifiedUtc';E={$_.Properties.LastModifiedTime}} |
    Format-Table -AutoSize
```

### Verify Module Installation and Version

```powershell
Get-Module -Name Microsoft.PowerApps.Administration.PowerShell -ListAvailable |
    Format-Table Name, Version, Path
```

### List All Environments Visible to Current Identity

```powershell
Get-AdminPowerAppEnvironment | Format-Table DisplayName, EnvironmentName, EnvironmentType
```

### Confirm Authentication and Role Access

```powershell
# A non-zero count confirms authentication landed in the right cloud
Get-AdminPowerAppEnvironment | Measure-Object
```

---

## Related Documentation

- [Microsoft Learn: Copilot Studio file upload knowledge source](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-file-upload)
- [Microsoft Learn: Copilot Studio — Allow file input from users](https://learn.microsoft.com/en-us/microsoft-copilot-studio/image-input-analysis)
- [Microsoft Learn: Power Platform Admin Center security overview](https://learn.microsoft.com/en-us/power-platform/admin/security/security-overview)
- [Microsoft Learn: Microsoft Dataverse security concepts](https://learn.microsoft.com/en-us/power-platform/admin/wp-security-cds)
- [Microsoft Learn: Microsoft Purview sensitivity labels](https://learn.microsoft.com/en-us/purview/sensitivity-labels)
- [Microsoft Learn: Auto-apply sensitivity labels](https://learn.microsoft.com/en-us/purview/apply-sensitivity-label-automatically)
- [PowerShell Authoring Baseline for FSI Implementations](../../_shared/powershell-baseline.md)

---

[Back to Control 1.26](../../../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)
---

*Updated: June 2026 | Version: v1.6.2 | UI Verification Status: Current*
