# Glossary of Terms

Key terms and definitions used in the FSI Agent Governance Framework.

---

## A

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

**Agent AI Model Rules**
[Environment group rules](https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules) that control which AI models agents can use within an environment group. Configured in Power Platform Admin Center under Manage → Environment groups → Rules.

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

---

## C

**CAB (Change Advisory Board)**
Committee that reviews and approves changes before production deployment.

**CISO (Chief Information Security Officer)**
Executive responsible for organization's security program.

**Cloud DLP**
See DLP.

**Compliance Officer**
Role responsible for regulatory compliance and oversight.

**Conditional Access**
Microsoft Entra policy that enforces authentication requirements (like MFA) based on risk conditions.

**Connector**
Integration between an agent and external systems (SharePoint, Teams, Excel, etc.).

**Copilot**
Generic label used across multiple Microsoft products (e.g., Microsoft 365 Copilot, Copilot Studio, Security Copilot). In this framework, avoid using “Copilot” alone; prefer the full product name.

**Copilot Studio**
Microsoft platform for building, testing, and publishing agents. See [What is Copilot Studio?](https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio)

**Copilot Command Center**
Unified dashboard in Power Platform Admin Center that consolidates governance, analytics, and business value metrics for Copilot usage across the organization. Access via PPAC → Copilot. See [Copilot hub](https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub).

---

## D

**DLP (Data Loss Prevention)**
Policy that prevents unauthorized sharing of sensitive data by blocking actions or warning users.

**DSPM for AI (Data Security Posture Management for AI)**
Microsoft tool that monitors how AI agents interact with sensitive data.

**Disaster Recovery (DR)**
Plan to restore systems after a disaster.

**Developer Environment**
Personal sandbox environment for makers to build and test agents with limited governance requirements. Users can have up to 3 free developer environments. See [Create developer environment](https://learn.microsoft.com/en-us/power-platform/developer/create-developer-environment).

---

## E

**ECOA (Equal Credit Opportunity Act)**
Federal law prohibiting discrimination in lending based on protected characteristics.

**Environment**
Container where Power Platform solutions and agents are hosted. Each organization can have multiple environments.

**Environment Group**
Collection of Power Platform environments with shared governance policies and rules. Environment groups enable consistent policy application across multiple environments, preventing configuration drift. Configured in PPAC under Manage → Environment groups. See [Environment groups](https://learn.microsoft.com/en-us/power-platform/admin/environment-groups).

**Environment Routing**
Automatic placement of makers into appropriate Power Platform environments based on organizational rules such as security group membership. Prevents shadow AI creation in the default environment. See [Environment routing](https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing).

---

## F

**FINRA (Financial Industry Regulatory Authority)**
Self-regulatory organization for securities brokers and dealers.

**Fair Lending**
Practice of lending without discrimination based on protected characteristics (race, color, religion, national origin, sex, marital status, age, disability, receipt of public assistance).

**FDIC (Federal Deposit Insurance Corporation)**
Federal regulator for state non-member banks, state savings associations, and insured depository institutions. FDIC-supervised institutions follow interagency guidance including SR 11-7 for model risk and FFIEC IT examination standards.

**FIDO2**
Phishing-resistant authentication method using hardware keys.

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

**HSM (Hardware Security Module)**
Physical device that stores and manages encryption keys securely.

---

## I

**IAG (Information Access Governance)**
See RCD (Restricted Content Discovery).

**Immutable Storage**
Storage where data cannot be deleted or modified (WORM - Write Once, Read Many).

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
The built-in AI assistant in Microsoft 365 apps (e.g., Teams, Outlook, Word) that can use organizational data and policies. Distinct from **Copilot Studio**, which is for building agents. See [Microsoft 365 Copilot overview](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-overview)

**Model**
System that makes predictions or decisions based on data. AI agents using ML algorithms are treated as models.

**Model Risk**
Risk that a model may produce inaccurate or biased outputs.

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

**Phishing-Resistant MFA**
MFA that uses hardware keys (FIDO2) or Windows Hello, making it resistant to phishing attacks.

**PPAC (Power Platform Admin Center)**
Administrative portal for Power Platform governance and configuration.

**Purview**
Microsoft platform for data governance, compliance, and information protection.

**PPAC Inventory**
Tenant-wide visibility of all apps, flows, and Copilot agents within Power Platform Admin Center. Provides cross-environment snapshot for governance. Access via PPAC → Resources → Agents. See [View agent inventory](https://learn.microsoft.com/en-us/power-platform/admin/tenant-wide-agent-inventory).

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
Unauthorized agent creation outside governed environments, typically in the default Power Platform environment. Environment routing prevents shadow AI by directing makers to governed environments. See [Environment routing](https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing).

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
Storage principle where data can be written once but not modified or deleted.

---

## Z

**Zone (Governance Zone)**
Risk classification for agents:
- Zone 1: Personal (low risk)
- Zone 2: Team (medium risk)
- Zone 3: Enterprise (high risk)

---

## Regulatory Acronyms

| Acronym | Full Name | Purpose |
|---------|-----------|---------|
| FINRA 3110 | Supervision Rule | Requires written policies and procedures |
| FINRA 4511 | Books and Records | Requires 6-year recordkeeping |
| FINRA 4512 | Continuing Education | Training requirements |
| SEC 17a-3/4 | Recordkeeping | Requires 6-year record retention |
| SEC 10b-5 | Anti-Fraud Rule | Prohibits deceptive trading practices |
| Reg BI | Best Interest | Requires best interest for retail customers |
| Reg S-P | Privacy Rule | Customer information protection |
| SOX 302/404 | Internal Controls | Management responsibility for controls |
| GLBA 501-505 | Safeguards | Data protection requirements |
| OCC 2011-12 | Model Risk Guidance | Governance for models |
| SR 11-7 | Model Risk Management | Federal Reserve guidance for models |
| ECOA | Fair Lending | Prohibits lending discrimination |
| FDIC | Federal Deposit Insurance Corporation | Regulates state non-member banks |
| NCUA | National Credit Union Administration | Regulates federal credit unions |
| NCUA Part 748 | Security Program | Credit union information security |
| NYDFS Part 500 | Cybersecurity Regulation | NY state cybersecurity requirements |
| UDAAP | Unfair/Deceptive/Abusive Acts | CFPB consumer protection authority |
| NAIC Model Law | Insurance Data Security | State insurance data security baseline |

---

*FSI Agent Governance Framework Beta - December 2025*
