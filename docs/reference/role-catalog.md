# Administrator Role Catalog

Canonical, framework-friendly role names used throughout this framework (controls, templates, and downloads).

---

## How to Use This Catalog

- **Primary Owner Admin Role**: each control should name **one** primary owner role (who is accountable for implementing/configuring that control).
- **Supporting Roles** (optional): add only when needed for access, evidence collection, or shared responsibility.
- **Naming rule**: use the **canonical short name** from this page in control prerequisites.

> This catalog is intentionally **framework-friendly** (short names). It is not a complete list of all Microsoft built-in role display names.

---

## Canonical Roles (Short Names)

### Entra (Identity)

| Canonical Role | Typical Responsibilities | Accepted Aliases (Normalize From) |
|---|---|---|
| **Entra Global Admin** | Tenant-wide configuration and access | Global Administrator, Global Admin |
| **Entra Privileged Role Admin** | Role assignment and privileged access | Privileged Role Administrator |
| **Entra App Admin** | App registrations and enterprise apps | Application Administrator |
| **Entra User Admin** | User and group administration | User Administrator |
| **Entra Identity Governance Admin** | Access reviews, entitlement management | Identity Governance Administrator |
| **Authentication Administrator** | Manage authentication methods for non-admin users | Authentication Administrator |
| **Entra Security Admin** | Security configuration, policy, and Defender XDR access | Security Administrator, Defender XDR Admin (informal) |
| **Entra Global Reader** | Read-only tenant visibility | Global Reader |
| **Entra Security Reader** | Read-only security visibility | Security Reader |
| **AI Administrator** | Manage M365 Copilot settings, AI services, connector delegation, Copilot feature access controls, and agent governance settings | Microsoft 365 AI Administrator |
| **AI Reader** | Read all aspects of Microsoft 365 Copilot and AI-related enterprise services (read-only counterpart to AI Administrator). Role template ID `1fe13547-53f6-408d-ac04-7f8eed167b38`. | Microsoft 365 AI Reader |
| **Entra Agent ID Admin** | Manage agent identity registrations and lifecycle | Agent ID Administrator |
| **Entra Agent ID Developer** | Register and configure agent identities | Agent ID Developer |

!!! note "Agent 365 Read-Only Role — AI Reader (May 2026)"
    **AI Reader** is the new read-only counterpart to AI Administrator, added with Microsoft Agent 365 GA on May 1, 2026. AI Reader provides view-only access to Microsoft 365 Copilot and AI-related enterprise service configuration — appropriate for compliance officers, internal auditors, FINRA Rule 3110 supervisors, and SOC analysts who need visibility into AI governance posture without authoring authority. Prior to May 2026, Agent 365 administrative access was limited to Entra Global Admin and AI Administrator only; AI Reader closes the longstanding read-only gap. Microsoft has not yet announced fine-grained Agent 365 admin roles beyond AI Administrator and AI Reader — verify against Microsoft Learn for current role granularity. Use Entra Privileged Identity Management (PIM) for just-in-time elevation of AI Administrator where possible.

!!! note "Defender XDR Administrator"
    "Defender XDR Administrator" is informal terminology used in community and operational contexts. There is no distinct Microsoft Entra built-in role named "Defender XDR Administrator." The official role for managing Microsoft Defender XDR is **Entra Security Admin** (Security Administrator). This framework uses "Entra Security Admin" as the canonical name and accepts "Defender XDR Admin" as a normalization alias. See [Microsoft Learn: Manage access to Defender XDR](https://learn.microsoft.com/en-us/defender-xdr/m365d-permissions) for authoritative role documentation.

### Purview (Compliance)

| Canonical Role | Typical Responsibilities | Accepted Aliases (Normalize From) |
|---|---|---|
| **Microsoft Purview Admin** | Purview portal administration and configuration | Purview Administrator |
| **Purview Compliance Admin** | Core compliance configuration | Compliance Administrator, Purview Compliance Administrator |
| **Purview Compliance Reader** | Read-only compliance visibility | Compliance Reader |
| **Purview Compliance Data Admin** | Compliance data access/exports | Compliance Data Administrator |
| **Purview Info Protection Admin** | Labels, policies, and information protection | Information Protection Admin |
| **Purview Records Manager** | Retention/records governance | Records Management Administrator, Records Manager |
| **Purview Audit Admin** | Audit configuration | Audit Administrator |
| **Purview Audit Reader** | Audit search/read-only | Audit Log Reader |
| **Compliance Manager Admin** | Compliance Manager setup and templates | Compliance Manager Administrator |
| **Purview Communication Compliance Roles** | Communication compliance workflows | Communication Compliance Admin/Analyst/Investigator/Viewer |
| **Purview Insider Risk Roles** | Insider risk program workflows | Insider Risk Management Admin/Analyst/Investigator/Auditor |
| **Purview eDiscovery Roles** | eDiscovery workflows | eDiscovery Administrator/Manager/Case Member |
| **Purview Data Security AI Admin** | Manage DSPM for AI policies, configurations, and data security settings | Data Security AI Administrator |
| **Purview Data Security AI Viewer** | View-only access to DSPM for AI dashboards and reports | Data Security AI Viewer |
| **Purview Data Security AI Content Viewer** | View sensitive content flagged by DSPM for AI policies | Data Security AI Content Viewer |
| **Purview DLP Content Viewer** | View actual matched sensitive content in Content Explorer (gating role for DLP investigation) | Content Explorer Content Viewer |

### Power Platform (PPAC / Copilot Studio)

| Canonical Role | Typical Responsibilities | Accepted Aliases (Normalize From) |
|---|---|---|
| **Power Platform Admin** | Tenant-level Power Platform governance | Power Platform Administrator, Power Platform Admin |
| **Environment Admin** | Environment-level administration | Environment Administrator, Environment Admin |
| **Power Automate Admin** | Power Automate governance | Power Automate Administrator |
| **Pipeline Admin** | Deployment pipeline administration | Pipeline Administrator |

### Scenario-Based Roles (Use Only When Needed)

| Canonical Role | When to Use | Accepted Aliases (Normalize From) |
|---|---|---|
| **Dataverse System Admin** | When a control requires Dataverse security role elevation | System Administrator, Power Platform System Administrator |
| **Exchange Online Admin** | Email governance, message retention, transport rules, and DLP enforcement for Exchange workloads | Exchange Administrator, Exchange Admin |
| **SharePoint Admin** | SharePoint tenant settings and governance | SharePoint Administrator, SharePoint Admin |
| **SharePoint Site Collection Admin** | Site collection admin operations | Site Collection Administrator |
| **SharePoint Site Owner** | Site-level ownership tasks | SharePoint Site Owner, Site Owner |

---

## AI Governance Permission Matrix

| Permission | AI Administrator | Entra Global Admin | Entra Security Admin | Power Platform Admin |
|------------|------------------|---------------------|----------------------|----------------------|
| Manage Copilot settings | ✓ | ✓ | ✗ | ✗ |
| Manage Copilot connectors | ✓ | ✓ | ✗ | ✗ |
| Register Entra apps (delegated) | ✓* | ✓ | ✗ | ✗ |
| Consent to ExternalItem/ExternalConnection APIs | ✓ | ✓ | ✗ | ✗ |
| Consent to all Graph APIs | ✗ | ✓ | ✗ | ✗ |
| View Copilot usage reports | ✓ | ✓ | ✗ | ✗ |
| Manage AI feature access controls | ✓ | ✓ | ✗ | ✗ |
| Configure Admin Exclusion Groups | ✓ | ✓ | ✗ | ✗ |
| Create support tickets | ✓ | ✓ | ✓ | ✓ |
| Configure Defender XDR | ✗ | ✓ | ✓ | ✗ |
| Manage Defender policies | ✗ | ✓ | ✓ | ✗ |
| View Defender XDR security reports | ✗ | ✓ | ✓ | ✗ |
| Manage Conditional Access for agents | ✗ | ✓ | ✓ | ✗ |
| Configure DLP policies | ✗ | ✓ | ✗ | ✗ |
| Manage Power Platform environments | ✗ | ✓ | ✗ | ✓ |
| Configure Power Platform DLP | ✗ | ✓ | ✗ | ✓ |

*Requires delegation via Entra admin consent or custom role for app registration and limited API consent scope.

!!! tip "FSI Least-Privilege Role Assignment"
    - **For agent governance and Copilot management:** Prefer AI Administrator over Global Admin to enforce least-privilege access
    - **For Copilot connector management:** AI Administrator is sufficient for most connector delegation tasks
    - **For Defender XDR operations:** Use Entra Security Admin (not Global Admin) for security operations teams
    - **When Global Admin is required:** Initial tenant setup, broad Graph API consent beyond ExternalItem/ExternalConnection scope, or cross-service configuration
    - **For FINRA-regulated firms:** Document role assignments in your supervisory procedures per FINRA Rule 3110

## Role Selection Guidance

For FSI organizations implementing agent governance, selecting the right administrative role is critical for separation of duties and least-privilege compliance.

| Scenario | Recommended Role | Why Not Global Admin | Regulatory Alignment |
|----------|------------------|----------------------|---------------------|
| Manage Copilot settings and feature access | AI Administrator | Scoped to AI services only; prevents unnecessary tenant-wide access | FINRA 3110: least-privilege supervisory access |
| Manage Copilot connectors and delegation | AI Administrator | Sufficient permissions for connector management without broad admin scope | SOX 404: segregation of duties |
| Configure Defender XDR policies for AI workloads | Entra Security Admin | Security-scoped; no need for full tenant administration | OCC 2011-12: security operations separation |
| Configure DLP policies for AI applications | Purview Compliance Admin | Dedicated compliance role; Global Admin is overprivileged | GLBA 501(b): data protection oversight |
| Manage Power Platform environments | Power Platform Admin | Platform-scoped; AI Admin cannot manage environments | SOX 404: platform vs. AI governance separation |
| Initial tenant setup and broad API consent | Entra Global Admin | Required for initial configuration only; delegate afterward | Industry best practice: time-boxed elevation |

!!! tip "FSI Role Assignment Best Practice"
    For FINRA-regulated firms: Document all administrative role assignments in your Written Supervisory Procedures (WSPs). Use Entra Privileged Identity Management (PIM) to require just-in-time elevation for Global Admin access. Prefer AI Administrator for day-to-day Copilot governance and Entra Security Admin for Defender XDR security operations.

---

## Governance Roles (Non-Admin)

These roles appear in some controls under **Support & Questions** or governance workflows.

- **AI Governance Lead**
- **Compliance Officer**
- **Security Team** (organizational function, not a directory role)

---

## Functional and Operational Roles

Non-admin roles commonly referenced in controls for governance workflows, risk management, and agent development.

| Role | Scope | Description |
|------|-------|-------------|
| **Cloud Security Architect** | Organization | Designs cloud security architecture and evaluates AI agent security posture |
| **Copilot Studio Agent Author** | Power Platform | Creates and configures Copilot Studio agents within governed environments |
| **Agent Owner** | Power Platform | Owns agent lifecycle, configuration, and compliance for assigned agents |
| **Model Risk Manager** | Organization | Oversees model risk management per OCC 2011-12 and Fed SR 26-2 (formerly SR 11-7) |
| **Security Architect** | Organization | Defines security standards and reviews agent security configurations |
| **SOC Analyst** | Organization | Monitors security alerts and investigates AI agent-related incidents — see [SOC Analyst Purview RBAC Role Matrix](purview-soc-analyst-roles.md) for required Purview role assignments |

### Adoption Lead *[NEW in v1.5.0 — Microsoft CAPE alignment]*

**Primary purpose:** Drives end-user enablement, training, and change management for AI agent adoption across the organization. The Adoption Lead orchestrates community engagement, builder enablement programs, and behavior-change campaigns to support safe and effective agent usage aligned to FSI governance requirements.

**FSI accountability:** The Adoption Lead owns enablement strategy and training execution but does NOT replace regulated supervisory or oversight functions. For FINRA-supervised firms, FINRA Rule 3110 supervisory obligations remain with the designated registered principal. For banks subject to OCC 2011-12 or Fed SR 26-2, model risk oversight remains with the named model risk management function. The Adoption Lead supports compliance with training requirements (e.g., Control 2.14) but does not satisfy supervision or oversight obligations independently.

**Accepted aliases:** Training Lead, Enablement Lead, Change Management Lead, Community Manager

**Typical CoE function:** Enable — the Adoption Lead primarily operates within the Enable function of an Agentic Center of Excellence, working alongside Subject Matter Experts and Copilot Studio Agent Authors to accelerate safe adoption. See [Agentic Center of Excellence](../framework/agentic-coe.md) for full CoE function mapping.

**Related controls:** [2.14 (Training and Awareness Program)](../controls/pillar-2-management/2.14-training-and-awareness-program.md), [2.5 (Testing, Validation, and Quality Assurance)](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md), [2.13 (Documentation and Record Keeping)](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md)

**Related framework docs:** [Agentic Center of Excellence](../framework/agentic-coe.md), [Governance Cadence](../framework/governance-cadence.md), [Operating Model](../framework/operating-model.md)

### Agent Product Owner *[NEW in v1.5.0 — Microsoft CAPE alignment]*

**Primary purpose:** Owns the lifecycle of an individual agent or agent product family from intake through retirement. The Agent Product Owner is accountable for scenario prioritization, roadmap planning, business-line alignment, and portfolio-level value delivery for one or more agents. This role operates at the portfolio layer above individual agent configurations.

**FSI accountability:** The Agent Product Owner is responsible for agent lifecycle management and business value delivery but does NOT replace regulated supervisory roles or model risk management functions. FINRA Rule 3110 supervision of customer-facing agents remains with the designated registered principal. OCC 2011-12 and Fed SR 26-2 model risk oversight remains with the Model Risk Manager and independent validation function. SOX 302/404 controls over financial-reporting agents remain with the named control owner. The Agent Product Owner coordinates across these functions but does not substitute for them.

**Accepted aliases:** Agent Portfolio Owner, Agent Program Manager, AI Product Owner, Agent Lifecycle Owner

**Typical CoE function:** Scale — the Agent Product Owner primarily operates within the Scale function, responsible for intake pipeline, portfolio prioritization, and pattern reuse. May also support Optimize function for portfolio-level health signals and retirement triggers. See [Agentic Center of Excellence](../framework/agentic-coe.md) for full CoE function mapping.

**Related controls:** [3.1 (Agent Inventory and Metadata Management)](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md), [2.3 (Change Management and Release Planning)](../controls/pillar-2-management/2.3-change-management-and-release-planning.md), [2.13 (Documentation and Record Keeping)](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md), [3.6 (Orphaned Agent Detection and Remediation)](../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)

**Related framework docs:** [Agent Lifecycle](../framework/agent-lifecycle.md), [Agentic Center of Excellence](../framework/agentic-coe.md), [Governance Cadence](../framework/governance-cadence.md), [Operating Model](../framework/operating-model.md)

### Executive Sponsor *[NEW in v1.5.0 — Microsoft CAPE alignment]*

**Primary purpose:** Board-level or senior executive lead accountable for the enterprise AI program, CoE charter, and strategic alignment of AI agent initiatives to business objectives. The Executive Sponsor provides governance oversight, removes organizational barriers, and ensures adequate resourcing for the AI governance program. In FSI organizations, the Executive Sponsor is typically a Board committee chair, Chief Operating Officer, or Chief Innovation Officer.

**FSI accountability:** The Executive Sponsor provides strategic oversight and program governance but does NOT replace regulated supervisory or compliance functions. FINRA Rule 3110 supervision remains with the designated registered principal, not the Executive Sponsor. OCC 2011-12 and Fed SR 26-2 model risk oversight remains with the named Chief Risk Officer and independent validation function. SEC 17a-4 and FINRA 4511 recordkeeping obligations remain with the Chief Compliance Officer. The Executive Sponsor ensures these functions are adequately resourced and coordinated but does not substitute for them. For FINRA-supervised firms, the Executive Sponsor is typically NOT a registered principal unless explicitly designated as such in the firm's Written Supervisory Procedures (WSPs).

**Accepted aliases:** AI Program Sponsor, Board AI Committee Chair, Chief Innovation Officer (when serving in sponsor capacity), AI Governance Executive Sponsor

**Typical CoE function:** Scale (strategic oversight) — the Executive Sponsor operates across all CoE functions (Govern, Enable, Optimize, Scale) at the governance oversight layer, ensuring strategic alignment and adequate resourcing. The Executive Sponsor typically chairs or sponsors the quarterly AI Governance Committee per [Governance Cadence](../framework/governance-cadence.md). See [Agentic Center of Excellence](../framework/agentic-coe.md) for full CoE function mapping.

**Related controls:** [2.12 (Supervision and Oversight — FINRA Rule 3110)](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [2.6 (Model Risk Management)](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.13 (Documentation and Record Keeping)](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md), [3.3 (Compliance and Regulatory Reporting)](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md)

**Related framework docs:** [Agentic Center of Excellence](../framework/agentic-coe.md), [Operating Model](../framework/operating-model.md), [Governance Cadence](../framework/governance-cadence.md), [Governance Fundamentals](../framework/governance-fundamentals.md)

### Service Owner *[NEW in v1.5.0 — Microsoft CAPE alignment]*

**Primary purpose:** Business process or service owner responsible for the end-to-end operational performance of a business service supported by an AI agent. The Service Owner defines service-level objectives, owns escalation procedures, coordinates with the Agent Product Owner on feature priorities, and is accountable for business outcomes. Examples include the HR Helpdesk Manager for an HR-support agent, the KYC Operations Manager for a KYC-screening agent, or the IT Service Desk Manager for an IT-support agent.

**FSI accountability:** The Service Owner owns operational service delivery and business outcomes but does NOT replace regulated supervisory or model risk oversight functions. For customer-facing services in FINRA-supervised firms, FINRA Rule 3110 supervisory obligations remain with the designated registered principal. For agents affecting safety-and-soundness or financial reporting, OCC 2011-12 and Fed SR 26-2 model risk oversight remains with the Model Risk Manager. For agents handling personally identifiable information, GLBA 501(b) safeguards obligations remain with the Chief Information Security Officer. The Service Owner ensures agent outputs align to service-level objectives and escalates performance issues but does not satisfy independent oversight obligations.

**Accepted aliases:** Business Service Owner, Process Owner, Functional Owner, Service Manager

**Typical CoE function:** Optimize — the Service Owner primarily operates within the Optimize function, monitoring agent performance against service-level objectives, coordinating incident response, and surfacing drift or degradation signals. The Service Owner provides business-context feedback to the Enable and Scale functions. See [Agentic Center of Excellence](../framework/agentic-coe.md) for full CoE function mapping.

**Related controls:** [3.2 (Usage Analytics and Activity Monitoring)](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md), [2.9 (Agent Performance Monitoring and Optimization)](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md), [3.10 (Hallucination Feedback Loop)](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md), [3.4 (Incident Reporting and Root Cause Analysis)](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)

**Related framework docs:** [Agentic Center of Excellence](../framework/agentic-coe.md), [Agent Lifecycle](../framework/agent-lifecycle.md), [Governance Cadence](../framework/governance-cadence.md)

### Subject Matter Expert (SME) *[NEW in v1.5.0 — Microsoft CAPE alignment]*

**Primary purpose:** Domain expert responsible for validating the accuracy, completeness, and currency of knowledge sources, training data, and agent-generated outputs within their area of expertise. The SME provides subject-matter review for RAG corpus content, validates agent responses against authoritative sources, and participates in bias and fairness testing. The SME is NOT necessarily a technical role or a registered person — examples include a compliance policy expert validating a compliance Q&A agent's knowledge base, a claims adjudication expert reviewing a claims-support agent's recommendations, or a tax specialist validating a tax-advisory agent's outputs.

**FSI accountability:** The Subject Matter Expert validates knowledge accuracy and domain correctness but does NOT replace regulated supervisory functions or model risk management oversight. For FINRA-supervised firms, FINRA Rule 3110 supervision of customer-facing recommendations remains with the designated registered principal — the SME validates content accuracy but does not satisfy supervisory review obligations. For agents subject to OCC 2011-12 or Fed SR 26-2, independent model validation remains with the Model Risk Manager and validation function — the SME provides domain expertise to support validation but does not substitute for independent validation. The SME role is one input to the broader governance process, not a single point of accountability.

**Accepted aliases:** Domain Expert, Knowledge Owner, Content Validator, Business Analyst (when serving in knowledge-validation capacity)

**Typical CoE function:** Enable — the SME primarily operates within the Enable function, validating knowledge sources, reviewing agent templates, and supporting bias testing. The SME may also support Optimize function activities such as hallucination review and drift detection. See [Agentic Center of Excellence](../framework/agentic-coe.md) for full CoE function mapping.

**Related controls:** [2.16 (RAG Source Integrity Validation)](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md), [2.11 (Bias Testing and Fairness Assessment)](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.5 (Testing, Validation, and Quality Assurance)](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md), [3.10 (Hallucination Feedback Loop)](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md)

**Related framework docs:** [Agentic Center of Excellence](../framework/agentic-coe.md), [Agent Lifecycle](../framework/agent-lifecycle.md), [Operating Model](../framework/operating-model.md)

---

## Microsoft CAPE Role Mapping (cross-reference)

> **Note:** Microsoft's CAPE Frontier CoE blueprint defines 10 roles (6 strategic + 4 edge). This table maps each CAPE role to its FSI-AgentGov canonical equivalent. The 5 net-new roles introduced in v1.5.0 (Executive Sponsor, Agent Product Owner, Subject Matter Expert, Service Owner, Adoption Lead) are defined in [Functional and Operational Roles](#functional-and-operational-roles) above.
>
> **Position:** FSI-AgentGov retains canonical role names. CAPE role names are reference vocabulary used in `agentic-coe.md` and `microsoft-cape-crosswalk.md` only.

### Strategic CoE roles (6)

| CAPE role | FSI-AgentGov canonical role | Status | Notes |
|---|---|---|---|
| Executive Sponsor | Executive Sponsor | Map | Board-level AI program lead. See [Functional and Operational Roles](#executive-sponsor-new-in-v150-microsoft-cape-alignment) for full definition. |
| Business Owner | Business Owner (existing) | Map | Existing role per Zone 3 Governance Committee; clarified in v1.5.0 to avoid CAPE name collision. |
| CoE Lead | AI Governance Lead (existing) | Map | Functional equivalent in FSI-AgentGov context. |
| Agent Product Owner | Agent Product Owner | Map | Lifecycle owner (intake → retire) for individual agents or product families. See [Functional and Operational Roles](#agent-product-owner-new-in-v150-microsoft-cape-alignment) for full definition. |
| Platform & Operations | Power Platform Admin (existing) + Copilot Studio Agent Author (existing) | Map (split) | Two existing FSI roles cover this CAPE role. |
| Security / Risk / Compliance | CISO + Chief Risk Officer + Chief Compliance Officer (existing trio) | Map (trio) | All three FSI roles together cover this CAPE role. Each retains independent FSI accountability. |

### Edge / federated CoE roles (4)

| CAPE role | FSI-AgentGov canonical role | Status | Notes |
|---|---|---|---|
| Makers (citizen developers) | (Implicit — agent authors in business units) | Implicit | FSI-AgentGov does not name a "Maker" role. The function exists as agent authors operating under Power Platform Admin and Copilot Studio Agent Author governance. |
| Subject Matter Experts (SMEs) | Subject Matter Expert (SME) | Map | Domain expert who validates agent knowledge sources. See [Functional and Operational Roles](#subject-matter-expert-sme-new-in-v150-microsoft-cape-alignment) for full definition. |
| Service Owners | Service Owner | Map | Business service owner responsible for an agent in production (e.g., HR helpdesk owner for an HR agent). See [Functional and Operational Roles](#service-owner-new-in-v150-microsoft-cape-alignment) for full definition. |
| Adoption Leads | Adoption Lead | Map | Drives end-user enablement and change management. See [Functional and Operational Roles](#adoption-lead-new-in-v150-microsoft-cape-alignment) for full definition. |

### Federation principle

Federation of CoE roles to business units does NOT transfer regulated supervisory accountability. FINRA 3110 supervision, OCC 2011-12 model risk oversight, and SR 26-2 compliance remain with the named FSI roles (Chief Compliance Officer, Chief Risk Officer, AI Governance Lead) regardless of CoE shape (Centralized, Hybrid, or Federated). See `agentic-coe.md` (Phase 2) for the federation guardrail.

---

*FSI Agent Governance Framework v1.5.0 - May 2026*
