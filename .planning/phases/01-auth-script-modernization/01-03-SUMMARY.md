---
phase: 1
plan: 3
status: Complete
completed: 2026-02-10
---

# Plan 01-03 Summary: Script Hardening (AUTH-03)

## Status: Complete

All 7 tasks completed. The four DEC extraction scripts have been modernized with `#Requires` statements, Azure Key Vault credential retrieval via DECClient.psm1, structured error handling, parameter validation, comment-based help, and updated framework playbooks.

## Task Completion

### Task 1: Add #Requires Statements to All Scripts ✅

- `Export-CopilotDenyEvents.ps1`: `#Requires -Version 7.0` + `#Requires -Modules @{ ModuleName="ExchangeOnlineManagement"; ModuleVersion="3.0.0" }`
- `Export-DlpCopilotEvents.ps1`: `#Requires -Version 7.0` + `#Requires -Modules @{ ModuleName="ExchangeOnlineManagement"; ModuleVersion="3.0.0" }`
- `Export-RaiTelemetry.ps1`: Verified existing `#Requires` from Plan 01-01 (correct); no changes needed to `#Requires` lines
- `Invoke-DailyDenyReport.ps1`: `#Requires -Version 7.0` + `#Requires -Modules @{ ModuleName="Az.Accounts"; ModuleVersion="3.0.0" }, @{ ModuleName="Az.KeyVault"; ModuleVersion="5.0.0" }, @{ ModuleName="ExchangeOnlineManagement"; ModuleVersion="3.0.0" }`
- All `#Requires` use version-pinned `@{ ModuleName=...; ModuleVersion=... }` syntax
- All `#Requires` appear before any other code (after comment header)

### Task 2: Refactor Credential Handling to Key Vault ✅

- Zero occurrences of `ConvertTo-SecureString ... -AsPlainText -Force` in any script
- Zero occurrences of inline `$password`, `$apiKey`, or `Get-Credential`
- `Export-CopilotDenyEvents.ps1`: Uses `-KeyVaultName` parameter; passes to `Connect-DECExchangeOnline` which retrieves EXO credentials from Key Vault
- `Export-DlpCopilotEvents.ps1`: Same pattern as CopilotDenyEvents
- `Export-RaiTelemetry.ps1`: Uses `-KeyVaultName` and `-SecretName`; passes to `Connect-DECAppInsights` for Key Vault retrieval
- `Invoke-DailyDenyReport.ps1`: Centralizes Key Vault configuration via single `-KeyVaultName` parameter; passes to `Connect-DECServices` and sub-scripts
- Key Vault secret requirements documented in `.NOTES` for all scripts

### Task 3: Refactor Scripts to Use DECClient.psm1 ✅

- All 4 scripts import DECClient: `Import-Module "$PSScriptRoot/private/DECClient.psm1" -Force`
- `Export-CopilotDenyEvents.ps1`: Uses `Connect-DECExchangeOnline` with splatted parameters
- `Export-DlpCopilotEvents.ps1`: Uses `Connect-DECExchangeOnline` with splatted parameters
- `Export-RaiTelemetry.ps1`: Uses `Connect-DECAppInsights` and `Invoke-DECAppInsightsQuery`; removed inline `New-ErrorResult`, `Get-AppInsightsToken`, and manual REST calls
- `Invoke-DailyDenyReport.ps1`: Uses `Connect-DECServices -Services @('ExchangeOnline','AppInsights')` for master connection validation

### Task 4: Add Structured Error Handling ✅

- All major operations wrapped in try/catch blocks
- Error results: `[PSCustomObject]@{ Status = 'Error'; ErrorType; Message; Script; Timestamp }`
- Success results: `[PSCustomObject]@{ Status = 'Success'; EventCount; OutputPath; Duration; Timestamp }`
- `$ErrorActionPreference = 'Stop'` set at script level in all 4 scripts
- `Write-Error` for terminating errors, `Write-Warning` for recoverable issues
- `-Verbose` checkpoints at each operation phase (connect, extract, export)
- `[System.Diagnostics.Stopwatch]` used for duration tracking in all scripts

### Task 5: Add Parameter Validation ✅

- All scripts have `[CmdletBinding()]` attribute
- All string parameters have `[ValidateNotNullOrEmpty()]`
- `-DaysBack` parameters have `[ValidateRange(1, 90)]`
- `-OutputPath` parameters have `[ValidateScript({ Test-Path (Split-Path $_) })]`
- `-OutputFormat` parameter added to all extraction scripts: `[ValidateSet('CSV','JSON')]`
- `Invoke-DailyDenyReport.ps1`: Has `[switch]$DryRun` parameter
- Optional `-CertificateThumbprint` parameter on EXO scripts for certificate-based auth

### Task 6: Add Script Help Comments ✅

- All 4 scripts have `.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER`, `.EXAMPLE`, `.NOTES`
- `.NOTES` includes: version, framework version, Key Vault secrets, Azure RBAC roles, module dependencies
- `.EXAMPLE` shows both interactive and automated (Azure Automation) invocation patterns
- Help text uses FSI hedged language ("supports compliance", "aids in") — no overclaims

### Task 7: Update Framework Playbooks ✅

- `purview-audit-extraction.md`: Added Entra ID prerequisites section; replaced v1.x inline script with modernized version using `#Requires`, `DECClient`, Key Vault; added deprecation warning for legacy auth
- `dlp-event-extraction.md`: Added Entra ID prerequisites section; replaced v1.x inline script with modernized version using `#Requires`, `DECClient`, Key Vault; added deprecation warning for legacy auth
- `deployment-guide.md`: Replaced service account pattern with App Registration; replaced `ExoServicePassword`/`AppInsightsApiKey` Key Vault secrets with `sp-exchangeonline`/`sp-appinsights`; removed `ConvertTo-SecureString -AsPlainText -Force`; added Key Vault Prerequisites section; added DECClient module deployment step; updated orchestrator runbook with DECClient pattern; updated troubleshooting table; updated footer version
- All three playbooks updated from `v1.2 - January 2026` to `v1.2.38 - February 2026`
- `mkdocs build --strict` passes (exit code 0)
- `python scripts/verify_controls.py` passes (62 controls valid)

## Commits

| Hash | Message |
|------|---------|
| `227e7d5` | `docs(dec): modernize DEC playbooks with Entra ID auth, DECClient, and Key Vault patterns` |

Note: Script files are under `maintainers-local/solutions-staging/` which is gitignored. These files are staged locally for transfer to the FSI-AgentGov-Solutions repository.

## File Manifest

| File | Action | Status |
|------|--------|--------|
| `maintainers-local/solutions-staging/deny-event-correlation-report/scripts/Export-CopilotDenyEvents.ps1` | Created | Local (gitignored) |
| `maintainers-local/solutions-staging/deny-event-correlation-report/scripts/Export-DlpCopilotEvents.ps1` | Created | Local (gitignored) |
| `maintainers-local/solutions-staging/deny-event-correlation-report/scripts/Invoke-DailyDenyReport.ps1` | Created | Local (gitignored) |
| `maintainers-local/solutions-staging/deny-event-correlation-report/scripts/Export-RaiTelemetry.ps1` | Modified | Local (gitignored) |
| `docs/playbooks/advanced-implementations/deny-event-correlation-report/purview-audit-extraction.md` | Modified | Committed |
| `docs/playbooks/advanced-implementations/deny-event-correlation-report/dlp-event-extraction.md` | Modified | Committed |
| `docs/playbooks/advanced-implementations/deny-event-correlation-report/deployment-guide.md` | Modified | Committed |

## Decisions Made

1. **Local error helper per script:** Each script has its own `New-ErrorResult` function with a `Script` field, since `New-DECErrorResult` in DECClient.psm1 is a private function (not exported). This gives script-specific error attribution.

2. **OutputPath default set after param block:** Rather than using a default value with format interpolation in the param declaration (which would lock the extension), the default is computed after the param block based on `-OutputFormat`. This allows the file extension to match the chosen format.

3. **EXO scripts don't require Az.* modules in #Requires:** Following the plan's specification, the two EXO scripts only declare `ExchangeOnlineManagement` in `#Requires`. The Az.Accounts and Az.KeyVault dependencies are indirect (via DECClient when using Key Vault auth) and are documented in `.NOTES`.

4. **Orchestrator calls sub-scripts via `&` with splatting:** The orchestrator calls each extraction script as a child scope using `& "$PSScriptRoot\script.ps1" @params`. Each sub-script re-imports DECClient.psm1 and manages its own connections. This ensures each script is fully standalone while the orchestrator provides validation and coordination.

5. **Export-RaiTelemetry.ps1 version bumped to 2.1.0:** Since Plan 01-01 created the v2.0.0 version, this refactoring (adding DECClient, OutputFormat, removing inline auth) warranted a minor version bump to 2.1.0.

6. **`x-api-key` references kept in RAI script comments only:** The `.DESCRIPTION` and `.NOTES` in Export-RaiTelemetry.ps1 mention the deprecated x-api-key pattern for migration context. No functional code uses x-api-key.

7. **Deployment guide Key Vault secrets renamed:** Changed from `ExoServiceAccount`/`ExoServicePassword`/`AppInsightsApiKey` to `sp-exchangeonline`/`sp-appinsights` to reflect app registration (not user account) pattern and align with DECClient defaults.

## Discovered Work

1. **FSI-AgentGov-Solutions transfer:** All 4 scripts and the DECClient module need to be committed to the FSI-AgentGov-Solutions repository. Files are staged at `maintainers-local/solutions-staging/`.

2. **Azure Automation DECClient deployment:** The deployment guide references uploading DECClient.psm1 as a custom module to Azure Automation. The module may need packaging as a .zip with a module manifest (.psd1) for Automation Account import. This is Phase 2 work.

3. **Module re-import in orchestrator flow:** When the orchestrator calls sub-scripts with `Import-Module -Force`, it resets DECClient module state. Each sub-script re-authenticates independently. This is acceptable for daily runs but adds latency for multi-script orchestration. A future optimization could use `-Force:$false` conditional import.

## Verification Results

| Check | Result |
|-------|--------|
| No `ConvertTo-SecureString.*-AsPlainText` in scripts | ✅ Pass |
| No `Get-Credential` in scripts | ✅ Pass |
| No `x-api-key` in functional code | ✅ Pass (only in comments) |
| All 4 scripts have `#Requires -Version 7.0` | ✅ Pass |
| All 4 scripts import DECClient.psm1 | ✅ Pass |
| All 4 scripts have `[CmdletBinding()]` | ✅ Pass |
| All 4 scripts have `.SYNOPSIS` | ✅ Pass |
| All 4 scripts have `.DESCRIPTION` | ✅ Pass |
| All 4 scripts have `.PARAMETER` | ✅ Pass |
| All 4 scripts have `.EXAMPLE` | ✅ Pass |
| All 4 scripts have `.NOTES` | ✅ Pass |
| All 4 scripts have `$ErrorActionPreference = 'Stop'` | ✅ Pass |
| All 4 scripts have `-OutputFormat` `[ValidateSet('CSV','JSON')]` | ✅ Pass |
| `Invoke-DailyDenyReport.ps1` has `-DryRun` switch | ✅ Pass |
| `Connect-DECExchangeOnline` used in EXO scripts | ✅ Pass |
| `Connect-DECAppInsights` used in RAI script | ✅ Pass |
| `Invoke-DECAppInsightsQuery` used in RAI script | ✅ Pass |
| `Connect-DECServices` used in orchestrator | ✅ Pass |
| Framework playbooks updated | ✅ Pass |
| No `ConvertTo-SecureString` in deployment guide (except warning) | ✅ Pass |
| `mkdocs build --strict` | ✅ Pass (exit 0) |
| `python scripts/verify_controls.py` | ✅ Pass (62 controls valid) |
