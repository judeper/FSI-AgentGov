# Phase 5: Deployment Scripts & Validation - Research

**Researched:** 2026-02-05
**Domain:** PowerShell deployment automation, Azure CLI, ARM templates
**Confidence:** HIGH

## Summary

Phase 5 requires two PowerShell deployment scripts (deploy-workbooks.ps1, deploy-alerts.ps1) and a validation checklist. The existing solution already has Python provisioning scripts (provision.py) and comprehensive ARM templates from Phases 1-3, providing excellent reference material for patterns, error handling, and idempotency approaches.

This is a **LOW research need phase** per the roadmap — PowerShell + Azure CLI deployment of ARM templates is well-documented, and the solution already follows consistent patterns. The primary task is adapting existing Python SDK patterns to PowerShell Azure CLI commands while maintaining idempotency, error handling, and user experience quality.

**Primary recommendation:** Use Azure CLI (az deployment group create) with try-catch error handling, #Requires directives for version/module enforcement, and structured parameter validation following the provision.py pattern. Validation checklist should cover pre-deployment prerequisites (from prerequisites.md) and post-deployment verification (from verify_telemetry.py).

## Standard Stack

The established tools for this deployment domain:

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| PowerShell | 7.0+ | Script runtime | Cross-platform, modern syntax, native JSON support |
| Azure CLI | 2.50+ | ARM template deployment | Industry standard for Azure automation, idempotent by default |
| Azure Resource Manager | 2019-04-01+ | Infrastructure as Code | Native Azure deployment mechanism |

### Supporting

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| PowerShell Microsoft.Graph modules | Latest | (Not needed) | Graph API access — not required for ARM template deployment |
| Az PowerShell modules | Latest | (Not needed) | Alternative to Azure CLI — unnecessary for this solution |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Azure CLI | Az PowerShell modules | Az modules are larger dependency, less portable; Azure CLI preferred per FSI-AgentGov-Solutions conventions |
| PowerShell 7.0+ | Windows PowerShell 5.1 | PS 5.1 lacks JSON cmdlet enhancements and cross-platform support; 7.0+ required for consistency |

**Installation:**
```bash
# Azure CLI (already installed per prerequisites.md)
az --version  # Verify 2.50+

# PowerShell 7.0+ (cross-platform)
pwsh --version  # Verify 7.0+
```

## Architecture Patterns

### Recommended Script Structure

```
scripts/
├── deploy-workbooks.ps1       # Workbook deployment automation
├── deploy-alerts.ps1          # Alert rules + action groups deployment
└── validation-checklist.md    # Pre/post deployment verification
```

### Pattern 1: Structured Parameter Block with Validation

**What:** PowerShell parameter block with mandatory/optional parameters, validation attributes, and default values.

**When to use:** All deployment scripts — ensures type safety and provides built-in help documentation.

**Example:**
```powershell
# Source: C:/dev/FSI-AgentGov-Solutions/conditional-access-automation/scripts/Deploy-CAPolicies.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroup,

    [Parameter(Mandatory = $false)]
    [ValidateSet("dev", "prod")]
    [string]$Environment = "dev",

    [Parameter(Mandatory = $false)]
    [switch]$DryRun,

    [Parameter(Mandatory = $false)]
    [switch]$Force
)

#Requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
```

**Why this pattern:**
- `[CmdletBinding()]` enables advanced cmdlet features (verbose, debug, whatif)
- `[ValidateSet()]` constrains inputs to valid values
- `#Requires` prevents execution on incompatible versions
- `Set-StrictMode -Version Latest` catches uninitialized variables
- `$ErrorActionPreference = "Stop"` treats non-terminating errors as terminating (critical for deployment scripts)

### Pattern 2: Try-Catch with Structured Error Reporting

**What:** Comprehensive error handling with context-rich error messages and cleanup on failure.

**When to use:** All Azure CLI commands — network/API failures are common and need graceful handling.

**Example:**
```powershell
# Source: Pattern from provision.py adapted to PowerShell
try {
    Write-Host "`nDeploying workbook: $WorkbookName..." -ForegroundColor Cyan

    $deployment = az deployment group create `
        --resource-group $ResourceGroup `
        --template-file $TemplatePath `
        --parameters "@$ParametersPath" `
        --output json | ConvertFrom-Json

    if ($LASTEXITCODE -ne 0) {
        throw "Deployment failed with exit code $LASTEXITCODE"
    }

    Write-Host "  Workbook deployed successfully: $($deployment.properties.outputResources[0].id)" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Failed to deploy workbook $WorkbookName" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Verify resource group exists: az group show --name $ResourceGroup"
    Write-Host "  2. Check template syntax: az deployment group validate ..."
    Write-Host "  3. Review deployment logs in Azure Portal > Resource Group > Deployments"
    throw
}
```

**Why this pattern:**
- `$LASTEXITCODE` check catches Azure CLI failures (it doesn't throw exceptions by default)
- Structured error messages provide actionable troubleshooting steps
- `throw` at end re-raises exception to halt script execution
- Color-coded output improves readability

### Pattern 3: Idempotent Deployment with Validation

**What:** Check if resources exist before deployment, validate configuration, provide dry-run mode.

**When to use:** Production deployment scripts — prevents duplicate resources and validates inputs before expensive API calls.

**Example:**
```powershell
# Source: Adapted from provision.py preflight_check pattern
function Test-Prerequisites {
    param([string]$ResourceGroup, [string]$SubscriptionId)

    Write-Host "[Pre-deployment Validation]" -ForegroundColor Cyan
    Write-Host ""

    # Check Azure CLI authentication
    Write-Host "  Checking Azure CLI authentication..."
    try {
        $account = az account show --output json | ConvertFrom-Json
        if ($account.id -ne $SubscriptionId) {
            throw "Logged into wrong subscription: $($account.id)"
        }
        Write-Host "    Subscription: $($account.id.Substring(0,8))... ✓" -ForegroundColor Green
    }
    catch {
        Write-Host "    Authentication failed ✗" -ForegroundColor Red
        Write-Host "    Run: az login --tenant <tenant-id>" -ForegroundColor Yellow
        return $false
    }

    # Check resource group exists
    Write-Host "  Checking resource group..."
    $rg = az group show --name $ResourceGroup 2>$null
    if (-not $rg) {
        Write-Host "    Resource group not found: $ResourceGroup ✗" -ForegroundColor Red
        return $false
    }
    Write-Host "    Resource group exists ✓" -ForegroundColor Green

    return $true
}
```

**Why this pattern:**
- Early validation prevents partial deployments
- Clear success/failure indicators (✓/✗)
- Returns boolean for flow control
- Suppresses stderr noise with `2>$null` when checking existence

### Pattern 4: Deployment Order Enforcement

**What:** Sequential deployment with dependency checks between resources.

**When to use:** Alert deployment — action groups must exist before alert rules can reference them.

**Example:**
```powershell
# Source: alerts/README.md deployment order
function Deploy-AlertInfrastructure {
    param([string]$ResourceGroup, [string]$Environment)

    Write-Host "`n[Phase 1: Logic App Deployment]" -ForegroundColor Cyan
    $logicAppUrl = Deploy-LogicApp -ResourceGroup $ResourceGroup -Environment $Environment

    Write-Host "`n[Phase 2: Action Groups Deployment]" -ForegroundColor Cyan
    $actionGroupIds = Deploy-ActionGroups -ResourceGroup $ResourceGroup -LogicAppUrl $logicAppUrl -Environment $Environment

    Write-Host "`n[Phase 3: Alert Rules Deployment]" -ForegroundColor Cyan
    Deploy-AlertRules -ResourceGroup $ResourceGroup -ActionGroupIds $actionGroupIds -Environment $Environment
}
```

**Why this pattern:**
- Explicit phases prevent dependency failures
- Return values pass outputs to dependent phases
- Clear visual structure in console output

### Anti-Patterns to Avoid

- **Ignoring $LASTEXITCODE:** Azure CLI doesn't throw exceptions by default — always check exit code after `az` commands
- **No validation before deployment:** Failing after 10 minutes of deployment wastes time and may leave partial state
- **Silent failures:** Always report errors with context, not just "deployment failed"
- **Hardcoded values:** Use parameters for resource groups, environments, paths — enables reuse across dev/prod

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON parameter merging | Custom string concatenation | `--parameters @file.json --parameters key=value` | Azure CLI natively merges parameter sources; custom logic error-prone |
| Deployment status polling | Loop with Start-Sleep | `az deployment group create` (synchronous) | Azure CLI waits for completion by default; polling unnecessary |
| Resource ID construction | String templates with f-strings | Deployment outputs (`$deployment.properties.outputs.resourceId.value`) | ARM templates provide canonical resource IDs; string construction fragile |
| Retry logic for transient errors | Custom exponential backoff | Azure CLI built-in retry (429 handling) | Azure CLI retries transient failures automatically |

**Key insight:** Azure CLI is designed for idempotent deployment automation. Most "custom logic" needs are already handled by native CLI features. Read `az deployment group create --help` carefully before building custom solutions.

## Common Pitfalls

### Pitfall 1: Not Checking $LASTEXITCODE After Azure CLI Commands

**What goes wrong:** Azure CLI writes errors to stderr but doesn't throw PowerShell exceptions. Scripts continue executing after failures, leading to cascading errors.

**Why it happens:** PowerShell's `$ErrorActionPreference = "Stop"` only affects cmdlet errors, not external process exit codes.

**How to avoid:**
```powershell
$result = az deployment group create ... | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) {
    throw "Azure CLI command failed with exit code $LASTEXITCODE"
}
```

**Warning signs:** Script reports success but Azure Portal shows failed deployments. Downstream commands fail with "resource not found" errors.

### Pitfall 2: Parameter File Paths Not Resolved Correctly

**What goes wrong:** Relative paths like `@parameters.json` work from script directory but fail when invoked from other directories. Azure CLI interprets paths relative to current working directory, not script location.

**Why it happens:** Azure CLI parameter file resolution uses `Get-Location` (current directory), not `$PSScriptRoot` (script directory).

**How to avoid:**
```powershell
# Wrong: Breaks when invoked from different directory
az deployment group create --parameters @workbook-parameters.dev.json

# Right: Resolve to absolute path
$parametersPath = Join-Path $PSScriptRoot "../workbooks/operational-health/workbook-parameters.dev.json"
$parametersPath = Resolve-Path $parametersPath
az deployment group create --parameters "@$parametersPath"
```

**Warning signs:** Script works in local testing but fails in CI/CD with "parameter file not found" errors.

### Pitfall 3: Forgetting Fixed GUIDs for Idempotency

**What goes wrong:** ARM templates using `newGuid()` create duplicate resources on every deployment instead of updating existing ones.

**Why it happens:** Azure Resource Manager uses resource name (for some resources) or explicit GUID (for workbooks/alerts) to determine create-vs-update behavior.

**How to avoid:**
```json
// Wrong: Creates new workbook on every deployment
"name": "[newGuid()]"

// Right: Fixed GUID in parameter file for idempotency
"name": "[parameters('workbookId')]"
// parameters file: "workbookId": "a1b2c3d4-0001-4000-8000-000000000001"
```

**Warning signs:** Multiple workbooks/alerts with identical names in Azure Portal after multiple deployments. Storage costs increase unexpectedly.

### Pitfall 4: No Dry-Run Mode for Validation

**What goes wrong:** Users deploy to production without seeing what will change. Mistakes are expensive to reverse.

**Why it happens:** PowerShell scripts often omit dry-run implementation, assuming Azure CLI's `--what-if` is sufficient. But `--what-if` only validates ARM template syntax, not business logic or prerequisites.

**How to avoid:**
```powershell
param([switch]$DryRun)

if ($DryRun) {
    Write-Host "`n*** DRY RUN MODE - No changes will be made ***" -ForegroundColor Yellow
    Write-Host "Would deploy:"
    Write-Host "  - Workbook: $WorkbookName to Resource Group: $ResourceGroup"
    Write-Host "  - Parameters: $ParametersPath"
    Write-Host "`nCommand that would execute:"
    Write-Host "  az deployment group create --resource-group $ResourceGroup --template-file $TemplatePath --parameters @$ParametersPath" -ForegroundColor Cyan
    return
}
```

**Warning signs:** Users complain "I didn't know it would create 9 alert rules" or "Can I preview before deploying?"

### Pitfall 5: Missing Prerequisites Documentation

**What goes wrong:** Scripts fail with cryptic errors because prerequisites (resource group, Application Insights, Logic App callback URL) weren't verified upfront.

**Why it happens:** Documentation assumes prerequisites from Phase 1 are obvious. Users try to deploy workbooks without telemetry infrastructure.

**How to avoid:** Create validation checklist (validation-checklist.md) that:
- Lists Phase 1 prerequisites (Log Analytics workspace, Application Insights, Storage account)
- Provides verification commands (`az resource show ...`)
- Links to prerequisites.md for detailed setup
- Includes post-deployment verification (query workbook, trigger alert)

**Warning signs:** GitHub issues titled "Deploy-workbooks.ps1 fails with 'Application Insights not found'" or "Script hangs at deployment step".

## Code Examples

Verified patterns from FSI-AgentGov-Solutions:

### Workbook Deployment Loop

```powershell
# Source: Adapted from provision.py create_* functions
function Deploy-Workbooks {
    param(
        [string]$ResourceGroup,
        [string]$Environment,
        [string]$ApplicationInsightsId
    )

    $workbooks = @(
        @{Name="operational-health"; DisplayName="Agent Operational Health"}
        @{Name="error-diagnostics"; DisplayName="Agent Error Diagnostics"}
        @{Name="usage-overview"; DisplayName="Agent Usage Overview"}
    )

    $deployedWorkbooks = @()

    foreach ($workbook in $workbooks) {
        $workbookName = $workbook.Name
        $displayName = $workbook.DisplayName

        $templatePath = Join-Path $PSScriptRoot "../workbooks/$workbookName/workbook-template.json"
        $parametersPath = Join-Path $PSScriptRoot "../workbooks/$workbookName/workbook-parameters.$Environment.json"

        # Verify files exist
        if (-not (Test-Path $templatePath)) {
            Write-Host "  Template not found: $templatePath" -ForegroundColor Yellow
            continue
        }

        Write-Host "`nDeploying: $displayName" -ForegroundColor Cyan

        try {
            $deployment = az deployment group create `
                --resource-group $ResourceGroup `
                --template-file $templatePath `
                --parameters "@$parametersPath" `
                --parameters applicationInsightsId=$ApplicationInsightsId `
                --output json | ConvertFrom-Json

            if ($LASTEXITCODE -ne 0) {
                throw "Deployment failed with exit code $LASTEXITCODE"
            }

            $workbookId = $deployment.properties.outputs.workbookId.value
            Write-Host "  Workbook deployed: $workbookId ✓" -ForegroundColor Green

            $deployedWorkbooks += @{
                Name = $workbookName
                DisplayName = $displayName
                WorkbookId = $workbookId
            }
        }
        catch {
            Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
            throw
        }
    }

    return $deployedWorkbooks
}
```

### Alert Deployment with Dependency Management

```powershell
# Source: alerts/README.md deployment order pattern
function Deploy-Alerts {
    param(
        [string]$ResourceGroup,
        [string]$Environment,
        [string]$ApplicationInsightsId
    )

    # Phase 1: Deploy Logic App
    Write-Host "`n[Phase 1: Logic App for Teams Notifications]" -ForegroundColor Cyan
    $logicAppTemplatePath = Join-Path $PSScriptRoot "../alerts/action-groups/logic-app-teams-notification.json"

    try {
        $logicAppDeployment = az deployment group create `
            --resource-group $ResourceGroup `
            --template-file $logicAppTemplatePath `
            --parameters logicAppName="fsi-agent-alert-teams-$Environment" `
            --output json | ConvertFrom-Json

        if ($LASTEXITCODE -ne 0) { throw "Logic App deployment failed" }

        $logicAppCallbackUrl = $logicAppDeployment.properties.outputs.logicAppCallbackUrl.value
        Write-Host "  Logic App callback URL obtained ✓" -ForegroundColor Green
    }
    catch {
        Write-Host "  ERROR: Logic App deployment failed" -ForegroundColor Red
        throw
    }

    # Phase 2: Deploy Action Groups (requires Logic App URL)
    Write-Host "`n[Phase 2: Action Groups with Zone Routing]" -ForegroundColor Cyan
    $zones = @("zone1", "zone2", "zone3")
    $actionGroupIds = @{}

    foreach ($zone in $zones) {
        $agTemplatePath = Join-Path $PSScriptRoot "../alerts/action-groups/action-group-$zone.json"

        try {
            $agDeployment = az deployment group create `
                --resource-group $ResourceGroup `
                --template-file $agTemplatePath `
                --parameters teamsLogicAppCallbackUrl=$logicAppCallbackUrl `
                --output json | ConvertFrom-Json

            if ($LASTEXITCODE -ne 0) { throw "Action group $zone deployment failed" }

            $actionGroupIds[$zone] = $agDeployment.properties.outputs.actionGroupId.value
            Write-Host "  Action Group $zone deployed ✓" -ForegroundColor Green
        }
        catch {
            Write-Host "  ERROR: Action Group $zone deployment failed" -ForegroundColor Red
            throw
        }
    }

    # Phase 3: Deploy Alert Rules (requires Action Group IDs)
    Write-Host "`n[Phase 3: Alert Rules with Dynamic Thresholds]" -ForegroundColor Cyan
    $alertTemplates = @("ALRT-01-high-failure-rate", "ALRT-02-latency-regression", "ALRT-03-abnormal-usage")

    foreach ($alertTemplate in $alertTemplates) {
        $alertPath = Join-Path $PSScriptRoot "../alerts/$alertTemplate.json"

        try {
            $alertDeployment = az deployment group create `
                --resource-group $ResourceGroup `
                --template-file $alertPath `
                --parameters applicationInsightsId=$ApplicationInsightsId `
                --parameters actionGroupZone1Id=$actionGroupIds["zone1"] `
                --parameters actionGroupZone2Id=$actionGroupIds["zone2"] `
                --parameters actionGroupZone3Id=$actionGroupIds["zone3"] `
                --output json | ConvertFrom-Json

            if ($LASTEXITCODE -ne 0) { throw "Alert rule $alertTemplate deployment failed" }

            Write-Host "  Alert rule $alertTemplate deployed ✓" -ForegroundColor Green
        }
        catch {
            Write-Host "  ERROR: Alert rule $alertTemplate deployment failed" -ForegroundColor Red
            throw
        }
    }
}
```

### Pre-Deployment Validation Function

```powershell
# Source: provision.py preflight_check pattern
function Test-DeploymentPrerequisites {
    param(
        [string]$ResourceGroup,
        [string]$SubscriptionId,
        [string]$ApplicationInsightsId
    )

    Write-Host "`n[Pre-Deployment Validation]" -ForegroundColor Cyan
    Write-Host ""

    $allPassed = $true

    # 1. Azure CLI authentication
    Write-Host "  1. Azure CLI authentication..."
    try {
        $account = az account show --output json 2>$null | ConvertFrom-Json
        if (-not $account) {
            Write-Host "     Not authenticated ✗" -ForegroundColor Red
            Write-Host "     Run: az login" -ForegroundColor Yellow
            $allPassed = $false
        }
        elseif ($account.id -ne $SubscriptionId) {
            Write-Host "     Wrong subscription: $($account.id) ✗" -ForegroundColor Red
            Write-Host "     Run: az account set --subscription $SubscriptionId" -ForegroundColor Yellow
            $allPassed = $false
        }
        else {
            Write-Host "     Authenticated to subscription $($account.id.Substring(0,8))... ✓" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "     Authentication check failed ✗" -ForegroundColor Red
        $allPassed = $false
    }

    # 2. Resource group exists
    Write-Host "  2. Resource group exists..."
    $rg = az group show --name $ResourceGroup 2>$null
    if (-not $rg) {
        Write-Host "     Resource group not found: $ResourceGroup ✗" -ForegroundColor Red
        $allPassed = $false
    }
    else {
        Write-Host "     Resource group exists ✓" -ForegroundColor Green
    }

    # 3. Application Insights exists (from Phase 1)
    Write-Host "  3. Application Insights exists..."
    if ($ApplicationInsightsId -match "^/subscriptions/.*/resourceGroups/.*/providers/microsoft.insights/components/(.*)$") {
        $aiName = $Matches[1]
        $aiResource = az monitor app-insights component show --app $aiName --resource-group $ResourceGroup 2>$null
        if (-not $aiResource) {
            Write-Host "     Application Insights not found: $aiName ✗" -ForegroundColor Red
            Write-Host "     Run Phase 1 provisioning first: python scripts/provision.py" -ForegroundColor Yellow
            $allPassed = $false
        }
        else {
            Write-Host "     Application Insights exists ✓" -ForegroundColor Green
        }
    }
    else {
        Write-Host "     Invalid Application Insights resource ID format ✗" -ForegroundColor Red
        $allPassed = $false
    }

    # 4. Azure CLI version
    Write-Host "  4. Azure CLI version..."
    $azVersion = az version --output json | ConvertFrom-Json
    $azCliVersion = [version]$azVersion.'azure-cli'
    if ($azCliVersion -lt [version]"2.50.0") {
        Write-Host "     Azure CLI version $azCliVersion < 2.50.0 ✗" -ForegroundColor Red
        Write-Host "     Update: az upgrade" -ForegroundColor Yellow
        $allPassed = $false
    }
    else {
        Write-Host "     Azure CLI $azCliVersion ✓" -ForegroundColor Green
    }

    Write-Host ""
    if (-not $allPassed) {
        Write-Host "Pre-deployment validation FAILED. Fix errors above before deploying." -ForegroundColor Red
        return $false
    }

    Write-Host "Pre-deployment validation PASSED." -ForegroundColor Green
    return $true
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Az PowerShell modules | Azure CLI | 2020+ | Azure CLI is lighter weight, cross-platform, and faster to install |
| newGuid() for workbook IDs | Fixed GUIDs in parameter files | ARM templates best practice | Enables idempotent deployment without duplicates |
| Synchronous deployment polling | Native az deployment wait behavior | Azure CLI 2.0+ default | Eliminates custom polling logic |
| Manual JSON string building | Native `--parameters key=value` merging | Azure CLI 2.0+ | Eliminates error-prone string manipulation |

**Deprecated/outdated:**
- **Windows PowerShell 5.1 for cross-platform scripts:** PowerShell 7.0+ is now the standard, supports Linux/macOS
- **Az PowerShell modules for simple deployments:** Azure CLI is preferred for ARM template deployment (Az modules still valid for Graph API, complex SDK operations)

## Open Questions

Things that couldn't be fully resolved:

1. **Should deploy-alerts.ps1 support incremental updates or full redeployment?**
   - What we know: ARM templates support both modes (`--mode Incremental` vs `--mode Complete`)
   - What's unclear: Whether users need ability to add single alert without redeploying all 3 templates
   - Recommendation: Start with incremental mode (safer default), document Complete mode for cleanup scenarios

2. **Should validation checklist be markdown or interactive PowerShell script?**
   - What we know: Markdown is easier to read/print, PowerShell can auto-verify
   - What's unclear: User preference — some orgs prefer checklists for audit trails, others want automation
   - Recommendation: Provide both — validation-checklist.md (human-readable) + Test-DeploymentPrerequisites function (automation-friendly)

3. **How to handle Teams webhook configuration in automation?**
   - What we know: Logic App callback URL must be captured from Phase 1 deployment and passed to Phase 2
   - What's unclear: Whether to store URL in parameter files (security risk) or prompt user to paste it (UX friction)
   - Recommendation: Prompt user to paste URL during script execution, document parameter file option for CI/CD

## Sources

### Primary (HIGH confidence)

- **FSI-AgentGov-Solutions repo structure** - Examined existing solution patterns
  - `C:/dev/FSI-AgentGov-Solutions/agent-observability-foundation/scripts/provision.py` - Python SDK provisioning patterns
  - `C:/dev/FSI-AgentGov-Solutions/conditional-access-automation/scripts/Deploy-CAPolicies.ps1` - PowerShell deployment example
  - `C:/dev/FSI-AgentGov-Solutions/agent-observability-foundation/workbooks/README.md` - Workbook deployment documentation
  - `C:/dev/FSI-AgentGov-Solutions/agent-observability-foundation/alerts/README.md` - Alert deployment order and dependencies
  - `C:/dev/FSI-AgentGov-Solutions/agent-observability-foundation/prerequisites.md` - Prerequisites checklist structure
- **ARM template structure** - `C:/dev/FSI-AgentGov-Solutions/agent-observability-foundation/alerts/ALRT-01-high-failure-rate.json` - Fixed GUID idempotency pattern
- **Phase 1-4 artifacts** - 16 plans completed, providing comprehensive reference material

### Secondary (MEDIUM confidence)

- **Azure CLI documentation patterns** - `az deployment group create --help` (standard Azure CLI deployment syntax)
- **PowerShell best practices** - #Requires directives, Set-StrictMode, $ErrorActionPreference patterns (industry standard)

### Tertiary (LOW confidence)

None — all research based on existing solution artifacts and well-documented Azure CLI patterns.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - PowerShell 7.0+ and Azure CLI are explicit solution conventions
- Architecture: HIGH - Existing provision.py and Deploy-CAPolicies.ps1 provide clear patterns to adapt
- Pitfalls: HIGH - Documented in alerts/README.md deployment order, workbooks/README.md idempotency notes

**Research date:** 2026-02-05
**Valid until:** 90 days (stable — PowerShell and Azure CLI deployment patterns change infrequently)
