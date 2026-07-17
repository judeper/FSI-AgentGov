Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-InsiderRiskFailureClassification {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Message,
        [Parameter()][string]$CommandName = ''
    )

    $text = $Message.ToLowerInvariant()
    $category = 'unknown'
    $guidance = 'Collect portal evidence manually and escalate to Purview engineering support if required.'

    if (
        $text -match 'commandnotfoundexception' -or
        $text -match 'is not recognized as the name of a cmdlet' -or
        $text -match 'could not find command' -or
        $text -match 'cmdlet .+ not (present|found|available)'
    ) {
        $category = 'command_not_found'
        $guidance = 'Treat as unsupported automation surface. Do not map this to licensing. Collect Insider Risk policy evidence manually from the Purview portal.'
    }
    elseif (
        $text -match 'unsupported' -or
        $text -match 'not supported' -or
        $text -match 'preview'
    ) {
        $category = 'unsupported_surface'
        $guidance = 'Use only first-party documented GA surfaces. Collect policy inventory through manual portal export.'
    }
    elseif (
        $text -match 'insufficient\s+(license|licenses|licensing|service\s*plan|service\s*plans|subscription|sku)' -or
        $text -match 'requires?\s+an?\s+eligible\s+(license|service\s*plan|subscription)' -or
        $text -match 'license' -or
        $text -match 'licensing' -or
        $text -match 'service plan' -or
        $text -match 'subscription' -or
        $text -match '\bsku\b' -or
        $text -match 'not enabled for your organization' -or
        $text -match 'feature is not available'
    ) {
        $category = 'licensing'
        $guidance = 'Validate Purview Insider Risk licensing and service-plan assignment.'
    }
    elseif (
        $text -match 'access is denied' -or
        $text -match 'unauthorized' -or
        $text -match 'forbidden' -or
        $text -match 'not authorized' -or
        $text -match 'permission' -or
        $text -match 'privilege' -or
        $text -match 'insufficient\s+(permission|permissions|privilege|privileges|rights|role|roles|authorization)'
    ) {
        $category = 'auth_or_permission'
        $guidance = 'Validate IRM role-group assignment and Security & Compliance session permissions.'
    }

    [PSCustomObject]@{
        Category    = $category
        CommandName = $CommandName
        Message     = $Message
        Guidance    = $guidance
    }
}

function Get-InsiderRiskUnifiedAuditDependencyState {
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object]$AuditConfig
    )

    $state = [ordered]@{
        Status                   = 'unknown'
        Source                   = 'Section 1 auditConfig.UnifiedAuditLogIngestionEnabled'
        UnifiedAuditDependencyMet = $null
        Classification           = 'unknown'
        Detail                   = 'Audit dependency could not be derived because Section 1 audit configuration is missing or incomplete.'
    }

    if ($null -eq $AuditConfig) {
        return [PSCustomObject]$state
    }

    $rawValue = $null
    $hasField = $false

    if ($AuditConfig -is [System.Collections.IDictionary]) {
        $hasField = $AuditConfig.Contains('UnifiedAuditLogIngestionEnabled')
        if ($hasField) {
            $rawValue = $AuditConfig['UnifiedAuditLogIngestionEnabled']
        }
    }
    elseif ($AuditConfig.PSObject -and $AuditConfig.PSObject.Properties.Name -contains 'UnifiedAuditLogIngestionEnabled') {
        $hasField = $true
        $rawValue = $AuditConfig.UnifiedAuditLogIngestionEnabled
    }

    if (-not $hasField) {
        return [PSCustomObject]$state
    }

    $normalized = $null
    if ($rawValue -is [bool]) {
        $normalized = $rawValue
    }
    elseif ($rawValue -is [string]) {
        $parsed = $false
        if ([bool]::TryParse($rawValue, [ref]$parsed)) {
            $normalized = $parsed
        }
    }

    if ($null -eq $normalized) {
        $state.Detail = 'Audit dependency could not be derived because UnifiedAuditLogIngestionEnabled is not a reliable boolean value.'
        return [PSCustomObject]$state
    }

    $state.Status = 'collected'
    $state.UnifiedAuditDependencyMet = [bool]$normalized
    if ($normalized) {
        $state.Classification = $null
        $state.Detail = 'Unified Audit Log ingestion is enabled; prerequisite audit signal for Insider Risk evidence is met.'
    }
    else {
        $state.Classification = 'audit_dependency_not_met'
        $state.Detail = 'Unified Audit Log ingestion is disabled; Insider Risk evidence must be treated as incomplete until audit ingestion is restored.'
    }

    [PSCustomObject]$state
}

function New-InsiderRiskEvidence {
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object]$AuditConfig
    )

    $policyMessage = 'Insider Risk policy inventory automation is not supported on a first-party documented GA surface.'
    $policyClassification = Get-InsiderRiskFailureClassification -Message $policyMessage -CommandName 'Get-InsiderRiskPolicy'
    $auditState = Get-InsiderRiskUnifiedAuditDependencyState -AuditConfig $AuditConfig

    [ordered]@{
        policyInventory = [ordered]@{
            status                 = 'manual_required'
            automationSupported    = $false
            classification         = $policyClassification.Category
            detail                 = "$($policyClassification.Message) $($policyClassification.Guidance)".Trim()
            manualEvidenceRequired = @(
                'Purview portal export: Insider Risk Management > Policies (name, template, status, scope).',
                'Purview portal export: Alerts reviewed/dispositioned for the current quarter.',
                'Reviewer attestation linking alert dispositions to case records.'
            )
        }
        auditDependency = [ordered]@{
            status                   = $auditState.Status
            evidenceSource           = $auditState.Source
            unifiedAuditDependencyMet = $auditState.UnifiedAuditDependencyMet
            classification           = $auditState.Classification
            detail                   = $auditState.Detail
        }
    }
}
