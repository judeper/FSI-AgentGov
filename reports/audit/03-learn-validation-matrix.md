# Microsoft Learn Validation Matrix

**Method:** Technical claims extracted from control docs, framework docs, reference docs, and solution READMEs/scripts. Each claim verified via web search against Microsoft Learn. Read-based review (no live API testing).

## Summary

| Status | Count | Description |
|--------|-------|-------------|
| Contradicted | 22 | Claim conflicts with current Microsoft Learn documentation |
| Not Found | 5 | Claim references cmdlets/features not documented in Learn |
| Partially Verified | 4 | Claim partially correct but needs updating |
| **Total flagged** | **31** | |

---

## Contradicted Claims

### CRITICAL — Runtime/Deployment Impact

| # | Repo | File | Claim | Correct Per Learn | Learn URL | Notes |
|---|------|------|-------|-------------------|-----------|-------|
| 1 | Solutions | Enable-AuditLogging.ps1 | `#Requires -Version 7.2` with `Microsoft.PowerApps.Administration.PowerShell` | PowerApps Admin module requires Windows PowerShell 5.1, NOT PS 7+ | [PowerApps PowerShell](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell) | **CRITICAL** — scripts cannot run |
| 2 | Solutions | Enable-AuditLogging.ps1 | `PUT` for EntityDefinitions metadata update | Must use `PATCH` not `PUT` for Dataverse metadata updates | [Dataverse Web API](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-update-entity-definitions-using-web-api) | May wipe metadata |
| 3 | Solutions | Enable-AuditLogging.ps1 | `RecordType` values `PowerAppsPlan`, `PowerAppsResource` | Only `PowerAppsApp` is documented; others are NOT valid | [Search-UnifiedAuditLog](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog) | False negatives |

### HIGH — Feature/Behavior Inaccuracy

| # | Repo | File | Claim | Correct Per Learn | Learn URL | Notes |
|---|------|------|-------|-------------------|-----------|-------|
| 4 | Docs | 2.12-agent-identity-and-lifecycle.md | "Entra Agent ID and CA for agents are GA" | Still in Preview as of early 2026 | [Entra CA Agent ID](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id) | FSI customers may deploy based on false GA status |
| 5 | Docs | 2.12-agent-identity-and-lifecycle.md | Entra Lifecycle Workflows auto-reassign sponsorship | Default workflows send notifications only; auto-reassign requires custom extensions | [Agent Sponsor Tasks](https://learn.microsoft.com/en-us/entra/id-governance/agent-sponsor-tasks) | Overstates capability |
| 6 | Docs | 2.23-copilot-actions-and-connectors.md | Portal: "Settings > Org settings > Copilot > AI Disclaimer" | Actual: Copilot > Settings > Copilot actions > Copilot AI disclaimer | [AI Disclaimers](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-ai-disclaimers) | Wrong portal path |
| 7 | Docs | 3.11-centralized-agent-inventory-enforcement.md | "AB-900: Microsoft AI and Automation Fundamentals" | No AB-900 certification exists; link redirects to PL-900 | [PL-900](https://learn.microsoft.com/en-us/credentials/certifications/power-platform-fundamentals/) | Fabricated certification code |
| 8 | Docs | 3.8-copilot-hub-and-governance-dashboard.md | CopilotForM365AdminExclude excludes from M365 Copilot | Only excludes from Copilot in admin centers, NOT end-user M365 Copilot | [Copilot Admin](https://learn.microsoft.com/en-us/copilot/microsoft-365/copilot-for-microsoft-365-admin) | Scope overstated |
| 9 | Docs | 4.6-knowledge-source-security.md | "Sync Frequency: 4-6 hours" for knowledge sources | 4-6h applies to Salesforce/ServiceNow only; SharePoint requires manual sync | [File Sync Kit](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/kit-file-synchronization) | Admins may expect auto-sync |
| 10 | Docs | license-requirements.md | Copilot Studio Dataverse default 5 GB | Increased to 15 GB since December 2025 | [Capacity Storage](https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage) | Stale figure |
| 11 | Docs | solutions-architecture-guide.md | Search-UnifiedAuditLog "50,000 records per query" | Per-query limit is 5,000 (`-ResultSize`); 50,000 is per-session via pagination | [Search-UAL](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog) | Misleading |
| 12 | Docs | 1.15-customer-key.md | Specific "M365 Copilot interactions" DEP location | Copilot data in Exchange mailboxes covered by Exchange DEP; Copilot Studio CMK is separate | [Customer Key Overview](https://learn.microsoft.com/en-us/purview/customer-key-overview) | Reword scope |
| 13 | Docs | 1.17-global-secure-access.md | "Microsoft Entra GSA (formerly Internet Access)" | GSA is umbrella for Internet Access + Private Access; Internet Access is a component | [GSA Overview](https://learn.microsoft.com/en-us/entra/global-secure-access/overview-what-is-global-secure-access) | Incorrect lineage |
| 14 | Docs | 2.20-ai-risk-assessment.md | MITRE ATLAS "15 tactics, 66 techniques" | ATLAS has ~12 core tactics and 100+ techniques | [ATLAS](https://atlas.mitre.org/) | Update counts |
| 15 | Solutions | elm | PrivilegeDepth values 1,2,4,8 | Correct enum: 0,1,2,3 | [PrivilegeDepth](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/reference/privilegedepth) | Uses bitmask not enum |
| 16 | Solutions | elm | Copilot Studio "may be included in M365 E3/E5" | Requires separate licensing | [CS Licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing) | Misleading |
| 17 | Solutions | mcm | Power Automate standard license sufficient | Dataverse+HTTP connectors require Premium | [Premium Connectors](https://learn.microsoft.com/en-us/connectors/connector-reference/connector-reference-premium-connectors) | Licensing understatement |
| 18 | Solutions | mcm | Graph severity includes "critical" | serviceUpdateMessage: normal, high, unknownFutureValue only | [Service Update](https://learn.microsoft.com/en-us/graph/api/resources/serviceupdatemessage) | critical only in serviceHealthIssue |
| 19 | Solutions | sdm | Send-MailMessage in PS 7.0+ | Deprecated in PS7; use Send-MgUserMail | [Send-MailMessage](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/send-mailmessage) | Obsolete warning |
| 20 | Solutions | dashboard | MSAL scope admin.services.crm.dynamics.com | Standard: env-specific {env}.crm.dynamics.com | [Dataverse Auth](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/authenticate-oauth) | Non-standard |
| 21 | Solutions | dashboard | References 62 controls | Framework has 71 controls | — | Stale data model |
| 22 | Solutions | decr | README shows deprecated x-api-key pattern | Script migrated to Entra auth | — | README misleading |

## Not Found in Learn

| # | Repo | File | Claim | Notes |
|---|------|------|-------|-------|
| 1 | Docs | 1.2-agent-store.md | `Get-M365AgentStoreSettings` and `Set-M365AgentStoreVisibility` | Preview placeholders; control notes preview status |
| 2 | Docs | 1.25-mime-type.md | `FsiMimeControl` module and `Set-FsiMimePolicy` | Framework-custom modules, not MS-provided |
| 3 | Docs | 2.2-naming-standards.md | "Computer-Using Agents (CUA) must be DISABLED" | Not documented as configurable rule in Learn |
| 4 | Docs | 3.6-agent-inventory.md | `Get-MgUser -Filter "userType eq AgenticUser"` | `AgenticUser` not a standard Entra userType (only Member, Guest) |
| 5 | Solutions | acv | `Compliance.ManageAsApp` permission | Not documented as valid API permission |

## Partially Verified

| # | Repo | File | Claim | Status | Learn URL |
|---|------|------|-------|--------|-----------|
| 1 | Docs | sam-licensing.md | SAM "11 of 12 features" included with Copilot | MS now lists 13+ features; count stale | [SAM Licensing](https://learn.microsoft.com/en-us/sharepoint/sharepoint-advanced-management-licensing) |
| 2 | Solutions | finra | M365 E5 Compliance product name | Renamed to Microsoft Purview Suite Sept 2025 | [Licensing Guide](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-365-security-compliance-licensing-guidance) |
| 3 | Solutions | fus | Get-AzAccessToken .Token as plain text | Returns SecureString in Az.Accounts 5.0+; breaking change | [Get-AzAccessToken](https://learn.microsoft.com/en-us/powershell/module/az.accounts/get-azaccesstoken) |
| 4 | Solutions | aam | `Get-AdminPowerAppEnvironmentGroup` cmdlet | No such cmdlet exists; use PAC CLI | [Environment Groups](https://learn.microsoft.com/en-us/power-platform/admin/environment-groups) |
