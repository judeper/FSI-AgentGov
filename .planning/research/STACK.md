# Stack Research: Microsoft Agent Governance (2025-2026 Updates)

**Project:** FSI-AgentGov v1.2.37
**Research Date:** February 2, 2026
**Research Mode:** Ecosystem - What's NEW or CHANGED
**Overall Confidence:** HIGH

## Summary

Microsoft has released significant governance, security, and platform enhancements for Copilot Studio and Power Platform in 2025-2026. Key findings:

- **Model Context Protocol (MCP) reached GA** at Build 2025, enabling 1,400+ system integrations
- **Microsoft Entra Agent ID** launched in preview (May 2025) with automatic identity assignment
- **Microsoft Agent 365** rolled out in Frontier program (November 2025) as centralized governance control plane
- **Defender AI-SPM expanded to GCP Vertex AI** (May 2025 preview) and added unified agent posture management
- **DLP for Copilot prompts reached Public Preview** (November 2025) with GA planned March/April 2026
- **Major API retirements approaching:** EWS (Oct 2026), SharePoint Add-Ins (Apr 2026), Azure Key Vault pre-2026 APIs (Feb 2027)
- **BYOK deprecated January 6, 2026** - must migrate to Customer-Managed Keys (CMK)

All findings verified against official Microsoft Learn documentation and release plans.

---

## New Capabilities (2025-2026)

### 1. Copilot Studio Platform Enhancements

| Feature | Status | Timeline | Impact | Confidence |
|---------|--------|----------|--------|------------|
| **GPT-5 Chat** | GA | Nov 24, 2025 | New model option for agents | HIGH |
| **GPT-4.1 default** | GA | Oct 27, 2025 | Replaced GPT-4o for new agents | HIGH |
| **Model Context Protocol (MCP)** | GA | Build 2025 | 1,400+ system integrations | HIGH |
| **Automated agent evaluation** | Preview | 2025 Wave 2 | Systematic testing at scale | HIGH |
| **Express mode optimization** | Preview | 2025 Wave 2 | Finish flows within 2 minutes | MEDIUM |
| **Python code interpreter** | Preview | 2025 Wave 2 | Excel/CSV/PDF file analysis | HIGH |
| **File groups for knowledge** | GA | 2025 Wave 2 | Organized local file uploads | HIGH |

**Sources:**
- [What's new in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new)
- [2025 Wave 2 Planned Features](https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/microsoft-copilot-studio/planned-features)
- [MCP GA Announcement](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/model-context-protocol-mcp-is-now-generally-available-in-microsoft-copilot-studio/)

### 2. Identity & Access Management

| Feature | Status | Timeline | Impact | Confidence |
|---------|--------|----------|--------|------------|
| **Microsoft Entra Agent ID** | Preview | May 2025+ | Automatic agent identity creation | HIGH |
| **Auto-assign agent identities** | Preview | 2025 Wave 2 | Copilot Studio integration | HIGH |
| **SSO for non-Entra ID** | Preview/GA | Feb-May 2026 | External identity providers | HIGH |
| **End-user credential triggers** | GA | Feb 2026 | Replace service accounts | HIGH |

**Key Details:**

**Entra Agent ID:**
- Announced at Ignite 2025, initially previewed May 2025
- When enabled in Power Platform admin center, Copilot Studio agents automatically receive agent identities
- Unified directory across Copilot Studio and Azure AI Foundry
- Part of Microsoft Agent 365 (Frontier program)
- Additional platforms (Security Copilot, M365 Copilot, third-party) coming throughout 2025-2026

**Sources:**
- [Microsoft Entra Agent ID Overview](https://learn.microsoft.com/en-us/entra/agent-id/identity-professional/microsoft-entra-agent-identities-for-ai-agents)
- [Automatically create agent identities](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-use-entra-agent-identities)
- [Ignite 2025 Announcements](https://learn.microsoft.com/en-us/entra/fundamentals/whats-new-ignite-2025)

### 3. Security & Threat Protection

| Feature | Status | Timeline | Impact | Confidence |
|---------|--------|----------|--------|------------|
| **Defender AI-SPM for GCP Vertex AI** | Preview | May 2025 | Multi-cloud posture management | HIGH |
| **Defender AI Agent Security** | Preview | Ignite 2025 | Unified agent inventory | HIGH |
| **Copilot Studio threat protection** | Preview/GA | Sep 2025 - Feb 2026 | Additional threat capabilities | HIGH |
| **IP firewall for Copilot Studio** | GA | Dec 2025 | Network-level protection | HIGH |
| **Sentinel MCP server** | Preview | 2025 | Natural language threat hunting | HIGH |

**Key Details:**

**Defender AI-SPM Expansion:**
- Extended beyond Azure and AWS to include Google Vertex AI (May 2025 preview)
- Coverage for Gemini, Gemma, Meta Llama, Mistral, and custom models
- AI Bill of Materials (AI BOM) discovery across code-to-runtime
- Attack path analysis with contextual security recommendations
- Included with Defender CSPM at no extra cost (preview pricing)

**Defender AI Agent Security (Preview at Ignite 2025):**
- Unified, risk-based inventory of AI agents across Microsoft Foundry and Copilot Studio
- Eliminates blind spots and reduces shadow agents
- Consolidates metadata, instructions, identities, and connected tools
- Requires: Defender CSPM for Azure Foundry agents, Defender for Cloud Apps license for Copilot Studio agents

**Sources:**
- [AI Security Posture Management](https://learn.microsoft.com/en-us/azure/defender-for-cloud/ai-security-posture)
- [Defender AI agent journey](https://techcommunity.microsoft.com/blog/microsoft-security-blog/start-secure-and-stay-secure-on-your-ai-agent-journey-with-microsoft-defender/4469430)
- [IDC MarketScape Leader announcement](https://www.microsoft.com/en-us/security/blog/2026/01/14/microsoft-named-a-leader-in-idc-marketscape-for-unified-ai-governance-platforms/)

### 4. Data Loss Prevention & Compliance

| Feature | Status | Timeline | Impact | Confidence |
|---------|--------|----------|--------|------------|
| **DLP for Copilot prompts** | Preview | Nov 2025 | Block sensitive data in prompts | HIGH |
| **DLP for Copilot prompts** | GA | Late Mar - Late Apr 2026 | Worldwide rollout | HIGH |
| **Sensitivity labels in Copilot Studio** | Preview/GA | Nov 2025 - Jun 2026 | MIP label visibility | HIGH |
| **Sensitivity labels in connectors** | Preview/GA | Nov 2025 - Jun 2026 | Connector-level protection | HIGH |
| **Column-level security masking** | GA | Oct 31, 2025 | Dataverse field masking | HIGH |

**Key Details:**

**DLP for Copilot Prompts (MC1181998):**
- **Public Preview:** Mid-November 2025 (completed late December 2025)
- **General Availability:** Late March 2026 (completion late April 2026)
- **Licensing:** Available to ALL tenants with M365 Copilot access (E1, E3, E5) regardless of license tier by December 2025
- **Scope:** Microsoft 365 Copilot, Copilot Chat, and pre-built agents
- **Capabilities:** Prevents Copilot from returning responses when prompts contain sensitive information types (default and custom SITs)
- **New Roles:** Entra AI Admin, Purview Data Security AI Admin

**Sources:**
- [MC1181998 Message Center](https://mc.merill.net/message/MC1181998)
- [DLP for Copilot prompts Learn documentation](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about)
- [Power Platform Wave 2 Security Features](https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/power-platform-governance-administration/planned-features)

### 5. Microsoft Agent 365 (New Control Plane)

| Feature | Status | Timeline | Impact | Confidence |
|---------|--------|----------|--------|------------|
| **Agent 365 control plane** | Frontier | Nov 18, 2025 | Centralized governance | HIGH |
| **Unified agent directory** | Frontier | Nov 2025+ | Cross-platform agent inventory | HIGH |
| **Admin center integration** | Frontier | Nov 2025+ | M365 admin center governance | HIGH |

**Key Details:**

**Microsoft Agent 365:**
- Rolled out in Frontier program starting November 18, 2025, 9:00 AM PST
- Centralized control plane for deploying, organizing, and governing agents at scale
- Integrates with M365 admin center, Defender, Entra, and Purview
- Requires at least one Microsoft 365 Copilot license to enable
- Unified directory of agent identities across Copilot Studio and Azure AI Foundry
- Initially limited to Frontier early access program participants

**Frontier Program:**
- Extended to individuals with M365 Personal, Family, or Premium subscriptions
- Provides early access to newest Copilot and agent experiences

**Sources:**
- [Microsoft Agent 365 Overview](https://learn.microsoft.com/en-us/microsoft-agent-365/overview)
- [Ignite 2025 Agent 365 announcement](https://www.microsoft.com/en-us/microsoft-365/blog/2025/11/18/microsoft-ignite-2025-copilot-and-agents-built-to-power-the-frontier-firm/)
- [New capabilities for AI admins](https://techcommunity.microsoft.com/blog/microsoft365copilotblog/new-capabilities-for-ai-admins-from-ignite-2025/4478906)

### 6. Analytics & Observability

| Feature | Status | Timeline | Impact | Confidence |
|---------|--------|----------|--------|------------|
| **ROI analytics** | 2025 Wave 2 | Oct 2025 - Mar 2026 | Time/cost savings estimates | MEDIUM |
| **User comment analytics** | 2025 Wave 2 | Oct 2025 - Mar 2026 | Thumbs up/down feedback | MEDIUM |
| **MCP tracing & analytics** | GA | Build 2025 | Activity map with MCP server invocations | HIGH |

**Sources:**
- [2025 Wave 2 Copilot Studio Features](https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/microsoft-copilot-studio/planned-features)

### 7. SharePoint Governance for AI

| Feature | Status | Timeline | Impact | Confidence |
|---------|--------|----------|--------|------------|
| **SharePoint Admin Agent** | Preview | Nov 2025+ | AI-powered governance tasks | HIGH |
| **Storage skill** | Preview | Full by end Jan 2026 | Storage management | MEDIUM |
| **Knowledge Agent** | GA planned | Early CY 2026 | Included with M365 Copilot | MEDIUM |
| **1,000 files per agent** | GA | Oct 6, 2025 | SharePoint/OneDrive uploads | HIGH |

**Key Details:**

**SharePoint Admin Agent:**
- Currently in public preview (Ignite 2025 announcement)
- Requires M365 Copilot license (at least one user must have license)
- Monitors inactive sites, overshared content, permissions sprawl
- Applies policies like archiving, adjusting access
- No specific GA date announced for Admin Agent itself

**Sources:**
- [SharePoint Admin Agent documentation](https://learn.microsoft.com/en-us/sharepoint/content-governance-agent)
- [SharePoint Ignite 2025 announcements](https://techcommunity.microsoft.com/blog/spblog/sharepoint-showcase-announcements-at-microsoft-ignite-2025/4470378)

### 8. Licensing Changes

| Feature | Status | Timeline | Impact | Confidence |
|---------|--------|----------|--------|------------|
| **M365 Copilot Business (SMB)** | GA | Dec 2, 2025 | $21/user/month, 300-user limit | HIGH |
| **Copilot Business promo** | Active | Dec 1, 2025 - Mar 31, 2026 | 15% off ($18/user/month) | HIGH |
| **Power Apps per app SKU** | End of sale | 2026 | Affects per-app licensing | MEDIUM |

**Key Details:**

**Microsoft 365 Copilot Business:**
- Designed for SMBs with fewer than 300 users
- Standard price: $21/user/month
- Promotional price (Dec 1, 2025 - Mar 31, 2026): $18/user/month (15% off)
- Can be added to M365 Business Basic, Standard, Premium plans
- Same features as enterprise Copilot at lower price point
- Bundle pricing: Business Standard + Copilot = $42.50/user/month (35% off bundle)

**Managed Environment Licensing:**
- All active users in Managed Environments need premium licenses (Power Apps Premium, Power Automate Premium, Dynamics 365 Enterprise, or Copilot Studio)
- Pay-as-you-go does NOT satisfy Managed Environment licensing requirements for active users (documented in v1.2.25)
- February 2026 deadline for pipeline Managed Environment enforcement (documented in v1.2.25)

**Sources:**
- [Microsoft 365 Copilot Licensing](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-licensing)
- [Copilot Business announcement](https://www.microsoft.com/en-us/microsoft-365/blog/2025/12/02/microsoft-365-copilot-business-the-future-of-work-for-small-businesses/)
- [Managed Environment Licensing](https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-licensing)

---

## Deprecated / Changed Features

### 1. API Retirements (CRITICAL)

| API / Service | Retirement Date | Impact | Migration Path | Confidence |
|---------------|----------------|--------|----------------|------------|
| **Exchange Web Services (EWS)** | October 1, 2026 | Blocks non-Microsoft app requests | Migrate to Microsoft Graph | HIGH |
| **SharePoint Add-Ins** | April 2, 2026 | Add-in model no longer available | Migrate to SharePoint Framework (SPFx) | HIGH |
| **Azure ACS for SharePoint** | April 2, 2026 | Authentication stops working | Migrate to Entra ID | HIGH |
| **Azure Key Vault APIs (pre-2026-02-01)** | February 27, 2027 | Old APIs retired | Update to API version 2026-02-01+ | HIGH |
| **Microsoft Graph Toolkit** | August 28, 2026 | Retirement period begins Sep 1, 2025 | No replacement specified | HIGH |
| **SMTP AUTH with Basic Auth** | March 1, 2026 | Basic auth removed for SMTP | Modern auth required | HIGH |
| **Entra ID Protection Risk Policies** | October 1, 2026 | Risk policy experience retired | Migrate to Conditional Access | HIGH |
| **Entra PIM Iteration 2 (beta) APIs** | October 28, 2026 | Beta APIs deprecated | Use GA PIM APIs | HIGH |
| **Public Folder APIs** | October 2026 | No programmatic CRUD for public folders | Manual management only | MEDIUM |

**Critical Details:**

**Exchange Web Services (MC676299):**
- Microsoft will START BLOCKING EWS requests from non-Microsoft apps on October 1, 2026
- Three-year notice period (announced September 2023)
- Only affects Microsoft 365 and Exchange Online (no changes to Exchange Server)
- Applications still using EWS after October 2026 will fail catastrophically
- **Action Required:** Migrate to Microsoft Graph immediately

**SharePoint Add-Ins:**
- SharePoint add-in model retired fully April 2, 2026
- Azure ACS for SharePoint Online retired November 27, 2023; stops working April 2, 2026
- **Action Required:** Migrate to SharePoint Framework (SPFx) before April 2026

**Azure Key Vault API Version 2026-02-01:**
- Releasing February 2026 with Azure RBAC as default access control
- All API versions BEFORE 2026-02-01 retire February 27, 2027
- New key vaults default to enableRbacAuthorization = true unless explicitly set to false
- Existing key vaults continue using current access control model
- **Action Required:** Update ARM/BICEP/Terraform templates to API version 2026-02-01 or later before Feb 27, 2027

**Sources:**
- [EWS Retirement announcement](https://devblogs.microsoft.com/microsoft365dev/retirement-of-exchange-web-services-in-exchange-online/)
- [SharePoint Add-Ins retirement FAQ](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/add-ins-and-azure-acs-retirements-faq)
- [Azure Key Vault API 2026-02-01](https://learn.microsoft.com/en-us/azure/key-vault/general/access-control-default)
- [2026 End-of-Support Milestone](https://blog.admindroid.com/2026-end-of-support-milestone-in-microsoft-365/)

### 2. Power Platform Deprecations

| Feature | Deprecation Date | Impact | Migration Path | Confidence |
|---------|------------------|--------|----------------|------------|
| **Bring Your Own Key (BYOK)** | January 6, 2026 | Must migrate to CMK or revert to Microsoft-managed keys | Migrate to Customer-Managed Keys (CMK) | HIGH |
| **BYOK for production environments** | June 1, 2025 | Can no longer apply BYOK to production | Use CMK instead | HIGH |

**Critical Details:**

**BYOK Deprecation:**
- Microsoft discontinued support for BYOK effective January 6, 2026
- As of June 1, 2025, customers cannot apply BYOK to production environments
- Environments not migrated by January 6, 2026 automatically revert to Microsoft-managed keys
- **Migration Required:** Move to Customer-Managed Keys (CMK) immediately

**CMK Benefits over BYOK:**
- Removes upload size limits for files and images
- Faster key application with less downtime
- Improved handling of key vault access changes
- Expanded global availability
- Enhanced data protection for Dataverse environments

**Sources:**
- [CMK Updates announcement](https://www.microsoft.com/en-us/power-platform/blog/2025/08/12/customer-managed-key-updates/)
- [Migrate BYOK to CMK](https://learn.microsoft.com/en-us/power-platform/admin/cmk-migrate-from-byok)
- [Important changes coming](https://learn.microsoft.com/en-us/power-platform/important-changes-coming)

### 3. Platform Changes & Corrections

| Item | Status | Timeline | Impact | Confidence |
|------|--------|----------|--------|------------|
| **Sentinel Azure portal deprecation** | Extended | Now March 31, 2027 (was July 2026) | More time to migrate | HIGH |
| **Classic eDiscovery retirement** | Clarified | 21Vianet only | No impact on global Microsoft 365 | HIGH |
| **GPT-4o replaced by GPT-4.1** | Changed | Oct 27, 2025 | New agents use GPT-4.1 by default | HIGH |

**Sources:**
- Documented in FSI-AgentGov v1.2.37 (Learn Monitor PR #6)

---

## Platform Announcements

### 1. Microsoft Purview AI Governance

**Status:** Microsoft named Leader in 2025-2026 IDC MarketScape for Unified AI Governance Platforms (December 2025)

**Key Capabilities:**
- Data Security Posture Management (DSPM) for AI with graphical tools
- Compliance Manager with 100+ regulatory framework templates
- Native integration of Microsoft Foundry, Agent 365, Purview, Entra, Defender
- Centralized oversight across AI lifecycle
- Support for Microsoft Agent 365

**Sources:**
- [IDC MarketScape announcement](https://www.microsoft.com/en-us/security/blog/2026/01/14/microsoft-named-a-leader-in-idc-marketscape-for-unified-ai-governance-platforms/)
- [Compliance Meets AI 2026](https://techcommunity.microsoft.com/blog/healthcareandlifesciencesblog/compliance-meets-ai-2026-microsoft-purview-in-the-age-of-ai/4475027)

### 2. Sentinel MCP Server Integration

**Status:** Public Preview (2025)

**Key Capabilities:**
- Natural language queries to Sentinel data lake without KQL
- Available in GitHub Copilot, Copilot Studio, Microsoft Foundry
- Fully hosted, no infrastructure deployment required
- Microsoft Entra ID authentication
- Scenario-focused security tool collections
- Graph-based approach for Security Copilot agents

**Sources:**
- [Sentinel MCP Overview](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-overview)
- [Use Sentinel MCP in Copilot Studio](https://learn.microsoft.com/en-us/azure/sentinel/datalake/sentinel-mcp-use-tool-copilot-studio)
- [Sentinel December 2025 updates](https://techcommunity.microsoft.com/blog/microsoftsentinelblog/what%E2%80%99s-new-in-microsoft-sentinel-december-2025/4477063)

### 3. Power Platform Governance Pillars (2025 Wave 2)

**Four Foundational Pillars:**

1. **Managed Security** - Advanced protection for AI-driven world, security by default, comprehensive auditing
2. **Managed Governance** - Comprehensive visibility, granular control, reduced administrative overhead
3. **Managed Operations** - Monitoring, alerting, lifecycle management
4. **Managed Availability** - Enterprise-grade reliability for mission-critical workloads

**Key Focus Areas:**
- Security and compliance with enterprise-grade protection for all Power Platform assets
- Copilot governance with improved enterprise scalability
- Enterprise scale administration with unified interface, API, PowerShell, CLI automation

**Sources:**
- [Wave 2 Governance Overview](https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/power-platform-governance-administration/)
- [Wave 2 Planned Features](https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/power-platform-governance-administration/planned-features)

---

## Recommendations for Framework Updates

### HIGH PRIORITY (Update Required)

1. **Document Entra Agent ID (Control 1.23 or new control)**
   - Automatic agent identity creation feature
   - Configuration in Power Platform admin center
   - Integration with Microsoft Agent 365
   - Frontier program access requirements
   - **Confidence:** HIGH
   - **Source:** Official Microsoft Learn documentation

2. **Update DLP for Copilot Prompts (Control 1.5)**
   - Public Preview completed (December 2025)
   - GA timeline: Late March - Late April 2026
   - New roles: Entra AI Admin, Purview Data Security AI Admin
   - Available to ALL tenants (E1/E3/E5) by December 2025
   - **Status:** Already documented in v1.2.33
   - **Action:** Update with final GA dates and new roles
   - **Confidence:** HIGH

3. **Add Microsoft Agent 365 Documentation (Framework section)**
   - New centralized governance control plane
   - Frontier program access (November 2025)
   - Integration with M365 admin center, Defender, Entra, Purview
   - Requires M365 Copilot license
   - **Confidence:** HIGH
   - **Source:** Official Microsoft Learn and Ignite 2025 announcements

4. **Update API Deprecation Warnings (Multiple controls)**
   - EWS retirement October 1, 2026 (affects email integrations)
   - SharePoint Add-Ins retirement April 2, 2026 (affects SharePoint extensibility)
   - Azure Key Vault API retirement February 27, 2027 (affects key management)
   - BYOK deprecated January 6, 2026 (affects encryption key management)
   - **Action:** Add deprecation warnings to Controls 1.12 (encryption), any SharePoint integration guidance
   - **Confidence:** HIGH

5. **Document MCP GA (Control 2.17 or new section)**
   - MCP reached GA at Build 2025
   - 1,400+ system integrations available
   - Enhanced tracing and analytics in activity map
   - Sentinel MCP server for security use cases
   - **Confidence:** HIGH

6. **Update Defender AI-SPM (Control 1.24)**
   - GCP Vertex AI support (May 2025 preview)
   - AI Agent Security preview (Ignite 2025)
   - Unified agent inventory across Foundry and Copilot Studio
   - **Status:** Control 1.24 added in v1.2.10
   - **Action:** Update with GCP support and agent security preview
   - **Confidence:** HIGH

7. **Update Managed Environment Licensing (Control 2.1)**
   - BYOK deprecated January 6, 2026; must migrate to CMK
   - Power Apps per app SKU end of sale (2026)
   - **Status:** Already documented in v1.2.25
   - **Action:** Add BYOK deprecation warning
   - **Confidence:** HIGH

### MEDIUM PRIORITY (Consider Adding)

8. **Document M365 Copilot Business License (Framework section)**
   - New SMB SKU at $21/user/month (300-user limit)
   - Promotional pricing: $18/user/month (Dec 1, 2025 - Mar 31, 2026)
   - **Status:** Already documented in v1.2.33
   - **Action:** Update with promotional pricing end date
   - **Confidence:** HIGH

9. **Add SharePoint Admin Agent (Control 4.x or new control)**
   - Currently in public preview
   - AI-powered governance tasks
   - Monitors inactive sites, overshared content, permissions sprawl
   - Requires M365 Copilot license
   - **Confidence:** MEDIUM (no GA date announced)

10. **Document Sentinel MCP Integration (Control 3.9)**
    - Alternative to Power Platform Admin Activity connector
    - Natural language queries without KQL
    - Available in Copilot Studio, GitHub Copilot, Microsoft Foundry
    - **Status:** Sentinel integration already documented in v1.2.32
    - **Action:** Add MCP as integration option
    - **Confidence:** HIGH

11. **Add Express Mode Optimization (Control 2.17)**
    - Preview feature optimizes flows to finish within 2 minutes
    - Avoids timeouts for complex orchestrations
    - **Confidence:** MEDIUM (preview only)

### LOW PRIORITY (Monitor for GA)

12. **Python Code Interpreter (Knowledge/Training section)**
    - Preview: Excel/CSV/PDF file analysis
    - Powered by code interpreter in chat
    - **Confidence:** MEDIUM (preview only)

13. **ROI Analytics (Control 3.x)**
    - Time and cost savings estimates
    - Based on successful runs or actions
    - **Confidence:** MEDIUM (limited details)

14. **Automated Agent Evaluation (Control 2.5)**
    - Public preview for systematic testing at scale
    - Compare multiple agent versions
    - **Confidence:** MEDIUM (preview only)

---

## Verification Sources

All findings verified against:

### Official Microsoft Documentation
- [Microsoft Copilot Studio What's New](https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new)
- [Power Platform 2025 Wave 2 Release Plan](https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/)
- [Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/)
- [Microsoft Agent 365 Overview](https://learn.microsoft.com/en-us/microsoft-agent-365/overview)
- [Defender for Cloud AI Security](https://learn.microsoft.com/en-us/azure/defender-for-cloud/ai-security-posture)
- [Purview DLP for Copilot](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about)
- [Azure Key Vault API 2026-02-01](https://learn.microsoft.com/en-us/azure/key-vault/general/access-control-default)

### Official Announcements
- [Ignite 2025 Entra Announcements](https://learn.microsoft.com/en-us/entra/fundamentals/whats-new-ignite-2025)
- [Ignite 2025 M365 Copilot](https://www.microsoft.com/en-us/microsoft-365/blog/2025/11/18/microsoft-ignite-2025-copilot-and-agents-built-to-power-the-frontier-firm/)
- [MCP GA Announcement](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/model-context-protocol-mcp-is-now-generally-available-in-microsoft-copilot-studio/)
- [CMK Updates](https://www.microsoft.com/en-us/power-platform/blog/2025/08/12/customer-managed-key-updates/)
- [Copilot Business SKU](https://www.microsoft.com/en-us/microsoft-365/blog/2025/12/02/microsoft-365-copilot-business-the-future-of-work-for-small-businesses/)

### Message Center
- [MC1181998 - DLP for Copilot Prompts](https://mc.merill.net/message/MC1181998)
- [MC676299 - EWS Retirement](https://mc.merill.net/message/MC676299)

### Community & Tech Blogs
- [2026 End-of-Support Milestones](https://blog.admindroid.com/2026-end-of-support-milestone-in-microsoft-365/)
- [IDC MarketScape Announcement](https://www.microsoft.com/en-us/security/blog/2026/01/14/microsoft-named-a-leader-in-idc-marketscape-for-unified-ai-governance-platforms/)
- [Sentinel December 2025 Updates](https://techcommunity.microsoft.com/blog/microsoftsentinelblog/what%E2%80%99s-new-in-microsoft-sentinel-december-2025/4477063)

---

## Confidence Assessment

| Category | Confidence | Rationale |
|----------|-----------|-----------|
| **New Capabilities** | HIGH | All features verified against official Microsoft Learn release plans and announcements |
| **Deprecations** | HIGH | Official deprecation notices from Microsoft with specific dates |
| **Platform Announcements** | HIGH | Ignite 2025 announcements and official blog posts |
| **Timeline Accuracy** | HIGH | Dates sourced from official release plans and Message Center |
| **Feature Availability** | MEDIUM-HIGH | Some preview features may change before GA |

---

## Research Gaps

1. **SharePoint Admin Agent GA Date** - No specific GA timeline announced; monitoring required
2. **Agent 365 Broader Rollout** - Currently Frontier-only; general availability timeline unclear
3. **ROI Analytics Details** - Limited technical documentation on calculation methodology
4. **Express Mode Technical Details** - Preview feature with minimal architectural documentation
5. **Python Code Interpreter Limitations** - Security boundaries and file size limits not fully documented

---

## Next Steps for Framework

1. **Immediate Updates (Q1 2026):**
   - Add Entra Agent ID documentation (new control or update Control 1.23)
   - Document Microsoft Agent 365 as centralized governance control plane
   - Update API deprecation warnings across affected controls
   - Add MCP GA status to integration guidance

2. **Q2 2026 Updates:**
   - Update DLP for Copilot prompts with final GA status (after April 2026)
   - Monitor SharePoint Admin Agent for GA announcement
   - Track Agent 365 rollout beyond Frontier program

3. **Q3 2026 Updates:**
   - Add deprecation reminders for EWS (Oct 1, 2026 deadline)
   - Monitor preview features (Express mode, Python interpreter, automated evaluation) for GA

4. **Q4 2026 and Beyond:**
   - Track Azure Key Vault API migration deadlines (Feb 27, 2027)
   - Monitor Agent 365 expansion to Security Copilot, M365 Copilot, third-party platforms

---

**Research Completed:** February 2, 2026
**Researcher:** Claude (GSD Project Researcher)
**Framework Version Reviewed:** v1.2.37
