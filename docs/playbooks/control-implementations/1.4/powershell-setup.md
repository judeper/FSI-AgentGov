# Control 1.4: Advanced Connector Policies (ACP) - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md).

---

## Prerequisites

```powershell
# Install Power Platform Admin modules
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser
```

---

## Connect to Power Platform

```powershell
# Connect to Power Platform
Add-PowerAppsAccount
```

---

## Enable Managed Environment

```powershell
# Enable Managed Environment (required for ACP)
$EnvironmentName = "your-environment-id-here"
$GovernanceConfiguration = [pscustomobject]@{
    protectionLevel = "Standard"  # Use "Standard" for FSI
    settings = [pscustomobject]@{
        extendedSettings = @{
            # FSI recommended settings
            "limitSharingMode" = "excludeSharingToSecurityGroups"
            "solutionCheckerEnforcement" = "block"
        }
    }
}

Set-AdminPowerAppEnvironmentGovernanceConfiguration `
    -EnvironmentName $EnvironmentName `
    -UpdatedGovernanceConfiguration $GovernanceConfiguration
```

---

## Validate Managed Environment Status

```powershell
# Validation: Check Managed Environment status
Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName |
    Select-Object DisplayName, EnvironmentName, GovernanceConfiguration

Write-Host "Managed Environment enabled. Configure ACP via portal." -ForegroundColor Yellow
```

> **Note:** Advanced Connector Policies currently require portal configuration. PowerShell support is limited as of December 2025.

---

## MCP Audit Logging Configuration

```powershell
# MCP Interaction Logging Configuration
$mcpAuditConfig = @{
    LoggingEnabled = $true
    LogDestination = "Azure Log Analytics"
    RetentionDays = 2190  # 6 years

    EventsToCapture = @(
        "MCP_Connection_Established",
        "MCP_Tool_Invoked",
        "MCP_Resource_Accessed",
        "MCP_Error_Occurred",
        "MCP_Connection_Terminated"
    )

    RequiredFields = @(
        "Timestamp",
        "UserId",
        "AgentId",
        "MCPServerId",
        "MCPServerName",
        "ToolName",
        "Action",
        "DataClassification",
        "ResponseStatus"
    )

    AlertConditions = @(
        @{ Condition = "Unapproved MCP Server"; Severity = "Critical" },
        @{ Condition = "High-volume MCP calls"; Severity = "Warning" },
        @{ Condition = "MCP Error Rate > 10%"; Severity = "Warning" }
    )
}

# Example: Log MCP interaction
function Write-MCPAuditLog {
    param(
        [string]$UserId,
        [string]$AgentId,
        [string]$MCPServerId,
        [string]$ToolName,
        [string]$Action,
        [string]$DataClassification
    )

    $logEntry = @{
        Timestamp = Get-Date -Format "o"
        UserId = $UserId
        AgentId = $AgentId
        MCPServerId = $MCPServerId
        ToolName = $ToolName
        Action = $Action
        DataClassification = $DataClassification
        Source = "MCP_Governance"
    }

    # Send to Log Analytics (implementation varies by setup)
    Write-Host "MCP Audit: $($logEntry | ConvertTo-Json -Compress)"

    return $logEntry
}
```

---

## Evidence Collection via Automation

If your organization collects evidence via automation, capture:

- DLP policies (inventory and scope)
- Environment group membership
- Connector/connection inventory per environment

```powershell
# Get all environments for evidence
Get-AdminPowerAppEnvironment |
    Select-Object DisplayName, EnvironmentName, Location, EnvironmentType |
    Export-Csv -Path "environment-inventory.csv" -NoTypeInformation

# Get DLP policies
Get-DlpPolicy |
    Select-Object PolicyName, CreatedTime, LastModifiedTime |
    Export-Csv -Path "dlp-policy-inventory.csv" -NoTypeInformation
```

> **Note:** PowerShell cmdlet availability varies by module version and tenant configuration; use as evidence support, not as the primary control implementation method.

---

## MCP Governance Policy Template

```yaml
# Model Context Protocol (MCP) Governance Policy
mcp_governance_policy:
  policy_version: "1.0"
  effective_date: "2026-01-15"
  policy_owner: "AI Governance Lead"

  # Default Behavior
  default_stance: "deny"
  approval_required: true

  # Approved MCP Servers
  allowlist:
    - server_id: "MCP-INT-001"
      name: "Internal Document Server"
      type: "internal"
      data_classification: "internal"
      approval_date: "2026-01-10"
      owner: "IT Operations"
      audit_enabled: true

  # Blocked MCP Patterns
  blocklist:
    - pattern: "*community*"
      reason: "Community MCP servers require exception approval"
    - pattern: "*public*"
      reason: "Public MCP servers not permitted in regulated environments"

  # Zone-Specific MCP Rules
  zone_rules:
    zone_1:
      mcp_allowed: false
      rationale: "Personal productivity agents do not use MCP"

    zone_2:
      mcp_allowed: true
      restriction: "Internal MCP servers only"
      approval_required: true

    zone_3:
      mcp_allowed: true
      restriction: "Approved internal + vetted vendor MCP only"
      additional_controls:
        - full_audit_logging
        - data_flow_mapping
        - quarterly_review

  # Audit Requirements
  audit_requirements:
    log_all_connections: true
    log_all_tool_invocations: true
    retention_days: 2190  # 6 years per SEC 17a-4
    export_format: "JSON"
    worm_storage_required: true  # For Zone 3
```

---

## BYOA Policy Template

```yaml
# Bring Your Own Agent (BYOA) Policy
byoa_policy:
  policy_version: "1.0"

  # Personal AI Tools
  personal_ai:
    consumer_ai_tools: "blocked"        # ChatGPT, Gemini, etc.
    personal_copilot: "allowed"         # Microsoft 365 Copilot (licensed)
    exception_process: "None - no exceptions for consumer AI"

  # External AI Agents
  external_agents:
    default_stance: "blocked"
    exception_process: "Full vendor + technical assessment"
    requirements:
      - vendor_risk_assessment
      - technical_security_review
      - data_processing_agreement
      - audit_rights_in_contract
      - integration_with_audit_logging

  # Partner AI Integrations
  partner_ai:
    default_stance: "case-by-case"
    requirements:
      - joint_governance_agreement
      - defined_data_boundaries
      - incident_response_coordination
      - regular_joint_reviews

  # Documentation Requirements
  documentation:
    - architecture_diagram
    - data_flow_mapping
    - risk_assessment_completed
    - approval_record
```

---

*Updated: January 2026 | Version: v1.1*
