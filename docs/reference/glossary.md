# Glossary of Terms

Key terms and definitions used in the FSI Agent Governance Framework.

---

## A

**Agent**
A Microsoft 365 AI service that performs tasks based on user prompts. Includes Copilot Studio agents, Agent Builder agents, and SharePoint agents.

**ALM (Application Lifecycle Management)**
Process for managing agent development from creation through testing to production deployment.

**ALIM (Allowlist)**
List of approved connectors, actions, or data sources that agents can use. Opposite of blocklist.

**Allowlist**
See ALIM.

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

---

## D

**DLP (Data Loss Prevention)**
Policy that prevents unauthorized sharing of sensitive data by blocking actions or warning users.

**DSPM for AI (Data Security Posture Management for AI)**
Microsoft tool that monitors how AI agents interact with sensitive data.

**Disaster Recovery (DR)**
Plan to restore systems after a disaster.

---

## E

**ECOA (Equal Credit Opportunity Act)**
Federal law prohibiting discrimination in lending based on protected characteristics.

**Environment**
Container where Power Platform solutions and agents are hosted. Each organization can have multiple environments.

**Environment Group**
Collection of environments with shared governance policies.

---

## F

**FINRA (Financial Industry Regulatory Authority)**
Self-regulatory organization for securities brokers and dealers.

**Fair Lending**
Practice of lending without discrimination based on protected characteristics (race, color, religion, national origin, sex, marital status, age, disability, receipt of public assistance).

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

**Model**
System that makes predictions or decisions based on data. AI agents using ML algorithms are treated as models.

**Model Risk**
Risk that a model may produce inaccurate or biased outputs.

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
| Reg BI | Beneficial Ownership | Requires best interest for customers |
| Reg S-P | Privacy Rule | Customer information protection |
| SOX 302/404 | Internal Controls | Management responsibility for controls |
| GLBA 501-505 | Safeguards | Data protection requirements |
| OCC 2011-12 | Model Risk Guidance | Governance for models |
| SR 11-7 | Model Risk Management | Federal Reserve guidance for models |
| ECOA | Fair Lending | Prohibits lending discrimination |

---

*FSI Agent Governance Framework Beta - December 2025*
