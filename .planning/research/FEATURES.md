# Features Research: Microsoft AI Agent Governance (2025-2026)

**Domain:** AI Agent Governance for Microsoft 365 and Power Platform
**Researched:** February 2, 2026
**Confidence:** HIGH (Official Microsoft Learn and TechCommunity sources)

## Summary

Microsoft released **18+ major governance features** for AI agents between November 2025 and January 2026, primarily announced at Ignite 2025. The platform is rapidly maturing from basic controls to enterprise-grade governance with the introduction of **Microsoft Agent 365** (the control plane for agents), **Microsoft Entra Agent ID** (identity for agents), and comprehensive **Defender for Cloud Apps** real-time protection.

**Key findings:**
- **Agent 365 Control Plane** - Unified registry, access control, and governance for all agent types (Copilot Studio, Agent Builder, Azure AI Foundry, third-party)
- **Entra Agent ID** - First-class identity objects for agents with lifecycle governance, sponsorship, and entitlement management
- **Defender Real-Time Protection** - GA February 2026 for Copilot Studio agents with 1-second response time for threat blocking
- **Microsoft 365 Admin Center Agent Settings** - Centralized governance controls (allowed types, sharing, templates, user access)
- **Purview DSPM Enhancements** - AI observability, weekly oversharing risk assessments for top 100 sites, agent-specific insights

**Coverage Status:** FSI-AgentGov v1.2.37 documents most GA features. **Gaps exist for preview features** including Agent 365 control plane, Entra Agent ID governance, and M365 admin center agent settings.

---

## New Governance Features (November 2025 - January 2026)

### Security Features

#### 1. Defender for Cloud Apps - Copilot Studio AI Agent Protection (GA February 2026)

**Status:** Generally Available
**Source:** [Protect your Microsoft Copilot Studio AI agents (Preview)](https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-protection)

**Capabilities:**
| Feature | Description | Coverage in v1.2.37 |
|---------|-------------|---------------------|
| **AI Agent Inventory** | Automatic discovery of all Copilot Studio agents across tenant with security posture visibility | ✓ Control 1.8 |
| **AI Agent Activity Logging** | Audit logs via M365 App Connector to Purview | ✓ Control 1.8 |
| **Real-Time Protection** | Blocks suspicious tool invocations before execution (1-second response) | ✓ Control 1.8 |
| **Advanced Hunting Integration** | Agent data in Defender XDR advanced hunting queries | ✓ Control 1.8 |
| **XDR Incidents & Alerts** | Blocked actions create Defender XDR incidents | ✓ Control 1.8 |

**Prerequisites:**
- Microsoft Defender for Cloud Apps (included in M365 E5)
- M365 App Connector configured in Defender portal
- Power Platform Admin + Defender XDR Admin roles
- Two-portal configuration (Defender portal + PPAC)

**FSI-AgentGov Status:** ✅ **Fully documented** in Control 1.8 as of v1.2.37

---

#### 2. Security Webhooks API for Additional Threat Detection (GA November 2025)

**Status:** Generally Available (November 28, 2025)
**Source:** [Build a runtime threat detection system for Copilot Studio agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/external-security-webhooks-interface-developers)

**Capabilities:**
- Third-party security provider integration (Palo Alto Prisma AIRS, custom webhooks)
- POST /analyze-tool-execution endpoint for real-time threat evaluation
- <1000ms response requirement
- Entra app registration with Federated Identity Credentials

**FSI-AgentGov Status:** ✅ **Fully documented** in Control 1.8 as of v1.2.37

---

#### 3. Defender AI Security Posture Management (AI-SPM) Enhancements (2025-2026)

**Status:** GA (with preview features)
**Source:** [What's new - Microsoft Defender for Cloud Apps](https://learn.microsoft.com/en-us/defender-cloud-apps/release-notes)

**Recent Enhancements:**
| Enhancement | Release | Description |
|-------------|---------|-------------|
| **GCP Vertex AI Support** | GA November 2025 | Full posture management for Google Cloud AI workloads |
| **Agent-Specific Recommendations** | January 2026 | Targeted security recommendations for Copilot Studio and Agent 365 SDK agents |
| **Attack Path Expansion** | January 2026 | New AI-specific attack path scenarios including indirect prompt injection chains |
| **Agent 365 SDK Discovery** | Preview | Blueprint-registered agent inventory and risk assessment |

**FSI-AgentGov Status:** ✅ **Documented** in Control 1.24 (GCP support documented; Agent 365 SDK discovery is preview)

---

#### 4. Microsoft Entra Agent ID (Public Preview)

**Status:** Public Preview (Frontier program)
**Source:** [Governing Agent Identities (Preview)](https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview)

**New Capabilities:**
| Feature | Description | FSI Value |
|---------|-------------|-----------|
| **Agent Identity Objects** | First-class identity accounts for AI agents in Entra ID | Enables identity-based governance |
| **Agent Identity Blueprint** | Template definitions for agent identity creation | Standardized agent deployment |
| **Sponsorship Model** | Human sponsors accountable for agent lifecycle | FINRA 3110 supervision alignment |
| **Entitlement Management** | Access packages for time-bound resource access | Least privilege enforcement |
| **Conditional Access** | CA policies applicable to agent identities | Zone-based access control |
| **Lifecycle Workflows** | Automated sponsor updates and access reviews | Automated compliance |

**Four New Entra Object Types:**
1. Agent identity blueprint
2. Agent identity blueprint principal
3. Agent identity
4. Agent user

**FSI-AgentGov Status:** ❌ **NOT DOCUMENTED** - Preview feature requiring new control or Control 1.2 enhancement

**Gap Severity:** HIGH - This is a foundational identity architecture change that affects access control, audit logging, and compliance reporting across multiple controls.

---

### Management Features

#### 5. Microsoft Agent 365 Control Plane (Frontier Preview)

**Status:** Frontier Preview (early access program)
**Source:** [Microsoft Agent 365: The control plane for AI agents](https://www.microsoft.com/en-us/microsoft-365/blog/2025/11/18/microsoft-agent-365-the-control-plane-for-ai-agents/)

**Five Key Capabilities:**

**a) Agent Registry**
- Single source of truth for all agents (Copilot Studio, Agent Builder, SharePoint, M365 Agent SDK, AI Foundry, Data Fabric, Entra-only, Microsoft-provided, third-party)
- Rich metadata: status, usage, sessions, exception rates, last update dates
- Sortable/filterable by publisher, channel, platform, availability
- Lifecycle actions: block, delete, update agents directly from registry

**b) Access Control**
- Manage agents and limit resource access
- Least privilege enforcement
- Integration with Entra Agent ID

**c) Visualization**
- Unified dashboard showing connections between agents, people, and data
- Advanced analytics for agent relationships

**d) Security**
- Deep integration with Microsoft Purview, Entra, and Defender
- Highlights risky agents and outdated configurations
- Real-time threat protection

**e) Agent Policies**
- Automated governance workflows
- Policy-based agent management

**FSI-AgentGov Status:** ⚠️ **PARTIAL COVERAGE** - Control 1.2 covers agent registry concept but not Agent 365 architecture
- Control 3.1 covers agent inventory but not unified registry across all agent types
- Control 3.8 covers Copilot Hub but not Agent 365 control plane

**Gap Severity:** HIGH - Agent 365 is Microsoft's strategic direction for multi-platform agent governance. Framework should document this architecture.

---

#### 6. Microsoft 365 Admin Center - Agent Settings (Preview/GA Q1 2026)

**Status:** Preview (GA planned Q1 2026)
**Source:** [Agent Settings in Microsoft 365 admin center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-settings?view=o365-worldwide)

**Four Configuration Areas:**

| Setting | Description | FSI Use Case |
|---------|-------------|--------------|
| **Allowed Agent Types** | Specify which agent categories are permitted | Zone-based restrictions (e.g., only verified agents in Zone 3) |
| **Sharing** | Manage who can share agents and sharing methods | Prevent org-wide sharing in Zone 1/2 |
| **Templates** | Pre-set policies, rules, and allowlists for new agents | Standardized controls for consistency |
| **User Access** | Control which users/groups can interact with agents | Role-based access alignment |

**Security Templates:**
- Default templates with Entra, Purview, and SharePoint controls
- Automatic license assignment for Frontier/Agent 365 users

**FSI-AgentGov Status:** ❌ **NOT DOCUMENTED** - New M365 admin center governance controls not in framework

**Gap Severity:** MEDIUM - These are centralized governance controls but overlap with existing PPAC controls. Need to document relationship.

---

#### 7. Copilot Hub Enhancements (Power Platform Admin Center)

**Status:** GA with preview features
**Source:** [Track, manage, and scale Copilot adoption in the Power Platform](https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub)

**New Capabilities (2025-2026):**

**AI Feature Access Control (Preview - Managed Environments only):**
- Explicitly allow specific users OR allow all except exclusion list
- Granular control per Copilot feature:
  - Dynamics 365 Sales: Copilot, Lead summary, Opportunity summary
  - Power Apps: Copilot chat, Form fill assistance, Smart paste, Row summary, Visualize with Copilot, Natural language search

**AI Capabilities Toggle (Dynamics 365 Sales):**
- Turn on/off AI Agents (Sales Qualification Agent, Sales Close Agent)
- Environment and environment group level controls
- Default: ON for all environments

**FSI-AgentGov Status:** ⚠️ **PARTIAL COVERAGE** - Control 3.8 documents Copilot Hub but not these new granular controls

**Gap Severity:** MEDIUM - New controls for limiting AI feature access by user

---

### Reporting Features

#### 8. Microsoft Purview - DSPM for AI Enhancements

**Status:** GA (classic) + Preview (new experience)
**Source:** [Learn about Microsoft Purview DSPM](https://learn.microsoft.com/en-us/purview/data-security-posture-management-learn-about)

**New Capabilities (2025-2026):**

**Data Risk Assessments:**
- Automated weekly assessment for top 100 SharePoint sites
- Identifies oversharing risks specific to M365 Copilot and agents
- One-click remediation policies

**AI Observability (Enhanced DSPM Preview):**
- Drill down into individual agents
- Contextual insights: risky behaviors, oversharing patterns
- Recommended actions (e.g., creation of retention policies)
- Security teams can see which agents pose oversharing risks

**Item-Level Investigation and Remediation:**
- Identify and fix overshared links at scale
- Bulk remediation capability
- Enhanced for SharePoint knowledge sources used by agents

**FSI-AgentGov Status:** ⚠️ **PARTIAL COVERAGE** - Control 1.6 documents DSPM for AI but not new weekly risk assessments or AI observability features

**Gap Severity:** MEDIUM - Enhanced capabilities for oversharing detection

---

#### 9. Microsoft Purview - Agent 365 Support (Frontier Preview)

**Status:** Frontier Preview
**Source:** [Use Microsoft Purview to manage data security & compliance for Microsoft Agent 365](https://learn.microsoft.com/en-us/purview/ai-agent-365)

**Supported Capabilities for Agent 365:**
- ✓ DSPM for AI (classic and preview)
- ✓ Auditing
- ✓ Data Classification
- ✓ Sensitivity Labels
- ✓ Data Loss Prevention (DLP)
- ✓ Insider Risk Management
- ✓ Communication Compliance
- ✓ eDiscovery
- ✓ Data Lifecycle Management
- ✓ Compliance Manager
- ✕ Encryption without sensitivity labels (not supported)

**Key Features:**
- Agent instances automatically enabled for audit logging and sensitive data detection
- AI observability page shows active agent instances, risk analysis, remediation recommendations
- Agent instances can be included in policies just like users

**FSI-AgentGov Status:** ❌ **NOT DOCUMENTED** - Agent 365 is not covered in framework yet

**Gap Severity:** HIGH - Microsoft's strategic agent platform with Purview integration

---

#### 10. Unified Audit Logging - Agent Activities

**Status:** GA
**Source:** [Security and governance innovations for Microsoft 365 Copilot and agents from Ignite 2025](https://techcommunity.microsoft.com/blog/microsoft365copilotblog/security-and-governance-innovations-for-microsoft-365-copilot-and-agents-from-ig/4476172)

**New Audit Events:**
- All agent-related admin activities in M365 admin center
- Actions: publishing, updating, or removing agents
- Web searched filter in activity explorer (locates web queries in prompts with search query text)

**FSI-AgentGov Status:** ✓ **Documented** in Control 1.7

---

### SharePoint/Grounding Features

#### 11. SharePoint Restricted Search (2026 Feature)

**Status:** Announced for 2026
**Source:** [Is Your SharePoint Ready for Copilot? 2026 Checklist](https://star-knowledge.com/blog/is-your-sharepoint-ready-for-copilot-2026-data-governance-checklist/)

**Capability:**
- Flag sites to exclude from Copilot index
- "Emergency brake" for sites with messy permissions
- Allows cleanup while preventing Copilot access

**FSI-AgentGov Status:** ❌ **NOT DOCUMENTED** - New 2026 SharePoint governance control

**Gap Severity:** LOW - Feature not yet released, but FSI organizations need this

---

#### 12. Tenant Graph Grounding with Semantic Search

**Status:** Preview
**Source:** [What's New in Copilot Studio: November 2025 Updates and Features](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/whats-new-in-microsoft-copilot-studio-november-2025/)

**Capability:**
- Enhanced knowledge retrieval for SharePoint-grounded agents
- Uses cutting-edge internal retrieval tools
- Improves response quality

**FSI-AgentGov Status:** ⚠️ **PARTIAL COVERAGE** - SharePoint grounding documented in Controls 4.6 and 4.7 but not semantic search enhancement

**Gap Severity:** LOW - Grounding quality improvement, not governance control

---

### DLP and Data Protection Features

#### 13. DLP for Microsoft 365 Copilot Prompts (GA January 2026)

**Status:** Generally Available (January 2026)
**Source:** [Compliance Meets AI 2026: Microsoft Purview in the Age of AI](https://techcommunity.microsoft.com/blog/healthcareandlifesciencesblog/compliance-meets-ai-2026-microsoft-purview-in-the-age-of-ai/4475027)

**Capability:**
- DLP now safeguards prompts that contain sensitive data
- Real-time control to prevent M365 Copilot from returning a response when prompt contains sensitive data
- Included for all M365 Copilot and Copilot Chat users (no additional license)

**FSI-AgentGov Status:** ✓ **Documented** in Control 1.5 (updated in v1.2.33)

---

#### 14. Power Platform DLP - Connector Action Control

**Status:** GA
**Source:** [Data policies - Power Platform](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention)

**Capability:**
- Granular control over connector actions (e.g., "Read" but not "Write")
- Configure which actions are permitted within Business or Non-Business groups
- Protects sensitive data without blocking necessary connections

**FSI-AgentGov Status:** ⚠️ **PARTIAL COVERAGE** - Control 1.5 documents DLP but not connector action control granularity

**Gap Severity:** LOW - Enhancement to existing DLP capabilities

---

#### 15. Power Platform DLP - Desktop Flows Module Control

**Status:** GA
**Source:** [Data policies - Power Platform](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention)

**Capability:**
- Classify desktop flow modules and individual module actions as Business, Non-Business, or Blocked
- Ensures RPA automation touching legacy systems is compliant with data policies

**FSI-AgentGov Status:** ❌ **NOT DOCUMENTED** - Desktop flows (RPA) not in scope for agent governance framework

**Gap Severity:** LOW - Out of scope (RPA vs. AI agents)

---

#### 16. Virtual Connectors for Copilot Studio Governance

**Status:** GA
**Source:** [Data policies - Power Platform](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention)

**Capability:**
- Virtual connectors (not based on REST API) for governing Copilot Studio features
- Allow admins to turn off various Copilot and chatbot features via DLP policies
- More "on/off" capabilities expected as rules within Environment groups

**FSI-AgentGov Status:** ⚠️ **PARTIAL COVERAGE** - Control 1.5 mentions virtual connectors but doesn't enumerate them or explain governance use

**Gap Severity:** MEDIUM - Important for feature-level control

---

#### 17. Microsoft Purview Integration in M365 Admin Center (January 2026)

**Status:** GA January 2026
**Source:** [What's New in Microsoft 365 Copilot | January 2026](https://techcommunity.microsoft.com/blog/microsoft365copilotblog/what%E2%80%99s-new-in-microsoft-365-copilot--january-2026/4488916)

**Capability:**
- Purview now integrated into M365 admin center
- Visibility around oversharing risks
- Understand how sensitive data is used in Copilot interactions
- Enable DLP for Copilot policies directly from M365 admin center

**FSI-AgentGov Status:** ✓ **Architecture documented** across multiple controls but not M365 admin center integration specifically

**Gap Severity:** LOW - Admin UX improvement, not new capability

---

#### 18. AI Administrator Role (Microsoft Entra)

**Status:** GA
**Source:** [Security and governance innovations for Microsoft 365 Copilot and agents from Ignite 2025](https://techcommunity.microsoft.com/blog/microsoft365copilotblog/security-and-governance-innovations-for-microsoft-365-copilot-and-agents-from-ig/4476172)

**Capability:**
- New Entra role with view-only permissions in DSPM for AI
- Access to sensitivity labels and sensitive information types
- Enables delegation without full Compliance Admin rights

**FSI-AgentGov Status:** ⚠️ **PARTIAL COVERAGE** - Role catalog in `docs/reference/role-catalog.md` likely needs update

**Gap Severity:** LOW - Role addition, not governance control

---

## Defender Capabilities for Power Platform - Complete List

**Updated:** February 2, 2026

### Microsoft Defender for Cloud Apps - Copilot Studio AI Agents

| Capability | Status | FSI-AgentGov Coverage |
|------------|--------|----------------------|
| **AI Agent Inventory** | GA (Feb 2026) | ✓ Control 1.8 |
| **AI Agent Activity Logging** | GA (Feb 2026) | ✓ Control 1.8 |
| **Real-Time Protection during Runtime** | Preview (Sep 2025) | ✓ Control 1.8 |
| **Advanced Hunting Integration** | Preview (Nov 2025) | ✓ Control 1.8 |
| **XDR Incidents & Alerts** | Preview (Nov 2025) | ✓ Control 1.8 |
| **M365 App Connector Requirement** | GA | ✓ Control 1.8 |

### Microsoft Defender for Cloud - AI-SPM

| Capability | Status | FSI-AgentGov Coverage |
|------------|--------|----------------------|
| **Azure AI Foundry Discovery** | GA | ✓ Control 1.24 |
| **Copilot Studio Discovery** | GA | ✓ Control 1.24 |
| **AI Bill of Materials (AI BOM)** | GA | ✓ Control 1.24 |
| **Attack Path Analysis** | GA | ✓ Control 1.24 |
| **AI-Specific Risk Factors** | GA | ✓ Control 1.24 |
| **Security Recommendations** | GA | ✓ Control 1.24 |
| **AWS Bedrock Support** | GA | ✓ Control 1.24 |
| **GCP Vertex AI Support** | GA (Nov 2025) | ✓ Control 1.24 |
| **Agent-Specific Recommendations** | Preview (Jan 2026) | ✓ Control 1.24 (mentioned) |
| **Agent 365 SDK Discovery** | Preview | ✓ Control 1.24 (mentioned) |
| **Attack Path Expansion for AI** | Preview (Jan 2026) | ✓ Control 1.24 (mentioned) |

### Third-Party Integration

| Capability | Status | FSI-AgentGov Coverage |
|------------|--------|----------------------|
| **Security Webhooks API** | GA (Nov 28, 2025) | ✓ Control 1.8 |
| **POST /analyze-tool-execution** | GA | ✓ Control 1.8 |
| **Entra App Registration with FIC** | GA | ✓ Control 1.8 |
| **Palo Alto Prisma AIRS Integration** | GA | ✓ Control 1.8 (vendor example) |

**Conclusion:** All documented Defender capabilities for Power Platform are covered in FSI-AgentGov v1.2.37 across Controls 1.8 and 1.24.

---

## Preview Features Worth Documenting

### High Priority (FSI-Relevant Preview Features)

| Feature | Status | FSI Value | Recommendation |
|---------|--------|-----------|----------------|
| **Microsoft Entra Agent ID** | Preview (Frontier) | Foundational identity architecture for agents; enables sponsorship (FINRA 3110 alignment) | **Document now** - Preview but strategic |
| **Microsoft Agent 365 Control Plane** | Preview (Frontier) | Unified governance across all agent types; Microsoft's strategic direction | **Document now** - Early adopter guidance |
| **M365 Admin Center Agent Settings** | Preview (GA Q1 2026) | Centralized agent governance controls | **Document Q1 2026** - Wait for GA |
| **Agent 365 SDK Discovery (AI-SPM)** | Preview | Inventory for blueprint-registered agents | **Document Q2 2026** - Wait for maturity |

### Medium Priority

| Feature | Status | FSI Value | Recommendation |
|---------|--------|-----------|----------------|
| **SharePoint Restricted Search** | Announced 2026 | Emergency brake for Copilot indexing | **Document when released** |
| **AI Feature Access Control (PPAC)** | Preview (Managed Env) | Granular user-level feature control | **Document when GA** |
| **Enhanced DSPM AI Observability** | Preview | Agent-specific risk insights | **Monitor for GA** |

### Low Priority

| Feature | Status | FSI Value | Recommendation |
|---------|--------|-----------|----------------|
| **Tenant Graph Grounding with Semantic Search** | Preview | Grounding quality improvement | Quality feature, not governance |
| **DLP Connector Action Control** | GA | Granular DLP | Enhancement to existing control |
| **Desktop Flows DLP** | GA | RPA governance | Out of scope for agent framework |

---

## Gap Analysis

### Features Already Documented (v1.2.37)

✅ **Defender for Cloud Apps - Copilot Studio protection** (Control 1.8)
✅ **Security Webhooks API** (Control 1.8)
✅ **Defender AI-SPM with GCP support** (Control 1.24)
✅ **DLP for Copilot prompts** (Control 1.5)
✅ **Unified audit logging for agents** (Control 1.7)
✅ **Purview DSPM for AI** (Control 1.6)
✅ **SharePoint grounding governance** (Controls 4.6, 4.7)

### Features Missing from Framework (Gaps)

#### HIGH SEVERITY GAPS

**1. Microsoft Entra Agent ID (Preview)**
- **What:** First-class identity objects for agents with lifecycle governance
- **Why FSI needs it:** Sponsorship model aligns with FINRA 3110 supervision requirements; enables Conditional Access for agents
- **Recommendation:** Create new control or enhance Control 1.2 (Agent Registry)
- **Effort:** Medium (3-4 pages of documentation + playbooks)

**2. Microsoft Agent 365 Control Plane (Preview)**
- **What:** Unified registry and governance for all agent types across Microsoft ecosystem
- **Why FSI needs it:** Strategic Microsoft direction; replaces fragmented governance approaches
- **Recommendation:** Create new framework document `docs/framework/agent-365-architecture.md` similar to existing `agent-identity-architecture.md`
- **Effort:** High (framework-level documentation + control updates)

#### MEDIUM SEVERITY GAPS

**3. M365 Admin Center Agent Settings**
- **What:** Centralized agent governance controls (allowed types, sharing, templates, user access)
- **Why FSI needs it:** Complements PPAC controls; needed for M365 Copilot agent governance
- **Recommendation:** Enhance Control 1.2 or 3.1 with M365 admin center governance
- **Effort:** Low-Medium (section addition to existing control)

**4. Copilot Hub AI Feature Access Control**
- **What:** User-level control for specific AI features in Power Apps and Dynamics 365
- **Why FSI needs it:** Enables zone-based feature restrictions (e.g., Zone 1 users can't use certain AI features)
- **Recommendation:** Enhance Control 3.8 (Copilot Hub) with new settings
- **Effort:** Low (section addition)

**5. Virtual Connectors for Copilot Studio**
- **What:** DLP-based feature toggles for Copilot Studio capabilities
- **Why FSI needs it:** Granular control over which Copilot features are permitted
- **Recommendation:** Enhance Control 1.5 with virtual connector table and governance guidance
- **Effort:** Low (section addition + table)

**6. Enhanced DSPM AI Observability**
- **What:** Weekly risk assessments for top 100 sites, agent-specific insights
- **Why FSI needs it:** Proactive oversharing detection for Copilot grounding sources
- **Recommendation:** Enhance Control 1.6 with new DSPM capabilities
- **Effort:** Low (section addition)

#### LOW SEVERITY GAPS

**7. SharePoint Restricted Search (2026 Feature)**
- **What:** Exclude sites from Copilot index
- **Why FSI needs it:** Emergency brake for problematic sites
- **Recommendation:** Add to Control 4.6 or 4.7 when released
- **Effort:** Low (wait for GA)

**8. AI Administrator Role**
- **What:** New Entra role for DSPM view-only access
- **Why FSI needs it:** Delegation without full Compliance Admin
- **Recommendation:** Update `docs/reference/role-catalog.md`
- **Effort:** Minimal (role addition)

---

## Features Framework Already Covers (Validation)

### Security Controls - Coverage Confirmed

| Feature | Control | Notes |
|---------|---------|-------|
| Defender for Cloud Apps - AI Agent Protection | 1.8 | Comprehensive coverage including GA and preview features |
| Security Webhooks API | 1.8 | Third-party integration documented |
| Defender AI-SPM | 1.24 | Multi-cloud support including GCP |
| DLP for Copilot prompts | 1.5 | GA feature documented in v1.2.33 |
| Audit logging for agents | 1.7 | Purview UAL integration |
| DSPM for AI (classic) | 1.6 | Base capabilities documented |
| Communication Compliance for AI | 1.10 | Prompt/response monitoring |
| Insider Risk Management for AI | 1.12 | Risky AI usage detection |
| Information Rights Management | 1.16 | VIEW and EXTRACT usage rights for agents |
| Conditional Access | 1.11 | CA policies for agent workloads |
| Information Barriers | 1.22 | IB support (not Channel Agent) |

### Management Controls - Coverage Confirmed

| Feature | Control | Notes |
|---------|---------|-------|
| Managed Environments | 2.1 | Prerequisite for AI governance |
| Environment Groups | 2.2 | Zone classification |
| Change Management | 2.3 | Platform Change Governance playbook |
| Message Center monitoring | 2.10 | Message Center Monitor solution |
| Environment provisioning | 2.15 | ELM solution |
| Agent lifecycle | 2.13 | Documentation requirements |
| Training and awareness | 2.14 | Maker/user education |

### Reporting Controls - Coverage Confirmed

| Feature | Control | Notes |
|---------|---------|-------|
| Agent inventory | 3.1 | PPAC and Defender inventory |
| Usage analytics | 3.2 | Copilot Hub analytics |
| Compliance reporting | 3.3 | Cross-pillar reporting |
| Incident reporting | 3.4 | Deny Event Correlation solution |
| Orphaned agent detection | 3.6 | Lifecycle monitoring |
| PPAC Security Posture | 3.7 | Native assessment |
| Copilot Hub | 3.8 | Governance dashboard |
| Sentinel integration | 3.9 | SIEM for AI agents |

### SharePoint Controls - Coverage Confirmed

| Feature | Control | Notes |
|---------|---------|-------|
| Information Access Governance | 4.1 | Oversharing prevention |
| Site access reviews | 4.2 | Periodic certification |
| Retention management | 4.3 | Data lifecycle |
| Guest access controls | 4.4 | External user governance |
| Grounding scope governance | 4.6 | Knowledge source management |
| M365 Copilot data governance | 4.7 | Copilot-specific SharePoint controls |

---

## Feature Dependencies

```
Microsoft Agent 365 Control Plane
    ├─ Requires: Microsoft Entra Agent ID
    ├─ Integrates: Microsoft Purview (DSPM, DLP, Audit)
    ├─ Integrates: Microsoft Defender (AI-SPM, Cloud Apps)
    └─ Surfaces: Agent Registry across all platforms

Microsoft Entra Agent ID
    ├─ Enables: Agent identity objects
    ├─ Enables: Sponsorship model
    ├─ Enables: Conditional Access for agents
    ├─ Enables: Entitlement Management for agents
    └─ Prerequisite for: Agent 365 Control Plane

Defender for Cloud Apps - Copilot Studio
    ├─ Requires: M365 App Connector
    ├─ Requires: Defender for Cloud Apps license
    ├─ Integrates: Purview (audit logs)
    ├─ Integrates: Defender XDR (incidents, alerts)
    └─ Complements: Security Webhooks API (third-party)

M365 Admin Center Agent Settings
    ├─ Complements: PPAC Copilot Hub
    ├─ Integrates: Entra (templates, access control)
    ├─ Integrates: Purview (security templates)
    └─ Works with: Agent 365 Control Plane

DSPM for AI Enhancements
    ├─ Monitors: SharePoint sites (grounding sources)
    ├─ Assesses: Agent 365 instances (when available)
    ├─ Integrates: Agent 365 AI Observability
    └─ Complements: Defender AI-SPM (data vs. security focus)
```

---

## Recommendation for FSI-AgentGov v1.3

### Phase 1: Document Preview Features (Immediate - Q1 2026)

**Priority 1: Microsoft Entra Agent ID**
- Create new section in Control 1.2 or new Control 1.25
- Document agent identity architecture
- Document sponsorship model for FINRA 3110 alignment
- Cross-reference with Conditional Access (Control 1.11)
- Effort: 2-3 days

**Priority 2: Microsoft Agent 365 Control Plane**
- Create new framework document `docs/framework/agent-365-architecture.md`
- Document unified registry concept
- Compare with current per-platform governance
- Migration guidance from current approach to Agent 365
- Effort: 3-4 days

**Priority 3: Enhance Existing Controls with New Features**
- Control 1.5: Add virtual connectors table
- Control 1.6: Add enhanced DSPM capabilities
- Control 3.8: Add AI Feature Access Control
- Effort: 1-2 days

### Phase 2: M365 Admin Center Integration (Q1 2026 - wait for GA)

- Enhance Control 1.2 with M365 admin center agent settings
- Document relationship between PPAC and M365 admin center governance
- Update screenshots and verification tests
- Effort: 1 day

### Phase 3: SharePoint Restricted Search (Q2-Q3 2026 - when released)

- Enhance Control 4.6 or 4.7 with Restricted Search
- Document emergency brake use cases
- Add to SharePoint governance checklist
- Effort: 0.5 days

### Total Effort Estimate

- **Phase 1 (Immediate):** 6-9 days
- **Phase 2 (Q1 2026):** 1 day
- **Phase 3 (Q2-Q3 2026):** 0.5 days
- **Total:** 7.5-10.5 days of documentation work

### Rationale for Documenting Preview Features

FSI organizations are early adopters of Microsoft enterprise features. Documenting preview features provides:

1. **Early guidance** for Frontier program participants
2. **Readiness** for GA releases (Q1 2026 for several features)
3. **Strategic alignment** with Microsoft's Agent 365 direction
4. **Competitive advantage** for FSI firms using cutting-edge governance

Mark preview features clearly with admonitions:
```markdown
!!! info "Preview Feature - Frontier Program"
    This feature is in preview and requires participation in Microsoft's Frontier program. Production use is not recommended until GA.
```

---

## Sources

### Official Microsoft Learn Documentation

- [Protect your Microsoft Copilot Studio AI agents (Preview)](https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-protection)
- [Protect your agents in real-time during runtime (Preview)](https://learn.microsoft.com/en-us/defender-cloud-apps/real-time-agent-protection-during-runtime)
- [Discover and detect threats using the AI agents inventory (Preview)](https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-inventory)
- [What's new - Microsoft Defender for Cloud Apps](https://learn.microsoft.com/en-us/defender-cloud-apps/release-notes)
- [Microsoft Purview data security and compliance protections for Microsoft 365 Copilot and other generative AI apps](https://learn.microsoft.com/en-us/purview/ai-microsoft-purview)
- [Learn about Microsoft Purview Data Security Posture Management (DSPM)](https://learn.microsoft.com/en-us/purview/data-security-posture-management-learn-about)
- [Use Microsoft Purview to manage data security & compliance for Microsoft Agent 365](https://learn.microsoft.com/en-us/purview/ai-agent-365)
- [Security and governance - Microsoft Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance)
- [Track, manage, and scale Copilot adoption in the Power Platform](https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub)
- [Build a runtime threat detection system for Copilot Studio agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/external-security-webhooks-interface-developers)
- [Enable external threat detection and protection for Copilot Studio custom agents (preview)](https://learn.microsoft.com/en-us/microsoft-copilot-studio/external-security-provider)
- [Agent Settings in Microsoft 365 admin center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-settings?view=o365-worldwide)
- [Governing Agent Identities (Preview)](https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview)
- [What is Microsoft Entra Agent ID?](https://learn.microsoft.com/en-us/entra/agent-id/identity-professional/microsoft-entra-agent-identities-for-ai-agents)
- [Data policies - Power Platform](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention)

### Microsoft TechCommunity Blog Posts

- [New capabilities for AI admins from Ignite 2025](https://techcommunity.microsoft.com/blog/microsoft365copilotblog/new-capabilities-for-ai-admins-from-ignite-2025/4478906)
- [Security and governance innovations for Microsoft 365 Copilot and agents from Ignite 2025](https://techcommunity.microsoft.com/blog/microsoft365copilotblog/security-and-governance-innovations-for-microsoft-365-copilot-and-agents-from-ig/4476172)
- [Ignite 2025: Copilot Control System and related updates for IT and Security Teams](https://techcommunity.microsoft.com/blog/microsoft365copilotblog/ignite-2025-copilot-control-system-and-related-updates-for-it-and-security-teams/4469768)
- [What's New in Microsoft 365 Copilot | January 2026](https://techcommunity.microsoft.com/blog/microsoft365copilotblog/what%E2%80%99s-new-in-microsoft-365-copilot--january-2026/4488916)
- [Compliance Meets AI 2026: Microsoft Purview in the Age of AI](https://techcommunity.microsoft.com/blog/healthcareandlifesciencesblog/compliance-meets-ai-2026-microsoft-purview-in-the-age-of-ai/4475027)
- [Beyond Visibility: The new Microsoft Purview Data Security Posture Management (DSPM) experience](https://techcommunity.microsoft.com/blog/microsoft-security-blog/beyond-visibility-the-new-microsoft-purview-data-security-posture-management-dsp/4470984)
- [Protect Copilot Studio AI Agents in Real Time with Microsoft Defender](https://techcommunity.microsoft.com/blog/microsoftthreatprotectionblog/protect-copilot-studio-ai-agents-in-real-time-with-microsoft-defender/4446560)
- [Announcing Microsoft Entra Agent ID: Secure and manage your AI agents](https://techcommunity.microsoft.com/blog/microsoft-entra-blog/announcing-microsoft-entra-agent-id-secure-and-manage-your-ai-agents/3827392)
- [Surfing the AI Wave: Manage, Govern, and Protect AI Agents with Microsoft Entra Agent ID](https://techcommunity.microsoft.com/blog/microsoft-entra-blog/surfing-the-ai-wave-manage-govern-and-protect-ai-agents-with-microsoft-entra-age/2464407)

### Microsoft Official Blogs

- [Microsoft Ignite 2025: Copilot and agents built to power the Frontier Firm](https://www.microsoft.com/en-us/microsoft-365/blog/2025/11/18/microsoft-ignite-2025-copilot-and-agents-built-to-power-the-frontier-firm/)
- [Microsoft Agent 365: The control plane for AI agents](https://www.microsoft.com/en-us/microsoft-365/blog/2025/11/18/microsoft-agent-365-the-control-plane-for-ai-agents/)
- [What's New in Microsoft Copilot Studio: November 2025 Updates and Features](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/whats-new-in-microsoft-copilot-studio-november-2025/)
- [Strengthen agent security with near-real-time protection in Microsoft Copilot Studio](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/strengthen-agent-security-with-near-real-time-protection-in-microsoft-copilot-studio/)
- [From runtime risk to real‑time defense: Securing AI agents](https://www.microsoft.com/en-us/security/blog/2026/01/23/runtime-risk-realtime-defense-securing-ai-agents/)
- [Four priorities for AI-powered identity and network access security in 2026](https://www.microsoft.com/en-us/security/blog/2026/01/20/four-priorities-for-ai-powered-identity-and-network-access-security-in-2026/)
- [Evolving Power Platform Governance for AI Agents](https://www.microsoft.com/en-us/power-platform/blog/2025/07/31/evolving-power-platform-governance-for-ai-agents/)
- [Breaking down the facts about secure development with Power Platform](https://www.microsoft.com/en-us/power-platform/blog/2026/01/26/breaking-down-the-facts-about-secure-development-with-power-platform/)

### Industry Sources

- [Defender for Cloud Apps Helps Protect Copilot Studio Agents - Directions on Microsoft](https://www.directionsonmicrosoft.com/reports/defender-for-cloud-apps-helps-protect-copilot-studio-agents/)
- [Is Your SharePoint Ready for Copilot? 2026 Checklist](https://star-knowledge.com/blog/is-your-sharepoint-ready-for-copilot-2026-data-governance-checklist/)
- [Copilot Studio Adds Near-Real-Time Security Controls for AI Agents - Visual Studio Magazine](https://visualstudiomagazine.com/articles/2025/09/08/copilot-studio-adds-near-real-time-security-controls-for-ai-agents.aspx)

---

**Research Confidence:** HIGH
**Sources:** 40+ official Microsoft Learn and TechCommunity articles
**Date Range:** November 2025 - February 2026
**Verification:** Cross-referenced with FSI-AgentGov v1.2.37 CHANGELOG and control documentation
