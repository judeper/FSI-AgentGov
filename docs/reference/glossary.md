# Glossary of Terms

Key terms and definitions used in the FSI Agent Governance Framework.

---

## A

**Adaptive Governance**
A governance approach where controls scale proportionally with risk level rather than applying uniform restrictions across all use cases. In this framework, adaptive governance is implemented through three [governance zones](../framework/zones-and-tiers.md) (Personal, Team, Enterprise), platform-enforced sharing limits, and promotion paths that require increasing oversight as agents access more sensitive data or broader audiences. The goal is to enable innovation in low-risk scenarios while applying rigorous controls where risk is highest. See [Governance Fundamentals](../framework/governance-fundamentals.md#adaptive-governance-philosophy).

**Agent**
In this framework, an **agent** means a **Microsoft 365 agent**: an AI capability in Microsoft 365 that performs tasks based on user prompts and configured tools/data. Examples include Copilot Studio agents, Agent Builder agents, SharePoint agents, and Teams agents. *Note: This framework governs only Microsoft 365 agents; other AI platforms are out of scope.*

**Agent Builder**
A Microsoft 365 capability for creating agents within Microsoft 365 experiences. Use this term when referring to Agent Builder specifically; otherwise use **agent**.

**AI agent**
Generic term for an AI-powered agent. In this framework, treat **AI agent** as synonymous with **agent** unless explicitly stated.

**ALM (Application Lifecycle Management)**
Process for managing agent development from creation through testing to production deployment.

**ALIM (Allowlist)**
List of approved connectors, actions, or data sources that agents can use. Opposite of blocklist.

**Allowlist**
See ALIM.

**Autonomy Cap**
The maximum level of agent autonomy supported for a given pattern, zone, or use case. Required by FSI regulatory framework (e.g., Reg B fair lending, FINRA 3110 supervision) to prevent agents from exercising authority that requires a human supervisor. Each pattern in `microsoft-cape-crosswalk.md` documents its Autonomy Cap.

*Source: FSI-AgentGov × Microsoft CAPE crosswalk; see `microsoft-cape-crosswalk.md`.*

**Agent AI Model Rules**
[Environment group rules](https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules) that control which AI models agents can use within an environment group. Configured in Power Platform Admin Center under Manage → Environment groups → Rules.

**Agent 365 (Microsoft Agent 365)**
Microsoft's centralized control plane for unified agent governance across the Microsoft 365 ecosystem. Provides a single registry, lifecycle management, observability dashboards, and policy enforcement for all agent types — including Copilot Studio, Agent Builder, SharePoint, and third-party agents. Generally available as of May 1, 2026 (announced Ignite 2025; GA as part of Microsoft 365 E7). See [Agent 365 Architecture](../framework/agent-identity-architecture.md) for how this framework maps to the platform.

**Agentic User**
An identity that acts on behalf of a human user but with delegated autonomy. In the Microsoft agent governance model, agentic users can perform tasks without direct real-time human supervision. See [Agent Identity Architecture](../framework/agent-identity-architecture.md).

**Agent Publishing**
The process of exposing agents through channels such as Microsoft Teams, websites, or third-party messaging platforms. Distinct from agent sharing. See [Publish and deploy agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels).

**Agent Sharing**
Controls who can access and co-author agents. Sharing grants edit or view permissions to other users, while publishing makes agents accessible to end users. See [Share and manage agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-share-bots).

---

## B

**Bias Testing**
Evaluation of whether an agent treats different demographic groups fairly and equitably. Required for agents making credit or employment decisions.

**Blocklist**
List of blocked/forbidden connectors, actions, or data sources that agents cannot use.

**Business Continuity (BC)**
Plan to continue operations if primary system fails.

**Break Glass Account**
Emergency access account excluded from Conditional Access policies, used when normal authentication is unavailable. Must be monitored and audited. See [Control 1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) for governance requirements.

---

## C

**CAB (Change Advisory Board)**
Committee that reviews and approves changes before production deployment.

**Capability Driver**
One of five dimensions in Microsoft's Agentic AI Maturity Model: AI Strategy & Experience, Business Strategy, AI Governance & Security, Technology & Data, and Organization & Culture. Each driver is measured 100 (Initial) through 500 (Optimized). The weakest driver determines an organization's effective ceiling regardless of strength on others.

**Note:** "Capability Driver" (or simply "Driver") is the FSI-AgentGov canonical term. Microsoft's source materials sometimes alternate "pillars" and "drivers" for the same concept; FSI-AgentGov adopts "Driver" exclusively to avoid collision with our four control families called "Pillars".

*Source: Microsoft CAPE Agentic Transformation Patterns Playbook; see `microsoft-cape-crosswalk.md` and `agentic-capability-drivers.md` (Phase 2).*

**CISO (Chief Information Security Officer)**
Executive responsible for organization's security program.

**Cloud DLP**
See DLP.

**Compliance Officer**
Role responsible for regulatory compliance and oversight.

**Center of Excellence (CoE)**
A cross-functional operating structure responsible for governing, enabling, optimizing, and scaling agentic AI within an organization. In FSI-AgentGov, the CoE concept is articulated in `agentic-coe.md` (Phase 2) and integrates with existing FSI governance committees, RACI assignments in `operating-model.md`, and lifecycle management in `agent-lifecycle.md`. CoE shapes (Centralized, Hybrid, Federated) describe organizational implementation; **federation does not transfer regulated supervisory accountability**.

*Source: FSI-AgentGov operating model + Microsoft CAPE CoE blueprint.*

**Conditional Access**
Microsoft Entra policy that enforces authentication requirements (like MFA) based on risk conditions.

**Connector**
Integration between an agent and external systems (SharePoint, Teams, Excel, etc.).

**Copilot**
Generic label used across multiple Microsoft products (e.g., Microsoft 365 Copilot, Copilot Studio, Security Copilot). In this framework, avoid using “Copilot” alone; prefer the full product name.

**Copilot Studio**
Microsoft platform for building, testing, and publishing agents. See [What is Copilot Studio?](https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio)

**Copilot Hub**
Unified dashboard in Power Platform Admin Center that consolidates governance, analytics, and business value metrics for Copilot usage across the organization. Access via PPAC → Copilot. Microsoft officially uses "Copilot area/hub" terminology. See [Copilot hub](https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub).

---

## D

**DLP (Data Loss Prevention)**
Policy that helps prevent unauthorized sharing of sensitive data by blocking actions or warning users.

**DSPM for AI (Data Security Posture Management for AI)**
Microsoft tool that monitors how AI agents interact with sensitive data (now labeled 'classic' in the Purview portal).

**Disaster Recovery (DR)**
Plan to restore systems after a disaster.

**Drift (drift thesis)**
The phenomenon where agents in production silently degrade in accuracy, relevance, or compliance posture over time without dramatic failure. Microsoft frames this as "agents don't fail dramatically; they slowly drift, giving wrong answers with confidence." For FSI, drift is the regulatory hook for FINRA 4511 / SEC 17a-4 ongoing supervision and OCC Bulletin 2026-13 (formerly OCC 2011-12) monitoring requirements. Mitigated by control 3.10 (Hallucination Tracking) and the Optimize CoE function.

*Source: Microsoft CAPE Walking Deck; see `agent-lifecycle.md` and `microsoft-cape-crosswalk.md`.*

**Developer Environment**
Personal sandbox environment for makers to build and test agents with limited governance requirements. Users can have up to 3 free developer environments. See [Create developer environment](https://learn.microsoft.com/en-us/power-platform/developer/create-developer-environment).

---

## E

**eDiscovery**
Microsoft Purview capability for identifying, collecting, and producing electronically stored information (ESI) in response to legal requests or regulatory examinations. In the context of AI agents, eDiscovery enables search and export of agent interaction records, conversation histories, and generated content. See [Control 1.19](../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md).

**Entra Agent ID**
Microsoft Entra capability that provides first-class identity objects for AI agents, enabling Conditional Access policies, Identity Protection, and lifecycle management for non-human agent identities. Currently in Public Preview. See [Agent Identity Architecture](../framework/agent-identity-architecture.md).

**ECOA (Equal Credit Opportunity Act)**
Federal law prohibiting discrimination in lending based on protected characteristics.

**Environment**
Container where Power Platform solutions and agents are hosted. Each organization can have multiple environments.

**Environment Group**
Collection of Power Platform environments with shared governance policies and rules. Environment groups enable consistent policy application across multiple environments, preventing configuration drift. Configured in PPAC under Manage → Environment groups. See [Environment groups](https://learn.microsoft.com/en-us/power-platform/admin/environment-groups).

**Environment Routing**
Automatic placement of makers into appropriate Power Platform environments based on organizational rules such as security group membership. Helps prevent shadow AI creation in the default environment. See [Environment routing](https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing).

---

## F

**FINRA (Financial Industry Regulatory Authority)**
Self-regulatory organization for securities brokers and dealers.

**Fair Lending**
Practice of lending without discrimination based on protected characteristics (race, color, religion, national origin, sex, marital status, age, disability, receipt of public assistance).

**FDIC (Federal Deposit Insurance Corporation)**
Federal regulator for state non-member banks, state savings associations, and insured depository institutions. FDIC-supervised institutions follow interagency guidance including SR 26-2 (formerly SR 11-7) for model risk and FFIEC IT examination standards.

**FIDO2**
Phishing-resistant authentication method using hardware keys.

**Frontier Readiness**
A parallel assessment in FSI-AgentGov (Phase 3 deliverable) that evaluates organizational maturity across Microsoft's five Capability Drivers using a 100–500 scale. Distinct from the 78-control assessment (which evaluates technical control implementation). The two assessments measure different things and are NOT mathematically merged.

*Source: FSI-AgentGov assessment engine; see `assessment/manifest/frontier-readiness.json` (Phase 3).*

---

## G

**GLBA (Gramm-Leach-Bliley Act)**
Federal law protecting consumer financial information.

**Governance**
Systems and procedures to ensure agents are used safely, securely, and in compliance with regulations.

**Governance Committee**
Decision-making body for Zone 3 agent approvals and oversight.

**Group Rules**
Policies applied consistently across environment groups to enforce governance and prevent drift. Rule types include: Sharing agents with Editor/Viewer permissions, Channel access for published agents, Authentication for agents, Generative AI settings, and Maker welcome content. Configured in PPAC under Manage → Environment groups → Rules. See [Environment group rules](https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules).

---

## H

**HITL (Human-in-the-Loop)**
A workflow pattern requiring human review and approval at defined checkpoints before an AI agent action proceeds. Required for Zone 2–3 agents performing sensitive operations. See [Control 2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).

**HSM (Hardware Security Module)**
Physical device that stores and manages encryption keys securely.

---

## I

**IAG (Information Access Governance)**
See RCD (Restricted Content Discovery).

**Immutable Storage**
Storage where data cannot be deleted or modified (WORM - Write Once, Read Many).

**Information Barriers**
Microsoft Purview policies that prevent specific groups of users from communicating with or discovering each other. In the context of AI agents, information barriers help prevent agents from accessing data across restricted segments (e.g., investment banking vs. research). See [Control 1.22](../controls/pillar-1-security/1.22-information-barriers.md).

**Insider Risk**
Risk that employees or authorized users may misuse their access for personal gain or harm.

**Integrated Apps**
Applications and connectors integrated into Microsoft 365.

**IRM (Information Rights Management)**
Technology that encrypts documents and restricts permissions (no copy, no print, no screenshot).

---

## L

**Legal Hold**
Requirement to preserve all relevant data for legal proceedings.

**Least Privilege**
Security principle of granting only the minimum permissions necessary to perform job duties.

---

## M

**Managed Environment**
Environment with governance policies enforced at the platform level.

**MFA (Multi-Factor Authentication)**
Login requirement combining something you know (password) with something you have (phone, security key).

**Microsoft 365 Copilot**
The built-in AI assistant in Microsoft 365 apps (e.g., Teams, Outlook, Word) that can use organizational data and policies. Distinct from **Copilot Studio**, which is for building agents. See [Microsoft 365 Copilot overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview)

**Microsoft Foundry (formerly Azure AI Foundry)**
Microsoft's unified platform for building, evaluating, and deploying generative AI applications and agents. Renamed from **Azure AI Foundry** to **Microsoft Foundry** as of May 2026. Existing documentation, URL slugs (`/azure/ai-foundry/`), SDK package names, and many in-product strings still reference "Azure AI Foundry" — both names refer to the same product. Foundry is the recommended evaluation harness for FSI quality, safety, and risk-and-safety assessments referenced by Controls 2.5, 2.6, 2.20, 1.21, and 1.24.

**Model**
System that makes predictions or decisions based on data. AI agents using ML algorithms are treated as models.

**Model Risk**
Risk that a model may produce inaccurate or biased outputs.

**MRM (Model Risk Management)**
Framework for identifying, measuring, monitoring, and controlling model risk, aligned with OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) and Fed SR 26-2 (formerly SR 11-7). See [Control 2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) for AI agent MRM requirements.

**M365 Certification**
Microsoft validation that an application meets security and compliance requirements. Higher trust level than Publisher Attested. Visible in M365 Admin Center under Settings → Integrated Apps.

**Maker Routing**
See Environment Routing.

---

## N

**NCUA (National Credit Union Administration)**
Federal regulator for federally insured credit unions. NCUA Part 748 establishes security program requirements. Credit unions follow similar technology risk management principles as banking regulators.

**NYDFS (New York Department of Financial Services)**
State regulator for financial institutions licensed in New York. NYDFS Part 500 (23 NYCRR 500) establishes cybersecurity requirements for covered entities including banks, insurers, and money transmitters with New York operations.

---

## O

**OCC (Office of the Comptroller of the Currency)**
Federal regulator for national banks and federal savings associations.

---

## P

**Pattern (Frontier Transformation Pattern)**
One of six design choices in Microsoft's CAPE framework describing how an organization deploys agents: Employee AI Enablement (1), Business Expert Empowerment (2), Workplace & IT Services (3), Core Business Process Transformation (4), External Engagement (5), AI-First Capabilities (6). Patterns are not stages — most organizations run multiple patterns simultaneously. Each pattern has a target maturity profile and a "scale-breaker" — the capability that will block scale first.

*Source: Microsoft CAPE Agentic Transformation Patterns Playbook; see `microsoft-cape-crosswalk.md` and `transformation-patterns.md` (Phase 2).*

**Phishing-Resistant MFA**
MFA that uses hardware keys (FIDO2) or Windows Hello, making it resistant to phishing attacks.

**Pillar (FSI control family)**
In FSI-AgentGov, "Pillar" refers exclusively to one of the four control families: **Pillar 1 Security** (29 controls), **Pillar 2 Management** (26 controls), **Pillar 3 Reporting** (14 controls), **Pillar 4 SharePoint** (9 controls). Together the four pillars contain all 78 controls.

> **Important disambiguation:** Microsoft CAPE materials sometimes use "pillar" to describe the five dimensions of the Agentic AI Maturity Model. In FSI-AgentGov, those five dimensions are called **Capability Drivers** (or simply **Drivers**). "Pillar" must NEVER be used to refer to a CAPE driver in FSI-AgentGov documentation. See `verify_language_rules.py` for enforcement.

*Source: FSI-AgentGov framework; see `governance-fundamentals.md` and `controls/CONTROL-INDEX.md`.*

**PPAC (Power Platform Admin Center)**
Administrative portal for Power Platform governance and configuration.

**Purview**
Microsoft platform for data governance, compliance, and information protection.

**PPAC Inventory**
Tenant-wide visibility of all apps, flows, and Copilot agents within Power Platform Admin Center. Provides cross-environment snapshot for governance. Access via PPAC → Copilot Hub or PPAC → Resources → Agents. See [Copilot Hub](https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub).

**PPAC Monitoring**
Health and performance insights for Copilot Studio agents in Power Platform Admin Center, including session success rates and degradation trends. Access via PPAC → Monitor → Copilot Studio. See [Monitor Copilot Studio](https://learn.microsoft.com/en-us/power-platform/admin/monitoring/monitor-copilot-studio).

**PPAC Security**
Centralized security posture management in Power Platform Admin Center providing security scores, recommendations, and misconfiguration detection. Access via PPAC → Security. See [Security overview](https://learn.microsoft.com/en-us/power-platform/admin/security/security-overview).

**Publisher Attested**
Self-attestation by application publishers regarding their security practices. Lower trust level than M365 Certification. Visible in M365 Admin Center under Settings → Integrated Apps.

---

## Q

**QA (Quality Assurance)**
Testing process to verify software quality and functionality.

---

## R

**RACI (Responsible, Accountable, Consulted, Informed)**
Matrix defining roles and responsibilities for activities.

**RCA (Root Cause Analysis)**
Investigation into why an incident occurred and what steps prevent recurrence.

**RCD (Restricted Content Discovery)**
SharePoint feature that controls which sites agents can access.

**Recordkeeping**
Maintaining records of activities for audit and compliance purposes.

**Runtime Protection**
Real-time monitoring and protection of agent activities to prevent misuse.

**Scale-breaker**
The single capability dimension that will block an organization's ability to scale its agent portfolio, regardless of strength on other dimensions. Microsoft's diagnostic identifies five common scale-breaker signals: many pilots with no portfolio; one-off agents with no reuse; great demos with low adoption; licenses without usage; shadow agents appearing. Each FSI Pattern has a typical scale-breaker documented in `microsoft-cape-crosswalk.md`.

*Source: Microsoft CAPE Agentic Transformation Patterns Playbook; see `microsoft-cape-crosswalk.md`.*

---

## S

**SEC (Securities and Exchange Commission)**
Federal regulator for securities markets and investment advisers.

**Sensitivity Label**
Metadata applied to documents indicating sensitivity level (e.g., Confidential, Internal).

**Segregation of Duties**
Principle that no single person should have authority over all steps of a critical process.

**SharePoint**
Microsoft platform for document management and collaboration.

**SIT (Sensitive Information Type)**
Pattern for identifying sensitive data types (e.g., credit cards, social security numbers).

**SOX (Sarbanes-Oxley Act)**
Federal law requiring internal controls and financial reporting for public companies.

**Supervised Learning**
Type of machine learning using labeled training data.

**Shadow AI**
Unauthorized agent creation outside governed environments, typically in the default Power Platform environment. Environment routing helps prevent shadow AI by directing makers to governed environments. See [Environment routing](https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing).

---

## T

**Tier**
Classification of environments by risk level (Development, Test, Production).

**TLS (Transport Layer Security)**
Encryption protocol for data in transit.

---

## U

**UAT (User Acceptance Testing)**
Testing by actual end-users to confirm system meets requirements.

**UDAAP (Unfair, Deceptive, or Abusive Acts or Practices)**
CFPB authority prohibiting financial institutions from engaging in unfair, deceptive, or abusive practices. Consumer-facing AI agents must avoid UDAAP violations by ensuring accurate outputs, proper disclosures, and fair treatment.

**Unsupervised Learning**
Type of machine learning without labeled training data.

---

## V

**Validation**
Independent testing to confirm a model works as intended.

**Vendor Risk**
Risk associated with third-party connectors and integrations.

---

## W

**WORM (Write Once, Read Many)**
Storage principle where data can be written once but not modified or deleted. Per SEC October 2022 amendments (effective May 2023), WORM is one of two acceptable approaches for SEC 17a-4 compliance; the audit-trail alternative is also permitted.

---

## Z

**Zone (Governance Zone)**
Risk classification for agents:

- Zone 1: Personal Productivity (low risk)
- Zone 2: Team Collaboration (medium risk)
- Zone 3: Enterprise Managed (high risk)

---

## Regulatory Acronyms

| Acronym | Full Name | Purpose |
|---------|-----------|---------|
| FINRA 3110 | Supervision Rule | Requires written policies and procedures |
| FINRA 4511 | Books and Records | Requires 6-year recordkeeping |
| FINRA 4512 | Customer Account Information | Customer account record requirements |
| SEC 17a-3/4 | Recordkeeping | Requires 3–6 year record retention (varies by record type) |
| SEC 10b-5 | Anti-Fraud Rule | Prohibits deceptive trading practices |
| Reg BI | Best Interest | Requires best interest for retail customers |
| Reg S-P | Privacy Rule | Customer information protection |
| SOX 302/404 | Internal Controls | Management responsibility for controls |
| GLBA 501-505 | Safeguards | Data protection requirements |
| OCC Bulletin 2026-13 (formerly 2011-12) | Model Risk Guidance | Governance for models |
| SR 26-2 (formerly SR 11-7) | Model Risk Management | Federal Reserve guidance for models |
| ECOA | Fair Lending | Prohibits lending discrimination |
| FDIC | Federal Deposit Insurance Corporation | Regulates state non-member banks |
| NCUA | National Credit Union Administration | Regulates federal credit unions |
| NCUA Part 748 | Security Program | Credit union information security |
| NYDFS Part 500 | Cybersecurity Regulation | NY state cybersecurity requirements |
| UDAAP | Unfair/Deceptive/Abusive Acts | CFPB consumer protection authority |
| NAIC Model Law | Insurance Data Security | State insurance data security baseline |

---

*FSI Agent Governance Framework v1.6.2 - May 2026*
