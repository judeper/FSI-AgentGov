# Conditional Access Agent Identity Templates

> This playbook provides agent-specific Conditional Access policy templates for [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md).

---

## Overview

This playbook provides production-ready Conditional Access (CA) policy recipes for agent identity governance. These templates address both **agent creators** (humans who build and publish agents) and **Agentic Users** (AI agent identities in Entra ID).

!!! note "Preview Features"
    Microsoft Entra Agent ID and Agentic Users are preview features. Templates include both GA baseline configurations and preview-specific enhancements.

---

## Prerequisites

- Microsoft Entra ID P1/P2 licenses assigned
- Emergency access (break-glass) accounts configured
- Authentication strengths defined (see [Portal Walkthrough](portal-walkthrough.md))
- Agent inventory completed ([Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md))
- Security groups created for agent creators and sponsors

---

## Security Groups Setup

Before implementing policies, create the following security groups:

| Group Name | Purpose | Members |
|------------|---------|---------|
| `sg-agent-creators-zone1` | Personal agent creators | Self-managed |
| `sg-agent-creators-zone2` | Team agent publishers | Approved makers |
| `sg-agent-creators-zone3` | Enterprise agent admins | PIM-eligible only |
| `sg-agent-sponsors` | Human sponsors for Agentic Users | Director+ level |
| `sg-breakglass-accounts` | Emergency access accounts | 2 cloud-only accounts |
| `sg-agent-cicd-principals` | Service principals for automation | DevOps pipelines |

---

## Policy 1: Zone 1 Baseline - Agent Creator MFA

**Purpose:** Enforce baseline MFA for all users creating personal productivity agents.

**Scoping:** All users accessing Copilot Studio or Power Apps Maker Portal.

### Configuration

| Setting | Value |
|---------|-------|
| **Name** | `FSI-Z1-AgentCreators-BaselineMFA` |
| **State** | Enabled |
| **Users** | All users |
| **Exclude** | `sg-breakglass-accounts` |
| **Cloud apps** | Power Apps, Power Apps Maker Portal, Copilot Studio |
| **Conditions** | None |
| **Grant** | Require multifactor authentication |
| **Session** | Sign-in frequency: 12 hours |

### PowerShell Implementation

```powershell
# Zone 1: Baseline MFA for Agent Creators
$params = @{
    DisplayName = "FSI-Z1-AgentCreators-BaselineMFA"
    State = "enabled"
    Conditions = @{
        Users = @{
            IncludeUsers = @("All")
            ExcludeGroups = @("sg-breakglass-accounts")
        }
        Applications = @{
            IncludeApplications = @(
                "9e0c93b0-c0e0-4cd8-9c2e-3e396d76e3e0",  # Power Apps
                "51c00ca4-e94c-4e91-8e0f-b9e6d4e7e9f3",  # Copilot Studio
                "12a0c4dd-9e59-4f3a-9e3d-9e8e8e8e8e8e"   # Power Apps Maker
            )
        }
    }
    GrantControls = @{
        BuiltInControls = @("mfa")
        Operator = "OR"
    }
    SessionControls = @{
        SignInFrequency = @{
            Value = 12
            Type = "hours"
            IsEnabled = $true
        }
    }
}
New-MgIdentityConditionalAccessPolicy -BodyParameter $params
```

### Evidence Queries

```kql
// Monitor Zone 1 agent creator sign-ins
SigninLogs
| where TimeGenerated > ago(7d)
| where ConditionalAccessPolicies has "FSI-Z1-AgentCreators-BaselineMFA"
| extend policyResult = tostring(ConditionalAccessPolicies[0].result)
| summarize
    totalSignIns = count(),
    mfaSatisfied = countif(policyResult == "success"),
    mfaRequired = countif(policyResult == "failure")
    by bin(TimeGenerated, 1d)
| order by TimeGenerated desc
```

---

## Policy 2: Zone 2 Team Agent Publisher

**Purpose:** Require phishing-resistant MFA and device compliance for team agent publishers.

**Scoping:** Members of Zone 2 agent creator group accessing agent management portals.

### Configuration

| Setting | Value |
|---------|-------|
| **Name** | `FSI-Z2-AgentPublishers-PhishingResistant` |
| **State** | Enabled |
| **Users** | `sg-agent-creators-zone2` |
| **Exclude** | `sg-breakglass-accounts` |
| **Cloud apps** | Power Apps, Copilot Studio, Power Platform Admin Center |
| **Conditions** | Client apps: Browser, Mobile apps and desktop clients |
| **Grant** | Require authentication strength: Phishing-resistant MFA **AND** Require compliant device |
| **Session** | Sign-in frequency: 4 hours; Persistent browser session: Never |

### PowerShell Implementation

```powershell
# Zone 2: Phishing-Resistant MFA + Device Compliance
$params = @{
    DisplayName = "FSI-Z2-AgentPublishers-PhishingResistant"
    State = "enabled"
    Conditions = @{
        Users = @{
            IncludeGroups = @("sg-agent-creators-zone2")
            ExcludeGroups = @("sg-breakglass-accounts")
        }
        Applications = @{
            IncludeApplications = @(
                "9e0c93b0-c0e0-4cd8-9c2e-3e396d76e3e0",  # Power Apps
                "51c00ca4-e94c-4e91-8e0f-b9e6d4e7e9f3",  # Copilot Studio
                "5e3ce6c0-2b1f-4285-8d4b-75ee78787346"   # PPAC
            )
        }
        ClientAppTypes = @("browser", "mobileAppsAndDesktopClients")
    }
    GrantControls = @{
        AuthenticationStrength = @{
            Id = "00000000-0000-0000-0000-000000000004"  # Phishing-resistant MFA
        }
        BuiltInControls = @("compliantDevice")
        Operator = "AND"
    }
    SessionControls = @{
        SignInFrequency = @{
            Value = 4
            Type = "hours"
            IsEnabled = $true
        }
        PersistentBrowser = @{
            Mode = "never"
            IsEnabled = $true
        }
    }
}
New-MgIdentityConditionalAccessPolicy -BodyParameter $params
```

### Evidence Queries

```kql
// Zone 2 publisher authentication compliance
SigninLogs
| where TimeGenerated > ago(30d)
| where ConditionalAccessPolicies has "FSI-Z2-AgentPublishers"
| extend
    authMethod = tostring(AuthenticationDetails[0].authenticationMethod),
    deviceCompliant = DeviceDetail.isCompliant
| summarize
    totalAttempts = count(),
    phishingResistant = countif(authMethod in ("FIDO2", "Certificate")),
    deviceCompliant = countif(deviceCompliant == true),
    failures = countif(ResultType != 0)
    by UserPrincipalName
| where failures > 0 or phishingResistant < totalAttempts
| order by failures desc
```

---

## Policy 3: Zone 3 Enterprise Agent Admin

**Purpose:** Maximum security for enterprise agent administrators with PIM integration, compliant devices, and session controls.

**Scoping:** Zone 3 agent administrators accessing any agent management capability.

### Configuration

| Setting | Value |
|---------|-------|
| **Name** | `FSI-Z3-EnterpriseAgentAdmin-Maximum` |
| **State** | Enabled |
| **Users** | `sg-agent-creators-zone3` |
| **Exclude** | `sg-breakglass-accounts` |
| **Cloud apps** | All cloud apps (when accessing from agent admin context) |
| **Conditions** | All client apps; All locations (including trusted) |
| **Grant** | Require authentication strength: Phishing-resistant MFA **AND** Require compliant device **AND** Require approved client app |
| **Session** | Sign-in frequency: 1 hour; Conditional Access App Control: Block downloads |

### PowerShell Implementation

```powershell
# Zone 3: Maximum Security for Enterprise Agent Admins
$params = @{
    DisplayName = "FSI-Z3-EnterpriseAgentAdmin-Maximum"
    State = "enabled"
    Conditions = @{
        Users = @{
            IncludeGroups = @("sg-agent-creators-zone3")
            ExcludeGroups = @("sg-breakglass-accounts")
        }
        Applications = @{
            IncludeApplications = @("All")
        }
        ClientAppTypes = @("all")
    }
    GrantControls = @{
        AuthenticationStrength = @{
            Id = "00000000-0000-0000-0000-000000000004"  # Phishing-resistant MFA
        }
        BuiltInControls = @("compliantDevice", "approvedApplication")
        Operator = "AND"
    }
    SessionControls = @{
        SignInFrequency = @{
            Value = 1
            Type = "hours"
            IsEnabled = $true
        }
        CloudAppSecurity = @{
            CloudAppSecurityType = "blockDownloads"
            IsEnabled = $true
        }
    }
}
New-MgIdentityConditionalAccessPolicy -BodyParameter $params
```

### PIM Integration Requirements

Zone 3 agent administrators must activate their role through PIM before policies apply:

1. **PIM Role:** Power Platform Admin or custom Agent Admin role
2. **Activation Duration:** Maximum 4 hours
3. **Approval Required:** AI Governance Lead + Compliance Officer
4. **Justification:** Required with ticket reference
5. **MFA at Activation:** Phishing-resistant required

```powershell
# Configure PIM settings for Zone 3 agent admin role
$roleDefinitionId = (Get-MgRoleManagementDirectoryRoleDefinition -Filter "displayName eq 'Power Platform Administrator'").Id

$settings = @{
    Rules = @(
        @{
            "@odata.type" = "#microsoft.graph.unifiedRoleManagementPolicyExpirationRule"
            Id = "Expiration_EndUser_Assignment"
            MaximumDuration = "PT4H"
        }
        @{
            "@odata.type" = "#microsoft.graph.unifiedRoleManagementPolicyAuthenticationContextRule"
            Id = "AuthenticationContext_EndUser_Assignment"
            IsEnabled = $true
            ClaimValue = "c1"  # Phishing-resistant auth context
        }
        @{
            "@odata.type" = "#microsoft.graph.unifiedRoleManagementPolicyApprovalRule"
            Id = "Approval_EndUser_Assignment"
            Setting = @{
                IsApprovalRequired = $true
                ApprovalStages = @(
                    @{
                        ApprovalStageTimeOutInDays = 1
                        PrimaryApprovers = @(
                            @{
                                "@odata.type" = "#microsoft.graph.groupMembers"
                                GroupId = "sg-ai-governance-approvers"
                            }
                        )
                    }
                )
            }
        }
    )
}
```

### Evidence Queries

```kql
// Zone 3 admin activity with PIM correlation
let pimActivations = AuditLogs
| where TimeGenerated > ago(7d)
| where OperationName == "Add member to role completed (PIM activation)"
| extend userId = tostring(TargetResources[0].id)
| project ActivationTime = TimeGenerated, userId, RoleName = tostring(TargetResources[0].displayName);

SigninLogs
| where TimeGenerated > ago(7d)
| where ConditionalAccessPolicies has "FSI-Z3-EnterpriseAgentAdmin"
| extend userId = UserId
| join kind=leftouter pimActivations on userId
| extend
    hadPimActivation = isnotnull(ActivationTime),
    timeSinceActivation = datetime_diff('minute', TimeGenerated, ActivationTime)
| summarize
    totalSignIns = count(),
    withPim = countif(hadPimActivation and timeSinceActivation < 240),
    withoutPim = countif(not(hadPimActivation) or timeSinceActivation >= 240)
    by UserPrincipalName
```

---

## Policy 4: Break-Glass Emergency Access

**Purpose:** Provide emergency administrative access when primary authentication is unavailable.

**Scoping:** Cloud-only emergency access accounts with minimal restrictions.

### Configuration

| Setting | Value |
|---------|-------|
| **Name** | `FSI-BreakGlass-EmergencyAccess` |
| **State** | Enabled |
| **Users** | `sg-breakglass-accounts` |
| **Cloud apps** | All cloud apps |
| **Conditions** | None |
| **Grant** | Block access (inverted - other policies must explicitly exclude) |

### Break-Glass Account Requirements

| Requirement | Configuration |
|-------------|---------------|
| **Account Type** | Cloud-only (no federation) |
| **Password** | 128+ character random, stored in physical safe |
| **MFA** | Enrolled with hardware key stored separately |
| **Monitoring** | Immediate alert on any sign-in attempt |
| **Testing** | Quarterly verification without actual use |
| **Documentation** | Sealed envelope with dual-control access |

### Monitoring Query

```kql
// CRITICAL: Break-glass account usage alert
SigninLogs
| where TimeGenerated > ago(1h)
| where UserPrincipalName in ("breakglass1@contoso.com", "breakglass2@contoso.com")
| project
    TimeGenerated,
    UserPrincipalName,
    IPAddress,
    Location,
    AppDisplayName,
    ResultType,
    ResultDescription,
    DeviceDetail
| extend
    AlertSeverity = "Critical",
    AlertMessage = strcat("Break-glass account used: ", UserPrincipalName)
```

---

## Policy 5: CI/CD Service Principal for Automated Publishing

**Purpose:** Enable automated agent publishing through DevOps pipelines with appropriate controls.

**Scoping:** Service principals used for ALM pipeline deployments.

### Configuration

| Setting | Value |
|---------|-------|
| **Name** | `FSI-CICD-AgentPublishing-ServicePrincipal` |
| **State** | Enabled |
| **Users** | Workload identities: `sg-agent-cicd-principals` |
| **Cloud apps** | Power Platform, Dataverse |
| **Conditions** | Filter for devices: Managed Identity |
| **Grant** | Require compliant network location |
| **Session** | None (non-interactive) |

### Service Principal Requirements

| Requirement | Zone 2 | Zone 3 |
|-------------|--------|--------|
| **Identity Type** | Managed Identity preferred | Managed Identity required |
| **Certificate Auth** | Recommended | Required |
| **Network Restrictions** | Azure DevOps IP ranges | Private endpoint required |
| **Permissions** | Environment-scoped | Explicitly granted per environment |
| **Credential Rotation** | 90 days | 30 days |
| **Activity Logging** | Standard | Enhanced with correlation ID |

### PowerShell Implementation

```powershell
# Service principal CA policy for CI/CD
$params = @{
    DisplayName = "FSI-CICD-AgentPublishing-ServicePrincipal"
    State = "enabled"
    Conditions = @{
        ClientApplications = @{
            IncludeServicePrincipals = @("sg-agent-cicd-principals")
        }
        Applications = @{
            IncludeApplications = @(
                "9e0c93b0-c0e0-4cd8-9c2e-3e396d76e3e0",  # Power Apps
                "00000007-0000-0000-c000-000000000000"   # Dataverse
            )
        }
    }
    GrantControls = @{
        BuiltInControls = @("compliantNetworkLocation")
        Operator = "OR"
    }
}
New-MgIdentityConditionalAccessPolicy -BodyParameter $params

# Configure named location for Azure DevOps
$locationParams = @{
    DisplayName = "Azure-DevOps-Hosted-Agents"
    IsTrusted = $true
    IpRanges = @(
        @{
            "@odata.type" = "#microsoft.graph.iPv4CidrRange"
            CidrAddress = "13.107.6.0/24"
        }
        @{
            "@odata.type" = "#microsoft.graph.iPv4CidrRange"
            CidrAddress = "13.107.9.0/24"
        }
        # Add additional Azure DevOps IP ranges per region
    )
}
New-MgIdentityConditionalAccessNamedLocation -BodyParameter $locationParams
```

### Evidence Queries

```kql
// CI/CD service principal authentication audit
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(7d)
| where ServicePrincipalName has "agent" or ServicePrincipalName has "cicd"
| extend
    resourceAccessed = ResourceDisplayName,
    authMethod = AuthenticationProcessingDetails
| summarize
    totalAuth = count(),
    uniqueResources = dcount(resourceAccessed),
    uniqueIPs = dcount(IPAddress)
    by ServicePrincipalName, bin(TimeGenerated, 1d)
| order by TimeGenerated desc
```

---

## Agentic User Policies (Preview)

The following policies apply to Agentic User identities created through Microsoft Entra Agent ID.

### Policy 6: Agentic User Authentication Controls

**Purpose:** Control how Agentic Users authenticate and access resources.

**Scoping:** All Agentic User identities (userType = AgenticUser).

### Configuration

| Setting | Value |
|---------|-------|
| **Name** | `FSI-AgenticUser-AuthenticationControls` |
| **State** | Report-only (preview) |
| **Users** | Filter: userType eq 'AgenticUser' |
| **Cloud apps** | All cloud apps |
| **Conditions** | All locations |
| **Grant** | Require managed identity authentication |
| **Session** | Continuous access evaluation: Enabled |

!!! warning "Preview Limitation"
    Agentic User filtering in Conditional Access is a preview feature. Test thoroughly in report-only mode before enabling.

### Evidence Query for Agentic User Activity

```kql
// Agentic User sign-in patterns
SigninLogs
| where TimeGenerated > ago(30d)
| where UserType == "AgenticUser" or UserPrincipalName contains "agent"
| extend
    sponsorId = tostring(parse_json(AuthenticationDetails).sponsorId),
    agentZone = case(
        UserPrincipalName contains "z3", "Zone 3",
        UserPrincipalName contains "z2", "Zone 2",
        "Zone 1"
    )
| summarize
    totalInteractions = count(),
    uniqueResources = dcount(ResourceDisplayName),
    uniqueIPs = dcount(IPAddress),
    failures = countif(ResultType != 0)
    by UserPrincipalName, agentZone, sponsorId, bin(TimeGenerated, 1d)
| order by failures desc, totalInteractions desc
```

---

## Exclusion Patterns

### Recommended Exclusions

| Exclusion | Applies To | Rationale |
|-----------|------------|-----------|
| Break-glass accounts | All policies | Emergency access |
| Directory sync accounts | Device compliance policies | Service accounts |
| Guest users (if applicable) | Zone-specific policies | Separate B2B policies |
| Specific service principals | MFA policies | Non-interactive auth |

### Exclusion Governance

1. **Document all exclusions** in the agent registry
2. **Review quarterly** with Compliance Officer sign-off
3. **Compensating controls** required for each exclusion
4. **Alert on exclusion usage** patterns

```powershell
# Audit CA policy exclusions
Get-MgIdentityConditionalAccessPolicy | ForEach-Object {
    $policy = $_
    [PSCustomObject]@{
        PolicyName = $policy.DisplayName
        ExcludedUsers = $policy.Conditions.Users.ExcludeUsers -join ", "
        ExcludedGroups = $policy.Conditions.Users.ExcludeGroups -join ", "
        State = $policy.State
    }
} | Export-Csv -Path "CA-Exclusions-Audit.csv" -NoTypeInformation
```

---

## Monitoring and Evidence Collection

### Daily Monitoring Queries

```kql
// Daily CA policy effectiveness report
SigninLogs
| where TimeGenerated > ago(24h)
| where ConditionalAccessPolicies has "FSI"
| extend
    policyName = tostring(ConditionalAccessPolicies[0].displayName),
    policyResult = tostring(ConditionalAccessPolicies[0].result)
| summarize
    applied = countif(policyResult == "success"),
    notApplied = countif(policyResult == "notApplied"),
    failed = countif(policyResult == "failure")
    by policyName
| order by failed desc
```

### Weekly Compliance Report

```powershell
# Generate weekly CA compliance report
$report = @()
$policies = Get-MgIdentityConditionalAccessPolicy | Where-Object { $_.DisplayName -like "FSI-*" }

foreach ($policy in $policies) {
    $signIns = Get-MgAuditLogSignIn -Filter "conditionalAccessPolicies/any(c:c/displayName eq '$($policy.DisplayName)')" -Top 1000

    $report += [PSCustomObject]@{
        PolicyName = $policy.DisplayName
        State = $policy.State
        TotalEvaluations = $signIns.Count
        Applied = ($signIns | Where-Object { $_.ConditionalAccessPolicies.Result -eq "success" }).Count
        Failures = ($signIns | Where-Object { $_.ConditionalAccessPolicies.Result -eq "failure" }).Count
        LastModified = $policy.ModifiedDateTime
    }
}

$report | Export-Csv -Path "FSI-CA-Weekly-Report-$(Get-Date -Format 'yyyy-MM-dd').csv" -NoTypeInformation
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Agent creators blocked unexpectedly | Missing group membership | Verify `sg-agent-creators-zoneX` membership |
| MFA prompt loop | Authentication strength mismatch | Verify user has registered phishing-resistant method |
| Service principal failures | Network location not recognized | Add DevOps agent IPs to named location |
| PIM activation blocked | Missing approval | Check PIM approval queue |
| Break-glass not working | Exclusion missing from policy | Verify exclusion in all blocking policies |

### What-If Testing

Before enabling any policy, test with What-If:

1. Navigate to **Entra ID** > **Conditional Access** > **What If**
2. Select target user or service principal
3. Select target application
4. Click **What If**
5. Review which policies would apply
6. Verify break-glass exclusions function correctly

---

## Related Resources

- [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) - Parent control
- [Agent Identity Architecture](../../../framework/agent-identity-architecture.md) - Agent ID vs Blueprint guidance
- [Portal Walkthrough](portal-walkthrough.md) - Step-by-step portal configuration
- [PowerShell Setup](powershell-setup.md) - Automation scripts

---

*Updated: January 2026 | Version: v1.2.6*
