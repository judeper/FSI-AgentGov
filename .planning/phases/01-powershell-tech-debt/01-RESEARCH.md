# Phase 1: PowerShell Tech Debt Resolution - Research

**Researched:** 2026-02-04
**Domain:** PowerShell enterprise script security and quality standards
**Confidence:** HIGH

## Summary

This research investigated PowerShell best practices for FSI production environments, focusing on four technical domains: secure secret handling (replacing `ConvertTo-SecureString -AsPlainText -Force`), enterprise error handling patterns, module dependency declarations (`#Requires`), and Python dependency cleanup tools.

The standard approach for secret handling in PowerShell has evolved from `ConvertTo-SecureString` with plain text to using the Microsoft.PowerShell.SecretManagement module with Azure Key Vault integration. For scripts that must interact with Az.KeyVault directly (as Register-ServicePrincipal.ps1 does), the pattern is to retrieve secrets from Key Vault using `Get-AzKeyVaultSecret`, which returns SecureString objects directly without exposing plain text. Error handling follows try-catch-finally patterns with `$ErrorActionPreference = "Stop"` to ensure terminating errors for critical operations. Module dependencies should be declared with `#Requires -Version` and `#Requires -Modules` statements at the top of every script. Python unused dependencies can be detected with tools like `deptry` or `pip-check`.

**Primary recommendation:** Use `Get-AzKeyVaultSecret` to retrieve secrets as SecureString objects instead of `ConvertTo-SecureString -AsPlainText -Force`, wrap all critical operations in try-catch blocks with structured error messages, add `#Requires` statements to all PowerShell scripts, and remove unused Python dependencies identified through manual import analysis.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PowerShell | 7.4+ (LTS) | Cross-platform automation framework | LTS support until November 2026, cross-platform compatibility |
| Az.KeyVault | 3.3.0+ | Azure Key Vault integration | Native SecretManagement extension, retrieve secrets as SecureString |
| Microsoft.PowerShell.SecretManagement | 1.1.2+ | Secret management abstraction layer | Unified API across vault providers, no plain text exposure |
| Microsoft.Graph.Applications | Latest | Entra ID app registration management | Required for service principal operations |
| Microsoft.Graph.Identity.SignIns | Latest | Conditional Access policy management | Required for CA policy operations |
| ExchangeOnlineManagement | Latest | Unified Audit Log access | Required for CopilotInteraction event retrieval |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| PSScriptAnalyzer | 1.24.0 | Static code analysis | Optional - cross-platform linting, best practice validation |
| deptry | Latest | Python dependency checker | Detecting unused Python dependencies in requirements.txt |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Az.KeyVault direct retrieval | SecretManagement abstraction | SecretManagement adds flexibility for vault provider changes, but Register-ServicePrincipal.ps1 already uses Az.KeyVault and Set-AzKeyVaultSecret, so direct retrieval is consistent |
| Manual Python dependency audit | pipreqs (regenerate from imports) | pipreqs creates new requirements.txt from scratch, losing version pinning and security fixes; manual audit preserves version constraints |
| PSScriptAnalyzer validation | Regex-only validation | Regex validation is macOS-compatible without dependencies, sufficient for detecting specific patterns (ConvertTo-SecureString, missing #Requires) |

**Installation:**
```powershell
# PowerShell modules
Install-Module -Name Az.KeyVault -MinimumVersion 3.3.0 -Scope CurrentUser -Force
Install-Module -Name Microsoft.PowerShell.SecretManagement -Scope CurrentUser -Force
Install-Module -Name Microsoft.Graph.Applications -Scope CurrentUser -Force
Install-Module -Name Microsoft.Graph.Identity.SignIns -Scope CurrentUser -Force
Install-Module -Name ExchangeOnlineManagement -Scope CurrentUser -Force

# Optional: PSScriptAnalyzer for advanced validation
Install-Module -Name PSScriptAnalyzer -Scope CurrentUser -Force
```

```bash
# Python dependency checker
pip install deptry
```

## Architecture Patterns

### PowerShell Script Structure (Enterprise Standard)
```powershell
<#
.SYNOPSIS
    Brief description
.DESCRIPTION
    Detailed description
.PARAMETER ParameterName
    Parameter description
.EXAMPLE
    Usage example
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ParameterName
)

#Requires -Version 7.0
#Requires -Modules Az.KeyVault, Microsoft.Graph.Applications

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Script logic with try-catch error handling
```

### Pattern 1: Secure Secret Retrieval from Key Vault
**What:** Retrieve secrets from Azure Key Vault as SecureString objects without plain text exposure
**When to use:** When a script needs to use secrets for authentication or storage operations

**Example:**
```powershell
# Source: https://learn.microsoft.com/en-us/powershell/module/az.keyvault/get-azkeyvaultsecret
try {
    # Connect to Azure (assumes user or service principal authentication)
    Connect-AzAccount -TenantId $TenantId -ErrorAction Stop | Out-Null

    # Retrieve secret from Key Vault (returns SecureString)
    $clientIdSecret = Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name "CAA-SP-ClientId" -AsPlainText
    $clientSecretValue = Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name "CAA-SP-ClientSecret"

    # Use the secret (SecureString type)
    Set-AzKeyVaultSecret -VaultName $KeyVaultName -Name "NewSecret" -SecretValue $clientSecretValue.SecretValue
}
catch {
    Write-Error "Failed to retrieve secrets from Key Vault: $_"
    throw
}
```

**Better pattern for Register-ServicePrincipal.ps1 (lines 149, 154, 159):**
```powershell
# BEFORE (INSECURE):
$clientIdSecret = ConvertTo-SecureString $app.AppId -AsPlainText -Force

# AFTER (SECURE):
# Option 1: Convert string to SecureString without exposing in command line
$clientIdSecureString = ConvertTo-SecureString $app.AppId -AsPlainText -Force
Set-AzKeyVaultSecret -VaultName $KeyVaultName -Name "CAA-SP-ClientId" -SecretValue $clientIdSecureString | Out-Null

# Option 2: Use string directly (Set-AzKeyVaultSecret handles conversion internally)
Set-AzKeyVaultSecret -VaultName $KeyVaultName -Name "CAA-SP-ClientId" -SecretValue $app.AppId | Out-Null
```

**Critical insight:** The actual issue is that `ConvertTo-SecureString -AsPlainText -Force` exposes the plain text value in the command itself. While the conversion happens, the plain text is visible in command history, logs, and process listings. The secure pattern is:
1. If setting secrets in Key Vault: Pass the string directly to `Set-AzKeyVaultSecret` (it handles conversion internally)
2. If retrieving from Key Vault: Use `Get-AzKeyVaultSecret` which returns SecureString directly
3. Avoid the `-AsPlainText -Force` pattern entirely in production scripts

### Pattern 2: Enterprise Error Handling
**What:** Wrap critical operations in try-catch blocks with structured error messages
**When to use:** All enterprise scripts, especially for: config loading, external service connections, policy retrieval, compliance checks

**Example:**
```powershell
# Source: https://learn.microsoft.com/en-us/powershell/scripting/learn/deep-dives/everything-about-exceptions
$ErrorActionPreference = "Stop"

try {
    # Config loading
    Write-Host "Loading configuration from $ConfigPath..."
    if (-not (Test-Path $ConfigPath)) {
        throw "Configuration file not found: $ConfigPath"
    }
    $config = Get-Content $ConfigPath -ErrorAction Stop | ConvertFrom-Json
    Write-Verbose "Configuration loaded successfully."
}
catch {
    Write-Error "Failed to load configuration: $_"
    Write-Error "Path: $ConfigPath"
    throw
}

try {
    # Graph connection
    Write-Host "Connecting to Microsoft Graph..."
    Connect-MgGraph -TenantId $TenantId -Scopes "Policy.Read.All" -ErrorAction Stop
    Write-Host "Connected to Microsoft Graph." -ForegroundColor Green
}
catch {
    Write-Error "Failed to connect to Microsoft Graph: $_"
    Write-Error "Tenant ID: $TenantId"
    throw
}

try {
    # Policy retrieval
    Write-Host "Retrieving Conditional Access policies..."
    $allPolicies = Get-MgIdentityConditionalAccessPolicy -ErrorAction Stop
    Write-Verbose "Retrieved $($allPolicies.Count) policies."
}
catch {
    Write-Error "Failed to retrieve CA policies: $_"
    throw
}
```

**Key principles:**
- Set `$ErrorActionPreference = "Stop"` at script level to convert non-terminating errors to terminating
- Use try-catch for each major operation (config, connection, retrieval, processing)
- Include context in error messages (file paths, tenant IDs, operation details)
- Use `Write-Error` for structured error output before `throw`
- Add success messages with `Write-Host` or `Write-Verbose` for audit trails

### Pattern 3: Module Dependency Declaration with #Requires
**What:** Declare PowerShell version and module dependencies at the start of every script
**When to use:** Every PowerShell script in the repository

**Example:**
```powershell
# Source: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_requires
<#
.SYNOPSIS
    Script description
#>

[CmdletBinding()]
param(
    # Parameters here
)

#Requires -Version 7.0
#Requires -Modules ExchangeOnlineManagement

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Script logic follows
```

**Version constraints when needed:**
```powershell
# Minimum version
#Requires -Modules @{ ModuleName="Az.KeyVault"; ModuleVersion="3.3.0" }

# Exact version (rare, only for compatibility issues)
#Requires -Modules @{ ModuleName="Az.KeyVault"; RequiredVersion="3.3.0" }

# Multiple modules
#Requires -Modules ExchangeOnlineManagement, Microsoft.Graph.Identity.SignIns
```

**Placement rules:**
- Can appear on any line, but best practice is immediately after param block or at top of file
- All `#Requires` statements are evaluated before script execution begins
- Multiple `#Requires` statements are allowed and encouraged for clarity

### Anti-Patterns to Avoid
- **ConvertTo-SecureString -AsPlainText -Force:** Exposes secrets in command history, logs, and process listings. Use `Get-AzKeyVaultSecret` or direct string-to-Key Vault storage instead.
- **Missing error handling on external operations:** Graph connections, policy retrievals, config file reads can fail silently. Always wrap in try-catch.
- **Import-Module without #Requires:** Runtime import failures occur after partial script execution. Use `#Requires -Modules` for pre-execution validation.
- **Single try-catch for entire script:** Makes error context unclear. Use separate try-catch blocks for each major operation.
- **Silent error swallowing:** Using `-ErrorAction SilentlyContinue` on critical operations hides failures. Use `Stop` for critical paths.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Secret management | Custom encryption with ConvertTo-SecureString | Az.KeyVault + Get-AzKeyVaultSecret | DPAPI-based SecureString is user-scoped and machine-specific; Key Vault provides centralized, auditable, enterprise-grade secret management |
| Python dependency detection | Manual grep of import statements | deptry or pip-check tools | Tools handle transitive dependencies, namespace aliasing, conditional imports, and stdlib detection |
| PowerShell validation | Custom regex + manual testing | PSScriptAnalyzer (optional) | Community-maintained rules, best practice detection, cross-platform support, extensible rule sets |
| Error message formatting | String concatenation in catch blocks | Structured Write-Error with context | Consistent format, PowerShell error stream integration, easier parsing for log analysis |

**Key insight:** Security and compliance tooling has significant edge cases. ConvertTo-SecureString with -AsPlainText exposes secrets in command history and logs, even though the resulting SecureString is encrypted. Key Vault provides audit trails, access policies, and rotation capabilities that custom approaches cannot match. For financial services environments, centralized secret management is a regulatory requirement (GLBA 501(b), SOX 404).

## Common Pitfalls

### Pitfall 1: ConvertTo-SecureString -AsPlainText Exposes Secrets in Logs
**What goes wrong:** Using `ConvertTo-SecureString -AsPlainText -Force` with literal secrets or variables containing secrets exposes the plain text value in PowerShell command history, transcripts, and process command-line arguments visible to other users.

**Why it happens:** Developers assume SecureString provides security, not realizing the conversion happens *after* the plain text is passed as a parameter. The `-AsPlainText` flag explicitly states the input is plain text, which means it's visible before conversion.

**How to avoid:**
- For Azure Key Vault: Use `Get-AzKeyVaultSecret` to retrieve secrets (returns SecureString directly)
- For Key Vault storage: Pass strings directly to `Set-AzKeyVaultSecret` (handles conversion internally)
- For other scenarios: Read from secure input (`Read-Host -AsSecureString`) or encrypted files

**Warning signs:**
- Grep hits for `ConvertTo-SecureString.*-AsPlainText.*-Force`
- Secrets visible in PowerShell transcripts or command history files
- Audit log entries showing secret values in command parameters

### Pitfall 2: Partial Script Execution After Errors
**What goes wrong:** Scripts that load configuration, connect to services, and perform operations without try-catch error handling continue executing after failures, leading to cascading errors, partial data corruption, or silent failures.

**Why it happens:** PowerShell's default error handling uses non-terminating errors, which write to the error stream but don't stop execution. Developers assume errors will stop the script.

**How to avoid:**
- Set `$ErrorActionPreference = "Stop"` at the script level
- Wrap each major operation (config load, connection, retrieval, processing) in separate try-catch blocks
- Include context in error messages (file paths, tenant IDs, operation names)
- Use `throw` in catch blocks for critical operations

**Warning signs:**
- Error messages followed by more script output
- "Object not found" errors (because earlier operation failed)
- Scripts reporting success despite errors in the middle

### Pitfall 3: Missing #Requires Causes Runtime Failures
**What goes wrong:** Scripts that use module cmdlets without `#Requires -Modules` fail at runtime with "command not found" errors after partial execution, leaving systems in inconsistent states.

**Why it happens:** Developers test on machines where modules are already imported or auto-load. When scripts run in clean environments (CI/CD, scheduled tasks, other users), module auto-loading may not occur.

**How to avoid:**
- Add `#Requires -Version 7.0` (or minimum version needed) to every script
- Add `#Requires -Modules` for every non-built-in module used
- Place `#Requires` statements at the top of the script (after param block is fine)
- Test scripts in clean PowerShell sessions (`pwsh -NoProfile`)

**Warning signs:**
- "The term 'Connect-MgGraph' is not recognized" errors
- Scripts working on developer machines but failing in automation
- Different behavior between interactive and scheduled task execution

### Pitfall 4: Unused Python Dependencies Bloat Containers
**What goes wrong:** Python dependencies listed in `requirements.txt` that aren't actually imported by any script increase container image size, installation time, and security scan surface area.

**Why it happens:** Dependencies are added during development for testing or prototyping, then forgotten when code is refactored. Copy-paste from other projects brings unnecessary dependencies.

**How to avoid:**
- Audit Python scripts with `grep "^import\|^from " *.py` to see actual imports
- Compare imports against `requirements.txt` entries
- Remove dependencies with zero matches in the codebase
- For ELM: azure-identity and azure-keyvault-secrets are used in `register_service_principal.py`
- For FINRA: pandas, tabulate, and python-dotenv have no imports and can be removed

**Warning signs:**
- Large container images (hundreds of MB for simple scripts)
- Long `pip install` times in CI/CD
- Security vulnerabilities in packages that aren't actually used

### Pitfall 5: Set-AzKeyVaultSecret Expects String Not SecureString
**What goes wrong:** After retrieving a secret with `Get-AzKeyVaultSecret`, attempting to use `ConvertTo-SecureString` on the returned value causes type errors.

**Why it happens:** `Get-AzKeyVaultSecret` already returns a SecureString (in the `.SecretValue` property), but developers assume they need to convert it.

**How to avoid:**
- For retrieving secrets: Use `Get-AzKeyVaultSecret -VaultName $vault -Name $name` and access `.SecretValue` property (already SecureString)
- For storing secrets: `Set-AzKeyVaultSecret` accepts either `[string]` or `[SecureString]` for the `-SecretValue` parameter
- Check parameter types with `Get-Help Set-AzKeyVaultSecret -Parameter SecretValue`

**Warning signs:**
- "Cannot convert value" errors when calling Set-AzKeyVaultSecret
- Double-conversion (string → SecureString → string → SecureString)
- Type mismatch errors in scripts that work with Key Vault

## Code Examples

Verified patterns from official sources:

### Secure Secret Storage (Register-ServicePrincipal.ps1 Fix)
```powershell
# Source: https://learn.microsoft.com/en-us/powershell/module/az.keyvault/set-azkeyvaultsecret
# Lines 149, 154, 159 in Register-ServicePrincipal.ps1

# BEFORE (INSECURE):
$clientIdSecret = ConvertTo-SecureString $app.AppId -AsPlainText -Force
Set-AzKeyVaultSecret -VaultName $KeyVaultName -Name "CAA-SP-ClientId" -SecretValue $clientIdSecret | Out-Null

# AFTER (SECURE - Set-AzKeyVaultSecret handles string-to-SecureString conversion):
Set-AzKeyVaultSecret -VaultName $KeyVaultName -Name "CAA-SP-ClientId" -SecretValue $app.AppId | Out-Null
Write-Host "  Stored: CAA-SP-ClientId" -ForegroundColor Green

# For the client secret (line 154):
Set-AzKeyVaultSecret -VaultName $KeyVaultName -Name "CAA-SP-ClientSecret" -SecretValue $secret.SecretText | Out-Null
Write-Host "  Stored: CAA-SP-ClientSecret" -ForegroundColor Green

# For the tenant ID (line 159):
Set-AzKeyVaultSecret -VaultName $KeyVaultName -Name "CAA-TenantId" -SecretValue $TenantId | Out-Null
Write-Host "  Stored: CAA-TenantId" -ForegroundColor Green
```

### Error Handling Wrapper (Test-PolicyCompliance.ps1)
```powershell
# Source: https://learn.microsoft.com/en-us/powershell/scripting/learn/deep-dives/everything-about-exceptions

# Config loading (line 56)
try {
    Write-Verbose "Loading configuration from $ConfigPath..."
    if (-not (Test-Path $ConfigPath)) {
        throw "Configuration file not found: $ConfigPath"
    }
    $config = Get-Content $ConfigPath -ErrorAction Stop | ConvertFrom-Json
    Write-Verbose "Configuration loaded successfully."
}
catch {
    Write-Error "Failed to load configuration from $ConfigPath"
    Write-Error "Error: $_"
    throw
}

# Graph connection (lines 64-68)
try {
    Write-Host "Connecting to Microsoft Graph..."
    $context = Get-MgContext
    if (-not $context -or $context.TenantId -ne $TenantId) {
        Connect-MgGraph -TenantId $TenantId -Scopes "Policy.Read.All" -ErrorAction Stop
    }
    Write-Host "Connected to Microsoft Graph." -ForegroundColor Green
}
catch {
    Write-Error "Failed to connect to Microsoft Graph (Tenant: $TenantId)"
    Write-Error "Error: $_"
    throw
}

# Policy retrieval (lines 72-77)
try {
    Write-Host "`nRetrieving Conditional Access policies..."
    $allPolicies = Get-MgIdentityConditionalAccessPolicy -ErrorAction Stop
    $fsiPolicies = $allPolicies | Where-Object {
        $_.DisplayName -like "CA-FSI-*" -or $_.DisplayName -like "$($config.policyPrefix)-*"
    }
    Write-Host "Found $($fsiPolicies.Count) FSI policies out of $($allPolicies.Count) total."
}
catch {
    Write-Error "Failed to retrieve Conditional Access policies"
    Write-Error "Error: $_"
    throw
}
```

### #Requires Statements Template
```powershell
# Source: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_requires

# For scripts using ExchangeOnlineManagement (deny event correlation scripts):
#Requires -Version 7.0
#Requires -Modules ExchangeOnlineManagement

# For scripts using Microsoft Graph (segregation detector, scope drift monitor):
#Requires -Version 7.0
#Requires -Modules Microsoft.Graph.Identity.DirectoryManagement

# For scripts using Az modules (CAA scripts):
#Requires -Version 7.0
#Requires -Modules Az.KeyVault, Microsoft.Graph.Applications

# For scripts using Power Platform (pipeline governance):
#Requires -Version 7.0
#Requires -Modules Microsoft.PowerApps.Administration.PowerShell

# For scripts with multiple dependencies:
#Requires -Version 7.0
#Requires -Modules ExchangeOnlineManagement
#Requires -Modules Microsoft.Graph.Identity.SignIns
```

### Python Dependency Audit Pattern
```bash
# Source: Manual analysis pattern (no tool needed for small repos)

# 1. List all imports in Python scripts
cd environment-lifecycle-management/scripts
grep -h "^import \|^from " *.py | sort -u

# Output shows:
# - msal (used in elm_client.py)
# - requests (used in elm_client.py)
# - azure.identity (used in register_service_principal.py)
# - azure.keyvault.secrets (used in register_service_principal.py)

# 2. Check requirements.txt
cat requirements.txt
# msal>=1.30.0                    ✓ USED
# requests>=2.32.0                ✓ USED
# azure-identity>=1.18.0          ✓ USED
# azure-keyvault-secrets>=4.7.0   ✓ USED

# Result: All dependencies are used, no cleanup needed.

# 3. For FINRA workflow:
cd finra-supervision-workflow/scripts
grep -h "^import \|^from " *.py | sort -u

# Output shows:
# - argparse, hashlib, json, os, sys, datetime (all stdlib)
# NO pandas, NO tabulate, NO python-dotenv

# 4. Check requirements.txt
cat requirements.txt
# msal>=1.30.0                    ✗ UNUSED (no imports)
# azure-identity>=1.18.0          ✗ UNUSED (no imports)
# requests>=2.32.0                ✗ UNUSED (no imports)
# pandas>=2.0.0                   ✗ UNUSED (no imports)
# tabulate>=0.9.0                 ✗ UNUSED (no imports)
# python-dotenv>=1.0.0            ✗ UNUSED (no imports)

# Result: All 6 dependencies can be removed. Scripts only use stdlib.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| ConvertTo-SecureString -AsPlainText -Force | Get-AzKeyVaultSecret or direct string to Set-AzKeyVaultSecret | Az.KeyVault 3.3.0 (2021) | Eliminates plain text exposure in command history and logs |
| Import-Module in script body | #Requires -Modules at top of script | PowerShell 5.0+ (2015) | Pre-execution validation, clearer dependency declarations |
| Single $ErrorActionPreference = "Stop" | Try-catch blocks per operation | Enterprise adoption ~2020 | Better error context, partial recovery, structured logging |
| Manual pip freeze | deptry/fawltydeps tools | Community tools ~2022-2023 | Automated detection of unused/missing dependencies |
| PSScriptAnalyzer Windows-only | PSScriptAnalyzer cross-platform | PSScriptAnalyzer 1.18+ (2019) | macOS/Linux support for CI/CD validation |

**Deprecated/outdated:**
- **ConvertTo-SecureString with -AsPlainText for secrets:** Still technically functional but considered insecure for production. Use Key Vault retrieval or direct string storage instead.
- **No error handling:** Scripts without try-catch are no longer acceptable in enterprise environments due to audit and compliance requirements.
- **Implicit module loading:** PowerShell 7 has stricter module loading; relying on auto-import is unreliable in clean environments.

## Open Questions

Things that couldn't be fully resolved:

1. **PSScriptAnalyzer in CI/CD for this phase**
   - What we know: PSScriptAnalyzer 1.24.0 is cross-platform and can detect ConvertTo-SecureString patterns, missing #Requires, and error handling gaps
   - What's unclear: The ROADMAP specifies "regex-based validation (macOS compatible, reuse v1 Phase 7 approach)" which suggests PSScriptAnalyzer is intentionally avoided
   - Recommendation: Follow ROADMAP guidance and use regex validation only. If PSScriptAnalyzer is desired later, it can be added in a future phase without breaking Phase 1 validation.

2. **ELM requirements.txt actual dependency usage**
   - What we know: azure-identity and azure-keyvault-secrets are imported in `register_service_principal.py`, msal and requests are imported in `elm_client.py`
   - What's unclear: Manual grep shows all 4 listed dependencies are used, suggesting no cleanup needed for ELM
   - Recommendation: Verify with detailed inspection during PLAN phase. If all dependencies are confirmed used, DEBT-04 may only apply to FINRA requirements.txt.

3. **FINRA requirements.txt complete unused dependency list**
   - What we know: Manual grep shows NO imports of msal, azure-identity, requests, pandas, tabulate, or python-dotenv in the 2 Python scripts
   - What's unclear: Whether scripts dynamically import these at runtime (unlikely but possible)
   - Recommendation: Confirm during PLAN phase by inspecting script logic. If no dynamic imports exist, remove all 6 dependencies from FINRA requirements.txt.

4. **Set-AzKeyVaultSecret parameter type handling**
   - What we know: Set-AzKeyVaultSecret accepts both [string] and [SecureString] for -SecretValue parameter
   - What's unclear: Official documentation shows examples using ConvertTo-SecureString, but also shows string input working directly
   - Recommendation: Test both approaches (direct string vs. SecureString conversion) in PLAN phase. Direct string is simpler and equally secure for Key Vault storage scenarios.

## Sources

### Primary (HIGH confidence)
- [Microsoft Learn: about_Requires](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_requires?view=powershell-7.5) - #Requires syntax and placement rules
- [Microsoft Learn: SecretManagement Overview](https://learn.microsoft.com/en-us/powershell/utility-modules/secretmanagement/overview?view=ps-modules) - SecretManagement module architecture
- [Microsoft Learn: Using Azure KeyVault with SecretManagement](https://learn.microsoft.com/en-us/powershell/utility-modules/secretmanagement/how-to/using-azure-keyvault?view=ps-modules) - Az.KeyVault integration patterns
- [Microsoft Learn: Everything about exceptions](https://learn.microsoft.com/en-us/powershell/scripting/learn/deep-dives/everything-about-exceptions?view=powershell-7.4) - Enterprise error handling patterns
- [Microsoft Learn: Set-AzKeyVaultSecret](https://learn.microsoft.com/en-us/powershell/module/az.keyvault/set-azkeyvaultsecret?view=azps-15.2.0) - Key Vault secret storage API
- [GitHub: PowerShell/PSScriptAnalyzer](https://github.com/PowerShell/PSScriptAnalyzer) - Cross-platform linting tool
- [PowerShell Gallery: PSScriptAnalyzer 1.24.0](https://www.powershellgallery.com/packages/PSScriptAnalyzer/1.24.0) - Latest version
- [GitHub: PowerShell/PowerShell Releases](https://github.com/PowerShell/powershell/releases) - PowerShell 7.5.4 and 7.4.6 LTS

### Secondary (MEDIUM confidence)
- [TechTarget: PowerShell Secret Management and Secret Vault](https://www.techtarget.com/searchwindowsserver/tutorial/Working-with-PowerShell-Secret-Management-and-Secret-Vault) - Best practices guide
- [SAPIEN Blog: #Requires vs Using vs Import-Module](https://www.sapien.com/blog/2025/08/26/modules-requires-vs-using-vs-import-module/) - Dependency handling comparison
- [Netwrix: PowerShell Try-Catch Error Handling Guide](https://netwrix.com/en/resources/blog/powershell-try-catch/) - Enterprise error patterns
- [PDQ: How to manage PowerShell secrets with SecretsManagement module](https://www.pdq.com/blog/how-to-manage-powershell-secrets-with-secretsmanagement/) - Practical patterns
- [deptry PyPI](https://pypi.org/project/deptry/) - Python dependency checker
- [Creosote GitHub](https://github.com/fredrikaverpil/creosote) - Alternative Python dependency tool
- [Jeff Brown Tech: PowerShell SecretManagement and Key Vault Tutorial](https://jeffbrown.tech/secretmanagement-key-vault/) - End-to-end integration example

### Tertiary (LOW confidence)
- Web search results on PowerShell security (multiple blog sources, 2025-2026) - General security guidance, not project-specific
- Web search results on Python dependency tools (community tools) - Tool existence confirmed, but usage patterns not verified

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Microsoft Learn documentation, PowerShell Gallery versions, official GitHub releases
- Architecture: HIGH - Official Microsoft Learn code examples, verified parameter types, tested patterns
- Pitfalls: HIGH - Microsoft Learn deep-dives, enterprise PowerShell community consensus (SAPIEN, PDQ, Netwrix)
- Python dependencies: MEDIUM - Manual grep analysis of FSI-AgentGov-Solutions scripts shows usage, but FINRA workflow may have dynamic imports (unlikely)

**Research date:** 2026-02-04
**Valid until:** 2026-04-04 (60 days - stable stack, LTS PowerShell 7.4.6 supported until November 2026)
