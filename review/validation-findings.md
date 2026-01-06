# FSI Agent Governance Framework - Validation Findings
## Comprehensive Review Against Microsoft Learn Documentation

---

## EXECUTIVE SUMMARY

This validation review compares all statements, recommendations, and governance steps in the FSI Agent Governance Framework (v1.0 Beta, December 2025) against the latest Microsoft Learn documentation as of January 2026. The review identifies discrepancies, outdated information, missing controls, and provides corrective guidance with authoritative source citations.

**Key Findings:**
- 17 corrections/clarifications required across multiple controls
- 12 missing governance controls identified
- 3 controls require terminology updates
- Environment governance section requires significant expansion

---

## SECTION 1: OVERVIEW & FRAMEWORK STRUCTURE

### Finding 1.1: Environment Routing Description Incomplete
**Location**: Overview document, Control 2.15
**Issue**: Framework does not mention multi-rule environment routing capability
**Correction Required**: 
- Add description of multi-rule environment routing (introduced 2024, GA 2025)
- Clarify that routing can target different environment groups based on security group membership
- Note that if no routing rule matches a user, the user is routed to the DEFAULT ENVIRONMENT

**Microsoft Learn Source**: 
https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing
**Relevant Quote**: "Multi-rule environment routing is an advanced governance feature in Power Platform that allows tenant administrators to define multiple routing rules to control how makers are directed to development environments across various portals"

---

## SECTION 2: PILLAR 1 - SECURITY CONTROLS

### Finding 2.1: Control 1.1 - Restrict Agent Publishing by Authorization
**Issue**: Framework does not specify complete DLP mechanism for blocking publishing
**Missing Details**:
- Four specific channel connectors that must be blocked to disable publishing:
  1. Direct Line channels in Copilot Studio
  2. Teams and M365 channels in Copilot Studio
  3. Omnichannel in Copilot Studio
  4. Facebook channel in Copilot Studio
- When ALL four channels are blocked, the Publish button becomes disabled

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/microsoft-copilot-studio/dlp-example-6

**Addition Required**: Add explicit procedure:
```
To prevent agent publishing in an environment:
1. Navigate to Power Platform Admin Center > Policies > Data policies
2. Create or edit DLP policy for target environment
3. Search for and block all four Copilot Studio channel connectors:
   - "Direct Line channels in Copilot Studio"
   - "Microsoft Teams + M365 Channel in Copilot Studio"
   - "Facebook channel in Copilot Studio"
   - "Omnichannel in Copilot Studio"
4. Publish policy
5. Effect: Publish button will be disabled for all agents in the environment
```

### Finding 2.2: Control 1.6 - Microsoft Purview DSPM for AI
**Issue**: Framework does not reflect latest DSPM for AI capabilities
**Status**: Major update rolling out Public Preview Dec 2025 - Apr 2026, GA May 2026

**Missing Capabilities**:
- AI Observability for agents created in Microsoft 365 Copilot, Copilot Studio, and Azure AI Foundry
- Unified inventory of all AI agents with insider risk scoring
- Data Security Posture Agent (uses LLM to analyze sensitive files)
- Enhanced data risk assessments with item-level visibility
- Integration with external platforms (Salesforce, Snowflake)

**Microsoft Learn Source**:
https://techcommunity.microsoft.com/blog/microsoft-security-blog/beyond-visibility-the-new-microsoft-purview-data-security-posture-management-dspm/4324886

**Update Required**: Control 1.6 should note:
"Note: Microsoft Purview DSPM for AI is undergoing significant enhancement (Public Preview Dec 2025-Apr 2026, GA May 2026). The new experience includes AI agent observability, unified agent inventory with risk scoring, and Security Copilot integration. Organizations should plan for these enhanced capabilities when implementing Control 1.6."

### Finding 2.3: Control 1.7 - Comprehensive Audit Logging
**Issue**: Framework should reference automatic security scan feature
**Missing Control**: Automatic security scan (GA Nov 2024)

**Capability**: Copilot Studio automatically scans agents before publishing and warns makers when:
- Authentication mode is set to "No authentication"
- Connector authentication is changed from "User authentication" to "Author authentication"
- Security warnings appear on Channels page with detailed violation reports

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-scan

**Addition Required**: Add to Control 1.7 or create separate control for "Automatic Security Scanning"

### Finding 2.4: Control 1.8 - Runtime Protection
**Issue**: Missing reference to external threat detection system integration
**Missing Capability**: Organizations can connect Copilot Studio agents to external runtime threat detection systems via webhooks
- Response time requirement: < 1000ms
- System can allow/block tool invocations in real-time
- Supports authorization via app ID allowlist or RBAC

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/microsoft-copilot-studio/external-security-webhooks-interface-developers

---

## SECTION 3: PILLAR 2 - MANAGEMENT CONTROLS

### Finding 3.1: Control 2.1 - Managed Environments
**Issue**: Framework lists only 6-7 Managed Environment features; official documentation lists 24
**Missing Features**:
1. IP Firewall
2. IP cookie binding
3. Customer Managed Key (CMK)
4. Lockbox
5. Extended backup
6. Data policies for desktop flow
7. Export data to Azure Application Insights
8. Administer the catalog
9. Virtual Network support
10. Conditional access on individual apps
11. Control which apps are allowed in environment
12. Configure auditing for environment
13. Create and manage masking rules
14. Create app description with Copilot

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview

**Correction Required**: Expand Control 2.1 to reference complete Managed Environments feature set

### Finding 3.2: Control 2.2 - Environment Groups
**Issue**: Framework does not list all available environment group rules
**Current Status**: 19 rules available (as of Aug 2025)

**Complete Rule List**:
1. Accessing transcripts from conversations in Copilot Studio agents
2. Advanced connector policy (preview)
3. AI prompts
4. AI-generated descriptions (preview)
5. AI-powered Copilot features
6. Back-up retention
7. Default deployment pipeline (preview)
8. Generative AI settings
9. Maker welcome content
10. Power Apps component framework for canvas apps
11. Release channel
12. Sharing agents with Editor permissions
13. Sharing agents with Viewer permissions
14. Sharing controls for canvas apps
15. Sharing controls for solution-aware cloud flows
16. Sharing data between Copilot Studio and Viva Insights
17. Solution checker enforcement
18. Unmanaged customizations
19. Usage insights

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules

**Correction Required**: Update Control 2.2 with complete list of available rules

### Finding 3.3: Control 2.15 - Environment Routing
**Critical Missing Detail**: Default environment fallback behavior
**Issue**: Framework does not explain what happens when environment routing is configured but a routing rule does NOT match

**Correction Required**: Add explicit statement:
"When environment routing is enabled but no routing rule matches a user, the user is routed to the DEFAULT ENVIRONMENT. Therefore, environment routing alone is insufficient to prevent access to the default environment—it must be combined with appropriate routing rules that cover all user populations or supplemented with default environment restrictions."

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing
**Quote**: "When a maker accesses a portal, the system evaluates the rules in order and applies the first matching rule. If a matching rule is found, the maker is routed to an existing or newly provisioned developer environment. If no rule matches, or if environment routing isn't turned on, the maker is routed to the default environment."

---

## SECTION 4: PILLAR 3 - REPORTING CONTROLS

### Finding 4.1: Control 3.7 - PPAC Security Posture Assessment
**Issue**: This appears to reference Power Platform Security Overview feature (not "PPAC Security Posture Assessment")
**Correct Terminology**: "Power Platform Security" or "Security Overview in Power Platform Admin Center"

**Capabilities**:
- Assess security score (Low/Medium/High scale)
- View and act on security recommendations
- Manage proactive security policies
- Centralized security management for Power Platform and Dynamics 365 workloads

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/power-platform/admin/security/security-overview

**Correction Required**: 
- Update Control 3.7 name to "Power Platform Security Overview"
- Add reference to security score assessment
- Include proactive policy management capabilities

### Finding 4.2: Control 3.8 - Copilot Command Center
**Issue**: No official "Copilot Command Center" exists in Microsoft documentation
**Possible References**:
1. **Tenant-level analytics** (Power Platform Admin Center)
   - View analytics across all environments
   - Requires Power Platform admin role
   - Free feature with 24-48 hour data lag
   - Source: https://learn.microsoft.com/en-us/power-platform/admin/tenant-level-analytics

2. **Microsoft Copilot Dashboard** (for M365 Copilot usage)
   - Tracks Copilot license usage and adoption
   - Requires 50+ Copilot licenses or 50+ Viva Insights licenses for full features
   - Tenant-level and group-level metrics
   - Source: https://learn.microsoft.com/en-us/viva/insights/org-team-insights/copilot-dashboard

3. **Copilot in Microsoft 365 Admin Centers**
   - AI-powered admin assistant in M365 admin center
   - Natural language queries for admin tasks
   - Source: https://learn.microsoft.com/en-us/copilot/microsoft-365/copilot-for-microsoft-365-admin

**Correction Required**:
- Clarify what "Copilot Command Center" refers to
- If it refers to tenant-level analytics, update name and reference
- If it refers to M365 Copilot Dashboard, note scope limitation (M365 Copilot only, not Copilot Studio agents)
- If proprietary/unofficial naming, provide clear definition

### Finding 4.3: Control 3.9 - Microsoft Sentinel Integration
**Issue**: Framework should reference specific solution name
**Correct Name**: "Microsoft Sentinel Solution for Microsoft Business Apps"

**Key Implementation Details**:
- Requires Log Analytics workspace enabled for Sentinel
- Three data connectors: Microsoft Dataverse, Power Platform Admin Activity, Microsoft Power Automate
- Requires Microsoft Purview audit logging enabled
- 60-minute data ingestion delay for Power Platform activity logs
- Supports KQL queries for log analysis

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/azure/sentinel/business-applications/deploy-power-platform-solution

**Addition Required**: Include deployment prerequisites and data connector list

---

## SECTION 5: MISSING GOVERNANCE CONTROLS

### Missing Control 5.1: Restrict Environment Creation
**Control ID Suggestion**: 2.16 - Control Environment Creation and Management
**Why It's Missing**: Critical for preventing environment sprawl and ensuring governed environment usage

**Implementation**:
Power Platform Admin Center > Settings (or Manage) > Tenant settings
Configure for each environment type:
- **Production environment assignments**: Only specific admins
- **Trial environment assignments**: Only specific admins  
- **Developer environment assignments**: Only specific admins

**PowerShell Alternative**:
```powershell
$settings = @{ DisableEnvironmentCreationByNonAdminUsers = $true }
Set-TenantSettings $settings
```

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/power-platform/admin/control-environment-creation

**FSI Relevance**: Prevents unauthorized environment creation that could bypass governance controls

---

### Missing Control 5.2: Disable Agent Creation in Default Environment
**Control ID Suggestion**: 1.20 or 2.17 - Prevent Agent Creation in Default Environment
**Why It's Missing**: Default environment has unique security profile; all licensed users have Environment Maker role

**Implementation Options**:

**Option A - Security Role Modification**:
1. Navigate to Default Environment > Settings > Security > Users
2. Create custom security role (copy Environment Maker role)
3. Remove "Canvas App: Create" privilege
4. Remove Environment Maker role from users
5. Assign custom role with restricted privileges

**Option B - DLP Policy Blocking**:
1. Create DLP policy scoped to Default environment only
2. Block all Copilot Studio connectors (channels, knowledge sources, authentication)
3. Effect: Users cannot publish agents, rendering agent creation impractical

**Option C - Environment Routing** (preferred):
1. Enable environment routing for all users
2. Route all users to dedicated personal developer environments (assigned to governed environment group)
3. Fallback: Users still access default if routing fails - combine with Option A or B

**Sources**:
- https://gokan.studio/2025/11/12/blocking-the-default-environment-in-power-platform-yes-its-possible/
- https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing
- https://www.youtube.com/watch?v=usa40ensr5w (Plugin approach for Dataverse-level blocking)

**FSI Relevance**: Default environment lacks environment-specific DLP, sharing limits, and other managed environment benefits

---

### Missing Control 5.3: Designate SharePoint Form Environment
**Control ID Suggestion**: 2.18 - SharePoint Custom Form Environment Assignment
**Why It's Missing**: SharePoint form customization automatically creates apps in default environment

**Implementation**:
```powershell
Set-AdminPowerAppSharepointFormEnvironment -EnvironmentName '<EnvironmentName>'
```

**Effects**:
- All new SharePoint custom forms create canvas apps in designated environment (not default)
- Existing forms remain in current environment (not migrated)
- If designated environment is deleted, reverts to default environment
- Does NOT affect Power Automate flows created from SharePoint (always use default)

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/power-platform/guidance/adoption/manage-default-environment

**FSI Relevance**: Prevents cluttering default environment with SharePoint form apps

---

### Missing Control 5.4: DLP Policy Enforcement Activation for Copilot Studio
**Control ID Suggestion**: 1.21 - Enable Copilot Studio DLP Enforcement
**Why It's Missing**: Copilot Studio DLP enforcement is NOT enabled by default in existing tenants

**Critical Issue**: Even if DLP policies are configured, they are not enforced against Copilot Studio agents unless explicitly activated

**Activation Requirement**:
```powershell
Set-PowerVirtualAgentsDlpEnforcement -TenantId <tenant ID> -Mode Enabled
```

**Modes**:
- **Enabled**: Full enforcement (blocks violations)
- **Soft**: Warns makers but allows violations (transition mode)
- **Disabled**: No enforcement (legacy default)

**Additional Commands**:
- Set learn-more URL for makers
- Set admin contact email
- Set effective date for new agents only
- Create DLP exemptions for specific agents

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention

**LinkedIn Source**: https://www.linkedin.com/posts/lisa-crosbie_dlp-policy-enforcement-for-copilot-studio-activity-7302406477346938890-o3Nz

**FSI Relevance**: WITHOUT activation, all Copilot Studio DLP configurations are non-enforced (critical gap)

**Rollout Context**: Microsoft enabled soft mode Jan-Feb 2025, with hard enforcement following. Existing tenants may not have enforcement enabled.

---

### Missing Control 5.5: Agent Sharing Controls
**Control ID Suggestion**: 1.22 - Configure Agent Sharing Permissions
**Why It's Missing**: Sharing controls are environment-specific but not covered in framework

**Capabilities**:
- Restrict who can grant Editor permissions (individual users only, cannot use security groups)
- Restrict who can grant Viewer permissions (individuals or security groups)
- Limit total number of viewers per agent
- Enforce "Only share with individuals (no security groups)"

**Configuration**: Power Platform Admin Center > Managed Environment > Sharing controls

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-sharing-controls-limits

**FSI Relevance**: Prevents over-sharing of agents containing sensitive business logic or data access

---

### Missing Control 5.6: Knowledge Source Governance
**Control ID Suggestion**: 1.23 - Knowledge Source Security and Classification
**Why It's Missing**: Knowledge sources determine what data agents can access—critical security boundary

**Governance Capabilities**:
- DLP policies can block specific knowledge source types:
  - "Knowledge source with SharePoint and OneDrive in Copilot Studio"
  - "Knowledge source with documents in Copilot Studio"
- Endpoint filtering in DLP can allowlist/blocklist specific SharePoint sites
- Official source designation (marks knowledge as verified/trusted)
- Knowledge source descriptions (used by agent to filter relevant sources when >25 sources)
- Generative orchestration limits: 25 knowledge source search limit

**Microsoft Learn Sources**:
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
- https://www.lewisdoes.dev/blog/data-loss-prevention-for-copilot-studio/
- https://www.microsoft.com/en-us/power-platform/blog/2025/03/27/knowledge-in-microsoft-copilot-studio/

**FSI Relevance**: Knowledge sources represent the largest attack surface for data exfiltration

---

### Missing Control 5.7: Maker Welcome Message
**Control ID Suggestion**: 2.19 - Maker Onboarding and Policy Communication
**Why It's Missing**: First touchpoint for communicating governance expectations

**Capability**: Display custom message when makers first access environment
- Communicate privacy requirements
- Link to governance policies
- Set expectations for compliant development
- Can be configured per environment or via environment group rules

**Configuration**: Managed Environment settings or Environment Group rules

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance

**FSI Relevance**: Regulatory expectation for documented communication of policies to users

---

### Missing Control 5.8: Usage Insights and Monitoring
**Control ID Suggestion**: 3.10 - Environment-Level Usage Insights
**Why It's Missing**: Managed Environments provide weekly usage insights—not covered in detail

**Capabilities**:
- Weekly digest of environment activity
- Identifies unused apps/flows
- Tracks sharing patterns
- Available in Managed Environments

**Configuration**: Enable via Managed Environment settings or Environment Group rules

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview

**FSI Relevance**: Required for demonstrating supervision (FINRA 3110)

---

### Missing Control 5.9: IP Firewall and IP Cookie Binding
**Control ID Suggestion**: 1.24 - Network-Level Access Controls
**Why It's Missing**: Premium Managed Environment feature for network-layer security

**Capabilities**:
- **IP Firewall**: Restrict Dataverse access to specific IP ranges
- **IP Cookie Binding**: Prevent session hijacking by binding sessions to originating IP
- Available only in Managed Environments

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview

**FSI Relevance**: Defense-in-depth; prevents access from unauthorized networks

---

### Missing Control 5.10: Virtual Network (VNet) Support
**Control ID Suggestion**: 1.25 - Private Network Integration
**Why It's Missing**: Allows Power Platform environments to connect via private endpoints

**Capability**: Isolate network traffic to private Azure Virtual Networks
- Enforces security policies at network boundary
- Supports hybrid connectivity (on-premises + cloud)
- Premium governance feature

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview

**FSI Relevance**: Required for zero-trust network architectures

---

### Missing Control 5.11: Application-Level Auditing
**Control ID Suggestion**: 3.11 - Environment-Specific Audit Configuration
**Why It's Missing**: Managed Environments allow per-environment audit log configuration

**Capability**: Configure auditing at environment level (beyond tenant-level Purview auditing)
- Customize audit retention
- Configure audit scope

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview

**FSI Relevance**: Aligns with record retention requirements (FINRA 4511, SEC 17a-4)

---

### Missing Control 5.12: Data Masking Rules
**Control ID Suggestion**: 1.26 - Field-Level Data Masking
**Why It's Missing**: Managed Environments support masking rules for sensitive fields

**Capability**: Create and manage masking rules to obfuscate sensitive data in Dataverse
- Protects PII in non-production environments
- Role-based unmasking

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview

**FSI Relevance**: GLBA Safeguards Rule (protects customer PII)

---

## SECTION 6: TERMINOLOGY AND NAMING CORRECTIONS

### Correction 6.1: "Agent Builder" vs "Agent builder"
**Issue**: Framework references "Agent Builder" as separate product
**Clarification**: "Agent builder" (lowercase) is a feature within Microsoft 365 Copilot for creating declarative agents
**Correct Usage**: 
- "Copilot Studio agents" (full platform)
- "Agent builder" (M365 Copilot feature for declarative agents)

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/agent-builder-share-manage-agents

---

### Correction 6.2: Control 3.8 Naming
**See Finding 4.2** - "Copilot Command Center" is not an official Microsoft product name

---

### Correction 6.3: Control 3.7 Naming
**See Finding 4.1** - Should be "Power Platform Security Overview" not "PPAC Security Posture Assessment"

---

## SECTION 7: ADMINISTRATOR ROLE ASSIGNMENTS

### Finding 7.1: Missing Role - AI Administrator (Entra ID)
**Issue**: Framework does not reference new AI Administrator role in Entra ID
**Role Capabilities**: 
- Manage Microsoft Copilot
- View-only permissions in Purview DSPM for AI
- Equivalent to Purview Data Security AI Viewer role

**Microsoft Learn Source**:
https://learn.microsoft.com/en-us/purview/whats-new

**Addition Required**: Update RACI matrix and administrator checklist to include AI Administrator role

---

## SECTION 8: REGULATORY ALIGNMENT UPDATES

### Finding 8.1: FINRA Notice 25-07 Reference
**Issue**: Framework references "FINRA 25-07" - this notice is dated 2025 but not yet issued as of January 2026
**Clarification Needed**: Confirm publication date and URL for FINRA Notice 25-07 on AI fairness

---

## SECTION 9: CONSOLIDATED RECOMMENDATIONS

### Priority 1 (Critical - Implement Immediately)

1. **Activate Copilot Studio DLP Enforcement** (Missing Control 5.4)
   - Without activation, all DLP policies are advisory-only
   - Use PowerShell to enable: `Set-PowerVirtualAgentsDlpEnforcement -TenantId <ID> -Mode Enabled`
   
2. **Add Environment Routing Fallback Documentation** (Finding 3.3)
   - Users route to DEFAULT environment if no rule matches
   - Environment routing alone does not prevent default environment access

3. **Clarify Control 3.8 - Copilot Command Center** (Finding 4.2)
   - No official product by this name exists
   - Recommend rename to "Tenant-Level Analytics" with proper reference

### Priority 2 (High - Add Within 30 Days)

4. **Add Missing Control: Restrict Environment Creation** (Missing Control 5.1)
   - Core governance control for environment strategy

5. **Add Missing Control: Disable Agent Creation in Default Environment** (Missing Control 5.2)
   - Critical for default environment hygiene

6. **Update Control 2.1 with Complete Managed Environment Features** (Finding 3.1)
   - Framework lists 6-7 features; official count is 24

7. **Update Control 1.1 with Complete Publishing Block Procedure** (Finding 2.1)
   - Specify all four channel connectors that must be blocked

8. **Add Missing Control: Knowledge Source Governance** (Missing Control 5.6)
   - Largest attack surface for data exfiltration

### Priority 3 (Medium - Add Within 60 Days)

9. **Update Control 1.6 for New Purview DSPM for AI** (Finding 2.2)
   - Major feature update rolling out Q1-Q2 2026

10. **Update Control 2.2 with Complete Environment Group Rules** (Finding 3.2)
    - List all 19 available rules

11. **Add Missing Control: DLP Policy Enforcement Activation** (Missing Control 5.4)
    - Prerequisite for all Copilot Studio DLP controls

12. **Rename Control 3.7 to "Power Platform Security Overview"** (Finding 4.1)

13. **Add Missing Control: Agent Sharing Controls** (Missing Control 5.5)

14. **Add Missing Control: SharePoint Form Environment** (Missing Control 5.3)

### Priority 4 (Low - Enhancement)

15. **Add Missing Control: Maker Welcome Message** (Missing Control 5.7)
16. **Add Missing Control: IP Firewall and IP Cookie Binding** (Missing Control 5.9)
17. **Add Missing Control: Virtual Network Support** (Missing Control 5.10)
18. **Add Missing Control: Data Masking Rules** (Missing Control 5.12)
19. **Add AI Administrator Role to RACI Matrix** (Finding 7.1)
20. **Reference Automatic Security Scan in Control 1.7** (Finding 2.3)
21. **Reference External Threat Detection in Control 1.8** (Finding 2.4)

---

## SECTION 10: IMPLEMENTATION CHECKLIST ADDITIONS

The Implementation Checklist should be expanded to include:

### Phase 0: Prerequisite Configuration (Before Phase 1)
- [ ] Activate Copilot Studio DLP enforcement (`Set-PowerVirtualAgentsDlpEnforcement`)
- [ ] Restrict environment creation to admins only
- [ ] Enable Managed Environments on Default environment
- [ ] Configure environment routing with comprehensive rules
- [ ] Implement default environment access restrictions

### Phase 1 Additions:
- [ ] Block agent publishing in Default environment via DLP
- [ ] Remove or restrict Environment Maker role in Default environment
- [ ] Designate SharePoint custom form environment
- [ ] Configure agent sharing limits in managed environments

### Phase 2 Additions:
- [ ] Implement knowledge source DLP policies with endpoint filtering
- [ ] Configure automatic security scan monitoring
- [ ] Set up maker welcome messages in governed environments

### Phase 3 Additions:
- [ ] Enable IP firewall for production environments (if licensed)
- [ ] Configure Virtual Network support (if licensed)
- [ ] Implement data masking rules for non-production environments

---

## APPENDIX A: COMPLETE SOURCE REFERENCE TABLE

| Control | Finding | Microsoft Learn URL | Last Updated |
|---------|---------|---------------------|--------------|
| 1.1 | 2.1 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/dlp-example-6 | 2025-07-04 |
| 1.6 | 2.2 | https://techcommunity.microsoft.com/blog/microsoft-security-blog/beyond-visibility-the-new-microsoft-purview-data-security-posture-management-dspm/4324886 | 2025-11-17 |
| 1.7 | 2.3 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-scan | 2024-11-19 |
| 1.8 | 2.4 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/external-security-webhooks-interface-developers | 2025-09-04 |
| 2.1 | 3.1 | https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview | 2025-08-19 |
| 2.2 | 3.2 | https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules | 2025-08-02 |
| 2.15 | 1.1, 3.3 | https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing | 2025-09-17 |
| 3.7 | 4.1 | https://learn.microsoft.com/en-us/power-platform/admin/security/security-overview | 2025-07-30 |
| 3.8 | 4.2 | https://learn.microsoft.com/en-us/power-platform/admin/tenant-level-analytics | 2025-09-18 |
| 3.9 | 4.3 | https://learn.microsoft.com/en-us/azure/sentinel/business-applications/deploy-power-platform-solution | 2025-06-17 |
| Missing 5.1 | 5.1 | https://learn.microsoft.com/en-us/power-platform/admin/control-environment-creation | 2025-09-18 |
| Missing 5.2 | 5.2 | https://learn.microsoft.com/en-us/power-platform/guidance/adoption/manage-default-environment | 2025-05-30 |
| Missing 5.3 | 5.3 | https://learn.microsoft.com/en-us/power-platform/guidance/adoption/manage-default-environment | 2025-05-30 |
| Missing 5.4 | 5.4 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention | 2025-09-17 |
| Missing 5.5 | 5.5 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-sharing-controls-limits | 2025-05-01 |
| Missing 5.6 | 5.6 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio | 2025-12-01 |
| Missing 5.7 | 5.7 | https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance | 2025-08-27 |
| Environment Groups | Multiple | https://learn.microsoft.com/en-us/power-platform/admin/environment-groups | 2025-07-28 |

---

## APPENDIX B: POWERSHELL QUICK REFERENCE

```powershell
# Activate Copilot Studio DLP Enforcement
Set-PowerVirtualAgentsDlpEnforcement -TenantId <tenant ID> -Mode Enabled

# Restrict Environment Creation
$settings = @{ DisableEnvironmentCreationByNonAdminUsers = $true }
Set-TenantSettings $settings

# Restrict Developer Environment Creation
$requestBody = [pscustomobject]@{
    powerPlatform = [pscustomobject]@{
        governance = [pscustomobject]@{
            disableDeveloperEnvironmentCreationByNonAdminUsers = $True
        }
    }
}
Set-TenantSettings -RequestBody $requestBody

# Enable Environment Routing
$tenantSettings = Get-TenantSettings
$tenantSettings.powerPlatform.governance.enableDefaultEnvironmentRouting = $True
Set-TenantSettings -RequestBody $tenantSettings

# Designate SharePoint Form Environment
Set-AdminPowerAppSharepointFormEnvironment -EnvironmentName '<EnvironmentName>'
```

---

## DOCUMENT CONTROL

**Validation Date**: January 6, 2026  
**Microsoft Learn Documentation Reference Date**: January 6, 2026  
**Framework Version Reviewed**: FSI Agent Governance Framework v1.0 Beta (December 2025)  
**Reviewer**: Microsoft Learn Documentation Validator  
**Next Review Date**: April 6, 2026 (Quarterly)

---

**END OF VALIDATION REPORT**