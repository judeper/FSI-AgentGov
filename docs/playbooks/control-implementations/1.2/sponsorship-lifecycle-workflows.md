# Sponsorship Lifecycle Workflows

> This playbook provides Entra ID Lifecycle Workflows configuration for agent sponsorship governance, supporting [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) and the [Agent Identity Architecture](../../../framework/agent-identity-architecture.md).

---

## Overview

Human sponsorship is a foundational requirement for Agentic Users in Microsoft Entra ID. This playbook provides step-by-step configuration for automating sponsor reviews, handling sponsor departures, and maintaining accountability chains for AI agents.

!!! note "Preview Features"
    Microsoft Entra Agent ID and Agentic Users are preview features. Lifecycle Workflows for Agentic Users may have limited functionality compared to standard user workflows.

---

## Prerequisites

- Microsoft Entra ID Governance license (P2 or Governance SKU)
- Lifecycle Workflows enabled in tenant
- Agent inventory with sponsor assignments (Control 3.1)
- Security groups for sponsor eligibility
- Email/Teams configured for notifications

---

## Sponsorship Model

### Sponsor Requirements by Zone

| Requirement | Zone 1 | Zone 2 | Zone 3 |
|-------------|--------|--------|--------|
| **Minimum Role** | Any licensed user | Manager level | Director level |
| **Approval Chain** | Self-sponsor | Manager approval | Director + Compliance |
| **Maximum Agents** | 10 | 5 | 3 |
| **Training Required** | Recommended | Required | Required + Certification |
| **Backup Sponsor** | Optional | Recommended | Required |

### Sponsor Responsibilities

| Responsibility | Frequency | Evidence |
|----------------|-----------|----------|
| Review agent activity | Weekly (Z3), Monthly (Z2) | Activity report sign-off |
| Attestation of continued need | Per schedule | Attestation record |
| Respond to security alerts | Within SLA | Incident response record |
| Approve configuration changes | Per change | Change approval record |
| Maintain agent documentation | Ongoing | Registry metadata |

---

## Step 1: Configure Lifecycle Workflows Prerequisites

### Enable Lifecycle Workflows

**Portal Path:** Entra ID > Identity Governance > Lifecycle Workflows

1. Navigate to **Microsoft Entra admin center**
2. Go to **Identity Governance** > **Lifecycle Workflows**
3. Verify Lifecycle Workflows is enabled
4. Review **Workflow settings** for notification preferences

### Create Sponsor Eligibility Groups

```powershell
# Create security groups for sponsor eligibility
$groups = @(
    @{
        DisplayName = "sg-agent-sponsors-zone1"
        Description = "Eligible sponsors for Zone 1 agents"
        MailNickname = "agent-sponsors-z1"
    },
    @{
        DisplayName = "sg-agent-sponsors-zone2"
        Description = "Eligible sponsors for Zone 2 agents (Manager+)"
        MailNickname = "agent-sponsors-z2"
    },
    @{
        DisplayName = "sg-agent-sponsors-zone3"
        Description = "Eligible sponsors for Zone 3 agents (Director+)"
        MailNickname = "agent-sponsors-z3"
    },
    @{
        DisplayName = "sg-agent-sponsors-backup"
        Description = "Backup sponsors for all zones"
        MailNickname = "agent-sponsors-backup"
    }
)

foreach ($group in $groups) {
    New-MgGroup -DisplayName $group.DisplayName `
                -Description $group.Description `
                -MailNickname $group.MailNickname `
                -MailEnabled:$false `
                -SecurityEnabled:$true
}
```

---

## Step 2: Create Periodic Sponsor Review Workflows

### Zone 2 Quarterly Review Workflow

**Portal Path:** Lifecycle Workflows > + New workflow

1. Click **+ New workflow**
2. Select **Custom workflow**
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `FSI-Z2-Quarterly-Sponsor-Review` |
| **Description** | Quarterly sponsor attestation for Zone 2 agents |
| **Category** | Custom |
| **Trigger** | Scheduled (every 90 days) |

4. **Execution conditions:**
   - User type: AgenticUser (when available) or attribute filter
   - Attribute: `extension_GovernanceZone` equals "Zone2"

5. **Tasks:**

| Order | Task | Configuration |
|-------|------|---------------|
| 1 | Send email | Notify sponsor of pending review |
| 2 | Request approval | Single-stage approval from sponsor |
| 3 | Run custom extension (if approved) | Update attestation date |
| 4 | Run custom extension (if rejected) | Suspend agent, notify compliance |

### PowerShell: Create Zone 2 Review Workflow

```powershell
# Create Zone 2 Quarterly Review Workflow
$workflowParams = @{
    DisplayName = "FSI-Z2-Quarterly-Sponsor-Review"
    Description = "Quarterly sponsor attestation for Zone 2 agents"
    IsEnabled = $true
    IsSchedulingEnabled = $true
    Category = "leaver"  # Using leaver category for scheduled reviews
    ExecutionConditions = @{
        Scope = @{
            "@odata.type" = "#microsoft.graph.identityGovernance.ruleBasedSubjectSet"
            Rule = "(user.extension_GovernanceZone -eq 'Zone2') and (user.userType -eq 'AgenticUser')"
        }
        Trigger = @{
            "@odata.type" = "#microsoft.graph.identityGovernance.timeBasedAttributeTrigger"
            TimeBasedAttribute = "createdDateTime"
            OffsetInDays = 90
        }
    }
    Tasks = @(
        @{
            ContinueOnError = $false
            DisplayName = "Send sponsor review notification"
            IsEnabled = $true
            TaskDefinitionId = "aab41899-9972-422a-9a53-f4bb8b36b8ae"  # Send email
            Arguments = @(
                @{
                    Name = "emailSubject"
                    Value = "ACTION REQUIRED: Quarterly Agent Sponsor Review - {{displayName}}"
                }
                @{
                    Name = "emailBody"
                    Value = "Your sponsored agent requires quarterly attestation. Please review agent activity and confirm continued business need within 14 days."
                }
                @{
                    Name = "emailRecipients"
                    Value = "{{sponsor}}"
                }
            )
        },
        @{
            ContinueOnError = $false
            DisplayName = "Request sponsor attestation"
            IsEnabled = $true
            TaskDefinitionId = "22085229-5809-45e8-97fd-270d28d66910"  # Request approval
            Arguments = @(
                @{
                    Name = "approvers"
                    Value = "{{sponsor}}"
                }
                @{
                    Name = "requestSubject"
                    Value = "Agent Sponsor Attestation: {{displayName}}"
                }
                @{
                    Name = "requestBody"
                    Value = "Please confirm this agent is still required for business operations."
                }
                @{
                    Name = "escalationRecipients"
                    Value = "sg-compliance-officers"
                }
                @{
                    Name = "escalationAfterDays"
                    Value = "7"
                }
            )
        }
    )
}

New-MgIdentityGovernanceLifecycleWorkflow -BodyParameter $workflowParams
```

### Zone 3 Monthly Review Workflow

Create a similar workflow with these differences:

| Setting | Zone 2 Value | Zone 3 Value |
|---------|--------------|--------------|
| Trigger frequency | 90 days | 30 days |
| Approval stages | Single (sponsor) | Dual (sponsor + compliance) |
| Escalation time | 7 days | 3 days |
| Non-attestation action | Suspend | Suspend + alert security |

```powershell
# Zone 3 Monthly Review - dual approval
$zone3Tasks = @(
    @{
        DisplayName = "Send sponsor review notification"
        TaskDefinitionId = "aab41899-9972-422a-9a53-f4bb8b36b8ae"
        # Email configuration
    },
    @{
        DisplayName = "Request sponsor attestation"
        TaskDefinitionId = "22085229-5809-45e8-97fd-270d28d66910"
        Arguments = @(
            @{ Name = "approvers"; Value = "{{sponsor}}" }
            @{ Name = "escalationAfterDays"; Value = "3" }
        )
    },
    @{
        DisplayName = "Request compliance attestation"
        TaskDefinitionId = "22085229-5809-45e8-97fd-270d28d66910"
        Arguments = @(
            @{ Name = "approvers"; Value = "sg-compliance-officers" }
            @{ Name = "escalationAfterDays"; Value = "3" }
        )
    },
    @{
        DisplayName = "Update attestation record"
        TaskDefinitionId = "4262b724-8dba-4fad-afc3-43fcbb497a0e"  # Custom extension
        Arguments = @(
            @{ Name = "extensionId"; Value = "{{attestationExtensionId}}" }
        )
    }
)
```

---

## Step 3: Configure Sponsor Departure Handling

### Workflow: Sponsor Leaves Organization

**Trigger:** When a user (sponsor) leaves the organization

**Purpose:** Automatically handle agent reassignment when a sponsor departs

```powershell
# Sponsor Departure Workflow
$sponsorDepartureWorkflow = @{
    DisplayName = "FSI-Sponsor-Departure-Handler"
    Description = "Handle agent reassignment when sponsor leaves organization"
    IsEnabled = $true
    Category = "leaver"
    ExecutionConditions = @{
        Scope = @{
            "@odata.type" = "#microsoft.graph.identityGovernance.ruleBasedSubjectSet"
            Rule = "(user.memberOf -any (group.displayName -eq 'sg-agent-sponsors-zone2')) or (user.memberOf -any (group.displayName -eq 'sg-agent-sponsors-zone3'))"
        }
        Trigger = @{
            "@odata.type" = "#microsoft.graph.identityGovernance.membershipChangeTrigger"
            ChangeType = "remove"
        }
    }
    Tasks = @(
        @{
            DisplayName = "Identify sponsored agents"
            TaskDefinitionId = "4262b724-8dba-4fad-afc3-43fcbb497a0e"
            Arguments = @(
                @{
                    Name = "extensionId"
                    Value = "{{identifySponsoredAgentsExtensionId}}"
                }
            )
        },
        @{
            DisplayName = "Notify backup sponsor"
            TaskDefinitionId = "aab41899-9972-422a-9a53-f4bb8b36b8ae"
            Arguments = @(
                @{ Name = "emailSubject"; Value = "URGENT: Agent Sponsor Departure - Reassignment Required" }
                @{ Name = "emailBody"; Value = "{{departingSponsorName}} has left the organization. The following agents require reassignment: {{sponsoredAgents}}" }
                @{ Name = "emailRecipients"; Value = "{{backupSponsor}},{{managerEmail}}" }
            )
        },
        @{
            DisplayName = "Start 14-day reassignment timer"
            TaskDefinitionId = "4262b724-8dba-4fad-afc3-43fcbb497a0e"
            Arguments = @(
                @{
                    Name = "extensionId"
                    Value = "{{startReassignmentTimerExtensionId}}"
                }
            )
        }
    )
}

New-MgIdentityGovernanceLifecycleWorkflow -BodyParameter $sponsorDepartureWorkflow
```

### Workflow: Auto-Suspend After Reassignment Deadline

**Trigger:** 14 days after sponsor departure without reassignment

```powershell
# Agent Auto-Suspend Workflow
$autoSuspendWorkflow = @{
    DisplayName = "FSI-Agent-AutoSuspend-NoSponsor"
    Description = "Suspend agents without sponsor after 14-day grace period"
    IsEnabled = $true
    Category = "custom"
    ExecutionConditions = @{
        Scope = @{
            "@odata.type" = "#microsoft.graph.identityGovernance.ruleBasedSubjectSet"
            Rule = "(user.userType -eq 'AgenticUser') and (user.extension_SponsorDepartureDate -ne null) and (user.extension_NewSponsorId -eq null)"
        }
        Trigger = @{
            "@odata.type" = "#microsoft.graph.identityGovernance.timeBasedAttributeTrigger"
            TimeBasedAttribute = "extension_SponsorDepartureDate"
            OffsetInDays = 14
        }
    }
    Tasks = @(
        @{
            DisplayName = "Disable agent account"
            TaskDefinitionId = "1dfdfcc7-52fa-4c2e-bf3a-e3919cc12950"  # Disable account
        },
        @{
            DisplayName = "Move to Quarantined collection"
            TaskDefinitionId = "4262b724-8dba-4fad-afc3-43fcbb497a0e"
            Arguments = @(
                @{
                    Name = "extensionId"
                    Value = "{{moveToQuarantineExtensionId}}"
                }
            )
        },
        @{
            DisplayName = "Notify compliance team"
            TaskDefinitionId = "aab41899-9972-422a-9a53-f4bb8b36b8ae"
            Arguments = @(
                @{ Name = "emailSubject"; Value = "Agent Suspended: No Sponsor - {{displayName}}" }
                @{ Name = "emailBody"; Value = "Agent {{displayName}} (ID: {{agentId}}) has been suspended due to no sponsor assignment after 14-day grace period." }
                @{ Name = "emailRecipients"; Value = "sg-compliance-officers,sg-ai-governance" }
            )
        },
        @{
            DisplayName = "Create audit record"
            TaskDefinitionId = "4262b724-8dba-4fad-afc3-43fcbb497a0e"
            Arguments = @(
                @{
                    Name = "extensionId"
                    Value = "{{createAuditRecordExtensionId}}"
                }
            )
        }
    )
}
```

---

## Step 4: Configure Zone 3 Immediate Suspension

For Zone 3 agents, sponsor departure triggers immediate suspension:

```powershell
# Zone 3 Immediate Suspension
$zone3ImmediateSuspend = @{
    DisplayName = "FSI-Z3-Immediate-Sponsor-Departure"
    Description = "Immediately suspend Zone 3 agents when sponsor leaves"
    IsEnabled = $true
    Category = "leaver"
    ExecutionConditions = @{
        Scope = @{
            "@odata.type" = "#microsoft.graph.identityGovernance.ruleBasedSubjectSet"
            Rule = "(user.userType -eq 'AgenticUser') and (user.extension_GovernanceZone -eq 'Zone3')"
        }
        Trigger = @{
            "@odata.type" = "#microsoft.graph.identityGovernance.attributeChangeTrigger"
            TriggerAttribute = "extension_SponsorId"
            ChangeType = "remove"
        }
    }
    Tasks = @(
        @{
            DisplayName = "Disable agent immediately"
            TaskDefinitionId = "1dfdfcc7-52fa-4c2e-bf3a-e3919cc12950"
        },
        @{
            DisplayName = "Move to Quarantined collection"
            TaskDefinitionId = "4262b724-8dba-4fad-afc3-43fcbb497a0e"
        },
        @{
            DisplayName = "Alert security operations"
            TaskDefinitionId = "aab41899-9972-422a-9a53-f4bb8b36b8ae"
            Arguments = @(
                @{ Name = "emailSubject"; Value = "CRITICAL: Zone 3 Agent Suspended - Sponsor Departed" }
                @{ Name = "emailRecipients"; Value = "sg-security-ops,sg-compliance-officers,sg-ai-governance" }
            )
        }
    )
}
```

---

## Step 5: Evidence Collection and Audit Trail

### Attestation Records

Each attestation cycle should generate:

| Evidence Type | Storage Location | Retention |
|---------------|------------------|-----------|
| Attestation request | Lifecycle Workflows logs | 7 years |
| Approval decision | Lifecycle Workflows logs | 7 years |
| Activity summary | SharePoint (sponsor access) | 7 years |
| Compliance sign-off (Z3) | SharePoint + Dataverse | 10 years |

### Query Attestation History

```kql
// Sponsor attestation audit trail
AuditLogs
| where TimeGenerated > ago(90d)
| where Category == "LifecycleWorkflows"
| where OperationName has "FSI-Z2-Quarterly" or OperationName has "FSI-Z3-Monthly"
| extend
    agentId = tostring(TargetResources[0].id),
    sponsorId = tostring(InitiatedBy.user.id),
    decision = tostring(Result)
| project
    TimeGenerated,
    WorkflowName = OperationName,
    agentId,
    sponsorId,
    decision,
    CorrelationId
| order by TimeGenerated desc
```

### PowerShell: Export Attestation Report

```powershell
# Generate attestation compliance report
function Get-AttestationComplianceReport {
    param(
        [int]$DaysBack = 90
    )

    $startDate = (Get-Date).AddDays(-$DaysBack)

    # Get all Agentic Users
    $agents = Get-MgUser -Filter "userType eq 'AgenticUser'" -All

    $report = foreach ($agent in $agents) {
        # Get extension attributes
        $extensions = Get-MgUserExtension -UserId $agent.Id

        # Get attestation history from audit logs
        $attestations = Get-MgAuditLogDirectoryAudit -Filter "targetResources/any(t:t/id eq '$($agent.Id)') and category eq 'LifecycleWorkflows'" -Top 10

        [PSCustomObject]@{
            AgentId = $agent.Id
            AgentName = $agent.DisplayName
            Zone = $extensions.extension_GovernanceZone
            SponsorId = $extensions.extension_SponsorId
            LastAttestation = ($attestations | Sort-Object ActivityDateTime -Descending | Select-Object -First 1).ActivityDateTime
            AttestationCount = $attestations.Count
            Status = if ($extensions.extension_SponsorId) { "Active" } else { "NoSponsor" }
        }
    }

    # Flag overdue attestations
    $report | ForEach-Object {
        $requiredFrequency = switch ($_.Zone) {
            "Zone2" { 90 }
            "Zone3" { 30 }
            default { 180 }
        }

        $daysSinceAttestation = if ($_.LastAttestation) {
            ((Get-Date) - $_.LastAttestation).Days
        } else { 999 }

        $_ | Add-Member -NotePropertyName "DaysSinceAttestation" -NotePropertyValue $daysSinceAttestation
        $_ | Add-Member -NotePropertyName "RequiredFrequency" -NotePropertyValue $requiredFrequency
        $_ | Add-Member -NotePropertyName "Overdue" -NotePropertyValue ($daysSinceAttestation -gt $requiredFrequency)
    }

    return $report
}

# Generate and export report
$report = Get-AttestationComplianceReport -DaysBack 90
$report | Export-Csv -Path "SponsorAttestationReport-$(Get-Date -Format 'yyyy-MM-dd').csv" -NoTypeInformation

# Alert on overdue attestations
$overdue = $report | Where-Object { $_.Overdue -eq $true }
if ($overdue.Count -gt 0) {
    Write-Warning "Found $($overdue.Count) agents with overdue attestations"
    $overdue | Format-Table AgentName, Zone, DaysSinceAttestation, RequiredFrequency
}
```

---

## Step 6: Integration with Control 3.6 (Orphan Detection)

### Link Sponsorship to Orphan Detection

When an agent loses its sponsor, it should appear in orphan detection scans:

```powershell
# Enhanced orphan detection including sponsorship status
function Get-OrphanedAndUnsponsoredAgents {
    $agents = Get-MgUser -Filter "userType eq 'AgenticUser'" -All -ExpandProperty Extensions

    $results = foreach ($agent in $agents) {
        $extensions = $agent.Extensions | Where-Object { $_.Id -like "*extension*" }

        [PSCustomObject]@{
            AgentId = $agent.Id
            AgentName = $agent.DisplayName
            Zone = $extensions.extension_GovernanceZone
            SponsorId = $extensions.extension_SponsorId
            SponsorStatus = $null
            Category = $null
            RiskLevel = $null
        }
    }

    # Check sponsor status for each agent
    foreach ($result in $results) {
        if ([string]::IsNullOrEmpty($result.SponsorId)) {
            $result.SponsorStatus = "NoSponsor"
            $result.Category = "Orphaned"
            $result.RiskLevel = switch ($result.Zone) {
                "Zone3" { "Critical" }
                "Zone2" { "High" }
                default { "Medium" }
            }
        } else {
            try {
                $sponsor = Get-MgUser -UserId $result.SponsorId -ErrorAction Stop
                if (-not $sponsor.AccountEnabled) {
                    $result.SponsorStatus = "SponsorDisabled"
                    $result.Category = "OrphanedPending"
                    $result.RiskLevel = "High"
                } else {
                    $result.SponsorStatus = "Active"
                    $result.Category = "Healthy"
                    $result.RiskLevel = "Low"
                }
            } catch {
                $result.SponsorStatus = "SponsorNotFound"
                $result.Category = "Orphaned"
                $result.RiskLevel = switch ($result.Zone) {
                    "Zone3" { "Critical" }
                    "Zone2" { "High" }
                    default { "Medium" }
                }
            }
        }
    }

    return $results
}
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Workflow not triggering | Execution conditions too restrictive | Verify attribute values match filter |
| Approval notifications not received | Email configuration issue | Check notification settings |
| Sponsor not found | Sponsor attribute not populated | Verify sponsor assignment in Agent ID |
| Extension tasks failing | Custom extension not deployed | Deploy Logic App/Azure Function |

### Verification Queries

```powershell
# Verify workflow is enabled
Get-MgIdentityGovernanceLifecycleWorkflow | Where-Object { $_.DisplayName -like "FSI-*" } | Select-Object DisplayName, IsEnabled

# Check recent workflow executions
Get-MgIdentityGovernanceLifecycleWorkflowRun -WorkflowId $workflowId -Top 10 | Select-Object Id, Status, CompletedDateTime

# Verify agent has sponsor attribute
Get-MgUser -UserId $agentId -ExpandProperty Extensions | Select-Object -ExpandProperty Extensions
```

---

## Related Resources

- [Control 1.2 - Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)
- [Control 3.6 - Orphaned Agent Detection](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- [Agent Identity Architecture](../../../framework/agent-identity-architecture.md)
- [Microsoft Learn: Lifecycle Workflows](https://learn.microsoft.com/en-us/entra/id-governance/what-are-lifecycle-workflows)

---

*Updated: January 2026 | Version: v1.2.6*
