# Control 3.7: PPAC Security Posture Assessment — Troubleshooting

> Common issues and resolutions for [Control 3.7](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md). Audience: M365 administrators in US financial services.

---

## Issue 1 — Security score stuck on "Calculating security score"

**Symptoms:** `PPAC > Security > Overview` displays "Calculating security score" indefinitely; recommendations list is empty or sparse.

**Most likely cause:** Tenant-level analytics is not enabled, or it was enabled less than 24 hours ago.

**Resolution:**

1. Open `PPAC > Settings > Tenant settings > Tenant-level analytics` and confirm the toggle is on. See [How do I turn on tenant-level analytics?](https://learn.microsoft.com/en-us/power-platform/admin/tenant-level-analytics).
2. If just enabled, wait up to **24 hours** before retesting.
3. Confirm signed-in identity has Power Platform Admin or Dynamics 365 Administrator role (Environment Admins do not see the tenant-wide score).
4. If still stuck after 24 hours, raise a Microsoft support case referencing tenant-level analytics ingestion.

---

## Issue 2 — Score did not change after remediation

**Symptoms:** A recommendation is now Completed but the headline score is unchanged.

**Likely causes and resolutions:**

1. **Score updates every 24 hours.** Wait one full update cycle and re-check.
2. **Total possible score changed.** Microsoft adds scored features periodically. Open Microsoft release notes for the period and document the model change in the posture report.
3. **Other features regressed simultaneously.** Compare the per-feature breakdown on Security > Overview against the prior posture report.
4. **Action applied to a non-Managed Environment.** Recommendations from the Actions page generally only score-improve when applied to Managed Environments. Convert in-scope environments and retest.

---

## Issue 3 — "Inline action" greyed out or shows lock icon

**Symptoms:** A recommendation cannot be remediated from the Actions page; a lock icon or "Managed Environments only" banner appears.

**Cause:** The affected environment is not a Managed Environment.

**Resolution:**

1. Convert the environment to Managed via `PPAC > Environments > [Environment] > Enable Managed Environments`. See [Control 2.1 — Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md).
2. Allow up to **72 hours** for the Actions page to populate full affected-resource detail.
3. If conversion is not appropriate (e.g., dev/test environment), apply the recommended setting manually via the environment Settings page and document under the Configuration Hardening Baseline.

---

## Issue 4 — PowerShell collector returns zero environments in a sovereign cloud

**Symptoms:** Script runs without error in GCC / GCC High / DoD but `Get-AdminPowerAppEnvironment` returns nothing — producing **false-clean** evidence.

**Cause:** `Add-PowerAppsAccount` was called without `-Endpoint`, so authentication landed on commercial endpoints.

**Resolution:**

1. Re-run the orchestrator with the correct `-Endpoint` parameter (`usgov`, `usgovhigh`, or `dod`). See [PowerShell baseline §3](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).
2. Add a guard at the top of every wrapper script to refuse to run if `-Endpoint` was not explicitly provided in non-commercial tenants.
3. Discard the false-clean evidence file from the manifest and re-collect.

---

## Issue 5 — PowerShell collector returns empty results in PowerShell 7

**Symptoms:** Cmdlets like `Get-AdminPowerAppEnvironment` and `Get-DlpPolicy` return nothing in PowerShell 7, but work in Windows PowerShell 5.1.

**Cause:** `Microsoft.PowerApps.Administration.PowerShell` is a Desktop-only module (PS 5.1). Under PS 7 it loads but silently produces empty results.

**Resolution:**

1. Run the collector under **Windows PowerShell 5.1 (Desktop)** only.
2. Keep the canonical edition guard in every script (PowerShell baseline §2):

    ```powershell
    if ($PSVersionTable.PSEdition -ne 'Desktop') {
        throw "Requires Windows PowerShell 5.1 (Desktop). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
    }
    ```

3. If you only have PS 7 available, use the Power Platform for Admin v2 connector in a Power Automate flow as an alternative.

---

## Issue 6 — Recommendation not appearing despite condition being met

**Symptoms:** A known trigger condition (e.g., environment with no security group) is present but no recommendation appears.

**Likely causes and resolutions:**

1. **Refresh frequency** — some recommendations refresh weekly, not real time. Wait up to 7 days.
2. **Sovereign cloud rollout lag.** Some recommendations roll out to GCC / GCC High / DoD on a delay. Confirm parity in [Power Platform US Government plans](https://learn.microsoft.com/en-us/power-platform/admin/microsoft-dynamics-365-government).
3. **Recommendation was previously dismissed.** Open `PPAC > Actions > Dismissed recommendations` and re-activate.
4. **Recommendation is Managed-only.** Some recommendations only enumerate affected resources for Managed Environments.

---

## Issue 7 — Defender for Cloud Apps AI agent inventory empty

**Symptoms:** `Defender > Cloud apps > AI agent inventory` is empty even though agents are deployed.

**Likely causes and resolutions:**

1. The AI agent inventory feature is in **preview** and rolls out by region — confirm availability in your tenant per [Microsoft Learn: AI agent inventory](https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-inventory).
2. The Power Platform connector in Defender for Cloud Apps must be enabled by an Entra Security Admin.
3. New agents take up to 24 hours to enumerate.

---

## Issue 8 — `Get-DlpPolicy` shape changed between module versions

**Symptoms:** Collector script throws on `.environments` or `.environmentType` property access; or `HasCoverage` calculation is wrong.

**Cause:** The `Get-DlpPolicy` return shape has shifted across `Microsoft.PowerApps.Administration.PowerShell` versions.

**Resolution:**

1. Pin the module to your CAB-approved version (PowerShell baseline §1).
2. Test the collector against the pinned version before each change window.
3. Update the `Get-Control37DlpCoverage` accessor logic to match the pinned version's return shape.

---

## Issue 9 — Audit logs not visible from PPAC

**Symptoms:** Following the audit-log link from the Security area returns no results.

**Likely causes and resolutions:**

1. **Dataverse auditing not enabled** for the environment — see [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).
2. **Unified audit log not enabled at the tenant level** — Purview Audit Admin to enable.
3. **Date range too narrow or recent activity not yet ingested** — allow up to 60 minutes for ingestion latency.
4. **Reader lacks Purview audit role** — assign `Purview Audit Reader` per the role catalog.

---

## Issue 10 — Evidence manifest fails SHA-256 verification

**Symptoms:** Re-hashing an archived JSON evidence file produces a different SHA-256 from the manifest.

**Likely causes and resolutions:**

1. **File was modified after collection.** Investigate as a chain-of-custody incident; re-collect and notify the AI Governance Lead.
2. **Encoding mismatch on re-hash.** The collector emits UTF-8 without BOM; verify your hashing tool reads bytes (not text) and is not normalizing line endings.
3. **Storage system rewrote the file** (e.g., antivirus quarantine touch, cloud sync re-upload). Move the evidence pipeline output directly into WORM storage to prevent post-hash modification.

---

## Diagnostic Commands

```powershell
# Confirm edition (must be Desktop / 5.1 for the collector)
$PSVersionTable

# Confirm environments visible (zero in sovereign tenants → wrong endpoint)
Get-AdminPowerAppEnvironment | Select-Object DisplayName, EnvironmentType, EnvironmentName

# Confirm DLP visibility
Get-DlpPolicy | Format-Table DisplayName, Type

# Confirm Managed Environment status
Get-AdminPowerAppEnvironment |
    Select-Object DisplayName,
                  @{N='IsManaged';E={$_.Internal.properties.governanceConfiguration.enableManagedEnvironment}},
                  @{N='HasSecurityGroup';E={[bool]$_.Internal.properties.linkedEnvironmentMetadata.securityGroupId}}

# Confirm tenant settings (note: cmdlet shape varies by module version)
Get-TenantSettings | ConvertTo-Json -Depth 5
```

---

## Escalation Path

| Issue Severity | Escalate To | Target Response |
|----------------|-------------|-----------------|
| Security area / Actions page completely unavailable | Microsoft Support (Sev A) + Power Platform Admin | 4 hours |
| Score calculation suspected incorrect after release | Microsoft Support (Sev B) + Power Platform Admin | 1 business day |
| Sovereign cloud false-clean evidence detected | AI Governance Lead + Compliance Officer | Immediate; halt evidence emission |
| Audit log gap suspected | Security Team + Purview Audit Admin | Immediate |
| Evidence integrity (SHA-256) mismatch | AI Governance Lead + Compliance Officer | Immediate; chain-of-custody incident |
| Recommendation not appearing as expected | Power Platform Admin | 2 business days |

---

[Back to Control 3.7](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
