# PowerShell Authoring Baseline for FSI Implementations

**Purpose:** Pre-flight requirements that apply to **every** PowerShell playbook in this framework. Read this **once** before running any control's PowerShell setup, and treat it as the canonical source for module versions, mutation safety, and evidence emission.

**Audience:** M365 administrators executing controls in production tenants subject to FINRA / SEC / GLBA / OCC / Fed SR 26-2 (formerly SR 11-7) / CFTC oversight.

---

## 1. Module Version Pinning (Non-Negotiable in Regulated Tenants)

Every `Install-Module` command in this framework should be pinned to a specific version that has been approved by your Change Advisory Board (CAB). Floating versions break reproducibility and can fail SOX 404 / OCC 2023-17 evidence requirements.

**Approved baseline (verify before each change window):**

| Module | Recommended Pinning Approach |
|---|---|
| `Microsoft.PowerApps.Administration.PowerShell` | Pin to a specific version verified against your tenant; check release notes for breaking changes between minor versions |
| `Microsoft.PowerApps.PowerShell` | Same baseline as Administration module |
| `Microsoft.Graph` | Pin minor version; meta-module pulls in 30+ sub-modules — pin all together |
| `ExchangeOnlineManagement` | Pin to a stable production release; avoid preview channels in regulated tenants |
| `PnP.PowerShell` | **Breaking change:** v2+ requires Entra app registration with explicit consent; do not silently upgrade from v1 |
| `MicrosoftTeams` | Pin and verify cmdlet surface; module renamed and refactored repeatedly |
| `Microsoft.Online.SharePoint.PowerShell` | Pin; some cmdlets behave differently between Windows PowerShell and PowerShell 7 |

**Canonical install pattern:**

```powershell
# REQUIRED: Replace <version> with the version approved by your CAB.
# DO NOT use -Force without -RequiredVersion in regulated tenants.
Install-Module -Name <ModuleName> `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense
```

**If a control playbook in this framework shows `Install-Module ... -Force` without `-RequiredVersion`, treat that as an authoring shortcut — substitute the canonical pattern above and record the pinned version in your change ticket.**

---

## 2. PowerShell Edition and Version Requirements

| Module | Supported Edition | Minimum Version |
|---|---|---|
| `Microsoft.PowerApps.Administration.PowerShell` | **Desktop only** (Windows PowerShell 5.1) | 5.1 |
| `Microsoft.PowerApps.PowerShell` | Desktop only | 5.1 |
| `Microsoft.Graph` | Core (PS 7+) | 7.2 LTS or 7.4 |
| `ExchangeOnlineManagement` | Both Desktop and Core | 5.1 / 7.2+ |
| `PnP.PowerShell` v2+ | **Core only** (PS 7+) | 7.2 |
| `MicrosoftTeams` | Both | 5.1 / 7.2+ |

**Required guard for Power Apps Administration cmdlets:**

```powershell
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop edition). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}
```

Without this guard, scripts run in PowerShell 7 silently fail or return empty results — producing **false-clean evidence**.

---

## 4. Mutation Safety: SupportsShouldProcess / -WhatIf / Snapshot

Any script that **changes tenant state** (creates / modifies / deletes role assignments, DLP policies, environments, agent settings, etc.) **must**:

1. Declare `[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]`.
2. Wrap each mutation in `if ($PSCmdlet.ShouldProcess(...))`.
3. Capture a **before-mutation snapshot** to disk for rollback evidence.
4. Use `Start-Transcript` to capture full session for audit.

**Canonical mutation wrapper:**

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string]$EnvironmentId,
    [string]$EvidencePath = ".\evidence"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
Start-Transcript -Path "$EvidencePath\transcript-$ts.log" -IncludeInvocationHeader

# Snapshot BEFORE mutating
$snapshot = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId
$snapshot | ConvertTo-Json -Depth 10 | Set-Content "$EvidencePath\before-$ts.json"

if ($PSCmdlet.ShouldProcess($EnvironmentId, "Modify environment setting")) {
    # mutation here
}

Stop-Transcript
```

**Always invoke first with `-WhatIf` before running for real.** This is the difference between an undo-able config change and a production incident.

---

## 5. Evidence Emission: SHA-256 Integrity

Audit-defensible evidence requires **content-integrity proofs**. Screenshots alone are not sufficient under SEC 17a-4(f) WORM requirements or FINRA 4511 record-keeping rules.

**Every script that produces evidence must:**

1. Emit JSON (machine-readable) **and** a human-readable summary.
2. Compute SHA-256 hash of each artifact.
3. Write a `manifest.json` listing `{file, sha256, bytes, generated_utc, script_version}`.
4. Land artifacts in storage configured for **WORM** (Microsoft Purview Data Lifecycle Management retention lock, or Azure Storage immutability policy).

**Canonical evidence emit:**

```powershell
function Write-FsiEvidence {
    param(
        [Parameter(Mandatory)] $Object,
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [string]$EvidencePath
    )
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $jsonPath = Join-Path $EvidencePath "$Name-$ts.json"
    $Object | ConvertTo-Json -Depth 20 | Set-Content -Path $jsonPath -Encoding UTF8
    $hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
    $manifestPath = Join-Path $EvidencePath "manifest.json"
    $manifest = @()
    if (Test-Path $manifestPath) { $manifest = @(Get-Content $manifestPath | ConvertFrom-Json) }
    $manifest += [PSCustomObject]@{
        file = (Split-Path $jsonPath -Leaf)
        sha256 = $hash
        bytes = (Get-Item $jsonPath).Length
        generated_utc = $ts
        script_version = $MyInvocation.MyCommand.Module.Version.ToString()
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
    return $jsonPath
}
```

---

## 6. Dataverse Compatibility for Power Apps Admin Cmdlets

The `*-AdminPowerAppEnvironmentRoleAssignment` cmdlets **only function on environments that do NOT have a Dataverse database**. On Dataverse-backed environments:

- `Get-AdminPowerAppEnvironmentRoleAssignment` returns empty (silent — no error)
- `Set-AdminPowerAppEnvironmentRoleAssignment` and `Remove-` throw **403 Forbidden**

For Dataverse environments, role administration must be performed via **Dataverse Security Roles** in the Power Platform Admin Center (PPAC) or via the Dataverse Web API, **not** these cmdlets.

**Required detection guard:**

```powershell
$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId
if ($env.CommonDataServiceDatabaseProvisioningState -eq 'Succeeded') {
    Write-Warning "Environment $EnvironmentId has Dataverse. Use PPAC Dataverse Security Roles, not Get/Set-AdminPowerAppEnvironmentRoleAssignment."
    return
}
```

**Filter property quirk:** `Get-AdminPowerAppEnvironmentRoleAssignment` returns the role in a property named `RoleName` with **spaces** (e.g., `"Environment Maker"`, `"System Administrator"`), not `RoleType` and not camel-case `"EnvironmentMaker"`. The corresponding `Set-` cmdlet accepts `-RoleName EnvironmentMaker` (no space). This Get/Set inconsistency is documented Microsoft behavior — verify on each module version.

---

## 7. Authoring Convention for Playbook Authors

When you contribute a new PowerShell playbook to this framework, the playbook **must**:

- Link to this baseline at the top.
- Use the canonical patterns from sections 1, 4, 5, and 6 instead of re-deriving them.
- Document any module-specific deviations explicitly.
- Pass the validation script (see `scripts/verify_controls.py`).

If you find a control playbook in this framework that does **not** follow this baseline, file an issue or open a PR — it is a regression.

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
